"""The index folio retry: one re-measure, then the build still fails closed.

An empty index slot and a filled one can lay out differently, so the numbers
measured before inking may describe pages that moved. The build re-measures the
filled HTML once; a second mismatch is still an error.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "yuyu-book"))

from yuyu_book import app  # noqa: E402
from yuyu_book.core import BuildError  # noqa: E402

DRIFT = "pdf: 2 index folio(s) moved between the measuring print and this one"


class FakePdf:
    """Two measurements that disagree, then a build that settles."""

    def __init__(self, drifts: int):
        self.drifts = drifts
        self.measures: list[int] = []
        self.builds: list[dict] = []

    def measure(self, out, anchors, browser):
        self.measures.append(len(anchors))
        page = 40 + 10 * (len(self.measures) - 1)
        return {anchor: page for anchor in anchors}

    def build_pdf(self, out, meta, browser, folios=None, **kwargs):
        self.builds.append(dict(folios or {}))
        if self.drifts:
            self.drifts -= 1
            raise BuildError(DRIFT)
        return Path("book.pdf")


def meta(anchors=("ch01", "ch02")):
    return SimpleNamespace(index_rows=[SimpleNamespace(anchor=a) for a in anchors])


class FolioRetry(unittest.TestCase):
    def run_build(self, pdf, pmeta=None, html="<p>sheet</p>"):
        real_fill = app.pages.fill_index_folios
        app.pages.fill_index_folios = lambda text, folios: text
        self.addCleanup(setattr, app.pages, "fill_index_folios", real_fill)
        temporary = tempfile.TemporaryDirectory(prefix="folio-retry-")
        self.addCleanup(temporary.cleanup)
        out = Path(temporary.name) / "book.html"
        return app.print_with_index(pdf, out, html, pmeta or meta(), None)

    def test_stable_layout_measures_and_prints_once(self):
        pdf = FakePdf(drifts=0)
        path, folios = self.run_build(pdf)
        self.assertEqual(path, Path("book.pdf"))
        self.assertEqual(len(pdf.measures), 1)
        self.assertEqual(len(pdf.builds), 1)
        self.assertEqual(folios, {"ch01": 41, "ch02": 41})

    def test_a_repaged_index_is_measured_again_and_printed_once_more(self):
        pdf = FakePdf(drifts=1)
        _, folios = self.run_build(pdf)
        self.assertEqual(len(pdf.measures), 2)
        self.assertEqual(len(pdf.builds), 2)
        self.assertEqual(folios, {"ch01": 51, "ch02": 51},
                         "the shipped folios must come from the second print")

    def test_a_second_drift_still_fails_the_build(self):
        pdf = FakePdf(drifts=2)
        with self.assertRaises(BuildError):
            self.run_build(pdf)
        self.assertEqual(len(pdf.builds), 2, "only one retry is allowed")

    def test_other_build_errors_are_not_retried(self):
        pdf = FakePdf(drifts=0)
        pdf.build_pdf = lambda *a, **k: (_ for _ in ()).throw(
            BuildError("pdf: no CJK face available"))
        with self.assertRaises(BuildError):
            self.run_build(pdf)
        self.assertEqual(len(pdf.measures), 1)

    def test_a_book_without_an_index_prints_directly(self):
        pdf = FakePdf(drifts=0)
        blank = SimpleNamespace(index_rows=[])
        _, folios = self.run_build(pdf, pmeta=blank)
        self.assertEqual(pdf.measures, [])
        self.assertEqual(folios, {})


if __name__ == "__main__":
    unittest.main()
