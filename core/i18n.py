from __future__ import annotations

from core.config_manager import ConfigManager

_MESSAGES = {
    "fr": {
        "rbac_denied": "Action non autorisée pour ce rôle.",
        "approval_pending": "Commande placée en attente d'approbation secondaire.",
        "approval_need": "Exécutez --approve-command <id> puis relancez.",
        "catalog_sig_missing": "Signature du catalogue absente.",
        "catalog_sig_invalid": "Signature du catalogue invalide.",
    },
    "en": {
        "rbac_denied": "Action not allowed for this role.",
        "approval_pending": "Command queued for secondary approval.",
        "approval_need": "Run --approve-command <id> and retry.",
        "catalog_sig_missing": "Catalog signature is missing.",
        "catalog_sig_invalid": "Catalog signature is invalid.",
    },
}


def tr(key: str, lang: str | None = None) -> str:
    current = lang or ConfigManager().get("lang")
    return _MESSAGES.get(current, _MESSAGES["fr"]).get(key, key)
