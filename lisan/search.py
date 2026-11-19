"""A small BM25 search index with Arabic-aware analysis, so search over Arabic text works without a search server."""
from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Callable, Iterable
from dataclasses import dataclass

from .normalize import normalize
from .stem import char_ngrams, light_stem

Analyzer = Callable[[str], list[str]]


def _words(text: str, profile: str) -> list[str]:
    return re.findall(r"[^\W_]+", normalize(text, profile=profile).lower(), flags=re.UNICODE)


def _raw(text: str) -> list[str]:
    return text.split()


def _normalized(text: str) -> list[str]:
    return _words(text, "search")


def _stemmed(text: str) -> list[str]:
    return [light_stem(w) for w in _words(text, "search")]


def _ngrams(text: str) -> list[str]:
    return [g for w in _words(text, "search") for g in char_ngrams(w, 3)]


ANALYZERS: dict[str, Analyzer] = {"raw": _raw, "normalized": _normalized, "stemmed": _stemmed, "trigram": _ngrams}


@dataclass(frozen=True)
class Hit:
    id: str
    score: float
    text: str


class Index:
    """BM25 over documents analyzed by one of ``raw`` (whitespace split, the baseline), ``normalized``, ``stemmed`` (normalized then
    light-stemmed) or ``trigram`` (character 3-grams of normalized words), or by your own function ``str -> list[str]``."""

    def __init__(self, analyzer: str | Analyzer = "stemmed", k1: float = 1.5, b: float = 0.75) -> None:
        if isinstance(analyzer, str):
            if analyzer not in ANALYZERS:
                raise ValueError(f"unknown analyzer {analyzer!r}; use one of {', '.join(ANALYZERS)}")
            analyzer = ANALYZERS[analyzer]
        self.analyze = analyzer
        self.k1, self.b = k1, b
        self._docs: dict[str, str] = {}
        self._post: dict[str, dict[str, int]] = {}
        self._len: dict[str, int] = {}

    def __len__(self) -> int:
        return len(self._docs)

    def add(self, doc_id: str, text: str) -> None:
        if doc_id in self._docs:
            raise ValueError(f"document id {doc_id!r} is already in the index")
        terms = self.analyze(text)
        self._docs[doc_id] = text
        self._len[doc_id] = len(terms)
        for term, count in Counter(terms).items():
            self._post.setdefault(term, {})[doc_id] = count

    def add_many(self, docs: Iterable[tuple[str, str]]) -> None:
        for doc_id, text in docs:
            self.add(doc_id, text)

    def search(self, query: str, k: int = 10) -> list[Hit]:
        """The ``k`` best documents for ``query``, best first. Ties break by document id so results are reproducible."""
        n = len(self._docs)
        if not n:
            return []
        avg = (sum(self._len.values()) / n) or 1.0
        terms = Counter(self.analyze(query))
        scores: dict[str, float] = {}
        for term, qtf in terms.items():
            postings = self._post.get(term)
            if not postings:
                continue
            df = len(postings)
            idf = math.log(1.0 + (n - df + 0.5) / (df + 0.5))
            for doc_id, f in postings.items():
                norm = f * (self.k1 + 1.0) / (f + self.k1 * (1.0 - self.b + self.b * self._len[doc_id] / avg))
                scores[doc_id] = scores.get(doc_id, 0.0) + idf * norm * qtf
        ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))[:k]
        return [Hit(doc_id, score, self._docs[doc_id]) for doc_id, score in ranked]
