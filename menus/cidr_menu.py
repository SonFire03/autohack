"""CIDR / IP calculator — subnet math without external libs."""
import ipaddress
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from core.theme import help_footer, status_bar

console = Console()


def _parse_network(expr: str):
    """Parse 'ip/prefix' or plain IP. Returns (network, host_ip|None)."""
    expr = expr.strip()
    try:
        net = ipaddress.ip_network(expr, strict=False)
        host = ipaddress.ip_address(expr.split("/")[0]) if "/" in expr else net.network_address
        return net, host
    except ValueError as e:
        return None, str(e)


def _render_network(expr: str) -> None:
    net, extra = _parse_network(expr)
    if net is None:
        console.print(f"  [bold red]Erreur :[/bold red] {extra}")
        return

    is_v6 = isinstance(net, ipaddress.IPv6Network)
    host_ip = ipaddress.ip_address(expr.split("/")[0]) if "/" in expr else None

    t = Table(show_header=False, box=box.SIMPLE_HEAVY, expand=True, padding=(0,1))
    t.add_column("Champ",   style="bold yellow", width=22)
    t.add_column("Valeur",  style="bold white")

    t.add_row("Réseau",         str(net.network_address))
    t.add_row("Broadcast",      str(net.broadcast_address) if not is_v6 else "N/A (IPv6)")
    t.add_row("Masque",         str(net.netmask)           if not is_v6 else f"/{net.prefixlen}")
    t.add_row("Wildcard",       str(net.hostmask)          if not is_v6 else "—")
    t.add_row("CIDR",           str(net))
    t.add_row("Prefixlen",      f"/{net.prefixlen}")

    if not is_v6:
        num_hosts = net.num_addresses - 2 if net.prefixlen < 31 else net.num_addresses
        t.add_row("Hôtes utilisables", f"{max(0, num_hosts):,}")
        if net.prefixlen <= 24:
            first = next(net.hosts())
            last_host = list(net.hosts())[-1]
            t.add_row("Premier hôte",   str(first))
            t.add_row("Dernier hôte",   str(last_host))
    else:
        t.add_row("Adresses totales",  f"2^{128 - net.prefixlen}")

    if host_ip:
        in_net = host_ip in net
        t.add_row("Hôte spécifié",  f"{host_ip}  [{'bold green' if in_net else 'bold red'}]{'✓ dans le réseau' if in_net else '✗ hors réseau'}[/{'bold green' if in_net else 'bold red'}]")

    scope = _scope(net)
    t.add_row("Portée",          scope)

    console.print(Panel(t, title=f" Réseau : {net} ", title_align="left",
                        border_style="dim cyan", padding=(0,1)))

    # Show example IP range for small subnets
    if not is_v6 and net.prefixlen >= 24 and net.prefixlen <= 30:
        hosts = list(net.hosts())
        if hosts:
            console.print(f"  [dim]Hôtes ({len(hosts)}) : {hosts[0]} … {hosts[-1]}[/dim]")


def _scope(net) -> str:
    if net.is_loopback:
        return "[grey70]loopback[/grey70]"
    if net.is_link_local:
        return "[yellow]link-local[/yellow]"
    if net.is_private:
        return "[green]privé / RFC1918[/green]"
    if net.is_multicast:
        return "[magenta]multicast[/magenta]"
    return "[red]public / routé[/red]"


def _render_contains(net_expr: str, ip_expr: str) -> None:
    net, extra = _parse_network(net_expr)
    if net is None:
        console.print(f"  [bold red]Réseau invalide :[/bold red] {extra}")
        return
    try:
        host = ipaddress.ip_address(ip_expr.strip())
    except ValueError:
        console.print(f"  [bold red]IP invalide :[/bold red] {ip_expr}")
        return
    inside = host in net
    style = "bold green" if inside else "bold red"
    icon  = "✓" if inside else "✗"
    rel   = "est dans" if inside else "n'est PAS dans"
    console.print(f"  [{style}]{icon}[/{style}]  {host}  {rel}  {net}")


def _render_subnets(net_expr: str, new_prefix: int) -> None:
    net, extra = _parse_network(net_expr)
    if net is None:
        console.print(f"  [bold red]Erreur :[/bold red] {extra}")
        return
    if new_prefix <= net.prefixlen:
        console.print(f"  [bold red]Prefixlen /{new_prefix} doit être > /{net.prefixlen}[/bold red]")
        return
    subs = list(net.subnets(new_prefix=new_prefix))
    if len(subs) > 64:
        console.print(f"  [dim]Affichage des 64 premiers sur {len(subs)} sous-réseaux /{new_prefix}[/dim]")
        subs = subs[:64]
    t = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE_HEAVY, expand=False)
    t.add_column("#",       style="grey50",  width=5, justify="right")
    t.add_column("Réseau",  style="bold white")
    t.add_column("Broadcast", style="grey70")
    for i, s in enumerate(subs, 1):
        t.add_row(str(i), str(s), str(s.broadcast_address))
    console.print(Panel(t, title=f" /{new_prefix} subnets de {net} ", title_align="left",
                        border_style="dim blue", padding=(0,1)))


class CidrMenu:
    """Calculatrice IP / CIDR interactive."""

    def show(self) -> None:
        _last = ""

        while True:
            console.clear()
            console.print(Panel(
                "[bold cyan]CIDR Calculator[/bold cyan]  [dim]— calcul de sous-réseaux IP[/dim]",
                border_style="cyan", padding=(0, 1),
            ))
            console.print()
            status_bar([
                ("Libs requises", "aucune (stdlib)", "grey70"),
            ])
            console.print()

            help_footer([
                ("c <ip/prefix>",           "info sur un réseau  ex: c 192.168.1.0/24"),
                ("in <net/pref> <ip>",       "vérifier si IP appartient au réseau"),
                ("sub <net/pref> <newpref>", "découper en sous-réseaux  ex: sub 10.0.0.0/8 16"),
                ("b / q",                    "retour"),
            ], title="CIDR Calculator")

            try:
                raw = console.input("\n  [bold cyan]>[/bold cyan] ").strip()
            except (KeyboardInterrupt, EOFError):
                break

            if not raw or raw in {"b", "q"}:
                break

            parts = raw.split()
            cmd = parts[0].lower()

            if cmd == "c" and len(parts) >= 2:
                _last = parts[1]
                console.print()
                _render_network(parts[1])
                console.input("\n[dim]  Entrée…[/dim]")

            elif cmd == "in" and len(parts) >= 3:
                console.print()
                _render_contains(parts[1], parts[2])
                console.input("\n[dim]  Entrée…[/dim]")

            elif cmd == "sub" and len(parts) >= 3:
                try:
                    new_prefix = int(parts[2])
                except ValueError:
                    console.print("  [bold red]Prefixlen invalide[/bold red]")
                    console.input("[dim]  Entrée…[/dim]")
                    continue
                console.print()
                _render_subnets(parts[1], new_prefix)
                console.input("\n[dim]  Entrée…[/dim]")

            elif "/" in raw or (len(parts) == 1 and _looks_like_ip(raw)):
                # Bare ip/cidr
                _last = raw
                console.print()
                _render_network(raw)
                console.input("\n[dim]  Entrée…[/dim]")

            else:
                console.print("  [dim]Commande inconnue. Utilisez c, in, sub.[/dim]")
                console.input("[dim]  Entrée…[/dim]")


def _looks_like_ip(s: str) -> bool:
    return bool(s.count(".") >= 3 or s.count(":") >= 2)
