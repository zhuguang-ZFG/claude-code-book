"""Ensure redistributed MIT files retain their pinned upstream bytes."""
import hashlib
import json
import unittest
from pathlib import Path


class MinbpeProvenance(unittest.TestCase):
    def test_vendored_sources_and_license_match_registered_hashes(self):
        root = Path(__file__).resolve().parents[1]
        vendor = root / "llm/examples/vendor/minbpe"
        record = json.loads((vendor / "UPSTREAM.json").read_text(encoding="utf-8"))
        sources = json.loads((root / "llm/facts/source-lock.json").read_text(encoding="utf-8"))
        pin = next(item for item in sources["repositories"] if item["repo"] == "karpathy/minbpe")
        self.assertEqual(record["commit"], pin["commit"])
        self.assertEqual(record["license"], "MIT")
        self.assertEqual({item["local_path"] for item in record["files"]},
                         {"base.py", "basic.py", "LICENSE"})
        for item in record["files"]:
            with self.subTest(path=item["local_path"]):
                data = (vendor / item["local_path"]).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), item["sha256"])
                blob = b"blob " + str(len(data)).encode() + b"\0" + data
                self.assertEqual(hashlib.sha1(blob).hexdigest(), item["git_blob_sha"])
