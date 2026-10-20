"""One tool, two forms: Beerus is bundled as an app AND linked as a
bootable stick in the same manifest. Both cards must render, the app
must be launchable through the seam, and the stick's card must stay
an honest no-button card — the two forms are told apart by name.
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

APP_ENTRY = bundled_tool(
    name="Beerus", entrypoint="Beerus/Beerus.exe", readme="README-PORTABLE-Beerus.txt"
)
STICK_ENTRY = {
    "name": "Beerus — Destruct Key Pro",
    "job": "Wipes drives completely, with proof it was done.",
    "note": "A bootable USB stick of its own — get it from the Beerus repo.",
}


@pytest.fixture(scope="module")
def qapp():
    yield QApplication.instance() or QApplication([])


def _two_forms_bundle(root):
    write_bundle(root, tools=[APP_ENTRY], linked=[STICK_ENTRY])
    exe = root / "Beerus" / "Beerus.exe"
    exe.parent.mkdir(parents=True, exist_ok=True)
    exe.write_bytes(b"fake tool")


def test_two_forms_load_and_pair_with_states(tmp_path):
    _two_forms_bundle(tmp_path)
    manifest = load_manifest(tmp_path)
    assert [t.status for t in manifest.tools] == ["bundled", "linked"]
    states = discover(tmp_path, manifest)
    by_name = {s.entry.name: s for s in states}
    assert by_name["Beerus"].state == "ready"
    assert by_name["Beerus"].entrypoint_path == tmp_path.resolve() / "Beerus" / "Beerus.exe"
    assert by_name["Beerus — Destruct Key Pro"].state == "separate"
    assert "bootable USB stick" in by_name["Beerus — Destruct Key Pro"].detail


def test_two_forms_window_cards(qapp, tmp_path):
    _two_forms_bundle(tmp_path)
    window = build_window(tmp_path)
    cards = {c["entry"].name: c for c in window.tool_cards}
    assert set(cards) == {"Beerus", "Beerus — Destruct Key Pro"}
    assert cards["Beerus"]["button"].isEnabled()
    assert cards["Beerus"]["button"].text() == "Launch"
    stick = cards["Beerus — Destruct Key Pro"]
    assert not stick["button"].isEnabled()
    assert stick["button"].text() == "Bootable USB"
    window.close()


def test_two_forms_app_launches_through_the_seam(qapp, tmp_path, runner):
    _two_forms_bundle(tmp_path)
    window = build_window(tmp_path, launcher=Launcher(tmp_path, runner=runner))
    card = next(c for c in window.tool_cards if c["entry"].name == "Beerus")
    card["button"].click()
    assert len(runner.calls) == 1
    assert runner.calls[0]["argv"][0].endswith(os.path.join("Beerus", "Beerus.exe"))
    window.close()


def test_two_forms_check_output_names_both(tmp_path, capsys):
    _two_forms_bundle(tmp_path)
    assert run_check(tmp_path) == 0
    out = capsys.readouterr().out
    assert "Beerus" in out and "ready" in out
    assert "Beerus — Destruct Key Pro" in out and "separate" in out


def test_about_text_tells_both_forms():
    assert "Beerus Portable, the app" in ABOUT_TEXT
    assert "Destruct Key Pro" in ABOUT_TEXT
    assert "certificates folder beside its own start file" in ABOUT_TEXT
    # The v0.1.0 claim — Beerus is not a folder in this bundle — is
    # false now that the app ships as files; it must not come back.
    assert "is not a folder in this bundle" not in ABOUT_TEXT
