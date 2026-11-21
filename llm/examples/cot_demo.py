#!/usr/bin/env python3
"""Test-time compute: self-consistency accuracy and cost per correct answer.

The per-sample correctness probability is an assumption, not a model result.
The simulation shows the shape of majority voting: accuracy rises with more
samples, but cost rises faster, and independence is doing a lot of the work.
"""
from __future__ import annotations

import random

PRICE_PER_MILLION = 0.6  # an input knob, not a vendor quote
REASONING_TOKENS = 300
ANSWER_TOKENS = 100
TRIALS = 4000


def majority_accuracy(p: float, samples: int, trials: int = TRIALS,
                      seed: int = 7) -> float:
    if not 0 < p < 1:
        raise ValueError("p must be in (0, 1)")
    if samples <= 0 or samples % 2 == 0:
        raise ValueError("samples must be a positive odd number")
    rng = random.Random(seed)
    correct = 0
    for _ in range(trials):
        votes = sum(1 for _ in range(samples) if rng.random() < p)
        if votes * 2 > samples:
            correct += 1
    return correct / trials


def cost_per_correct(tokens: int, price_per_million: float,
                     accuracy: float) -> float:
    if not 0 < accuracy <= 1:
        raise ValueError("accuracy must be in (0, 1]")
    return tokens / 1_000_000 * price_per_million / accuracy


def main() -> int:
    print(f"assumption: each sample is correct with p=0.60; "
          f"{TRIALS} simulated problems")
    print("  samples   majority accuracy   tokens/problem")
    for samples in (1, 3, 5, 9, 15):
        accuracy = majority_accuracy(0.60, samples)
        print(f"  {samples:>7}   {accuracy * 100:>16.1f}%   "
              f"{samples * (REASONING_TOKENS + ANSWER_TOKENS):>14,}")
    print()

    print(f"cost per correct answer at ${PRICE_PER_MILLION:.2f}/M output tokens")
    print("  strategy          tokens   accuracy   cost/correct")
    strategies = [
        ("direct answer", ANSWER_TOKENS, 0.45),
        ("CoT once", REASONING_TOKENS + ANSWER_TOKENS, 0.65),
        ("CoT x5 majority", 5 * (REASONING_TOKENS + ANSWER_TOKENS),
         majority_accuracy(0.65, 5)),
        ("CoT x15 majority", 15 * (REASONING_TOKENS + ANSWER_TOKENS),
         majority_accuracy(0.65, 15)),
    ]
    for label, tokens, accuracy in strategies:
        cost = cost_per_correct(tokens, PRICE_PER_MILLION, accuracy)
        print(f"  {label:<17} {tokens:>6,}   {accuracy * 100:>7.1f}%   "
              f"${cost:.6f}")
    print()
    print(f"CoT x15 vs CoT once: accuracy "
          f"{majority_accuracy(0.65, 15) / 0.65 - 1:+.1%}, "
          f"tokens {15 / 1:.0f}x")
    print("note: majority voting assumes independent errors; correlated "
          "errors, a weak verifier or a biased sampler can erase the gain")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
