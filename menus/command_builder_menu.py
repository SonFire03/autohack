"""Command Builder — render reusable lab command templates."""

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from core.command_builder import COMMAND_TEMPLATES, placeholders_for, render_template
from core.theme import help_footer, status_bar
from core.variables import VariableStore

console = Console()


class CommandBuilderMenu:
    """Générateur de commandes depuis les variables du workspace."""

    def __init__(self, store: VariableStore) -> None:
        self._store = store

    def show(self) -> None:
        while True:
            console.clear()
            console.print(Panel(
                "[bold cyan]Command Builder[/bold cyan]  [dim]— générer des commandes depuis le workspace[/dim]",
                border_style="cyan",
                padding=(0, 1),
            ))
            console.print()

            status_bar([
                ("Templates", str(len(COMMAND_TEMPLATES)), "bold bright_cyan"),
                ("Variables", str(len(self._store)), "bold white"),
                ("Exécution", "jamais automatique", "bold bright_yellow"),
            ])
            console.print()
            self._render_templates()
            console.print()

            help_footer([
                ("<n>",          "générer la commande n"),
                ("c <n>",        "copier la commande n"),
                ("s <VAR> <val>","définir une variable"),
                ("vars",         "voir les variables actives"),
                ("b / q",        "retour"),
            ], title="Command Builder")

            try:
                raw = console.input("\n  [bold cyan]>[/bold cyan] ").strip()
            except (KeyboardInterrupt, EOFError):
                break

            if not raw or raw in {"b", "q"}:
                break

            self._handle(raw)

    def _render_templates(self) -> None:
        table = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE_HEAVY, expand=True)
        table.add_column("#", style="bold yellow", width=4, justify="right")
        table.add_column("Template", style="bold white", min_width=20)
        table.add_column("Catégorie", style="cyan", width=12)
        table.add_column("Variables", style="grey70", min_width=20)
        table.add_column("Description", style="grey70")

        for index, template in enumerate(COMMAND_TEMPLATES, start=1):
            placeholders = ", ".join(f"${name}" for name in placeholders_for(template)) or "-"
            table.add_row(
                str(index),
                template.label,
                template.category,
                placeholders,
                template.description,
            )
        console.print(Panel(
            table,
            title=" Templates disponibles ",
            title_align="left",
            border_style="dim blue",
            padding=(0, 1),
        ))

    def _handle(self, raw: str) -> None:
        parts = raw.split(None, 2)
        cmd = parts[0].lower()

        if cmd == "vars":
            self._show_vars()
            return

        if cmd == "s" and len(parts) == 3:
            name = parts[1].upper().lstrip("$")
            self._store.set(name, parts[2])
            console.print(f"  [bold green]✓[/bold green] ${name} = {parts[2]!r}")
            console.input("[dim]  Entrée...[/dim]")
            return

        copy_result = False
        if cmd == "c" and len(parts) >= 2:
            copy_result = True
            raw_index = parts[1]
        else:
            raw_index = cmd

        if raw_index.isdigit():
            index = int(raw_index) - 1
            if 0 <= index < len(COMMAND_TEMPLATES):
                self._render_command(index, copy_result)
                return

        console.print("  [dim]Commande inconnue. Utilisez <n>, c <n>, vars ou s <VAR> <val>.[/dim]")
        console.input("[dim]  Entrée...[/dim]")

    def _render_command(self, index: int, copy_result: bool = False) -> None:
        template = COMMAND_TEMPLATES[index]
        command, missing = render_template(template, self._store.all())
        console.print()
        console.print(Panel(
            Syntax(command, "bash", theme="monokai", word_wrap=True),
            title=f" {template.label} ",
            title_align="left",
            border_style="green" if not missing else "yellow",
            padding=(0, 1),
        ))
        if missing:
            console.print(f"  [bold yellow]Variables manquantes :[/bold yellow] {', '.join('$' + name for name in missing)}")
        else:
            console.print("  [bold green]✓[/bold green] Toutes les variables sont résolues.")

        if copy_result:
            try:
                import pyperclip

                pyperclip.copy(command)
                console.print("  [bold green]✓[/bold green] Commande copiée.")
            except Exception:
                console.print("  [dim]Impossible de copier dans le presse-papiers.[/dim]")

        console.input("\n[dim]  Entrée...[/dim]")

    def _show_vars(self) -> None:
        current = self._store.all()
        if not current:
            console.print("  [dim]Aucune variable définie.[/dim]")
            console.input("[dim]  Entrée...[/dim]")
            return

        table = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE_HEAVY)
        table.add_column("Variable", style="bold yellow")
        table.add_column("Valeur", style="bold white")
        for name, value in sorted(current.items()):
            table.add_row(f"${name}", value if len(value) <= 70 else value[:67] + "...")
        console.print(Panel(table, title=" Variables actives ", title_align="left", border_style="dim blue"))
        console.input("\n[dim]  Entrée...[/dim]")
