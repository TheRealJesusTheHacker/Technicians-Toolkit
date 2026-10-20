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
