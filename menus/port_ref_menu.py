"""Port Reference — port-to-service lookup with pentesting notes."""
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from core.theme import help_footer, status_bar

console = Console()

# (port, proto, service, category, notes)
PORTS: list[tuple[int, str, str, str, str]] = [
    (20,    "TCP", "FTP Data",          "network",   "Transfert fichiers — anonymous FTP souvent vuln"),
    (21,    "TCP", "FTP Control",       "network",   "Brute-force hydra, anonymous, bounce"),
    (22,    "TCP", "SSH",               "network",   "Brute-force, clés faibles, user enum CVE-2018-15473"),
    (23,    "TCP", "Telnet",            "network",   "Texte clair — sniff credentials"),
    (25,    "TCP", "SMTP",              "network",   "Open relay, user enum VRFY/EXPN, phishing"),
    (53,    "TCP/UDP","DNS",            "network",   "Zone transfer (AXFR), DDoS amplif, cache poison"),
    (67,    "UDP", "DHCP Server",       "network",   "Rogue DHCP, starvation"),
    (68,    "UDP", "DHCP Client",       "network",   ""),
    (69,    "UDP", "TFTP",             "network",   "Souvent non authentifié — firmware dump"),
    (79,    "TCP", "Finger",            "network",   "User enumération"),
    (80,    "TCP", "HTTP",              "web",       "Web attacks : SQLi, XSS, LFI, SSRF, RCE"),
    (88,    "TCP", "Kerberos",          "windows",   "AS-REP Roasting, Kerberoasting, Golden Ticket"),
    (110,   "TCP", "POP3",              "network",   "Brute-force, MITM, creds en clair"),
    (111,   "TCP/UDP","RPC",            "network",   "NFS enum, Portmapper"),
    (119,   "TCP", "NNTP",              "network",   ""),
    (123,   "UDP", "NTP",              "network",   "DDoS amplification"),
    (135,   "TCP", "MSRPC",             "windows",   "WMI exec, DCOM lateral movement"),
    (137,   "UDP", "NetBIOS-NS",        "windows",   "Name Service — host enum"),
    (138,   "UDP", "NetBIOS-DGM",       "windows",   ""),
    (139,   "TCP", "NetBIOS-SSN",       "windows",   "SMB sans chiffrement — enum, relay"),
    (143,   "TCP", "IMAP",              "network",   "Brute-force, MITM"),
    (161,   "UDP", "SNMP",              "network",   "Community 'public' — info dump, write config"),
    (162,   "UDP", "SNMP Trap",         "network",   ""),
    (389,   "TCP", "LDAP",              "windows",   "AD enum, password spray, null bind"),
    (443,   "TCP", "HTTPS",             "web",       "Même que HTTP + certificat — HSTS bypass"),
    (445,   "TCP", "SMB",               "windows",   "EternalBlue MS17-010, Pass-the-Hash, relay, psexec"),
    (465,   "TCP", "SMTP/TLS",          "network",   ""),
    (500,   "UDP", "IKE/IPSec",         "network",   "VPN fingerprint, IKE agg mode"),
    (512,   "TCP", "rexec",             "network",   "Remote exec legacy — auth faible"),
    (513,   "TCP", "rlogin",            "network",   "Remote login legacy — auth faible"),
    (514,   "TCP/UDP","RSH/Syslog",     "network",   "Remote shell sans auth"),
    (515,   "TCP", "LPD/LPR",           "network",   "Print spooler"),
    (521,   "UDP", "RIPng",             "network",   "Routing poison"),
    (548,   "TCP", "AFP",               "network",   "Apple Filing Protocol"),
    (554,   "TCP", "RTSP",              "network",   "Caméras IP — souvent admin/admin"),
    (587,   "TCP", "SMTP Submission",   "network",   "Relay sortant"),
    (593,   "TCP", "RPC/HTTP",          "windows",   ""),
    (631,   "TCP", "IPP/CUPS",          "network",   "Printer — RCE potentiel"),
    (636,   "TCP", "LDAPS",             "windows",   "LDAP sur TLS"),
    (873,   "TCP", "rsync",             "network",   "Non authentifié souvent — lecture/écriture FS"),
    (902,   "TCP", "VMware ESXi",       "network",   "Console ESXi"),
    (993,   "TCP", "IMAPS",             "network",   ""),
    (995,   "TCP", "POP3S",             "network",   ""),
    (1080,  "TCP", "SOCKS Proxy",       "network",   "Proxy ouvert"),
    (1090,  "TCP", "Java RMI",          "network",   "Deserialization RCE"),
    (1099,  "TCP", "Java RMI Registry", "network",   "Deserialization RCE — ysoserial"),
    (1433,  "TCP", "MSSQL",             "database",  "SA brute, xp_cmdshell RCE, linked servers"),
    (1521,  "TCP", "Oracle DB",         "database",  "TNS poison, SID bruteforce, SQLi"),
    (1723,  "TCP", "PPTP",              "network",   "VPN legacy — faiblesses MS-CHAPv2"),
    (2049,  "TCP/UDP","NFS",            "network",   "Mount sans auth — lecture FS entier"),
    (2181,  "TCP", "ZooKeeper",         "network",   "Souvent non authentifié — accès config Kafka"),
    (2375,  "TCP", "Docker (non TLS)",  "container", "API Docker exposée — RCE hôte trivial"),
    (2376,  "TCP", "Docker (TLS)",      "container", "Docker avec TLS — vérifier certs"),
    (2379,  "TCP", "etcd",              "container", "etcd K8s — secrets Kubernetes en clair"),
    (3000,  "TCP", "Grafana/NodeJS",    "web",       "Grafana: CVE-2021-43798 LFI, admin/admin"),
    (3268,  "TCP", "Global Catalog",    "windows",   "LDAP Global Catalog AD"),
    (3269,  "TCP", "Global Catalog TLS","windows",   ""),
    (3306,  "TCP", "MySQL",             "database",  "Brute-force, INTO OUTFILE webshell, UDF RCE"),
    (3389,  "TCP", "RDP",               "windows",   "BlueKeep CVE-2019-0708, brute-force, MitM"),
    (4369,  "TCP", "RabbitMQ/Erlang",   "network",   "Cookie Erlang — RCE si connu"),
    (4443,  "TCP", "HTTPS Alt",         "web",       ""),
    (4505,  "TCP", "SaltStack Master",  "network",   "CVE-2020-11651 RCE non authentifié"),
    (4506,  "TCP", "SaltStack Pub",     "network",   "SaltStack"),
    (5000,  "TCP", "Flask/Docker Reg",  "web",       "Registry Docker non sécurisé, Flask debug"),
    (5432,  "TCP", "PostgreSQL",        "database",  "Brute-force, COPY TO/FROM RCE, pg_read_file"),
    (5601,  "TCP", "Kibana",            "elastic",   "Accès ES souvent sans auth — data dump"),
    (5672,  "TCP", "RabbitMQ AMQP",     "network",   "Brute-force, CVE"),
    (5900,  "TCP", "VNC",               "network",   "Brute-force, auth bypass CVE-2006-2369"),
    (5985,  "TCP", "WinRM HTTP",        "windows",   "Evil-WinRM, PS remoting — admin requis"),
    (5986,  "TCP", "WinRM HTTPS",       "windows",   "Evil-WinRM TLS"),
    (6000,  "TCP", "X11",               "network",   "Accès GUI à distance si xhost +"),
    (6379,  "TCP", "Redis",             "database",  "Non authentifié souvent — RCE via SLAVEOF/config"),
    (6443,  "TCP", "K8s API Server",    "container", "Kubernetes API — accès pods/secrets"),
    (7001,  "TCP", "WebLogic",          "web",       "CVE-2020-14882 RCE, deserialization"),
    (7547,  "TCP", "TR-069 (ISP)",      "network",   "Routeurs FAI — Misfortune Cookie CVE"),
    (8080,  "TCP", "HTTP Alt/Tomcat",   "web",       "Tomcat manager /manager/html admin/admin"),
    (8443,  "TCP", "HTTPS Alt",         "web",       ""),
    (8500,  "TCP", "Consul",            "network",   "Consul sans ACL — exécution commandes"),
    (8888,  "TCP", "Jupyter Notebook",  "web",       "Sans token souvent — RCE Python trivial"),
    (9000,  "TCP", "PHP-FPM/Portainer", "web",       "Portainer: admin/portainer — Docker RCE"),
    (9090,  "TCP", "Prometheus",        "network",   "Métriques sans auth — data exfil"),
    (9200,  "TCP", "Elasticsearch",     "elastic",   "REST API sans auth souvent — data dump, RCE script"),
    (9300,  "TCP", "Elasticsearch P2P", "elastic",   ""),
    (10250, "TCP", "Kubelet API",       "container", "Pods exec sans auth — RCE K8s"),
    (11211, "TCP/UDP","Memcached",      "database",  "Non authentifié — données, DDoS amplif"),
    (15672, "TCP", "RabbitMQ Web",      "network",   "Interface web guest/guest"),
    (27017, "TCP", "MongoDB",           "database",  "Non authentifié souvent — data dump complet"),
    (27018, "TCP", "MongoDB Shard",     "database",  ""),
    (32764, "TCP", "Backdoor routeur",  "network",   "Backdoor firmware Linksys/Netgear"),
    (47001, "TCP", "WinRM (MSL)",       "windows",   ""),
    (49152, "TCP", "RPC dynamic",       "windows",   "Ports dynamiques MSRPC"),
]

CATEGORIES = sorted({p[3] for p in PORTS})


class PortRefMenu:
    def show(self) -> None:
        filter_cat = ""
        filter_q   = ""

        while True:
            console.clear()
            console.print(Panel(
                "[bold yellow]Port Reference[/bold yellow]  [dim]— ports courants avec notes de pentest[/dim]",
                border_style="yellow", padding=(0, 1),
            ))
            console.print()

            shown = PORTS
            if filter_cat:
                shown = [p for p in shown if p[3] == filter_cat]
            if filter_q:
                q = filter_q.lower()
                shown = [p for p in shown
                         if q in str(p[0]) or q in p[2].lower()
                         or q in p[4].lower() or q in p[3].lower()]

            status_bar([
                ("Ports totaux",  str(len(PORTS)),   "bold bright_yellow"),
                ("Filtrés",       str(len(shown)),   "grey70"),
                ("Catégorie",     filter_cat or "toutes", "grey70"),
                ("Query",         filter_q   or "—",      "grey70"),
            ])
            console.print()

            t = Table(show_header=True, header_style="bold yellow",
                      box=box.SIMPLE_HEAVY, expand=True)
            t.add_column("Port",     width=7,  style="bold yellow",  justify="right")
            t.add_column("Proto",    width=8,  style="dim")
            t.add_column("Service",  width=20, style="bold white")
            t.add_column("Cat",      width=10, style="bold cyan")
            t.add_column("Notes pentest", style="grey70")

            for port, proto, svc, cat, notes in shown[:60]:
                t.add_row(str(port), proto, svc, cat, notes)

            if len(shown) > 60:
                t.add_row("[dim]…[/dim]", "", f"[dim]+{len(shown)-60} résultats — affinez le filtre[/dim]", "", "")

            console.print(Panel(t, title=" Référence ports ", title_align="left",
                                border_style="dim yellow", padding=(0, 1)))
            console.print()

            cats_display = "  ".join(CATEGORIES)
            console.print(f"  [dim]Catégories: {cats_display}[/dim]\n")

            help_footer([
                ("<port>",        "chercher un port précis"),
                ("f <query>",     "filtrer par service/notes/catégorie"),
                ("c <cat>",       "filtrer par catégorie (web/windows/database/container…)"),
                ("fa",            "tout afficher"),
                ("b / q",         "retour"),
            ], title="Port Reference")

            try:
                raw = console.input("\n  [bold yellow]>[/bold yellow] ").strip()
            except (KeyboardInterrupt, EOFError):
                break
            if not raw or raw in {"b", "q"}:
                break

            parts = raw.split(None, 1)
            cmd = parts[0].lower()

            if cmd == "fa":
                filter_cat = ""; filter_q = ""
            elif cmd == "f" and len(parts) >= 2:
                filter_q = parts[1]; filter_cat = ""
            elif cmd == "c" and len(parts) >= 2:
                filter_cat = parts[1].lower(); filter_q = ""
            elif cmd.isdigit():
                port_num = int(cmd)
                matches = [p for p in PORTS if p[0] == port_num]
                if matches:
                    for port, proto, svc, cat, notes in matches:
                        console.print(f"\n  [bold yellow]{port}/{proto}[/bold yellow]  [bold white]{svc}[/bold white]  [{cat}]")
                        if notes:
                            console.print(f"  [dim]{notes}[/dim]")
                else:
                    console.print(f"  [dim]Port {port_num} non référencé.[/dim]")
                console.input("\n  [dim]Entrée…[/dim]")
            else:
                filter_q = raw; filter_cat = ""
