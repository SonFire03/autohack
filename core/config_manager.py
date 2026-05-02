import json
from pathlib import Path
from typing import Any

CONFIG_PATH = Path.home() / ".autohack.json"

DEFAULTS: dict[str, Any] = {
    "export_format": "markdown",   # markdown | txt | json
    "page_size": 10,               # commandes par page dans les menus
    "log_level": "INFO",
    "export_dir": None,            # None = utiliser le dossier exports/ du projet
    "confirm_safe_commands": True, # demander confirmation même pour safe_to_run=True
    "show_history_in_menu": True,
    "history_size": 10,
    "command_timeout": 30,         # timeout d'exécution global (secondes)
    "strict_shell_mode": False,    # bloque les opérateurs shell risqués à l'exécution
    "redact_secrets_in_logs": True,# masque mots de passe/tokens dans logs/exports
    "user_role": "admin",          # reader | operator | admin
    "lang": "fr",                  # fr | en
    "enforce_catalog_signature": False,
    "require_secondary_approval": False,
    "tool_cache_ttl_seconds": 120,
}


class ConfigManager:
    """Lit et écrit la configuration utilisateur dans ~/.autohack.json."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = dict(DEFAULTS)
        self._load()

    def _load(self) -> None:
        if CONFIG_PATH.exists():
            try:
                saved = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
                self._data.update({k: v for k, v in saved.items() if k in DEFAULTS})
            except Exception:
                pass  # fichier corrompu → utiliser les défauts

    def save(self) -> None:
        CONFIG_PATH.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def get(self, key: str) -> Any:
        return self._data.get(key, DEFAULTS.get(key))

    _ALLOWED: dict[str, set] = {
        "export_format": {"markdown", "txt", "json"},
        "log_level":     {"INFO", "DEBUG", "WARNING"},
        "user_role": {"reader", "operator", "admin"},
        "lang": {"fr", "en"},
    }
    _POSITIVE_INT_KEYS = {"page_size", "history_size", "command_timeout"}

    def set(self, key: str, value: Any) -> None:
        if key not in DEFAULTS:
            return
        allowed = self._ALLOWED.get(key)
        if allowed and value not in allowed:
            raise ValueError(f"'{value}' non autorisé pour {key} — valeurs : {sorted(allowed)}")
        if key in self._POSITIVE_INT_KEYS and (not isinstance(value, int) or value <= 0):
            raise ValueError(f"'{key}' doit être un entier > 0 (reçu : {value!r})")
        self._data[key] = value
        self.save()

    def reset(self) -> None:
        self._data = dict(DEFAULTS)
        self.save()

    def all_settings(self) -> dict[str, Any]:
        return dict(self._data)
