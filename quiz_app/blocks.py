"""算数の式をブロック（立方体）で見せるアニメーション。

答えたあとに、式の意味を目で見て分かるようにする。
- 掛け算 a × b: a こずつの ブロックの れつが b つぶん（1れつずつ ふえる）
- 割り算 N ÷ d: N この ブロックを d こずつ とりだして れつに ならべる
- たし算・ひき算 a ± b ± c: 1ぎょうずつ、ふえる・へる ようすを 見せる
5こ・10こ ごとに すきまを あけて、数えやすくしている。
"""
import tkinter.font as tkfont

BG = "#111827"
TEXT = "#F9FAFB"
SUB_TEXT = "#9CA3AF"
COUNT_TEXT = "#FBBF24"
PILE_COLOR = "#6B7280"
ROW_COLORS = [
    "#60A5FA", "#34D399", "#FBBF24", "#F472B6", "#A78BFA",
    "#F87171", "#2DD4BF", "#FB923C", "#A3E635",
]
START_COLOR = "#60A5FA"
ADD_COLORS = ["#34D399", "#FB923C"]
MINUS_COLOR = "#F87171"
CAPTION_H = 64
MAX_PITCH = 64


def _shade(color, factor):
    r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    if factor >= 1:
        r, g, b = (int(v + (255 - v) * (factor - 1)) for v in (r, g, b))
    else:
        r, g, b = (int(v * factor) for v in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


class _Board:
    def __init__(self, canvas, pitch):
        self.canvas = canvas
        self.pitch = pitch
        self.size = pitch * 0.78
        self.depth = pitch * 0.18
        self.font = tkfont.Font(family="Meiryo", size=max(14, int(pitch * 0.42)), weight="bold")
        self.caption_font = tkfont.Font(family="Meiryo", size=26, weight="bold")

    def later(self, ms, fn):
        def run():
            if self.canvas.winfo_exists():
                fn()
        self.canvas.after(int(ms), run)

    def cube(self, x, y, color, tag):
        """(x, y) を前の面の左上として、立方体を描く。"""
        c, s, d = self.canvas, self.size, self.depth
        edge = _shade(color, 0.55)
        c.create_rectangle(x, y, x + s, y + s, fill=color, outline=edge, width=2,
                           tags=(tag, f"{tag}front"))
        c.create_polygon(x, y, x + d, y - d, x + s + d, y - d, x + s, y,
                         fill=_shade(color, 1.35), outline=edge, width=2, tags=(tag, f"{tag}top"))
        c.create_polygon(x + s, y, x + s + d, y - d, x + s + d, y + s - d, x + s, y + s,
                         fill=_shade(color, 0.75), outline=edge, width=2, tags=(tag, f"{tag}side"))

    def recolor(self, tag, color):
        c = self.canvas
        edge = _shade(color, 0.55)
        c.itemconfigure(f"{tag}front", fill=color, outline=edge)
        c.itemconfigure(f"{tag}top", fill=_shade(color, 1.35), outline=edge)
        c.itemconfigure(f"{tag}side", fill=_shade(color, 0.75), outline=edge)

    def ghost(self, x, y, tag):
        """ひいた（なくなった）ブロック: 点線のわくと赤い ×。"""
        c, s = self.canvas, self.size
        c.delete(tag)
        c.create_rectangle(x, y, x + s, y + s, outline=SUB_TEXT, dash=(4, 3), width=2)
        m = s * 0.2
        c.create_line(x + m, y + m, x + s - m, y + s - m, fill=MINUS_COLOR, width=3)
        c.create_line(x + s - m, y + m, x + m, y + s - m, fill=MINUS_COLOR, width=3)

    def label(self, x, y, text, color=TEXT, anchor="w"):
        return self.canvas.create_text(x, y, text=text, fill=color, font=self.font, anchor=anchor)

    def caption(self, text, item=None):
        c = self.canvas
        if item is not None:
            c.itemconfigure(item, text=text)
            return item
        return c.create_text(
            int(c.cget("width")) / 2, int(c.cget("height")) - CAPTION_H / 2,
            text=text, fill=TEXT, font=self.caption_font,
        )


def _offset(i, pitch):
    """i 番目のブロックの横位置。5こごと・10こごとに すきまを あける。"""
    return i * pitch + (i // 5) * pitch * 0.3 + (i // 10) * pitch * 0.4


def _span(n, pitch):
    return _offset(n - 1, pitch) + pitch if n else 0


def show(canvas, payload):
    """payload の式をアニメーションで描く。描き終わるまでの時間（ミリ秒）を返す。"""
    canvas.delete("all")
    kind = payload[0]
    if kind == "multiplication":
        return _show_multiplication(canvas, payload[1], payload[2])
    if kind == "division":
        return _show_division(canvas, payload[1], payload[2])
    if kind == "addsub":
        return _show_addsub(canvas, *payload[1:])
    return 0


def _size(canvas):
    return int(canvas.cget("width")), int(canvas.cget("height"))


def _show_multiplication(canvas, a, b):
    # a こずつ が b つぶん（「1つ分の数 × いくつ分」）。1れつ ずつ ふやす。
    w, h = _size(canvas)
    unit = 1.0
    label_units = 2.5
    pitch = min(w * 0.92 / (_span(a, unit) + label_units), (h - CAPTION_H) / (b + 0.4), MAX_PITCH)
    board = _Board(canvas, pitch)
    grid_w = _span(a, pitch)
    x0 = (w - grid_w - label_units * pitch) / 2
    y0 = (h - CAPTION_H - b * pitch) / 2 + board.depth

    t = 0
    for r in range(b):
        color = ROW_COLORS[r % len(ROW_COLORS)]
        y = y0 + r * pitch
        for i in range(a):
            board.later(t + i * 45, lambda i=i, y=y, color=color, r=r:
                        board.cube(x0 + _offset(i, pitch), y, color, f"m{r}_{i}"))
        board.later(t + a * 45, lambda r=r, y=y: board.label(
            x0 + grid_w + pitch * 0.5, y + board.size / 2, f"{a * (r + 1)}", COUNT_TEXT))
        t += max(a * 45 + 200, 500)

    board.later(t, lambda: board.caption(f"{a}こずつ が {b}つぶん  →  {a * b}こ"))
    return t


def _show_division(canvas, divisor, quotient):
    # N こを divisor こずつ とりだして、1れつに ならべていく（「わり算 = いくつ分」）。
    n = divisor * quotient
    w, h = _size(canvas)
    pile_rows = (n + 9) // 10
    unit = 1.0
    pile_units = _span(min(n, 10), unit)
    gap_units = 1.5
    grid_units = _span(divisor, unit)
    label_units = 2.5
    rows = max(pile_rows, quotient)
    pitch = min(
        w * 0.94 / (pile_units + gap_units + grid_units + label_units),
        (h - CAPTION_H) / (rows + 0.4),
        MAX_PITCH,
    )
    board = _Board(canvas, pitch)
    total_w = (pile_units + gap_units + grid_units + label_units) * pitch
    pile_x = (w - total_w) / 2
    grid_x = pile_x + (pile_units + gap_units) * pitch
    y0 = (h - CAPTION_H - rows * pitch) / 2 + board.depth

    def pile_pos(i):
        return pile_x + _offset(i % 10, pitch), y0 + (i // 10) * pitch

    for i in range(n):
        x, y = pile_pos(i)
        board.cube(x, y, PILE_COLOR, f"d{i}")
    board.label(grid_x - gap_units * pitch / 2, y0 + board.size / 2, "→", SUB_TEXT, anchor="center")
    caption = board.caption(f"{n}こを {divisor}こずつ わけよう")

    frames, frame_ms = 8, 35
    t = 700
    for g in range(quotient):
        color = ROW_COLORS[g % len(ROW_COLORS)]
        # 山の うしろから divisor こ とりだして、g ばんめの れつへ うごかす。
        moves = []
        for k in range(divisor):
            idx = n - (g + 1) * divisor + k
            sx, sy = pile_pos(idx)
            tx, ty = grid_x + _offset(k, pitch), y0 + g * pitch
            moves.append((f"d{idx}", (tx - sx) / frames, (ty - sy) / frames))

        def pick(moves=moves, color=color):
            for tag, _, _ in moves:
                board.recolor(tag, color)
                canvas.tag_raise(tag)

        board.later(t, pick)
        for f in range(1, frames + 1):
            board.later(t + 150 + f * frame_ms,
                        lambda moves=moves: [canvas.move(tag, dx, dy) for tag, dx, dy in moves])
        t += 150 + frames * frame_ms
        board.later(t, lambda g=g: board.label(
            grid_x + grid_units * pitch + pitch * 0.5, y0 + g * pitch + board.size / 2,
            f"{g + 1}つ", COUNT_TEXT))
        t += 250

    board.later(t, lambda: board.caption(
        f"{n}こを {divisor}こずつ わけると {quotient}つぶん", caption))
    return t


def _show_addsub(canvas, a, op1, b, op2, c):
    # 1ぎょうめ: a こ。2・3ぎょうめ: まえの ぎょうから ふえる（新しい色）・へる（×）。
    steps = [("", a), (op1, b), (op2, c)]
    counts, lengths = [], []
    count = 0
    for op, value in steps:
        before = count
        count = count - value if op == "-" else count + value
        counts.append(count)
        lengths.append(before if op == "-" else count)

    w, h = _size(canvas)
    unit = 1.0
    left_units, right_units = 3.0, 3.0
    row_units = 1.25
    pitch = min(
        w * 0.94 / (left_units + _span(max(lengths), unit) + right_units),
        (h - CAPTION_H) / (row_units * 3 + 0.2),
        MAX_PITCH,
    )
    board = _Board(canvas, pitch)
    total_w = (left_units + right_units) * pitch + _span(max(lengths), pitch)
    x0 = (w - total_w) / 2 + left_units * pitch
    y0 = (h - CAPTION_H - row_units * 3 * pitch) / 2 + board.depth + pitch * 0.1
    signs = {"+": "＋", "-": "−"}

    colors = []  # いま ある ブロックの 色（どこから きたか 分かるように 色を のこす）
    t = 0
    for row, (op, value) in enumerate(steps):
        y = y0 + row * row_units * pitch
        mid = y + board.size / 2
        text = f"{value}" if not op else f"{signs[op]} {value}"
        label_color = TEXT if not op else (MINUS_COLOR if op == "-" else ADD_COLORS[row - 1])
        board.later(t, lambda text=text, mid=mid, label_color=label_color: board.label(
            x0 - pitch * 0.6, mid, text, label_color, anchor="e"))

        # まえの ぎょうの ブロックを そのまま うつす。
        existing = list(colors)
        board.later(t, lambda existing=existing, y=y, row=row: [
            board.cube(x0 + _offset(i, pitch), y, col, f"s{row}_{i}")
            for i, col in enumerate(existing)])
        t += 300 if existing else 0

        if op == "-":
            for k in range(value):
                i = len(colors) - 1 - k
                board.later(t + k * 150, lambda i=i, y=y, row=row: board.ghost(
                    x0 + _offset(i, pitch), y, f"s{row}_{i}"))
            t += value * 150
            del colors[len(colors) - value:]
        else:
            color = START_COLOR if not op else ADD_COLORS[row - 1]
            start = len(colors)
            for k in range(value):
                i = start + k
                board.later(t + k * 70, lambda i=i, y=y, row=row, color=color: board.cube(
                    x0 + _offset(i, pitch), y, color, f"s{row}_{i}"))
            t += value * 70
            colors.extend([color] * value)

        right_x = x0 + _span(lengths[row], pitch) + pitch * 0.6
        board.later(t, lambda right_x=right_x, mid=mid, n=counts[row]: board.label(
            right_x, mid, f"{n}こ", COUNT_TEXT))
        t += 600

    result = counts[-1]
    board.later(t, lambda: board.caption(
        f"{a} {signs[op1]} {b} {signs[op2]} {c} ＝ {result}"))
    return t
