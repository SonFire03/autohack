from menus.base import BaseMenu


def test_command_preview_truncates_long_commands():
    preview = BaseMenu._command_preview("a" * 60, max_len=20)
    assert preview == ("a" * 20) + "…"


def test_command_preview_keeps_short_commands():
    assert BaseMenu._command_preview("echo ok", max_len=20) == "echo ok"


def test_safety_label_for_dangerous_command():
    label = BaseMenu._safety_label({"dangerous": True, "safe_to_run": False})
    assert label.plain == "danger"


def test_safety_label_for_safe_command():
    label = BaseMenu._safety_label({"safe_to_run": True})
    assert label.plain == "safe"


def test_safety_label_for_manual_command():
    label = BaseMenu._safety_label({})
    assert label.plain == "manual"


def test_safety_label_for_lab_only_command():
    label = BaseMenu._safety_label({"execution_policy": "lab_only"})
    assert label.plain == "danger"


def test_safety_label_for_dry_run_only_command():
    label = BaseMenu._safety_label({"execution_policy": "dry_run_only"})
    assert label.plain == "dry-run"


def test_clamp_focus_limits_to_range():
    assert BaseMenu._clamp_focus(9, 3) == 2
    assert BaseMenu._clamp_focus(-2, 3) == 0
    assert BaseMenu._clamp_focus(0, 0) == 0
