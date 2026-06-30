from core.cheatsheet_importer import build_external_templates, load_external_cheatsheets, normalize_command
from core.command_builder import COMMAND_TEMPLATES


def test_normalize_command_collapses_whitespace():
    assert normalize_command("  nmap   -sV  $TARGET  ") == "nmap -sV $TARGET"


def test_load_external_cheatsheets_from_missing_dir_returns_empty(tmp_path):
    assert load_external_cheatsheets(tmp_path / "missing") == []


def test_build_external_templates_deduplicates_commands_and_keys():
    records = [
        {
            "key": "extra-web",
            "title": "Extra web audit",
            "category": "web",
            "command": "whatweb http://$TARGET",
            "description": "authorized web audit",
        },
        {
            "key": "extra-web-copy",
            "title": "Duplicate command",
            "category": "web",
            "command": " whatweb   http://$TARGET ",
            "description": "same command",
        },
        {
            "key": "extra-web",
            "title": "Duplicate key",
            "category": "web",
            "command": "nikto -h http://$TARGET",
            "description": "different command",
        },
    ]
    templates, skipped = build_external_templates(
        records,
        existing_commands=(tpl.command for tpl in COMMAND_TEMPLATES),
        existing_keys=(tpl.key for tpl in COMMAND_TEMPLATES),
    )
    assert len(templates) == 1
    assert templates[0]["key"] == "extra-web"
    assert "duplicate-command:extra-web-copy" in skipped
    assert "duplicate-key:extra-web" in skipped


def test_external_file_loader_reads_json_list(tmp_path):
    root = tmp_path / "external_cheatsheets"
    root.mkdir()
    (root / "web.json").write_text(
        """
        [
          {
            "key": "extra-web",
            "title": "Extra web audit",
            "category": "web",
            "command": "whatweb http://$TARGET",
            "description": "authorized web audit"
          }
        ]
        """,
        encoding="utf-8",
    )
    records = load_external_cheatsheets(root)
    assert len(records) == 1


def test_write_external_cheatsheets_roundtrip(tmp_path):
    from core.cheatsheet_importer import write_external_cheatsheets

    output = tmp_path / "out.json"
    write_external_cheatsheets(
        [
            {
                "key": "extra-web",
                "title": "Extra web audit",
                "category": "web",
                "command": "whatweb http://$TARGET",
                "description": "authorized web audit",
                "policy": "safe",
                "policy_reasons": [],
            }
        ],
        output,
    )
    assert output.exists()
    assert output.read_text(encoding="utf-8")
