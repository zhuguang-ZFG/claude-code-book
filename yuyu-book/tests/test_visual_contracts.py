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

TOC_FIXTURE = """<html><head><style>__CSS__</style></head>
<body class="lang-zh __PRODUCT__"><main class="sheet">
<section class="front-page toc" id="toc">
<div class="toc-group"><a class="toc-part">Earlier section</a></div>
<div class="toc-group"><a class="toc-part">Sources and permissions</a></div>
</section></main></body></html>"""


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


class NarrowChapterContracts(unittest.TestCase):
    def test_long_heading_keeps_the_emblem_inside_the_mobile_column(self):
        with sync_playwright() as playwright:
            browser = _launch(playwright, None)
            try:
                page = browser.new_page(viewport={"width": 390, "height": 844})
                page.set_content('<html><head><style>' + CSS + '</style></head>'
                                 '<body class="lang-zh collected"><main class="sheet">'
                                 '<article class="chapter"><header class="chapter-head">'
                                 '<div class="ch-head-row"><span class="ch-seal">01</span>'
                                 '<h1>AbortController 与取消</h1>'
                                 '<span class="ch-emblem"></span></div></header>'
                                 '</article></main></body></html>')
                sizes = page.evaluate("""() => ({
                    column: document.querySelector('article').getBoundingClientRect().right,
                    emblem: document.querySelector('.ch-emblem').getBoundingClientRect().right,
                    width: document.documentElement.scrollWidth
                })""")
                self.assertLessEqual(sizes["emblem"], sizes["column"] + 1)
                self.assertLessEqual(sizes["width"], 390)
            finally:
                browser.close()


class CollectedTocPrintContracts(unittest.TestCase):
    def test_only_the_omnibus_final_toc_heading_loses_print_spacing(self):
        with sync_playwright() as playwright:
            browser = _launch(playwright, None)
            try:
                page = browser.new_page()
                page.set_content(TOC_FIXTURE.replace("__CSS__", CSS)
                                 .replace("__PRODUCT__", "collected"))
                page.emulate_media(media="print")
                collected = page.evaluate("""() => {
                    const rows = [...document.querySelectorAll('.toc-part')];
                    return rows.map(row => {
                        const style = getComputedStyle(row);
                        return {marginTop: style.marginTop,
                                marginBottom: style.marginBottom,
                                fontSize: style.fontSize,
                                lineHeight: style.lineHeight};
                    });
                }""")
                self.assertEqual(collected[1]["marginTop"], "4px")
                self.assertEqual(collected[1]["marginBottom"], "2.4px")
                self.assertEqual(collected[1]["fontSize"], collected[0]["fontSize"])
                self.assertEqual(collected[1]["lineHeight"], "18.36px")

                page.set_content(TOC_FIXTURE.replace("__CSS__", CSS)
                                 .replace("__PRODUCT__", "standalone"))
                page.emulate_media(media="print")
                standalone = page.locator(".toc-part").last.evaluate(
                    "element => getComputedStyle(element).marginTop")
                self.assertEqual(standalone, "25.6px")

                page.set_content(TOC_FIXTURE.replace("__CSS__", CSS)
                                 .replace("__PRODUCT__", "collected"))
                page.emulate_media(media="screen")
                screen = page.locator(".toc-part").last.evaluate(
                    "element => getComputedStyle(element).marginTop")
                self.assertEqual(screen, "25.6px")
            finally:
                browser.close()


class CollectedNavigationContracts(unittest.TestCase):
    def test_deep_anchor_clears_the_wrapped_sticky_collection_bar(self):
        fixture = (
            '<html><head><style>' + CSS + '</style></head>'
            '<body class="lang-zh collected"><main class="sheet">'
            '<nav class="collection-jumps no-print" aria-label="合集导航">'
            '<a href="#cover">Agent Harness 十二卷合订本</a>'
            '<a href="#collection-guide">合集导读</a>'
            '<a href="#toc">目录</a></nav>'
            '<article class="chapter"><div class="chapter-body">'
            '<h2 id="deep-link">7.6 会话从列表里消失后，怎样找回再分叉</h2>'
            '</div></article></main></body></html>'
        )
        with sync_playwright() as playwright:
            browser = _launch(playwright, None)
            try:
                for width in (320, 390, 520):
                    page = browser.new_page(viewport={"width": width, "height": 900})
                    page.set_content(fixture)
                    metrics = page.evaluate("""() => {
                        const bar = document.querySelector('.collection-jumps');
                        const target = document.getElementById('deep-link');
                        return {
                            barHeight: bar.getBoundingClientRect().height,
                            scrollMargin: parseFloat(getComputedStyle(target).scrollMarginTop),
                        };
                    }""")
                    page.close()
                    self.assertGreaterEqual(
                        metrics["scrollMargin"], metrics["barHeight"],
                        f"{width}px: anchor offset {metrics['scrollMargin']} "
                        f"is smaller than sticky bar {metrics['barHeight']}")
            finally:
                browser.close()


class AestheticContrastContracts(unittest.TestCase):
    """Guard computed-style invariants for callouts, epigraphs, and code plates
    across light/dark screen themes, print, and agent engineering volumes."""

    def test_section_tier_labels_keep_ten_pixel_minimum_on_phone(self):
        fixture = (
            '<html><head><style>' + CSS + '</style></head>'
            '<body class="lang-zh"><main class="sheet">'
            '<article class="chapter"><div class="chapter-body">'
            '<h2>章节标题<span class="sec-tier t-start">起步</span></h2>'
            '</div></article><div class="tier-legend">'
            '<span class="tier-chip t-core">主干</span>'
            '</div></main></body></html>'
        )
        with sync_playwright() as playwright:
            browser = _launch(playwright, None)
            try:
                page = browser.new_page(viewport={"width": 390, "height": 844})
                page.set_content(fixture)
                sizes = page.evaluate("""() => {
                    return [...document.querySelectorAll('.sec-tier,.tier-chip')]
                        .map(e => parseFloat(getComputedStyle(e).fontSize));
                }""")
                self.assertEqual(len(sizes), 2)
                for size in sizes:
                    self.assertGreaterEqual(size, 10.0)
            finally:
                browser.close()

    @staticmethod
    def _rgb_to_lum(rgb: str) -> float:
        nums = [int(x) / 255.0 for x in re.findall(r"\d+", rgb)[:3]]
        def chan(c: float) -> float:
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        r, g, b = (chan(c) for c in nums)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def _contrast(self, fg: str, bg: str) -> float:
        a, b = sorted((self._rgb_to_lum(fg), self._rgb_to_lum(bg)), reverse=True)
        return (a + 0.05) / (b + 0.05)

    def test_callouts_keep_semantic_border_and_epigraph_keeps_borderless_left(self):
        with sync_playwright() as playwright:
            browser = _launch(playwright, None)
            try:
                page = browser.new_page()
                page.set_content(
                    '<html><head><style>' + CSS + '</style></head>'
                    '<body class="lang-zh"><main class="sheet"><article class="chapter">'
                    '<div class="chapter-body">'
                    '<blockquote id="epi"><p>开篇题辞</p></blockquote>'
                    '<blockquote id="tip" class="callout callout-tip"><p class="callout-tag"><strong>最佳实践：</strong></p><p class="callout-body">内容</p></blockquote>'
                    '<blockquote id="warn" class="callout callout-warning"><p class="callout-tag"><strong>注意：</strong></p><p class="callout-body">内容</p></blockquote>'
                    '<blockquote id="concept" class="callout callout-concept"><p class="callout-tag"><strong>设计洞察：</strong></p><p class="callout-body">内容</p></blockquote>'
                    '</div></article></main></body></html>')
                got = page.evaluate("""() => {
                    const pick = id => {
                        const s = getComputedStyle(document.getElementById(id));
                        return {bLW: s.borderLeftWidth, bLC: s.borderLeftColor, bT: s.borderTopStyle};
                    };
                    return {epi: pick('epi'), tip: pick('tip'), warn: pick('warn'), concept: pick('concept')};
                }""")
                self.assertEqual(got["epi"]["bLW"], "0px")
                self.assertEqual(got["epi"]["bT"], "solid")
                self.assertEqual(got["tip"]["bLW"], "4px")
                self.assertEqual(got["tip"]["bLC"], "rgb(78, 110, 93)")
                self.assertEqual(got["warn"]["bLC"], "rgb(180, 71, 47)")
                self.assertEqual(got["concept"]["bLC"], "rgb(76, 112, 147)")
            finally:
                browser.close()

    def test_agent_book_and_print_code_plates_clear_aa_contrast(self):
        fixture = (
            '<html><head><style>' + CSS + '</style></head>'
            '<body class="lang-zh __BODY__"><main class="sheet"><article class="chapter">'
            '<div class="chapter-body"><div class="codehilite" data-lang="py"><pre>'
            '<span class="k">def</span> <span class="nf">f</span>'
            '<span class="p">(</span><span class="n">x</span><span class="p">):</span> '
            '<span class="s2">"hi"</span> <span class="o">+</span> '
            '<span class="mi">1</span> <span class="c1"># c</span>'
            '</pre></div></div></article></main></body></html>'
        )
        with sync_playwright() as playwright:
            browser = _launch(playwright, None)
            try:
                for body_cls, media, scheme in (
                    ("agent-book agent-deepseek", "screen", "light"),
                    ("agent-book agent-deepseek", "screen", "dark"),
                    ("", "print", "light"),
                ):
                    page = browser.new_page()
                    page.emulate_media(media=media, color_scheme=scheme)
                    page.set_content(fixture.replace("__BODY__", body_cls))
                    colors = page.evaluate("""() => {
                        const bg = getComputedStyle(document.querySelector('.codehilite')).backgroundColor;
                        const pre = getComputedStyle(document.querySelector('.codehilite pre')).color;
                        const spans = [...document.querySelectorAll('.codehilite pre span')].map(
                            s => [s.className, getComputedStyle(s).color]);
                        return {bg, pre, spans};
                    }""")
                    page.close()
                    self.assertGreaterEqual(
                        self._contrast(colors["pre"], colors["bg"]), 4.5,
                        f"{body_cls} {media} {scheme} pre fg={colors['pre']} bg={colors['bg']}")
                    for cls, fg in colors["spans"]:
                        ratio = self._contrast(fg, colors["bg"])
                        self.assertGreaterEqual(
                            ratio, 4.5,
                            f"{body_cls} {media} {scheme} .{cls} fg={fg} bg={colors['bg']} ratio={ratio:.2f}")
            finally:
                browser.close()

    def test_structural_lists_do_not_inherit_prose_diamond_bullets_and_cover_seal_clears_kicker(self):
        fixture = (
            '<html><head><style>' + CSS + '</style></head>'
            '<body class="lang-zh"><main class="sheet">'
            '<section class="front-page cover" id="cover"><div class="cover-inner">'
            '<span class="cover-seal" aria-hidden="true">御舆</span>'
            '<p class="cover-kicker">AGENT HARNESS · 深度架构解析</p>'
            '<h1 class="book-title"><span class="bt-main">御舆</span></h1>'
            '</div></section>'
            '<section class="front-page revisions" id="revisions"><h1 class="page-title">修订</h1>'
            '<ul id="rev-ul"><li id="rev-li">条目</li></ul></section>'
            '<section class="front-page"><ul class="route-parts"><li id="rp-li">第一部分</li></ul>'
            '<ul class="reg-list"><li id="reg-li">来源</li></ul>'
            '<ul class="idx-list"><li id="idx-li">索引</li></ul></section>'
            '<article class="chapter"><div class="chapter-body">'
            '<ul><li id="prose-li">正文要点</li></ul>'
            '<aside class="new-terms"><ul class="nt-list"><li id="nt-li" class="nt-row">新词</li></ul></aside>'
            '</div></article></main></body></html>'
        )
        with sync_playwright() as playwright:
            browser = _launch(playwright, None)
            try:
                for vp in ({"width": 1440, "height": 900}, {"width": 390, "height": 844}):
                    page = browser.new_page(viewport=vp)
                    page.set_content(fixture)
                    res = page.evaluate("""() => {
                        const bef = id => getComputedStyle(document.getElementById(id), '::before').content;
                        const sr = document.querySelector('.cover-seal').getBoundingClientRect();
                        const kr = document.querySelector('.cover-kicker').getBoundingClientRect();
                        const ov = Math.max(0, Math.min(sr.right, kr.right) - Math.max(sr.left, kr.left)) *
                                   Math.max(0, Math.min(sr.bottom, kr.bottom) - Math.max(sr.top, kr.top));
                        return {
                            prose: bef('prose-li'),
                            rev: bef('rev-li'),
                            rp: bef('rp-li'),
                            reg: bef('reg-li'),
                            idx: bef('idx-li'),
                            nt: bef('nt-li'),
                            sealOverlap: Math.round(ov),
                        };
                    }""")
                    page.close()
                    self.assertEqual(res["prose"], '"◆"')
                    self.assertEqual(res["rev"], '"◆"')
                    for key in ("rp", "reg", "idx", "nt"):
                        self.assertEqual(res[key], "none", f"vp={vp['width']} {key} leaked bullet")
                    self.assertEqual(res["sealOverlap"], 0, f"vp={vp['width']} seal overlapped kicker")
            finally:
                browser.close()

    def test_collected_long_volume_divider_uses_two_columns_and_fits_a4_sheet(self):
        from yuyu_book import pages
        rows = [(f"llm-p{i}", f"第{i}篇", f"篇目 {i}") for i in range(1, 11)]
        divider = pages.volume_divider(
            {"id": "vol2", "no": {"zh": "卷二"},
             "title": {"zh": "大模型：写给 Agent 工程师的原理与实战"},
             "motto": {"zh": "从 token 到多模态，把模型侧原理连成一张图"},
             "goal": {"zh": "从 token、向量与注意力开始，逐步理解训练、推理、RAG 和评测。"}},
            "zh", 2, rows, counts="10 篇 · 16 章")
        self.assertIn('class="pd-list pd-list-cols"', divider)
        with sync_playwright() as playwright:
            browser = _launch(playwright, None)
            try:
                page = browser.new_page(viewport={"width": 794, "height": 1123})
                page.set_content('<html><head><style>' + CSS + '</style></head>'
                                 '<body class="lang-zh collected"><main class="sheet">'
                                 + divider + '</main></body></html>')
                page.emulate_media(media="print")
                metrics = page.evaluate("""() => {
                    const div = document.querySelector('.volume-divider');
                    const list = document.querySelector('.pd-list');
                    return {
                        height: Math.round(div.getBoundingClientRect().height),
                        cols: getComputedStyle(list).gridTemplateColumns.split(' ').length,
                    };
                }""")
                self.assertEqual(metrics["cols"], 2)
                self.assertLessEqual(metrics["height"], 960,
                                     f"10-part volume divider spilled A4 page ({metrics['height']}px)")
            finally:
                browser.close()

    def test_chinese_emphasis_uses_kaiti_without_slanted_faux_italic(self):
        with sync_playwright() as playwright:
            browser = _launch(playwright, None)
            try:
                page = browser.new_page()
                page.set_content(
                    '<html><head><style>' + CSS + '</style></head>'
                    '<body class="lang-zh"><main class="sheet"><article class="chapter">'
                    '<div class="chapter-body"><p>这是一句<em id="zh-em">强调</em>。</p></div>'
                    '</article></main></body></html>')
                zh = page.evaluate("""() => {
                    const s = getComputedStyle(document.getElementById('zh-em'));
                    return {style: s.fontStyle, family: s.fontFamily};
                }""")
                self.assertEqual(zh["style"], "normal")
                self.assertRegex(zh["family"], r"Kai|楷")
            finally:
                browser.close()

    def test_agent_book_tables_and_blockquotes_use_cool_surfaces_not_warm_beige(self):
        fixture = (
            '<html><head><style>' + CSS + '</style></head>'
            '<body class="lang-zh agent-book agent-deepseek"><main class="sheet">'
            '<article class="chapter"><div class="chapter-body">'
            '<p>正文段落。</p>'
            '<blockquote id="bq"><p>引文</p></blockquote>'
            '<div class="table-scroll"><table><tbody>'
            '<tr><td>1</td></tr><tr id="even-row"><td>2</td></tr>'
            '</tbody></table></div></div></article></main></body></html>'
        )
        with sync_playwright() as playwright:
            browser = _launch(playwright, None)
            try:
                page = browser.new_page()
                page.set_content(fixture)
                got = page.evaluate("""() => ({
                    bqBg: getComputedStyle(document.getElementById('bq')).backgroundColor,
                    bqBorder: getComputedStyle(document.getElementById('bq')).borderLeftColor,
                    rowBg: getComputedStyle(document.getElementById('even-row')).backgroundColor,
                })""")
                self.assertEqual(got["bqBg"], "rgb(240, 243, 242)")
                self.assertEqual(got["bqBorder"], "rgb(49, 90, 166)")
                self.assertIn("240, 243, 242", got["rowBg"])
            finally:
                browser.close()


if __name__ == "__main__":
    unittest.main()
