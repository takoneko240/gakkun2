import random

from .speech import multiplication_reading

FULLWIDTH_DIGITS = "０１２３４５６７８９"
HALFWIDTH_DIGITS = "0123456789"
_DIGIT_TRANSLATION = str.maketrans(FULLWIDTH_DIGITS, HALFWIDTH_DIGITS)
_KATAKANA_TO_HIRAGANA = {code: code - 0x60 for code in range(ord("ァ"), ord("ヶ") + 1)}
_HIRAGANA_TO_KATAKANA = {code: code + 0x60 for code in range(ord("ぁ"), ord("ゖ") + 1)}

KANJI_KINDS = ("kanji", "kanji_write")


def to_katakana(text):
    return text.translate(_HIRAGANA_TO_KATAKANA)


def _normalize_kana(text):
    return "".join(text.split()).translate(_KATAKANA_TO_HIRAGANA)


class Question:
    def __init__(self, kind, key, prompt, answers, level=None, sentence=None, reading=None):
        self.kind = kind
        self.key = key
        self.prompt = prompt
        self.answers = answers
        self.level = level
        # 漢字問題のみ: (線より前, 線を引く語, 線より後)
        self.sentence = sentence
        # 算数のみ: 答えたあとに読み上げる九九（割り算も掛け算の形で読む）
        self.reading = reading

    @property
    def answer(self):
        return self.answers[0]

    def is_correct(self, user_input):
        if self.kind == "kanji":
            return _normalize_kana(user_input) in self.answers
        if self.kind == "kanji_write":
            return "".join(user_input.split()) in self.answers

        normalized = user_input.strip().translate(_DIGIT_TRANSLATION)
        return normalized in self.answers


def _multiplication_candidates(config):
    lo, hi = config["multiplication_min"], config["multiplication_max"]
    for a in range(lo, hi + 1):
        for b in range(lo, hi + 1):
            yield f"multiplication:{a}:{b}", ("multiplication", a, b)


def _division_candidates(config):
    lo, hi = config["multiplication_min"], config["multiplication_max"]
    for divisor in range(lo, hi + 1):
        for quotient in range(lo, hi + 1):
            yield f"division:{divisor}:{quotient}", ("division", divisor, quotient)


def _build_question(key, payload):
    kind = payload[0]
    if kind == "multiplication":
        _, a, b = payload
        return Question(kind, key, f"{a} × {b} = ?", [str(a * b)],
                        reading=multiplication_reading(a, b))
    if kind == "division":
        _, divisor, quotient = payload
        return Question(kind, key, f"{divisor * quotient} ÷ {divisor} = ?", [str(quotient)],
                        reading=multiplication_reading(divisor, quotient))

    if kind == "kanji_write":
        # 線を引く語を読み（カタカナ）にして見せ、漢字で書かせる。
        _, entry, more_kanji_forms = payload
        shown = to_katakana(entry.readings[0])
        return Question(
            kind, key, f"{entry.before}［{shown}］{entry.after}",
            [entry.target, *more_kanji_forms],
            level=entry.level, sentence=(entry.before, shown, entry.after),
        )
    _, entry = payload
    return Question(
        kind, key, f"{entry.before}［{entry.target}］{entry.after}", entry.readings,
        level=entry.level, sentence=(entry.before, entry.target, entry.after),
    )


def _is_mastered(key, scores, config):
    return scores.get(key, 0) >= config["mastery_score"]


def current_kanji_level(kanji_list, scores, config):
    """まだ習得しきれていない一番やさしいレベルを返す。

    各レベルの問題のうち level_up_ratio 以上を習得したら、次のレベルに進む。
    """
    levels = sorted({entry.level for entry in kanji_list})
    for level in levels:
        keys = {entry.key for entry in kanji_list if entry.level == level}
        mastered = sum(1 for key in keys if _is_mastered(key, scores, config))
        if mastered < len(keys) * config["level_up_ratio"]:
            return level
    return levels[-1] if levels else None


def _kanji_chars(text):
    return {ch for ch in text if ch == "々" or "一" <= ch <= "鿿"}


def _more_kanji_forms(entry, kanji_list):
    """同じ読みで、より多く漢字を使った書き方（例: 月よう日 → 月曜日）を返す。

    IME で変換すると交ぜ書きにならないので、書き取りではこれらも正解にする。
    同音の別の語（花/鼻）は漢字が含まれないので正解にならない。
    """
    chars = _kanji_chars(entry.target)
    forms = []
    for other in kanji_list:
        if (
            other.readings[0] == entry.readings[0]
            and other.target != entry.target
            and other.target not in forms
            and chars < _kanji_chars(other.target)
        ):
            forms.append(other.target)
    return forms


def _kanji_candidates(kanji_list, scores, config):
    level = current_kanji_level(kanji_list, scores, config)
    # 同じ語・読みの例文が複数ある場合は、例文をランダムに1つ選ぶ。
    by_key = {}
    for entry in kanji_list:
        if entry.level <= level:
            by_key.setdefault(entry.key, []).append(entry)
    for key, entries in by_key.items():
        yield key, ("kanji", random.choice(entries))
        # 書き取りは、読みを習得した語だけを出題する（読めない字は書けないため）。
        if _is_mastered(key, scores, config):
            yield entries[0].write_key, (
                "kanji_write", random.choice(entries),
                _more_kanji_forms(entries[0], kanji_list),
            )


def _weight(key, scores):
    # 苦手な問題・未出題の問題ほど出やすく、習得済みの問題は時々復習として出る。
    # 最低点の問題だけを出し続けると、1問で詰まったときに同じ問題ばかりに
    # なってしまうため、重み付きのランダムにしている。
    if key not in scores:
        return 3.0
    score = scores[key]
    if score <= 0:
        return 4.0
    if score == 1:
        return 1.0
    if score == 2:
        return 0.5
    return 0.2


def pick_question(config, kanji_list, scores, recent_keys=()):
    categories = list(config["categories"])
    if "kanji" in categories and not kanji_list:
        categories.remove("kanji")
    if not categories:
        categories = ["multiplication"]

    # カテゴリはまず category_weights の比率でランダム選択し、その中で出題対象を
    # 絞り込む。全問題を1つのプールにすると、問題数が多いカテゴリ（掛け算・割り算）に
    # 埋もれて漢字などが出にくくなるため、カテゴリ単位で分けている。
    category_weights = config.get("category_weights") or {}
    category = random.choices(
        categories, weights=[category_weights.get(c, 1) for c in categories],
    )[0]
    if category == "multiplication":
        candidates = list(_multiplication_candidates(config))
    elif category == "division":
        candidates = list(_division_candidates(config))
    else:
        candidates = list(_kanji_candidates(kanji_list, scores, config))

    # 直近に出した問題は、他に候補があれば避ける。
    fresh = [c for c in candidates if c[0] not in recent_keys]
    if fresh:
        candidates = fresh

    weights = [_weight(key, scores) for key, _ in candidates]
    key, payload = random.choices(candidates, weights=weights)[0]
    return _build_question(key, payload)
