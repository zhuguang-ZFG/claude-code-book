"""The LLM volume's examples must run with the standard library alone."""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "llm" / "examples"


def load(name: str):
    spec = importlib.util.spec_from_file_location(f"llm_{name}", EXAMPLES / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run(name: str) -> str:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    completed = subprocess.run(
        [sys.executable, str(EXAMPLES / f"{name}.py")],
        cwd=ROOT, env=env, check=True, capture_output=True, text=True,
        encoding="utf-8")
    return completed.stdout


class BpeExample(unittest.TestCase):
    def setUp(self):
        self.bpe = load("bpe_demo")

    def test_every_sample_round_trips_through_bytes_and_ids(self):
        rules, vocab = self.bpe.train(self.bpe.CORPUS, 32)
        self.assertEqual(len(rules), 32)
        for text in [*self.bpe.SAMPLES, "", "生僻字：龘", "a b\tc\n"]:
            ids = self.bpe.encode(text, rules)
            self.assertEqual(self.bpe.decode(ids, vocab), text)
            self.assertLessEqual(len(ids), len(text.encode("utf-8")))

    def test_training_is_reproducible(self):
        first = self.bpe.train(self.bpe.CORPUS, 16)
        second = self.bpe.train(self.bpe.CORPUS, 16)
        self.assertEqual(first[0], second[0])
        self.assertEqual(first[1], second[1])

    def test_command_prints_the_three_counts_and_round_trip(self):
        output = run("bpe_demo")
        self.assertIn("round-trip OK", output)
        self.assertIn("merges learned: 32", output)
        self.assertIn("青禾工作坊", output)
        self.assertIn("🙂", output)

    def test_command_survives_a_gbk_locale(self):
        # The documented command must work when Windows inherits code page 936.
        env = {**os.environ, "PYTHONIOENCODING": "gbk"}
        completed = subprocess.run(
            [sys.executable, str(EXAMPLES / "bpe_demo.py")],
            cwd=ROOT, env=env, check=True, capture_output=True)
        self.assertIn("🙂", completed.stdout.decode("utf-8"))


class EmbeddingExample(unittest.TestCase):
    def setUp(self):
        self.embedding = load("embedding_demo")

    def test_cosine_handles_direction_and_zero_vectors(self):
        module = self.embedding
        self.assertAlmostEqual(module.cosine([1.0, 0.0], [2.0, 0.0]), 1.0)
        self.assertAlmostEqual(module.cosine([1.0, 0.0], [0.0, 1.0]), 0.0)
        self.assertAlmostEqual(module.cosine([1.0, 0.0], [-1.0, 0.0]), -1.0)
        with self.assertRaises(ValueError):
            module.cosine([0.0, 0.0], [1.0, 0.0])

    def test_dot_and_cosine_can_disagree_on_ranking(self):
        module = self.embedding
        query = [3.0, 0.0]
        short, long = [1.0, 0.0], [2.0, 2.0]
        self.assertGreater(module.dot(query, long), module.dot(query, short))
        self.assertGreater(module.cosine(query, short),
                           module.cosine(query, long))

    def test_top_k_excludes_the_query_and_sorts_by_cosine(self):
        module = self.embedding
        rows = module.top_k(module.VECTORS["退款"], module.VECTORS, 3)
        names = [row[0] for row in rows]
        self.assertNotIn("退款", names)
        self.assertEqual(names[0], "不退款")
        scores = [row[1] for row in rows]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_negation_is_nearly_parallel_in_the_toy_space(self):
        module = self.embedding
        self.assertAlmostEqual(
            module.cosine(module.VECTORS["退款"], module.VECTORS["不退款"]),
            0.9997, places=4)

    def test_command_prints_costs_and_the_negation_warning(self):
        output = run("embedding_demo")
        self.assertIn("dot ranks B first; cosine ranks A first", output)
        self.assertIn("cosine(退款, 不退款) = 0.9997", output)
        self.assertIn("131,072,000 params", output)
        self.assertIn("1.5 GiB", output)


class SftExample(unittest.TestCase):
    def setUp(self):
        self.sft = load("sft_demo")

    def test_masking_changes_the_loss_average(self):
        module = self.sft
        losses, all_mean, assistant_mean = module.masked_loss(
            module.TARGET_PROB, module.MASK)
        self.assertAlmostEqual(losses[0], 0.051, places=3)
        self.assertAlmostEqual(losses[-1], 0.693, places=3)
        self.assertAlmostEqual(all_mean, 0.367, places=3)
        self.assertAlmostEqual(assistant_mean, 0.520, places=3)
        self.assertLess(all_mean, assistant_mean)
        self.assertEqual(sum(module.MASK), 3)

    def test_lora_delta_has_the_expected_low_rank_update(self):
        module = self.sft
        delta = module.lora_delta(module.A, module.B, module.ALPHA, module.RANK)
        self.assertEqual(len(delta), 4)
        self.assertEqual([round(value, 3) for value in delta[0]],
                         [0.1, 0.0, -0.1, 0.0])
        base = module.matvec(module.W, module.X)
        adapted = module.matvec(module.add(module.W, delta), module.X)
        self.assertEqual([round(value, 3) for value in base],
                         [0.3, 0.4, 0.3, 0.5])
        self.assertEqual([round(value, 3) for value in adapted],
                         [0.3, 0.5, 0.3, 0.54])

    def test_zero_b_starts_from_the_base_model(self):
        module = self.sft
        zero = [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]
        delta = module.lora_delta(module.A, zero, module.ALPHA, module.RANK)
        self.assertTrue(all(value == 0 for row in delta for value in row))
        self.assertEqual(module.matvec(module.add(module.W, delta), module.X),
                         module.matvec(module.W, module.X))

    def test_parameter_counts_and_adapter_size(self):
        module = self.sft
        r8 = module.params(4096, 8)
        self.assertEqual(r8["trainable"], 65_536)
        self.assertAlmostEqual(r8["ratio"], 0.00390625)
        self.assertEqual(r8["trainable"] * 2, 131_072)
        self.assertEqual(module.size(r8["trainable"] * 2 * 32), "4.0 MiB")
        self.assertEqual(module.params(4096, 4096)["ratio"], 2.0)

    def test_command_prints_the_masked_loss_and_lora_table(self):
        output = run("sft_demo")
        self.assertIn("assistant-only mean:  0.520", output)
        self.assertIn("[0.300, 0.500, 0.300, 0.540]", output)
        self.assertIn("merge check: OK", output)
        self.assertIn("65,536", output)
        self.assertIn("4.0 MiB", output)


class AlignmentExample(unittest.TestCase):
    def setUp(self):
        self.alignment = load("alignment_demo")

    def test_bradley_terry_loss_follows_the_margin(self):
        module = self.alignment
        loss, margin = module.bt_loss(2.0, 1.0)
        self.assertAlmostEqual(margin, 1.0)
        self.assertAlmostEqual(loss, 0.313, places=3)
        loss, margin = module.bt_loss(1.2, 1.2)
        self.assertAlmostEqual(margin, 0.0)
        self.assertAlmostEqual(loss, 0.693, places=3)
        loss, margin = module.bt_loss(-1.0, -0.5)
        self.assertAlmostEqual(margin, -0.5)
        self.assertAlmostEqual(loss, 0.974, places=3)

    def test_toy_pairs_have_one_win_and_a_high_mean_loss(self):
        module = self.alignment
        losses, correct = [], 0
        for _label, chosen, rejected in module.PAIRS:
            loss, margin = module.bt_loss(chosen, rejected)
            losses.append(loss)
            correct += int(margin > 0)
        self.assertEqual(correct, 1)
        self.assertAlmostEqual(sum(losses) / len(losses), 0.681, places=3)

    def test_dpo_terms_and_beta_scale_the_margin(self):
        module = self.alignment
        chosen, rejected, gap = module.dpo_terms(-0.2, -0.5, -0.6, -0.4)
        self.assertAlmostEqual(chosen, 0.3)
        self.assertAlmostEqual(rejected, -0.2)
        self.assertAlmostEqual(gap, 0.5)
        loss, margin = module.dpo_loss(-0.2, -0.5, -0.6, -0.4, 0.1)
        self.assertAlmostEqual(margin, 0.05)
        self.assertAlmostEqual(loss, 0.668, places=3)
        loss, margin = module.dpo_loss(-0.2, -0.5, -0.6, -0.4, 1.0)
        self.assertAlmostEqual(margin, 0.5)
        self.assertAlmostEqual(loss, 0.474, places=3)

    def test_reversed_preference_has_a_higher_loss_and_beta_must_be_positive(self):
        module = self.alignment
        loss, margin = module.dpo_loss(-0.4, -0.5, -0.2, -0.6, 1.0)
        self.assertAlmostEqual(margin, -0.3)
        self.assertAlmostEqual(loss, 0.854, places=3)
        with self.assertRaises(ValueError):
            module.dpo_loss(-0.2, -0.5, -0.6, -0.4, 0)

    def test_command_prints_both_losses_and_the_log_two_check(self):
        output = run("alignment_demo")
        self.assertIn("pairwise accuracy (margin > 0): 1/4", output)
        self.assertIn("mean loss: 0.681", output)
        self.assertIn("0.474", output)
        self.assertIn("0.854", output)
        self.assertIn("-log(sigmoid(0)) = 0.693", output)


class ScalingExample(unittest.TestCase):
    def setUp(self):
        self.scaling = load("scaling_demo")

    def test_training_flops_follows_six_nd(self):
        module = self.scaling
        self.assertEqual(module.training_flops(7e9, 300e9), 1.26e22)
        self.assertEqual(module.training_flops(7e9, 1e9), 4.2e19)

    def test_chinchilla_allocation_balances_parameters_and_tokens(self):
        module = self.scaling
        params, tokens = module.allocation(1e22)
        self.assertAlmostEqual(params, 9.1287e9, places=-6)
        self.assertAlmostEqual(tokens, 1.8257e11, places=-8)
        self.assertAlmostEqual(tokens / params, 20.0)

    def test_gpu_days_and_inference_flops(self):
        module = self.scaling
        self.assertAlmostEqual(module.gpu_days(1e22), 289.35, places=1)
        self.assertEqual(module.inference_flops(7e9, 1e6), 1.4e16)
        self.assertEqual(module.size(112e9), "104.3 GiB")

    def test_command_prints_the_compute_table_and_inference_cost(self):
        output = run("scaling_demo")
        self.assertIn("9.1B", output)
        self.assertIn("1.00e+22", output)
        self.assertIn("2,431", output)
        self.assertIn("14 GFLOP per token", output)
        self.assertIn("35 GPU-seconds", output)


class ServingExample(unittest.TestCase):
    def setUp(self):
        self.serving = load("serving_demo")

    def test_kv_cache_and_weight_sizes(self):
        module = self.serving
        self.assertEqual(module.KV_PER_TOKEN, 131_072)
        self.assertEqual(module.size(module.KV_PER_TOKEN), "128.0 KiB")
        self.assertEqual(module.size(module.weights_bytes(7e9, 2)), "13.0 GiB")
        self.assertEqual(module.size(module.weights_bytes(7e9, 1)), "6.5 GiB")
        self.assertEqual(module.size(module.weights_bytes(7e9, 0.5)), "3.3 GiB")

    def test_decode_time_and_throughput_grow_with_batch(self):
        module = self.serving
        one = module.decode_seconds(1, 8192, module.weights_bytes(7e9, 2))
        many = module.decode_seconds(32, 8192, module.weights_bytes(7e9, 2))
        self.assertAlmostEqual(one * 1000, 5.02, places=2)
        self.assertAlmostEqual(many * 1000, 16.12, places=2)
        self.assertLess(module.decode_throughput(1, 8192, 14e9), 200)
        self.assertGreater(module.decode_throughput(32, 8192, 14e9), 1900)

    def test_long_context_batch_does_not_fit(self):
        module = self.serving
        self.assertTrue(module.fits(8, 32768, module.weights_bytes(7e9, 2)))
        self.assertFalse(module.fits(32, 32768, module.weights_bytes(7e9, 2)))

    def test_continuous_batching_keeps_slots_busier(self):
        module = self.serving
        lengths = [20, 200, 50, 120]
        static = module.static_utilization(lengths, 2)
        continuous = module.continuous_utilization(lengths, 2)
        self.assertAlmostEqual(static, 0.609375)
        self.assertAlmostEqual(continuous, 0.975)
        self.assertGreater(continuous, static)

    def test_command_prints_memory_and_scheduler_tables(self):
        output = run("serving_demo")
        self.assertIn("131,072 B/token", output)
        self.assertIn("5.02", output)
        self.assertIn("1985", output)
        self.assertIn("static utilization:     60.9%", output)
        self.assertIn("continuous utilization: 97.5%", output)


class RagExample(unittest.TestCase):
    def setUp(self):
        self.rag = load("rag_demo")

    def test_chunk_size_can_split_the_answer(self):
        module = self.rag
        text = "退款审核通过后原路退回"
        small = module.chunk_fixed(text, 10)
        large = module.chunk_fixed(text, 20)
        self.assertFalse(any("原路退回" in chunk for chunk in small))
        self.assertTrue(any("原路退回" in chunk for chunk in large))

    def test_version_filter_and_dedupe_shrink_the_candidate_set(self):
        module = self.rag
        raw = module.build_chunks(module.DOCS)
        self.assertEqual(len(raw), 13)
        filtered = module.filter_stale(raw)
        self.assertEqual(len(filtered), 12)
        self.assertTrue(all(chunk["version"] >= 2 for chunk in filtered))
        self.assertEqual(len(module.dedupe(filtered)), 12)

    def test_lexical_and_vector_recall_disagree_then_rrf_fuses(self):
        module = self.rag
        chunks = module.dedupe(module.filter_stale(module.build_chunks(module.DOCS)))
        lexical = module.bm25(chunks, module.QUERY)
        semantic = module.vector_search(chunks, module.QUERY_VEC)
        self.assertEqual(lexical[0][0]["chunk_id"], "refund-faq#0")
        self.assertEqual(semantic[0][0]["chunk_id"], "refund-policy#0")
        fused = module.rrf([[row[0] for row in lexical],
                            [row[0] for row in semantic]])
        self.assertEqual(fused[0][0]["chunk_id"], "refund-policy#0")
        reranked = module.rerank([row[0] for row in fused[:8]], module.QUERY)
        self.assertEqual(reranked[0][0]["chunk_id"], "refund-policy#2")

    def test_command_prints_the_pipeline_and_top_hits(self):
        output = run("rag_demo")
        self.assertIn("raw chunks: 13", output)
        self.assertIn("after version filter + dedupe: 12", output)
        self.assertIn("refund-faq#0", output)
        self.assertIn("refund-policy#2", output)
        self.assertIn("intact=False", output)
        self.assertIn("intact=True", output)


class ToolCallExample(unittest.TestCase):
    def setUp(self):
        self.tool = load("toolcall_demo")

    def test_schema_rejects_wrong_types_and_unknown_tools(self):
        module = self.tool
        errors = module.validate("get_refund_status", {"order_id": 1001})
        self.assertIn("order_id must be a string", errors[0])
        self.assertEqual(module.validate("get_refund_status",
                                         {"order_id": "ORD-1001"}), [])
        self.assertIn("unknown tool",
                      module.validate("delete_order", {})[0])

    def test_a_validation_error_becomes_a_tool_result(self):
        module = self.tool
        bad = module.call_tool("get_refund_status", {"order_id": 1001})
        self.assertTrue(bad["isError"])
        self.assertIn("validation failed", bad["content"])
        good = module.call_tool("get_refund_status", {"order_id": "ORD-1001"})
        self.assertFalse(good["isError"])
        self.assertIn("退款处理中", good["content"])
        missing = module.call_tool("get_refund_status", {"order_id": "ORD-9999"})
        self.assertTrue(missing["isError"])
        self.assertIn("order not found", missing["content"])

    def test_mcp_messages_have_the_expected_shape(self):
        module = self.tool
        messages = module.mcp_messages()
        self.assertEqual([message["method"] for message in messages],
                         ["initialize", "tools/list", "tools/call"])
        self.assertTrue(all(message["jsonrpc"] == "2.0" for message in messages))
        self.assertEqual(messages[0]["params"]["protocolVersion"], "2026-07-28")
        self.assertEqual(messages[-1]["params"]["name"], "get_refund_status")

    def test_command_prints_validation_and_mcp(self):
        output = run("toolcall_demo")
        self.assertIn("get_refund_status: 181 chars", output)
        self.assertIn("create_ticket: 241 chars", output)
        self.assertIn("validation failed: order_id must be a string", output)
        self.assertIn('"method": "tools/call"', output)
        self.assertIn("退款处理中", output)


class CotExample(unittest.TestCase):
    def setUp(self):
        self.cot = load("cot_demo")

    def test_majority_accuracy_rises_with_samples(self):
        module = self.cot
        scores = [module.majority_accuracy(0.60, n) for n in (1, 3, 5, 9)]
        self.assertAlmostEqual(scores[0], 0.607, places=3)
        self.assertEqual(scores, sorted(scores))
        self.assertGreater(scores[-1], scores[0])

    def test_invalid_sample_counts_are_rejected(self):
        module = self.cot
        with self.assertRaises(ValueError):
            module.majority_accuracy(0.6, 2)
        with self.assertRaises(ValueError):
            module.majority_accuracy(0.0, 3)

    def test_cost_per_correct_divides_by_accuracy(self):
        module = self.cot
        self.assertAlmostEqual(module.cost_per_correct(100, 0.6, 0.5),
                               0.00012)
        with self.assertRaises(ValueError):
            module.cost_per_correct(100, 0.6, 0)

    def test_command_prints_voting_and_cost_tables(self):
        output = run("cot_demo")
        self.assertIn("60.7%", output)
        self.assertIn("79.5%", output)
        self.assertIn("CoT x15 majority", output)
        self.assertIn("$0.004053", output)
        self.assertIn("independent errors", output)


class EvalExample(unittest.TestCase):
    def setUp(self):
        self.eval = load("eval_demo")

    def test_wilson_interval_contains_the_point_estimate(self):
        module = self.eval
        low, high = module.wilson(164, 200)
        self.assertLess(low, 0.82)
        self.assertGreater(high, 0.82)
        self.assertAlmostEqual(low, 0.7606, places=3)
        self.assertAlmostEqual(high, 0.8674, places=3)
        low_b, high_b = module.wilson(172, 200)
        self.assertLessEqual(max(low, low_b), min(high, high_b))

    def test_contamination_and_abstention_counts(self):
        module = self.eval
        result = module.contamination(144, 180, 20, 20)
        self.assertAlmostEqual(result["clean"], 0.80)
        self.assertAlmostEqual(result["reported"], 0.82)
        self.assertAlmostEqual(result["inflation"], 0.02)
        result = module.abstention(80, 72, 100)
        self.assertAlmostEqual(result["coverage"], 0.80)
        self.assertAlmostEqual(result["answered_precision"], 0.90)
        self.assertAlmostEqual(result["overall"], 0.72)
        self.assertAlmostEqual(result["wrong_rate"], 0.08)

    def test_cost_per_correct_and_invalid_inputs(self):
        module = self.eval
        self.assertAlmostEqual(module.cost_per_correct(0.006, 0.85),
                               0.0070588, places=6)
        self.assertAlmostEqual(module.cost_per_correct(0.0012, 0.78),
                               0.0015385, places=6)
        with self.assertRaises(ValueError):
            module.cost_per_correct(0.006, 0)
        with self.assertRaises(ValueError):
            module.wilson(201, 200)

    def test_command_prints_intervals_and_cost(self):
        output = run("eval_demo")
        self.assertIn("[76.1%, 86.7%]", output)
        self.assertIn("[80.5%, 90.1%]", output)
        self.assertIn("clean accuracy:    80.0%", output)
        self.assertIn("coverage:           80.0%", output)
        self.assertIn("$0.0071", output)
        self.assertIn("$0.0015", output)


class AttentionExample(unittest.TestCase):
    def setUp(self):
        self.attention = load("attention_demo")

    def test_causal_rows_never_read_the_future(self):
        module = self.attention
        q = module.project(module.X, module.IDENTITY)
        k = module.project(module.X, module.IDENTITY)
        v = module.project(module.X, module.IDENTITY)
        _outputs, rows = module.attention(q, k, v, causal=True)
        for i, weights in enumerate(rows):
            self.assertAlmostEqual(sum(weights), 1.0)
            for j, weight in enumerate(weights):
                if j > i:
                    self.assertEqual(weight, 0.0, (i, j))
                else:
                    self.assertGreater(weight, 0.0, (i, j))

    def test_without_the_mask_the_first_row_changes(self):
        module = self.attention
        q = module.project(module.X, module.IDENTITY)
        k = module.project(module.X, module.IDENTITY)
        v = module.project(module.X, module.IDENTITY)
        causal, _ = module.attention(q, k, v, causal=True)
        future, rows = module.attention(q, k, v, causal=False)
        self.assertGreater(rows[0][1], 0.0)
        self.assertNotAlmostEqual(causal[0][0], future[0][0], places=3)

    def test_head_concat_keeps_one_value_per_head(self):
        module = self.attention
        concat = []
        for _name, wq, wk, wv in module.HEADS:
            out, _rows = module.attention(module.project(module.X, wq),
                                          module.project(module.X, wk),
                                          module.project(module.X, wv),
                                          causal=True)
            concat.append(out[0][0])
        self.assertEqual(len(concat), len(module.HEADS))

    def test_parameter_counts_and_kv_cache_are_exact(self):
        module = self.attention
        self.assertEqual(module.attention_params(4096, 32, 32)["total"],
                         67_108_864)
        self.assertEqual(module.attention_params(4096, 32, 8)["total"],
                         41_943_040)
        self.assertEqual(module.attention_params(4096, 32, 1)["total"],
                         34_603_008)
        self.assertEqual(module.kv_bytes_per_token(32, 32, 128), 524_288)
        self.assertEqual(module.kv_bytes_per_token(32, 8, 128), 131_072)
        self.assertEqual(module.kv_bytes_per_token(32, 1, 128), 16_384)

    def test_command_prints_weights_heads_and_params(self):
        output = run("attention_demo")
        self.assertIn("causal attention weights", output)
        self.assertIn("0.465", output)
        self.assertIn("0.535", output)
        self.assertIn("head 维度 0", output)
        self.assertIn("41,943,040", output)
        self.assertIn("16,384 B", output)


class TransformerExample(unittest.TestCase):
    def setUp(self):
        self.transformer = load("transformer_demo")

    def test_norms_center_or_scale_the_vector(self):
        module = self.transformer
        rms, scale = module.rms_norm(module.X0)
        self.assertEqual(len(rms), len(module.X0))
        self.assertAlmostEqual(module.norm(rms), 3 ** 0.5, places=5)
        self.assertGreater(scale, 0)
        centered, mean, _scale = module.layer_norm(module.X0)
        self.assertAlmostEqual(mean, 2.0)
        self.assertAlmostEqual(sum(centered), 0.0, places=6)
        self.assertAlmostEqual(
            sum(value * value for value in centered) / len(centered), 1.0,
            places=4)

    def test_zero_updates_leave_the_residual_stream_untouched(self):
        module = self.transformer
        zero = [0.0, 0.0, 0.0]
        self.assertEqual(module.block(module.X0, zero, zero), module.X0)

    def test_parameter_breakdown_matches_the_model_card(self):
        module = self.transformer
        counts = module.params(4096, 32, 32, 11008, 32000, True, False)
        self.assertEqual(counts["attention"], 67_108_864)
        self.assertEqual(counts["ffn"], 135_266_304)
        self.assertEqual(counts["per_layer"], 202_383_360)
        self.assertEqual(counts["total"], 6_738_411_520)
        tied = module.params(4096, 32, 32, 11008, 32000, True, True)
        self.assertEqual(counts["total"] - tied["total"], 131_072_000)

    def test_rope_dot_depends_on_the_offset(self):
        module = self.transformer
        query = [1.0, 0.0]
        key = [1.0, 0.0]
        import math
        for offset in range(4):
            value = module.dot(module.rope(query, offset),
                               module.rope(key, 0))
            self.assertAlmostEqual(value, math.cos(offset), places=6)
        self.assertAlmostEqual(
            module.dot(module.rope(query, 5), module.rope(key, 2)),
            module.dot(module.rope(query, 3), module.rope(key, 0)),
            places=6)

    def test_command_prints_params_and_rope_offsets(self):
        output = run("transformer_demo")
        self.assertIn("202,383,360", output)
        self.assertIn("6,738,411,520", output)
        self.assertIn("m-n=2: dot=-0.416", output)


class SamplingExample(unittest.TestCase):
    def setUp(self):
        self.sampling = load("sampling_demo")

    def test_softmax_is_a_distribution_and_temperature_sharpens_it(self):
        cold = self.sampling.softmax(self.sampling.LOGITS, 0.2)
        hot = self.sampling.softmax(self.sampling.LOGITS, 1.0)
        for dist in (cold, hot):
            self.assertAlmostEqual(sum(dist.values()), 1.0)
            self.assertTrue(all(value >= 0 for value in dist.values()))
        self.assertGreater(max(cold.values()), max(hot.values()))

    def test_filters_keep_a_renormalized_subset(self):
        dist = self.sampling.softmax(self.sampling.LOGITS, 1.0)
        for filtered in (self.sampling.top_k(dist, 3),
                         self.sampling.top_p(dist, 0.9)):
            self.assertLessEqual(len(filtered), len(dist))
            self.assertAlmostEqual(sum(filtered.values()), 1.0)
            self.assertTrue(set(filtered).issubset(dist))

    def test_top_p_keeps_at_least_one_token_and_rejects_bad_inputs(self):
        dist = self.sampling.softmax(self.sampling.LOGITS, 1.0)
        self.assertEqual(len(self.sampling.top_p(dist, 0.0001)), 1)
        with self.assertRaises(ValueError):
            self.sampling.softmax(self.sampling.LOGITS, 0)
        with self.assertRaises(ValueError):
            self.sampling.top_p(dist, 0)
        with self.assertRaises(ValueError):
            self.sampling.top_k(dist, 0)

    def test_same_seed_and_order_repeat(self):
        import random
        dist = self.sampling.top_p(self.sampling.softmax(self.sampling.LOGITS, 0.2), 0.9)
        first = [self.sampling.sample(dist, random.Random(11)) for _ in range(8)]
        second = [self.sampling.sample(dist, random.Random(11)) for _ in range(8)]
        self.assertEqual(first, second)

    def test_command_prints_both_temperatures(self):
        output = run("sampling_demo")
        self.assertIn("temperature=0.2", output)
        self.assertIn("temperature=1.0", output)
        self.assertIn("same seed", output)


class ContextExample(unittest.TestCase):
    def setUp(self):
        self.context = load("context_budget")

    def test_kv_cache_is_linear_and_attention_pairs_are_quadratic(self):
        per_token = self.context.kv_bytes_per_token(32, 8, 128, 2)
        self.assertEqual(per_token, 131_072)
        self.assertEqual(per_token * 32_768, 4 * 1024 ** 3)
        self.assertEqual(self.context.attention_pairs(4_096), 8_390_656)
        self.assertEqual(self.context.attention_pairs(32_768),
                         536_887_296)

    def test_default_budget_leaves_room_and_prints_costs(self):
        output = run("context_budget")
        self.assertIn("remaining        40,556 (OK)", output)
        self.assertIn("16.0 GiB", output)
        self.assertIn("$12.19", output)

    def test_over_budget_is_reported(self):
        env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        completed = subprocess.run(
            [sys.executable, str(EXAMPLES / "context_budget.py"),
             "--retrieved", "120000"],
            cwd=ROOT, env=env, check=True, capture_output=True, text=True,
            encoding="utf-8")
        self.assertIn("OVER BUDGET", completed.stdout)


class MultimodalExample(unittest.TestCase):
    def setUp(self):
        self.multimodal = load("multimodal_demo")

    def test_a_6x4_image_cuts_into_six_row_major_patches(self):
        module = self.multimodal
        blocks = module.patches(module.IMAGE, module.PATCH)
        self.assertEqual(len(blocks), 6)
        self.assertEqual(blocks[0][0], (0, 0))
        self.assertEqual(blocks[5][0], (1, 2))
        self.assertEqual(blocks[0][1], [10, 12, 11, 13])
        self.assertEqual(blocks[4][1], [40, 41, 42, 44])

    def test_projection_maps_each_patch_to_three_dims(self):
        module = self.multimodal
        token = module.project([10, 12, 11, 13])
        self.assertEqual(len(token), 3)
        self.assertAlmostEqual(token[0], 10 * 0.5 + 12 * 0.2 - 11 * 0.1,
                               places=9)
        bright = module.project([40, 41, 42, 44])
        dim = module.project([5, 4, 5, 6])
        self.assertGreater(max(bright), max(dim))

    def test_resolution_decides_the_budget_and_scaling_shrinks_it(self):
        module = self.multimodal
        self.assertEqual(module.direct_tokens(1920, 1080), 8160)
        self.assertEqual(module.direct_tokens(4032, 3024), 47628)
        scaled = module.resized(1920, 1080, 1568)
        self.assertEqual(scaled, (1568, 882))
        self.assertEqual(module.direct_tokens(*scaled), 5488)
        self.assertEqual(module.pixel_priced(*scaled), 1844)
        self.assertEqual(module.resized(2480, 3508, 1568), (1109, 1568))
        self.assertEqual(module.pixel_priced(1109, 1568), 2319)

    def test_detail_levels_differ_by_about_four_times(self):
        module = self.multimodal
        low = module.pixel_priced(*module.resized(1920, 1080, 768))
        high = module.pixel_priced(*module.resized(1920, 1080, 1568))
        self.assertEqual(low, 442)
        self.assertEqual(high, 1844)
        self.assertGreater(high / low, 4)

    def test_command_prints_patches_and_the_budget_table(self):
        output = run("multimodal_demo")
        self.assertIn("patches: 6 (row-major, 3 per row)", output)
        self.assertIn("8160", output)
        self.assertIn("47628", output)
        self.assertIn("1844", output)
        self.assertIn("low  (max edge 768)", output)
        self.assertIn("high (max edge 1568)", output)


if __name__ == "__main__":
    unittest.main()
