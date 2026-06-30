#!/usr/bin/env python3
"""Strict validation for AUTOHACK catalog structure and command objects."""

# ruff: noqa: E402

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.catalog_schema import load_and_validate_catalog

CATALOG_PATH = ROOT / "commands_catalog.json"


def validate_catalog(path: Path = CATALOG_PATH) -> list[str]:
    _, errors = load_and_validate_catalog(path)
    return errors


def main() -> int:
    errors = validate_catalog()
    if errors:
        print("Catalog schema validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Catalog schema validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
