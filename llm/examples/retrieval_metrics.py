#!/usr/bin/env python3
"""Score two rankers with recall@k, MRR, NDCG@k and MAP@k.

Each query has a small pool of documents with graded relevance (2 = answers
the question, 1 = related, 0 = off-topic). The "keyword" ranker retrieves
more relevant documents but orders them by string match; the "vector" ranker
drops one relevant document but puts the best answer first.

Binary relevance means grade > 0. AP@k uses min(k, R) as denominator;
RR scans the full ranking. Inputs are unique document IDs and positive k.

The point is that one number is never enough: recall@3 rewards the keyword
ranker, NDCG@3 rewards the vector ranker, and both are right.
"""
from __future__ import annotations

import math

K = 3

CASES = [
    {
        "query": "退款多久到账",
        "grades": {"d1": 2, "d2": 2, "d3": 1, "d4": 0, "d5": 0},
        "keyword": ["d3", "d1", "d2", "d4", "d5"],
        "vector": ["d1", "d2", "d4", "d3", "d5"],
    },
    {
        "query": "发票怎么开",
        "grades": {"e1": 2, "e2": 1, "e3": 0, "e4": 0},
        "keyword": ["e2", "e1", "e3", "e4"],
        "vector": ["e1", "e3", "e2", "e4"],
    },
    {
        "query": "关闭自动续费",
        "grades": {"f1": 2, "f2": 2, "f3": 0, "f4": 0},
        "keyword": ["f3", "f2", "f1", "f4"],
        "vector": ["f1", "f2", "f3", "f4"],
    },
    {
        "query": "海外配送范围",
        "grades": {"g1": 2, "g2": 0, "g3": 1, "g4": 0},
        "keyword": ["g3", "g1", "g2", "g4"],
        "vector": ["g1", "g3", "g2", "g4"],
    },
    {
        "query": "优惠券能叠加吗",
        "grades": {"h1": 2, "h2": 1, "h3": 1, "h4": 0},
        "keyword": ["h2", "h3", "h1", "h4"],
        "vector": ["h1", "h2", "h3", "h4"],
    },
]


def recall_at_k(ranking: list[str], grades: dict[str, int], k: int) -> float:
    relevant = sum(1 for grade in grades.values() if grade > 0)
    found = sum(1 for doc in ranking[:k] if grades.get(doc, 0) > 0)
    return found / relevant if relevant else 0.0


def reciprocal_rank(ranking: list[str], grades: dict[str, int]) -> float:
    for position, doc in enumerate(ranking, start=1):
        if grades.get(doc, 0) > 0:
            return 1.0 / position
    return 0.0


def dcg(gains: list[float]) -> float:
    return sum(gain / math.log2(position + 1)
               for position, gain in enumerate(gains, start=1))


def ndcg_at_k(ranking: list[str], grades: dict[str, int], k: int) -> float:
    gains = [2 ** grades.get(doc, 0) - 1 for doc in ranking[:k]]
    ideal = sorted((2 ** grade - 1 for grade in grades.values()), reverse=True)[:k]
    best = dcg(ideal)
    return dcg(gains) / best if best else 0.0


def average_precision(ranking: list[str], grades: dict[str, int], k: int) -> float:
    hits = 0
    total = 0.0
    for position, doc in enumerate(ranking[:k], start=1):
        if grades.get(doc, 0) > 0:
            hits += 1
            total += hits / position
    relevant = min(k, sum(1 for grade in grades.values() if grade > 0))
    return total / relevant if relevant else 0.0


def main() -> int:
    print(f"k = {K}; grades 2/1/0 = answers / related / off-topic")
    print(f"{len(CASES)} queries; two rankers over the same pools")
    print()
    top_label = f"top-{K}"
    header = (f"  {'query':<12} {'ranker':<8} {top_label:<14} "
              f"{'recall':>6} {'RR':>6} {'NDCG':>6} {'AP':>6}")
    print(header)
    totals = {"keyword": [0.0] * 4, "vector": [0.0] * 4}
    for case in CASES:
        for ranker in ("keyword", "vector"):
            ranking = case[ranker]
            grades = case["grades"]
            row = (
                recall_at_k(ranking, grades, K),
                reciprocal_rank(ranking, grades),
                ndcg_at_k(ranking, grades, K),
                average_precision(ranking, grades, K),
            )
            for index, value in enumerate(row):
                totals[ranker][index] += value
            top = " ".join(ranking[:K])
            print(f"  {case['query']:<12} {ranker:<8} {top:<14} "
                  f"{row[0]:>6.2f} {row[1]:>6.2f} {row[2]:>6.2f} {row[3]:>6.2f}")
    print()
    print(f"  averages: recall@{K}, MRR (full ranking), NDCG@{K}, MAP@{K}")
    print(f"  {'average':<12} {'keyword':<8} {'':<14} "
          f"{totals['keyword'][0] / len(CASES):>6.2f} "
          f"{totals['keyword'][1] / len(CASES):>6.2f} "
          f"{totals['keyword'][2] / len(CASES):>6.2f} "
          f"{totals['keyword'][3] / len(CASES):>6.2f}")
    print(f"  {'average':<12} {'vector':<8} {'':<14} "
          f"{totals['vector'][0] / len(CASES):>6.2f} "
          f"{totals['vector'][1] / len(CASES):>6.2f} "
          f"{totals['vector'][2] / len(CASES):>6.2f} "
          f"{totals['vector'][3] / len(CASES):>6.2f}")
    print()
    print("reading the table")
    print(f"  recall@{K}  punished when relevant documents fall outside top-{K}")
    print("  MRR       punished when the first relevant document is far down")
    print(f"  NDCG@{K}    punished when the best answer is not near the top")
    print(f"  MAP@{K}     mean AP@{K}; AP denominator = min(k, relevant count)")
    print()
    print("note: grade 1 counts as a hit for RR, recall and AP. Only NDCG "
          "uses the graded gains here. Compare coverage and ordering, then "
          "check end-to-end answer quality")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
