"""The three static tables the site serves are generated, deterministic, and
true to both editions.

`docs/search-index.json`, `docs/language-map.json` and `docs/concept-map.json`
are committed products like the HTML pages. The site loads them without a
server, so a stale table would quietly search prose that no longer exists.
These tests pin the contract: coverage, anchors, bilingual alignment and
concept relations, and fail when the committed files stop matching the model.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "yuyu-book"))

from yuyu_book.io import load_json  # noqa: E402
from yuyu_book.paths import BOOK_DIR  # noqa: E402
from yuyu_book.products import indices  # noqa: E402
from yuyu_book.products.loader import load_repo_model  # noqa: E402

KINDS = {"paragraph", "heading", "list", "table", "quote", "fence"}


class SiteTables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = load_repo_model(["zh"])
        cls.glosses = load_json(BOOK_DIR / "glosses.json")
        cls.search = indices.search_index(cls.model)
        cls.concept = indices.concept_map(cls.model, cls.glosses)

    def shipped(self, name: str) -> str:
        return (ROOT / "docs" / name).read_text(encoding="utf-8")

    def test_the_shipped_tables_are_a_fresh_generation(self):
        want = {
            indices.OUT["search"]: self.search,
            indices.OUT["concept"]: self.concept,
        }
        for name, data in want.items():
            text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
            self.assertEqual(
                self.shipped(name), text,
                f"{name} is stale — run scripts/build_site_indices.py")

    def test_every_table_names_its_schema_and_baseline(self):
        for name in indices.OUT.values():
            data = json.loads(self.shipped(name))
            self.assertEqual(data["schema_version"], indices.SCHEMA_VERSION,
                             name)
            self.assertEqual(data["baseline"], self.model.version, name)

    def test_search_indexes_every_non_empty_block(self):
        want = sum(1 for edition in self.model.editions.values()
                   for unit in edition.units for section in unit.sections
                   for block in section.blocks
                   if indices._plain(block).strip())
        self.assertEqual(len(self.search["entries"]), want)

    def test_every_search_entry_lands_on_a_real_section(self):
        for entry in self.search["entries"]:
            unit = self.model.unit(entry["lang"], entry["unit"])
            self.assertIsNotNone(unit, entry)
            anchors = {anchor for _level, _title, anchor
                       in indices._anchors(unit)}
            self.assertIn(entry["section"], anchors, entry)
            self.assertIn(entry["kind"], KINDS, entry)
            self.assertTrue(entry["text"].strip(), entry)

    def test_the_concept_map_lists_every_registered_term_once(self):
        want = sorted(gid for gid, raw in self.glosses.items()
                      if isinstance(raw, dict) and "term" in raw)
        self.assertEqual([term["id"] for term in self.concept["terms"]], want)
        for term in self.concept["terms"]:
            raw = self.glosses[term["id"]]
            self.assertEqual(term["term"], raw["term"], term["id"])
            self.assertEqual(term["forms"], {
                lang: list(forms)
                for lang, forms in (raw.get("forms") or {}).items()},
                term["id"])

    def test_concept_units_are_real_and_relationships_count_them(self):
        known = {u.id for edition in self.model.editions.values()
                 for u in edition.units}
        by_id = {term["id"]: set(term["units"])
                 for term in self.concept["terms"]}
        for term in self.concept["terms"]:
            self.assertTrue(set(term["units"]) <= known, term["id"])
            self.assertEqual(len(term["units"]), len(set(term["units"])),
                             term["id"])
            for relation in term["related"]:
                self.assertNotEqual(relation["id"], term["id"], term["id"])
                self.assertEqual(
                    relation["shared"],
                    len(by_id[term["id"]] & by_id[relation["id"]]), term["id"])
                self.assertGreater(relation["shared"], 0, term["id"])

    def test_related_entries_are_ranked_and_capped(self):
        for term in self.concept["terms"]:
            shares = [relation["shared"] for relation in term["related"]]
            self.assertEqual(shares, sorted(shares, reverse=True), term["id"])
            self.assertLessEqual(len(term["related"]), 5, term["id"])


if __name__ == "__main__":
    unittest.main()
