#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import importlib.util
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback.
    tomllib = None


ROOT = Path(__file__).resolve().parents[1]


def load_installer_module():
    spec = importlib.util.spec_from_file_location("install_codex", ROOT / "scripts" / "install_codex.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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

        installer = load_installer_module()
        rendered_hooks = installer.render(
            (ROOT / "templates" / "codex" / "hooks.json").read_text(encoding="utf-8"),
            Path(r"C:\Users\Lumos-之\.codex"),
            r"C:\Users\Lumos-之\self-improving-codex-kit",
            r"C:\Program Files\Python\python.exe",
        )
        json.loads(rendered_hooks)
        assert "C:/Users/Lumos-之/.codex" in rendered_hooks
        assert r"C:\Users" not in rendered_hooks

        if tomllib is not None:
            rendered_automation = installer.render(
                (ROOT / "templates" / "codex" / "automations" / "self-improve-apply-approved" / "automation.toml").read_text(encoding="utf-8"),
                Path(r"C:\Users\Lumos-之\.codex"),
                r"C:\Users\Lumos-之\self-improving-codex-kit",
                r"C:\Program Files\Python\python.exe",
            )
            parsed = tomllib.loads(rendered_automation)
            assert parsed["cwds"] == ["C:/Users/Lumos-之/self-improving-codex-kit"]

            broken_home = tmp / "broken-codex-home"
            broken_home.mkdir()
            (broken_home / "config.toml").write_text("[broken\n", encoding="utf-8")
            failed = run(
                [sys.executable, "scripts/install_codex.py", "--codex-home", str(broken_home)],
                check=False,
            )
            assert failed.returncode != 0
            repaired_home = tmp / "repaired-codex-home"
            repaired_home.mkdir()
            (repaired_home / "config.toml").write_text("[broken\n", encoding="utf-8")
            run([sys.executable, "scripts/install_codex.py", "--codex-home", str(repaired_home), "--repair-config"])
            repaired_config = (repaired_home / "config.toml").read_text(encoding="utf-8")
            tomllib.loads(repaired_config)
            assert "[features]" in repaired_config
            assert list((repaired_home / "self-improve" / "backups").glob("**/config.toml"))

        print("smoke tests passed")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
