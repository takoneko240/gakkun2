from . import allowance as allowance_module
from . import excel_data, questions, quiz_window
from . import scores as scores_module
from .applog import logger

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
        self.regular_episode_key = None

    def _pick_question(self):
        kanji_list = excel_data.load_kanji_list(self.excel_path)
        if scores_module.prune_missing_kanji(self.scores, kanji_list):
            scores_module.save_scores(self.scores_path, self.scores)
        return questions.pick_question(self.config, kanji_list, self.scores)

    def start(self):
        self._trigger_regular()

    def _schedule_next_regular(self):
        interval_ms = int(self.config["interval_minutes"] * 60 * 1000)
        self.root.after(interval_ms, self._trigger_regular)

    def _trigger_regular(self):
        if self.quiz_open:
            self.root.after(RECHECK_MS, self._trigger_regular)
            return

        question = self._pick_question()
        self.regular_episode_key = question.key
        logger.info("定期出題: %s %s", question.kind, question.key)
        self._open_quiz(question)
        # 次の5分後の予約は、このエピソード(誤答リトライを含む)が正解で
        # 終わった時点で _on_result から行う。ここで即座に予約すると、
        # 出題に気づくのが遅れたり誤答リトライが挟まったりした場合に、
        # 実際に正解してから5分経たずに次の問題が出てしまう。

    def _trigger_retry(self, question):
        if self.quiz_open:
            self.root.after(RECHECK_MS, lambda: self._trigger_retry(question))
            return

        logger.info("誤答リトライ出題: %s %s", question.kind, question.key)
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
        logger.info("回答結果: %s %s -> %s", question.kind, question.key, "正解" if correct else "不正解")

        scores_module.apply_result(self.scores, question.key, correct)
        scores_module.save_scores(self.scores_path, self.scores)

        if correct and self.allowance_path:
            self.total_yen += self.config["allowance_per_correct"]
            allowance_module.save_total(self.allowance_path, self.total_yen)

        if not correct:
            retry_ms = int(self.config["retry_minutes"] * 60 * 1000)
            self.root.after(retry_ms, lambda: self._trigger_retry(question))
        elif question.key == self.regular_episode_key:
            self.regular_episode_key = None
            self._schedule_next_regular()

    def force_quiz_now(self):
        if self.quiz_open:
            return
        question = self._pick_question()
        logger.info("強制出題(テスト): %s %s", question.kind, question.key)
        self._open_quiz(question)
