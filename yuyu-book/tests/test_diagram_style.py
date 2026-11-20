"""Diagram labels must keep their styling and never cover one another."""
import itertools
import json
import re
import sys
import unittest
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from playwright.sync_api import sync_playwright
from yuyu_book import mermaid as mm
from yuyu_book.core import REPO_ROOT
from yuyu_book.pdf import _launch
from yuyu_book.style_css import CSS


class StateDiagramLabelSeparation(unittest.TestCase):
    """Opaque edge labels must never cover one another (book p420/p163).

    Mermaid paints edge labels on opaque backgrounds. Two long <br/> labels
    anchored near the same state can overlap in screen space, hiding the
    later one. This checks rendered geometry, not source text, so it fails
    on the old labels and passes on the shortened ones.
    """

    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        # The harness imports mermaid from a file:// URL, which needs the
        # file-access flag; _launch() is for PDFs and omits it.
        mm.MM_DIR.mkdir(parents=True, exist_ok=True)
        for channel in ("msedge", "chrome", None):
            try:
                cls.browser = (cls.playwright.chromium.launch(
                    channel=channel, args=["--allow-file-access-from-files"])
                    if channel else cls.playwright.chromium.launch(
                        args=["--allow-file-access-from-files"]))
                break
            except Exception:
                continue
        else:
            cls.playwright.stop()
            raise AssertionError("no Chromium/Edge available for diagram tests")
        cls.page = cls.browser.new_page()
        harness = mm.MM_DIR / "_label_separation_harness.html"
        harness.write_text(mm._HARNESS.format(
            esm_url=mm.MERMAID_ESM.resolve().as_uri(),
            theme_json=json.dumps(mm.THEME["themeVariables"]),
            flow_json=json.dumps(mm.THEME["flowchart"])),
            encoding="utf-8")
        cls.page.goto(harness.resolve().as_uri(), wait_until="load")
        cls.page.wait_for_function("() => window.__ready === true",
                                   timeout=30000)

    @classmethod
    def tearDownClass(cls):
        cls.page.close()
        cls.browser.close()
        cls.playwright.stop()

    @staticmethod
    def label_boxes(svg):
        """Absolute box + text of each opaque edge label in a rendered SVG."""
        out = []
        pattern = (r'<g class="edgeLabel" transform="translate\(([^,]+),\s*([^)]+)\)">'
                   r'<g class="label"[^>]*transform="translate\(([^,]+),\s*([^)]+)\)">'
                   r'<foreignObject width="([\d.]+)" height="([\d.]+)">.*?<p>(.*?)</p>')
        for m in re.finditer(pattern, svg, re.S):
            gx, gy, ix, iy, width, height, body = m.groups()
            out.append((float(gx) + float(ix), float(gy) + float(iy),
                        float(width), float(height),
                        re.sub(r"<[^>]+>", "", body).strip()))
        return out

    def check_diagram(self, rel, marker, must_contain):
        text = (REPO_ROOT / rel).read_text(encoding="utf-8")
        src = next(s for m in re.finditer(r"```mermaid\n(.*?)```", text, re.S)
                   if (s := m.group(1)) and "stateDiagram" in s and marker in s)
        svg = self.page.evaluate("([id, src]) => window.__render(id, src)",
                                 [f"sep-{rel[:2]}", src])
        boxes = self.label_boxes(svg)
        self.assertTrue(boxes, f"{rel}: no edge labels rendered")
        for a, b in itertools.combinations(boxes, 2):
            ox = max(0, min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0]))
            oy = max(0, min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]))
            self.assertFalse(ox > 0 and oy > 0,
                             f"{rel}: {a[4]!r} covers {b[4]!r} by {ox}x{oy}pt")
        for want in must_contain:
            self.assertTrue(any(want in b[4] for b in boxes),
                            f"{rel}: {want!r} missing from rendered labels")

    def test_ch07_compact_breaker_labels_are_separated(self):
        self.check_diagram("第二部分-核心系统篇/07-上下文管理-Agent的工作记忆.md",
                           "CLOSED", ["压缩成功"])

    def test_ch15_harness_breaker_labels_are_separated(self):
        self.check_diagram("第四部分-工程实践篇/15-构建你自己的Agent-Harness.md",
                           "Closed", ["操作成功", "连败"])


class DiagramLabelStyle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = _launch(cls.playwright, None)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def test_chinese_quote_border_does_not_apply_to_diagram_labels(self):
        page = self.browser.new_page()
        try:
            page.set_content('<html><head><style>' + CSS + '</style></head>'
                '<body class="lang-zh"><article><div class="chapter-body">'
                '<p id="prose">正文</p><blockquote id="quote">引用</blockquote>'
                '<figure class="diagram"><div class="diagram-frame">'
                '<svg width="300" height="100"><foreignObject width="200" height="60">'
                '<div xmlns="http://www.w3.org/1999/xhtml">'
                '<span class="nodeLabel"><p id="label">before_agent_start</p></span>'
                '</div></foreignObject></svg></div></figure></div></article></body></html>')
            for media in ("screen", "print"):
                page.emulate_media(media=media)
                values = page.evaluate('''() => Object.fromEntries(
                    ['prose','quote','label'].map(id => {
                        const style = getComputedStyle(document.getElementById(id));
                        return [id, {border: parseFloat(style.borderInlineStartWidth),
                                     padding: parseFloat(style.paddingInlineStart)}];
                    }))''')
                for name in ("prose", "label"):
                    self.assertEqual(values[name], {"border": 0, "padding": 0},
                                     f"{media}: {name} acquired a quote gutter")
                self.assertGreater(values["quote"]["border"], 0)
        finally:
            page.close()


if __name__ == "__main__":
    unittest.main()
