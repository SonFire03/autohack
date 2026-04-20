from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from menus.base import BaseMenu
from core.exporter import Exporter

console = Console()


class ExportAllMenu(BaseMenu):
    TITLE = "Export de toutes les commandes"
    CATEGORY = "system"

    def show(self) -> None:
        while True:
            self._header("📦 Export de toutes les commandes")

            table = Table(show_header=False, box=box.SIMPLE, expand=False)
            table.add_column("Option", style="bold yellow", width=4)
            table.add_column("Description", style="white")
            table.add_row("1", "Exporter en Markdown  (rapport complet)")
            table.add_row("2", "Exporter en TXT       (catalogue brut)")
            table.add_row("3", "Exporter en JSON      (catalogue structuré)")
            table.add_row("4", "Exporter en HTML      (page web interactive)")
            table.add_row("5", "Tout exporter         (les 4 formats)")
            table.add_row("6", "Voir les exports existants")
            table.add_row("b", "Retour au menu principal")
            console.print(table)

            choice = console.input("[bold yellow]Choix > [/bold yellow]").strip().lower()

            if choice in ("1", "2", "3", "4", "5"):
                self._do_export(choice)
            elif choice == "6":
                self._list_exports()
            elif choice == "b":
                break
            else:
                console.print("[dim]Choix invalide.[/dim]")

            if choice in ("1", "2", "3", "4", "5", "6"):
                console.input("\n[dim]Appuyez sur Entrée pour continuer…[/dim]")

    def _do_export(self, choice: str) -> None:
        export_dir = self._config.get("export_dir")
        exporter = Exporter(self._catalog.get_all(), export_dir=export_dir)
        paths = []
        with console.status("[bold green]Génération en cours…[/bold green]"):
            if choice in ("1", "5"):
                paths.append(exporter.export_markdown())
            if choice in ("2", "5"):
                paths.append(exporter.export_txt())
            if choice in ("3", "5"):
                paths.append(exporter.export_json())
            if choice in ("4", "5"):
                paths.append(exporter.export_html())

        for path in paths:
            console.print(Panel(
                f"[bold green]✅ Export créé :[/bold green]\n  [magenta]{path}[/magenta]",
                border_style="green",
            ))

    def _list_exports(self) -> None:
        from datetime import datetime
        from config.settings import EXPORTS_DIR

        if not EXPORTS_DIR.exists():
            console.print(Panel("[dim]Dossier exports/ introuvable.[/dim]", border_style="dim"))
            return

        files = [
            f for f in EXPORTS_DIR.iterdir()
            if f.is_file() and not f.name.startswith(".")
        ]
        if not files:
            console.print(Panel("[dim]Aucun export trouvé dans exports/[/dim]", border_style="dim"))
            return

        files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

        table = Table(
            title=f"Exports disponibles ({len(files)} fichier(s))",
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE_HEAVY,
        )
        table.add_column("Fichier", style="magenta")
        table.add_column("Type", style="cyan", width=10)
        table.add_column("Date", style="dim white", width=16)
        table.add_column("Taille", style="dim white", width=8)

        _TYPE_MAP = {
            "report_":        "Markdown",
            "commands_":      "TXT",
            "check_report_":  "Rapport",
            "results_":       "Capture",
        }
        _EXT_MAP = {".html": "HTML", ".json": "JSON"}

        for f in files:
            stat = f.stat()
            size = stat.st_size
            size_str = f"{size // 1024} KB" if size >= 1024 else f"{size} B"
            date_str = datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m %H:%M")
            ftype = next(
                (v for k, v in _TYPE_MAP.items() if f.name.startswith(k)),
                _EXT_MAP.get(f.suffix, f.suffix[1:].upper() or "—"),
            )
            table.add_row(f.name, ftype, date_str, size_str)

        console.print()
        console.print(table)
