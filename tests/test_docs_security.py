from pathlib import Path


def test_security_md_exists():
    security = Path("SECURITY.md").read_text(encoding="utf-8")
    assert "personal lab environments" in security
    assert "CTFs" in security
    assert "homelabs" in security
    assert "malware" in security
    assert "unauthorized access" in security


def test_readme_mentions_security_and_use_cases():
    readme = Path("README.md").read_text(encoding="utf-8")
    assert "Security Lab Command Organizer" in readme
    assert "Safe by Design" in readme
    assert "Use Cases" in readme
    assert "Risk Levels" in readme
    assert "fastapi" in readme.lower()
    assert "uvicorn" in readme.lower()
    assert "pytest-cov" in readme.lower()
    assert "ruff" in readme.lower()
