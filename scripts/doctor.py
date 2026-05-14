#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback.
    tomllib = None


REQUIRED = [
    "AGENTS.md",
    "hooks.json",
    "hooks/self_improve_hook.py",
    "rules/default.rules",
    "self-improve/bin/apply_approved.py",
    "self-improve/memories/ACTIVE.md",
    "self-improve/memories/CANDIDATES.md",
    "self-improve/promotions/pending/README.md",
    "skills/self-improving-codex/SKILL.md",
    "automations/self-improve-apply-approved/automation.toml",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a Self-Improving Codex Kit installation.")
    parser.add_argument("--codex-home", default=os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    return parser.parse_args()


def run_hook(codex_home: Path, payload: dict) -> str:
    hook = codex_home / "hooks" / "self_improve_hook.py"
    result = subprocess.run(
        [sys.executable, str(hook)],
        input=json.dumps(payload),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "CODEX_HOME": str(codex_home)},
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr.strip() or f"hook exited {result.returncode}")
    return result.stdout.strip()


def main() -> int:
    args = parse_args()
    codex_home = Path(args.codex_home).expanduser()
    failures: list[str] = []

    for rel in REQUIRED:
        if not (codex_home / rel).exists():
            failures.append(f"missing {rel}")

    for rel in ("hooks/self_improve_hook.py", "self-improve/bin/apply_approved.py"):
        path = codex_home / rel
        if path.exists():
            try:
                compile(path.read_text(encoding="utf-8"), str(path), "exec")
            except Exception as exc:
                failures.append(f"python compile failed for {rel}: {exc}")

    hooks_json = codex_home / "hooks.json"
    if hooks_json.exists():
        try:
            json.loads(hooks_json.read_text(encoding="utf-8"))
        except Exception as exc:
            failures.append(f"invalid hooks.json: {exc}")

    if tomllib is not None:
        for toml_path in [codex_home / "config.toml", *sorted((codex_home / "automations").glob("**/*.toml"))]:
            if toml_path.exists():
                try:
                    tomllib.loads(toml_path.read_text(encoding="utf-8"))
                except Exception as exc:
                    rel = toml_path.relative_to(codex_home)
                    failures.append(f"invalid TOML in {rel}: {exc}")

    rules = codex_home / "rules" / "default.rules"
    if rules.exists():
        text = rules.read_text(encoding="utf-8")
        for bad in ("/private/tmp", "killall", "codex_self_improve_executor_setup.py"):
            if bad in text:
                failures.append(f"temporary or machine-local rule remains: {bad}")

    if (codex_home / "hooks" / "self_improve_hook.py").exists():
        try:
            dangerous = run_hook(codex_home, {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "git reset --hard"},
            })
            if '"decision": "block"' not in dangerous:
                failures.append("git reset --hard was not blocked")
            readonly = run_hook(codex_home, {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "sed -n '1,80p' ~/.codex/self-improve/memories/ACTIVE.md"},
            })
            if readonly:
                failures.append("read-only sed unexpectedly produced hook output")
        except Exception as exc:
            failures.append(f"hook fixture failed: {exc}")

    if failures:
        print("Self-Improving Codex Kit doctor failed:")
        for item in failures:
            print(f"- {item}")
        return 1

    print("Self-Improving Codex Kit doctor passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
