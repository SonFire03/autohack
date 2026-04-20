import pytest
from core.session_history import SessionHistory

CMD = {"id": "sys_001", "name": "Test", "command": "echo hi", "category": "system"}


@pytest.fixture
def hist():
    return SessionHistory(max_size=5)


@pytest.fixture
def hist_persist(tmp_path):
    return SessionHistory(max_size=5, persist_path=tmp_path / "history.json")


# ── Comportement de base ──────────────────────────────────────────────────────

def test_add_and_len(hist):
    assert len(hist) == 0
    hist.add(CMD, 0)
    assert len(hist) == 1


def test_max_size_respected(hist):
    for i in range(10):
        hist.add(CMD, i)
    assert len(hist) <= 5


def test_last_returns_newest_first(hist):
    for code in range(5):
        hist.add(CMD, code)
    entries = hist.last(3)
    assert entries[0]["exit_code"] == 4
    assert entries[1]["exit_code"] == 3


def test_all_returns_oldest_first(hist):
    for code in range(3):
        hist.add(CMD, code)
    assert hist.all()[0]["exit_code"] == 0
    assert hist.all()[-1]["exit_code"] == 2


def test_clear(hist):
    hist.add(CMD, 0)
    hist.clear()
    assert len(hist) == 0


def test_dry_run_flag(hist):
    hist.add(CMD, 0, dry_run=True)
    assert hist.all()[0]["dry_run"] is True


# ── Persistance ───────────────────────────────────────────────────────────────

def test_persist_writes_file(hist_persist, tmp_path):
    hist_persist.add(CMD, 0)
    path = tmp_path / "history.json"
    assert path.exists()
    content = path.read_text()
    assert "sys_001" in content


def test_persist_loads_on_new_instance(tmp_path):
    path = tmp_path / "history.json"
    h1 = SessionHistory(max_size=10, persist_path=path)
    h1.add(CMD, 42)

    h2 = SessionHistory(max_size=10, persist_path=path)
    assert len(h2) == 1
    assert h2.all()[0]["exit_code"] == 42


def test_persist_clear_removes_file_content(hist_persist, tmp_path):
    hist_persist.add(CMD, 0)
    hist_persist.clear()
    path = tmp_path / "history.json"
    import json
    data = json.loads(path.read_text())
    assert data == []


def test_persist_survives_corrupt_file(tmp_path):
    path = tmp_path / "history.json"
    path.write_text("not valid json")
    h = SessionHistory(max_size=5, persist_path=path)
    assert len(h) == 0  # ne doit pas lever d'exception


def test_no_persist_path_does_not_write(tmp_path):
    h = SessionHistory(max_size=5)  # pas de persist_path
    h.add(CMD, 0)
    # Aucun fichier ne doit avoir été créé dans le répertoire courant
    assert not (tmp_path / "history.json").exists()
