import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.check_epub import EpubValidationError, member_name_is_safe, unpack_epub


class EpubArchiveChecks(unittest.TestCase):
    def create_epub(self, path: Path, extra_members=()) -> None:
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("mimetype", "application/epub+zip",
                             compress_type=zipfile.ZIP_STORED)
            archive.writestr("EPUB/package.opf", "<package/ >")
            for name, contents in extra_members:
                archive.writestr(name, contents)

    def test_valid_archive_expands_for_epubcheck(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            epub = root / "book.epub"
            expanded = root / "expanded"
            self.create_epub(epub)

            unpack_epub(epub, expanded)

            self.assertEqual((expanded / "mimetype").read_bytes(),
                             b"application/epub+zip")
            self.assertTrue((expanded / "EPUB/package.opf").is_file())

    def test_path_traversal_member_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            epub = root / "unsafe.epub"
            self.create_epub(epub, [("../escape.txt", "no")])

            with self.assertRaisesRegex(EpubValidationError, "Unsafe EPUB member path"):
                unpack_epub(epub, root / "expanded")
            self.assertFalse((root / "escape.txt").exists())

    def test_duplicate_members_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            epub = root / "duplicate.epub"
            self.create_epub(epub, [("EPUB/package.opf", "duplicate")])

            with self.assertRaisesRegex(EpubValidationError, "Duplicate EPUB member"):
                unpack_epub(epub, root / "expanded")

    def test_windows_separators_and_drive_colons_are_rejected(self):
        # zipfile rewrites "\\" to "/" on Windows, so the archive round trip
        # cannot exercise these names; the predicate is the contract.
        for name in ("EPUB\\package.opf", "EPUB/package.opf:stream",
                     "C:EPUB/package.opf", "", "/EPUB/package.opf",
                     "EPUB/../package.opf"):
            with self.subTest(name=name):
                self.assertFalse(member_name_is_safe(name))
        for name in ("EPUB/package.opf", "EPUB/images/a b.png"):
            with self.subTest(name=name):
                self.assertTrue(member_name_is_safe(name))


if __name__ == "__main__":
    unittest.main()
