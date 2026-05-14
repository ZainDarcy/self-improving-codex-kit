# Self-Improving AI Specification

This specification describes a controlled self-improvement workflow. It is not an installer-only format, and other AI tools should not blindly copy Codex templates. Any AI tool can read this spec and generate an equivalent implementation using its own native configuration system.

## Goal

Make AI behavior more stable through auditable external scaffolding:

```text
observe behavior -> write candidates -> user approves -> deterministic application -> audit log -> regression evals
```

Do not silently promote one-off observations, temporary preferences, or unconfirmed suggestions into high-priority rules.

## Required Layers

An implementation should include these semantic layers:

- Entry rules: stable instructions loaded at startup, such as `AGENTS.md`, system rules, or project instructions.
- Active rules: short rules that should apply every time, such as `ACTIVE.md`.
- User profile: long-lived user preferences, such as `PROFILE.md`.
- Candidate queue: automation and retrospectives may write here, such as `CANDIDATES.md`.
- Error log: recurring failures, recovery notes, and root causes, such as `ERRORS.md`.
- Learnings: validated lessons that are not necessarily ready for promotion, such as `LEARNINGS.md`.
- Promotion queue: machine-readable user-approved changes, such as `promotions/pending/*.yaml`.
- Audit log: record applied, blocked, and rollback actions.
- Eval cases: replay 3 to 5 failure cases to check whether new rules improve behavior.

Tools may rename files, but the semantic boundaries should stay separate.

## Authority Model

- Automations may write candidates and reports.
- Automations must not directly edit entry rules, active rules, user profile, hooks, rules, or skills.
- A candidate becomes durable only after explicit user approval.
- Approved changes must be machine-readable, preferably YAML or JSON.
- Executors should only perform deterministic operations and must not guess complex edits.

Recommended v1 operations:

- `append_unique`
- `replace_literal`
- `delete_literal`

Complex changes that cannot be expressed deterministically must be moved to `blocked` with a user-readable report.

## Protected Targets

By default, only the promotion executor may modify these high-priority targets:

- entry rules
- active rules
- user profile
- command approval rules
- hook scripts
- self-improvement skill or equivalent workflow notes

Other targets are forbidden unless the user explicitly expands the allowlist.

## Paths and Cross-Platform Rules

Generated config must handle platform differences:

- Do not write Windows paths such as `C:\Users\name\.ai` directly into JSON/TOML quoted strings.
- Prefer slash paths in config files: `C:/Users/name/.ai`.
- If backslashes are required, escape them according to the target format.
- Before writing global config, parse the existing config. If it is invalid, back it up and stop instead of appending.
- Do not commit machine-local absolute paths in public templates. Use placeholders or generate paths locally.

## User-Facing Language

User-readable content should use the user's preferred language. For Chinese-speaking users:

- reports, candidate explanations, blocked reasons, and migration notes should be Chinese
- AI-facing hook context may remain English when that is more reliable

## Safety Boundary

Never store:

- API keys, tokens, passwords, account credentials
- private personal data
- session logs, browsing history, trusted hook hashes
- backups, local databases, temporary state

Dangerous actions should be blocked or require explicit confirmation:

- `rm -rf`
- `git reset --hard`
- `git clean -fdx`
- sudo/admin elevation
- destructive system or disk operations

## Guidance for Other AI Tools

Other AI tools should not blindly copy Codex `hooks.json` or `config.toml`. The right workflow is:

1. Read this specification.
2. Inspect the tool's own configuration and permission model.
3. Generate native rules, memories, automations, or workflows for that tool.
4. Dry-run or present a plan first.
5. Write local configuration only after user confirmation.
6. Run a minimal eval after writing.

The Codex templates are a reference implementation, not the universal output for every AI tool.
