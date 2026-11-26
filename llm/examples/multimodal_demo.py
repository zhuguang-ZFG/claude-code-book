#!/usr/bin/env python3
"""Patch tokenization and the image-token budget, on toy numbers only.

The "image" is a list and the projection is hand-set, with no trained vision
encoder or positional embeddings. Patch counts and pixels/750 are distinct
teaching quantities, not a current API token counter or price card.
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
]  # 4 patch values -> a 3-d vector; linear projection, not an attention head


def patches(image: list[list[int]], size: int) -> list[tuple[tuple[int, int],
                                                           list[int]]]:
    """Cut row-major blocks, padding the bottom/right edges with zeros."""
    if size <= 0 or not image or not image[0]:
        raise ValueError("image must be nonempty and patch size positive")
    height, width = len(image), len(image[0])
    if any(len(row) != width for row in image):
        raise ValueError("image rows must have equal width")
    out = []
    for row in range(0, len(image), size):
        for col in range(0, len(image[0]), size):
            block = [image[r][c] if r < height and c < width else 0
                     for r in range(row, row + size)
                     for c in range(col, col + size)]
            out.append(((row // size, col // size), block))
    return out


def project(block: list[int]) -> list[float]:
    """Flatten one patch through the toy projection: 4 values -> 3 dims."""
    if len(block) != len(PROJECTION):
        raise ValueError("projection expects exactly 4 patch values (2x2)")
    return [sum(value * PROJECTION[i][j] for i, value in enumerate(block))
            for j in range(len(PROJECTION[0]))]


def patch_grid_count(width: int, height: int, patch: int = 16) -> int:
    """Padded patch-grid count, not billable image tokens."""
    if min(width, height, patch) <= 0:
        raise ValueError("dimensions and patch size must be positive")
    return math.ceil(width / patch) * math.ceil(height / patch)


def resized(width: int, height: int, max_edge: int) -> tuple[int, int]:
    """Downscale to at most max_edge; integer rounding, no upscaling."""
    if min(width, height, max_edge) <= 0:
        raise ValueError("dimensions and max_edge must be positive")
    scale = min(1.0, max_edge / max(width, height))
    return max(1, round(width * scale)), max(1, round(height * scale))


def area_units(width: int, height: int, per: int = 750) -> int:
    """Toy area/750 accounting units, not a current vendor pricing rule."""
    if min(width, height, per) <= 0:
        raise ValueError("dimensions and divisor must be positive")
    return round(width * height / per)


def main() -> int:
    blocks = patches(IMAGE, PATCH)
    grid_w = math.ceil(len(IMAGE[0]) / PATCH)
    print(f"toy image: {len(IMAGE[0])}x{len(IMAGE)} pixels, patch {PATCH}x{PATCH}")
    print(f"patches: {len(blocks)} (row-major, {grid_w} per row)")
    for index, ((row, col), block) in enumerate(blocks):
        token = project(block)
        flat = row * grid_w + col
        print(f"  pos {index}: patch({row},{col}) flat={flat} {block}"
              f" -> [{', '.join(f'{v:+.2f}' for v in token)}]")
    print("each patch becomes one projected vector; the printed index"
          " is not a positional embedding; no Transformer runs here")
    print(f"projection: {len(PROJECTION)} patch values ->"
          f" {len(PROJECTION[0])} dims per token")

    print()
    print("teaching counts: patch 16 on raw pixels vs downscaled-to-1568;")
    print("the last column uses area/750 units, not a provider token counter")
    print(f"{'image':<24} {'raw patch':>10} {'scaled patch':>13}"
          f" {'pixels/750':>12}")
    samples = [
        ("1920x1080 screenshot", 1920, 1080),
        ("4032x3024 photo", 4032, 3024),
        ("2480x3508 A4 300dpi scan", 2480, 3508),
    ]
    for name, width, height in samples:
        scaled = resized(width, height, 1568)
        print(f"{name:<24} {patch_grid_count(width, height):>10}"
              f" {patch_grid_count(*scaled):>13}"
              f" {area_units(*scaled):>12}")

    print()
    print("two teaching resize settings on 1920x1080 (area/750 units):")
    for label, edge in (("A (max edge 768)", 768),
                        ("B (max edge 1568)", 1568)):
        small = resized(1920, 1080, edge)
        print(f"  {label:<20} {small[0]}x{small[1]}"
              f" -> {area_units(*small)} units")

    print()
    print("note: vendors differ -- some cut large images into tiles and"
          " price each tile; check the API's own page before budgeting")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
