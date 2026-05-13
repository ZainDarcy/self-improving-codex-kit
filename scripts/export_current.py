#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path


INCLUDE = [
    "AGENTS.md",
    "hooks.json",
    "hooks",
    "rules",
    "self-improve/memories",
    "self-improve/promotions",
    "self-improve/evals",
    "self-improve/reports/README.md",
    "skills/self-improving-codex",
    "automations",
]

EXCLUDE_PARTS = {"backups", "state", "__pycache__"}
EXCLUDE_NAMES = {".run-jitter-salt"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a sanitized copy of a local Codex self-improvement setup.")
    parser.add_argument("--codex-home", default=os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def should_skip(path: Path) -> bool:
    return bool(EXCLUDE_PARTS.intersection(path.parts)) or path.name in EXCLUDE_NAMES


def copy_clean(src: Path, dest: Path) -> None:
    if should_skip(src):
        return
    if src.is_dir():
        for child in src.iterdir():
            copy_clean(child, dest / child.name)
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    text = src.read_text(encoding="utf-8", errors="replace")
    if src.name == "config.toml":
        lines = []
        skip_hook_state = False
        for line in text.splitlines():
            if line.strip() == "[hooks.state]":
                skip_hook_state = True
                continue
            if skip_hook_state and line.startswith("["):
                skip_hook_state = False
            if skip_hook_state:
                continue
            lines.append(line)
        text = "\n".join(lines) + "\n"
    text = text.replace(str(Path.home()), "~")
    dest.write_text(text, encoding="utf-8")


def main() -> int:
    args = parse_args()
    codex_home = Path(args.codex_home).expanduser()
    out = Path(args.out).expanduser()
    if out.exists():
        shutil.rmtree(out)
    for rel in INCLUDE:
        src = codex_home / rel
        if src.exists():
            copy_clean(src, out / rel)
    print(f"Exported sanitized files to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
