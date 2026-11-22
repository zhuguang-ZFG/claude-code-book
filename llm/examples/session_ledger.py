#!/usr/bin/env python3
"""One agent session, priced turn by turn.

A four-turn coding session resends its whole prompt every turn. This script
adds up the tokens, the money and the waiting time for three serving
strategies, so the numbers behind chapters 6 and 10 become one bill:

  no cache            pay full price for every resent token
  stable prefix       cache only the system prompt and the retrieved docs
  append-only prefix  cache the previous turn's whole prompt (it is a prefix
                      of the next one, because history only grows)

Prices, rates and the model shape are assumptions, not vendor quotes.
Replace them with your own provider's numbers before making a budget.
"""
from __future__ import annotations

KI = 1024

# --- assumptions -----------------------------------------------------------
SYSTEM_TOKENS = 1200          # stable system prompt, never edited
TASK_TOKENS = 300             # the user's opening request
DOCS = 3                      # retrieved chunks attached once
DOC_TOKENS = 600              # tokens per chunk
TURNS = 4                     # agent turns in the session
OUTPUT_TOKENS = (250, 250, 250, 400)
TOOL_TOKENS = 800             # each tool result appended to the history

LAYERS = 80                   # a 70B-class model
KV_HEADS = 8
HEAD_DIM = 128
DTYPE_BYTES = 2

PRICE_INPUT = 3.00            # USD per million input tokens
PRICE_CACHED = 0.30           # USD per million cached input tokens
PRICE_OUTPUT = 15.00          # USD per million output tokens

PREFILL_RATE = 2000.0         # tokens per second, batched prefill
DECODE_RATE = 50.0            # tokens per second, one request

KV_PER_TOKEN = 2 * LAYERS * KV_HEADS * HEAD_DIM * DTYPE_BYTES


def size(count: float) -> str:
    units = ("B", "KiB", "MiB", "GiB")
    value = float(count)
    for unit in units:
        if value < KI or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= KI
    raise AssertionError("unreachable")


def turn_prompts() -> list[int]:
    """Prompt length seen by the model on each turn (history only grows)."""
    prompts = []
    history = SYSTEM_TOKENS + TASK_TOKENS + DOCS * DOC_TOKENS
    for turn in range(TURNS):
        prompts.append(history)
        history += OUTPUT_TOKENS[turn] + TOOL_TOKENS
    return prompts


def prefix_tokens() -> int:
    """The part of turn 1 that never changes: system prompt plus docs."""
    return SYSTEM_TOKENS + DOCS * DOC_TOKENS


def cost(prompt: int, cached: int, output: int) -> tuple[float, float]:
    """Return (input cost, output cost) in USD for one turn."""
    fresh = prompt - cached
    input_cost = (fresh * PRICE_INPUT + cached * PRICE_CACHED) / 1e6
    return input_cost, output * PRICE_OUTPUT / 1e6


def run(strategy: str) -> dict[str, object]:
    """Price and time the session under one caching strategy."""
    prompts = turn_prompts()
    stable = prefix_tokens()
    rows = []
    for index, prompt in enumerate(prompts):
        if strategy == "no cache":
            cached = 0
        elif strategy == "stable prefix":
            cached = stable if index else 0
        elif strategy == "append-only prefix":
            # The previous prompt is a literal prefix of this one.
            cached = prompts[index - 1] if index else 0
        else:
            raise ValueError(strategy)
        fresh = prompt - cached
        input_cost, output_cost = cost(prompt, cached, OUTPUT_TOKENS[index])
        prefill = fresh / PREFILL_RATE
        decode = OUTPUT_TOKENS[index] / DECODE_RATE
        rows.append({
            "prompt": prompt, "cached": cached, "fresh": fresh,
            "output": OUTPUT_TOKENS[index], "input_cost": input_cost,
            "output_cost": output_cost, "prefill": prefill, "decode": decode,
        })
    return {
        "rows": rows,
        "input_cost": sum(row["input_cost"] for row in rows),
        "output_cost": sum(row["output_cost"] for row in rows),
        "bill": sum(row["input_cost"] + row["output_cost"] for row in rows),
        "seconds": sum(row["prefill"] + row["decode"] for row in rows),
    }


def main() -> int:
    prompts = turn_prompts()
    fresh = [prompt - (prompts[index - 1] if index else 0)
             for index, prompt in enumerate(prompts)]
    resent = sum(prompts) - sum(fresh)
    total_output = sum(OUTPUT_TOKENS)
    peak = prompts[-1] + OUTPUT_TOKENS[-1]

    print(f"session: {TURNS} turns, system {SYSTEM_TOKENS:,} + task "
          f"{TASK_TOKENS:,} + {DOCS} docs x {DOC_TOKENS:,} tokens")
    print(f"model:  {LAYERS} layers, {KV_HEADS} KV heads x {HEAD_DIM}, "
          f"fp16 -> {size(KV_PER_TOKEN)}/token")
    print(f"prices: ${PRICE_INPUT:.2f}/M input, ${PRICE_CACHED:.2f}/M cached, "
          f"${PRICE_OUTPUT:.2f}/M output (assumptions)")
    print()

    print("what the model sees on each turn")
    print("  turn   prompt   re-sent   fresh   output")
    for index, prompt in enumerate(prompts):
        print(f"  {index + 1:>4} {prompt:>8,} {prompt - fresh[index]:>9,} "
              f"{fresh[index]:>7,} {OUTPUT_TOKENS[index]:>8,}")
    print(f"  {'sum':>4} {sum(prompts):>8,} {resent:>9,} "
          f"{sum(fresh):>7,} {total_output:>8,}")
    print()

    print("where the input tokens go (no cache)")
    rows = [
        ("system prompt", SYSTEM_TOKENS * TURNS),
        ("retrieved docs", DOCS * DOC_TOKENS * TURNS),
        ("tool results", sum(sum(OUTPUT_TOKENS[:i]) + TOOL_TOKENS * i
                             for i in range(TURNS))),
        ("task", TASK_TOKENS * TURNS),
    ]
    for label, tokens in rows:
        print(f"  {label:<15} {tokens:>7,} {tokens / sum(prompts) * 100:>6.1f}%")
    print(f"  only {sum(fresh):,} of {sum(prompts):,} input tokens are fresh "
          f"({sum(fresh) / sum(prompts) * 100:.1f}%)")
    print()

    print("three strategies, same session")
    print("  strategy                input $  output $    bill $   model s")
    baseline = None
    for strategy in ("no cache", "stable prefix", "append-only prefix"):
        result = run(strategy)
        if baseline is None:
            baseline = result["bill"]
        saved = (baseline - result["bill"]) / baseline * 100
        tail = "" if strategy == "no cache" else f"  -{saved:.1f}%"
        print(f"  {strategy:<22} {result['input_cost']:>7.5f} "
              f"{result['output_cost']:>9.5f} {result['bill']:>8.5f} "
              f"{result['seconds']:>9.2f}{tail}")
    print()

    kv = peak * KV_PER_TOKEN
    print(f"KV cache at peak context ({peak:,} tokens): {size(kv)} per request")
    print("  sessions   KV cache")
    for batch in (1, 8, 32):
        print(f"  {batch:>8}   {size(kv * batch):>9}")
    print()
    print("note: the append-only row assumes every turn's prompt is the last "
          "turn's prompt plus new text, and that the cache survives; history "
          "rewrites, trimming and cache eviction all break it")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
