"""Curated read-only command packs for common lab workflows."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CommandPack:
    name: str
    title: str
    description: str
    command_ids: tuple[str, ...]


COMMAND_PACKS: dict[str, CommandPack] = {
    "web-recon": CommandPack(
        name="web-recon",
        title="Web Recon",
        description="Reconnaissance web initiale: sous-domaines, HTTP probing, crawling et templates.",
        command_ids=(
            "rec_043",
            "rec_046",
            "rec_044",
            "rec_045",
            "web_059",
            "web_052",
            "web_058",
        ),
    ),
    "ad-lab": CommandPack(
        name="ad-lab",
        title="Active Directory Lab",
        description="Chaîne de lab AD: découverte, Kerberos, ADCS, relay et privesc contrôlée.",
        command_ids=(
            "rec_037",
            "pwd_031",
            "pwd_033",
            "pwd_034",
            "pex_070",
            "pex_071",
            "pex_072",
            "pex_074",
            "pex_069",
        ),
    ),
    "cloud-audit": CommandPack(
        name="cloud-audit",
        title="Cloud Audit",
        description="Audit cloud/Kubernetes: conteneurs, IaC, clusters, buckets et posture AWS.",
        command_ids=(
            "cloud_015",
            "cloud_016",
            "cloud_012",
            "cloud_013",
            "cloud_001",
            "cloud_002",
            "cloud_006",
            "cloud_007",
            "cloud_010",
        ),
    ),
    "forensics": CommandPack(
        name="forensics",
        title="Forensics / DFIR",
        description="Tri DFIR: mémoire, artefacts Windows/Linux, logs, YARA et timeline.",
        command_ids=(
            "dfir_001",
            "dfir_002",
            "dfir_003",
            "dfir_004",
            "dfir_005",
            "dfir_006",
            "dfir_008",
            "dfir_012",
            "dfir_013",
        ),
    ),
    "binary-ctf": CommandPack(
        name="binary-ctf",
        title="Binary / CTF",
        description="Workflow reverse/pwn CTF: metadata ELF, protections, debug et analyse statique.",
        command_ids=(
            "bin_001",
            "bin_002",
            "bin_005",
            "bin_003",
            "bin_004",
            "bin_008",
            "bin_010",
            "bin_011",
            "bin_015",
        ),
    ),
}


def list_pack_names() -> list[str]:
    return sorted(COMMAND_PACKS)


def get_pack(name: str) -> CommandPack | None:
    return COMMAND_PACKS.get(name.strip().lower())
