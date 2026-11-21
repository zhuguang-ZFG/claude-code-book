#!/usr/bin/env python3
"""A pre-norm Transformer block in scalar Python: norms, residuals, RoPE, params.

No training, no GPU, no third-party packages. The vectors are hand-set so the
arithmetic stays printable; the parameter counts use the same layout a model
card reports, so they can be checked against a real configuration.
"""
from __future__ import annotations

import math

X0 = [1.0, 2.0, 3.0]
# Two hand-set block updates: the "attention" and "FFN" deltas. A trained
# model learns these maps; here they only move the residual stream.
ATTN = [0.5, -0.25, 0.1]
FFN = [0.2, 0.3, -0.1]


def norm(vector: list[float]) -> float:
    return math.sqrt(sum(value * value for value in vector))


def rms_norm(vector: list[float], eps: float = 1e-6):
    scale = math.sqrt(sum(value * value for value in vector) / len(vector) + eps)
    return [value / scale for value in vector], scale


def layer_norm(vector: list[float], eps: float = 1e-6):
    mean = sum(vector) / len(vector)
    variance = sum((value - mean) ** 2 for value in vector) / len(vector)
    scale = math.sqrt(variance + eps)
    return [(value - mean) / scale for value in vector], mean, scale


def add(left: list[float], right: list[float]) -> list[float]:
    return [a + b for a, b in zip(left, right)]


def scale(vector: list[float], factor: float) -> list[float]:
    return [value * factor for value in vector]


def block(x: list[float], attention: list[float], ffn: list[float]):
    """Pre-norm block: normalize, compute a delta, add it back, twice."""
    h, _ = rms_norm(x)
    x = add(x, [a * b for a, b in zip(attention, h)])
    h, _ = rms_norm(x)
    x = add(x, [a * b for a, b in zip(ffn, h)])
    return x


def params(d_model: int, layers: int, heads: int, d_ff: int, vocab: int,
           swiglu: bool = True, tied: bool = True) -> dict:
    """Dense decoder parameter count, ignoring biases and minor terms."""
    attention = 4 * d_model * d_model
    ffn = (3 if swiglu else 2) * d_model * d_ff
    norms = 2 * d_model
    per_layer = attention + ffn + norms
    embedding = d_model * vocab * (1 if tied else 2)
    return {
        "attention": attention,
        "ffn": ffn,
        "per_layer": per_layer,
        "body": per_layer * layers,
        "embedding": embedding,
        "total": per_layer * layers + embedding,
    }


def rope(vector: list[float], position: int, base: float = 10_000.0) -> list[float]:
    """Rotate each coordinate pair by position-dependent angles."""
    out = []
    for i in range(0, len(vector), 2):
        theta = position / (base ** (i / len(vector)))
        cos, sin = math.cos(theta), math.sin(theta)
        out += [vector[i] * cos - vector[i + 1] * sin,
                vector[i] * sin + vector[i + 1] * cos]
    return out


def dot(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def fmt(vector: list[float]) -> str:
    return "[" + ", ".join(f"{value:.3f}" for value in vector) + "]"


def main() -> int:
    print("input x:", fmt(X0), "norm:", f"{norm(X0):.3f}")
    normalized, scale_value = rms_norm(X0)
    print("rms_norm:", fmt(normalized), "scale:", f"{scale_value:.3f}")
    centered, mean, scale_value = layer_norm(X0)
    print("layer_norm:", fmt(centered), "mean:", f"{mean:.3f}",
          "scale:", f"{scale_value:.3f}")
    print()

    print("residual stream, two pre-norm blocks")
    x = X0
    for index in range(1, 3):
        x = block(x, ATTN, FFN)
        print(f"  block {index}: {fmt(x)} norm={norm(x):.3f}")
    print("  the stream keeps the input and adds each block's update")
    print()

    print("parameter count, d_model=4096, layers=32, heads=32, vocab=32000")
    for label, d_ff, swiglu in (("SwiGLU d_ff=11008", 11008, True),
                                ("ReLU d_ff=16384", 16384, False)):
        for tied in (True, False):
            counts = params(4096, 32, 32, d_ff, 32000, swiglu, tied)
            print(f"  {label:<18} tied={str(tied):<5} "
                  f"per_layer={counts['per_layer']:,} "
                  f"total={counts['total']:,}")
    counts = params(4096, 32, 32, 11008, 32000, True, False)
    print(f"  attention per layer: {counts['attention']:,}")
    print(f"  ffn per layer:       {counts['ffn']:,}")
    print(f"  embedding (untied):  {counts['embedding']:,}")
    print()

    print("RoPE: dot product depends on the offset, not the absolute position")
    query = [1.0, 0.0]
    key = [1.0, 0.0]
    for offset in (0, 1, 2, 3):
        left = rope(query, offset)
        right = rope(key, 0)
        print(f"  m-n={offset}: dot={dot(left, right):+.3f}")
    print("  a learned position embedding would grow with absolute position; "
          "rotation keeps the relative offset in the dot product")
    print()
    print("note: this is a forward-pass sketch; training also needs gradients, "
          "a loss and an optimizer, which this volume does not cover")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
