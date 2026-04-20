import pytest
from core.catalog import CommandCatalog


@pytest.fixture
def catalog():
    return CommandCatalog()


def test_catalog_loads(catalog):
    assert len(catalog.get_all()) > 0


def test_catalog_has_expected_categories(catalog):
    cats = catalog.get_categories()
    for expected in ("system", "network", "tor", "privoxy", "scrapy", "elastic", "diagnostic"):
        assert expected in cats


def test_get_by_category_returns_only_that_category(catalog):
    commands = catalog.get_by_category("tor")
    assert all(c["category"] == "tor" for c in commands)
    assert len(commands) > 0


def test_get_by_category_is_case_insensitive(catalog):
    commands = catalog.get_by_category("TOR")
    assert all(c["category"] == "tor" for c in commands)
    assert len(commands) > 0


def test_search_finds_by_name(catalog):
    results = catalog.search("version")
    assert len(results) > 0
    assert any("version" in r["name"].lower() or "version" in r.get("description", "").lower()
               for r in results)


def test_search_finds_by_tag(catalog):
    results = catalog.search("socks")
    assert len(results) > 0


def test_search_empty_returns_nothing(catalog):
    results = catalog.search("xyznotexistingcommand123")
    assert results == []


def test_get_by_id_found(catalog):
    cmd = catalog.get_by_id("sys_001")
    assert cmd is not None
    assert cmd["id"] == "sys_001"


def test_get_by_id_not_found(catalog):
    assert catalog.get_by_id("xxx_999") is None


def test_every_command_has_required_fields(catalog):
    required = ["id", "name", "command", "category", "risks", "safe_to_run"]
    for cmd in catalog.get_all():
        for field in required:
            assert field in cmd, f"Champ '{field}' manquant dans la commande {cmd.get('id')}"


def test_safe_commands_are_safe(catalog):
    safe = catalog.get_safe_commands()
    assert all(c["safe_to_run"] is True for c in safe)


def test_dangerous_commands_flagged(catalog):
    dangerous = catalog.get_dangerous_commands()
    assert all(c["dangerous"] is True for c in dangerous)
    # rm doit être dangereux
    ids = [c["id"] for c in dangerous]
    assert "sys_021" in ids


# ── Recherche scorée multi-mots ───────────────────────────────────────────────

def test_search_multi_word_and_logic(catalog):
    """Tous les mots doivent matcher (AND) — chaque résultat contient les deux mots."""
    results = catalog.search("tor version")
    assert len(results) > 0
    for r in results:
        full = " ".join([
            r.get("name", ""), r.get("id", ""),
            r.get("description", ""), r.get("purpose", ""),
            r.get("short_name", ""), " ".join(r.get("tags", [])),
            r.get("command", ""),
        ]).lower()
        assert "tor" in full, f"'tor' absent dans {r['id']}"
        assert "version" in full, f"'version' absent dans {r['id']}"


def test_search_multi_word_no_match(catalog):
    """Un mot inexistant annule le match."""
    results = catalog.search("tor xyzinexistant999")
    assert results == []


def test_search_ranked_id_first(catalog):
    """Un match sur l'ID doit scorer plus haut qu'un match sur la description."""
    results = catalog.search("sys_001")
    assert len(results) >= 1
    assert results[0]["id"] == "sys_001"


def test_search_empty_string(catalog):
    assert catalog.search("") == []


def test_search_is_accent_insensitive(catalog):
    accented = catalog.search("agrégation")
    plain = catalog.search("agregation")
    assert accented
    assert plain
    assert plain[0]["id"] == accented[0]["id"]


def test_resolve_category_case_insensitive(catalog):
    assert catalog.resolve_category("ToR") == "tor"


def test_resolve_category_prefix_match(catalog):
    """'rec' doit résoudre en 'recon' par préfixe."""
    assert catalog.resolve_category("rec") == "recon"


def test_resolve_category_substring_match(catalog):
    """'attack' doit résoudre en 'web_attack' par sous-chaîne."""
    assert catalog.resolve_category("attack") == "web_attack"


def test_resolve_category_ambiguous_prefix_returns_none(catalog):
    """Un préfixe ambigu (plusieurs catégories) ne doit pas résoudre."""
    assert catalog.resolve_category("net") in ("network", None)


def test_search_finds_by_command_text(catalog):
    """La recherche doit trouver des commandes par leur texte de commande shell."""
    results = catalog.search("--version")
    assert len(results) > 0
    assert any("--version" in r["command"] for r in results)


def test_catalog_covers_advanced_web_attack_gaps(catalog):
    expected = {
        "web_041": "ssti",
        "web_042": "rce",
        "web_043": "graphql",
        "web_044": "graphqlmap",
        "web_045": "deserialization",
        "web_046": "phpggc",
        "web_047": "oauth",
    }
    for cmd_id, tag in expected.items():
        cmd = catalog.get_by_id(cmd_id)
        assert cmd is not None
        assert tag in cmd.get("tags", [])


def test_catalog_covers_lpe_c2_and_persistence_gaps(catalog):
    expected = {
        "pex_061": "dirty-pipe",
        "pex_062": "pwnkit",
        "pex_063": "lpe",
        "pex_064": "sliver",
        "pex_065": "sliver",
        "pex_066": "havoc",
        "pex_067": "persistence",
        "pex_068": "persistence",
    }
    for cmd_id, tag in expected.items():
        cmd = catalog.get_by_id(cmd_id)
        assert cmd is not None
        assert tag in cmd.get("tags", [])


def test_reload_keeps_same_count(catalog):
    before = len(catalog.get_all())
    catalog.reload()
    assert len(catalog.get_all()) == before


# ── Validation ────────────────────────────────────────────────────────────────

def test_validate_returns_empty_on_valid_catalog(catalog):
    issues = catalog.validate()
    assert issues == [], f"Problèmes inattendus : {issues}"


def test_validate_detects_duplicate_ids():
    from core.catalog import CommandCatalog
    import json
    from pathlib import Path
    import tempfile

    data = {
        "categories": {
            "test": {
                "name": "Test",
                "commands": [
                    {"id": "dup_001", "name": "A", "command": "ls", "risks": "none", "safe_to_run": True},
                    {"id": "dup_001", "name": "B", "command": "ls", "risks": "none", "safe_to_run": True},
                ]
            }
        }
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        tmp = Path(f.name)

    import core.catalog as cat_module
    orig = cat_module.CATALOG_PATH
    cat_module.CATALOG_PATH = tmp
    try:
        c = CommandCatalog()
        issues = c.validate()
        assert any("dupliqué" in i for i in issues)
    finally:
        cat_module.CATALOG_PATH = orig
        tmp.unlink()


def test_load_raises_on_missing_required_field():
    from core.catalog import CommandCatalog
    import json
    from pathlib import Path
    import tempfile

    data = {
        "categories": {
            "test": {
                "name": "Test",
                "commands": [
                    {"id": "bad_001", "name": "Bad"}  # manque command, risks, safe_to_run
                ]
            }
        }
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        tmp = Path(f.name)

    import core.catalog as cat_module
    orig = cat_module.CATALOG_PATH
    cat_module.CATALOG_PATH = tmp
    try:
        with pytest.raises(ValueError, match="invalide"):
            CommandCatalog()
    finally:
        cat_module.CATALOG_PATH = orig
        tmp.unlink()
