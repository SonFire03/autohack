from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.syntax import Syntax
from rich.columns import Columns
from rich.rule import Rule
from core.catalog import CommandCatalog
from core.executor import CommandExecutor
from core.checker import ToolChecker
from core.config_manager import ConfigManager
from core.session_history import SessionHistory
from core.favorites import Favorites
from core.palette import parse_palette_command
from core.theme import (
    page_header, C_ACCENT, C_OK, C_DANGER, C_WARN,
    C_PRIMARY, BOX_TABLE, status_bar, help_footer, metric_cards, legend_panel,
)
from config.settings import CATEGORY_ICONS, CATEGORY_LABELS

console = Console()

_ACTIONS = [
    ("r", "Run",        "bright_green"),
    ("d", "Dry-run",    "bright_blue"),
    ("e", "Expliquer",  "bright_cyan"),
    ("c", "Copier",     "bright_yellow"),
    ("s", "Sauvegarder","magenta"),
    ("p", "Prérequis",  "white"),
    ("f", "Favori",     "yellow"),
    ("b", "Retour",     "grey50"),
]


def _render_action_bar() -> None:
    line = Text("  ")
    for key, label, color in _ACTIONS:
        line.append(f" {key.upper()} ", style=f"bold black on {color}")
        line.append(f" {label}  ", style="grey50")
    console.print(line)
    console.print()


def _risk_style(cmd: Dict[str, Any]) -> str:
    if cmd.get("dangerous"):
        return C_DANGER
    if cmd.get("requires_sudo"):
        return C_WARN
    return C_OK


class BaseMenu:
    CATEGORY: str = ""
    TITLE: str    = ""

    def __init__(
        self,
        catalog: CommandCatalog,
        executor: CommandExecutor,
        checker: ToolChecker,
        config: Optional[ConfigManager] = None,
        history: Optional[SessionHistory] = None,
        favorites: Optional[Favorites] = None,
    ) -> None:
        self._catalog   = catalog
        self._executor  = executor
        self._checker   = checker
        self._config    = config   or ConfigManager()
        self._history   = history  or SessionHistory()
        self._favorites = favorites or Favorites()

    # ── En-tête ───────────────────────────────────────────────────────────────

    def _header(self, title: str, subtitle: str = "", breadcrumb: str = "") -> None:
        page_header(title, subtitle=subtitle, breadcrumb=breadcrumb)

    def _menu_kwargs(self) -> Dict[str, Any]:
        return {
            "catalog": self._catalog,
            "executor": self._executor,
            "checker": self._checker,
            "config": self._config,
            "history": self._history,
            "favorites": self._favorites,
        }

    def _show_palette_help(self) -> None:
        help_footer([
            (":search", "ouvrir la recherche globale"),
            (":favorites", "ouvrir les favoris"),
            (":config", "ouvrir la configuration"),
            (":checks", "lancer les vérifications"),
            (":help", "ouvrir l'aide"),
            (":home", "retour au menu principal"),
            (":quit", "quitter l'application"),
            (":sys_001", "ouvrir directement une commande par ID"),
        ], title="Palette")

    def _handle_palette_command(self, raw: str) -> Optional[str]:
        parsed = parse_palette_command(raw.strip())
        if not parsed:
            return None

        action, argument = parsed
        if action == "palette":
            self._show_palette_help()
            return "handled"
        if action == "home":
            return "home"
        if action == "quit":
            return "quit"
        if action == "command":
            cmd = self._catalog.get_by_id(argument)
            if cmd is None:
                console.print(f"  [grey50]ID introuvable dans la palette : {argument}[/grey50]")
                return "handled"
            self._header(f"⌘  {cmd['name']}", subtitle=cmd["id"])
            self._show_command_card(cmd)
            self._action_loop(cmd)
            return "handled"

        if action == "search":
            from menus.search import SearchMenu
            SearchMenu(**self._menu_kwargs()).show()
            return "handled"
        if action == "favorites":
            from menus.favorites_menu import FavoritesMenu
            FavoritesMenu(**self._menu_kwargs()).show()
            return "handled"
        if action == "config":
            from menus.config_menu import ConfigMenuScreen
            ConfigMenuScreen(**self._menu_kwargs()).show()
            return "handled"
        if action == "checks":
            from menus.run_all_checks import RunAllChecksMenu
            RunAllChecksMenu(**self._menu_kwargs()).show()
            return "handled"
        if action == "help":
            from menus.help_menu import HelpMenu
            HelpMenu(**self._menu_kwargs()).show()
            return "handled"
        return None

    @staticmethod
    def _command_preview(command: str, max_len: int = 50) -> str:
        return command[:max_len] + ("…" if len(command) > max_len else "")

    @staticmethod
    def _clamp_focus(focus: int, total: int) -> int:
        if total <= 0:
            return 0
        return max(0, min(focus, total - 1))

    @staticmethod
    def _safety_label(cmd: Dict[str, Any]) -> Text:
        policy = cmd.get("execution_policy")
        if policy == "dry_run_only":
            return Text("dry-run", style="bold black on bright_yellow")
        if cmd.get("dangerous") or policy == "lab_only":
            return Text("danger", style="bold white on bright_red")
        if cmd.get("requires_sudo"):
            return Text("sudo", style="bold black on bright_yellow")
        if cmd.get("safe_to_run"):
            return Text("safe", style="bold black on bright_green")
        return Text("manual", style="bold white on grey23")

    def _readiness_label(self, tool: str) -> Text:
        if not tool:
            return Text("intégré", style="bold black on bright_green")
        available = self._checker.check(tool)
        if available:
            return Text("prêt", style="bold black on bright_green")
        return Text("manquant", style="bold white on bright_red")

    def _build_command_preview_panel(self, cmd: Dict[str, Any], title: str = "Aperçu") -> Panel:
        tool = cmd.get("tool_required", "")
        preview = Table(show_header=False, box=None, padding=(0, 1), expand=True)
        preview.add_column("k", style="grey50", width=10, no_wrap=True)
        preview.add_column("v", style="white", min_width=20)
        preview.add_row("ID", Text(cmd["id"], style="bold bright_cyan"))
        preview.add_row("Nom", Text(cmd["name"], style="bold white"))
        preview.add_row("Profil", self._safety_label(cmd))
        preview.add_row("État", self._readiness_label(tool))
        preview.add_row("Commande", Text(self._command_preview(cmd["command"], max_len=68), style="magenta"))
        preview.add_row("But", Text(cmd.get("purpose") or cmd.get("description") or "—", style="grey70"))
        return Panel(
            preview,
            title=f" {title} ",
            title_align="left",
            border_style="cyan",
            padding=(0, 1),
            expand=True,
        )

    def _render_command_preview_panel(self, cmd: Dict[str, Any], title: str = "Aperçu") -> None:
        console.print(self._build_command_preview_panel(cmd, title=title))
        console.print()

    def _render_collection_status(
        self,
        commands: List[Dict[str, Any]],
        page: int,
        page_size: int,
        active_filter: Optional[str] = None,
    ) -> None:
        total = len(commands)
        total_pages = max(1, (total + page_size - 1) // page_size)
        installed = sum(
            1 for cmd in commands
            if not cmd.get("tool_required") or self._checker.check(cmd.get("tool_required", ""))
        )
        status_bar([
            ("Vue", f"page {page + 1}/{total_pages}", "bold white"),
            ("Résultats", str(total), "bold bright_cyan"),
            ("Outils prêts", f"{installed}/{total}", "bold bright_green" if installed == total else "bold bright_yellow"),
            ("Filtre", active_filter or "aucun", "bold bright_magenta" if active_filter else "grey70"),
        ])

    # ── Table de commandes ────────────────────────────────────────────────────

    def _build_commands_table(
        self,
        commands: List[Dict[str, Any]],
        page: int,
        page_size: int,
        focused_index: Optional[int] = None,
    ) -> tuple[Table, List[Dict[str, Any]], int]:
        total       = len(commands)
        total_pages = max(1, (total + page_size - 1) // page_size)
        page        = max(0, min(page, total_pages - 1))
        start       = page * page_size
        page_cmds   = commands[start:start + page_size]

        t = Table(
            show_header=True,
            header_style=f"bold {C_ACCENT}",
            box=BOX_TABLE,
            expand=True,
            row_styles=["", "on grey3"],
            border_style="dim blue",
        )
        t.add_column("#",        width=6,  style="bold bright_yellow", justify="right")
        t.add_column("Nom",      min_width=22, style=C_PRIMARY)
        t.add_column("Commande", min_width=32, style="magenta")
        t.add_column("Profil",   width=10, style="white")
        t.add_column("État",     width=10, style="white")
        t.add_column("Outil",    width=14, style="cyan")

        for i, cmd in enumerate(page_cmds, start + 1):
            tool      = cmd.get("tool_required", "")
            is_focused = focused_index == (i - 1)

            name_cell = Text(cmd["name"])
            if cmd.get("dangerous"):
                name_cell.append("  ⚠", style="bright_red")
            elif cmd.get("requires_sudo"):
                name_cell.append("  🔐", style="bright_yellow")

            index_cell = f"› {i}" if is_focused else str(i)

            t.add_row(
                index_cell,
                name_cell,
                self._command_preview(cmd["command"]),
                self._safety_label(cmd),
                self._readiness_label(tool),
                tool or "—",
                style="bold on grey11" if is_focused else None,
            )

        return t, page_cmds, total_pages

    def _render_commands_table(
        self,
        commands: List[Dict[str, Any]],
        page: int,
        page_size: int,
        focused_index: Optional[int] = None,
    ) -> tuple[List[Dict[str, Any]], int]:
        table, page_cmds, total_pages = self._build_commands_table(
            commands, page, page_size, focused_index=focused_index
        )
        console.print(table)
        if total_pages > 1:
            nav = []
            if page > 0:
                nav.append("[bold]p[/bold] précédente")
            if page < total_pages - 1:
                nav.append("[bold]n[/bold] suivante")
            suffix = "  ·  " + "  ".join(nav) if nav else ""
            console.print(f"  [grey50]Page {page + 1}/{total_pages}  ·  {len(commands)} commandes{suffix}[/grey50]")
        return page_cmds, total_pages

    # ── Fiche commande ────────────────────────────────────────────────────────

    def _show_command_card(self, cmd: Dict[str, Any]) -> None:
        tool      = cmd.get("tool_required", "")
        available = self._checker.check(tool) if tool else True
        is_fav    = self._favorites.is_favorite(cmd["id"])
        cat       = cmd.get("category", "")
        cat_label = CATEGORY_LABELS.get(cat, cat)
        cat_icon  = CATEGORY_ICONS.get(cat, "")

        # ── Titre de fiche ────────────────────────────────────────────────────
        title_line = Text("  ")
        title_line.append(f" {cat_icon} {cat_label} ", style="bold white on blue")
        title_line.append("  ›  ", style="grey50")
        title_line.append(cmd["name"], style="bold white")
        if is_fav:
            title_line.append("  ⭐", style="bright_yellow")
        console.print(title_line)
        console.print(Rule(style="dim blue"))
        console.print()

        status_bar([
            ("ID", cmd["id"], "bold bright_cyan"),
            ("Profil", self._safety_label(cmd).plain, "bold bright_red" if cmd.get("dangerous") else "bold bright_yellow" if cmd.get("requires_sudo") else "bold bright_green" if cmd.get("safe_to_run") else "grey70"),
            ("État", "prêt" if available or not tool else "outil manquant", "bold bright_green" if available or not tool else "bold bright_red"),
            ("Favori", "oui" if is_fav else "non", "bold bright_yellow" if is_fav else "grey70"),
        ])
        metric_cards([
            ("Profil", self._safety_label(cmd).plain, "bold bright_red" if cmd.get("execution_policy") == "lab_only" or cmd.get("dangerous") else "bold bright_yellow" if cmd.get("execution_policy") == "dry_run_only" or cmd.get("requires_sudo") else "bold bright_green"),
            ("Outil", tool or "intégré", "bold bright_green" if available or not tool else "bold bright_red"),
            ("Tags", str(len(cmd.get("tags", []))), "bold bright_cyan"),
            ("Favori", "oui" if is_fav else "non", "bold bright_yellow" if is_fav else "bold white"),
        ])

        # ── Commande en syntaxe monokai ───────────────────────────────────────
        syntax = Syntax(cmd["command"], "bash", theme="monokai",
                        word_wrap=True, padding=(1, 3))
        console.print(Panel(syntax, border_style="magenta",
                            padding=(0, 0), expand=False))
        console.print()

        runbook = Table(show_header=False, box=None, padding=(0, 1), expand=True)
        runbook.add_column("k", style="grey50", width=12, no_wrap=True)
        runbook.add_column("v", style="white", min_width=20)
        runbook.add_row("Commande", Text(self._command_preview(cmd["command"], max_len=72), style="magenta"))
        runbook.add_row("Exécution", self._readiness_label(tool))
        runbook.add_row("Profil", self._safety_label(cmd))
        runbook.add_row("Sortie", Text(cmd.get("expected_output", "—"), style="grey70"))

        context = Table(show_header=False, box=None, padding=(0, 1), expand=True)
        context.add_column("k", style="grey50", width=12, no_wrap=True)
        context.add_column("v", style="white", min_width=18)
        context.add_row("ID", Text(cmd["id"], style="grey50"))
        context.add_row("Catég.", f"{cat_icon} {cat_label}")
        context.add_row("Outil", (Text(f"{tool}  ✔", style="bright_green")
                                   if tool and available
                                   else Text(f"{tool}  ✘  {self._checker.install_hint(tool)}", style="bright_red")
                                   if tool
                                   else Text("aucun", style="grey50")))
        if cmd.get("description"):
            context.add_row("Résumé", Text(cmd["description"], style="grey70"))

        prereq = Table(show_header=False, box=None, padding=(0, 1), expand=True)
        prereq.add_column("k", style="grey50", width=3, no_wrap=True)
        prereq.add_column("v", style="white", min_width=18)
        prerequisites = cmd.get("prerequisites", [])
        if prerequisites:
            for item in prerequisites[:6]:
                prereq.add_row("•", Text(item, style="white"))
        else:
            prereq.add_row("•", Text("Aucun prérequis particulier", style="grey70"))

        security = Table(show_header=False, box=None, padding=(0, 1), expand=True)
        security.add_column("k", style="grey50", width=12, no_wrap=True)
        security.add_column("v", style="white", min_width=18)
        security.add_row("Risques", Text(cmd.get("risks", "—"), style=_risk_style(cmd)))
        security.add_row("Sudo", Text("oui" if cmd.get("requires_sudo") else "non",
                                      style="bold bright_yellow" if cmd.get("requires_sudo") else "grey70"))
        security.add_row("Danger", Text("oui" if cmd.get("dangerous") else "non",
                                        style="bold bright_red" if cmd.get("dangerous") else "grey70"))
        security.add_row("Politique", self._safety_label(cmd))

        tags = cmd.get("tags", [])
        tags_table = Table(show_header=False, box=None, padding=(0, 1), expand=True)
        tags_table.add_column("v", style="white")
        if tags:
            tag_line = Text()
            for tg in tags:
                tag_line.append(f" {tg} ", style="bold black on grey30")
                tag_line.append(" ")
            tags_table.add_row(tag_line)
        else:
            tags_table.add_row(Text("Aucun tag", style="grey70"))

        objective = Panel(
            Text(cmd.get("purpose", "—"), style="white"),
            border_style="cyan",
            padding=(0, 1),
            expand=True,
            title=" Objectif ",
            title_align="left",
        )
        run_panel = Panel(runbook, border_style="grey23", padding=(0, 1), expand=True, title=" Exécution ", title_align="left")
        ctx_panel = Panel(context, border_style="grey23", padding=(0, 1), expand=True, title=" Contexte ", title_align="left")
        pre_panel = Panel(prereq, border_style="grey23", padding=(0, 1), expand=True, title=" Prérequis ", title_align="left")
        sec_panel = Panel(security, border_style="grey23", padding=(0, 1), expand=True, title=" Sécurité ", title_align="left")
        tag_panel = Panel(tags_table, border_style="grey23", padding=(0, 1), expand=True, title=" Tags ", title_align="left")

        console.print(Columns([objective], equal=True, padding=(0, 1), expand=True))
        console.print(Columns([run_panel, ctx_panel], equal=True, padding=(0, 1), expand=True))
        console.print(Columns([pre_panel, sec_panel, tag_panel], equal=True, padding=(0, 1), expand=True))
        console.print()
        legend_panel([
            ("safe", "commande passive ou peu risquée"),
            ("dry-run", "commande sensible à relire avant usage"),
            ("danger", "confirmation double requise — cible à spécifier"),
            ("prêt", "outil détecté localement"),
        ], title="Lecture")

        # ── Barre d'actions ───────────────────────────────────────────────────
        _render_action_bar()
        help_footer([
            ("r", "exécuter"),
            ("d", "dry-run"),
            ("e", "explication"),
            ("p", "prérequis"),
            ("f", "basculer favori"),
            ("b", "retour"),
        ], title="Actions")

    # ── Boucle d'actions ─────────────────────────────────────────────────────

    def _action_loop(self, cmd: Dict[str, Any]) -> Optional[str]:
        while True:
            choice = console.input(
                f"  [bold {C_ACCENT}]›[/bold {C_ACCENT}] "
            ).strip().lower()

            palette = self._handle_palette_command(choice)
            if palette == "handled":
                self._show_command_card(cmd)
                continue
            if palette == "home":
                return "home"
            if palette == "quit":
                return "quit"

            if choice == "r":
                skip = (cmd.get("safe_to_run", False)
                        and not self._config.get("confirm_safe_commands"))
                code = self._executor.confirm_and_run(cmd, skip_confirm=skip)
                if code is not None:
                    self._history.add(cmd, code)
                console.input("\n  [grey50]Entrée pour continuer…[/grey50]")

            elif choice == "d":
                self._executor.dry_run(cmd)
                self._history.add(cmd, 0, dry_run=True)
                console.input("\n  [grey50]Entrée pour continuer…[/grey50]")

            elif choice == "e":
                self._show_explanation(cmd)
                console.input("\n  [grey50]Entrée pour continuer…[/grey50]")

            elif choice == "c":
                self._executor.copy_to_clipboard(cmd)
                console.input("\n  [grey50]Entrée pour continuer…[/grey50]")

            elif choice == "s":
                path, save_code = self._executor.run_and_save(
                    cmd, export_dir=self._config.get("export_dir")
                )
                if path is not None:
                    self._history.add(cmd, save_code)
                console.input("\n  [grey50]Entrée pour continuer…[/grey50]")

            elif choice == "p":
                self._show_prerequisites(cmd)
                console.input("\n  [grey50]Entrée pour continuer…[/grey50]")

            elif choice == "f":
                added = self._favorites.toggle(cmd["id"])
                if added:
                    console.print(f"  [bright_yellow]⭐ Ajouté aux favoris : {cmd['id']}[/bright_yellow]")
                else:
                    console.print(f"  [grey50]Retiré des favoris : {cmd['id']}[/grey50]")
                console.input("\n  [grey50]Entrée pour continuer…[/grey50]")

            elif choice == "b":
                return None
            else:
                console.print("  [grey50]Touche invalide.[/grey50]")
                _render_action_bar()

    # ── Panneaux détails ──────────────────────────────────────────────────────

    def _show_explanation(self, cmd: Dict[str, Any]) -> None:
        t = Table(show_header=False, box=None, padding=(0, 2), expand=False)
        t.add_column("k", style="grey50",  width=14, no_wrap=True)
        t.add_column("v", style="white",   min_width=40)
        t.add_row("📖 But",     cmd.get("purpose",         "Non documenté"))
        t.add_row("📤 Sortie",  cmd.get("expected_output", "Non documenté"))
        t.add_row("⚡ Risques", Text(cmd.get("risks", "Non documenté"),
                                     style=_risk_style(cmd)))
        console.print(Panel(t, title=Text(" Explication pédagogique ", style="grey50"),
                            title_align="left",
                            border_style="cyan", padding=(1, 1)))

    def _show_prerequisites(self, cmd: Dict[str, Any]) -> None:
        prereqs = cmd.get("prerequisites", [])
        tool    = cmd.get("tool_required", "")
        lines   = Text()
        if prereqs:
            for p in prereqs:
                lines.append(f"  ▸ {p}\n", style="white")
        else:
            lines.append("  Aucun prérequis particulier.\n", style="grey50")
        if tool:
            ok     = self._checker.check(tool)
            status = Text("✔ installé" if ok else f"✘ manquant — {self._checker.install_hint(tool)}",
                          style="bright_green" if ok else "bright_red")
            lines.append(f"\n  Outil requis : {tool}  ")
            lines.append_text(status)
            lines.append("\n")
        console.print(Panel(lines, title=Text(" Prérequis ", style="grey50"),
                            title_align="left",
                            border_style="grey23", padding=(1, 2)))

    # ── Boucle catégorie ──────────────────────────────────────────────────────

    def run_loop(self, category: str, title: str) -> None:
        all_commands = self._catalog.get_by_category(category)
        icon         = CATEGORY_ICONS.get(category, "")
        self.run_commands_loop(
            all_commands,
            title=title,
            icon=icon,
        )

    def run_commands_loop(
        self,
        all_commands: List[Dict[str, Any]],
        title: str,
        icon: str = "",
        subtitle_hint: Optional[str] = None,
        empty_message: str = "Aucune commande disponible.",
    ) -> None:
        page_size    = self._config.get("page_size")
        page         = 0
        focus        = 0
        active_filter: Optional[str] = None

        while True:
            if active_filter:
                cat_ids  = {c["id"] for c in all_commands}
                commands = [c for c in self._catalog.search(active_filter)
                            if c["id"] in cat_ids]
                subtitle = f'🔎 "{active_filter}"  ·  {len(commands)} résultat(s)'
            else:
                commands = all_commands
                subtitle = subtitle_hint or f"{len(commands)} commandes"

            focus = self._clamp_focus(focus, len(commands))
            page = (focus // page_size) if commands else 0
            self._header(f"{icon}  {title}", subtitle=subtitle)
            self._render_collection_status(commands, page, page_size, active_filter)
            table, page_cmds, total_pages = self._build_commands_table(commands, page, page_size, focused_index=focus)
            if commands:
                console.print(Columns([
                    Panel(table, title=" Liste ", title_align="left", border_style="dim blue", padding=(0, 0), expand=True),
                    self._build_command_preview_panel(commands[focus], title="Élément en focus"),
                ], equal=True, expand=True, padding=(0, 1)))
                console.print()
            else:
                console.print(Panel(
                    Text(empty_message, style="grey70"),
                    title=" Liste ",
                    title_align="left",
                    border_style="dim blue",
                    padding=(1, 2),
                    expand=True,
                ))

            help_footer([
                ("j / k", "descendre / monter"),
                ("Entrée ou o", "ouvrir l'élément en focus"),
                ("numéro", "ouvrir directement"),
                ("v<num>", "aperçu rapide sans ouvrir"),
                ("/mot", "filtrer la catégorie"),
                ("/", "effacer le filtre"),
                ("n / p", "changer de page"),
                (":", "palette globale"),
                ("b", "retour"),
            ], title="Navigation")

            choice = console.input(
                f"  [bold {C_ACCENT}]›[/bold {C_ACCENT}] "
            ).strip()

            palette = self._handle_palette_command(choice)
            if palette == "handled":
                continue
            if palette == "home":
                break
            if palette == "quit":
                raise SystemExit(0)

            if choice.startswith("/"):
                kw = choice[1:].lower().strip()
                active_filter = kw if kw else None
                page = 0
                focus = 0
                continue

            cl = choice.lower()
            if cl == "b":
                break
            elif cl == "j" and commands:
                focus = min(focus + 1, len(commands) - 1)
            elif cl == "k" and commands:
                focus = max(focus - 1, 0)
            elif cl == "n" and page < total_pages - 1:
                page += 1
                focus = min(page * page_size, len(commands) - 1)
            elif cl == "p" and page > 0:
                page -= 1
                focus = page * page_size
            elif cl in {"", "o"} and commands:
                cmd = commands[focus]
                self._header(f"{icon}  {title}", breadcrumb="", subtitle=cmd["name"])
                self._show_command_card(cmd)
                route = self._action_loop(cmd)
                if route == "home":
                    break
                if route == "quit":
                    raise SystemExit(0)
            elif cl.startswith("v") and cl[1:].isdigit():
                idx = int(cl[1:]) - 1
                if 0 <= idx < len(commands):
                    focus = idx
                    self._header(f"{icon}  {title}", subtitle=f"Aperçu · {commands[idx]['name']}")
                    self._render_command_preview_panel(commands[idx], title="Aperçu rapide")
                    console.input("  [grey50]Entrée pour revenir à la liste…[/grey50]")
                else:
                    console.print(f"  [grey50]Numéro hors plage (1–{len(commands)}).[/grey50]")
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(commands):
                    focus = idx
                    cmd = commands[idx]
                    self._header(f"{icon}  {title}", breadcrumb="", subtitle=cmd["name"])
                    self._show_command_card(cmd)
                    route = self._action_loop(cmd)
                    if route == "home":
                        break
                    if route == "quit":
                        raise SystemExit(0)
                else:
                    console.print(f"  [grey50]Numéro hors plage (1–{len(commands)}).[/grey50]")
            else:
                console.print("  [grey50]Entrée invalide.[/grey50]")

    def show(self) -> None:
        self.run_loop(self.CATEGORY, self.TITLE)
