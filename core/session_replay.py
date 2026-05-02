from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def export_session(path: Path, history, variables_store=None, loot_vault=None) -> Path:
    payload: dict[str, Any] = {
        "history": history.all() if history else [],
        "variables": variables_store.all() if variables_store and hasattr(variables_store, "all") else {},
        "loot": loot_vault.all() if loot_vault and hasattr(loot_vault, "all") else [],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_session(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
