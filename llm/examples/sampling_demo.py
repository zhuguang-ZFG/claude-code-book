#!/usr/bin/env python3
"""Temperature, top-k and top-p on a synthetic next-token distribution.

The numbers are deliberately small. They show the arithmetic an agent
engineer needs to read a sampling configuration, not the output of a model.
"""
from __future__ import annotations

import math
import random

# A made-up next-token distribution after the prompt "北京是中国的".
LOGITS = {
    "首都": 2.4,
    "城市": 2.0,
    "中心": 1.6,
    "地方": 1.2,
    "天气": 0.6,
    "。": 0.2,
}


def softmax(logits: dict[str, float], temperature: float) -> dict[str, float]:
    if not math.isfinite(temperature) or temperature <= 0:
        raise ValueError("temperature must be finite and greater than zero")
    if not logits or any(not math.isfinite(value) for value in logits.values()):
        raise ValueError("logits must be nonempty and finite")
    largest = max(logits.values())
    weights = {}
    for token, value in logits.items():
        offset = value - largest
        # Center before dividing: tiny T must not turn the maximum into inf.
        # Opposite-sign extreme logits can overflow the subtraction instead.
        scaled = (offset / temperature if math.isfinite(offset)
                  else value / temperature - largest / temperature)
        weights[token] = math.exp(scaled)
    total = sum(weights.values())
    return {token: weight / total for token, weight in weights.items()}


def top_k(dist: dict[str, float], k: int) -> dict[str, float]:
    if k <= 0:
        raise ValueError("k must be positive")
    kept = dict(sorted(_renormalize(dist).items(), key=lambda item: item[1],
                       reverse=True)[:k])
    return _renormalize(kept)


def top_p(dist: dict[str, float], p: float) -> dict[str, float]:
    if not 0 < p <= 1:
        raise ValueError("p must be in (0, 1]")
    kept: dict[str, float] = {}
    cumulative = 0.0
    for token, probability in sorted(_renormalize(dist).items(), key=lambda item: item[1],
                                     reverse=True):
        kept[token] = probability
        cumulative += probability
        if cumulative >= p:
            break
    return _renormalize(kept)


def _renormalize(dist: dict[str, float]) -> dict[str, float]:
    if not dist or any(not math.isfinite(p) or p < 0 for p in dist.values()):
        raise ValueError("probabilities must be nonempty, finite and nonnegative")
    total = sum(dist.values())
    if not math.isfinite(total) or total <= 0:
        raise ValueError("probabilities must have positive finite total mass")
    return {token: probability / total for token, probability in dist.items()}


def sample(dist: dict[str, float], rng: random.Random) -> str:
    ordered = [(token, p) for token, p in sorted(
        _renormalize(dist).items(), key=lambda item: item[1], reverse=True) if p > 0]
    draw = rng.random()
    cumulative = 0.0
    for token, probability in ordered:
        cumulative += probability
        if draw < cumulative:
            return token
    # A rounding residual belongs to the final positive interval.
    return ordered[-1][0]


def sample_sequence(dist: dict[str, float], seed: int, count: int) -> list[str]:
    """Advance one generator through the whole sequence, then replay by seed."""
    rng = random.Random(seed)
    return [sample(dist, rng) for _ in range(count)]


def main() -> int:
    rng = random.Random(7)
    greedy = max(LOGITS, key=LOGITS.get)
    print(f"greedy token (argmax, no sampling): {greedy}")
    print()

    for temperature in (0.2, 1.0):
        dist = softmax(LOGITS, temperature)
        kept_p = top_p(dist, 0.9)
        print(f"temperature={temperature:.1f}")
        print("  probabilities: " + ", ".join(
            f"{token}={probability:.3f}"
            for token, probability in sorted(
                dist.items(), key=lambda item: item[1], reverse=True)))
        print(f"  top-p=0.90 keeps {len(kept_p)} token(s): "
              + ", ".join(kept_p))
        for label, filtered in (("all", dist), ("top-k=3", top_k(dist, 3)),
                                ("top-p=0.90", kept_p)):
            runs = 2_000
            counts: dict[str, int] = {}
            for _ in range(runs):
                token = sample(filtered, rng)
                counts[token] = counts.get(token, 0) + 1
            summary = ", ".join(
                f"{token}:{counts.get(token, 0) / runs:.2f}"
                for token in sorted(filtered, key=lambda item: filtered[item],
                                    reverse=True))
            print(f"  {label:<10} {runs} draws -> {summary}")
        print()

    replay_dist = top_p(softmax(LOGITS, 1.0), 0.9)
    first = sample_sequence(replay_dist, seed=11, count=8)
    second = sample_sequence(replay_dist, seed=11, count=8)
    assert first == second
    print("same seed, same call order -> same toys:", " ".join(first))
    print("note: a real provider may change batching, kernels or versions; "
          "a seed is not a cross-service determinism promise")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
