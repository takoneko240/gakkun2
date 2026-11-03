import ctypes
import glob
import os
import random
import tempfile

from .applog import logger

winmm = ctypes.windll.winmm
winmm.mciSendStringW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint, ctypes.c_void_p]
winmm.mciSendStringW.restype = ctypes.c_uint32

_ALIAS = "gakkun2music"

# 誤答時の待ち時間に流す曲。放置時のランダム再生には含めない。
WAIT_FILE_NAME = "wait.mp3"


def _mci(command):
    return winmm.mciSendStringW(command, None, 0, None)


def is_playing():
    buf = ctypes.create_unicode_buffer(32)
    winmm.mciSendStringW(f"status {_ALIAS} mode", buf, 32, None)
    return buf.value.strip().lower() == "playing"


def list_mp3_files(folder):
    if not os.path.isdir(folder):
        return []
    return [
        path for path in glob.glob(os.path.join(folder, "*.mp3"))
        if os.path.basename(path).lower() != WAIT_FILE_NAME
    ]


def play_random(folder):
    files = list_mp3_files(folder)
    if not files:
        return False
    return play_file(random.choice(files))


def play_wait(folder):
    path = os.path.join(folder, WAIT_FILE_NAME)
    if not os.path.isfile(path):
        logger.warning("待ち時間の曲がありません: %s", path)
        return False
    return play_file(path)


def play_file(path):
    stop()
    open_result = _mci(f'open "{path}" type mpegvideo alias {_ALIAS}')
    if open_result != 0:
        # ID3v2.4 タグ付きの MP3 は MCI で開けないことがあるので、
        # タグを取り除いた一時コピーで再試行する（元ファイルは変更しない）。
        stripped = _without_id3v2(path)
        if stripped:
            open_result = _mci(f'open "{stripped}" type mpegvideo alias {_ALIAS}')
    if open_result != 0:
        logger.warning("音楽ファイルを開けませんでした: %s (MCIエラー=%s)", path, open_result)
        return False
    play_result = _mci(f"play {_ALIAS}")
    if play_result != 0:
        logger.warning("音楽の再生に失敗しました: %s (MCIエラー=%s)", path, play_result)
        return False
    return True


def _without_id3v2(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        return None
    if data[:3] != b"ID3" or len(data) < 10:
        return None
    size = 0
    for byte in data[6:10]:
        size = (size << 7) | (byte & 0x7F)
    size += 10
    if data[5] & 0x10:  # フッターあり
        size += 10
    out_path = os.path.join(
        tempfile.gettempdir(), "gakkun2_" + os.path.basename(path),
    )
    try:
        with open(out_path, "wb") as f:
            f.write(data[size:])
    except OSError:
        return None
    return out_path


def stop():
    _mci(f"stop {_ALIAS}")
    _mci(f"close {_ALIAS}")
