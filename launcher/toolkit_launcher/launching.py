"""Starting a tool from the bundle — the launcher's one sharp edge.

The launcher starts programs, so this module is deliberately small
and strict:

- The only things ever started are bundled tools whose manifest
  entrypoint resolves to a real file inside the bundle folder.
- Arguments are exactly the fixed list the manifest carries for that
  tool. There is no shell, no command string, no user-typed input —
  a list of arguments goes to the operating system as a list.
- Environment additions are exactly the manifest's fixed map for that
  tool; the "{bundle}" placeholder is replaced with the bundle
  folder's path, and a value that resolves to a path must stay inside
  the bundle folder.
- Folders the manifest says to prepare (a tool's data folder) are
  created inside the bundle folder only, before the start.

A refusal is a LaunchError with a plain-language message — never a
traceback, never a silent no-op.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from .discovery import ToolState
from .manifest import BUNDLE_PLACEHOLDER, resolve_confined


class LaunchError(Exception):
    """A plain-language refusal to start a tool."""


def _default_runner(argv, cwd, env):
    return subprocess.Popen(argv, cwd=cwd, env=env, shell=False)


class Launcher:
    def __init__(self, root: Path, runner=None):
        self.root = Path(root).resolve()
        self.runner = runner or _default_runner

    def build_command(self, state: ToolState):
        """(argv, cwd, env) for a ready tool, or raise LaunchError."""
        entry = state.entry
        if state.state != "ready" or state.entrypoint_path is None:
            raise LaunchError(f"{entry.name} can't be started from here: {state.detail}")
        argv = [str(state.entrypoint_path), *entry.args]
        env = dict(os.environ)
        for key, value in entry.env.items():
            env[key] = self._substitute(value, entry.name)
        return argv, str(self.root), env

    def _substitute(self, value: str, tool_name: str) -> str:
        if BUNDLE_PLACEHOLDER not in value:
            return value
        resolved = value.replace(BUNDLE_PLACEHOLDER, str(self.root))
        candidate = Path(resolved).resolve()
        if candidate.is_absolute():
            root = self.root
            if candidate != root and root not in candidate.parents:
                raise LaunchError(
                    f"{tool_name} can't be started: a setting points outside the bundle folder."
                )
        return resolved

    def launch(self, state: ToolState):
        """Start the tool. Returns the runner's process handle."""
        entry = state.entry
        argv, cwd, env = self.build_command(state)
        for rel in entry.prepare_dirs:
            target = resolve_confined(self.root, rel)
            try:
                target.mkdir(parents=True, exist_ok=True)
            except OSError:
                raise LaunchError(
                    f"{entry.name} can't be started: its data folder "
                    f"('{rel}') could not be created in the bundle folder."
                ) from None
        try:
            return self.runner(argv, cwd, env)
        except OSError:
            raise LaunchError(
                f"{entry.name} could not be started. Its files may be damaged — "
                "re-download the bundle to replace them."
            ) from None
