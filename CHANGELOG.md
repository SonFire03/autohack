# Changelog

## 0.2.2

- Split CLI parsing and dispatch into `core/cli_runtime.py` to keep `main.py` thin.
- Centralized catalog schema validation in `core/catalog_schema.py`.
- Enforced the same schema rules at build time, validation time, and runtime load.
- Added tests for unknown fields, invalid types, duplicate IDs, and plugin/category collisions.

## 0.2.1

- Improved release packaging around the CLI and catalog runtime.
- Fixed multi-term regex search semantics and hard shell-strict blocking.
- Normalized config export formats and added stronger validation.
- Cached API catalog/checker instances and cleaned approval expiry handling.
- Prevented plugin category collisions during catalog builds.
- Added regression coverage for the latest fixes.

## 0.2.0

- Hardened catalog search semantics, including correct multi-term regex matching.
- Normalized configuration export formats and added stronger config validation.
- Strengthened shell execution policy detection and strict-mode blocking.
- Cached local API catalog and tool checker instances for fewer repeated loads.
- Cleaned up CLI entrypoint and removed leftover bootstrap code.
- Prevented plugin category collisions in catalog builds.
- Added approval queue expiry cleanup and coverage for the new behavior.
- Added regression tests for the search, executor, config, approval queue, and catalog build paths.

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
- Added category-based command allowlist enforcement (`enforce_command_allowlist`).
- Added environment profiles (`--apply-profile`) for lab and engagement contexts.
- Added catalog diff command (`--catalog-diff refA..refB`) to review release changes.
- Added hash-chained signed audit logs and verification command (`--verify-audit-chain`).
- Added playbook generator from packs (`--generate-playbook`).
- Added local read-only API server (`--serve-api`) with catalog and metrics endpoints.
- Added local usage metrics command (`--usage-metrics`) from execution telemetry.
- Added mutation-inspired security regression tests (`tests/test_security_mutation_guards.py`).
- Added binary packaging script + CI workflow (`scripts/build_binary.sh`, `.github/workflows/binary.yml`).

## Unreleased

- No unreleased changes yet.

## 0.1.0

- Initial public release.
- Interactive TUI built with Rich.
- CLI search, category browsing, run, dry-run, export, stats, tags, and missing-tools commands.
- Command catalog with 1,331 entries.
- XSS payload catalog with 1,013 payloads.
- Tests for catalog loading, CLI behavior, executor behavior, exports, configuration, menus, logging, and session history.
- GitHub Actions test workflow for Python 3.10, 3.11, and 3.12.
