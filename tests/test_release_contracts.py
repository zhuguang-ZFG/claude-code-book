"""Release preflight is cheap and must fail closed before anything is built.

A full ``assemble()`` compiles both editions and the videos, so these tests
cover only the guards that run before the first subprocess: a version that
disagrees with the canonical manifest and an already existing destination.
Both must return 2 and leave the filesystem untouched.
"""
from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_reports  # noqa: E402
import release  # noqa: E402


def canonical_version() -> str:
    manifest = json.loads((ROOT / "yuyu-book/manifest.json")
                          .read_text(encoding="utf-8"))
    return manifest["version"]


def assemble(version, destination):
    with contextlib.redirect_stdout(io.StringIO()), \
            contextlib.redirect_stderr(io.StringIO()):
        return release.assemble(version, str(destination))


class ReleasePreflight(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="release-preflight-")
        self.addCleanup(temporary.cleanup)
        self.tmp = Path(temporary.name)

    def test_version_mismatch_returns_2_before_creating_anything(self):
        destination = self.tmp / "not-created" / "release"
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = release.assemble(canonical_version() + "-mismatch",
                                    str(destination))
        self.assertEqual(code, 2)
        self.assertIn("differs from canonical", stderr.getvalue())
        self.assertFalse(destination.exists())
        self.assertFalse(destination.parent.exists())
        self.assertEqual(list(self.tmp.iterdir()), [])

    def test_existing_destination_is_refused_without_touching_it(self):
        destination = self.tmp / "release"
        destination.mkdir()
        sentinel = destination / "keep.txt"
        sentinel.write_text("pre-existing", encoding="utf-8")
        self.assertEqual(assemble(canonical_version(), destination), 2)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "pre-existing")
        self.assertEqual([path.name for path in destination.iterdir()],
                         ["keep.txt"])
        self.assertEqual([path for path in self.tmp.iterdir()
                          if path.name.startswith("yuyu-release-")], [])

    def test_cli_refuses_a_mismatched_version(self):
        destination = self.tmp / "cli-release"
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/release.py"),
             "--version", canonical_version() + "-mismatch",
             "--out-dir", str(destination)],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("differs from canonical", result.stderr)
        self.assertFalse(destination.exists())


class ChecksumManifest(unittest.TestCase):
    def test_sha256sums_lines_are_sorted_and_well_formed(self):
        with tempfile.TemporaryDirectory(prefix="release-sums-") as tmp:
            staged = Path(tmp)
            (staged / "nested").mkdir()
            (staged / "empty").mkdir()
            payloads = {
                "b.pdf": b"%PDF-1.7",
                "a.html": b"<html/>",
                "nested/c.epub": b"PK",
            }
            for name, payload in payloads.items():
                (staged / name).write_bytes(payload)

            lines = release.checksum_lines(staged).splitlines()
            self.assertEqual([line[66:] for line in lines],
                             ["a.html", "b.pdf", "nested/c.epub"])
            for line in lines:
                self.assertRegex(line, r"^[0-9a-f]{64}  [^/\\].*$")
                self.assertEqual(line[:64],
                                 build_reports.digest(staged / line[66:]))

            empty = staged / "empty"
            self.assertEqual(release.checksum_lines(empty), "")


class ReleaseNotes(unittest.TestCase):
    def revision(self) -> dict:
        revisions = json.loads((ROOT / "yuyu-book/revisions.json")
                               .read_text(encoding="utf-8"))
        return revisions["entries"][0]

    def test_body_is_markdown_not_the_machine_readable_ledger(self):
        version = canonical_version()
        entry = self.revision()
        body = release.release_notes_markdown(version, entry)
        self.assertEqual(body.splitlines()[0],
                         f"# 御舆 v{version}（{entry['date']}）")
        self.assertNotIn('"version":', body)
        self.assertFalse(body.lstrip().startswith("{"),
                         "the body must not be the JSON ledger")
        self.assertTrue(body.endswith("\n"))

    def test_every_revision_bullet_matches_the_ledger(self):
        entry = self.revision()
        body = release.release_notes_markdown("9.9.9", entry)
        self.assertIn("## 内容修订", body)
        self.assertNotIn("## Content changes", body)
        for bullet in entry["zh"]:
            self.assertIn(f"- {bullet}", body)
        self.assertIn("sha256sum --check SHA256SUMS", body)

    def test_empty_language_section_is_omitted(self):
        body = release.release_notes_markdown(
            "9.9.9", {"date": "2026-01-01", "zh": ["只有中文"], "en": []})
        self.assertIn("- 只有中文", body)
        self.assertNotIn("Content changes", body)

    def test_staging_writes_markdown_body_and_json_ledger(self):
        entry = {"version": "9.9.9", "date": "2026-01-01",
                 "zh": ["甲"], "en": ["A"]}
        revisions = {"schema_version": 1,
                     "entries": [entry, {"version": "9.9.8"}]}
        with tempfile.TemporaryDirectory(prefix="release-notes-") as tmp:
            staged = Path(tmp)
            written = release.write_release_notes(staged, "9.9.9", revisions)
            self.assertEqual(written, staged / "release-notes.md")
            self.assertEqual(written.read_text(encoding="utf-8"),
                             release.release_notes_markdown("9.9.9", entry))
            ledger = json.loads((staged / "release-notes.json")
                                .read_text(encoding="utf-8"))
            self.assertEqual(ledger, {"version": "9.9.9", "entries": [entry]})


class CompanionVolumes(unittest.TestCase):
    def test_every_volume_has_its_manifest_and_sources(self):
        for product in release.COMPANION_VOLUMES:
            for name in (f"manifest-{product}.json", f"sources-{product}.json"):
                self.assertTrue((ROOT / "yuyu-book" / name).is_file(), name)

    def test_the_site_zip_keeps_the_shelf_out(self):
        """Volumes ship as release assets; site.zip mirrors the two volumes the
        Pages site actually serves, so it must not balloon to shelf size."""
        for name in ("yuyu-vibe-zh.html", "yuyu-pi-zh.pdf", "yuyu-kimi-zh.epub",
                     "yuyu-collected-zh.pdf"):
            self.assertTrue(release.release_only(name), name)
        for name in ("yuyu-agent-harness-zh.html", "yuyu-omp-zh.html",
                     "portal.html", "site.zip"):
            self.assertFalse(release.release_only(name), name)


if __name__ == "__main__":
    unittest.main()
