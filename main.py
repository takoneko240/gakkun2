import argparse
import os
import traceback
import tkinter as tk

from quiz_app import config as config_module
from quiz_app import excel_data, keyboard_block, monitors, tray
from quiz_app.scheduler import Scheduler


def _report_callback_exception(exc, val, tb):
    # Tkinter/Tcl can fire a widget's pending after() callback just after that
    # widget destroys itself (e.g. IME-related internal timers on Windows),
    # which crashes tkinter's own cleanup with this benign AttributeError.
    if isinstance(val, AttributeError) and "_tclCommands" in str(val):
        return
    traceback.print_exception(exc, val, tb)


def parse_args():
    parser = argparse.ArgumentParser(description="gakkun2 - 学習強制出題アプリ")
    parser.add_argument(
        "--monitor", type=int, default=None,
        help="出題ウィンドウを表示するモニタ番号(1始まり)。省略時はプライマリモニタ。",
    )
    parser.add_argument(
        "--list-monitors", action="store_true",
        help="検出されたモニタの一覧を表示して終了する。",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.list_monitors:
        for i, m in enumerate(monitors.list_monitors(), start=1):
            tag = " (primary)" if m["primary"] else ""
            print(f"{i}: {m['width']}x{m['height']} at ({m['left']},{m['top']}){tag}")
        return

    config = config_module.load_config()
    excel_path = config_module.resolve_path(config["excel_path"])
    excel_data.ensure_sample_file(excel_path)
    scores_path = config_module.resolve_path("scores.json")
    monitor_geometry = monitors.resolve_monitor_geometry(args.monitor)
    music_folder = config_module.resolve_path(config["music_folder"])
    os.makedirs(music_folder, exist_ok=True)

    root = tk.Tk()
    root.withdraw()
    root.report_callback_exception = _report_callback_exception

    keyboard_block.install()

    scheduler = Scheduler(root, config, excel_path, scores_path, monitor_geometry, music_folder)

    def on_exit():
        keyboard_block.uninstall()
        root.quit()

    tray.start_tray(root, scheduler, on_exit)

    scheduler.start()
    root.mainloop()


if __name__ == "__main__":
    main()
