#!/usr/bin/env python3
"""README quotes the printed book; this checks the quotes against a build.

Two of the numbers are the size of each single-file HTML — those come out the
same on every machine. The page counts are the CI/Noto CJK sheet count: a
build with another CJK face paginates differently (Microsoft YaHei on Windows
runs both editions longer), so to see this pass locally, point it at the
artifact directory CI produced, not at your own dist.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_CLAIM = re.compile(r"单文件 HTML（中文版 ([\d.]+) MB / 英文版 ([\d.]+) MB）")
PDF_CLAIM = re.compile(
    r"PDF（中文版 (\d+) 页 / [\d.]+ MB，英文版 (\d+) 页 / [\d.]+ MB）")


def pages(pdf: Path) -> int:
    import fitz  # PyMuPDF, already a book-build dependency
    doc = fitz.open(str(pdf))
    try:
        return doc.page_count
    finally:
        doc.close()


def main(dist: Path) -> int:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    bad = []
    missing = []

    m = PDF_CLAIM.search(readme)
    if not m:
        missing.append("PDF page claim: no sentence matches — the wording "
                       "changed; re-pin PDF_CLAIM in this script")
    else:
        for lang, claimed in (("zh", int(m.group(1))), ("en", int(m.group(2)))):
            pdf = dist / f"yuyu-agent-harness-{lang}.pdf"
            if not pdf.exists():
                missing.append(f"{pdf.name}: no PDF here — run "
                               f"`python yuyu-book/build.py --lang both --pdf` "
                               f"or point this script at the CI artifact dir")
                continue
            got = pages(pdf)
            size = got == claimed
            print(f"  {pdf.name}: {got} pages, README says {claimed}  "
                  f"[{'ok' if size else 'STALE'}]")
            if not size:
                bad.append(f"{lang}: the book prints {got} pages, "
                           f"README says {claimed}")

    m = HTML_CLAIM.search(readme)
    if not m:
        missing.append("HTML size claim: no sentence matches — the wording "
                       "changed; re-pin HTML_CLAIM in this script")
    else:
        for lang, claimed in (("zh", m.group(1)), ("en", m.group(2))):
            html = dist / f"yuyu-agent-harness-{lang}.html"
            if not html.exists():
                missing.append(f"{html.name}: no HTML here — build the book first")
                continue
            got = f"{html.stat().st_size / 1e6:.1f}"
            print(f"  {html.name}: {got} MB, README says {claimed}  "
                  f"[{'ok' if got == claimed else 'STALE'}]")
            if got != claimed:
                bad.append(f"{lang}: the reader HTML is {got} MB, "
                           f"README says {claimed}")

    if missing:
        print("\n".join(["cannot check README's artifact claims:"] + missing))
        return 1
    if bad:
        print("\n".join(["README's artifact claims are stale:"] + bad))
        return 1
    print("README's page count and file sizes match the build")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "yuyu-book" / "dist"))
