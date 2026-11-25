#!/usr/bin/env python3
"""A tiny RAG retrieval pipeline: chunks, BM25, vectors, RRF and rerank.

The corpus and vectors are hand-set. The code shows the shape of a retrieval
stack, not the quality of a trained retriever. Chinese is tokenized into
character bigrams because the example has no segmenter dependency.
"""
from __future__ import annotations

import math
import re

DOCS = [
    {
        "id": "refund-policy",
        "title": "退款政策",
        "version": 2,
        "text": "未发货订单可以申请退款。退款审核通过后原路退回。"
                "到账时间通常为 1–3 个工作日。",
        "vec": [0.95, 0.05, 0.0],
    },
    {
        "id": "return-policy",
        "title": "退货政策",
        "version": 2,
        "text": "已发货订单需要先申请退货。退货签收后才会退款。"
                "退款同样原路退回。",
        "vec": [0.80, 0.15, 0.0],
    },
    {
        "id": "shipping",
        "title": "物流时效",
        "version": 2,
        "text": "发货后 48 小时内更新物流单号。物流停滞超过 72 小时可以申请排查。",
        "vec": [0.05, 0.95, 0.0],
    },
    {
        "id": "invoice",
        "title": "发票申请",
        "version": 2,
        "text": "订单完成后可以申请电子发票。发票会在 3 个工作日内开出。",
        "vec": [0.0, 0.05, 0.95],
    },
    {
        "id": "refund-faq",
        "title": "退款常见问题",
        "version": 2,
        "text": "退款到账时间受银行处理速度影响。不退款的情况包括已使用和超期。",
        "vec": [0.90, 0.10, 0.0],
    },
    {
        "id": "refund-policy",
        "title": "退款政策（旧版）",
        "version": 1,
        "text": "退款审核通过后 7 天内退回。",
        "vec": [0.85, 0.05, 0.0],
    },
]
QUERY = "退款多久到账"
QUERY_VEC = [0.95, 0.05, 0.0]


def tokens(text: str) -> list[str]:
    lowered = text.lower()
    words = re.findall(r"[a-z0-9]+", lowered)
    han = re.findall(r"[\u4e00-\u9fff]", lowered)
    bigrams = [han[i] + han[i + 1] for i in range(len(han) - 1)]
    return words + bigrams


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[。；！？])", text)
    return [part.strip() for part in parts if part.strip()]


def chunk_fixed(text: str, size: int) -> list[str]:
    return [text[i:i + size] for i in range(0, len(text), size)]


def build_chunks(docs: list[dict]) -> list[dict]:
    chunks = []
    for doc in docs:
        for index, sentence in enumerate(split_sentences(doc["text"])):
            chunks.append({
                **doc,
                "chunk_id": f'{doc["id"]}@v{doc["version"]}#{index}',
                "text": f'{doc["title"]}：{sentence}',
            })
    return chunks


def dedupe(chunks: list[dict]) -> list[dict]:
    seen = set()
    kept = []
    for chunk in chunks:
        key = re.sub(r"\s+", "", chunk["text"])
        if key in seen:
            continue
        seen.add(key)
        kept.append(chunk)
    return kept


def filter_stale(chunks: list[dict], min_version: int = 2) -> list[dict]:
    return [chunk for chunk in chunks if chunk["version"] >= min_version]


def bm25(chunks: list[dict], query: str, k1: float = 1.2,
         b: float = 0.75) -> list[tuple[dict, float]]:
    docs = [tokens(chunk["text"]) for chunk in chunks]
    query_terms = tokens(query)
    n_docs = len(docs)
    avg_len = sum(len(doc) for doc in docs) / n_docs
    df = {term: sum(1 for doc in docs if term in doc) for term in set(query_terms)}
    scored = []
    for chunk, doc in zip(chunks, docs):
        score = 0.0
        for term in query_terms:
            tf = doc.count(term)
            if not tf:
                continue
            idf = math.log(1 + (n_docs - df[term] + 0.5) / (df[term] + 0.5))
            norm = k1 * (1 - b + b * len(doc) / avg_len)
            score += idf * tf * (k1 + 1) / (tf + norm)
        scored.append((chunk, score))
    return sorted(scored, key=lambda row: row[1], reverse=True)


def cosine(left: list[float], right: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right))
    denominator = math.sqrt(sum(a * a for a in left)) * math.sqrt(
        sum(b * b for b in right))
    return numerator / denominator if denominator else 0.0


def vector_search(chunks: list[dict], query_vec: list[float]):
    return sorted(((chunk, cosine(query_vec, chunk["vec"])) for chunk in chunks),
                  key=lambda row: row[1], reverse=True)


def rrf(rankings: list[list[dict]], k: int = 60) -> list[tuple[dict, float]]:
    scores: dict[str, float] = {}
    by_id: dict[str, dict] = {}
    for ranking in rankings:
        for rank, chunk in enumerate(ranking, 1):
            cid = chunk["chunk_id"]
            by_id[cid] = chunk
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank)
    return sorted(((by_id[cid], score) for cid, score in scores.items()),
                  key=lambda row: row[1], reverse=True)


def rerank(chunks: list[dict], query: str):
    query_terms = set(tokens(query))
    scored = []
    for chunk in chunks:
        overlap = len(query_terms & set(tokens(chunk["text"])))
        title_hit = int(any(term in chunk["title"] for term in query_terms))
        score = 0.6 * cosine(QUERY_VEC, chunk["vec"]) + 0.1 * overlap + 0.2 * title_hit
        scored.append((chunk, score))
    return sorted(scored, key=lambda row: row[1], reverse=True)


def main() -> int:
    raw = build_chunks(DOCS)
    chunks = dedupe(filter_stale(raw))
    print(f"documents: {len(DOCS)}, raw chunks: {len(raw)}, "
          f"after version filter + dedupe: {len(chunks)}")
    print(f"query: {QUERY}")
    print()

    small = chunk_fixed("退款审核通过后原路退回", 10)
    large = chunk_fixed("退款审核通过后原路退回", 20)
    print("chunk size check for the answer span '退款审核通过后原路退回'")
    print(f"  size 10: {small} -> intact={any('原路退回' in c for c in small)}")
    print(f"  size 20: {large} -> intact={any('原路退回' in c for c in large)}")
    print()

    lexical = bm25(chunks, QUERY)
    semantic = vector_search(chunks, QUERY_VEC)
    fused = rrf([[row[0] for row in lexical],
                 [row[0] for row in semantic]])
    reranked = rerank([row[0] for row in fused[:8]], QUERY)

    print("top 3 by each stage")
    print("  rank   BM25                         vector                       RRF                          rerank")
    for index in range(3):
        print(f"  {index + 1:^4}   {lexical[index][0]['chunk_id']:<28} "
              f"{semantic[index][0]['chunk_id']:<28} "
              f"{fused[index][0]['chunk_id']:<28} "
              f"{reranked[index][0]['chunk_id']}")
    print()
    print("scores")
    print(f"  BM25 top:   {lexical[0][1]:.3f}  {lexical[0][0]['text']}")
    print(f"  vector top: {semantic[0][1]:.3f}  {semantic[0][0]['text']}")
    print(f"  RRF top:    {fused[0][1]:.4f}  {fused[0][0]['text']}")
    print(f"  rerank top: {reranked[0][1]:.3f}  {reranked[0][0]['text']}")
    print()
    print("note: BM25 is lexical, the vectors are hand-set, and the reranker "
          "is a toy. Validate production retrieval on real documents and an "
          "evaluation set; choose dense retrieval and reranking components "
          "to match the task")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
