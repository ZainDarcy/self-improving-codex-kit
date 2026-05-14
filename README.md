# Self-Improving Codex Kit

选择下面的语言面板即可在当前 README 内阅读，不需要跳转到另一个页面。

<details open>
<summary><strong>中文</strong></summary>

## 概览

这是一个可迁移、可审计的 Codex 自我进化工具包。它不修改模型权重，而是给 Codex 一套受控闭环：

```text
观察 -> 写候选 -> 用户批准 -> 确定性 executor 应用 -> 审计日志
```

## 会安装什么

- 全局 `AGENTS.md` 工作说明
- Codex hooks：提醒、拦截危险动作、结束前质量检查
- 命令 rules：放行低风险只读命令，阻止破坏性命令
- 记忆文件：用户画像、当前规则、经验、错误、能力需求、候选
- Promotion YAML 工作流和确定性 executor
- Codex skill：`self-improving-codex`
- 定时自动化：每日复盘、每周整理、每周评测、应用已批准提升

## 快速开始

```bash
git clone https://github.com/YOUR-USER/self-improving-codex-kit.git
cd self-improving-codex-kit
python3 scripts/install_codex.py --dry-run
python3 scripts/install_codex.py
python3 scripts/doctor.py
```

安装器会在覆盖文件前备份到 `~/.codex/self-improve/backups/`。

## 安全模型

- 自动化可以写候选和报告。
- 只有用户批准并放入 `~/.codex/self-improve/promotions/pending/` 的 YAML，才允许修改高优先级文件。
- executor 只支持三种确定性操作：`append_unique`、`replace_literal`、`delete_literal`。
- 不应提交 secrets、token、账号凭据、私人敏感信息、backups、trusted hashes 或本机私有状态。

## Promotion 示例

创建 `~/.codex/self-improve/promotions/pending/example.yaml`：

```yaml
id: 2026-05-14-example
target: self-improve/memories/ACTIVE.md
operation: append_unique
content: |
  - 完成代码修改前，总是说明验证了什么。
expected: |
  ACTIVE.md 中只出现一次这条规则。
confirmed_by: 用户明确批准本次提升。
```

然后运行：

```bash
python3 ~/.codex/self-improve/bin/apply_approved.py
```

## 上传发布

见 [docs/upload.md](docs/upload.md) 和 [docs/upload.zh-CN.md](docs/upload.zh-CN.md)。

## 其他 AI 工具

Codex v1 支持完整自动化。Claude、Cursor、Gemini 等其他 AI 可以手动读取 [docs/for-other-ai.md](docs/for-other-ai.md) 和 [docs/for-other-ai.zh-CN.md](docs/for-other-ai.zh-CN.md) 中的通用规则。

## 许可证

MIT

</details>

<details>
<summary><strong>English</strong></summary>

## Overview

A portable, auditable self-improvement layer for Codex. It does not modify model weights. It gives Codex a controlled loop:

```text
observe -> write candidates -> user approves -> deterministic executor applies -> audit log
```

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

</details>
