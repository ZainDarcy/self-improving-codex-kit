# Self-Improving Codex Kit

A portable, auditable self-improvement layer for Codex. It does not modify model weights. It gives Codex a controlled loop:

```text
observe -> write candidates -> user approves -> deterministic executor applies -> audit log
```

Chinese guide: [README.zh-CN.md](README.zh-CN.md)

## What It Installs

- Global `AGENTS.md` operating notes
- Codex hooks for reminders and guardrails
- Command rules for low-risk allows and destructive-command blocks
- Memory files for profile, active rules, learnings, errors, feature requests, and candidates
- Promotion YAML workflow with a deterministic executor
- Codex skill: `self-improving-codex`
- Recurring automations for review, consolidation, eval, and applying approved promotions

## Quick Start

```bash
git clone https://github.com/YOUR-USER/self-improving-codex-kit.git
cd self-improving-codex-kit
python3 scripts/install_codex.py --dry-run
python3 scripts/install_codex.py
python3 scripts/doctor.py
```

The installer backs up overwritten files under `~/.codex/self-improve/backups/`.

## Safety Model

- Automations may write candidates and reports.
- Only user-approved YAML files in `~/.codex/self-improve/promotions/pending/` may change high-priority files.
- The executor supports only deterministic operations: `append_unique`, `replace_literal`, and `delete_literal`.
- Secrets, tokens, account credentials, private personal data, backups, trusted hashes, and machine-local state should never be committed.

## Promotion Example

Create `~/.codex/self-improve/promotions/pending/example.yaml`:

```yaml
id: 2026-05-14-example
target: self-improve/memories/ACTIVE.md
operation: append_unique
content: |
  - Always explain what was verified before finalizing code changes.
expected: |
  ACTIVE.md contains the rule exactly once.
confirmed_by: User explicitly approved this promotion.
```

Then run:

```bash
python3 ~/.codex/self-improve/bin/apply_approved.py
```

## Publishing

See [docs/upload.md](docs/upload.md) and [docs/upload.zh-CN.md](docs/upload.zh-CN.md).

## Other AI Tools

Codex gets the full automatic workflow. Other AI tools can read the portable rules in [docs/for-other-ai.md](docs/for-other-ai.md) and [docs/for-other-ai.zh-CN.md](docs/for-other-ai.zh-CN.md).

## License

MIT
