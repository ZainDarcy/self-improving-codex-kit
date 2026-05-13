# 自我进化候选区

自动化可以追加到这里。本文件中的内容在用户确认前都不是强制规则。

决策标签：
- promote：证据强、通用性好，且经过用户确认或多次出现。
- keep_candidate：有价值，但还需要更多证据。
- discard：噪声、过期、不安全或过窄。

## 如何批准候选

只有用户明确批准后，候选才允许被 executor 应用。推荐把批准项写成 YAML 文件并放入 `~/.codex/self-improve/promotions/pending/`。

示例：

```yaml
id: 2026-05-14-short-title
target: self-improve/memories/ACTIVE.md
operation: append_unique
content: |
  - New durable rule.
expected: |
  ACTIVE.md contains the new durable rule exactly once.
confirmed_by: User explicitly approved this promotion.
```

executor 只处理 `pending/*.yaml` 中结构完整的条目；缺少目标、操作或内容时只能写报告，不能猜。

## 队列
