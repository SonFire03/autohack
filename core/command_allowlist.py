from __future__ import annotations

import re
from typing import Any

# Conservative patterns by category to reduce accidental arbitrary execution.
ALLOWLIST: dict[str, list[str]] = {
    "system": [r"^python3\b", r"^ls\b", r"^cat\b", r"^uname\b", r"^df\b", r"^free\b", r"^docker\b"],
    "network": [r"^ip\b", r"^ifconfig\b", r"^ss\b", r"^netstat\b", r"^nmap\b", r"^tcpdump\b"],
    "tor": [r"^tor\b", r"^systemctl\b", r"^journalctl\b"],
    "web_attack": [r"^ffuf\b", r"^nikto\b", r"^gobuster\b", r"^sqlmap\b", r"^curl\b"],
    "recon": [r"^nmap\b", r"^whois\b", r"^dig\b", r"^dnsrecon\b", r"^subfinder\b", r"^httpx\b"],
}


def is_allowed(cmd: dict[str, Any]) -> bool:
    command = (cmd.get("command") or "").strip()
    category = cmd.get("category", "")
    if not command:
        return False
    patterns = ALLOWLIST.get(category)
    if not patterns:
        # fallback: allow known command IDs only if explicitly tagged safe_to_run
        return bool(cmd.get("safe_to_run"))
    return any(re.search(pat, command) for pat in patterns)
