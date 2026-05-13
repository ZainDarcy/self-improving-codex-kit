# Codex Global Operating Notes

Use this file as the stable entrypoint for the local self-improvement system.

- At session start, load high-priority guidance from `~/.codex/self-improve/memories/ACTIVE.md` when it is available.
- Treat `~/.codex/self-improve/memories/PROFILE.md` as user preference context, not as permission to override explicit user requests.
- Record new self-improvement observations as candidates first. Do not promote them into `ACTIVE.md`, `PROFILE.md`, this file, hooks, or rules unless the user explicitly confirms the promotion.
- Follow global hooks and rules. If a hook blocks an action, explain the reason and choose a safer path.
- Before finishing implementation work, check whether edits were verified, failed commands were addressed, and the final answer accurately names any unrun tests or residual risk.
- Never store secrets, tokens, account credentials, or private personal data in memory files.
