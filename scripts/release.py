#!/usr/bin/env python3
"""Assemble a release atomically from canonical content, never publish partial success."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path

from build_reports import digest, write_reports
from check_site_redirects import check as check_site

ROOT = Path(__file__).resolve().parents[1]


def checksum_lines(staged: Path) -> str:
    """SHA256SUMS body: hex digest, two spaces, POSIX path; sorted by path."""
    return "".join(f"{digest(path)}  {path.relative_to(staged).as_posix()}\n"
                   for path in sorted(staged.rglob("*")) if path.is_file())


def release_notes_markdown(version: str, entry: dict) -> str:
    """Readable release body: dated heading and Chinese revision bullets.

    ``gh release create --notes-file`` renders this file as Markdown, so the
    body has to be prose; the machine-readable ledger stays in
    ``release-notes.json``.
    """
    date = str(entry.get("date") or "").strip()
    heading = f"# 御舆 v{version}" + (f"（{date}）" if date else "")
    lines = [heading]
    for language, title in (("zh", "内容修订"),):
        bullets = [" ".join(str(item).splitlines()).strip()
                   for item in entry.get(language) or []]
        bullets = [bullet for bullet in bullets if bullet]
        if not bullets:
            continue
        lines += ["", f"## {title}", ""]
        lines += [f"- {bullet}" for bullet in bullets]
    lines += ["", "## 校验方式", "", "```bash",
              "sha256sum --check SHA256SUMS", "```", "",
              "迁移说明见 `docs/migrations/release-migration.md`。", ""]
    return "\n".join(lines)


def write_release_notes(staged: Path, version: str, revisions: dict) -> Path:
    """Write the JSON ledger excerpt and the Markdown body the release uses."""
    entry = revisions["entries"][0]
    (staged / "release-notes.json").write_text(
        json.dumps({"version": version, "entries": revisions["entries"][:1]},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown = staged / "release-notes.md"
    markdown.write_text(release_notes_markdown(version, entry), encoding="utf-8")
    return markdown


# The ten volumes after 御舆 and Omp. Each carries its own manifest/sources
# pair, so the release builds them with the same call the Makefile uses; pi is
# not in `make book-agents` but has the same shape.
COMPANION_VOLUMES = ("pi", "opencode", "deepseek", "hermes", "codex",
                     "kimi", "prompt", "vibe", "llm", "t3code")


RELEASE_ONLY_PREFIXES = (
    tuple(f"yuyu-{product}-" for product in COMPANION_VOLUMES) + ("yuyu-collected-",)
)


def release_only(name: str) -> bool:
    """True for files shipped as release assets rather than as site pages."""
    return name.startswith(RELEASE_ONLY_PREFIXES)


def assemble(version: str, destination=None, *, epub=False) -> int:
    manifest = json.loads((ROOT / "yuyu-book/manifest.json").read_text(encoding="utf-8"))
    if version != manifest["version"]:
        print(f"RELEASE FAILED: version {version} differs from canonical {manifest['version']}", file=sys.stderr)
        return 2
    target = Path(destination).resolve() if destination else ROOT / "yuyu-book/dist" / f"release-{version}"
    if target.exists():
        print(f"RELEASE FAILED: destination already exists: {target}; choose a new directory", file=sys.stderr)
        return 2
    target.parent.mkdir(parents=True, exist_ok=True)
    measurements = []
    environment = {**os.environ, "PYTHONPATH": str(ROOT / "yuyu-book")}
    with tempfile.TemporaryDirectory(prefix="yuyu-release-", dir=target.parent) as temporary:
        staged = Path(temporary) / "release"
        staged.mkdir()
        def run(label, command):
            started = time.perf_counter()
            result = subprocess.run(command, cwd=ROOT, env=environment)
            measurements.append({"name": label, "command": command, "returncode": result.returncode,
                                 "seconds": round(time.perf_counter() - started, 3)})
            if result.returncode:
                raise subprocess.CalledProcessError(result.returncode, command)
        try:
            run("Chinese HTML/PDF", [sys.executable, "-m", "yuyu_book", "--lang", "zh", "--pdf", "--out-dir", str(staged)])
            run("omp HTML/PDF", [sys.executable, "-m", "yuyu_book", "--manifest", "manifest-omp.json", "--sources", "sources-omp.json", "--lang", "zh", "--pdf", "--out-dir", str(staged)])
            for product in COMPANION_VOLUMES:
                run(f"{product} HTML/PDF", [sys.executable, "-m", "yuyu_book",
                                            "--manifest", f"manifest-{product}.json",
                                            "--sources", f"sources-{product}.json",
                                            "--lang", "zh", "--pdf",
                                            "--out-dir", str(staged)])
            # The shipped registries are what each volume was built from; the
            # release notes promise them, so they travel with the assets.
            for product in COMPANION_VOLUMES:
                for name in (f"manifest-{product}.json", f"sources-{product}.json"):
                    shutil.copy2(ROOT / "yuyu-book" / name, staged / name)
            shutil.copy2(ROOT / "yuyu-book/manifest-collected.json",
                         staged / "manifest-collected.json")
            # The compilation is the tenth volume's whole point: print it here
            # so the release carries a PDF/EPUB that matches today's text.
            run("collected HTML/PDF", [sys.executable, "-m", "yuyu_book",
                                       "--manifest", "manifest-collected.json",
                                       "--lang", "zh", "--pdf",
                                       "--out-dir", str(staged)])
            run("product idempotence and links", [sys.executable, "scripts/check_products.py"])
            run("video configuration", [sys.executable, "video/pipeline/cli.py", "check", "--config-only"])
            run("video content assembly", [sys.executable, "video/pipeline/cli.py", "build"])
            if epub:
                run("zh EPUB", [sys.executable, "scripts/build_epub.py",
                                "--html", str(staged / "yuyu-agent-harness-zh.html"),
                                "--output", str(staged / "yuyu-agent-harness-zh.epub"),
                                "--lang", "zh"])
            if epub:
                run("omp EPUB", [sys.executable, "scripts/build_epub.py", "--html", str(staged / "yuyu-omp-zh.html"), "--output", str(staged / "yuyu-omp-zh.epub"), "--lang", "zh"])
                for product in COMPANION_VOLUMES:
                    run(f"{product} EPUB", [sys.executable, "scripts/build_epub.py",
                                            "--html", str(staged / f"yuyu-{product}-zh.html"),
                                            "--output", str(staged / f"yuyu-{product}-zh.epub"),
                                            "--lang", "zh"])
                run("collected EPUB", [sys.executable, "scripts/build_epub.py",
                                       "--html", str(staged / "yuyu-collected-zh.html"),
                                       "--output", str(staged / "yuyu-collected-zh.epub"),
                                       "--lang", "zh"])
            site = staged / "site"
            site.mkdir()
            for path in (ROOT / "docs").iterdir():
                if path.is_file() and path.suffix in (".html", ".json", ".svg"):
                    shutil.copy2(path, site / path.name)
            # The site mirrors the Pages deployment (御舆 + Omp only); the
            # companion volumes ship as release assets, not as site pages, so
            # site.zip keeps the size of the site rather than of the shelf.
            # Omp is served at omp/yuyu-omp-zh.html, so its root copy is the
            # one file the loop must skip: two 60 MB copies in one zip earn
            # nothing.
            for path in staged.glob("*.html"):
                if not release_only(path.name) and path.name != "yuyu-omp-zh.html":
                    shutil.copy2(path, site / path.name)
            shutil.copy2(ROOT / "cover.png", site / "cover.png")
            shutil.copy2(ROOT / "docs/illustration-prompts.md", site / "illustration-prompts.md")
            # site.zip carries the omp page, so the portal must link it: the
            # committed docs/portal.html is the offline variant without that
            # link. Pages serves the volume at omp/yuyu-omp-zh.html, so the
            # zip keeps that path and the --omp card points at it.
            (site / "omp").mkdir()
            shutil.copy2(staged / "yuyu-omp-zh.html",
                         site / "omp" / "yuyu-omp-zh.html")
            run("site portal", [sys.executable, "scripts/build_site_portal.py",
                                str(site / "portal.html"), "--omp"])
            shutil.copy2(site / "portal.html", site / "index.html")
            shutil.copy2(site / "yuyu-agent-harness-zh.html", site / "book.html")
            for path in staged.glob("*.pdf"):
                if not release_only(path.name):
                    shutil.copy2(path, site / path.name)
            images = ROOT / "docs/images"
            if images.is_dir():
                shutil.copytree(images, site / "images")
            failures = check_site(site)
            if failures:
                raise ValueError("site check failed: " + "; ".join(failures[:5]))
            with zipfile.ZipFile(staged / "site.zip", "w", zipfile.ZIP_DEFLATED) as archive:
                for path in sorted(site.rglob("*")):
                    if path.is_file():
                        archive.write(path, path.relative_to(site).as_posix())
            shutil.rmtree(site)
            videos = []
            video_out = staged / "video-manifests"
            video_out.mkdir()
            for number in range(1, 16):
                cid = f"ch{number:02d}"
                source = ROOT / "video/.build" / cid
                destination_dir = video_out / cid
                shutil.copytree(source, destination_dir)
                videos.append(json.loads((destination_dir / "manifest.json").read_text(encoding="utf-8")))
            (staged / "video-manifest.json").write_text(json.dumps({"schema_version": 1, "version": version, "chapters": videos}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            revisions = json.loads((ROOT / "yuyu-book/revisions.json").read_text(encoding="utf-8"))
            write_release_notes(staged, version, revisions)
            for step in measurements:
                step["command"] = [part.replace(str(staged), ".") for part in step["command"]]
            files = [path for path in staged.rglob("*") if path.is_file()]
            write_reports(staged, measurements, files, warnings=["Video manifests are source/configuration verified; no new narration or completed-video quality is claimed without the media gate."])
            (staged / "SHA256SUMS").write_text(checksum_lines(staged), encoding="utf-8")
            staged.replace(target)
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            failure_dir = ROOT / ".scratch/release-failed"
            write_reports(failure_dir, measurements, warnings=[str(exc)])
            print(f"RELEASE FAILED: {exc}; no release directory was published", file=sys.stderr)
            return 1
    print(f"release {version}: {target}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True,
                        help="exact manifest version, without a leading v")
    parser.add_argument("--out-dir", help="new directory to publish the release into")
    parser.add_argument("--epub", action="store_true", help="also assemble EPUB editions")
    arguments = parser.parse_args(argv)
    return assemble(arguments.version, arguments.out_dir, epub=arguments.epub)


if __name__ == "__main__":
    sys.exit(main())
