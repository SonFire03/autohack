"""Import helpers for external cheatsheets and command templates."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Iterable

from core.cheatsheet_policy import sanitize_cheatsheet_entry


def normalize_command(command: str) -> str:
    """Normalize command text for duplicate detection."""
    return re.sub(r"\s+", " ", command.strip())


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "cheatsheet"


def _read_json_file(path: Path) -> list[dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        if isinstance(payload.get("templates"), list):
            items = payload["templates"]
        else:
            items = [payload]
    elif isinstance(payload, list):
        items = payload
    else:
        raise ValueError(f"Unsupported cheatsheet payload in {path}")
    result: list[dict[str, object]] = []
    for item in items:
        if isinstance(item, dict):
            result.append(item)
    return result


def load_external_cheatsheets(directory: Path | None = None) -> list[dict[str, object]]:
    """Load raw cheatsheet records from a directory of JSON files."""
    root = directory or Path(os.environ.get("AUTOHACK_EXTRA_CHEATSHEET_DIR", "catalog/external_cheatsheets"))
    if not root.exists() or not root.is_dir():
        return []

    records: list[dict[str, object]] = []
    for path in sorted(root.glob("*.json")):
        records.extend(_read_json_file(path))
    return records


def build_external_templates(
    records: Iterable[dict[str, object]],
    existing_commands: Iterable[str] = (),
    existing_keys: Iterable[str] = (),
) -> tuple[list[dict[str, object]], list[str]]:
    """Normalize and deduplicate cheatsheet records."""
    seen_commands = {normalize_command(command) for command in existing_commands}
    seen_keys = {key.strip().lower() for key in existing_keys}
    templates: list[dict[str, object]] = []
    skipped: list[str] = []

    for record in records:
        normalized = sanitize_cheatsheet_entry(record)
        key = str(normalized.get("key", "")).strip().lower() or _slugify(str(normalized["title"]))
        command = normalize_command(str(normalized["command"]))
        if key in seen_keys:
            skipped.append(f"duplicate-key:{key}")
            continue
        if command in seen_commands:
            skipped.append(f"duplicate-command:{key}")
            continue
        normalized["key"] = key
        normalized["command"] = command
        templates.append(normalized)
        seen_keys.add(key)
        seen_commands.add(command)

    return templates, skipped
