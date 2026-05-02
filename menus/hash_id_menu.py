"""Hash Identifier — identify hash type and suggest hashcat/john mode."""
import re
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from core.theme import help_footer

console = Console()

# (pattern, name, hashcat_mode, john_format, notes)
HASH_DB: list[tuple[re.Pattern, str, str, str, str]] = [
    (re.compile(r'^[a-f0-9]{32}$', re.I),           "MD5",             "-m 0",    "--format=raw-md5",    "très répandu, non salé"),
    (re.compile(r'^\$1\$[^$]+\$.{22}$'),             "MD5 crypt ($1$)", "-m 500",  "--format=md5crypt",   "Linux /etc/shadow ancien"),
    (re.compile(r'^[a-f0-9]{32}:[a-f0-9]{32}$', re.I), "MD5 + sel",   "-m 20",   "--format=raw-md5",    "MD5(:salt) — web courant"),
    (re.compile(r'^[a-f0-9]{40}$', re.I),            "SHA-1",           "-m 100",  "--format=raw-sha1",   "Git, anciens systèmes"),
    (re.compile(r'^[a-f0-9]{56}$', re.I),            "SHA-224",         "-m 1300", "--format=raw-sha224", ""),
    (re.compile(r'^[a-f0-9]{64}$', re.I),            "SHA-256",         "-m 1400", "--format=raw-sha256", "courant API/tokens"),
    (re.compile(r'^[a-f0-9]{96}$', re.I),            "SHA-384",         "-m 10800","--format=raw-sha384", ""),
    (re.compile(r'^[a-f0-9]{128}$', re.I),           "SHA-512",         "-m 1700", "--format=raw-sha512", "Linux modern, Django"),
    (re.compile(r'^\$6\$[^$]+\$.{86}$'),             "SHA-512 crypt",   "-m 1800", "--format=sha512crypt","Linux /etc/shadow moderne"),
    (re.compile(r'^\$5\$[^$]+\$.{43}$'),             "SHA-256 crypt",   "-m 7400", "--format=sha256crypt","Linux /etc/shadow"),
    (re.compile(r'^[a-f0-9]{32}$', re.I),            "NTLM",            "-m 1000", "--format=NT",         "Windows — même longueur que MD5!"),
    (re.compile(r'^[a-f0-9]{16}$', re.I),            "LM (demi-hash)",  "-m 3000", "--format=lm",         "Windows ancien, toujours coupé"),
    (re.compile(r'^[a-f0-9]{32}:[a-f0-9]{32}$', re.I), "NTLMv1 / LM",  "-m 3000", "--format=lm",         "Windows LAN Manager"),
    (re.compile(r'^\$2[ayb]\$\d{2}\$.{53}$'),        "bcrypt",          "-m 3200", "--format=bcrypt",     "lent — GPU inefficace"),
    (re.compile(r'^\$argon2[id]\$'),                  "Argon2",          "-m 25600","N/A",                 "moderne — très résistant"),
    (re.compile(r'^\$P\$[a-zA-Z0-9./]{31}$'),        "phpBB/WordPress", "-m 400",  "--format=phpass",     "phpass — WordPress, Joomla"),
    (re.compile(r'^\$apr1\$[^$]+\$.{22}$'),          "Apache MD5",      "-m 1600", "--format=md5-apr1",   "Apache htpasswd"),
    (re.compile(r'^[a-f0-9]{32}:[a-z0-9]+$', re.I), "MD5 + alphanum",  "-m 10",   "",                    "format $hash:$salt"),
    (re.compile(r'^\$krb5asrep\$23\$'),              "Kerberos AS-REP", "-m 18200","--format=krb5asrep",  "AS-REP Roasting — craquable"),
    (re.compile(r'^\$krb5tgs\$23\$'),                "Kerberos TGS",    "-m 13100","--format=krb5tgs",    "Kerberoasting — craquable"),
    (re.compile(r'^[a-f0-9]{16}:'),                  "NetNTLMv1",       "-m 5500", "--format=netntlmv1",  "capturé par Responder"),
    (re.compile(r'^[a-zA-Z0-9+/]+=*$'),              "Base64 possible", "N/A",     "N/A",                 "décode d'abord avec base64 -d"),
    (re.compile(r'^\$S\$[a-zA-Z0-9./]{52}$'),        "Drupal SHA-512",  "-m 7900", "--format=drupal7",    "Drupal 7"),
    (re.compile(r'^[a-f0-9]{40}:[a-f0-9]{40}$', re.I), "SHA-1 + sel",  "-m 110",  "",                    "SHA1($pass.$salt)"),
    (re.compile(r'^sha1\$[^$]+\$[a-f0-9]{40}$'),     "Django SHA-1",    "-m 124",  "",                    "Django ancien"),
    (re.compile(r'^pbkdf2_sha256\$'),                 "Django PBKDF2",   "-m 20000","",                    "Django moderne — lent"),
    (re.compile(r'^\$mysql4[01]\$'),                  "MySQL 4.x",       "-m 200",  "--format=mysql",      ""),
    (re.compile(r'^\*[a-f0-9]{40}$', re.I),          "MySQL 5.x",       "-m 300",  "--format=mysql-sha1", "MySQL PASSWORD()"),
    (re.compile(r'^[a-f0-9]{16}$', re.I),            "MySQL 3.x",       "-m 200",  "--format=mysql",      "MySQL ancien"),
    (re.compile(r'^\{SHA\}[a-zA-Z0-9+/=]+$'),        "LDAP SHA",        "-m 101",  "",                    "LDAP {SHA}"),
    (re.compile(r'^[a-zA-Z0-9+/]{27}=$'),            "Base64 MD5",      "-m 0",    "",                    "MD5 en base64 (24 chars)"),
]

NTLMv2_PATTERN = re.compile(
    r'^[a-zA-Z0-9_-]+::[a-zA-Z0-9_-]+:[a-f0-9]{16}:[a-f0-9]{32}:[a-f0-9]+$', re.I
)


def identify(h: str) -> list[tuple[str, str, str, str]]:
    h = h.strip()
    results = []
    if NTLMv2_PATTERN.match(h):
        results.append(("NTLMv2", "-m 5600", "--format=netntlmv2",
                         "capturé par Responder/Inveigh — CRACKE HORS LIGNE"))
    seen = set()
    for pat, name, hc, jn, notes in HASH_DB:
        if pat.match(h) and name not in seen:
            results.append((name, hc, jn, notes))
            seen.add(name)
    return results


class HashIdMenu:
    def show(self) -> None:
        while True:
            console.clear()
            console.print(Panel(
                "[bold magenta]Hash Identifier[/bold magenta]  [dim]— identifie le type et suggère hashcat / john[/dim]",
                border_style="magenta", padding=(0, 1),
            ))
            console.print()
            help_footer([
                ("coller un hash", "identifier le type"),
                ("b / q",          "retour"),
            ], title="Hash Identifier")

            try:
                raw = console.input("\n  [bold magenta]Hash >[/bold magenta] ").strip()
            except (KeyboardInterrupt, EOFError):
                break
            if not raw or raw in {"b", "q"}:
                break

            matches = identify(raw)
            console.print()
            console.print(f"  [dim]Hash:[/dim] [white]{raw[:80]}[/white]")
            console.print(f"  [dim]Longueur:[/dim] {len(raw)} caractères\n")

            if not matches:
                console.print("  [yellow]⚠[/yellow]  Type de hash non reconnu.\n")
            else:
                t = Table(show_header=True, header_style="bold magenta",
                          box=box.SIMPLE_HEAVY, expand=True)
                t.add_column("Type",           style="bold white", min_width=22)
                t.add_column("hashcat",        style="bold yellow", width=12)
                t.add_column("john",           style="bold cyan",   width=22)
                t.add_column("Notes",          style="grey70")
                for name, hc, jn, notes in matches:
                    t.add_row(name, hc, jn, notes)
                console.print(Panel(t, title=" Résultats ", title_align="left",
                                    border_style="dim magenta", padding=(0, 1)))

                if matches:
                    hc = matches[0][1]
                    jn = matches[0][2]
                    console.print()
                    console.print(f"  [dim]Commande hashcat suggérée :[/dim]")
                    console.print(f"  [yellow]hashcat {hc} hash.txt -a 0 /usr/share/wordlists/rockyou.txt -O[/yellow]")
                    if jn and jn != "N/A":
                        console.print(f"  [dim]Commande john suggérée   :[/dim]")
                        console.print(f"  [cyan]john hash.txt {jn} --wordlist=/usr/share/wordlists/rockyou.txt[/cyan]")

            console.input("\n  [dim]Entrée pour continuer…[/dim]")
