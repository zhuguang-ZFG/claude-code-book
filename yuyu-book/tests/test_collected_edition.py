"""A collected edition binds whole books; no page anchor may appear twice.

`load_collection` is the only gate that stops two volumes from claiming the
same anchor, so it is tested on the real registry and on deliberately broken
specs. Rendering is exercised by the collected CI job.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

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

    def test_the_same_two_volumes_bind_cleanly_when_nothing_collides(self):
        volumes = load_collection({"volumes": [
            volume("vol1", "manifest-prompt.json", "sources-prompt.json"),
            volume("vol2", "manifest-kimi.json", "sources-kimi.json")]})
        self.assertEqual([v.id for v in volumes], ["vol1", "vol2"])


if __name__ == "__main__":
    unittest.main()
