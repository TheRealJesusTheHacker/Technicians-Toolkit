"""Sphinx, the kit's eighth member: tracked, not yet bundled.

Sphinx has no published release, and the bundle assembles only from
published releases — so bundle/tools.json accounts for it under
``absent``, the same honest shape Lazarus and Aegis held in bundles
v0.1.0/v0.2.0 before their first releases. These tests pin that
membership against the repo's real pin file and against the window
the assembler-built manifest produces: seven bundled tools ready,
the Beerus stick separate, and Sphinx's card present with no working
Launch, its truthful note, and its namesake identity stripe —
guardian bronze-gold, canonical since Sphinx's Windows Phase 3
(v0.3.0); while that palette did not exist the card wore the quiet
panel edge, and no color was improvised for it in the meantime.
"""

import json
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QLabel  # noqa: E402

from conftest import bundled_tool, write_bundle  # noqa: E402
from toolkit_launcher import __version__  # noqa: E402
from toolkit_launcher.app import build_window, run_check  # noqa: E402
from toolkit_launcher.discovery import discover  # noqa: E402
from toolkit_launcher.manifest import load_manifest  # noqa: E402
from toolkit_launcher.theme import IDENTITY_STRIPES, PANEL_EDGE, stripe_for  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS_JSON = REPO_ROOT / "bundle" / "tools.json"

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

# The seven bundled pins, exactly as bundle 1.0.0 shipped them. Any
# change here is a member sync of its own, never a side effect of
# membership bookkeeping.
EXPECTED_PINS = [
    ("Argus", "1.2.7", "v1.2.7", "ArgusPortable.zip"),
    ("NitroCore", "1.1.6", "v1.1.6", "NitroCorePortable.zip"),
    ("VectorZip", "1.2.8", "v1.2.8", "VectorZipPortable.zip"),
    ("Charon", "1.0.5", "v1.0.5", "CharonPortable.zip"),
    ("Lazarus", "1.0.3", "v1.0.3", "LazarusPortable.zip"),
    ("Aegis", "1.0.5", "v1.0.5", "AegisPortable.zip"),
    ("Beerus", "0.6.2", "v0.6.2", "BeerusPortable.zip"),
]


@pytest.fixture(scope="module")
def qapp():
    yield QApplication.instance() or QApplication([])


def _tools_json():
    return json.loads(TOOLS_JSON.read_text(encoding="utf-8"))


def _sphinx_absent_entry():
    absent = _tools_json()["absent"]
    assert len(absent) == 1
    return absent[0]


def _membership_bundle(root):
    write_bundle(root, tools=SEVEN, linked=[STICK_ENTRY], absent=[_sphinx_absent_entry()])
    for rel in ENTRYPOINTS:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"fake tool")


def test_tools_json_accounts_for_sphinx_as_absent_only():
    config = _tools_json()
    # The seven bundled members' pins are untouched, and this change
    # cuts no new bundle: the manifest still names bundle 1.0.0.
    assert [
        (t["name"], t["version"], t["tag"], t["artifact"]) for t in config["tools"]
    ] == EXPECTED_PINS
    assert config["bundle_version"] == "1.0.0"
    assert config["zip_name"] == "TechniciansToolkit-v1.0.0.zip"
    assert [e["name"] for e in config["linked"]] == ["Beerus — Live Boot"]
    # Sphinx is a member in the absent list only — with nothing a
    # release would pin: no version, tag, artifact, sums, or start
    # file exists to write down, so none is invented.
    entry = _sphinx_absent_entry()
    assert entry["name"] == "Sphinx"
    assert entry["repo"] == "TheRealJesusTheHacker/Sphinx"
    assert set(entry) == {"job", "name", "note", "repo"}
    assert "first release ships" in entry["note"]


def test_tools_json_launcher_version_matches_the_launcher():
    # The manifest the assembler writes names the launcher version
    # from tools.json; the launcher names its own in __init__. They
    # move together or the shipped bundle would misreport itself.
    assert _tools_json()["launcher"]["version"] == __version__


def test_membership_states(qapp, tmp_path):
    _membership_bundle(tmp_path)
    manifest = load_manifest(tmp_path)
    assert [t.status for t in manifest.tools] == ["bundled"] * 7 + ["linked", "absent"]
    states = discover(tmp_path, manifest)
    by_name = {s.entry.name: s for s in states}
    for tool in SEVEN:
        assert by_name[tool["name"]].state == "ready", tool["name"]
    assert by_name["Beerus — Live Boot"].state == "separate"
    sphinx = by_name["Sphinx"]
    assert sphinx.state == "not_in_bundle"
    assert sphinx.detail == _sphinx_absent_entry()["note"]
    assert sphinx.entry.version == ""  # no release, no version to show


def test_sphinx_card_has_no_launch_and_its_own_stripe(qapp, tmp_path):
    _membership_bundle(tmp_path)
    window = build_window(tmp_path)
    cards = {c["entry"].name: c for c in window.tool_cards}
    assert set(cards) == {t["name"] for t in SEVEN} | {"Beerus — Live Boot", "Sphinx"}
    sphinx = cards["Sphinx"]
    # No Launch: the button the card carries for layout is disabled
    # and says what is true instead.
    assert not sphinx["button"].isEnabled()
    assert sphinx["button"].text() == "Not in this bundle"
    assert sphinx["status"].text() == _sphinx_absent_entry()["note"]
    # Its own identity stripe: Sphinx's namesake palette shipped
    # canonical in its Windows Phase 3 (v0.3.0) — basalt black,
    # sandstone, bronze-gold — and the stripe is that bronze,
    # exactly the BRONZE of Sphinx's own theme module
    # (windows/src/sphinx_win/app/theme.py at Sphinx HEAD
    # c9ea4f0dfc1d). It is not the panel edge the card wore while
    # the palette did not exist, and it is not Beerus's violet.
    assert IDENTITY_STRIPES["Sphinx"] == "#cf9a3e"
    assert stripe_for("Sphinx") == "#cf9a3e"
    assert "#cf9a3e" in sphinx["stripe"].styleSheet()
    assert PANEL_EDGE not in sphinx["stripe"].styleSheet()
    for name, color in IDENTITY_STRIPES.items():
        if name != "Sphinx":
            assert color not in sphinx["stripe"].styleSheet()
    summary = window.findChild(QLabel, "SummaryLine")
    assert summary.text() == (
        "7 tools in this bundle  ·  1 still to come  ·  "
        "1 on its own bootable stick"
    )
    window.close()


def test_membership_check_output(tmp_path, capsys):
    _membership_bundle(tmp_path)
    assert run_check(tmp_path) == 0
    out = capsys.readouterr().out
    assert "- Sphinx: not_in_bundle" in out
    assert "first release ships" in out
    assert "Beerus — Live Boot" in out and "separate" in out
