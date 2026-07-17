from . import allowance as allowance_module
from . import excel_data, questions, quiz_window
from . import scores as scores_module

RECHECK_MS = 5000


class Scheduler:
    def __init__(
        self, root, config, excel_path, scores_path, monitor_geometry=None,
        music_folder=None, allowance_path=None,
    ):
        self.root = root
        self.config = config
        self.excel_path = excel_path
        self.scores_path = scores_path
        self.scores = scores_module.load_scores(scores_path)
        self.monitor_geometry = monitor_geometry
        self.music_folder = music_folder
        self.allowance_path = allowance_path
        self.total_yen = allowance_module.load_total(allowance_path) if allowance_path else 0
        self.quiz_open = False

    def _pick_question(self):
        kanji_list = excel_data.load_kanji_list(self.excel_path)
        return questions.pick_question(self.config, kanji_list, self.scores)

    def start(self):
        self._schedule_next_regular()

    def _schedule_next_regular(self):
        interval_ms = int(self.config["interval_minutes"] * 60 * 1000)
        self.root.after(interval_ms, self._trigger_regular)

    def _trigger_regular(self):
        if self.quiz_open:
            self.root.after(RECHECK_MS, self._trigger_regular)
            return

        self._open_quiz(self._pick_question())
        self._schedule_next_regular()

    def _trigger_retry(self, question):
        if self.quiz_open:
            self.root.after(RECHECK_MS, lambda: self._trigger_retry(question))
            return

        self._open_quiz(question)

    def _open_quiz(self, question):
        self.quiz_open = True
        quiz_window.show_quiz(
            self.root,
            question,
            self._on_result,
            monitor_geometry=self.monitor_geometry,
            music_folder=self.music_folder,
            idle_music_minutes=self.config["idle_music_minutes"],
            total_yen=self.total_yen,
            allowance_per_correct=self.config["allowance_per_correct"],
        )

    def _on_result(self, correct, question):
        self.quiz_open = False

        scores_module.apply_result(self.scores, question.key, correct)
        scores_module.save_scores(self.scores_path, self.scores)

        if correct and self.allowance_path:
            self.total_yen += self.config["allowance_per_correct"]
            allowance_module.save_total(self.allowance_path, self.total_yen)

        if not correct:
            retry_ms = int(self.config["retry_minutes"] * 60 * 1000)
            self.root.after(retry_ms, lambda: self._trigger_retry(question))

    def force_quiz_now(self):
        if self.quiz_open:
            return
        self._open_quiz(self._pick_question())
