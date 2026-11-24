"""Reader-facing status has to match the shelf that actually ships.

The Pages site serves the Chinese 御舆 book, the Chinese beginner reader and
the Omp Chinese HTML. It does not serve an English edition, a PDF, or the
later volumes. These checks pin that boundary in the Chinese project notes
and in the command help, and they keep the English captions and the English
CI path trigger that are already there.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = "https://zhuguang-zfg.github.io/claude-code-book/"
POLICY = "英文整书停止新增和精修"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class ReadingEntry(unittest.TestCase):
    def test_the_readme_points_at_this_repository_pages_site(self):
        readme = read("README.md")
        self.assertIn(PAGES, readme)
        self.assertNotIn("lintsinghua.github.io", readme)
        # Star history still names the upstream repository. That is attribution,
        # not the reading entry.
        self.assertIn("lintsinghua/claude-code-book", readme)

    def test_the_readme_names_what_the_site_does_not_carry(self):
        readme = read("README.md")
        self.assertIn("站点上还没有这些页面", readme)
        self.assertIn("PDF 不在 Pages 上", readme)
        for name in ("Pi", "Vibe Coding", "英文整书"):
            self.assertIn(name, readme)

    def test_vibe_is_twelve_chapters_plus_four_appendices(self):
        manifest = json.loads(read("yuyu-book/manifest-vibe.json"))
        chapters = sum(len(part["units"]) for part in manifest["parts"])
        appendix_ids = [item["id"] for item in manifest["appendices"]]
        self.assertEqual(chapters, 12)
        self.assertEqual(
            appendix_ids, ["vibe-apxa", "vibe-apxb", "vibe-apxc", "vibe-apxd"])
        start = read("README.md").index("## 第十一册")
        end = read("README.md").index("## 阅读说明")
        section = read("README.md")[start:end]
        self.assertIn("12 章加附录 A–D", section)
        self.assertNotIn("8 章", section)


class SiteCopy(unittest.TestCase):
    def test_the_committed_portal_does_not_call_the_reader_bilingual(self):
        page = read("docs/portal.html")
        source = read("yuyu-book/yuyu_book/products/portal.py")
        for text in (page, source):
            self.assertNotIn("双语入门", text)
            self.assertNotIn("施工中", text)
            self.assertNotIn("研究与试章", text)
            self.assertIn("中文入门分册", text)
        # The file in git is the offline card. The live site adds the link.
        self.assertIn("本站还没挂上它的页面", page)
        self.assertNotIn('href="omp/yuyu-omp-zh.html"', page)

    def test_the_gallery_keeps_its_english_captions(self):
        gallery = read("docs/illustration-gallery.html")
        self.assertIn("plain-en", gallery)
        self.assertIn("中英双语题注", gallery)

    def test_omp_readme_matches_the_live_html_and_stops_the_english_plan(self):
        text = read("omp/README.md")
        self.assertNotIn("站点待上线", text)
        self.assertNotIn("延后", text)
        self.assertNotIn("| 中英 |", text)
        self.assertIn(PAGES + "omp/yuyu-omp-zh.html", text)
        self.assertIn("PDF 不在 Pages 上", text)
        self.assertIn(POLICY, text)


class MaintenanceNotes(unittest.TestCase):
    def test_chinese_notes_record_that_english_maintenance_has_stopped(self):
        readme = read("README.md")
        contributing = read("CONTRIBUTING.md")
        self.assertIn(POLICY, readme)
        self.assertIn(POLICY, contributing)
        self.assertNotIn("请同步检查英文版", readme)
        self.assertNotIn("双语 PDF", readme)
        self.assertNotIn("test_manifest 会扫描全部英文单元", contributing)
        self.assertNotIn("不要只在中文里标", contributing)

    def test_structure_describes_the_omp_pages_job(self):
        text = read("STRUCTURE.md")
        self.assertNotIn("没把 omp 塞进站点", text)
        self.assertIn("omp/**", text)
        self.assertIn("omp/yuyu-omp-zh.html", text)

    def test_the_migration_note_does_not_still_sell_a_bilingual_build(self):
        text = read("docs/migrations/release-migration.md")
        self.assertNotIn("双语 PDF", text)
        self.assertNotIn("双语整书", text)
        self.assertNotIn("yuyu-agent-harness-en.html / .pdf", text)

    def test_the_package_blurb_is_chinese_only(self):
        self.assertNotIn("bilingual offline editions", read("pyproject.toml"))

    def test_the_baseline_readme_does_not_rebuild_english(self):
        text = read("docs/baseline/README.md")
        self.assertNotIn("--lang both", text)
        self.assertIn("--lang zh --pdf", text)
        self.assertIn("fragments/en/", text)

    def test_command_help_does_not_advertise_an_english_build(self):
        # Force the child process to write UTF-8: builder --help embeds 《御舆》,
        # and Windows otherwise defaults to the active code page (often GBK).
        check_help = subprocess.check_output(
            [sys.executable, "scripts/bookctl.py", "check", "--help"],
            cwd=ROOT, text=True, encoding="utf-8")
        entry_help = subprocess.check_output(
            [sys.executable, "scripts/bookctl.py", "--help"],
            cwd=ROOT, text=True, encoding="utf-8")
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "yuyu-book")
        env["PYTHONIOENCODING"] = "utf-8"
        builder_help = subprocess.check_output(
            [sys.executable, "-m", "yuyu_book", "--help"],
            cwd=ROOT, text=True, encoding="utf-8", env=env)
        self.assertNotIn("both PDF", check_help)
        self.assertIn("Chinese PDF", check_help)
        self.assertNotIn("--lang both", entry_help)
        self.assertNotIn("--lang both", builder_help)
        self.assertNotIn("--lang en", builder_help)

    def test_lang_both_is_rejected_for_every_shelf_product(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "yuyu-book")
        for product in ("book", "omp", "collected"):
            proc = subprocess.run(
                [sys.executable, "scripts/bookctl.py", "build",
                 "--product", product, "--lang", "both"],
                cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(proc.returncode, 2, product)
            self.assertIn("invalid choice", proc.stderr)
        builder = subprocess.run(
            [sys.executable, "-m", "yuyu_book", "--lang", "both"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
            env=env)
        self.assertEqual(builder.returncode, 2)
        self.assertIn("invalid choice", builder.stderr)

    def test_existing_english_hooks_stay(self):
        pages = read(".github/workflows/pages.yml")
        book = read(".github/workflows/book.yml")
        self.assertIn("- 'en/**'", pages)
        self.assertIn("name: omp-site", pages)
        self.assertIn("name: Omp", book)
        self.assertNotIn("full bilingual audit", book)
        revisions = json.loads(read("yuyu-book/revisions.json"))
        latest = revisions["entries"][0]
        self.assertTrue(any(POLICY in line for line in latest["zh"]))
        self.assertIn("构建器测试", latest["zh"][-1])
        self.assertFalse(any(POLICY in line for line in latest["en"]))


if __name__ == "__main__":
    unittest.main()
