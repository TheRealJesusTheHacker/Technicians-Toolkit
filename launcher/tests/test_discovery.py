"""Discovery: manifest entries paired with honest on-disk states."""

from conftest import bundled_tool, make_ready_bundle, write_bundle
from toolkit_launcher.discovery import discover, locate_bundle_root
from toolkit_launcher.manifest import load_manifest


def test_ready_tool_found(tmp_path):
    _, states = make_ready_bundle(tmp_path, [bundled_tool()])
    assert states[0].state == "ready"
    assert states[0].entrypoint_path == tmp_path.resolve() / "FakeTool.exe"


def test_missing_entrypoint_is_missing_not_a_crash(tmp_path):
    write_bundle(tmp_path, tools=[bundled_tool()])
    states = discover(tmp_path, load_manifest(tmp_path))
    assert states[0].state == "missing"
    assert "Not found in this bundle" in states[0].detail


def test_nested_entrypoint_found(tmp_path):
    tool = bundled_tool(name="Charon", entrypoint="Charon/Charon.exe")
    _, states = make_ready_bundle(tmp_path, [tool])
    assert states[0].state == "ready"


def test_absent_and_linked_states_pass_through(tmp_path):
    write_bundle(
        tmp_path,
        tools=[bundled_tool()],
        linked=[{"name": "Beerus", "job": "Wipes.", "note": "Bootable stick."}],
        absent=[{"name": "Aegis", "job": "Protects.", "note": "Joins later."}],
    )
    (tmp_path / "FakeTool.exe").write_bytes(b"x")
    states = discover(tmp_path, load_manifest(tmp_path))
    by_name = {s.entry.name: s for s in states}
    assert by_name["Beerus"].state == "separate"
    assert by_name["Beerus"].detail == "Bootable stick."
    assert by_name["Aegis"].state == "not_in_bundle"
    assert by_name["Aegis"].detail == "Joins later."


def test_explicit_root_wins(tmp_path):
    assert locate_bundle_root(tmp_path) == tmp_path
    assert locate_bundle_root(str(tmp_path)) == tmp_path


def test_gutted_support_folder_is_missing_not_ready(tmp_path):
    """Regression pin (kit hunt, 2026-10-20): discovery used to
    check only the start file, so a one-folder tool whose
    _internal support folder was gutted (an interrupted unzip is
    the owner's real first-run scenario) still got a "Ready."
    card. A manifest may name files/folders the tool requires;
    without them the card says what is missing."""
    tool = bundled_tool(
        name="NitroCore",
        entrypoint="NitroCoreOptimizer.exe",
        requires=["_internal"],
    )
    write_bundle(tmp_path, tools=[tool])
    (tmp_path / "NitroCoreOptimizer.exe").write_bytes(b"fake tool")
    states = discover(tmp_path, load_manifest(tmp_path))
    assert states[0].state == "missing"
    assert "_internal" in states[0].detail


def test_required_support_folder_present_is_ready(tmp_path):
    tool = bundled_tool(
        name="NitroCore",
        entrypoint="NitroCoreOptimizer.exe",
        requires=["_internal"],
    )
    write_bundle(tmp_path, tools=[tool])
    (tmp_path / "NitroCoreOptimizer.exe").write_bytes(b"fake tool")
    internal = tmp_path / "_internal"
    internal.mkdir()
    (internal / "python311.dll").write_bytes(b"fake")
    states = discover(tmp_path, load_manifest(tmp_path))
    assert states[0].state == "ready"


def test_nested_required_folder_missing_names_it(tmp_path):
    tool = bundled_tool(
        name="Charon",
        entrypoint="Charon/Charon.exe",
        requires=["Charon/_internal"],
    )
    _, states = make_ready_bundle(tmp_path, [tool])
    # make_ready_bundle created only the entrypoint, not _internal.
    assert states[0].state == "missing"
    assert "Charon/_internal" in states[0].detail


def test_requires_pointing_outside_is_not_called_missing(tmp_path):
    """A requires entry escaping through a symlink was reported as
    "missing — re-download", which was never the truth: the file is
    there, it points outside the bundle. The card says so now."""
    import os

    root = tmp_path / "bundle"
    outside = tmp_path / "outside-dir"
    outside.mkdir()
    write_bundle(root, tools=[bundled_tool(requires=["ReqDir"])])
    (root / "FakeTool.exe").write_bytes(b"fake")
    os.symlink(outside, root / "ReqDir", target_is_directory=True)
    state = discover(root, load_manifest(root))[0]
    assert state.state == "missing"
    assert "points outside this bundle" in state.detail
    assert "is missing" not in state.detail
