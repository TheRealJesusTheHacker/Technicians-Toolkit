"""Sphinx, the kit's eighth member: bundled since bundle 1.1.0.

Sphinx published its first release (v1.0.0, 2026-10-23), and the
bundle assembles only from published releases — so bundle/tools.json
now pins it as a bundled tool like every other member, and the
``absent`` list is empty: the whole kit is in the bundle as files.
(Before that release, Sphinx held the honest absent shape Lazarus
and Aegis held in bundles v0.1.0/v0.2.0; that history lives in the
tracker and the changelog.) These tests pin the membership against
the repo's real pin file and against the window the assembler-built
manifest produces: eight bundled tools ready, the Beerus stick
separate, and Sphinx's card carrying a working Launch and its
namesake identity stripe — guardian bronze-gold, canonical since
Sphinx's Windows Phase 3 (v0.3.0), read from Sphinx's own theme
module; while the palette did not exist the card wore the quiet
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

EIGHT = [
    bundled_tool(name="Argus", entrypoint="Argus.exe"),
    bundled_tool(name="NitroCore", entrypoint="NitroCoreOptimizer.exe"),
    bundled_tool(name="VectorZip", entrypoint="VectorZip.exe"),
    bundled_tool(name="Charon", entrypoint="Charon/Charon.exe"),
    bundled_tool(name="Lazarus", entrypoint="Lazarus.exe"),
    bundled_tool(name="Aegis", entrypoint="Aegis/Aegis.exe"),
    bundled_tool(name="Beerus", entrypoint="Beerus/Beerus.exe"),
    bundled_tool(name="Sphinx", entrypoint="SphinxPortable/Sphinx.exe"),
]
STICK_ENTRY = {
    "name": "Beerus — Live Boot",
    "job": "Wipes drives completely, with proof it was done.",
    "note": "A bootable USB stick of its own — get it from the Beerus repo.",
}
ENTRYPOINTS = [t["entrypoint"] for t in EIGHT]

# The eight bundled pins, exactly as the current bundle ships them. Any
# change here is a member sync of its own, never a side effect of
# membership bookkeeping.
EXPECTED_PINS = [
    ("Argus", "1.2.9", "v1.2.9", "ArgusPortable.zip"),
    ("NitroCore", "1.1.6", "v1.1.6", "NitroCorePortable.zip"),
    ("VectorZip", "1.2.9", "v1.2.9", "VectorZipPortable.zip"),
    ("Charon", "1.0.5", "v1.0.5", "CharonPortable.zip"),
    ("Lazarus", "1.0.3", "v1.0.3", "LazarusPortable.zip"),
    ("Aegis", "1.0.5", "v1.0.5", "AegisPortable.zip"),
    ("Beerus", "0.6.2", "v0.6.2", "BeerusPortable.zip"),
    ("Sphinx", "1.0.1", "v1.0.1", "SphinxPortable.zip"),
]


@pytest.fixture(scope="module")
def qapp():
    yield QApplication.instance() or QApplication([])


def _tools_json():
    return json.loads(TOOLS_JSON.read_text(encoding="utf-8"))


def _membership_bundle(root):
    write_bundle(root, tools=EIGHT, linked=[STICK_ENTRY], absent=[])
    for rel in ENTRYPOINTS:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"fake tool")


def test_tools_json_bundles_sphinx_with_the_eight():
    config = _tools_json()
    # The eight bundled members' pins, Sphinx's among them, and the
    # bundle they ship as: 1.2.0 (1.1.0 was the first with the whole kit).
    assert [
        (t["name"], t["version"], t["tag"], t["artifact"]) for t in config["tools"]
    ] == EXPECTED_PINS
    assert config["bundle_version"] == "1.2.0"
    assert config["zip_name"] == "TechniciansToolkit-v1.2.0.zip"
    assert [e["name"] for e in config["linked"]] == ["Beerus — Live Boot"]
    # Nobody is absent any more: every member of the kit is in the
    # bundle as files, so the honest shape is an empty absent list.
    assert config["absent"] == []
    # Sphinx's pin is a real release pin, of the same shape as every
    # other member's: the portable its maker released, its published
    # checksums, and the start file inside its own shipped folder.
    sphinx = config["tools"][-1]
    assert sphinx["name"] == "Sphinx"
    assert sphinx["repo"] == "TheRealJesusTheHacker/Sphinx"
    assert sphinx["entrypoint"] == "SphinxPortable/Sphinx.exe"
    assert sphinx["sums"] == "SHA256SUMS.txt"


def test_tools_json_launcher_version_matches_the_launcher():
    # The manifest the assembler writes names the launcher version
    # from tools.json; the launcher names its own in __init__. They
    # move together or the shipped bundle would misreport itself.
    assert _tools_json()["launcher"]["version"] == __version__


def test_membership_states(qapp, tmp_path):
    _membership_bundle(tmp_path)
    manifest = load_manifest(tmp_path)
    assert [t.status for t in manifest.tools] == ["bundled"] * 8 + ["linked"]
    states = discover(tmp_path, manifest)
    by_name = {s.entry.name: s for s in states}
    for tool in EIGHT:
        assert by_name[tool["name"]].state == "ready", tool["name"]
    assert by_name["Beerus — Live Boot"].state == "separate"
    assert not any(s.state == "not_in_bundle" for s in states)
    sphinx = by_name["Sphinx"]
    assert sphinx.entry.version == "1.0.0"


def test_sphinx_card_launches_and_keeps_its_own_stripe(qapp, tmp_path):
    _membership_bundle(tmp_path)
    window = build_window(tmp_path)
    cards = {c["entry"].name: c for c in window.tool_cards}
    assert set(cards) == {t["name"] for t in EIGHT} | {"Beerus — Live Boot"}
    sphinx = cards["Sphinx"]
    # A bundled member's card: a working Launch, and Ready on it.
    assert sphinx["button"].isEnabled()
    assert sphinx["button"].text() == "Launch"
    assert sphinx["status"].text() == "Ready."
    # Its own identity stripe: Sphinx's namesake palette shipped
    # canonical in its Windows Phase 3 (v0.3.0) — basalt black,
    # sandstone, bronze-gold — and the stripe is that bronze,
    # exactly the BRONZE of Sphinx's own theme module
    # (windows/src/sphinx_win/app/theme.py at Sphinx HEAD
    # c9ea4f0dfc1d). It is not the panel edge the card wore while
    # Sphinx was not in the bundle, and it is not Beerus's violet.
    assert IDENTITY_STRIPES["Sphinx"] == "#cf9a3e"
    assert stripe_for("Sphinx") == "#cf9a3e"
    assert "#cf9a3e" in sphinx["stripe"].styleSheet()
    assert PANEL_EDGE not in sphinx["stripe"].styleSheet()
    for name, color in IDENTITY_STRIPES.items():
        if name != "Sphinx":
            assert color not in sphinx["stripe"].styleSheet()
    summary = window.findChild(QLabel, "SummaryLine")
    assert summary.text() == (
        "8 tools in this bundle  ·  1 on its own bootable stick"
    )
    window.close()


def test_membership_check_output(tmp_path, capsys):
    _membership_bundle(tmp_path)
    assert run_check(tmp_path) == 0
    out = capsys.readouterr().out
    assert "- Sphinx v1.0.0: ready" in out
    assert "not_in_bundle" not in out
    assert "Beerus — Live Boot" in out and "separate" in out
