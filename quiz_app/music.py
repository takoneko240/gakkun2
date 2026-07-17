import ctypes
import glob
import os
import random

winmm = ctypes.windll.winmm
winmm.mciSendStringW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint, ctypes.c_void_p]
winmm.mciSendStringW.restype = ctypes.c_uint32

_ALIAS = "gakkun2music"


def _mci(command):
    return winmm.mciSendStringW(command, None, 0, None)


def is_playing():
    buf = ctypes.create_unicode_buffer(32)
    winmm.mciSendStringW(f"status {_ALIAS} mode", buf, 32, None)
    return buf.value.strip().lower() == "playing"


def list_mp3_files(folder):
    if not os.path.isdir(folder):
        return []
    return glob.glob(os.path.join(folder, "*.mp3"))


def play_random(folder):
    files = list_mp3_files(folder)
    if not files:
        return False

    stop()

    path = random.choice(files)
    if _mci(f'open "{path}" type mpegvideo alias {_ALIAS}') != 0:
        return False
    _mci(f"play {_ALIAS}")
    return True


def stop():
    _mci(f"stop {_ALIAS}")
    _mci(f"close {_ALIAS}")
