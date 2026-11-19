import unittest

from lisan import PROFILES, clean, normalize, search_key, tokens


class LegacyCompatibilityTests(unittest.TestCase):
    def test_default_is_the_old_behaviour(self):
        for text in ["مُحَمَّد", "أحمد إسلام آمنة", "مــن", "على", "١٢٣ ۴۵", "مدرسة", "Dubai 2026"]:
            self.assertEqual(normalize(text), normalize(text, profile="legacy"))
        self.assertEqual(normalize("مدرسة"), "مدرسة")
        self.assertEqual(normalize("كتابک"), "كتابک")  # Persian kaf is left alone unless asked

    def test_search_key_default_folds_teh_marbuta_only(self):
        self.assertEqual(search_key("  مدرسة   ALI "), "مدرسه ali")

    def test_tokens_default(self):
        self.assertEqual(tokens("الكِتَاب الجَديد"), ["الكتاب", "الجديد"])


class ProfileTests(unittest.TestCase):
    def test_unknown_profile_and_digit_mode(self):
        with self.assertRaises(ValueError):
            normalize("x", profile="nope")
        with self.assertRaises(ValueError):
            normalize("x", digits="roman")

    def test_nfkc_unfolds_presentation_forms_and_ligatures(self):
        self.assertEqual(normalize("ﷲ", profile="clean"), "الله")          # the Allah ligature
        self.assertEqual(normalize("ﻻ", profile="clean"), "لا")            # isolated lam-alef
        self.assertEqual(normalize("ﺍﻟ", profile="clean"), "ال")      # isolated alef, initial lam

    def test_controls_are_removed(self):
        self.assertEqual(normalize("ab‏ج‮​", profile="clean"), "abج")
        self.assertEqual(normalize("ab‏ج", profile="legacy"), "ab‏ج")

    def test_quranic_marks(self):
        self.assertEqual(normalize("بِسْمِ ٱللَّهِ۝", profile="clean"), "بسم الله")

    def test_persian_letters(self):
        self.assertEqual(normalize("کی", persian=True), "كي")
        self.assertEqual(normalize("ہھە", persian=True), "ههه")
        self.assertEqual(normalize("مرکز", profile="search"), "مركز")

    def test_hamza_spellings_of_one_word_compare_equal(self):
        self.assertEqual(normalize("مسؤول", profile="search"), normalize("مسئول", profile="search"))
        self.assertEqual(normalize("مسؤول", profile="search"), "مسول")

    def test_hamza_is_off_unless_asked(self):
        self.assertNotEqual(normalize("مسؤول"), normalize("مسئول"))

    def test_punctuation(self):
        self.assertEqual(normalize("كيف حالك؟ ٣٫٥٪", profile="search"), "كيف حالك? 3.5%")
        self.assertEqual(normalize("«نص»", profile="search"), '"نص"')

    def test_digit_modes(self):
        self.assertEqual(normalize("١٢۳"), "123")
        self.assertEqual(normalize("١٢", digits="keep"), "١٢")
        self.assertEqual(normalize("12", digits="eastern"), "١٢")
        self.assertEqual(normalize("١٢", digits="persian"), "۱۲")
        self.assertEqual(normalize("12 ab", digits="persian"), "۱۲ ab")

    def test_override_beats_profile(self):
        self.assertEqual(normalize("مدرسة", profile="search"), "مدرسه")
        self.assertEqual(normalize("مدرسة", profile="search", ta_marbuta=False), "مدرسة")

    def test_search_profile_makes_spellings_of_one_word_equal(self):
        variants = ["الجامعة", "الجامعه", "اَلْجَامِعَةُ", "ﺍﻟﺠﺎﻣﻌﺔ"]
        self.assertEqual(len({normalize(v, profile="search") for v in variants}), 1)

    def test_normalization_is_idempotent(self):
        for text in ["مُحَمَّد ﷲ ۱۲۳ کی مسؤول", "ab‏ ج", "إِبْرَاهِيمُ"]:
            for profile in PROFILES:
                once = normalize(text, profile=profile)
                self.assertEqual(normalize(once, profile=profile), once, (text, profile))

    def test_clean_keeps_diacritics_and_collapses_space(self):
        self.assertEqual(clean("  مُحَمَّد‏ \n  ﷲ "), "مُحَمَّد الله")


if __name__ == "__main__":
    unittest.main()
