from typing import Optional, Tuple


def parse_palette_command(raw: str) -> Optional[Tuple[str, str]]:
    """Parse une commande de palette `:...` et retourne (action, argument)."""
    if not raw.startswith(":"):
        return None

    payload = raw[1:].strip()
    if not payload:
        return "palette", ""

    parts = payload.split(maxsplit=1)
    head = parts[0].lower()
    tail = parts[1].strip() if len(parts) > 1 else ""

    aliases = {
        "home": "home",
        "menu": "home",
        "search": "search",
        "find": "search",
        "favorites": "favorites",
        "fav": "favorites",
        "config": "config",
        "settings": "config",
        "checks": "checks",
        "check": "checks",
        "help": "help",
        "quit": "quit",
        "exit": "quit",
    }

    if head in aliases:
        return aliases[head], tail
    return "command", payload
