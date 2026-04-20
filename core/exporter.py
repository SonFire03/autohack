import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from config.settings import EXPORTS_DIR, CATEGORY_LABELS, CATEGORY_ICONS, APP_NAME, APP_VERSION
from core.logger import ActionLogger


class Exporter:
    """Génère des exports du catalogue en TXT, Markdown et JSON."""

    def __init__(
        self,
        all_commands: List[Dict[str, Any]],
        export_dir: Optional[Path] = None,
    ) -> None:
        self._cmds = all_commands
        self._ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
        self._dir = Path(export_dir) if export_dir else EXPORTS_DIR
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self, name: str) -> Path:
        return self._dir / name

    def export_txt(self) -> Path:
        path = self._path(f"commands_{self._ts}.txt")
        lines = [f"{APP_NAME} v{APP_VERSION}", f"Export TXT — {self._ts}", "=" * 60, ""]
        current_cat = None
        for cmd in self._cmds:
            cat = cmd.get("category", "")
            if cat != current_cat:
                current_cat = cat
                label = CATEGORY_LABELS.get(cat, cat.upper())
                icon = CATEGORY_ICONS.get(cat, "")
                lines += ["", f"{icon}  {label}", "-" * 50]
            purpose = cmd['purpose']
            purpose_line = purpose[:100] + ("…" if len(purpose) > 100 else "")
            lines += [
                f"  [{cmd['id']}] {cmd['name']}",
                f"  Commande : {cmd['command']}",
                f"  But      : {purpose_line}",
                "",
            ]
        path.write_text("\n".join(lines), encoding="utf-8")
        ActionLogger.log_export(str(path), "txt")
        return path

    def export_markdown(self) -> Path:
        path = self._path(f"report_{self._ts}.md")
        lines = [
            f"# {APP_NAME} — Catalogue de commandes",
            f"",
            f"> Généré le {datetime.now().strftime('%Y-%m-%d à %H:%M')} | Version {APP_VERSION}",
            f"",
        ]
        current_cat = None
        for cmd in self._cmds:
            cat = cmd.get("category", "")
            if cat != current_cat:
                current_cat = cat
                label = CATEGORY_LABELS.get(cat, cat.upper())
                icon = CATEGORY_ICONS.get(cat, "")
                lines += ["", f"## {icon} {label}", ""]
            sudo_badge = " `[sudo]`" if cmd.get("requires_sudo") else ""
            danger_badge = " ⚠️**DANGEREUX**" if cmd.get("dangerous") else ""
            lines += [
                f"### `{cmd['id']}` — {cmd['name']}{sudo_badge}{danger_badge}",
                f"",
                f"**Description :** {cmd.get('description', '')}",
                f"",
                f"```bash",
                f"{cmd['command']}",
                f"```",
                f"",
                f"**But :** {cmd.get('purpose', '')}",
                f"",
                f"**Sortie attendue :** `{cmd.get('expected_output', '')}`",
                f"",
                f"**Risques :** {cmd.get('risks', '')}",
                f"",
                f"**Prérequis :** {', '.join(cmd.get('prerequisites', [])) or 'Aucun'}",
                f"",
                "---",
                "",
            ]
        path.write_text("\n".join(lines), encoding="utf-8")
        ActionLogger.log_export(str(path), "markdown")
        return path

    def export_json(self) -> Path:
        path = self._path(f"catalog_{self._ts}.json")
        path.write_text(
            json.dumps(self._cmds, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        ActionLogger.log_export(str(path), "json")
        return path

    def export_html(self) -> Path:
        path = self._path(f"catalog_{self._ts}.html")
        from html import escape
        from collections import defaultdict

        by_cat: dict = defaultdict(list)
        for cmd in self._cmds:
            by_cat[cmd.get("category", "")].append(cmd)

        sections = []
        for cat, cmds in by_cat.items():
            label = escape(CATEGORY_LABELS.get(cat, cat.upper()))
            icon = CATEGORY_ICONS.get(cat, "")
            rows = []
            for cmd in cmds:
                danger = '<span class="badge danger">⚠ dangereux</span>' if cmd.get("dangerous") else ""
                sudo = '<span class="badge sudo">🔐 sudo</span>' if cmd.get("requires_sudo") else ""
                desc = escape(cmd.get("description") or cmd.get("purpose", ""))
                rows.append(
                    f'<details><summary>'
                    f'<code class="cmd-id">{escape(cmd["id"])}</code> '
                    f'<strong>{escape(cmd["name"])}</strong> {danger}{sudo}'
                    f'</summary>'
                    f'<p class="desc">{desc}</p>'
                    f'<pre><code>{escape(cmd["command"])}</code></pre>'
                    f'<table>'
                    f'<tr><th>But</th><td>{escape(cmd.get("purpose",""))}</td></tr>'
                    f'<tr><th>Sortie</th><td><code>{escape(cmd.get("expected_output",""))}</code></td></tr>'
                    f'<tr><th>Risques</th><td>{escape(cmd.get("risks",""))}</td></tr>'
                    f'<tr><th>Prérequis</th><td>{escape(", ".join(cmd.get("prerequisites",[])) or "Aucun")}</td></tr>'
                    f'</table>'
                    f'</details>'
                )
            sections.append(
                f'<section>'
                f'<h2>{icon} {label} <small>({len(cmds)} commandes)</small></h2>'
                + "\n".join(rows)
                + "</section>"
            )

        date_str = datetime.now().strftime("%Y-%m-%d à %H:%M")
        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(APP_NAME)} — Catalogue v{escape(APP_VERSION)}</title>
<style>
  :root{{--bg:#0d1117;--surface:#161b22;--border:#30363d;--accent:#58a6ff;--green:#3fb950;--red:#f85149;--yellow:#d29922;--text:#c9d1d9;--dim:#8b949e}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,sans-serif;padding:1.5rem;line-height:1.6}}
  header{{border-bottom:1px solid var(--border);padding-bottom:1rem;margin-bottom:1.5rem}}
  header h1{{color:var(--accent);font-size:1.6rem}} header p{{color:var(--dim);font-size:.9rem}}
  #search{{width:100%;padding:.6rem 1rem;background:var(--surface);border:1px solid var(--border);border-radius:6px;color:var(--text);font-size:1rem;margin-bottom:1.5rem}}
  #search:focus{{outline:none;border-color:var(--accent)}}
  section{{margin-bottom:2rem}}
  h2{{color:var(--accent);font-size:1.15rem;margin-bottom:.75rem;padding:.4rem .6rem;background:var(--surface);border-radius:6px;border-left:3px solid var(--accent)}}
  h2 small{{color:var(--dim);font-size:.85rem;font-weight:normal}}
  details{{background:var(--surface);border:1px solid var(--border);border-radius:6px;margin-bottom:.4rem;overflow:hidden}}
  details[open]{{border-color:var(--accent)}}
  summary{{padding:.6rem 1rem;cursor:pointer;list-style:none;display:flex;align-items:center;gap:.5rem}}
  summary:hover{{background:#1f2937}} summary::marker{{display:none}}
  .cmd-id{{background:#1f2937;color:var(--dim);padding:.1rem .4rem;border-radius:4px;font-size:.8rem}}
  .badge{{font-size:.75rem;padding:.1rem .4rem;border-radius:4px;font-weight:600}}
  .badge.danger{{background:#3d1a1a;color:var(--red)}} .badge.sudo{{background:#2a2a0d;color:var(--yellow)}}
  .desc{{padding:.5rem 1rem;color:var(--dim);font-size:.9rem;border-top:1px solid var(--border)}}
  pre{{background:#0d1117;padding:1rem;overflow-x:auto;font-size:.9rem;border-top:1px solid var(--border)}}
  pre code{{color:#79c0ff}}
  table{{width:100%;border-collapse:collapse;font-size:.88rem;border-top:1px solid var(--border)}}
  th,td{{padding:.4rem 1rem;text-align:left;border-bottom:1px solid var(--border)}}
  th{{color:var(--dim);font-weight:600;width:110px;white-space:nowrap}}
  td code{{background:#1f2937;padding:.1rem .3rem;border-radius:3px;font-size:.85rem}}
  .hidden{{display:none}}
</style>
</head>
<body>
<header>
  <h1>🔒 {escape(APP_NAME)}</h1>
  <p>Catalogue de commandes · v{escape(APP_VERSION)} · Généré le {date_str} · {len(self._cmds)} commandes</p>
</header>
<input id="search" type="search" placeholder="🔍 Filtrer les commandes…" autocomplete="off">
{"".join(sections)}
<script>
const s=document.getElementById('search');
s.addEventListener('input',()=>{{
  const q=s.value.toLowerCase();
  document.querySelectorAll('details').forEach(d=>{{
    d.classList.toggle('hidden',q&&!d.textContent.toLowerCase().includes(q));
  }});
  document.querySelectorAll('section').forEach(sec=>{{
    sec.style.display=[...sec.querySelectorAll('details')].every(d=>d.classList.contains('hidden'))?'none':'';
  }});
}});
</script>
</body>
</html>"""
        path.write_text(html, encoding="utf-8")
        ActionLogger.log_export(str(path), "html")
        return path

    def generate_full_report(self) -> Path:
        return self.export_markdown()
