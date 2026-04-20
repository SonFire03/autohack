from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich import box

from menus.base import BaseMenu
from config.settings import EXPORTS_DIR as _DEFAULT_EXPORTS_DIR

console = Console()


class RunAllChecksMenu(BaseMenu):
    TITLE = "Exécuter toutes les vérifications"

    def show(self) -> None:
        self._header("🚦 Exécuter toutes les vérifications")

        safe_cmds = self._catalog.get_safe_commands()
        console.print(
            f"  [bold white]{len(safe_cmds)} commandes[/bold white] "
            f"[dim]marquées safe_to_run=True dans le catalogue.[/dim]\n"
            "  Aucune confirmation individuelle requise — toutes sont en lecture seule.\n"
        )

        from rich.prompt import Confirm
        if not Confirm.ask(
            f"[bold yellow]Lancer les {len(safe_cmds)} vérifications maintenant ?[/bold yellow]",
            default=False,
        ):
            console.print("[dim]Annulé.[/dim]")
            return

        results = self._run_all(safe_cmds)
        self._show_results_table(results)
        self._offer_save(results)
        console.input("\n[dim]Appuyez sur Entrée pour retourner au menu principal…[/dim]")

    def _run_all(self, commands: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        import subprocess

        results = []
        for cmd in track(commands, description="Vérifications en cours…"):
            command_str = cmd.get("command", "")
            try:
                result = subprocess.run(
                    command_str,
                    shell=True,
                    text=True,
                    capture_output=True,
                    timeout=15,
                )
                code = result.returncode
                stdout = result.stdout.strip()[:200]
                stderr = result.stderr.strip()[:100]
            except Exception as exc:
                code = -1
                stdout = ""
                stderr = str(exc)[:100]

            results.append({
                **cmd,
                "exit_code": code,
                "stdout":    stdout,
                "stderr":    stderr,
            })

        return results

    def _show_results_table(self, results: List[Dict[str, Any]]) -> None:
        ok = sum(1 for r in results if r["exit_code"] == 0)
        fail = len(results) - ok

        console.print(
            f"\n[bold green]✅ {ok} succès[/bold green]  "
            f"[bold red]❌ {fail} échec(s)[/bold red]\n"
        )

        table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE_HEAVY,
            expand=True,
        )
        table.add_column("ID", style="dim", width=10)
        table.add_column("Nom", style="bold white", min_width=22)
        table.add_column("Statut", width=10)
        table.add_column("Sortie (extrait)", style="dim", min_width=30)

        for r in results:
            if r["exit_code"] == 0:
                status = "[green]✅ OK[/green]"
                output = r["stdout"][:60] if r["stdout"] else "[dim](vide)[/dim]"
            else:
                status = f"[red]❌ {r['exit_code']}[/red]"
                output = r["stderr"][:60] if r["stderr"] else r["stdout"][:60]

            table.add_row(r["id"], r["name"], status, output)

        console.print(table)

    def _offer_save(self, results: List[Dict[str, Any]]) -> None:
        from rich.prompt import Confirm
        if not Confirm.ask("\n[bold yellow]Sauvegarder ce rapport ?[/bold yellow]", default=True):
            return

        configured = self._config.get("export_dir")
        export_dir = Path(configured) if configured else _DEFAULT_EXPORTS_DIR
        export_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
        path = export_dir / f"check_report_{ts}.md"
        ok = sum(1 for r in results if r["exit_code"] == 0)
        fail = len(results) - ok

        lines = [
            f"# Rapport de vérifications — {ts}",
            "",
            f"**Total :** {len(results)}  |  **✅ OK :** {ok}  |  **❌ Échec :** {fail}",
            "",
            "| ID | Nom | Statut | Sortie |",
            "|---|---|---|---|",
        ]
        for r in results:
            stat = "✅" if r["exit_code"] == 0 else f"❌ ({r['exit_code']})"
            out = (r["stdout"] or r["stderr"] or "").replace("\n", " ")[:80]
            lines.append(f"| {r['id']} | {r['name']} | {stat} | {out} |")

        path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"[bold green]✅ Rapport sauvegardé :[/bold green] [magenta]{path}[/magenta]")
