#!/usr/bin/env python3
"""Train a tiny character-level Transformer with hand-written backprop.

Standard library only. The model is deliberately tiny; the honesty is the
point. A real loss goes down under real gradient descent, a numeric gradient
check proves the backprop formulas, and the trained model continues the
prompt in its own repetitive style. Every number is reproducible with the
fixed seed.
"""
from __future__ import annotations

import math
import random

D_MODEL = 24
D_FF = 48
N_CTX = 10
STEPS = 240
LR = 0.6
WARMUP = 12
MIN_LR_RATIO = 0.1
SEED = 7

CORPUS = (
    "青禾工作坊的 agent 报名。青禾工作坊的 agent 退款。青禾工作坊的 agent 查单。"
    "青禾工作坊的 agent 改地址。青禾工作坊的 agent 修票。青禾工作坊的 agent 退单。"
    "青禾工作坊的 agent 报名。青禾工作坊的 agent 退款。青禾工作坊的 agent 查单。"
    "青禾工作坊的 agent 改地址。青禾工作坊的 agent 修票。青禾工作坊的 agent 退单。"
    "the agent files a report. the agent checks the list. the agent files a report. "
    "the agent checks the list. the agent files a report. the agent checks the list. "
    "工具调用的 JSON 也占 token。同一个 token 在不同模型里可能不同。"
    "工具调用的 JSON 也占 token。同一个 token 在不同模型里可能不同。"
)

VOCAB = sorted(set(CORPUS))
CH_TO_ID = {ch: i for i, ch in enumerate(VOCAB)}
IDS = [CH_TO_ID[ch] for ch in CORPUS]


def zeros(rows: int, cols: int) -> list[list[float]]:
    return [[0.0] * cols for _ in range(rows)]


def gaussian(rng: random.Random, rows: int, cols: int,
            scale: float) -> list[list[float]]:
    return [[rng.gauss(0.0, scale) for _ in range(cols)] for _ in range(rows)]


def matmul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    """(r,k) @ (k,c)"""
    cols = range(len(b[0]))
    return [[sum(row[k] * b[k][c] for k in range(len(b))) for c in cols]
            for row in a]


def matmul_at_b(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    """a @ b^T where b is stored (rows, cols): result (len(a), len(b))."""
    return [[sum(x * y for x, y in zip(row, other)) for other in b] for row in a]


def matmul_bt_a(b: list[list[float]], a: list[list[float]]) -> list[list[float]]:
    """b^T @ a where b is stored (rows, cols): result (len(b[0]), len(a[0]))."""
    out = zeros(len(b[0]), len(a[0]))
    for i in range(len(b)):
        for k in range(len(b[0])):
            factor = b[i][k]
            if factor:
                row = out[k]
                for j, value in enumerate(a[i]):
                    row[j] += factor * value
    return out


class Tiny:
    """One causal self-attention layer, one FFN, untied output, no norm.

    Norms and biases are left out for readability; the gradients below are
    the real formulas and the numeric check proves them.
    """

    def __init__(self, vocab: int, rng: random.Random):
        scale = 0.1 / math.sqrt(D_MODEL)
        self.wte = gaussian(rng, vocab, D_MODEL, scale)
        self.wpe = gaussian(rng, N_CTX, D_MODEL, scale)
        self.wq = gaussian(rng, D_MODEL, D_MODEL, scale)
        self.wk = gaussian(rng, D_MODEL, D_MODEL, scale)
        self.wv = gaussian(rng, D_MODEL, D_MODEL, scale)
        self.wo = gaussian(rng, D_MODEL, D_MODEL, scale)
        self.w1 = gaussian(rng, D_MODEL, D_FF, scale)
        self.w2 = gaussian(rng, D_FF, D_MODEL, scale)
        self.wout = gaussian(rng, vocab, D_MODEL, scale)
        self.vocab = vocab

    def params(self) -> dict[str, list[list[float]]]:
        return {"wte": self.wte, "wpe": self.wpe, "wq": self.wq, "wk": self.wk,
                "wv": self.wv, "wo": self.wo, "w1": self.w1, "w2": self.w2,
                "wout": self.wout}

    def _forward(self, ids: list[int]) -> dict:
        T = len(ids)
        x = [[self.wte[i][d] + self.wpe[t][d] for d in range(D_MODEL)]
             for t, i in enumerate(ids)]
        q = matmul(x, self.wq)
        k = matmul(x, self.wk)
        v = matmul(x, self.wv)
        scale = math.sqrt(D_MODEL)
        scores = [[(dot(q[i], k[j]) / scale if j <= i else float("-inf"))
                   for j in range(T)] for i in range(T)]
        attn = [softmax(scores[i]) for i in range(T)]
        o = matmul(attn, v)
        attn_out = matmul(o, self.wo)
        h1 = [[x[t][d] + attn_out[t][d] for d in range(D_MODEL)] for t in range(T)]
        u = matmul(h1, self.w1)
        r = [[value if value > 0 else 0.0 for value in row] for row in u]
        f2 = matmul(r, self.w2)
        h2 = [[h1[t][d] + f2[t][d] for d in range(D_MODEL)] for t in range(T)]
        logits = matmul_at_b(h2, self.wout)
        return {"ids": ids, "x": x, "q": q, "k": k, "v": v, "attn": attn,
                "o": o, "h1": h1, "u": u, "r": r, "h2": h2, "logits": logits}

    def loss(self, ids: list[int], targets: list[int]) -> float:
        cache = self._forward(ids)
        total = 0.0
        for row, target in zip(cache["logits"], targets):
            total += -log_softmax(row)[target]
        return total / len(ids)

    def loss_and_grads(self, ids: list[int],
                       targets: list[int]) -> tuple[float, dict]:
        cache = self._forward(ids)
        T = len(ids)
        probs = [softmax(row) for row in cache["logits"]]
        loss = sum(-math.log(p[t]) for p, t in zip(probs, targets)) / T

        # softmax + cross-entropy, averaged over positions
        dlogits = zeros(T, self.vocab)
        for i, target in enumerate(targets):
            row = probs[i]
            dlogits[i] = [(row[j] - (1.0 if j == target else 0.0)) / T
                          for j in range(self.vocab)]

        h2 = cache["h2"]
        dwout = matmul_bt_a(dlogits, h2)
        dh2 = matmul(dlogits, self.wout)

        # residual: h2 = h1 + FFN(h1)
        dh1 = [row[:] for row in dh2]
        df2 = dh2
        dw2 = matmul_bt_a(cache["r"], df2)
        dr = matmul_at_b(df2, self.w2)
        du = [[dr[t][d] if cache["u"][t][d] > 0 else 0.0
               for d in range(D_FF)] for t in range(T)]
        dw1 = matmul_bt_a(cache["h1"], du)
        for t in range(T):
            for d in range(D_MODEL):
                dh1[t][d] += sum(du[t][f] * self.w1[d][f] for f in range(D_FF))

        # residual: h1 = x + attention(x)
        dx = [row[:] for row in dh1]
        dattn_out = dh1
        dwo = matmul_bt_a(cache["o"], dattn_out)
        do = matmul(dattn_out, self.wo)

        # attention weights: softmax rows
        dattn = matmul_at_b(do, cache["v"])
        dv = matmul_bt_a(cache["attn"], do)
        dscores = zeros(T, T)
        scale = math.sqrt(D_MODEL)
        for i in range(T):
            p = cache["attn"][i]
            g = dattn[i]
            total = sum(p[j] * g[j] for j in range(i + 1))
            for j in range(i + 1):
                dscores[i][j] = p[j] * (g[j] - total) / scale

        dq = matmul(dscores, cache["k"])
        dk = matmul_bt_a(dscores, cache["q"])
        dwq = matmul_bt_a(cache["x"], dq)
        dwk = matmul_bt_a(cache["x"], dk)
        dwv = matmul_bt_a(cache["x"], dv)
        for t in range(T):
            for d in range(D_MODEL):
                extra = (sum(dq[t][c] * self.wq[c][d] for c in range(D_MODEL))
                         + sum(dk[t][c] * self.wk[c][d] for c in range(D_MODEL))
                         + sum(dv[t][c] * self.wv[c][d] for c in range(D_MODEL)))
                dx[t][d] += extra

        dwte = zeros(self.vocab, D_MODEL)
        dwpe = zeros(N_CTX, D_MODEL)
        for t, i in enumerate(ids):
            for d in range(D_MODEL):
                dwte[i][d] += dx[t][d]
                dwpe[t][d] += dx[t][d]

        return loss, {"wte": dwte, "wpe": dwpe, "wq": dwq, "wk": dwk,
                      "wv": dwv, "wo": dwo, "w1": dw1, "w2": dw2,
                      "wout": dwout}


def dot(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def softmax(scores: list[float]) -> list[float]:
    largest = max(scores)
    exps = [math.exp(score - largest) for score in scores]
    total = sum(exps)
    return [value / total for value in exps]


def log_softmax(scores: list[float]) -> list[float]:
    largest = max(scores)
    total = sum(math.exp(score - largest) for score in scores)
    shift = largest + math.log(total)
    return [score - shift for score in scores]


def sgd(model: Tiny, grads: dict[str, list[list[float]]],
        lr: float) -> None:
    for name, weight in model.params().items():
        grad = grads[name]
        for i in range(len(weight)):
            for j in range(len(weight[0])):
                weight[i][j] -= lr * grad[i][j]


def gradcheck(model: Tiny, ids: list[int], targets: list[int],
              rng: random.Random, tries: int = 8,
              epsilon: float = 1e-4) -> float:
    """Central differences on a few random weights vs the analytic grads."""
    _loss, grads = model.loss_and_grads(ids, targets)
    worst = 0.0
    for _ in range(tries):
        name = rng.choice(list(grads))
        rows, cols = len(grads[name]), len(grads[name][0])
        i, j = rng.randrange(rows), rng.randrange(cols)
        if name == "wte":
            i = ids[i % len(ids)]  # a token actually in this window
        weight = model.params()[name]
        original = weight[i][j]
        weight[i][j] = original + epsilon
        plus = model.loss(ids, targets)
        weight[i][j] = original - epsilon
        minus = model.loss(ids, targets)
        weight[i][j] = original
        numeric = (plus - minus) / (2 * epsilon)
        worst = max(worst, abs(numeric - grads[name][i][j]))
    return worst


def lr_at(step: int) -> float:
    """Warmup linearly, then cosine-decay to MIN_LR_RATIO: the standard
    schedule in practice.

    Small steps early keep noisy first gradients from throwing the weights
    around; shrinking (but never zero) steps late let the loss settle.
    """
    if step <= WARMUP:
        return LR * step / WARMUP
    progress = (step - WARMUP) / max(1, STEPS - WARMUP)
    floor = LR * MIN_LR_RATIO
    span = LR - floor
    return floor + span * 0.5 * (1.0 + math.cos(math.pi * progress))


def train(model: Tiny, rng: random.Random) -> list[tuple[int, float]]:
    history = []
    for step in range(1, STEPS + 1):
        start = rng.randrange(0, len(IDS) - N_CTX - 1)
        window = IDS[start:start + N_CTX]
        targets = IDS[start + 1:start + N_CTX + 1]
        loss, grads = model.loss_and_grads(window, targets)
        sgd(model, grads, lr_at(step))
        if step == 1 or step % 60 == 0:
            history.append((step, loss))
    return history


def generate(model: Tiny, prompt: str, length: int = 24) -> str:
    ids = [CH_TO_ID[ch] for ch in prompt]
    out = list(prompt)
    for _ in range(length):
        window = ids[-N_CTX:]
        cache = model._forward(window)
        row = cache["logits"][-1]
        best = max(range(len(row)), key=row.__getitem__)
        ids.append(best)
        out.append(VOCAB[best])
    return "".join(out)


def main() -> int:
    rng = random.Random(SEED)
    model = Tiny(len(VOCAB), rng)
    count = sum(len(w) * len(w[0]) for w in model.params().values())
    print(f"corpus: {len(CORPUS)} chars, vocab {len(VOCAB)}, ctx {N_CTX}")
    print(f"model: d_model={D_MODEL}, ffn={D_FF}, 1 causal layer, "
          f"{count} params, untied head")
    print(f"optimizer: SGD lr={LR}, warmup {WARMUP} steps then cosine decay "
          f"to {MIN_LR_RATIO:.0%}, batch=1 random window, {STEPS} steps")

    start = rng.randrange(0, len(IDS) - N_CTX - 1)
    probe = IDS[start:start + N_CTX]
    targets = IDS[start + 1:start + N_CTX + 1]
    untrained = model.loss(probe, targets)
    print(f"loss before training: {untrained:.2f} "
          f"(ln {len(VOCAB)}) = {math.log(len(VOCAB)):.2f})")

    worst = gradcheck(model, probe, targets, random.Random(SEED + 1))
    print(f"gradcheck: 8 sampled weights, max |analytic-numeric| "
          f"diff = {worst:.2e}")

    history = train(model, random.Random(SEED))
    for step, loss in history:
        print(f"  step {step:>3}: loss {loss:.2f}")
    trained = model.loss(probe, targets)
    print(f"loss after training: {trained:.2f} on the same window "
          f"({untrained - trained:+.2f})")

    sample = generate(model, "青禾工作坊", 20)
    print(f"greedy sample from '青禾工作坊': {sample}")
    print("note: a real nano-GPT is the same loop with more layers, "
          "bytes and GPUs; the curve above is the honest small version")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
