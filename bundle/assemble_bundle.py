#!/usr/bin/env python3
"""Assemble a Technician's Toolkit bundle release.

The bundle is ASSEMBLED, never hand-copied:

1. Pull each tool's portable artifact from that tool's own GitHub
   release (pinned in tools.json).
2. Verify every artifact's SHA-256 against the SHA256SUMS file
   published with that release. A mismatch stops the build.
3. Lay out the ONE bundle folder: every tool's files together at one
   level (the owner's flat layout — the bundle adds no per-tool
   folders of its own; a tool keeps only the structure its own
   portable edition ships with). The known collisions are resolved
   openly, and the manifest records each: every portable carries a
   README-PORTABLE.txt, kept as README-PORTABLE-<Tool>.txt, contents
   unchanged; and a tool pinned with a "folder" in tools.json (Beerus
   — its _internal support folder shares NitroCore's name, and two
   cannot share one level) is laid out under that folder name, its
   files unchanged. Any OTHER overwrite aborts the build.
4. Add the launcher (a single file), write MANIFEST.json and the
   bundle's SHA256SUMS.txt.
5. Zip the folder and write the release-level SHA256SUMS.txt.

``verify`` re-opens a built zip in a fresh folder and proves it:
single top folder, every checksum line verifies, the launcher's own
manifest code loads the manifest and finds every bundled tool ready.

Standard library only. Usage:

    assemble_bundle.py assemble --launcher-file TechniciansToolkit.exe \
        [--download-dir downloads] [--work-dir assembly] [--out-dir dist]
    assemble_bundle.py verify --zip dist/TechniciansToolkit-vX.Y.Z.zip
"""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG = HERE / "tools.json"
README_NAME = "README-PORTABLE.txt"
USER_AGENT = "TechniciansToolkit-bundle-assembler"


class AssemblyError(Exception):
    """A plain description of why assembly stopped."""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request) as response, open(dest, "wb") as out:
        shutil.copyfileobj(response, out, 1 << 20)


def release_url(tool: dict, filename: str) -> str:
    return (
        f"https://github.com/{tool['repo']}/releases/download/"
        f"{tool['tag']}/{filename}"
    )


def fetch_verified(tool: dict, download_dir: Path) -> tuple[Path, str]:
    """Download a tool's artifact and prove it against its own sums."""
    artifact = download_dir / tool["artifact"]
    sums = download_dir / f"{tool['name']}-{tool['sums']}"
    if not sums.is_file():
        download(release_url(tool, tool["sums"]), sums)
    expected = None
    for line in sums.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) == 2 and parts[1].lstrip("*").strip() == tool["artifact"]:
            expected = parts[0].strip().lower()
            break
    if not expected:
        raise AssemblyError(
            f"{tool['name']}: its published {tool['sums']} does not list "
            f"{tool['artifact']} — refusing to build on an unverifiable artifact."
        )
    actual = sha256_file(artifact) if artifact.is_file() else None
    if actual != expected:
        download(release_url(tool, tool["artifact"]), artifact)
        actual = sha256_file(artifact)
    if actual != expected:
        raise AssemblyError(
            f"{tool['name']}: {tool['artifact']} hash mismatch — published "
            f"{expected}, downloaded {actual}. Assembly stopped."
        )
    return artifact, expected


def safe_member_name(name: str) -> str:
    """A zip member name, normalized; refuses anything that escapes."""
    name = name.replace("\\", "/")
    parts = [p for p in name.split("/") if p not in ("", ".")]
    if not parts or any(p == ".." for p in parts):
        raise AssemblyError(f"Unsafe path inside a portable zip: {name!r}")
    return "/".join(parts)


def extract_tool(tool: dict, artifact: Path, bundle_root: Path) -> dict:
    """Extract one portable zip into the flat bundle folder.

    Returns the manifest fragment for the tool. Aborts on any
    overwrite the documented answers don't explain: the portable
    readme's rename, and — for a tool pinned with a "folder" —
    laying its files out under that one folder name (Beerus: its
    _internal support folder shares NitroCore's name, and two
    different support folders cannot share one level; the tool's
    files are unchanged, only where they sit differs; the readme
    still lands at the bundle's level under its qualified name).
    """
    folder = tool.get("folder")
    if folder is not None and (
        not isinstance(folder, str)
        or folder != folder.strip()
        or safe_member_name(folder) != folder
        or "/" in folder
    ):
        raise AssemblyError(
            f"{tool['name']}: the 'folder' pin in tools.json must be one "
            f"plain folder name, not {folder!r}."
        )
    readme_final = None
    # Windows file names are case-insensitive: two bundle paths that
    # differ only by letter case are the SAME file when the bundle
    # is extracted on Windows, however distinct they look on the
    # Linux machine that may run this assembly. Track every path
    # already in the bundle — and every path this zip adds — by its
    # folded name, so a case-only twin aborts here instead of
    # silently overwriting its sibling on the owner's machine.
    seen = {}
    if bundle_root.is_dir():
        for existing in bundle_root.rglob("*"):
            if existing.is_file():
                rel = existing.relative_to(bundle_root).as_posix()
                seen[rel.lower()] = rel
    with zipfile.ZipFile(artifact) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            member = safe_member_name(info.filename)
            if member == README_NAME:
                member = f"README-PORTABLE-{tool['name']}.txt"
                readme_final = member
            elif folder:
                member = f"{folder}/{member}"
            target = bundle_root / member
            if target.exists() or member.lower() in seen:
                raise AssemblyError(
                    f"Collision while laying out {tool['name']}: '{member}' "
                    f"would overwrite '{seen.get(member.lower(), member)}' "
                    "in the bundle folder (Windows treats names that "
                    "differ only by letter case as the same file). "
                    "Assembly stopped — collisions are resolved on "
                    "purpose, never by overwrite."
                )
            seen[member.lower()] = member
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src, open(target, "wb") as dst:
                shutil.copyfileobj(src, dst, 1 << 20)
    entrypoint = bundle_root / tool["entrypoint"]
    if not entrypoint.is_file():
        raise AssemblyError(
            f"{tool['name']}: entrypoint {tool['entrypoint']} not found after "
            "extraction — the portable's layout changed; update tools.json."
        )
    fragment = {
        "name": tool["name"],
        "job": tool["job"],
        "repo": tool["repo"],
        "version": tool["version"],
        "artifact": tool["artifact"],
        "source_release": (
            f"https://github.com/{tool['repo']}/releases/tag/{tool['tag']}"
        ),
        "path": posixpath.dirname(tool["entrypoint"]) or ".",
        "entrypoint": tool["entrypoint"],
        "args": tool.get("args", []),
    }
    if readme_final:
        fragment["readme"] = readme_final
    if tool.get("env"):
        fragment["env"] = tool["env"]
    if tool.get("prepare_dirs"):
        fragment["prepare_dirs"] = tool["prepare_dirs"]
    if tool.get("requires"):
        fragment["requires"] = tool["requires"]
    return fragment


def check_reserved_names(bundle_root: Path, launcher_name: str) -> None:
    """Refuse if a tool's files already claim a bundle-owned name.

    The launcher file, MANIFEST.json, and SHA256SUMS.txt are written
    by the assembler itself, after every tool is laid out. A tool
    file already sitting at one of those names (in any letter case —
    Windows cannot tell them apart) would be silently overwritten;
    that is a collision like any other, so it stops assembly.
    """
    present = {}
    if bundle_root.is_dir():
        for existing in bundle_root.iterdir():
            if existing.is_file():
                present[existing.name.lower()] = existing.name
    for reserved in (launcher_name, "MANIFEST.json", "SHA256SUMS.txt"):
        if reserved.lower() in present:
            raise AssemblyError(
                f"A laid-out tool file already uses the bundle's own "
                f"name '{present[reserved.lower()]}' — the assembler "
                f"would have to overwrite it to add '{reserved}'. "
                "Assembly stopped."
            )


def write_checksums(bundle_root: Path) -> Path:
    sums_path = bundle_root / "SHA256SUMS.txt"
    lines = []
    for path in sorted(bundle_root.rglob("*")):
        if path.is_file() and path != sums_path:
            rel = path.relative_to(bundle_root).as_posix()
            lines.append(f"{sha256_file(path)}  {rel}")
    sums_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return sums_path


def assemble(args) -> Path:
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    # A "folder" pin is one tool's answer to a top-level name
    # collision; two tools claiming the same folder would merge
    # their files into it — refuse before anything is laid out.
    claimed = {}
    for tool in config["tools"]:
        folder = tool.get("folder")
        if folder:
            if folder in claimed:
                raise AssemblyError(
                    f"tools.json pins the folder '{folder}' for both "
                    f"{claimed[folder]} and {tool['name']} — one folder "
                    "can only hold one tool. Assembly stopped."
                )
            claimed[folder] = tool["name"]
    download_dir = Path(args.download_dir)
    download_dir.mkdir(parents=True, exist_ok=True)
    work = Path(args.work_dir)
    if work.exists():
        shutil.rmtree(work)
    bundle_root = work / "bundle" / config["folder"]
    bundle_root.mkdir(parents=True)

    fragments = []
    hashes = {}
    for tool in config["tools"]:
        artifact, digest = fetch_verified(tool, download_dir)
        hashes[tool["name"]] = digest
        fragment = extract_tool(tool, artifact, bundle_root)
        fragment["sha256"] = digest
        # Manifest field order follows docs/ROADMAP.md's spec.
        ordered = {
            k: fragment[k]
            for k in (
                "name", "job", "repo", "version", "artifact", "sha256",
                "source_release", "path", "readme", "entrypoint", "args",
                "env", "prepare_dirs", "requires",
            )
            if k in fragment
        }
        fragments.append(ordered)
        print(f"verified + laid out: {tool['name']} {tool['version']} ({digest[:12]}…)")

    launcher_src = Path(args.launcher_file)
    if not launcher_src.is_file():
        raise AssemblyError(f"Launcher file not found: {launcher_src}")
    launcher_name = args.launcher_name or config["launcher"]["file"]
    check_reserved_names(bundle_root, launcher_name)
    shutil.copyfile(launcher_src, bundle_root / launcher_name)
    print(f"launcher added: {launcher_name}")

    manifest = {
        "bundle": config["bundle"],
        "bundle_version": config["bundle_version"],
        "assembled": args.date,
        "launcher": config["launcher"],
        "tools": fragments,
        "linked": config.get("linked", []),
        "absent": config.get("absent", []),
        "notes": config.get("notes", []),
    }
    (bundle_root / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    sums = write_checksums(bundle_root)
    print(f"manifest + checksums written ({sum(1 for _ in sums.open())} files covered)")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / config["zip_name"]
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for path in sorted(bundle_root.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(work / "bundle").as_posix())
    release_sums = out_dir / "SHA256SUMS.txt"
    release_sums.write_text(
        f"{sha256_file(zip_path)}  {config['zip_name']}\n", encoding="utf-8"
    )
    print(f"bundle zipped: {zip_path} ({zip_path.stat().st_size:,} bytes)")
    print(f"release checksums: {release_sums}")
    return zip_path


def verify(args) -> int:
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    zip_path = Path(args.zip)
    scratch = Path(args.work_dir) / "verify"
    if scratch.exists():
        shutil.rmtree(scratch)
    scratch.mkdir(parents=True)
    with zipfile.ZipFile(zip_path) as zf:
        tops = {n.split("/")[0] for n in zf.namelist() if n.strip()}
        if tops != {config["folder"]}:
            print(f"FAIL: bundle must contain exactly one folder "
                  f"({config['folder']}); found {sorted(tops)}")
            return 1
        zf.extractall(scratch)
    root = scratch / config["folder"]

    # 1. Every checksum line verifies; no unlisted files.
    listed = {}
    problems = []
    for line in (root / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            problems.append(f"checksum line not written correctly: {line!r}")
            continue
        digest, rel = parts
        rel = rel.strip()
        if any(p == ".." for p in rel.replace("\\", "/").split("/")):
            problems.append(f"checksum line points outside the bundle folder: {rel}")
            continue
        listed[rel] = digest.strip()
    for rel, digest in listed.items():
        target = root / rel
        if not target.is_file():
            problems.append(f"missing file listed in SHA256SUMS.txt: {rel}")
        elif sha256_file(target) != digest:
            problems.append(f"checksum mismatch: {rel}")
    for path in root.rglob("*"):
        if path.is_file():
            rel = path.relative_to(root).as_posix()
            if rel != "SHA256SUMS.txt" and rel not in listed:
                problems.append(f"file not covered by SHA256SUMS.txt: {rel}")
    if problems:
        for p in problems[:20]:
            print("FAIL:", p)
        return 1
    print(f"checksums: all {len(listed)} files verify")

    # 2. The launcher's own manifest code finds every bundled tool ready.
    sys.path.insert(0, str(HERE.parent / "launcher"))
    from toolkit_launcher.discovery import check_bundle

    try:
        manifest, states = check_bundle(root)
    except Exception as exc:  # the launcher's plain-language error
        print(f"FAIL: launcher manifest check: {exc}")
        return 1
    not_ready = [s for s in states if s.entry.status == "bundled" and s.state != "ready"]
    if not_ready:
        for s in not_ready:
            print(f"FAIL: {s.entry.name} not ready: {s.detail}")
        return 1
    for s in states:
        print(f"  {s.entry.name}: {s.state}")
    print(f"verify OK: {zip_path.name} ({zip_path.stat().st_size:,} bytes)")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p_asm = sub.add_parser("assemble")
    p_asm.add_argument("--config", default=str(DEFAULT_CONFIG))
    p_asm.add_argument("--download-dir", default="downloads")
    p_asm.add_argument("--work-dir", default="assembly")
    p_asm.add_argument("--out-dir", default="dist")
    p_asm.add_argument("--launcher-file", required=True)
    p_asm.add_argument("--launcher-name", default=None)
    p_asm.add_argument("--date", default=None)

    p_ver = sub.add_parser("verify")
    p_ver.add_argument("--config", default=str(DEFAULT_CONFIG))
    p_ver.add_argument("--work-dir", default="assembly")
    p_ver.add_argument("--zip", required=True)

    args = parser.parse_args(argv)
    if args.command == "assemble":
        if not args.date:
            from datetime import date

            args.date = date.today().isoformat()
        try:
            assemble(args)
        except AssemblyError as exc:
            print(f"ASSEMBLY STOPPED: {exc}")
            return 1
        return 0
    return verify(args)


if __name__ == "__main__":
    raise SystemExit(main())
