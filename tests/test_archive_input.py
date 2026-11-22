"""Regression tests for the exact checker script served in archives."""
import json
import pathlib
import re
import shutil
import subprocess
import unittest

import build


CASES = [
    ("6456549", 0), ("645654071470", 0), ("x645654", 0),
    ("645654 12345", 0), ("", 0), ("645654 " * 21, 0),
    ("645654", 1), ("071470", 1), ("๐๗๑๔๗๐", 1),
    ("645654\n071470", 2), ("000000 " * 20, 20),
]
ROOT = pathlib.Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node is needed to exercise archive JavaScript")
class ArchiveInputTests(unittest.TestCase):
    def exercise(self, page):
        script = re.search(r"<script>(var SLK=.*?)</script>", page, re.S)[1]
        cases = [x for x, _ in CASES]
        setup = """const out={};const q={addEventListener(){}};const go={};
const document={getElementById:id=>({out,q,go})[id]};"""
        driver = """
const results = CASES.map(value => {
  q.value=value;go.onclick();
  return out.innerHTML;
});
console.log(JSON.stringify(results));""".replace("CASES", json.dumps(cases))
        results = json.loads(subprocess.check_output(["node", "-e", setup + script + driver], text=True))
        for (raw, expected), result in zip(CASES, results):
            with self.subTest(raw=raw):
                self.assertEqual(result.count('<div class="res '), expected)
        self.assertIn("รางวัลที่ 1", results[6])
        for idx in (7, 8, 9):
            self.assertIn("<b>071470</b>", results[idx])
            self.assertIn("รางวัลที่ 2", results[idx])

    def test_template(self):
        self.exercise(build.checker_html({"first": "645654", "last2": "06", "second": ["071470"]}))

    def test_published_archive_fixture(self):
        self.exercise((ROOT / "r/20261116/index.html").read_text(encoding="utf-8"))
