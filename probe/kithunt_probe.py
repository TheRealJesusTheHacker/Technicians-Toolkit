"""Kit-hunt Windows probe (temporary; removed after the hunt).

Runs on the windows-latest runner against the REAL assembled bundle
and answers, with the launcher's own code:

1. For every bundled tool: does Launcher.launch() start it, and is
   it still alive seconds later? (The runner's token is elevated,
   so this alone cannot reproduce the owner's standard-user 740 —
   that is what probe 2 is for.)
2. Reduced-integrity spawn (runas /trustlevel:0x20000, a filtered
   standard-user token like the owner's laptop): for every tool,
   does the plain route refuse with WinError 740 and invoke the
   elevator? Recorded via a stand-in elevator — no real UAC prompt
   is triggered on the runner.
3. check_bundle honesty on the real layout: gut NitroCore's
   _internal and confirm the state stops saying ready.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "launcher"))

from toolkit_launcher.discovery import check_bundle  # noqa: E402
from toolkit_launcher.launching import LaunchError, Launcher  # noqa: E402

BUNDLE = REPO / "assembly" / "bundle" / "TechniciansToolkit"
IMAGES = [
    "Argus.exe",
    "NitroCoreOptimizer.exe",
    "VectorZip.exe",
    "Charon.exe",
    "Lazarus.exe",
    "Aegis.exe",
    "Beerus.exe",
]


def kill_all():
    for image in IMAGES:
        subprocess.run(
            ["taskkill", "/IM", image, "/F"],
            capture_output=True,
        )
    time.sleep(1)


def probe_full_integrity():
    print("=== PROBE 1: Launcher.launch per tool (runner integrity) ===")
    _, states = check_bundle(BUNDLE)
    for state in states:
        if state.entry.status != "bundled":
            print(f"{state.entry.name}: skipped ({state.state})")
            continue
        kill_all()
        launcher = Launcher(BUNDLE, settle_seconds=2.0)
        try:
            proc = launcher.launch(state)
        except LaunchError as exc:
            print(f"{state.entry.name}: LAUNCH_ERROR: {exc}")
            continue
        except OSError as exc:
            print(f"{state.entry.name}: OSERROR winerror={getattr(exc, 'winerror', None)}: {exc}")
            continue
        pid = getattr(proc, "pid", None)
        time.sleep(5)
        code = proc.poll() if hasattr(proc, "poll") else None
        if code is None:
            print(f"{state.entry.name}: STARTED pid={pid} ALIVE after settle+5s")
        else:
            print(f"{state.entry.name}: STARTED pid={pid} but EXITED code={code}")
        kill_all()


SPAWN_ONE = '''
import sys, time
from pathlib import Path
sys.path.insert(0, sys.argv[3])
from toolkit_launcher.discovery import check_bundle
from toolkit_launcher.launching import Launcher, LaunchError

root = Path(sys.argv[2])
name = sys.argv[1]
out = Path(sys.argv[4])
_, states = check_bundle(root)
state = next(s for s in states if s.entry.name == name)

class Alive:
    def poll(self):
        return None

def recording_elevator(argv, cwd, env):
    out.write_text(f"ELEVATOR_INVOKED argv0={argv[0]} cwd={cwd}", encoding="utf-8")
    return Alive()

try:
    Launcher(root, elevator=recording_elevator, settle_seconds=0.5).launch(state)
    if not out.exists():
        out.write_text("LAUNCH_OK_NO_ELEVATOR", encoding="utf-8")
except LaunchError as exc:
    out.write_text(f"LAUNCH_ERROR: {exc}", encoding="utf-8")
except OSError as exc:
    out.write_text(f"OSERROR winerror={getattr(exc, 'winerror', None)}", encoding="utf-8")
'''


def probe_reduced_integrity():
    print("=== PROBE 2: reduced-integrity spawn (owner-laptop shape) ===")
    spawn_one = REPO / "probe" / "spawn_one.py"
    spawn_one.write_text(SPAWN_ONE, encoding="utf-8")
    _, states = check_bundle(BUNDLE)
    for state in states:
        if state.entry.status != "bundled":
            continue
        kill_all()
        result = REPO / "probe" / f"result-{state.entry.name}.txt"
        if result.exists():
            result.unlink()
        cmd = (
            f'"{sys.executable}" "{spawn_one}" "{state.entry.name}" '
            f'"{BUNDLE}" "{REPO / "launcher"}" "{result}"'
        )
        run = subprocess.run(
            ["runas", "/trustlevel:0x20000", cmd],
            capture_output=True,
            text=True,
            timeout=60,
        )
        deadline = time.time() + 30
        while not result.exists() and time.time() < deadline:
            time.sleep(0.5)
        if result.exists():
            print(f"{state.entry.name}: {result.read_text(encoding='utf-8').strip()}")
        else:
            print(
                f"{state.entry.name}: NO_RESULT (runas rc={run.returncode}) "
                f"stdout={run.stdout.strip()[:200]} stderr={run.stderr.strip()[:200]}"
            )
        kill_all()


def probe_gutted():
    print("=== PROBE 3: gutted _internal honesty ===")
    internal = BUNDLE / "_internal"
    gone = BUNDLE / "_internal.gone"
    internal.rename(gone)
    try:
        _, states = check_bundle(BUNDLE)
        for state in states:
            if state.entry.name in ("NitroCore", "Argus"):
                print(f"{state.entry.name}: state={state.state} detail={state.detail}")
    finally:
        gone.rename(internal)
    _, states = check_bundle(BUNDLE)
    nitro = next(s for s in states if s.entry.name == "NitroCore")
    print(f"NitroCore after restore: state={nitro.state}")


if __name__ == "__main__":
    print(f"bundle: {BUNDLE} exists={BUNDLE.is_dir()}")
    probe_full_integrity()
    probe_reduced_integrity()
    probe_gutted()
    kill_all()
    print("PROBE DONE")
