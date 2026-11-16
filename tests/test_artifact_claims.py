"""The READMEs quote the built book; only the sizes are checkable off CI.

Page counts follow the installed CJK face — a Windows runner with Microsoft
YaHei prints longer than CI's Noto CJK — so `--sizes-only` drops them and holds
the one claim that is identical everywhere: the reader's own HTML size. These
tests pin both halves of that bargain against a made-up `dist`.
"""
from __future__ import annotations

import contextlib
import io
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_artifact_claims as claims  # noqa: E402


def claimed_size() -> str:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    match = claims.CLAIMS[0][2].search(readme)
    assert match, "README no longer states the reader's HTML size"
    return match.group(1)


class SizesOnly(unittest.TestCase):
    def setUp(self):
        self._dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self._dir, True)

    def dist(self, *, zh: str) -> Path:
        (self._dir / "yuyu-agent-harness-zh.html").write_bytes(
            b"x" * round(float(zh) * 1e6))
        return self._dir

    def run_main(self, dist: Path, *, sizes_only: bool) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = claims.main(dist, sizes_only=sizes_only)
        return code, out.getvalue()

    def test_a_windows_runner_can_check_the_sizes_without_the_pdfs(self):
        zh = claimed_size()
        code, out = self.run_main(self.dist(zh=zh), sizes_only=True)
        self.assertEqual(code, 0, out)
        self.assertIn("page counts not measured", out)
        self.assertNotIn("no PDF here", out)

    def test_a_wrong_size_still_fails_even_without_the_pdfs(self):
        zh = claimed_size()
        code, out = self.run_main(self.dist(zh=f"{float(zh) - 0.1:.1f}"),
                                  sizes_only=True)
        self.assertEqual(code, 1, out)
        self.assertIn("the reader HTML is", out)

    def test_the_full_pass_still_demands_the_pdfs(self):
        # the regression guard: sizes-only must not become the only mode, or
        # the page-count claim would stop being checked anywhere but CI
        zh = claimed_size()
        code, out = self.run_main(self.dist(zh=zh), sizes_only=False)
        self.assertEqual(code, 1, out)
        self.assertIn("no PDF here", out)

    def test_the_size_claim_is_read_as_a_rounding_of_megabytes(self):
        # 6.345 MB prints as 6.3, not 6.4: the claim is `size / 1e6`, one place
        zh = claimed_size()
        self.assertEqual(f"{float(zh):.1f}", zh)
        self.assertTrue(re.fullmatch(r"\d+\.\d", zh), zh)


if __name__ == "__main__":
    unittest.main()
