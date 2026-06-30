from pathlib import Path
from typing import Any

from core.secure_storage import read_json_file, write_json_atomic

CONFIG_PATH = Path.home() / ".autohack.json"

DEFAULTS: dict[str, Any] = {
    "export_format": "markdown",   # markdown | txt | json | html
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
    "enforce_command_allowlist": False,
}


class ConfigManager:
    """Lit et écrit la configuration utilisateur dans ~/.autohack.json."""

    _EXPORT_FORMAT_ALIASES = {
        "md": "markdown",
        "markdown": "markdown",
        "txt": "txt",
        "json": "json",
        "html": "html",
    }

    def __init__(self) -> None:
        self._data: dict[str, Any] = dict(DEFAULTS)
        self._load()

    def _normalize_value(self, key: str, value: Any) -> Any:
        if key == "export_format":
            if not isinstance(value, str):
                return value
            normalized = value.strip().lower()
            return self._EXPORT_FORMAT_ALIASES.get(normalized, value)
        if key == "export_dir" and value == "":
            return None
        return value

    def _load(self) -> None:
        saved = read_json_file(CONFIG_PATH, {})
        if isinstance(saved, dict):
            for key, value in saved.items():
                if key in DEFAULTS:
                    self._data[key] = self._normalize_value(key, value)

    def save(self) -> None:
        write_json_atomic(CONFIG_PATH, self._data)

    def get(self, key: str) -> Any:
        return self._normalize_value(key, self._data.get(key, DEFAULTS.get(key)))

    _ALLOWED: dict[str, set] = {
        "export_format": {"markdown", "txt", "json", "html"},
        "log_level":     {"INFO", "DEBUG", "WARNING"},
        "user_role": {"reader", "operator", "admin"},
        "lang": {"fr", "en"},
    }
    _POSITIVE_INT_KEYS = {"page_size", "history_size", "command_timeout", "tool_cache_ttl_seconds"}

    def set(self, key: str, value: Any) -> None:
        if key not in DEFAULTS:
            return
        value = self._normalize_value(key, value)
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
