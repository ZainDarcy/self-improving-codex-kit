#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path


CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
ROOT = CODEX_HOME / "self-improve"
MEMORIES = ROOT / "memories"
STATE = ROOT / "state"
EXECUTOR = ROOT / "bin" / "apply_approved.py"

try:
    STATE.mkdir(parents=True, exist_ok=True)
except PermissionError:
    pass


def emit(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def hook_output(event: str, text: str) -> dict:
    return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}


def read_input() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception as exc:
        return {"_hook_parse_error": str(exc)}


def get_event(data: dict) -> str:
    return str(data.get("hook_event_name") or data.get("hookEventName") or "")


def text_from_file(path: Path, max_chars: int = 2200) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    return text[:max_chars]


SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{12,}"),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
]


def contains_secret(text: str) -> bool:
    return any(pattern.search(text or "") for pattern in SECRET_PATTERNS)


def classify_prompt(prompt: str) -> list[str]:
    lower = prompt.lower()
    reminders: list[str] = []
    if any(k in lower for k in ["implement", "fix", "修改", "实现", "修复", "代码"]):
        reminders.append("This looks like implementation work: inspect existing files first, keep edits scoped, and verify before finalizing.")
    if any(k in lower for k in ["deploy", "publish", "production", "生产", "上线", "数据库", "migration"]):
        reminders.append("This may affect production or persistence: call out risk, prefer reversible changes, and avoid destructive operations without explicit confirmation.")
    if any(k in lower for k in ["latest", "today", "最新", "今天", "现在"]):
        reminders.append("This may require fresh facts: verify time-sensitive information before relying on memory.")
    if any(k in lower for k in ["self-improve", "self improvement", "自我进化", "记忆", "hook", "hooks", "rules", "技能", "skill"]):
        reminders.append("Self-improvement changes must be auditable: write candidates first and promote only after explicit user confirmation.")
    return reminders


def handle_session_start(data: dict) -> None:
    active = text_from_file(MEMORIES / "ACTIVE.md")
    errors = text_from_file(MEMORIES / "ERRORS.md", 1200)
    parts = []
    if active:
        parts.append("Self-improvement ACTIVE memory:\n" + active)
    if errors:
        parts.append("Recent self-improvement error notes:\n" + errors)
    if parts:
        emit(hook_output("SessionStart", "\n\n".join(parts)))


def handle_user_prompt_submit(data: dict) -> None:
    prompt = str(data.get("prompt") or data.get("user_prompt") or data.get("message") or "")
    if contains_secret(prompt):
        emit({
            "decision": "block",
            "reason": "The prompt appears to contain a secret or credential. Remove the secret before continuing; do not store it in Codex memory.",
        })
        return
    reminders = classify_prompt(prompt)
    if reminders:
        emit(hook_output("UserPromptSubmit", "\n".join(f"- {item}" for item in reminders)))


def command_from_tool(data: dict) -> str:
    tool_input = data.get("tool_input") or data.get("toolInput") or {}
    if isinstance(tool_input, dict):
        for key in ("command", "cmd"):
            if key in tool_input:
                return str(tool_input[key])
    return str(data.get("command") or "")


DANGEROUS_COMMANDS = [
    (re.compile(r"(^|\s)rm\s+(-[^\s]*r[^\s]*f|-f[^\s]*r)\s+(/|~|\$HOME)(\s|$)"), "Refusing recursive force removal of a home/root path."),
    (re.compile(r"(^|\s)git\s+reset\s+--hard(\s|$)"), "Refusing `git reset --hard` without explicit user direction."),
    (re.compile(r"(^|\s)git\s+clean\s+-[^\s]*[fxd][^\s]*(\s|$)"), "Refusing destructive `git clean` without explicit user direction."),
    (re.compile(r"(^|\s)chmod\s+-R\s+777(\s|$)"), "Refusing broad world-writable chmod."),
    (re.compile(r"(^|\s)chown\s+-R(\s|$)"), "Refusing recursive ownership changes."),
    (re.compile(r"(^|\s)sudo(\s|$)"), "Refusing sudo from Codex hooks; request explicit approval if truly needed."),
    (re.compile(r"(^|\s)dd\s+.*\bof=/dev/"), "Refusing raw writes to device paths."),
    (re.compile(r"mkfs|diskutil\s+erase|:\(\)\s*\{\s*:\|:"), "Refusing destructive system-level command."),
]


PROTECTED_CODEX_PATHS = [
    "AGENTS.md",
    "config.toml",
    "hooks.json",
    "hooks/",
    "rules/",
    "skills/self-improving-codex/",
    "self-improve/memories/ACTIVE.md",
    "self-improve/memories/PROFILE.md",
    "self-improve/promotions/",
]


def invokes_dedicated_executor(command: str) -> bool:
    expanded = command.replace(str(Path.home()), "~")
    executor_paths = {
        str(EXECUTOR),
        str(EXECUTOR).replace(str(Path.home()), "~"),
        "~/.codex/self-improve/bin/apply_approved.py",
    }
    return any(path in expanded or path in command for path in executor_paths)


def touches_protected_codex_config(command: str) -> bool:
    expanded = command.replace(str(Path.home()), "~")
    if "~/.codex/self-improve/memories/CANDIDATES.md" in expanded:
        return False
    if "~/.codex/self-improve/reports/" in expanded:
        return False
    if "~/.codex" not in expanded and str(CODEX_HOME) not in command:
        return False
    writeish = re.search(r">\s*|>>\s*|\b(cp|mv|rm|perl|python|node|ruby|tee|chmod|chown)\b|\bsed\s+-[^\s]*i", command)
    if not writeish:
        return False
    return any(f"~/.codex/{suffix}" in expanded or str(CODEX_HOME / suffix) in command for suffix in PROTECTED_CODEX_PATHS)


def handle_pre_tool_use(data: dict) -> None:
    tool = str(data.get("tool_name") or data.get("toolName") or "")
    if tool and tool.lower() not in {"bash", "shell", "exec_command"}:
        return
    command = command_from_tool(data)
    if contains_secret(command):
        emit({"decision": "block", "reason": "The command appears to include a secret. Remove it from the command and use a safer secret-handling path."})
        return
    for pattern, reason in DANGEROUS_COMMANDS:
        if pattern.search(command):
            emit({"decision": "block", "reason": reason})
            return
    if touches_protected_codex_config(command) and not invokes_dedicated_executor(command):
        emit({"decision": "block", "reason": "Protected Codex self-improvement files should not be changed silently. Write a candidate/report first or use the dedicated promotion executor for approved YAML."})


def handle_permission_request(data: dict) -> None:
    command = command_from_tool(data)
    if not command:
        return
    low_risk_prefixes = ("rg ", "git diff", "git status", "ls ", "sed -n", "find ")
    if command.startswith(low_risk_prefixes):
        emit({"decision": "approve", "reason": "Low-risk read-only command."})
        return
    for pattern, reason in DANGEROUS_COMMANDS:
        if pattern.search(command):
            emit({"decision": "deny", "reason": reason})
            return


def git_changed_files() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only"],
            cwd=os.getcwd(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=3,
            check=False,
        )
        return [line for line in result.stdout.splitlines() if line.strip()]
    except Exception:
        return []


def handle_post_tool_use(data: dict) -> None:
    tool_result = data.get("tool_response") or data.get("toolResponse") or data.get("result") or {}
    text = json.dumps(tool_result, ensure_ascii=False) if not isinstance(tool_result, str) else tool_result
    command = command_from_tool(data)
    reminders = []
    if re.search(r"exit(ed)? with code [1-9]|failed|error|traceback|panic", text, re.I):
        reminders.append("The last tool call appears to have failed. Diagnose or clearly report the failure before finalizing.")
    if re.search(r"\b(test|pytest|vitest|jest|cargo test|go test|npm test)\b", command, re.I) and re.search(r"fail|failed|error", text, re.I):
        reminders.append("A verification command failed. Do not claim success until the failure is fixed or explicitly explained.")
    changed = git_changed_files()
    if len(changed) > 20:
        reminders.append(f"The working tree has {len(changed)} changed files. Confirm the edit scope before continuing.")
    if reminders:
        emit(hook_output("PostToolUse", "\n".join(f"- {item}" for item in reminders)))


def handle_stop(data: dict) -> None:
    changed = git_changed_files()
    if not changed:
        return
    transcript = json.dumps(data, ensure_ascii=False).lower()
    mentions_verification = any(k in transcript for k in ["test", "verified", "verification", "lint", "build", "检查", "测试", "验证"])
    if not mentions_verification:
        emit({"decision": "block", "reason": "Code changes are present but the final response does not mention verification. Run relevant checks or explicitly state what was not run."})


def main() -> None:
    data = read_input()
    event = get_event(data)
    handlers = {
        "SessionStart": handle_session_start,
        "UserPromptSubmit": handle_user_prompt_submit,
        "PreToolUse": handle_pre_tool_use,
        "PermissionRequest": handle_permission_request,
        "PostToolUse": handle_post_tool_use,
        "Stop": handle_stop,
    }
    handler = handlers.get(event)
    if handler:
        handler(data)


if __name__ == "__main__":
    main()
