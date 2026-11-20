"""One XHTML document per article, cross-document links, and a declared cover.

The reference EPUBs ship one file per chapter; a single six-megabyte
document is what this test replaced. It also pins the link rewriting that
comes with splitting: a fragment that stays in its own document keeps its
short form, everything else names its target document.
"""
from __future__ import annotations

import re
import sys
import tempfile
import unittest
import urllib.parse
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_epub import OPF, build

from yuyu_book.diagnostics import BuildError

XHTML = "{http://www.w3.org/1999/xhtml}"
PIXEL = ("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8"
         "z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
FIXTURE = f'''<!doctype html><html lang="en"><head>
    <meta charset="utf-8"><title>Split fixture — Author</title>
    <meta name="author" content="Author"></head><body><main>
    <section class="front-page cover" id="cover">
      <div class="cover-art"><img src="data:image/png;base64,{PIXEL}" alt="Cover art"></div>
    </section>
    <nav class="collection-jumps no-print"><a href="#toc">Contents</a></nav>
    <section class="volume">
      <article class="chapter" id="ch01"><h1>First chapter</h1>
        <p>Stay <a href="#section-a">inside</a>, then <a href="#ch02">next</a>.</p>
        <h2 id="section-a">Section A</h2></article>
    </section>
    <section class="volume">
      <article class="chapter" id="ch02"><h1>Second chapter</h1>
        <p>Back to <a href="#ch01">one</a>.</p></article>
    </section>
    <footer>Colophon text</footer>
</main></body></html>'''


class EpubDocumentSplit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        root = Path(cls.temporary.name)
        source = root / "fixture.html"
        source.write_text(FIXTURE, encoding="utf-8")
        cls.output = root / "fixture.epub"
        cls.report = build(source, cls.output, "en")
        cls.archive = zipfile.ZipFile(cls.output)
        cls.package = ET.fromstring(cls.archive.read("EPUB/package.opf"))
        cls.spine = [item.get("idref") for item in cls.package.find(f"{{{OPF}}}spine")]
        cls.manifest = {item.get("id"): item for item in cls.package.find(f"{{{OPF}}}manifest")}

    @classmethod
    def tearDownClass(cls):
        cls.archive.close()
        cls.temporary.cleanup()

    def body(self, stem: str) -> ET.Element:
        return ET.fromstring(self.archive.read(f"EPUB/{stem}.xhtml")).find(f"{XHTML}body")

    def test_each_article_ships_its_own_document(self):
        self.assertNotIn("EPUB/content.xhtml", self.archive.namelist())
        self.assertEqual(self.spine, ["cover", "ch01", "ch02", "part-004"])
        self.assertEqual(self.report["documents"], 4)
        for stem in self.spine:
            self.assertEqual(self.manifest[stem].get("href"), stem + ".xhtml")

    def test_documents_carry_their_own_titles(self):
        titles = {
            stem: ET.fromstring(self.archive.read(f"EPUB/{stem}.xhtml"))
            .find(f"{XHTML}head/{XHTML}title").text
            for stem in ("ch01", "ch02", "part-004")
        }
        self.assertEqual(titles, {"ch01": "First chapter", "ch02": "Second chapter",
                                  "part-004": "Split fixture"})

    def test_cross_document_links_name_their_target_file(self):
        links = [element.get("href") for element in self.body("ch01").iter()
                 if element.tag == f"{XHTML}a"]
        self.assertEqual(links, ["#section-a", "ch02.xhtml#ch02"])
        back = [element.get("href") for element in self.body("ch02").iter()
                if element.tag == f"{XHTML}a"]
        self.assertEqual(back, ["ch01.xhtml#ch01"])

    def test_navigation_points_into_the_split_documents(self):
        nav = ET.fromstring(self.archive.read("EPUB/nav.xhtml"))
        targets = [element.get("href") for element in nav.iter()
                   if element.tag == f"{XHTML}a"]
        self.assertEqual(len(targets), 3)
        self.assertTrue(all(re.fullmatch(r"ch0[12]\.xhtml#.+", target)
                            for target in targets), targets)

    def test_every_link_resolves_inside_the_archive(self):
        anchors = {}
        for name in self.archive.namelist():
            if name.startswith("EPUB/") and name.endswith(".xhtml"):
                tree = ET.fromstring(self.archive.read(name))
                anchors[name.rsplit("/", 1)[1]] = {
                    element.get("id") for element in tree.iter() if element.get("id")}
        members = set(self.archive.namelist())
        links = resources = cross = 0
        for name, ids in anchors.items():
            for element in ET.fromstring(self.archive.read("EPUB/" + name)).iter():
                if element.tag == f"{XHTML}link" or element.tag == f"{XHTML}img":
                    src = element.get("src") or element.get("href") or ""
                    if not src or src.startswith(("http:", "https:", "data:")):
                        continue
                    resources += 1
                    self.assertIn("EPUB/" + src, members, src)
                    continue
                href = element.get("href", "")
                if not href or href.startswith(("http:", "https:", "mailto:")):
                    continue
                page, anchor = urllib.parse.urldefrag(href)
                page = urllib.parse.unquote(page) or name
                anchor = urllib.parse.unquote(anchor)
                links += 1
                cross += page != name
                self.assertIn(page, anchors, f"{name}: {href}")
                if anchor:
                    self.assertIn(anchor, anchors[page], f"{name}: {href}")
        self.assertGreater(cross, 0, "no cross-document link was exercised")
        self.assertGreater(resources, 0, "no resource reference was exercised")

    def test_a_link_to_an_unknown_anchor_stops_the_build(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "dangling.html"
            source.write_text(FIXTURE.replace(
                '<a href="#ch02">next</a>', '<a href="#nowhere">next</a>'),
                encoding="utf-8")
            with self.assertRaisesRegex(BuildError, "dangling internal link #nowhere"):
                build(source, Path(directory) / "dangling.epub", "en")

    def test_cover_image_is_declared_in_the_package(self):
        cover = self.manifest[self.report["cover_image"]]
        self.assertEqual(cover.get("properties"), "cover-image")
        self.assertEqual(cover.get("media-type"), "image/png")
        title = self.package.find(f"{{{OPF}}}metadata/{{{OPF}}}meta[@name='cover']")
        self.assertIsNone(title, "legacy meta cover is deprecated in EPUB 3")


if __name__ == "__main__":
    unittest.main()
