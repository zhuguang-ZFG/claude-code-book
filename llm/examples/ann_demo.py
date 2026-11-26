#!/usr/bin/env python3
"""Exact search vs an inverted-file index: what nprobe buys and costs.

The corpus is 400 two-dimensional points in 8 blobs, so the buckets can be
drawn as text. Flat search compares the query with every point; IVF (inverted
file) compares it with the bucket centroids first, then scans only the
`nprobe` nearest buckets. Recall is measured against the flat answer.

This demonstrates IVF bucket search, one index family available in Faiss.
HNSW instead searches a graph. This is not a benchmark: vectors are 2-D,
the bucket count is tiny, and no product quantization is applied.
"""
from __future__ import annotations

import math
import random

SEED = 7
CLUSTERS = 8
PER_CLUSTER = 50
NOISE = 0.85
CENTROID_SPREAD = 4.0
QUERIES = 40
K = 10
NPROBES = (1, 2, 4, 8)
KMEANS_ROUNDS = 8


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def build_corpus(rng: random.Random) -> tuple[list[tuple[float, float]], list[int]]:
    centres = [(rng.uniform(-CENTROID_SPREAD, CENTROID_SPREAD),
                rng.uniform(-CENTROID_SPREAD, CENTROID_SPREAD))
               for _ in range(CLUSTERS)]
    points = []
    labels = []
    for index, centre in enumerate(centres):
        for _ in range(PER_CLUSTER):
            points.append((rng.gauss(centre[0], NOISE), rng.gauss(centre[1], NOISE)))
            labels.append(index)
    return points, labels


def nearest(point: tuple[float, float], points: list[tuple[float, float]],
            k: int) -> list[int]:
    order = sorted(range(len(points)), key=lambda i: (distance(point, points[i]), i))
    return order[:k]


def kmeans(points: list[tuple[float, float]], k: int,
           rng: random.Random) -> list[tuple[float, float]]:
    centroids = [points[rng.randrange(len(points))] for _ in range(k)]
    for _ in range(KMEANS_ROUNDS):
        groups: list[list[tuple[float, float]]] = [[] for _ in range(k)]
        for point in points:
            owner = min(range(k), key=lambda c: distance(point, centroids[c]))
            groups[owner].append(point)
        moved = []
        for index, group in enumerate(groups):
            if group:
                moved.append((sum(p[0] for p in group) / len(group),
                              sum(p[1] for p in group) / len(group)))
            else:
                moved.append(centroids[index])
        if all(distance(a, b) < 1e-9 for a, b in zip(centroids, moved)):
            centroids = moved
            break
        centroids = moved
    return centroids


def assign(points: list[tuple[float, float]],
           centroids: list[tuple[float, float]]) -> list[list[int]]:
    buckets: list[list[int]] = [[] for _ in centroids]
    for index, point in enumerate(points):
        owner = min(range(len(centroids)),
                    key=lambda c: distance(point, centroids[c]))
        buckets[owner].append(index)
    return buckets


def ivf_search(query: tuple[float, float], points: list[tuple[float, float]],
               buckets: list[list[int]], centroids: list[tuple[float, float]],
               nprobe: int) -> tuple[list[int], int]:
    order = sorted(range(len(centroids)),
                   key=lambda c: distance(query, centroids[c]))
    candidates = [index for c in order[:nprobe] for index in buckets[c]]
    # Match flat search's ID tie-break, independent of bucket traversal order.
    ranked = sorted(candidates, key=lambda i: (distance(query, points[i]), i))
    return ranked[:K], len(candidates)


def ascii_map(points: list[tuple[float, float]],
              buckets: list[list[int]], query: tuple[float, float],
              width: int = 46, height: int = 20) -> list[str]:
    owner = {}
    for bucket, members in enumerate(buckets):
        for index in members:
            owner[index] = str(bucket)
    xs = [p[0] for p in points] + [query[0]]
    ys = [p[1] for p in points] + [query[1]]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    grid = [[" "] * width for _ in range(height)]

    def cell(x: float, y: float) -> tuple[int, int]:
        col = int((x - x0) / (x1 - x0) * (width - 1))
        row = int((y - y0) / (y1 - y0) * (height - 1))
        return row, col

    for index, point in enumerate(points):
        row, col = cell(*point)
        grid[row][col] = owner[index]
    row, col = cell(*query)
    grid[row][col] = "Q"
    return ["".join(row) for row in reversed(grid)]


def main() -> int:
    rng = random.Random(SEED)
    points, labels = build_corpus(rng)
    centroids = kmeans(points, CLUSTERS, rng)
    buckets = assign(points, centroids)
    sizes = sorted(len(bucket) for bucket in buckets)
    queries = [(rng.uniform(-CENTROID_SPREAD - 1, CENTROID_SPREAD + 1),
                rng.uniform(-CENTROID_SPREAD - 1, CENTROID_SPREAD + 1))
               for _ in range(QUERIES)]
    exact = [nearest(query, points, K) for query in queries]

    # The worst nprobe=1 query drives the map below: it shows what an
    # approximate index misses when the query lands near a bucket boundary.
    worst = None
    for query, answer in zip(queries, exact):
        found, count = ivf_search(query, points, buckets, centroids, 1)
        recall = len(set(found) & set(answer)) / K
        if worst is None or recall < worst[0]:
            worst = (recall, query, answer, found, count)
    worst_recall, worst_query, worst_answer, worst_found, worst_count = worst

    print(f"corpus: {len(points)} points in {CLUSTERS} blobs, noise {NOISE}, "
          f"{PER_CLUSTER} per blob")
    print(f"index:  k-means with {CLUSTERS} centroids; bucket sizes "
          f"min {sizes[0]}, median {sizes[len(sizes) // 2]}, max {sizes[-1]}")
    print(f"queries: {QUERIES}, top-{K}, recall measured against flat search")
    print()

    print("bucket map (digit = bucket, Q = the boundary query below)")
    for line in ascii_map(points, buckets, worst_query):
        print("  " + line)
    print()

    print(f"  {'nprobe':>6}  {'buckets':>7}  {'scanned':>8}  {'of corpus':>9}  {'recall@10':>9}")
    for nprobe in NPROBES:
        hits = 0
        scanned = 0
        for probe, expected in zip(queries, exact):
            probe_found, probe_count = ivf_search(
                probe, points, buckets, centroids, nprobe)
            scanned += probe_count
            hits += len(set(probe_found) & set(expected)) / K
        print(f"  {nprobe:>6}  {nprobe:>7}  {scanned / QUERIES:>8.1f}  "
              f"{scanned / QUERIES / len(points) * 100:>8.1f}%  "
              f"{hits / QUERIES:>9.3f}")
    print()

    print(f"worst nprobe=1 query: recall {worst_recall:.2f} "
          f"(scanned {worst_count} points, query near bucket boundary)")
    missed = [doc for doc in worst_answer if doc not in worst_found]
    print(f"  missed ids: {missed}")
    print(f"  their true blobs: {[labels[i] for i in missed]}")
    if missed:
        first = missed[0]
        bucket = next(b for b, members in enumerate(buckets) if first in members)
        query_bucket = min(range(len(centroids)),
                           key=lambda c: distance(worst_query, centroids[c]))
        print(f"  first miss sits in bucket {bucket}, while the query probed "
              f"bucket {query_bucket}")
    print()
    print("note: recall rises with nprobe while every extra bucket costs "
          "distance computations; HNSW trades the same two numbers with a "
          "graph instead of buckets, and product quantization shrinks the "
          "bytes each comparison touches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
