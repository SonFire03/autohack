import os
import logging
import json
import re
import hashlib
from datetime import datetime, timezone
from typing import Any
from config.settings import LOG_FILE, EXECUTION_LOG_FILE


def _setup_logger() -> logging.Logger:
    logger = logging.getLogger("autohack")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))
        logger.addHandler(handler)
    return logger


def apply_log_level(level: str) -> None:
    """Met à jour le niveau de log du logger actif (INFO/DEBUG/WARNING)."""
    numeric = getattr(logging, level.upper(), logging.INFO)
    _logger.setLevel(numeric)
    for handler in _logger.handlers:
        handler.setLevel(numeric)


_logger = _setup_logger()


_SECRET_PATTERNS = [
    (re.compile(r"(?i)(password|passwd|token|apikey|api_key|secret)\s*=\s*([^\s'\";]+)"), r"\1=***"),
    (re.compile(r"(?i)(-p|--password)\s+([^\s'\";]+)"), r"\1 ***"),
    (re.compile(r"\$PASS(?:WORD)?"), "$***"),
]


def redact_sensitive(text: str, enabled: bool = True) -> str:
    if not enabled:
        return text
    masked = text
    for pattern, replacement in _SECRET_PATTERNS:
        masked = pattern.sub(replacement, masked)
    return masked


def write_execution_event(event: dict[str, Any]) -> None:
    payload = dict(event)
    payload["ts"] = datetime.now(timezone.utc).isoformat()
    prev_hash = ""
    if EXECUTION_LOG_FILE.exists():
        try:
            last = EXECUTION_LOG_FILE.read_text(encoding="utf-8").splitlines()[-1]
            prev_hash = json.loads(last).get("event_hash", "")
        except Exception:
            prev_hash = ""
    payload["prev_hash"] = prev_hash
    event_material = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    payload["event_hash"] = hashlib.sha256(event_material.encode("utf-8")).hexdigest()
    with EXECUTION_LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


class ActionLogger:
    """Journalise les actions de l'utilisateur dans logs/autohack.log."""

    @staticmethod
    def log_run(command: str, exit_code: int, dry_run: bool = False, redact: bool = True) -> None:
        user = os.environ.get("USER", "unknown")
        mode = "DRY-RUN" if dry_run else "RUN"
        status = "OK" if exit_code == 0 else f"ERROR({exit_code})"
        _logger.info(f"[{mode}] user={user} exit={status} cmd={redact_sensitive(command, redact)!r}")

    @staticmethod
    def log_copy(command: str, redact: bool = True) -> None:
        user = os.environ.get("USER", "unknown")
        _logger.info(f"[COPY] user={user} cmd={redact_sensitive(command, redact)!r}")

    @staticmethod
    def log_export(path: str, fmt: str) -> None:
        user = os.environ.get("USER", "unknown")
        _logger.info(f"[EXPORT] user={user} format={fmt} path={path!r}")

    @staticmethod
    def log_event(message: str) -> None:
        _logger.info(f"[EVENT] {message}")
