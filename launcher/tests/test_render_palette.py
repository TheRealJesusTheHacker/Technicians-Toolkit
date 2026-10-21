"""Rendered-palette guard: the frozen window must stay on-palette.

Renders the real window offscreen and inspects the pixels: the
Sentinel palette is present, red appears only where a problem state
asks for it, and no purple pixel exists anywhere. Visual polish is a
release criterion in this fleet, so it is pinned by a test, not by
someone's memory of a screenshot.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402

pytest.importorskip("PySide6")

from PySide6.QtGui import QColor  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from conftest import bundled_tool, write_bundle  # noqa: E402
from toolkit_launcher.app import build_window  # noqa: E402
from toolkit_launcher.theme import (  # noqa: E402
    BG,
    GREEN,
    IDENTITY_STRIPES,
    PANEL,
    PANEL_EDGE,
    RED,
    TEXT,
    stripe_for,
)


@pytest.fixture(scope="module")
def qapp():
    yield QApplication.instance() or QApplication([])


def _pixels(image):
    img = image.convertToFormat(image.Format.Format_RGB32)
    width, height = img.width(), img.height()
    for y in range(height):
        for x in range(width):
            yield img.pixelColor(x, y)


def _is_purple(color: QColor) -> bool:
    r, g, b = color.red(), color.green(), color.blue()
    return r > 60 and b > 60 and b > g + 25 and r > g + 25


def test_rendered_window_is_on_palette(qapp, tmp_path):
    write_bundle(tmp_path, tools=[bundled_tool()])
    (tmp_path / "FakeTool.exe").write_bytes(b"fake")
    window = build_window(tmp_path)
    window.show()
    qapp.processEvents()
    image = window.grab().toImage()
    window.close()

    colors = {}
    purple_at = []
    width = image.width()
    for index, color in enumerate(_pixels(image)):
        key = color.name().lower()
        colors[key] = colors.get(key, 0) + 1
        if _is_purple(color):
            purple_at.append((index % width, index // width))
    # Font anti-aliasing can leave an isolated fringe pixel or two at
    # glyph edges. A purple UI element — a button, a background, text —
    # would render as a cluster of many. Forbid clusters and any count
    # beyond rasterizer noise.
    assert len(purple_at) <= 5, f"purple pixels rendered: {purple_at}"
    for x, y in purple_at:
        neighbours = {
            (x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
        } - {(x, y)}
        assert not (neighbours & set(purple_at)), "clustered purple pixels rendered"
    assert colors.get(BG, 0) > 0, "bundle background color missing from render"
    assert colors.get(PANEL, 0) > 0, "card panel color missing from render"
    assert colors.get(GREEN, 0) > 0, "Sentinel green missing from render"
    assert colors.get(TEXT, 0) > 0, "main text color missing from render"
    # A healthy all-ready window must not render the problem accent.
    assert colors.get(RED, 0) == 0, "red accent rendered without a problem state"


STICK_ENTRY = {
    "name": "Beerus \u2014 Live Boot",
    "job": "Wipes drives completely, with proof it was done.",
    "note": "A bootable USB stick of its own \u2014 get it from the Beerus repo.",
}


def _color_counts(image):
    counts = {}
    for color in _pixels(image):
        key = color.name().lower()
        counts[key] = counts.get(key, 0) + 1
    return counts


def _render(root, height=820):
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    window = build_window(root)
    window.resize(720, height)
    window.show()
    app.processEvents()
    image = window.grab().toImage()
    window.close()
    return image


def test_identity_stripes_are_the_locked_values():
    # The namesake primaries, exactly as the palette program locked
    # them. Beerus's violet is the owner's single namesake exception.
    # Sphinx's guardian bronze-gold joined the locked set when its
    # palette shipped canonical in Sphinx's Windows Phase 3 (v0.3.0):
    # the hex is Sphinx's own BRONZE, read from its theme module
    # (windows/src/sphinx_win/app/theme.py) — not an invention here.
    assert IDENTITY_STRIPES == {
        "Argus": "#25cc8a",
        "NitroCore": "#2ea3ff",
        "VectorZip": "#33b5e8",
        "Charon": "#2fbfa8",
        "Lazarus": "#f0a13c",
        "Aegis": "#d29f3c",
        "Beerus": "#a478f7",
        "Sphinx": "#cf9a3e",
    }


def test_stripe_for_maps_names_and_forms():
    for name, hexcode in IDENTITY_STRIPES.items():
        assert stripe_for(name) == hexcode
    # A linked entry names the tool before its form.
    assert stripe_for("Beerus \u2014 Live Boot") == "#a478f7"
    # An unknown tool gets the quiet panel edge, never a guess.
    assert stripe_for("FakeTool") == PANEL_EDGE


def test_rendered_stripes_carry_each_tools_color(qapp, tmp_path):
    tools = [
        bundled_tool(name="Argus", entrypoint="Argus.exe"),
        bundled_tool(name="Beerus", entrypoint="Beerus/Beerus.exe"),
    ]
    write_bundle(tmp_path, tools=tools, linked=[STICK_ENTRY])
    for tool in tools:
        ep = tmp_path / tool["entrypoint"]
        ep.parent.mkdir(parents=True, exist_ok=True)
        ep.write_bytes(b"fake tool")
    counts = _color_counts(_render(tmp_path))
    # Both stripes render at scale: the peacock emerald and the
    # Beerus violet (two cards carry his: the app and the stick).
    assert counts.get("#25cc8a", 0) >= 100, counts.get("#25cc8a", 0)
    assert counts.get("#a478f7", 0) >= 200, counts.get("#a478f7", 0)


def test_rendered_purple_is_only_beerus_violet(qapp, tmp_path):
    tools = [
        bundled_tool(name="Argus", entrypoint="Argus.exe"),
        bundled_tool(name="Beerus", entrypoint="Beerus/Beerus.exe"),
    ]
    write_bundle(tmp_path, tools=tools, linked=[STICK_ENTRY])
    for tool in tools:
        ep = tmp_path / tool["entrypoint"]
        ep.parent.mkdir(parents=True, exist_ok=True)
        ep.write_bytes(b"fake tool")
    image = _render(tmp_path)
    off_violet = []
    img = image.convertToFormat(image.Format.Format_RGB32)
    for y in range(img.height()):
        for x in range(img.width()):
            color = img.pixelColor(x, y)
            if _is_purple(color) and color.name().lower() != "#a478f7":
                off_violet.append((x, y, color.name()))
    # Anti-aliasing at the stripe's edges may blend a few pixels;
    # a painted purple element would be a field of them.
    assert len(off_violet) <= 12, off_violet


def test_nitrocore_and_vectorzip_stripes_side_by_side(qapp, tmp_path):
    # The design stage flagged these two as the suite's closest
    # pair: azure #2ea3ff against cyan #33b5e8. Rendered adjacent,
    # both must appear at scale \u2014 and they are different colors.
    tools = [
        bundled_tool(name="NitroCore", entrypoint="NitroCoreOptimizer.exe"),
        bundled_tool(name="VectorZip", entrypoint="VectorZip.exe"),
    ]
    write_bundle(tmp_path, tools=tools)
    for tool in tools:
        (tmp_path / tool["entrypoint"]).write_bytes(b"fake tool")
    counts = _color_counts(_render(tmp_path, height=640))
    assert counts.get("#2ea3ff", 0) >= 100, counts.get("#2ea3ff", 0)
    assert counts.get("#33b5e8", 0) >= 100, counts.get("#33b5e8", 0)
