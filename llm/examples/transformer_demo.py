#!/usr/bin/env python3
"""A pre-norm Transformer decoder sketch in pure stdlib Python.

No training, no GPU, no third-party packages. Keeps both the lightweight scalar
residual proxy (`block`) and a real multi-token Pre-LN decoder forward path
(`forward_block`, `forward_model`) with RoPE, causal GQA/MHA attention, SwiGLU,
sparse top-k MoE routing, parameter accounting, and KV cache budget helpers.
"""
from __future__ import annotations

import math
import struct

X0 = [1.0, 2.0, 3.0]
# Scalar multiplicative coefficients used by the toy `block()` proxy so zero
# deltas keep the stream unchanged while nonzero deltas scale `h`.
ATTN = [0.5, -0.25, 0.1]
FFN = [0.2, 0.3, -0.1]


def _f32(value: float) -> float:
    return struct.unpack("f", struct.pack("f", float(value)))[0]


def norm(vector: list[float]) -> float:
    return math.sqrt(math.fsum(value * value for value in vector))


def rms_norm(
    vector: list[float],
    eps: float = 1e-6,
    weight: list[float] | None = None,
    float32_stats: bool = False,
) -> tuple[list[float], float]:
    """RMSNorm without mean subtraction; optional IEEE float32 input/output casts.

    When ``float32_stats=True``, rounds each element of ``vector`` to IEEE
    float32, computes the mean-of-squares and ``+ eps`` root in 64-bit float,
    rounds the normalized vector back to float32, and then applies ``weight``.
    """
    if not vector:
        raise ValueError("vector must not be empty")
    if weight is not None and len(weight) != len(vector):
        raise ValueError("weight length must match vector length")
    if float32_stats:
        xs = [_f32(v) for v in vector]
        mean_sq = math.fsum(v * v for v in xs) / len(xs)
        rms = math.sqrt(mean_sq + eps)
        normed = [_f32(v / rms) for v in xs]
    else:
        rms = math.sqrt(math.fsum(v * v for v in vector) / len(vector) + eps)
        normed = [v / rms for v in vector]
    if weight is not None:
        normed = [v * w for v, w in zip(normed, weight)]
    return normed, rms


def layer_norm(
    vector: list[float],
    eps: float = 1e-6,
    weight: list[float] | None = None,
    bias: list[float] | None = None,
) -> tuple[list[float], float, float]:
    """Standard LayerNorm with optional affine gamma/beta."""
    if not vector:
        raise ValueError("vector must not be empty")
    if weight is not None and len(weight) != len(vector):
        raise ValueError("weight length must match vector length")
    if bias is not None and len(bias) != len(vector):
        raise ValueError("bias length must match vector length")
    n = len(vector)
    mean = math.fsum(vector) / n
    variance = math.fsum((value - mean) ** 2 for value in vector) / n
    scale = math.sqrt(variance + eps)
    out = [(value - mean) / scale for value in vector]
    if weight is not None:
        out = [v * w for v, w in zip(out, weight)]
    if bias is not None:
        out = [v + b for v, b in zip(out, bias)]
    return out, mean, scale


def add(left: list[float], right: list[float]) -> list[float]:
    if len(left) != len(right):
        raise ValueError("vector lengths must match")
    return [a + b for a, b in zip(left, right)]


def block(x: list[float], attention: list[float], ffn: list[float]) -> list[float]:
    """Toy scalar gating proxy: `x + sublayer_coeff * RMSNorm(x)` twice."""
    h, _ = rms_norm(x)
    x = add(x, [a * b for a, b in zip(attention, h)])
    h, _ = rms_norm(x)
    x = add(x, [a * b for a, b in zip(ffn, h)])
    return x


def dot(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("dot vectors must have equal length")
    return math.fsum(a * b for a, b in zip(left, right))


def matvec(
    matrix: list[list[float]],
    vector: list[float],
    bias: list[float] | None = None,
) -> list[float]:
    if any(len(row) != len(vector) for row in matrix):
        raise ValueError("matrix row width must match vector length")
    if bias is not None and len(bias) != len(matrix):
        raise ValueError("bias length must match output rows")
    out = [dot(row, vector) for row in matrix]
    if bias is not None:
        out = [v + b for v, b in zip(out, bias)]
    return out


def softmax(logits: list[float]) -> list[float]:
    if not logits:
        raise ValueError("logits must not be empty")
    peak = max(logits)
    exps = [math.exp(v - peak) for v in logits]
    denom = math.fsum(exps)
    return [v / denom for v in exps]


def silu(x: float) -> float:
    """Overflow-safe SiLU / Swish(beta=1): x * sigmoid(x)."""
    if x >= 0.0:
        return x / (1.0 + math.exp(-x))
    ex = math.exp(x)
    return x * ex / (1.0 + ex)


def gelu(x: float, approximate: str = "none") -> float:
    """Exact Gaussian-erf GELU or tanh GPT-2 approximation."""
    if approximate == "tanh":
        inner = math.sqrt(2.0 / math.pi) * (x + 0.044715 * (x ** 3))
        return 0.5 * x * (1.0 + math.tanh(inner))
    if approximate == "none":
        return 0.5 * x * (1.0 + math.erf(x / math.sqrt(2.0)))
    raise ValueError(f"unknown approximate mode: {approximate}")


def swiglu_ffn(
    x: list[float],
    w_gate: list[list[float]],
    w_up: list[list[float]],
    w_down: list[list[float]],
) -> list[float]:
    gate = [silu(v) for v in matvec(w_gate, x)]
    up = matvec(w_up, x)
    return matvec(w_down, [g * u for g, u in zip(gate, up)])


def two_layer_ffn(
    x: list[float],
    w_up: list[list[float]],
    w_down: list[list[float]],
    activation: str = "gelu",
) -> list[float]:
    hidden = matvec(w_up, x)
    if activation == "relu":
        act = [v if v > 0.0 else 0.0 for v in hidden]
    elif activation == "gelu":
        act = [gelu(v, approximate="none") for v in hidden]
    elif activation == "gelu_tanh":
        act = [gelu(v, approximate="tanh") for v in hidden]
    else:
        raise ValueError(f"unknown activation: {activation}")
    return matvec(w_down, act)


def rope(vector: list[float], position: int, base: float = 10_000.0) -> list[float]:
    """RoFormer interleaved rotation over adjacent pairs (2i, 2i+1)."""
    dim = len(vector)
    if dim % 2:
        raise ValueError("RoPE dimension must be even")
    out: list[float] = []
    for i in range(0, dim, 2):
        theta = position / (base ** (i / dim))
        c, s = math.cos(theta), math.sin(theta)
        out.append(vector[i] * c - vector[i + 1] * s)
        out.append(vector[i] * s + vector[i + 1] * c)
    return out


def rotate_half_rope(
    vector: list[float],
    position: int,
    base: float = 10_000.0,
) -> list[float]:
    """Hugging Face Llama/Qwen2 split-half rotation over pairs (i, i + d/2)."""
    dim = len(vector)
    if dim % 2:
        raise ValueError("RoPE dimension must be even")
    half = dim // 2
    first = [0.0] * half
    second = [0.0] * half
    for i in range(half):
        theta = position / (base ** ((2 * i) / dim))
        c, s = math.cos(theta), math.sin(theta)
        x1, x2 = vector[i], vector[i + half]
        first[i] = x1 * c - x2 * s
        second[i] = x1 * s + x2 * c
    return first + second


def interleaved_to_half(vector: list[float]) -> list[float]:
    """Permute (2i, 2i+1) layout to split-half (i, i + d/2) layout."""
    if len(vector) % 2:
        raise ValueError("dimension must be even")
    return vector[0::2] + vector[1::2]


def _apply_rope(vec: list[float], pos: int, base: float, mode: str) -> list[float]:
    if mode == "half":
        return rotate_half_rope(vec, pos, base=base)
    if mode == "interleaved":
        return rope(vec, pos, base=base)
    raise ValueError(f"unknown rope_mode: {mode}")


def causal_rope_attention(
    xs: list[list[float]],
    w_q: list[list[float]],
    w_k: list[list[float]],
    w_v: list[list[float]],
    w_o: list[list[float]],
    n_heads: int,
    n_kv_heads: int | None = None,
    rope_mode: str = "half",
    base: float = 10_000.0,
    qkv_bias: tuple[list[float] | None, list[float] | None, list[float] | None] | None = None,
) -> list[list[float]]:
    """Multi-head / GQA causal self-attention with per-head RoPE."""
    if not xs:
        return []
    d_model = len(xs[0])
    if d_model <= 0 or any(len(row) != d_model for row in xs):
        raise ValueError("all token vectors in xs must share a positive d_model")
    kv_heads = n_heads if n_kv_heads is None else n_kv_heads
    if n_heads <= 0 or kv_heads <= 0 or n_heads % kv_heads != 0:
        raise ValueError("n_heads must be a positive multiple of n_kv_heads")
    head_dim = len(w_q) // n_heads
    q_width = n_heads * head_dim
    kv_width = kv_heads * head_dim
    if head_dim * n_heads != len(w_q) or len(w_k) != kv_width or len(w_v) != kv_width:
        raise ValueError("projection row counts mismatch head configuration")
    if head_dim <= 0 or head_dim % 2:
        raise ValueError("head_dim must be positive and even for RoPE")
    if (any(len(row) != d_model for row in w_q)
            or any(len(row) != d_model for row in w_k)
            or any(len(row) != d_model for row in w_v)):
        raise ValueError("Q/K/V projection column width must match d_model")
    if len(w_o) != d_model or any(len(row) != q_width for row in w_o):
        raise ValueError("w_o shape mismatch")

    bq, bk, bv = qkv_bias if qkv_bias is not None else (None, None, None)
    seq_len = len(xs)
    q_proj = [matvec(w_q, x, bq) for x in xs]
    k_proj = [matvec(w_k, x, bk) for x in xs]
    v_proj = [matvec(w_v, x, bv) for x in xs]

    groups = n_heads // kv_heads
    inv_scale = 1.0 / math.sqrt(head_dim)
    out: list[list[float]] = []

    for i in range(seq_len):
        concat: list[float] = []
        for h in range(n_heads):
            kv_h = h // groups
            q_slice = q_proj[i][h * head_dim:(h + 1) * head_dim]
            q_rot = _apply_rope(q_slice, i, base, rope_mode)
            scores: list[float] = []
            vs_visible: list[list[float]] = []
            for j in range(i + 1):
                k_slice = k_proj[j][kv_h * head_dim:(kv_h + 1) * head_dim]
                k_rot = _apply_rope(k_slice, j, base, rope_mode)
                scores.append(dot(q_rot, k_rot) * inv_scale)
                vs_visible.append(v_proj[j][kv_h * head_dim:(kv_h + 1) * head_dim])
            weights = softmax(scores)
            head_out = [
                math.fsum(weights[j] * vs_visible[j][d] for j in range(i + 1))
                for d in range(head_dim)
            ]
            concat.extend(head_out)
        if len(w_o[0]) != len(concat) or len(w_o) != d_model:
            raise ValueError("w_o shape mismatch")
        out.append(matvec(w_o, concat))
    return out


def forward_block(
    xs: list[list[float]],
    weights: dict,
    eps: float = 1e-6,
    base: float = 10_000.0,
    rope_mode: str = "half",
) -> list[list[float]]:
    """Run one full Pre-LN decoder block (RMSNorm -> RoPE GQA/MHA -> RMSNorm -> SwiGLU)."""
    in_norm_w = weights.get("input_layernorm")
    post_norm_w = weights.get("post_attention_layernorm")
    normed1 = [rms_norm(x, eps=eps, weight=in_norm_w)[0] for x in xs]
    attn_out = causal_rope_attention(
        normed1,
        weights["w_q"],
        weights["w_k"],
        weights["w_v"],
        weights["w_o"],
        n_heads=weights["n_heads"],
        n_kv_heads=weights.get("n_kv_heads"),
        rope_mode=rope_mode,
        base=base,
        qkv_bias=weights.get("qkv_bias"),
    )
    after_attn = [add(x, delta) for x, delta in zip(xs, attn_out)]
    normed2 = [rms_norm(x, eps=eps, weight=post_norm_w)[0] for x in after_attn]
    ffn_out = [
        swiglu_ffn(h, weights["w_gate"], weights["w_up"], weights["w_down"])
        for h in normed2
    ]
    return [add(x, delta) for x, delta in zip(after_attn, ffn_out)]


def forward_model(
    xs: list[list[float]],
    blocks: list[dict],
    final_norm_weight: list[float] | None = None,
    lm_head_weight: list[list[float]] | None = None,
    eps: float = 1e-6,
    base: float = 10_000.0,
    rope_mode: str = "half",
) -> tuple[list[list[float]], list[list[float]] | None]:
    """Run stacked Pre-LN blocks followed by Final RMSNorm and optional lm_head."""
    hidden = [row[:] for row in xs]
    for blk in blocks:
        hidden = forward_block(hidden, blk, eps=eps, base=base, rope_mode=rope_mode)
    normed = [rms_norm(h, eps=eps, weight=final_norm_weight)[0] for h in hidden]
    logits = [matvec(lm_head_weight, h) for h in normed] if lm_head_weight else None
    return normed, logits


def sparse_moe_forward(
    x: list[float],
    router_weight: list[list[float]],
    experts: list[dict[str, list[list[float]]]],
    top_k: int = 2,
) -> tuple[list[float], list[tuple[int, float]]]:
    """Mixtral-style sparse MoE: linear gate -> softmax -> top_k -> renormalize."""
    if top_k <= 0 or top_k > len(experts):
        raise ValueError("top_k must lie in [1, len(experts)]")
    probs = softmax(matvec(router_weight, x))
    ranked = sorted(enumerate(probs), key=lambda item: (-item[1], item[0]))[:top_k]
    kept_sum = math.fsum(weight for _, weight in ranked)
    renorm = [(idx, weight / kept_sum) for idx, weight in ranked]
    acc = [0.0] * len(x)
    for idx, weight in renorm:
        exp = experts[idx]
        exp_out = swiglu_ffn(x, exp["w_gate"], exp["w_up"], exp["w_down"])
        acc = add(acc, [weight * v for v in exp_out])
    return acc, renorm


def params(
    d_model: int,
    layers: int,
    heads: int,
    d_ff: int,
    vocab: int,
    swiglu: bool = True,
    tied: bool = True,
    *,
    kv_heads: int | None = None,
    head_dim: int | None = None,
    moe_experts: int = 1,
    moe_active: int = 1,
    shared_experts: int = 0,
    final_norm: bool = False,
    qkv_bias: bool = False,
    o_bias: bool = False,
    mlp_bias: bool = False,
) -> dict[str, int]:
    """Model-card parameter count covering MHA/GQA, SwiGLU/FFN, Final Norm, biases & MoE."""
    if d_model <= 0 or layers <= 0 or heads <= 0 or d_ff <= 0 or vocab <= 0:
        raise ValueError("model dimensions and layer/vocab counts must be positive")
    kv = heads if kv_heads is None else kv_heads
    if kv <= 0 or heads % kv != 0:
        raise ValueError("heads must be a positive multiple of kv_heads")
    if head_dim is None:
        if d_model % heads != 0:
            raise ValueError("d_model must be divisible by heads when head_dim is omitted")
        head_dim = d_model // heads
    elif head_dim <= 0:
        raise ValueError("head_dim must be positive")
    if moe_experts <= 0 or moe_active <= 0 or moe_active > moe_experts or shared_experts < 0:
        raise ValueError("invalid MoE expert counts")
    q_proj = d_model * heads * head_dim
    o_proj = heads * head_dim * d_model
    k_proj = d_model * kv * head_dim
    v_proj = d_model * kv * head_dim
    attention = q_proj + k_proj + v_proj + o_proj
    attn_bias = 0
    if qkv_bias:
        attn_bias += heads * head_dim + 2 * kv * head_dim
    if o_bias:
        attn_bias += d_model

    ffn_per_expert = (3 if swiglu else 2) * d_model * d_ff
    ffn_bias_per_expert = ((2 if swiglu else 1) * d_ff + d_model) if mlp_bias else 0
    bias = attn_bias + ffn_bias_per_expert * (moe_experts + shared_experts)
    active_bias = attn_bias + ffn_bias_per_expert * (moe_active + shared_experts)
    total_ffn = ffn_per_expert * (moe_experts + shared_experts)
    active_ffn = ffn_per_expert * (moe_active + shared_experts)
    router = d_model * moe_experts if moe_experts > 1 else 0
    norms = 2 * d_model

    per_layer = attention + total_ffn + norms + router + bias
    active_per_layer = attention + active_ffn + norms + router + active_bias
    fn_params = d_model if final_norm else 0
    embedding = d_model * vocab * (1 if tied else 2)
    return {
        "attention": attention,
        "ffn": total_ffn,
        "active_ffn": active_ffn,
        "norms": norms,
        "router": router,
        "bias": bias,
        "final_norm": fn_params,
        "per_layer": per_layer,
        "active_per_layer": active_per_layer,
        "body": per_layer * layers,
        "embedding": embedding,
        "total": per_layer * layers + fn_params + embedding,
        "active_total": active_per_layer * layers + fn_params + embedding,
    }


def memory_budget(
    total_params: int,
    layers: int,
    kv_heads: int,
    head_dim: int,
    context_len: int,
    concurrency: int = 1,
    weight_bytes: float = 2.0,
    kv_bytes: float = 2.0,
) -> dict[str, float]:
    """Separate weight memory from KV cache memory in both binary GiB and decimal GB."""
    w_bytes = total_params * weight_bytes
    kvc_bytes = 2 * layers * kv_heads * head_dim * kv_bytes * context_len * concurrency
    gib = 1024 ** 3
    gb = 1000 ** 3
    return {
        "weight_bytes": w_bytes,
        "kv_bytes": kvc_bytes,
        "weight_gib": w_bytes / gib,
        "kv_gib": kvc_bytes / gib,
        "total_gib": (w_bytes + kvc_bytes) / gib,
        "weight_gb": w_bytes / gb,
        "kv_gb": kvc_bytes / gb,
        "total_gb": (w_bytes + kvc_bytes) / gb,
    }


def fmt(vector: list[float]) -> str:
    return "[" + ", ".join(f"{value:.3f}" for value in vector) + "]"


def _demo_real_block() -> tuple[list[list[float]], list[list[float]]]:
    xs = [[1.0, 0.5, -0.5, 0.25], [0.2, 1.2, 0.4, -0.8]]
    eye4 = [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]
    w_k = [
        [0.5, 0.0, 0.5, 0.0],
        [0.0, 0.5, 0.0, 0.5],
        [-0.5, 0.5, 0.5, 0.0],
        [0.5, 0.5, 0.0, -0.5],
    ]
    blk = {
        "n_heads": 1,
        "n_kv_heads": 1,
        "w_q": eye4,
        "w_k": w_k,
        "w_v": eye4,
        "w_o": eye4,
        "w_gate": eye4,
        "w_up": eye4,
        "w_down": eye4,
    }
    after = forward_block(xs, blk, rope_mode="half")
    final_norm, _ = forward_model(xs, [blk, blk], final_norm_weight=[1.0] * 4)
    return after, final_norm


def _demo_moe() -> tuple[list[float], list[tuple[int, float]]]:
    x = [1.0, -0.5]
    router = [[1.4, -0.6], [0.5, -1.2], [-0.8, 1.5]]
    experts = [
        {"w_gate": [[1.0, 0.0], [0.0, 1.0]], "w_up": [[1.0, 0.0], [0.0, 1.0]], "w_down": [[0.5, 0.0], [0.0, 0.5]]},
        {"w_gate": [[0.0, 1.0], [1.0, 0.0]], "w_up": [[1.0, 0.5], [-0.5, 1.0]], "w_down": [[0.4, 0.0], [0.0, 0.4]]},
        {"w_gate": [[-1.0, 1.0], [0.5, 0.5]], "w_up": [[0.5, -0.5], [1.0, 1.0]], "w_down": [[0.3, 0.0], [0.0, 0.3]]},
    ]
    return sparse_moe_forward(x, router, experts, top_k=2)


def main() -> int:
    print("input x:", fmt(X0), "norm:", f"{norm(X0):.3f}")
    normalized, scale_value = rms_norm(X0)
    print("rms_norm:", fmt(normalized), "scale:", f"{scale_value:.3f}")
    centered, mean, scale_value = layer_norm(X0)
    print("layer_norm:", fmt(centered), "mean:", f"{mean:.3f}",
          "scale:", f"{scale_value:.3f}")
    print()

    print("residual stream, two scalar-proxy pre-norm blocks")
    x = X0
    for index in range(1, 3):
        x = block(x, ATTN, FFN)
        print(f"  block {index}: {fmt(x)} norm={norm(x):.3f}")
    print("  the stream keeps the input and adds each block's update")
    print()

    print("real 2-token Pre-LN RoPE+SwiGLU sequence block (d_model=4, n_heads=1):")
    after_block, after_final = _demo_real_block()
    print("  1-block output:", fmt(after_block[0]), fmt(after_block[1]))
    print("  2-block + Final Norm:", fmt(after_final[0]), "norm=", f"{norm(after_final[0]):.3f}")
    print()

    print("parameter count, d_model=4096, layers=32, heads=32, vocab=32000")
    for label, d_ff, swiglu in (("SwiGLU d_ff=11008", 11008, True),
                                ("ReLU d_ff=16384", 16384, False)):
        for tied in (True, False):
            counts = params(4096, 32, 32, d_ff, 32000, swiglu, tied)
            print(f"  {label:<18} tied={str(tied):<5} "
                  f"per_layer={counts['per_layer']:,} "
                  f"total={counts['total']:,}")
    counts = params(4096, 32, 32, 11008, 32000, True, False)
    llama_exact = params(4096, 32, 32, 11008, 32000, True, False, final_norm=True)
    gqa8 = params(4096, 32, 32, 11008, 32000, True, False, kv_heads=8, final_norm=True)
    moe8 = params(4096, 32, 32, 14336, 32000, True, False,
                  kv_heads=8, moe_experts=8, moe_active=2, final_norm=True)
    budget = memory_budget(counts["total"], 32, 32, 128, 131_072)
    print(f"  attention per layer: {counts['attention']:,}")
    print(f"  ffn per layer:       {counts['ffn']:,}")
    print(f"  embedding (untied):  {counts['embedding']:,}")
    print(f"  + Final Norm (4096): {llama_exact['total']:,}")
    print(f"  GQA-8 attention:     {gqa8['attention']:,} (total={gqa8['total']:,})")
    print(f"  MoE 8x-top2 (14336): total={moe8['total']:,} active={moe8['active_total']:,}")
    print(
        f"  128K fp16 budget:    weights={budget['weight_gib']:.2f} GiB "
        f"({budget['weight_gb']:.2f} GB) + kv={budget['kv_gib']:.2f} GiB "
        f"= {budget['total_gib']:.2f} GiB"
    )
    print()

    print("RoPE with fixed query/key content: shared position shifts preserve the dot product")
    query = [1.0, 0.0]
    key = [1.0, 0.0]
    for offset in (0, 1, 2, 3):
        left = rope(query, offset)
        right = rope(key, 0)
        print(f"  m-n={offset}: dot={dot(left, right):+.3f}")
    print("  in 2D the only frequency is base**0 = 1; changing base has no effect")
    print()

    print("RoPE in 4D: compare bases using two coordinate pairs")
    query = [1.0, 0.0, 1.0, 0.0]
    key = [1.0, 0.0, 1.0, 0.0]
    for base in (10_000.0, 100.0):
        value = dot(rope(query, 10, base), rope(key, 0, base))
        shifted = dot(rope(query, 17, base), rope(key, 7, base))
        print(f"  base={base:g}, m-n=10: dot={value:+.3f}; "
              f"after shifting both positions by 7: {shifted:+.3f}")

    q4 = [0.4, -1.2, 0.7, 2.0]
    k4 = [1.3, 0.5, -0.8, 0.1]
    interleaved_dot = dot(rope(q4, 10), rope(k4, 0))
    half_matched_dot = dot(
        rotate_half_rope(interleaved_to_half(q4), 10),
        rotate_half_rope(interleaved_to_half(k4), 0),
    )
    half_mixed_dot = dot(rotate_half_rope(q4, 10), rotate_half_rope(k4, 0))
    print(
        f"  layout check: interleaved={interleaved_dot:+.3f}, "
        f"permuted rotate_half={half_matched_dot:+.3f}, "
        f"unpermuted mismatch={half_mixed_dot:+.3f}"
    )
    moe_out, moe_weights = _demo_moe()
    weights_str = ", ".join(f"E{i}:{w:.3f}" for i, w in moe_weights)
    print(f"  sparse MoE top-2:    [{weights_str}] -> {fmt(moe_out)}")
    print("  changing query/key content can change scores at the same offset")
    print()
    print("note: this is a forward-pass sketch; chapter 7 adds a separate "
          "training example with gradients, a loss and an optimizer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
