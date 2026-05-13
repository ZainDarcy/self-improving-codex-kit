# Architecture

Self-Improving Codex Kit separates discovery from authority.

```text
review automations -> CANDIDATES.md/reports
weekly consolidation -> promote/keep/discard recommendations
user approval -> promotions/pending/*.yaml
deterministic executor -> target files + promotions.log.md
evals/doctor -> regression checks
```

## Layers

- `AGENTS.md`: stable global entrypoint.
- `memories/ACTIVE.md`: short rules that should always apply.
- `memories/CANDIDATES.md`: non-binding observations and proposals.
- hooks: real-time reminders and guardrails.
- rules: command-level allow/prompt/forbidden policy.
- promotion executor: the only automated writer for high-priority files.
- reports/logs: user-readable audit trail.

## Authority Boundary

Automations can discover and summarize. They cannot promote by themselves. A user-approved YAML file is required before the executor changes `ACTIVE.md`, `PROFILE.md`, `AGENTS.md`, hooks, rules, or skills.
