"""Loot Vault — store credentials, hashes, flags and keys captured during pentest."""
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from core.loot import LootVault, LOOT_TYPES
from core.theme import help_footer, status_bar
from config.settings import EXPORTS_DIR

console = Console()

TYPE_ICONS = {
    "credential": "🔐",
    "hash":       "🔑",
    "flag":       "🚩",
    "ssh_key":    "🗝 ",
    "api_key":    "⚙️ ",
    "token":      "🎫",
    "note":       "📝",
    "other":      "📦",
}


class LootMenu:
    def __init__(self, vault: LootVault) -> None:
        self._vault = vault

    def _type_color(self, t: str) -> str:
        return {
            "credential": "bold red",
            "hash":       "bold yellow",
            "flag":       "bold green",
            "ssh_key":    "bold cyan",
            "api_key":    "bold magenta",
            "token":      "bold blue",
            "note":       "grey70",
            "other":      "white",
        }.get(t, "white")

    def _build_table(self, entries: list) -> Table:
        t = Table(show_header=True, header_style="bold cyan",
                  box=box.SIMPLE_HEAVY, expand=True)
        t.add_column("ID",      width=10, style="dim")
        t.add_column("Type",    width=12, style="bold white")
        t.add_column("Valeur",  min_width=30, style="white")
        t.add_column("Source",  width=18, style="grey70")
        t.add_column("Date",    width=16, style="grey50")
        for e in entries:
            icon = TYPE_ICONS.get(e["type"], "📦")
            val = e["value"] if len(e["value"]) <= 48 else e["value"][:45] + "…"
            t.add_row(
                e["id"],
                f"{icon} {e['type']}",
                Text(val, style=self._type_color(e["type"])),
                e.get("source", ""),
                e.get("timestamp", ""),
            )
        return t

    def show(self) -> None:
        filter_type = ""
        while True:
            console.clear()
            console.print(Panel(
                "[bold green]Loot Vault[/bold green]  [dim]— butin de pentest : credentials, hashes, flags, clés[/dim]",
                border_style="green", padding=(0, 1),
            ))
            console.print()

            all_entries = self._vault.all()
            entries = self._vault.by_type(filter_type) if filter_type else all_entries

            counts = {t: len(self._vault.by_type(t)) for t in LOOT_TYPES if self._vault.by_type(t)}
            status_bar([
                ("Total", str(len(all_entries)), "bold bright_green"),
                *[(TYPE_ICONS.get(t, "") + " " + t, str(c), "bold yellow") for t, c in list(counts.items())[:4]],
                ("Filtre", filter_type or "tous", "grey70"),
            ])
            console.print()

            if not entries:
                console.print("  [dim]Vault vide — ajoutez du butin avec [bold]a[/bold].[/dim]\n")
            else:
                console.print(Panel(self._build_table(entries),
                                    title=" Butin ", title_align="left",
                                    border_style="dim green", padding=(0, 1)))
            console.print()

            help_footer([
                ("a <type> <val>",   "ajouter  ex: a hash 31d6cfe0d16ae931b73c59d7e0c089c0"),
                ("as <type>",        "ajouter avec saisie interactive"),
                ("d <id>",           "supprimer une entrée"),
                ("f <type>",         "filtrer par type (credential/hash/flag/ssh_key/api_key/token/note)"),
                ("fa",               "tout afficher"),
                ("s <query>",        "rechercher"),
                ("v <id>",           "voir valeur complète"),
                ("e",                "exporter en markdown"),
                ("b / q",            "retour"),
            ], title="Loot Vault")

            try:
                raw = console.input("\n  [bold green]>[/bold green] ").strip()
            except (KeyboardInterrupt, EOFError):
                break
            if not raw or raw in {"b", "q"}:
                break

            parts = raw.split(None, 3)
            cmd = parts[0].lower()

            if cmd == "a" and len(parts) >= 3:
                ltype = parts[1].lower()
                if ltype not in LOOT_TYPES:
                    console.print(f"  [red]Type invalide. Valides: {', '.join(LOOT_TYPES)}[/red]")
                    console.input("[dim]  Entrée…[/dim]"); continue
                val    = parts[2]
                source = parts[3] if len(parts) > 3 else ""
                entry  = self._vault.add(ltype, val, source=source)
                console.print(f"  [green]✓[/green] [{entry['id']}] {ltype}: {val[:50]}")
                console.input("[dim]  Entrée…[/dim]")

            elif cmd == "as" and len(parts) >= 2:
                ltype = parts[1].lower()
                if ltype not in LOOT_TYPES:
                    console.print(f"  [red]Type invalide: {ltype}[/red]")
                    console.input("[dim]  Entrée…[/dim]"); continue
                try:
                    val    = console.input(f"  [bold yellow]Valeur ({ltype}):[/bold yellow] ").strip()
                    source = console.input("  [dim]Source (optionnel):[/dim] ").strip()
                    notes  = console.input("  [dim]Notes  (optionnel):[/dim] ").strip()
                    if val:
                        entry = self._vault.add(ltype, val, source=source, notes=notes)
                        console.print(f"  [green]✓[/green] [{entry['id']}] ajouté.")
                    else:
                        console.print("  [dim]Annulé.[/dim]")
                except (KeyboardInterrupt, EOFError):
                    console.print("\n  [dim]Annulé.[/dim]")
                console.input("[dim]  Entrée…[/dim]")

            elif cmd == "d" and len(parts) >= 2:
                if self._vault.remove(parts[1]):
                    console.print(f"  [green]✓[/green] {parts[1]} supprimé.")
                else:
                    console.print(f"  [dim]{parts[1]} introuvable.[/dim]")
                console.input("[dim]  Entrée…[/dim]")

            elif cmd == "f" and len(parts) >= 2:
                filter_type = parts[1].lower()
                if filter_type not in LOOT_TYPES:
                    console.print(f"  [red]Type invalide: {filter_type}[/red]")
                    filter_type = ""
                    console.input("[dim]  Entrée…[/dim]")

            elif cmd == "fa":
                filter_type = ""

            elif cmd == "s" and len(parts) >= 2:
                results = self._vault.search(" ".join(parts[1:]))
                console.print(f"\n  [dim]{len(results)} résultat(s)[/dim]\n")
                if results:
                    console.print(Panel(self._build_table(results),
                                        title=" Résultats recherche ",
                                        title_align="left", border_style="dim yellow"))
                console.input("\n  [dim]Entrée…[/dim]")

            elif cmd == "v" and len(parts) >= 2:
                entry_id = parts[1]
                found = [e for e in all_entries if e["id"] == entry_id]
                if found:
                    e = found[0]
                    console.print()
                    console.print(Panel(
                        f"[bold]Type:[/bold] {e['type']}\n"
                        f"[bold]Date:[/bold] {e['timestamp']}\n"
                        f"[bold]Source:[/bold] {e.get('source','—')}\n"
                        f"[bold]Notes:[/bold] {e.get('notes','—')}\n\n"
                        f"[bold yellow]{e['value']}[/bold yellow]",
                        title=f" [{entry_id}] ", border_style="green", padding=(1, 2),
                    ))
                else:
                    console.print(f"  [dim]{entry_id} introuvable.[/dim]")
                console.input("\n  [dim]Entrée…[/dim]")

            elif cmd == "e":
                md = self._vault.export_markdown()
                path = EXPORTS_DIR / "loot_vault.md"
                path.write_text(md, encoding="utf-8")
                console.print(f"  [green]✓[/green] Exporté → {path}")
                console.input("[dim]  Entrée…[/dim]")

            else:
                console.print("  [dim]Commande inconnue.[/dim]")
                console.input("[dim]  Entrée…[/dim]")
