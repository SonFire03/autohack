import shutil
import time
from typing import Dict, List, Tuple
from core.catalog import CommandCatalog

_CACHE_TTL = 120  # secondes avant ré-interrogation du système


class ToolChecker:
    """Vérifie la disponibilité des outils sur le système via shutil.which."""

    def __init__(self, catalog: CommandCatalog, ttl_seconds: int = _CACHE_TTL) -> None:
        self._catalog = catalog
        self._ttl = max(1, int(ttl_seconds))
        self._cache: Dict[str, Tuple[bool, float]] = {}  # tool → (present, timestamp)

    def check(self, tool_name: str) -> bool:
        now = time.monotonic()
        cached = self._cache.get(tool_name)
        if cached is None or now - cached[1] > self._ttl:
            self._cache[tool_name] = (shutil.which(tool_name) is not None, now)
        return self._cache[tool_name][0]

    def refresh(self) -> None:
        """Vide le cache pour forcer une ré-vérification complète."""
        self._cache.clear()

    def set_ttl(self, ttl_seconds: int) -> None:
        self._ttl = max(1, int(ttl_seconds))
        self.refresh()

    def check_all(self) -> Dict[str, bool]:
        tools = {
            cmd.get("tool_required")
            for cmd in self._catalog.get_all()
            if cmd.get("tool_required")
        }
        return {t: self.check(t) for t in sorted(tools)}

    def badge(self, tool_name: str) -> str:
        return "✅" if self.check(tool_name) else "❌"

    def install_hint(self, tool_name: str) -> str:
        hints: Dict[str, str] = {
            "tor":           "sudo apt install tor",
            "privoxy":       "sudo apt install privoxy",
            "scrapy":        "pip install scrapy",
            "elasticsearch": "Voir: elastic.co/downloads/elasticsearch",
            "jq":            "sudo apt install jq",
            "nc":            "sudo apt install netcat",
            "curl":          "sudo apt install curl",
            "lsof":          "sudo apt install lsof",
            "nmap":          "sudo apt install nmap",
            "masscan":       "sudo apt install masscan",
            "hydra":         "sudo apt install hydra",
            "hashcat":       "sudo apt install hashcat",
            "sqlmap":        "sudo apt install sqlmap",
            "nikto":         "sudo apt install nikto",
            "gobuster":      "sudo apt install gobuster",
            "john":          "sudo apt install john",
            "wpscan":        "sudo apt install wpscan",
            "whatweb":       "sudo apt install whatweb",
            "ffuf":          "sudo apt install ffuf",
            "dirb":          "sudo apt install dirb",
            "dirbuster":     "sudo apt install dirbuster",
            "netcat":        "sudo apt install netcat",
            "netdiscover":   "sudo apt install netdiscover",
            "arp-scan":      "sudo apt install arp-scan",
            "whois":         "sudo apt install whois",
            "dig":           "sudo apt install dnsutils",
            "dnsenum":       "sudo apt install dnsenum",
            "dnsrecon":      "sudo apt install dnsrecon",
            "fierce":        "pip install fierce",
            "theHarvester":  "sudo apt install theharvester",
            "maltego":       "Voir: maltego.com/downloads",
            "metasploit":    "Voir: metasploit.com/download",
            "msfconsole":    "Voir: metasploit.com/download",
            "msfvenom":      "Voir: metasploit.com/download",
            "netstat":       "sudo apt install net-tools",
            "ss":            "sudo apt install iproute2",
            "tcpdump":       "sudo apt install tcpdump",
            "wireshark":     "sudo apt install wireshark",
            "aircrack-ng":   "sudo apt install aircrack-ng",
            "airodump-ng":   "sudo apt install aircrack-ng",
            "aireplay-ng":   "sudo apt install aircrack-ng",
            "proxychains":   "sudo apt install proxychains",
            "proxychains4":  "sudo apt install proxychains4",
            "socat":         "sudo apt install socat",
            "ssh":           "sudo apt install openssh-client",
            "python3":       "sudo apt install python3",
            "pip3":          "sudo apt install python3-pip",
            "docker":        "Voir: docs.docker.com/engine/install",
            "wget":          "sudo apt install wget",
        }
        return hints.get(tool_name, f"sudo apt install {tool_name}")

    def missing_tools(self) -> List[str]:
        return [t for t, ok in self.check_all().items() if not ok]

    def available_tools(self) -> List[str]:
        return [t for t, ok in self.check_all().items() if ok]
