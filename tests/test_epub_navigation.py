from __future__ import annotations

import sys
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_epub import EPUB, XHTML, _navigation


class EpubNavigation(unittest.TestCase):
    def test_toc_nests_section_headings_under_their_chapter(self):
        body = ET.Element(f"{{{XHTML}}}body")
        ET.SubElement(body, f"{{{XHTML}}}h2", {"id": "orphan"}).text = "Front matter"
        chapter = ET.SubElement(body, f"{{{XHTML}}}h1", {"id": "chapter"})
        ET.SubElement(chapter, f"{{{XHTML}}}span").text = "Chapter one"
        ET.SubElement(body, f"{{{XHTML}}}h2", {"id": "section"}).text = "First section"
        ET.SubElement(body, f"{{{XHTML}}}h1", {"id": "empty-heading"})
        ET.SubElement(body, f"{{{XHTML}}}h2", {"id": "orphan-section"}).text = "Orphan section"
        second = ET.SubElement(body, f"{{{XHTML}}}h1", {"id": "appendix"})
        second.text = "Appendix"
        ET.SubElement(body, f"{{{XHTML}}}h2", {"id": "epub-heading-7"}).text = "Existing ID"
        generated = ET.SubElement(body, f"{{{XHTML}}}h2")
        generated.text = "Generated section"

        nav_body, headings = _navigation(
            body,
            "en",
            {
                "orphan", "chapter", "section", "empty-heading",
                "orphan-section", "appendix", "epub-heading-7",
            },
        )
        ns = {"h": XHTML, "epub": EPUB}
        nav = nav_body.find("h:nav", ns)
        self.assertEqual(nav.get(f"{{{EPUB}}}type"), "toc")
        self.assertEqual(
            [link.text for link in nav.findall("h:ol/h:li/h:a", ns)],
            ["Front matter", "Chapter one", "Orphan section", "Appendix"],
        )
        appendix = nav.findall("h:ol/h:li", ns)[3]
        self.assertEqual(
            [link.text for link in appendix.findall("h:ol/h:li/h:a", ns)],
            ["Existing ID", "Generated section"],
        )
        self.assertEqual(
            headings,
            ["orphan", "chapter", "section", "orphan-section", "appendix",
             "epub-heading-7", "epub-heading-7-x"],
        )
        self.assertEqual(generated.get("id"), "epub-heading-7-x")


if __name__ == "__main__":
    unittest.main()
