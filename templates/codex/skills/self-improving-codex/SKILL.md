---
name: self-improving-codex
description: Maintain a controlled Codex self-improvement system using memories, hooks, rules, skills, automations, promotion YAML, and evals. Use when the user mentions self-improvement, 自我进化, Codex becoming smarter, memory promotion, retrospective learning, hook/rule tuning, recurring Codex mistakes, or turning repeated feedback into durable Codex behavior.
---

# Self-Improving Codex

Use this skill to make Codex better through auditable local scaffolding, not by changing model weights.

## Workflow

1. Inspect current state before changing anything: `~/.codex/AGENTS.md`, `~/.codex/config.toml`, `~/.codex/hooks.json`, `~/.codex/rules/`, and `~/.codex/self-improve/`.
2. Classify the requested improvement:
   - preference: candidate for `PROFILE.md`
   - always-on behavior: candidate for `ACTIVE.md`
   - workflow: candidate for a skill update
   - command safety: candidate for rules or hooks
   - recurring failure: candidate for `ERRORS.md` and evals
3. Write new observations to `CANDIDATES.md` or a dated report first.
4. Promote only after explicit user confirmation. Approved promotions should be YAML files under `self-improve/promotions/pending/`.
5. Keep high-priority files short. If the detail is long, leave it in `LEARNINGS.md`, `ERRORS.md`, or a report and link to it.
6. Validate hook JSON, hook sample behavior, and the promotion executor before declaring the system updated.

## Promotion Rules

- Promote to `ACTIVE.md` only when the rule is stable, broadly useful, and unlikely to conflict with project-specific instructions.
- Promote to `PROFILE.md` only for durable user preferences, not one-off task choices.
- Update `AGENTS.md`, hooks, or rules only when the user explicitly asks for implementation or confirms a pending promotion.
- Never store secrets, access tokens, credentials, or private personal data in memory files.
- User-facing reports and candidate explanations should be Chinese for Chinese-speaking users; AI-facing hook context may remain English.

## Output Expectations

When proposing improvements, group each item as:

- `promote`: ready to apply, with evidence and a pending YAML template.
- `keep_candidate`: plausible but needs more evidence.
- `discard`: noisy, stale, unsafe, or too narrow.

When implementing approved improvements, run the dedicated executor and report the changed global files and verification.
