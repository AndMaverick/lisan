import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from lisan.cli import main


def run(*argv, stdin=""):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), mock.patch("sys.stdin", io.StringIO(stdin)):
        code = main(list(argv))
    return code, out.getvalue(), err.getvalue()


class CliTests(unittest.TestCase):
    def test_normalize_from_stdin(self):
        code, out, _ = run("normalize", "-", stdin="مُدَرِّسَةٌ\n١٢\n")
        self.assertEqual((code, out), (0, "مدرسه\n12\n"))

    def test_normalize_profile_and_digits(self):
        self.assertEqual(run("normalize", "--profile", "legacy", "--digits", "eastern", stdin="مدرسة 12")[1], "مدرسة ١٢\n")

    def test_clean(self):
        self.assertEqual(run("clean", stdin="  ﷲ‏  أكبر ")[1], "الله أكبر\n")

    def test_tokens_with_stem(self):
        self.assertEqual(run("tokens", "--stem", stdin="الكتاب والمعلمون")[1], "كتاب\nمعلم\n")

    def test_translit_both_ways(self):
        self.assertEqual(run("translit", stdin="كتاب\n")[1], "ktAb\n")
        self.assertEqual(run("translit", "--reverse", stdin="ktAb\n")[1], "كتاب\n")

    def test_numbers(self):
        self.assertEqual(run("numbers", stdin="سعر ٣٫٥ و 12")[1], "3.5\t٣٫٥\n12\t12\n")

    def test_detect_and_gate(self):
        code, out, _ = run("detect", stdin="مرحبا hello")
        data = json.loads(out)
        self.assertEqual(code, 0)
        self.assertAlmostEqual(data["arabic_ratio"], 5 / 10)
        self.assertEqual([r["script"] for r in data["runs"]], ["arabic", "latin"])
        code, _, err = run("detect", "--min-arabic", "0.9", stdin="مرحبا hello")
        self.assertEqual(code, 1)
        self.assertIn("gate", err)
        self.assertEqual(run("detect", "--min-arabic", "0.9", stdin="مرحبا")[0], 0)

    def test_match_exit_codes(self):
        code, out, _ = run("match", "محمد", "Muhammad")
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(out)["match"])
        code, out, _ = run("match", "محمد", "Ahmed")
        self.assertEqual(code, 1)
        self.assertFalse(json.loads(out)["match"])
        self.assertEqual(run("match", "Tariq", "Tarek", "--threshold", "0.95")[0], 1)

    def test_missing_file_exits_2(self):
        code, _, err = run("normalize", "/no/such/file.txt")
        self.assertEqual(code, 2)
        self.assertIn("error", err)

    def test_reads_a_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "t.txt")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("مدرسة")
            self.assertEqual(run("normalize", path)[1], "مدرسه\n")

    def test_module_entry_point(self):
        proc = subprocess.run([sys.executable, "-m", "lisan", "match", "خالد", "Khaled"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(json.loads(proc.stdout)["match"])


if __name__ == "__main__":
    unittest.main()
