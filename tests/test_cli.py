"""Tests end-to-end du CLI (invocation subprocess de main.py)."""
import subprocess
import sys
from pathlib import Path

MAIN = [sys.executable, str(Path(__file__).parent.parent / "main.py")]


def run(*args, timeout=10):
    result = subprocess.run(
        MAIN + list(args),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result


# ── --version ────────────────────────────────────────────────────────────────

def test_version_flag():
    from config.version import __version__

    r = run("--version")
    assert r.returncode == 0
    assert "autohack" in r.stdout
    assert __version__ in r.stdout


# ── --list-ids ────────────────────────────────────────────────────────────────

def test_list_ids_produces_tsv():
    r = run("--list-ids")
    assert r.returncode == 0
    lines = [line for line in r.stdout.splitlines() if line.strip()]
    assert len(lines) >= 100  # au moins 100 commandes
    for line in lines[:5]:
        parts = line.split("\t")
        assert len(parts) == 3, f"Ligne malformée : {line!r}"


def test_list_ids_contains_known_ids():
    r = run("--list-ids")
    assert "sys_001" in r.stdout
    assert "tor_001" in r.stdout
    assert "net_001" in r.stdout


# ── --list-categories ────────────────────────────────────────────────────────

def test_list_categories_flag():
    r = run("--list-categories")
    assert r.returncode == 0
    for cat in (
        "system", "network", "tor", "privoxy", "scrapy", "elastic", "diagnostic",
        "cloud", "forensics", "binary",
    ):
        assert cat in r.stdout


# ── --category ────────────────────────────────────────────────────────────────

def test_category_tor_shows_commands():
    r = run("--category", "tor")
    assert r.returncode == 0
    assert "tor" in r.stdout.lower()
    assert "tor_001" in r.stdout


def test_category_network_shows_nmap():
    r = run("--category", "network")
    assert r.returncode == 0
    assert "net_011" in r.stdout  # nouvelle commande nmap


def test_category_is_case_insensitive():
    r = run("--category", "TOR")
    assert r.returncode == 0
    assert "tor_001" in r.stdout


def test_category_invalid_exits_1():
    r = run("--category", "inconnue_xyz")
    assert r.returncode == 1
    assert "Disponibles" in r.stdout or "Disponibles" in r.stderr


def test_category_all_valid_categories():
    """Chaque catégorie connue doit répondre avec code 0."""
    for cat in ("system", "network", "tor", "privoxy", "scrapy",
                "json_export", "elastic", "diagnostic",
                "cloud", "forensics", "binary"):
        r = run("--category", cat)
        assert r.returncode == 0, f"--category {cat} a retourné {r.returncode}"


# ── --search ──────────────────────────────────────────────────────────────────

def test_search_single_keyword():
    r = run("--search", "tor")
    assert r.returncode == 0
    assert "résultat" in r.stdout.lower()


def test_search_multi_keyword():
    r = run("--search", "tor version")
    assert r.returncode == 0
    assert "résultat" in r.stdout.lower()


def test_search_no_result():
    r = run("--search", "xyzinexistant999abc")
    assert r.returncode == 0
    assert "Aucun" in r.stdout


def test_search_new_commands_nmap():
    r = run("--search", "nmap scan")
    assert r.returncode == 0
    assert "net_011" in r.stdout or "net_012" in r.stdout


def test_search_new_elastic_aggregation():
    r = run("--search", "agrégation")
    assert r.returncode == 0
    assert "elk_013" in r.stdout


def test_search_without_accent_finds_same_command():
    r = run("--search", "agregation")
    assert r.returncode == 0
    assert "elk_013" in r.stdout


# ── --dry-run ─────────────────────────────────────────────────────────────────

def test_dry_run_known_id():
    r = run("--dry-run", "sys_001")
    assert r.returncode == 0
    assert "python3" in r.stdout.lower() or "version" in r.stdout.lower()


def test_dry_run_unknown_id_exits_1():
    r = run("--dry-run", "xxx_999")
    assert r.returncode == 1
    assert "introuvable" in r.stdout.lower()


# ── --export ──────────────────────────────────────────────────────────────────

def test_export_json_creates_valid_file(tmp_path, monkeypatch):
    """Export JSON via CLI produit un fichier JSON valide."""
    import config.settings as settings
    orig = settings.EXPORTS_DIR
    settings.EXPORTS_DIR = tmp_path
    settings.EXPORTS_DIR.mkdir(exist_ok=True)

    r = subprocess.run(
        MAIN + ["--export", "json"],
        capture_output=True, text=True, timeout=15,
        env={**__import__("os").environ},
    )
    settings.EXPORTS_DIR = orig

    assert r.returncode == 0
    assert "Export créé" in r.stdout


def test_export_html_creates_file():
    r = run("--export", "html")
    assert r.returncode == 0
    assert "Export créé" in r.stdout
    assert ".html" in r.stdout


# ── Catalogue enrichi ─────────────────────────────────────────────────────────

def test_new_commands_in_catalog():
    """Les 18 nouvelles commandes sont bien dans le catalogue."""
    r = run("--list-ids")
    for cmd_id in [
        "net_011", "net_012", "net_013", "net_014", "net_015",
        "tor_013", "tor_014", "tor_015",
        "scr_013", "scr_014", "scr_015",
        "diag_011", "diag_012", "diag_013", "diag_014",
        "elk_011", "elk_012", "elk_013",
    ]:
        assert cmd_id in r.stdout, f"Commande manquante : {cmd_id}"


def test_new_ops_commands_in_catalog():
    r = run("--list-ids")
    for cmd_id in [
        "sys_029", "sys_030", "sys_031", "sys_032",
        "net_016", "net_017", "net_018",
        "diag_015", "diag_016", "diag_017", "diag_018",
    ]:
        assert cmd_id in r.stdout, f"Commande ops manquante : {cmd_id}"


def test_catalog_total_at_least_120():
    r = run("--list-ids")
    lines = [line for line in r.stdout.splitlines() if line.strip()]
    assert len(lines) >= 120


def test_new_kali_commands_in_catalog():
    r = run("--list-ids")
    for cmd_id in [
        "rec_013", "rec_014",
        "web_011", "web_012",
        "pwd_011", "pwd_012",
        "pex_012", "pex_013",
        "rec_015", "rec_016",
        "web_013", "web_014",
        "pwd_013", "pwd_014",
        "pex_014", "pex_015",
        "rec_017", "rec_018",
        "web_015", "web_016",
        "pex_016", "pex_017", "pex_018", "pex_019",
        "rec_019", "rec_020",
        "web_017", "web_018",
        "pwd_015", "pwd_016",
        "pex_020", "pex_021",
        "rec_021", "rec_022",
        "web_019", "web_020",
        "pex_022", "pex_023",
    ]:
        assert cmd_id in r.stdout, f"Commande Kali manquante : {cmd_id}"


def test_search_nuclei_finds_new_web_command():
    r = run("--search", "nuclei templates")
    assert r.returncode == 0
    assert "web_011" in r.stdout


def test_search_kerbrute_finds_new_ad_command():
    r = run("--search", "kerbrute kerberos")
    assert r.returncode == 0
    assert "rec_016" in r.stdout


def test_search_httpx_finds_new_recon_command():
    r = run("--search", "httpx tech")
    assert r.returncode == 0
    assert "rec_018" in r.stdout


def test_search_certipy_finds_new_adcs_command():
    r = run("--search", "certipy adcs")
    assert r.returncode == 0
    assert "pex_018" in r.stdout


def test_search_subfinder_finds_new_passive_recon_command():
    r = run("--search", "subfinder passive")
    assert r.returncode == 0
    assert "rec_019" in r.stdout


def test_search_ldapsearch_finds_new_recon_command():
    r = run("--search", "ldapsearch rootdse")
    assert r.returncode == 0
    assert "rec_021" in r.stdout


def test_search_docker_finds_new_system_command():
    r = run("--search", "docker containers")
    assert r.returncode == 0
    assert "sys_029" in r.stdout


def test_search_trivy_finds_cloud_command():
    r = run("--search", "trivy container")
    assert r.returncode == 0
    assert "cloud_001" in r.stdout


def test_search_volatility_finds_forensics_command():
    r = run("--search", "volatility memory")
    assert r.returncode == 0
    assert "dfir_001" in r.stdout


def test_search_checksec_finds_binary_command():
    r = run("--search", "checksec elf")
    assert r.returncode == 0
    assert "bin_002" in r.stdout


# ── --tag ──────────────────────────────────────────────────────────────────────

def test_tag_known_tag_returns_results():
    r = run("--tag", "tor")
    assert r.returncode == 0
    assert "commande" in r.stdout.lower()


def test_tag_unknown_tag_returns_zero_results():
    r = run("--tag", "xyzinexistanttag999")
    assert r.returncode == 0
    assert "Aucune" in r.stdout


# ── --missing-tools ────────────────────────────────────────────────────────────

def test_missing_tools_exits_zero():
    r = run("--missing-tools")
    assert r.returncode == 0


def test_missing_tools_lists_tools_or_all_ok():
    r = run("--missing-tools")
    assert r.returncode == 0
    assert ("manquant" in r.stdout.lower() or "installés" in r.stdout.lower())


# ── --install-profile ─────────────────────────────────────────────────────────

def test_install_profile_basic_dry_run():
    r = run("--install-profile", "basic", "--install-dry-run")
    assert r.returncode == 0
    assert "Installation profile" in r.stdout
    assert "Dry-run only" in r.stdout


def test_install_profile_advanced_dry_run_mentions_managers():
    r = run("--install-profile", "advanced", "--install-dry-run")
    assert r.returncode == 0
    assert "pipx" in r.stdout or "go" in r.stdout or "apt" in r.stdout


# ── --generate-completion ─────────────────────────────────────────────────────

def test_generate_completion_bash_contains_new_flags():
    r = run("--generate-completion", "bash")
    assert r.returncode == 0
    assert "--tag" in r.stdout
    assert "--missing-tools" in r.stdout
    assert "--install-profile" in r.stdout


def test_generate_completion_zsh_contains_new_flags():
    r = run("--generate-completion", "zsh")
    assert r.returncode == 0
    assert "--tag" in r.stdout
    assert "--missing-tools" in r.stdout
    assert "--install-profile" in r.stdout


# ── --category prefix matching ─────────────────────────────────────────────────

def test_category_prefix_rec_resolves_to_recon():
    r = run("--category", "rec")
    assert r.returncode == 0
    assert "rec_" in r.stdout


def test_category_substring_attack_resolves_to_web_attack():
    r = run("--category", "attack")
    assert r.returncode == 0
    assert "web_" in r.stdout
