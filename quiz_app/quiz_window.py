import tkinter as tk
import tkinter.font as tkfont

from . import ime_control, keyboard_block

CATEGORY_LABELS = {
    "multiplication": "掛け算",
    "division": "割り算",
    "kanji": "漢字",
}


def show_quiz(root, question, on_result):
    win = tk.Toplevel(root)
    win.overrideredirect(True)
    win.attributes("-topmost", True)
    win.configure(bg="#111827")

    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    win.geometry(f"{screen_w}x{screen_h}+0+0")

    win.protocol("WM_DELETE_WINDOW", lambda: None)
    win.bind("<Escape>", lambda e: "break")
    win.bind("<Alt-F4>", lambda e: "break")

    keyboard_block.set_blocking(True)

    category_font = tkfont.Font(family="Meiryo", size=22)
    prompt_font = tkfont.Font(family="Meiryo", size=48, weight="bold")
    entry_font = tkfont.Font(family="Meiryo", size=32)
    status_font = tkfont.Font(family="Meiryo", size=26)

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

    def close_and_report(correct):
        keyboard_block.set_blocking(False)
        win.destroy()
        on_result(correct, question)

    def submit(event=None):
        if entry.cget("state") == "disabled":
            return

        answer = entry_var.get()
        correct = question.is_correct(answer)
        entry.configure(state="disabled")

        if correct:
            status_label.configure(text="正解！", fg="#34D399")
            win.after(750, lambda: close_and_report(True))
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
    win.after(50, apply_ime_mode)

    return win
