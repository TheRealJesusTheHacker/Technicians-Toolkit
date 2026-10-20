"""The full kit: bundle 1.0.0 carries all seven medic-kit tools as
files, plus Beerus's bootable stick as the one linked entry. Every
member gets a launchable card; no "still to come" cards remain.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication  # noqa: E402

from conftest import bundled_tool, write_bundle  # noqa: E402
from toolkit_launcher.app import ABOUT_TEXT, build_window, run_check  # noqa: E402
from toolkit_launcher.discovery import discover  # noqa: E402
from toolkit_launcher.launching import Launcher  # noqa: E402
from toolkit_launcher.manifest import load_manifest  # noqa: E402

SEVEN = [
    bundled_tool(name="Argus", entrypoint="Argus.exe"),
    bundled_tool(name="NitroCore", entrypoint="NitroCoreOptimizer.exe"),
    bundled_tool(name="VectorZip", entrypoint="VectorZip.exe"),
    bundled_tool(name="Charon", entrypoint="Charon/Charon.exe"),
    bundled_tool(name="Lazarus", entrypoint="Lazarus.exe"),
    bundled_tool(name="Aegis", entrypoint="Aegis/Aegis.exe"),
    bundled_tool(name="Beerus", entrypoint="Beerus/Beerus.exe"),
]
STICK_ENTRY = {
    "name": "Beerus — Live Boot",
    "job": "Wipes drives completely, with proof it was done.",
    "note": "A bootable USB stick of its own — get it from the Beerus repo.",
}
ENTRYPOINTS = [t["entrypoint"] for t in SEVEN]


@pytest.fixture(scope="module")
def qapp():
    yield QApplication.instance() or QApplication([])


def _full_kit_bundle(root):
    write_bundle(root, tools=SEVEN, linked=[STICK_ENTRY])
    for rel in ENTRYPOINTS:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"fake tool")


def test_full_kit_loads_and_all_ready(tmp_path):
    _full_kit_bundle(tmp_path)
    manifest = load_manifest(tmp_path)
    assert [t.status for t in manifest.tools] == ["bundled"] * 7 + ["linked"]
    states = discover(tmp_path, manifest)
    by_name = {s.entry.name: s for s in states}
    for tool in SEVEN:
        assert by_name[tool["name"]].state == "ready", tool["name"]
    assert by_name["Beerus — Live Boot"].state == "separate"
    assert not any(s.state == "not_in_bundle" for s in states)


def test_full_kit_window_cards(qapp, tmp_path):
    _full_kit_bundle(tmp_path)
    window = build_window(tmp_path)
    cards = {c["entry"].name: c for c in window.tool_cards}
    assert set(cards) == {t["name"] for t in SEVEN} | {"Beerus — Live Boot"}
    for tool in SEVEN:
        card = cards[tool["name"]]
        assert card["button"].isEnabled(), tool["name"]
        assert card["button"].text() == "Launch", tool["name"]
        assert card["status"].text() == "Ready.", tool["name"]
    stick = cards["Beerus — Live Boot"]
    assert not stick["button"].isEnabled()
    assert stick["button"].text() == "Bootable USB"
    window.close()


def test_aegis_and_lazarus_launch_through_the_seam(qapp, tmp_path, runner):
    _full_kit_bundle(tmp_path)
    window = build_window(tmp_path, launcher=Launcher(tmp_path, runner=runner))
    cards = {c["entry"].name: c for c in window.tool_cards}
    cards["Aegis"]["button"].click()
    cards["Lazarus"]["button"].click()
    assert len(runner.calls) == 2
    argvs = [c["argv"][0] for c in runner.calls]
    assert argvs[0].endswith(os.path.join("Aegis", "Aegis.exe"))
    assert argvs[1].endswith("Lazarus.exe")
    window.close()


def test_full_kit_check_output(tmp_path, capsys):
    _full_kit_bundle(tmp_path)
    assert run_check(tmp_path) == 0
    out = capsys.readouterr().out
    for tool in SEVEN:
        assert f"- {tool['name']}" in out, tool["name"]
        assert f"{tool['name']} v1.0.0: ready" in out or "ready" in out
    assert "Beerus — Live Boot" in out and "separate" in out
    assert "not_in_bundle" not in out


def test_about_text_claims_the_complete_kit():
    assert "all seven tools" in ABOUT_TEXT
    assert "Lazarus" in ABOUT_TEXT and "Aegis" in ABOUT_TEXT
    # Both Beerus forms stay told apart (see test_two_forms.py).
    assert "Beerus Portable, the app" in ABOUT_TEXT
    assert "Live Boot" in ABOUT_TEXT


def test_about_dialog_fits_its_whole_text(qapp):
    """The About box must show every paragraph — never clipped.

    Regression pin: when the full-kit paragraph joined the About
    copy, the dialog's fixed height silently cut the text off
    mid-sentence. The label's laid-out height must cover the height
    its own font metrics need for the full text at its real width.
    """
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QLabel

    from toolkit_launcher.app import build_about_dialog

    dialog = build_about_dialog()
    dialog.show()
    qapp.processEvents()
    label = dialog.findChild(QLabel, "AboutText")
    needed = label.fontMetrics().boundingRect(
        0, 0, label.width(), 100000, Qt.TextFlag.TextWordWrap, ABOUT_TEXT
    ).height()
    assert label.height() >= needed, (
        f"About text clipped: label is {label.height()}px tall, "
        f"the text needs {needed}px"
    )
    dialog.close()
