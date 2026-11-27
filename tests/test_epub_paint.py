"""EPUB format validation cannot detect diagrams that rasterize as black blocks."""
from __future__ import annotations

import io
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_epub import build


class EpubPaint(unittest.TestCase):
    def test_svg_local_styles_survive_until_rasterization(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            source = folder / "fixture.html"
            output = folder / "fixture.epub"
            source.write_text('''<!doctype html><html lang="en"><head>
                <meta charset="utf-8"><title>Paint fixture</title></head><body><main>
                <h1 id="title">Paint fixture</h1><style>.extra{color:blue}</style>
                <figure><svg xmlns="http://www.w3.org/2000/svg" id="diagram"
                    viewBox="0 0 120 80" width="120" height="80">
                  <style>#diagram .node{fill:#e4ebf2;stroke:#4c7093}
                    #diagram .edge{fill:none;stroke:#4c7093;stroke-width:2}</style>
                  <rect class="node" x="10" y="10" width="100" height="60"/>
                  <path class="edge" d="M20 60 L60 20 L100 60"/>
                </svg><figcaption>Styled diagram</figcaption></figure>
                </main></body></html>''', encoding="utf-8")
            report = build(source, output, "en")
            self.assertEqual(report["rasterized_svg"], 1)
            with zipfile.ZipFile(output) as archive:
                images = [name for name in archive.namelist() if name.endswith(".png")]
                self.assertEqual(len(images), 1)
                image = Image.open(io.BytesIO(archive.read(images[0]))).convert("RGB")
                # A point in the V-shaped path's interior stays the pale node
                # color. If fill:none or the node fill is lost, it becomes black.
                x, y = int(image.width * .5), int(image.height * .65)
                self.assertEqual(image.getpixel((x, y)), (228, 235, 242))
                content = "".join(
                    archive.read(name).decode("utf-8")
                    for name in archive.namelist()
                    if name.endswith(".xhtml") and not name.endswith("nav.xhtml"))
                self.assertIn("Styled diagram", content)
                self.assertNotIn("<style", content)
                self.assertNotIn(".node{", content)

    def test_il_semantic_ink_classes_survive_rasterization(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            source = folder / "inks.html"
            output = folder / "inks.epub"
            source.write_text('''<!doctype html><html lang="zh"><head>
                <meta charset="utf-8"><title>Multi-ink fixture</title>
                <style>
                :root{--ink:#26221B;--cinnabar:#B4472F;--jade:#4E6E5D;--sky:#4C7093}
                .illu-frame svg .il-cinnabar{color:var(--cinnabar)}
                .illu-frame svg .il-jade{color:var(--jade)}
                .illu-frame svg .il-sky{color:var(--sky)}
                </style></head><body><main>
                <h1 id="title">Multi-ink fixture</h1>
                <figure class="illu"><div class="illu-frame">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 100" width="300" height="100">
                    <rect class="il-cinnabar" x="0" y="0" width="100" height="100" fill="currentColor" stroke="none"/>
                    <rect class="il-jade" x="100" y="0" width="100" height="100" fill="currentColor" stroke="none"/>
                    <rect class="il-sky" x="200" y="0" width="100" height="100" fill="currentColor" stroke="none"/>
                  </svg>
                </div><figcaption>Semantic inks</figcaption></figure>
                </main></body></html>''', encoding="utf-8")
            report = build(source, output, "zh")
            self.assertEqual(report["rasterized_svg"], 1)
            with zipfile.ZipFile(output) as archive:
                images = [name for name in archive.namelist() if name.endswith(".png")]
                self.assertEqual(len(images), 1)
                image = Image.open(io.BytesIO(archive.read(images[0]))).convert("RGB")
                mid_y = image.height // 2
                cinnabar = image.getpixel((int(image.width * 0.16), mid_y))
                jade = image.getpixel((int(image.width * 0.50), mid_y))
                sky = image.getpixel((int(image.width * 0.84), mid_y))
                self.assertEqual(cinnabar, (180, 71, 47))
                self.assertEqual(jade, (78, 110, 93))
                self.assertEqual(sky, (76, 112, 147))
                css = archive.read("EPUB/book.css").decode("utf-8")
                self.assertIn(".diagram-frame,.illu-frame{background:#F5EFE2", css)
                self.assertIn(".diagram-frame img,.illu-frame img{mix-blend-mode:multiply}", css)


if __name__ == "__main__":
    unittest.main()
