from core.approval_queue import ApprovalQueue
from datetime import datetime, timedelta


def test_queue_and_approve(tmp_path):
    q = ApprovalQueue(path=tmp_path / "approvals.json")
    q.queue("sys_001")
    assert "sys_001" in q.list_pending()
    assert q.approve("sys_001") is True
    assert q.is_approved("sys_001") is True


def test_expired_approval_is_removed_from_pending(tmp_path):
    q = ApprovalQueue(path=tmp_path / "approvals.json", ttl_minutes=0)
    q._data["sys_002"] = "approved:" + (datetime.now() - timedelta(minutes=5)).isoformat()
    q._save()
    assert q.list_pending() == []
    assert q.is_approved("sys_002") is False
