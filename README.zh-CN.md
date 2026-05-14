# Self-Improving Codex Kit

这是一个可迁移、可审计的自我进化规范和 Codex 参考实现。它不修改模型权重，而是让 AI 通过外部脚手架形成受控闭环：

```text
观察 -> 写候选 -> 用户批准 -> 确定性 executor 应用 -> 审计日志
```

主 README 已内置中英文面板：[README.md](README.md)

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

## 迁移和修复

新电脑迁移、Windows 配置修复和安全导入见 [docs/migration.zh-CN.md](docs/migration.zh-CN.md)。

## 许可证

MIT
