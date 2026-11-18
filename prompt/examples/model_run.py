"""Record a frozen prompt A/B plan without calling a model by default.

A real provider client is intentionally absent. Tests pass a fake transport.
This module does not read the process environment.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import lab

_SECRET = re.compile(
    r"(?i)bearer\s+\S+|sk-[A-Za-z0-9_\-]+|(?:api[_-]?key|authorization)\s*[:=]\s*\S+")


def redact(text):
    if not isinstance(text, str):
        return ""
    return _SECRET.sub("[redacted]", text)


def load_lock(lock):
    if not isinstance(lock, dict):
        raise ValueError("Sampling lock must be an object")
    required = {"model_id", "model_card_date", "temperature", "top_p",
                "seed_policy", "max_output_tokens", "repeats"}
    if not required <= set(lock):
        raise ValueError("Sampling lock is missing a field")
    if not isinstance(lock["model_id"], str) or not lock["model_id"].strip():
        raise ValueError("model_id is required")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(lock["model_card_date"])):
        raise ValueError("model_card_date must be YYYY-MM-DD")
    for name in ("temperature", "top_p"):
        if lock[name] is not None and type(lock[name]) not in (int, float):
            raise ValueError(f"{name} must be a number or null")
    if lock["seed_policy"] not in ("required", "unavailable"):
        raise ValueError("seed_policy must be required or unavailable")
    if type(lock["repeats"]) is not int or lock["repeats"] < 1:
        raise ValueError("repeats must be a positive integer")
    if type(lock["max_output_tokens"]) is not int or lock["max_output_tokens"] < 1:
        raise ValueError("max_output_tokens must be a positive integer")
    if lock["seed_policy"] == "required":
        if type(lock.get("seed")) is not int:
            raise ValueError("A required seed must be an integer")
    return lock


def plan_size(plan):
    return len(plan["runs"])


def _planned(folder, lock):
    chosen = load_lock(lock)
    plan = lab.load_plan(Path(folder))
    if chosen["repeats"] != plan["repeats"]:
        raise ValueError("Sampling lock repeats do not match the frozen plan")
    return plan, chosen, plan_size(plan)


def _budget(max_calls):
    if type(max_calls) is not int or max_calls < 0:
        raise ValueError("max_calls must be a non-negative integer")
    return max_calls


def dry_run(folder, lock, max_calls):
    _plan, _chosen, planned = _planned(folder, lock)
    limit = _budget(max_calls)
    status = "refused_over_budget" if planned > limit else "offline"
    return {"planned_requests": planned, "executed_model_calls": 0,
            "status": status, "slots": []}


def _stamp():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_online(folder, lock, max_calls, transport):
    folder = Path(folder)
    plan, chosen, planned = _planned(folder, lock)
    limit = _budget(max_calls)
    if transport is None:
        raise ValueError("Online run requires an injected transport")
    if planned > limit:
        return {"planned_requests": planned, "executed_model_calls": 0,
                "status": "refused_over_budget", "slots": []}
    executed = 0
    slots = []
    status = "responses_received"

    def call(slot, request):
        nonlocal executed
        if executed >= limit:
            return None
        executed += 1
        raw = transport(slot, request, chosen)
        if not isinstance(raw, dict):
            raw = {"kind": "transport_error", "detail": "malformed transport result"}
        kind = raw.get("kind")
        if kind not in ("ok", "refusal_text", "unsupported_parameter", "transport_error"):
            kind = "transport_error"
        return {"kind": kind, "body": raw.get("body"),
                "detail": redact(raw.get("detail") or ""),
                "started_at": _stamp(), "ended_at": _stamp()}

    for run in plan["runs"]:
        if executed >= limit:
            status = "stopped_at_call_cap"
            break
        slot = run["slot"]
        request = (folder / slot / "request.txt").read_bytes()
        attempts = []
        errors = 0
        while True:
            attempt = call(slot, request)
            if attempt is None:
                status = "stopped_at_call_cap"
                break
            attempts.append({key: attempt[key] for key in
                             ("kind", "detail", "started_at", "ended_at")})
            kind = attempt["kind"]
            if kind == "unsupported_parameter":
                status = "blocked_unsupported_parameter"
                break
            if kind == "transport_error":
                errors += 1
                if errors >= 3:
                    break
                continue
            body = attempt["body"] if isinstance(attempt["body"], str) else ""
            (folder / slot / "response.txt").write_text(body, encoding="utf-8")
            break
        if attempts:
            lab.write_json(folder / slot / "attempts.json", attempts)
        slots.append({"slot": slot, "kind": attempts[-1]["kind"] if attempts else "missing"})
        if status == "blocked_unsupported_parameter":
            break
    if executed >= limit and status == "responses_received":
        finished = sum(1 for item in slots if item["kind"] in ("ok", "refusal_text"))
        if finished != planned:
            status = "stopped_at_call_cap"
    return {"planned_requests": planned, "executed_model_calls": executed,
            "status": status, "slots": slots}


def public_summary(folder, result):
    kinds = {}
    for item in result.get("slots") or []:
        kinds[item.get("kind") or "missing"] = kinds.get(item.get("kind") or "missing", 0) + 1
    return {"planned_requests": result["planned_requests"],
            "executed_model_calls": result["executed_model_calls"],
            "status": result["status"], "kinds": kinds, "usage": None}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run")
    run.add_argument("experiment", type=Path)
    run.add_argument("--online", action="store_true")
    run.add_argument("--max-calls", type=int, required=True)
    args = parser.parse_args(argv)
    if args.online:
        print(json.dumps({"executed_model_calls": 0,
                          "status": "real_transport_not_built"}, ensure_ascii=False))
        return 2
    plan = lab.load_plan(args.experiment)
    planned = plan_size(plan)
    status = "refused_over_budget" if planned > args.max_calls else "offline"
    print(json.dumps({"planned_requests": planned, "executed_model_calls": 0,
                      "status": status}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
