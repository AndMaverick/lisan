"""Reproduce the README numbers: python examples/evaluate.py"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from name_pairs import COLLIDE, DIFFERENT, MISSED, SAME  # noqa: E402
from search_fixture import DOCS, MORPH_DOCS, MORPH_QUERIES, QUERIES  # noqa: E402

from lisan import ANALYZERS, Index, match_names  # noqa: E402


def names() -> None:
    print("Name matching (hand-written regression set, threshold 0.85)")
    print(f"  same-name pairs matched      {sum(match_names(a, b).is_match for a, b in SAME)}/{len(SAME)}")
    print(f"  different-name pairs merged  {sum(match_names(a, b).is_match for a, b in DIFFERENT)}/{len(DIFFERENT)}")
    print(f"  known collisions (merged)    {sum(match_names(a, b).is_match for a, b in COLLIDE)}/{len(COLLIDE)}: " + ", ".join(f"{a}~{b}" for a, b in COLLIDE))
    print(f"  known misses (not matched)   {sum(not match_names(a, b).is_match for a, b in MISSED)}/{len(MISSED)}: " + ", ".join(f"{a}~{b}" for a, b in MISSED))


def search() -> None:
    print("\nSearch, success at rank 1 (the target document is the top hit)")
    print(f"  {'analyzer':<12}{'spelling variants':>20}{'inflections':>14}")
    for name in ANALYZERS:
        index = Index(name)
        index.add_many({**DOCS, **MORPH_DOCS}.items())
        row = []
        for queries in (QUERIES, MORPH_QUERIES):
            ok = sum(1 for target, q in queries.items() if (hits := index.search(q, 1)) and hits[0].id == target)
            row.append(f"{ok}/{len(queries)}")
        print(f"  {name:<12}{row[0]:>20}{row[1]:>14}")


if __name__ == "__main__":
    names()
    search()
