#!/usr/bin/env python3
"""Import an external cheatsheet JSON file into AUTOHACK-compatible templates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from core.cheatsheet_importer import (
    build_external_templates,
    load_external_cheatsheets,
    write_external_cheatsheets,
)
from core.command_builder import all_templates


def _load_source(path: Path) -> list[dict[str, object]]:
    if path.is_dir():
        return load_external_cheatsheets(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and isinstance(payload.get("templates"), list):
        items = payload["templates"]
    elif isinstance(payload, dict):
        items = [payload]
    elif isinstance(payload, list):
        items = payload
    else:
        raise ValueError(f"Unsupported JSON structure in {path}")
    records: list[dict[str, object]] = []
    for item in items:
        if isinstance(item, dict):
            records.append(item)
    return records


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert an external cheatsheet JSON file into AUTOHACK-compatible templates.",
    )
    parser.add_argument("source", type=Path, help="JSON file or directory to import")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output JSON file (defaults to catalog/external_cheatsheets/<source>.json)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would be written without writing files")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    source = args.source
    if not source.exists():
        print(f"Source not found: {source}", file=sys.stderr)
        return 1

    records = _load_source(source)
    templates, skipped = build_external_templates(
        records,
        existing_commands=(tpl.command for tpl in all_templates()),
        existing_keys=(tpl.key for tpl in all_templates()),
    )

    if source.is_dir():
        default_output = Path("catalog/external_cheatsheets") / f"{source.name}.json"
    else:
        default_output = Path("catalog/external_cheatsheets") / f"{source.stem}.json"
    output = args.output or default_output

    print(f"Loaded: {len(records)}")
    print(f"Kept: {len(templates)}")
    print(f"Skipped: {len(skipped)}")
    for item in skipped[:20]:
        print(f"  - {item}")

    if args.dry_run:
        print(f"Dry-run, nothing written. Output would be: {output}")
        return 0

    write_external_cheatsheets(templates, output)
    print(f"Wrote: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
