"""Observe sandbox preflight, approval replies, Hook stderr and a local MCP server."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from jsonschema import validate

HERE = Path(__file__).resolve().parent


def check(binary):
    if os.name != "nt":
        raise SystemExit("This example requires Windows.")
    with tempfile.TemporaryDirectory(prefix="codex-book-recovery-") as tmp:
        root = Path(tmp)
        profile = root / "codex"
        profile.mkdir()
        env = {k: v for k, v in os.environ.items()
               if k.upper() in {"SYSTEMROOT", "WINDIR", "COMSPEC", "PATH", "PATHEXT",
                                "TEMP", "TMP", "PROGRAMFILES", "PROGRAMFILES(X86)"}}
        env["CODEX_HOME"] = str(profile)

        def run(args, payload=None):
            return subprocess.run(args, input=payload, cwd=root, env=env, timeout=60,
                                  text=True, encoding="utf-8", errors="replace", capture_output=True)

        assert run([binary, "--version"]).stdout.strip() == "codex-cli 0.167.0"
        cmd = [os.environ["COMSPEC"], "/d", "/c", "echo", "BOOK_READY"]
        blocked_dir = profile / ".sandbox"
        blocked_dir.write_text("book fixture", encoding="utf-8")
        bad = run([binary, "sandbox", "--", *cmd])
        assert bad.returncode != 0 and "183" in bad.stderr and "BOOK_READY" not in bad.stdout, bad.stderr
        blocked_dir.rename(profile / "sandbox-file.backup")
        good = run([binary, "sandbox", "--", *cmd])
        assert good.returncode == 0 and good.stdout.strip() == "BOOK_READY", good.stderr
        print("sandbox: setup path collision (183); same command after recovery printed BOOK_READY")

        schema = root / "schema"
        run([binary, "app-server", "generate-json-schema", "--out", str(schema)]).check_returncode()
        def validate_as(name, value):
            file = next(schema.rglob(name + ".json"))
            validate(value, json.loads(file.read_text(encoding="utf-8")))

        for success, error in [(False, "book fixture: setup failed"), (True, None)]:
            validate_as("WindowsSandboxSetupCompletedNotification",
                        {"mode": "unelevated", "success": success, "error": error})
        cases = json.loads((HERE / "fixtures/app-server-requests.json").read_text(encoding="utf-8"))
        approval = next(c["message"] for c in cases if c["message"].get("method") ==
                        "item/commandExecution/requestApproval")
        validate_as("CommandExecutionRequestApprovalParams", approval["params"])
        policy = run([binary, "execpolicy", "check", "--rules", str(HERE / "review.rules"),
                      "git", "push", "origin", "review"])
        policy.check_returncode()
        assert json.loads(policy.stdout)["decision"] == "prompt"
        for decision in ("decline", "accept"):
            reply = {"id": approval["id"], "result": {"decision": decision}}
            assert reply["id"] == approval["id"]
            validate_as("CommandExecutionRequestApprovalResponse", reply["result"])
        print("approval: setup notifications and accept/decline replies validated against CLI schemas")

        hook = [sys.executable, "-I", str(HERE / "hook_guard.py")]
        malformed = run(hook, "{}")
        assert malformed.returncode == 1 and "PreToolUse" in malformed.stderr
        repaired = run(hook, (HERE / "fixtures/hook-read.json").read_text(encoding="utf-8"))
        repaired.check_returncode()
        assert json.loads(repaired.stdout)["hookSpecificOutput"]["hookEventName"] == "PreToolUse"
        print("hook: invalid input returned 1 on stderr; valid input returned structured JSON")

        server = HERE.parents[1] / "kimi/examples/review-plugin/rules_server.py"
        request = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}) + "\n"
        for script in [root / "missing.py", server]:
            if script == server:
                run([binary, "mcp", "remove", "book"]).check_returncode()
            run([binary, "mcp", "add", "book", "--", sys.executable, "-I", str(script)]).check_returncode()
            saved = run([binary, "mcp", "get", "book", "--json"])
            saved.check_returncode()
            transport = json.loads(saved.stdout)["transport"]
            response = run([transport["command"], *transport["args"]], request)
            if script == server:
                response.check_returncode()
                result = json.loads(response.stdout)
                assert result["id"] == 1 and result["result"]["tools"][0]["name"] == "get_rule"
            else:
                assert response.returncode != 0 and "missing.py" in response.stderr and not response.stdout
        print("mcp: configuration readable in both cases; corrected stdio command listed get_rule")


if __name__ == "__main__":
    check(str(Path(sys.argv[1]).resolve(strict=True)))
