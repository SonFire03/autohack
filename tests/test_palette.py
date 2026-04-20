from core.palette import parse_palette_command


def test_parse_palette_search_alias():
    assert parse_palette_command(":find") == ("search", "")


def test_parse_palette_command_id():
    assert parse_palette_command(":sys_001") == ("command", "sys_001")


def test_parse_palette_empty_shows_palette():
    assert parse_palette_command(":") == ("palette", "")


def test_parse_palette_ignores_non_palette_input():
    assert parse_palette_command("sys_001") is None
