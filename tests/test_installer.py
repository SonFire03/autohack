from core.installer import ToolInstaller


def test_basic_profile_contains_apt_packages():
    installer = ToolInstaller(["nmap", "curl", "SharpHound.exe"])
    plan = installer.plan("basic", only_missing=False)
    assert "nmap" in plan.apt_packages
    assert "curl" in plan.apt_packages
    assert "SharpHound.exe" not in plan.manual


def test_all_profile_keeps_manual_tools_separate():
    installer = ToolInstaller(["nxc", "certipy", "SharpHound.exe", "dalfox"])
    plan = installer.plan("all", only_missing=False)
    assert "netexec" in plan.pipx_packages
    assert "certipy-ad" in plan.pipx_packages
    assert "github.com/hahwul/dalfox/v2@latest" in plan.go_packages
    assert "SharpHound.exe" in plan.manual


def test_dry_run_does_not_execute_commands():
    installer = ToolInstaller(["nmap"])
    plan = installer.plan("basic", only_missing=False)
    assert ToolInstaller.run(plan, dry_run=True) == 0


def test_pipx_commands_use_python_module():
    installer = ToolInstaller(["nxc"])
    plan = installer.plan("all", only_missing=False)
    commands = plan.commands()
    assert ["python3", "-m", "pipx", "install", "netexec"] in commands
