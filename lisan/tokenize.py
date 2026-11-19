"""Tokens and canonical keys. ``tokens`` and ``search_key`` keep their 0.1 behaviour by default."""
from __future__ import annotations

import re

from .normalize import normalize
from .stem import light_stem


def tokens(text: str, *, profile: str = "legacy", stem: bool = False) -> list[str]:
    """Word tokens of the normalized text. With ``stem=True`` each token is light-stemmed (see ``lisan.stem``)."""
    words = re.findall(r"[^\W_]+", normalize(text, profile=profile), flags=re.UNICODE)
    return [light_stem(w) for w in words] if stem else words


def search_key(text: str, *, profile: str | None = None) -> str:
    """A canonical key for lookups and deduplication: normalized, lowercased Latin, single-spaced.

    The default is the 0.1 key (teh marbuta folded to heh). ``profile="search"`` also applies NFKC, invisible-character removal,
    Persian letter folding, hamza folding and punctuation folding."""
    folded = normalize(text, ta_marbuta=True) if profile is None else normalize(text, profile=profile)
    return " ".join(folded.lower().split())
