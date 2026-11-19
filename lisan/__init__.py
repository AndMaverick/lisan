"""lisan: Arabic text infrastructure. Normalization, light stemming, search, name matching, transliteration, numbers and routing
signals for Arabic-script text. Dependency-free."""
from __future__ import annotations

from .chars import is_arabic_letter, is_arabic_script
from .detect import Run, arabic_ratio, arabizi_score, dialect_hints, is_rtl, script_runs
from .names import NameMatch, match_names, skeleton
from .normalize import PROFILES, clean, normalize
from .numbers import Number, extract_numbers, parse_number, to_ascii_digits, to_eastern
from .search import ANALYZERS, Hit, Index
from .stem import char_ngrams, light_stem
from .tokenize import search_key, tokens
from .translit import from_buckwalter, to_buckwalter

__version__ = "0.2.0"

__all__ = [
    "ANALYZERS", "PROFILES", "Hit", "Index", "NameMatch", "Number", "Run", "arabic_ratio", "arabizi_score", "char_ngrams", "clean",
    "dialect_hints", "extract_numbers", "from_buckwalter", "is_arabic_letter", "is_arabic_script", "is_rtl", "light_stem", "match_names",
    "normalize", "parse_number", "script_runs", "search_key", "skeleton", "to_ascii_digits", "to_buckwalter", "to_eastern", "tokens",
]
