"""Offline prompt A/B runner: no network, no score inflation, hard call cap."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "prompt/examples"
sys.path.insert(0, str(EXAMPLES))
import lab
import model_run
sys.path.remove(str(EXAMPLES))


def lock(**overrides):
    value = {"model_id": "reader-chosen", "model_card_date": "2026-11-18",
             "temperature": 0, "top_p": None, "seed_policy": "required",
             "seed": 7, "max_output_tokens": 512, "repeats": 2}
    value.update(overrides)
    return value


class Prepared(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name) / "experiment"

    def prepare(self, repeats=2):
        lab.prepare(self.folder, "validation", repeats,
                    "synthetic unit-test fixtures; no model")
        return self.folder


class DryRun(Prepared):
    def test_dry_run_prints_the_formula_and_sends_nothing(self):
        self.prepare(repeats=2)
        result = model_run.dry_run(self.folder, lock(), max_calls=28)
        self.assertEqual(result["planned_requests"], 28)
        self.assertEqual(result["executed_model_calls"], 0)
        self.assertEqual(result["status"], "offline")

    def test_holdout_is_eight_not_twenty_eight(self):
        lab.prepare(self.folder, "holdout", 2, "synthetic unit-test fixtures; no model")
        result = model_run.dry_run(self.folder, lock(), max_calls=8)
        self.assertEqual(result["planned_requests"], 8)
        self.assertEqual(result["executed_model_calls"], 0)

    def test_invalid_lock_and_over_budget_send_nothing(self):
        self.prepare(repeats=2)
        calls = []

        def transport(slot, request, chosen):
            calls.append(slot)
            return {"kind": "ok", "body": "{}"}

        with self.assertRaises(ValueError):
            model_run.run_online(self.folder, lock(seed_policy="required", seed=None),
                                 28, transport)
        self.assertEqual(calls, [])
        refused = model_run.run_online(self.folder, lock(), 27, transport)
        self.assertEqual(refused["status"], "refused_over_budget")
        self.assertEqual(refused["executed_model_calls"], 0)
        self.assertEqual(calls, [])


class Online(Prepared):
    def test_missing_transport_raises_before_any_call(self):
        self.prepare(repeats=1)
        with self.assertRaises(ValueError):
            model_run.run_online(self.folder, lock(repeats=1), 14, None)

    def test_unsupported_parameter_counts_once_and_stops(self):
        self.prepare(repeats=1)
        seen = []

        def transport(slot, request, chosen):
            seen.append(dict(chosen))
            return {"kind": "unsupported_parameter", "detail": "seed is not supported"}

        result = model_run.run_online(self.folder, lock(repeats=1), 14, transport)
        self.assertEqual(len(seen), 1)
        self.assertEqual(seen[0]["seed"], 7)
        self.assertEqual(result["executed_model_calls"], 1)
        self.assertEqual(result["status"], "blocked_unsupported_parameter")
        responses = list(self.folder.glob("*/response.txt"))
        self.assertEqual(responses, [])

    def test_retries_cannot_exceed_max_calls(self):
        self.prepare(repeats=1)
        calls = []

        def transport(slot, request, chosen):
            calls.append(slot)
            return {"kind": "transport_error", "detail": "connection reset"}

        result = model_run.run_online(self.folder, lock(repeats=1), 14, transport)
        self.assertEqual(len(calls), 14)
        self.assertEqual(result["executed_model_calls"], 14)
        attempts = json.loads((self.folder / calls[0] / "attempts.json").read_text(encoding="utf-8"))
        self.assertLessEqual(len(attempts), 3)
        self.assertEqual(sum(len(json.loads(path.read_text(encoding="utf-8")))
                             for path in self.folder.glob("*/attempts.json")), 14)

    def test_one_slot_stops_after_three_transport_errors(self):
        self.prepare(repeats=1)
        per_slot = []

        def transport(slot, request, chosen):
            per_slot.append(slot)
            if slot == per_slot[0] and per_slot.count(slot) <= 3:
                return {"kind": "transport_error", "detail": "timeout"}
            return {"kind": "ok", "body": "{}"}

        model_run.run_online(self.folder, lock(repeats=1), 20, transport)
        first = per_slot[0]
        self.assertEqual(per_slot.count(first), 3)
        self.assertFalse((self.folder / first / "response.txt").exists())

    def test_refusal_is_a_response_not_a_pass(self):
        self.prepare(repeats=1)

        def transport(slot, request, chosen):
            return {"kind": "refusal_text", "body": "我不能完成这个请求"}

        result = model_run.run_online(self.folder, lock(repeats=1), 14, transport)
        self.assertEqual(result["executed_model_calls"], 14)
        sample = next(self.folder.glob("*/response.txt"))
        self.assertEqual(sample.read_text(encoding="utf-8"), "我不能完成这个请求")
        with self.assertRaises(ValueError):
            lab.review(self.folder, sample.parent.name, "pass", "refusal is not a pass")
        compared = lab.compare(self.folder)
        self.assertIsNone(compared["pass_count_delta_b_minus_a"])

    def test_public_summary_drops_secrets_and_answer_text(self):
        self.prepare(repeats=1)

        def transport(slot, request, chosen):
            return {"kind": "ok", "body": "sk-secret answer",
                    "detail": "Authorization: Bearer sk-secret"}

        result = model_run.run_online(self.folder, lock(repeats=1), 14, transport)
        blob = json.dumps(model_run.public_summary(self.folder, result), ensure_ascii=False)
        self.assertNotIn("sk-secret", blob)
        self.assertNotIn("Bearer", blob)
        self.assertNotIn("answer", blob.lower())
        stored = (self.folder / result["slots"][0]["slot"] / "attempts.json").read_text(encoding="utf-8")
        self.assertNotIn("sk-secret", stored)


class ChapterBoundary(unittest.TestCase):
    def test_chapter_sixteen_still_says_the_model_comparison_has_not_run(self):
        text = (ROOT / "prompt/ch16.md").read_text(encoding="utf-8")
        self.assertIn("新册模型对照还未运行", text)
        self.assertIn("计划请求数 = 题目数 × 2 × 重复次数", text)
        self.assertIn("字符数不是 token 数", text)

    def test_model_chapter_explains_sampling_without_a_new_volume(self):
        text = (ROOT / "omp/ch02.md").read_text(encoding="utf-8")
        self.assertIn("温度", text)
        self.assertIn("../prompt/ch16.md", text)


class CommandLine(Prepared):
    def test_online_flag_does_not_open_a_real_client(self):
        self.prepare(repeats=1)
        source = (EXAMPLES / "model_run.py").read_text(encoding="utf-8")
        self.assertNotIn("os.environ", source)
        self.assertNotIn("socket", source)
        completed = subprocess.run(
            [sys.executable, str(EXAMPLES / "model_run.py"), "run",
             str(self.folder), "--online", "--max-calls", "14"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(completed.returncode, 2)
        self.assertIn("executed_model_calls", completed.stdout + completed.stderr)
        self.assertIn("0", completed.stdout + completed.stderr)

    def test_default_command_stays_offline(self):
        self.prepare(repeats=1)
        completed = subprocess.run(
            [sys.executable, str(EXAMPLES / "model_run.py"), "run", str(self.folder),
             "--max-calls", "14"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["executed_model_calls"], 0)
        self.assertEqual(payload["status"], "offline")


if __name__ == "__main__":
    unittest.main()
