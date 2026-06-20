from __future__ import annotations

from pathlib import Path
from typing import Any
import json

REQUIRED_CMD_FIELDS: dict[str, type] = {
    "id": str,
    "name": str,
    "command": str,
    "risks": str,
    "safe_to_run": bool,
}

OPTIONAL_CMD_FIELDS: dict[str, Any] = {
    "description": str,
    "purpose": str,
    "expected_output": str,
    "category": str,
    "short_name": str,
    "tool_required": (str, type(None)),
    "requires_sudo": bool,
    "dangerous": bool,
    "prerequisites": list,
    "tags": list,
    "execution_policy": str,
    "timeout_seconds": int,
    "allow_shell_features": bool,
}

ALLOWED_POLICIES = {"normal", "safe", "lab_only", "dry_run_only", "dangerous"}


def _assert_type(value: Any, expected: Any, path: str, errors: list[str]) -> None:
    if isinstance(expected, tuple):
        if not isinstance(value, expected):
            names = "|".join(t.__name__ for t in expected)
            errors.append(f"{path}: expected {names}, got {type(value).__name__}")
        return
    if expected is list:
        if not isinstance(value, list):
            errors.append(f"{path}: expected list, got {type(value).__name__}")
    elif not isinstance(value, expected):
        errors.append(f"{path}: expected {expected.__name__}, got {type(value).__name__}")


def validate_catalog_data(data: Any) -> list[str]:
    errors: list[str] = []

    if not isinstance(data, dict):
        return ["root must be an object"]
    if "categories" not in data or not isinstance(data["categories"], dict):
        return ["root.categories must be an object"]

    ids_seen: set[str] = set()
    for cat_key, cat_data in data["categories"].items():
        if not isinstance(cat_data, dict):
            errors.append(f"categories.{cat_key}: expected object")
            continue
        commands = cat_data.get("commands")
        if not isinstance(commands, list):
            errors.append(f"categories.{cat_key}.commands: expected list")
            continue

        for idx, cmd in enumerate(commands):
            prefix = f"categories.{cat_key}.commands[{idx}]"
            if not isinstance(cmd, dict):
                errors.append(f"{prefix}: expected object")
                continue

            for key, expected in REQUIRED_CMD_FIELDS.items():
                if key not in cmd:
                    errors.append(f"{prefix}: missing required field '{key}'")
                    continue
                _assert_type(cmd[key], expected, f"{prefix}.{key}", errors)

            unknown = set(cmd.keys()) - set(REQUIRED_CMD_FIELDS) - set(OPTIONAL_CMD_FIELDS)
            if unknown:
                errors.append(f"{prefix}: unknown fields {sorted(unknown)}")

            for key, expected in OPTIONAL_CMD_FIELDS.items():
                if key in cmd:
                    _assert_type(cmd[key], expected, f"{prefix}.{key}", errors)

            cmd_id = cmd.get("id")
            if isinstance(cmd_id, str):
                if cmd_id in ids_seen:
                    errors.append(f"{prefix}.id: duplicate id '{cmd_id}'")
                ids_seen.add(cmd_id)

            if isinstance(cmd.get("tags"), list) and any(not isinstance(t, str) for t in cmd["tags"]):
                errors.append(f"{prefix}.tags: all entries must be strings")
            if isinstance(cmd.get("prerequisites"), list) and any(
                not isinstance(t, str) for t in cmd["prerequisites"]
            ):
                errors.append(f"{prefix}.prerequisites: all entries must be strings")

            policy = cmd.get("execution_policy")
            if policy is not None and policy not in ALLOWED_POLICIES:
                errors.append(f"{prefix}.execution_policy: invalid value '{policy}'")

            timeout_seconds = cmd.get("timeout_seconds")
            if timeout_seconds is not None and isinstance(timeout_seconds, int) and timeout_seconds <= 0:
                errors.append(f"{prefix}.timeout_seconds: must be > 0")

            if cmd.get("dangerous") and cmd.get("safe_to_run"):
                errors.append(f"{prefix}: dangerous=true conflicts with safe_to_run=true")
            if cmd.get("safe_to_run") and policy == "lab_only":
                errors.append(f"{prefix}: safe_to_run=true conflicts with lab_only policy")

    return errors


def load_and_validate_catalog(path: Path) -> tuple[dict[str, Any], list[str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data, validate_catalog_data(data)
