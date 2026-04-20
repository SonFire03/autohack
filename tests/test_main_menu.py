from menus.main_menu import MainMenu, _ITEMS


class DummyChecker:
    def __init__(self, installed):
        self._installed = set(installed)

    def check(self, tool):
        return tool in self._installed


class DummyCatalog:
    def __init__(self, commands):
        self._commands = commands

    def get_all(self):
        return list(self._commands)


def make_menu(commands, installed_tools=()):
    menu = MainMenu.__new__(MainMenu)
    menu._catalog = DummyCatalog(commands)
    menu._checker = DummyChecker(installed_tools)
    return menu


def test_matches_quick_view_safe():
    assert MainMenu._matches_quick_view("safe", {"execution_policy": "safe"}) is True
    assert MainMenu._matches_quick_view("safe", {"safe_to_run": True}) is True
    assert MainMenu._matches_quick_view("safe", {}) is False


def test_matches_quick_view_by_tag():
    assert MainMenu._matches_quick_view("docker", {"tags": ["docker"]}) is True
    assert MainMenu._matches_quick_view("hardware", {"tags": ["hardware"]}) is True
    assert MainMenu._matches_quick_view("logs", {"tags": ["logs"]}) is True
    assert MainMenu._matches_quick_view("lab", {"execution_policy": "lab_only"}) is True


def test_quick_view_ready_keeps_only_available_tools():
    commands = [
        {"id": "sys_001", "tool_required": ""},
        {"id": "sys_002", "tool_required": "docker"},
        {"id": "sys_003", "tool_required": "hashcat"},
    ]
    menu = make_menu(commands, installed_tools={"docker"})
    ready_ids = [cmd["id"] for cmd in menu._quick_view_commands("ready")]
    assert ready_ids == ["sys_001", "sys_002"]


def test_quick_view_docker_collects_tool_and_tag_matches():
    commands = [
        {"id": "sys_029", "tool_required": "docker", "tags": []},
        {"id": "sys_031", "tool_required": "", "tags": ["hardware"]},
        {"id": "diag_018", "tool_required": "", "tags": ["docker"]},
    ]
    menu = make_menu(commands)
    docker_ids = [cmd["id"] for cmd in menu._quick_view_commands("docker")]
    assert docker_ids == ["sys_029", "diag_018"]


def test_main_menu_exposes_new_catalog_sections():
    keys = {item[0] for item in _ITEMS}
    assert {"21", "22", "23"} <= keys
    labels = {item[2] for item in _ITEMS}
    assert "Cloud / K8s" in labels
    assert "Forensics / DFIR" in labels
    assert "Binary / Reverse" in labels
