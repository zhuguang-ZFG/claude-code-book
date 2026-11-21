#!/usr/bin/env python3
"""Patch tokenization and the image-token budget, on toy numbers only.

The arithmetic is the real mechanism; the "image" is a list. Every vendor
resizes and tiles differently, so the counts here demonstrate the
relationship between resolution and tokens, not any vendor's price card.
"""
from __future__ import annotations

import math

PATCH = 2
IMAGE = [
    [10, 12, 9, 8, 20, 22],
    [11, 13, 8, 7, 21, 23],
    [30, 32, 40, 41, 5, 4],
    [31, 33, 42, 44, 5, 6],
]  # 6 wide, 4 tall: two bright blocks on a toy "screenshot"
PROJECTION = [
    [0.5, 0.1, -0.2],
    [0.2, 0.4, 0.0],
    [-0.1, 0.3, 0.5],
    [0.0, -0.3, 0.4],
]  # 4 patch values -> a 3-d image token, one toy head


def patches(image: list[list[int]], size: int) -> list[tuple[tuple[int, int],
                                                           list[int]]]:
    """Cut the image into size x size blocks, in row-major order."""
    out = []
    for row in range(0, len(image), size):
        for col in range(0, len(image[0]), size):
            block = [image[r][c]
                     for r in range(row, row + size)
                     for c in range(col, col + size)]
            out.append(((row // size, col // size), block))
    return out


def project(block: list[int]) -> list[float]:
    """Flatten one patch through the toy projection: 4 values -> 3 dims."""
    return [sum(value * PROJECTION[i][j] for i, value in enumerate(block))
            for j in range(len(PROJECTION[0]))]


def direct_tokens(width: int, height: int, patch: int = 16) -> int:
    """Tokens when the raw pixels are cut straight into patches."""
    return math.ceil(width / patch) * math.ceil(height / patch)


def resized(width: int, height: int, max_edge: int) -> tuple[int, int]:
    """Scale the image so its longest edge is max_edge, keep the ratio."""
    scale = max_edge / max(width, height)
    return round(width * scale), round(height * scale)


def pixel_priced(width: int, height: int, per: int = 750) -> int:
    """One vendor-style pricing rule: tokens ~= pixels / 750."""
    return round(width * height / per)


def main() -> int:
    blocks = patches(IMAGE, PATCH)
    grid_w = len(IMAGE[0]) // PATCH
    print(f"toy image: {len(IMAGE[0])}x{len(IMAGE)} pixels, patch {PATCH}x{PATCH}")
    print(f"patches: {len(blocks)} (row-major, {grid_w} per row)")
    for index, ((row, col), block) in enumerate(blocks):
        token = project(block)
        flat = row * grid_w + col
        print(f"  pos {index}: patch({row},{col}) flat={flat} {block}"
              f" -> [{', '.join(f'{v:+.2f}' for v in token)}]")
    print("every patch becomes one image token; positions flatten"
          " row-major, just like text")
    print(f"projection: {len(PROJECTION)} patch values ->"
          f" {len(PROJECTION[0])} dims per token")

    print()
    print("resolution decides the budget (patch 16 on raw pixels"
          " vs scaled-to-1568):")
    print(f"{'image':<24} {'raw patch':>10} {'scaled patch':>13}"
          f" {'pixels/750':>12}")
    samples = [
        ("1920x1080 screenshot", 1920, 1080),
        ("4032x3024 photo", 4032, 3024),
        ("2480x3508 A4 300dpi scan", 2480, 3508),
    ]
    for name, width, height in samples:
        scaled = resized(width, height, 1568)
        print(f"{name:<24} {direct_tokens(width, height):>10}"
              f" {direct_tokens(*scaled):>13}"
              f" {pixel_priced(*scaled):>12}")

    print()
    print("detail levels on the same 1920x1080 screenshot (pixels/750):")
    for label, edge in (("low  (max edge 768)", 768),
                        ("high (max edge 1568)", 1568)):
        small = resized(1920, 1080, edge)
        print(f"  {label:<20} {small[0]}x{small[1]}"
              f" -> {pixel_priced(*small)} tokens")

    print()
    print("note: vendors differ -- some cut large images into tiles and"
          " price each tile; check the API's own page before budgeting")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
