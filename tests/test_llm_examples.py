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


if __name__ == "__main__":
    unittest.main()
