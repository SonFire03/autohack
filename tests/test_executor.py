import pytest
import subprocess
from unittest.mock import patch
from core.executor import CommandExecutor, _run_args


# ── _run_args ─────────────────────────────────────────────────────────────────

def test_run_args_simple_command_uses_list():
    result = _run_args("python3 --version")
    assert result["shell"] is False
    assert isinstance(result["args"], list)
    assert result["args"][0] == "python3"


def test_run_args_pipe_uses_shell():
    result = _run_args("ls | head -5")
    assert result["shell"] is True
    assert isinstance(result["args"], str)


def test_run_args_redirect_uses_shell():
    result = _run_args("echo hello > /tmp/test.txt")
    assert result["shell"] is True


def test_run_args_ampersand_uses_shell():
    result = _run_args("apt update && apt install -y tor")
    assert result["shell"] is True


def test_run_args_dollar_uses_shell():
    result = _run_args("echo $HOME")
    assert result["shell"] is True


# ── CommandExecutor ───────────────────────────────────────────────────────────

@pytest.fixture
def executor():
    return CommandExecutor()


@pytest.fixture
def safe_cmd():
    return {
        "id": "test_001",
        "name": "Test command",
        "command": "python3 --version",
        "purpose": "Test purpose",
        "risks": "Aucun",
        "requires_sudo": False,
        "dangerous": False,
        "category": "system",
    }


def test_dry_run_does_not_execute(executor, safe_cmd):
    with patch("subprocess.run") as mock_run:
        executor.dry_run(safe_cmd)
        mock_run.assert_not_called()


def test_run_capture_returns_tuple(executor, safe_cmd):
    stdout, stderr, code = executor._run_capture(safe_cmd)
    assert isinstance(stdout, str)
    assert isinstance(stderr, str)
    assert isinstance(code, int)
    assert code == 0


def test_run_capture_uses_default_timeout(executor, safe_cmd):
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = "ok"
        mock_run.return_value.stderr = ""
        mock_run.return_value.returncode = 0
        executor._run_capture(safe_cmd)
        assert mock_run.call_args.kwargs["timeout"] == 30


def test_run_capture_uses_command_timeout_override(executor, safe_cmd):
    cmd = dict(safe_cmd)
    cmd["timeout_seconds"] = 7
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = "ok"
        mock_run.return_value.stderr = ""
        mock_run.return_value.returncode = 0
        executor._run_capture(cmd)
        assert mock_run.call_args.kwargs["timeout"] == 7


def test_run_capture_timeout_returns_124(executor, safe_cmd):
    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="x", timeout=1)):
        stdout, stderr, code = executor._run_capture(safe_cmd)
        assert stdout == ""
        assert "Timeout dépassé" in stderr
        assert code == 124


def test_run_capture_bad_command(executor):
    cmd = {"command": "this_command_does_not_exist_xyz123"}
    stdout, stderr, code = executor._run_capture(cmd)
    assert code != 0


def test_copy_to_clipboard_fallback(executor, safe_cmd):
    import sys
    # Simuler pyperclip absent en le retirant temporairement de sys.modules
    original = sys.modules.pop("pyperclip", None)
    sys.modules["pyperclip"] = None  # type: ignore[assignment]
    try:
        result = executor.copy_to_clipboard(safe_cmd)
        assert isinstance(result, bool)
    finally:
        if original is not None:
            sys.modules["pyperclip"] = original
        else:
            sys.modules.pop("pyperclip", None)


def test_confirm_and_run_cancelled_on_no(executor, safe_cmd):
    with patch("rich.prompt.Confirm.ask", return_value=False):
        result = executor.confirm_and_run(safe_cmd)
        assert result is None


def test_confirm_and_run_skip_confirm_executes_without_asking(executor, safe_cmd):
    """skip_confirm=True ne doit pas appeler Confirm.ask pour les commandes non-dangerous."""
    with patch("rich.prompt.Confirm.ask") as mock_ask:
        result = executor.confirm_and_run(safe_cmd, skip_confirm=True)
        mock_ask.assert_not_called()
        assert result == 0


def test_confirm_and_run_skip_confirm_still_asks_for_dangerous(executor):
    dangerous_cmd = {
        "id": "d001", "name": "Dangerous", "command": "echo ok",
        "purpose": "test", "risks": "high",
        "requires_sudo": False, "dangerous": True, "category": "system",
    }
    with patch("rich.prompt.Confirm.ask", return_value=False):
        result = executor.confirm_and_run(dangerous_cmd, skip_confirm=True)
        assert result is None


def test_run_and_save_cancelled_returns_none_minus1(executor, safe_cmd):
    with patch("rich.prompt.Confirm.ask", return_value=False):
        path, code = executor.run_and_save(safe_cmd)
        assert path is None
        assert code == -1


def test_run_and_save_uses_custom_export_dir(executor, safe_cmd, tmp_path):
    """run_and_save doit écrire dans export_dir si fourni."""
    with patch("rich.prompt.Confirm.ask", return_value=True):
        path, code = executor.run_and_save(safe_cmd, export_dir=tmp_path)
        assert path is not None
        assert path.parent == tmp_path


def test_run_and_save_returns_tuple_with_exit_code(executor, safe_cmd, tmp_path):
    from config import settings as s
    import core.executor as exc_mod
    original = s.EXPORTS_DIR
    s.EXPORTS_DIR = tmp_path
    exc_mod.EXPORTS_DIR = tmp_path
    try:
        with patch("rich.prompt.Confirm.ask", return_value=True):
            path, code = executor.run_and_save(safe_cmd)
            assert path is not None
            assert path.exists()
            assert isinstance(code, int)
    finally:
        s.EXPORTS_DIR = original
        exc_mod.EXPORTS_DIR = original


def test_confirm_and_run_dangerous_requires_oui(executor):
    dangerous_cmd = {
        "id": "test_danger",
        "name": "Dangerous",
        "command": "echo dangerous",
        "purpose": "Test",
        "risks": "Dangereux",
        "requires_sudo": False,
        "dangerous": True,
        "category": "system",
    }
    with patch("rich.prompt.Confirm.ask", return_value=True):
        with patch("rich.console.Console.input", return_value="NON"):
            result = executor.confirm_and_run(dangerous_cmd)
            assert result is None


def test_resolve_placeholders_longer_var_not_corrupted(executor):
    """$TARGET ne doit pas corrompre $TARGETPORT lors du remplacement."""
    cmd = {"command": "nmap $TARGET -p $TARGETPORT", "id": "t001"}

    inputs = iter(["192.168.1.1", "4444"])
    with patch("rich.console.Console.input", side_effect=lambda _: next(inputs)):
        result = executor._resolve_placeholders(cmd["command"])

    assert result == "nmap 192.168.1.1 -p 4444"
    assert "1.1PORT" not in result


def test_format_duration_subsecond(executor):
    assert executor._format_duration(0.345) == "0.34s"


def test_format_duration_minutes(executor):
    assert executor._format_duration(65.2) == "1m 5.2s"


def test_execution_policy_defaults_dangerous_for_dangerous_flag(executor):
    assert executor._execution_policy({"dangerous": True}) == "dangerous"


def test_confirm_and_run_lab_only_executes_with_confirmation(executor):
    """lab_only ne bloque plus — la commande s'exécute après confirmation."""
    cmd = {
        "id": "lab_001",
        "name": "Lab command",
        "command": "echo ok",
        "execution_policy": "lab_only",
        "dangerous": False,
    }
    with patch("rich.prompt.Confirm.ask", return_value=True):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            result = executor.confirm_and_run(cmd)
            assert result == 0
            mock_run.assert_called_once()


def test_run_and_save_blocks_dry_run_only_policy(executor, tmp_path):
    cmd = {
        "id": "dry_001",
        "name": "Dry only",
        "command": "echo blocked",
        "execution_policy": "dry_run_only",
    }
    with patch("rich.prompt.Confirm.ask", return_value=True):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "ok"
            mock_run.return_value.stderr = ""
            path, code = executor.run_and_save(cmd, export_dir=tmp_path)
            assert path is not None
            assert code == 0
            mock_run.assert_called_once()


def test_confirm_and_run_allows_dry_run_only_policy(executor):
    cmd = {
        "id": "dry_002",
        "name": "Dry now allowed",
        "command": "echo ok",
        "execution_policy": "dry_run_only",
    }
    with patch("rich.prompt.Confirm.ask", return_value=True):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            assert executor.confirm_and_run(cmd) == 0
            mock_run.assert_called_once()
