from core.command_builder import COMMAND_TEMPLATES, placeholders_for, render_template, template_by_key


def test_template_lookup_by_key():
    template = template_by_key("nmap-basic")
    assert template is not None
    assert template.label == "Nmap service scan"


def test_render_template_replaces_known_variables():
    template = template_by_key("nmap-basic")
    command, missing = render_template(template, {"TARGET": "10.10.10.10"})
    assert missing == []
    assert "10.10.10.10" in command
    assert "$TARGET" not in command


def test_render_template_reports_missing_variables():
    template = template_by_key("hydra-ssh")
    command, missing = render_template(template, {"TARGET": "10.10.10.10"})
    assert "$USER" in command
    assert missing == ["USER", "WORDLIST"]


def test_templates_have_unique_keys():
    keys = [template.key for template in COMMAND_TEMPLATES]
    assert len(keys) == len(set(keys))


def test_placeholders_are_detected():
    template = template_by_key("certutil-download")
    assert placeholders_for(template) == ["FILE", "LHOST", "PORT"]
