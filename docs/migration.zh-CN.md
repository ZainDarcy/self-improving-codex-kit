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

## Windows 安装后启动报错

如果 Codex 启动时报类似 `config.toml: unclosed table`，说明本机 `~/.codex/config.toml` 已经不是合法 TOML。如果你需要先让 Codex 立刻能启动，可以先备份坏配置：

```powershell
Rename-Item "$env:USERPROFILE\.codex\config.toml" "config.toml.broken"
```

然后拉取最新版工具包并重新安装：

```powershell
python scripts/install_codex.py --dry-run
python scripts/install_codex.py --repair-config
python scripts/doctor.py
```

`--repair-config` 会备份坏掉的 `config.toml`，并重建一个只启用 hooks 和 memories 的最小配置。新版安装器会把 Windows 路径渲染成 `/`，避免 `C:\Users\...` 里的反斜杠破坏 JSON 或 TOML。
