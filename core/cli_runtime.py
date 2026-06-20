from __future__ import annotations

import argparse

import sys
from pathlib import Path

from core import cli_commands as commands
from rich.console import Console
from rich.panel import Panel

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
    group.add_argument("--run-pack", metavar="PACK",    help="Exécuter un pack guidé pas-à-pas")
    group.add_argument("--generate-playbook", metavar="PACK", help="Générer un playbook markdown depuis un pack")
    group.add_argument("--catalog-diff", metavar="RANGE", help="Comparer deux refs de catalogue (ex: v0.3.0..v0.4.0)")
    group.add_argument("--usage-metrics", action="store_true", help="Afficher les métriques d'usage locales")
    group.add_argument("--verify-audit-chain", action="store_true", help="Vérifier l'intégrité de la chaîne d'audit")
    group.add_argument("--serve-api", action="store_true", help="Lancer l'API locale read-only")
    group.add_argument("--apply-profile", metavar="PROFILE", help="Appliquer un profil environnement (lab1/lab2/ctf/client)")
    group.add_argument("--approve-command", metavar="CMD_ID", help="Approuver une commande en file secondaire")
    group.add_argument("--list-approvals", action="store_true", help="Lister les commandes en attente d'approbation")
    group.add_argument("--export",   metavar="FORMAT",  choices=["md", "txt", "json", "html"],
                       help="Exporter le catalogue (md | txt | json | html)")
    group.add_argument("--export-exec-report", action="store_true", help="Exporter le rapport HTML des exécutions")
    group.add_argument("--check",    action="store_true", help="Lancer toutes les vérifications safe")
    group.add_argument("--list-ids", action="store_true", help="Lister tous les IDs du catalogue")
    group.add_argument("--list-categories", action="store_true", help="Lister les catégories disponibles")
    group.add_argument("--stats",   action="store_true", help="Statistiques du catalogue")
    group.add_argument("--favorites", action="store_true", help="Afficher les commandes favorites")
    group.add_argument("--generate-completion", metavar="SHELL", choices=["bash", "zsh"],
                       help="Générer le script de complétion shell (bash | zsh)")
    group.add_argument("--refresh-tools", action="store_true", help="Vider le cache des outils détectés")
    group.add_argument("--export-session", metavar="FILE", help="Exporter la session (history + variables + loot) en JSON")
    group.add_argument("--replay-session", metavar="FILE", help="Afficher un replay de session exportée")
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
    parser.add_argument("--regex", action="store_true",
                        help="Interpréter --search comme regex")
    parser.add_argument("--sort-by", choices=["score", "risk"],
                        default="score",
                        help="Tri de --search: score | risk")
    parser.add_argument("--limit", metavar="N", type=int,
                        help="Limiter le nombre de résultats --search")
    parser.add_argument("--install-dry-run", action="store_true",
                        help="Afficher les commandes d'installation sans les exécuter")
    parser.add_argument("-y", "--yes", action="store_true",
                        help="Confirmer automatiquement les installations")
    return parser


def _app_module():
    return commands


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    app = _app_module()

    if args.run:
        app.cli_run(args.run)
    elif getattr(args, "generate_playbook", None):
        app.cli_generate_playbook(args.generate_playbook)
    elif getattr(args, "catalog_diff", None):
        app.cli_catalog_diff(args.catalog_diff)
    elif getattr(args, "usage_metrics", False):
        app.cli_usage_metrics()
    elif getattr(args, "verify_audit_chain", False):
        app.cli_verify_audit_chain()
    elif getattr(args, "serve_api", False):
        app.cli_serve_api()
    elif getattr(args, "apply_profile", None):
        app.cli_apply_profile(args.apply_profile)
    elif getattr(args, "approve_command", None):
        from core.approval_queue import ApprovalQueue
        from core.rbac import can

        if not can(app._role(), "approve"):
            console.print("[bold red]❌ Action non autorisée pour ce rôle.[/bold red]")
            sys.exit(1)
        ok = ApprovalQueue().approve(args.approve_command)
        console.print("[bold green]✅ Approuvée.[/bold green]" if ok else "[yellow]Aucune entrée en attente.[/yellow]")
    elif getattr(args, "list_approvals", False):
        from core.approval_queue import ApprovalQueue

        pending = ApprovalQueue().list_pending()
        if not pending:
            console.print("[dim]Aucune commande en attente.[/dim]")
        else:
            for cmd_id in pending:
                print(cmd_id)
    elif getattr(args, "dry_run", None):
        app.cli_dry_run(args.dry_run)
    elif args.search:
        app.cli_search(args.search, args.category, args.tool, args.safe, args.dangerous, args.limit, args.regex, args.sort_by)
    elif getattr(args, "pack", None):
        app.cli_pack(args.pack)
    elif getattr(args, "run_pack", None):
        app.cli_run_pack(args.run_pack)
    elif args.export:
        app.cli_export(args.export)
    elif getattr(args, "export_exec_report", False):
        app.cli_export_exec_report()
    elif args.check:
        app.cli_check()
    elif args.list_ids:
        app.cli_list_ids()
    elif args.category:
        app.cli_category(args.category)
    elif getattr(args, "list_categories", False):
        app.cli_list_categories()
    elif getattr(args, "stats", False):
        app.cli_stats()
    elif getattr(args, "favorites", False):
        app.cli_favorites()
    elif getattr(args, "generate_completion", None):
        app.cli_generate_completion(args.generate_completion)
    elif getattr(args, "tag", None):
        app.cli_tag(args.tag)
    elif getattr(args, "missing_tools", False):
        app.cli_missing_tools()
    elif getattr(args, "install_profile", None):
        app.cli_install_profile(args.install_profile, args.install_dry_run, args.yes)
    elif getattr(args, "refresh_tools", False):
        _, _, checker = app._get_core()
        checker.refresh()
        console.print("[bold green]✅ Cache outils vidé.[/bold green]")
    elif getattr(args, "export_session", None):
        from core.session_replay import export_session

        from core.session_history import SessionHistory, HISTORY_PATH
        from core.variables import VariableStore
        from core.loot import LootVault

        out = Path(args.export_session)
        export_session(out, SessionHistory(persist_path=HISTORY_PATH), VariableStore(), LootVault())
        console.print(f"[bold green]✅ Session exportée:[/bold green] {out}")
    elif getattr(args, "replay_session", None):
        from core.session_replay import load_session

        data = load_session(Path(args.replay_session))
        hist = data.get("history", [])
        console.print(f"[bold]Replay[/bold] entries={len(hist)} variables={len(data.get('variables', {}))} loot={len(data.get('loot', []))}")
        for item in hist[:30]:
            print(f"{item.get('timestamp','')}\t{item.get('id','')}\t{item.get('exit_code','')}\t{item.get('command','')[:80]}")
    else:
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
