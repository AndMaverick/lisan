"""Arabic text normalization with named profiles. ``legacy`` is exactly the 0.1 behaviour."""
from __future__ import annotations

import unicodedata
from typing import Any

from . import chars

PROFILES: dict[str, dict[str, Any]] = {
    # 0.1: strip diacritics and tatweel, unify alef and yeh, Eastern digits to ASCII.
    "legacy": {},
    # Unicode hygiene only: NFKC (presentation forms and ligatures become plain letters), invisible controls and Quranic marks removed.
    "clean": {"nfkc": True, "controls": True, "quranic": True},
    # Everything that makes two spellings of one word compare equal, at some cost in precision.
    "search": {"nfkc": True, "controls": True, "quranic": True, "persian": True, "hamza": True, "ta_marbuta": True, "punctuation": True},
}


def normalize(
    text: str, *, profile: str = "legacy", ta_marbuta: bool | None = None, nfkc: bool | None = None, persian: bool | None = None,
    hamza: bool | None = None, controls: bool | None = None, quranic: bool | None = None, punctuation: bool | None = None,
    digits: str | None = None,
) -> str:
    """Normalize Arabic-script text.

    Always: strip fathatan to sukun and the dagger alef, strip tatweel, fold the alef forms (hamza above, below, madda, wasla) to
    bare alef, fold alef maqsura to yeh. Choose a ``profile`` ("legacy", "clean", "search") and override any option by keyword:

    nfkc         Unicode NFKC first, so presentation forms and ligatures (U+FB50 to U+FDFF, U+FE70 to U+FEFF) become plain letters.
    controls     remove bidi controls, zero-width characters, the Arabic letter mark, soft hyphens and byte-order marks.
    quranic      also strip Quranic annotation marks and the rarer vowel signs.
    persian      Persian and Urdu kaf, yeh and heh forms to the Arabic letters.
    hamza        remove the hamza and its carriers (waw with hamza, yeh with hamza, bare hamza), so the two spellings of mas'ul
                 (with a waw or a yeh seat) compare equal. Lossy: use it to match, not to display.
    ta_marbuta   teh marbuta to heh. Improves recall, costs precision.
    punctuation  Arabic comma, semicolon, question mark, percent and decimal separators, and curly quotes to ASCII.
    digits       "ascii" (default) Eastern and Persian digits to 0-9; "keep" leaves them; "eastern" or "persian" converts ASCII digits to them.
    """
    base = PROFILES.get(profile)
    if base is None:
        raise ValueError(f"unknown profile {profile!r}; use one of {', '.join(PROFILES)}")
    opts = {
        "nfkc": nfkc, "controls": controls, "quranic": quranic, "persian": persian, "hamza": hamza, "ta_marbuta": ta_marbuta,
        "punctuation": punctuation,
    }
    on = {k: (base.get(k, False) if v is None else v) for k, v in opts.items()}
    mode = digits or "ascii"
    if mode not in ("ascii", "keep", "eastern", "persian"):
        raise ValueError(f"digits must be ascii, keep, eastern or persian, not {mode!r}")
    if on["nfkc"]:
        text = unicodedata.normalize("NFKC", text)
    out: list[str] = []
    for ch in text:
        if ch in chars.DIACRITICS or ch == chars.TATWEEL:
            continue
        if on["controls"] and ch in chars.CONTROLS:
            continue
        if on["quranic"] and ch in chars.EXTRA_MARKS:
            continue
        ch = chars.ALEF_VARIANTS.get(ch, ch)
        if on["persian"]:
            ch = chars.PERSIAN_FOLD.get(ch, ch)
        if mode == "ascii":
            ch = chars.DIGITS.get(ch, ch)
        elif mode in ("eastern", "persian"):
            target = chars.EASTERN if mode == "eastern" else chars.PERSIAN_DIGITS
            ascii_digit = chars.DIGITS.get(ch, ch if ch in target else "")
            ch = target.get(ascii_digit, ch)
        if ch == chars.ALEF_MAQSURA:
            ch = chars.YEH
        if on["hamza"] and ch in (chars.WAW_HAMZA, chars.YEH_HAMZA, chars.HAMZA):
            continue
        if on["ta_marbuta"] and ch == chars.TEH_MARBUTA:
            ch = chars.HEH
        if on["punctuation"]:
            ch = chars.PUNCTUATION.get(ch, ch)
        out.append(ch)
    return "".join(out)


def clean(text: str) -> str:
    """Make text safe to store, compare and show: NFKC, invisible controls removed, whitespace collapsed. Keeps diacritics."""
    text = unicodedata.normalize("NFKC", text)
    text = "".join(ch for ch in text if ch not in chars.CONTROLS)
    return " ".join(text.split())
