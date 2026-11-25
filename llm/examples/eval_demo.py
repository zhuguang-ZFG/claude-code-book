#!/usr/bin/env python3
"""Evaluation arithmetic: Wilson intervals, paired tests, abstention, cost.

The counts are hand-set. The point is to show how a single accuracy number can
hide sample size, test-set contamination, abstention and serving cost.
"""
from __future__ import annotations

import math

Z = 1.96


def wilson(correct: int, total: int, z: float = Z) -> tuple[float, float]:
    if total <= 0 or not 0 <= correct <= total:
        raise ValueError("need 0 <= correct <= total and total > 0")
    p = correct / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total))
    half /= denominator
    return center - half, center + half


def mcnemar_exact(a_only: int, b_only: int) -> float:
    """Two-sided exact McNemar p-value from discordant paired outcomes.

    Under equal marginal accuracy, each discordant pair favors either
    system with probability 1/2. This small-count teaching implementation
    sums the binomial lower tail and doubles it, capped at one.
    """
    if a_only < 0 or b_only < 0:
        raise ValueError("discordant counts must be nonnegative")
    discordant = a_only + b_only
    if discordant == 0:
        return 1.0
    tail = sum(math.comb(discordant, k)
               for k in range(min(a_only, b_only) + 1))
    return min(1.0, 2 * tail / 2 ** discordant)


def contamination(clean_correct: int, clean_total: int,
                  seen_correct: int, seen_total: int) -> dict:
    reported = (clean_correct + seen_correct) / (clean_total + seen_total)
    clean = clean_correct / clean_total
    return {"clean": clean, "reported": reported, "inflation": reported - clean}


def abstention(answered: int, correct: int, total: int) -> dict:
    coverage = answered / total
    precision = correct / answered
    overall = correct / total
    wrong = (answered - correct) / total
    return {"coverage": coverage, "answered_precision": precision,
            "overall": overall, "wrong_rate": wrong}


def cost_per_correct(price: float, accuracy: float) -> float:
    if not 0 < accuracy <= 1:
        raise ValueError("accuracy must be in (0, 1]")
    return price / accuracy


def main() -> int:
    print("95% Wilson intervals on 200 questions")
    print("  system   correct   accuracy   interval")
    for label, correct in (("A", 164), ("B", 172)):
        low, high = wilson(correct, 200)
        print(f"  {label:<7} {correct:>7}   {correct / 200 * 100:>6.1f}%   "
              f"[{low * 100:.1f}%, {high * 100:.1f}%]")
    low_a, high_a = wilson(164, 200)
    low_b, high_b = wilson(172, 200)
    print(f"  intervals overlap: {max(low_a, low_b) <= min(high_a, high_b)}")
    print("  overlap of separate intervals does not test the paired difference")
    print()
    print("same marginal accuracies, different paired outcomes")
    print("  both correct   A only   B only   both wrong   exact McNemar p")
    for both, a_only, b_only, neither in ((164, 0, 8, 28),
                                         (144, 20, 28, 8)):
        p_value = mcnemar_exact(a_only, b_only)
        print(f"  {both:>12}   {a_only:>6}   {b_only:>6}   {neither:>10}   "
              f"{p_value:.4f}")
    print("  each table has A=164/200 and B=172/200; keep item-level results")
    print()

    result = contamination(144, 180, 20, 20)
    print("contamination: 20 of 200 test items were seen in training")
    print(f"  clean accuracy:    {result['clean'] * 100:.1f}%")
    print(f"  reported accuracy: {result['reported'] * 100:.1f}%")
    print(f"  inflation:         {result['inflation'] * 100:+.1f} points")
    print()

    result = abstention(80, 72, 100)
    print("abstention: 80 of 100 answered, 72 of those correct")
    print(f"  coverage:           {result['coverage'] * 100:.1f}%")
    print(f"  answered precision: {result['answered_precision'] * 100:.1f}%")
    print(f"  overall accuracy:   {result['overall'] * 100:.1f}%")
    print(f"  wrong-answer rate:  {result['wrong_rate'] * 100:.1f}%")
    print()

    print("distillation cost per correct answer")
    for label, accuracy, price in (("teacher", 0.85, 0.006),
                                   ("student", 0.78, 0.0012)):
        cost = cost_per_correct(price, accuracy)
        print(f"  {label:<7} accuracy={accuracy * 100:.1f}%  "
              f"price/request=${price:.4f}  cost/correct=${cost:.4f}")
    print("  the student is cheaper per correct answer, but 7 points lower "
          "before task-specific evaluation")
    print()
    print("note: these counts are illustrative; a real eval needs a held-out "
          "set, confidence intervals, contamination checks and task metrics")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
