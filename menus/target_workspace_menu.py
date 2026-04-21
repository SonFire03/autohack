"""Target Workspace — session scope and shared variables."""

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from core.theme import help_footer, status_bar
from core.variables import VAR_HINTS, VariableStore

console = Console()

_PRIMARY_VARS = [
    "TARGET",
    "URL",
    "DOMAIN",
    "DC_IP",
    "LHOST",
    "LPORT",
    "PORT",
    "USER",
    "PASSWORD",
    "WORDLIST",
    "FILE",
    "SCOPE",
    "NOTES",
]

_SHORTCUTS = {
    "t": "TARGET",
    "url": "URL",
    "d": "DOMAIN",
    "dc": "DC_IP",
    "lh": "LHOST",
    "lp": "LPORT",
    "p": "PORT",
    "u": "USER",
    "pw": "PASSWORD",
    "w": "WORDLIST",
    "file": "FILE",
    "scope": "SCOPE",
    "note": "NOTES",
}


class TargetWorkspaceMenu:
    """Cockpit de session pour variables, scope et notes."""

    def __init__(self, store: VariableStore) -> None:
        self._store = store

    def show(self) -> None:
        while True:
            console.clear()
            console.print(Panel(
                "[bold cyan]Target Workspace[/bold cyan]  [dim]— cible, scope et variables partagées[/dim]",
                border_style="cyan",
                padding=(0, 1),
            ))
            console.print()

            current = self._store.all()
            status_bar([
                ("Variables", str(len(current)), "bold bright_cyan"),
                ("Target", current.get("TARGET", "non défini"), "bold white"),
                ("Scope", "défini" if current.get("SCOPE") else "à définir", "bold bright_yellow"),
            ])
            console.print()
            self._render_workspace(current)
            console.print()

            help_footer([
                ("t <target>",       "définir TARGET"),
                ("url <url>",        "définir URL"),
                ("lh/lp <val>",      "définir LHOST/LPORT"),
                ("d/dc <val>",       "définir DOMAIN/DC_IP"),
                ("u/pw <val>",       "définir USER/PASSWORD"),
                ("scope <texte>",    "définir le périmètre autorisé"),
                ("note <texte>",     "définir les notes rapides"),
                ("s <VAR> <val>",    "définir une variable libre"),
                ("del <VAR>",        "supprimer une variable"),
                ("b / q",           "retour"),
            ], title="Target Workspace")

            try:
                raw = console.input("\n  [bold cyan]>[/bold cyan] ").strip()
            except (KeyboardInterrupt, EOFError):
                break

            if not raw or raw in {"b", "q"}:
                break

            self._handle(raw)

    def _render_workspace(self, current: dict[str, str]) -> None:
        table = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE_HEAVY, expand=True)
        table.add_column("Variable", style="bold yellow", width=14)
        table.add_column("Valeur", style="bold white", min_width=28)
        table.add_column("Rôle", style="grey70")

        for name in _PRIMARY_VARS:
            value = current.get(name, "")
            display = value if value else "[dim]non défini[/dim]"
            if len(value) > 64:
                display = value[:61] + "..."
            table.add_row(f"${name}", display, VAR_HINTS.get(name, "Variable de session"))

        extra = [name for name in sorted(current) if name not in _PRIMARY_VARS]
        for name in extra:
            value = current[name]
            display = value if len(value) <= 64 else value[:61] + "..."
            table.add_row(f"${name}", display, VAR_HINTS.get(name, "Variable personnalisée"))

        console.print(Panel(
            table,
            title=" Workspace actif ",
            title_align="left",
            border_style="dim blue",
            padding=(0, 1),
        ))

    def _handle(self, raw: str) -> None:
        parts = raw.split(None, 1)
        cmd = parts[0].lower()
        value = parts[1].strip() if len(parts) == 2 else ""

        if cmd in _SHORTCUTS and value:
            self._set(_SHORTCUTS[cmd], value)
            return

        if cmd == "s":
            sub = value.split(None, 1)
            if len(sub) == 2:
                self._set(sub[0].upper().lstrip("$"), sub[1])
            else:
                console.print("  [dim]Usage: s <VAR> <valeur>[/dim]")
                console.input("[dim]  Entrée...[/dim]")
            return

        if cmd in {"del", "delete", "rm"} and value:
            name = value.upper().lstrip("$")
            if self._store.delete(name):
                console.print(f"  [bold green]✓[/bold green] ${name} supprimée.")
            else:
                console.print(f"  [dim]${name} n'est pas définie.[/dim]")
            console.input("[dim]  Entrée...[/dim]")
            return

        if cmd == "clear":
            from rich.prompt import Confirm

            if Confirm.ask("Effacer toutes les variables ?", default=False):
                self._store.clear()
                console.print("  [bold green]✓[/bold green] Workspace effacé.")
            console.input("[dim]  Entrée...[/dim]")
            return

        console.print("  [dim]Commande inconnue. Utilisez t, url, lh, lp, scope, note, s ou del.[/dim]")
        console.input("[dim]  Entrée...[/dim]")

    def _set(self, name: str, value: str) -> None:
        self._store.set(name, value)
        console.print(f"  [bold green]✓[/bold green] ${name} = {value!r}")
        console.input("[dim]  Entrée...[/dim]")
