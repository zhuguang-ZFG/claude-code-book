#!/usr/bin/env python3
"""Train toy word embeddings from co-occurrence, skip-gram style.

Standard library only. The vectors in ch02 are hand-set to explain the
geometry; here two embedding tables are learned with binary logistic loss.
This controlled corpus separates three topics. Uniform negative sampling
and per-pair SGD are teaching choices, not a reproduction of word2vec.c.
"""
from __future__ import annotations

import math
import random

DIM = 16
WINDOW = 2
NEGATIVES = 3
LR = 0.03
EPOCHS = 30
SEED = 11

# Three topics; words inside one topic share contexts, topics never mix.
SENTENCES = (
    ["退款", "退货", "换货", "售后", "退款", "退货", "换货", "售后"],
    ["发货", "物流", "签收", "配送", "发货", "物流", "签收", "配送"],
    ["报名", "开课", "退课", "改期", "报名", "开课", "退课", "改期"],
) * 12

VOCAB = sorted({word for sentence in SENTENCES for word in sentence})
ID = {word: i for i, word in enumerate(VOCAB)}
IDS = [[ID[word] for word in sentence] for sentence in SENTENCES]

TOPIC = {
    "退款": "售后", "退货": "售后", "换货": "售后", "售后": "售后",
    "发货": "物流", "物流": "物流", "签收": "物流", "配送": "物流",
    "报名": "课程", "开课": "课程", "退课": "课程", "改期": "课程",
}


def sigmoid(x: float) -> float:
    """Split by sign to avoid exp(-x) overflow for large negative x."""
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    scaled = math.exp(x)
    return scaled / (1.0 + scaled)


def softplus(x: float) -> float:
    """log(1+e^x) without overflow or underflow; keeps log(sigmoid) sane."""
    if x > 30:
        return x
    if x < -30:
        return 0.0
    return math.log1p(math.exp(x))


def dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def cosine(a: list[float], b: list[float]) -> float:
    na = math.sqrt(dot(a, a))
    nb = math.sqrt(dot(b, b))
    return dot(a, b) / (na * nb)


def pairs(ids: list[int]) -> list[tuple[int, int]]:
    """(center, context) pairs inside the window, both directions."""
    out = []
    for position in range(len(ids)):
        for offset in range(-WINDOW, WINDOW + 1):
            if offset == 0:
                continue
            other = position + offset
            if 0 <= other < len(ids):
                out.append((ids[position], ids[other]))
    return out


def sgd_pair(center: list[float], context: list[float],
             label: float, rate: float) -> float:
    """Update two distinct embedding rows; return their pre-update loss."""
    score = dot(center, context)
    loss = softplus(-score) if label else softplus(score)
    grad = sigmoid(score) - label
    for d in range(len(center)):
        old_center, old_context = center[d], context[d]
        center[d] -= rate * grad * old_context
        context[d] -= rate * grad * old_center
    return loss


def negative_pool(center: int, contexts: set[int], vocab_size: int) -> list[int]:
    """Finite uniform-sampling pool for this sentence's known contexts."""
    pool = [word for word in range(vocab_size)
            if word != center and word not in contexts]
    if not pool:
        raise ValueError("no eligible negative words; change corpus or window")
    return pool


def train(rng: random.Random) -> tuple[list[list[float]], list[list[float]],
                                      list[tuple[int, float]]]:
    """Return trained input vectors, initial input vectors and online losses."""
    corpus_pairs = [pairs(sentence) for sentence in IDS]
    if not any(corpus_pairs):
        raise ValueError("training needs at least one context pair")
    pools = []
    for sentence_pairs in corpus_pairs:
        real: dict[int, set[int]] = {}
        for center, context in sentence_pairs:
            real.setdefault(center, set()).add(context)
        pools.append({center: negative_pool(center, contexts, len(VOCAB))
                      for center, contexts in real.items()} if NEGATIVES else {})
    scale = 0.1
    vec = [[rng.gauss(0.0, scale) for _ in range(DIM)] for _ in VOCAB]
    out = [[rng.gauss(0.0, scale) for _ in range(DIM)] for _ in VOCAB]
    initial = [row[:] for row in vec]
    history = []
    for epoch in range(1, EPOCHS + 1):
        total = 0.0
        seen = 0
        for sentence_pairs, pool in zip(corpus_pairs, pools):
            for center, context in sentence_pairs:
                steps = [(center, context, 1.0)]
                for _ in range(NEGATIVES):
                    neg = rng.choice(pool[center])
                    steps.append((center, neg, 0.0))
                for c, o, label in steps:
                    total += sgd_pair(vec[c], out[o], label, LR)
                    seen += 1
        if epoch == 1 or epoch % 10 == 0:
            history.append((epoch, total / seen))
    return vec, initial, history


def neighbours(vec: list[list[float]], word: str, k: int = 3):
    index = ID[word]
    scored = [(cosine(vec[index], vec[j]), VOCAB[j])
              for j in range(len(VOCAB)) if j != index]
    scored.sort(reverse=True)
    return scored[:k]


def main() -> int:
    print(f"corpus: {len(SENTENCES)} sentences, {len(VOCAB)} words, "
          f"dim {DIM}, window ±{WINDOW}, {NEGATIVES} negatives")
    print(f"objective: skip-gram with negative sampling, "
          f"SGD lr={LR}, {EPOCHS} epochs")

    rng = random.Random(SEED)
    vec, initial, history = train(rng)
    for epoch, loss in history:
        print(f"  epoch {epoch:>2}: pair loss {loss:.6f}")

    same, cross = [], []
    for word in VOCAB:
        best = neighbours(vec, word)
        topics = {TOPIC[other] for _score, other in best}
        (same if topics == {TOPIC[word]} else cross).append(word)
    print(f"words whose top-3 neighbours all match their own topic: "
          f"{len(same)}/{len(VOCAB)}")
    misses = [w for w in cross]
    if misses:
        print(f"  misses: {', '.join(misses)}")

    print()
    print("nearest neighbours, before vs after training:")
    for word in ("退款", "发货", "报名"):
        before = "  ".join(f"{other} {score:+.2f}" for score, other in
                           neighbours(initial, word))
        after = "  ".join(f"{other} {score:+.2f}" for score, other in
                          neighbours(vec, word))
        print(f"  {word}")
        print(f"    before: {before}")
        print(f"    after : {after}")

    print()
    print("note: pair loss averages pre-update binary losses, including "
          "new negative draws. Neighbours use the input table only; "
          "topic grouping here is not a retrieval-quality evaluation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
