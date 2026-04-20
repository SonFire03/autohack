# Contributing

Thanks for taking the time to improve AUTOHACK LAB COMMANDER.

## Setup

```bash
git clone https://github.com/SonFire03/autohack.git
cd autohack
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e ".[dev]"
```

## Run Tests

```bash
python3 -m pytest
```

## Lint And Coverage

```bash
python3 -m ruff check .
python3 scripts/build_catalog.py --check
python3 -m pytest --cov --cov-report=term-missing
```

## Guidelines

- Keep command metadata consistent.
- Edit category files in `catalog/`, then run `python3 scripts/build_catalog.py`.
- Add tests for new behavior.
- Add catalog coverage tests for broad command additions.
- Do not add commands intended for unauthorized use.
- Prefer clear descriptions over shorthand.
- Mark risky commands with `dangerous: true`.
- Use `dry_run_only` or `lab_only` for commands that should not be executed casually.
- Keep Ruff lint and coverage checks passing.
- Do not commit local logs, generated exports, virtual environments, or personal data.

## Legal Scope

Contributions must keep the project positioned as a legal lab, training, CTF, and authorized-assessment command organizer. Do not contribute stealth, persistence, evasion, or exploitation automation intended for unauthorized use.
