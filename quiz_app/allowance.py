import json
import os


def load_total(path):
    if not os.path.exists(path):
        return 0
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("total_yen", 0)


def save_total(path, total_yen):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"total_yen": total_yen}, f, ensure_ascii=False, indent=2)
