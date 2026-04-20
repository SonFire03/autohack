import json
import unicodedata
from typing import List, Dict, Any, Optional
from config.settings import CATALOG_PATH


class CommandCatalog:
    """Charge et interroge le catalogue de commandes JSON."""

    def __init__(self) -> None:
        self._data: Dict[str, Any] = {}
        self._all_commands: List[Dict[str, Any]] = []
        self.load()

    REQUIRED_FIELDS = ("id", "name", "command", "risks", "safe_to_run")

    @staticmethod
    def _normalize_text(value: str) -> str:
        """Normalise pour rendre la recherche tolérante aux accents et à la casse."""
        normalized = unicodedata.normalize("NFKD", value.casefold())
        return "".join(char for char in normalized if not unicodedata.combining(char))

    def load(self) -> None:
        with open(CATALOG_PATH, encoding="utf-8") as f:
            self._data = json.load(f)
        self._all_commands = []
        errors = []
        for cat_key, cat in self._data["categories"].items():
            for cmd in cat["commands"]:
                cmd["category"] = cat_key
                missing = [f for f in self.REQUIRED_FIELDS if f not in cmd]
                if missing:
                    errors.append(f"[{cmd.get('id', '?')}] champs manquants : {missing}")
                self._all_commands.append(cmd)
        if errors:
            raise ValueError(
                f"Catalogue invalide — {len(errors)} erreur(s) :\n" + "\n".join(errors)
            )

    def validate(self) -> List[str]:
        """Retourne la liste des problèmes sans lever d'exception."""
        issues = []
        ids_seen: set = set()
        for cmd in self._all_commands:
            cmd_id = cmd.get("id", "?")
            for f in self.REQUIRED_FIELDS:
                if f not in cmd:
                    issues.append(f"[{cmd_id}] champ requis manquant : '{f}'")
            if cmd_id in ids_seen:
                issues.append(f"ID dupliqué : '{cmd_id}'")
            ids_seen.add(cmd_id)
            if cmd.get("dangerous") and cmd.get("safe_to_run"):
                issues.append(f"[{cmd_id}] dangerous=true ET safe_to_run=true sont contradictoires")
        return issues

    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        resolved = self.resolve_category(category)
        if not resolved:
            return []
        return [c for c in self._all_commands if c["category"] == resolved]

    def get_by_id(self, cmd_id: str) -> Optional[Dict[str, Any]]:
        return next((c for c in self._all_commands if c["id"] == cmd_id), None)

    def get_all(self) -> List[Dict[str, Any]]:
        return list(self._all_commands)

    def search(self, keyword: str) -> List[Dict[str, Any]]:
        """Recherche multi-mots avec scoring par pertinence.

        Score : +10 match ID, +8 nom/short_name, +5 tags, +2 description/purpose.
        Tous les mots doivent correspondre (AND). Résultats triés score desc.
        """
        words = self._normalize_text(keyword).split()
        if not words:
            return []

        scored: List[tuple[int, Dict[str, Any]]] = []
        for cmd in self._all_commands:
            name     = self._normalize_text(cmd.get("name", "") + " " + cmd.get("short_name", ""))
            tags     = self._normalize_text(" ".join(cmd.get("tags", [])))
            desc     = self._normalize_text(cmd.get("description", "") + " " + cmd.get("purpose", ""))
            cmd_id   = self._normalize_text(cmd.get("id", ""))
            cmd_text = self._normalize_text(cmd.get("command", ""))

            score = 0
            for w in words:
                if w not in cmd_id and w not in name and w not in tags and w not in desc and w not in cmd_text:
                    score = -1
                    break
                if w in cmd_id:
                    score += 10
                if w in name:
                    score += 8
                if w in tags:
                    score += 5
                if w in desc:
                    score += 2
                if w in cmd_text:
                    score += 1

            if score > 0:
                scored.append((score, cmd))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [cmd for _, cmd in scored]

    def get_categories(self) -> List[str]:
        return list(self._data["categories"].keys())

    def resolve_category(self, category: str) -> Optional[str]:
        """Retourne la catégorie canonique correspondant à l'entrée utilisateur.

        Supporte la correspondance exacte, les préfixes (rec → recon) et les
        sous-chaînes (attack → web_attack).
        """
        wanted = self._normalize_text(category.strip())
        if not wanted:
            return None
        categories = self.get_categories()
        for existing in categories:
            if self._normalize_text(existing) == wanted:
                return existing
        prefix_matches = [c for c in categories if self._normalize_text(c).startswith(wanted)]
        if len(prefix_matches) == 1:
            return prefix_matches[0]
        substr_matches = [c for c in categories if wanted in self._normalize_text(c)]
        if len(substr_matches) == 1:
            return substr_matches[0]
        return None

    def get_category_meta(self, category: str) -> Dict[str, str]:
        return self._data["categories"].get(category, {})

    def reload(self) -> None:
        """Recharge le catalogue depuis le disque (utile si le JSON a été modifié)."""
        self.load()

    def get_safe_commands(self) -> List[Dict[str, Any]]:
        return [c for c in self._all_commands if c.get("safe_to_run")]

    def get_dangerous_commands(self) -> List[Dict[str, Any]]:
        return [c for c in self._all_commands if c.get("dangerous")]
