# 上传和发布指南

## 发布前检查

运行：

```bash
python3 tests/run_smoke.py
python3 scripts/install_codex.py --dry-run --codex-home /tmp/self-improving-codex-check
```

确认仓库不包含：

- secrets 或 token
- `~/.codex/self-improve/backups`
- hook trusted hashes
- 本地 sqlite 数据库或会话日志
- 一次性临时 rules

## 创建 GitHub 仓库

创建一个公开仓库，名称为 `self-improving-codex-kit`。

## 推送

```bash
git init
git add .
git commit -m "Initial self-improving Codex kit"
git branch -M main
git remote add origin https://github.com/YOUR-USER/self-improving-codex-kit.git
git push -u origin main
```

## 发布后验证

把公开仓库克隆到临时目录，运行 install dry-run，然后用临时 `CODEX_HOME` 运行 doctor。
