#!/usr/bin/env python3
"""Cosine similarity and a tiny vector index. Standard library only.

The vectors are hand-set to make the geometry visible. They are not the
output of a trained embedding model, and a 3-D toy cannot show the
anisotropy, negation or domain drift of a real 1024-D encoder.
"""
from __future__ import annotations

import math

# Six support-desk intents in a 3-D space: returns, shipping, invoices.
VECTORS = {
    "退款": [0.9, 0.1, 0.0],
    "退货": [0.8, 0.2, 0.0],
    "换货": [0.6, 0.5, 0.1],
    "发货": [0.1, 0.9, 0.0],
    "物流": [0.0, 0.8, 0.4],
    "发票": [0.0, 0.1, 0.9],
    "不退款": [0.88, 0.12, 0.0],
}
QUERIES = ["退款", "物流"]


def dot(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def norm(vector: list[float]) -> float:
    return math.sqrt(dot(vector, vector))


def cosine(left: list[float], right: list[float]) -> float:
    denominator = norm(left) * norm(right)
    if denominator == 0:
        raise ValueError("cosine is undefined for a zero vector")
    return dot(left, right) / denominator


def top_k(query: list[float], vectors: dict[str, list[float]],
          k: int) -> list[tuple[str, float, float]]:
    """Return (name, cosine, dot) sorted by cosine, highest first."""
    scored = [(name, cosine(query, vector), dot(query, vector))
              for name, vector in vectors.items() if vector != query]
    return sorted(scored, key=lambda row: row[1], reverse=True)[:k]


def size(count: int) -> str:
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    value = float(count)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    raise AssertionError("unreachable")


def main() -> int:
    print("dot product vs cosine (the query is longer than both candidates)")
    query = [3.0, 0.0]
    candidates = {"A: 同方向短向量": [1.0, 0.0],
                  "B: 不同方向长向量": [2.0, 2.0]}
    for name, vector in candidates.items():
        print(f"  {name:<18} dot={dot(query, vector):.3f} "
              f"cosine={cosine(query, vector):.3f}")
    print("  dot ranks B first; cosine ranks A first")
    print("  an inner-product index must normalize vectors if you want cosine")
    print()

    for query_name in QUERIES:
        print(f"query: {query_name}")
        for rank, (name, cos, raw) in enumerate(
                top_k(VECTORS[query_name], VECTORS, 4), 1):
            print(f"  {rank}. {name:<4} cosine={cos:.3f} dot={raw:.3f}")
        print()

    negation = cosine(VECTORS["退款"], VECTORS["不退款"])
    print(f"cosine(退款, 不退款) = {negation:.4f}")
    print("  the toy puts them almost on top of each other: cosine measures "
          "direction, not polarity")
    print()

    print("embedding table cost")
    for vocab, dimension in ((32000, 4096), (32000, 768)):
        params = vocab * dimension
        print(f"  vocab={vocab:,} d={dimension}: {params:,} params, "
              f"fp16={size(params * 2)}")
    chunks, dimension = 100_000, 4096
    print(f"  {chunks:,} chunks x {dimension} dims x fp32 = "
          f"{size(chunks * dimension * 4)} before any index overhead")
    print(f"  one exact scan = {chunks * dimension:,} multiply-adds")
    print()
    print("note: real retrieval uses trained encoders, normalization, "
          "metadata filters and reranking; cosine alone is not relevance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
