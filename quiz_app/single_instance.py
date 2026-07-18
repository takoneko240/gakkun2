import ctypes

MUTEX_NAME = "Gakkun2SingleInstanceMutex"
ERROR_ALREADY_EXISTS = 183

kernel32 = ctypes.windll.kernel32
kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, ctypes.c_bool, ctypes.c_wchar_p]
kernel32.CreateMutexW.restype = ctypes.c_void_p
kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
kernel32.CloseHandle.restype = ctypes.c_bool
kernel32.GetLastError.restype = ctypes.c_uint32

_mutex_handle = None


def acquire():
    """既に起動していなければTrue、既に起動していればFalseを返す。"""
    global _mutex_handle
    _mutex_handle = kernel32.CreateMutexW(None, False, MUTEX_NAME)
    return kernel32.GetLastError() != ERROR_ALREADY_EXISTS


def release():
    global _mutex_handle
    if _mutex_handle:
        kernel32.CloseHandle(_mutex_handle)
        _mutex_handle = None
