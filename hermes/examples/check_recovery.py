"""Exercise the pinned SQLite schema and cron parser/transition functions offline."""
import argparse
import ast
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
import logging
from pathlib import Path
import sqlite3
import sys
import tempfile
from typing import Any, Optional


def pinned_source(root, name, blob):
    raw = (root / name).read_bytes().replace(b"\r\n", b"\n")
    assert hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest() == blob, name
    return ast.parse(raw, filename=name)


def check_session(root, tmp):
    module = pinned_source(root, "hermes_state_common.py", "c31526f02c6516cdd25cd611df8a388098564366")
    schema = next(node for node in module.body if isinstance(node, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == "SCHEMA_SQL" for t in node.targets))
    pinned_source(root, "hermes_state_keys.py", "38abd6e6d5c1330b3a309bb71f8acef3c57ef8ea")
    from hermes_state_keys import CRON_PRINCIPAL_ID
    sql = eval(compile(ast.Expression(schema.value), "SCHEMA_SQL", "eval"),
               {"__builtins__": {}, "CRON_PRINCIPAL_ID": CRON_PRINCIPAL_ID})
    db = tmp / "state.db"
    backup = tmp / "saved.db"
    with closing(sqlite3.connect(db)) as conn, closing(sqlite3.connect(backup)) as saved:
        conn.executescript(sql)
        conn.execute("INSERT INTO sessions (id, source, started_at) VALUES ('aurora','cli',1)")
        conn.execute("INSERT INTO messages (session_id, role, content, timestamp) VALUES (?,?,?,?)",
                     ("aurora", "user", "check inventory", 2))
        conn.commit()
        conn.backup(saved)
    db.rename(tmp / "moved.db")
    uri = db.as_uri() + "?mode=ro"
    try:
        sqlite3.connect(uri, uri=True).close()
    except sqlite3.OperationalError:
        assert not db.exists()
    else:
        raise AssertionError("Missing read-only database unexpectedly opened")
    with closing(sqlite3.connect(backup.as_uri() + "?mode=ro", uri=True)) as saved:
        with closing(sqlite3.connect(db)) as restored:
            saved.backup(restored)
    with closing(sqlite3.connect(uri, uri=True)) as conn:
        assert conn.execute("PRAGMA integrity_check").fetchall() == [("ok",)]
        rows = conn.execute("SELECT s.id, m.role, m.content FROM sessions s JOIN messages m "
                            "ON m.session_id = s.id ORDER BY m.id").fetchall()
        assert rows == [("aurora", "user", "check inventory")]
    print("SQLite: read-only missing DB refused; restored aurora with 1 message; integrity_check=ok")


def check_cron(root, tmp):
    pinned_source(root, "hermes_cli/subcommands/cron.py", "e4911627294f176d7c876ab9e9d5584876011399")
    pinned_source(root, "hermes_cli/subcommands/_shared.py", "6cf86df360a9c186e6a7627054ddb74a0f66b7ae")
    from hermes_cli.subcommands.cron import build_cron_parser
    parser = argparse.ArgumentParser(prog="hermes")
    build_cron_parser(parser.add_subparsers(), cmd_cron=lambda args: None)
    assert parser.parse_args(["cron", "list", "--all"]).all
    resume = parser.parse_args(["cron", "resume", "inventory"])
    assert resume.cron_command == "resume" and resume.job_id == "inventory"
    print("CLI parser: cron list --all; cron resume inventory")

    store = tmp / "job.json"
    slot = "2026-01-01T00:00:00+00:00"
    store.write_text(json.dumps({"id": "inventory", "schedule": {"kind": "interval"},
                                "enabled": True, "state": "scheduled", "next_run_at": slot}))
    def find(job_id):
        job = json.loads(store.read_text())
        return job if job["id"] == job_id else None

    def update(job_id, fields):
        job = find(job_id)
        job.update(fields)
        store.write_text(json.dumps(job))
        return job

    source = pinned_source(root, "cron/jobs.py", "1809214b9df26595d7a964f920ed47bb5bac927e")
    funcs = [n for n in source.body if isinstance(n, ast.FunctionDef) and
             n.name in {"pause_job", "resume_job", "_instant_at_or_before"}]
    assert {node.name for node in funcs} == {"pause_job", "resume_job", "_instant_at_or_before"}
    scope = {"Optional": Optional, "Any": Any, "datetime": datetime, "UTC": timezone.utc,
             "_hermes_now": lambda: datetime(2026, 1, 2, tzinfo=timezone.utc),
             "_parse_aware": datetime.fromisoformat, "logger": logging.getLogger("book"),
             "resolve_job_ref": find, "update_job": update}
    exec(compile(ast.Module(body=funcs, type_ignores=[]), "cron/jobs.py", "exec"), scope)
    scope["pause_job"]("inventory", "check inputs")
    paused = find("inventory")
    assert (paused["enabled"], paused["state"], paused["paused_reason"]) == (False, "paused", "check inputs")
    scope["resume_job"](resume.job_id)
    active = find("inventory")
    assert (active["enabled"], active["state"], active["next_run_at"]) == (True, "scheduled", slot)
    assert active["paused_reason"] is None and active["paused_at"] is None
    print("cron: paused reason retained; resumed recurring job retained its overdue slot")


if __name__ == "__main__":
    upstream = Path(sys.argv[1]).resolve(strict=True)
    sys.path.insert(0, str(upstream))
    with tempfile.TemporaryDirectory(prefix="hermes-book-recovery-") as directory:
        check_session(upstream, Path(directory))
        check_cron(upstream, Path(directory))
