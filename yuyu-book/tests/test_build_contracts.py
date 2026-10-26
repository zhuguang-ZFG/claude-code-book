"""Typesetting and delivery contracts: tokens, contrast, print rules, and the
end-to-end no-browser build."""
import re
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from yuyu_book.core import BOOK_DIR, REPO_ROOT  # noqa: E402
from yuyu_book.mermaid import BOOK_FAMILIES  # noqa: E402
from yuyu_book.style import CSS  # noqa: E402

MIN_RATIO = 4.5      # WCAG 2.1 AA for body-size text


def _tokens(block: str) -> dict[str, str]:
    return {k: v for k, v in re.findall(r"(--[\w-]+):\s*(#[0-9A-Fa-f]{6})", block)}


def _luminance(hex_: str) -> float:
    def chan(i):
        c = int(hex_.lstrip("#")[i:i + 2], 16) / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (chan(i) for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _ratio(fg: str, bg: str) -> float:
    a, b = sorted([_luminance(fg), _luminance(bg)], reverse=True)
    return (a + 0.05) / (b + 0.05)


LIGHT = _tokens(CSS.split("@media (prefers-color-scheme:dark)")[0])
DARK = _tokens(re.search(r"body:not\(\.force-light\)\{(.*?)\}", CSS, re.S).group(1))


def _rule(selector: str) -> str:
    m = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", CSS)
    return m.group(1) if m else ""


class Palette(unittest.TestCase):
    def test_the_book_defines_its_own_token_set(self):
        for key in ("paper", "paper-2", "paper-3", "card", "ink", "ink-2",
                    "ink-3", "line", "line-2", "bronze", "bronze-2", "bronze-3",
                    "cinnabar", "jade", "sky", "code-bg", "code-fg", "serif",
                    "kai", "sans", "mono", "measure"):
            self.assertIn(f"--{key}", CSS, key)

    def test_dark_mode_overrides_the_surface_and_ink_tokens(self):
        for key in ("--paper", "--card", "--ink", "--ink-2", "--ink-3",
                    "--bronze", "--cinnabar", "--code-bg"):
            self.assertIn(key, DARK, f"{key} has no dark override")

    def test_body_text_meets_wcag_aa_on_every_surface(self):
        inks = ("--ink", "--ink-2", "--ink-3")
        for mode, tokens in (("light", LIGHT), ("dark", DARK)):
            for ink in inks:
                for surface in ("--paper", "--card", "--paper-2", "--paper-3"):
                    fg, bg = tokens.get(ink), tokens.get(surface)
                    self.assertTrue(fg and bg, f"{mode}: missing {ink or surface}")
                    ratio = _ratio(fg, bg)
                    self.assertGreaterEqual(
                        round(ratio, 2), MIN_RATIO,
                        f"{mode}: {ink} on {surface} is {ratio:.2f}")

    def test_accent_colours_clear_aa_on_the_page(self):
        for mode, tokens in (("light", LIGHT), ("dark", DARK)):
            for ink in ("--bronze", "--bronze-3", "--cinnabar", "--jade", "--sky"):
                ratio = _ratio(tokens[ink], tokens["--paper"])
                self.assertGreaterEqual(round(ratio, 2), MIN_RATIO,
                                        f"{mode}: {ink} is {ratio:.2f} on paper")

    def test_diagram_families_keep_their_labels_readable(self):
        """Re-inked plates are the one place a colour pair is invented in Python
        rather than CSS, so the AA gate has to reach it too."""
        for name, (fill, _stroke, text) in BOOK_FAMILIES.items():
            ratio = _ratio(text, fill)
            self.assertGreaterEqual(round(ratio, 2), MIN_RATIO,
                                    f"diagram family {name} is {ratio:.2f}")

    def test_tertiary_ink_is_not_reused_for_decorative_rules_only(self):
        """--ink-3 carries figure captions, folios and colophon copy, so it
        must clear AA on the page background in both modes."""
        self.assertGreaterEqual(round(_ratio(LIGHT["--ink-3"], LIGHT["--paper"]), 2),
                                MIN_RATIO)
        self.assertGreaterEqual(round(_ratio(DARK["--ink-3"], DARK["--paper"]), 2),
                                MIN_RATIO)

    def test_gold_is_reserved_for_ornament_not_small_copy(self):
        self.assertLess(_ratio(LIGHT["--bronze-2"], LIGHT["--paper"]), MIN_RATIO,
                        "bronze-2 is intentionally decorative")
        for selector in (".toc-n", ".reg-no", ".rk-n", ".fig-no", ".cc-src-t",
                         ".pd-no", ".page-ref", ".fig-cap"):
            self.assertNotIn("bronze-2", _rule(selector),
                             f"{selector} sets small copy in gold")


class Typography(unittest.TestCase):
    def test_serif_for_prose_sans_for_furniture(self):
        self.assertIn("font:400 17px/1.8 var(--serif)", CSS)
        self.assertIn("h1,h2,h3,h4{font-family:var(--sans)", CSS)

    def test_cjk_prose_is_justified_with_strict_line_breaking(self):
        self.assertIn(".chapter-body p,.chapter-body li{text-align:justify}", CSS)
        self.assertIn("line-break:strict", CSS)
        self.assertIn("hyphens:auto", CSS)

    def test_a_phone_measure_stops_justifying_chinese(self):
        """Justification is a trade: an even right edge paid for in inter-word
        space. A wide line has enough words to hide the cost; a 390px line that
        cannot fit `CompactionResult` moves the whole token down and stretches
        the six CJK glyphs left behind across the row. Latin hyphenates out of
        the same trouble, so this is a Chinese-only concession."""
        self.assertRegex(
            CSS, r"@media \(max-width:30rem\)\{"
                 r"body\.lang-zh \.chapter-body p,"
                 r"body\.lang-zh \.chapter-body li\{text-align:left\}\}")
        self.assertNotIn("lang-en .chapter-body p,.chapter-body li{text-align:left",
                         CSS)

    def test_a_standalone_block_keeps_the_alignment_its_container_set(self):
        # the epigraph is a right-aligned block; the prose rule used to win on
        # its paragraphs, so a two-line English quote justified a river under a
        # short last line instead of hanging flush right like the rest of it.
        self.assertIn(".chapter-body blockquote p{text-align:inherit}", CSS)

    def test_a_source_chip_shows_its_whole_label(self):
        # chips were capped with an ellipsis, which cut
        # "Building Effective Agents（Anthropic 工程博客，2024-12-19）" mid-date;
        # the chip row already wraps, so the label may simply get taller.
        chip = _rule(".source-chip")
        self.assertTrue(chip, "no .source-chip rule")
        self.assertNotIn("text-overflow", chip)
        self.assertNotIn("white-space:nowrap", chip)

    def test_no_web_font_is_downloaded(self):
        self.assertNotIn("@font-face", CSS)
        self.assertNotIn("@import", CSS)
        for url in re.findall(r"url\(([^)]*)\)", CSS):
            self.assertNotIn("http", url, url)

    def test_every_component_the_audit_counts_has_a_style(self):
        for cls in ("chapter", "unit", "appendix", "compass", "compass-card",
                    "callout", "callout-tip", "callout-warning", "callout-info",
                    "callout-concept", "diagram", "diagram-frame", "table-scroll",
                    "codehilite", "page-ref", "xref", "source-chip", "rail",
                    "part-divider", "front-page", "colophon", "toc-group",
                    "fig-hint"):
            self.assertIn(cls, CSS, cls)


class ColumnWidths(unittest.TestCase):
    """Two widths, one column: sentences stay at the reading measure while
    plates, tables and code take the sheet. A build that quietly drops either
    half turns into a wall of 100-character lines or a page of thumbnails."""

    @staticmethod
    def _var(name: str) -> float:
        m = re.search(rf"--{name}:(\d+(?:\.\d+)?)rem", CSS)
        assert m, f"--{name} is not a rem value"
        return float(m.group(1)) * 16

    @staticmethod
    def _capped_selectors() -> list[str]:
        block = re.search(r"^\.chapter-body>p,", CSS, re.M)
        assert block, "the prose cap rule is missing"
        head = CSS[block.start(): CSS.index("{", block.start())]
        return [s.strip() for s in head.split(",")]

    def test_the_measure_is_a_reading_column_and_the_furniture_is_wider(self):
        measure, furniture = self._var("measure"), self._var("furniture")
        self.assertGreaterEqual(measure, 40 * 16, "a 40em column is too narrow")
        self.assertLessEqual(measure, 46 * 16, "sentences run past a comfortable line")
        self.assertGreater(furniture, measure, "the furniture column is redundant")
        self.assertLessEqual(furniture, 66 * 16, "code lines would need scrolling")

    def test_a_wide_sheet_gives_the_furniture_its_own_width(self):
        block = CSS[CSS.index("@media (min-width:1360px)"):]
        self.assertIn(".sheet{max-width:var(--furniture)}", block)

    def test_prose_blocks_are_capped_and_centred(self):
        body = CSS[CSS.index(".chapter-body>p,.chapter-body>ul"):]
        body = body[: body.index("}") + 1]
        self.assertIn("max-width:var(--measure)", body)
        # centred, because a column pinned to the left of a wide sheet leaves a
        # dead gutter the reader reads as a broken page
        self.assertIn("margin-inline:auto", body)
        for sel in (".chapter-body>p", ".chapter-body .callout", ".chapter-notes"):
            self.assertIn(sel, self._capped_selectors(), sel)

    def test_the_chapter_furniture_keeps_the_sheet_width(self):
        # an inset lead band sitting over full-width compass cards reads as a
        # misaligned page, not as a hierarchy
        capped = " ".join(self._capped_selectors())
        for cls in (".lead-band", ".new-terms", ".compass"):
            self.assertNotIn(cls, capped, f"{cls} should span the sheet")

    def test_the_wide_blocks_are_left_out_of_the_cap(self):
        capped = " ".join(self._capped_selectors())
        for cls in ("figure.diagram", ".table-scroll", ".codehilite"):
            self.assertNotIn(cls, capped, f"{cls} should use the full sheet width")

    def test_latin_gets_a_shorter_measure_than_cjk(self):
        """46rem of Chinese is ~43 characters; the same box in 17px Palatino is
        a 90-character line, which is the classic 'no one can track the return'
        failure. English overrides the token instead of the font size."""
        m = re.search(r"body\.lang-en\{--measure:(\d+(?:\.\d+)?)rem", CSS)
        self.assertTrue(m, "the English column does not set its own measure")
        en = float(m.group(1)) * 16
        self.assertLess(en, self._var("measure"), "English is not narrower")
        # ~8.2px per character at 17px Palatino; 80 characters is already long
        self.assertLessEqual(round(en / 8.2), 80)

    def test_the_gloss_bubble_is_demoted_before_it_can_hang_off_screen(self):
        """A centred bubble only fits beside the column if the screen can hold
        the whole measure plus the bubble on the side the term sits at. The
        worst case is a term at the very end of the 46rem column, so the float
        becomes a bottom caption below measure + bubble width -- a 720px screen
        used to clip 100px of it and make the document scroll sideways."""
        bubble = re.search(
            r"\.gloss-pop\{[^}]*max-width:min\((\d+(?:\.\d+)?)rem", CSS)
        assert bubble, "the gloss bubble has no rem cap"
        cap = re.search(
            r"@media \(max-width:([\d.]+)rem\)\s*\{\s*\.gloss-pop\{"
            r"position:fixed", CSS)
        assert cap, "the bubble is never demoted to a caption"
        self.assertGreaterEqual(
            float(cap.group(1)) * 16,
            self._var("measure") + float(bubble.group(1)) * 16,
            "a term at the end of the measure overflows the viewport")
        # pinned to the viewport rather than to the term: an absolutely placed
        # caption would be written off the bottom of the page the reader left
        demo = CSS[cap.start():]
        demo = demo[: demo.index("}") + 1]
        self.assertIn("left:50%", demo)
        self.assertIn("92vw", demo)

    def test_a_bubble_inside_a_scrolling_sheet_is_pinned(self):
        # a table scrolls sideways and clips everything painted inside it, so a
        # floating bubble whose term sits near the sheet edge hovers into empty
        # space; at 1360px 13 of the book's tables hid their bubbles outright
        sheet = re.search(r"\.table-scroll \.gloss-pop\{([^}]*)\}", CSS)
        assert sheet, "table bubbles still hang inside the box that clips them"
        self.assertIn("position:fixed", sheet.group(1))
        cap = re.search(r"@media \(max-width:([\d.]+)rem\)\s*\{\s*\.gloss-pop\{"
                        r"([^}]*)\}", CSS)
        assert cap, "the narrow-screen caption rule moved"
        # one caption, two triggers: if the two drift apart the bubble jumps as
        # the reader resizes the window
        self.assertEqual(" ".join(cap.group(2).split()),
                         " ".join(sheet.group(1).split()))

    def test_the_cap_stands_down_on_paper(self):
        # @page margins are 17mm each side of 210mm; rem is the 16px root, so a
        # printed measure wider than the page box means paper is unaffected
        box_px = (210 - 2 * 17) / 25.4 * 96
        m = re.search(r"@page\{size:A4;margin:21mm (\d+)mm", CSS)
        self.assertTrue(m, "@page margins moved out from under this test")
        print_block = CSS[CSS.index("@media print{"):]
        pm = re.search(r"body,body\.lang-en\{--measure:(\d+(?:\.\d+)?)rem",
                       print_block)
        self.assertTrue(pm, "paper does not release the reading-column cap")
        self.assertGreaterEqual(float(pm.group(1)) * 16, box_px)
        for name in ("--measure", "--furniture"):
            self.assertLess(self._var(name[2:]), box_px * 1.6,
                            f"{name} is wider than a page for no reason")


class PrintContract(unittest.TestCase):
    def test_print_block_exists_with_a4_geometry(self):
        self.assertIn("@media print{", CSS)
        self.assertIn("@page{size:A4", CSS)

    def test_units_and_parts_start_new_pages(self):
        self.assertIn("article.chapter,article.unit{", CSS)
        self.assertIn("break-before:page", CSS)
        self.assertIn("section.front-page{break-before:page}", CSS)
        self.assertIn(".part-divider", CSS)

    def test_orphan_and_widow_control(self):
        self.assertIn("p{orphans:2;widows:2}", CSS)
        self.assertIn("h1,h2,h3{break-after:avoid}", CSS)
        self.assertIn(".toc-group{break-inside:avoid}", CSS)
        self.assertIn("figure.diagram", CSS)
        # a registry row is a bordered card, so a page break may not cut it
        self.assertRegex(CSS, r"\.reg-list li\{[^}]*break-inside:avoid")

    def test_rail_disappears_on_paper_and_narrow_screens_use_the_column(self):
        self.assertIn("nav.rail,.no-print{display:none!important}", CSS)
        self.assertRegex(CSS, r"@media \(min-width:1360px\)")

    def test_the_wide_screen_rail_rule_outranks_its_own_default(self):
        """`nav.rail{display:none}` and the media query's `nav.rail{display:block}`
        are equally specific, so whichever is written last wins. With the query
        first, every screen 1360px and up reserved a 17.5rem gutter and left it
        empty — a rail the reader never sees."""
        hidden = CSS.index("nav.rail{display:none")
        shown = CSS.index("nav.rail{display:block}")
        self.assertLess(hidden, shown)

    def test_an_index_row_never_loses_its_leader(self):
        """A long identifier used to squeeze the dotted leader down to a stub.
        The term breaks anywhere rather than eat the dots, so every entry still
        reads as term — leader — page."""
        self.assertRegex(CSS, r"\.idx-term\{[^}]*overflow-wrap:anywhere")
        self.assertRegex(CSS, r"\.idx-row \.leader\{[^}]*min-width")


class RunningHeads(unittest.TestCase):
    def test_every_bookmarked_section_opens_its_own_head(self):
        """The PDF pass reads its section map out of the bookmarks. Part ids
        were once filtered out, which left each divider page wearing the head
        of the chapter that ended before it."""
        import build
        from yuyu_book.core import load_configs
        manifest, _ = load_configs()
        outline = [(1, p["no"]["zh"] + " · " + p["title"]["zh"], p["id"])
                   for p in manifest["parts"]]
        outline.append((2, "第 1 章", "ch01"))
        meta = build.pdf_meta(manifest, outline, [], "zh")
        self.assertEqual([a for a, _label in meta["heads"]],
                         [a for _lvl, _t, a in outline])
        self.assertEqual(meta["lang"], "zh")
        self.assertTrue(meta["title"])

    def test_the_screen_floor_for_wide_plates_is_dropped_on_paper(self):
        # render.py pins a min-width onto plates too wide to read at column
        # width; on A4 that must give back the whole page width or the
        # overflow-x frame would clip the drawing.
        print_block = CSS[CSS.index("@media print{"):]
        self.assertIn("min-width:0!important", print_block)
        self.assertIn(".fig-hint{display:none}", print_block)
        # ...and the cap is a per-plate variable, so a tall plate can stand up
        self.assertIn("max-height:var(--plate-cap,150mm)", print_block)

    def test_a_wide_plate_gets_a_landscape_sheet_of_its_own(self):
        print_block = CSS[CSS.index("@media print{"):]
        self.assertIn("@page plate-landscape{size:A4 landscape", print_block)
        rule = re.search(r"figure\.landscape\{[^}]*\}", print_block).group(0)
        self.assertIn("break-before:page", rule)
        # the named page already ends the sheet; asking for a break afterwards
        # left one empty landscape page behind every fold-out
        self.assertNotIn("break-after", rule)

    def test_a_capped_plate_is_printed_without_its_screen_frame(self):
        # the height cap makes a plate narrower than the column, so a bordered
        # frame would print as a wide empty box around a small drawing. The box
        # stands down on paper; it may NOT shrink-to-fit instead, because every
        # plate root is width="100%" and a fit-content frame collapses it.
        print_block = CSS[CSS.index("@media print{"):]
        self.assertIn(".diagram-frame{background:none;border:0", print_block)
        self.assertNotIn("fit-content", print_block)
        self.assertIn(".diagram-frame::before,.diagram-frame::after{display:none}",
                      print_block)

    def test_part_and_unit_openers_own_their_whole_sheet(self):
        # a part plate taller than the text column drops its last chapter onto
        # the next sheet as a page of one line.
        print_block = CSS[CSS.index("@media print{"):]
        self.assertIn(".part-divider{padding:26mm 0 24mm}", print_block)
        self.assertIn(".tier-legend{break-inside:avoid", print_block)
        self.assertIn(".tl-list{display:grid;grid-template-columns:repeat(2",
                      print_block)
        self.assertIn(".route-parts li{padding:.3rem 0}", print_block)

    def test_wide_tables_wrap_on_paper_instead_of_losing_a_column(self):
        # .table-scroll is a screen device; on paper its overflow-x would
        # silently cut the last column of the appendix flag/glossary tables.
        print_block = CSS[CSS.index("@media print{"):]
        self.assertIn("th{white-space:normal;word-break:keep-all;overflow-wrap:break-word}",
                      print_block)
        self.assertIn("table td{overflow-wrap:break-word}", print_block)
        # `anywhere` feeds min-content width, which is exactly what let the
        # layout squeeze a column below the width of one word.
        self.assertNotIn("overflow-wrap:anywhere", print_block)
        self.assertRegex(CSS, r"@media \(max-width:860px\)\{\.compass")

    def test_a_cut_off_table_advertises_the_rest_on_screen(self):
        # a phone paints no scrollbar until the reader drags it, so an appendix
        # table running 493px past a 390px screen read as a complete table with
        # one narrow last column. Naming the bar keeps it in layout.
        at = CSS.index(".table-scroll{overflow-x:auto")
        base = CSS[at: CSS.index("}", at)]
        self.assertIn("scrollbar-width:thin", base)
        self.assertIn("scrollbar-color:", base)
        self.assertRegex(CSS, r"\.table-scroll::-webkit-scrollbar\{height:\d+px\}")
        # `tab-index` is not a CSS property at all; the focus ring under it only
        # works because render.py writes a real tabindex on the wrapper
        self.assertNotIn("tab-index", CSS)
        # code plates get the same stop, and their ring has to sit inside the
        # frame because the frame is what clips it
        self.assertRegex(CSS, r"\.codehilite pre:focus-visible\{outline:2px solid "
                              r"var\(--bronze-2\);outline-offset:-2px")

    def test_the_plate_hint_wraps_instead_of_leaving_the_page_on_phones(self):
        # the hint chip is nowrap and the caption is a centered flex row, so on
        # a 380px screen the row overflows sideways unless it may wrap.
        self.assertIn("@media (max-width:44rem){figcaption{flex-wrap:wrap", CSS)

    def test_the_printed_cover_frame_is_the_page_not_a_card_at_the_top(self):
        print_block = CSS[CSS.index("@media print{"):]
        self.assertIn(".front-page.cover{min-height:250mm", print_block)
        self.assertIn(".cover-inner{margin:0;width:100%", print_block)

    def test_the_printed_subject_index_keeps_two_columns(self):
        print_block = CSS[CSS.index("@media print{"):]
        self.assertIn(".idx-cols{columns:2", print_block)

    def test_a_unit_closes_on_the_page_it_ends_on(self):
        print_block = CSS[CSS.index("@media print{"):]
        # break-before:avoid is what the ruts used to carry, and Chromium does
        # not implement it -- the keep has to sit on the wrapper instead
        self.assertIn(".ch-close{break-inside:avoid}", print_block)
        self.assertRegex(print_block, r"\.ch-rut\{[^}]*margin-top:[0-9.]+rem")
        self.assertIn(".chapter-body .ch-close",
                      CSS[:CSS.index("@media print{")])

    def test_no_unit_padding_spills_onto_a_sheet_of_its_own(self):
        print_block = CSS[CSS.index("@media print{"):]
        # 2.2rem of screen padding under a line that ends 15pt from the box edge
        # buys an empty page: Chromium keeps the sheet to paint the padding, and
        # the next unit's forced break makes it permanent.
        self.assertIn("article.chapter,article.unit{padding-bottom:0}",
                      print_block)

    def test_pdf_bookmarks_are_driven_by_css_not_injected_markers(self):
        self.assertIn("bookmark-level:1", CSS)
        self.assertIn("bookmark-label:content()", CSS)
        self.assertIn("bookmark-level:none", CSS)


class Deliverables(unittest.TestCase):
    def test_requirements_pin_the_tools_the_build_needs(self):
        text = (BOOK_DIR / "requirements.txt").read_text(encoding="utf-8")
        for pkg in ("Markdown", "Pygments", "playwright", "PyMuPDF",
                    "Pillow", "fonttools"):
            self.assertIn(pkg, text, pkg)

    def test_package_json_pins_the_mermaid_version_used(self):
        pkg = (REPO_ROOT / "package.json").read_text(encoding="utf-8")
        self.assertRegex(pkg, r'"mermaid"\s*:\s*"[^"]+"')

    def test_repository_docs_exist(self):
        for name in ("CREDITS.md", "STRUCTURE.md", "CONTRIBUTING.md", "LICENSE"):
            self.assertTrue((REPO_ROOT / name).exists(), name)
            self.assertGreater((REPO_ROOT / name).stat().st_size, 200, name)


class EndToEndNoBrowser(unittest.TestCase):
    """The whole pipeline, with diagrams degraded to source listings: this is
    the assertion that a machine without Edge still produces a legal book."""

    def test_check_mode_passes_for_both_languages(self):
        proc = subprocess.run(
            [sys.executable, str(BOOK_DIR / "build.py"), "--check",
             "--mermaid=source"],
            cwd=str(REPO_ROOT), capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("CHECK OK", proc.stdout)
        self.assertIn("20 units", proc.stdout)


if __name__ == "__main__":
    unittest.main()
