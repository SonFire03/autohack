"""JWT decoder — decode and inspect JWT tokens without external libs."""
import base64
import json
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from core.theme import help_footer, status_bar

console = Console()


def _b64_decode(segment: str) -> str:
    """Decode base64url segment with padding."""
    padded = segment + "=" * (-len(segment) % 4)
    try:
        raw = base64.urlsafe_b64decode(padded)
        return raw.decode("utf-8", errors="replace")
    except Exception:
        return ""


def _decode_jwt(token: str):
    """Return (header_dict, payload_dict, signature_b64, error_str)."""
    token = token.strip()
    parts = token.split(".")
    if len(parts) != 3:
        return None, None, None, f"Attendu 3 parties séparées par '.', trouvé {len(parts)}"
    header_raw  = _b64_decode(parts[0])
    payload_raw = _b64_decode(parts[1])
    sig = parts[2]
    try:
        header  = json.loads(header_raw)
    except Exception:
        return None, None, None, f"Header invalide : {header_raw[:80]}"
    try:
        payload = json.loads(payload_raw)
    except Exception:
        return None, None, None, f"Payload invalide : {payload_raw[:80]}"
    return header, payload, sig, None


def _ts(val) -> str:
    """Format epoch timestamp to human-readable."""
    try:
        dt = datetime.fromtimestamp(int(val))
        now = datetime.now()
        diff = dt - now
        if diff.total_seconds() < 0:
            suffix = f"[bold red]expiré il y a {abs(int(diff.total_seconds()//60))}m[/bold red]"
        else:
            suffix = f"[bold green]expire dans {int(diff.total_seconds()//60)}m[/bold green]"
        return f"{dt.strftime('%Y-%m-%d %H:%M:%S')}  {suffix}"
    except Exception:
        return str(val)


def _render_jwt(token: str) -> None:
    header, payload, sig, err = _decode_jwt(token)
    if err:
        console.print(f"  [bold red]Erreur :[/bold red] {err}")
        return

    # Header table
    ht = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE_HEAVY, expand=True)
    ht.add_column("Clé",    style="bold yellow", width=16)
    ht.add_column("Valeur", style="bold white")
    for k, v in header.items():
        ht.add_row(str(k), str(v))
    console.print(Panel(ht, title=" Header ", title_align="left", border_style="dim cyan", padding=(0,1)))

    # Payload table — highlight known claims
    _CLAIM_HINTS = {
        "sub": "Subject — identifiant de l'utilisateur",
        "iss": "Issuer — émetteur du token",
        "aud": "Audience — destinataire",
        "exp": "Expiration",
        "iat": "Issued At",
        "nbf": "Not Before",
        "jti": "JWT ID — identifiant unique",
    }
    pt = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE_HEAVY, expand=True)
    pt.add_column("Claim",  style="bold yellow", width=16)
    pt.add_column("Valeur", style="bold white", min_width=30)
    pt.add_column("Info",   style="grey70")
    time_claims = {"exp", "iat", "nbf"}
    for k, v in payload.items():
        hint = _CLAIM_HINTS.get(k, "")
        if k in time_claims:
            display = _ts(v)
        elif isinstance(v, (dict, list)):
            display = json.dumps(v, ensure_ascii=False)
        else:
            display = str(v)
        pt.add_row(str(k), display, hint)
    console.print(Panel(pt, title=" Payload ", title_align="left", border_style="dim blue", padding=(0,1)))

    # Signature
    alg = header.get("alg", "?")
    alg_warn = ""
    if alg.lower() == "none":
        alg_warn = "  [bold red]⚠ alg=none — token NON signé — vulnérable ![/bold red]"
    elif alg.lower().startswith("hs"):
        alg_warn = "  [dim]HMAC — secret symétrique[/dim]"
    elif alg.lower().startswith("rs"):
        alg_warn = "  [dim]RSA — clé publique/privée[/dim]"
    console.print(Panel(
        Text.from_markup(f"  [grey70]{sig[:64]}{'…' if len(sig)>64 else ''}[/grey70]{alg_warn}"),
        title=" Signature ", title_align="left", border_style="dim grey50", padding=(0,1),
    ))


class JwtMenu:
    """Décodeur JWT interactif."""

    def show(self) -> None:
        _history: list[str] = []

        while True:
            console.clear()
            console.print(Panel(
                "[bold cyan]JWT Decoder[/bold cyan]  [dim]— décode et inspecte les JSON Web Tokens[/dim]",
                border_style="cyan", padding=(0, 1),
            ))
            console.print()
            status_bar([
                ("Décodés", str(len(_history)), "bold bright_cyan"),
                ("Libs requises", "aucune", "grey70"),
            ])
            console.print()

            if _history:
                console.print("  [dim]Dernier token :[/dim]")
                console.print(f"  [grey50]{_history[-1][:80]}…[/grey50]" if len(_history[-1]) > 80 else f"  [grey50]{_history[-1]}[/grey50]")
                console.print()

            help_footer([
                ("p <token>",  "décoder un JWT"),
                ("last",       "re-décoder le dernier token"),
                ("b / q",      "retour"),
            ], title="JWT Decoder")

            try:
                raw = console.input("\n  [bold cyan]>[/bold cyan] ").strip()
            except (KeyboardInterrupt, EOFError):
                break

            if not raw or raw in {"b", "q"}:
                break

            if raw == "last":
                if _history:
                    console.print()
                    _render_jwt(_history[-1])
                    console.input("\n[dim]  Entrée…[/dim]")
                else:
                    console.print("  [dim]Aucun token décodé cette session.[/dim]")
                    console.input("[dim]  Entrée…[/dim]")
                continue

            parts = raw.split(None, 1)
            if parts[0].lower() == "p" and len(parts) == 2:
                token = parts[1].strip()
                _history.append(token)
                console.print()
                _render_jwt(token)
                console.input("\n[dim]  Entrée…[/dim]")
            elif "." in raw and len(raw) > 20:
                # Bare token pasted directly
                _history.append(raw)
                console.print()
                _render_jwt(raw)
                console.input("\n[dim]  Entrée…[/dim]")
            else:
                console.print("  [dim]Commande inconnue. Utilisez : p <token>[/dim]")
                console.input("[dim]  Entrée…[/dim]")
