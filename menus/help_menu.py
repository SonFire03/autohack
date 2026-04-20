from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from menus.base import BaseMenu
from config.settings import CATEGORY_LABELS, CATEGORY_ICONS

console = Console()

GLOSSARY = {
    "Spider":       "Classe Python qui définit comment naviguer un site et extraire des données dans Scrapy.",
    "Items":        "Conteneurs de données structurées dans Scrapy, similaires à des dict typés.",
    "Pipelines":    "Chaîne de traitement des items après extraction : nettoyage, validation, stockage.",
    "Middlewares":  "Couche intermédiaire qui intercepte les requêtes/réponses dans Scrapy.",
    "Settings":     "Fichier de configuration global d'un projet Scrapy (delays, user-agent, etc.).",
    "SOCKS5":       "Protocole proxy de niveau 4 utilisé par Tor pour tunneliser le trafic TCP.",
    "torrc":        "Fichier de configuration de Tor situé dans /etc/tor/torrc.",
    "Circuit Tor":  "Chemin chiffré à 3 nœuds (guard→middle→exit) que Tor construit pour chaque connexion.",
    "Privoxy":      "Proxy HTTP qui peut être chaîné avec Tor pour convertir HTTP→SOCKS5.",
    "Index ES":     "Equivalent Elasticsearch d'une 'table' SQL. Contient des documents JSON.",
    "Document ES":  "Unité de données dans Elasticsearch, stockée en JSON avec un _id unique.",
    "Shard ES":     "Fragment d'un index Elasticsearch pour la distribution des données.",
    "systemctl":    "Outil de contrôle des services systemd (start/stop/status/enable/disable).",
    "journalctl":   "Outil de lecture des journaux systemd, remplace syslog.",
    "subprocess":   "Module Python pour exécuter des commandes shell depuis un script.",
    "SOCKS5 proxy": "Port 9050 de Tor — permet de router n'importe quel trafic TCP via Tor.",
    "HTTP proxy":   "Port 8118 de Privoxy — accepte les requêtes HTTP et les reroute.",
}


class HelpMenu(BaseMenu):
    TITLE = "Aide pédagogique"
    CATEGORY = "system"

    def show(self) -> None:
        while True:
            self._header("📚 Aide pédagogique")

            table = Table(show_header=False, box=box.SIMPLE, expand=False)
            table.add_column("Option", style="bold yellow", width=4)
            table.add_column("Description", style="white")
            table.add_row("1", "Glossaire des termes techniques")
            table.add_row("2", "Vue d'ensemble des catégories")
            table.add_row("3", "Architecture Tor + Privoxy expliquée")
            table.add_row("4", "Concepts Scrapy (spider/items/pipelines)")
            table.add_row("5", "Guide de démarrage rapide du lab")
            table.add_row("b", "Retour au menu principal")
            console.print(table)

            choice = console.input("[bold yellow]Choix > [/bold yellow]").strip().lower()

            if choice == "1":
                self._show_glossary()
            elif choice == "2":
                self._show_categories_overview()
            elif choice == "3":
                self._show_tor_privoxy_architecture()
            elif choice == "4":
                self._show_scrapy_concepts()
            elif choice == "5":
                self._show_quickstart()
            elif choice == "b":
                break
            else:
                console.print("[dim]Choix invalide.[/dim]")

            if choice in ("1", "2", "3", "4", "5"):
                console.input("\n[dim]Appuyez sur Entrée pour continuer…[/dim]")

    def _show_glossary(self) -> None:
        table = Table(
            title="Glossaire technique",
            show_header=True,
            header_style="bold cyan",
            box=box.ROUNDED,
            expand=True,
        )
        table.add_column("Terme", style="bold yellow", min_width=16)
        table.add_column("Définition", style="white")
        for term, definition in GLOSSARY.items():
            table.add_row(term, definition)
        console.print()
        console.print(table)

    def _show_categories_overview(self) -> None:
        text = Text()
        for cat, label in CATEGORY_LABELS.items():
            icon = CATEGORY_ICONS.get(cat, "")
            count = len(self._catalog.get_by_category(cat))
            text.append(f"  {icon}  ", style="bold")
            text.append(f"{label}", style="bold white")
            text.append(f"  ({count} commandes)\n", style="dim")
        console.print(Panel(text, title="[bold]Catégories disponibles[/bold]", border_style="cyan"))

    def _show_tor_privoxy_architecture(self) -> None:
        content = (
            "[bold cyan]Architecture Tor + Privoxy :[/bold cyan]\n\n"
            "[white]Application[/white] → [yellow]HTTP[/yellow] → "
            "[bold]Privoxy :8118[/bold] → [yellow]SOCKS5[/yellow] → "
            "[bold]Tor :9050[/bold] → [green]Réseau Tor[/green]\n\n"
            "[dim]• Privoxy accepte les requêtes HTTP et les forward via SOCKS5 vers Tor\n"
            "• Tor construit un circuit chiffré à 3 nœuds vers la destination\n"
            "• Configuration Privoxy clé : forward-socks5 / 127.0.0.1:9050 .\n"
            "• Vérification : curl -x http://127.0.0.1:8118 <URL_CIBLE>[/dim]"
        )
        console.print(Panel(content, title="[bold]Tor + Privoxy[/bold]", border_style="cyan"))

    def _show_scrapy_concepts(self) -> None:
        content = (
            "[bold cyan]Composants d'un projet Scrapy :[/bold cyan]\n\n"
            "[bold yellow]Spider[/bold yellow]      : Définit les URLs de départ, comment naviguer et extraire\n"
            "[bold yellow]Items[/bold yellow]       : Conteneurs de données (comme des dataclasses)\n"
            "[bold yellow]Pipelines[/bold yellow]   : Traitement post-extraction (nettoyage, stockage, DB)\n"
            "[bold yellow]Middlewares[/bold yellow] : Intercepteurs de requêtes/réponses (headers, retry, proxy)\n"
            "[bold yellow]Settings[/bold yellow]    : Config globale (DOWNLOAD_DELAY, USER_AGENT, PROXIES)\n\n"
            "[dim]Flux : Spider → Request → Middleware → Downloader → Response → Parser → Items → Pipeline[/dim]"
        )
        console.print(Panel(content, title="[bold]Concepts Scrapy[/bold]", border_style="yellow"))

    def _show_quickstart(self) -> None:
        content = (
            "[bold white]Démarrage rapide du lab :[/bold white]\n\n"
            "[bold cyan]1.[/bold cyan] Vérifier les dépendances   → Menu [2]\n"
            "[bold cyan]2.[/bold cyan] Démarrer Tor               → Menu [4] → systemctl start tor\n"
            "[bold cyan]3.[/bold cyan] Démarrer Privoxy           → Menu [5] → systemctl start privoxy\n"
            "[bold cyan]4.[/bold cyan] Tester la chaîne proxy     → Menu [3] → Test proxy complet\n"
            "[bold cyan]5.[/bold cyan] Créer projet Scrapy        → Menu [6] → scrapy startproject\n"
            "[bold cyan]6.[/bold cyan] Exporter les résultats     → Menu [7] ou [11]\n\n"
            "[dim]Conseil : commencez toujours par [2] Vérification des dépendances.[/dim]"
        )
        console.print(Panel(content, title="[bold]Guide de démarrage[/bold]", border_style="green"))
