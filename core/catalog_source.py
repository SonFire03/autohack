from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from typing import Any

from core.paths import runtime_catalog_path

CATEGORY_ORDER = [
    "system",
    "network",
    "tor",
    "privoxy",
    "scrapy",
    "json_export",
    "elastic",
    "diagnostic",
    "recon",
    "web_attack",
    "passwords",
    "post_exploit",
    "cloud",
    "forensics",
    "binary",
    "xss",
]


def load_packaged_categories() -> dict[str, dict[str, Any]]:
    package_root = resources.files("catalog")
    categories: dict[str, dict[str, Any]] = {}
    for category in CATEGORY_ORDER:
        resource = package_root.joinpath(f"{category}.json")
        if not resource.is_file():
            raise FileNotFoundError(f"Missing packaged category: {category}.json")
        categories[category] = json.loads(resource.read_text(encoding="utf-8"))
    return categories


def load_catalog_document(path: Path | None = None) -> dict[str, Any]:
    catalog_path = path or runtime_catalog_path()
    if catalog_path.exists():
        with catalog_path.open(encoding="utf-8") as handle:
            return json.load(handle)
    return {
        "version": "1.0.0",
        "categories": load_packaged_categories(),
    }

