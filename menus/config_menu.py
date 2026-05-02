from rich.console import Console
from rich.table import Table
from rich import box
from menus.base import BaseMenu
from core.config_manager import ConfigManager, DEFAULTS

console = Console()

SETTING_LABELS = {
    "export_format":         ("Format d'export par défaut",  "markdown | txt | json"),
    "page_size":             ("Commandes par page",           "entier > 0"),
    "confirm_safe_commands": ("Confirmer commandes safe",     "true | false"),
    "show_history_in_menu":  ("Afficher historique en menu",  "true | false"),
    "history_size":          ("Taille historique de session", "entier > 0"),
    "command_timeout":       ("Timeout commande (s)",         "entier > 0"),
    "strict_shell_mode":     ("Mode shell strict",            "true | false"),
    "redact_secrets_in_logs":("Masquer secrets logs",         "true | false"),
    "user_role":             ("Rôle utilisateur",             "reader | operator | admin"),
    "lang":                  ("Langue interface",             "fr | en"),
    "enforce_catalog_signature": ("Vérifier signature catalogue", "true | false"),
    "require_secondary_approval": ("Approval secondaire",      "true | false"),
    "tool_cache_ttl_seconds":("TTL cache outils (s)",         "entier > 0"),
    "log_level":             ("Niveau de log",                "INFO | DEBUG | WARNING"),
    "export_dir":            ("Dossier d'export",             "chemin absolu ou vide (=défaut)"),
}


class ConfigMenuScreen(BaseMenu):
    TITLE = "Configuration utilisateur"

    def __init__(self, catalog, executor, checker, config: ConfigManager, **kwargs) -> None:
        super().__init__(catalog, executor, checker, config=config, **kwargs)

    def show(self) -> None:
        while True:
            self._header("⚙️  Configuration utilisateur")
            self._show_current()
            console.print(
                f"\n  [bold yellow]1-{len(SETTING_LABELS)}[/bold yellow] modifier un paramètre  "
                "[bold yellow]r[/bold yellow] réinitialiser  "
                "[bold yellow]b[/bold yellow] retour\n"
            )
            choice = console.input("[bold yellow]Choix > [/bold yellow]").strip().lower()

            if choice == "b":
                break
            elif choice == "r":
                self._config.reset()
                console.print("[bold green]✅ Configuration réinitialisée.[/bold green]")
                console.input("[dim]Entrée pour continuer…[/dim]")
            elif choice.isdigit() and 1 <= int(choice) <= len(SETTING_LABELS):
                key = list(SETTING_LABELS.keys())[int(choice) - 1]
                self._edit(key)
            else:
                console.print("[dim]Choix invalide.[/dim]")

    def _show_current(self) -> None:
        table = Table(
            show_header=True, header_style="bold cyan",
            box=box.ROUNDED, expand=False,
        )
        table.add_column("#", style="bold yellow", width=3)
        table.add_column("Paramètre", style="bold white", min_width=28)
        table.add_column("Valeur actuelle", style="magenta", min_width=16)
        table.add_column("Valeurs acceptées", style="dim", min_width=20)

        for i, (key, (label, accepted)) in enumerate(SETTING_LABELS.items(), 1):
            val = str(self._config.get(key))
            default = str(DEFAULTS[key])
            marker = "" if val == default else " [dim]*[/dim]"
            table.add_row(str(i), label + marker, val, accepted)

        console.print()
        console.print(table)
        console.print("  [dim]* = valeur modifiée (défaut souligné dans DEFAULTS)[/dim]")

    def _edit(self, key: str) -> None:
        label, accepted = SETTING_LABELS[key]
        current = self._config.get(key)
        new_raw = console.input(
            f"\n  [bold]{label}[/bold] (actuel: [magenta]{current}[/magenta], "
            f"accepté: [dim]{accepted}[/dim])\n  Nouvelle valeur > "
        ).strip()

        if not new_raw:
            console.print("[dim]Inchangé.[/dim]")
            return

        # Conversion de type selon le défaut
        default_val = DEFAULTS[key]
        try:
            if isinstance(default_val, bool):
                new_val = new_raw.lower() in ("true", "1", "yes", "oui")
            elif isinstance(default_val, int):
                new_val = int(new_raw)
                if new_val <= 0:
                    raise ValueError("doit être > 0")
            elif key == "export_dir":
                # Vide = revenir au dossier par défaut
                new_val = new_raw.strip() or None
            else:
                new_val = new_raw
            self._config.set(key, new_val)
            display = str(new_val) if new_val is not None else "(défaut)"
            console.print(f"[bold green]✅ {label} = {display}[/bold green]")
        except ValueError as exc:
            console.print(f"[bold red]❌ Valeur invalide : {exc}[/bold red]")

        console.input("[dim]Entrée pour continuer…[/dim]")
