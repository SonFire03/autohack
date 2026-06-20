from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

APPROVAL_PATH = Path.home() / ".autohack_approvals.json"


class ApprovalQueue:
    def __init__(self, path: Path = APPROVAL_PATH, ttl_minutes: int = 30) -> None:
        self._path = path
        self._ttl = ttl_minutes
        self._data = self._load()

    def _load(self) -> dict[str, str]:
        if not self._path.exists():
            return {}
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
            return raw if isinstance(raw, dict) else {}
        except Exception:
            return {}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _is_expired(self, marker: str) -> bool:
        if not marker.startswith("approved:"):
            return False
        ts = marker.split(":", 1)[1]
        try:
            at = datetime.fromisoformat(ts)
        except Exception:
            return True
        return datetime.now() - at > timedelta(minutes=self._ttl)

    def _cleanup_expired(self) -> None:
        expired = [cmd_id for cmd_id, marker in self._data.items() if self._is_expired(str(marker))]
        if not expired:
            return
        for cmd_id in expired:
            self._data.pop(cmd_id, None)
        self._save()

    def queue(self, cmd_id: str) -> None:
        self._data[cmd_id] = datetime.now().isoformat()
        self._save()

    def approve(self, cmd_id: str) -> bool:
        if cmd_id not in self._data:
            return False
        self._data[cmd_id] = "approved:" + datetime.now().isoformat()
        self._save()
        return True

    def is_approved(self, cmd_id: str) -> bool:
        marker = self._data.get(cmd_id)
        if not marker or not isinstance(marker, str) or not marker.startswith("approved:"):
            return False
        if self._is_expired(marker):
            self._data.pop(cmd_id, None)
            self._save()
            return False
        return True

    def list_pending(self) -> list[str]:
        self._cleanup_expired()
        return sorted(k for k, v in self._data.items() if not str(v).startswith("approved:"))
