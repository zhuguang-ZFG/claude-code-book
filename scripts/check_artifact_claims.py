#!/usr/bin/env python3
"""The README quotes the printed book; this checks the quotes against a build.

Two of the numbers are the size of each single-file HTML — those come out the
same on every machine. The page counts are the CI/Noto CJK sheet count: a
build with another CJK face paginates differently (Microsoft YaHei on Windows
runs the build longer), so to see this pass locally, point it at the
artifact directory CI produced, not at your own dist.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# doc, how the PDF sheet count is claimed, how the HTML size is claimed
CLAIMS = [
    ("README.md",
     re.compile(r"PDF（(\d+) 页 / [\d.]+ MB）"),
     re.compile(r"单文件 HTML（([\d.]+) MB）")),
]


def pages(pdf: Path) -> int:
    import fitz  # PyMuPDF, already a book-build dependency
    doc = fitz.open(str(pdf))
    try:
        return doc.page_count
    finally:
        doc.close()


def main(dist: Path, sizes_only: bool = False) -> int:
    """Compare the README to `dist`.

    `sizes_only` drops the page counts, which follow the installed CJK face: a
    Windows build with Microsoft YaHei runs longer than CI's Noto CJK, so a
    local runner can only hold the HTML sizes, the one claim that is the same
    on every machine.
    """
    bad, missing = [], []
    for doc, pdf_rx, html_rx in CLAIMS:
        readme = (ROOT / doc).read_text(encoding="utf-8")

        m = pdf_rx.search(readme)
        if not m:
            missing.append(f"{doc}: no PDF page claim matches — the wording "
                           "changed; re-pin the pattern in this script")
        elif sizes_only:
            print(f"  {doc}: page counts not measured (font-dependent)")
        else:
            claimed = int(m.group(1))
            pdf = dist / "yuyu-agent-harness-zh.pdf"
            if not pdf.exists():
                missing.append(f"{pdf.name}: no PDF here — run "
                               "`python scripts/bookctl.py build --lang zh --pdf` "
                               "or point this script at the CI artifact dir")
            else:
                got = pages(pdf)
                print(f"  {doc}: {pdf.name} has {got} pages, README says "
                      f"{claimed}  [{'ok' if got == claimed else 'STALE'}]")
                if got != claimed:
                    bad.append(f"{doc}: the book prints {got} pages, "
                               f"the README says {claimed}")

        m = html_rx.search(readme)
        if not m:
            missing.append(f"{doc}: no HTML size claim matches — the wording "
                           "changed; re-pin the pattern in this script")
        else:
            claimed = m.group(1)
            html = dist / "yuyu-agent-harness-zh.html"
            if not html.exists():
                missing.append(f"{html.name}: no HTML here — build the "
                               "book first")
            else:
                got = f"{html.stat().st_size / 1e6:.1f}"
                print(f"  {doc}: {html.name} is {got} MB, README says "
                      f"{claimed}  [{'ok' if got == claimed else 'STALE'}]")
                if got != claimed:
                    bad.append(f"{doc}: the reader HTML is {got} MB, "
                               f"the README says {claimed}")

    if missing:
        print("\n".join(["cannot check README's artifact claims:"] + missing))
        return 1
    if bad:
        print("\n".join(["README's artifact claims are stale:"] + bad))
        return 1
    print("README matches the build: page counts and file sizes")
    return 0


if __name__ == "__main__":
    flags = [a for a in sys.argv[1:] if a != "--sizes-only"]
    dist = Path(flags[0]) if flags else ROOT / "yuyu-book" / "dist"
    sys.exit(main(dist, sizes_only="--sizes-only" in sys.argv[1:]))
