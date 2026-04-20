#!/usr/bin/env python3
"""
AUTOHACK LAB COMMANDER — Point d'entrée principal.

Usage interactif :
    python3 main.py

Mode non-interactif :
    python3 main.py --run sys_001          # exécuter une commande par ID
    python3 main.py --dry-run sys_001      # afficher sans exécuter
    python3 main.py --search tor           # rechercher dans le catalogue
    python3 main.py --export md            # exporter le catalogue (md|txt|json|html)
    python3 main.py --check                # lancer toutes les vérifications safe
    python3 main.py --list-ids             # lister tous les IDs du catalogue
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()


def build_parser() -> argparse.ArgumentParser:
    from config.settings import APP_VERSION
    parser = argparse.ArgumentParser(
        prog="autohack",
        description="AUTOHACK LAB COMMANDER — Centralisateur de commandes de lab",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {APP_VERSION}")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--run",      metavar="CMD_ID",  help="Exécuter une commande par son ID")
    group.add_argument("--dry-run",  metavar="CMD_ID",  help="Afficher une commande sans l'exécuter")
    group.add_argument("--search",   metavar="KEYWORD", help="Rechercher dans le catalogue (multi-mots)")
    group.add_argument("--pack",     metavar="PACK",    help="Afficher un pack de commandes guidé")
    group.add_argument("--export",   metavar="FORMAT",  choices=["md", "txt", "json", "html"],
                       help="Exporter le catalogue (md | txt | json | html)")
    group.add_argument("--check",    action="store_true", help="Lancer toutes les vérifications safe")
    group.add_argument("--list-ids", action="store_true", help="Lister tous les IDs du catalogue")
    group.add_argument("--list-categories", action="store_true", help="Lister les catégories disponibles")
    group.add_argument("--stats",   action="store_true", help="Statistiques du catalogue")
    group.add_argument("--favorites", action="store_true", help="Afficher les commandes favorites")
    group.add_argument("--generate-completion", metavar="SHELL", choices=["bash", "zsh"],
                       help="Générer le script de complétion shell (bash | zsh)")
    group.add_argument("--tag", metavar="TAG",
                       help="Lister les commandes ayant un tag donné")
    group.add_argument("--missing-tools", action="store_true",
                       help="Lister les outils requis non installés")
    group.add_argument("--install-profile", choices=["basic", "advanced", "all"],
                       help="Installer les dépendances manquantes d'un profil (basic | advanced | all)")
    parser.add_argument("--category", metavar="CAT",
                        help="Lister une catégorie, ou filtrer --search par catégorie")
    parser.add_argument("--safe", action="store_true",
                        help="Filtrer --search sur les commandes safe")
    parser.add_argument("--dangerous", action="store_true",
                        help="Filtrer --search sur les commandes dangereuses")
    parser.add_argument("--tool", metavar="TOOL",
                        help="Filtrer --search sur l'outil requis")
    parser.add_argument("--limit", metavar="N", type=int,
                        help="Limiter le nombre de résultats --search")
    parser.add_argument("--install-dry-run", action="store_true",
                        help="Afficher les commandes d'installation sans les exécuter")
    parser.add_argument("-y", "--yes", action="store_true",
                        help="Confirmer automatiquement les installations")
    return parser


def _get_core():
    """Instancie le minimum nécessaire pour le mode non-interactif."""
    from core.catalog import CommandCatalog
    from core.executor import CommandExecutor
    from core.checker import ToolChecker
    catalog = CommandCatalog()
    executor = CommandExecutor()
    checker = ToolChecker(catalog)
    return catalog, executor, checker


def cli_run(cmd_id: str) -> None:
    catalog, executor, checker = _get_core()
    cmd = catalog.get_by_id(cmd_id)
    if not cmd:
        console.print(f"[bold red]❌ ID introuvable : {cmd_id}[/bold red]")
        sys.exit(1)
    code = executor.confirm_and_run(cmd)
    sys.exit(0 if code in (None, 0) else code)


def cli_dry_run(cmd_id: str) -> None:
    catalog, executor, _ = _get_core()
    cmd = catalog.get_by_id(cmd_id)
    if not cmd:
        console.print(f"[bold red]❌ ID introuvable : {cmd_id}[/bold red]")
        sys.exit(1)
    executor.dry_run(cmd)


def cli_search(
    keyword: str,
    category: str | None = None,
    tool: str | None = None,
    safe: bool = False,
    dangerous: bool = False,
    limit: int | None = None,
) -> None:
    catalog, _, _ = _get_core()
    results = catalog.search(keyword)
    filters = []
    if safe and dangerous:
        console.print("[bold red]❌ --safe et --dangerous sont incompatibles.[/bold red]")
        sys.exit(1)
    if category:
        resolved_cat = catalog.resolve_category(category)
        if not resolved_cat:
            available = ", ".join(sorted(catalog.get_categories()))
            console.print(
                f"[bold red]❌ Catégorie inconnue : {category}[/bold red]\n"
                f"[dim]Disponibles : {available}[/dim]"
            )
            sys.exit(1)
        results = [cmd for cmd in results if cmd["category"] == resolved_cat]
        filters.append(f"category={resolved_cat}")
    if tool:
        wanted_tool = tool.lower().strip()
        results = [cmd for cmd in results if cmd.get("tool_required", "").lower() == wanted_tool]
        filters.append(f"tool={wanted_tool}")
    if safe:
        results = [cmd for cmd in results if cmd.get("safe_to_run")]
        filters.append("safe")
    if dangerous:
        results = [cmd for cmd in results if cmd.get("dangerous")]
        filters.append("dangerous")
    if limit is not None:
        if limit < 1:
            console.print("[bold red]❌ --limit doit être supérieur à 0.[/bold red]")
            sys.exit(1)
        results = results[:limit]
        filters.append(f"limit={limit}")
    if not results:
        console.print(f"[yellow]Aucun résultat pour « {keyword} »[/yellow]")
        sys.exit(0)
    suffix = f" [dim]({' · '.join(filters)})[/dim]" if filters else ""
    console.print(f"\n[bold green]{len(results)} résultat(s) pour « {keyword} »[/bold green]{suffix}\n")
    table = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE_HEAVY)
    table.add_column("ID", style="dim", width=10)
    table.add_column("Catégorie", style="cyan", width=14)
    table.add_column("Nom", style="bold white", min_width=22)
    table.add_column("Outil", style="yellow", width=14)
    table.add_column("Commande", style="magenta")
    for r in results:
        table.add_row(r["id"], r["category"], r["name"], r.get("tool_required", ""), r["command"][:60])
    console.print(table)


def cli_pack(pack_name: str) -> None:
    from core.packs import get_pack, list_pack_names

    catalog, _, checker = _get_core()
    pack = get_pack(pack_name)
    if not pack:
        console.print(
            f"[bold red]❌ Pack inconnu : {pack_name}[/bold red]\n"
            f"[dim]Disponibles : {', '.join(list_pack_names())}[/dim]"
        )
        sys.exit(1)

    console.print(f"\n[bold cyan]{pack.title}[/bold cyan] [dim]({pack.name})[/dim]")
    console.print(f"[dim]{pack.description}[/dim]\n")
    table = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE_HEAVY)
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("ID", style="dim", width=10)
    table.add_column("Catégorie", style="cyan", width=14)
    table.add_column("Nom", style="bold white", min_width=22)
    table.add_column("Outil", style="yellow", width=14)
    table.add_column("Dispo", width=6)
    table.add_column("Commande", style="magenta", min_width=28)
    for index, cmd_id in enumerate(pack.command_ids, start=1):
        cmd = catalog.get_by_id(cmd_id)
        if not cmd:
            table.add_row(str(index), cmd_id, "[red]?[/red]", "[red]ID introuvable[/red]", "", "", "")
            continue
        tool = cmd.get("tool_required", "")
        badge = checker.badge(tool) if tool else "  "
        table.add_row(
            str(index),
            cmd["id"],
            cmd["category"],
            cmd["name"],
            tool,
            badge,
            cmd["command"][:55],
        )
    console.print(table)


def cli_export(fmt: str) -> None:
    from core.exporter import Exporter
    from core.config_manager import ConfigManager
    catalog, _, _ = _get_core()
    config = ConfigManager()
    exporter = Exporter(catalog.get_all(), export_dir=config.get("export_dir"))
    dispatch = {"md": exporter.export_markdown, "txt": exporter.export_txt, "json": exporter.export_json, "html": exporter.export_html}
    path = dispatch[fmt]()
    console.print(f"[bold green]✅ Export créé :[/bold green] [magenta]{path}[/magenta]")


def cli_check() -> None:
    import subprocess
    catalog, _, _ = _get_core()
    safe = catalog.get_safe_commands()
    console.print(f"[bold]Exécution de {len(safe)} vérifications…[/bold]\n")
    ok = fail = 0
    for cmd in safe:
        try:
            r = subprocess.run(cmd["command"], shell=True, capture_output=True, text=True, timeout=10)
            code = r.returncode
        except Exception:
            code = -1
        icon = "✅" if code == 0 else "❌"
        if code == 0:
            ok += 1
        else:
            fail += 1
        console.print(f"  {icon} [{cmd['id']}] {cmd['name']}")
    console.print(f"\n[bold green]{ok} OK[/bold green]  [bold red]{fail} échec(s)[/bold red]")


def cli_list_ids() -> None:
    catalog, _, _ = _get_core()
    for cmd in catalog.get_all():
        print(f"{cmd['id']}\t{cmd['category']}\t{cmd['name']}")


def cli_category(cat: str) -> None:
    from config.settings import CATEGORY_LABELS, CATEGORY_ICONS
    catalog, _, checker = _get_core()
    available = catalog.get_categories()
    resolved_cat = catalog.resolve_category(cat)
    if not resolved_cat:
        console.print(
            f"[bold red]❌ Catégorie inconnue : {cat}[/bold red]\n"
            f"[dim]Disponibles : {', '.join(sorted(available))}[/dim]"
        )
        sys.exit(1)
    commands = catalog.get_by_category(resolved_cat)
    label = CATEGORY_LABELS.get(resolved_cat, resolved_cat)
    icon = CATEGORY_ICONS.get(resolved_cat, "")
    console.print(f"\n[bold]{icon}  {label}[/bold]  [dim]({len(commands)} commandes)[/dim]\n")
    table = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE_HEAVY)
    table.add_column("ID", style="dim", width=10)
    table.add_column("Nom", style="bold white", min_width=24)
    table.add_column("Commande", style="magenta", min_width=30)
    table.add_column("Dispo", width=6)
    for cmd in commands:
        tool = cmd.get("tool_required", "")
        badge = checker.badge(tool) if tool else "  "
        danger = " ⚠" if cmd.get("dangerous") else ""
        table.add_row(cmd["id"], cmd["name"] + danger, cmd["command"][:55], badge)
    console.print(table)


def cli_stats() -> None:
    from config.settings import CATEGORY_LABELS, CATEGORY_ICONS
    catalog, _, checker = _get_core()
    cmds = catalog.get_all()
    total = len(cmds)
    safe = sum(1 for c in cmds if c.get("safe_to_run"))
    dangerous = sum(1 for c in cmds if c.get("dangerous"))
    sudo = sum(1 for c in cmds if c.get("requires_sudo"))
    tools = {c.get("tool_required") for c in cmds if c.get("tool_required")}
    tools_ok = sum(1 for t in tools if checker.check(t))

    console.print("\n[bold]AUTOHACK — Statistiques du catalogue[/bold]\n")

    summary = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    summary.add_column("Clé", style="dim")
    summary.add_column("Valeur", style="bold white")
    summary.add_row("Total commandes",     str(total))
    summary.add_row("Safe (sans confirm)", f"{safe}  [dim]({safe*100//total}%)[/dim]")
    summary.add_row("Dangereuses",         f"[red]{dangerous}[/red]")
    summary.add_row("Requièrent sudo",     str(sudo))
    summary.add_row("Outils couverts",     f"{len(tools)}")
    summary.add_row("Outils installés",    f"[green]{tools_ok}[/green] / {len(tools)}")
    console.print(summary)

    cat_table = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE_HEAVY)
    cat_table.add_column("Catégorie", style="bold white", min_width=20)
    cat_table.add_column("Cmds", style="dim", width=6)
    cat_table.add_column("Safe", style="green", width=6)
    cat_table.add_column("Sudo", style="yellow", width=6)
    for cat in catalog.get_categories():
        cat_cmds = catalog.get_by_category(cat)
        icon = CATEGORY_ICONS.get(cat, "")
        label = CATEGORY_LABELS.get(cat, cat)
        n_safe = sum(1 for c in cat_cmds if c.get("safe_to_run"))
        n_sudo = sum(1 for c in cat_cmds if c.get("requires_sudo"))
        cat_table.add_row(f"{icon} {label}", str(len(cat_cmds)), str(n_safe), str(n_sudo) or "—")
    console.print(cat_table)


def cli_favorites() -> None:
    from core.favorites import Favorites
    catalog, _, checker = _get_core()
    favs = Favorites()
    ids = favs.all_ids()
    if not ids:
        console.print("[dim]Aucun favori. Utilisez [bold]f[/bold] sur une fiche commande pour en ajouter.[/dim]")
        return
    console.print(f"\n[bold yellow]⭐ {len(ids)} favori(s)[/bold yellow]\n")
    table = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE_HEAVY)
    table.add_column("ID", style="dim", width=10)
    table.add_column("Catégorie", style="cyan", width=14)
    table.add_column("Nom", style="bold white", min_width=24)
    table.add_column("Commande", style="magenta")
    for cmd_id in ids:
        cmd = catalog.get_by_id(cmd_id)
        if cmd:
            table.add_row(cmd["id"], cmd["category"], cmd["name"], cmd["command"][:50])
        else:
            table.add_row(cmd_id, "[red]?[/red]", "[red]ID introuvable[/red]", "")
    console.print(table)


def cli_tag(tag: str) -> None:
    catalog, _, checker = _get_core()
    tag_norm = tag.lower().strip()
    results = [
        cmd for cmd in catalog.get_all()
        if tag_norm in [t.lower() for t in cmd.get("tags", [])]
    ]
    if not results:
        console.print(f"[yellow]Aucune commande avec le tag « {tag} »[/yellow]")
        sys.exit(0)
    console.print(f"\n[bold green]{len(results)} commande(s) avec le tag « {tag} »[/bold green]\n")
    table = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE_HEAVY)
    table.add_column("ID", style="dim", width=10)
    table.add_column("Catégorie", style="cyan", width=14)
    table.add_column("Nom", style="bold white", min_width=22)
    table.add_column("Commande", style="magenta")
    for r in results:
        table.add_row(r["id"], r["category"], r["name"], r["command"][:55])
    console.print(table)


def cli_missing_tools() -> None:
    catalog, _, checker = _get_core()
    missing = checker.missing_tools()
    if not missing:
        console.print("[bold green]✅ Tous les outils requis sont installés.[/bold green]")
        return
    console.print(f"\n[bold red]❌ {len(missing)} outil(s) manquant(s) :[/bold red]\n")
    table = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE_HEAVY)
    table.add_column("Outil", style="bold white", width=20)
    table.add_column("Installation", style="magenta")
    for tool in sorted(missing):
        table.add_row(tool, checker.install_hint(tool))
    console.print(table)


def cli_install_profile(profile: str, dry_run: bool = False, assume_yes: bool = False) -> None:
    from rich.prompt import Confirm

    from core.installer import ToolInstaller

    catalog, _, _ = _get_core()
    required_tools = [cmd.get("tool_required", "") for cmd in catalog.get_all()]
    installer = ToolInstaller(required_tools)
    plan = installer.plan(profile)
    commands = plan.commands()

    console.print(f"\n[bold]Installation profile:[/bold] [cyan]{profile}[/cyan]\n")

    table = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE_HEAVY)
    table.add_column("Manager", style="bold white", width=12)
    table.add_column("Packages / command", style="magenta")
    if plan.apt_packages:
        table.add_row("apt", " ".join(plan.apt_packages))
    if plan.pipx_packages:
        table.add_row("pipx", " ".join(plan.pipx_packages))
    if plan.go_packages:
        table.add_row("go", "\n".join(plan.go_packages))
    if not commands:
        table.add_row("auto", "[green]No automatic installs needed[/green]")
    console.print(table)

    if plan.manual:
        manual = Table(show_header=True, header_style="bold yellow", box=box.SIMPLE_HEAVY)
        manual.add_column("Manual tool", style="bold white", width=22)
        manual.add_column("Reason / instruction", style="yellow")
        for tool, hint in plan.manual.items():
            manual.add_row(tool, hint)
        console.print("\n[bold yellow]Manual steps still required:[/bold yellow]")
        console.print(manual)

    if commands:
        console.print("\n[bold]Commands to run:[/bold]")
        for command in commands:
            console.print("  [cyan]" + " ".join(command) + "[/cyan]")

    if dry_run:
        console.print("\n[bold yellow]Dry-run only. Nothing was installed.[/bold yellow]")
        return
    if not commands:
        console.print("\n[bold green]Nothing to install automatically.[/bold green]")
        return

    if not assume_yes and not Confirm.ask(
        "\n[bold yellow]Run these installation commands now?[/bold yellow]",
        default=False,
    ):
        console.print("[dim]Installation cancelled.[/dim]")
        return

    code = installer.run(plan)
    if code != 0:
        console.print(f"[bold red]Installation failed with exit code {code}.[/bold red]")
        sys.exit(code)
    console.print("[bold green]Installation commands completed.[/bold green]")


def cli_list_categories() -> None:
    from config.settings import CATEGORY_LABELS, CATEGORY_ICONS
    catalog, _, _ = _get_core()
    console.print()
    for cat in catalog.get_categories():
        label = CATEGORY_LABELS.get(cat, cat)
        icon = CATEGORY_ICONS.get(cat, "")
        count = len(catalog.get_by_category(cat))
        print(f"{icon}  {cat:<14} {label:<30} ({count} commandes)")


def cli_generate_completion(shell: str) -> None:
    from core.catalog import CommandCatalog
    from core.packs import list_pack_names
    catalog = CommandCatalog()
    ids = " ".join(cmd["id"] for cmd in catalog.get_all())
    cats = " ".join(catalog.get_categories())
    packs = " ".join(list_pack_names())

    if shell == "bash":
        script = f"""# Autohack bash completion — source this file or add to ~/.bashrc
# Usage: source <(python3 main.py --generate-completion bash)

_autohack_complete() {{
    local cur prev
    COMPREPLY=()
    cur="${{COMP_WORDS[COMP_CWORD]}}"
    prev="${{COMP_WORDS[COMP_CWORD-1]}}"

    local opts="--run --dry-run --search --pack --category --safe --dangerous --tool --limit --export --check --list-ids --list-categories --stats --favorites --generate-completion --tag --missing-tools --install-profile --install-dry-run --yes --version"
    local ids="{ids}"
    local cats="{cats}"
    local packs="{packs}"
    local formats="md txt json html"
    local shells="bash zsh"
    local profiles="basic advanced all"

    case "$prev" in
        --run|--dry-run) COMPREPLY=($(compgen -W "$ids" -- "$cur")) ; return ;;
        --pack)          COMPREPLY=($(compgen -W "$packs" -- "$cur")) ; return ;;
        --category)      COMPREPLY=($(compgen -W "$cats" -- "$cur")) ; return ;;
        --export)        COMPREPLY=($(compgen -W "$formats" -- "$cur")) ; return ;;
        --generate-completion) COMPREPLY=($(compgen -W "$shells" -- "$cur")) ; return ;;
        --install-profile) COMPREPLY=($(compgen -W "$profiles" -- "$cur")) ; return ;;
    esac

    if [[ "$cur" == -* ]]; then
        COMPREPLY=($(compgen -W "$opts" -- "$cur"))
    else
        COMPREPLY=($(compgen -W "$ids" -- "$cur"))
    fi
}}

complete -F _autohack_complete autohack
complete -F _autohack_complete "python3 main.py"
"""
    else:  # zsh
        script = f"""#compdef autohack
# Autohack zsh completion — add to fpath or eval
# Usage: eval "$(python3 main.py --generate-completion zsh)"

_autohack() {{
    local -a ids cats packs
    ids=({ids})
    cats=({cats})
    packs=({packs})

    _arguments \\
        '--run[Exécuter une commande]:id:($ids)' \\
        '--dry-run[Afficher sans exécuter]:id:($ids)' \\
        '--search[Rechercher]:keyword:' \\
        '--pack[Afficher un pack guidé]:pack:($packs)' \\
        '--category[Lister une catégorie]:cat:($cats)' \\
        '--safe[Filtrer la recherche sur les commandes safe]' \\
        '--dangerous[Filtrer la recherche sur les commandes dangereuses]' \\
        '--tool[Filtrer la recherche par outil]:tool:' \\
        '--limit[Limiter les résultats de recherche]:limit:' \\
        '--export[Exporter le catalogue]:format:(md txt json html)' \\
        '--check[Vérifications safe]' \\
        '--list-ids[Lister les IDs]' \\
        '--list-categories[Lister les catégories]' \\
        '--stats[Statistiques]' \\
        '--favorites[Afficher les favoris]' \\
        '--generate-completion[Complétion shell]:shell:(bash zsh)' \\
        '--tag[Lister les commandes ayant un tag]:tag:' \\
        '--missing-tools[Lister les outils requis non installés]' \\
        '--install-profile[Installer les dépendances manquantes]:profile:(basic advanced all)' \\
        '--install-dry-run[Afficher les commandes sans installer]' \\
        '--yes[Confirmer automatiquement]' \\
        '--version[Afficher la version]' \\
        ':id:($ids)'
}}

_autohack "$@"
"""

    print(script)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.run:
        cli_run(args.run)
    elif getattr(args, "dry_run", None):
        cli_dry_run(args.dry_run)
    elif args.search:
        cli_search(args.search, args.category, args.tool, args.safe, args.dangerous, args.limit)
    elif getattr(args, "pack", None):
        cli_pack(args.pack)
    elif args.export:
        cli_export(args.export)
    elif args.check:
        cli_check()
    elif args.list_ids:
        cli_list_ids()
    elif args.category:
        cli_category(args.category)
    elif getattr(args, "list_categories", False):
        cli_list_categories()
    elif getattr(args, "stats", False):
        cli_stats()
    elif getattr(args, "favorites", False):
        cli_favorites()
    elif getattr(args, "generate_completion", None):
        cli_generate_completion(args.generate_completion)
    elif getattr(args, "tag", None):
        cli_tag(args.tag)
    elif getattr(args, "missing_tools", False):
        cli_missing_tools()
    elif getattr(args, "install_profile", None):
        cli_install_profile(args.install_profile, args.install_dry_run, args.yes)
    else:
        # Mode interactif par défaut
        try:
            from menus.main_menu import MainMenu
            MainMenu().run()
        except KeyboardInterrupt:
            console.print("\n\n[dim]Interruption (Ctrl+C). Au revoir.[/dim]")
            sys.exit(0)
        except Exception as exc:
            console.print(Panel(
                f"[bold red]Erreur inattendue :[/bold red]\n{exc}\n\n"
                "[dim]Vérifiez que commands_catalog.json est présent et valide.[/dim]",
                title="[bold red]Erreur[/bold red]",
                border_style="red",
            ))
            sys.exit(1)


if __name__ == "__main__":
    main()
