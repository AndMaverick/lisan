import unittest

from lisan import (
    arabic_ratio,
    arabizi_score,
    dialect_hints,
    extract_numbers,
    from_buckwalter,
    is_rtl,
    parse_number,
    script_runs,
    to_ascii_digits,
    to_buckwalter,
    to_eastern,
)
from lisan.translit import BUCKWALTER


class TranslitTests(unittest.TestCase):
    def test_known_words(self):
        self.assertEqual(to_buckwalter("كتاب"), "ktAb")
        self.assertEqual(to_buckwalter("مدرسة"), "mdrsp")
        self.assertEqual(to_buckwalter("الله"), "Allh")
        self.assertEqual(to_buckwalter("أحمد إبراهيم"), ">Hmd <brAhym")

    def test_round_trip_with_marks(self):
        for text in ["كِتَابٌ", "مُحَمَّد", "بِسْمِ ٱللَّهِ", "قرآن", "ؤئء آ"]:
            self.assertEqual(from_buckwalter(to_buckwalter(text)), text)

    def test_table_is_one_to_one(self):
        self.assertEqual(len(set(BUCKWALTER.values())), len(BUCKWALTER))

    def test_non_arabic_passes_through_going_out(self):
        self.assertEqual(to_buckwalter("abc 123 !"), "abc 123 !")


class NumberTests(unittest.TestCase):
    def test_parse_in_every_digit_set(self):
        self.assertEqual(parse_number("123"), 123)
        self.assertEqual(parse_number("١٢٣"), 123)
        self.assertEqual(parse_number("۱۲۳"), 123)
        self.assertEqual(parse_number("-٥"), -5)

    def test_separators(self):
        self.assertEqual(parse_number("١٬٢٣٤٫٥"), 1234.5)
        self.assertEqual(parse_number("1,234"), 1234)
        self.assertEqual(parse_number("1,234,567"), 1234567)
        self.assertEqual(parse_number("3,5"), 3.5)
        self.assertEqual(parse_number("12.5"), 12.5)
        self.assertEqual(parse_number("1,234.5"), 1234.5)
        self.assertEqual(parse_number("1.234,5"), 1234.5)

    def test_not_a_number(self):
        for bad in ["", "abc", "1.2.3"]:
            with self.assertRaises(ValueError):
                parse_number(bad)

    def test_extract_with_positions(self):
        text = "سعر ٣٫٥ ريال وعدد 12 و ٤٢٪"
        found = extract_numbers(text)
        self.assertEqual([n.value for n in found], [3.5, 12, 42])
        for n in found:
            self.assertEqual(text[n.start:n.end], n.text)

    def test_digits_glued_to_letters_are_still_numbers(self):
        self.assertEqual([n.value for n in extract_numbers("abc123def 45")], [123, 45])
        self.assertEqual(extract_numbers("1٢3")[0].value, 123)

    def test_digit_conversion(self):
        self.assertEqual(to_eastern(2026), "٢٠٢٦")
        self.assertEqual(to_eastern("a1", persian=True), "a۱")
        self.assertEqual(to_ascii_digits("٢٠٢٦ ۲۰۲۶"), "2026 2026")


class DetectTests(unittest.TestCase):
    def test_ratio_and_rtl(self):
        self.assertEqual(arabic_ratio("hello"), 0.0)
        self.assertEqual(arabic_ratio("محمد"), 1.0)
        self.assertAlmostEqual(arabic_ratio("محمدabcd"), 0.5)
        self.assertTrue(is_rtl("مرحبا بالعالم"))
        self.assertFalse(is_rtl("hello مرحبا world today"))
        self.assertFalse(is_rtl("123"))

    def test_script_runs(self):
        runs = script_runs("iPhone 15 الجديد وصل")
        self.assertEqual([(r.script, r.text) for r in runs], [("latin", "iPhone 15"), ("arabic", "الجديد وصل")])
        text = "iPhone 15 الجديد وصل"
        for r in runs:
            self.assertEqual(text[r.start:r.end], r.text)
        self.assertEqual(script_runs("123 !"), [])
        self.assertEqual([r.script for r in script_runs("مرحبا hello مرحبا")], ["arabic", "latin", "arabic"])

    def test_dialect_hints(self):
        self.assertEqual(dialect_hints("ازاي حالك دلوقتي؟ عايز اروح")["egyptian"], ["ازاي", "دلوقتي", "عايز"])
        self.assertIn("gulf", dialect_hints("شلونك وايد حلو"))
        self.assertIn("maghrebi", dialect_hints("بزاف ديال الناس"))
        self.assertIn("levantine", dialect_hints("هلق كتير منيح"))
        self.assertEqual(dialect_hints("هذا الكتاب جميل جدا"), {})

    def test_dialect_hints_survive_spelling_variation(self):
        self.assertIn("egyptian", dialect_hints("عَايِز"))

    def test_arabizi(self):
        self.assertEqual(arabizi_score("ana 7abibi w 3arabi"), 0.5)
        self.assertEqual(arabizi_score("hello world"), 0.0)
        self.assertEqual(arabizi_score("مرحبا"), 0.0)
        self.assertEqual(arabizi_score("yalla habibi inshallah"), 1.0)

    def test_arabizi_does_not_fire_on_technical_words(self):
        self.assertEqual(arabizi_score("mp3 b2b h2o k8s web3 gpt5 ec2"), 0.0)


if __name__ == "__main__":
    unittest.main()
