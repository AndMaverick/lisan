"""Fast signals for routing text: how Arabic is it, which script runs does it contain, which dialect words does it use, is it Arabizi."""
from __future__ import annotations

import re
from dataclasses import dataclass

from .chars import is_arabic_letter, is_arabic_script
from .normalize import normalize


def arabic_ratio(text: str) -> float:
    """Share of letters that are Arabic. Useful for routing mixed-language input."""
    letters = [c for c in text if c.isalpha()]
    return sum(is_arabic_letter(c) for c in letters) / len(letters) if letters else 0.0


def is_rtl(text: str, threshold: float = 0.5) -> bool:
    """True when Arabic-script letters are at least ``threshold`` of all letters."""
    letters = [c for c in text if c.isalpha()]
    return bool(letters) and sum(is_arabic_script(c) for c in letters) / len(letters) >= threshold


@dataclass(frozen=True)
class Run:
    script: str  # "arabic", "latin" or "other"
    text: str
    start: int
    end: int


def _run(script: str, text: str, begin: int, end: int) -> Run:
    piece = text[begin:end]
    lead = len(piece) - len(piece.lstrip())
    return Run(script, piece.strip(), begin + lead, begin + lead + len(piece.strip()))


def script_runs(text: str) -> list[Run]:
    """Split text into runs of one script. Digits, spaces and punctuation attach to the run before them (or the first run, at the start)."""
    runs: list[Run] = []
    current: str | None = None
    begin = 0
    for i, ch in enumerate(text):
        if not ch.isalpha():
            continue
        kind = "arabic" if is_arabic_script(ch) else "latin" if ch.isascii() else "other"
        if kind == current:
            continue
        if current is not None:
            runs.append(_run(current, text, begin, i))
            begin = i
        current = kind
    if current is not None:
        runs.append(_run(current, text, begin, len(text)))
    return runs


# Words that mark a dialect. Only words that are rare outside it are listed, so words shared across dialects or with another meaning
# (a name, a greeting, MSA) are left out on purpose. This is a lookup of evidence, not a classifier, and it says nothing about text that
# uses none of these words.
_DIALECT_WORDS = {
    "egyptian": ["ازاي", "دلوقتي", "عايز", "عاوز", "كده", "ازيك", "بتاع"],
    "levantine": ["هلق", "كتير", "هيك", "بدي", "منيح", "كيفك"],
    "gulf": ["وايد", "شلونك", "شلون", "شنو", "ابغى"],
    "maghrebi": ["بزاف", "ديال", "واش", "دابا", "كيفاش", "علاش", "مزيان", "شحال"],
}
_DIALECT_INDEX: dict[str, set[str]] = {}
for _region, _words in _DIALECT_WORDS.items():
    for _w in _words:
        _DIALECT_INDEX.setdefault(normalize(_w, profile="search"), set()).add(_region)


def dialect_hints(text: str) -> dict[str, list[str]]:
    """Dialect marker words found in ``text``, by region. Empty when none are found, which is not evidence of Modern Standard Arabic."""
    hits: dict[str, list[str]] = {}
    for word in re.findall(r"[^\W\d_]+", normalize(text, profile="search")):
        for region in _DIALECT_INDEX.get(word, ()):
            hits.setdefault(region, []).append(word)
    return hits


_ARABIZI_LEXICON = {"habibi", "habibti", "inshallah", "mashallah", "yalla", "wallah", "wallahi", "shukran", "ahlan", "marhaba", "khalas",
                    "yaani", "bukra", "kteer", "keefak", "kifak"}
_NOT_ARABIZI_STEMS = {"web", "gpt", "ipv", "sha", "utf", "aes", "rsa", "python", "covid"}
_ARABIZI_SHAPE = re.compile(r"[A-Za-z']*(?:[A-Za-z][235-9]|[235-9][A-Za-z])[A-Za-z0-9']*")


def _looks_arabizi(word: str) -> bool:
    if word.lower() in _ARABIZI_LEXICON:
        return True
    letters = re.sub(r"[^A-Za-z]", "", word)
    if len(letters) < 3 or letters.lower() in _NOT_ARABIZI_STEMS or len(re.findall(r"\d", word)) > 2:
        return False
    return bool(_ARABIZI_SHAPE.fullmatch(word)) and bool(re.search(r"[235-9]", word))


def arabizi_score(text: str) -> float:
    """Share of Latin-letter words that look like Arabizi (Arabic written in Latin letters with digits for sounds: 3 for ain, 7 for ha, 5 for
    kha, 2 for hamza, 9 for qaf or sad, 6 for ta, 8 for ghain) or are common Arabizi words. A heuristic for routing, not a language identifier."""
    latin = [w for w in re.findall(r"[A-Za-z0-9']+", text) if any(c.isalpha() for c in w)]
    return sum(_looks_arabizi(w) for w in latin) / len(latin) if latin else 0.0
