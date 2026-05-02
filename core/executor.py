import re
import shlex
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Confirm
from rich.text import Text
from rich.table import Table

from config.settings import EXPORTS_DIR
from core.logger import ActionLogger, redact_sensitive, write_execution_event

console = Console()

# Lazy import to avoid circular deps — resolved at first use
_VariableStore = None

def _get_variable_store():
    global _VariableStore
    if _VariableStore is None:
        from core.variables import VariableStore
        _VariableStore = VariableStore
    return _VariableStore

# Opérateurs shell nécessitant shell=True
_SHELL_OPERATORS = ("|", "&&", "||", ">>", "> ", "< ", ";", "$(", "`", "$HOME")

# Variables shell natives jamais demandées à l'utilisateur
_SHELL_NATIVE_VARS = {
    "HOME", "PATH", "SHELL", "PWD", "HOSTNAME", "TERM",
    "DISPLAY", "LANG", "LOGNAME", "EUID", "UID", "PPID",
}

# Descriptions affichées lors de la saisie
_PLACEHOLDER_HINTS: Dict[str, str] = {
    "TARGET":       "Adresse IP ou hostname de la cible  (ex: 192.168.1.10)",
    "DOMAIN":       "Nom de domaine  (ex: example.com)",
    "PORT":         "Numéro de port  (ex: 4444)",
    "LOCALPORT":    "Port local sur votre machine  (ex: 8080)",
    "REMOTEPORT":   "Port distant sur la cible  (ex: 3306)",
    "USER":         "Nom d'utilisateur  (ex: admin)",
    "PASS":         "Mot de passe",
    "INTERFACE":    "Interface réseau  (ex: eth0, wlan0)",
    "HASHFILE":     "Chemin vers le fichier de hashs  (ex: hashes.txt)",
    "HASH":         "Valeur du hash à analyser",
    "SHADOWFILE":   "Chemin vers le fichier shadow extrait  (ex: shadow.txt)",
    "CAPFILE":      "Chemin vers le fichier de capture  (ex: capture.cap)",
    "NTLMFILE":     "Chemin vers le fichier de hashs NTLM",
    "BSSID":        "BSSID du point d'accès WiFi  (ex: AA:BB:CC:DD:EE:FF)",
    "ATTACKER":     "Votre adresse IP (attaquant)  (ex: 10.10.14.5)",
    "SERVICE":      "Nom du service  (ex: Apache, vsftpd)",
    "VERSION":      "Version du service  (ex: 2.4.49)",
    "INTERNALHOST": "Hôte interne à atteindre via le tunnel  (ex: 10.0.0.5)",
    "HANDSHAKE":    "Chemin vers le fichier handshake (sans extension)",
}


def _run_args(command_str: str) -> dict:
    """Retourne les kwargs subprocess : shell=True uniquement si nécessaire."""
    if any(op in command_str for op in _SHELL_OPERATORS):
        return {"args": command_str, "shell": True}
    try:
        return {"args": shlex.split(command_str), "shell": False}
    except ValueError:
        return {"args": command_str, "shell": True}


class CommandExecutor:
    """Gère l'exécution, le dry-run, la copie et la capture des commandes shell."""

    def __init__(
        self,
        var_store=None,
        default_timeout: int = 30,
        strict_shell_mode: bool = False,
        redact_secrets: bool = True,
    ) -> None:
        # Valeurs saisies durant la session — réutilisées comme défaut
        self._var_cache: Dict[str, str] = {}
        # Persistent variable store (VariableStore) — checked before prompting
        self._var_store = var_store
        self._default_timeout = max(1, int(default_timeout))
        self._strict_shell_mode = strict_shell_mode
        self._redact_secrets = redact_secrets

    def show_warning(self, cmd: Dict[str, Any]) -> None:
        """Affiche un avertissement pédagogique avant toute exécution."""
        command_str = cmd.get("command", "")
        requires_sudo = cmd.get("requires_sudo", False)
        dangerous = cmd.get("dangerous", False)

        color = "bold red" if dangerous else ("bold yellow" if requires_sudo else "yellow")
        icon = "🚨" if dangerous else ("⚠️ " if requires_sudo else "📋")

        lines = Text()
        lines.append(f"{icon}  Commande à exécuter :\n\n", style="bold white")
        lines.append(f"  {command_str}\n\n", style="bold magenta")
        lines.append("📖 But : ", style="bold cyan")
        lines.append(f"{cmd.get('purpose', '')}\n\n", style="white")
        lines.append("⚡ Risques : ", style="bold")
        lines.append(f"{cmd.get('risks', 'Non spécifié')}\n", style=color)

        if requires_sudo:
            lines.append("\n🔐 Cette commande nécessite des droits sudo.\n", style="bold yellow")
        if dangerous:
            lines.append("\n🚨 COMMANDE DANGEREUSE — double confirmation requise.\n", style="bold red")

        console.print(Panel(lines, title="[bold]Avertissement pédagogique[/bold]",
                            border_style=color, padding=(1, 2)))

    @staticmethod
    def _execution_policy(cmd: Dict[str, Any]) -> str:
        policy = cmd.get("execution_policy")
        if policy:
            return policy
        if cmd.get("dangerous"):
            return "dangerous"
        return "normal"

    def _check_execution_policy(self, cmd: Dict[str, Any], action: str) -> bool:
        policy = self._execution_policy(cmd)
        if policy == "dry_run_only" and action in {"run", "capture"}:
            console.print("[bold red]❌ Cette commande est marquée dry-run only.[/bold red]")
            return False
        if policy == "lab_only" and action in {"run", "capture"}:
            console.print(
                "[bold yellow]🧪 Commande lab-only : confirmez le contexte contrôlé.[/bold yellow]"
            )
            marker = console.input("[bold yellow]Tapez LAB pour continuer > [/bold yellow]").strip()
            if marker != "LAB":
                console.print("[dim]Annulé.[/dim]")
                return False
        if self._strict_shell_mode and action in {"run", "capture"}:
            command = cmd.get("command", "")
            allow_shell = bool(cmd.get("allow_shell_features"))
            if (any(op in command for op in _SHELL_OPERATORS)) and not allow_shell:
                console.print(
                    "[bold red]❌ Mode shell strict: opérateurs shell bloqués "
                    "(ajouter allow_shell_features=true pour cette commande).[/bold red]"
                )
                return False
        return True

    @staticmethod
    def _format_duration(seconds: float) -> str:
        if seconds < 1:
            return f"{seconds:.2f}s"
        if seconds < 60:
            return f"{seconds:.1f}s"
        minutes, rest = divmod(seconds, 60)
        return f"{int(minutes)}m {rest:.1f}s"

    def _render_execution_summary(
        self,
        cmd: Dict[str, Any],
        exit_code: int,
        duration_s: float,
        saved_path: Optional[Path] = None,
        stdout: str = "",
        stderr: str = "",
    ) -> None:
        summary = Table(show_header=False, box=None, padding=(0, 1), expand=False)
        summary.add_column("k", style="grey50", width=10, no_wrap=True)
        summary.add_column("v", style="white", min_width=30)
        summary.add_row("Commande", Text(cmd.get("id", "—"), style="bold bright_cyan"))
        summary.add_row("Statut", Text("succès" if exit_code == 0 else f"échec ({exit_code})",
                                       style="bold bright_green" if exit_code == 0 else "bold bright_red"))
        summary.add_row("Durée", Text(self._format_duration(duration_s), style="bold white"))
        summary.add_row("Shell", Text(cmd.get("command", ""), style="magenta"))
        if saved_path is not None:
            summary.add_row("Capture", Text(str(saved_path), style="bold bright_yellow"))
        timeout_s = cmd.get("_effective_timeout")
        if timeout_s:
            summary.add_row("Timeout", Text(f"{timeout_s}s", style="grey70"))
        if stdout:
            summary.add_row("stdout", Text(f"{len(stdout)} caractères", style="grey70"))
        if stderr:
            summary.add_row("stderr", Text(f"{len(stderr)} caractères", style="grey70"))

        title = " Exécution terminée " if saved_path is None else " Exécution + capture terminée "
        console.print()
        console.print(Panel(
            summary,
            title=title,
            title_align="left",
            border_style="bright_green" if exit_code == 0 else "bright_red",
            padding=(1, 2),
        ))

    def _resolve_placeholders(self, command_str: str) -> Optional[str]:
        """Détecte les $VARIABLES dans la commande et demande les valeurs.

        Retourne la commande avec les valeurs substituées, ou None si l'utilisateur
        annule (Ctrl+C ou réponse vide sur une variable obligatoire).
        """
        found = list(dict.fromkeys(  # préserver l'ordre, dédupliquer
            m for m in re.findall(r'\$([A-Z][A-Z0-9_]*)', command_str)
            if m not in _SHELL_NATIVE_VARS
        ))
        if not found:
            return command_str

        # Pre-populate cache from VariableStore (persistent) then session cache
        store_applied: list[str] = []
        for var in found:
            if var not in self._var_cache and self._var_store is not None:
                stored = self._var_store.get(var)
                if stored:
                    self._var_cache[var] = stored
                    store_applied.append(var)

        # Séparer les variables qui ont déjà une valeur en cache
        needs_input = [v for v in found if v not in self._var_cache]
        will_reuse  = [v for v in found if v in self._var_cache]

        if store_applied:
            console.print(f"[dim]Variables depuis le store : {', '.join(f'${v}={self._var_cache[v]}' for v in store_applied)}[/dim]")

        if needs_input:
            console.print()
            console.print(Panel(
                "[bold cyan]Variables à renseigner :[/bold cyan]",
                border_style="cyan",
                padding=(0, 0),
            ))

        try:
            for var in needs_input:
                cached = self._var_cache.get(var, "")
                hint   = _PLACEHOLDER_HINTS.get(var, "Valeur à saisir")
                prompt = (
                    f"  [bold yellow]${var}[/bold yellow]  [dim]{hint}[/dim]"
                    + (f"  [[dim]{cached}[/dim]]" if cached else "")
                    + "\n  [bold yellow]> [/bold yellow]"
                )
                raw = console.input(prompt).strip()
                val = raw if raw else cached
                if not val:
                    console.print(f"[dim]${var} vide — abandon.[/dim]")
                    return None
                self._var_cache[var] = val
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Annulé.[/dim]")
            return None

        result = command_str
        for var in sorted(found, key=len, reverse=True):
            result = result.replace(f"${var}", self._var_cache[var])

        if will_reuse and not needs_input and not store_applied:
            # Tout venait du cache session : juste une ligne discrète
            console.print(f"[dim]Variables réutilisées : {', '.join(f'${v}={self._var_cache[v]}' for v in found)}[/dim]")
        elif not needs_input:
            console.print()

        return result

    def _effective_timeout(self, cmd: Dict[str, Any]) -> int:
        raw = cmd.get("timeout_seconds", self._default_timeout)
        try:
            return max(1, int(raw))
        except (TypeError, ValueError):
            return self._default_timeout

    def _masked(self, command: str) -> str:
        return redact_sensitive(command, self._redact_secrets)

    def _record_execution(
        self, cmd: Dict[str, Any], exit_code: int, duration_s: float, mode: str, stderr: str = ""
    ) -> None:
        write_execution_event({
            "mode": mode,
            "id": cmd.get("id"),
            "category": cmd.get("category"),
            "tool": cmd.get("tool_required"),
            "exit_code": exit_code,
            "duration_s": round(duration_s, 3),
            "timeout_s": self._effective_timeout(cmd),
            "command": self._masked(cmd.get("command", "")),
            "stderr": (stderr or "")[:500],
        })

    def confirm_and_run(
        self, cmd: Dict[str, Any], capture: bool = False, skip_confirm: bool = False
    ) -> Optional[int]:
        """Affiche l'avertissement, demande confirmation, exécute si accordé.

        skip_confirm=True exécute directement sans confirmation (réservé aux
        commandes safe_to_run=True quand confirm_safe_commands=False dans la config).
        Les commandes dangerous ignorent toujours skip_confirm.
        """
        resolved = self._resolve_placeholders(cmd.get("command", ""))
        if resolved is None:
            return None
        cmd = {**cmd, "command": resolved}
        cmd["_effective_timeout"] = self._effective_timeout(cmd)

        if not self._check_execution_policy(cmd, "run"):
            return None

        self.show_warning(cmd)

        if not skip_confirm or cmd.get("dangerous"):
            if not Confirm.ask("[bold yellow]Exécuter cette commande ?[/bold yellow]", default=False):
                console.print("[dim]Annulé.[/dim]")
                return None

        if cmd.get("dangerous"):
            console.print(
                Panel(
                    "[bold red]ATTENTION : Cette opération est IRRÉVERSIBLE.[/bold red]\n"
                    "Tapez [bold]OUI[/bold] en majuscules pour confirmer.",
                    border_style="bold red",
                )
            )
            confirm2 = console.input("[bold red]Confirmation > [/bold red]").strip()
            if confirm2 != "OUI":
                console.print("[dim]Annulé — bonne décision.[/dim]")
                return None

        if capture:
            stdout, _, code = self._run_capture(cmd)
            return code
        return self._run(cmd)

    def run_and_save(
        self, cmd: Dict[str, Any], export_dir: Optional[Path] = None
    ) -> Tuple[Optional[Path], int]:
        """Exécute la commande, capture la sortie et sauvegarde dans exports/.

        export_dir : dossier de destination (None = EXPORTS_DIR par défaut).
        Retourne (path, exit_code). path vaut None si annulé.
        """
        resolved = self._resolve_placeholders(cmd.get("command", ""))
        if resolved is None:
            return None, -1
        cmd = {**cmd, "command": resolved}
        cmd["_effective_timeout"] = self._effective_timeout(cmd)

        if not self._check_execution_policy(cmd, "capture"):
            return None, -1

        self.show_warning(cmd)

        if not Confirm.ask(
            "[bold yellow]Exécuter et sauvegarder la sortie ?[/bold yellow]", default=False
        ):
            console.print("[dim]Annulé.[/dim]")
            return None, -1

        console.print("\n[bold green]▶ Exécution + capture…[/bold green]\n")
        started = time.perf_counter()
        stdout, stderr, code = self._run_capture(cmd)
        duration_s = time.perf_counter() - started

        dest = Path(export_dir) if export_dir else EXPORTS_DIR
        dest.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        slug = cmd.get("id", "cmd").replace("/", "_")
        path = dest / f"results_{slug}_{ts}.txt"

        content = [
            f"# Résultat : {cmd.get('name', '')}",
            f"# Commande : {self._masked(cmd.get('command', ''))}",
            f"# Date     : {ts}",
            f"# Code     : {code}",
            "",
            "## stdout",
            stdout or "(vide)",
        ]
        if stderr:
            content += ["", "## stderr", stderr]

        path.write_text("\n".join(content), encoding="utf-8")
        ActionLogger.log_run(cmd.get("command", ""), code, redact=self._redact_secrets)
        ActionLogger.log_export(str(path), "txt-capture")
        self._record_execution(cmd, code, duration_s, mode="capture", stderr=stderr)

        self._render_execution_summary(
            cmd,
            code,
            duration_s,
            saved_path=path,
            stdout=stdout,
            stderr=stderr,
        )

        if stdout:
            console.print(Panel(stdout[:2000], title="[dim]stdout (2000 premiers cars)[/dim]",
                                border_style="dim"))
        return path, code

    def dry_run(self, cmd: Dict[str, Any]) -> None:
        """Affiche la commande sans l'exécuter."""
        resolved = self._resolve_placeholders(cmd.get("command", ""))
        if resolved is None:
            return
        command_str = resolved
        syntax = Syntax(command_str, "bash", theme="monokai", word_wrap=True)
        console.print(Panel(
            syntax,
            title="[bold blue]DRY-RUN — commande NON exécutée[/bold blue]",
            border_style="blue",
            padding=(1, 2),
        ))
        ActionLogger.log_run(command_str, 0, dry_run=True, redact=self._redact_secrets)

    def copy_to_clipboard(self, cmd: Dict[str, Any]) -> bool:
        """Copie la commande dans le presse-papiers (avec substitution des variables)."""
        resolved = self._resolve_placeholders(cmd.get("command", ""))
        if resolved is None:
            return False
        command_str = resolved
        try:
            import pyperclip
            pyperclip.copy(command_str)
            console.print("[bold green]✅ Commande copiée dans le presse-papiers ![/bold green]")
            ActionLogger.log_copy(command_str, redact=self._redact_secrets)
            return True
        except Exception:
            console.print(
                "[yellow]⚠️  Copie impossible (pyperclip non disponible ou pas d'affichage X11).[/yellow]\n"
                f"[bold]Commande :[/bold] [magenta]{command_str}[/magenta]"
            )
            return False

    # ── Méthodes internes ────────────────────────────────────────────────────

    def _run(self, cmd: Dict[str, Any]) -> int:
        """Exécute en mode streaming (sortie live, pas capturée)."""
        command_str = cmd.get("command", "")
        console.print(f"\n[bold green]▶ Exécution :[/bold green] [magenta]{command_str}[/magenta]\n")
        started = time.perf_counter()
        timeout_s = self._effective_timeout(cmd)
        try:
            result = subprocess.run(**_run_args(command_str), text=True, timeout=timeout_s)
            code = result.returncode
        except subprocess.TimeoutExpired:
            console.print(
                f"[bold red]❌ Timeout dépassé ({timeout_s}s). Commande interrompue.[/bold red]"
            )
            code = 124
        except Exception as exc:
            console.print(f"[bold red]❌ Erreur : {exc}[/bold red]")
            code = 1
        duration_s = time.perf_counter() - started

        ActionLogger.log_run(command_str, code, redact=self._redact_secrets)
        self._record_execution(cmd, code, duration_s, mode="run")
        self._render_execution_summary(cmd, code, duration_s)
        return code

    def _run_capture(self, cmd: Dict[str, Any]) -> Tuple[str, str, int]:
        """Exécute et capture stdout + stderr."""
        command_str = cmd.get("command", "")
        timeout_s = self._effective_timeout(cmd)
        try:
            result = subprocess.run(
                **_run_args(command_str),
                text=True,
                capture_output=True,
                timeout=timeout_s,
            )
            return result.stdout or "", result.stderr or "", result.returncode
        except subprocess.TimeoutExpired:
            return "", f"Timeout dépassé ({timeout_s}s).", 124
        except Exception as exc:
            return "", str(exc), 1
