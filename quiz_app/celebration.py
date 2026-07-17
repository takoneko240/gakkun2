import random
import winsound

from . import config

CONFETTI_COLORS = ["#FBBF24", "#FCD34D", "#F59E0B"]  # コインを模した金〜黄色

FRAME_MS = 30

SUCCESS_SOUND_PATH = config.resolve_path("wav/charin.wav")


def play_chime():
    winsound.PlaySound(
        SUCCESS_SOUND_PATH,
        winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT,
    )


def burst_confetti(canvas, width, height, count=90, duration_ms=1400):
    particles = []
    for _ in range(count):
        x = random.uniform(0, width)
        y = random.uniform(-height * 0.4, 0)
        size = random.uniform(6, 13) * 1.5
        color = random.choice(CONFETTI_COLORS)
        item = canvas.create_oval(x, y, x + size, y + size, fill=color, outline="")
        vx = random.uniform(-2.5, 2.5)
        vy = random.uniform(4, 10) * 2.0
        particles.append([item, vx, vy])

    remaining_steps = max(1, duration_ms // FRAME_MS)

    def step(remaining):
        if remaining <= 0 or not canvas.winfo_exists():
            return
        for item, vx, vy in particles:
            canvas.move(item, vx, vy)
        canvas.after(FRAME_MS, lambda: step(remaining - 1))

    step(remaining_steps)
