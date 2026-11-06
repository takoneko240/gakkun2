"""Windows 標準の音声合成（SAPI）で文章を読み上げる。"""
from .applog import logger

_voice = None

# SpeechVoiceSpeakFlags
_SVSF_ASYNC = 1
_SVSF_PURGE_BEFORE_SPEAK = 2
# SpeechRunState
_SRSE_DONE = 1

_DIGITS = ["", "いち", "に", "さん", "よん", "ご", "ろく", "なな", "はち", "きゅう"]


def number_to_hiragana(n):
    """0〜999 の数をひらがなの読みにする（九九の読み上げ用）。"""
    if n == 0:
        return "ぜろ"
    hundreds, rest = divmod(n, 100)
    tens, ones = divmod(rest, 10)
    parts = []
    if hundreds:
        parts.append({1: "ひゃく", 3: "さんびゃく", 6: "ろっぴゃく", 8: "はっぴゃく"}.get(
            hundreds, _DIGITS[hundreds] + "ひゃく"))
    if tens:
        parts.append(("" if tens == 1 else _DIGITS[tens]) + "じゅう")
    if ones:
        parts.append(_DIGITS[ones])
    return "".join(parts)


def multiplication_reading(a, b):
    return f"{number_to_hiragana(a)}　かける　{number_to_hiragana(b)}　は　{number_to_hiragana(a * b)}"


def _get_voice():
    global _voice
    if _voice is None:
        import win32com.client

        _voice = win32com.client.Dispatch("SAPI.SpVoice")
        for token in _voice.GetVoices():
            if "Japanese" in token.GetDescription() or "日本語" in token.GetDescription():
                _voice.Voice = token
                break
        _voice.Rate = -2  # 少しゆっくり
    return _voice


def speak(text, widget=None, on_done=None):
    """text を非同期で読み上げる。widget を渡すと、読み終わったら on_done を呼ぶ。

    読み上げに失敗しても出題は続けられるよう、例外はログに残して on_done を呼ぶ。
    """
    try:
        _get_voice().Speak(text, _SVSF_ASYNC | _SVSF_PURGE_BEFORE_SPEAK)
    except Exception:
        logger.exception("読み上げに失敗しました: %s", text)
        if on_done:
            on_done()
        return

    if widget is None or on_done is None:
        return

    def poll():
        try:
            done = _voice.Status.RunningState == _SRSE_DONE
        except Exception:
            done = True
        if done:
            on_done()
        elif widget.winfo_exists():
            widget.after(100, poll)

    widget.after(100, poll)
