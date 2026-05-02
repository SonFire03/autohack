from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EnvProfile:
    name: str
    config_overrides: dict[str, Any]
    variables: dict[str, str]


PROFILES: dict[str, EnvProfile] = {
    "lab1": EnvProfile(
        name="lab1",
        config_overrides={"strict_shell_mode": True, "require_secondary_approval": True},
        variables={"SCOPE": "10.10.10.0/24", "NOTES": "Lab network 1"},
    ),
    "lab2": EnvProfile(
        name="lab2",
        config_overrides={"strict_shell_mode": True, "require_secondary_approval": False},
        variables={"SCOPE": "172.16.56.0/24", "NOTES": "Lab network 2"},
    ),
    "ctf": EnvProfile(
        name="ctf",
        config_overrides={"strict_shell_mode": False, "require_secondary_approval": False},
        variables={"SCOPE": "ctf", "NOTES": "CTF sandbox"},
    ),
    "client": EnvProfile(
        name="client",
        config_overrides={"strict_shell_mode": True, "require_secondary_approval": True, "user_role": "operator"},
        variables={"SCOPE": "authorized-client", "NOTES": "Client engagement"},
    ),
}


def list_profiles() -> list[str]:
    return sorted(PROFILES.keys())


def get_profile(name: str) -> EnvProfile | None:
    return PROFILES.get(name.strip().lower())
