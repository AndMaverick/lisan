import os
import sys
import unittest

from lisan import match_names, skeleton

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "examples"))
from name_pairs import COLLIDE, DIFFERENT, MISSED, SAME  # noqa: E402


class SkeletonTests(unittest.TestCase):
    def test_latin_variants_share_a_skeleton(self):
        for variants in [("Mohammed", "Muhammad", "Mohamad", "Muhammed"), ("Khaled", "Khalid"), ("Youssef", "Yusuf", "Yousef"),
                         ("Hussein", "Husain", "Hussain")]:
            self.assertEqual(len({skeleton(v) for v in variants}), 1, variants)

    def test_arabic_and_latin_land_in_one_alphabet(self):
        self.assertEqual(skeleton("محمد"), skeleton("Muhammad"))
        self.assertEqual(skeleton("خالد"), "xld")

    def test_digraphs(self):
        self.assertEqual(skeleton("Khalid"), "xld")
        self.assertEqual(skeleton("Shaker"), "škr")
        self.assertEqual(skeleton("Dhiyab"), "ðb")

    def test_arabizi_digits(self):
        self.assertEqual(skeleton("7abibi"), skeleton("Habibi"))
        self.assertEqual(skeleton("3ali"), skeleton("Ali"))
        self.assertEqual(skeleton("5aled"), skeleton("Khaled"))
        self.assertEqual(skeleton("9aleh"), skeleton("Qaleh"))

    def test_particles_titles_and_articles_are_set_aside(self):
        self.assertEqual(skeleton("Mohammed bin Rashid Al Maktoum"), skeleton("Mohammed Rashid Maktoum"))
        self.assertEqual(skeleton("Dr. Sheikh Ahmed"), skeleton("Ahmed"))
        self.assertEqual(skeleton("al-Hajri"), skeleton("Hajri"))

    def test_a_name_that_is_only_a_particle_is_kept(self):
        self.assertEqual(skeleton("Al"), "l")


class MatchTests(unittest.TestCase):
    def test_every_same_pair_matches(self):
        missed = [(a, b, round(match_names(a, b).score, 2)) for a, b in SAME if not match_names(a, b).is_match]
        self.assertEqual(missed, [])

    def test_every_different_pair_is_kept_apart(self):
        merged = [(a, b, round(match_names(a, b).score, 2)) for a, b in DIFFERENT if match_names(a, b).is_match]
        self.assertEqual(merged, [])

    def test_the_documented_collisions_collide(self):
        for a, b in COLLIDE:
            self.assertTrue(match_names(a, b).is_match, (a, b))

    def test_the_documented_misses_are_missed(self):
        for a, b in MISSED:
            self.assertFalse(match_names(a, b).is_match, (a, b))

    def test_one_wrong_token_is_not_averaged_away(self):
        m = match_names("Abdul Rahman Mohammed Al Rashid", "Abdul Rahim Mohammed Al Rashid")
        self.assertFalse(m.is_match)
        self.assertLess(m.score, 0.8)

    def test_arabic_to_arabic_keeps_hasan_and_husayn_apart(self):
        self.assertFalse(match_names("حسن", "حسين").is_match)
        self.assertTrue(match_names("حسين", "Hussein").is_match)

    def test_partial_names_report_coverage(self):
        m = match_names("Mohammed Al Rashid", "Mohammed bin Rashid Al Maktoum")
        self.assertTrue(m.is_match)
        self.assertAlmostEqual(m.coverage, 2 / 3)
        self.assertEqual(match_names("Mohammed Rashid", "Muhammad Rashid").coverage, 1.0)

    def test_solid_versus_split_uses_the_joined_form(self):
        m = match_names("Abdul Rahman", "Abdurrahman")
        self.assertEqual(m.method, "joined")
        self.assertTrue(m.is_match)

    def test_short_skeletons_are_flagged_low_confidence(self):
        self.assertEqual(match_names("Ali", "Aly").confidence, "low")
        self.assertEqual(match_names("Mohammed", "Muhammad").confidence, "high")

    def test_threshold_is_applied(self):
        m = match_names("Tariq", "Tarek", threshold=0.95)
        self.assertFalse(m.is_match)
        self.assertTrue(match_names("Tariq", "Tarek", threshold=0.8).is_match)

    def test_empty_and_symmetry(self):
        self.assertEqual(match_names("", "Ali").score, 0.0)
        self.assertEqual(match_names("   ", "").score, 0.0)
        for a, b in SAME[:30] + DIFFERENT[:20]:
            self.assertAlmostEqual(match_names(a, b).score, match_names(b, a).score, msg=(a, b))

    def test_scores_stay_in_range(self):
        for a, b in SAME + DIFFERENT:
            self.assertTrue(0.0 <= match_names(a, b).score <= 1.0)


if __name__ == "__main__":
    unittest.main()
