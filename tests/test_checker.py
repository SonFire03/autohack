import pytest
from unittest.mock import patch
from core.catalog import CommandCatalog
from core.checker import ToolChecker


@pytest.fixture
def checker():
    catalog = CommandCatalog()
    return ToolChecker(catalog)


def test_check_existing_tool(checker):
    # python3 est toujours présent dans l'env de test
    assert checker.check("python3") is True


def test_check_nonexistent_tool(checker):
    assert checker.check("outil_inexistant_xyz123") is False


def test_badge_green_for_existing(checker):
    assert checker.badge("python3") == "✅"


def test_badge_red_for_missing(checker):
    assert checker.badge("outil_inexistant_xyz123") == "❌"


def test_cache_used(checker):
    checker.check("python3")
    with patch("shutil.which") as mock_which:
        checker.check("python3")
        mock_which.assert_not_called()


def test_install_hint_known_tool(checker):
    hint = checker.install_hint("tor")
    assert "apt" in hint or "install" in hint


def test_install_hint_unknown_tool(checker):
    hint = checker.install_hint("unknown_tool_xyz")
    assert "unknown_tool_xyz" in hint


def test_check_all_returns_dict(checker):
    result = checker.check_all()
    assert isinstance(result, dict)
    assert len(result) > 0
    assert all(isinstance(v, bool) for v in result.values())


def test_cache_expires_after_ttl(checker):
    """Après le TTL, shutil.which doit être rappelé."""
    import time
    import core.checker as checker_module

    checker.check("python3")

    # Simuler que le TTL est dépassé
    with patch("time.monotonic", return_value=time.monotonic() + checker_module._CACHE_TTL + 1):
        with patch("shutil.which", return_value="/usr/bin/python3") as mock_which:
            checker.check("python3")
            mock_which.assert_called_once_with("python3")


def test_refresh_clears_cache(checker):
    checker.check("python3")
    assert len(checker._cache) >= 1
    checker.refresh()
    assert len(checker._cache) == 0
