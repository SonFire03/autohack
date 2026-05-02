import pytest
from core.config_manager import ConfigManager, DEFAULTS


@pytest.fixture
def config(tmp_path, monkeypatch):
    monkeypatch.setattr("core.config_manager.CONFIG_PATH", tmp_path / ".autohack.json")
    return ConfigManager()


def test_defaults_loaded(config):
    for key, val in DEFAULTS.items():
        assert config.get(key) == val


def test_set_and_get(config):
    config.set("page_size", 20)
    assert config.get("page_size") == 20


def test_set_persists_to_disk(config, tmp_path, monkeypatch):
    monkeypatch.setattr("core.config_manager.CONFIG_PATH", tmp_path / ".autohack.json")
    config.set("page_size", 15)
    # Charger une nouvelle instance depuis le même fichier
    config2 = ConfigManager()
    assert config2.get("page_size") == 15


def test_reset_restores_defaults(config):
    config.set("page_size", 99)
    config.reset()
    assert config.get("page_size") == DEFAULTS["page_size"]


def test_set_invalid_key_ignored(config):
    config.set("clé_inconnue", "valeur")
    assert config.get("clé_inconnue") is None


def test_set_export_format_valid(config):
    for fmt in ("markdown", "txt", "json"):
        config.set("export_format", fmt)
        assert config.get("export_format") == fmt


def test_set_export_format_invalid(config):
    with pytest.raises(ValueError, match="non autorisé"):
        config.set("export_format", "pdf")


def test_set_log_level_invalid(config):
    with pytest.raises(ValueError, match="non autorisé"):
        config.set("log_level", "VERBOSE")


def test_all_settings_returns_all_keys(config):
    settings = config.all_settings()
    assert set(settings.keys()) == set(DEFAULTS.keys())


def test_set_page_size_zero_raises(config):
    with pytest.raises(ValueError, match="entier > 0"):
        config.set("page_size", 0)


def test_set_page_size_negative_raises(config):
    with pytest.raises(ValueError, match="entier > 0"):
        config.set("page_size", -5)


def test_set_history_size_zero_raises(config):
    with pytest.raises(ValueError, match="entier > 0"):
        config.set("history_size", 0)


def test_set_page_size_valid(config):
    config.set("page_size", 5)
    assert config.get("page_size") == 5


def test_set_export_dir_none(config):
    config.set("export_dir", None)
    assert config.get("export_dir") is None


def test_set_export_dir_string(config):
    config.set("export_dir", "/tmp/myexports")
    assert config.get("export_dir") == "/tmp/myexports"


def test_set_command_timeout_valid(config):
    config.set("command_timeout", 45)
    assert config.get("command_timeout") == 45


def test_set_command_timeout_zero_raises(config):
    with pytest.raises(ValueError, match="entier > 0"):
        config.set("command_timeout", 0)


def test_set_strict_shell_mode_bool(config):
    config.set("strict_shell_mode", True)
    assert config.get("strict_shell_mode") is True
