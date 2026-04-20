#!/usr/bin/env python3
"""Build the merged AUTOHACK command catalog from per-category files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_DIR = ROOT / "catalog"
DEFAULT_OUTPUT = ROOT / "commands_catalog.json"

CATEGORY_ORDER = [
    "system",
    "network",
    "tor",
    "privoxy",
    "scrapy",
    "json_export",
    "elastic",
    "diagnostic",
    "recon",
    "web_attack",
    "passwords",
    "post_exploit",
    "xss",
]

REQUIRED_FIELDS = ("id", "name", "command", "risks", "safe_to_run")


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_categories(source_dir: Path) -> dict[str, dict[str, Any]]:
    categories: dict[str, dict[str, Any]] = {}
    missing = []

    for category in CATEGORY_ORDER:
        path = source_dir / f"{category}.json"
        if not path.exists():
            missing.append(str(path.relative_to(ROOT)))
            continue
        data = load_json(path)
        if "commands" not in data:
            raise ValueError(f"{path}: missing 'commands' list")
        categories[category] = data

    if missing:
        raise ValueError("Missing category files: " + ", ".join(missing))

    extras = sorted(
        path.stem for path in source_dir.glob("*.json") if path.stem not in CATEGORY_ORDER
    )
    if extras:
        raise ValueError("Unknown category files: " + ", ".join(extras))

    return categories


def validate_catalog(catalog: dict[str, Any]) -> None:
    ids_seen: set[str] = set()
    errors = []

    for category, data in catalog["categories"].items():
        commands = data.get("commands", [])
        if not isinstance(commands, list):
            errors.append(f"[{category}] commands must be a list")
            continue

        for command in commands:
            command_id = command.get("id", "?")
            missing = [field for field in REQUIRED_FIELDS if field not in command]
            if missing:
                errors.append(f"[{command_id}] missing fields: {', '.join(missing)}")
            if command_id in ids_seen:
                errors.append(f"[{command_id}] duplicate command id")
            ids_seen.add(command_id)
            if command.get("category") and command["category"] != category:
                errors.append(f"[{command_id}] category field does not match '{category}'")

    if errors:
        raise ValueError("Invalid catalog:\n" + "\n".join(errors))


def build_catalog(source_dir: Path = DEFAULT_SOURCE_DIR) -> dict[str, Any]:
    catalog = {
        "version": "1.0.0",
        "categories": load_categories(source_dir),
    }
    validate_catalog(catalog)
    return catalog


def write_catalog(catalog: dict[str, Any], output: Path) -> None:
    output.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=DEFAULT_SOURCE_DIR,
        help="Directory containing one JSON file per category",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Merged catalog output path",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate that the output file already matches the generated catalog",
    )
    args = parser.parse_args()

    catalog = build_catalog(args.source_dir)
    if args.check:
        expected = json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"
        current = args.output.read_text(encoding="utf-8")
        if current != expected:
            raise SystemExit(f"{args.output} is out of date. Run scripts/build_catalog.py.")
        print(f"{args.output} is up to date.")
        return 0

    write_catalog(catalog, args.output)
    total = sum(len(category["commands"]) for category in catalog["categories"].values())
    print(f"Wrote {args.output.relative_to(ROOT)} with {total} commands.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
