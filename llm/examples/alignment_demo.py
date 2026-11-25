#!/usr/bin/env python3
"""Bradley-Terry reward loss and DPO loss on toy preferences. Stdlib only.

The scores and log-probabilities are hand-set. They show the shape of the
losses and the role of beta; they are not a trained reward model or policy.
"""
from __future__ import annotations

import math

# (label, reward of the chosen answer, reward of the rejected answer)
PAIRS = [
    ("更有帮助", 2.0, 1.0),
    ("更安全", 0.5, 0.6),
    ("更诚实", -1.0, -0.5),
    ("格式正确", 1.2, 1.2),
]
# (label, policy logp chosen, reference logp chosen,
#         policy logp rejected, reference logp rejected)
# Distinct complete answers: their probabilities sum to less than one;
# the remaining mass belongs to other possible answers.
CASES = [
    ("偏好正确", -2.2, -2.5, -2.6, -2.4),
    ("偏好反转", -2.4, -2.5, -2.2, -2.6),
]
BETAS = (0.1, 1.0)


def sigmoid(value: float) -> float:
    if value >= 0:
        return 1.0 / (1.0 + math.exp(-value))
    scale = math.exp(value)
    return scale / (1.0 + scale)


def bt_loss(chosen: float, rejected: float):
    margin = chosen - rejected
    return negative_log_sigmoid(margin), margin


def negative_log_sigmoid(value: float) -> float:
    """softplus(-value), avoiding exp overflow and log(0)."""
    return max(0.0, -value) + math.log1p(math.exp(-abs(value)))


def dpo_terms(policy_chosen: float, reference_chosen: float,
              policy_rejected: float, reference_rejected: float):
    chosen_ratio = policy_chosen - reference_chosen
    rejected_ratio = policy_rejected - reference_rejected
    return chosen_ratio, rejected_ratio, chosen_ratio - rejected_ratio


def dpo_loss(policy_chosen: float, reference_chosen: float,
             policy_rejected: float, reference_rejected: float,
             beta: float):
    if beta <= 0:
        raise ValueError("beta must be positive")
    _c, _r, gap = dpo_terms(policy_chosen, reference_chosen,
                            policy_rejected, reference_rejected)
    margin = beta * gap
    return negative_log_sigmoid(margin), margin


def main() -> int:
    print("Bradley-Terry reward loss")
    print("  pair          chosen  rejected  margin   loss   correct")
    losses = []
    correct = 0
    for label, chosen, rejected in PAIRS:
        loss, margin = bt_loss(chosen, rejected)
        losses.append(loss)
        ok = margin > 0
        correct += int(ok)
        print(f"  {label:<12} {chosen:>6.2f}  {rejected:>8.2f}  "
              f"{margin:>6.2f}  {loss:>6.3f}   {str(ok):<5}")
    print(f"  mean loss: {sum(losses) / len(losses):.3f}")
    print(f"  pairwise accuracy (margin > 0): {correct}/{len(PAIRS)}")
    print("  a wrong pair keeps a positive loss; a tie is not a win")
    print()

    print("DPO loss (policy vs reference)")
    print("  case          beta  ratio_w  ratio_l  margin   loss")
    for label, pc, rc, pr, rr in CASES:
        chosen_ratio, rejected_ratio, gap = dpo_terms(pc, rc, pr, rr)
        for beta in BETAS:
            loss, margin = dpo_loss(pc, rc, pr, rr, beta)
            print(f"  {label:<12} {beta:>4.1f}  {chosen_ratio:>7.2f}  "
                  f"{rejected_ratio:>7.2f}  {margin:>6.2f}  {loss:>6.3f}")
    print("  larger beta amplifies the same log-ratio gap")
    print("  DPO needs a reference model and preference pairs; "
          "it does not remove the data problem")
    print()

    loss, margin = dpo_loss(-2.2, -2.5, -2.6, -2.4, 0.1)
    print(f"worked example: gap=0.50, beta=0.1 -> margin={margin:.2f}, "
          f"loss={loss:.3f}")
    print("  at init the policy often equals the reference, so the gap is 0 "
          "and the loss is log(2)")
    print(f"  check: -log(sigmoid(0)) = {-math.log(sigmoid(0)):.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
