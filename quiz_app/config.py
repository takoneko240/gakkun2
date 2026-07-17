import json
import os
import sys

DEFAULTS = {
    "excel_path": "kanji.xlsx",
    "interval_minutes": 5,
    "retry_minutes": 1,
    "multiplication_min": 2,
    "multiplication_max": 9,
    "categories": ["multiplication", "division", "kanji"],
    "music_folder": "music",
    "idle_music_minutes": 3,
}


def base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def config_path():
    return os.path.join(base_dir(), "config.json")


def load_config():
    path = config_path()
    if not os.path.exists(path):
        save_config(DEFAULTS)
        return dict(DEFAULTS)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    merged = dict(DEFAULTS)
    merged.update(data)
    return merged


def save_config(config):
    with open(config_path(), "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def resolve_path(relative_path):
    return os.path.join(base_dir(), relative_path)
