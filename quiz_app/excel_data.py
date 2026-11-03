import os
import re

import openpyxl

HEADER = ["レベル", "例文", "読み"]

# 例文の中で読ませたい語を［］で囲む。読みは［］の中の語の読み。
# 正解が複数ある場合は読みを「/」で区切る（例: きょう/こんにち）。
SAMPLE_ROWS = [
    (1, "がっこうには たくさんの ［人］が いる", "ひと"),
    (1, "［山］に のぼる", "やま"),
    (2, "［先生］に あいさつする", "せんせい"),
]

_TARGET_PATTERN = re.compile(r"^(.*?)［(.+?)］(.*)$")


class KanjiEntry:
    def __init__(self, level, before, target, after, readings):
        self.level = level
        self.before = before
        self.target = target
        self.after = after
        self.readings = readings

    @property
    def key(self):
        # 例文を書き直してもスコアが引き継がれるよう、例文ではなく
        # 「語＋読み」でキーを作る。
        return f"kanji:{self.target}:{self.readings[0]}"

    @property
    def write_key(self):
        # 書き取り問題（読みをカタカナで見せて漢字で書かせる）のキー。
        return f"kanji_write:{self.target}:{self.readings[0]}"


def ensure_sample_file(path):
    if os.path.exists(path):
        return

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(HEADER)
    for row in SAMPLE_ROWS:
        ws.append(list(row))
    wb.save(path)


def parse_row(level, sentence, yomi):
    if level is None or sentence is None or yomi is None:
        return None
    try:
        level = int(level)
    except (TypeError, ValueError):
        return None

    sentence = str(sentence).strip()
    readings = [r.strip() for r in str(yomi).split("/") if r.strip()]
    if not sentence or not readings:
        return None

    match = _TARGET_PATTERN.match(sentence)
    if match:
        before, target, after = match.groups()
    else:
        # ［］が無い行は、文全体を読ませる語として扱う。
        before, target, after = "", sentence, ""
    return KanjiEntry(level, before, target, after, readings)


def load_kanji_list(path):
    if not os.path.exists(path):
        return []

    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.active

    entries = []
    for row in ws.iter_rows(min_row=2, max_col=3, values_only=True):
        entry = parse_row(*row)
        if entry:
            entries.append(entry)

    wb.close()
    return entries
