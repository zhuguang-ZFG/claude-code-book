#!/usr/bin/env python3
"""Generate the GitHub Pages portal (site index).

The page lives in yuyu_book.products.portal; this entry point keeps the
`python scripts/build_site_portal.py [out]` contract the Pages workflow uses.
`--omp` swaps in the second-volume card that links the deployed omp page.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "yuyu-book"))

from yuyu_book.products.portal import PAGE, page, write  # noqa: E402,F401


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out", nargs="?", default="docs/portal.html")
    parser.add_argument("--omp", action="store_true",
                        help="link the omp card at omp/yuyu-omp-zh.html")
    args = parser.parse_args()
    out = write(Path(args.out), omp_live=args.omp)
    print(f"{out} ({len(page(args.omp))} bytes)")


if __name__ == "__main__":
    main()
