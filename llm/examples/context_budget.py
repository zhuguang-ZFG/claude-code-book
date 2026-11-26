#!/usr/bin/env python3
"""Plan a context budget and estimate the two long-context costs.

All model shape and price values are illustrative knobs, not a claim about
any provider. The formulas are the point; substitute the real configuration
and the current price list before using the result for a decision.
"""
from __future__ import annotations

import argparse
import math


def size(count: int) -> str:
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    value = float(count)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    raise AssertionError("unreachable")


def kv_bytes_per_token(layers: int, kv_heads: int, head_dim: int,
                       dtype_bytes: int) -> int:
    # K and V are both stored for every layer and every cached position.
    return 2 * layers * kv_heads * head_dim * dtype_bytes


def attention_pairs(tokens: int) -> int:
    # Valid position pairs per head per layer for dense causal attention.
    return tokens * (tokens + 1) // 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--window", type=int, default=128_000)
    parser.add_argument("--output", type=int, default=4_096)
    parser.add_argument("--system", type=int, default=900)
    parser.add_argument("--tools", type=int, default=2_400)
    parser.add_argument("--history", type=int, default=18_000)
    parser.add_argument("--retrieved", type=int, default=60_000)
    parser.add_argument("--safety", type=int, default=2_048)
    parser.add_argument("--layers", type=int, default=32)
    parser.add_argument("--kv-heads", type=int, default=8)
    parser.add_argument("--head-dim", type=int, default=128)
    parser.add_argument("--dtype-bytes", type=int, default=2)
    parser.add_argument("--price-per-million", type=float, default=0.15)
    parser.add_argument("--calls", type=int, default=1_000)
    args = parser.parse_args()
    for name in ("window", "layers", "kv_heads", "head_dim", "dtype_bytes"):
        if getattr(args, name) <= 0:
            parser.error(f"--{name.replace('_', '-')} must be positive")
    for name in ("output", "system", "tools", "history", "retrieved", "safety", "calls"):
        if getattr(args, name) < 0:
            parser.error(f"--{name} must be nonnegative")
    if not math.isfinite(args.price_per_million) or args.price_per_million < 0:
        parser.error("--price-per-million must be finite and nonnegative")

    used = (args.system + args.tools + args.history + args.retrieved
            + args.output + args.safety)
    remaining = args.window - used
    print("budget")
    print(f"  window        {args.window:>9,} tokens")
    print(f"  system        {args.system:>9,}")
    print(f"  tools         {args.tools:>9,}")
    print(f"  history       {args.history:>9,}")
    print(f"  retrieved     {args.retrieved:>9,}")
    print(f"  output reserve{args.output:>9,}")
    print(f"  safety        {args.safety:>9,}")
    print(f"  used          {used:>9,}")
    print(f"  remaining     {remaining:>9,} "
          f"({'OK' if remaining >= 0 else 'OVER BUDGET'})")
    if remaining < 0:
        print("  action: cut retrieved/history first; never spend the output "
              "reserve on input")

    per_token = kv_bytes_per_token(args.layers, args.kv_heads, args.head_dim,
                                   args.dtype_bytes)
    print()
    print("kv cache (one sequence)")
    print(f"  shape: layers={args.layers} kv_heads={args.kv_heads} "
          f"head_dim={args.head_dim} dtype={args.dtype_bytes} bytes")
    print(f"  per token: {per_token:,} B = {size(per_token)}")
    for tokens in (4_096, 32_768, 131_072):
        total = per_token * tokens
        print(f"  {tokens:>7,} tokens -> {total:>14,} B = {size(total)}")

    print()
    print("dense causal attention pairs (per head per layer)")
    for tokens in (4_096, 32_768, 131_072):
        print(f"  {tokens:>7,} tokens -> {attention_pairs(tokens):>18,} pairs")
    print("  note: FlashAttention avoids materializing the matrix, but the "
          "arithmetic still grows quadratically")

    input_per_call = args.system + args.tools + args.history + args.retrieved
    billed_input = input_per_call * args.calls
    cost = billed_input / 1_000_000 * args.price_per_million
    print()
    print("hypothetical input-only bill")
    print(f"  {args.calls:,} calls x {input_per_call:,} input "
          f"tokens = {billed_input:,} tokens")
    print(f"  at ${args.price_per_million:.2f} per million input tokens: "
          f"${cost:,.2f}")
    print("  (price is an input knob, not a quote; prompt caching and "
          "batch discounts change the bill)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
