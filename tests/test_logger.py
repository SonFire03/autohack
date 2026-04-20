import pytest
from core.logger import ActionLogger


@pytest.fixture(autouse=True)
def temp_log(tmp_path, monkeypatch):
    log_file = tmp_path / "test_autohack.log"
    monkeypatch.setattr("core.logger.LOG_FILE", log_file)
    # Réinitialiser le logger pour utiliser le nouveau fichier
    import logging
    import core.logger as logger_module
    logger = logging.getLogger("autohack")
    for h in logger.handlers[:]:
        logger.removeHandler(h)
    logger_module._logger = logger_module._setup_logger()
    yield log_file


def test_log_run_creates_entry(temp_log):
    ActionLogger.log_run("python3 --version", 0)
    content = temp_log.read_text()
    assert "[RUN]" in content
    assert "python3 --version" in content
    assert "OK" in content


def test_log_run_error_code(temp_log):
    ActionLogger.log_run("bad_cmd", 1)
    content = temp_log.read_text()
    assert "ERROR(1)" in content


def test_log_dry_run(temp_log):
    ActionLogger.log_run("ls -la", 0, dry_run=True)
    content = temp_log.read_text()
    assert "[DRY-RUN]" in content


def test_log_copy(temp_log):
    ActionLogger.log_copy("echo test")
    content = temp_log.read_text()
    assert "[COPY]" in content
    assert "echo test" in content


def test_log_export(temp_log):
    ActionLogger.log_export("/tmp/report.md", "markdown")
    content = temp_log.read_text()
    assert "[EXPORT]" in content
    assert "markdown" in content


def test_log_event(temp_log):
    ActionLogger.log_event("Session démarrée")
    content = temp_log.read_text()
    assert "[EVENT]" in content
    assert "Session démarrée" in content


def test_apply_log_level_debug(temp_log):
    import logging
    from core.logger import apply_log_level, _logger
    apply_log_level("DEBUG")
    assert _logger.level == logging.DEBUG
    # Remettre INFO pour ne pas polluer les autres tests
    apply_log_level("INFO")


def test_apply_log_level_warning(temp_log):
    import logging
    from core.logger import apply_log_level, _logger
    apply_log_level("WARNING")
    assert _logger.level == logging.WARNING
    apply_log_level("INFO")
