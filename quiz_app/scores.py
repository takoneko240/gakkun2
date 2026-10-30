import json
import os

# わざと間違え続けても点数が際限なく下がらないよう、上下限を設ける。
# 下限が深いと、その問題だけが延々と出題され続けてしまうため。
SCORE_MIN = -3
SCORE_MAX = 5


def load_scores(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_scores(path, scores):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)


def apply_result(scores, key, correct):
    score = scores.get(key, 0) + (1 if correct else -1)
    scores[key] = max(SCORE_MIN, min(SCORE_MAX, score))


def prune_missing_kanji(scores, kanji_list):
    valid_keys = {entry.key for entry in kanji_list}
    stale_keys = [
        key for key in scores
        if key.startswith("kanji:") and key not in valid_keys
    ]
    for key in stale_keys:
        del scores[key]
    return bool(stale_keys)
