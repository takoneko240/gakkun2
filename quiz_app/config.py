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
    "idle_music_minutes": 10,
    "allowance_per_correct": 2,
    # カテゴリの出題比率（相対値）。ここに無いカテゴリは 1 として扱う。
    # 掛け算・割り算は、答えたあと（正解でも不正解でも）九九を読み上げる。
    "speak_math_answer": True,
    "category_weights": {"multiplication": 1, "division": 1, "kanji": 2},
    # 誤答時は正解を表示したまま、待ち時間がたつまで書き写しの入力を受け付けない。
    # 待ち時間は誤答のたびに +step、正解のたびに -step（min〜max の範囲）。
    "wrong_wait_min_seconds": 10,
    "wrong_wait_max_seconds": 60,
    "wrong_wait_step_seconds": 5,
    # 漢字は易しいレベルから出題し、そのレベルの問題の level_up_ratio 以上が
    # mastery_score 点以上になったら次のレベルを出題対象に加える。
    "mastery_score": 1,
    "level_up_ratio": 0.8,
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
