"""The launch seam: only manifest paths, only fixed args, no shell."""

import pytest

from conftest import bundled_tool, make_ready_bundle, write_bundle
from toolkit_launcher.discovery import discover
from toolkit_launcher.launching import LaunchError, Launcher
from toolkit_launcher.manifest import load_manifest


def test_launch_ready_tool_records_exact_argv(tmp_path, runner):
    _, states = make_ready_bundle(
        tmp_path, [bundled_tool(args=["--portable"])]
    )
    Launcher(tmp_path, runner=runner).launch(states[0])
    assert len(runner.calls) == 1
    call = runner.calls[0]
    assert call["argv"] == [str(tmp_path.resolve() / "FakeTool.exe"), "--portable"]
    assert call["cwd"] == str(tmp_path.resolve())


def test_env_placeholder_substituted_and_confined(tmp_path, runner):
    tool = bundled_tool(
        env={"FAKE_DATA_DIR": "{bundle}/FakeData"}, prepare_dirs=["FakeData"]
    )
    _, states = make_ready_bundle(tmp_path, [tool])
    Launcher(tmp_path, runner=runner).launch(states[0])
    env = runner.calls[0]["env"]
    assert env["FAKE_DATA_DIR"] == str(tmp_path.resolve() / "FakeData")
    assert (tmp_path / "FakeData").is_dir()


def test_env_escape_refused_and_nothing_started(tmp_path, runner):
    tool = bundled_tool(env={"FAKE_DIR": "{bundle}/../outside"})
    _, states = make_ready_bundle(tmp_path, [tool])
    with pytest.raises(LaunchError):
        Launcher(tmp_path, runner=runner).launch(states[0])
    assert runner.calls == []


def test_launch_missing_tool_refused_plainly(tmp_path, runner):
    write_bundle(tmp_path, tools=[bundled_tool()])
    state = discover(tmp_path, load_manifest(tmp_path))[0]
    assert state.state == "missing"
    with pytest.raises(LaunchError) as exc:
        Launcher(tmp_path, runner=runner).launch(state)
    assert "can't be started" in str(exc.value)
    assert runner.calls == []


def test_launch_not_in_bundle_refused(tmp_path, runner):
    write_bundle(
        tmp_path,
        absent=[{"name": "Aegis", "job": "Protects.", "note": "Joins later."}],
    )
    state = discover(tmp_path, load_manifest(tmp_path))[0]
    with pytest.raises(LaunchError):
        Launcher(tmp_path, runner=runner).launch(state)
    assert runner.calls == []


def test_runner_failure_becomes_a_plain_error(tmp_path):
    def boom(argv, cwd, env):
        raise OSError("no such file")

    _, states = make_ready_bundle(tmp_path, [bundled_tool()])
    with pytest.raises(LaunchError) as exc:
        Launcher(tmp_path, runner=boom).launch(states[0])
    assert "could not be started" in str(exc.value)


def test_default_runner_never_uses_a_shell(tmp_path):
    import inspect

    from toolkit_launcher import launching

    source = inspect.getsource(launching._default_runner)
    assert "shell=False" in source
    assert "shell=True" not in source
