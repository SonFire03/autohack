from core.session_history import SessionHistory
from core.session_replay import export_session, load_session


def test_export_and_load_session(tmp_path):
    hist = SessionHistory(max_size=5)
    hist.add({"id": "sys_001", "name": "n", "command": "echo ok", "category": "system"}, 0)
    out = tmp_path / "session.json"
    export_session(out, hist)
    data = load_session(out)
    assert "history" in data
    assert len(data["history"]) == 1
