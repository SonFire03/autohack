import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

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
        if self._path and self._path.exists():
            try:
                data = json.loads(self._path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    self._entries = data[-self._max:]
            except Exception:
                pass  # historique corrompu → repartir de zéro

    def _save(self) -> None:
        if self._path:
            try:
                self._path.write_text(
                    json.dumps(self._entries, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
            except Exception:
                pass  # échec silencieux (droits, disque plein…)

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
