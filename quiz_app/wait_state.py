import json
import os

# 誤答時の待ち時間（秒）を保存する。アプリを再起動しても引き継ぐ。


def load_wait_seconds(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return int(json.load(f).get("wrong_wait_seconds", default))
    except (OSError, ValueError, TypeError, AttributeError):
        return default


def save_wait_seconds(path, seconds):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"wrong_wait_seconds": seconds}, f, ensure_ascii=False, indent=2)
