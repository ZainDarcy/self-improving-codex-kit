# Self-Improving Codex Kit

选择下面的语言面板即可在当前 README 内阅读，不需要跳转到另一个页面。

<details open>
<summary><strong>中文</strong></summary>

## 概览

这是一个可迁移、可审计的 Codex 自我进化工具包。它不修改模型权重，而是给 Codex 一套受控闭环：

```text
观察 -> 写候选 -> 用户批准 -> 确定性 executor 应用 -> 审计日志
```

## 这是什么

这首先是一套规范，其次才是 Codex 参考实现。

- 通用规范：[docs/spec.zh-CN.md](docs/spec.zh-CN.md)
- 其他 AI 适配指南：[docs/for-other-ai.zh-CN.md](docs/for-other-ai.zh-CN.md)
- Codex 参考模板：`templates/codex/`
- Codex 辅助脚本：`scripts/`

## 快速开始

给任何 AI 使用时，先让它阅读规范，而不是盲目执行安装器：

```text
请阅读 docs/spec.zh-CN.md，并按照你自己的配置机制生成等价的自我进化模板。先输出计划和 dry-run，不要直接改全局配置。
```

只在 Codex 上使用参考实现时，再运行：

```bash
git clone https://github.com/YOUR-USER/self-improving-codex-kit.git
cd self-improving-codex-kit
python3 scripts/install_codex.py --dry-run
python3 scripts/install_codex.py
python3 scripts/doctor.py
```

安装器只是 Codex 的参考实现辅助工具。它会在覆盖文件前备份到 `~/.codex/self-improve/backups/`。

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

## What This Is

This is a specification first and a Codex reference implementation second.

- General spec: [docs/spec.md](docs/spec.md)
- Other AI adaptation guide: [docs/for-other-ai.md](docs/for-other-ai.md)
- Codex reference templates: `templates/codex/`
- Codex helper scripts: `scripts/`

## Quick Start

For any AI tool, ask it to read the spec instead of blindly running the installer:

```text
Read docs/spec.md and generate an equivalent self-improvement template using your own native configuration system. Present a plan and dry-run first; do not directly edit global config.
```

Only use the helper installer for the Codex reference implementation:

```bash
git clone https://github.com/YOUR-USER/self-improving-codex-kit.git
cd self-improving-codex-kit
python3 scripts/install_codex.py --dry-run
python3 scripts/install_codex.py
python3 scripts/doctor.py
```

The installer is only a helper for the Codex reference implementation. It backs up overwritten files under `~/.codex/self-improve/backups/`.

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
