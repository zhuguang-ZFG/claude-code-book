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
    spec = importlib.util.spec_from_file_location(f"llm.examples.{name}", EXAMPLES / f"{name}.py")
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

    def test_overlapping_pairs_merge_left_to_right(self):
        self.assertEqual(self.bpe.apply([97, 97, 97], (97, 97), 256), [256, 97])
        self.assertEqual(self.bpe.apply([97] * 4, (97, 97), 256), [256, 256])
        self.assertEqual(self.bpe.apply([], (97, 97), 256), [])

    def test_encoding_uses_rank_before_pair_frequency(self):
        # 'ab' ranks before the more frequent 'bc'; merging it enables 'abc'.
        rules = [(97, 98), (256, 99), (98, 99)]
        self.assertEqual(self.bpe.encode('abcbcbc', rules), [257, 258, 258])
        self.assertEqual(self.bpe.encode('', rules), [])
        self.assertEqual(self.bpe.encode('x', rules), [120])

    def test_training_preserves_document_boundaries_and_tie_break(self):
        rules, _ = self.bpe.train(['a', 'b'], 2)
        self.assertEqual(rules, [])
        forward = self.bpe.train(['ab', 'bc'], 1)
        reverse = self.bpe.train(['bc', 'ab'], 1)
        self.assertEqual(forward, reverse)
        self.assertEqual(forward[0], [(97, 98)])

    def test_printed_walkthrough_matches_reused_encoder(self):
        import re
        chapter = (ROOT / "llm/ch01.md").read_text(encoding="utf-8")
        code = next(block for block in re.findall(r"```python\n(.*?)\n```", chapter, re.S)
                    if "def train(" in block)
        walkthrough = {}
        exec(compile(code, "llm/ch01.md", "exec"), walkthrough)
        for corpus in (self.bpe.CORPUS, ["aaaaa", "abcbcbc"], ["青禾🙂", "e\u0301"]):
            for count in (0, 8, 32):
                rules, vocab = self.bpe.train(corpus, count)
                self.assertEqual(walkthrough["train"](corpus, count), (rules, vocab))
                for sample in [*corpus, *self.bpe.SAMPLES, ""]:
                    with self.subTest(corpus=corpus, count=count, sample=sample):
                        self.assertEqual(walkthrough["encode"](sample, rules),
                                         self.bpe.encode(sample, rules))

    def test_unicode_and_partial_tokens_have_distinct_boundaries(self):
        rules, vocab = self.bpe.train(self.bpe.CORPUS, 32)
        for text in ("e\u0301", "𠮷", "👩\u200d💻"):
            self.assertEqual(self.bpe.decode(self.bpe.encode(text, rules), vocab), text)
        with self.assertRaises(UnicodeDecodeError):
            self.bpe.decode(self.bpe.encode("🙂", rules)[:1], vocab)

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

    def test_unmerged_and_merged_lora_agree_for_rectangular_weights(self):
        module = self.sft
        w = [[1.0, 0.0, -1.0], [0.0, 2.0, 0.0]]
        a, b = [[1.0, -2.0, 0.5]], [[0.5], [-1.0]]
        for x in ([1.0, 2.0, -1.0], [-2.0, 0.0, 3.0]):
            branch = module.lora_output(w, a, b, x, 2.0)
            merged = module.matvec(
                module.add(w, module.lora_delta(a, b, 2.0, 1)), x)
            for left, right in zip(branch, merged):
                self.assertAlmostEqual(left, right)
        self.assertEqual(module.lora_output(w, a, b, [1.0, 2.0, -1.0], 2.0),
                         [-1.5, 11.0])

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
    def test_losses_remain_finite_for_extreme_margins(self):
        import math
        module = load("alignment_demo")
        for margin in (-1000.0, 1000.0):
            loss, _ = module.bt_loss(margin, 0.0)
            self.assertTrue(math.isfinite(loss))
            self.assertAlmostEqual(loss, max(0.0, -margin))
        loss, margin = module.dpo_loss(-1000.0, 0.0, 0.0, 0.0, 1.0)
        self.assertEqual(margin, -1000.0)
        self.assertAlmostEqual(loss, 1000.0)

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
        chosen, rejected, gap = module.dpo_terms(-2.2, -2.5, -2.6, -2.4)
        self.assertAlmostEqual(chosen, 0.3)
        self.assertAlmostEqual(rejected, -0.2)
        self.assertAlmostEqual(gap, 0.5)
        loss, margin = module.dpo_loss(-2.2, -2.5, -2.6, -2.4, 0.1)
        self.assertAlmostEqual(margin, 0.05)
        self.assertAlmostEqual(loss, 0.668, places=3)
        loss, margin = module.dpo_loss(-2.2, -2.5, -2.6, -2.4, 1.0)
        self.assertAlmostEqual(margin, 0.5)
        self.assertAlmostEqual(loss, 0.474, places=3)

    def test_reversed_preference_has_a_higher_loss_and_beta_must_be_positive(self):
        module = self.alignment
        loss, margin = module.dpo_loss(-2.4, -2.5, -2.2, -2.6, 1.0)
        self.assertAlmostEqual(margin, -0.3)
        self.assertAlmostEqual(loss, 0.854, places=3)
        with self.assertRaises(ValueError):
            module.dpo_loss(-2.2, -2.5, -2.6, -2.4, 0)

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

    def test_rrf_keeps_document_versions_separate(self):
        module = self.rag
        chunks = module.filter_stale(module.build_chunks(module.DOCS), min_version=1)
        ids = [chunk["chunk_id"] for chunk in chunks]
        self.assertEqual(len(ids), len(set(ids)))
        fused = module.rrf([chunks, list(reversed(chunks))])
        self.assertEqual(len(fused), len(chunks))
        refunds = [chunk for chunk, _ in fused if chunk["id"] == "refund-policy"]
        self.assertEqual({chunk["version"] for chunk in refunds}, {1, 2})

    def test_lexical_and_vector_recall_disagree_then_rrf_fuses(self):
        module = self.rag
        chunks = module.dedupe(module.filter_stale(module.build_chunks(module.DOCS)))
        lexical = module.bm25(chunks, module.QUERY)
        semantic = module.vector_search(chunks, module.QUERY_VEC)
        self.assertEqual(lexical[0][0]["chunk_id"], "refund-faq@v2#0")
        self.assertEqual(semantic[0][0]["chunk_id"], "refund-policy@v2#0")
        fused = module.rrf([[row[0] for row in lexical],
                            [row[0] for row in semantic]])
        self.assertEqual(fused[0][0]["chunk_id"], "refund-policy@v2#0")
        reranked = module.rerank([row[0] for row in fused[:8]], module.QUERY)
        self.assertEqual(reranked[0][0]["chunk_id"], "refund-policy@v2#2")

    def test_command_prints_the_pipeline_and_top_hits(self):
        output = run("rag_demo")
        self.assertIn("raw chunks: 13", output)
        self.assertIn("after version filter + dedupe: 12", output)
        self.assertIn("refund-faq@v2#0", output)
        self.assertIn("refund-policy@v2#2", output)
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

    def test_non_object_arguments_fail_without_executing(self):
        for arguments in (None, [], "oops", 1001):
            with self.subTest(arguments=arguments):
                result = self.tool.call_tool("get_refund_status", arguments)
                self.assertTrue(result["isError"])
                self.assertIn("arguments must be an object", result["content"])
        for name in (None, [], {}, 1001):
            with self.subTest(name=name):
                result = self.tool.call_tool(name, {})
                self.assertTrue(result["isError"])
                self.assertIn("tool name must be a string", result["content"])
                response = self.tool.mcp_tool_response(11, name, {})
                self.assertEqual(response["error"]["code"], -32602)

    def test_declared_required_extra_enum_and_ascii_constraints(self):
        for name, arguments, message in (
            ("get_refund_status", {}, "missing required field"),
            ("get_refund_status", {"order_id": "ORD-1001", "user_id": "other"},
             "unexpected field"),
            ("create_ticket", {"order_id": "ORD-1001", "reason": "unknown"},
             "must be one of"),
            ("get_refund_status", {"order_id": "ORD-１００１"}, "does not match"),
        ):
            with self.subTest(name=name, arguments=arguments):
                result = self.tool.call_tool(name, arguments)
                self.assertTrue(result["isError"])
                self.assertIn(message, result["content"])

    def test_mcp_messages_have_the_expected_shape(self):
        module = self.tool
        messages = module.mcp_messages()
        requests, responses = messages[::2], messages[1::2]
        self.assertEqual([message["method"] for message in requests],
                         ["server/discover", "tools/list", "tools/call"])
        self.assertTrue(all(message["jsonrpc"] == "2.0" for message in messages))
        for request, response in zip(requests, responses):
            self.assertEqual(request["id"], response["id"])
            meta = request["params"]["_meta"]
            self.assertEqual(meta["io.modelcontextprotocol/protocolVersion"],
                             "2026-07-28")
            self.assertEqual(meta["io.modelcontextprotocol/clientCapabilities"], {})
            self.assertEqual(response["result"]["resultType"], "complete")
        advertised = responses[1]["result"]["tools"]
        self.assertEqual({tool["name"] for tool in advertised}, set(module.TOOLS))
        self.assertIn(requests[-1]["params"]["name"], module.TOOLS)
        self.assertFalse(responses[-1]["result"]["isError"])

    def test_mcp_protocol_errors_are_distinct_from_tool_failures(self):
        for name, arguments in (("absent", {}), ("get_refund_status", [])):
            response = self.tool.mcp_tool_response(9, name, arguments)
            self.assertEqual(response["id"], 9)
            self.assertEqual(response["error"]["code"], -32602)
            self.assertNotIn("result", response)
        for arguments in ({"order_id": 1001}, {"order_id": "ORD-9999"}):
            response = self.tool.mcp_tool_response(10, "get_refund_status", arguments)
            self.assertNotIn("error", response)
            self.assertTrue(response["result"]["isError"])
            self.assertEqual(response["result"]["content"][0]["type"], "text")

    def test_command_prints_validation_and_mcp(self):
        output = run("toolcall_demo")
        self.assertIn("get_refund_status: 183 chars", output)
        self.assertIn("create_ticket: 243 chars", output)
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
        with self.assertRaises(ValueError):
            module.majority_accuracy(0.6, 3, trials=0)

    def test_binary_majority_matches_enumerated_vote_outcomes(self):
        import itertools
        module = self.cot
        for p in (0.45, 0.5, 0.6, 0.75):
            for n in (1, 3, 5):
                expected = 0.0
                for votes in itertools.product((0, 1), repeat=n):
                    if sum(votes) > n // 2:
                        probability = 1.0
                        for vote in votes:
                            probability *= p if vote else 1 - p
                        expected += probability
                self.assertAlmostEqual(module.exact_majority_accuracy(p, n), expected)
                self.assertAlmostEqual(module.majority_accuracy(p, n, trials=20000),
                                       expected, delta=0.02)
        self.assertLess(module.exact_majority_accuracy(0.45, 15), 0.45)
        self.assertGreater(module.exact_majority_accuracy(0.6, 15), 0.6)

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

    def test_paired_evidence_differs_with_the_same_accuracy_totals(self):
        module = self.eval
        # Both tables have A=164 and B=172 out of 200, so their separate
        # Wilson intervals are identical. Their paired evidence differs.
        cases = ((164, 0, 8, 28), (144, 20, 28, 8))
        for both, a_only, b_only, neither in cases:
            self.assertEqual(both + a_only, 164)
            self.assertEqual(both + b_only, 172)
            self.assertEqual(both + a_only + b_only + neither, 200)
        self.assertEqual(module.mcnemar_exact(0, 8), 1 / 128)
        self.assertGreater(module.mcnemar_exact(20, 28), 0.05)

    def test_exact_paired_test_is_symmetric_and_handles_no_disagreements(self):
        module = self.eval
        self.assertEqual(module.mcnemar_exact(0, 0), 1.0)
        self.assertEqual(module.mcnemar_exact(4, 4), 1.0)
        self.assertEqual(module.mcnemar_exact(2, 6), 74 / 256)
        self.assertEqual(module.mcnemar_exact(2, 6), module.mcnemar_exact(6, 2))
        with self.assertRaises(ValueError):
            module.mcnemar_exact(-1, 2)

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
        self.assertIn("exact McNemar p", output)
        self.assertIn("0.0078", output)


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

    def test_cached_single_and_chunked_queries_match_full_attention(self):
        import random
        module = self.attention
        rng = random.Random(17)
        q = [[rng.uniform(-2, 2) for _ in range(3)] for _ in range(6)]
        k = [[rng.uniform(-2, 2) for _ in range(3)] for _ in range(6)]
        v = [[rng.uniform(-2, 2) for _ in range(2)] for _ in range(6)]
        full, _ = module.attention(q, k, v)
        for chunk in (1, 2, 3):
            cached = []
            for start in range(0, len(q), chunk):
                stop = start + chunk
                result, rows = module.attention(q[start:stop], k[:stop], v[:stop],
                                                query_start=start)
                cached.extend(result)
                for offset, row in enumerate(rows):
                    self.assertTrue(all(w == 0 for w in row[start + offset + 1:]))
            for actual, expected in zip(cached, full):
                for a, b in zip(actual, expected):
                    self.assertAlmostEqual(a, b, places=12)

    def test_decode_query_position_must_not_reset_to_zero(self):
        module = self.attention
        correct, _ = module.attention(module.X[-1:], module.X, module.X, query_start=2)
        wrong, _ = module.attention(module.X[-1:], module.X, module.X)
        self.assertEqual(wrong, [[1.0, 0.0]])
        self.assertAlmostEqual(correct[0][0], 0.488, places=3)
        self.assertAlmostEqual(correct[0][1], 0.646, places=3)

    def test_shape_mismatches_do_not_silently_truncate_vectors(self):
        module = self.attention
        for q, k, v in [([], [[1]], [[1]]), ([[1, 2]], [[1]], [[1]]),
                        ([[1]], [[1], [2]], [[1]]),
                        ([[1]], [[1], [2]], [[1], [2, 3]])]:
            with self.subTest(q=q, k=k, v=v), self.assertRaises(ValueError):
                module.attention(q, k, v)
        for start in (-1, 0.5, 3):
            with self.subTest(start=start), self.assertRaises(ValueError):
                module.attention([[1]], [[1]], [[1]], query_start=start)
        for config in ((0, 1, 1), (8, 0, 1), (10, 3, 1), (8, 4, 3), (8, 2, 4)):
            with self.subTest(config=config), self.assertRaises(ValueError):
                module.attention_params(*config)

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
        self.assertIn("base=10000, m-n=10: dot=+0.156", output)
        self.assertIn("base=100, m-n=10: dot=-0.299", output)

    def test_rope_base_exercise_needs_a_second_coordinate_pair(self):
        module = self.transformer
        two_dim = [1.0, 0.0]
        self.assertEqual(module.rope(two_dim, 10, 10000),
                         module.rope(two_dim, 10, 100))
        four_dim = [1.0, 0.0, 1.0, 0.0]
        # The worked example has angles 10 and 0.1, or 10 and 1 radians.
        import math
        for base, second_angle in ((10000, 0.1), (100, 1.0)):
            expected = math.cos(10) + math.cos(second_angle)
            value = module.dot(module.rope(four_dim, 10, base), four_dim)
            self.assertAlmostEqual(value, expected)

    def test_rope_shift_invariance_does_not_remove_content_dependence(self):
        module = self.transformer
        query = [0.4, -1.2, 0.7, 2.0]
        key = [1.3, 0.5, -0.8, 0.1]
        for base in (100, 10000):
            value = module.dot(module.rope(query, 10, base),
                               module.rope(key, 0, base))
            shifted = module.dot(module.rope(query, 17, base),
                                 module.rope(key, 7, base))
            self.assertAlmostEqual(value, shifted)
            changed_content = module.dot(
                module.rope([-x for x in query], 10, base),
                module.rope(key, 0, base))
            self.assertNotAlmostEqual(value, changed_content)


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
        dist = self.sampling.top_p(self.sampling.softmax(self.sampling.LOGITS, 1.0), 0.9)
        first = self.sampling.sample_sequence(dist, 11, 8)
        second = self.sampling.sample_sequence(dist, 11, 8)
        self.assertEqual(first, second)
        self.assertGreater(len(set(first)), 1)
        # Independent inverse-CDF oracle, one random stream for the whole run.
        rng = random.Random(11)
        ordered = sorted(dist.items(), key=lambda item: item[1], reverse=True)
        expected = []
        for _ in range(8):
            draw, total = rng.random(), 0.0
            for token, probability in ordered:
                total += probability
                if draw < total:
                    expected.append(token)
                    break
        self.assertEqual(first, expected)

    def test_softmax_handles_extreme_temperature_and_tied_maxima(self):
        import math
        for t in (1e-320, 1e308):
            probs = self.sampling.softmax({"a": 1e308, "b": -1e308}, t)
            self.assertAlmostEqual(sum(probs.values()), 1)
            self.assertTrue(all(math.isfinite(v) for v in probs.values()))
        hot = self.sampling.softmax({"a": 1e308, "b": -1e308}, 1e308)
        self.assertAlmostEqual(hot["a"], 1 / (1 + math.exp(-2)))
        tied = self.sampling.softmax({"a": 800.0, "b": 800.0, "c": 0.0}, 1e-320)
        self.assertEqual(tied, {"a": 0.5, "b": 0.5, "c": 0.0})
        for t in (float("nan"), float("inf"), -1):
            with self.assertRaises(ValueError):
                self.sampling.softmax({"a": 0.0}, t)

    def test_sampler_respects_zero_mass_and_interval_boundaries(self):
        from unittest.mock import Mock
        # Half-open CDF intervals: the exact boundary belongs to the next token.
        rng = Mock()
        rng.random.return_value = 0.5
        self.assertEqual(self.sampling.sample({"a": 0.5, "b": 0.5, "zero": 0}, rng), "b")
        rng.random.return_value = 0.9999999999999999
        self.assertEqual(self.sampling.sample({"b": 0.2, "a": 0.8, "zero": 0}, rng), "b")
        for dist in ({}, {"a": 0}, {"a": -1}, {"a": float("nan")}):
            with self.assertRaises(ValueError):
                self.sampling.sample(dist, rng)

    def test_top_p_is_smallest_descending_prefix_at_threshold(self):
        dist = {"c": 0.2, "a": 0.5, "b": 0.3}
        self.assertEqual(set(self.sampling.top_p(dist, 0.5)), {"a"})
        self.assertEqual(set(self.sampling.top_p(dist, 0.8)), {"a", "b"})
        self.assertEqual(set(self.sampling.top_p(dist, 1.0)), set(dist))

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

    def test_zero_calls_has_zero_bill_and_negative_inputs_are_rejected(self):
        command = [sys.executable, str(EXAMPLES / "context_budget.py")]
        zero = subprocess.run(command + ["--calls", "0"], capture_output=True, text=True)
        self.assertEqual(zero.returncode, 0)
        self.assertIn("$0.00", zero.stdout)
        for args in (["--retrieved", "-1"], ["--layers", "0"],
                     ["--price-per-million", "nan"]):
            result = subprocess.run(command + args, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)


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

    def test_partial_patches_are_zero_padded_and_match_grid_count(self):
        module = self.multimodal
        image = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        blocks = module.patches(image, 2)
        self.assertEqual(len(blocks), module.patch_grid_count(3, 3, 2))
        self.assertEqual(blocks, [((0, 0), [1, 2, 4, 5]),
                                  ((0, 1), [3, 0, 6, 0]),
                                  ((1, 0), [7, 8, 0, 0]),
                                  ((1, 1), [9, 0, 0, 0])])
        for _, block in blocks:
            self.assertEqual(len(module.project(block)), 3)

    def test_resize_caps_dimensions_without_upscaling_or_zero_edges(self):
        module = self.multimodal
        self.assertEqual(module.resized(640, 480, 1568), (640, 480))
        self.assertEqual(module.resized(1, 10000, 768), (1, 768))
        for width, height, cap in ((1920, 1080, 768), (1080, 1920, 768)):
            small = module.resized(width, height, cap)
            self.assertLessEqual(max(small), cap)
            self.assertLessEqual(small[0], width)
            self.assertLessEqual(small[1], height)

    def test_mismatched_projection_and_invalid_image_shapes_are_rejected(self):
        module = self.multimodal
        for block in ([1, 2, 3], [1] * 9):
            with self.assertRaises(ValueError):
                module.project(block)
        for image, size in (([], 2), ([[1], [1, 2]], 2), ([[1]], 0)):
            with self.assertRaises(ValueError):
                module.patches(image, size)

    def test_resolution_decides_the_budget_and_scaling_shrinks_it(self):
        module = self.multimodal
        self.assertEqual(module.patch_grid_count(1920, 1080), 8160)
        self.assertEqual(module.patch_grid_count(4032, 3024), 47628)
        scaled = module.resized(1920, 1080, 1568)
        self.assertEqual(scaled, (1568, 882))
        self.assertEqual(module.patch_grid_count(*scaled), 5488)
        self.assertEqual(module.area_units(*scaled), 1844)
        self.assertEqual(module.resized(2480, 3508, 1568), (1109, 1568))
        self.assertEqual(module.area_units(1109, 1568), 2319)

    def test_teaching_resize_settings_differ_by_about_four_times(self):
        module = self.multimodal
        low = module.area_units(*module.resized(1920, 1080, 768))
        high = module.area_units(*module.resized(1920, 1080, 1568))
        self.assertEqual(low, 442)
        self.assertEqual(high, 1844)
        self.assertGreater(high / low, 4)

    def test_command_prints_patches_and_the_budget_table(self):
        output = run("multimodal_demo")
        self.assertIn("patches: 6 (row-major, 3 per row)", output)
        self.assertIn("8160", output)
        self.assertIn("47628", output)
        self.assertIn("1844", output)
        self.assertIn("A (max edge 768)", output)
        self.assertIn("B (max edge 1568)", output)


class TrainExample(unittest.TestCase):
    def setUp(self):
        self.module = load("train_demo")

    def _trained(self, seed: int):
        import random
        model = self.module.Tiny(len(self.module.VOCAB), random.Random(seed))
        history = self.module.train(model, random.Random(seed))
        return model, history

    def test_backprop_matches_numeric_gradients(self):
        import random
        model = self.module.Tiny(len(self.module.VOCAB), random.Random(1))
        probe = self.module.IDS[:self.module.N_CTX]
        targets = self.module.IDS[1:self.module.N_CTX + 1]
        worst = self.module.gradcheck(model, probe, targets, random.Random(2))
        self.assertLess(worst, 1e-4)

    def test_all_backprop_parameters_on_small_nonsymmetric_models(self):
        import random
        from unittest.mock import patch

        module = self.module
        # Larger, nonsymmetric weights expose transposed-Jacobian mistakes
        # that tiny attention gradients can hide under an absolute tolerance.
        with patch.multiple(module, D_MODEL=4, D_FF=6, N_CTX=4):
            for seed in (7, 17):
                model = module.Tiny(6, random.Random(seed))
                for weight in model.params().values():
                    for row in weight:
                        for j in range(len(row)):
                            row[j] *= 10
                # Repeated token IDs also exercise accumulated embedding grads.
                ids, targets = [0, 1, 0, 2], [1, 0, 2, 3]
                _loss, grads = model.loss_and_grads(ids, targets)
                epsilon = 1e-5
                for name, weight in model.params().items():
                    for i, row in enumerate(weight):
                        for j, original in enumerate(row):
                            with self.subTest(seed=seed, tensor=name, row=i, col=j):
                                try:
                                    row[j] = original + epsilon
                                    plus = model.loss(ids, targets)
                                    row[j] = original - epsilon
                                    minus = model.loss(ids, targets)
                                finally:
                                    row[j] = original
                                numeric = (plus - minus) / (2 * epsilon)
                                self.assertAlmostEqual(
                                    grads[name][i][j], numeric, delta=1e-7)

    def test_the_loss_actually_drops(self):
        model, history = self._trained(self.module.SEED)
        first = history[0][1]
        final = model.loss(self.module.IDS[:self.module.N_CTX],
                           self.module.IDS[1:self.module.N_CTX + 1])
        self.assertGreater(first, 3.0)      # ~ln(vocab) at the start
        self.assertLess(final, 2.0)        # learned the corpus patterns
        for _step, loss in history[1:]:
            self.assertLess(loss, first)

    def test_training_is_reproducible(self):
        _first_model, first = self._trained(self.module.SEED)
        _second_model, second = self._trained(self.module.SEED)
        self.assertEqual(first, second)

    def test_generate_keeps_the_prompt_and_the_vocab(self):
        model, _history = self._trained(self.module.SEED)
        sample = self.module.generate(model, "青禾工作坊", 8)
        self.assertTrue(sample.startswith("青禾工作坊"))
        self.assertEqual(len(sample), len("青禾工作坊") + 8)
        for ch in sample:
            self.assertIn(ch, self.module.VOCAB)

    def test_command_prints_the_training_curve(self):
        output = run("train_demo")
        self.assertIn("gradcheck", output)
        self.assertIn("loss before training", output)
        self.assertIn("step 240", output)
        self.assertIn("loss after training", output)
        self.assertIn("greedy sample", output)


class EmbeddingTrainExample(unittest.TestCase):
    def setUp(self):
        self.module = load("embedding_train_demo")

    def test_sigmoid_and_softplus_survive_extreme_scores(self):
        module = self.module
        self.assertEqual(module.sigmoid(1000.0), 1.0)
        self.assertEqual(module.sigmoid(-1000.0), 0.0)
        self.assertAlmostEqual(module.softplus(1000.0), 1000.0)
        self.assertEqual(module.softplus(-1000.0), 0.0)

    def test_pairs_stay_inside_the_window(self):
        module = self.module
        ids = list(range(8))
        found = module.pairs(ids)
        # positions 0 and 7 keep 2 neighbours, 1 and 6 keep 3, the rest 4
        self.assertEqual(len(found), 2 + 3 + 4 * 4 + 3 + 2)
        for center, context in found:
            self.assertNotEqual(center, context)
            self.assertIn(abs(center - context), (1, 2))

    def test_training_groups_words_by_topic(self):
        import random
        vec, _initial, _history = self.module.train(
            random.Random(self.module.SEED))
        hits = 0
        for index, word in enumerate(self.module.VOCAB):
            scored = [(self.module.cosine(vec[index], vec[j]),
                       self.module.VOCAB[j])
                      for j in range(len(vec)) if j != index]
            scored.sort(reverse=True)
            topics = {self.module.TOPIC[other] for _s, other in scored[:3]}
            hits += self.module.TOPIC[word] in topics
        self.assertEqual(hits, len(self.module.VOCAB))

    def test_training_is_reproducible(self):
        import random
        _v1, _i1, h1 = self.module.train(random.Random(self.module.SEED))
        _v2, _i2, h2 = self.module.train(random.Random(self.module.SEED))
        self.assertEqual(h1, h2)

    def test_command_prints_before_and_after_neighbours(self):
        output = run("embedding_train_demo")
        self.assertIn("pair loss", output)
        self.assertIn("own topic: 12/12", output)
        self.assertIn("before:", output)
        self.assertIn("after :", output)


class RejectionExample(unittest.TestCase):
    def setUp(self):
        self.module = load("rejection_demo")

    def test_verifier_is_exact_match(self):
        module = self.module
        prompt = next(iter(module.PROMPTS))
        self.assertTrue(module.passes(module.PROMPTS[prompt], prompt))
        self.assertFalse(module.passes("#error", prompt))

    def test_rejection_round_counts_stay_in_bounds(self):
        module = self.module
        attempts, kept, hit = module.rejection_round(
            module.P_CORRECT, 16, __import__("random").Random(module.SEED))
        self.assertEqual(attempts, 16 * len(module.PROMPTS))
        self.assertLessEqual(kept, attempts)
        self.assertLessEqual(hit, len(module.PROMPTS))

    def test_more_candidates_solve_more_prompts(self):
        module = self.module
        import random
        small = module.best_of_n(
            module.P_CORRECT, 4, random.Random(module.SEED))
        big = module.best_of_n(
            module.P_CORRECT, 64, random.Random(module.SEED))
        self.assertGreaterEqual(big, small)
        self.assertEqual(big, len(module.PROMPTS))
        self.assertGreaterEqual(small, 0)

    def test_sampling_respects_zero_and_one_success_probabilities(self):
        module = self.module
        import random
        for prompt in module.PROMPTS:
            for probability in (0.0, 1.0):
                draws = module.sample_n(prompt, 8, random.Random(11), probability)
                self.assertEqual(len(draws), 8)
                self.assertTrue(all(module.passes(x, prompt) == bool(probability)
                                    for x in draws))

    def test_command_prints_filter_and_loop(self):
        output = run("rejection_demo")
        self.assertIn("rejection sampling", output)
        self.assertIn("best-of-N at inference", output)
        self.assertIn("p stays fixed", output)
        self.assertIn("P(at least one pass)", output)


class SessionLedgerExample(unittest.TestCase):
    def setUp(self):
        self.module = load("session_ledger")

    def test_prompts_grow_by_output_plus_tool_result(self):
        module = self.module
        prompts = module.turn_prompts()
        growth = module.OUTPUT_TOKENS[0] + module.TOOL_TOKENS
        for before, after in zip(prompts, prompts[1:]):
            self.assertEqual(after - before, growth)
        self.assertEqual(prompts[0], module.SYSTEM_TOKENS + module.TASK_TOKENS
                         + module.DOCS * module.DOC_TOKENS)

    def test_cached_tokens_are_cheaper_than_fresh_ones(self):
        module = self.module
        fresh, _ = module.cost(1000, 0, 0)
        cached, _ = module.cost(1000, 1000, 0)
        self.assertLess(cached, fresh)
        self.assertAlmostEqual(cached / fresh, module.PRICE_CACHED
                               / module.PRICE_INPUT)

    def test_prefix_caching_never_costs_more(self):
        module = self.module
        none = module.run("no cache")["bill"]
        stable = module.run("stable prefix")["bill"]
        append = module.run("append-only prefix")["bill"]
        self.assertLess(stable, none)
        self.assertLess(append, stable)

    def test_bill_equals_the_sum_of_turns(self):
        module = self.module
        result = module.run("append-only prefix")
        per_turn = sum(row["input_cost"] + row["output_cost"]
                       for row in result["rows"])
        self.assertAlmostEqual(result["bill"], per_turn, places=12)
        self.assertAlmostEqual(result["input_cost"],
                               sum(row["input_cost"] for row in result["rows"]),
                               places=12)

    def test_input_categories_separate_tool_results_from_assistant_history(self):
        categories = self.module.input_categories()
        self.assertEqual(categories["tool results"], 4_800)
        self.assertEqual(categories["assistant history"], 1_500)
        self.assertEqual(sum(categories.values()), sum(self.module.turn_prompts()))

    def test_command_prints_the_three_strategies(self):
        output = run("session_ledger")
        self.assertIn("what the model sees on each turn", output)
        self.assertIn("no cache", output)
        self.assertIn("stable prefix", output)
        self.assertIn("append-only prefix", output)
        self.assertIn("input tokens are fresh", output)
        self.assertIn("KV cache at peak context", output)


class AnnExample(unittest.TestCase):
    def setUp(self):
        self.module = load("ann_demo")

    def test_flat_search_returns_k_sorted_neighbours(self):
        module = self.module
        import random
        rng = random.Random(module.SEED)
        points, _labels = module.build_corpus(rng)
        query = points[0]
        answer = module.nearest(query, points, module.K)
        self.assertEqual(len(answer), module.K)
        distances = [module.distance(query, points[i]) for i in answer]
        self.assertEqual(distances, sorted(distances))

    def test_buckets_partition_the_corpus_exactly_once(self):
        module = self.module
        import random
        rng = random.Random(module.SEED)
        points, _labels = module.build_corpus(rng)
        centroids = module.kmeans(points, module.CLUSTERS, rng)
        buckets = module.assign(points, centroids)
        flattened = [index for bucket in buckets for index in bucket]
        self.assertEqual(sorted(flattened), list(range(len(points))))

    def test_full_probe_equals_flat_search(self):
        module = self.module
        import random
        rng = random.Random(module.SEED)
        points, _labels = module.build_corpus(rng)
        centroids = module.kmeans(points, module.CLUSTERS, rng)
        buckets = module.assign(points, centroids)
        for query in points[:5]:
            found, _count = module.ivf_search(
                query, points, buckets, centroids, module.CLUSTERS)
            self.assertEqual(found, module.nearest(query, points, module.K))

    def test_more_probes_never_reduce_recall(self):
        module = self.module
        import random
        rng = random.Random(module.SEED)
        points, _labels = module.build_corpus(rng)
        centroids = module.kmeans(points, module.CLUSTERS, rng)
        buckets = module.assign(points, centroids)
        queries = points[::37][:8]
        exact = [module.nearest(q, points, module.K) for q in queries]
        previous = -1.0
        for nprobe in (1, 2, 4, 8):
            hits = 0.0
            for query, answer in zip(queries, exact):
                found, _count = module.ivf_search(
                    query, points, buckets, centroids, nprobe)
                hits += len(set(found) & set(answer)) / module.K
            recall = hits / len(queries)
            self.assertGreaterEqual(recall, previous)
            previous = recall

    def test_command_prints_the_tradeoff(self):
        output = run("ann_demo")
        self.assertIn("recall@10", output)
        self.assertIn("bucket map", output)
        self.assertIn("worst nprobe=1 query", output)


class RetrievalMetricsExample(unittest.TestCase):
    def setUp(self):
        self.module = load("retrieval_metrics")

    def test_ideal_ranking_scores_one(self):
        module = self.module
        grades = {"a": 2, "b": 1, "c": 0}
        ideal = ["a", "b", "c"]
        self.assertEqual(module.recall_at_k(ideal, grades, 3), 1.0)
        self.assertEqual(module.ndcg_at_k(ideal, grades, 3), 1.0)
        self.assertEqual(module.average_precision(ideal, grades, 3), 1.0)
        self.assertEqual(module.reciprocal_rank(ideal, grades), 1.0)

    def test_ndcg_punishes_a_buried_best_answer(self):
        module = self.module
        grades = {"a": 2, "b": 2, "c": 0}
        good = module.ndcg_at_k(["a", "b", "c"], grades, 3)
        bad = module.ndcg_at_k(["c", "b", "a"], grades, 3)
        self.assertGreater(good, bad)

    def test_recall_ignores_order(self):
        module = self.module
        grades = {"a": 2, "b": 1, "c": 0}
        self.assertEqual(module.recall_at_k(["c", "a", "b"], grades, 3),
                         module.recall_at_k(["a", "b", "c"], grades, 3))

    def test_mrr_reports_the_first_hit_position(self):
        module = self.module
        grades = {"a": 0, "b": 0, "c": 1}
        self.assertAlmostEqual(module.reciprocal_rank(["a", "b", "c"], grades),
                               1 / 3)

    def test_command_prints_both_rankers(self):
        output = run("retrieval_metrics")
        self.assertIn("keyword", output)
        self.assertIn("vector", output)
        self.assertIn("recall@3", output)
        self.assertIn("NDCG@3", output)


if __name__ == "__main__":
    unittest.main()
