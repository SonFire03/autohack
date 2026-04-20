from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich import box
from menus.base import BaseMenu
from core.favorites import Favorites
from core.theme import status_bar, help_footer
from core.theme import metric_cards, empty_state, legend_panel

console = Console()


class FavoritesMenu(BaseMenu):
    TITLE = "Commandes favorites"

    def __init__(self, *args, favorites: Favorites, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._favorites = favorites

    def show(self) -> None:
        focus = 0
        while True:
            self._header("⭐ Commandes favorites")
            ids = self._favorites.all_ids()

            if not ids:
                empty_state(
                    "Favoris vides",
                    "Aucun favori enregistré pour le moment.",
                    "Ajoute des commandes avec la touche f depuis une fiche.",
                )
                console.input("\n[dim]Entrée pour retourner…[/dim]")
                return

            cmds = [c for i in ids if (c := self._catalog.get_by_id(i)) is not None]
            orphans = [i for i in ids if self._catalog.get_by_id(i) is None]
            focus = self._clamp_focus(focus, len(cmds))

            status_bar([
                ("Favoris", str(len(cmds)), "bold bright_yellow"),
                ("Orphelins", str(len(orphans)), "bold bright_red" if orphans else "grey70"),
                ("Mode", "raccourcis personnels", "grey70"),
            ])
            metric_cards([
                ("Safe", str(sum(1 for c in cmds if c.get("execution_policy") == "safe" or c.get("safe_to_run"))), "bold bright_green"),
                ("Lab-only", str(sum(1 for c in cmds if c.get("execution_policy") == "lab_only")), "bold bright_red"),
                ("Dry-run", str(sum(1 for c in cmds if c.get("execution_policy") == "dry_run_only")), "bold bright_yellow"),
            ])
            console.print(f"  [bold yellow]{len(cmds)} favori(s)[/bold yellow]\n")
            fav_table = self._build_favorites_table(cmds, focused_index=focus)
            if cmds:
                console.print(Columns([
                    Panel(fav_table, title=" Favoris ", title_align="left", border_style="dim blue", padding=(0, 0), expand=True),
                    self._build_command_preview_panel(cmds[focus], title="Favori en focus"),
                ], equal=True, expand=True, padding=(0, 1)))
                console.print()
            else:
                console.print(Panel(fav_table, title=" Favoris ", title_align="left", border_style="dim blue", padding=(0, 0), expand=True))
            legend_panel([
                ("› n", "favori actuellement sélectionné"),
                ("safe", "exécution ou lecture à faible risque"),
                ("lab-only", "commande non lancée depuis l'app"),
            ], title="Repères")

            if orphans:
                console.print(
                    f"  [dim]⚠ {len(orphans)} ID(s) introuvable(s) dans le catalogue : "
                    f"{', '.join(orphans)}[/dim]"
                )

            help_footer([
                ("j / k", "descendre / monter"),
                ("Entrée ou o", "ouvrir le focus"),
                ("numéro", "ouvrir la fiche"),
                ("v<num>", "aperçu rapide"),
                ("xID", "retirer un favori"),
                ("c", "tout effacer"),
                (":", "palette globale"),
                ("b", "retour"),
            ], title="Favoris")

            choice = console.input(
                "\n  Numéro=ouvrir  [bold]x[/bold]=supprimer  [bold]c[/bold]=tout effacer  "
                "[bold]b[/bold]=retour > "
            ).strip().lower()

            palette = self._handle_palette_command(choice)
            if palette == "handled":
                continue
            if palette in {"home", "quit"}:
                return

            if choice == "b":
                break
            elif choice == "j" and cmds:
                focus = min(focus + 1, len(cmds) - 1)
            elif choice == "k" and cmds:
                focus = max(focus - 1, 0)
            elif choice == "c":
                from rich.prompt import Confirm
                if Confirm.ask("[bold yellow]Effacer tous les favoris ?[/bold yellow]", default=False):
                    self._favorites.clear()
                    console.print("[bold green]✅ Favoris effacés.[/bold green]")
                    console.input("[dim]Entrée pour continuer…[/dim]")
            elif choice in {"", "o"} and cmds:
                cmd = cmds[focus]
                self._header(f"⭐ {cmd['name']}")
                self._show_command_card(cmd)
                route = self._action_loop(cmd)
                if route in {"home", "quit"}:
                    return
            elif choice.startswith("x") and len(choice) > 1:
                target = choice[1:].strip()
                if self._favorites.remove(target):
                    console.print(f"[bold green]✅ {target} retiré des favoris.[/bold green]")
                else:
                    console.print(f"[dim]{target} n'est pas dans vos favoris.[/dim]")
                console.input("[dim]Entrée pour continuer…[/dim]")
            elif choice.startswith("v") and choice[1:].isdigit():
                idx = int(choice[1:]) - 1
                if 0 <= idx < len(cmds):
                    focus = idx
                    self._header(f"⭐ Aperçu · {cmds[idx]['name']}")
                    self._render_command_preview_panel(cmds[idx], title="Aperçu rapide")
                    console.input("[dim]Entrée pour revenir…[/dim]")
                else:
                    console.print(f"[dim]Numéro hors plage (1–{len(cmds)}).[/dim]")
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(cmds):
                    focus = idx
                    cmd = cmds[idx]
                    self._header(f"⭐ {cmd['name']}")
                    self._show_command_card(cmd)
                    route = self._action_loop(cmd)
                    if route in {"home", "quit"}:
                        return
                else:
                    console.print(f"[dim]Numéro hors plage (1–{len(cmds)}).[/dim]")

    def _build_favorites_table(self, cmds, focused_index: int | None = None) -> Table:
        table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE_HEAVY,
            expand=True,
        )
        table.add_column("#", style="dim", width=4)
        table.add_column("ID", style="dim", width=10)
        table.add_column("Catégorie", style="dim cyan", width=14)
        table.add_column("Nom", style="bold white", min_width=22)
        table.add_column("Commande", style="magenta", min_width=28)
        table.add_column("Profil", width=10)
        table.add_column("État", width=10)
        table.add_column("Outil", width=12)

        for i, cmd in enumerate(cmds, 1):
            tool = cmd.get("tool_required", "")
            is_focused = focused_index == (i - 1)
            table.add_row(
                f"› {i}" if is_focused else str(i), cmd["id"], cmd.get("category", ""),
                cmd["name"],
                self._command_preview(cmd["command"], max_len=40),
                self._safety_label(cmd),
                self._readiness_label(tool),
                tool or "—",
                style="bold on grey11" if is_focused else None,
            )
        return table
