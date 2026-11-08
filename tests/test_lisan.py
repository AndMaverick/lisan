import unittest

from lisan import arabic_ratio, is_arabic_letter, normalize, search_key, tokens

MUHAMMAD_VOWELED = "مُحَمَّد"
MUHAMMAD = "محمد"


class LisanTests(unittest.TestCase):
    def test_diacritics_removed(self):
        self.assertEqual(normalize(MUHAMMAD_VOWELED), MUHAMMAD)

    def test_alef_variants_unified(self):
        self.assertEqual(normalize("أحمد"), "احمد")
        self.assertEqual(normalize("إسلام"), "اسلام")

    def test_tatweel_removed(self):
        self.assertEqual(normalize("مــن"), "من")

    def test_yeh_unified(self):
        self.assertEqual(normalize("على"), "علي")

    def test_eastern_digits_become_ascii(self):
        self.assertEqual(normalize("١٢٣"), "123")
        self.assertEqual(normalize("۴۵"), "45")

    def test_ta_marbuta_is_opt_in(self):
        word = "مدرسة"
        self.assertEqual(normalize(word), word)
        self.assertEqual(normalize(word, ta_marbuta=True), "مدرسه")

    def test_latin_passes_through(self):
        self.assertEqual(normalize("Dubai 2026"), "Dubai 2026")

    def test_arabic_ratio(self):
        self.assertEqual(arabic_ratio("hello"), 0.0)
        self.assertEqual(arabic_ratio(MUHAMMAD), 1.0)
        self.assertAlmostEqual(arabic_ratio(MUHAMMAD + "abcd"), 0.5)
        self.assertEqual(arabic_ratio("123"), 0.0)

    def test_tokens_and_search_key(self):
        self.assertEqual(tokens(MUHAMMAD_VOWELED + " Ali"), [MUHAMMAD, "Ali"])
        self.assertEqual(search_key("  " + MUHAMMAD_VOWELED + "   ALI "), MUHAMMAD + " ali")

    def test_is_arabic_letter(self):
        self.assertTrue(is_arabic_letter("م"))
        self.assertFalse(is_arabic_letter("m"))


if __name__ == "__main__":
    unittest.main()
