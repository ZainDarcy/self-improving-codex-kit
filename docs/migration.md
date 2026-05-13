# Migration

## New Computer

```bash
git clone https://github.com/YOUR-USER/self-improving-codex-kit.git
cd self-improving-codex-kit
python3 scripts/install_codex.py --dry-run
python3 scripts/install_codex.py
python3 scripts/doctor.py
```

## Import Local Preferences Safely

Do not copy an old `~/.codex` wholesale. Instead:

1. export a sanitized copy with `scripts/export_current.py`
2. review `PROFILE.md`, `ACTIVE.md`, and `CANDIDATES.md`
3. convert durable changes into pending promotion YAML
4. run the promotion executor

## Update Existing Install

Pull the repository, run the installer, then run doctor. Existing files are backed up before overwrite.
