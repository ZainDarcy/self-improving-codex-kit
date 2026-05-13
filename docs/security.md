# Security

This kit is designed for conservative automation.

## Never Store

- API keys, tokens, passwords, credentials
- private personal data
- machine-local paths unless they are install-time generated
- backups, trusted hook hashes, local databases, session logs

## Guardrails

- dangerous shell commands are blocked by hooks and rules
- high-priority files are protected from silent shell writes
- approved promotions must be deterministic YAML
- unsupported or malformed promotions are blocked, not guessed

## Rollback

The installer and promotion executor create backups under `~/.codex/self-improve/backups/`. To roll back, restore the backed-up file over the current file and run `python3 scripts/doctor.py`.
