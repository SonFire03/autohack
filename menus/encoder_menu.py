"""Payload Encoder/Decoder — base64, URL, HTML, hex, unicode, rot13."""
import base64
import urllib.parse
import html
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from core.theme import help_footer

console = Console()

MODES = [
    ("1",  "Base64 encode",       lambda s: base64.b64encode(s.encode()).decode()),
    ("2",  "Base64 decode",       lambda s: base64.b64decode(s + "==").decode(errors="replace")),
    ("3",  "Base64 URL encode",   lambda s: base64.urlsafe_b64encode(s.encode()).decode()),
    ("4",  "Base64 URL decode",   lambda s: base64.urlsafe_b64decode(s + "==").decode(errors="replace")),
    ("5",  "URL encode",          lambda s: urllib.parse.quote(s, safe="")),
    ("6",  "URL decode",          lambda s: urllib.parse.unquote(s)),
    ("7",  "URL encode double",   lambda s: urllib.parse.quote(urllib.parse.quote(s, safe=""), safe="")),
    ("8",  "HTML encode",         lambda s: html.escape(s, quote=True)),
    ("9",  "HTML decode",         lambda s: html.unescape(s)),
    ("10", "Hex encode",          lambda s: s.encode().hex()),
    ("11", "Hex decode",          lambda s: bytes.fromhex(s).decode(errors="replace")),
    ("12", "Hex encode \\xNN",    lambda s: "".join(f"\\x{b:02x}" for b in s.encode())),
    ("13", "Unicode \\uNNNN",     lambda s: s.encode("unicode_escape").decode()),
    ("14", "ROT13",               lambda s: s.translate(str.maketrans(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm"))),
    ("15", "MD5",                 lambda s: __import__("hashlib").md5(s.encode()).hexdigest()),
    ("16", "SHA-1",               lambda s: __import__("hashlib").sha1(s.encode()).hexdigest()),
    ("17", "SHA-256",             lambda s: __import__("hashlib").sha256(s.encode()).hexdigest()),
    ("18", "SHA-512",             lambda s: __import__("hashlib").sha512(s.encode()).hexdigest()),
    ("19", "NTLM hash",           lambda s: __import__("hashlib").new("md4", s.encode("utf-16-le")).hexdigest()),
    ("20", "Reverse string",      lambda s: s[::-1]),
    ("21", "XSS <script>",        lambda s: f"<script>alert('{s}')</script>"),
    ("22", "XSS img onerror",     lambda s: f"<img src=x onerror=alert('{s}')>"),
    ("23", "SQL union probe",     lambda s: f"' OR '{s}'='{s}' -- -"),
    ("24", "Base64 PS (UTF16-LE)",lambda s: base64.b64encode(s.encode("utf-16-le")).decode()),
]


class EncoderMenu:
    def show(self) -> None:
        last_input = ""
        last_output = ""

        while True:
            console.clear()
            console.print(Panel(
                "[bold blue]Payload Encoder / Decoder[/bold blue]  [dim]— transformations utiles pour pentest[/dim]",
                border_style="blue", padding=(0, 1),
            ))
            console.print()

            if last_input:
                console.print(f"  [dim]Dernier input:[/dim]  [white]{last_input[:80]}[/white]")
                console.print(f"  [dim]Dernier output:[/dim] [bold yellow]{last_output[:80]}[/bold yellow]\n")

            t = Table(show_header=True, header_style="bold blue",
                      box=box.SIMPLE_HEAVY, expand=True)
            t.add_column("#",    width=4,  style="bold yellow", justify="right")
            t.add_column("Mode", min_width=22, style="bold white")
            for i in range(0, len(MODES), 2):
                left = MODES[i]
                right = MODES[i+1] if i+1 < len(MODES) else None
                r_key  = right[0] if right else ""
                r_mode = right[1] if right else ""
                t.add_row(left[0], left[1], r_key, r_mode)

            console.print(Panel(t, title=" Modes disponibles ", title_align="left",
                                border_style="dim blue", padding=(0, 1)))
            console.print()
            help_footer([
                ("<n> <texte>", "encoder/décoder — ex: 1 hello world"),
                ("b / q",       "retour"),
            ], title="Encoder")

            try:
                raw = console.input("\n  [bold blue]>[/bold blue] ").strip()
            except (KeyboardInterrupt, EOFError):
                break
            if not raw or raw in {"b", "q"}:
                break

            parts = raw.split(None, 1)
            if len(parts) < 2 or not parts[0].isdigit():
                console.print("  [dim]Usage: <n> <texte>  ex: 1 hello[/dim]")
                console.input("[dim]  Entrée…[/dim]"); continue

            key, text = parts[0], parts[1]
            fn = None
            label = ""
            for k, lbl, func in MODES:
                if k == key:
                    fn = func; label = lbl; break

            if fn is None:
                console.print(f"  [dim]Mode {key} inconnu.[/dim]")
                console.input("[dim]  Entrée…[/dim]"); continue

            try:
                result = fn(text)
                last_input = text
                last_output = result
            except Exception as e:
                console.print(f"  [red]Erreur:[/red] {e}")
                console.input("[dim]  Entrée…[/dim]"); continue

            console.print()
            console.print(f"  [dim]{label}[/dim]")
            console.print(f"  [bold]Input:[/bold]  [white]{text}[/white]")
            console.print(Panel(f"[bold yellow]{result}[/bold yellow]",
                                border_style="blue", padding=(0, 1)))
            action = console.input("  [dim]Entrée=copier  b=retour >[/dim] ").strip().lower()
            if action != "b":
                try:
                    import pyperclip; pyperclip.copy(result)
                    console.print("  [green]✓[/green] Copié.")
                except Exception:
                    console.print("  [dim]pyperclip non disponible.[/dim]")
            console.input("[dim]  Entrée…[/dim]")
