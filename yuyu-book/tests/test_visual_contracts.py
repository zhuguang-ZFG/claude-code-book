"""Inked-plate animation must not overwrite an authored dash rhythm.

The guard is a computed-style contract, not a source-text check: the same
CSS is valid with or without the :not() exclusion, but only one version
keeps a dashed blueprint path dashed once the scroll animation applies.
"""
import re
import sys
import unittest
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from playwright.sync_api import sync_playwright
from yuyu_book.pdf import _launch
from yuyu_book.style_css import CSS

# The ink selectors are scoped to .illu-frame (style_screen.py), and the
# shipped markup is figure.illu > .illu-frame > svg. A bare figure.illu
# would match no animation rule and make this guard pass vacuously.
FIXTURE = """<html><head><style>__CSS__</style></head>
<body class="lang-zh"><article><div class="chapter-body">
<figure class="illu illu-photo"><div class="illu-frame">
<svg viewBox="0 0 340 130" fill="none" stroke="currentColor">
<path id="dashed" d="M190 36q64 -16 126 -25" pathLength="100" stroke-dasharray="2 6"/>
<path id="solid" d="M10 10h100" pathLength="100"/>
</svg></div><figcaption>plate</figcaption></figure>
</div></article></body></html>"""


def _dash_parts(value):
    return tuple(float(part) for part in re.findall(r"[\d.]+", value))


class InkedPlateContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = _launch(cls.playwright, None)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def _probe(self, css, reduced_motion):
        page = self.browser.new_page()
        try:
            page.set_content(FIXTURE.replace("__CSS__", css))
            page.emulate_media(reduced_motion=reduced_motion)
            return page.evaluate("""() => {
                const read = id => {
                    const s = getComputedStyle(document.getElementById(id));
                    return {dash: s.strokeDasharray, animation: s.animationName};
                };
                return {timeline: CSS.supports('animation-timeline', 'view()'),
                        dashed: read('dashed'), solid: read('solid')};
            }""")
        finally:
            page.close()

    def _require_timeline(self, values):
        # An unsupported browser means this branch was NOT tested. A skip
        # here would turn an untested animation contract into a false pass.
        if not values["timeline"]:
            self.fail("animation-timeline:view() unsupported: "
                      "ink-draw/ink-fade branch is untested, not passed")

    def test_a_dashed_path_keeps_its_authored_rhythm_and_fades(self):
        values = self._probe(CSS, "no-preference")
        self._require_timeline(values)
        self.assertEqual(_dash_parts(values["dashed"]["dash"]), (2.0, 6.0))
        self.assertEqual(values["dashed"]["animation"], "ink-fade")

    def test_a_solid_path_still_draws_in_with_the_full_dash(self):
        values = self._probe(CSS, "no-preference")
        self._require_timeline(values)
        self.assertEqual(_dash_parts(values["solid"]["dash"]), (100.0, 100.0))
        self.assertEqual(values["solid"]["animation"], "ink-draw")

    def test_the_guard_would_catch_the_old_dash_overriding_css(self):
        old = CSS.replace(":not([stroke-dasharray])", "")
        self.assertNotEqual(old, CSS, "the fixture must change the shipped CSS")
        values = self._probe(old, "no-preference")
        self._require_timeline(values)
        # This is the exact regression the guard exists to reject.
        self.assertEqual(_dash_parts(values["dashed"]["dash"]), (100.0, 100.0))
        self.assertEqual(values["dashed"]["animation"], "ink-draw")

    def test_reduced_motion_leaves_both_paths_static(self):
        values = self._probe(CSS, "reduce")
        self.assertEqual(values["dashed"]["animation"], "none")
        self.assertEqual(values["solid"]["animation"], "none")


if __name__ == "__main__":
    unittest.main()
