"""Assembler guards: collisions are resolved on purpose, never by
overwrite — including the collisions only Windows can see.

Synthetic portable zips only; no downloads, no real tools.
"""

import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import assemble_bundle as ab  # noqa: E402


def make_zip(path: Path, members: dict) -> Path:
    with zipfile.ZipFile(path, "w") as zf:
        for name, data in members.items():
            zf.writestr(name, data)
    return path


def tool(name, entrypoint, **extra):
    entry = {
        "name": name,
        "entrypoint": entrypoint,
        "job": "Does its job.",
        "repo": f"TheRealJesusTheHacker/{name}",
        "version": "1.0.0",
        "tag": "v1.0.0",
        "artifact": f"{name}Portable.zip",
    }
    entry.update(extra)
    return entry


def test_exact_collision_still_aborts(tmp_path):
    first = make_zip(tmp_path / "a.zip", {"Tool.exe": b"a", "shared.dll": b"1"})
    second = make_zip(tmp_path / "b.zip", {"Other.exe": b"b", "shared.dll": b"2"})
    root = tmp_path / "bundle"
    root.mkdir()
    ab.extract_tool(tool("A", "Tool.exe"), first, root)
    with pytest.raises(ab.AssemblyError):
        ab.extract_tool(tool("B", "Other.exe"), second, root)


def test_case_only_collision_aborts(tmp_path):
    """Regression pin (kit hunt, 2026-10-20): two files whose names
    differ only by letter case extract side by side on Linux — the
    old assembler's whole collision guard was a case-sensitive
    exists() check — and then overwrite each other when the bundle
    is unzipped on Windows. Assembly itself must refuse them."""
    first = make_zip(tmp_path / "a.zip", {"Tool.exe": b"a", "Support.dll": b"1"})
    second = make_zip(tmp_path / "b.zip", {"Other.exe": b"b", "support.DLL": b"2"})
    root = tmp_path / "bundle"
    root.mkdir()
    ab.extract_tool(tool("A", "Tool.exe"), first, root)
    with pytest.raises(ab.AssemblyError) as exc:
        ab.extract_tool(tool("B", "Other.exe"), second, root)
    assert "differ only by letter case" in str(exc.value)


def test_case_only_collision_inside_one_zip_aborts(tmp_path):
    both = make_zip(
        tmp_path / "a.zip",
        {"Tool.exe": b"a", "Data.bin": b"1", "data.BIN": b"2"},
    )
    root = tmp_path / "bundle"
    root.mkdir()
    with pytest.raises(ab.AssemblyError):
        ab.extract_tool(tool("A", "Tool.exe"), both, root)


def test_folder_pin_and_readme_rename_still_work(tmp_path):
    z = make_zip(
        tmp_path / "b.zip",
        {"Beerus.exe": b"b", "README-PORTABLE.txt": b"readme", "_internal/x.dll": b"x"},
    )
    root = tmp_path / "bundle"
    root.mkdir()
    fragment = ab.extract_tool(
        tool("Beerus", "Beerus/Beerus.exe", folder="Beerus"), z, root
    )
    assert (root / "Beerus" / "Beerus.exe").is_file()
    assert (root / "Beerus" / "_internal" / "x.dll").is_file()
    assert (root / "README-PORTABLE-Beerus.txt").is_file()
    assert fragment["readme"] == "README-PORTABLE-Beerus.txt"


def test_reserved_bundle_names_refused(tmp_path):
    """The assembler writes the launcher file, MANIFEST.json and
    SHA256SUMS.txt itself, after layout. A tool file already using
    one of those names (any letter case) must stop assembly, not
    be overwritten."""
    root = tmp_path / "bundle"
    root.mkdir()
    (root / "manifest.JSON").write_bytes(b"tool file")
    with pytest.raises(ab.AssemblyError):
        ab.check_reserved_names(root, "TechniciansToolkit.exe")


def test_reserved_names_clear_when_absent(tmp_path):
    root = tmp_path / "bundle"
    root.mkdir()
    (root / "Tool.exe").write_bytes(b"x")
    ab.check_reserved_names(root, "TechniciansToolkit.exe")


def test_requires_passed_into_manifest_fragment(tmp_path):
    """The manifest's `requires` list (what discovery checks before
    calling a tool ready) comes from tools.json through the
    assembler, untouched."""
    z = make_zip(
        tmp_path / "n.zip",
        {"NitroCoreOptimizer.exe": b"n", "_internal/python311.dll": b"p"},
    )
    root = tmp_path / "bundle"
    root.mkdir()
    fragment = ab.extract_tool(
        tool("NitroCore", "NitroCoreOptimizer.exe", requires=["_internal"]),
        z,
        root,
    )
    assert fragment["requires"] == ["_internal"]


# --- Sweep-4 regression pins (2026-10-23) ---


def test_fetch_verified_never_trusts_a_cached_sums_file(tmp_path, monkeypatch):
    """Regression pin (fleet sweep #4, supply chain): the download
    folder kept a sums file per tool NAME, so a warm folder from
    an earlier assembly carried the earlier release's sums — and
    a stale artifact matching them passed verification under the
    new pin's label without any download at all. The sums must be
    fetched fresh from the pinned release every time, and only an
    artifact matching THOSE sums may pass."""
    import hashlib

    dl = tmp_path / "dl"
    dl.mkdir()
    stale = b"stale artifact from the previous pin"
    fresh = b"the pinned release's real artifact"
    (dl / "ArgusPortable.zip").write_bytes(stale)
    (dl / "Argus-SHA256SUMS.txt").write_text(
        f"{hashlib.sha256(stale).hexdigest()}  ArgusPortable.zip\n",
        encoding="utf-8",
    )
    served = []

    def fake_download(url, dest):
        served.append(url)
        if url.endswith("SHA256SUMS.txt"):
            dest.write_text(
                f"{hashlib.sha256(fresh).hexdigest()}  ArgusPortable.zip\n",
                encoding="utf-8",
            )
        else:
            dest.write_bytes(fresh)

    monkeypatch.setattr(ab, "download", fake_download)
    pinned = tool(
        "Argus", "Argus.exe", sums="SHA256SUMS.txt", tag="v1.2.8"
    )
    artifact, digest = ab.fetch_verified(pinned, dl)
    assert digest == hashlib.sha256(fresh).hexdigest()
    assert artifact.read_bytes() == fresh
    assert any("/v1.2.8/" in url for url in served)


def test_fetch_verified_stops_when_fresh_sums_cannot_be_matched(
    tmp_path, monkeypatch
):
    """With fresh sums in hand, an artifact that matches neither
    the cache nor a fresh download stops assembly — fail closed."""
    import hashlib

    dl = tmp_path / "dl"
    dl.mkdir()
    (dl / "ArgusPortable.zip").write_bytes(b"not the artifact")

    def fake_download(url, dest):
        if url.endswith("SHA256SUMS.txt"):
            dest.write_text(
                f"{hashlib.sha256(b'real').hexdigest()}  ArgusPortable.zip\n",
                encoding="utf-8",
            )
        else:
            dest.write_bytes(b"still not the artifact")

    monkeypatch.setattr(ab, "download", fake_download)
    pinned = tool(
        "Argus", "Argus.exe", sums="SHA256SUMS.txt", tag="v1.2.8"
    )
    with pytest.raises(ab.AssemblyError):
        ab.fetch_verified(pinned, dl)


# --- Sweep-3 regression pins (2026-10-21) ---


def _verify_args(tmp_path, zip_path):
    class A:
        pass

    a = A()
    a.config = str(Path(__file__).resolve().parents[1] / "tools.json")
    a.work_dir = str(tmp_path / "work")
    a.zip = str(zip_path)
    return a


def _bundle_zip(tmp_path, sums_text, files):
    import hashlib  # noqa: F401  (kept local; builders below use it)

    src = tmp_path / "src" / "TechniciansToolkit"
    src.mkdir(parents=True)
    for name, data in files.items():
        (src / name).write_bytes(data)
    (src / "SHA256SUMS.txt").write_text(sums_text, encoding="utf-8")
    z = tmp_path / "bundle.zip"
    with zipfile.ZipFile(z, "w") as zf:
        for p in sorted(src.rglob("*")):
            if p.is_file():
                zf.write(p, p.relative_to(tmp_path / "src").as_posix())
    return z


def test_verify_tolerates_blank_lines_in_sums(tmp_path):
    """A trailing blank line in SHA256SUMS.txt crashed verify with
    an uncaught ValueError instead of a verdict. Blank lines are
    skipped now and the bundle verifies."""
    import hashlib
    import json

    manifest = {
        "bundle": "TechniciansToolkit",
        "bundle_version": "1.0.0",
        "assembled": "2026-10-21",
        "launcher": {"file": "TechniciansToolkit.exe", "version": "1.0.5"},
        "tools": [
            {
                "name": "Tool",
                "job": "Does its job.",
                "repo": "TheRealJesusTheHacker/Tool",
                "version": "1.0.0",
                "entrypoint": "Tool.exe",
                "args": [],
            }
        ],
        "linked": [],
        "absent": [],
        "notes": [],
    }
    manifest_bytes = json.dumps(manifest).encode()
    sums = (
        f"{hashlib.sha256(b't').hexdigest()}  Tool.exe\n"
        f"{hashlib.sha256(manifest_bytes).hexdigest()}  MANIFEST.json\n\n"
    )
    z = _bundle_zip(
        tmp_path, sums, {"Tool.exe": b"t", "MANIFEST.json": manifest_bytes}
    )
    assert ab.verify(_verify_args(tmp_path, z)) == 0


def test_verify_malformed_sums_line_is_a_fail_not_a_traceback(tmp_path):
    z = _bundle_zip(tmp_path, "not-a-checksum-line\n", {"Tool.exe": b"t"})
    assert ab.verify(_verify_args(tmp_path, z)) == 1


def test_verify_sums_line_pointing_outside_is_a_fail(tmp_path):
    import hashlib

    digest = hashlib.sha256(b"t").hexdigest()
    z = _bundle_zip(tmp_path, f"{digest}  ../outside.txt\n", {"Tool.exe": b"t"})
    assert ab.verify(_verify_args(tmp_path, z)) == 1


# --- Sweep-5 regression pins (2026-10-24) ---


def test_verify_missing_sums_file_is_a_fail_not_a_traceback(tmp_path):
    """A bundle zip whose folder carries no SHA256SUMS.txt crashed
    verify with an uncaught FileNotFoundError. A damaged bundle is
    exactly the input this proof exists for, so — like a missing
    manifest or a malformed sums line — it gets a FAIL verdict."""
    z = tmp_path / "nosums.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("TechniciansToolkit/Tool.exe", b"t")
    assert ab.verify(_verify_args(tmp_path, z)) == 1


def test_verify_non_zip_is_a_fail_not_a_traceback(tmp_path):
    """A truncated or corrupt download is not a zip at all; opening it
    raised BadZipFile out of verify instead of returning a verdict."""
    z = tmp_path / "corrupt.zip"
    z.write_bytes(b"this is not a zip file, just a truncated download")
    assert ab.verify(_verify_args(tmp_path, z)) == 1


def test_extract_file_then_child_path_aborts_with_assembly_error(tmp_path):
    """One portable lays a file named Data; another needs Data/ as a
    folder. Laying out the second used to die with a raw
    FileExistsError from mkdir instead of the assembler's plain
    collision stop — assembly still stopped, but as a traceback."""
    first = make_zip(
        tmp_path / "a.zip", {"Tool.exe": b"a", "Data": b"a file, not a folder"}
    )
    second = make_zip(
        tmp_path / "b.zip", {"Other.exe": b"b", "Data/x.dll": b"x"}
    )
    root = tmp_path / "bundle"
    root.mkdir()
    ab.extract_tool(tool("A", "Tool.exe"), first, root)
    with pytest.raises(ab.AssemblyError):
        ab.extract_tool(tool("B", "Other.exe"), second, root)


def test_extract_child_then_file_within_one_zip_aborts(tmp_path):
    """The same collision inside a single portable: Data/x.dll first,
    then a file named Data. The second member's target already exists
    as a folder, which the collision guard already refused — this
    pins that both orders end in AssemblyError, never a traceback
    and never an overwrite."""
    z = make_zip(
        tmp_path / "a.zip",
        {"Tool.exe": b"t", "Data/x.dll": b"x", "Data": b"a file"},
    )
    root = tmp_path / "bundle"
    root.mkdir()
    with pytest.raises(ab.AssemblyError):
        ab.extract_tool(tool("A", "Tool.exe"), z, root)
