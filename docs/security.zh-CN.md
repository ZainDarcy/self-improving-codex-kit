# 安全模型

这套工具默认采用保守自动化。

## 永不记录

- API key、token、密码、账号凭据
- 私人敏感信息
- 除安装时生成外的本机私有路径
- backups、trusted hook hashes、本地数据库、会话日志

## 护栏

- 危险 shell 命令由 hooks 和 rules 阻断。
- 高优先级文件禁止被静默 shell 写入。
- 已批准提升必须是确定性 YAML。
- 不支持或格式错误的提升会进入 blocked，不会猜。

## 回滚

安装器和 promotion executor 会把备份写到 `~/.codex/self-improve/backups/`。回滚时，把备份文件恢复到当前位置，然后运行 `python3 scripts/doctor.py`。
