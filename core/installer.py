import shutil
import subprocess
from dataclasses import dataclass


APT_PACKAGES = {
    "curl": "curl",
    "jq": "jq",
    "nmap": "nmap",
    "masscan": "masscan",
    "nc": "netcat-openbsd",
    "netcat": "netcat-openbsd",
    "lsof": "lsof",
    "traceroute": "traceroute",
    "dig": "dnsutils",
    "nslookup": "dnsutils",
    "whois": "whois",
    "netstat": "net-tools",
    "ss": "iproute2",
    "tcpdump": "tcpdump",
    "nikto": "nikto",
    "gobuster": "gobuster",
    "ffuf": "ffuf",
    "dirb": "dirb",
    "whatweb": "whatweb",
    "sqlmap": "sqlmap",
    "hydra": "hydra",
    "john": "john",
    "hashcat": "hashcat",
    "aircrack-ng": "aircrack-ng",
    "tor": "tor",
    "privoxy": "privoxy",
    "proxychains4": "proxychains4",
    "socat": "socat",
    "wget": "wget",
    "python3": "python3",
    "pip": "python3-pip",
    "pip3": "python3-pip",
    "scrapy": "python3-scrapy",
    "responder": "responder",
    "evil-winrm": "evil-winrm",
    "mitm6": "mitm6",
    "cewl": "cewl",
    "chisel": "chisel",
    "crackmapexec": "crackmapexec",
    "crunch": "crunch",
    "dnsenum": "dnsenum",
    "enum4linux": "enum4linux",
    "eyewitness": "eyewitness",
    "feroxbuster": "feroxbuster",
    "hashid": "hashid",
    "kerbrute": "kerbrute",
    "klist": "krb5-user",
    "medusa": "medusa",
    "netdiscover": "netdiscover",
    "redis-cli": "redis-tools",
    "rpcclient": "smbclient",
    "rustscan": "rustscan",
    "searchsploit": "exploitdb",
    "showmount": "nfs-common",
    "smbclient": "smbclient",
    "smbmap": "smbmap",
    "smtp-user-enum": "smtp-user-enum",
    "snmpwalk": "snmp",
    "sslyze": "sslyze",
    "sublist3r": "sublist3r",
    "theHarvester": "theharvester",
    "wafw00f": "wafw00f",
    "wfuzz": "wfuzz",
    "wpscan": "wpscan",
    "yara": "yara",
    "exiftool": "libimage-exiftool-perl",
    "binwalk": "binwalk",
    "foremost": "foremost",
    "bulk_extractor": "bulk-extractor",
    "strings": "binutils",
    "hashdeep": "hashdeep",
    "clamscan": "clamav",
    "file": "file",
    "checksec": "checksec",
    "readelf": "binutils",
    "objdump": "binutils",
    "ltrace": "ltrace",
    "strace": "strace",
    "gdb": "gdb",
    "r2": "radare2",
    "kubectl": "kubectl",
    "aws": "awscli",
}

PIPX_PACKAGES = {
    "impacket": "impacket",
    "nxc": "netexec",
    "netexec": "netexec",
    "certipy": "certipy-ad",
    "coercer": "coercer",
    "arjun": "arjun",
    "commix": "commix",
    "dirsearch": "dirsearch",
    "paramspider": "paramspider",
    "bloodhound-python": "bloodhound",
    "prowler": "prowler",
    "scout": "scoutsuite",
    "pacu": "pacu",
    "newman": "newman",
    "vol": "volatility3",
    "ROPgadget": "ropgadget",
    "one_gadget": "one_gadget",
}

GO_PACKAGES = {
    "subfinder": "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
    "httpx": "github.com/projectdiscovery/httpx/cmd/httpx@latest",
    "katana": "github.com/projectdiscovery/katana/cmd/katana@latest",
    "nuclei": "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest",
    "dalfox": "github.com/hahwul/dalfox/v2@latest",
    "dnsx": "github.com/projectdiscovery/dnsx/cmd/dnsx@latest",
    "naabu": "github.com/projectdiscovery/naabu/v2/cmd/naabu@latest",
    "gau": "github.com/lc/gau/v2/cmd/gau@latest",
    "trivy": "github.com/aquasecurity/trivy/cmd/trivy@latest",
    "syft": "github.com/anchore/syft/cmd/syft@latest",
    "grype": "github.com/anchore/grype/cmd/grype@latest",
}

BASIC_TOOLS = {
    "curl",
    "jq",
    "nmap",
    "nc",
    "lsof",
    "traceroute",
    "dig",
    "whois",
    "netstat",
    "tcpdump",
    "nikto",
    "gobuster",
    "ffuf",
    "whatweb",
    "sqlmap",
    "hydra",
    "john",
    "hashcat",
    "tor",
    "privoxy",
    "proxychains4",
    "socat",
    "wget",
    "python3",
    "pip3",
}

ADVANCED_TOOLS = {
    "masscan",
    "dirb",
    "scrapy",
    "responder",
    "evil-winrm",
    "impacket",
    "nxc",
    "certipy",
    "coercer",
    "mitm6",
    "arjun",
    "commix",
    "subfinder",
    "httpx",
    "katana",
    "nuclei",
    "dalfox",
}

MANUAL_TOOLS = {
    "SharpHound.exe": "Download SharpHound from the official BloodHound collectors release.",
    "Seatbelt.exe": "Build or download Seatbelt from GhostPack in a controlled lab tool folder.",
    "SharpUp.exe": "Build or download SharpUp from GhostPack in a controlled lab tool folder.",
    "PrintSpoofer": "Download PrintSpoofer manually and verify the source/hash before use.",
    "PrintSpoofer.exe": "Download PrintSpoofer manually and verify the source/hash before use.",
    "JuicyPotato": "Download JuicyPotato manually and verify the source/hash before use.",
    "Rubeus": "Build or download Rubeus from GhostPack in a controlled lab tool folder.",
    "GodPotato.exe": "Download GodPotato manually and verify the source/hash before use.",
    "mimikatz": "Download/build Mimikatz manually only for authorized lab use.",
    "mimikatz.exe": "Download/build Mimikatz manually only for authorized lab use.",
    "pspy64": "Download pspy64 manually from the official release and transfer it to the lab target.",
    "./pspy64": "Download pspy64 manually from the official release and transfer it to the lab target.",
    "sliver-server": "Install Sliver from its official release packages.",
    "sliver-client": "Install Sliver from its official release packages.",
    "havoc": "Build Havoc from source in a dedicated lab environment.",
    "tplmap": "Clone tplmap manually and run it from its project directory.",
    "xsstrike": "Clone XSStrike manually and run it from its project directory.",
    "graphql-cop": "Clone GraphQL Cop manually and run it from its project directory.",
    "PetitPotam.py": "Clone PetitPotam manually and run it from its project directory.",
    "amass": "Install OWASP Amass from your distribution, Snap, or official release.",
    "phpggc": "Install PHPGGC manually from its official repository or release package.",
    "procdump": "Install Sysinternals ProcDump manually and verify the source/hash.",
    "reg": "Windows built-in command. No Linux installation needed.",
    "schtasks": "Windows built-in command. No Linux installation needed.",
    "wevtutil": "Windows built-in command. No Linux installation needed.",
    "docker": "Install Docker Engine from the official Docker repository for your distribution.",
    "kube-bench": "Install kube-bench from the official Aqua Security releases.",
    "kube-hunter": "Install kube-hunter manually or in a dedicated Python environment.",
    "gcloud": "Install Google Cloud CLI from the official Google Cloud packages.",
    "az": "Install Azure CLI from the official Microsoft packages.",
    "kr": "Install Kiterunner from the official Assetnote release.",
    "jwt_tool": "Clone jwt_tool manually and run it from its project directory.",
    "corsy": "Clone Corsy manually and run it from its project directory.",
    "loki": "Clone Loki manually and run it from its project directory.",
    "cutter": "Install Cutter from the official release package.",
    "ghidraRun": "Install Ghidra manually from the official release package.",
}


def apt_package_available(package: str) -> bool:
    if shutil.which("apt-cache") is None:
        return True
    result = subprocess.run(
        ["apt-cache", "show", package],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and bool(result.stdout.strip())


@dataclass(frozen=True)
class InstallPlan:
    profile: str
    package_manager: str
    apt_packages: list[str]
    pipx_packages: list[str]
    go_packages: list[str]
    manual: dict[str, str]

    def commands(self) -> list[list[str]]:
        commands = []
        if self.apt_packages:
            if self.package_manager == "apt":
                commands.append(["sudo", "apt-get", "update"])
                commands.append(["sudo", "apt-get", "install", "-y", *self.apt_packages])
            elif self.package_manager == "dnf":
                commands.append(["sudo", "dnf", "install", "-y", *self.apt_packages])
            elif self.package_manager == "pacman":
                commands.append(["sudo", "pacman", "-S", "--noconfirm", *self.apt_packages])
            elif self.package_manager == "brew":
                commands.append(["brew", "install", *self.apt_packages])
        if self.pipx_packages:
            commands.append(["python3", "-m", "pip", "install", "--user", "pipx"])
            commands.append(["python3", "-m", "pipx", "ensurepath"])
            for package in self.pipx_packages:
                commands.append(["python3", "-m", "pipx", "install", package])
        for package in self.go_packages:
            commands.append(["go", "install", package])
        return commands


class ToolInstaller:
    def __init__(self, required_tools: list[str]) -> None:
        self._required_tools = sorted({tool for tool in required_tools if tool})

    @staticmethod
    def _is_present(tool: str) -> bool:
        if tool.startswith("./") or tool.endswith(".exe") or tool.endswith(".py"):
            return False
        return shutil.which(tool) is not None

    def _profile_tools(self, profile: str) -> set[str]:
        if profile == "basic":
            return set(BASIC_TOOLS)
        if profile == "advanced":
            return set(BASIC_TOOLS | ADVANCED_TOOLS)
        if profile == "all":
            return set(self._required_tools)
        raise ValueError(f"Unknown install profile: {profile}")

    def plan(
        self,
        profile: str,
        only_missing: bool = True,
        check_apt_availability: bool = True,
    ) -> InstallPlan:
        selected = self._profile_tools(profile)
        if only_missing:
            selected = {tool for tool in selected if not self._is_present(tool)}

        apt_tools = {tool: APT_PACKAGES[tool] for tool in selected if tool in APT_PACKAGES}
        if check_apt_availability:
            apt_packages = sorted(
                {package for package in apt_tools.values() if apt_package_available(package)}
            )
        else:
            apt_packages = sorted(set(apt_tools.values()))
        pipx_packages = sorted({PIPX_PACKAGES[tool] for tool in selected if tool in PIPX_PACKAGES})
        go_packages = sorted({GO_PACKAGES[tool] for tool in selected if tool in GO_PACKAGES})
        automated = set(APT_PACKAGES) | set(PIPX_PACKAGES) | set(GO_PACKAGES)
        manual = {
            tool: MANUAL_TOOLS.get(tool, "No automatic installer is configured for this tool.")
            for tool in sorted(selected - automated)
        }
        for tool, package in sorted(apt_tools.items()):
            if package not in apt_packages:
                manual[tool] = (
                    f"APT package '{package}' is not available in the configured repositories."
                )
        return InstallPlan(profile, self.detect_package_manager(), apt_packages, pipx_packages, go_packages, manual)

    @staticmethod
    def run(plan: InstallPlan, dry_run: bool = False) -> int:
        for command in plan.commands():
            if dry_run:
                continue
            result = subprocess.run(command)
            if result.returncode != 0:
                return result.returncode
        return 0
    @staticmethod
    def detect_package_manager() -> str:
        if shutil.which("apt-get"):
            return "apt"
        if shutil.which("dnf"):
            return "dnf"
        if shutil.which("pacman"):
            return "pacman"
        if shutil.which("brew"):
            return "brew"
        return "manual"
