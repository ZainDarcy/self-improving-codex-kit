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

## Windows Startup Error After Install

If Codex fails to start with an error like `config.toml: unclosed table`, the local `~/.codex/config.toml` is not valid TOML. If you need Codex to boot immediately, back up the broken config:

```powershell
Rename-Item "$env:USERPROFILE\.codex\config.toml" "config.toml.broken"
```

Then pull the latest kit and rerun:

```powershell
python scripts/install_codex.py --dry-run
python scripts/install_codex.py --repair-config
python scripts/doctor.py
```

`--repair-config` backs up an invalid `config.toml` and recreates a minimal one with hooks and memories enabled. The installer now renders Windows paths with `/` so JSON and TOML files do not break on backslashes.
