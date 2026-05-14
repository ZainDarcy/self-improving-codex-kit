# Adaptation Guide for Other AI Tools

Other AI tools such as Claude, Cursor, and Gemini should not directly copy Codex `hooks.json`, `config.toml`, or installer output. Read the general specification first: [spec.md](spec.md).

## Adaptation Workflow

1. Read `docs/spec.md`.
2. Inspect the AI tool's own configuration, memory, hook/rule, and automation mechanisms.
3. Generate native templates or rules for that tool instead of forcing the Codex file structure.
4. Present a plan and dry-run first.
5. Write local configuration only after user confirmation.
6. Run a minimal eval after writing to confirm startup, permissions, and normal tasks still work.

## Universal Rules

1. Do not silently promote observations into durable rules.
2. Write candidates first; require explicit user approval before changing durable instructions.
3. Never store secrets, credentials, tokens, or private personal data.
4. Before finalizing code changes, state what was verified and what was not.
5. Prefer reversible changes and backups for configuration or automation edits.
6. User-facing reports should use the user's preferred language; AI-facing internal context may use the language that is most reliable for the tool.

The Codex templates are a reference implementation, not the standard output for other AI tools.
