import threading

import pystray
from PIL import Image, ImageDraw, ImageFont


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

    def handle_exit(icon, item):
        icon.stop()
        root.after(0, on_exit)

    menu = pystray.Menu(
        pystray.MenuItem("今すぐ出題（テスト）", handle_force_quiz),
        pystray.MenuItem("終了", handle_exit),
    )

    icon = pystray.Icon("gakkun2", _build_icon_image(), "がっくん2", menu)

    if hasattr(icon, "run_detached"):
        icon.run_detached()
    else:
        threading.Thread(target=icon.run, daemon=True).start()

    return icon
