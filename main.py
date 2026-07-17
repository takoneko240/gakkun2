import tkinter as tk

from quiz_app import config as config_module
from quiz_app import excel_data, keyboard_block, tray
from quiz_app.scheduler import Scheduler


def main():
    config = config_module.load_config()
    excel_path = config_module.resolve_path(config["excel_path"])
    excel_data.ensure_sample_file(excel_path)
    scores_path = config_module.resolve_path("scores.json")

    root = tk.Tk()
    root.withdraw()

    keyboard_block.install()

    scheduler = Scheduler(root, config, excel_path, scores_path)

    def on_exit():
        keyboard_block.uninstall()
        root.quit()

    tray.start_tray(root, scheduler, on_exit)

    scheduler.start()
    root.mainloop()


if __name__ == "__main__":
    main()
