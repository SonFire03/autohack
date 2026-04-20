import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "build_catalog.py"


def load_build_script():
    spec = importlib.util.spec_from_file_location("build_catalog", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_split_catalog_rebuilds_current_catalog():
    build_catalog = load_build_script()
    generated = build_catalog.build_catalog(ROOT / "catalog")
    current = json.loads((ROOT / "commands_catalog.json").read_text(encoding="utf-8"))
    assert generated == current


def test_split_catalog_has_expected_category_files():
    build_catalog = load_build_script()
    expected = {f"{category}.json" for category in build_catalog.CATEGORY_ORDER}
    actual = {path.name for path in (ROOT / "catalog").glob("*.json")}
    assert actual == expected
