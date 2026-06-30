from __future__ import annotations

import hashlib
import hmac
from pathlib import Path

from core.paths import runtime_root

SIG_PATH = runtime_root() / "commands_catalog.sig"


def digest_catalog(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sign_catalog(path: Path, secret: str) -> str:
    payload = path.read_bytes()
    return hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()


def verify_signature(path: Path, sig_path: Path, secret: str) -> bool:
    if not sig_path.exists():
        return False
    actual = sign_catalog(path, secret)
    expected = sig_path.read_text(encoding="utf-8").strip()
    return hmac.compare_digest(actual, expected)
