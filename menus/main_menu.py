from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.align import Align
from core.catalog import CommandCatalog
from core.executor import CommandExecutor
from core.checker import ToolChecker
from core.config_manager import ConfigManager
from core.session_history import SessionHistory, HISTORY_PATH
from core.favorites import Favorites, FAVORITES_PATH
from core.palette import parse_palette_command
from core.theme import (
    render_banner, pill,
    C_ACCENT, status_bar, help_footer,
    legend_panel,
)
from config.settings import APP_VERSION
from menus.environment import EnvironmentMenu
from menus.dependencies import DependenciesMenu
from menus.network import NetworkMenu
from menus.tor import TorMenu
from menus.privoxy import PrivoxyMenu
from menus.scrapy_menu import ScrapyMenu
from menus.json_export import JsonExportMenu
from menus.elastic import ElasticMenu
from menus.diagnostic import DiagnosticMenu
from menus.help_menu import HelpMenu
from menus.export_all import ExportAllMenu
from menus.search import SearchMenu
from menus.run_all_checks import RunAllChecksMenu
from menus.config_menu import ConfigMenuScreen
from menus.favorites_menu import FavoritesMenu
from menus.recon import ReconMenu
from menus.web_attack import WebAttackMenu
from menus.passwords import PasswordsMenu
from menus.post_exploit import PostExploitMenu
from menus.cloud import CloudMenu
from menus.forensics import ForensicsMenu
from menus.binary import BinaryMenu
from menus.xss_menu import XssMenu
from menus.variables_menu import VariablesMenu
from menus.revshell_menu import RevShellMenu
from menus.hash_id_menu import HashIdMenu
from menus.loot_menu import LootMenu
from menus.encoder_menu import EncoderMenu
from menus.wordlist_menu import WordlistMenu
from menus.port_ref_menu import PortRefMenu
from menus.jwt_menu import JwtMenu
from menus.cidr_menu import CidrMenu
from menus.report_menu import ReportMenu
from menus.toolbox_menu import ToolboxMenu
from core.variables import VariableStore
from core.loot import LootVault

console = Console()

DASHBOARD_WIDTH = 78
MENU_CARD_WIDTH = 62

# (key, icon, label, description, section)
_ITEMS = [
    # LAB
    ("1",  "🖥 ", "Environnement",    "Python · pip · système",        "lab"),
    ("2",  "🔍", "Dépendances",       "Vérifier les outils installés", "lab"),
    ("3",  "🌐", "Réseau local",      "Interfaces · ports · services", "lab"),
    ("4",  "🧅", "Tor",               "Anonymisation · circuits",      "lab"),
    ("5",  "🔀", "Privoxy",           "Proxy HTTP → Tor",              "lab"),
    ("6",  "🕷 ", "Scrapy",           "Crawling · spiders",            "lab"),
    ("7",  "📦", "JSON / Export",     "Fichiers · archives",           "lab"),
    ("8",  "🔍", "Elastic / Logs",    "Elasticsearch · index",         "lab"),
    ("9",  "🔧", "Diagnostic",        "Debug · CPU · mémoire",         "lab"),
    # KALI
    ("16", "🔭", "Recon & Scan",      "nmap · masscan · OSINT",        "kali"),
    ("17", "🕸 ", "Attaque Web",      "nikto · gobuster · sqlmap",     "kali"),
    ("18", "🔑", "Cracking",          "hashcat · john · hydra",        "kali"),
    ("19", "💀", "Post-Exploitation", "shells · pivot · privesc",      "kali"),
    ("20", "⚡", "XSS Payloads",      "1013 payloads classifiés",      "kali"),
    ("21", "☁️ ", "Cloud / K8s",       "trivy · kubectl · prowler",     "kali"),
    ("22", "🧬", "Forensics / DFIR",  "volatility · yara · logs",      "kali"),
    ("23", "🧩", "Binary / Reverse",  "gdb · checksec · ghidra",       "kali"),
    # UTILS
    ("24", "🌐", "Variables",         "$TARGET · $LHOST · $LPORT",     "utils"),
    ("25", "🐚", "Rev Shells",        "Bash · Python · PS · Java",     "utils"),
    ("26", "🔓", "Hash Identifier",   "MD5 · NTLM · bcrypt · SHA",     "utils"),
    ("27", "💎", "Loot Vault",        "Credentials · flags · clés",    "utils"),
    ("28", "🔤", "Encoder",           "Base64 · URL · Hex · NTLM",     "utils"),
    ("29", "📚", "Wordlists",         "Parcourir les listes système",   "utils"),
    ("30", "🔌", "Port Reference",    "85+ ports · pentest notes",     "utils"),
    ("31", "🪙", "JWT Decoder",       "Header · payload · alg check",  "utils"),
    ("32", "📐", "CIDR Calc",         "Subnet · broadcast · hosts",    "utils"),
    ("33", "📝", "Report Generator",  "Markdown · session + loot",     "utils"),
    ("34", "🧰", "Toolbox Installer", "Installer les profils outils",  "utils"),
    # TOOLS
    ("10", "📚", "Aide",              "Documentation pédagogique",     "tools"),
    ("11", "💾", "Export catalogue",  "md · txt · json · html",        "tools"),
    ("12", "🔎", "Recherche",         "Chercher une commande",         "tools"),
    ("13", "🚦", "Vérifications",     "Lancer les checks safe",        "tools"),
    ("14", "⚙️ ", "Configuration",    "Paramètres de l'appli",         "tools"),
]


def _menu_section(items, title: str, checker, catalog) -> Panel:
    t = Table(show_header=False, box=None, padding=(0, 1), expand=True)
    t.add_column("n",     width=4,  style="bold bright_yellow", justify="right")
    t.add_column("icon",  width=3)
    t.add_column("label", min_width=17, style="bold white")
    t.add_column("desc",  style="grey50")

    for key, icon, label, desc, _ in items:
        t.add_row(key, icon, label, desc)

    mapped = {
        "🛠  LAB": ["system", "network", "tor", "privoxy", "scrapy", "json_export", "elastic", "diagnostic"],
        "🗡  KALI": [
            "recon",
            "web_attack",
            "passwords",
            "post_exploit",
            "xss",
            "cloud",
            "forensics",
            "binary",
        ],
        "🔧  UTILS": [],
        "⚙  OUTILS": [],
    }
    cats = mapped.get(title, [])
    if cats:
        cmds = [cmd for cat in cats for cmd in catalog.get_by_category(cat)]
        ready = sum(1 for cmd in cmds if not cmd.get("tool_required") or checker.check(cmd.get("tool_required")))
        subtitle = Text(f" {len(cmds)} cmds · {ready} prêtes ", style="grey70")
    else:
        subtitle = Text(" navigation ", style="grey70")
    title_text = Text(f" {title} ", style="bold black on blue")
    return Panel(t, title=title_text, subtitle=subtitle, subtitle_align="right",
                 title_align="left",
                 border_style="dim blue", padding=(0, 1),
                 width=MENU_CARD_WIDTH, expand=False)


class MainMenu:
    def __init__(self) -> None:
        self._catalog    = CommandCatalog()
        self._var_store  = VariableStore()
        self._loot_vault = LootVault()
        self._executor   = CommandExecutor(var_store=self._var_store)
        self._checker    = ToolChecker(self._catalog)
        self._config     = ConfigManager()
        self._history    = SessionHistory(
            max_size=self._config.get("history_size"),
            persist_path=HISTORY_PATH,
        )
        self._favorites = Favorites(path=FAVORITES_PATH)

        kwargs = dict(
            catalog=self._catalog,
            executor=self._executor,
            checker=self._checker,
            config=self._config,
            history=self._history,
            favorites=self._favorites,
        )
        self._menus = {
            "1":  EnvironmentMenu(**kwargs),
            "2":  DependenciesMenu(**kwargs),
            "3":  NetworkMenu(**kwargs),
            "4":  TorMenu(**kwargs),
            "5":  PrivoxyMenu(**kwargs),
            "6":  ScrapyMenu(**kwargs),
            "7":  JsonExportMenu(**kwargs),
            "8":  ElasticMenu(**kwargs),
            "9":  DiagnosticMenu(**kwargs),
            "10": HelpMenu(**kwargs),
            "11": ExportAllMenu(**kwargs),
            "12": SearchMenu(**kwargs),
            "13": RunAllChecksMenu(**kwargs),
            "14": ConfigMenuScreen(**kwargs),
            "15": FavoritesMenu(**kwargs),
            "16": ReconMenu(**kwargs),
            "17": WebAttackMenu(**kwargs),
            "18": PasswordsMenu(**kwargs),
            "19": PostExploitMenu(**kwargs),
            "20": XssMenu(**kwargs),
            "21": CloudMenu(**kwargs),
            "22": ForensicsMenu(**kwargs),
            "23": BinaryMenu(**kwargs),
            # Utility menus
            "24": VariablesMenu(store=self._var_store),
            "25": RevShellMenu(store=self._var_store),
            "26": HashIdMenu(),
            "27": LootMenu(vault=self._loot_vault),
            "28": EncoderMenu(),
            "29": WordlistMenu(),
            "30": PortRefMenu(),
            "31": JwtMenu(),
            "32": CidrMenu(),
            "33": ReportMenu(history=self._history, vault=self._loot_vault),
            "34": ToolboxMenu(),
        }

    def _open_command(self, cmd_id: str) -> bool:
        cmd = self._catalog.get_by_id(cmd_id)
        if cmd is None:
            return False
        from menus.base import BaseMenu
        jump = BaseMenu(self._catalog, self._executor, self._checker,
                        self._config, self._history, self._favorites)
        console.clear()
        jump._show_command_card(cmd)
        route = jump._action_loop(cmd)
        if route == "quit":
            raise SystemExit(0)
        return True

    @staticmethod
    def _matches_quick_view(view: str, cmd) -> bool:
        tags = {tag.lower() for tag in cmd.get("tags", [])}
        policy = cmd.get("execution_policy")
        tool = cmd.get("tool_required")
        if view == "safe":
            return policy == "safe" or bool(cmd.get("safe_to_run"))
        if view == "ready":
            return True
        if view == "docker":
            return "docker" in tags or tool == "docker"
        if view == "hardware":
            return "hardware" in tags
        if view == "logs":
            return "logs" in tags
        if view == "lab":
            return policy == "lab_only"
        return False

    def _quick_view_commands(self, view: str):
        commands = []
        for cmd in self._catalog.get_all():
            if self._matches_quick_view(view, cmd):
                if view == "ready":
                    tool = cmd.get("tool_required")
                    if tool and not self._checker.check(tool):
                        continue
                commands.append(cmd)
        return commands

    def _open_quick_view(self, view: str) -> bool:
        specs = {
            "safe": ("🟢", "Vue Safe", "commandes passives ou peu risquées", "Aucune commande safe disponible."),
            "ready": ("🧰", "Vue Ready", "outils et commandes immédiatement disponibles", "Aucune commande prête localement."),
            "docker": ("🐳", "Vue Docker", "runtime, conteneurs et images", "Aucune commande Docker disponible."),
            "hardware": ("🖥", "Vue Hardware", "CPU, bus, stockage et capteurs", "Aucune commande hardware disponible."),
            "logs": ("📜", "Vue Logs", "journaux et commandes d'observation", "Aucune commande logs disponible."),
            "lab": ("🧪", "Vue Lab", "commandes réservées au lab contrôlé", "Aucune commande lab-only disponible."),
        }
        spec = specs.get(view)
        if spec is None:
            return False

        icon, title, subtitle, empty_message = spec
        from menus.base import BaseMenu
        jump = BaseMenu(
            self._catalog,
            self._executor,
            self._checker,
            self._config,
            self._history,
            self._favorites,
        )
        jump.run_commands_loop(
            self._quick_view_commands(view),
            title=title,
            icon=icon,
            subtitle_hint=subtitle,
            empty_message=empty_message,
        )
        return True

    def _handle_dashboard_shortcuts(self, choice: str) -> bool:
        if len(choice) == 2 and choice[0] == "f" and choice[1].isdigit():
            idx = int(choice[1]) - 1
            fav_ids = [cmd_id for cmd_id in reversed(self._favorites.all_ids()[-5:])]
            if 0 <= idx < len(fav_ids):
                return self._open_command(fav_ids[idx])
            console.print(f"  [grey50]Raccourci favori invalide : {choice}[/grey50]")
            return True

        if len(choice) == 2 and choice[0] == "a" and choice[1].isdigit():
            idx = int(choice[1]) - 1
            entries = self._history.last(5)
            if 0 <= idx < len(entries):
                return self._open_command(entries[idx]["id"])
            console.print(f"  [grey50]Raccourci activité invalide : {choice}[/grey50]")
            return True

        if choice in {"safe", "ready", "docker", "hardware", "logs", "lab"}:
            return self._open_quick_view(choice)

        return False

    # ── Rendu ─────────────────────────────────────────────────────────────────

    def _render(self) -> None:
        console.clear()
        dashboard_width = min(console.width, DASHBOARD_WIDTH)

        # ── Bannière ──────────────────────────────────────────────────────────
        render_banner()
        sub = Text(justify="center")
        sub.append(f"  v{APP_VERSION}  ", style="dim blue")
        sub.append("·  ", style="grey50")
        sub.append(f"{len(self._catalog.get_all())} commandes  ", style=f"bold {C_ACCENT}")
        sub.append("·  ", style="grey50")
        sub.append(datetime.now().strftime("%a %d %b  %H:%M"), style="grey50")
        console.print(Align.center(sub))
        console.print()

        # ── Status pills ──────────────────────────────────────────────────────
        services = [
            ("tor",           "Tor"),
            ("privoxy",       "Privoxy"),
            ("nmap",          "Nmap"),
            ("masscan",       "Masscan"),
            ("hashcat",       "Hashcat"),
            ("hydra",         "Hydra"),
            ("sqlmap",        "SQLmap"),
            ("elasticsearch", "Elastic"),
        ]
        pills = [pill(n, self._checker.check(t)) for t, n in services]
        console.print(Align.center(Columns(pills, padding=(0, 0), equal=False)))
        console.print()
        status_bar([
            ("Catalogue", f"{len(self._catalog.get_all())} commandes", "bold bright_cyan"),
            ("Favoris", str(len(self._favorites)), "bold bright_yellow"),
            ("Historique", str(len(self._history)), "bold white"),
            ("Mode", "menu principal", "grey70"),
        ], center=True)
        # ── Grille 4 colonnes : LAB | KALI | UTILS | TOOLS ──────────────────────
        lab_items   = [i for i in _ITEMS if i[4] == "lab"]
        kali_items  = [i for i in _ITEMS if i[4] == "kali"]
        utils_items = [i for i in _ITEMS if i[4] == "utils"]
        tools_items = [i for i in _ITEMS if i[4] == "tools"]

        # Status annotations for utils section
        var_count  = len(self._var_store)
        loot_count = len(self._loot_vault)
        for idx, item in enumerate(utils_items):
            if item[0] == "24":
                utils_items[idx] = (item[0], item[1], item[2],
                                    f"{var_count} variable(s) définies", item[4])
            elif item[0] == "27":
                utils_items[idx] = (item[0], item[1], item[2],
                                    f"{loot_count} entrée(s) capturées", item[4])

        # Favoris dans la section tools
        fav_count = len(self._favorites)
        fav_desc  = f"{fav_count} enregistré(s)" if fav_count else "aucun pour l'instant"
        tools_items.append(("15", "⭐", "Favoris", fav_desc, "tools"))
        tools_items.append(("q",  "🚪", "Quitter", "", "tools"))

        col_lab   = _menu_section(lab_items,   "🛠  LAB",    self._checker, self._catalog)
        col_kali  = _menu_section(kali_items,  "🗡  KALI",   self._checker, self._catalog)
        col_utils = _menu_section(utils_items, "🔧  UTILS",  self._checker, self._catalog)
        col_tools = _menu_section(tools_items, "⚙  OUTILS",  self._checker, self._catalog)

        menu_columns = Columns(
            [col_lab, col_kali, col_utils, col_tools],
            padding=(0, 1),
            equal=False,
            expand=False,
        )
        console.print(Align.center(menu_columns))
        console.print()

        # ── Historique compact ────────────────────────────────────────────────
        if self._config.get("show_history_in_menu") and len(self._history) > 0:
            self._render_history()

        legend_panel([
            ("[green]safe[/green]", "lecture seule ou exécution peu risquée"),
            ("[yellow]dry-run[/yellow]", "commande sensible à relire avant usage"),
            ("[red]danger[/red]", "confirmation double requise — cible à spécifier"),
        ], title="Profils", width=dashboard_width)

        help_footer([
            ("1-34", "ouvrir une section"),
            ("q", "quitter"),
        ], title="Accès rapide", width=dashboard_width)

    def _render_history(self) -> None:
        entries = self._history.last(4)
        t = Table(show_header=False, box=None, padding=(0, 1), expand=False)
        t.add_column("●",    width=2)
        t.add_column("time", style="grey50", width=7)
        t.add_column("cmd",  style="dim magenta")

        for e in entries:
            if e["dry_run"]:
                dot = Text("●", style="bright_blue")
            elif e["exit_code"] == 0:
                dot = Text("●", style="bright_green")
            else:
                dot = Text("●", style="bright_red")
            t.add_row(dot, e["timestamp"], e["command"][:60])

        console.print(Panel(
            t,
            title=Text(" Historique de session ", style="grey50"),
            title_align="left",
            border_style="grey23",
            padding=(0, 1),
        ))
        console.print()

    def _show_palette_help(self) -> None:
        help_footer([
            (":search", "ouvrir la recherche"),
            (":favorites", "ouvrir les favoris"),
            (":config", "ouvrir la configuration"),
            (":checks", "lancer les vérifications"),
            (":help", "ouvrir l'aide"),
            (":quit", "quitter"),
            (":sys_001", "ouvrir une commande par ID"),
        ], title="Palette")

    def _handle_palette_command(self, raw: str) -> bool:
        parsed = parse_palette_command(raw.strip())
        if not parsed:
            return False

        action, argument = parsed
        if action == "palette":
            self._show_palette_help()
            return True
        if action == "quit":
            raise SystemExit(0)
        if action == "command":
            cmd = self._catalog.get_by_id(argument)
            if cmd is None:
                console.print(f"  [grey50]ID introuvable dans la palette : {argument}[/grey50]")
                return True
            from menus.base import BaseMenu
            jump = BaseMenu(self._catalog, self._executor, self._checker,
                            self._config, self._history, self._favorites)
            console.clear()
            jump._show_command_card(cmd)
            route = jump._action_loop(cmd)
            if route == "quit":
                raise SystemExit(0)
            return True

        route = {
            "search": "12",
            "favorites": "15",
            "config": "14",
            "checks": "13",
            "help": "10",
            "home": None,
        }.get(action, "")
        if route is None:
            return True
        if route:
            self._menus[route].show()
            return True
        return False

    # ── Boucle principale ─────────────────────────────────────────────────────

    def run(self) -> None:
        from core.logger import ActionLogger, apply_log_level
        apply_log_level(self._config.get("log_level"))
        ActionLogger.log_event("Session démarrée")

        while True:
            self._render()

            choice = console.input(
                f"  [bold {C_ACCENT}]›[/bold {C_ACCENT}] "
            ).strip().lower()

            if self._handle_palette_command(choice):
                continue
            if self._handle_dashboard_shortcuts(choice):
                continue

            if choice == "q":
                console.print()
                bye = Text(justify="center")
                bye.append("  Session terminée  ", style="bold white on blue")
                bye.append(f"  {len(self._history)} commande(s) · logs/autohack.log  ",
                           style="grey50")
                console.print(Panel(Align.center(bye), border_style="dim blue",
                                    padding=(1, 4)))
                console.print()
                ActionLogger.log_event("Session terminée")
                break

            if choice in self._menus:
                self._menus[choice].show()
            elif (cmd := self._catalog.get_by_id(choice)) is not None:
                from menus.base import BaseMenu
                _jump = BaseMenu(self._catalog, self._executor, self._checker,
                                 self._config, self._history, self._favorites)
                console.clear()
                _jump._show_command_card(cmd)
                route = _jump._action_loop(cmd)
                if route == "quit":
                    raise SystemExit(0)
            else:
                console.print(
                    "  [grey50]Choix invalide — entrez 1–34, un ID (ex: rec_001), ou q.[/grey50]"
                )
