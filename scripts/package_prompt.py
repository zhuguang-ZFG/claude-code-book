#!/usr/bin/env python3
"""Pack the prompt volume's offline exercise sources into one deterministic ZIP.

``prompt/README.md`` and ``prompt/VERIFY.md`` document this command, and the
package manifest records the SHA-256 of every shipped file so a reader can prove
which sources they received. The archive carries its own copy of
``prompt/PACKAGE-README.md`` as the root ``README.md``.

Every entry is stamped with the volume's publication date instead of the file
mtime, so packaging the same sources twice produces the same archive.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "yuyu-book" / "manifest-prompt.json"
KIND = "offline_teaching_sources"
PACKAGE_README = "prompt/PACKAGE-README.md"
TESTS = ("tests/test_prompt_exercise.py", "tests/test_prompt_workshop.py")


def relative_files(folder: str) -> list[str]:
    base = ROOT / folder
    if not base.is_dir():
        raise SystemExit(f"missing source folder: {folder}")
    return sorted(path.relative_to(ROOT).as_posix()
                  for path in base.rglob("*")
                  if path.is_file() and "__pycache__" not in path.parts
                  and path.suffix != ".pyc")


def payloads() -> list[tuple[str, bytes]]:
    """Every shipped member except the manifest, in archive order."""
    plan = [("LICENSE", "LICENSE"), ("README.md", PACKAGE_README)]
    plan += [(name, name) for name in (*relative_files("prompt"), *TESTS)]
    for name in TESTS:
        if not (ROOT / name).is_file():
            raise SystemExit(f"missing test module: {name} — the package "
                             f"would ship an exercise set nobody checked")
    entries = []
    for name, source in plan:
        data = (ROOT / source).read_bytes()
        if not data:
            raise SystemExit(f"empty source file: {source}")
        entries.append((name, data))
    return entries


def package_manifest(entries: list[tuple[str, bytes]], version: str) -> bytes:
    """The digest table, README and LICENSE first, then case-insensitive order."""
    head = [name for name in ("README.md", "LICENSE")]
    rest = sorted((name for name, _data in entries if name not in head),
                  key=str.lower)
    digest = {name: data for name, data in entries}
    document = {"version": version, "kind": KIND,
                "sha256": {name: hashlib.sha256(digest[name]).hexdigest()
                           for name in [*head, *rest]}}
    return (json.dumps(document, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def stamp(manifest: dict) -> tuple[int, int, int, int, int, int]:
    date = manifest.get("date") or ""
    try:
        year, month, day = (int(part) for part in date.split("-"))
    except ValueError:
        raise SystemExit(f"{MANIFEST.name}: needs a YYYY-MM-DD date, got {date!r}")
    return (year, month, day, 0, 0, 0)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--output", default="yuyu-book/dist/yuyu-prompt-zh-examples.zip",
                    help="archive to write")
    args = ap.parse_args(argv)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    version = str(manifest.get("version") or "")
    if not version:
        raise SystemExit(f"{MANIFEST.name}: version is empty")
    entries = payloads()
    document = package_manifest(entries, version)
    members = [*entries[:2], ("package-manifest.json", document), *entries[2:]]

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    when = stamp(manifest)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in members:
            info = zipfile.ZipInfo(name, date_time=when)
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)

    sizes = sum(len(data) for name, data in members)
    print(f"{output} · {len(members)} files · {sizes} B of sources · "
          f"version {version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
