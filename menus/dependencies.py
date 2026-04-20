from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from menus.base import BaseMenu

console = Console()

# Outils supplémentaires importants qui peuvent ne pas figurer dans le catalogue
EXTRA_TOOLS = [
    ("systemctl",  "systemctl (systemd)"),
    ("journalctl", "journalctl (systemd)"),
    ("ip",         "ip (iproute2)"),
    ("ss",         "ss (iproute2)"),
]


class DependenciesMenu(BaseMenu):
    CATEGORY = "system"
    TITLE = "Vérification des dépendances"

    def show(self) -> None:
        self._header("🔍 Vérification des dépendances")
        self._check_all_tools()
        console.input("\n[dim]Appuyez sur Entrée pour retourner au menu principal…[/dim]")

    def _check_all_tools(self) -> None:
        # Dériver la liste des outils depuis le catalogue (sans doublons)
        seen: set[str] = set()
        tools: list[tuple[str, str]] = []

        for cmd in self._catalog.get_all():
            tool = cmd.get("tool_required", "")
            if tool and tool not in seen:
                seen.add(tool)
                tools.append((tool, tool))

        # Ajouter les outils système supplémentaires
        for t, label in EXTRA_TOOLS:
            if t not in seen:
                seen.add(t)
                tools.append((t, label))

        tools.sort(key=lambda x: x[0])

        table = Table(
            title=f"État des outils du lab ({len(tools)} outils)",
            show_header=True,
            header_style="bold cyan",
            box=box.ROUNDED,
            expand=False,
        )
        table.add_column("Outil", style="bold white", min_width=16)
        table.add_column("Statut", width=14)
        table.add_column("Installation si absent", style="dim magenta", min_width=32)

        statuses = {tool_bin: self._checker.check(tool_bin) for tool_bin, _ in tools}

        for tool_bin, _label in tools:
            ok = statuses[tool_bin]
            status = "[bold green]✅ installé[/bold green]" if ok \
                else "[bold red]❌ manquant[/bold red]"
            hint = "[dim]—[/dim]" if ok else f"[magenta]{self._checker.install_hint(tool_bin)}[/magenta]"
            table.add_row(tool_bin, status, hint)

        console.print()
        console.print(table)

        missing = [t for t, ok in statuses.items() if not ok]
        if not missing:
            console.print(Panel(
                "[bold green]✅ Tous les outils référencés dans le catalogue sont installés ![/bold green]",
                border_style="green",
            ))
        else:
            console.print(Panel(
                f"[bold yellow]⚠️  {len(missing)} outil(s) manquant(s) : {', '.join(missing)}[/bold yellow]\n"
                "[dim]Consultez la colonne 'Installation' ci-dessus.[/dim]",
                border_style="yellow",
            ))
