from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from core.secure_storage import read_json_file, write_json_atomic

HISTORY_PATH = Path.home() / ".autohack_history.json"
_PERSIST_FIELDS = ("id", "name", "command", "category", "exit_code", "dry_run", "timestamp")


class SessionHistory:
    """Trace les commandes exécutées. Persiste optionnellement sur disque."""

    def __init__(self, max_size: int = 10, persist_path: Optional[Path] = None) -> None:
        self._entries: List[Dict[str, Any]] = []
        self._max = max_size
        self._path = persist_path
        if persist_path:
            self._load()

    # ── Persistance ───────────────────────────────────────────────────────────

    def _load(self) -> None:
        data = read_json_file(self._path, []) if self._path else []
        if isinstance(data, list):
            self._entries = data[-self._max:]

    def _save(self) -> None:
        if self._path:
            write_json_atomic(self._path, self._entries)

    # ── API publique ──────────────────────────────────────────────────────────

    def add(self, cmd: Dict[str, Any], exit_code: int, dry_run: bool = False) -> None:
        entry: Dict[str, Any] = {
            f: cmd.get(f, "") for f in _PERSIST_FIELDS
            if f not in ("exit_code", "dry_run", "timestamp")
        }
        entry["exit_code"] = exit_code
        entry["dry_run"] = dry_run
        entry["timestamp"] = datetime.now().strftime("%H:%M:%S")
        self._entries.append(entry)
        if len(self._entries) > self._max:
            self._entries.pop(0)
        self._save()

    def last(self, n: int = 5) -> List[Dict[str, Any]]:
        return list(reversed(self._entries[-n:]))

    def all(self) -> List[Dict[str, Any]]:
        return list(self._entries)

    def clear(self) -> None:
        self._entries.clear()
        self._save()

    def __len__(self) -> int:
        return len(self._entries)
