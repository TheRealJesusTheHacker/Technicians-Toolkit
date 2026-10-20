"""Reading and validating MANIFEST.json — the bundle's source of truth.

The manifest is DATA. It is parsed with ``json`` and validated field
by field; nothing in it is ever executed, evaluated, or handed to a
shell. Every path it names is bundle-relative and must resolve
inside the bundle folder — a manifest that points outside the folder
is refused, in plain language.

Manifest shape (see docs/ROADMAP.md for the full spec):

    {
      "bundle": "TechniciansToolkit",
      "bundle_version": "0.1.0",
      "assembled": "2026-10-20",
      "launcher": {"file": "TechniciansToolkit.exe", "version": "0.1.0"},
      "tools":  [ {bundled tool entries} ],
      "linked": [ {tools carried by link, e.g. Beerus} ],
      "absent": [ {kit tools not in this bundle yet} ],
      "notes":  [ "bundle-level notes" ]
    }

A bundled tool entry carries: name, job (one plain sentence), repo,
version, artifact, sha256, source_release, readme, entrypoint,
args (a fixed list, possibly empty), and optionally env (fixed
environment variables; a value may start with the "{bundle}"
placeholder for the bundle folder's own path), prepare_dirs
(bundle-relative folders to create before starting the tool — the
portable Argus data folder is the first user of this), and requires
(bundle-relative files or folders that must also be present for
the tool to count as ready — a one-folder tool's "_internal"
support folder is the first user of this: the start file alone,
with its support folder gone, is not a working tool and the card
must not call it ready).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

MANIFEST_NAME = "MANIFEST.json"
BUNDLE_PLACEHOLDER = "{bundle}"
_ENV_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class ManifestError(Exception):
    """A problem with the bundle manifest, in plain language."""


@dataclass
class ToolEntry:
    name: str
    job: str
    status: str  # "bundled" | "linked" | "absent"
    version: str = ""
    repo: str = ""
    note: str = ""
    entrypoint: str = ""
    args: list = field(default_factory=list)
    env: dict = field(default_factory=dict)
    prepare_dirs: list = field(default_factory=list)
    requires: list = field(default_factory=list)


@dataclass
class BundleManifest:
    bundle: str
    bundle_version: str
    assembled: str
    launcher_version: str
    tools: list  # list[ToolEntry], bundled first, then linked, then absent
    notes: list  # list[str]
    source: Path


def _plain(text: str) -> str:
    return " ".join(str(text).split())


def _check_relative_path(value, what: str) -> str:
    """Validate a bundle-relative path from the manifest.

    Forward slashes only, never absolute, never escaping the folder.
    """
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"The manifest's {what} is missing or empty.")
    value = value.strip()
    if value.startswith("/") or value.startswith("~"):
        raise ManifestError(
            f"The manifest's {what} ('{value}') is not a plain bundle-relative path."
        )
    if "\\" in value or ":" in value:
        raise ManifestError(
            f"The manifest's {what} ('{value}') is not a plain bundle-relative path."
        )
    parts = [p for p in value.split("/") if p not in ("", ".")]
    if not parts or any(p == ".." for p in parts):
        raise ManifestError(
            f"The manifest's {what} ('{value}') points outside the bundle folder."
        )
    return "/".join(parts)


def resolve_confined(root: Path, relative: str) -> Path:
    """Resolve a manifest path inside the bundle folder, or refuse."""
    root_resolved = Path(root).resolve()
    candidate = (root_resolved / relative).resolve()
    if candidate != root_resolved and root_resolved not in candidate.parents:
        raise ManifestError(
            f"The path '{relative}' points outside the bundle folder."
        )
    return candidate


def _parse_tool(raw, status: str) -> ToolEntry:
    if not isinstance(raw, dict):
        raise ManifestError("A tool entry in the manifest is not written correctly.")
    name = _plain(raw.get("name", ""))
    job = _plain(raw.get("job", ""))
    if not name:
        raise ManifestError("A tool entry in the manifest has no name.")
    entry = ToolEntry(
        name=name,
        job=job,
        status=status,
        version=_plain(raw.get("version", "")),
        repo=_plain(raw.get("repo", "")),
        note=_plain(raw.get("note", "")),
    )
    if status == "bundled":
        entry.entrypoint = _check_relative_path(
            raw.get("entrypoint", ""), f"start file for {name}"
        )
        args = raw.get("args", [])
        if not isinstance(args, list) or any(
            not isinstance(a, str) or len(a) > 128 or "\x00" in a or "\n" in a
            for a in args
        ):
            raise ManifestError(
                f"The manifest's start options for {name} are not written correctly."
            )
        entry.args = list(args)
        env = raw.get("env", {})
        if not isinstance(env, dict) or len(env) > 32:
            raise ManifestError(
                f"The manifest's environment settings for {name} are not written correctly."
            )
        for key, value in env.items():
            if not _ENV_NAME.match(str(key)):
                raise ManifestError(
                    f"The manifest has an environment setting with a bad name ('{key}')."
                )
            if (
                not isinstance(value, str)
                or len(value) > 512
                or "\x00" in value
                or "\n" in value
                or value.count(BUNDLE_PLACEHOLDER) > 1
                or (BUNDLE_PLACEHOLDER in value and not value.startswith(BUNDLE_PLACEHOLDER))
            ):
                raise ManifestError(
                    f"The manifest's environment setting '{key}' for {name} "
                    "is not written correctly."
                )
            entry.env[str(key)] = value
        prepare = raw.get("prepare_dirs", [])
        if not isinstance(prepare, list):
            raise ManifestError(
                f"The manifest's folder list for {name} is not written correctly."
            )
        entry.prepare_dirs = [
            _check_relative_path(p, f"folder to prepare for {name}") for p in prepare
        ]
        requires = raw.get("requires", [])
        if not isinstance(requires, list):
            raise ManifestError(
                f"The manifest's required-files list for {name} is not written correctly."
            )
        entry.requires = [
            _check_relative_path(p, f"required file or folder for {name}")
            for p in requires
        ]
    return entry


def load_manifest(root: Path) -> BundleManifest:
    """Load and validate the manifest in the bundle folder at ``root``.

    Raises ManifestError with a plain-language message on any problem —
    missing file, unreadable JSON, or a field that fails validation.
    """
    root = Path(root)
    path = root / MANIFEST_NAME
    if not path.is_file():
        raise ManifestError(
            "This folder does not look like a Technician's Toolkit bundle: "
            f"{MANIFEST_NAME} is missing from it."
        )
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        raise ManifestError(
            f"The bundle's {MANIFEST_NAME} could not be read — it may be damaged. "
            "Re-download the bundle and try again."
        ) from None
    if not isinstance(raw, dict):
        raise ManifestError(f"The bundle's {MANIFEST_NAME} is not written correctly.")
    bundle = _plain(raw.get("bundle", ""))
    version = _plain(raw.get("bundle_version", ""))
    if not bundle or not version:
        raise ManifestError(
            f"The bundle's {MANIFEST_NAME} does not say which bundle this is."
        )
    launcher = raw.get("launcher", {})
    launcher_version = ""
    if isinstance(launcher, dict):
        launcher_version = _plain(launcher.get("version", ""))
    tools = []
    for status, key in (("bundled", "tools"), ("linked", "linked"), ("absent", "absent")):
        entries = raw.get(key, [])
        if not isinstance(entries, list):
            raise ManifestError(f"The manifest's '{key}' list is not written correctly.")
        tools.extend(_parse_tool(e, status) for e in entries)
    notes = raw.get("notes", [])
    if not isinstance(notes, list):
        notes = []
    return BundleManifest(
        bundle=bundle,
        bundle_version=version,
        assembled=_plain(raw.get("assembled", "")),
        launcher_version=launcher_version,
        tools=tools,
        notes=[_plain(n) for n in notes if isinstance(n, str)],
        source=path,
    )
