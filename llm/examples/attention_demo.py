#!/usr/bin/env python3
"""Scaled dot-product attention on three tiny tokens. Standard library only.

The vectors and projections are hand-set so the arithmetic stays readable.
This is a teaching model, not a trained network: the weights show how
attention mixes positions, not what any real model has learned.
"""
from __future__ import annotations

import math

TOKENS = ["青禾", "工作坊", "报名"]
X = [
    [1.0, 0.0],
    [0.8, 0.6],
    [0.0, 1.0],
]
IDENTITY = [[1.0, 0.0], [0.0, 1.0]]
# Two one-dimensional heads: one reads the first coordinate, one the second.
HEADS = [
    ("维度 0", [[1.0, 0.0]], [[1.0, 0.0]], [[1.0, 0.0]]),
    ("维度 1", [[0.0, 1.0]], [[0.0, 1.0]], [[0.0, 1.0]]),
]


def matvec(matrix: list[list[float]], vector: list[float]) -> list[float]:
    return [sum(a * b for a, b in zip(row, vector)) for row in matrix]


def project(vectors: list[list[float]],
            weights: list[list[float]]) -> list[list[float]]:
    return [matvec(weights, vector) for vector in vectors]


def dot(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("query and key dimensions must match")
    return sum(a * b for a, b in zip(left, right))


def softmax(scores: list[float]) -> list[float]:
    largest = max(scores)
    exps = [math.exp(score - largest) for score in scores]
    total = sum(exps)
    return [value / total for value in exps]


def attention(queries: list[list[float]], keys: list[list[float]],
              values: list[list[float]], causal: bool = True,
              query_start: int = 0):
    """One head; key positions start at zero, query positions at query_start.

    For cached decoding, include the new key/value in the cache and pass the
    query's absolute position. This example has no sliding/evicted cache.
    """
    if not queries or not keys or not values:
        raise ValueError("queries, keys and values must be nonempty")
    if len(keys) != len(values):
        raise ValueError("each key must have a matching value")
    width = len(queries[0])
    value_width = len(values[0])
    if not width or any(len(row) != width for row in [*queries, *keys]):
        raise ValueError("query and key rows must have the same positive width")
    if not value_width or any(len(row) != value_width for row in values):
        raise ValueError("value rows must have a consistent positive width")
    if not isinstance(query_start, int) or query_start < 0:
        raise ValueError("query_start must be a nonnegative integer")
    if causal and query_start + len(queries) > len(keys):
        raise ValueError("causal keys must include every queried position")
    scale = math.sqrt(len(queries[0]))
    outputs, rows = [], []
    for i, query in enumerate(queries):
        scores = [dot(query, key) / scale for key in keys]
        if causal:
            scores = [score if j <= query_start + i else float("-inf")
                      for j, score in enumerate(scores)]
        weights = softmax(scores)
        outputs.append([sum(weights[j] * values[j][d]
                            for j in range(len(values)))
                        for d in range(len(values[0]))])
        rows.append(weights)
    return outputs, rows


def attention_params(d_model: int, heads: int, kv_heads: int | None = None) -> dict:
    """Per-layer Q/K/V/O parameters for equal-width MHA/GQA/MQA heads.

    Assumes head_dim = d_model / heads and an output width of d_model;
    ignores biases and the FFN. This does not count mixed-width heads.
    """
    kv_heads = heads if kv_heads is None else kv_heads
    if any(not isinstance(value, int) or value <= 0 for value in (d_model, heads, kv_heads)):
        raise ValueError("model width and head counts must be positive integers")
    if d_model % heads or heads % kv_heads:
        raise ValueError("model width must divide into heads, and query heads into KV groups")
    d_head = d_model // heads
    q = o = d_model * d_model
    k = v = d_model * kv_heads * d_head
    return {"q": q, "k": k, "v": v, "o": o, "total": q + k + v + o}


def kv_bytes_per_token(layers: int, kv_heads: int, head_dim: int,
                       dtype_bytes: int = 2) -> int:
    return 2 * layers * kv_heads * head_dim * dtype_bytes


def fmt_row(values: list[float]) -> str:
    return "[" + ", ".join(f"{value:.3f}" for value in values) + "]"


def main() -> int:
    print("tokens: " + " / ".join(TOKENS))
    print("x_i:    " + "; ".join(fmt_row(vector) for vector in X))
    print("projections: identity for this walkthrough (Q = K = V = x)")
    print()

    queries = project(X, IDENTITY)
    keys = project(X, IDENTITY)
    values = project(X, IDENTITY)

    outputs, rows = attention(queries, keys, values, causal=True)
    print("causal attention weights (row = query, column = key)")
    for token, weights in zip(TOKENS, rows):
        print(f"  {token:<4} {fmt_row(weights)}")
    print("causal outputs")
    for token, output in zip(TOKENS, outputs):
        print(f"  {token:<4} {fmt_row(output)}")
    print()

    future, future_rows = attention(queries, keys, values, causal=False)
    print("without the mask, the first token also reads the future:")
    print(f"  weights {fmt_row(future_rows[0])} -> {fmt_row(future[0])}")
    print(f"  with mask it stays {fmt_row(outputs[0])}")
    print()

    cached = []
    for position in range(len(X)):
        step, _ = attention(queries[position:position + 1], keys[:position + 1],
                            values[:position + 1], query_start=position)
        cached.extend(step)
    error = max(abs(a - b) for full, step in zip(outputs, cached)
                for a, b in zip(full, step))
    print(f"cached decode matches full causal attention: max error {error:.1e}")
    wrong, _ = attention(queries[-1:], keys, values)
    print(f"  last query with reset position: {fmt_row(wrong[0])}")
    print(f"  last query at position 2:       {fmt_row(cached[-1])}")
    print()

    print("two heads, each one dimension wide (causal)")
    concat: list[list[float]] = [[] for _ in TOKENS]
    for name, wq, wk, wv in HEADS:
        head_out, head_rows = attention(project(X, wq), project(X, wk),
                                        project(X, wv), causal=True)
        for i, value in enumerate(head_out):
            concat[i].extend(value)
        flat = " ".join(fmt_row(row) for row in head_rows)
        print(f"  head {name}: weights {flat}")
    print("  concatenated:")
    for token, vector in zip(TOKENS, concat):
        print(f"    {token:<4} {fmt_row(vector)}")
    print()

    print("attention parameters per layer (d_model=4096, heads=32)")
    for label, kv_heads in (("MHA", 32), ("GQA", 8), ("MQA", 1)):
        counts = attention_params(4096, 32, kv_heads)
        cache = kv_bytes_per_token(32, kv_heads, 128)
        print(f"  {label:<4} kv_heads={kv_heads:<2} "
              f"q={counts['q']:,} k={counts['k']:,} "
              f"v={counts['v']:,} o={counts['o']:,} "
              f"total={counts['total']:,} "
              f"kv_cache/token={cache:,} B")
    print()
    print("note: inputs and projection matrices are hand-set; attention "
          "weights are computed from dot products and softmax. "
          "No trained model is involved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
