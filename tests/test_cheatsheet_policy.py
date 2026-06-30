import pytest

from core.cheatsheet_policy import assess_cheatsheet, sanitize_cheatsheet_entry
from core.command_builder import COMMAND_TEMPLATES, policy_counts, policy_for_template, template_by_key


def test_safe_cheatsheet_is_allowed():
    result = assess_cheatsheet("Lab notes", "transparent review", "nmap -sV")
    assert result.allowed is True
    assert result.policy == "safe"


def test_lab_only_cheatsheet_is_flagged():
    result = assess_cheatsheet("Exploit audit", "controlled review", "sqlmap -u $URL")
    assert result.allowed is True
    assert result.policy == "lab_only"


def test_blocked_cheatsheet_is_rejected():
    result = assess_cheatsheet("Malware builder", "stealth persistence", "dropper.exe")
    assert result.allowed is False
    assert result.policy == "blocked"


def test_sanitize_cheatsheet_entry_adds_policy():
    entry = sanitize_cheatsheet_entry(
        {
            "title": "HTTP audit",
            "description": "recon for authorized lab",
            "command": "whatweb http://example",
            "tags": ["web", "lab"],
        }
    )
    assert entry["policy"] == "safe"
    assert entry["policy_reasons"] == []
    assert entry["tags"] == ["web", "lab"]


def test_sanitize_cheatsheet_entry_blocks_malware():
    with pytest.raises(ValueError, match="blocked"):
        sanitize_cheatsheet_entry(
            {
                "title": "Backdoor notes",
                "description": "malware",
                "command": "evil.exe",
            }
        )


def test_builtin_templates_have_no_blocked_policy():
    assert policy_counts()["blocked"] == 0


def test_builtin_template_policies_are_classified():
    template = template_by_key("nmap-basic")
    assert template is not None
    assert policy_for_template(template) in {"safe", "lab_only"}
    assert len(COMMAND_TEMPLATES) > 0
