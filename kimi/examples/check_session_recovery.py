"""Restore a synthetic session and fork it with the pinned Kimi CLI."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

def check(binary):
    with tempfile.TemporaryDirectory(prefix="kimi-book-restore-") as tmp:
        root = Path(tmp)
        data = root / "data"
        work = root / "project"
        work.mkdir()
        (work / ".git").mkdir()
        parent = "book-source"
        digest = hashlib.sha256(work.as_posix().encode()).hexdigest()[:12]
        directory = data / "sessions" / f"wd_project_{digest}" / parent
        agent = directory / "agents" / "main"
        agent.mkdir(parents=True)
        (data / "config.toml").write_text("telemetry = false\nauto_session_title = false\n")
        env = {k: v for k, v in os.environ.items() if not k.startswith("KIMI_")}
        env.update(KIMI_CODE_HOME=str(data), KIMI_DISABLE_TELEMETRY="1", USERPROFILE=tmp)

        def run(*args):
            return subprocess.run([binary, *args], cwd=work, env=env, capture_output=True,
                                  encoding="utf-8", timeout=30, stdin=subprocess.DEVNULL)

        assert run("--version").stdout.strip() == "2.5.2"
        state = directory / "state.json"
        state.write_text(json.dumps({"id": parent, "cwd": str(work), "title": "Book inventory",
                                     "createdAt": 1000, "updatedAt": 2000}), encoding="utf-8")
        wire = agent / "wire.jsonl"
        records = [{"type": "metadata", "protocol_version": "1.5", "created_at": 1},
                   {"type": "context.append_message", "time": 2, "message": {"role": "user",
                    "content": [{"type": "text", "text": "book-marker"}], "origin": {"kind": "user"}}}]
        wire.write_text("".join(json.dumps(row) + "\n" for row in records), encoding="utf-8")
        backup = root / "backup"
        shutil.copytree(directory, backup)
        original = wire.read_bytes()
        state.rename(directory / "state.damaged")
        missing = run("session", "list", "--all", "--json")
        missing.check_returncode()
        assert json.loads(missing.stdout) == []
        shutil.copyfile(backup / "state.json", state)
        visible = run("session", "list", "--all", "--json")
        visible.check_returncode()
        rows = json.loads(visible.stdout)
        assert [(row["id"], row["title"]) for row in rows] == [(parent, "Book inventory")]
        fork = run("fork", parent, "--yes")
        assert fork.returncode == 0, (fork.stdout, fork.stderr)
        children = [p for p in (data / "sessions").glob("*/*/state.json") if p != state]
        assert len(children) == 1, children
        child = json.loads(children[0].read_text(encoding="utf-8"))
        assert child["id"] != parent and child["forkedFrom"] == parent, child
        child_wire = children[0].parent / "agents/main/wire.jsonl"
        assert b"book-marker" in child_wire.read_bytes()
        assert wire.read_bytes() == original
        print("Kimi 2.5.2: missing parent restored; fork has its own ID and inherits book-marker")

if __name__ == "__main__":
    check(str(Path(sys.argv[1]).resolve(strict=True)))
