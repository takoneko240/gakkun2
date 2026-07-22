import random

FULLWIDTH_DIGITS = "０１２３４５６７８９"
HALFWIDTH_DIGITS = "0123456789"
_DIGIT_TRANSLATION = str.maketrans(FULLWIDTH_DIGITS, HALFWIDTH_DIGITS)


class Question:
    def __init__(self, kind, key, prompt, answer):
        self.kind = kind
        self.key = key
        self.prompt = prompt
        self.answer = answer

    def is_correct(self, user_input):
        if self.kind == "kanji":
            return user_input.strip() == self.answer

        normalized = user_input.strip().translate(_DIGIT_TRANSLATION)
        return normalized == self.answer


def _multiplication_candidates(config):
    lo, hi = config["multiplication_min"], config["multiplication_max"]
    for a in range(lo, hi + 1):
        for b in range(lo, hi + 1):
            yield f"multiplication:{a}:{b}", "multiplication", a, b


def _division_candidates(config):
    lo, hi = config["multiplication_min"], config["multiplication_max"]
    for divisor in range(lo, hi + 1):
        for quotient in range(lo, hi + 1):
            yield f"division:{divisor}:{quotient}", "division", divisor, quotient


def _kanji_candidates(kanji_list):
    for kanji, yomi in kanji_list:
        yield f"kanji:{kanji}", "kanji", kanji, yomi


def _build_question(kind, key, a, b):
    if kind == "multiplication":
        return Question(kind, key, f"{a} × {b} = ?", str(a * b))
    if kind == "division":
        dividend = a * b
        return Question(kind, key, f"{dividend} ÷ {a} = ?", str(b))

    kanji, yomi = a, b
    return Question(kind, key, f"「{kanji}」の読みを ひらがな で入力してください", yomi)


def _candidates_for_category(category, config, kanji_list):
    if category == "multiplication":
        return list(_multiplication_candidates(config))
    if category == "division":
        return list(_division_candidates(config))
    return list(_kanji_candidates(kanji_list))


def _min_score_subset(group, scores):
    min_score = min(scores[c[0]] for c in group)
    return [c for c in group if scores[c[0]] == min_score]


def pick_question(config, kanji_list, scores):
    categories = list(config["categories"])
    if "kanji" in categories and not kanji_list:
        categories.remove("kanji")
    if not categories:
        categories = ["multiplication"]

    # カテゴリはまず均等にランダム選択し、その中で出題対象を絞り込む。
    # 全問題を1つのプールにすると、問題数が多いカテゴリ（掛け算・割り算）に
    # 埋もれて漢字などが出にくくなるため、カテゴリ単位で分けている。
    category = random.choice(categories)
    candidates = _candidates_for_category(category, config, kanji_list)

    # 出題対象を「解答済み（scores.jsonに記録あり）」と「未出題」に分ける。
    # 解答済みの中に0点以下（要復習）のものがあれば、未出題より先にそちらを
    # 優先し、その中でも最低点のものを優先する。未出題の問題は、解答済みが
    # 全て1点以上（＝一巡して習得済み）になって初めて出題対象に入る。
    scored = [c for c in candidates if c[0] in scores]
    unscored = [c for c in candidates if c[0] not in scores]

    needs_review = [c for c in scored if scores[c[0]] <= 0]
    if needs_review:
        lowest = _min_score_subset(needs_review, scores)
    elif unscored:
        lowest = unscored
    elif scored:
        lowest = _min_score_subset(scored, scores)
    else:
        lowest = candidates

    key, kind, a, b = random.choice(lowest)
    return _build_question(kind, key, a, b)
