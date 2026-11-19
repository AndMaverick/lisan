"""Matching person names across spellings and scripts: the problem behind name screening, KYC and de-duplication in the Arabic-speaking
world, where one name has many Latin spellings and the same Latin spelling can stand for several Arabic ones.

Approach: reduce each name to a consonant skeleton (vowels dropped, transliteration variants merged: kh, sh, th, dh, gh, ou/u/o, double
letters, the arabizi digits 2 3 5 6 7 8 9), then compare skeletons with an edit distance in which a few phonetically close pairs (q and k,
j and g, th and t) cost less than a plain substitution. Multi-token names are matched token by token with titles and particles
(bin, ibn, al, el) set aside. Arabic against Arabic skips the skeleton and compares the normalized letters, so Hasan and Husayn stay apart.

This is a transparent scorer, not a trained model. Its limits are listed in the README and pinned down in the tests."""
from __future__ import annotations

import re
from dataclasses import dataclass

from .chars import is_arabic_letter
from .normalize import normalize

LATIN_PARTICLES = {"bin", "ibn", "bint", "ben", "binti", "ould", "wuld"}
LATIN_ARTICLES = {"al", "el", "ul", "ar", "as", "ash", "ad", "at", "az", "an", "ath", "adh"}
LATIN_TITLES = {"mr", "mrs", "ms", "miss", "dr", "prof", "eng", "engr", "hajj", "haj", "haji", "hajji", "sheikh", "shaikh", "sheikha", "shaykh"}
ABD_LATIN = {"abd", "abed", "abdal", "abdel", "abdul", "abdil"}
ARABIC_PARTICLES = {"بن", "ابن", "بنت"}  # bin ibn bint
ARABIC_TITLES = {"الشيخ", "الدكتور", "د", "م", "المهندس",
                 "الحاج", "السيد", "شيخ"}
ABD_ARABIC = "عبد"
AL = "ال"
ALLAH = "الله"

_ARABIC_SKELETON = {
    "ب": "b", "ت": "t", "ث": "θ", "ج": "j", "ح": "h", "خ": "x", "د": "d", "ذ": "ð",
    "ر": "r", "ز": "z", "س": "s", "ش": "š", "ص": "s", "ض": "d", "ط": "t", "ظ": "z",
    "غ": "ġ", "ف": "f", "ق": "q", "ك": "k", "ل": "l", "م": "m", "ن": "n", "ه": "h",
}
_DIGRAPHS = (("kh", "x"), ("sh", "š"), ("ch", "š"), ("th", "θ"), ("dh", "ð"), ("gh", "ġ"), ("ph", "f"), ("ck", "k"))
_ARABIZI = {"2": "", "3": "", "5": "x", "6": "t", "7": "h", "8": "ġ", "9": "q"}
_VOWELS = set("aeiou")

# Phonetically close pairs: replacing one by the other costs less than a plain substitution.
_CLOSE = {frozenset(p): c for p, c in [(("θ", "t"), 0.35), (("θ", "s"), 0.35), (("ð", "d"), 0.35), (("ð", "z"), 0.35),
                                       (("q", "k"), 0.35), (("q", "g"), 0.35), (("j", "g"), 0.35), (("ġ", "g"), 0.35), (("h", "x"), 0.5)]}


def _collapse(s: str) -> str:
    return re.sub(r"(.)\1+", r"\1", s)


def _is_arabic(text: str) -> bool:
    return any(is_arabic_letter(c) for c in text)


def _latin_tokens(text: str) -> list[str]:
    raw = re.sub(r"[-_.]", " ", text.lower().replace("'", "").replace("’", ""))
    toks = re.findall(r"[a-z0-9]+", raw)
    toks = [t for t in toks if t not in LATIN_PARTICLES]
    toks = [t for t in toks if t not in LATIN_TITLES] or toks
    merged: list[str] = []
    i = 0
    while i < len(toks):
        t = toks[i]
        if t in ABD_LATIN and i + 1 < len(toks) and toks[i + 1] in LATIN_ARTICLES:  # "abd al" is one unit: abdal
            merged.append("abdal")
            i += 2
            continue
        merged.append(t)
        i += 1
    kept = [t for t in merged if t not in LATIN_ARTICLES] or merged
    out = []
    for t in kept:
        if len(t) >= 6 and t[:2] in ("al", "el") and t[2] not in _VOWELS and t[2].isalpha() and t not in ABD_LATIN:
            t = t[2:]  # fused article: alhajri, elsayed
        out.append(t)
    return out


def _latin_skeleton(token: str) -> str:
    t = token.lower()
    if any(ch.isdigit() for ch in t) and any(ch.isalpha() for ch in t):
        t = t.replace("3'", "ġ")
        t = "".join(_ARABIZI.get(ch, ch) for ch in t)
    t = re.sub(r"[0-9]", "", t)
    for src, dst in _DIGRAPHS:
        t = t.replace(src, dst)
    out: list[str] = []
    for i, ch in enumerate(t):
        if ch in _VOWELS:
            continue
        if ch in "yw":
            if i == 0:
                out.append(ch)
            continue
        if ch == "c":
            ch = "s" if t[i + 1:i + 2] in ("e", "i", "y") else "k"
        elif ch == "p":
            ch = "b"
        elif ch == "v":
            ch = "f"
        out.append(ch)
    s = _collapse("".join(out))
    return s[:-1] if len(s) > 1 and s.endswith("h") else s


def _arabic_tokens(text: str) -> list[str]:
    toks = normalize(text, profile="search").split()
    toks = [t for t in toks if t not in ARABIC_PARTICLES]
    toks = [t for t in toks if t not in ARABIC_TITLES] or toks
    return [t for t in toks if t != AL] or toks


def _arabic_units(toks: list[str]) -> list[str]:
    """Tokens with the article attached to ``abd`` kept (abd al-X is abdul X) and every other leading article removed."""
    out: list[str] = []
    i = 0
    while i < len(toks):
        t = toks[i]
        if t == ABD_ARABIC and i + 1 < len(toks) and toks[i + 1].startswith(AL) and len(toks[i + 1]) > 3 and toks[i + 1] != ALLAH:
            out.append(t + AL)
            toks = toks[:i + 1] + [toks[i + 1][2:]] + toks[i + 2:]
            i += 1
            continue
        if t.startswith(AL) and len(t) > 4 and t != ALLAH:
            t = t[2:]
        out.append(t)
        i += 1
    return out


def _arabic_skeleton(token: str) -> str:
    out: list[str] = []
    for i, ch in enumerate(token):
        if ch in ("و", "ي"):
            if i == 0:
                out.append("w" if ch == "و" else "y")
            continue
        out.append(_ARABIC_SKELETON.get(ch, ""))
    s = _collapse("".join(out))
    return s[:-1] if len(s) > 1 and s.endswith("h") else s


def _distance(a: str, b: str) -> float:
    prev = [float(j) for j in range(len(b) + 1)]
    for i, ca in enumerate(a, 1):
        cur = [float(i)]
        for j, cb in enumerate(b, 1):
            sub = 0.0 if ca == cb else _CLOSE.get(frozenset((ca, cb)), 1.0)
            cur.append(min(prev[j] + 1.0, cur[j - 1] + 1.0, prev[j - 1] + sub))
        prev = cur
    return prev[-1]


def _similarity(a: str, b: str) -> float:
    if not a and not b:
        return 1.0
    return max(0.0, 1.0 - _distance(a, b) / max(len(a), len(b)))


def skeleton(text: str) -> str:
    """The consonant skeleton of a name, tokens joined with spaces. Arabic and Latin names land in one alphabet, so they can be compared."""
    return " ".join(_skeleton_tokens(text))


def _skeleton_tokens(text: str) -> list[str]:
    if _is_arabic(text):
        return [s for s in (_arabic_skeleton(t) for t in _arabic_units(_arabic_tokens(text))) if s]
    return [s for s in (_latin_skeleton(t) for t in _latin_tokens(text)) if s]


@dataclass(frozen=True)
class NameMatch:
    score: float       # 0 to 1: how well every token of the shorter name is matched by the other name
    coverage: float    # tokens in the shorter name over tokens in the longer: 1.0 when both have the same number
    method: str        # "aligned" (token by token), "joined" (written solid versus split), or "exact"
    confidence: str    # "low" when the skeletons are very short, so many unrelated names look alike
    left: str
    right: str
    threshold: float = 0.85

    @property
    def is_match(self) -> bool:
        return self.score >= self.threshold


def match_names(a: str, b: str, threshold: float = 0.85) -> NameMatch:
    """Score how likely two written names are the same name. Works Arabic to Arabic, Latin to Latin and Arabic to Latin.

    Every token of the shorter name must find a counterpart in the other, and the score is the worst of those pairings, so one wrong
    token (Rahman against Rahim) cannot be averaged away by a long matching name. When one name is written solid and the other is
    split (Abdurrahman, Abdul Rahman), the joined skeletons are compared instead."""
    both_arabic = _is_arabic(a) and _is_arabic(b)
    if both_arabic:
        ta, tb = _arabic_units(_arabic_tokens(a)), _arabic_units(_arabic_tokens(b))
        raw_a, raw_b = "".join(_arabic_tokens(a)), "".join(_arabic_tokens(b))
    else:
        ta, tb = _skeleton_tokens(a), _skeleton_tokens(b)
        raw_a, raw_b = "".join(ta), "".join(tb)
        raw_a, raw_b = _collapse(raw_a), _collapse(raw_b)
    if not ta or not tb:
        return NameMatch(0.0, 0.0, "aligned", "low", " ".join(ta), " ".join(tb), threshold)
    left, right = " ".join(ta), " ".join(tb)
    shortest = min(len(raw_a), len(raw_b))
    confidence = "low" if shortest < 3 else "high"
    if left == right:
        return NameMatch(1.0, 1.0, "exact", confidence, left, right, threshold)
    short, long_ = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    coverage = len(short) / len(long_)
    # Align each token of the shorter name to its best unused partner in the longer one.
    used: set[int] = set()
    pair_scores: list[float] = []
    for token in short:
        options = [(_similarity(token, other), j) for j, other in enumerate(long_) if j not in used]
        best, where = max(options, default=(0.0, -1))
        if where >= 0:
            used.add(where)
        pair_scores.append(best)
    aligned = min(pair_scores)
    joined = _similarity(raw_a, raw_b) if len(ta) != len(tb) else 0.0  # one name written solid, the other split
    if joined > aligned:
        return NameMatch(joined, coverage, "joined", confidence, left, right, threshold)
    return NameMatch(aligned, coverage, "aligned", confidence, left, right, threshold)
