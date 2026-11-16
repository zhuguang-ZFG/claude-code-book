"""Every page the site ships must work without a mouse, make sense to a
screen reader, admit which colour scheme it supports, and stop animating when
the reader asked it to.

The generators differ; the contract does not. These tests read the committed
HTML — what a browser and a crawler actually receive — and refuse a page that
drops a landmark, hides focus, forgets its language, or animates past a
reduced-motion setting.
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "yuyu-book" / "dist"
sys.path.insert(0, str(ROOT / "yuyu-book"))

PAGES = {
    "docs/portal.html": "zh",
    "docs/beginner-reader.html": "zh",
    "docs/illustration-gallery.html": "zh",
    "docs/knowledge-cards.html": "zh",
    "docs/sample-chapter.html": "zh",
}
# Imported after sys.path so the test reads the gate's own scanner.
from yuyu_book.audit import exposed_svgs  # noqa: E402
# The sample rehosts a book chapter verbatim; the book's own guide band uses
# h4 labels under the chapter h1 by design, so heading-order is checked on the
# product shells only.
SAMPLE = {"docs/sample-chapter.html"}


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def styles(page: str) -> str:
    return "\n".join(re.findall(r"<style>(.*?)</style>", page, re.S))


def media_block(css: str, condition: str) -> str:
    """The body of the first @media whose condition matches `condition`."""
    for match in re.finditer(r"@media[^{]*\{", css):
        if not re.search(condition, match.group(0)):
            continue
        depth, index = 1, match.end()
        start = index
        while index < len(css) and depth:
            if css[index] == "{":
                depth += 1
            elif css[index] == "}":
                depth -= 1
            index += 1
        return css[start:index - 1]
    return ""


def exposed_unnamed_svgs(page: str) -> list[str]:
    """The gate's own scanner, so a test cannot drift from what a build refuses."""
    return exposed_svgs(page)


class SvgExposure(unittest.TestCase):
    def test_a_bare_drawing_is_flagged(self):
        self.assertEqual(exposed_unnamed_svgs('<svg viewBox="0 0 1 1"></svg>'),
                         ["<no class>"])

    def test_a_wrapper_hides_everything_inside_it(self):
        page = '<div aria-hidden="true"><span><svg class="a-x"></svg></span></div>'
        self.assertEqual(exposed_unnamed_svgs(page), [])

    def test_a_named_drawing_is_left_alone(self):
        page = ('<svg role="img" aria-label="Pausing differs from cancelling">'
                '</svg><svg aria-labelledby="cap-1"></svg>'
                '<svg aria-hidden="true"></svg>')
        self.assertEqual(exposed_unnamed_svgs(page), [])

    def test_role_alone_is_not_a_name(self):
        page = '<svg class="flowchart" role="graphics-document document"></svg>'
        self.assertEqual(exposed_unnamed_svgs(page), ["flowchart"])

    def test_aria_hidden_false_stays_exposed(self):
        page = '<svg class="a-x" aria-hidden="false" role="img"></svg>'
        self.assertEqual(exposed_unnamed_svgs(page), ["a-x"])

    def test_an_empty_label_is_not_a_name(self):
        page = '<svg aria-label="" aria-labelledby="  "></svg>'
        self.assertEqual(exposed_unnamed_svgs(page), ["<no class>"])


class PageContracts(unittest.TestCase):
    def test_every_page_is_one_offline_file(self):
        for path in PAGES:
            page = read(path)
            css = styles(page)
            self.assertNotIn("@import", css, path)
            self.assertIsNone(re.search(r'src="https?://', page), path)
            self.assertIsNone(re.search(r'url\(\s*["\']?https?://', css), path)
            self.assertNotIn('<link rel="stylesheet"', page, path)

    def test_every_page_declares_language_viewport_and_title(self):
        for path, lang in PAGES.items():
            page = read(path)
            self.assertRegex(page, rf'<html lang="{lang}', path)
            viewport = re.search(
                r'<meta name="viewport" content="([^"]+)"', page)
            self.assertIsNotNone(viewport, path)
            self.assertIn("width=device-width", viewport.group(1), path)
            self.assertNotIn("user-scalable=no", viewport.group(1), path)
            self.assertNotIn("maximum-scale=1", viewport.group(1), path)
            title = re.search(r"<title>(.*?)</title>", page, re.S)
            self.assertIsNotNone(title, path)
            self.assertTrue(title.group(1).strip(), path)

    def test_every_page_has_one_h1_and_the_three_landmarks(self):
        for path in PAGES:
            page = read(path)
            self.assertEqual(len(re.findall(r"<h1\b", page)), 1, path)
            for tag in ("header", "main", "footer"):
                self.assertRegex(page, rf"<{tag}\b", path)

    def test_headings_never_skip_a_level(self):
        for path in PAGES:
            if path in SAMPLE:
                continue
            levels = [int(level) for level in
                      re.findall(r"<h([1-6])\b", read(path))]
            skips = [(a, b) for a, b in zip(levels, levels[1:]) if b > a + 1]
            self.assertEqual(skips, [], path)

    def test_focus_has_a_visible_style(self):
        for path in PAGES:
            css = styles(read(path))
            self.assertIn(":focus-visible", css, path)
            block = css[css.index(":focus-visible"):]
            self.assertRegex(block, r"outline\s*:", path)

    def test_every_control_is_keyboard_reachable_and_named(self):
        for path in PAGES:
            page = read(path)
            for tag in re.findall(r"<a\b[^>]*>", page):
                self.assertIn("href=", tag, path)
            for opening, text in re.findall(
                    r"(<button\b[^>]*>)(.*?)</button>", page, re.S):
                self.assertTrue(text.strip() or "aria-label=" in opening, path)
            for tag in re.findall(r"<[^>]+role=\"button\"[^>]*>", page):
                self.assertIn('tabindex="0"', tag, path)
                self.assertRegex(tag, r'aria-label="[^"]+"', path)
            self.assertIsNone(re.search(r'tabindex="[1-9]', page), path)

    def test_images_and_named_graphics_carry_a_name(self):
        for path in PAGES:
            page = read(path)
            for tag in re.findall(r"<img\b[^>]*>", page):
                self.assertRegex(tag, r'alt="[^"]+"', path)
            for tag in re.findall(r"<svg\b[^>]*>", page):
                if 'role="img"' in tag:
                    self.assertRegex(tag, r'aria-label="[^"]+"', path)

    def test_every_exposed_drawing_is_named_or_hidden(self):
        """A plate repeats its caption; one announced bare reads as noise.

        Hidden on the SVG itself or on a wrapper both count — the drawing
        shelf wraps its plates rather than editing 46 files — but something
        has to say it, and `role="img"` without a label does not.
        """
        for path in PAGES:
            page = read(path)
            exposed = exposed_unnamed_svgs(page)
            self.assertEqual(exposed, [], f"{path}: {len(exposed)} drawings "
                                          f"announce nothing: {exposed[:3]}")

    def test_the_built_books_name_every_exposed_plate(self):
        """The products above copy a chapter; the books themselves are bigger.

        They ship 160-1400 Mermaid roots apiece, each rendered by the same
        `mermaid_figure`, so this is where a missing name actually shows up.
        `dist/` is generated, so a bare checkout skips rather than fails.
        """
        built = sorted(DIST.glob("*.html"))
        if not built:
            self.skipTest("no built books in dist/ (run `bookctl.py build`)")
        for path in built:
            page = path.read_text(encoding="utf-8")
            exposed = exposed_unnamed_svgs(page)
            self.assertEqual(exposed, [], f"{path.name}: {len(exposed)} drawings "
                                          f"announce nothing: {exposed[:3]}")

    def test_every_page_states_its_colour_scheme(self):
        for path in PAGES:
            page = read(path)
            meta = re.search(
                r'<meta name="color-scheme" content="([^"]+)">', page)
            self.assertIsNotNone(meta, path)
            scheme = meta.group(1)
            self.assertIn(scheme, ("light", "light dark"), path)
            dark = re.search(r"prefers-color-scheme\s*:\s*dark",
                             styles(page))
            if scheme == "light dark":
                self.assertIsNotNone(dark, path)
            else:
                self.assertIsNone(dark, path)

    def test_animation_is_cancelled_for_reduced_motion(self):
        for path in PAGES:
            css = styles(read(path))
            if "@keyframes" not in css:
                continue
            block = media_block(css, r"prefers-reduced-motion\s*:\s*reduce")
            self.assertTrue(block, f"{path}: no reduced-motion block")
            self.assertIn("animation:none", block.replace(" ", ""), path)

    def test_the_gallery_does_not_autoplay_for_reduced_motion(self):
        page = read("docs/illustration-gallery.html")
        guard = re.search(
            r'matchMedia\("\(prefers-reduced-motion: reduce\)"\)', page)
        self.assertIsNotNone(guard)

    def test_fixed_art_panels_are_capped_for_narrow_screens(self):
        for path in PAGES:
            page = read(path)
            css = styles(page)
            self.assertRegex(css, r"max-width\s*:", path)
            if 'style="width:' in page:
                self.assertIn("max-width:100%", css, path)

    def test_every_page_links_back_into_the_site(self):
        for path in PAGES:
            page = read(path)
            self.assertRegex(
                page, r'href="(?!https?:|#|mailto:)[^"]+\.html(?:#|")', path)
            if path != "docs/portal.html":
                self.assertIn('href="portal.html"', page, path)


if __name__ == "__main__":
    unittest.main()
