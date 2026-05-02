import json
import pytest
from core.catalog import CommandCatalog
from core.exporter import Exporter


@pytest.fixture
def exporter():
    catalog = CommandCatalog()
    return Exporter(catalog.get_all())


def test_export_txt_creates_file(exporter, tmp_path, monkeypatch):
    monkeypatch.setattr("core.exporter.EXPORTS_DIR", tmp_path)
    path = exporter.export_txt()
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "AUTOHACK" in content
    assert "sys_001" in content


def test_export_markdown_creates_file(exporter, tmp_path, monkeypatch):
    monkeypatch.setattr("core.exporter.EXPORTS_DIR", tmp_path)
    path = exporter.export_markdown()
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "# AUTOHACK LAB COMMANDER" in content
    assert "```bash" in content


def test_export_json_creates_valid_json(exporter, tmp_path, monkeypatch):
    monkeypatch.setattr("core.exporter.EXPORTS_DIR", tmp_path)
    path = exporter.export_json()
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]
    assert "command" in data[0]


def test_export_html_creates_searchable_document(exporter, tmp_path, monkeypatch):
    monkeypatch.setattr("core.exporter.EXPORTS_DIR", tmp_path)
    path = exporter.export_html()
    assert path.suffix == ".html"
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content
    assert "AUTOHACK LAB COMMANDER" in content
    assert "sys_001" in content


def test_export_markdown_contains_all_categories(exporter, tmp_path, monkeypatch):
    monkeypatch.setattr("core.exporter.EXPORTS_DIR", tmp_path)
    path = exporter.export_markdown()
    content = path.read_text(encoding="utf-8")
    for cat_label in ["Système", "Réseau", "Tor", "Privoxy", "Scrapy", "JSON", "Elastic", "Diagnostic"]:
        assert cat_label in content, f"Catégorie manquante : {cat_label}"


def test_export_txt_contains_commands(exporter, tmp_path, monkeypatch):
    monkeypatch.setattr("core.exporter.EXPORTS_DIR", tmp_path)
    path = exporter.export_txt()
    content = path.read_text(encoding="utf-8")
    assert "python3 --version" in content
    assert "tor --version" in content


def test_generate_full_report_is_markdown(exporter, tmp_path, monkeypatch):
    monkeypatch.setattr("core.exporter.EXPORTS_DIR", tmp_path)
    path = exporter.generate_full_report()
    assert path.suffix == ".md"
    assert path.exists()


def test_export_execution_html_creates_file(exporter, tmp_path, monkeypatch):
    log_path = tmp_path / "executions.jsonl"
    log_path.write_text('{"ts":"2026-01-01T00:00:00Z","mode":"run","id":"sys_001","tool":"python3","exit_code":0,"duration_s":0.2,"command":"python3 --version"}\n', encoding="utf-8")
    monkeypatch.setattr("core.exporter.EXECUTION_LOG_FILE", log_path)
    path = exporter.export_execution_html()
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "Execution Report" in content
    assert "sys_001" in content
