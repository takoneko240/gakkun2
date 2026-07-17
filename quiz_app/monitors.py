import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32

MONITORINFOF_PRIMARY = 0x1


class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", wintypes.RECT),
        ("rcWork", wintypes.RECT),
        ("dwFlags", wintypes.DWORD),
    ]


MonitorEnumProc = ctypes.WINFUNCTYPE(
    ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(wintypes.RECT), ctypes.c_void_p
)

user32.EnumDisplayMonitors.argtypes = [ctypes.c_void_p, ctypes.c_void_p, MonitorEnumProc, ctypes.c_void_p]
user32.EnumDisplayMonitors.restype = wintypes.BOOL
user32.GetMonitorInfoW.argtypes = [ctypes.c_void_p, ctypes.POINTER(MONITORINFO)]
user32.GetMonitorInfoW.restype = wintypes.BOOL


def list_monitors():
    monitors = []

    def _callback(hmonitor, hdc, rect, data):
        info = MONITORINFO()
        info.cbSize = ctypes.sizeof(MONITORINFO)
        user32.GetMonitorInfoW(hmonitor, ctypes.byref(info))
        r = info.rcMonitor
        monitors.append(
            {
                "left": r.left,
                "top": r.top,
                "width": r.right - r.left,
                "height": r.bottom - r.top,
                "primary": bool(info.dwFlags & MONITORINFOF_PRIMARY),
            }
        )
        return 1

    user32.EnumDisplayMonitors(None, None, MonitorEnumProc(_callback), None)
    return monitors


def resolve_monitor_geometry(monitor_number):
    """monitor_numberは1始まり。未指定/範囲外はプライマリモニタにフォールバックする。"""
    monitors = list_monitors()
    if not monitors:
        return None

    if monitor_number is not None:
        index = monitor_number - 1
        if 0 <= index < len(monitors):
            return monitors[index]
        print(
            f"警告: モニタ番号 {monitor_number} は存在しません"
            f"（検出数: {len(monitors)}）。プライマリモニタを使用します。"
        )

    for m in monitors:
        if m["primary"]:
            return m
    return monitors[0]
