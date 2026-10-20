"""The house palette — Sentinel green on black, the Argus standard.

Every text/background pairing used by the launcher, checked:
- TEXT (#e8f2ea) on BG/PANEL: >12:1
- TEXT_FAINT (#7d927f) on BG/PANEL: ~5.7:1
- GREEN (#2ee06f) on BG/PANEL: >9:1
- near-black text on the GREEN launch button: >9:1
- RED (#ff7b72) on PANEL: ~7.6:1 — the brand's rare accent, used only
  for problem states (a missing tool, an incomplete bundle).
The window itself carries no purple. The single violet in it is
Beerus's identity stripe: his canonical violet, by the owner's
namesake exception ("Beerus can have purple because it's
appropriate", 2026-10-20) — the same exception his own app carries.
The frozen renders are pixel-checked against this palette before a
bundle ships.
"""

BG = "#060a07"
PANEL = "#0c130d"
PANEL_EDGE = "#1d2b1f"
TEXT = "#e8f2ea"
TEXT_FAINT = "#7d927f"
GREEN = "#2ee06f"
GREEN_HOVER = "#46ec85"
GREEN_PRESSED = "#25b85c"
GREEN_DARK_TEXT = "#04140a"
RED = "#ff7b72"
DISABLED_BG = "#131a14"

# Namesake identity stripes: every tool in the kit carries its own
# namesake color on its card — a slim stripe beside the state accent,
# in the primary of the palette that tool's own app wears (the fleet
# namesake palette program; worst-pair figures live with each tool).
# The window stays Sentinel green on black; the stripes are the
# tools' colors, not the house's.
IDENTITY_STRIPES = {
    "Argus": "#25cc8a",  # peacock emerald
    "NitroCore": "#2ea3ff",  # nitrous azure
    "VectorZip": "#33b5e8",  # blueprint cyan
    "Charon": "#2fbfa8",  # Styx aqua
    "Lazarus": "#f0a13c",  # ember amber
    "Aegis": "#d29f3c",  # shield bronze
    "Beerus": "#a478f7",  # canonical violet — the owner's exception
}


def stripe_for(name: str) -> str:
    """The identity-stripe color for a card, by tool name.

    A linked entry names the tool before its form ("Beerus — Live
    Boot"), so the part before the em dash is tried too. A tool with
    no namesake color gets the panel edge — present, but quiet.
    """
    if name in IDENTITY_STRIPES:
        return IDENTITY_STRIPES[name]
    head = name.split(" \u2014 ")[0]
    return IDENTITY_STRIPES.get(head, PANEL_EDGE)

STYLESHEET = f"""
QMainWindow, QWidget#Root, QDialog {{
    background: {BG};
    color: {TEXT};
    font-family: "Segoe UI", "DejaVu Sans", sans-serif;
    font-size: 14px;
}}
QLabel#Title {{
    font-size: 26px;
    font-weight: 700;
    color: {TEXT};
}}
QLabel#Tagline {{
    color: {GREEN};
    font-size: 13px;
    font-weight: 600;
}}
QLabel#BundleLine, QLabel#SummaryLine, QLabel#Footer {{
    color: {TEXT_FAINT};
    font-size: 12px;
}}
QWidget#Rule {{
    background: {GREEN};
}}
QFrame#Card, QFrame#Panel {{
    background: {PANEL};
    border: 1px solid {PANEL_EDGE};
    border-radius: 8px;
}}
QLabel#ToolName {{
    font-size: 16px;
    font-weight: 700;
    color: {TEXT};
}}
QLabel#ToolVersion {{
    color: {TEXT_FAINT};
    font-size: 12px;
}}
QLabel#ToolJob {{
    color: {TEXT};
    font-size: 13px;
}}
QLabel#ToolStatus {{
    color: {TEXT_FAINT};
    font-size: 12px;
}}
QLabel#ToolStatusReady {{
    color: {GREEN};
    font-size: 12px;
    font-weight: 600;
}}
QLabel#ToolStatusProblem {{
    color: {RED};
    font-size: 12px;
}}
QLabel#ProblemTitle {{
    font-size: 17px;
    font-weight: 700;
    color: {TEXT};
}}
QLabel#ProblemText, QLabel#AboutText {{
    color: {TEXT_FAINT};
    font-size: 13px;
}}
QPushButton#Launch {{
    background: {GREEN};
    color: {GREEN_DARK_TEXT};
    font-weight: 700;
    border: none;
    border-radius: 6px;
    padding: 7px 20px;
    min-width: 96px;
}}
QPushButton#Launch:hover {{
    background: {GREEN_HOVER};
}}
QPushButton#Launch:pressed {{
    background: {GREEN_PRESSED};
}}
QPushButton#Launch:disabled {{
    background: {DISABLED_BG};
    color: {TEXT_FAINT};
    font-weight: 600;
}}
QPushButton#AboutToggle {{
    background: {PANEL};
    color: {TEXT};
    border: 1px solid {PANEL_EDGE};
    border-radius: 6px;
    padding: 6px 14px;
}}
QPushButton#AboutToggle:hover {{
    border-color: {GREEN};
}}
QScrollArea {{
    border: none;
    background: {BG};
}}
QScrollBar:vertical {{
    background: {BG};
    width: 10px;
}}
QScrollBar::handle:vertical {{
    background: {PANEL_EDGE};
    border-radius: 5px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
"""
