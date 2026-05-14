#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], *, input_text: str | None = None, env: dict[str, str] | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        input=input_text,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, **(env or {})},
        check=False,
    )
    if check and result.returncode != 0:
        raise AssertionError(f"command failed: {' '.join(cmd)}\nstdout={result.stdout}\nstderr={result.stderr}")
    return result


def hook(codex_home: Path, payload: dict) -> str:
    return run(
        [sys.executable, str(codex_home / "hooks" / "self_improve_hook.py")],
        input_text=json.dumps(payload),
        env={"CODEX_HOME": str(codex_home)},
    ).stdout.strip()


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="sicodex-"))
    try:
        codex_home = tmp / "codex-home"
        run([sys.executable, "scripts/install_codex.py", "--codex-home", str(codex_home), "--automation-cwd", str(ROOT)])
        run([sys.executable, "scripts/doctor.py", "--codex-home", str(codex_home)])

        session = hook(codex_home, {"hook_event_name": "SessionStart"})
        assert "Self-improvement ACTIVE memory" in session

        readonly = hook(codex_home, {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "sed -n '1,80p' ~/.codex/self-improve/memories/ACTIVE.md"},
        })
        assert readonly == ""

        dangerous = hook(codex_home, {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "git reset --hard"},
        })
        assert '"decision": "block"' in dangerous

        pending = codex_home / "self-improve" / "promotions" / "pending" / "append-rule.yaml"
        pending.write_text(
            """id: append-rule
target: self-improve/memories/ACTIVE.md
operation: append_unique
content: |
  - Smoke-test durable rule.
expected: |
  ACTIVE.md contains Smoke-test durable rule once.
confirmed_by: smoke test
""",
            encoding="utf-8",
        )
        run([sys.executable, str(codex_home / "self-improve" / "bin" / "apply_approved.py")])
        active = (codex_home / "self-improve" / "memories" / "ACTIVE.md").read_text(encoding="utf-8")
        assert active.count("Smoke-test durable rule") == 1
        assert not pending.exists()
        assert (codex_home / "self-improve" / "promotions" / "applied" / "append-rule.yaml").exists()

        forbidden = codex_home / "self-improve" / "promotions" / "pending" / "forbidden.yaml"
        forbidden.write_text(
            """id: forbidden
target: config.toml
operation: append_unique
content: |
  unsafe
confirmed_by: smoke test
""",
            encoding="utf-8",
        )
        result = run([sys.executable, str(codex_home / "self-improve" / "bin" / "apply_approved.py")], check=False)
        assert result.returncode == 1
        assert (codex_home / "self-improve" / "promotions" / "blocked" / "forbidden.yaml").exists()

        print("smoke tests passed")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
