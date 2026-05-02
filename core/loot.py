"""Loot vault — store captured credentials, hashes, flags and keys."""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

LOOT_PATH = Path.home() / ".autohack_loot.json"

LOOT_TYPES = [
    "credential",
    "hash",
    "flag",
    "ssh_key",
    "api_key",
    "token",
    "note",
    "other",
]


class LootVault:
    """Coffre-fort de butin persisté dans ~/.autohack_loot.json."""

    def __init__(self, path: Path = LOOT_PATH) -> None:
        self._path = path
        self._entries: List[Dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    self._entries = data
            except Exception:
                pass

    def _save(self) -> None:
        try:
            self._path.write_text(
                json.dumps(self._entries, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    def add(
        self,
        loot_type: str,
        value: str,
        source: str = "",
        notes: str = "",
    ) -> Dict[str, Any]:
        entry = {
            "id":        str(uuid.uuid4())[:8],
            "type":      loot_type,
            "value":     value,
            "source":    source,
            "notes":     notes,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        self._entries.append(entry)
        self._save()
        return entry

    def remove(self, entry_id: str) -> bool:
        before = len(self._entries)
        self._entries = [e for e in self._entries if e["id"] != entry_id]
        if len(self._entries) < before:
            self._save()
            return True
        return False

    def search(self, query: str) -> List[Dict[str, Any]]:
        q = query.lower()
        return [
            e for e in self._entries
            if q in e.get("value", "").lower()
            or q in e.get("source", "").lower()
            or q in e.get("notes", "").lower()
            or q in e.get("type", "").lower()
        ]

    def by_type(self, loot_type: str) -> List[Dict[str, Any]]:
        return [e for e in self._entries if e["type"] == loot_type]

    def all(self) -> List[Dict[str, Any]]:
        return list(self._entries)

    def export_markdown(self) -> str:
        lines = ["# Loot Vault\n"]
        by_type: Dict[str, List] = {}
        for e in self._entries:
            by_type.setdefault(e["type"], []).append(e)
        for t, entries in by_type.items():
            lines.append(f"## {t.upper()}\n")
            for e in entries:
                lines.append(f"- **[{e['id']}]** `{e['value']}`")
                if e["source"]:
                    lines.append(f"  - Source: {e['source']}")
                if e["notes"]:
                    lines.append(f"  - Notes: {e['notes']}")
                lines.append(f"  - {e['timestamp']}\n")
        return "\n".join(lines)

    def clear(self) -> None:
        self._entries.clear()
        self._save()

    def __len__(self) -> int:
        return len(self._entries)
