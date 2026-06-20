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

    subparsers = parser.add_subparsers(dest="command")

    search_parser = subparsers.add_parser("search", help="Rechercher dans le catalogue")
    search_parser.add_argument("keyword", metavar="KEYWORD", help="Mot-clé ou regex de recherche")
    search_parser.add_argument("--category", metavar="CAT", help="Filtrer par catégorie")
    search_parser.add_argument("--tool", metavar="TOOL", help="Filtrer par outil requis")
    search_parser.add_argument("--safe", action="store_true", help="Limiter aux commandes safe")
    search_parser.add_argument("--dangerous", action="store_true", help="Limiter aux commandes dangereuses")
    search_parser.add_argument("--regex", action="store_true", help="Interpréter la recherche comme regex")
    search_parser.add_argument("--sort-by", choices=["score", "risk"], default="score", help="Tri des résultats")
    search_parser.add_argument("--limit", metavar="N", type=int, help="Limiter le nombre de résultats")

    run_parser = subparsers.add_parser("run", help="Exécuter une commande")
    run_parser.add_argument("cmd_id", metavar="CMD_ID", help="Identifiant de commande")

    dry_run_parser = subparsers.add_parser("dry-run", help="Afficher une commande sans l'exécuter")
    dry_run_parser.add_argument("cmd_id", metavar="CMD_ID", help="Identifiant de commande")

    pack_parser = subparsers.add_parser("pack", help="Afficher un pack guidé")
    pack_parser.add_argument("pack", metavar="PACK", help="Nom du pack")

    run_pack_parser = subparsers.add_parser("run-pack", help="Exécuter un pack guidé pas-à-pas")
    run_pack_parser.add_argument("pack", metavar="PACK", help="Nom du pack")

    export_parser = subparsers.add_parser("export", help="Exporter le catalogue")
    export_parser.add_argument("format", choices=["md", "txt", "json", "html"], help="Format d'export")

    install_parser = subparsers.add_parser("install", help="Installer les dépendances d'un profil")
    install_parser.add_argument("--profile", choices=["basic", "advanced", "all"], required=True,
                                help="Profil à installer")
    install_parser.add_argument("--dry-run", action="store_true", help="Afficher les commandes sans exécuter")
    install_parser.add_argument("-y", "--yes", action="store_true", help="Confirmer automatiquement")

    subparsers.add_parser("list-ids", help="Lister tous les IDs du catalogue")
    subparsers.add_parser("list-categories", help="Lister les catégories disponibles")
    subparsers.add_parser("stats", help="Statistiques du catalogue")
    subparsers.add_parser("favorites", help="Afficher les commandes favorites")
    tag_parser = subparsers.add_parser("tag", help="Lister les commandes ayant un tag donné")
    tag_parser.add_argument("tag", metavar="TAG", help="Tag recherché")
    subparsers.add_parser("missing-tools", help="Lister les outils requis non installés")
    completion_parser = subparsers.add_parser("generate-completion", help="Générer un script de complétion shell")
    completion_parser.add_argument("shell", choices=["bash", "zsh"], help="Shell cible")

    session_parser = subparsers.add_parser("session", help="Exporter ou rejouer une session")
    session_sub = session_parser.add_subparsers(dest="session_command")
    session_export = session_sub.add_parser("export", help="Exporter la session")
    session_export.add_argument("file", metavar="FILE", help="Fichier de sortie JSON")
    session_replay = session_sub.add_parser("replay", help="Rejouer une session exportée")
    session_replay.add_argument("file", metavar="FILE", help="Fichier JSON à rejouer")

    catalog_parser = subparsers.add_parser("catalog", help="Inspecter le catalogue")
    catalog_sub = catalog_parser.add_subparsers(dest="catalog_command")
    catalog_sub.add_parser("list-ids", help="Lister tous les IDs")
    catalog_sub.add_parser("list-categories", help="Lister les catégories")
    catalog_sub.add_parser("stats", help="Statistiques du catalogue")
    catalog_sub.add_parser("favorites", help="Afficher les favoris")
    catalog_missing = catalog_sub.add_parser("missing-tools", help="Lister les outils requis non installés")
    catalog_missing.add_argument("--profile", choices=["basic", "advanced", "all"], help="Profil de référence optionnel")
    catalog_tag = catalog_sub.add_parser("tag", help="Lister les commandes ayant un tag")
    catalog_tag.add_argument("tag", metavar="TAG", help="Tag recherché")
    catalog_sub.add_parser("check", help="Lancer les vérifications safe")
    catalog_export = catalog_sub.add_parser("export", help="Exporter le catalogue")
    catalog_export.add_argument("format", choices=["md", "txt", "json", "html"], help="Format d'export")
    catalog_diff = catalog_sub.add_parser("diff", help="Comparer deux refs de catalogue")
    catalog_diff.add_argument("range_expr", metavar="RANGE", help="Référence de type refA..refB")
    catalog_search = catalog_sub.add_parser("search", help="Rechercher dans le catalogue")
    catalog_search.add_argument("keyword", metavar="KEYWORD", help="Mot-clé ou regex de recherche")
    catalog_search.add_argument("--category", metavar="CAT", help="Filtrer par catégorie")
    catalog_search.add_argument("--tool", metavar="TOOL", help="Filtrer par outil requis")
    catalog_search.add_argument("--safe", action="store_true", help="Limiter aux commandes safe")
    catalog_search.add_argument("--dangerous", action="store_true", help="Limiter aux commandes dangereuses")
    catalog_search.add_argument("--regex", action="store_true", help="Interpréter la recherche comme regex")
    catalog_search.add_argument("--sort-by", choices=["score", "risk"], default="score", help="Tri des résultats")
    catalog_search.add_argument("--limit", metavar="N", type=int, help="Limiter le nombre de résultats")

    admin_parser = subparsers.add_parser("admin", help="Actions d'administration")
    admin_sub = admin_parser.add_subparsers(dest="admin_command")
    admin_sub.add_parser("security-status", help="Afficher l'état de sécurité local")
    admin_sub.add_parser("usage-metrics", help="Afficher les métriques d'usage locales")
    admin_sub.add_parser("verify-audit-chain", help="Vérifier l'intégrité de la chaîne d'audit")
    admin_sub.add_parser("serve-api", help="Lancer l'API locale read-only")
    admin_apply = admin_sub.add_parser("apply-profile", help="Appliquer un profil environnement")
    admin_apply.add_argument("profile", metavar="PROFILE", help="Profil à appliquer")
    admin_approve = admin_sub.add_parser("approve", help="Approuver une commande en file secondaire")
    admin_approve.add_argument("cmd_id", metavar="CMD_ID", help="Identifiant de commande")
    admin_sub.add_parser("approvals", help="Lister les commandes en attente d'approbation")
    admin_sub.add_parser("refresh-tools", help="Vider le cache des outils détectés")
    admin_sub.add_parser("export-exec-report", help="Exporter le rapport HTML des exécutions")

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

    if getattr(args, "command", None) == "search":
        app.cli_search(
            args.keyword,
            args.category,
            args.tool,
            args.safe,
            args.dangerous,
            args.limit,
            args.regex,
            args.sort_by,
        )
    elif getattr(args, "command", None) == "run":
        app.cli_run(args.cmd_id)
    elif getattr(args, "command", None) == "dry-run":
        app.cli_dry_run(args.cmd_id)
    elif getattr(args, "command", None) == "pack":
        app.cli_pack(args.pack)
    elif getattr(args, "command", None) == "run-pack":
        app.cli_run_pack(args.pack)
    elif getattr(args, "command", None) == "export":
        app.cli_export(args.format)
    elif getattr(args, "command", None) == "install":
        app.cli_install(args.profile, args.dry_run, args.yes)
    elif getattr(args, "command", None) == "list-ids":
        app.cli_list_ids()
    elif getattr(args, "command", None) == "list-categories":
        app.cli_list_categories()
    elif getattr(args, "command", None) == "stats":
        app.cli_stats()
    elif getattr(args, "command", None) == "favorites":
        app.cli_favorites()
    elif getattr(args, "command", None) == "tag":
        app.cli_tag(args.tag)
    elif getattr(args, "command", None) == "missing-tools":
        app.cli_missing_tools()
    elif getattr(args, "command", None) == "generate-completion":
        shell = getattr(args, "generate_completion", None) or getattr(args, "shell", None)
        if shell is None:
            parser.error("generate-completion requires a shell argument")
        app.cli_generate_completion(shell)
    elif getattr(args, "command", None) == "session":
        if getattr(args, "session_command", None) == "export":
            from core.session_history import SessionHistory, HISTORY_PATH
            from core.session_replay import export_session
            from core.variables import VariableStore
            from core.loot import LootVault

            out = Path(args.file)
            export_session(out, SessionHistory(persist_path=HISTORY_PATH), VariableStore(), LootVault())
            console.print(f"[bold green]✅ Session exportée:[/bold green] {out}")
        elif getattr(args, "session_command", None) == "replay":
            from core.session_replay import load_session

            data = load_session(Path(args.file))
            hist = data.get("history", [])
            console.print(f"[bold]Replay[/bold] entries={len(hist)} variables={len(data.get('variables', {}))} loot={len(data.get('loot', []))}")
            for item in hist[:30]:
                print(f"{item.get('timestamp','')}\t{item.get('id','')}\t{item.get('exit_code','')}\t{item.get('command','')[:80]}")
        else:
            parser.error("session requires export or replay")
    elif getattr(args, "command", None) == "catalog":
        if getattr(args, "catalog_command", None) == "list-ids":
            app.cli_list_ids()
        elif getattr(args, "catalog_command", None) == "list-categories":
            app.cli_list_categories()
        elif getattr(args, "catalog_command", None) == "stats":
            app.cli_stats()
        elif getattr(args, "catalog_command", None) == "favorites":
            app.cli_favorites()
        elif getattr(args, "catalog_command", None) == "missing-tools":
            app.cli_missing_tools()
        elif getattr(args, "catalog_command", None) == "tag":
            app.cli_tag(args.tag)
        elif getattr(args, "catalog_command", None) == "check":
            app.cli_check()
        elif getattr(args, "catalog_command", None) == "export":
            app.cli_export(args.format)
        elif getattr(args, "catalog_command", None) == "diff":
            app.cli_catalog_diff(args.range_expr)
        elif getattr(args, "catalog_command", None) == "search":
            app.cli_search(
                args.keyword,
                args.category,
                args.tool,
                args.safe,
                args.dangerous,
                args.limit,
                args.regex,
                args.sort_by,
            )
        else:
            parser.error("catalog requires a subcommand")
    elif getattr(args, "command", None) == "admin":
        if getattr(args, "admin_command", None) == "security-status":
            app.cli_security_status()
        elif getattr(args, "admin_command", None) == "usage-metrics":
            app.cli_usage_metrics()
        elif getattr(args, "admin_command", None) == "verify-audit-chain":
            app.cli_verify_audit_chain()
        elif getattr(args, "admin_command", None) == "serve-api":
            app.cli_serve_api()
        elif getattr(args, "admin_command", None) == "apply-profile":
            app.cli_apply_profile(args.profile)
        elif getattr(args, "admin_command", None) == "approve":
            from core.approval_queue import ApprovalQueue
            from core.rbac import can

            if not can(app._role(), "approve"):
                console.print("[bold red]❌ Action non autorisée pour ce rôle.[/bold red]")
                sys.exit(1)
            ok = ApprovalQueue().approve(args.cmd_id)
            console.print("[bold green]✅ Approuvée.[/bold green]" if ok else "[yellow]Aucune entrée en attente.[/yellow]")
        elif getattr(args, "admin_command", None) == "approvals":
            from core.approval_queue import ApprovalQueue

            pending = ApprovalQueue().list_pending()
            if not pending:
                console.print("[dim]Aucune commande en attente.[/dim]")
            else:
                for cmd_id in pending:
                    print(cmd_id)
        elif getattr(args, "admin_command", None) == "refresh-tools":
            _, _, checker = app._get_core()
            checker.refresh()
            console.print("[bold green]✅ Cache outils vidé.[/bold green]")
        elif getattr(args, "admin_command", None) == "export-exec-report":
            app.cli_export_exec_report()
        else:
            parser.error("admin requires a subcommand")
    elif args.run:
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
        app.cli_install(args.install_profile, args.install_dry_run, args.yes)
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
