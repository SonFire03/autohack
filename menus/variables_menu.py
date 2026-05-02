"""Variable Manager — define $TARGET, $LHOST etc. once, used by all commands."""
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from core.variables import VariableStore, VAR_HINTS
from core.theme import help_footer, status_bar

console = Console()

_SUGGESTED_VARS = [
    "TARGET", "LHOST", "LPORT", "DOMAIN", "DC_IP",
    "USER", "PASSWORD", "HASH", "WORDLIST", "INTERFACE",
    "PORT", "CALLBACK_URL", "DOMAIN_SID", "KRBTGT_HASH", "CA_NAME",
]


class VariablesMenu:
    """Gestionnaire de variables globales persistantes."""

    def __init__(self, store: VariableStore) -> None:
        self._store = store

    def show(self) -> None:
        while True:
            console.clear()
            console.print(Panel(
                "[bold cyan]Variable Manager[/bold cyan]  [dim]— variables globales injectées dans toutes les commandes[/dim]",
                border_style="cyan", padding=(0, 1),
            ))
            console.print()

            current = self._store.all()
            status_bar([
                ("Variables définies", str(len(current)), "bold bright_cyan"),
                ("Fichier", "~/.autohack_variables.json", "grey70"),
            ])
            console.print()

            # ── Table des variables définies ──────────────────────────────
            t = Table(show_header=True, header_style="bold cyan",
                      box=box.SIMPLE_HEAVY, expand=True)
            t.add_column("Variable", style="bold yellow", width=18)
            t.add_column("Valeur", style="bold white", min_width=28)
            t.add_column("Description", style="grey70")

            if current:
                for name, val in sorted(current.items()):
                    hint = VAR_HINTS.get(name, "Variable personnalisée")
                    display = val if len(val) <= 50 else val[:47] + "…"
                    t.add_row(f"${name}", display, hint)
            else:
                t.add_row("[dim]aucune[/dim]", "[dim]—[/dim]", "[dim]définissez des variables avec s[/dim]")

            console.print(Panel(t, title=" Variables actives ", title_align="left",
                                border_style="dim blue", padding=(0, 1)))
            console.print()

            # ── Variables suggérées ───────────────────────────────────────
            missing = [v for v in _SUGGESTED_VARS if v not in current]
            if missing:
                console.print(f"  [dim]Suggérées non définies : {', '.join('$' + v for v in missing[:8])}[/dim]")
                console.print()

            help_footer([
                ("s <VAR> <val>", "définir une variable  ex: s TARGET 10.0.0.1"),
                ("d <VAR>",       "supprimer une variable"),
                ("c",             "effacer toutes les variables"),
                ("l",             "lister les variables suggérées"),
                ("b / q",         "retour"),
            ], title="Variable Manager")

            try:
                raw = console.input("\n  [bold cyan]>[/bold cyan] ").strip()
            except (KeyboardInterrupt, EOFError):
                break

            if not raw or raw in {"b", "q"}:
                break

            parts = raw.split(None, 2)
            cmd = parts[0].lower()

            if cmd == "s" and len(parts) >= 3:
                name = parts[1].upper().lstrip("$")
                val  = parts[2]
                self._store.set(name, val)
                console.print(f"  [bold green]✓[/bold green] ${name} = {val!r}")
                console.input("[dim]  Entrée…[/dim]")

            elif cmd == "s" and len(parts) == 2:
                name = parts[1].upper().lstrip("$")
                hint = VAR_HINTS.get(name, "Valeur")
                try:
                    val = console.input(f"  [bold yellow]${name}[/bold yellow]  [dim]{hint}[/dim]\n  > ").strip()
                    if val:
                        self._store.set(name, val)
                        console.print(f"  [bold green]✓[/bold green] ${name} = {val!r}")
                    else:
                        console.print("  [dim]Annulé.[/dim]")
                except (KeyboardInterrupt, EOFError):
                    console.print("\n  [dim]Annulé.[/dim]")
                console.input("[dim]  Entrée…[/dim]")

            elif cmd == "d" and len(parts) >= 2:
                name = parts[1].upper().lstrip("$")
                if self._store.delete(name):
                    console.print(f"  [bold green]✓[/bold green] ${name} supprimée.")
                else:
                    console.print(f"  [dim]${name} n'est pas définie.[/dim]")
                console.input("[dim]  Entrée…[/dim]")

            elif cmd == "c":
                from rich.prompt import Confirm
                if Confirm.ask("Effacer toutes les variables ?", default=False):
                    self._store.clear()
                    console.print("  [bold green]✓[/bold green] Variables effacées.")
                    console.input("[dim]  Entrée…[/dim]")

            elif cmd == "l":
                console.print()
                for v in _SUGGESTED_VARS:
                    hint = VAR_HINTS.get(v, "")
                    val  = self._store.get(v)
                    state = f"[green]{val}[/green]" if val else "[dim]non définie[/dim]"
                    console.print(f"  [yellow]${v:<18}[/yellow] {state}  [dim]{hint}[/dim]")
                console.input("\n[dim]  Entrée…[/dim]")

            else:
                console.print("  [dim]Commande inconnue. Utilisez s, d, c, l, b.[/dim]")
                console.input("[dim]  Entrée…[/dim]")
