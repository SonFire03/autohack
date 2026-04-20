"""
Thème visuel centralisé — toutes les couleurs et composants UI passent ici.
"""
from datetime import datetime
from rich.console import Console
from rich.text import Text
from rich.rule import Rule
from rich.panel import Panel
from rich.align import Align
from rich.table import Table
from rich.columns import Columns
from rich import box as rich_box

console = Console()

# ── Palette ───────────────────────────────────────────────────────────────────
C_PRIMARY   = "bold white"
C_ACCENT    = "bright_cyan"
C_DIM       = "grey50"
C_OK        = "bright_green"
C_WARN      = "bright_yellow"
C_DANGER    = "bright_red"
C_HEADER_BG = "blue"          # fond du bandeau titre
C_BORDER    = "blue"
C_MUTED     = "dim"

# ── Box styles ────────────────────────────────────────────────────────────────
BOX_TABLE   = rich_box.SIMPLE_HEAVY
BOX_PANEL   = rich_box.ROUNDED

# ── Bannière ASCII ────────────────────────────────────────────────────────────
BANNER_LINES = [
    "  ██████╗ ██╗   ██╗████████╗ ██████╗ ██╗  ██╗ █████╗  ██████╗██╗  ██╗",
    "  ██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗██║  ██║██╔══██╗██╔════╝██║ ██╔╝",
    "  ███████║██║   ██║   ██║   ██║   ██║███████║███████║██║     █████╔╝  ",
    "  ██╔══██║██║   ██║   ██║   ██║   ██║██╔══██║██╔══██║██║     ██╔═██╗  ",
    "  ██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║  ██║██║  ██║╚██████╗██║  ██╗ ",
    "  ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝",
]
BANNER_COLORS = ["#1a6eff", "#2a7fff", "#3a90ff", "#4aa0ff", "#5ab0ff", "#6ac0ff"]
AUTHOR_URL = "https://github.com/SonFire03"


def render_banner() -> None:
    """Imprime la bannière ASCII avec dégradé bleu."""
    for line, color in zip(BANNER_LINES, BANNER_COLORS):
        console.print(Align.center(Text(line, style=f"bold {color}")))
    console.print(Align.center(Text(AUTHOR_URL, style="dim bright_cyan")))


def render_separator(style: str = "dim blue") -> None:
    console.print(Rule(style=style))


def pill(label: str, ok: bool) -> Text:
    """Pill colorée indiquant la disponibilité d'un outil."""
    t = Text()
    if ok:
        t.append(f"  {label}  ", style="bold black on bright_green")
    else:
        t.append(f"  {label}  ", style="bold white on grey23")
    return t


def section_title(text: str) -> Text:
    """Titre de section dans le menu principal."""
    t = Text()
    t.append("  ")
    t.append(text.upper(), style=f"bold {C_ACCENT}")
    return t


def page_header(title: str, subtitle: str = "", breadcrumb: str = "") -> None:
    """En-tête de page avec breadcrumb optionnel."""
    from config.settings import APP_NAME
    console.clear()
    line = Text()
    line.append(f" {APP_NAME} ", style=f"bold white on {C_HEADER_BG}")
    if breadcrumb:
        line.append(f"  {breadcrumb}", style=C_DIM)
        line.append("  ›  ", style=C_DIM)
    else:
        line.append("  ", style="")
    line.append(title, style=C_PRIMARY)
    if subtitle:
        line.append(f"   {subtitle}", style=C_DIM)
    line.append(f"   {datetime.now().strftime('%H:%M')}", style=C_DIM)
    console.print(line)
    console.print(Rule(style="dim blue"))
    console.print()


def kbd(key: str, label: str, color: str = "bright_cyan") -> Text:
    """Touche de clavier stylée : [R] label."""
    t = Text()
    t.append(f" {key.upper()} ", style=f"bold black on {color}")
    t.append(f" {label}", style=C_DIM)
    return t


def prompt(context: str = "") -> str:
    """Prompt unifié avec contexte optionnel."""
    from rich.columns import Columns
    p = Text()
    p.append("\n  ", style="")
    if context:
        p.append(f"[{context}]", style=f"bold {C_ACCENT}")
        p.append(" › ", style=C_DIM)
    else:
        p.append("›", style=f"bold {C_ACCENT}")
        p.append(" ", style="")
    return console.input(p)


def action_bar(actions: list) -> None:
    """Barre d'actions : liste de (touche, label, couleur)."""
    from rich.columns import Columns
    keys = [kbd(k, lbl, col) for k, lbl, col in actions]
    console.print()
    console.print(Align.left(Text("  ") + sum((t for t in keys), Text())))
    console.print()


def status_bar(items: list[tuple[str, str, str]], center: bool = False) -> None:
    """Ligne de statut compacte : [(label, value, style)]."""
    line = Text("  ")
    for idx, (label, value, style) in enumerate(items):
        if idx:
            line.append("  •  ", style="grey35")
        line.append(f"{label} ", style="grey50")
        line.append(value, style=style)
    console.print(Align.center(line) if center else line)
    console.print()


def help_footer(
    actions: list[tuple[str, str]],
    title: str = "Raccourcis",
    width: int | None = None,
) -> None:
    """Panneau léger de raccourcis contextuels en bas d'écran."""
    table = Table(show_header=False, box=None, padding=(0, 1), expand=True)
    table.add_column("key", width=10, style="bold bright_cyan", no_wrap=True)
    table.add_column("label", style="grey70")
    for key, label in actions:
        table.add_row(key, label)
    panel = Panel(
        table,
        title=Text(f" {title} ", style="grey50"),
        title_align="left",
        border_style="grey23",
        padding=(0, 1),
        box=BOX_PANEL,
        width=width,
    )
    console.print(Align.center(panel) if width else panel)
    console.print()


def metric_cards(cards: list[tuple[str, str, str]], width: int | None = None) -> None:
    """Affiche des cartes compactes de métriques: [(label, value, style)]."""
    panels = []
    panel_width = None
    if width and cards:
        panel_width = max(14, (width - (len(cards) - 1) * 2) // len(cards))
    for label, value, style in cards:
        body = Text(justify="center")
        body.append(f"{value}\n", style=style)
        body.append(label, style="grey70")
        panels.append(Panel(
            Align.center(body),
            border_style="grey23",
            padding=(1, 2),
            box=BOX_PANEL,
            width=panel_width,
        ))
    columns = Columns(panels, equal=not width, expand=not width, padding=(0, 1))
    console.print(Align.center(columns) if width else columns)
    console.print()


def legend_panel(
    items: list[tuple[str, str]],
    title: str = "Légende",
    width: int | None = None,
) -> None:
    """Affiche une légende visuelle courte."""
    table = Table(show_header=False, box=None, padding=(0, 1), expand=True)
    table.add_column("token", width=16, no_wrap=True)
    table.add_column("meaning", style="grey70")
    for token, meaning in items:
        table.add_row(token, meaning)
    panel = Panel(
        table,
        title=Text(f" {title} ", style="grey50"),
        title_align="left",
        border_style="grey23",
        padding=(0, 1),
        box=BOX_PANEL,
        width=width,
    )
    console.print(Align.center(panel) if width else panel)
    console.print()


def empty_state(title: str, message: str, hint: str = "") -> None:
    """Affiche un état vide cohérent visuellement."""
    body = Text(justify="center")
    body.append(f"{message}\n", style="grey70")
    if hint:
        body.append(hint, style="bold bright_cyan")
    console.print(Panel(
        Align.center(body),
        title=Text(f" {title} ", style="grey50"),
        title_align="left",
        border_style="grey23",
        padding=(1, 2),
        box=BOX_PANEL,
    ))
    console.print()
