"""Mutation-inspired security regression tests."""

from unittest.mock import patch

from core.executor import CommandExecutor


def test_dry_run_only_never_executes_run_path():
    ex = CommandExecutor()
    cmd = {"id": "x", "command": "echo ok", "execution_policy": "dry_run_only"}
    with patch("subprocess.run") as mock_run:
        assert ex.confirm_and_run(cmd, skip_confirm=True) is None
        mock_run.assert_not_called()


def test_strict_shell_mode_blocks_pipe_even_if_confirmed():
    ex = CommandExecutor(strict_shell_mode=True)
    cmd = {"id": "x", "command": "echo a | cat", "safe_to_run": True}
    with patch("subprocess.run") as mock_run:
        assert ex.confirm_and_run(cmd, skip_confirm=True) is None
        mock_run.assert_not_called()
