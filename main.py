import argparse
import os
import sys
import tkinter as tk

from quiz_app import config as config_module
from quiz_app import excel_data, monitors, single_instance, tray
from quiz_app.applog import logger
from quiz_app.scheduler import Scheduler


def _report_callback_exception(exc, val, tb):
    # Tkinter/Tcl can fire a widget's pending after() callback just after that
    # widget destroys itself (e.g. IME-related internal timers on Windows),
    # which crashes tkinter's own cleanup with this benign AttributeError.
    if isinstance(val, AttributeError) and "_tclCommands" in str(val):
        return
    logger.error("Tkinterコールバック内で例外が発生しました", exc_info=(exc, val, tb))


def _excepthook(exc_type, exc_value, exc_tb):
    logger.error("未処理の例外でプロセスが終了します", exc_info=(exc_type, exc_value, exc_tb))
    sys.__excepthook__(exc_type, exc_value, exc_tb)


sys.excepthook = _excepthook


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

    if not single_instance.acquire():
        # 既に起動中。タスクスケジューラでの定期再起動などから呼ばれても
        # ダイアログで止まらないよう、何も表示せず黙って終了する。
        logger.info("既に起動中のインスタンスがあるため終了します")
        return

    logger.info("gakkun2 起動")

    config = config_module.load_config()
    excel_path = config_module.resolve_path(config["excel_path"])
    excel_data.ensure_sample_file(excel_path)
    scores_path = config_module.resolve_path("scores.json")
    monitor_geometry = monitors.resolve_monitor_geometry(args.monitor)
    music_folder = config_module.resolve_path(config["music_folder"])
    os.makedirs(music_folder, exist_ok=True)
    allowance_path = config_module.resolve_path("allowance.json")

    root = tk.Tk()
    root.withdraw()
    root.report_callback_exception = _report_callback_exception

    scheduler = Scheduler(
        root, config, excel_path, scores_path, monitor_geometry, music_folder, allowance_path,
    )

    def on_exit():
        logger.info("終了メニューから終了します")
        single_instance.release()
        root.quit()

    tray.start_tray(root, scheduler, on_exit)

    scheduler.start()
    root.mainloop()

    logger.info("gakkun2 終了 (mainloopが終了しました)")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("main()の実行中に例外が発生し、プロセスが終了します")
        raise
