from __future__ import annotations

import hashlib
import json
from pathlib import Path

from config.settings import EXECUTION_LOG_FILE


def verify(path: Path = EXECUTION_LOG_FILE) -> tuple[bool, int]:
    if not path.exists():
        return True, 0
    prev = ""
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines, 1):
        try:
            row = json.loads(line)
        except Exception:
            return False, i
        if row.get("prev_hash", "") != prev:
            return False, i
        event_hash = row.get("event_hash", "")
        material_row = dict(row)
        material_row.pop("event_hash", None)
        material = json.dumps(material_row, ensure_ascii=False, sort_keys=True)
        calc = hashlib.sha256(material.encode("utf-8")).hexdigest()
        if calc != event_hash:
            return False, i
        prev = event_hash
    return True, len(lines)
