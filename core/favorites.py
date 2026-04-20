import json
from pathlib import Path
from typing import List

FAVORITES_PATH = Path.home() / ".autohack_favorites.json"


class Favorites:
    """Gère les commandes favorites persistées dans ~/.autohack_favorites.json."""

    def __init__(self, path: Path = FAVORITES_PATH) -> None:
        self._path = path
        self._ids: List[str] = []
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    self._ids = [str(x) for x in data]
            except Exception:
                pass

    def _save(self) -> None:
        try:
            self._path.write_text(
                json.dumps(self._ids, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    def add(self, cmd_id: str) -> bool:
        """Ajoute un ID aux favoris. Retourne True si ajouté, False si déjà présent."""
        if cmd_id in self._ids:
            return False
        self._ids.append(cmd_id)
        self._save()
        return True

    def remove(self, cmd_id: str) -> bool:
        """Retire un ID des favoris. Retourne True si retiré, False si absent."""
        if cmd_id not in self._ids:
            return False
        self._ids.remove(cmd_id)
        self._save()
        return True

    def toggle(self, cmd_id: str) -> bool:
        """Ajoute si absent, retire si présent. Retourne True = ajouté."""
        if cmd_id in self._ids:
            self.remove(cmd_id)
            return False
        self.add(cmd_id)
        return True

    def is_favorite(self, cmd_id: str) -> bool:
        return cmd_id in self._ids

    def all_ids(self) -> List[str]:
        return list(self._ids)

    def clear(self) -> None:
        self._ids.clear()
        self._save()

    def __len__(self) -> int:
        return len(self._ids)
