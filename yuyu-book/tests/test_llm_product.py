"""The LLM volume is a registered, source-pinned product with its own shelf.

The preview deliberately ships three chapters, not the eighteen-chapter
companion shape. These checks pin what exists, keep future chapters from
being silently omitted, and make the source lock answer for every GitHub
source the volume cites.
"""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from yuyu_book import plain
from yuyu_book.core import REPO_ROOT, expected_ids, load_configs, load_unit, unit_stream


PREVIEW_IDS = ["llm-front", "llm-ch01", "llm-ch03", "llm-ch05", "llm-ch06"]
PREVIEW_CHAPTERS = {1, 3, 5, 6}
PLANNED_CHAPTERS = set(range(1, 16))


class LlmProduct(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest, cls.sources = load_configs(
            "manifest-llm.json", "sources-llm.json")
        cls.lock = json.loads(
            (REPO_ROOT / "llm/facts/source-lock.json").read_text(encoding="utf-8"))

    def test_preview_has_its_own_prefix_language_and_no_plain_layer(self):
        self.assertEqual(self.manifest["product"], "llm")
        self.assertEqual(self.manifest["output_prefix"], "yuyu-llm")
        self.assertEqual(plain.manifest_langs(self.manifest), ("zh",))
        self.assertTrue(self.manifest.get("plain_optional"))
        for key in ("guides", "subject_index_registry", "revisions_registry"):
            self.assertFalse(self.manifest.get(key), key)
        self.assertEqual(expected_ids(self.manifest), PREVIEW_IDS)

    def test_registered_units_and_disk_match_exactly(self):
        registered = set()
        for definition, kind, _part in unit_stream(self.manifest):
            relative = Path(definition["zh"])
            self.assertEqual(relative.parts[0], "llm")
            path = (REPO_ROOT / relative).resolve()
            self.assertTrue(path.is_file(), relative)
            self.assertNotIn(path, registered, "two units read one manuscript")
            registered.add(path)
            unit = load_unit(definition, kind, "zh", REPO_ROOT)
            self.assertTrue(unit.md.strip())
            if kind == "chapter":
                self.assertEqual(unit.no_plain,
                                 definition["id"].rsplit("ch", 1)[1])
        manuscripts = {path.resolve() for pattern in ("00-*.md", "ch[0-9][0-9].md")
                       for path in (REPO_ROOT / "llm").glob(pattern)}
        self.assertEqual(registered, manuscripts)

    def test_written_chapters_are_the_planned_preview(self):
        numbers = {int(uid.rsplit("ch", 1)[1])
                   for uid in expected_ids(self.manifest)
                   if "ch" in uid and uid.startswith("llm-ch")}
        self.assertEqual(numbers, PREVIEW_CHAPTERS)
        self.assertLessEqual(numbers, PLANNED_CHAPTERS)
        self.assertEqual(len(PLANNED_CHAPTERS), 15)

    def test_volume_plan_keeps_fifteen_chapters_and_names_the_preview(self):
        plan = (REPO_ROOT / "docs/llm-volume-plan.md").read_text(encoding="utf-8")
        section = plan.split("## 章节骨架（15 章）", 1)[1].split("\n## ", 1)[0]
        numbered = re.findall(r"^\d+\.\s+\*\*", section, flags=re.M)
        self.assertEqual(len(numbered), 15)
        self.assertIn("第 1、5、6 章先行", plan)
        self.assertIn("llm/", plan)

    def test_github_sources_are_full_sha_and_match_the_volume_lock(self):
        locked = {entry["repo"]: entry for entry in self.lock["repositories"]}
        used = set()
        for sid, source in self.sources.items():
            self.assertTrue(source["url"].startswith("https://"), sid)
            if source["kind"] != "github":
                continue
            match = re.search(r"github\.com/([^/]+/[^/]+)/", source["url"])
            self.assertIsNotNone(match, sid)
            repo = match.group(1)
            self.assertIn(repo, locked, sid)
            commit = source["pinned"]["commit"]
            self.assertRegex(commit, r"^[0-9a-f]{40}$")
            self.assertEqual(commit, locked[repo]["commit"], sid)
            self.assertEqual(source["license"], locked[repo]["license"], sid)
            used.add(repo)
        self.assertEqual(used, set(locked))

    def test_examples_and_readme_are_part_of_the_preview(self):
        readme = (REPO_ROOT / "llm/README.md").read_text(encoding="utf-8")
        for name in ("bpe_demo.py", "attention_demo.py", "sampling_demo.py",
                     "context_budget.py"):
            self.assertTrue((REPO_ROOT / "llm/examples" / name).is_file(), name)
            self.assertIn(name, readme)
        for chapter in ("ch01.md", "ch03.md", "ch05.md", "ch06.md"):
            self.assertIn(chapter, readme)


if __name__ == "__main__":
    unittest.main()
