import threading
from tkinter import messagebox, simpledialog

import pystray
from PIL import Image, ImageDraw, ImageFont

EXIT_PASSWORD = "0asgW8nu"


def _build_icon_image():
    size = 64
    image = Image.new("RGBA", (size, size), (17, 24, 39, 255))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("meiryo.ttc", 40)
    except OSError:
        font = ImageFont.load_default()
    text = "字"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        ((size - text_w) / 2 - bbox[0], (size - text_h) / 2 - bbox[1]),
        text,
        font=font,
        fill=(249, 250, 251, 255),
    )
    return image


def start_tray(root, scheduler, on_exit):
    def handle_force_quiz(icon, item):
        root.after(0, scheduler.force_quiz_now)

    def prompt_password(icon):
        password = simpledialog.askstring(
            "終了確認", "終了パスワードを入力してください:", show="*", parent=root,
        )
        if password is None:
            return
        if password == EXIT_PASSWORD:
            icon.stop()
            on_exit()
        else:
            messagebox.showerror("終了確認", "パスワードが違います。", parent=root)

    def confirm_withdraw():
        total_yen = scheduler.total_yen
        if total_yen <= 0:
            messagebox.showinfo("出金", "出金できる金額はありません。", parent=root)
            return
        if messagebox.askyesno(
            "出金", f"獲得金額 {total_yen}円 を出金して、0円に戻しますか？", parent=root,
        ):
            scheduler.withdraw()
            messagebox.showinfo("出金", f"{total_yen}円 を出金しました。", parent=root)

    def handle_withdraw(icon, item):
        root.after(0, confirm_withdraw)

    def handle_exit(icon, item):
        root.after(0, prompt_password, icon)

    menu = pystray.Menu(
        pystray.MenuItem("今すぐ出題（テスト）", handle_force_quiz),
        pystray.MenuItem("出金", handle_withdraw),
        pystray.MenuItem("終了", handle_exit),
    )

    icon = pystray.Icon("gakkun2", _build_icon_image(), "がっくん2", menu)

    if hasattr(icon, "run_detached"):
        icon.run_detached()
    else:
        threading.Thread(target=icon.run, daemon=True).start()

    return icon
