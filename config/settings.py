from pathlib import Path
from config.version import __version__

BASE_DIR = Path(__file__).parent.parent
CATALOG_PATH = BASE_DIR / "commands_catalog.json"
LOGS_DIR = BASE_DIR / "logs"
EXPORTS_DIR = BASE_DIR / "exports"

LOGS_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)

LOG_FILE = LOGS_DIR / "autohack.log"

APP_NAME = "AUTOHACK LAB COMMANDER"
APP_VERSION = __version__
APP_DESCRIPTION = "Centralisateur de commandes de lab — Recon · Web · Passwords · Post-Exploit · Tor · Scrapy"

CATEGORY_LABELS = {
    "system":      "Système / Environnement",
    "network":     "Réseau Local de Lab",
    "tor":         "Tor",
    "privoxy":     "Privoxy",
    "scrapy":      "Scrapy",
    "json_export": "JSON / Export",
    "elastic":     "Elastic / Logs",
    "diagnostic":  "Diagnostic / Debug",
    "recon":       "Reconnaissance & Scan",
    "web_attack":  "Attaque Web",
    "passwords":   "Cracking / Brute-force",
    "post_exploit":"Post-Exploitation",
    "cloud":       "Cloud / Kubernetes",
    "forensics":   "Forensics / DFIR",
    "binary":      "Binary / Reverse",
    "xss":         "XSS Payloads",
}

CATEGORY_ICONS = {
    "system":      "🖥 ",
    "network":     "🌐",
    "tor":         "🧅",
    "privoxy":     "🔀",
    "scrapy":      "🕷 ",
    "json_export": "📦",
    "elastic":     "🔍",
    "diagnostic":  "🔧",
    "recon":       "🔭",
    "web_attack":  "🕸 ",
    "passwords":   "🔑",
    "post_exploit":"💀",
    "cloud":       "☁️",
    "forensics":   "🧬",
    "binary":      "🧩",
    "xss":         "⚡",
}

MAIN_MENU_ITEMS = [
    ("1",  "system",      "Préparation de l'environnement"),
    ("2",  "system",      "Vérification des dépendances"),
    ("3",  "network",     "Services réseau locaux"),
    ("4",  "tor",         "Tor"),
    ("5",  "privoxy",     "Privoxy"),
    ("6",  "scrapy",      "Scrapy"),
    ("7",  "json_export", "Export JSON / fichiers"),
    ("8",  "elastic",     "Elastic / Logs"),
    ("9",  "diagnostic",  "Diagnostic / Debug"),
    ("10", "help",        "Aide pédagogique"),
    ("11", "export",      "Export de toutes les commandes"),
    ("12", "search",      "Recherche de commande"),
]
