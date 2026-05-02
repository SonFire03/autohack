from __future__ import annotations

ROLE_PERMISSIONS = {
    "reader": {"dry_run", "copy", "search", "export", "stats", "view"},
    "operator": {"dry_run", "copy", "search", "export", "stats", "view", "run", "run_pack"},
    "admin": {"dry_run", "copy", "search", "export", "stats", "view", "run", "run_pack", "install", "approve"},
}


def can(role: str, action: str) -> bool:
    return action in ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS["reader"])
