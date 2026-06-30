"""Global variable store — persist $TARGET, $LHOST, $LPORT etc. across commands."""
from pathlib import Path
from typing import Dict, Optional

from core.secure_storage import read_json_file, write_json_atomic

VARIABLES_PATH = Path.home() / ".autohack_variables.json"

# Default variable hints (same keys as executor _PLACEHOLDER_HINTS)
VAR_HINTS: Dict[str, str] = {
    "TARGET":       "IP ou domaine de la cible principale",
    "URL":          "URL complète ciblée (ex: https://app.lab/item?id=1)",
    "LHOST":        "Votre IP d'écoute (attaquant)",
    "LPORT":        "Port d'écoute reverse shell",
    "DOMAIN":       "Domaine Active Directory (ex: corp.local)",
    "DC_IP":        "IP du contrôleur de domaine",
    "USER":         "Nom d'utilisateur",
    "PASSWORD":     "Mot de passe",
    "HASH":         "Hash NTLM ou autre",
    "WORDLIST":     "Chemin vers la wordlist",
    "INTERFACE":    "Interface réseau (ex: eth0)",
    "PORT":         "Port cible",
    "FILE":         "Nom de fichier à transférer ou analyser",
    "SCOPE":        "Périmètre autorisé de la session",
    "NOTES":        "Notes rapides de session",
    "CALLBACK_URL": "URL de callback (blind XSS / SSRF)",
    "DOMAIN_SID":   "SID du domaine AD",
    "KRBTGT_HASH":  "Hash NTLM du compte krbtgt",
    "CA_NAME":      "Nom de la Certificate Authority AD CS",
}


class VariableStore:
    """Variables persistantes chargées depuis ~/.autohack_variables.json."""

    def __init__(self, path: Path = VARIABLES_PATH) -> None:
        self._path = path
        self._vars: Dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        data = read_json_file(self._path, {})
        if isinstance(data, dict):
            self._vars = {k: str(v) for k, v in data.items()}

    def _save(self) -> None:
        write_json_atomic(self._path, self._vars)

    def get(self, name: str) -> Optional[str]:
        return self._vars.get(name.upper())

    def set(self, name: str, value: str) -> None:
        self._vars[name.upper()] = value
        self._save()

    def delete(self, name: str) -> bool:
        key = name.upper()
        if key in self._vars:
            del self._vars[key]
            self._save()
            return True
        return False

    def all(self) -> Dict[str, str]:
        return dict(self._vars)

    def clear(self) -> None:
        self._vars.clear()
        self._save()

    def __len__(self) -> int:
        return len(self._vars)

    def __contains__(self, name: str) -> bool:
        return name.upper() in self._vars
