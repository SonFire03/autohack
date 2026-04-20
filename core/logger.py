import os
import logging
from config.settings import LOG_FILE


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


class ActionLogger:
    """Journalise les actions de l'utilisateur dans logs/autohack.log."""

    @staticmethod
    def log_run(command: str, exit_code: int, dry_run: bool = False) -> None:
        user = os.environ.get("USER", "unknown")
        mode = "DRY-RUN" if dry_run else "RUN"
        status = "OK" if exit_code == 0 else f"ERROR({exit_code})"
        _logger.info(f"[{mode}] user={user} exit={status} cmd={command!r}")

    @staticmethod
    def log_copy(command: str) -> None:
        user = os.environ.get("USER", "unknown")
        _logger.info(f"[COPY] user={user} cmd={command!r}")

    @staticmethod
    def log_export(path: str, fmt: str) -> None:
        user = os.environ.get("USER", "unknown")
        _logger.info(f"[EXPORT] user={user} format={fmt} path={path!r}")

    @staticmethod
    def log_event(message: str) -> None:
        _logger.info(f"[EVENT] {message}")
