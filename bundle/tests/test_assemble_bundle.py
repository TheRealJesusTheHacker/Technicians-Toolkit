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
