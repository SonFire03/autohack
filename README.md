# AUTOHACK LAB COMMANDER

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Linux-informational)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://github.com/SonFire03/autohack/actions/workflows/tests.yml/badge.svg)
![Lint](https://img.shields.io/badge/Lint-Ruff-46a2f1)

AUTOHACK LAB COMMANDER is a terminal application for organizing, searching, documenting, and carefully running security lab commands from one place. It is built for students, CTF players, homelab users, and security practitioners who want a structured command catalog instead of scattered notes.

The project provides both an interactive Rich-powered terminal UI and a non-interactive CLI. The catalog currently contains 1,331 commands across 13 categories, including system checks, local network diagnostics, Tor/Privoxy, Scrapy, Elasticsearch, reconnaissance, web testing, password auditing, post-exploitation lab workflows, and XSS payloads.

> Important: this project is intended for legal labs, owned systems, CTFs, training environments, and authorized security assessments only. Many catalog entries can be intrusive or dangerous outside a controlled environment.

## Why I Built This

I wanted a structured terminal tool to centralize security lab commands, reduce note sprawl, and make command usage easier to review before execution.

## What It Does

AUTOHACK helps you:

- browse a large security command catalog by category
- search commands by keyword, tag, command text, or ID
- inspect purpose, prerequisites, risks, expected output, and required tools
- run safe commands from the terminal UI
- dry-run sensitive commands before copying or executing them
- export the catalog as Markdown, TXT, JSON, or HTML
- track local command history and favorites
- check which required tools are installed on your machine

It is not an exploitation framework and it does not hide what commands do. The goal is to make command usage clearer, safer, and easier to review before anything is executed.

## What This Is Not

AUTOHACK is not:

- an autonomous exploitation framework
- a botnet tool
- a stealth malware platform
- a replacement for understanding what commands do

## Main Features

- Interactive TUI built with `rich`
- CLI mode for automation and quick lookups
- 1,331 catalog entries
- 1,013 XSS payload entries
- Tagged command search with accent-insensitive matching
- Safety metadata: `safe`, `dry-run`, `lab-only`, `dangerous`, `sudo`
- Tool availability checks
- Favorites and session history
- Export support: `md`, `txt`, `json`, `html`
- Shell completion generation for Bash and Zsh
- Test suite covering catalog, CLI, executor, config, exports, and menus
- CI with Ruff linting and coverage reporting

## Categories

| Category | ID | Commands |
|---|---|---:|
| System / Environment | `system` | 32 |
| Local Network | `network` | 18 |
| Tor | `tor` | 15 |
| Privoxy | `privoxy` | 10 |
| Scrapy | `scrapy` | 15 |
| JSON / Export | `json_export` | 10 |
| Elastic / Logs | `elastic` | 13 |
| Diagnostic / Debug | `diagnostic` | 18 |
| Recon & Scan | `recon` | 42 |
| Web Attack | `web_attack` | 47 |
| Password Auditing | `passwords` | 30 |
| Post-Exploitation Lab | `post_exploit` | 68 |
| XSS Payloads | `xss` | 1,013 |

## Installation

Requirements:

- Python 3.10+
- Linux is recommended

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/SonFire03/autohack.git
cd autohack
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

Dependencies are intentionally small:

- `rich` for the terminal UI
- `pyperclip` for clipboard integration
- `pytest` for tests

Some catalog commands require external security tools such as `nmap`, `ffuf`, `hydra`, `hashcat`, `sqlmap`, `tor`, `privoxy`, `nuclei`, and others. AUTOHACK can report missing tools, but it does not install system packages automatically.

Deactivate the virtual environment later:

```bash
deactivate
```

## Quick Start

Launch the interactive interface:

```bash
python3 main.py
```

<img width="1580" height="1309" alt="AUTOHACK main menu" src="https://github.com/user-attachments/assets/3480b699-05d5-4f3a-8d50-9e2d8cf0fc45" />

Search the catalog:

```bash
python3 main.py --search tor
python3 main.py --search "graphql introspection"
```

<img width="1580" height="1309" alt="AUTOHACK search results for Tor commands" src="https://github.com/user-attachments/assets/4b1f30cf-12dd-4185-a299-da4b9cb33792" />

Show one category:

```bash
python3 main.py --category recon
python3 main.py --category web_attack
```

<img width="1580" height="1309" alt="AUTOHACK reconnaissance category view" src="https://github.com/user-attachments/assets/c071e8f4-486e-4d64-84ca-fe21a8f904ec" />

Preview a command without executing it:

```bash
python3 main.py --dry-run sys_001
```

Run a command by ID:

```bash
python3 main.py --run sys_001
```

Export the full catalog:

```bash
python3 main.py --export md
python3 main.py --export json
python3 main.py --export html
```

Run tests:

```bash
python3 -m pytest
```

Run lint and coverage locally:

```bash
pip install -e ".[dev]"
python3 -m ruff check .
python3 -m pytest --cov --cov-report=term-missing
```

## CLI Reference

```text
python3 main.py --help
```

Available options:

| Option | Purpose |
|---|---|
| `--run CMD_ID` | Execute a command by catalog ID |
| `--dry-run CMD_ID` | Show a command without executing it |
| `--search KEYWORD` | Search the catalog with multi-word matching |
| `--category CAT` | List commands in a category |
| `--export FORMAT` | Export catalog as `md`, `txt`, `json`, or `html` |
| `--check` | Run safe tool checks |
| `--list-ids` | Print all command IDs |
| `--list-categories` | Print available categories |
| `--stats` | Show catalog statistics |
| `--favorites` | Show saved favorites |
| `--tag TAG` | List commands matching a tag |
| `--missing-tools` | List required tools missing locally |
| `--generate-completion SHELL` | Generate Bash or Zsh completion |
| `--version` | Print the app version |

## Legal and Safe Usage

This project is intended only for:

- personal labs
- owned systems
- CTF environments
- training platforms
- explicitly authorized security assessments

Do not use this tool against third-party systems without written authorization.

AUTOHACK does not automate stealth, persistence, or unauthorized exploitation. Its goal is to make security lab commands easier to organize, review, and execute safely.

## Safety Model

Each command contains metadata describing risk and execution behavior.

Common fields:

- `safe_to_run`: whether the command is considered low risk
- `dangerous`: whether the command may be destructive, intrusive, or sensitive
- `requires_sudo`: whether elevated privileges may be required
- `execution_policy`: policy such as `safe`, `normal`, `dry_run_only`, or `lab_only`
- `risks`: human-readable risk explanation
- `prerequisites`: what must be true before using the command

AUTOHACK is designed to slow you down before risky actions. It shows warnings, command previews, prerequisites, and risk notes so each command can be reviewed before use.

Still, you are responsible for where and how commands are executed. Do not run intrusive commands against systems you do not own or do not have permission to test.

## Data And Local Files

Runtime data is stored locally. These files are not meant to be committed:

- `logs/` for application logs
- `exports/` for generated catalog exports
- `~/.autohack.json` for user configuration
- `~/.autohack_history.json` for local history
- `~/.autohack_favorites.json` for favorites

The repository includes `.gitkeep` files so `logs/` and `exports/` exist, but generated content inside them is ignored by Git.

If your local working tree contains old generated files, remove them locally after confirming you do not need them. They are ignored by Git and are not required to run the project.

## Project Structure

```text
autohack/
├── main.py                  # CLI entrypoint and TUI launcher
├── commands_catalog.json    # Command and payload catalog
├── requirements.txt         # Python dependencies
├── pyproject.toml           # Packaging metadata and console script
├── .github/workflows/       # GitHub Actions test workflow
├── config/                  # App settings and category labels
├── core/                    # Catalog, executor, checker, exports, theme, config
├── menus/                   # Rich terminal UI screens
├── tests/                   # Pytest suite
├── docs/examples/           # Example generated report
├── logs/                    # Runtime logs, ignored except .gitkeep
└── exports/                 # Generated exports, ignored except .gitkeep
```

## How The Catalog Works

The source of truth is `commands_catalog.json`. Commands are grouped by category and include metadata used by both the TUI and CLI.

Minimal command shape:

```json
{
  "id": "sys_001",
  "name": "Python version",
  "command": "python3 --version",
  "risks": "No risk, read-only",
  "safe_to_run": true
}
```

Common optional fields:

```json
{
  "short_name": "python version",
  "description": "Show installed Python version",
  "purpose": "Verify the runtime before launching tools",
  "expected_output": "Python 3.x.x",
  "prerequisites": [],
  "tool_required": "python3",
  "dangerous": false,
  "requires_sudo": false,
  "tags": ["python", "system"],
  "execution_policy": "safe"
}
```

Search uses IDs, names, tags, descriptions, purpose text, and command text. Multi-word searches use AND logic, so every searched word must match somewhere in the command metadata.

An example generated Markdown report is available at `docs/examples/example_report.md`.

## Shell Completion

Generate completion scripts from the live catalog:

```bash
python3 main.py --generate-completion bash
python3 main.py --generate-completion zsh
```

The generated completion includes command IDs, categories, and CLI flags.

## Versioning

The application version is defined in `config/version.py` and reused by the CLI and packaging metadata. Check the installed version with:

```bash
python3 main.py --version
```

## Development

Run the test suite:

```bash
python3 -m pytest
```

Useful targeted tests:

```bash
python3 -m pytest tests/test_catalog.py
python3 -m pytest tests/test_cli.py
python3 -m pytest tests/test_executor.py
python3 -m pytest tests/test_main_menu.py
```

Before publishing changes, run:

```bash
python3 -m ruff check .
python3 -m pytest --cov --cov-report=term-missing
python3 main.py --stats
```

For contribution rules, setup notes, and catalog guidelines, see `CONTRIBUTING.md`.

## Adding Commands

To add a command:

1. Edit `commands_catalog.json`.
2. Pick a unique ID that matches the category prefix.
3. Fill in `name`, `command`, `risks`, and `safe_to_run`.
4. Add tags and prerequisites when useful.
5. Mark risky commands with `dangerous: true`.
6. Use `dry_run_only` or `lab_only` for commands that should not be executed casually.
7. Run the tests.

For broad catalog additions, add tests in `tests/test_catalog.py` so the coverage cannot disappear silently later.

## Roadmap

- [x] GitHub Actions CI
- [x] Modern packaging metadata with `pyproject.toml`
- [x] Centralized app version
- [x] Ruff linting in CI
- [x] Coverage reporting in CI
- [ ] Split `commands_catalog.json` by category and generate the merged catalog
- [ ] Improve HTML export styling
- [ ] Add demo/screenshot mode for repeatable screenshots

## Future Catalog Refactor

The current catalog is intentionally stored in one JSON file for simple loading and deployment. As it grows, a cleaner structure would be:

```text
catalog/
├── system.json
├── network.json
├── recon.json
├── web_attack.json
├── passwords.json
├── post_exploit.json
└── xss.json
```

A small build script could merge those files into `commands_catalog.json`. That would make Git diffs smaller, reviews easier, and category contributions less error-prone.

## Legal Notice

AUTOHACK contains commands and payloads that can be harmful when misused. The project is provided for education, defensive research, CTFs, and authorized lab work. You are responsible for complying with applicable laws and rules of engagement.

Do not use this project against third-party systems without explicit authorization.
