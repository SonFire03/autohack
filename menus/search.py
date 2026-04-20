from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich import box
from menus.base import BaseMenu
from core.theme import status_bar, help_footer
from core.theme import metric_cards, empty_state, legend_panel

console = Console()


class SearchMenu(BaseMenu):
    TITLE = "Recherche de commande"
    CATEGORY = "system"

    def show(self) -> None:
        while True:
            self._header("🔍 Recherche de commande")
            status_bar([
                ("Portée", "catalogue complet", "bold bright_cyan"),
                ("Mode", "recherche scorée", "bold white"),
                ("Astuce", "sans accent et insensible à la casse", "grey70"),
            ])
            metric_cards([
                ("Total catalogue", str(len(self._catalog.get_all())), "bold bright_cyan"),
                ("Catégories", str(len(self._catalog.get_categories())), "bold white"),
                ("Favoris", str(len(self._favorites)), "bold bright_yellow"),
            ])
            console.print(
                "  Tapez un ou plusieurs mots-clés pour rechercher dans le catalogue.\n"
                "  Exemples : [bold]tor[/bold], [bold]port[/bold], [bold]json status[/bold]\n"
                "  [bold]b[/bold] pour retourner.\n"
            )
            help_footer([
                ("mot-clé", "lancer une recherche"),
                (":", "palette globale"),
                ("b", "retour menu principal"),
            ], title="Saisie")

            keyword = console.input("[bold yellow]Mot-clé > [/bold yellow]").strip()

            palette = self._handle_palette_command(keyword)
            if palette == "handled":
                continue
            if palette in {"home", "quit"}:
                return

            if keyword.lower() == "b":
                break
            if len(keyword) < 2:
                console.print("[dim]Tapez au moins 2 caractères.[/dim]")
                continue

            results = self._catalog.search(keyword)

            if not results:
                empty_state(
                    "Aucun résultat",
                    f"Aucune commande ne correspond à « {keyword} ».",
                    "Essaie un mot plus court, une techno ou un outil.",
                )
                continue

            # Boucle de résultats avec pagination
            page_size = self._config.get("page_size")
            focus = 0

            while True:
                focus = self._clamp_focus(focus, len(results))
                page = (focus // page_size) if results else 0
                total_pages = max(1, (len(results) + page_size - 1) // page_size)
                self._header("🔍 Recherche de commande")
                status_bar([
                    ("Requête", keyword, "bold bright_magenta"),
                    ("Résultats", str(len(results)), "bold bright_green"),
                    ("Vue", f"page {page + 1}/{total_pages}", "bold white"),
                ])
                metric_cards([
                    ("Safe", str(sum(1 for r in results if r.get("execution_policy") == "safe" or r.get("safe_to_run"))), "bold bright_green"),
                    ("Lab-only", str(sum(1 for r in results if r.get("execution_policy") == "lab_only")), "bold bright_red"),
                    ("Dry-run", str(sum(1 for r in results if r.get("execution_policy") == "dry_run_only")), "bold bright_yellow"),
                ])
                console.print(
                    f"[bold green]{len(results)} résultat(s) pour « {keyword} »[/bold green]\n"
                )

                start = page * page_size
                page_results = results[start:start + page_size]
                results_table = self._build_results_table(page_results, start_index=start + 1, focused_index=focus)
                if results:
                    console.print(Columns([
                        Panel(results_table, title=" Résultats ", title_align="left", border_style="dim blue", padding=(0, 0), expand=True),
                        self._build_command_preview_panel(results[focus], title="Résultat en focus"),
                    ], equal=True, expand=True, padding=(0, 1)))
                    console.print()
                else:
                    console.print(Panel(results_table, title=" Résultats ", title_align="left", border_style="dim blue", padding=(0, 0), expand=True))
                legend_panel([
                    ("› n", "élément actuellement sélectionné"),
                    ("safe", "commande passive ou peu risquée"),
                    ("lab-only", "commande réservée au lab"),
                ], title="Repères")

                help_footer([
                    ("j / k", "descendre / monter"),
                    ("Entrée ou o", "ouvrir le focus"),
                    ("numéro", "ouvrir directement"),
                    ("n", "nouvelle recherche"),
                    ("p / s", "page précédente / suivante"),
                    (":", "palette globale"),
                    ("b", "retour"),
                ], title="Résultats")

                choice = console.input(
                    "\n  Numéro=voir fiche  "
                    "[bold]n[/bold]=nouvelle recherche  "
                    "[bold]b[/bold]=retour > "
                ).strip().lower()

                palette = self._handle_palette_command(choice)
                if palette == "handled":
                    continue
                if palette in {"home", "quit"}:
                    return

                if choice == "b":
                    return
                if choice == "n":
                    break
                if choice == "j":
                    focus = min(focus + 1, len(results) - 1)
                    continue
                if choice == "k":
                    focus = max(focus - 1, 0)
                    continue
                if choice == "s" and page < total_pages - 1:
                    focus = min((page + 1) * page_size, len(results) - 1)
                    continue
                if choice == "p" and page > 0:
                    focus = max((page - 1) * page_size, 0)
                    continue
                if choice in {"", "o"} and results:
                    cmd = results[focus]
                    self._header(f"🔍 {cmd['name']}")
                    self._show_command_card(cmd)
                    route = self._action_loop(cmd)
                    if route in {"home", "quit"}:
                        return
                    continue
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(results):
                        focus = idx
                        cmd = results[idx]
                        self._header(f"🔍 {cmd['name']}")
                        self._show_command_card(cmd)
                        route = self._action_loop(cmd)
                        if route in {"home", "quit"}:
                            return
                    else:
                        console.print(f"[dim]Numéro hors plage (1–{len(results)}).[/dim]")

    def _build_results_table(self, results, start_index: int = 1, focused_index: int | None = None) -> Table:
        table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE_HEAVY,
            expand=True,
        )
        table.add_column("#", style="dim", width=6)
        table.add_column("Catégorie", style="dim cyan", width=14)
        table.add_column("Nom", style="bold white", min_width=22)
        table.add_column("Commande", style="magenta", min_width=28)
        table.add_column("Profil", width=10)
        table.add_column("État", width=10)

        for i, cmd in enumerate(results, start_index):
            absolute_index = i - 1
            is_focused = focused_index == absolute_index
            tool = cmd.get("tool_required", "")
            table.add_row(
                f"› {i}" if is_focused else str(i),
                cmd.get("category", ""),
                cmd["name"],
                self._command_preview(cmd["command"], max_len=42),
                self._safety_label(cmd),
                self._readiness_label(tool),
                style="bold on grey11" if is_focused else None,
            )
        return table
