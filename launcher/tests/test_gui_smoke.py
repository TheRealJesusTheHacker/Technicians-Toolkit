"""Offscreen GUI smoke: the window builds from a synthetic bundle,
cards reflect states, and Launch reaches the injected seam."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QLabel  # noqa: E402

from conftest import bundled_tool, write_bundle  # noqa: E402
from toolkit_launcher.app import build_window, run_check  # noqa: E402
from toolkit_launcher.launching import Launcher  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def _mixed_bundle(root):
    write_bundle(
        root,
        tools=[
            bundled_tool(name="Ready", entrypoint="Ready.exe"),
            bundled_tool(name="Gone", entrypoint="Gone.exe"),
        ],
        linked=[{"name": "Beerus", "job": "Wipes drives.", "note": "Bootable stick."}],
        absent=[{"name": "Aegis", "job": "Protects files.", "note": "Joins later."}],
    )
    (root / "Ready.exe").write_bytes(b"fake")


def test_window_builds_with_honest_cards(qapp, tmp_path):
    _mixed_bundle(tmp_path)
    window = build_window(tmp_path)
    cards = {c["entry"].name: c for c in window.tool_cards}
    assert set(cards) == {"Ready", "Gone", "Beerus", "Aegis"}
    assert cards["Ready"]["button"].isEnabled()
    assert not cards["Gone"]["button"].isEnabled()
    assert not cards["Beerus"]["button"].isEnabled()
    assert not cards["Aegis"]["button"].isEnabled()
    assert cards["Gone"]["state"].state == "missing"
    assert cards["Aegis"]["state"].state == "not_in_bundle"
    window.close()


def test_launch_button_reaches_the_seam(qapp, tmp_path, runner):
    _mixed_bundle(tmp_path)
    window = build_window(tmp_path, launcher=Launcher(tmp_path, runner=runner))
    card = next(c for c in window.tool_cards if c["entry"].name == "Ready")
    card["button"].click()
    assert len(runner.calls) == 1
    assert runner.calls[0]["argv"][0].endswith("Ready.exe")
    assert "started" in card["status"].text()
    window.close()


def test_window_without_manifest_is_a_designed_state(qapp, tmp_path):
    window = build_window(tmp_path)  # no MANIFEST.json written
    assert window.tool_cards == []
    window.close()


def test_check_mode_reports_states(tmp_path, capsys):
    _mixed_bundle(tmp_path)
    assert run_check(tmp_path) == 0
    out = capsys.readouterr().out
    assert "Ready" in out and "ready" in out
    assert "Aegis" in out and "not_in_bundle" in out


def test_check_mode_without_manifest_exits_2(tmp_path, capsys):
    assert run_check(tmp_path) == 2
    assert "BUNDLE PROBLEM" in capsys.readouterr().out


# --- The in-window file check (M3, launcher 1.0.5) ---


def _teardown(qapp, *widgets):
    """Deterministic Qt teardown: a window or dialog dropped while
    still registered can make the test process die at interpreter
    shutdown even after a green summary (the fleet has hit this
    exact flake before). Close, delete, and pump the event loop."""
    for w in widgets:
        w.close()
        w.deleteLater()
    qapp.processEvents()


def test_window_carries_a_working_check_button(qapp, tmp_path):
    _mixed_bundle(tmp_path)
    window = build_window(tmp_path)
    assert window.integrity_button is not None
    assert window.integrity_button.isEnabled()
    assert window.integrity_button.text() == "Check bundle files"
    _teardown(qapp, window)


def test_integrity_dialog_says_what_the_report_says(qapp, tmp_path):
    from toolkit_launcher.app import build_integrity_dialog
    from toolkit_launcher.integrity import IntegrityReport

    good = IntegrityReport(checked=1668, problems=[], sums_found=True, extra=3)
    dialog = build_integrity_dialog(None, good)
    texts = [w.text() for w in dialog.findChildren(QLabel)]
    assert any("Every file checks out" in t for t in texts)
    assert any("1668" in t and "3 other files" in t for t in texts)
    _teardown(qapp, dialog)

    bad = IntegrityReport(
        checked=10, problems=["A file has changed: Tool.exe"], sums_found=True
    )
    dialog = build_integrity_dialog(None, bad)
    texts = [w.text() for w in dialog.findChildren(QLabel)]
    assert any("do not check out" in t for t in texts)
    assert any("Tool.exe" in t for t in texts)
    _teardown(qapp, dialog)
