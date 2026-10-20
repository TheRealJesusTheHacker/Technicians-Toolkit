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


# --- Working folder: a tool starts in its own folder, as by hand ---


def test_launch_folder_tool_uses_its_own_folder_as_cwd(tmp_path, runner):
    """Regression pin (kit hunt, 2026-10-20): the launcher used to
    start every tool with the bundle root as the working folder, so
    a tool living in a folder of its own (Charon, Aegis, Beerus)
    ran somewhere it does not run when started by hand. Its start
    file's own folder is the working folder now."""
    tool = bundled_tool(name="Charon", entrypoint="Charon/Charon.exe")
    _, states = make_ready_bundle(tmp_path, [tool])
    Launcher(tmp_path, runner=runner).launch(states[0])
    assert runner.calls[0]["cwd"] == str(tmp_path.resolve() / "Charon")


def test_launch_root_tool_uses_bundle_root_as_cwd(tmp_path, runner):
    _, states = make_ready_bundle(tmp_path, [bundled_tool()])
    Launcher(tmp_path, runner=runner).launch(states[0])
    assert runner.calls[0]["cwd"] == str(tmp_path.resolve())


# --- Elevation: a tool that asks Windows for administrator rights ---


def _os_error(winerror):
    err = OSError(f"windows error {winerror}")
    err.winerror = winerror
    return err


class _AliveProcess:
    def poll(self):
        return None


def test_elevation_refusal_retries_through_the_elevator(tmp_path):
    """Regression pin (kit hunt, 2026-10-20): NitroCore's program
    asks Windows for administrator permission (its manifest requests
    it), so the plain CreateProcess route refuses it with Windows
    error 740 — while a double-click asks the user and starts it.
    The launcher used to report that refusal as "files may be
    damaged"; it now retries through the ask-the-user route."""
    seen = {}

    def refuse(argv, cwd, env):
        raise _os_error(740)

    def elevate(argv, cwd, env):
        seen["argv"] = list(argv)
        seen["cwd"] = cwd
        return _AliveProcess()

    _, states = make_ready_bundle(
        tmp_path,
        [bundled_tool(name="NitroCore", entrypoint="NitroCoreOptimizer.exe")],
    )
    proc = Launcher(
        tmp_path, runner=refuse, elevator=elevate, settle_seconds=0.05
    ).launch(states[0])
    assert isinstance(proc, _AliveProcess)
    assert seen["argv"][0].endswith("NitroCoreOptimizer.exe")
    assert seen["cwd"] == str(tmp_path.resolve())


def test_elevation_declined_is_a_permission_message_not_damage(tmp_path):
    def refuse(argv, cwd, env):
        raise _os_error(740)

    def decline(argv, cwd, env):
        raise _os_error(1223)  # the user pressed No / Cancel

    _, states = make_ready_bundle(tmp_path, [bundled_tool()])
    with pytest.raises(LaunchError) as exc:
        Launcher(tmp_path, runner=refuse, elevator=decline).launch(states[0])
    message = str(exc.value)
    assert "administrator permission" in message
    assert "may be damaged" not in message


def test_access_denied_gets_its_own_message(tmp_path):
    def refuse(argv, cwd, env):
        raise _os_error(5)

    _, states = make_ready_bundle(tmp_path, [bundled_tool()])
    with pytest.raises(LaunchError) as exc:
        Launcher(tmp_path, runner=refuse).launch(states[0])
    assert "refused access" in str(exc.value)


def test_network_path_refusal_gets_its_own_message(tmp_path):
    def refuse(argv, cwd, env):
        raise _os_error(267)

    _, states = make_ready_bundle(tmp_path, [bundled_tool()])
    with pytest.raises(LaunchError) as exc:
        Launcher(tmp_path, runner=refuse).launch(states[0])
    assert "network path" in str(exc.value)


# --- Settling: "started" must mean the process survived a moment ---


class _ExitProcess:
    def __init__(self, code):
        self._code = code

    def poll(self):
        return self._code


def test_tool_that_dies_straight_away_is_not_reported_started(tmp_path):
    """Regression pin (kit hunt, 2026-10-20): a start used to count
    as started the moment Windows created the process — a tool
    whose support files are gutted dies straight away and was
    still announced as "started.". It is a failure now."""
    runner = lambda argv, cwd, env: _ExitProcess(3)  # noqa: E731
    _, states = make_ready_bundle(tmp_path, [bundled_tool()])
    with pytest.raises(LaunchError) as exc:
        Launcher(tmp_path, runner=runner, settle_seconds=0.2).launch(states[0])
    assert "closed straight away" in str(exc.value)


def test_tool_that_exits_cleanly_straight_away_counts_as_started(tmp_path):
    runner = lambda argv, cwd, env: _ExitProcess(0)  # noqa: E731
    _, states = make_ready_bundle(tmp_path, [bundled_tool()])
    proc = Launcher(tmp_path, runner=runner, settle_seconds=0.2).launch(states[0])
    assert isinstance(proc, _ExitProcess)


def test_tool_still_running_after_the_moment_counts_as_started(tmp_path):
    runner = lambda argv, cwd, env: _AliveProcess()  # noqa: E731
    _, states = make_ready_bundle(tmp_path, [bundled_tool()])
    proc = Launcher(tmp_path, runner=runner, settle_seconds=0.05).launch(states[0])
    assert isinstance(proc, _AliveProcess)
