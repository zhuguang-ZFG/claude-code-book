"""A collected edition binds whole books; no page anchor may appear twice.

`load_collection` is the only gate that stops two volumes from claiming the
same anchor, so it is tested on the real registry and on deliberately broken
specs. Rendering is exercised by the collected CI job.
"""
from __future__ import annotations

import sys
import copy
import io
import re
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from yuyu_book import registry
from yuyu_book.collected import load_collection
from yuyu_book.core import BuildError
from yuyu_book import plain


def volume(volume_id: str, manifest: str, sources: str, no: str = "卷一") -> dict:
    return {"id": volume_id, "no": {"zh": no}, "title": {"zh": "测试"},
            "manifest": manifest, "sources": sources}


class CollectedEdition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = registry.load("manifest-collected.json")

    def test_the_registered_collection_binds_every_named_volume_in_order(self):
        volumes = load_collection(self.spec)
        self.assertEqual([v.id for v in volumes],
                         [raw["id"] for raw in self.spec["volumes"]])
        self.assertGreater(len(volumes), 1)
        for loaded in volumes:
            with self.subTest(volume=loaded.id):
                # the collection publishes one zh edition of every volume it binds
                self.assertIn("zh", plain.manifest_langs(loaded.manifest))
                self.assertTrue(loaded.glosses or loaded.paths or loaded.notes
                                or loaded.manifest.get("plain_optional"), loaded.id)

    def test_every_shipped_chinese_product_is_bound_into_the_collection(self):
        registered = set()
        for path in sorted(registry.BOOK_DIR.glob("manifest-*.json")):
            manifest = registry.load(path.name)
            product = manifest.get("product")
            if (product not in (None, "collected")
                    and "zh" in manifest.get("langs", [])):
                registered.add(product)
        registered.add("book")
        included = {loaded.manifest.get("product") or "book" for loaded in
                    load_collection(self.spec)}
        self.assertEqual(registered, included,
                         f"unbound products: {sorted(registered - included)}; "
                         f"unknown collection entries: {sorted(included - registered)}")

    def test_collection_volume_numbers_are_contiguous_and_match_order(self):
        numbers = [raw["no"]["zh"] for raw in self.spec["volumes"]]
        expected = [f"卷{number}" for number in (
            "一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一")]
        self.assertEqual(numbers, expected)

    def test_two_volumes_may_not_share_one_page_anchor(self):
        with self.assertRaisesRegex(BuildError, "appears in both"):
            load_collection({"volumes": [volume("vol1", "manifest-prompt.json",
                                               "sources-prompt.json"),
                                         volume("vol2", "manifest-prompt.json",
                                                "sources-prompt.json")]})

    def test_a_volume_id_may_not_repeat(self):
        with self.assertRaisesRegex(BuildError, "duplicate volume id"):
            load_collection({"volumes": [volume("vol1", "manifest-prompt.json",
                                               "sources-prompt.json"),
                                         volume("vol1", "manifest-kimi.json",
                                                "sources-kimi.json")]})

    def test_a_collection_without_volumes_is_refused(self):
        with self.assertRaisesRegex(BuildError, "declares no volumes"):
            load_collection({"volumes": []})

    def test_a_volume_door_cannot_claim_another_units_anchor(self):
        with self.assertRaisesRegex(BuildError, "appears in both"):
            load_collection({"volumes": [volume("kimi-front", "manifest-kimi.json",
                                               "sources-kimi.json")]})

    def test_a_guide_cannot_claim_a_volume_anchor(self):
        spec = copy.deepcopy(self.spec)
        spec["guide"] = {"id": "vol1", "zh": "合集导读.md"}
        with self.assertRaisesRegex(BuildError, "appears in both"):
            load_collection(spec)

    def test_a_guide_cannot_replace_the_contents(self):
        spec = copy.deepcopy(self.spec)
        spec["guide"] = {"id": "toc", "zh": "合集导读.md"}
        with self.assertRaisesRegex(BuildError, "is reserved"):
            load_collection(spec)

    def test_the_same_two_volumes_bind_cleanly_when_nothing_collides(self):
        volumes = load_collection({"volumes": [
            volume("vol1", "manifest-prompt.json", "sources-prompt.json"),
            volume("vol2", "manifest-kimi.json", "sources-kimi.json")]})
        self.assertEqual([v.id for v in volumes], ["vol1", "vol2"])


class VolumeReading(unittest.TestCase):
    """The volume door has one line of its own: where this volume sits.

    The motto is the volume's subtitle, which says what the book is about and
    nothing about reading it after (or before) another volume. Before this the
    slot was filled with `{}`, so every door printed the same silent gap.
    """

    @classmethod
    def setUpClass(cls):
        cls.spec = registry.load("manifest-collected.json")

    def test_every_bound_volume_carries_a_reading_note(self):
        volumes = load_collection(self.spec)
        seen = {}
        for loaded in volumes:
            with self.subTest(volume=loaded.id):
                note = loaded.reading.get("zh", "")
                self.assertTrue(note.strip(), f"{loaded.id} has no reading note")
                self.assertLessEqual(len(note), 80, f"{loaded.id}: {len(note)} chars")
                self.assertNotIn(note, seen, f"{loaded.id} repeats {seen.get(note)}")
                seen[note] = loaded.id

    def test_the_door_prints_the_note_under_the_motto(self):
        from yuyu_book import pages
        out = pages.volume_divider(
            {"id": "vol9", "no": {"zh": "卷九"}, "title": {"zh": "提示词工程"},
             "motto": {"zh": "副标题"}, "goal": {"zh": "卷一没有这一域，当补章读。"}},
            "zh", 9, [("p1", "第一篇", "把需求变成能检查的任务")])
        self.assertIn('<p class="pd-motto">副标题</p>', out)
        self.assertIn('<p class="pd-goal">卷一没有这一域，当补章读。</p>', out)
        self.assertLess(out.index("pd-motto"), out.index("pd-goal"))

    def test_the_door_can_state_the_volume_size(self):
        from yuyu_book import pages
        out = pages.volume_divider(
            {"id": "vol9", "no": {"zh": "卷九"}, "title": {"zh": "提示词工程"},
             "motto": {"zh": "副标题"}, "goal": {"zh": "读完再走。"}},
            "zh", 9, [("p1", "第一篇", "把需求变成能检查的任务")],
            counts="4 篇 · 18 章")
        self.assertIn('<p class="pd-count">4 篇 · 18 章</p>', out)
        self.assertEqual(pages.ui("volume_count", "en").format(
            parts=4, chapters=18), "4 parts · 18 chapters")
        self.assertLess(out.index("pd-title"), out.index("pd-count"))
        self.assertLess(out.index("pd-count"), out.index("pd-motto"))

    def test_a_volume_without_a_note_prints_no_empty_paragraph(self):
        from yuyu_book import pages
        out = pages.volume_divider(
            {"id": "vol1", "no": {"zh": "卷一"}, "title": {"zh": "总纲"},
             "motto": {}, "goal": {}}, "zh", 1, [])
        self.assertNotIn("pd-motto", out)
        self.assertNotIn("pd-goal", out)


class VolumeStamp(unittest.TestCase):
    """Every volume restarts its own part and chapter numbers, so the eyebrow
    is the only place in the omnibus where the bound book can name itself."""

    def test_the_volume_rides_in_front_of_every_unit_eyebrow(self):
        from yuyu_book.app import _stamp_volume
        body = ['<p class="eyebrow">第一部分 基础篇 · 第 1 章</p>',
                "<p>正文</p>",
                '<p class="eyebrow">附录 A · 导航</p>']
        out = _stamp_volume(body, "卷三")
        self.assertEqual(out[1], "<p>正文</p>")
        for chunk in (out[0], out[2]):
            self.assertIn('<span class="vol-tag">卷三</span>', chunk)
        self.assertEqual(out[0].count('class="eyebrow"'), 1)

    def test_a_unit_without_an_eyebrow_is_left_alone(self):
        from yuyu_book.app import _stamp_volume
        self.assertEqual(_stamp_volume(["<p>前言没有眉标</p>"], "卷一"),
                         ["<p>前言没有眉标</p>"])


class CollectionNavigation(unittest.TestCase):
    """Exercise real Markdown assembly; capture only the expensive PDF pass."""

    @classmethod
    def setUpClass(cls):
        from yuyu_book import app
        from yuyu_book.core import REPO_ROOT

        scratch = REPO_ROOT / ".scratch"
        scratch.mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="collection-test-", dir=scratch)
        cls.addClassCleanup(temporary.cleanup)
        root = Path(temporary.name)
        guide = root / "guide.md"
        guide.write_text(
            "# 合集导读\n\n"
            "[恢复会话](../../kimi/ch07.md#76-会话从列表里消失后怎样找回再分叉)\n\n"
            "[构造任务](../../prompt/ch01.md)\n", encoding="utf-8")
        spec = copy.deepcopy(registry.load("manifest-collected.json"))
        spec["volumes"] = [v for v in spec["volumes"] if v["id"] in ("vol8", "vol9", "vol10")]
        spec["guide"] = {"id": "collection-guide",
                         "zh": guide.relative_to(REPO_ROOT).as_posix()}
        volumes = load_collection(spec)
        pdf_path = root / "captured.pdf"
        pdf_path.write_bytes(b"PDF pass captured by test")
        original_load = app.load_unit

        def with_cross_volume_link(*args, **kwargs):
            unit = original_load(*args, **kwargs)
            if unit.id == "kimi-front":
                unit.md += "\n\n[跨册任务](../prompt/ch01.md)\n"
            return unit

        with redirect_stdout(io.StringIO()), \
                patch.object(app, "load_unit", side_effect=with_cross_volume_link), \
                patch.object(app, "print_with_index", return_value=(pdf_path, {})) as printer, \
                patch("yuyu_book.pdf.sheet_count", return_value=1):
            output = app.build_collected(
                "zh", spec, volumes, mode="source", browser=None, autolink=True,
                out_dir=root, do_pdf=True, edge=None, plain_layer=False)
        cls.html = output.read_text(encoding="utf-8")
        cls.print_manifest = printer.call_args.args[3]

    def test_guide_and_cross_volume_chapter_links_stay_offline(self):
        self.assertIn('href="#prompt-ch01">跨册任务</a>', self.html)
        self.assertIn('href="#prompt-ch01">构造任务</a>', self.html)
        self.assertIn('href="#kimi-ch07-76-会话从列表里消失后怎样找回再分叉"',
                      self.html)

    def test_every_printed_contents_row_gets_a_folio_including_volume_doors(self):
        toc = re.search(r'<section class="front-page toc".*?</section>',
                        self.html, re.S).group()
        slots = re.findall(r'data-ref="([^"]+)"', toc)
        self.assertEqual(list(self.print_manifest.toc_rows), slots)
        self.assertTrue({"collection-guide", "vol8", "vol9"}.issubset(slots))

    def test_guide_and_volume_sources_are_bookmarked_and_reachable(self):
        anchors = {entry.anchor for entry in self.print_manifest.outline}
        self.assertTrue({"collection-guide", "vol8-subject-index", "vol9-sources"}
                        .issubset(anchors))
        self.assertNotIn("vol10-sources", anchors)
        rail = re.search(r'<nav class="rail".*?</nav>', self.html, re.S).group()
        for anchor in ("collection-guide", "vol8-subject-index", "vol9", "vol10", "vol9-sources"):
            self.assertIn(f'href="#{anchor}"', rail)
        self.assertIn('class="collection-jumps no-print"', self.html)


if __name__ == "__main__":
    unittest.main()
