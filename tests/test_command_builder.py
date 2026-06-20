from core.command_builder import (
    COMMAND_TEMPLATES,
    available_categories,
    placeholders_for,
    render_template,
    search_templates,
    template_by_key,
    templates_by_category,
)


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


def test_templates_have_unique_commands():
    commands = [template.command for template in COMMAND_TEMPLATES]
    assert len(commands) == len(set(commands))


def test_templates_by_category_are_sorted():
    templates = templates_by_category("web")
    assert templates
    assert all(template.category == "web" for template in templates)
    assert templates == sorted(templates, key=lambda tpl: (tpl.label.casefold(), tpl.key))


def test_search_templates_supports_multi_word_filters():
    results = search_templates("standard version")
    assert [template.key for template in results] == ["nmap-basic"]


def test_available_categories_are_ordered():
    assert available_categories()[:4] == ["recon", "network", "kali", "web"]
    assert "utils" in available_categories()


def test_placeholders_are_detected():
    template = template_by_key("certutil-download")
    assert placeholders_for(template) == ["FILE", "LHOST", "PORT"]
