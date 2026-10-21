"""Checking the bundle's files against its own SHA256SUMS.txt.

The roadmap's M3 growth item, landed: on-demand bundle hash
verification inside the window. The bundle ships a SHA256SUMS.txt
covering every file in the folder; this module re-reads it and
proves each listed file still hashes to what the bundle recorded.
It is the assembler's ``verify`` proof offered to the technician
in the field — a stick that has travelled, been copied, or sat in
a hot truck can be checked where it stands. One difference from
the build-time proof, on purpose: a working bundle folder gains
files of its own (Argus's data folder, Beerus's certificates,
Lazarus's stores), so unlisted files are counted and reported as
information, never as damage — the check's verdict is about the
files the bundle shipped.

Read-only and standard library only: nothing here writes, starts,
or deletes anything. A file that cannot be read is a problem to
report, never a crash. Listed paths are confined to the bundle
folder the same way manifest paths are — a sums line that points
outside the folder is itself a problem, and is never followed.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

SUMS_NAME = "SHA256SUMS.txt"


@dataclass
class IntegrityReport:
    checked: int = 0  # files whose hash matched the sums file
    problems: list = field(default_factory=list)  # plain-language lines
    sums_found: bool = False
    extra: int = 0  # unlisted files present (tool data, job records)

    @property
    def ok(self) -> bool:
        return self.sums_found and not self.problems


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def verify_bundle_files(root: Path) -> IntegrityReport:
    """Hash every file SHA256SUMS.txt lists in the bundle at root."""
    root = Path(root)
    report = IntegrityReport()
    sums_path = root / SUMS_NAME
    if not sums_path.is_file():
        report.problems.append(
            f"{SUMS_NAME} is missing from this folder, so there is "
            "nothing to check the files against. Re-download the bundle."
        )
        return report
    report.sums_found = True
    try:
        lines = sums_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        report.problems.append(
            f"{SUMS_NAME} could not be read — it may be damaged. "
            "Re-download the bundle."
        )
        return report

    root_resolved = root.resolve()
    listed: dict[str, str] = {}
    for line in lines:
        if not line.strip():
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            report.problems.append(
                f"A line in {SUMS_NAME} is not written correctly: {line.strip()!r}"
            )
            continue
        digest, rel = parts[0].strip().lower(), parts[1].strip().lstrip("*").strip()
        if not rel or any(p == ".." for p in rel.replace("\\", "/").split("/")):
            report.problems.append(
                f"A line in {SUMS_NAME} points outside this folder: {rel!r}"
            )
            continue
        listed[rel] = digest

    for rel, digest in listed.items():
        target = root_resolved / rel
        resolved = target.resolve()
        if resolved != root_resolved and root_resolved not in resolved.parents:
            report.problems.append(f"A listed file points outside this folder: {rel}")
            continue
        if not target.is_file():
            report.problems.append(f"A file listed in {SUMS_NAME} is missing: {rel}")
            continue
        try:
            actual = _sha256_file(target)
        except OSError:
            report.problems.append(f"A file could not be read for checking: {rel}")
            continue
        if actual != digest:
            report.problems.append(
                f"A file has changed since the bundle was put together: {rel}"
            )
            continue
        report.checked += 1

    for path in sorted(root.rglob("*")):
        if path.is_file():
            rel = path.relative_to(root).as_posix()
            if rel != SUMS_NAME and rel not in listed:
                report.extra += 1
    return report
