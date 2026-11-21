#!/usr/bin/env python3
"""Byte-level BPE trained on a tiny corpus. Standard library only.

This is a teaching implementation. It skips the pretokenization regex,
special tokens and vocabulary compaction used by production tokenizers, so
its counts demonstrate the mechanism, not any vendor's token count.
"""
from __future__ import annotations

from collections import Counter
import sys

BASE = 256
CORPUS = [
    "agent 需要数 token。",
    "agent 的上下文里有很多 token。",
    "token 不是字，也不是词。",
    "同一个 token 在不同模型里可能不同。",
    "青禾工作坊用 token 预算安排上下文。",
    "工具调用的 JSON 也占 token。",
    "青禾工作坊的报名助手先数 token，再决定放哪些材料。",
]
SAMPLES = [
    "agent 需要数 token。",
    "青禾工作坊",
    "工具调用的 JSON 也占 token。",
    "🙂",
    "hello",
]


def apply(sequence: list[int], pair: tuple[int, int],
          new_id: int) -> list[int]:
    """Replace every non-overlapping occurrence of `pair` with `new_id`."""
    out: list[int] = []
    i = 0
    while i < len(sequence):
        if i + 1 < len(sequence) and (sequence[i], sequence[i + 1]) == pair:
            out.append(new_id)
            i += 2
        else:
            out.append(sequence[i])
            i += 1
    return out


def train(texts: list[str], merges: int):
    """Learn `merges` byte-pair rules; return (rules, vocabulary)."""
    sequences = [list(text.encode("utf-8")) for text in texts]
    vocab = {i: bytes([i]) for i in range(BASE)}
    rules: list[tuple[int, int]] = []
    for _ in range(merges):
        counts: Counter[tuple[int, int]] = Counter()
        for sequence in sequences:
            counts.update(zip(sequence, sequence[1:]))
        if not counts:
            break
        # Sorting the candidates and taking the highest count gives a stable
        # tie-break; production trainers also pin an order to be reproducible.
        pair = max(sorted(counts), key=lambda item: counts[item])
        new_id = BASE + len(rules)
        vocab[new_id] = vocab[pair[0]] + vocab[pair[1]]
        sequences = [apply(sequence, pair, new_id)
                     for sequence in sequences]
        rules.append(pair)
    return rules, vocab


def encode(text: str, rules: list[tuple[int, int]]) -> list[int]:
    """Apply learned merges in rank order, exactly once each."""
    sequence = list(text.encode("utf-8"))
    for rank, pair in enumerate(rules):
        sequence = apply(sequence, pair, BASE + rank)
    return sequence


def decode(ids: list[int], vocab: dict[int, bytes]) -> str:
    return b"".join(vocab[token] for token in ids).decode("utf-8")


def show(token: int, vocab: dict[int, bytes]) -> str:
    # A learned token may hold a fragment of a UTF-8 character. Escaping the
    # bytes keeps the teaching output printable without pretending the
    # fragment is text a reader could decode on its own.
    return vocab[token].decode("utf-8", errors="backslashreplace")


def main() -> int:
    # Redirected output on Windows inherits the locale code page (GBK), which
    # cannot encode the 🙂 sample. Keep the documented command reproducible
    # without extra shell setup; an interactive UTF-8 console is a no-op.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    rules, vocab = train(CORPUS, 32)
    print(f"corpus: {len(CORPUS)} lines, {len(CORPUS)} UTF-8 sequences")
    print(f"merges learned: {len(rules)}; vocabulary: {BASE + len(rules)}")
    print("first merges (rank: left + right -> new):")
    for rank, (left, right) in enumerate(rules[:8]):
        print(f"  {rank:02d}: {show(left, vocab)!r} + {show(right, vocab)!r}"
              f" -> {show(BASE + rank, vocab)!r}")

    print()
    print(f"{'sample':<22} {'chars':>5} {'utf8':>5} {'tokens':>6} {'tok/char':>8}")
    for text in SAMPLES:
        ids = encode(text, rules)
        assert decode(ids, vocab) == text, text
        chars = len(text)
        nbytes = len(text.encode("utf-8"))
        ratio = len(ids) / chars if chars else 0
        print(f"{text!r:<22} {chars:>5} {nbytes:>5} {len(ids):>6} {ratio:>8.2f}")

    print()
    print("round-trip OK: every sample decoded back to its original text")
    print("note: these are toy counts; a production tokenizer has different "
          "merges and will report different numbers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
