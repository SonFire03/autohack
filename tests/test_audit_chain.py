import json

from core.audit_chain import verify


def test_verify_empty_ok(tmp_path):
    ok, line = verify(tmp_path / "missing.jsonl")
    assert ok is True
    assert line == 0


def test_verify_chain_valid(tmp_path):
    p = tmp_path / "events.jsonl"
    row1 = {"ts": "1", "prev_hash": "", "event_hash": ""}
    material1 = json.dumps({"ts": "1", "prev_hash": ""}, ensure_ascii=False, sort_keys=True)
    import hashlib
    row1["event_hash"] = hashlib.sha256(material1.encode()).hexdigest()

    row2 = {"ts": "2", "prev_hash": row1["event_hash"], "event_hash": ""}
    material2 = json.dumps({"ts": "2", "prev_hash": row1["event_hash"]}, ensure_ascii=False, sort_keys=True)
    row2["event_hash"] = hashlib.sha256(material2.encode()).hexdigest()

    p.write_text(json.dumps(row1) + "\n" + json.dumps(row2) + "\n", encoding="utf-8")
    ok, _ = verify(p)
    assert ok is True
