import json
import os


def load_scores(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_scores(path, scores):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)


def apply_result(scores, key, correct):
    scores[key] = scores.get(key, 0) + (1 if correct else -1)


def prune_missing_kanji(scores, kanji_list):
    valid_keys = {f"kanji:{kanji}" for kanji, _ in kanji_list}
    stale_keys = [
        key for key in scores
        if key.startswith("kanji:") and key not in valid_keys
    ]
    for key in stale_keys:
        del scores[key]
    return bool(stale_keys)
