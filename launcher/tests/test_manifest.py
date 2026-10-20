"""Manifest loading and validation: designed states, never tracebacks."""

import pytest

from conftest import bundled_tool, write_bundle
from toolkit_launcher.manifest import ManifestError, load_manifest


def test_valid_manifest_loads(tmp_path):
    write_bundle(
        tmp_path,
        tools=[bundled_tool()],
        linked=[{"name": "Beerus", "job": "Wipes drives.", "note": "Bootable."}],
        absent=[{"name": "Lazarus", "job": "Restores files.", "note": "Not yet."}],
    )
    manifest = load_manifest(tmp_path)
    assert manifest.bundle == "TechniciansToolkit"
    assert manifest.bundle_version == "0.1.0"
    assert manifest.launcher_version == "0.1.0"
    assert [t.status for t in manifest.tools] == ["bundled", "linked", "absent"]


def test_missing_manifest_is_a_designed_error(tmp_path):
    with pytest.raises(ManifestError) as exc:
        load_manifest(tmp_path)
    assert "MANIFEST.json is missing" in str(exc.value)


def test_corrupt_manifest_is_a_designed_error(tmp_path):
    (tmp_path / "MANIFEST.json").write_text("{not json", encoding="utf-8")
    with pytest.raises(ManifestError) as exc:
        load_manifest(tmp_path)
    assert "could not be read" in str(exc.value)


def test_manifest_without_bundle_identity_refused(tmp_path):
    write_bundle(tmp_path, raw={"tools": []})
    with pytest.raises(ManifestError):
        load_manifest(tmp_path)


@pytest.mark.parametrize(
    "bad_entrypoint",
    ["../evil.exe", "C:/evil.exe", "C:\\evil.exe", "/abs/evil.exe", "a/../../evil.exe", ""],
)
def test_entrypoint_escapes_refused(tmp_path, bad_entrypoint):
    write_bundle(tmp_path, tools=[bundled_tool(entrypoint=bad_entrypoint)])
    with pytest.raises(ManifestError):
        load_manifest(tmp_path)


def test_args_must_be_a_plain_string_list(tmp_path):
    write_bundle(tmp_path, tools=[bundled_tool(args="--run")])
    with pytest.raises(ManifestError):
        load_manifest(tmp_path)


def test_fixed_args_accepted(tmp_path):
    write_bundle(tmp_path, tools=[bundled_tool(args=["--portable"])])
    manifest = load_manifest(tmp_path)
    assert manifest.tools[0].args == ["--portable"]


def test_env_name_must_be_a_plain_name(tmp_path):
    write_bundle(tmp_path, tools=[bundled_tool(env={"BAD-NAME": "x"})])
    with pytest.raises(ManifestError):
        load_manifest(tmp_path)


def test_env_placeholder_must_be_a_prefix(tmp_path):
    write_bundle(tmp_path, tools=[bundled_tool(env={"X_DIR": "data/{bundle}"})])
    with pytest.raises(ManifestError):
        load_manifest(tmp_path)


def test_env_and_prepare_dirs_accepted(tmp_path):
    write_bundle(
        tmp_path,
        tools=[
            bundled_tool(
                env={"X_DATA_DIR": "{bundle}/XData"},
                prepare_dirs=["XData"],
            )
        ],
    )
    entry = load_manifest(tmp_path).tools[0]
    assert entry.env == {"X_DATA_DIR": "{bundle}/XData"}
    assert entry.prepare_dirs == ["XData"]


def test_prepare_dirs_escape_refused(tmp_path):
    write_bundle(tmp_path, tools=[bundled_tool(prepare_dirs=["../outside"])])
    with pytest.raises(ManifestError):
        load_manifest(tmp_path)
