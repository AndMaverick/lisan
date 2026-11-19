"""Light stemming and n-grams for Arabic retrieval.

The light stemmer is in the family of Larkey, Ballesteros and Connell (2002): it removes a small list of prefixes and suffixes and
nothing else, so it never produces a root. The affix lists follow that family. The minimum stem lengths are this library's own
choices and are parameters, because they trade recall for precision."""
from __future__ import annotations

from .normalize import normalize

PREFIXES = ("وال", "بال", "كال", "فال", "ال", "لل")  # wal bal kal fal al lil
SUFFIXES = ("ها", "ان", "ات", "ون", "ين", "يه", "ية",
            "ه", "ة", "ي")  # ha an at un in iyh iya h a y
WAW = "و"


def light_stem(word: str, *, min_stem: int = 2, strip_waw: bool = True) -> str:
    """Strip one definite-article prefix (or a leading waw, only when four or more letters remain, so wazir and walad keep their waw)
    and up to two suffixes, never leaving fewer than ``min_stem`` letters.

    The word is normalized first (diacritics, tatweel, alef forms, alef maqsura). Broken plurals are untouched: a light stemmer
    cannot map the plural to its singular, which would need a root or lemma."""
    w = normalize(word)
    for prefix in PREFIXES:
        if w.startswith(prefix) and len(w) - len(prefix) >= max(min_stem, 2):
            w = w[len(prefix):]
            break
    else:
        if strip_waw and w.startswith(WAW) and len(w) - 1 >= max(min_stem, 4):
            w = w[1:]
    for _ in range(2):  # a second pass lets "at" then "an" go, so the plural and the singular reach the same stem
        for suffix in SUFFIXES:
            if w.endswith(suffix) and len(w) - len(suffix) >= max(min_stem, 2):
                w = w[:-len(suffix)]
                break
        else:
            break
    return w


def char_ngrams(word: str, n: int = 3, *, pad: bool = True) -> list[str]:
    """Character n-grams of a normalized word, padded with ``_`` at both ends so prefixes and suffixes are visible."""
    w = normalize(word)
    if pad:
        w = f"_{w}_"
    if len(w) <= n:
        return [w] if w.strip("_") else []
    return [w[i:i + n] for i in range(len(w) - n + 1)]
