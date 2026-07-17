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
