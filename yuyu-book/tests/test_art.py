"""The illustration layer: one line drawing per unit, one per part, one plate.

The book inlines every drawing into a single offline file 20+ times over, so
the files themselves carry the guarantees that keep the build valid: no ids
(the audit fails on a duplicate), nothing that reaches outside the document,
and currentColor so one drawing serves paper, screen and dark mode. The cover
plate is inlined once, so it gets a budget of its own.
"""
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from yuyu_book import art, registry  # noqa: E402
from yuyu_book.core import BuildError, unit_stream  # noqa: E402

MANIFEST = registry.load("manifest.json")
UNIT_IDS = [u["id"] for u, _kind, _part in unit_stream(MANIFEST)]
PART_IDS = [p["id"] for p in MANIFEST["parts"]]

GOOD = ('<svg viewBox="0 0 64 64" fill="none" stroke="currentColor">'
        '<circle cx="32" cy="32" r="14"/></svg>')


def _write(tmp: Path, name: str, text: str) -> Path:
    (tmp / f"{name}.svg").write_text(text, encoding="utf-8")
    return tmp




class ShippedDrawings(unittest.TestCase):
    @unittest.skipUnless(art.ART_DIR.exists(), "no illustrations yet")
    def test_every_unit_and_part_has_its_own_drawing(self):
        gaps = art.missing(UNIT_IDS + [f"part-{p}" for p in PART_IDS])
        self.assertEqual(gaps, [], f"units without a drawing: {gaps}")

    @unittest.skipUnless(art.ART_DIR.exists(), "no illustrations yet")
    def test_every_shipped_drawing_passes_the_loader(self):
        # a drawing that breaks the rules must break the build, not be skipped
        for name in UNIT_IDS + [f"part-{p}" for p in PART_IDS]:
            if (art.ART_DIR / f"{name}.svg").exists():
                self.assertTrue(art._read(name), name)

    @unittest.skipUnless(art.ART_DIR.exists(), "no illustrations yet")
    def test_the_drawings_stay_small_enough_to_inline(self):
        for path in sorted(art.ART_DIR.glob("*.svg")):
            budget = art.PLATE_BYTES if path.stem == "cover" else art.MAX_BYTES
            size = len(path.read_text(encoding="utf-8").encode("utf-8"))
            self.assertLessEqual(size, budget, path.name)

    @unittest.skipUnless(art.ART_DIR.exists(), "no illustrations yet")
    def test_every_shipped_plate_stays_inside_its_budget(self):
        for directory in (art.ART_DIR, art.OMP_ART_DIR):
            for path in sorted(directory.glob("*.png")):
                self.assertTrue(path.stem == "cover" or path.stem.startswith("part-"),
                                f"small/semantic artwork must remain SVG: {path.name}")
                budget = art.COVER_RASTER_BYTES if path.stem == "cover" else art.PLATE_RASTER_BYTES
                self.assertLessEqual(path.stat().st_size, budget, path.name)
                width, height = art._png_size(path.read_bytes())
                self.assertTrue(0 < width <= 4096 and 0 < height <= 4096, path.name)

    @unittest.skipUnless(art.ART_DIR.exists(), "no illustrations yet")
    def test_no_drawing_repeats_a_shape_id(self):
        """Every drawing is inlined into one page: a shared id would collide, and the
        duplicate-id audit would fire far from the drawing that caused it."""
        ids = set()
        for path in sorted(art.ART_DIR.glob("*.svg")):
            found = set(re.findall(r"\bid=\"([^\"]+)\"", path.read_text("utf-8")))
            self.assertFalse(found, f"{path.name} declares {sorted(found)}")
            ids |= found

    @unittest.skipUnless(art.ART_DIR.exists(), "no illustrations yet")
    def test_every_shipped_svg_declares_the_svg_namespace(self):
        """独立打开或被 <img>/EPUB 引用时，根元素必须自带 xmlns；
        只靠 HTML 内联时的命名空间推断会让单独使用的插图变成破图。"""
        for directory in (art.ART_DIR, art.PI_ART_DIR, art.AGENT_ART_DIR, art.OMP_ART_DIR):
            for path in sorted(directory.glob("*.svg")):
                root = re.match(r"<svg\b[^>]*>", path.read_text("utf-8"))
                self.assertIsNotNone(root, path.name)
                self.assertIn('xmlns="http://www.w3.org/2000/svg"', root.group(0), path.name)

    @unittest.skipUnless(art.ART_DIR.exists(), "no illustrations yet")
    def test_every_body_drawing_is_named_or_hidden(self):
        """A body drawing is announced once: by its caption, or by itself.

        The figure already carries a `<figcaption>`; an SVG root with neither a
        name nor `aria-hidden` becomes an extra "graphic" stop that reads as
        unlabelled noise on the way to the caption it repeats.
        """
        for path in sorted(art.ART_DIR.glob("*.svg")):
            root = re.match(r"<svg\b[^>]*>", art.drawing(path.stem))
            self.assertIsNotNone(root, path.name)
            tag = root.group(0)
            named = bool(re.search(r'\b(?:aria-label|aria-labelledby)="[^"\s]', tag)
                         or "<title" in art.drawing(path.stem))
            hidden = re.search(r'aria-hidden="true"', tag)
            self.assertTrue(named or hidden, f"{path.name} is unnamed and unhidden: {tag}")
            self.assertFalse(named and hidden, f"{path.name} is both named and hidden")

    def test_a_drawing_that_names_itself_keeps_its_name(self):
        out = art.mark_decorative(
            '<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A cancels">'
            '</svg>')
        self.assertIn('role="img"', out)
        self.assertIn('aria-label="A cancels"', out)
        self.assertNotIn("aria-hidden", out)
        titled = art.mark_decorative("<svg viewBox=\"0 0 8 8\"><title>A cancels</title></svg>")
        self.assertNotIn("aria-hidden", titled)

    def test_role_alone_does_not_name_a_drawing(self):
        out = art.mark_decorative('<svg role="img" viewBox="0 0 8 8"></svg>')
        self.assertIn('aria-hidden="true"', out)
        self.assertEqual(out.count("aria-hidden"), 1)

    def test_an_explicit_show_becomes_a_hide(self):
        out = art.mark_decorative('<svg aria-hidden="false" viewBox="0 0 8 8"></svg>')
        self.assertIn('aria-hidden="true"', out)
        self.assertEqual(out.count("aria-hidden"), 1)

    def test_all_nonbook_products_have_distinct_offline_covers(self):
        products = (
            "llm", "opencode", "deepseek", "hermes", "codex", "t3code",
            "omp", "pi", "kimi", "prompt", "vibe",
        )
        drawings = []
        for product in products:
            drawing = art._read(f"cover-{product}", art.PLATE_BYTES)
            self.assertTrue(drawing, product)
            self.assertIn(drawing, art.cover_plate("zh", product))
            drawings.append(drawing)
        self.assertEqual(len(set(drawings)), len(products))
        self.assertNotIn(drawings[0], art.cover_plate("zh", "book"))


class Loader(unittest.TestCase):
    def setUp(self):
        self._dir = art.ART_DIR
        self._omp = art.OMP_ART_DIR
        self.tmp = Path(tempfile.mkdtemp())
        art.ART_DIR = self.tmp
        # the omp tray is searched first, so a sandboxed loader test has to
        # close it as well or a shipped drawing could answer for a missing one
        art.OMP_ART_DIR = self.tmp / "no-omp-tray"

    def tearDown(self):
        art.ART_DIR = self._dir
        art.OMP_ART_DIR = self._omp

    def test_a_unit_without_a_file_simply_has_no_emblem(self):
        self.assertEqual(art.emblem("ch99"), "")
        self.assertEqual(art.missing(["ch99"]), ["ch99"])

    def test_a_clean_drawing_becomes_hidden_markup(self):
        _write(self.tmp, "ch01", GOOD)
        out = art.emblem("ch01")
        self.assertTrue(out.startswith('<span class="ch-emblem" aria-hidden'))
        self.assertIn("<circle", out)

    def test_a_part_drawing_is_named_after_the_part(self):
        _write(self.tmp, "part-p1", GOOD)
        self.assertIn('class="pd-art"', art.headpiece("p1"))

    def test_the_cover_plate_inlines_as_a_drawing_not_a_bitmap(self):
        _write(self.tmp, "cover", GOOD)
        out = art.cover_plate()
        self.assertIn('class="cover-art"', out)
        self.assertNotIn("<img", out)

    def test_the_plate_gets_a_budget_of_its_own(self):
        # inlined once per edition, so it may run past the emblem cap
        pad = "<!--" + "x" * (art.PLATE_BYTES - 200) + "-->"
        _write(self.tmp, "cover", GOOD.replace("</svg>", pad + "</svg>"))
        self.assertTrue(art.cover_plate())
        with self.assertRaises(BuildError):
            art.emblem("cover")

    def test_a_missing_cover_plate_leaves_the_page_typeset_alone(self):
        self.assertEqual(art.cover_plate(), "")

    def test_a_drawing_that_cannot_re_ink_is_rejected(self):
        _write(self.tmp, "ch01", GOOD.replace("currentColor", "#8A6B3F"))
        with self.assertRaises(BuildError):
            art.emblem("ch01")

    def test_a_drawing_with_an_id_is_rejected(self):
        _write(self.tmp, "ch01", GOOD.replace("<circle", '<circle id="c1"'))
        with self.assertRaises(BuildError):
            art.emblem("ch01")

    def test_a_drawing_that_reaches_outside_the_book_is_rejected(self):
        for bad in (GOOD.replace("</svg>", '<script>x()</script></svg>'),
                    GOOD.replace("</svg>",
                                 '<image href="https://x/y.png"/></svg>'),
                    GOOD.replace("</svg>",
                                 '<path style="fill:url(#g)"/></svg>')):
            _write(self.tmp, "ch01", bad)
            with self.assertRaises(BuildError):
                art.emblem("ch01")

    def test_a_drawing_without_a_viewbox_is_rejected(self):
        _write(self.tmp, "ch01", GOOD.replace('viewBox="0 0 64 64" ', ""))
        with self.assertRaises(BuildError):
            art.emblem("ch01")




