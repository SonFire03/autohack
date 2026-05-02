"""Wordlist Browser — scan system wordlists with size, line count and path copy."""
import os
import subprocess
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from core.theme import help_footer, status_bar

console = Console()

SEARCH_DIRS = [
    Path("/usr/share/wordlists"),
    Path("/usr/share/seclists") if Path("/usr/share/seclists").exists() else None,
    Path("/opt/SecLists"),
    Path("/usr/share/john"),
    Path("/usr/share/dirb/wordlists"),
    Path("/usr/share/dirbuster/wordlists"),
    Path("/usr/share/metasploit-framework/data/wordlists"),
    Path.home() / "wordlists",
]


def _fmt_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f}{unit}"
        n /= 1024
    return f"{n:.1f}GB"


def _count_lines(path: Path) -> str:
    try:
        result = subprocess.run(["wc", "-l", str(path)], capture_output=True, text=True, timeout=5)
        return result.stdout.strip().split()[0]
    except Exception:
        return "?"


def _scan() -> list[dict]:
    found = []
    seen = set()
    for d in SEARCH_DIRS:
        if d is None or not d.exists():
            continue
        try:
            for p in sorted(d.rglob("*.txt")):
                if str(p) in seen:
                    continue
                seen.add(str(p))
                try:
                    size = p.stat().st_size
                    found.append({"path": p, "size": size, "dir": str(d)})
                except Exception:
                    pass
        except Exception:
            pass
    return sorted(found, key=lambda x: x["size"], reverse=True)


KNOWN_LISTS = {
    "rockyou.txt":                   "🔑 Passwords — 14M mots de passe réels (RockYou breach)",
    "darkweb2017-top10000.txt":      "🔑 Passwords — Top 10k fuite darkweb",
    "common.txt":                    "🌐 Dirb — chemins web courants",
    "big.txt":                       "🌐 Dirb — chemins web étendus",
    "directory-list-2.3-medium.txt": "🌐 DirBuster — 220k répertoires",
    "directory-list-2.3-small.txt":  "🌐 DirBuster — 87k répertoires",
    "top-usernames-shortlist.txt":   "👤 Usernames courants",
    "unix-passwords.txt":            "🔑 Passwords Unix classiques",
    "names.txt":                     "👤 Prénoms courants",
    "subdomains-top1million-5000.txt": "🌐 Sous-domaines — top 5000",
    "SecLists":                      "📦 SecLists — collection complète",
}


class WordlistMenu:
    def __init__(self) -> None:
        self._cache: list[dict] | None = None

    def _get_lists(self) -> list[dict]:
        if self._cache is None:
            console.print("  [dim]Scan des wordlists…[/dim]")
            self._cache = _scan()
        return self._cache

    def show(self) -> None:
        page = 0
        per_page = 20
        filter_q = ""

        while True:
            console.clear()
            console.print(Panel(
                "[bold cyan]Wordlist Browser[/bold cyan]  [dim]— wordlists disponibles sur le système[/dim]",
                border_style="cyan", padding=(0, 1),
            ))
            console.print()

            all_lists = self._get_lists()
            if filter_q:
                shown = [w for w in all_lists if filter_q.lower() in str(w["path"]).lower()]
            else:
                shown = all_lists

            total_pages = max(1, (len(shown) + per_page - 1) // per_page)
            page = max(0, min(page, total_pages - 1))
            page_items = shown[page * per_page:(page + 1) * per_page]

            status_bar([
                ("Wordlists trouvées", str(len(all_lists)), "bold bright_cyan"),
                ("Filtre", filter_q or "aucun", "grey70"),
                (f"Page {page+1}/{total_pages}", f"{len(shown)} résultats", "grey70"),
            ])
            console.print()

            if not shown:
                console.print("  [dim]Aucune wordlist trouvée. Installez wordlists: apt install wordlists seclists[/dim]\n")
            else:
                t = Table(show_header=True, header_style="bold cyan",
                          box=box.SIMPLE_HEAVY, expand=True)
                t.add_column("#",       width=4,  style="bold yellow", justify="right")
                t.add_column("Nom",     width=36, style="bold white")
                t.add_column("Taille",  width=9,  style="bold green",  justify="right")
                t.add_column("Lignes",  width=10, style="grey70",       justify="right")
                t.add_column("Chemin",  style="dim")

                for i, w in enumerate(page_items, page * per_page + 1):
                    name = w["path"].name
                    desc = ""
                    for k, v in KNOWN_LISTS.items():
                        if k in str(w["path"]):
                            desc = f"  [dim]{v}[/dim]"
                            break
                    size_str = _fmt_size(w["size"])
                    t.add_row(
                        str(i),
                        name + desc,
                        size_str,
                        "?" ,
                        str(w["path"].parent),
                    )
                console.print(Panel(t, title=" Wordlists ", title_align="left",
                                    border_style="dim cyan", padding=(0, 1)))

            console.print()
            help_footer([
                ("<n>",       "copier le chemin complet"),
                ("l <n>",     "compter les lignes (wc -l)"),
                ("p <n>",     "prévisualiser (head -20)"),
                ("f <query>", "filtrer par nom"),
                ("fa",        "tout afficher"),
                ("n / p",     "page suivante / précédente"),
                ("b / q",     "retour"),
            ], title="Wordlist Browser")

            try:
                raw = console.input("\n  [bold cyan]>[/bold cyan] ").strip()
            except (KeyboardInterrupt, EOFError):
                break
            if not raw or raw in {"b", "q"}:
                break

            parts = raw.split(None, 1)
            cmd = parts[0].lower()

            if cmd == "n":
                page = min(page + 1, total_pages - 1)
            elif cmd == "pp":
                page = max(page - 1, 0)
            elif cmd == "fa":
                filter_q = ""; page = 0
            elif cmd == "f" and len(parts) >= 2:
                filter_q = parts[1]; page = 0
            elif cmd == "l" and len(parts) >= 2 and parts[1].isdigit():
                idx = int(parts[1]) - 1
                if 0 <= idx < len(shown):
                    path = shown[idx]["path"]
                    lines = _count_lines(path)
                    console.print(f"  [green]{lines}[/green] lignes dans {path.name}")
                    console.input("[dim]  Entrée…[/dim]")
            elif cmd == "p" and len(parts) >= 2 and parts[1].isdigit():
                idx = int(parts[1]) - 1
                if 0 <= idx < len(shown):
                    path = shown[idx]["path"]
                    console.print(f"\n  [dim]Aperçu:[/dim] {path}")
                    try:
                        result = subprocess.run(["head", "-20", str(path)],
                                                capture_output=True, text=True, timeout=5)
                        console.print(Panel(result.stdout, border_style="dim", padding=(0, 1)))
                    except Exception as e:
                        console.print(f"  [red]{e}[/red]")
                    console.input("[dim]  Entrée…[/dim]")
            elif cmd.isdigit():
                idx = int(cmd) - 1
                if 0 <= idx < len(shown):
                    path = str(shown[idx]["path"])
                    try:
                        import pyperclip; pyperclip.copy(path)
                        console.print(f"  [green]✓[/green] Chemin copié: {path}")
                    except Exception:
                        console.print(f"  [dim]Chemin: {path}[/dim]")
                    console.input("[dim]  Entrée…[/dim]")
