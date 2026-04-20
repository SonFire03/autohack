"""Toolbox installer — install missing pentest tools by profile."""
import shutil
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from core.theme import help_footer, status_bar

console = Console()

# Profile → list of (apt_pkg, pip_pkg|None, check_cmd)
# check_cmd is the binary name to probe with shutil.which()
_PROFILES: dict = {
    "recon": [
        ("nmap",           None,             "nmap"),
        ("masscan",        None,             "masscan"),
        ("dnsutils",       None,             "dig"),
        ("whois",          None,             "whois"),
        ("curl",           None,             "curl"),
        ("wget",           None,             "wget"),
        ("python3-pip",    None,             "pip3"),
        (None,             "shodan",         "shodan"),
        (None,             "httpx-toolkit",  None),
        ("subfinder",      None,             "subfinder"),
        ("amass",          None,             "amass"),
        ("feroxbuster",    None,             "feroxbuster"),
        ("eyewitness",     None,             "eyewitness"),
        (None,             "trufflehog",     "trufflehog"),
    ],
    "web": [
        ("nikto",          None,             "nikto"),
        ("gobuster",       None,             "gobuster"),
        ("dirb",           None,             "dirb"),
        ("sqlmap",         None,             "sqlmap"),
        ("wfuzz",          None,             "wfuzz"),
        ("burpsuite",      None,             None),
        (None,             "xsstrike",       "xsstrike"),
        (None,             "dalfox",         "dalfox"),
        ("whatweb",        None,             "whatweb"),
        ("wafw00f",        None,             "wafw00f"),
    ],
    "passwords": [
        ("hashcat",        None,             "hashcat"),
        ("john",           None,             "john"),
        ("hydra",          None,             "hydra"),
        ("medusa",         None,             "medusa"),
        ("crunch",         None,             "crunch"),
        ("wordlists",      None,             None),
        (None,             "impacket-scripts","secretsdump.py"),
        (None,             "crackmapexec",   "cme"),
        ("evil-winrm",     None,             "evil-winrm"),
        (None,             "certipy-ad",     "certipy"),
    ],
    "ad": [
        (None,             "impacket-scripts","secretsdump.py"),
        (None,             "crackmapexec",   "cme"),
        (None,             "bloodhound-python","bloodhound-python"),
        (None,             "certipy-ad",     "certipy"),
        ("ldap-utils",     None,             "ldapsearch"),
        (None,             "ldapdomaindump", "ldapdomaindump"),
        ("krb5-user",      None,             "kinit"),
        ("smbclient",      None,             "smbclient"),
        (None,             "pypykatz",       "pypykatz"),
    ],
    "post": [
        (None,             "pwncat-cs",      "pwncat-cs"),
        ("netcat",         None,             "nc"),
        ("socat",          None,             "socat"),
        ("chisel",         None,             "chisel"),
        ("proxychains4",   None,             "proxychains4"),
        (None,             "ligolo-ng",      "ligolo-proxy"),
        ("strace",         None,             "strace"),
        ("ltrace",         None,             "ltrace"),
        ("gdb",            None,             "gdb"),
        ("pwndbg",         None,             None),
    ],
}

_PROFILE_LABELS = {
    "recon":     "Reconnaissance & OSINT",
    "web":       "Web Attacks",
    "passwords": "Password Cracking",
    "ad":        "Active Directory",
    "post":      "Post-Exploitation",
}


def _check_tool(check_cmd) -> bool:
    if not check_cmd:
        return False
    return shutil.which(check_cmd) is not None


def _render_profile(name: str) -> None:
    tools = _PROFILES.get(name, [])
    t = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE_HEAVY, expand=True)
    t.add_column("Outil",   style="bold white",   min_width=22)
    t.add_column("Type",    style="grey70",        width=8)
    t.add_column("Statut",  width=12)

    installed = 0
    for apt_pkg, pip_pkg, check_cmd in tools:
        label = apt_pkg or pip_pkg or check_cmd or "?"
        pkg_type = "apt" if apt_pkg else "pip"
        ok = _check_tool(check_cmd)
        if ok:
            installed += 1
        status = Text("✓ installé", style="bold green") if ok else Text("✗ manquant", style="bold red")
        t.add_row(label, pkg_type, status)

    console.print(Panel(
        t,
        title=f" {_PROFILE_LABELS.get(name, name)} — {installed}/{len(tools)} installés ",
        title_align="left",
        border_style="dim cyan" if installed == len(tools) else "dim red",
        padding=(0, 1),
    ))


def _install_profile(name: str) -> None:
    tools = _PROFILES.get(name, [])
    apt_pkgs = [apt for apt, _, check in tools if apt and not _check_tool(check)]
    pip_pkgs = [pip for _, pip, check in tools if pip and not _check_tool(check)]

    if not apt_pkgs and not pip_pkgs:
        console.print("  [bold green]✓ Tous les outils du profil sont déjà installés.[/bold green]")
        return

    console.print(f"\n  [bold yellow]Profil[/bold yellow] : {_PROFILE_LABELS.get(name, name)}")
    if apt_pkgs:
        console.print(f"  [dim]apt install :[/dim] {', '.join(apt_pkgs)}")
    if pip_pkgs:
        console.print(f"  [dim]pip3 install :[/dim] {', '.join(pip_pkgs)}")

    from rich.prompt import Confirm
    if not Confirm.ask("\n  [bold yellow]Lancer l'installation ?[/bold yellow]", default=False):
        console.print("  [dim]Annulé.[/dim]")
        return

    if apt_pkgs:
        console.print("\n  [bold green]▶ apt install…[/bold green]")
        subprocess.run(["sudo", "apt", "install", "-y", *apt_pkgs])

    if pip_pkgs:
        console.print("\n  [bold green]▶ pip3 install…[/bold green]")
        subprocess.run(["pip3", "install", "--break-system-packages", *pip_pkgs])

    console.print("\n  [bold green]✓ Installation terminée.[/bold green]")


class ToolboxMenu:
    """Installateur de profils d'outils pentest."""

    def show(self) -> None:
        while True:
            console.clear()
            console.print(Panel(
                "[bold cyan]Toolbox Installer[/bold cyan]  [dim]— installer les outils par profil[/dim]",
                border_style="cyan", padding=(0, 1),
            ))
            console.print()

            # Summary table
            t = Table(show_header=True, header_style="bold cyan",
                      box=box.SIMPLE_HEAVY, expand=True)
            t.add_column("#",       style="bold yellow", width=4, justify="right")
            t.add_column("Profil",  style="bold white",  min_width=18)
            t.add_column("Outils",  style="grey70",      width=8, justify="right")
            t.add_column("Statut",  width=20)

            profile_keys = list(_PROFILES.keys())
            for idx, key in enumerate(profile_keys, 1):
                tools = _PROFILES[key]
                total = len(tools)
                ok    = sum(1 for _, _, c in tools if _check_tool(c))
                bar   = "█" * ok + "░" * (total - ok)
                t.add_row(str(idx), _PROFILE_LABELS.get(key, key), str(total),
                          f"[green]{bar[:8]}[/green]  {ok}/{total}")

            console.print(Panel(t, title=" Profils disponibles ", title_align="left",
                                border_style="dim blue", padding=(0, 1)))
            console.print()

            help_footer([
                ("<n>",       "afficher le détail du profil n"),
                ("i <n>",     "installer les outils manquants du profil n"),
                ("ia",        "installer TOUS les profils"),
                ("b / q",     "retour"),
            ], title="Toolbox Installer")

            try:
                raw = console.input("\n  [bold cyan]>[/bold cyan] ").strip()
            except (KeyboardInterrupt, EOFError):
                break

            if not raw or raw in {"b", "q"}:
                break

            parts = raw.split()
            cmd = parts[0].lower()

            if cmd == "ia":
                for key in profile_keys:
                    console.print(f"\n  [bold cyan]━ {_PROFILE_LABELS.get(key, key)} ━[/bold cyan]")
                    _install_profile(key)
                console.input("\n[dim]  Entrée…[/dim]")

            elif cmd == "i" and len(parts) >= 2:
                try:
                    idx = int(parts[1]) - 1
                    key = profile_keys[idx]
                except (ValueError, IndexError):
                    console.print("  [dim]Numéro de profil invalide.[/dim]")
                    console.input("[dim]  Entrée…[/dim]")
                    continue
                _install_profile(key)
                console.input("\n[dim]  Entrée…[/dim]")

            elif cmd.isdigit():
                try:
                    idx = int(cmd) - 1
                    key = profile_keys[idx]
                except (ValueError, IndexError):
                    console.print("  [dim]Numéro de profil invalide.[/dim]")
                    console.input("[dim]  Entrée…[/dim]")
                    continue
                console.print()
                _render_profile(key)
                console.input("\n[dim]  Entrée…[/dim]")

            else:
                console.print("  [dim]Commande inconnue. Utilisez un numéro, i <n>, ia, b.[/dim]")
                console.input("[dim]  Entrée…[/dim]")
