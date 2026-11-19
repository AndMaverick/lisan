"""Command line for Arabic text. Reads a file or stdin (``-``), writes UTF-8.

Exit codes: 0 success, 1 a gate was hit (``match`` below its threshold, ``detect --min-arabic`` not met), 2 error."""
from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from . import (
    PROFILES,
    arabic_ratio,
    arabizi_score,
    clean,
    dialect_hints,
    extract_numbers,
    is_rtl,
    match_names,
    normalize,
    script_runs,
    to_buckwalter,
    tokens,
)
from .translit import from_buckwalter


def _read(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lisan", description="Arabic text infrastructure.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("normalize", help="normalize text line by line")
    p.add_argument("file", nargs="?", default="-")
    p.add_argument("--profile", choices=sorted(PROFILES), default="search")
    p.add_argument("--digits", choices=("ascii", "keep", "eastern", "persian"), default="ascii")

    p = sub.add_parser("clean", help="NFKC, drop invisible controls, collapse whitespace (keeps diacritics)")
    p.add_argument("file", nargs="?", default="-")

    p = sub.add_parser("tokens", help="print tokens, one per line")
    p.add_argument("file", nargs="?", default="-")
    p.add_argument("--profile", choices=sorted(PROFILES), default="search")
    p.add_argument("--stem", action="store_true")

    p = sub.add_parser("translit", help="Arabic to Buckwalter, or back with --reverse")
    p.add_argument("file", nargs="?", default="-")
    p.add_argument("--reverse", action="store_true")

    p = sub.add_parser("numbers", help="numbers in the text, whatever digits they use")
    p.add_argument("file", nargs="?", default="-")

    p = sub.add_parser("detect", help="routing signals as JSON")
    p.add_argument("file", nargs="?", default="-")
    p.add_argument("--min-arabic", type=float, help="exit 1 when the Arabic share of letters is below this")

    p = sub.add_parser("match", help="score whether two names are the same name; exit 1 below the threshold")
    p.add_argument("a")
    p.add_argument("b")
    p.add_argument("--threshold", type=float, default=0.85)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return _run(args)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def _run(a: argparse.Namespace) -> int:
    if a.command == "match":
        m = match_names(a.a, a.b, a.threshold)
        print(json.dumps({"score": round(m.score, 3), "match": m.is_match, "coverage": round(m.coverage, 3), "method": m.method,
                          "confidence": m.confidence, "left": m.left, "right": m.right}, ensure_ascii=False))
        return 0 if m.is_match else 1
    text = _read(a.file)
    if a.command == "normalize":
        for line in text.splitlines():
            print(normalize(line, profile=a.profile, digits=a.digits))
    elif a.command == "clean":
        print(clean(text))
    elif a.command == "tokens":
        for token in tokens(text, profile=a.profile, stem=a.stem):
            print(token)
    elif a.command == "translit":
        print(from_buckwalter(text.rstrip("\n")) if a.reverse else to_buckwalter(text.rstrip("\n")))
    elif a.command == "numbers":
        for n in extract_numbers(text):
            print(f"{n.value:g}\t{n.text}")
    else:
        ratio = arabic_ratio(text)
        print(json.dumps({"arabic_ratio": round(ratio, 3), "rtl": is_rtl(text), "arabizi": round(arabizi_score(text), 3),
                          "dialect_hints": dialect_hints(text), "runs": [{"script": r.script, "text": r.text} for r in script_runs(text)]},
                         ensure_ascii=False))
        if a.min_arabic is not None and ratio < a.min_arabic:
            print(f"gate: Arabic share {ratio:.3f} is below {a.min_arabic}", file=sys.stderr)
            return 1
    return 0



if __name__ == "__main__":
    sys.exit(main())
