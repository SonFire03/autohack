"""Command Builder — render reusable lab command templates."""

from collections import OrderedDict

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from core.command_builder import (
    available_categories,
    placeholders_for,
    render_template,
    search_templates,
)
from core.theme import help_footer, status_bar
from core.variables import VariableStore

console = Console()


class CommandBuilderMenu:
    """Générateur de commandes depuis les variables du workspace."""

    def __init__(self, store: VariableStore) -> None:
        self._store = store
        self._query = ""
        self._category: str | None = None
        self._visible_templates = []

    def show(self) -> None:
        while True:
            visible = self._visible_templates_for_current_filter()
            console.clear()
            console.print(Panel(
                "[bold cyan]Command Builder[/bold cyan]  [dim]— générer des commandes depuis le workspace[/dim]",
                border_style="cyan",
                padding=(0, 1),
            ))
            console.print()

            status_bar([
                ("Templates", str(len(visible)), "bold bright_cyan"),
                ("Variables", str(len(self._store)), "bold white"),
                ("Filtre", self._query or "aucun", "bold bright_yellow"),
                ("Catégorie", self._category or "toutes", "bold bright_green"),
                ("Exécution", "jamais automatique", "bold bright_yellow"),
            ])
            console.print()
            self._render_templates(visible)
            console.print()

            help_footer([
                ("<n>",          "générer la commande n"),
                ("c <n>",        "copier la commande n"),
                ("s <VAR> <val>","définir une variable"),
                ("f <mots>",     "filtrer par texte"),
                ("cat <cat>",    "filtrer par catégorie"),
                ("all",          "retirer les filtres"),
                ("cats",         "voir les catégories"),
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

    def _visible_templates_for_current_filter(self):
        return search_templates(self._query, self._category)

    def _render_templates(self, templates) -> None:
        self._visible_templates = list(templates)
        if not self._visible_templates:
            console.print(Panel(
                "[dim]Aucun template ne correspond aux filtres actuels.[/dim]",
                title=" Templates disponibles ",
                title_align="left",
                border_style="dim blue",
                padding=(0, 1),
            ))
            return

        grouped: "OrderedDict[str, list]" = OrderedDict()
        category_order = available_categories()
        for template in self._visible_templates:
            grouped.setdefault(template.category, []).append(template)
        ordered_categories = [category for category in category_order if category in grouped]
        for category in grouped:
            if category not in ordered_categories:
                ordered_categories.append(category)

        index = 1
        for category in ordered_categories:
            table = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE_HEAVY, expand=True)
            table.add_column("#", style="bold yellow", width=4, justify="right")
            table.add_column("Template", style="bold white", min_width=20)
            table.add_column("Variables", style="grey70", min_width=20)
            table.add_column("Description", style="grey70")

            for template in grouped[category]:
                placeholders = ", ".join(f"${name}" for name in placeholders_for(template)) or "-"
                table.add_row(
                    str(index),
                    template.label,
                    placeholders,
                    template.description,
                )
                index += 1

            console.print(Panel(
                table,
                title=f" {category} ",
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

        if cmd == "cats":
            self._show_categories()
            return

        if cmd in {"all", "clear", "reset"}:
            self._query = ""
            self._category = None
            return

        if cmd == "f":
            self._query = raw[1:].lstrip()
            return

        if cmd == "cat":
            if len(parts) < 2 or parts[1].lower() in {"all", "clear", "reset", "*"}:
                self._category = None
                return
            wanted = parts[1].lower()
            if wanted in available_categories():
                self._category = wanted
                return
            console.print(f"  [dim]Catégorie inconnue: {wanted}. Utilisez cats pour voir la liste.[/dim]")
            console.input("[dim]  Entrée...[/dim]")
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
            if 0 <= index < len(self._visible_templates):
                self._render_command(index, copy_result)
                return

        console.print("  [dim]Commande inconnue. Utilisez <n>, c <n>, vars ou s <VAR> <val>.[/dim]")
        console.input("[dim]  Entrée...[/dim]")

    def _render_command(self, index: int, copy_result: bool = False) -> None:
        template = self._visible_templates[index]
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

    def _show_categories(self) -> None:
        categories = available_categories()
        table = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE_HEAVY)
        table.add_column("Catégorie", style="bold yellow")
        table.add_column("Templates", style="bold white", justify="right")
        for category in categories:
            count = sum(1 for template in self._visible_templates_for_current_filter() if template.category == category)
            table.add_row(category, str(count))
        console.print(Panel(table, title=" Catégories ", title_align="left", border_style="dim blue"))
        console.input("\n[dim]  Entrée...[/dim]")
