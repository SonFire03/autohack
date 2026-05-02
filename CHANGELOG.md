# Changelog

## Unreleased

- Split source catalog into `catalog/*.json` with `scripts/build_catalog.py` generating `commands_catalog.json`.
- Added functional advanced lab commands for NetExec, Certipy, NTLM relay/coercion, Windows/Linux privesc, and web attack tooling.
- Added dependency installer profiles with dry-run, confirmation, and manual-step reporting.
- Added cloud/Kubernetes, forensics/DFIR, binary/reverse, and API security command coverage.
- Added advanced CLI search filters and guided read-only command packs.
- Added Target Workspace and Command Builder utilities for reusable lab variables and command generation.
- Enforced `execution_policy` at runtime (`dry_run_only` blocked in run/capture, `lab_only` requires explicit confirmation).
- Added configurable execution hardening: `command_timeout`, `strict_shell_mode`, and secret redaction in logs/exports.
- Added structured execution telemetry in `logs/executions.jsonl`.
- Added regex/risk sorting search options and `--run-pack` guided step-by-step pack execution.
- Added strict catalog schema validation script and CI gate (`scripts/validate_catalog_schema.py`).
- Added manual GitHub release workflow (`.github/workflows/release.yml`).
- Added RBAC roles (`reader`, `operator`, `admin`) enforced across CLI and TUI run actions.
- Added secondary approval queue (`--list-approvals`, `--approve-command`) for sensitive commands.
- Added catalog signing and verification support (`scripts/sign_catalog.py`, `commands_catalog.sig`, `AUTOHACK_CATALOG_SECRET`).
- Added session export/replay capabilities (`--export-session`, `--replay-session`).
- Added execution telemetry HTML exporter (`--export-exec-report`).
- Added plugin catalog merge support from `plugins/catalog/*.json` in build pipeline.
- Added configurable checker cache TTL and CLI cache refresh (`--refresh-tools`).
- Added OS-aware package manager detection for installer planning.
- Added FR/EN message layer for security and policy prompts.
- Added optional TUI E2E smoke test (`tests/test_e2e_tui.py` with `pexpect`).

## 0.1.0

- Initial public release.
- Interactive TUI built with Rich.
- CLI search, category browsing, run, dry-run, export, stats, tags, and missing-tools commands.
- Command catalog with 1,331 entries.
- XSS payload catalog with 1,013 payloads.
- Tests for catalog loading, CLI behavior, executor behavior, exports, configuration, menus, logging, and session history.
- GitHub Actions test workflow for Python 3.10, 3.11, and 3.12.
