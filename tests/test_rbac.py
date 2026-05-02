from core.rbac import can


def test_reader_permissions():
    assert can("reader", "dry_run") is True
    assert can("reader", "run") is False


def test_operator_permissions():
    assert can("operator", "run") is True
    assert can("operator", "install") is False


def test_admin_permissions():
    assert can("admin", "approve") is True
