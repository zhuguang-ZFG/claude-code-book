#!/usr/bin/env python3
"""Validate an EPUB archive, then run EPUBCheck against its expanded package.

EPUBCheck's expanded mode avoids platform-specific parsing of Windows paths
while still validating the package produced by this repository's builder.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath


class EpubValidationError(ValueError):
    """Raised when an EPUB archive cannot be safely expanded."""


def member_name_is_safe(name: str) -> bool:
    """Reject names that escape the archive or smuggle a Windows path.

    ZIP writers normalize ``\\`` to ``/`` on Windows, so a backslash or a
    drive colon can only reach this check from an archive built elsewhere;
    either one would create an unintended file or directory when extracted.
    """
    path = PurePosixPath(name)
    return bool(name) and not (path.is_absolute()
                               or any(part in (".", "..") for part in path.parts)
                               or "\\" in name or ":" in name)


def unpack_epub(epub_path: Path, destination: Path) -> None:
    """Check ZIP integrity and expand EPUB members under destination."""
    try:
        with zipfile.ZipFile(epub_path) as archive:
            members = archive.infolist()
            if not members or members[0].filename != "mimetype":
                raise EpubValidationError("EPUB must begin with its mimetype file")
            if members[0].compress_type != zipfile.ZIP_STORED:
                raise EpubValidationError("EPUB mimetype must be uncompressed")
            if archive.read(members[0]) != b"application/epub+zip":
                raise EpubValidationError("EPUB mimetype content is invalid")
            corrupt_member = archive.testzip()
            if corrupt_member is not None:
                raise EpubValidationError(f"ZIP CRC check failed: {corrupt_member}")

            seen: set[str] = set()
            root = destination.resolve()
            destination.mkdir(parents=True, exist_ok=True)
            for member in members:
                name = member.filename
                if not member_name_is_safe(name):
                    raise EpubValidationError(f"Unsafe EPUB member path: {name!r}")
                if name in seen:
                    raise EpubValidationError(f"Duplicate EPUB member: {name}")
                seen.add(name)
                if member.flag_bits & 0x1:
                    raise EpubValidationError(f"Encrypted EPUB member: {name}")
                if (member.external_attr >> 16) & 0o170000 == 0o120000:
                    raise EpubValidationError(f"Symbolic links are not allowed: {name}")

                target = destination.joinpath(*PurePosixPath(name).parts)
                if not target.resolve().is_relative_to(root):
                    raise EpubValidationError(f"EPUB member escapes destination: {name}")
                if member.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member) as source, target.open("xb") as output:
                    shutil.copyfileobj(source, output)
    except zipfile.BadZipFile as exc:
        raise EpubValidationError(f"Invalid EPUB ZIP archive: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("epub", type=Path, help="EPUB archive to validate")
    parser.add_argument("--epubcheck-jar", required=True, type=Path,
                        help="path to the pinned EPUBCheck jar")
    arguments = parser.parse_args()

    if not arguments.epub.is_file():
        parser.error(f"EPUB file not found: {arguments.epub}")
    if not arguments.epubcheck_jar.is_file():
        parser.error(f"EPUBCheck jar not found: {arguments.epubcheck_jar}")

    try:
        with tempfile.TemporaryDirectory(prefix="epubcheck-expanded-") as temporary:
            expanded = Path(temporary) / "book"
            unpack_epub(arguments.epub, expanded)
            result = subprocess.run([
                "java", "-jar", str(arguments.epubcheck_jar.resolve()),
                "--failonwarnings", "--mode", "exp", str(expanded),
            ], check=False)
            return result.returncode
    except (EpubValidationError, OSError) as exc:
        print(f"EPUB validation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
