from __future__ import annotations

import pytest

from core.catalog import CommandCatalog


SENSITIVE_PATTERNS = (
    "reverse shell",
    "reverse-shell",
    "payload",
    "privesc",
    "relay",
    "coercion",
    "credential",
    "ntlm",
    "kerberos",
    "mimikatz",
    "secretsdump",
    "responder",
    "ntlmrelayx",
    "msfvenom",
    "persistence",
    "c2",
    "tunneling",
    "post-exploit",
    "dcsync",
    "kerberoast",
    "getuserspns",
    "pass-the-hash",
    "pass-the-ticket",
    "hashdump",
    "lsass",
    "wmiexec",
    "evil-winrm",
    "printspoofer",
    "juicypotato",
    "godpotato",
    "dirty pipe",
    "pwnkit",
    "docker socket",
    "lxd",
    "ld_preload",
    "bloodhound",
    "lagazne",
    "lazagne",
    "hashcat -m 1000",
    "hashcat -m 13100",
    "hashcat -m 18200",
)

PAYLOAD_OR_CREDENTIAL_PATTERNS = (
    "msfvenom",
    "payload",
    "ysoserial",
    "phpggc",
    "reverse shell",
    "secretsdump",
    "mimikatz",
    "ntlmrelayx",
    "responder",
    "coercion",
    "relay",
    "dcsync",
    "hashdump",
    "lsass",
    "kerberoast",
    "getuserspns",
    "pass-the-hash",
    "pass-the-ticket",
    "pth",
    "credential",
    "ntlm",
)


@pytest.fixture
def catalog() -> CommandCatalog:
    return CommandCatalog()


def _blob(cmd: dict[str, object]) -> str:
    return " ".join(
        str(cmd.get(field, ""))
        for field in ("id", "name", "short_name", "command")
    ).lower() + " " + " ".join(str(tag).lower() for tag in cmd.get("tags", []))


def test_safe_commands_do_not_match_sensitive_patterns(catalog: CommandCatalog) -> None:
    for cmd in catalog.get_all():
        if not cmd.get("safe_to_run"):
            continue
        if cmd.get("id") == "tor_015":
            continue
        blob = _blob(cmd)
        assert not any(pattern in blob for pattern in SENSITIVE_PATTERNS), cmd.get("id")


def test_dangerous_or_lab_only_commands_are_never_safe(catalog: CommandCatalog) -> None:
    for cmd in catalog.get_all():
        if cmd.get("dangerous") or cmd.get("execution_policy") in {"lab_only", "dry_run_only"}:
            assert not cmd.get("safe_to_run"), cmd.get("id")


def test_payload_and_credential_commands_are_unsafe_and_policy_gated(catalog: CommandCatalog) -> None:
    for cmd in catalog.get_all():
        if cmd.get("id") == "tor_015":
            continue
        blob = _blob(cmd)
        if not any(pattern in blob for pattern in PAYLOAD_OR_CREDENTIAL_PATTERNS):
            continue
        assert not cmd.get("safe_to_run"), cmd.get("id")
        assert cmd.get("execution_policy") in {"lab_only", "dry_run_only"}, cmd.get("id")
        assert cmd.get("dangerous") is True, cmd.get("id")


def test_sensitive_diagnostics_remain_read_only_but_not_safe(catalog: CommandCatalog) -> None:
    expected = {"pex_020", "pex_023", "pex_061", "pex_063"}
    for cmd_id in expected:
        cmd = catalog.get_by_id(cmd_id)
        assert cmd is not None
        assert not cmd.get("safe_to_run")
        assert cmd.get("execution_policy") == "lab_only"
        assert cmd.get("dangerous") is False
