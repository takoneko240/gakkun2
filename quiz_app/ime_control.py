import ctypes

imm32 = ctypes.windll.imm32
imm32.ImmGetContext.restype = ctypes.c_void_p
imm32.ImmGetContext.argtypes = [ctypes.c_void_p]
imm32.ImmReleaseContext.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
imm32.ImmSetOpenStatus.argtypes = [ctypes.c_void_p, ctypes.c_bool]
imm32.ImmSetConversionStatus.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_ulong]

IME_CMODE_NATIVE = 0x1
IME_SMODE_NONE = 0x0


def set_mode(hwnd, japanese):
    himc = imm32.ImmGetContext(hwnd)
    if not himc:
        return

    try:
        if japanese:
            imm32.ImmSetOpenStatus(himc, True)
            imm32.ImmSetConversionStatus(himc, IME_CMODE_NATIVE, IME_SMODE_NONE)
        else:
            imm32.ImmSetOpenStatus(himc, False)
    finally:
        imm32.ImmReleaseContext(hwnd, himc)
