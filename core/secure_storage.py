from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def apply_secure_permissions(path: Path) -> None:
    if os.name == "nt":
        return
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def read_json_file(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return default


def write_text_atomic(path: Path, content: str, encoding: str = "utf-8") -> None:
    ensure_parent_dir(path)
    with tempfile.NamedTemporaryFile("w", encoding=encoding, dir=path.parent, delete=False) as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
        tmp_path = Path(handle.name)
    apply_secure_permissions(tmp_path)
    os.replace(tmp_path, path)
    apply_secure_permissions(path)


def write_json_atomic(path: Path, data: Any, *, indent: int = 2) -> None:
    payload = json.dumps(data, ensure_ascii=False, indent=indent)
    write_text_atomic(path, payload, encoding="utf-8")

