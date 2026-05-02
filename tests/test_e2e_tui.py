import pytest

pexpect = pytest.importorskip("pexpect")


def test_main_menu_starts_and_quits():
    child = pexpect.spawn("python3 main.py", timeout=20, encoding="utf-8")
    child.expect(["AUTOHACK", "LAB", "Choix"], timeout=20)
    child.sendline("q")
    child.expect(pexpect.EOF, timeout=20)
