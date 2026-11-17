"""Regression: the pedagogy report must use one consistent working-tree snapshot.

`report()` first reads every unit, then renders its marks. Re-reading the
manifest and the source file in the second pass can crash or mix versions if a
chapter is edited mid-run. The guard fails on the old two-pass implementation.
"""
from __future__ import annotations

import importlib.util
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "docs" / "yuyu-overhaul" / "measure_pedagogy.py"


def _load_script():
    spec = importlib.util.spec_from_file_location("measure_pedagogy", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SnapshotContracts(unittest.TestCase):
    def test_report_reads_each_source_once(self):
        module = _load_script()
        reads = []

        def read_text(path, *args, **kwargs):
            reads.append(str(path))
            if len(reads) > 1:
                raise RuntimeError(f"source re-read during report: {path}")
            return "正文"
        with (patch.object(module, "units", return_value=[("ch01", "zh", "unit.md")]),
              patch.object(module, "git_head", return_value="旧文"),
              patch.object(Path, "exists", return_value=True),
              patch.object(Path, "read_text", read_text)):
            out = io.StringIO()
            with redirect_stdout(out):
                rc = module.report(set())

        self.assertEqual(rc, 0)
        self.assertEqual(len(reads), 1, reads)
        self.assertIn("unit", out.getvalue())


if __name__ == "__main__":
    unittest.main()
