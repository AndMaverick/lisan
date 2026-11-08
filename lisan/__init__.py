"""lisan: Arabic text normalization for search, matching, and model input. Dependency-free."""

from __future__ import annotations

import re

__version__ = "0.1.0"

_DIACRITICS = {chr(c) for c in range(0x064B, 0x0656)} | {"ٰ"}
_TATWEEL = "ـ"
_ALEF_VARIANTS = {"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا"}
_DIGITS = {**{chr(0x0660 + i): str(i) for i in range(10)}, **{chr(0x06F0 + i): str(i) for i in range(10)}}


def is_arabic_letter(ch: str) -> bool:
    code = ord(ch)
    return (0x0621 <= code <= 0x064A) or (0x0671 <= code <= 0x06D3) or code in (0x06FA, 0x06FB, 0x06FC)


def normalize(text: str, *, ta_marbuta: bool = False) -> str:
    """Strip diacritics and tatweel, unify alef and yeh, and convert Eastern digits to ASCII.

    ta_marbuta=True also folds the final teh marbuta into heh, which helps loose matching.
    """
    out = []
    for ch in text:
        if ch in _DIACRITICS or ch == _TATWEEL:
            continue
        ch = _ALEF_VARIANTS.get(ch, ch)
        ch = _DIGITS.get(ch, ch)
        if ch == "ى":
            ch = "ي"
        if ta_marbuta and ch == "ة":
            ch = "ه"
        out.append(ch)
    return "".join(out)


def arabic_ratio(text: str) -> float:
    """Share of letters that are Arabic. Useful for routing mixed-language input."""
    letters = [c for c in text if c.isalpha()]
    return sum(is_arabic_letter(c) for c in letters) / len(letters) if letters else 0.0


def tokens(text: str) -> list:
    return re.findall(r"[^\W_]+", normalize(text), flags=re.UNICODE)


def search_key(text: str) -> str:
    """A canonical key: normalized, lowercased Latin, single-spaced."""
    return " ".join(normalize(text, ta_marbuta=True).lower().split())
