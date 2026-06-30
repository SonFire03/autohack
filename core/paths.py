from __future__ import annotations

import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SOURCE_CATALOG = PROJECT_ROOT / "commands_catalog.json"
_SOURCE_CATALOG_DIR = PROJECT_ROOT / "catalog"
_USER_DATA_ROOT = Path.home() / ".autohack"


def project_root() -> Path:
    return PROJECT_ROOT


def running_from_source() -> bool:
    return _SOURCE_CATALOG.exists() and _SOURCE_CATALOG_DIR.exists()


def runtime_root() -> Path:
    if running_from_source():
        return PROJECT_ROOT
    try:
        _USER_DATA_ROOT.mkdir(parents=True, exist_ok=True)
        return _USER_DATA_ROOT
    except OSError:
        fallback = Path(tempfile.gettempdir()) / "autohack"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback
    return _USER_DATA_ROOT


def runtime_logs_dir() -> Path:
    return runtime_root() / "logs"


def runtime_exports_dir() -> Path:
    return runtime_root() / "exports"


def runtime_catalog_path() -> Path:
    return runtime_root() / "commands_catalog.json"
