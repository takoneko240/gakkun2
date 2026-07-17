import os
import sys

import win32com.client

APP_NAME = "Gakkun2"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXE_PATH = os.path.join(BASE_DIR, "dist", "Gakkun2.exe")
MAIN_SCRIPT = os.path.join(BASE_DIR, "main.py")


def startup_folder():
    return os.path.join(
        os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup"
    )


def shortcut_path():
    return os.path.join(startup_folder(), f"{APP_NAME}.lnk")


def install():
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(shortcut_path())

    if os.path.exists(EXE_PATH):
        shortcut.TargetPath = EXE_PATH
        shortcut.WorkingDirectory = os.path.dirname(EXE_PATH)
    else:
        pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
        if not os.path.exists(pythonw):
            pythonw = sys.executable
        shortcut.TargetPath = pythonw
        shortcut.Arguments = f'"{MAIN_SCRIPT}"'
        shortcut.WorkingDirectory = BASE_DIR

    shortcut.IconLocation = shortcut.TargetPath
    shortcut.Save()
    print(f"スタートアップに登録しました: {shortcut_path()} -> {shortcut.TargetPath}")


def uninstall():
    path = shortcut_path()
    if os.path.exists(path):
        os.remove(path)
        print(f"スタートアップから削除しました: {path}")
    else:
        print("スタートアップ登録は見つかりませんでした。")


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "install"
    if action == "uninstall":
        uninstall()
    else:
        install()
