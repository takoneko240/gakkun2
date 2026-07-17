import tkinter as tk
import tkinter.font as tkfont

from . import celebration, ime_control, keyboard_block, music

CATEGORY_LABELS = {
    "multiplication": "掛け算",
    "division": "割り算",
    "kanji": "漢字",
}

CELEBRATE_COLORS = ["#34D399", "#FBBF24", "#60A5FA", "#F472B6"]


def show_quiz(
    root, question, on_result, monitor_geometry=None, music_folder=None,
    idle_music_minutes=10, total_yen=0, allowance_per_correct=0,
):
    win = tk.Toplevel(root)
    win.overrideredirect(True)
    win.attributes("-topmost", True)
    win.configure(bg="#111827")

    if monitor_geometry:
        left, top = monitor_geometry["left"], monitor_geometry["top"]
        screen_w, screen_h = monitor_geometry["width"], monitor_geometry["height"]
    else:
        left, top = 0, 0
        screen_w, screen_h = win.winfo_screenwidth(), win.winfo_screenheight()
    win.geometry(f"{screen_w}x{screen_h}+{left}+{top}")

    win.protocol("WM_DELETE_WINDOW", lambda: None)
    win.bind("<Escape>", lambda e: "break")
    win.bind("<Alt-F4>", lambda e: "break")

    keyboard_block.set_blocking(True)

    money_font = tkfont.Font(family="Meiryo", size=24, weight="bold")
    category_font = tkfont.Font(family="Meiryo", size=22)
    prompt_font = tkfont.Font(family="Meiryo", size=48, weight="bold")
    entry_font = tkfont.Font(family="Meiryo", size=32)
    status_font = tkfont.Font(family="Meiryo", size=26)

    confetti_canvas = tk.Canvas(win, width=screen_w, height=screen_h, bg="#111827", highlightthickness=0)
    confetti_canvas.place(x=0, y=0)

    money_var = tk.StringVar(value=f"獲得金額: {total_yen}円")
    tk.Label(
        win, textvariable=money_var, font=money_font, fg="#FBBF24", bg="#111827"
    ).place(relx=0.5, y=30, anchor="n")

    container = tk.Frame(win, bg="#111827")
    container.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(
        container,
        text=CATEGORY_LABELS.get(question.kind, ""),
        font=category_font,
        fg="#9CA3AF",
        bg="#111827",
    ).pack(pady=(0, 12))

    tk.Label(
        container,
        text=question.prompt,
        font=prompt_font,
        fg="#F9FAFB",
        bg="#111827",
        wraplength=int(screen_w * 0.8),
        justify="center",
    ).pack(pady=(0, 24))

    entry_var = tk.StringVar()
    entry = tk.Entry(
        container,
        textvariable=entry_var,
        font=entry_font,
        justify="center",
        width=12,
    )
    entry.pack(pady=(0, 16))

    status_label = tk.Label(
        container, text="", font=status_font, bg="#111827"
    )
    status_label.pack()

    music_job = None

    def stop_idle_music():
        nonlocal music_job
        if music_job is not None:
            try:
                win.after_cancel(music_job)
            except Exception:
                pass
            music_job = None
        music.stop()

    def play_idle_music():
        # idle_music_minutes放置したら1回だけ再生する。曲が終わっても、
        # この問題が未回答のままでも、この問題に対しては再度再生しない
        # (次に別の出題画面が表示され、そこでまた idle_music_minutes
        # 放置されたら、そちらで新たに1回再生される)。
        if music_folder:
            music.play_random(music_folder)

    def pulse_status(remaining):
        if remaining <= 0 or not win.winfo_exists():
            return
        status_label.configure(fg=CELEBRATE_COLORS[remaining % len(CELEBRATE_COLORS)])
        win.after(150, lambda: pulse_status(remaining - 1))

    def close_and_report(correct):
        keyboard_block.set_blocking(False)
        stop_idle_music()
        entry.unbind("<FocusIn>")
        try:
            win.after_cancel(ime_job)
        except Exception:
            pass
        win.destroy()
        on_result(correct, question)

    def submit(event=None):
        if entry.cget("state") == "disabled":
            return

        stop_idle_music()

        answer = entry_var.get()
        correct = question.is_correct(answer)
        entry.configure(state="disabled")

        if correct:
            celebrate_font = tkfont.Font(family="Meiryo", size=44, weight="bold")
            status_label.configure(text="🎉 正解！ 🎉", font=celebrate_font, fg=CELEBRATE_COLORS[0])
            money_var.set(f"獲得金額: {total_yen + allowance_per_correct}円")
            celebration.play_chime()
            celebration.burst_confetti(confetti_canvas, screen_w, screen_h, duration_ms=2800)
            pulse_status(18)
            win.after(3000, lambda: close_and_report(True))
        else:
            status_label.configure(
                text=f"不正解… 正解は「{question.answer}」", fg="#F87171"
            )
            win.after(2000, lambda: close_and_report(False))

    japanese_ime = question.kind == "kanji"

    def apply_ime_mode(event=None):
        ime_control.set_mode(entry.winfo_id(), japanese_ime)

    entry.bind("<Return>", submit)
    entry.bind("<FocusIn>", apply_ime_mode)
    win.lift()
    win.focus_force()
    entry.focus_set()
    ime_job = win.after(50, apply_ime_mode)
    music_job = win.after(int(idle_music_minutes * 60 * 1000), play_idle_music)

    return win
