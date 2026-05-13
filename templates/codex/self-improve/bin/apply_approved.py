#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


CODEX_HOME = Path(__file__).resolve().parents[2]
ROOT = CODEX_HOME / "self-improve"
PROMOTIONS = ROOT / "promotions"
PENDING = PROMOTIONS / "pending"
APPLIED = PROMOTIONS / "applied"
BLOCKED = PROMOTIONS / "blocked"
REPORTS = ROOT / "reports"
LOG = PROMOTIONS / "promotions.log.md"

ALLOWED_TARGETS = {
    "AGENTS.md",
    "rules/default.rules",
    "hooks/self_improve_hook.py",
    "skills/self-improving-codex/SKILL.md",
    "self-improve/memories/ACTIVE.md",
    "self-improve/memories/PROFILE.md",
}

SUPPORTED_OPERATIONS = {"append_unique", "replace_literal", "delete_literal"}


@dataclass
class Promotion:
    path: Path
    id: str
    target: str
    operation: str
    content: str
    replacement: str
    expected: str
    confirmed_by: str


def read_simple_yaml(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    current_key: str | None = None
    block_lines: list[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()

    def finish_block() -> None:
        nonlocal current_key, block_lines
        if current_key is not None:
            data[current_key] = "\n".join(block_lines).rstrip() + ("\n" if block_lines else "")
            current_key = None
            block_lines = []

    for raw in lines:
        if current_key is not None:
            if raw.startswith("  "):
                block_lines.append(raw[2:])
                continue
            finish_block()
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", raw)
        if not match:
            raise ValueError(f"Unsupported YAML line: {raw}")
        key, value = match.group(1), match.group(2)
        if value == "|":
            current_key = key
            block_lines = []
        else:
            data[key] = value.strip().strip('"').strip("'")
    finish_block()
    return data


def load_promotion(path: Path) -> Promotion:
    data = read_simple_yaml(path)
    missing = [key for key in ("id", "target", "operation", "content", "confirmed_by") if not data.get(key)]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")
    operation = data["operation"]
    target = data["target"]
    if operation not in SUPPORTED_OPERATIONS:
        raise ValueError(f"Unsupported operation: {operation}")
    if target not in ALLOWED_TARGETS:
        raise ValueError(f"Forbidden target: {target}")
    if operation == "replace_literal" and "replacement" not in data:
        raise ValueError("replace_literal requires replacement")
    return Promotion(
        path=path,
        id=data["id"],
        target=target,
        operation=operation,
        content=data.get("content", ""),
        replacement=data.get("replacement", ""),
        expected=data.get("expected", ""),
        confirmed_by=data.get("confirmed_by", ""),
    )


def backup_target(target: Path) -> Path | None:
    if not target.exists():
        return None
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = ROOT / "backups" / stamp / target.relative_to(CODEX_HOME)
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(target, backup)
    return backup


def apply_promotion(promotion: Promotion) -> tuple[bool, str]:
    target = CODEX_HOME / promotion.target
    target.parent.mkdir(parents=True, exist_ok=True)
    original = target.read_text(encoding="utf-8") if target.exists() else ""
    backup = backup_target(target)
    updated = original

    if promotion.operation == "append_unique":
        if promotion.content in original:
            return True, "content already present; no target write needed"
        sep = "" if not original or original.endswith("\n") else "\n"
        updated = original + sep + promotion.content
    elif promotion.operation == "replace_literal":
        if promotion.content not in original:
            raise ValueError("replace_literal content was not found in target")
        updated = original.replace(promotion.content, promotion.replacement, 1)
    elif promotion.operation == "delete_literal":
        if promotion.content not in original:
            return True, "content already absent; no target write needed"
        updated = original.replace(promotion.content, "", 1)

    if updated != original:
        target.write_text(updated, encoding="utf-8")
    backup_text = str(backup) if backup else "no previous file"
    return True, f"target={promotion.target}; backup={backup_text}"


def append_log(text: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    if not LOG.exists():
        LOG.write_text("# 提升执行日志\n\n## 日志\n", encoding="utf-8")
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(text.rstrip() + "\n")


def write_report(name: str, text: str) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    (REPORTS / f"{stamp}-{name}.md").write_text(text, encoding="utf-8")


def move(path: Path, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / path.name
    if dest.exists():
        stem = path.stem
        suffix = path.suffix
        dest = dest_dir / f"{stem}-{datetime.now().strftime('%Y%m%d-%H%M%S')}{suffix}"
    shutil.move(str(path), dest)
    return dest


def block(path: Path, reason: str) -> None:
    dest = move(path, BLOCKED)
    report = f"# 提升被阻止\n\n- 文件：`{path.name}`\n- 原因：{reason}\n- 移动到：`{dest}`\n"
    write_report(f"blocked-{path.stem}", report)
    append_log(f"- {datetime.now().isoformat(timespec='seconds')} blocked `{path.name}`: {reason}")


def main() -> int:
    PENDING.mkdir(parents=True, exist_ok=True)
    candidates = sorted(PENDING.glob("*.yaml"))
    if not candidates:
        return 0

    failures = 0
    for path in candidates:
        try:
            promotion = load_promotion(path)
            _, detail = apply_promotion(promotion)
            dest = move(path, APPLIED)
            append_log(
                f"- {datetime.now().isoformat(timespec='seconds')} applied `{promotion.id}` "
                f"to `{promotion.target}`: {detail}; yaml={dest}"
            )
            write_report(
                f"applied-{promotion.id}",
                f"# 提升已应用\n\n- ID：`{promotion.id}`\n- 目标：`{promotion.target}`\n- 操作：`{promotion.operation}`\n- 结果：{detail}\n- 验收：{promotion.expected or '未提供'}\n",
            )
        except Exception as exc:
            failures += 1
            block(path, str(exc))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
