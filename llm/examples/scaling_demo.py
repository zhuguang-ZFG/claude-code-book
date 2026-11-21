#!/usr/bin/env python3
"""Training FLOPs, inference FLOPs and a Chinchilla-style allocation.

All coefficients are rules of thumb. The point is the shape of the bill:
6ND for training, 2N per generated token, and a balanced split between
parameters and tokens for a fixed compute budget.
"""
from __future__ import annotations

import math

TOKENS_PER_PARAM = 20
# One assumed effective throughput for a data-center GPU, in FLOP/s.
EFFECTIVE_FLOPS = 4e14


def training_flops(params: float, tokens: float) -> float:
    # forward 2ND + backward 4ND
    return 6 * params * tokens


def inference_flops(params: float, tokens: float) -> float:
    # one forward pass per token, roughly 2N multiply-adds
    return 2 * params * tokens


def allocation(compute: float, tokens_per_param: float = TOKENS_PER_PARAM):
    # C = 6ND and D = kD * N  ->  N = sqrt(C / (6k))
    params = math.sqrt(compute / (6 * tokens_per_param))
    return params, tokens_per_param * params


def memory_bytes(params: float, bytes_per_param: float = 16) -> float:
    # rough mixed-precision training state: weights, grads, Adam moments
    return params * bytes_per_param


def gpu_days(flops: float, per_gpu: float = EFFECTIVE_FLOPS) -> float:
    return flops / per_gpu / 86_400


def size(count: float) -> str:
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    value = float(count)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    raise AssertionError("unreachable")


def main() -> int:
    print(f"assumptions: {TOKENS_PER_PARAM} tokens/param, "
          f"{EFFECTIVE_FLOPS:.0e} FLOP/s per GPU")
    print("compute-optimal allocation")
    print("  budget     params      tokens     training FLOPs   GPU-days   state")
    for exponent in (22, 23, 24):
        compute = 10.0 ** exponent
        params, tokens = allocation(compute)
        flops = training_flops(params, tokens)
        memory = memory_bytes(params)
        print(f"  1e{exponent}  {params / 1e9:>7.1f}B  {tokens / 1e9:>9.0f}B  "
              f"{flops:>14.2e}  {gpu_days(flops):>9,.0f}  {size(memory):>9}")
    print()

    print("same 7B model, different token budgets")
    print("  tokens     training FLOPs   GPU-days   state")
    for tokens in (140e9, 300e9, 2e12):
        flops = training_flops(7e9, tokens)
        print(f"  {tokens / 1e9:>5.0f}B  {flops:>14.2e}  "
              f"{gpu_days(flops):>9,.0f}  {size(memory_bytes(7e9)):>9}")
    print()

    per_token = inference_flops(7e9, 1)
    million = inference_flops(7e9, 1e6)
    print("inference")
    print(f"  7B model: {per_token / 1e9:.0f} GFLOP per token")
    print(f"  1M tokens: {million:.1e} FLOPs, "
          f"{million / EFFECTIVE_FLOPS:.0f} GPU-seconds at the assumed rate")
    print("  decode is memory-bandwidth bound in practice; FLOPs alone "
          "do not predict latency")
    print()
    print("note: 6ND and 2N are accounting identities, not measured "
          "throughput; real runs lose time to communication, bubbles and "
          "recomputation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
