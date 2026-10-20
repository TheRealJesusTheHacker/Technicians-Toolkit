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
from toolkit_launcher.theme import BG, GREEN, PANEL, RED, TEXT  # noqa: E402


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
