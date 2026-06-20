from __future__ import annotations

from datetime import datetime
from pathlib import Path

from core.packs import get_pack


def generate_pack_playbook(pack_name: str, catalog, out_dir: Path) -> Path:
    pack = get_pack(pack_name)
    if not pack:
        raise ValueError(f"Unknown pack: {pack_name}")

    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = out_dir / f"playbook_{pack.name}_{ts}.md"

    lines = [
        f"# Playbook — {pack.title}",
        "",
        f"> Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        f"{pack.description}",
        "",
        "## Steps",
        "",
    ]
    for idx, cmd_id in enumerate(pack.command_ids, 1):
        cmd = catalog.get_by_id(cmd_id)
        if not cmd:
            lines += [f"### {idx}. `{cmd_id}`", "- [ ] Missing command in catalog", ""]
            continue
        lines += [
            f"### {idx}. `{cmd['id']}` — {cmd['name']}",
            "- [ ] Execute",
            f"- Category: `{cmd.get('category','')}`",
            f"- Tool: `{cmd.get('tool_required','')}`",
            f"- Risk: {cmd.get('risks','')}",
            "```bash",
            cmd.get("command", ""),
            "```",
            "",
        ]

    path.write_text("\n".join(lines), encoding="utf-8")
    return path
