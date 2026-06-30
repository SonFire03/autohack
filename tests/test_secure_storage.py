from __future__ import annotations

import os
import stat

from core.catalog import CommandCatalog
from core.secure_storage import read_json_file, write_json_atomic


def test_write_json_atomic_creates_parent_and_restrictive_permissions(tmp_path):
    path = tmp_path / "nested" / "secret.json"
    write_json_atomic(path, {"token": "abc123"})

    assert path.exists()
    assert read_json_file(path, {}) == {"token": "abc123"}

    if os.name != "nt":
        mode = stat.S_IMODE(path.stat().st_mode)
        assert mode == 0o600


def test_catalog_loads_from_packaged_sources_when_generated_file_is_missing(monkeypatch, tmp_path):
    monkeypatch.setattr("core.catalog.CATALOG_PATH", tmp_path / "missing.json")

    catalog = CommandCatalog()

    assert catalog.get_by_id("sys_001") is not None
    assert len(catalog.get_all()) > 0

