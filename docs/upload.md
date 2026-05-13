# Upload and Publish Guide

## Before Publishing

Run:

```bash
python3 tests/run_smoke.py
python3 scripts/install_codex.py --dry-run --codex-home /tmp/self-improving-codex-check
```

Check that the repository does not include:

- secrets or tokens
- `~/.codex/self-improve/backups`
- hook trusted hashes
- local sqlite databases or session logs
- one-off temporary rules

## Create the GitHub Repository

Create a public repository named `self-improving-codex-kit`.

## Push

```bash
git init
git add .
git commit -m "Initial self-improving Codex kit"
git branch -M main
git remote add origin https://github.com/YOUR-USER/self-improving-codex-kit.git
git push -u origin main
```

## Verify After Publishing

Clone the public repository into a temporary directory, run install dry-run, then run doctor against a temporary `CODEX_HOME`.
