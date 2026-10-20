"""Shared fixtures: synthetic bundle trees and a recording runner.

No real tool is ever started in these tests. Entrypoints are empty
files (their existence is what discovery checks), and launching goes
through a fake runner that records what it was asked to start.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from toolkit_launcher.manifest import load_manifest  # noqa: E402
from toolkit_launcher.discovery import discover  # noqa: E402


def write_bundle(root: Path, tools=None, linked=None, absent=None, raw=None):
    """Create a synthetic bundle folder at root; returns the manifest dict."""
    root.mkdir(parents=True, exist_ok=True)
    manifest = raw if raw is not None else {
        "bundle": "TechniciansToolkit",
        "bundle_version": "0.1.0",
        "assembled": "2026-10-20",
        "launcher": {"file": "TechniciansToolkit.exe", "version": "0.1.0"},
        "tools": tools or [],
        "linked": linked or [],
        "absent": absent or [],
        "notes": [],
    }
    (root / "MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
    return manifest


def bundled_tool(name="FakeTool", entrypoint="FakeTool.exe", **extra):
    entry = {
        "name": name,
        "job": f"{name} does its one job.",
        "repo": "TheRealJesusTheHacker/FakeTool",
        "version": "1.0.0",
        "artifact": f"{name}Portable.zip",
        "sha256": "0" * 64,
        "source_release": "https://example.invalid/releases/v1.0.0",
        "readme": f"README-PORTABLE-{name}.txt",
        "entrypoint": entrypoint,
        "args": [],
    }
    entry.update(extra)
    return entry


def make_ready_bundle(root: Path, tools):
    """Write a bundle and create the entrypoint files it names."""
    write_bundle(root, tools=tools)
    for tool in tools:
        ep = root / tool["entrypoint"]
        ep.parent.mkdir(parents=True, exist_ok=True)
        ep.write_bytes(b"fake tool")
    manifest = load_manifest(root)
    return manifest, discover(root, manifest)


class RecordingRunner:
    def __init__(self):
        self.calls = []

    def __call__(self, argv, cwd, env):
        self.calls.append({"argv": list(argv), "cwd": cwd, "env": dict(env)})
        return object()


@pytest.fixture
def runner():
    return RecordingRunner()
