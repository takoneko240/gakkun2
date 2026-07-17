import ctypes
from ctypes import wintypes

WH_KEYBOARD_LL = 13
HC_ACTION = 0
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104

VK_TAB = 0x09
VK_ESCAPE = 0x1B
VK_F4 = 0x73
VK_LWIN = 0x5B
VK_RWIN = 0x5C

user32 = ctypes.windll.user32

blocking_enabled = False

_BLOCKED_VKS = {VK_TAB, VK_ESCAPE, VK_F4, VK_LWIN, VK_RWIN}


class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG)),
    ]


LOW_LEVEL_KEYBOARD_PROC = ctypes.WINFUNCTYPE(
    ctypes.c_long, ctypes.c_int, wintypes.WPARAM, ctypes.POINTER(KBDLLHOOKSTRUCT)
)

_hook_handle = None
_hook_proc_ref = None


def _low_level_keyboard_handler(nCode, wParam, lParam):
    if nCode == HC_ACTION and blocking_enabled:
        vk_code = lParam.contents.vkCode
        if wParam in (WM_KEYDOWN, WM_SYSKEYDOWN) and vk_code in _BLOCKED_VKS:
            return 1

    return user32.CallNextHookEx(_hook_handle, nCode, wParam, lParam)


def install():
    global _hook_handle, _hook_proc_ref
    if _hook_handle is not None:
        return

    _hook_proc_ref = LOW_LEVEL_KEYBOARD_PROC(_low_level_keyboard_handler)
    _hook_handle = user32.SetWindowsHookExW(WH_KEYBOARD_LL, _hook_proc_ref, None, 0)


def uninstall():
    global _hook_handle
    if _hook_handle is not None:
        user32.UnhookWindowsHookEx(_hook_handle)
        _hook_handle = None


def set_blocking(enabled):
    global blocking_enabled
    blocking_enabled = enabled
