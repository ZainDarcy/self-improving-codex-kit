# 架构

Self-Improving Codex Kit 把“发现问题”和“获得授权”分开。

```text
复盘自动化 -> CANDIDATES.md / reports
每周整理 -> promote / keep / discard 建议
用户批准 -> promotions/pending/*.yaml
确定性 executor -> 修改目标文件 + 写 promotions.log.md
evals / doctor -> 回归检查
```

## 分层

- `AGENTS.md`：稳定的全局入口。
- `memories/ACTIVE.md`：每次都应生效的短规则。
- `memories/CANDIDATES.md`：不具备强制力的观察和建议。
- hooks：实时提醒和护栏。
- rules：命令级 allow/prompt/forbidden 策略。
- promotion executor：唯一允许自动修改高优先级文件的执行器。
- reports/logs：给用户阅读的审计记录。

## 授权边界

自动化可以发现和总结，但不能自己提升规则。只有用户批准并写入 YAML 后，executor 才能修改 `ACTIVE.md`、`PROFILE.md`、`AGENTS.md`、hooks、rules 或 skills。
