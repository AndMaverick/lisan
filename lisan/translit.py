"""Buckwalter transliteration: a one-to-one mapping between Arabic letters and ASCII, so Arabic can be logged, diffed and typed
anywhere, and read back without loss. This is the standard table used by the Penn Arabic Treebank and many corpora."""
from __future__ import annotations

BUCKWALTER = {
    "ء": "'", "آ": "|", "أ": ">", "ؤ": "&", "إ": "<", "ئ": "}", "ا": "A", "ب": "b",
    "ة": "p", "ت": "t", "ث": "v", "ج": "j", "ح": "H", "خ": "x", "د": "d", "ذ": "*",
    "ر": "r", "ز": "z", "س": "s", "ش": "$", "ص": "S", "ض": "D", "ط": "T", "ظ": "Z",
    "ع": "E", "غ": "g", "ـ": "_", "ف": "f", "ق": "q", "ك": "k", "ل": "l", "م": "m",
    "ن": "n", "ه": "h", "و": "w", "ى": "Y", "ي": "y", "ً": "F", "ٌ": "N", "ٍ": "K",
    "َ": "a", "ُ": "u", "ِ": "i", "ّ": "~", "ْ": "o", "ٰ": "`", "ٱ": "{",
}
ARABIC = {v: k for k, v in BUCKWALTER.items()}


def to_buckwalter(text: str) -> str:
    """Arabic to Buckwalter. Characters outside the table (Latin, digits, spaces, punctuation) pass through unchanged."""
    return "".join(BUCKWALTER.get(ch, ch) for ch in text)


def from_buckwalter(text: str) -> str:
    """Buckwalter to Arabic. Only safe on text that is wholly Buckwalter: ASCII letters that are also Buckwalter symbols become
    Arabic letters, so mixed Latin-and-Arabic text does not round-trip (use ``to_buckwalter`` for that direction)."""
    return "".join(ARABIC.get(ch, ch) for ch in text)
