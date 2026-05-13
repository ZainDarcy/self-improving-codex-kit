#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = REPO_ROOT / "templates" / "codex"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install Self-Improving Codex Kit into CODEX_HOME.")
    parser.add_argument("--codex-home", default=os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    parser.add_argument("--automation-cwd", default=str(Path.cwd()))
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def log(dry_run: bool, message: str) -> None:
    prefix = "[dry-run] " if dry_run else ""
    print(prefix + message)


def backup(path: Path, codex_home: Path, dry_run: bool) -> Path | None:
    if not path.exists():
        return None
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = codex_home / "self-improve" / "backups" / stamp / path.relative_to(codex_home)
    log(dry_run, f"backup {path} -> {dest}")
    if not dry_run:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if path.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(path, dest)
        else:
            shutil.copy2(path, dest)
    return dest


def render(text: str, codex_home: Path, automation_cwd: str, python: str) -> str:
    return (
        text.replace("{CODEX_HOME}", str(codex_home))
        .replace("{AUTOMATION_CWD}", automation_cwd)
        .replace("{PYTHON}", python)
    )


def copy_template(src: Path, dest: Path, codex_home: Path, automation_cwd: str, python: str, dry_run: bool) -> None:
    if src.is_dir():
        for child in src.iterdir():
            copy_template(child, dest / child.name, codex_home, automation_cwd, python, dry_run)
        return
    backup(dest, codex_home, dry_run)
    log(dry_run, f"write {dest}")
    if dry_run:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        content = src.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        shutil.copy2(src, dest)
        return
    dest.write_text(render(content, codex_home, automation_cwd, python), encoding="utf-8")
    if dest.suffix == ".py":
        dest.chmod(0o755)


def update_config(codex_home: Path, dry_run: bool) -> None:
    path = codex_home / "config.toml"
    backup(path, codex_home, dry_run)
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    keys = {"hooks": "true", "codex_hooks": "true", "memories": "true"}
    lines = text.splitlines()
    out: list[str] = []
    in_features = False
    seen: set[str] = set()
    inserted = False

    if not any(line.strip() == "[features]" for line in lines):
        if text and not text.endswith("\n"):
            text += "\n"
        text += "\n[features]\n"
        for key, value in keys.items():
            text += f"{key} = {value}\n"
        log(dry_run, f"enable features in {path}")
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        return

    for line in lines:
        if line.startswith("[") and line.endswith("]"):
            if in_features and not inserted:
                for key, value in keys.items():
                    if key not in seen:
                        out.append(f"{key} = {value}")
                inserted = True
            in_features = line.strip() == "[features]"
            out.append(line)
            continue
        if in_features:
            stripped = line.strip()
            matched = False
            for key, value in keys.items():
                if stripped.startswith(f"{key} " ) or stripped.startswith(f"{key}="):
                    out.append(f"{key} = {value}")
                    seen.add(key)
                    matched = True
                    break
            if matched:
                continue
        out.append(line)
    if in_features and not inserted:
        for key, value in keys.items():
            if key not in seen:
                out.append(f"{key} = {value}")

    log(dry_run, f"enable features in {path}")
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(out) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    codex_home = Path(args.codex_home).expanduser()
    if not TEMPLATE_ROOT.exists():
        print(f"Template root not found: {TEMPLATE_ROOT}", file=sys.stderr)
        return 1

    copy_template(TEMPLATE_ROOT, codex_home, codex_home, args.automation_cwd, args.python, args.dry_run)
    update_config(codex_home, args.dry_run)
    log(args.dry_run, "install complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
