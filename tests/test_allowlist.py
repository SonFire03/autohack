from core.command_allowlist import is_allowed


def test_allowlist_allows_known_command():
    assert is_allowed({"category": "system", "command": "python3 --version", "safe_to_run": True}) is True


def test_allowlist_blocks_unknown_category_when_not_safe():
    assert is_allowed({"category": "unknown", "command": "echo ok", "safe_to_run": False}) is False
