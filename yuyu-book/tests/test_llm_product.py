"""The LLM volume is a registered, source-pinned product with its own shelf.

The preview deliberately ships three chapters, not the eighteen-chapter
companion shape. These checks pin what exists, keep future chapters from
being silently omitted, and make the source lock answer for every GitHub
source the volume cites.
"""
from __future__ import annotations

import json
import math
import re
import sys
import unittest
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from yuyu_book import plain
from yuyu_book.core import REPO_ROOT, expected_ids, load_configs, load_unit, unit_stream


PREVIEW_IDS = ["llm-front", "llm-ch01", "llm-ch02", "llm-ch03",
               "llm-ch04", "llm-ch05", "llm-ch06", "llm-ch07",
               "llm-ch08", "llm-ch09", "llm-ch10", "llm-ch11",
               "llm-ch12", "llm-ch13", "llm-ch14", "llm-ch15",
               "llm-ch16"]
PREVIEW_CHAPTERS = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16}
PLANNED_CHAPTERS = set(range(1, 17))


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

    def test_rope_plate_compares_original_and_rotated_qk_vectors(self):
        import xml.etree.ElementTree as ET

        plate_path = (REPO_ROOT / "yuyu-book/illustrations-agents/"
                      "llm-ch04-rope-rotation.svg")
        plate = plate_path.read_text(encoding="utf-8")
        root = ET.fromstring(plate)
        self.assertEqual(root.attrib.get("role"), "img")
        self.assertTrue(root.attrib.get("aria-label"))
        self.assertIn("llm-explainer", root.attrib.get("class", ""))
        self.assertIn("stroke-dasharray=\"4 4\" opacity=\".42\"", plate)
        ns = "{http://www.w3.org/2000/svg}"
        self.assertIsNotNone(root.find(f"{ns}title"))
        self.assertIsNotNone(root.find(f"{ns}desc"))
        q_circles = [
            el for el in root.findall(f"{ns}circle")
            if el.attrib.get("fill") == "currentColor" and el.attrib.get("r") == "4.2"
        ]
        ghost_q = [
            el for el in root.findall(f"{ns}circle")
            if el.attrib.get("fill") == "currentColor" and el.attrib.get("r") == "3.4"
        ]
        self.assertEqual(len(q_circles), 2, "solid q and rotated q' markers")
        self.assertEqual(len(ghost_q), 1, "ghost pre-shift q marker")
        # Verify left panel (10 deg, 55 deg) and right panel (+45 deg -> 55 deg, 100 deg)
        vector_paths = [
            el.attrib["d"] for el in root.findall(f"{ns}path")
            if el.attrib.get("stroke-width") == "2.2"
        ]
        self.assertEqual(len(vector_paths), 2)
        coords_before = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", vector_paths[0])]
        coords_after = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", vector_paths[1])]
        q_before = math.degrees(math.atan2(-(coords_before[3] - coords_before[1]),
                                           coords_before[2] - coords_before[0]))
        k_before = math.degrees(math.atan2(-(coords_before[7] - coords_before[5]),
                                           coords_before[6] - coords_before[4]))
        q_after = math.degrees(math.atan2(-(coords_after[3] - coords_after[1]),
                                          coords_after[2] - coords_after[0]))
        k_after = math.degrees(math.atan2(-(coords_after[7] - coords_after[5]),
                                          coords_after[6] - coords_after[4]))
        q_rotation = (q_after - q_before + 180) % 360 - 180
        k_rotation = (k_after - k_before + 180) % 360 - 180
        self.assertAlmostEqual(q_rotation, 45, delta=1)
        self.assertAlmostEqual(k_rotation, 45, delta=1)
        self.assertAlmostEqual(k_after - q_after, k_before - q_before, delta=1)

        block_path = (REPO_ROOT / "yuyu-book/illustrations-agents/"
                      "llm-ch04-transformer-block.svg")
        block = block_path.read_text(encoding="utf-8")
        for label in ("Pre-LN", "Post-LN", "RMSNorm", "Attention", "FFN", "Final", "lm_head"):
            self.assertIn(label, block)

    def test_all_llm_body_plates_carry_accessible_metadata_and_synced_wording(self):
        import xml.etree.ElementTree as ET

        ns = "{http://www.w3.org/2000/svg}"
        art_dir = REPO_ROOT / "yuyu-book/illustrations-agents"
        plates = sorted(p for p in art_dir.glob("llm-ch*.svg") if len(p.stem) > 8)
        self.assertEqual(len(plates), 31)
        for path in plates:
            text = path.read_text(encoding="utf-8")
            root = ET.fromstring(text)
            self.assertEqual(root.attrib.get("role"), "img", path.name)
            self.assertTrue(root.attrib.get("aria-label"), path.name)
            self.assertIn("llm-explainer", root.attrib.get("class", ""), path.name)
            self.assertIsNotNone(root.find(f"{ns}title"), path.name)
            self.assertIsNotNone(root.find(f"{ns}desc"), path.name)
            self.assertIn("currentColor", text, path.name)
        validation = (art_dir / "llm-ch12-validation-loop.svg").read_text(encoding="utf-8")
        self.assertIn("^ORD-[0-9]{4}$", validation)
        self.assertNotIn(r"\d{4}", validation)
        lora = (art_dir / "llm-ch08-sft-lora.svg").read_text(encoding="utf-8")
        self.assertIn("4 MiB", lora)
        cost = (art_dir / "llm-ch13-cost-curve.svg").read_text(encoding="utf-8")
        self.assertIn("正确率 +23.8pp", cost)
        self.assertNotIn("准率", cost)

    def test_written_chapters_are_the_planned_preview(self):
        numbers = {int(uid.rsplit("ch", 1)[1])
                   for uid in expected_ids(self.manifest)
                   if "ch" in uid and uid.startswith("llm-ch")}
        self.assertEqual(numbers, PREVIEW_CHAPTERS)
        self.assertLessEqual(numbers, PLANNED_CHAPTERS)
        self.assertEqual(len(PLANNED_CHAPTERS), 16)

    def test_volume_plan_keeps_sixteen_chapters_and_names_the_preview(self):
        plan = (REPO_ROOT / "docs/llm-volume-plan.md").read_text(encoding="utf-8")
        section = plan.split("## 章节骨架（16 章）", 1)[1].split("\n## ", 1)[0]
        numbered = re.findall(r"^\d+\.\s+\*\*", section, flags=re.M)
        self.assertEqual(len(numbered), 16)
        self.assertIn("第 1、5、6 章先行", plan)
        self.assertIn("llm/", plan)
        self.assertIn("多模态", plan)

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
        examples = sorted((REPO_ROOT / "llm/examples").glob("*.py"))
        self.assertGreaterEqual(len(examples), 21)
        for path in examples:
            self.assertIn(path.name, readme, path.name)
        for chapter in ("ch01.md", "ch02.md", "ch03.md", "ch04.md", "ch05.md",
                        "ch06.md", "ch07.md", "ch08.md", "ch09.md",
                        "ch10.md", "ch11.md", "ch12.md", "ch13.md",
                        "ch14.md", "ch15.md", "ch16.md"):
            self.assertIn(chapter, readme)

    def test_glossary_has_at_least_eighty_terms_and_preview_links(self):
        glossary = (REPO_ROOT / "llm/ch16.md").read_text(encoding="utf-8")
        rows = re.findall(r"^\| [^|]+ \| [^|]+ \| \[\d+\]\(ch\d{2}\.md\) \|",
                          glossary, flags=re.M)
        self.assertGreaterEqual(len(rows), 80, "the glossary shrank below 80 terms")
        linked = {int(value) for value in re.findall(r"ch(\d{2})\.md", glossary)}
        self.assertLessEqual(linked, PREVIEW_CHAPTERS,
                             "the glossary links to an unwritten chapter")


if __name__ == "__main__":
    unittest.main()
