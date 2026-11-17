"""Import-order contracts for the split page builders.

`pages` re-exports the builders at the bottom of the module. A builder that
imports `pages` at module scope cannot be imported first: `pages` is still
initializing and the re-exported names do not exist yet. Each case therefore
runs in a fresh interpreter so import order cannot leak between tests.
"""
import subprocess
import sys
import unittest
from pathlib import Path

BOOK_DIR = str(Path(__file__).resolve().parents[1])


class DirectImport(unittest.TestCase):
    def _import_first(self, module: str) -> None:
        proc = subprocess.run(
            [sys.executable, "-c", f"import yuyu_book.{module}"],
            cwd=BOOK_DIR,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(
            proc.returncode, 0,
            f"importing yuyu_book.{module} first failed:\n{proc.stderr}",
        )

    def test_backmatter_imports_without_pages_first(self):
        self._import_first("backmatter")

    def test_frontmatter_imports_without_pages_first(self):
        self._import_first("frontmatter")
