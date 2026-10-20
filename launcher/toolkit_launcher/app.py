"""The launcher window — one screen over the whole kit.

Reads the bundle manifest, shows one card per tool in the kit
(bundled tools get a Launch button; tools not in this bundle and the
bootable Beerus stick get honest cards without one), plus the bundle
version and an About panel in plain language.

Every state is designed: a missing or damaged manifest gets a plain
problem panel, a tool whose files are missing gets a problem card,
a failed start explains itself on the card. Nothing on the window is
decorative — every control does what it says.

``--check`` runs the same discovery without any window and prints the
states — used by the build's own smoke tests and by support.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .discovery import check_bundle, discover, locate_bundle_root
from .launching import LaunchError, Launcher
from .manifest import ManifestError, load_manifest

ABOUT_TEXT = (
    "This folder is the Technician's Toolkit — Sentinel Safeguard's medic-kit "
    "line in portable form. Nothing here is installed: every tool runs from "
    "this folder, and you can take the folder with you on a USB stick.\n\n"
    "The kit is complete in this bundle: all seven tools of the line are "
    "here — Argus, NitroCore, VectorZip, Charon, Lazarus, Aegis, and the "
    "Beerus app — each in the portable form its maker released. The one "
    "form that cannot be a folder, Beerus's bootable Destruct Key Pro, is "
    "accounted for below and in the manifest.\n\n"
    "This launcher is only a front door. Every tool also runs on its own, "
    "straight from this folder, with the launcher closed — starting a tool "
    "here starts the same program you would start by hand.\n\n"
    "Beerus comes in two forms over one engine. Beerus Portable, the app "
    "in this bundle, securely wipes drives, files and folders, and free "
    "space on a machine that is already running, and keeps its certificates "
    "and reports in a certificates folder beside its own start file. The "
    "Destruct Key Pro, its other form, is a bootable USB stick of its own — "
    "a drive is wiped by booting from the stick, for machines that are off "
    "or being decommissioned whole. Carry both sticks.\n\n"
    "Every file in this bundle was checked against its maker's published "
    "checksums before the bundle was put together; MANIFEST.json lists what "
    "is inside and SHA256SUMS.txt lets you check the files again."
)


def _say(message: str) -> None:
    """Print, tolerating a windowed build's missing console.

    The frozen launcher ships windowed (no console window). Run with
    --check from a terminal it still reports through the exit code;
    this guard keeps a missing stdout from ever becoming a crash.
    """
    try:
        print(message)
    except Exception:
        pass


def run_check(root: Path) -> int:
    """Headless bundle check: print tool states, exit 0/2."""
    try:
        manifest, states = check_bundle(root)
    except ManifestError as exc:
        _say(f"BUNDLE PROBLEM: {exc}")
        return 2
    _say(
        f"{manifest.bundle} bundle v{manifest.bundle_version} "
        f"(assembled {manifest.assembled or 'date not recorded'}) at {root}"
    )
    for state in states:
        entry = state.entry
        version = f" v{entry.version}" if entry.version else ""
        _say(f"- {entry.name}{version}: {state.state} — {state.detail}")
    return 0


def _summary_line(manifest, states) -> str:
    bundled = sum(1 for s in states if s.entry.status == "bundled")
    absent = sum(1 for s in states if s.state == "not_in_bundle")
    linked = sum(1 for s in states if s.state == "separate")
    parts = [f"{bundled} tool{'s' if bundled != 1 else ''} in this bundle"]
    if absent:
        parts.append(f"{absent} still to come")
    if linked:
        parts.append(f"{linked} on its own bootable stick")
    return "  ·  ".join(parts)


def build_about_dialog(parent=None):
    """The About box: a real dialog with the bundle explained plainly."""
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout

    from .theme import STYLESHEET

    dialog = QDialog(parent)
    dialog.setWindowTitle("About this toolkit")
    dialog.setStyleSheet(STYLESHEET)
    dialog.resize(560, 400)
    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(22, 20, 22, 18)
    layout.setSpacing(10)
    heading = QLabel("About this toolkit")
    heading.setObjectName("ProblemTitle")
    layout.addWidget(heading)
    text = QLabel(ABOUT_TEXT)
    text.setObjectName("AboutText")
    text.setWordWrap(True)
    layout.addWidget(text, stretch=1)
    close = QPushButton("Close")
    close.setObjectName("AboutToggle")
    close.clicked.connect(dialog.accept)
    layout.addWidget(close, alignment=Qt.AlignmentFlag.AlignRight)
    # Size the dialog to its text: the About copy is the bundle's own
    # explanation and must never be clipped by a fixed height. The
    # label's height comes from its own font metrics at the dialog's
    # text width; the dialog then adjusts around it. Polishing first
    # is what makes the metrics the stylesheet's real ones.
    dialog.ensurePolished()
    text_width = dialog.width() - 44  # the layout's left + right margins
    needed = text.fontMetrics().boundingRect(
        0, 0, text_width, 100000, Qt.TextFlag.TextWordWrap, ABOUT_TEXT
    ).height()
    text.setFixedHeight(needed + 4)
    dialog.adjustSize()
    # adjustSize may narrow the dialog to its size hint; the label's
    # height was measured at the width set above, so restore it —
    # every other row is one line tall at either width.
    dialog.resize(560, dialog.height())
    return dialog


def build_window(root: Path, launcher: Launcher | None = None):
    """Build (but do not show) the main window for the bundle at root."""
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QFrame,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QPushButton,
        QScrollArea,
        QSpacerItem,
        QSizePolicy,
        QVBoxLayout,
        QWidget,
    )

    from .theme import GREEN, PANEL_EDGE, RED, STYLESHEET

    window = QMainWindow()
    window.setWindowTitle("Technician's Toolkit — Sentinel Safeguard")
    window.resize(700, 660)
    window.setMinimumSize(560, 480)
    window.setStyleSheet(STYLESHEET)
    window.tool_cards = []  # filled below when a manifest loads

    root_widget = QWidget()
    root_widget.setObjectName("Root")
    layout = QVBoxLayout(root_widget)
    layout.setContentsMargins(24, 20, 24, 16)
    layout.setSpacing(0)

    def gap(height):
        layout.addSpacerItem(
            QSpacerItem(0, height, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        )

    title = QLabel("Technician's Toolkit")
    title.setObjectName("Title")
    layout.addWidget(title)
    tagline = QLabel("Security For Everyone.")
    tagline.setObjectName("Tagline")
    layout.addWidget(tagline)
    gap(10)
    rule = QWidget()
    rule.setObjectName("Rule")
    rule.setFixedHeight(2)
    layout.addWidget(rule)
    gap(10)

    try:
        manifest = load_manifest(root)
        states = discover(root, manifest)
        error = None
    except ManifestError as exc:
        manifest, states, error = None, [], str(exc)

    if error is not None:
        panel = QFrame()
        panel.setObjectName("Panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(18, 16, 18, 16)
        panel_layout.setSpacing(6)
        heading = QLabel("This bundle looks incomplete")
        heading.setObjectName("ProblemTitle")
        panel_layout.addWidget(heading)
        problem = QLabel(error)
        problem.setObjectName("ProblemText")
        problem.setWordWrap(True)
        panel_layout.addWidget(problem)
        layout.addWidget(panel)
        layout.addStretch(1)
    elif not states:
        panel = QFrame()
        panel.setObjectName("Panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(18, 16, 18, 16)
        panel_layout.setSpacing(6)
        heading = QLabel("No tools are listed in this bundle")
        heading.setObjectName("ProblemTitle")
        panel_layout.addWidget(heading)
        problem = QLabel(
            "The bundle's manifest is there, but it does not list any tools. "
            "Re-download the bundle to replace it."
        )
        problem.setObjectName("ProblemText")
        problem.setWordWrap(True)
        panel_layout.addWidget(problem)
        layout.addWidget(panel)
        layout.addStretch(1)
    else:
        bundle_line = QLabel(
            f"Bundle version {manifest.bundle_version}"
            + (f" — put together {manifest.assembled}" if manifest.assembled else "")
            + f"  ·  Launcher v{__version__}"
        )
        bundle_line.setObjectName("BundleLine")
        layout.addWidget(bundle_line)
        summary = QLabel(_summary_line(manifest, states))
        summary.setObjectName("SummaryLine")
        layout.addWidget(summary)
        gap(14)

        launcher = launcher or Launcher(root)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        cards_widget = QWidget()
        cards_widget.setObjectName("Root")
        cards = QVBoxLayout(cards_widget)
        cards.setContentsMargins(0, 0, 0, 0)
        cards.setSpacing(10)

        accent_by_state = {"ready": GREEN, "missing": RED}
        for state in states:
            entry = state.entry
            card = QFrame()
            card.setObjectName("Card")
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(0, 0, 0, 0)
            card_layout.setSpacing(0)

            accent = QWidget()
            accent.setFixedWidth(4)
            accent.setStyleSheet(
                f"background: {accent_by_state.get(state.state, PANEL_EDGE)};"
                " border-top-left-radius: 8px; border-bottom-left-radius: 8px;"
            )
            card_layout.addWidget(accent)

            content = QVBoxLayout()
            content.setContentsMargins(14, 12, 14, 12)
            content.setSpacing(4)

            top_row = QHBoxLayout()
            top_row.setSpacing(8)
            name = QLabel(entry.name)
            name.setObjectName("ToolName")
            top_row.addWidget(name)
            top_row.addStretch(1)
            if entry.version:
                version = QLabel(f"v{entry.version}")
                version.setObjectName("ToolVersion")
                top_row.addWidget(version)
            content.addLayout(top_row)

            if entry.job:
                job = QLabel(entry.job)
                job.setObjectName("ToolJob")
                job.setWordWrap(True)
                content.addWidget(job)

            bottom_row = QHBoxLayout()
            bottom_row.setSpacing(10)
            status = QLabel("Ready." if state.state == "ready" else state.detail)
            status.setObjectName(
                {"ready": "ToolStatusReady", "missing": "ToolStatusProblem"}.get(
                    state.state, "ToolStatus"
                )
            )
            status.setWordWrap(True)
            bottom_row.addWidget(status, stretch=1)

            button = QPushButton("Launch")
            button.setObjectName("Launch")
            if state.state == "ready":
                def _on_launch(_checked=False, s=state, st=status):
                    try:
                        launcher.launch(s)
                        st.setStyleSheet(
                            f"color: {GREEN}; font-size: 12px; font-weight: 600;"
                        )
                        st.setText(f"{s.entry.name} started.")
                    except LaunchError as exc:
                        st.setStyleSheet(f"color: {RED}; font-size: 12px;")
                        st.setText(str(exc))

                button.clicked.connect(_on_launch)
            else:
                button.setEnabled(False)
                button.setText(
                    "Not in this bundle" if state.state != "separate" else "Bootable USB"
                )
            bottom_row.addWidget(button, alignment=Qt.AlignmentFlag.AlignRight)
            content.addLayout(bottom_row)

            card_layout.addLayout(content, stretch=1)
            cards.addWidget(card)
            window.tool_cards.append(
                {"entry": entry, "state": state, "button": button, "status": status}
            )
        cards.addStretch(1)
        scroll.setWidget(cards_widget)
        layout.addWidget(scroll, stretch=1)

    gap(12)
    toggle = QPushButton("About this toolkit")
    toggle.setObjectName("AboutToggle")
    toggle.clicked.connect(lambda: build_about_dialog(window).exec())
    layout.addWidget(toggle, alignment=Qt.AlignmentFlag.AlignLeft)
    gap(10)
    footer = QLabel("Sentinel Safeguard LLC  ·  Kansas City, Missouri")
    footer.setObjectName("Footer")
    layout.addWidget(footer)

    window.setCentralWidget(root_widget)
    return window


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="TechniciansToolkit",
        description="The Technician's Toolkit suite launcher.",
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Bundle folder to open (default: the folder this app sits in).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Print the bundle's tool states and exit (no window).",
    )
    args = parser.parse_args(argv)
    root = locate_bundle_root(args.root)

    if args.check:
        return run_check(root)

    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv[:1])
    app.setApplicationName("Technician's Toolkit")
    app.setApplicationVersion(__version__)
    window = build_window(root)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
