from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _load_catalog_from_ref(ref: str) -> dict[str, Any]:
    if ref in {"working", "local", "HEAD"}:
        path = ROOT / "commands_catalog.json"
        return json.loads(path.read_text(encoding="utf-8"))
    result = subprocess.run(["git", "show", f"{ref}:commands_catalog.json"], capture_output=True, text=True)
    if result.returncode != 0:
        raise ValueError(f"Unable to load commands_catalog.json from ref: {ref}")
    return json.loads(result.stdout)


def _flatten(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for category, data in catalog.get("categories", {}).items():
        for cmd in data.get("commands", []):
            c = dict(cmd)
            c["category"] = category
            out[c["id"]] = c
    return out


def diff_refs(ref_a: str, ref_b: str) -> dict[str, Any]:
    a = _flatten(_load_catalog_from_ref(ref_a))
    b = _flatten(_load_catalog_from_ref(ref_b))
    a_ids = set(a)
    b_ids = set(b)

    added = sorted(b_ids - a_ids)
    removed = sorted(a_ids - b_ids)
    changed = []

    for cid in sorted(a_ids & b_ids):
        keys = ["name", "command", "risks", "safe_to_run", "dangerous", "execution_policy", "category"]
        delta = {k: {"from": a[cid].get(k), "to": b[cid].get(k)} for k in keys if a[cid].get(k) != b[cid].get(k)}
        if delta:
            changed.append({"id": cid, "changes": delta})

    return {"from": ref_a, "to": ref_b, "added": added, "removed": removed, "changed": changed}
