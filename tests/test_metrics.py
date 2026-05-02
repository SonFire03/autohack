import json

from core.metrics import usage_metrics


def test_usage_metrics_reads_events(tmp_path):
    p = tmp_path / "events.jsonl"
    p.write_text(
        "\n".join([
            json.dumps({"id": "sys_001", "tool": "python3", "exit_code": 0, "duration_s": 0.1, "category": "system"}),
            json.dumps({"id": "sys_001", "tool": "python3", "exit_code": 1, "duration_s": 0.2, "category": "system"}),
        ]) + "\n",
        encoding="utf-8",
    )
    m = usage_metrics(p)
    assert m["total"] == 2
    assert m["top_commands"][0][0] == "sys_001"
