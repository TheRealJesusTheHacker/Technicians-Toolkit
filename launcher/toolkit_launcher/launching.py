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
- The working folder for the start is the folder the tool's own
  start file sits in — the same folder the tool would have if the
  technician double-clicked it. Tools at the bundle's top level get
  the bundle folder; tools in a folder of their own (Charon, Aegis,
  Beerus) get that folder, never the bundle root above it.

Two start shapes get designed handling, because Windows treats them
differently from a plain start:

- A tool whose program asks Windows for administrator permission
  (its own manifest requests it — NitroCore is the kit's one such
  tool) cannot be started by the plain route at all: CreateProcess
  refuses it outright (Windows error 740) while a double-click asks
  the user and starts it. The launcher therefore retries such a
  refusal through the same ask-the-user route a double-click takes
  (ShellExecute with the "runas" verb, the fixed argument list
  quoted as parameters, never a shell). If the permission is not
  granted, the card says so in plain language — it never claims the
  tool's files are damaged when the real reason is permission.
- A start is only called "started" once the process has survived a
  short settling moment. A program whose support files are missing
  can be created by Windows and still die straight away; that is
  reported as the failure it is, not as a start. A program that
  ends cleanly inside the moment (a starter that hands off and
  exits) still counts as started.

A refusal is a LaunchError with a plain-language message — never a
traceback, never a silent no-op.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

from .discovery import ToolState
from .manifest import BUNDLE_PLACEHOLDER, ManifestError, resolve_confined

# Windows error codes whose plain meaning differs from "damaged
# files" — each gets its own designed answer.
ERROR_ACCESS_DENIED = 5
ERROR_ELEVATION_REQUIRED = 740
ERROR_DIRECTORY_INVALID = 267


class LaunchError(Exception):
    """A plain-language refusal to start a tool."""


def _default_runner(argv, cwd, env):
    return subprocess.Popen(argv, cwd=cwd, env=env, shell=False)


class _ShellExecutedProcess:
    """A poll()-shaped handle over a ShellExecuteEx process handle.

    ShellExecuteEx returns a raw process handle rather than a
    Python process object; this adapter gives it the one method
    the launcher's settling check uses, so an elevated start is
    watched exactly like a plain one.
    """

    def __init__(self, handle):
        self._handle = handle
        self._code = None

    def poll(self):
        if self._code is not None:
            return self._code
        import ctypes
        from ctypes import wintypes

        WAIT_TIMEOUT = 0x102
        if ctypes.windll.kernel32.WaitForSingleObject(self._handle, 0) == WAIT_TIMEOUT:
            return None
        code = wintypes.DWORD()
        ctypes.windll.kernel32.GetExitCodeProcess(
            self._handle, ctypes.byref(code)
        )
        ctypes.windll.kernel32.CloseHandle(self._handle)
        self._code = code.value
        return self._code


def _default_elevator(argv, cwd, env):
    """Start a tool the way a double-click would: ask, then start.

    Uses ShellExecuteEx with the "runas" verb — the route Windows
    itself takes when a program's manifest requests administrator
    permission. There is still no shell: the program is named
    directly, and the only parameters are the manifest's fixed
    argument list, quoted as a parameter string. The manifest's
    environment additions cannot ride this route (ShellExecute has
    no environment parameter; the tool inherits this process's
    environment) — no tool that needs them requests elevation, and
    if one ever did, its data-folder setting would be the price,
    never a silent shell.
    """
    if sys.platform != "win32":
        raise OSError("starting with administrator permission is Windows-only")
    import ctypes
    from ctypes import wintypes

    SEE_MASK_NOCLOSEPROCESS = 0x00000040
    SW_SHOWNORMAL = 1

    class SHELLEXECUTEINFOW(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.DWORD),
            ("fMask", wintypes.ULONG),
            ("lpVerb", wintypes.LPCWSTR),
            ("lpFile", wintypes.LPCWSTR),
            ("lpParameters", wintypes.LPCWSTR),
            ("lpDirectory", wintypes.LPCWSTR),
            ("nShow", ctypes.c_int),
            ("hInstApp", wintypes.HINSTANCE),
            ("lpIDList", ctypes.c_void_p),
            ("lpClass", wintypes.LPCWSTR),
            ("hkeyClass", wintypes.HKEY),
            ("dwHotKey", wintypes.DWORD),
            ("hIcon", wintypes.HANDLE),
            ("hProcess", wintypes.HANDLE),
        ]

    info = SHELLEXECUTEINFOW()
    info.cbSize = ctypes.sizeof(info)
    info.fMask = SEE_MASK_NOCLOSEPROCESS
    info.lpVerb = "runas"
    info.lpFile = argv[0]
    parameters = subprocess.list2cmdline(list(argv[1:]))
    info.lpParameters = parameters if parameters else None
    info.lpDirectory = cwd
    info.nShow = SW_SHOWNORMAL
    if not ctypes.windll.shell32.ShellExecuteExW(ctypes.byref(info)):
        raise ctypes.WinError()
    if not info.hProcess:
        return None
    return _ShellExecutedProcess(info.hProcess)


def _path_escapes(root: Path, value: str) -> bool:
    """True when an env value is a path that resolves outside root.

    Only path-shaped values are judged: absolute paths (POSIX or
    Windows form — a Windows absolute path can never name a place
    inside this folder, whatever machine reads it) and values with
    a ".." step. Anything else is a plain word, not a path.
    """
    import re

    if re.match(r"^[A-Za-z]:[\\/]", value) or value.startswith("\\\\"):
        return sys.platform != "win32" or not _confined(root, Path(value))
    if os.path.isabs(value):
        return not _confined(root, Path(value))
    if any(part == ".." for part in re.split(r"[/\\]", value)):
        return not _confined(root, root / value.replace("\\", "/"))
    return False


def _confined(root: Path, candidate: Path) -> bool:
    resolved = candidate.resolve()
    return resolved == root or root in resolved.parents


class Launcher:
    def __init__(self, root: Path, runner=None, elevator=None, settle_seconds=0.5):
        self.root = Path(root).resolve()
        self.runner = runner or _default_runner
        self.elevator = elevator or _default_elevator
        self.settle_seconds = settle_seconds

    def build_command(self, state: ToolState):
        """(argv, cwd, env) for a ready tool, or raise LaunchError.

        The working folder is the start file's own folder: the same
        folder the tool runs from when it is started by hand.
        """
        entry = state.entry
        if state.state != "ready" or state.entrypoint_path is None:
            raise LaunchError(f"{entry.name} can't be started from here: {state.detail}")
        argv = [str(state.entrypoint_path), *entry.args]
        env = dict(os.environ)
        for key, value in entry.env.items():
            env[key] = self._substitute(value, entry.name)
        return argv, str(state.entrypoint_path.parent), env

    def _substitute(self, value: str, tool_name: str) -> str:
        if BUNDLE_PLACEHOLDER not in value:
            # A plain value that is itself a path gets the same
            # confinement as a placeholder one: an absolute path, or
            # a ".." step, that lands outside the bundle folder is
            # refused (the roadmap's rule for env paths). Plain words
            # and bundle-relative paths pass through unchanged.
            if _path_escapes(self.root, value):
                raise LaunchError(
                    f"{tool_name} can't be started: a setting points outside the bundle folder."
                )
            return value
        resolved = value.replace(BUNDLE_PLACEHOLDER, str(self.root))
        candidate = Path(resolved).resolve()
        if candidate.is_absolute():
            root = self.root
            if candidate != root and root not in candidate.parents:
                raise LaunchError(
                    f"{tool_name} can't be started: a setting points outside the bundle folder."
                )
            # Return the native form: the manifest writes paths with
            # forward slashes, but the tool being started deserves a
            # clean path in its own platform's shape.
            return str(candidate)
        return resolved

    def _settle(self, entry, proc) -> None:
        """Watch a just-started process for one settling moment.

        A process that dies inside the moment with a failure code
        was never really started — say so. One that is still
        running, one that ended cleanly, and one that offers no
        way to ask (a test double) all count as started.
        """
        poll = getattr(proc, "poll", None)
        if not callable(poll) or not self.settle_seconds or self.settle_seconds <= 0:
            return
        deadline = time.monotonic() + self.settle_seconds
        while True:
            code = poll()
            if code is None:
                if time.monotonic() >= deadline:
                    return
                time.sleep(0.05)
                continue
            if code != 0:
                raise LaunchError(
                    f"{entry.name} started, then closed straight away. "
                    "Its files may be damaged — re-download the bundle to replace them."
                )
            return

    def launch(self, state: ToolState):
        """Start the tool. Returns the runner's process handle."""
        entry = state.entry
        argv, cwd, env = self.build_command(state)
        for rel in entry.prepare_dirs:
            try:
                target = resolve_confined(self.root, rel)
            except ManifestError:
                raise LaunchError(
                    f"{entry.name} can't be started: its data folder "
                    f"('{rel}') points outside the bundle folder."
                ) from None
            try:
                target.mkdir(parents=True, exist_ok=True)
            except OSError:
                raise LaunchError(
                    f"{entry.name} can't be started: its data folder "
                    f"('{rel}') could not be created in the bundle folder."
                ) from None
        try:
            proc = self.runner(argv, cwd, env)
        except OSError as exc:
            winerror = getattr(exc, "winerror", None)
            if winerror == ERROR_ELEVATION_REQUIRED:
                # The tool's own program asks Windows for
                # administrator permission; the plain route cannot
                # grant it. Retry the way a double-click starts it.
                try:
                    proc = self.elevator(argv, cwd, env)
                    if proc is None:
                        # The ask-the-user route came back with no
                        # process at all: nothing was started, and
                        # the card must not say otherwise.
                        raise LaunchError(
                            f"{entry.name} needs administrator permission to start, "
                            "but Windows did not start it. Try Launch again and "
                            "choose Yes when Windows asks."
                        )
                except OSError:
                    raise LaunchError(
                        f"{entry.name} needs administrator permission to start, "
                        "and Windows did not grant it. Try Launch again and "
                        "choose Yes when Windows asks — or right-click the "
                        "tool's own file in the bundle folder and choose "
                        "'Run as administrator'."
                    ) from None
            elif winerror == ERROR_ACCESS_DENIED:
                raise LaunchError(
                    f"{entry.name} could not be started: Windows refused "
                    "access to its start file. Security software may be "
                    "blocking it — or its files may be damaged; re-download "
                    "the bundle to replace them."
                ) from None
            elif winerror == ERROR_DIRECTORY_INVALID:
                raise LaunchError(
                    f"{entry.name} could not be started from this location: "
                    "Windows cannot start a program that sits behind a "
                    "network path like this one. Copy the bundle folder to "
                    "this computer or a USB stick and start it there."
                ) from None
            else:
                raise LaunchError(
                    f"{entry.name} could not be started. Its files may be damaged — "
                    "re-download the bundle to replace them."
                ) from None
        self._settle(entry, proc)
        return proc
