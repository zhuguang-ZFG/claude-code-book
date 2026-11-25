#!/usr/bin/env python3
"""SFT loss masking and LoRA arithmetic on toy matrices. Standard library only.

The probabilities and matrices are hand-set. They show which target positions
contribute direct loss and how a low-rank update changes a matrix; they are not a
trained model or a benchmark.
"""
from __future__ import annotations

import math

TOKENS = ["system", "user", "assistant", "已退款", "请查收"]
TARGET_PROB = [0.95, 0.80, 0.70, 0.60, 0.50]
MASK = [0, 0, 1, 1, 1]

# A 4x4 base weight and a rank-2 LoRA pair.
W = [
    [0.10, 0.00, 0.20, 0.00],
    [0.00, 0.30, 0.00, 0.10],
    [0.20, 0.00, 0.10, 0.00],
    [0.00, 0.10, 0.00, 0.40],
]
A = [
    [0.10, 0.00, -0.10, 0.00],
    [0.00, 0.20, 0.00, -0.10],
]
B = [
    [0.50, 0.00],
    [0.00, 0.50],
    [0.20, 0.00],
    [0.00, 0.20],
]
ALPHA, RANK = 4.0, 2
X = [1.0, 1.0, 1.0, 1.0]


def cross_entropy(probability: float) -> float:
    if not 0 < probability <= 1:
        raise ValueError("probability must be in (0, 1]")
    return -math.log(probability)


def masked_loss(probabilities: list[float], mask: list[int]):
    losses = [cross_entropy(value) for value in probabilities]
    all_mean = sum(losses) / len(losses)
    kept = [loss for loss, flag in zip(losses, mask) if flag]
    assistant_mean = sum(kept) / len(kept)
    return losses, all_mean, assistant_mean


def matmul(left: list[list[float]], right: list[list[float]]) -> list[list[float]]:
    return [[sum(left[i][k] * right[k][j] for k in range(len(right)))
             for j in range(len(right[0]))]
            for i in range(len(left))]


def matvec(matrix: list[list[float]], vector: list[float]) -> list[float]:
    return [sum(a * b for a, b in zip(row, vector)) for row in matrix]


def add(left: list[list[float]], right: list[list[float]]) -> list[list[float]]:
    return [[a + b for a, b in zip(row_l, row_r)]
            for row_l, row_r in zip(left, right)]


def lora_delta(a: list[list[float]], b: list[list[float]],
               alpha: float, rank: int) -> list[list[float]]:
    scale = alpha / rank
    return [[scale * value for value in row] for row in matmul(b, a)]


def lora_output(w: list[list[float]], a: list[list[float]],
                b: list[list[float]], x: list[float], alpha: float) -> list[float]:
    """Unmerged linear branch: W x + (alpha/r) B(A x), without dropout."""
    base = matvec(w, x)
    update = matvec(b, matvec(a, x))
    return [value + alpha / len(a) * delta
            for value, delta in zip(base, update)]


def params(d: int, rank: int) -> dict:
    trainable = 2 * d * rank
    return {"a": d * rank, "b": d * rank, "trainable": trainable,
            "full": d * d, "ratio": trainable / (d * d)}


def size(count: int) -> str:
    units = ("B", "KiB", "MiB", "GiB")
    value = float(count)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    raise AssertionError("unreachable")


def fmt(vector: list[float]) -> str:
    return "[" + ", ".join(f"{value:.3f}" for value in vector) + "]"


def main() -> int:
    losses, all_mean, assistant_mean = masked_loss(TARGET_PROB, MASK)
    print("SFT loss by position")
    print("  position     p     loss   mask")
    for token, probability, loss, flag in zip(TOKENS, TARGET_PROB, losses, MASK):
        print(f"  {token:<10} {probability:.2f}  {loss:.3f}   {flag}")
    print(f"  all-token mean:       {all_mean:.3f}")
    print(f"  assistant-only mean:  {assistant_mean:.3f}")
    kept = sum(MASK)
    print(f"  each selected target loss gets weight 1/{kept}; "
          "other target losses get 0")
    print("  prompt representations still condition the answers; "
          "masking target losses does not detach the prompt computation")
    print()

    delta = lora_delta(A, B, ALPHA, RANK)
    base_out = matvec(W, X)
    adapted_out = lora_output(W, A, B, X, ALPHA)
    print(f"LoRA rank={RANK}, alpha={ALPHA}, scale={ALPHA / RANK:.2f}")
    print(f"  base output:    {fmt(base_out)}")
    print(f"  adapted output: {fmt(adapted_out)}")
    merged_out = matvec(add(W, delta), X)
    equivalent = all(math.isclose(left, right, rel_tol=1e-12, abs_tol=1e-12)
                     for left, right in zip(merged_out, adapted_out))
    print(f"  merge check: {'OK' if equivalent else 'MISMATCH'}")
    print()

    print("trainable parameters for one 4096x4096 matrix")
    for rank in (1, 8, 16, 64):
        counts = params(4096, rank)
        print(f"  r={rank:<3} A={counts['a']:,} B={counts['b']:,} "
              f"total={counts['trainable']:,} "
              f"({counts['ratio'] * 100:.3f}% of full) "
              f"fp16/target-matrix={size(counts['trainable'] * 2)}")
    full = params(4096, 4096)
    print(f"  r=d   total={full['trainable']:,} "
          f"({full['ratio'] * 100:.1f}% of full): two full matrices, "
          f"not a saving")
    print(f"  full W: {full['full']:,} parameters")
    r8 = params(4096, 8)["trainable"]
    print(f"  r=8 on 32 layers: {size(r8 * 2 * 32)} for the adapters")
    print()
    print("note: B is usually initialized to zero, so training starts from "
          "the base model; alpha/r sets the update scale")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
