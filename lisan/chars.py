"""Character tables for Arabic-script text. Everything is written as code points so the file reads the same in any editor."""
from __future__ import annotations

# Marks stripped by default: fathatan .. sukun, superscript (dagger) alef, and the Quranic/rare marks stripped on request.
DIACRITICS: frozenset[str] = frozenset(chr(c) for c in range(0x064B, 0x0656)) | {"ٰ"}
EXTRA_MARKS: frozenset[str] = (
    frozenset(chr(c) for c in range(0x0610, 0x061B))      # honorific and Quranic signs
    | frozenset(chr(c) for c in range(0x0656, 0x0660))    # subscript alef, inverted damma, noon ghunna and relatives
    | frozenset(chr(c) for c in range(0x06D6, 0x06EE))    # Quranic annotation marks
    | frozenset(chr(c) for c in range(0x08D3, 0x0900))    # extended Arabic marks
)
TATWEEL = "ـ"

ALEF_VARIANTS = {"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا"}  # hamza above, below, madda, wasla
ALEF_MAQSURA = "ى"
YEH = "ي"
TEH_MARBUTA = "ة"
HEH = "ه"
WAW_HAMZA = "ؤ"
YEH_HAMZA = "ئ"
HAMZA = "ء"

# Persian, Urdu and Pashto letter forms that stand for an Arabic letter in search.
PERSIAN_FOLD = {
    "ک": "ك",  # keheh -> kaf
    "ی": "ي",  # farsi yeh -> yeh
    "ے": "ي",  # yeh barree -> yeh
    "ہ": "ه",  # heh goal -> heh
    "ھ": "ه",  # heh doachashmee -> heh
    "ە": "ه",  # ae -> heh
    "ۀ": "ه",  # heh with yeh above -> heh
}

# Eastern Arabic-Indic (U+0660) and Persian (U+06F0) digits to the digit they stand for.
DIGITS = {**{chr(0x0660 + i): str(i) for i in range(10)}, **{chr(0x06F0 + i): str(i) for i in range(10)}}
EASTERN = {str(i): chr(0x0660 + i) for i in range(10)}
PERSIAN_DIGITS = {str(i): chr(0x06F0 + i) for i in range(10)}

# Invisible characters that break matching: bidi controls, zero-width characters, the Arabic letter mark, soft hyphen, BOM.
CONTROLS: frozenset[str] = frozenset(
    ["​", "‌", "‍", "‎", "‏", "؜", "­", "﻿"]
    + [chr(c) for c in range(0x202A, 0x202F)] + [chr(c) for c in range(0x2066, 0x206A)]
)

PUNCTUATION = {
    "،": ",", "؛": ";", "؟": "?", "٪": "%", "٫": ".", "٬": ",", "۔": ".",
    "«": '"', "»": '"', "“": '"', "”": '"', "‘": "'", "’": "'",
}


def is_arabic_letter(ch: str) -> bool:
    code = ord(ch)
    return (0x0621 <= code <= 0x064A) or (0x0671 <= code <= 0x06D3) or code in (0x06FA, 0x06FB, 0x06FC)


def is_arabic_script(ch: str) -> bool:
    """Any character in an Arabic-script block, letters, marks, digits and presentation forms included."""
    code = ord(ch)
    return (0x0600 <= code <= 0x06FF) or (0x0750 <= code <= 0x077F) or (0x08A0 <= code <= 0x08FF) or (0xFB50 <= code <= 0xFDFF) or (0xFE70 <= code <= 0xFEFF)
