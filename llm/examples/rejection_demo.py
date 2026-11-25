#!/usr/bin/env python3
"""Rejection sampling and best-of-N on a toy policy. Stdlib only.

A prompt has one exact answer. The toy policy is right with probability p and
otherwise returns a wrong candidate; the verifier is exact match. The numbers
show how filtering N independent candidates per prompt raises the chance of
at least one pass. Filtering does not update p; this script does not train.
"""
from __future__ import annotations

import random

SEED = 11
P_CORRECT = 0.4
SIZES = (1, 4, 16, 64)

PROMPTS = {
    "计算 17 的平方": "289",
    "把 2024-02-29 换成 ISO 周": "2024-W09-4",
    "把 'Hello World' 转成 snake_case": "hello_world",
    "把 '3.14159' 四舍五入到两位小数": "3.14",
    "用小写十六进制写 255，不加 0x 前缀": "ff",
    "计算 2 ** 10": "1024",
}
WRONG = {
    "计算 17 的平方": ("279", "299", "287"),
    "把 2024-02-29 换成 ISO 周": ("2024-W08-4", "2024-W09-5", "2024-02-29"),
    "把 'Hello World' 转成 snake_case": ("HelloWorld", "hello-world", "hello_World"),
    "把 '3.14159' 四舍五入到两位小数": ("3.15", "3.1", "3.141"),
    "用小写十六进制写 255，不加 0x 前缀": ("FF", "0xff", "255"),
    "计算 2 ** 10": ("1000", "512", "1023"),
}


def sample(prompt: str, rng: random.Random, p: float) -> str:
    """One candidate: the exact answer with probability p, else a distractor."""
    if rng.random() < p:
        return PROMPTS[prompt]
    return rng.choice(WRONG[prompt])


def sample_n(prompt: str, n: int, rng: random.Random, p: float) -> list[str]:
    return [sample(prompt, rng, p) for _ in range(n)]


def passes(candidate: str, prompt: str) -> bool:
    """Toy verifier: exact match against the expected answer."""
    return candidate == PROMPTS[prompt]


def rejection_round(p: float, n: int, rng: random.Random):
    """Sample N per prompt and keep every passing answer.

    Returns (attempts, kept, prompts_with_at_least_one_hit).
    """
    attempts = kept = hit_prompts = 0
    for prompt in PROMPTS:
        hits = 0
        for candidate in sample_n(prompt, n, rng, p):
            if passes(candidate, prompt):
                kept += 1
                hits += 1
        attempts += n
        hit_prompts += int(hits > 0)
    return attempts, kept, hit_prompts


def best_of_n(p: float, n: int, rng: random.Random) -> int:
    """Generate all N candidates, then count a prompt if any passes."""
    solved = 0
    for prompt in PROMPTS:
        for candidate in sample_n(prompt, n, rng, p):
            if passes(candidate, prompt):
                solved += 1
                break
    return solved


def main() -> int:
    print(f"toy verifier: exact match; policy is right with p = {P_CORRECT}")
    print()

    print("rejection sampling (keep every passing answer)")
    print("   N  attempts  kept  keep%   hit-prompts")
    rng = random.Random(SEED)
    for n in SIZES:
        attempts, kept, hit = rejection_round(P_CORRECT, n, rng)
        print(f"  {n:>2}  {attempts:>8}  {kept:>4}  {100 * kept / attempts:>5.1f}%  "
              f"{hit}/{len(PROMPTS)}")
    print()

    print("best-of-N at inference (first passing answer counts)")
    print("   N  solved prompts")
    for n in SIZES:
        solved = best_of_n(P_CORRECT, n, random.Random(SEED))
        print(f"  {n:>2}  {solved}/{len(PROMPTS)}")
    print()

    print("notes:")
    print(f"  - with p = {P_CORRECT} and N = 4, P(at least one pass) = "
          f"{1 - (1 - P_CORRECT) ** 4:.3f}")
    print(f"  - with N = 16, P(at least one pass) = "
          f"{1 - (1 - P_CORRECT) ** 16:.4f}")
    print("  - p stays fixed: filtering candidates is not policy training")
    print("  - all N candidates are generated; no early-stopping cost saving")
    print("  - exact-match success is format-specific; a real verifier can "
          "reject valid alternatives or accept incorrect answers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
