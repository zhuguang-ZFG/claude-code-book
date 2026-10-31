"""The station and plate counts are quoted on the social card, in every station
label, and on the portal; a stale number is exactly what a reader checks."""

from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_beginner_reader as reader  # noqa: E402

# per language: (file, how the count is quoted in og:description, station label)
EDITIONS = {
    "zh": ("docs/beginner-reader.html", r"的 (\d+) 站看图入门", r"第 (\d+) / (\d+) 站"),
    "en": ("docs/beginner-reader.en.html", r"in (\d+) stations", r"Station (\d+) / (\d+)"),
}


class StationCounts(unittest.TestCase):
    def test_both_editions_walk_the_same_number_of_stations(self):
        self.assertEqual(reader.LANGS["zh"]["total"], reader.LANGS["en"]["total"],
                         "the two readers are the same walk; one edition grew a station")

    def test_the_count_is_derived_from_the_station_lists(self):
        for lang, t in reader.LANGS.items():
            want = sum(len(us) for _, _, _, us in t["parts"]) + len(reader.APPENDIX_STATIONS)
            self.assertEqual(t["total"], want, f"{lang}: total is not derived")

    def test_the_quoted_count_matches_the_labels_in_the_page(self):
        for lang, (path, og, label) in EDITIONS.items():
            page = (ROOT / path).read_text(encoding="utf-8")
            nums = [(int(n), int(total)) for n, total in re.findall(label, page)]
            self.assertTrue(nums, f"{path}: no station labels parsed")
            self.assertEqual(max(n for n, _ in nums), reader.LANGS[lang]["total"],
                             f"{path}: the walk stops short of its declared length")
            self.assertEqual({total for _, total in set(nums)},
                             {reader.LANGS[lang]["total"]},
                             f"{path}: the labels disagree about the total")
            m = re.search(og, page)
            self.assertIsNotNone(m, f"{path}: the social card no longer quotes the count")
            self.assertEqual(int(m.group(1)), reader.LANGS[lang]["total"],
                             f"{path}: the card says {m.group(1)}, the walk has "
                             f"{reader.LANGS[lang]['total']} stations")


class StationFurniture(unittest.TestCase):
    def test_no_station_shows_its_internal_id(self):
        for lang, (path, _og, _label) in EDITIONS.items():
            page = (ROOT / path).read_text(encoding="utf-8")
            leaked = re.findall(r"<h2>(ch\d\d|apx[a-d]|front|keeper)</h2>", page)
            self.assertEqual(leaked, [], f"{path}: raw anchor ids as headings: {leaked}")

    def test_every_station_carries_a_drawing(self):
        for lang, (path, _og, _label) in EDITIONS.items():
            page = (ROOT / path).read_text(encoding="utf-8")
            empty = [art for art in re.findall(
                r'<div class="st-art"[^>]*>([\s\S]{0,40})', page)
                if not art.lstrip().startswith("<svg")]
            self.assertEqual(empty, [], f"{path}: {len(empty)} stations have no plate")

    def test_the_plate_count_is_the_illustrations_on_disk(self):
        self.assertEqual(reader.PLATES, len(list(reader.ART.glob("*.svg"))))

    def test_the_shipped_pages_all_quote_that_plate_count(self):
        """The gallery, the portal and both readers advertise the same drawing
        shelf; a page that still says the old number is a page nobody re-ran."""
        quoted = {
            "docs/illustration-gallery.html": f"{reader.PLATES} 幅手绘插图",
            "docs/portal.html": f"{reader.PLATES} 幅手绘插图",
            "docs/beginner-reader.html": f"{reader.PLATES} 幅手绘插图",
            "docs/beginner-reader.en.html": f"{reader.PLATES} hand-inked figures",
        }
        for path, text in quoted.items():
            page = (ROOT / path).read_text(encoding="utf-8")
            self.assertIn(text, page, f"{path}: does not quote {text}")


class EditionBaseline(unittest.TestCase):
    def test_the_reader_names_the_edition_it_was_cut_from(self):
        want = json.loads(
            (ROOT / "yuyu-book" / "manifest.json").read_text(encoding="utf-8")
        )["version"]
        for _lang, (path, _og, _label) in EDITIONS.items():
            page = (ROOT / path).read_text(encoding="utf-8")
            self.assertNotIn("@@", page, f"{path}: an unfilled token shipped")
            m = re.search(r"(?:对应大书|baseline) v(\d+\.\d+\.\d+)", page)
            self.assertIsNotNone(m, f"{path}: no book edition quoted in the footer")
            self.assertEqual(m.group(1), want,
                             f"{path}: says v{m.group(1)}, the book is v{want}")


if __name__ == "__main__":
    unittest.main()
