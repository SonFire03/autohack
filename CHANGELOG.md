# Changelog

## Unreleased

- Split source catalog into `catalog/*.json` with `scripts/build_catalog.py` generating `commands_catalog.json`.
- Added functional advanced lab commands for NetExec, Certipy, NTLM relay/coercion, Windows/Linux privesc, and web attack tooling.
- Added dependency installer profiles with dry-run, confirmation, and manual-step reporting.

## 0.1.0

- Initial public release.
- Interactive TUI built with Rich.
- CLI search, category browsing, run, dry-run, export, stats, tags, and missing-tools commands.
- Command catalog with 1,331 entries.
- XSS payload catalog with 1,013 payloads.
- Tests for catalog loading, CLI behavior, executor behavior, exports, configuration, menus, logging, and session history.
- GitHub Actions test workflow for Python 3.10, 3.11, and 3.12.
