import os
import sys
import unittest

from lisan import ANALYZERS, Index, char_ngrams, light_stem, tokens

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "examples"))
from search_fixture import DOCS, MORPH_DOCS, MORPH_QUERIES, QUERIES  # noqa: E402


class StemTests(unittest.TestCase):
    def test_definite_article_and_clitic_prefixes(self):
        for word in ["كتاب", "الكتاب", "والكتاب", "بالكتاب", "كالكتاب", "فالكتاب", "للكتاب"]:
            self.assertEqual(light_stem(word), "كتاب", word)

    def test_plural_and_feminine_suffixes(self):
        self.assertEqual({light_stem(w) for w in ["معلم", "معلمون", "معلمين", "معلمات", "المعلمون"]}, {"معلم"})
        self.assertEqual({light_stem(w) for w in ["مدرسة", "المدرسة", "بالمدرسة"]}, {"مدرس"})

    def test_singular_and_plural_of_an_an_word_reach_one_stem(self):
        self.assertEqual(light_stem("الامتحان"), light_stem("بالامتحانات"))

    def test_waw_is_kept_where_it_is_a_root_letter(self):
        for word in ["وزير", "ولد", "والد", "وصل"]:
            self.assertEqual(light_stem(word), word)
        self.assertEqual(light_stem("وكتاب"), "كتاب")

    def test_minimum_stem_is_respected(self):
        self.assertEqual(light_stem("ال"), "ال")
        self.assertEqual(light_stem("بنة", min_stem=3), "بنة")
        self.assertEqual(light_stem("بنات", min_stem=3), "بنات")
        self.assertEqual(light_stem("بنات"), "بن")

    def test_diacritics_do_not_matter(self):
        self.assertEqual(light_stem("المُعَلِّمُونَ"), light_stem("المعلمون"))

    def test_verb_endings_are_not_touched(self):
        self.assertEqual(light_stem("يكتبون"), "يكتب")  # un is stripped like any plural suffix: a light stemmer does not know the part of speech

    def test_known_limits_are_real(self):
        self.assertNotEqual(light_stem("مدارس"), light_stem("مدرسة"))     # broken plural
        self.assertEqual(light_stem("عربي"), "عرب")                        # nisba suffix is over-stripped

    def test_stem_is_never_empty_or_longer_than_the_word(self):
        words = {w for text in [*DOCS.values(), *MORPH_DOCS.values(), *QUERIES.values(), *MORPH_QUERIES.values()] for w in tokens(text, profile="search")}
        self.assertGreater(len(words), 60)
        for w in words:
            stem = light_stem(w)
            self.assertGreaterEqual(len(stem), min(2, len(w)), w)
            self.assertLessEqual(len(stem), len(w), w)

    def test_tokens_stem_option(self):
        self.assertEqual(tokens("الكتاب والمعلمون", stem=True), ["كتاب", "معلم"])

    def test_char_ngrams(self):
        self.assertEqual(char_ngrams("كتاب"), ["_كت", "كتا", "تاب", "اب_"])
        self.assertEqual(char_ngrams("كتاب", 2, pad=False), ["كت", "تا", "اب"])
        self.assertEqual(char_ngrams("", 3), [])
        self.assertEqual(char_ngrams("ا", 3), ["_ا_"])


def success_at_1(analyzer, docs, queries):
    index = Index(analyzer)
    index.add_many({**DOCS, **MORPH_DOCS}.items() if docs == "all" else docs.items())
    return sum(1 for target, query in queries.items() if (hits := index.search(query, 1)) and hits[0].id == target)


class SearchTests(unittest.TestCase):
    def test_spelling_variation_breaks_raw_matching_and_normalization_fixes_it(self):
        raw = success_at_1("raw", "all", QUERIES)
        normalized = success_at_1("normalized", "all", QUERIES)
        self.assertEqual(normalized, len(QUERIES))
        self.assertLess(raw, normalized - 5)

    def test_inflection_needs_stemming(self):
        self.assertEqual(success_at_1("normalized", "all", MORPH_QUERIES), 0)
        self.assertEqual(success_at_1("stemmed", "all", MORPH_QUERIES), len(MORPH_QUERIES) - 1)  # the broken plural is the one miss
        self.assertGreaterEqual(success_at_1("trigram", "all", MORPH_QUERIES), 4)

    def test_every_analyzer_name_works(self):
        for name in ANALYZERS:
            index = Index(name)
            index.add("a", "مكتبة جديدة")
            self.assertEqual(index.search("مكتبة")[0].id, "a")

    def test_custom_analyzer_and_errors(self):
        index = Index(lambda text: text.split())
        index.add("a", "x y")
        with self.assertRaises(ValueError):
            index.add("a", "again")
        with self.assertRaises(ValueError):
            Index("nope")
        self.assertEqual(index.search("zzz"), [])
        self.assertEqual(Index().search("x"), [])
        self.assertEqual(len(index), 1)

    def test_ranking_prefers_the_rarer_term_and_ties_break_by_id(self):
        index = Index("normalized")
        index.add_many([("b", "نفط غاز"), ("a", "نفط غاز"), ("c", "غاز")])
        self.assertEqual([h.id for h in index.search("نفط")], ["a", "b"])
        self.assertEqual([h.id for h in index.search("نفط غاز")], ["a", "b", "c"])

    def test_k_limits_results(self):
        index = Index("normalized")
        index.add_many([(str(i), "كلمة") for i in range(5)])
        self.assertEqual(len(index.search("كلمة", k=3)), 3)


if __name__ == "__main__":
    unittest.main()
