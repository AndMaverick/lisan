"""Numbers written with Arabic-Indic or Persian digits and Arabic separators, found in text and read as values."""
from __future__ import annotations

import re
from dataclasses import dataclass

from .chars import DIGITS, EASTERN, PERSIAN_DIGITS

_DIGIT = "0-9٠-٩۰-۹"
_NUMBER = re.compile(rf"(?<![{_DIGIT}])[+-]?[{_DIGIT}]+(?:[,.،٫٬][{_DIGIT}]+)*(?![{_DIGIT}])")
_GROUPED = re.compile(r"^\d{1,3}(,\d{3})+$")


@dataclass(frozen=True)
class Number:
    value: float
    text: str
    start: int
    end: int


def to_ascii_digits(text: str) -> str:
    return "".join(DIGITS.get(ch, ch) for ch in text)


def to_eastern(text: str | int, *, persian: bool = False) -> str:
    """ASCII digits to Eastern Arabic-Indic (U+0660) digits, or Persian (U+06F0) with ``persian=True``."""
    table = PERSIAN_DIGITS if persian else EASTERN
    return "".join(table.get(ch, ch) for ch in str(text))


def parse_number(text: str) -> float:
    """Read one number written in any digit set. The Arabic decimal separator U+066B is always a decimal point and the Arabic thousands
    separator U+066C always groups. A comma groups when the text is groups of three digits (1,234,567), otherwise it is a decimal
    comma; a dot is a decimal point. Raises ValueError if the text is not a number."""
    s = to_ascii_digits(text.strip()).replace("،", ",")
    s = s.replace("٬", "").replace("٫", ".")
    sign = -1.0 if s.startswith("-") else 1.0
    s = s.lstrip("+-")
    if "," in s and "." in s:
        s = s.replace(",", "") if s.rfind(".") > s.rfind(",") else s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", "") if _GROUPED.match(s) else s.replace(",", ".")
    try:
        return sign * float(s)
    except ValueError:
        raise ValueError(f"not a number: {text!r}") from None


def extract_numbers(text: str) -> list[Number]:
    """Every number in ``text`` with its value and position, whatever digits it is written in."""
    found: list[Number] = []
    for m in _NUMBER.finditer(text):
        try:
            found.append(Number(parse_number(m.group()), m.group(), m.start(), m.end()))
        except ValueError:
            continue
    return found
