"""Regression checks for the Omp acceptance gates."""
from contextlib import redirect_stderr, redirect_stdout
import copy
import importlib.util
import io
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

from omp.overhaul import audit_delivery, audit_structure, markdown_scan


class StructureGateTests(unittest.TestCase):
    def audit_text(self, text):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ch01.md"
            path.write_text(text, encoding="utf-8")
            return audit_structure.audit(path)

    def test_empty_manuscript_tree_fails_strict_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(audit_structure, "ROOT", Path(directory)):
                with patch("sys.argv", ["audit_structure.py", "--check"]):
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        self.assertEqual(audit_structure.main(), 1)

    def test_csv_mode_still_fails_missing_elements(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for number in range(1, 34):
                (root / f"ch{number:02}.md").write_text("# Incomplete chapter\n", encoding="utf-8")
            with patch.object(audit_structure, "ROOT", root):
                with patch("sys.argv", ["audit_structure.py", "--check", "--csv"]):
                    with redirect_stdout(io.StringIO()):
                        self.assertEqual(audit_structure.main(), 1)

    def test_opening_audits_do_not_share_previous_chapters(self):
        self.assertEqual(audit_structure.prose_before_first_h2("# First\n\nOpening.\n\n## Next"), ["Opening."])
        self.assertEqual(audit_structure.prose_before_first_h2("# Second\n\n## Next"), [])

    def test_markdown_example_cannot_supply_chapter_requirements(self):
        row = self.audit_text(
            "# Chapter\n\nA concrete opening scenario with enough words to pass the opening check.\n\n"
            "````markdown\n## 跟做实验\n```sh\nomp --version\n```\n"
            "## 翻车对照\n| 问题 | 结果 |\n| --- | --- |\n| 错误 | 重试 |\n"
            "![示例](images/example.jpg)\n御舆\n版本核对：本机已验\n````\n"
        )
        for element in ("e2_principle_figure", "e3_runnable_experiment", "e4_pit_table",
                        "e5_yuyu_isomorphism", "e6_pin_checklist", "mark_verified"):
            self.assertEqual(row[element], "n", element)

    def test_commented_out_content_cannot_supply_chapter_requirements(self):
        row = self.audit_text(
            "# Chapter\n\nA concrete opening scenario with enough words to pass the opening check.\n\n"
            "<!--\n## 跟做实验\n```sh\nomp --version\n```\n"
            "## 翻车对照\n| 问题 | 结果 |\n| --- | --- |\n| 错误 | 重试 |\n"
            "![示例](images/example.jpg)\n御舆\n版本核对：本机已验\n-->\n"
        )
        for element in ("e2_principle_figure", "e3_runnable_experiment", "e4_pit_table",
                        "e5_yuyu_isomorphism", "e6_pin_checklist", "mark_verified"):
            self.assertEqual(row[element], "n", element)

    def test_tilde_mermaid_counts_as_a_real_figure(self):
        row = self.audit_text("# Chapter\n\n~~~mermaid\nflowchart LR\n  FIRST --> SECOND\n~~~\n")
        self.assertEqual(row["e2_principle_figure"], "Y")
        self.assertEqual(row["mermaid"], 1)

    def test_versioned_binary_observation_is_a_verification_marker(self):
        row = self.audit_text("# Chapter\n\n本机 18.16.0 回「在线」且 exit 0（facts/print-mode-online.txt）。\n")
        self.assertEqual(row["mark_verified"], "Y")

    def test_mermaid_info_must_match_the_builder(self):
        for info in ("Mermaid", "mermaid example"):
            with self.subTest(info=info):
                row = self.audit_text(f"# Chapter\n\n```{info}\nflowchart LR\n  FIRST --> SECOND\n```\n")
                self.assertEqual(row["e2_principle_figure"], "n")
                self.assertEqual(row["mermaid"], 0)

    def test_missing_chapter_cannot_be_replaced_by_an_extra_filename(self):
        valid_row = {key: "Y" for key in (
            "e1_opening_scene", "e2_principle_figure", "e3_runnable_experiment",
            "e4_pit_table", "e5_yuyu_isomorphism", "e6_pin_checklist", "mark_verified")}
        valid_row.update(unit="chapter", e3_cmd_blocks=1, han=0, chars=0)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for number in (*range(1, 33), 99):
                (root / f"ch{number:02}.md").touch()
            with patch.object(audit_structure, "ROOT", root):
                with patch.object(audit_structure, "audit", return_value=valid_row):
                    with patch("sys.argv", ["audit_structure.py", "--check"]):
                        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                            self.assertEqual(audit_structure.main(), 1)

    def test_pipe_in_prose_does_not_count_as_a_failure_table(self):
        row = self.audit_text("# Chapter\n\n## 翻车\n| 这里只是一行示例 | 不是表格 |\n")
        self.assertEqual(row["e4_pit_table"], "n")

    def test_unclosed_fence_fails_even_when_all_other_requirements_pass(self):
        valid_row = {key: "Y" for key in (
            "e1_opening_scene", "e2_principle_figure", "e3_runnable_experiment",
            "e4_pit_table", "e5_yuyu_isomorphism", "e6_pin_checklist", "mark_verified")}
        valid_row.update(unit="chapter", e3_cmd_blocks=1, han=0, chars=0,
                         errors=["line 3: unclosed code fence"])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for number in range(1, 34):
                (root / f"ch{number:02}.md").touch()
            with patch.object(audit_structure, "ROOT", root):
                with patch.object(audit_structure, "audit", return_value=valid_row):
                    with patch("sys.argv", ["audit_structure.py", "--check", "--csv"]):
                        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                            self.assertEqual(audit_structure.main(), 1)


class DeliveryGateTests(unittest.TestCase):
    def run_with_registry_change(self, filename, change):
        original = audit_delivery.load_json

        def changed(root, name):
            data = copy.deepcopy(original(root, name))
            if name == filename:
                change(data)
            return data

        with patch.object(audit_delivery, "load_json", side_effect=changed):
            return audit_delivery.check()

    def test_shipped_delivery_passes(self):
        self.assertEqual(audit_delivery.check(), [])

    def test_one_part_without_diagrams_fails_even_when_total_is_sufficient(self):
        def remove_diagrams(manifest):
            manifest["parts"][0]["units"] = [{"id": "omp-ch02", "zh": "omp/ch02.md"}]
            manifest["parts"][1]["units"].extend([
                {"id": "omp-ch01", "zh": "omp/ch01.md"},
                {"id": "omp-ch03", "zh": "omp/ch03.md"},
            ])

        errors = self.run_with_registry_change("manifest-omp.json", remove_diagrams)
        self.assertTrue(any("omp-p1: no Mermaid" in error for error in errors))
        self.assertFalse(any("at least 12" in error for error in errors))

    def test_shared_term_cannot_point_to_unknown_book_term(self):
        errors = self.run_with_registry_change(
            "glosses-omp.json",
            lambda terms: terms["agent-harness"].update(shared_with="missing-term"),
        )
        self.assertTrue(any("unknown shared glossary ID" in error for error in errors))

    def test_book_implementation_cannot_leak_into_definition(self):
        errors = self.run_with_registry_change(
            "glosses-omp.json",
            lambda terms: terms["agent-harness"]["plain"].update(zh="QueryEngine"),
        )
        self.assertTrue(any("implementation leaked" in error for error in errors))

    def test_missing_front_and_appendix_are_reported(self):
        for location in ("front", "appendices"):
            def remove_manuscript(manifest):
                unit = manifest["front"] if location == "front" else manifest["appendices"][0]
                unit["zh"] = "omp/missing-manuscript.md"

            with self.subTest(location=location):
                errors = self.run_with_registry_change("manifest-omp.json", remove_manuscript)
                self.assertTrue(any("missing-manuscript.md" in error for error in errors))

    def test_reference_image_in_appendix_is_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "appendix.md"
            path.write_text('![Caption][drawing]\n\n[drawing]: images/missing.jpg "Caption"\n', encoding="utf-8")
            errors = self.run_with_registry_change(
                "manifest-omp.json",
                lambda manifest: manifest["appendices"][0].update(zh=str(path)),
            )
        self.assertTrue(any("images/missing.jpg" in error for error in errors))

    def test_malformed_shared_term_has_a_diagnostic(self):
        errors = self.run_with_registry_change(
            "glosses-omp.json",
            lambda terms: terms["agent-harness"].update(shared_with=["agent-harness"]),
        )
        self.assertTrue(any("shared_with" in error for error in errors))

    def test_invalid_registry_is_reported_without_a_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "yuyu-book").mkdir()
            (root / "yuyu-book/manifest-omp.json").write_text("{", encoding="utf-8")
            errors = audit_delivery.check(root)
        self.assertTrue(any("manifest-omp.json" in error for error in errors))

    def test_nested_mermaid_example_cannot_supply_part_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "example.md"
            path.write_text("````markdown\n```mermaid\nflowchart LR\n  FIRST --> SECOND\n```\n````\n", encoding="utf-8")
            errors = self.run_with_registry_change(
                "manifest-omp.json",
                lambda manifest: manifest["parts"][0].update(units=[{"id": "omp-ch01", "zh": str(path)}]),
            )
        self.assertTrue(any("omp-p1: no Mermaid diagram" in error for error in errors))


class MarkdownScanTests(unittest.TestCase):
    def test_nested_example_keeps_the_outer_fence(self):
        content = markdown_scan.scan_markdown(
            "Before\n````markdown\n```mermaid\nflowchart LR\n  FIRST --> SECOND\n```\n````\nAfter"
        )
        self.assertEqual([language for language, _ in content.blocks], ["markdown"])
        self.assertEqual(content.prose.splitlines(), ["Before", "", "", "", "", "", "", "After"])
        self.assertEqual(content.errors, [])

    def test_comment_can_close_before_visible_content_on_the_same_line(self):
        content = markdown_scan.scan_markdown("Before <!-- hidden\n```mermaid\n--> After")
        self.assertEqual(content.prose, "Before \n\n After")
        self.assertEqual(content.blocks, [])
        self.assertEqual(content.errors, [])

    def test_unclosed_markdown_reports_its_location(self):
        content = markdown_scan.scan_markdown("Before\n~~~mermaid\nflowchart LR")
        self.assertEqual(content.blocks, [])
        self.assertEqual(content.errors, ["line 2: unclosed code fence"])

    def test_only_rendered_images_are_collected(self):
        prose = (
            '`![Example](images/code.jpg)`\n\n'
            '![Actual][picture]\n\n[picture]: <images/my%20image.jpg> "Caption"\n\n'
            '<img src="images/html.jpg">'
        )
        self.assertEqual(markdown_scan.image_sources(prose), ["images/my%20image.jpg", "images/html.jpg"])

    def test_literal_comment_marker_in_inline_code_does_not_hide_prose(self):
        text = "Use `<!--` in an example.\n\n## Still visible\n"
        content = markdown_scan.scan_markdown(text)
        self.assertEqual(content.prose, text.rstrip("\n"))
        self.assertEqual(content.errors, [])


REPO_ROOT = Path(__file__).resolve().parents[1]
# plates are drawn at 1200x800 logical pixels with --scale 2
PLATE_PIXELS = (2400, 1600)
PAPER_RGB = (251, 247, 239)
# figures whose bitmap comes from a hand-written SVG export, not the Pillow script
UPSTREAM_SHOTS = frozenset("""
    fig11-3-lsp-shot fig5-5-model-selector fig6-6-ask-shot fig6-7-slash-shot
""".split())
SVG_DERIVED = frozenset("""
    fig12-3-web-github fig17-1-model-roles fig19-2-skill-invoke fig20-2-mcp-transport
    fig21-1-custom-tool fig22-2-ext-load fig23-1-config-layers fig27-1-review-checklist
    fig28-1-sdk-embed fig33-3-tool-registry fig4-3-alpine-pitfall fig4-4-completions
    fig5-3-login-flow fig5-4-models-yml fig9-1-hashline-anchor fig9-2-hashline-vs-replace
""".split())


def edge_has_ink(image, box):
    """True when a border band holds anything but bare paper.

    Deviation is measured from paper, not from zero: getextrema returns
    absolute channel values, so paper itself reads 251. Any channel more
    than 30 away counts. The palest card fills differ by at most 24 on
    their worst channel, so they stay quiet; drawn ink differs by hundreds.
    """
    band = image.crop(box)
    return max(max(high - paper, paper - low)
               for (low, high), paper in zip(band.getextrema(), PAPER_RGB)) > 30


def load_illustration_script():
    path = REPO_ROOT / "scripts" / "draw_omp_illustrations.py"
    spec = importlib.util.spec_from_file_location("draw_omp_illustrations", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class IllustrationCoverageTests(unittest.TestCase):
    """Every hand-drawn JPG needs a reproducible source."""

    def test_every_illustration_has_a_generator_or_svg_source(self):
        images = {path.stem for path in (REPO_ROOT / "omp" / "images").glob("*.jpg")}
        generators = set(load_illustration_script().FIGURES)
        self.assertEqual(images - generators - SVG_DERIVED - UPSTREAM_SHOTS, set(),
                         "hand-drawn images with no redraw source")

    def test_generator_names_all_exist_as_images(self):
        images = {path.stem for path in (REPO_ROOT / "omp" / "images").glob("*.jpg")}
        generators = set(load_illustration_script().FIGURES)
        self.assertEqual(generators - images, set(), "registered figures without a bitmap")

    def test_source_scope_names_resolve_to_real_images(self):
        """Those scope strings are printed, not inert.

        backmatter renders every scope field as reg-scope text on the book's
        own sources page, so a renamed plate leaves a filename that does not
        exist in the shipped volume. Nothing else reads those fields, and the
        renumber pass rewrote only markdown, so this is the cheapest place to
        catch it.
        """
        stems = {path.stem for path in (REPO_ROOT / "omp" / "images").glob("*.jpg")}
        document = (REPO_ROOT / "yuyu-book" / "sources-omp.json").read_text(encoding="utf-8")
        tokens = re.findall(r"fig[0-9A-Z]+-\d+(?:[-a-z0-9]*)?", document)
        unresolved = sorted({token for token in tokens
                             if token not in stems
                             and not any(stem.startswith(token + "-") for stem in stems)})
        self.assertEqual(unresolved, [], "scope citations naming plates that do not exist")

    def test_source_sets_do_not_overlap(self):
        generators = set(load_illustration_script().FIGURES)
        self.assertEqual(generators & SVG_DERIVED, set())
        self.assertEqual(generators & UPSTREAM_SHOTS, set())

    def test_plate_numbers_run_in_document_order_without_gaps(self):
        """The i-th plate in a unit must be 图<unit>-i.

        Numbers were handed out as "the next free one" while units grew, so
        ch05 ended up with two different plates both labelled 图5-3 and 28 of
        39 units ran out of order. Nothing failed: the JPEGs were fine, the
        links resolved, the audits were green. A reader cannot tell a plate
        that moved from one that was mislabelled, so pin the rule here.
        """
        plates = re.compile(r"!\[图(\d+|[A-Z])-(\d+) [^\]]*\]\(images/[^)]+\)")
        offenders = []
        for chapter in sorted((REPO_ROOT / "omp").glob("*.md")):
            text = chapter.read_text(encoding="utf-8")
            for index, match in enumerate(plates.finditer(text), start=1):
                if match.group(2) != str(index):
                    offenders.append(
                        f"{chapter.name}: 图{match.group(1)}-{match.group(2)} is plate #{index}")
        self.assertEqual(offenders, [], "plates numbered out of document order")

    def test_no_generated_plate_paints_against_its_canvas_edge(self):
        """A plate whose layout runs off the canvas is cut, not shrunk.

        That failure is invisible downstream: the JPEG is still 1200x800,
        still under the byte budget, still passes every audit -- the lost
        half is simply gone. Nine plates were laid out past the right edge
        and shipped that way until a PDF page was sampled by eye.

        Plates are drawn on paper with a margin, so the outer band must be
        bare. Screenshots are excluded: they are photographs of a window,
        full-bleed by nature.
        """
        offenders = []
        for path in sorted((REPO_ROOT / "omp" / "images").glob("*.jpg")):
            with Image.open(path) as source:
                if source.size != PLATE_PIXELS:
                    continue   # upstream screenshot, not a drawn plate
                source.draft("RGB", (600, 400))
                image = source.convert("RGB")
            width, height = image.size
            bands = ((0, 0, width, 2), (0, height - 2, width, height),
                     (0, 0, 2, height), (width - 2, 0, width, height))
            if any(edge_has_ink(image, box) for box in bands):
                offenders.append(path.stem)
        self.assertEqual(offenders, [], "plates with content on the canvas edge")


def relative_luminance(color):
    channels = []
    for index in (1, 3, 5):
        value = int(color[index:index + 2], 16) / 255
        channels.append(value / 12.92 if value <= 0.04045
                        else ((value + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def contrast_ratio(left, right):
    lighter, darker = sorted((relative_luminance(left), relative_luminance(right)),
                             reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


class PlateContrastTests(unittest.TestCase):
    """Small plate labels must not rely on the graphic orange for legibility."""

    class DrawRecorder:
        def textlength(self, value, font=None):
            return len(value) * 16

        def text(self, position, value, **kwargs):
            self.text_fill = kwargs["fill"]

        def ellipse(self, bounds, **kwargs):
            self.ellipse_fill = kwargs["fill"]

    def plate_with_recorder(self):
        module = load_illustration_script()
        recorder = self.DrawRecorder()
        plate = object.__new__(module.Drawing)
        plate.scale = 2
        plate.font = lambda size, bold=False: None
        plate.draw = recorder
        return module, plate, recorder

    def test_text_tones_meet_normal_text_contrast_on_every_fill(self):
        module, plate, recorder = self.plate_with_recorder()
        backgrounds = (module.PAPER, module.WHITE, module.PEACH,
                       module.SAGE, module.SKY)
        for name in ("MUTED", "GREEN", "BLUE", "ORANGE"):
            plate.text((60, 60), "去这儿拿", 16, getattr(module, name))
            for background in backgrounds:
                ratio = contrast_ratio(recorder.text_fill, background)
                self.assertGreaterEqual(
                    ratio, 4.5,
                    f"{name} text on {background}: {ratio:.2f}:1")

    def test_badge_background_carries_white_text_readably(self):
        module, plate, recorder = self.plate_with_recorder()
        plate.badge((60, 60), "1")
        ratio = contrast_ratio("#FFFEFA", recorder.ellipse_fill)
        self.assertGreaterEqual(ratio, 4.5, f"badge text contrast {ratio:.2f}:1")

    def test_label_font_size_has_a_legibility_floor(self):
        module, plate, _ = self.plate_with_recorder()
        with self.assertRaises(ValueError):
            plate.text((60, 60), "先别读", 15, module.MUTED)


class SvgPlateContrastTests(unittest.TestCase):
    """Hand-written SVG plates share the generated plates' text contrast floor."""

    SVG_DIR = REPO_ROOT / "omp" / "overhaul" / "visual-redesign"
    # Fills that actually sit under .muted / .accent text. Saturated cards carry
    # .white text instead and are covered by PlateContrastTests.
    LIGHT_FILLS = frozenset("""
        #FAF7EF #FFFDF7 #F0EEE4 #E3EAD9 #E8E5D9 #E9E7DB #EEEDE3 #F7E6DC
    """.split())

    def test_text_classes_clear_the_contrast_floor_on_every_light_fill(self):
        offenders = []
        for path in sorted(self.SVG_DIR.glob("*.svg")):
            text = path.read_text(encoding="utf-8")
            style = re.search(r"<style>(.*?)</style>", text, re.S)
            self.assertIsNotNone(style, f"{path.name}: no style block")
            for name in ("muted", "accent"):
                declaration = re.search(
                    rf"\.{name}\s*\{{[^}}]*?fill:\s*(#[0-9A-Fa-f]{{6}})",
                    style.group(1))
                self.assertIsNotNone(declaration, f"{path.name}: no .{name} fill")
                for background in self.LIGHT_FILLS:
                    ratio = contrast_ratio(declaration.group(1), background)
                    if ratio < 4.5:
                        offenders.append(
                            f"{path.name}: .{name} on {background} {ratio:.2f}:1")
        self.assertEqual(offenders, [], "SVG plate text below 4.5:1")

    def test_white_labels_clear_the_contrast_floor_on_their_cards(self):
        """White plate labels sit on ink-dark cards, not on graphic orange."""
        offenders = []
        for path in sorted(self.SVG_DIR.glob("*.svg")):
            text = path.read_text(encoding="utf-8")
            style = re.search(r"<style>(.*?)</style>", text, re.S)
            self.assertIsNotNone(style, f"{path.name}: no style block")
            white = re.search(
                r"\.white\s*\{[^}]*?fill:\s*(#[0-9A-Fa-f]{6})", style.group(1))
            self.assertIsNotNone(white, f"{path.name}: no .white fill")

            cards = []
            for shape in re.finditer(r"<(rect|path)\b([^>]*)>", text):
                tag, attrs = shape.groups()
                def attribute(name):
                    return re.search(rf'\b{name}="([^"]*)"', attrs)
                fill = attribute("fill")
                if not fill or not re.fullmatch(r"#[0-9A-Fa-f]{6}", fill.group(1)):
                    continue
                if tag == "rect":
                    x, y = attribute("x"), attribute("y")
                    width, height = attribute("width"), attribute("height")
                    if not all((x, y, width, height)):
                        continue
                    left, top = float(x.group(1)), float(y.group(1))
                    right = left + float(width.group(1))
                    bottom = top + float(height.group(1))
                else:
                    d = attribute("d")
                    if not d:
                        continue
                    numbers = [float(v) for v in re.findall(
                        r"-?\d+(?:\.\d+)?", d.group(1))]
                    if len(numbers) < 6 or len(numbers) % 2:
                        continue
                    xs, ys = numbers[0::2], numbers[1::2]
                    left, right = min(xs), max(xs)
                    top, bottom = min(ys), max(ys)
                cards.append((left, top, right, bottom, fill.group(1)))

            for label in re.finditer(r"<text\b([^>]*)>(.*?)</text>", text, re.S):
                attrs, caption = label.groups()
                if not re.search(r'class="[^"]*\bwhite\b', attrs):
                    continue
                point = re.search(r'\bx="([\d.]+)"\s+y="([\d.]+)"', attrs)
                self.assertIsNotNone(point, f"{path.name}: white label without x/y")
                x, y = map(float, point.groups())
                behind = [fill for left, top, right, bottom, fill in cards
                          if left <= x <= right and top <= y <= bottom]
                self.assertTrue(behind, f"{path.name}: white label "
                                        f"{caption.strip()[:20]!r} has no card")
                background = min(behind, key=relative_luminance)
                ratio = contrast_ratio(white.group(1), background)
                if ratio < 4.5:
                    offenders.append(
                        f"{path.name}: white on {background} {ratio:.2f}:1")
        self.assertEqual(offenders, [], "white plate labels below 4.5:1")


class SvgPlateCraftTests(unittest.TestCase):
    """Hand-written SVG panels must not fall back to slide-deck rectangles."""

    SVG = REPO_ROOT / "omp" / "overhaul" / "visual-redesign" / "alpine-pitfall.svg"
    PANELS = {
        "warn": (96, 310, 456, 670),
        "soft": (580, 310, 940, 670),
        "hi": (1064, 310, 1364, 670),
    }

    def test_hero_panels_have_uneven_drawn_edges_and_grain(self):
        text = self.SVG.read_text(encoding="utf-8")

        for name, (left, top, right, bottom) in self.PANELS.items():
            self.assertIsNone(
                re.search(rf'<rect\b[^>]*\bclass="{name}"', text),
                f"{name} panel is still a machine-perfect rect")
            path = re.search(
                rf'<path\b[^>]*\bclass="{name}"[^>]*\bd="([^"]+)"', text)
            self.assertIsNotNone(path, f"{name} panel has no drawn path")
            d = path.group(1)
            self.assertGreaterEqual(d.count("Q"), 4,
                                    f"{name} panel has no hand-drawn corners")
            pairs = [(float(x), float(y)) for x, y in re.findall(
                r"(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)", d)]
            self.assertGreaterEqual(len(pairs), 10, f"{name} path is too plain")
            xs, ys = [x for x, _ in pairs], [y for _, y in pairs]
            overshoot = max(left - min(xs), top - min(ys),
                            max(xs) - right, max(ys) - bottom)
            self.assertGreaterEqual(overshoot, 6,
                                    f"{name} wobble is too small to see")
        style = re.search(r"<style>(.*?)</style>", text, re.S)
        self.assertIsNotNone(style, "SVG must carry an inline style block")
        css = style.group(1)
        widths = []
        for name in self.PANELS:
            rule = re.search(rf"\.{name}\s*\{{([^}}]*)\}}", css)
            self.assertIsNotNone(rule, f"{name} panel needs a CSS class rule")
            width = re.search(r"\bstroke-width\s*:\s*([\d.]+)", rule.group(1))
            self.assertIsNotNone(
                width, f"{name} panel needs an effective CSS stroke width")
            widths.append(float(width.group(1)))
        self.assertEqual(sorted(widths), [2.2, 2.8, 3.0],
                         "panels need three distinct effective stroke weights")

        hatch = re.findall(
            r'<g\b[^>]*\bclass="panel-hatch"[^>]*\bopacity="([\d.]+)"[^>]*>(.*?)</g>',
            text, re.S)
        self.assertEqual(len(hatch), 3, "each panel needs pencil grain")
        for opacity, body in hatch:
            self.assertTrue(0.18 <= float(opacity) <= 0.3,
                            f"grain opacity {opacity} is not visible enough")
            self.assertGreaterEqual(body.count("<path"), 5,
                                    "grain needs several hatch strokes")

    def test_command_card_is_drawn_not_a_sharp_rect(self):
        text = self.SVG.read_text(encoding="utf-8")
        self.assertIsNone(
            re.search(r'<rect\b[^>]*\bfill="#B0401C"', text),
            "command card is still a machine-perfect rect")
        card = re.search(r'<path\b[^>]*\bclass="cmd"[^>]*\bd="([^"]+)"', text)
        self.assertIsNotNone(card, "command card has no drawn path")
        d = card.group(1)
        self.assertGreaterEqual(d.count("Q"), 4,
                                "command card has no hand-drawn corners")
        pairs = [(float(x), float(y)) for x, y in re.findall(
            r"(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)", d)]
        self.assertGreaterEqual(len(pairs), 10,
                                "command card path is too plain")
        xs, ys = [x for x, _ in pairs], [y for _, y in pairs]
        overshoot = max(612 - min(xs), 440 - min(ys),
                        max(xs) - 908, max(ys) - 560)
        self.assertGreaterEqual(overshoot, 2,
                                "command card wobble is too small to see")
        self.assertRegex(text, r'<path\b[^>]*\bclass="cmd-echo"',
                         "command card needs a pencil underdrawing")

    def test_panel_borders_clear_the_graphic_contrast_floor(self):
        text = self.SVG.read_text(encoding="utf-8")
        background = re.search(
            r'<rect width="1440" height="960" fill="(#[0-9A-Fa-f]{6})"', text)
        self.assertIsNotNone(background, "plate has no canvas fill")
        style = re.search(r"<style>(.*?)</style>", text, re.S)
        self.assertIsNotNone(style, "SVG must carry an inline style block")
        css = style.group(1)
        for name in self.PANELS:
            rule = re.search(rf"\.{name}\s*\{{([^}}]*)\}}", css)
            self.assertIsNotNone(rule, f"{name} panel needs a CSS class rule")
            stroke = re.search(
                r"\bstroke\s*:\s*(#[0-9A-Fa-f]{6})", rule.group(1))
            self.assertIsNotNone(stroke, f"{name} panel needs a border color")
            ratio = contrast_ratio(stroke.group(1), background.group(1))
            self.assertGreaterEqual(
                ratio, 3.0,
                f"{name} border is only {ratio:.2f}:1 against the canvas")

    def test_header_mark_is_long_drawn_orange_with_echo(self):
        text = self.SVG.read_text(encoding="utf-8")
        header_paths = []
        for attrs in re.findall(r"<path\b([^>]*)>", text):
            stroke = re.search(r'\bstroke="(#[0-9A-Fa-f]{6})"', attrs)
            width = re.search(r'\bstroke-width="([\d.]+)"', attrs)
            d = re.search(r'\bd="([^"]+)"', attrs)
            if not all((stroke, width, d)):
                continue
            numbers = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", d.group(1))]
            if len(numbers) < 4 or len(numbers) % 2:
                continue
            xs, ys = numbers[0::2], numbers[1::2]
            if min(xs) <= 90 and min(ys) <= 100 and max(ys) >= 60:
                header_paths.append(
                    (stroke.group(1), float(width.group(1)), d.group(1), attrs))

        mark = [item for item in header_paths
                if item[0].upper() == "#DB582C" and item[1] >= 6
                and item[2].count("Q") >= 1]
        self.assertEqual(len(mark), 1,
                         "header mark must be one drawn orange stroke")
        numbers = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", mark[0][2])]
        self.assertGreaterEqual(max(numbers[0::2]), 170,
                                "header mark must reach at least x=170")
        echo = [attrs for _, width, d, attrs in header_paths
                if width < 3 and d.count("Q") >= 1
                and re.search(r'\bopacity="(0?\.\d+|1\.0)"', attrs)
                and 0.18 <= float(re.search(
                    r'\bopacity="(0?\.\d+|1\.0)"', attrs).group(1)) <= 0.35]
        self.assertTrue(echo, "header mark needs a low-opacity pencil echo")

        label = re.search(
            r'<text\b([^>]*)>安装环境</text>', text)
        self.assertIsNotNone(label, "header label is missing")
        x = re.search(r'\bx="([\d.]+)"', label.group(1))
        self.assertIsNotNone(x, "header label needs x")
        self.assertGreaterEqual(float(x.group(1)), 185,
                                "header label is too close to the mark")
        self.assertGreaterEqual(float(x.group(1)) - max(numbers[0::2]), 12,
                                "header label must clear the drawn mark")

    def test_dependency_caption_uses_ink_not_faint_grey(self):
        text = self.SVG.read_text(encoding="utf-8")
        caption = re.search(
            r'<text\b([^>]*)>包名以本节命令为准</text>', text)
        self.assertIsNotNone(caption, "panel-02 dependency caption is missing")
        attrs = caption.group(1)
        class_attr = re.search(r'\bclass="([^"]+)"', attrs)
        self.assertIsNotNone(class_attr, "dependency caption needs a class")
        classes = set(class_attr.group(1).split())
        self.assertNotIn("muted", classes,
                         "dependency caption is still faint grey")
        self.assertIn("ink", classes,
                      "dependency caption should use the ink fill")
        style = re.search(r"<style>(.*?)</style>", text, re.S)
        self.assertIsNotNone(style, "SVG must carry an inline style block")
        rule = re.search(
            r"\.ink\s*\{[^}]*?fill:\s*(#[0-9A-Fa-f]{6})", style.group(1))
        self.assertIsNotNone(rule, "dependency caption ink fill is missing")
        ratio = contrast_ratio(rule.group(1), "#F0EEE4")
        self.assertGreaterEqual(
            ratio, 7.0,
            f"dependency caption is still too faint on the soft panel: {ratio:.2f}:1")

    def test_connectors_have_drawn_flow_and_weight(self):
        text = self.SVG.read_text(encoding="utf-8")
        flows = []
        for attrs in re.findall(r"<path\b([^>]*)>", text):
            if 'class="flow"' not in attrs:
                continue
            d = re.search(r'\bd="([^"]+)"', attrs)
            if d:
                flows.append(d.group(1))
        self.assertEqual(len(flows), 2, "plate needs two connector paths")
        for d in flows:
            self.assertGreaterEqual(d.count("Q"), 1,
                                    "connector is still a straight line")
        style = re.search(r"<style>(.*?)</style>", text, re.S)
        self.assertIsNotNone(style, "SVG must carry an inline style block")
        rule = re.search(r"\.flow\s*\{([^}]*)\}", style.group(1))
        self.assertIsNotNone(rule, "connectors need a CSS rule")
        width = re.search(r"\bstroke-width\s*:\s*([\d.]+)", rule.group(1))
        self.assertIsNotNone(width, "connectors need a CSS stroke width")
        self.assertEqual(float(width.group(1)), 4.2,
                         "connector stroke drifted from the tuned weight")
        marker = re.search(r"<marker\b[^>]*>(.*?)</marker>", text, re.S)
        self.assertIsNotNone(marker, "connectors need an arrowhead")
        head = re.search(r'\bstroke-width="([\d.]+)"', marker.group(1))
        self.assertIsNotNone(head, "arrowhead needs a stroke width")
        self.assertEqual(float(head.group(1)), 2.2,
                         "arrowhead stroke drifted from the tuned weight")


if __name__ == "__main__":
    unittest.main()
