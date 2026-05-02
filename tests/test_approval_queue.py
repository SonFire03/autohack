from core.approval_queue import ApprovalQueue


def test_queue_and_approve(tmp_path):
    q = ApprovalQueue(path=tmp_path / "approvals.json")
    q.queue("sys_001")
    assert "sys_001" in q.list_pending()
    assert q.approve("sys_001") is True
    assert q.is_approved("sys_001") is True
