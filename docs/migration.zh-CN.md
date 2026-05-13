# 迁移指南

## 新电脑安装

```bash
git clone https://github.com/YOUR-USER/self-improving-codex-kit.git
cd self-improving-codex-kit
python3 scripts/install_codex.py --dry-run
python3 scripts/install_codex.py
python3 scripts/doctor.py
```

## 安全导入本地偏好

不要整包复制旧的 `~/.codex`。建议：

1. 用 `scripts/export_current.py` 导出脱敏副本。
2. 人工检查 `PROFILE.md`、`ACTIVE.md` 和 `CANDIDATES.md`。
3. 把真正稳定的改动写成 pending promotion YAML。
4. 运行 promotion executor。

## 更新已有安装

拉取仓库更新后，重新运行安装器，再运行 doctor。安装器会在覆盖前备份现有文件。
