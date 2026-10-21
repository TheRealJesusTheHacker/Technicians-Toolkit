"""Finding the bundle folder and reporting each tool's state.

The bundle folder is the single folder the bundle zip opens into:
MANIFEST.json, the tools' files, and this launcher all sit in it
together. Discovery reads the manifest and checks, for every bundled
tool, that the file the manifest says to start is really there.
Nothing is executed here — discovery only looks.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from .manifest import MANIFEST_NAME, BundleManifest, ToolEntry, load_manifest, resolve_confined


@dataclass
class ToolState:
    entry: ToolEntry
    state: str  # "ready" | "missing" | "not_in_bundle" | "separate"
    detail: str  # plain-language status line for the card
    entrypoint_path: Path | None = None


def locate_bundle_root(explicit: str | Path | None = None) -> Path:
    """Where the bundle folder is.

    An explicit root wins (tests, the --check flag). Otherwise the
    launcher's own folder: the bundled executable sits in the bundle
    folder, and in development the current folder stands in.
    """
    if explicit:
        return Path(explicit)
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path.cwd()


def discover(root: Path, manifest: BundleManifest) -> list[ToolState]:
    """Pair every manifest entry with its on-disk state."""
    root = Path(root)
    states: list[ToolState] = []
    for entry in manifest.tools:
        if entry.status == "linked":
            states.append(
                ToolState(
                    entry,
                    "separate",
                    entry.note
                    or "This tool lives on its own medium — it is not a folder in this bundle.",
                )
            )
        elif entry.status == "absent":
            states.append(
                ToolState(
                    entry,
                    "not_in_bundle",
                    entry.note or "Not in this bundle yet.",
                )
            )
        else:
            try:
                path = resolve_confined(root, entry.entrypoint)
            except Exception:
                states.append(
                    ToolState(entry, "missing", "Its start file points outside this bundle.")
                )
                continue
            missing_required = None
            escaped_required = None
            if path.is_file():
                for rel in entry.requires:
                    try:
                        needed = resolve_confined(root, rel)
                    except Exception:
                        escaped_required = rel
                        break
                    if not needed.exists():
                        missing_required = rel
                        break
            if path.is_file() and escaped_required is not None:
                states.append(
                    ToolState(
                        entry,
                        "missing",
                        f"Its start file is here, but '{escaped_required}' — "
                        "part of the tool — points outside this bundle. "
                        "Re-download the bundle to replace it.",
                    )
                )
            elif path.is_file() and missing_required is None:
                states.append(
                    ToolState(entry, "ready", "Ready.", entrypoint_path=path)
                )
            elif path.is_file():
                states.append(
                    ToolState(
                        entry,
                        "missing",
                        f"Its start file is here, but '{missing_required}' — "
                        "part of the tool — is missing. "
                        "Re-download the bundle to replace it.",
                    )
                )
            else:
                states.append(
                    ToolState(
                        entry,
                        "missing",
                        "Not found in this bundle — its files are missing. "
                        "Re-download the bundle to replace them.",
                    )
                )
    return states


def check_bundle(root: Path) -> tuple[BundleManifest, list[ToolState]]:
    """Manifest + states for the bundle at ``root`` (headless use)."""
    manifest = load_manifest(root)
    return manifest, discover(root, manifest)


def manifest_present(root: Path) -> bool:
    return (Path(root) / MANIFEST_NAME).is_file()
