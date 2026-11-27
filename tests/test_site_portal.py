from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_site_portal  # noqa: E402


class PortalPresentation(unittest.TestCase):
    def test_portal_has_no_nonessential_card_motion(self):
        page = build_site_portal.PAGE
        self.assertNotIn("@keyframes", page)
        self.assertNotIn("animation:", page)
        self.assertNotRegex(page, r"transition:[^;}]*transform")

    def test_the_committed_portal_matches_its_generator(self):
        committed = (ROOT / "docs" / "portal.html").read_text(encoding="utf-8")
        self.assertEqual(committed, build_site_portal.PAGE)

    def test_the_front_door_quotes_the_counts_the_builders_derive(self):
        """Cards advertise the readers and the gallery; a stale number is the
        first thing a visitor checks against the page it links to."""
        import build_beginner_reader as reader
        self.assertNotIn("@@", build_site_portal.PAGE, "unfilled token in the portal")
        self.assertIn(f"{reader.LANGS['zh']['total']} 站看图入门",
                      build_site_portal.PAGE)
        self.assertIn(f"{reader.PLATES} 幅手绘插图", build_site_portal.PAGE)

    def test_the_deployed_variant_links_the_omp_volume(self):
        """The committed portal has no omp page to point at; the Pages copy
        gains the link only when the workflow shipped that file."""
        live = build_site_portal.page(omp_live=True)
        self.assertIn('href="omp/yuyu-omp-zh.html"', live)
        self.assertNotIn("@@", live)
        self.assertNotIn('href="omp/yuyu-omp-zh.html"', build_site_portal.PAGE)


class PortalInformationArchitecture(unittest.TestCase):
    def test_front_door_is_a_quiet_document_index(self):
        page = build_site_portal.PAGE
        self.assertIn('<a class="skip-link" href="#content">跳到主要内容</a>',
                      page)
        self.assertIn('<main id="content" tabindex="-1">', page)
        self.assertIn('<nav class="cards" aria-label="阅读入口">', page)
        self.assertIn("</nav>", page)
        self.assertLess(page.index('href="beginner-reader.html"'),
                        page.index('href="yuyu-agent-harness-zh.html"'))
        self.assertLess(page.index('href="yuyu-agent-harness-zh.html"'),
                        page.index('href="sample-chapter.html"'))
        self.assertNotIn("radial-gradient", page)
        self.assertNotIn("box-shadow", page)
        self.assertNotIn('src="cover.png"', page)
        self.assertNotIn('class="ico"', page)


if __name__ == "__main__":
    unittest.main()
