from core.catalog import CommandCatalog
from core.playbook import generate_pack_playbook


def test_generate_pack_playbook(tmp_path):
    cat = CommandCatalog()
    path = generate_pack_playbook("web-recon", cat, tmp_path)
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "Playbook" in content
    assert "Steps" in content
