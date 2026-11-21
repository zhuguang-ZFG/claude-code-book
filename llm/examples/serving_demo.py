#!/usr/bin/env python3
"""Serving arithmetic: weights, KV cache, decode bandwidth and batching.

The bandwidth and compute figures are assumptions, not hardware specs. The
model shows why decode is memory-bound, how batch size trades latency for
throughput, and why continuous batching keeps slots busier than static batches.
"""
from __future__ import annotations

PARAMS = 7e9
LAYERS = 32
KV_HEADS = 8
HEAD_DIM = 128
DTYPE_BYTES = 2
KV_PER_TOKEN = 2 * LAYERS * KV_HEADS * HEAD_DIM * DTYPE_BYTES
BANDWIDTH = 3.0e12          # bytes per second, one assumed device
COMPUTE = 4e14              # FLOP/s, one assumed device
GPU_MEMORY = 80 * 1024 ** 3


def size(count: float) -> str:
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    value = float(count)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    raise AssertionError("unreachable")


def weights_bytes(params: float, bytes_per_param: float) -> float:
    return params * bytes_per_param


def kv_bytes(batch: int, context: int) -> float:
    return batch * context * KV_PER_TOKEN


def decode_seconds(batch: int, context: int, weight_bytes: float) -> float:
    # Every decode step reads the weights once plus the cached K/V.
    moved = weight_bytes + kv_bytes(batch, context)
    return moved / BANDWIDTH


def decode_throughput(batch: int, context: int, weight_bytes: float) -> float:
    return batch / decode_seconds(batch, context, weight_bytes)


def fits(batch: int, context: int, weight_bytes: float) -> bool:
    # weights + K/V + 10% headroom for activations and fragmentation
    used = weight_bytes + kv_bytes(batch, context)
    return used * 1.1 <= GPU_MEMORY


def static_utilization(lengths: list[int], slots: int) -> float:
    useful = sum(lengths)
    capacity = 0
    for start in range(0, len(lengths), slots):
        chunk = lengths[start:start + slots]
        capacity += slots * max(chunk)
    return useful / capacity


def continuous_utilization(lengths: list[int], slots: int) -> float:
    remaining = list(lengths)
    running: list[int] = []
    clock = 0
    useful = 0
    while remaining or running:
        while remaining and len(running) < slots:
            job = remaining.pop(0)
            running.append(job)
            useful += job
        if not running:
            break
        step = min(running)
        running = [job - step for job in running]
        clock += step
        running = [job for job in running if job > 0]
    return useful / (slots * clock)


def main() -> int:
    print(f"model: {PARAMS / 1e9:.0f}B params, {LAYERS} layers, "
          f"{KV_HEADS} KV heads x {HEAD_DIM}")
    print(f"KV cache: {KV_PER_TOKEN:,} B/token = {size(KV_PER_TOKEN)}")
    print("weights")
    for label, width in (("fp16", 2), ("int8", 1), ("int4", 0.5)):
        raw = weights_bytes(PARAMS, width)
        print(f"  {label:<5} {raw / 1e9:>6.1f} GB  {size(raw):>9}")
    print()

    for context in (8192, 32768):
        print(f"decode at context {context:,}")
        print("  batch   KV cache   step ms   tok/s   fits 80 GiB")
        for batch in (1, 8, 32):
            kv = kv_bytes(batch, context)
            step = decode_seconds(batch, context, weights_bytes(PARAMS, 2))
            print(f"  {batch:>5}   {size(kv):>9}   {step * 1000:>7.2f}   "
                  f"{decode_throughput(batch, context, weights_bytes(PARAMS, 2)):>7.0f}   "
                  f"{str(fits(batch, context, weights_bytes(PARAMS, 2))):<5}")
        print()

    context = 8192
    prefill = 2 * PARAMS * context
    print(f"prefill one {context:,}-token request: {prefill:.2e} FLOPs, "
          f"{prefill / COMPUTE:.2f} s at the assumed compute rate")
    print()

    lengths = [20, 200, 50, 120]
    print(f"batching toy: requests {lengths}, 2 slots")
    print(f"  static utilization:     {static_utilization(lengths, 2) * 100:.1f}%")
    print(f"  continuous utilization: {continuous_utilization(lengths, 2) * 100:.1f}%")
    print("  continuous batching fills a freed slot immediately; the toy "
          "ignores prefill and per-token variance")
    print()
    print("note: decode reads weights and K/V every step; FLOPs alone do not "
          "predict latency. Quantizing weights does not automatically "
          "quantize the KV cache")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
