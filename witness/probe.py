"""TEMPORARY witness probe for the bundle 1.0 publish (removed after
evidence collection, like the kit-hunt spawn probe before it).

Runs the Argus v1.2.6 source engine (the seam the GUI, realtime
engine, and service share: argus.scanner.scan_path / scan_file) on
windows-latest and records measured verdicts as JSON:

  anchored   — scan_path over the assembled bundle, ARGUS_DATA_DIR
               set to <bundle>/ArgusData (the launcher's contract)
  variant    — same, on a copy: an EICAR test file planted at the
               bundle root + one byte flipped in VectorZip.exe
  controls   — scan_file on control files, no bundle anchor
  unanchored — scan_file on bundle-exe copies in a bare folder,
               no bundle anchor
  frozen     — the shipped frozen Argus.exe from the bundle copy:
               --self-check / --self-check-qt exit codes, plus a
               time-boxed GUI-launch observation
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

ARGUS_SRC = os.environ["ARGUS_SRC"]
sys.path.insert(0, ARGUS_SRC)

from argus import signatures  # noqa: E402
from argus.rules import BUILTIN_RULES  # noqa: E402
from argus.scanner import scan_file, scan_path  # noqa: E402

EICAR = (
    rb"X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-"
    rb"TEST-FILE!$H+H*"
)

PINNED = [
    "Argus.exe", "TechniciansToolkit.exe", "NitroCoreOptimizer.exe",
    "VectorZip.exe", "Charon/Charon.exe", "Lazarus.exe",
    "Aegis/Aegis.exe", "Beerus/Beerus.exe",
]


def make_db(work: Path):
    db_path = work / "sig.db"
    if not db_path.exists():
        signatures.init_db(db_path, seed=True)
    return signatures.SignatureDB.open(db_path)


def describe(item, root: Path) -> dict:
    a = item.assessment
    try:
        rel = str(item.result.path.relative_to(root))
    except Exception:
        rel = str(item.result.path)
    return {
        "path": rel.replace("\\", "/"),
        "verdict": item.verdict.value,
        "score": a.score,
        "excluded": bool(item.excluded),
        "signals": [
            f"{getattr(s, 'name', '?')}({getattr(s, 'points', getattr(s, 'score', '?'))})"
            for s in a.signals
        ],
        "detections": [
            f"{d.kind}:{getattr(d, 'name', '?')}" for d in a.detections
        ],
        "notes": list(a.notes),
    }


def summarize(report, root: Path) -> dict:
    counts: dict[str, int] = {}
    non_clean = []
    pinned = {}
    for item in report.files:
        v = item.verdict.value
        counts[v] = counts.get(v, 0) + 1
        d = describe(item, root)
        if v != "Clean":
            non_clean.append(d)
        for pin in PINNED:
            if d["path"].replace("\\", "/").lower() == pin.lower():
                pinned[pin] = d
    return {
        "root": str(root),
        "stats": {
            "scanned": report.stats.files_scanned,
            "excluded": report.stats.files_excluded,
            "skipped": report.stats.files_skipped,
        },
        "verdict_counts": counts,
        "non_clean": non_clean,
        "pinned": pinned,
    }


def seg_anchored(bundle: Path, work: Path, out: Path) -> None:
    assert os.environ.get("ARGUS_DATA_DIR"), "anchored needs ARGUS_DATA_DIR"
    db = make_db(work)
    report = scan_path(bundle, db, BUILTIN_RULES)
    out.write_text(json.dumps(summarize(report, bundle), indent=1), encoding="utf-8")


def seg_variant(bundle: Path, work: Path, out: Path) -> None:
    assert os.environ.get("ARGUS_DATA_DIR"), "variant needs ARGUS_DATA_DIR"
    (bundle / "EICAR-TEST.txt").write_bytes(EICAR)
    vz = bundle / "VectorZip.exe"
    data = bytearray(vz.read_bytes())
    data[len(data) // 2] ^= 0xFF
    vz.write_bytes(bytes(data))
    db = make_db(work)
    report = scan_path(bundle, db, BUILTIN_RULES)
    summary = summarize(report, bundle)
    focus = {}
    for item in report.files:
        d = describe(item, bundle)
        if d["path"] in ("EICAR-TEST.txt", "VectorZip.exe"):
            focus[d["path"]] = d
    summary["focus"] = focus
    out.write_text(json.dumps(summary, indent=1), encoding="utf-8")


def seg_files(folder: Path, work: Path, out: Path) -> None:
    assert not os.environ.get("ARGUS_DATA_DIR"), "must run anchorless"
    db = make_db(work)
    results = {}
    for f in sorted(folder.iterdir()):
        if f.is_file():
            item = scan_file(f, db, BUILTIN_RULES)
            results[f.name] = describe(item, folder)
    out.write_text(json.dumps(results, indent=1), encoding="utf-8")


def seg_frozen(bundle: Path, work: Path, out: Path) -> None:
    exe = bundle / "Argus.exe"
    env = dict(os.environ)
    env["ARGUS_DATA_DIR"] = str(bundle / "ArgusData")
    obs: dict = {"exe": str(exe)}
    for flag in ("--self-check", "--self-check-qt"):
        try:
            r = subprocess.run(
                [str(exe), flag], capture_output=True, text=True,
                timeout=180, env=env,
            )
            obs[flag] = {
                "exit": r.returncode,
                "stdout_tail": r.stdout[-400:],
                "stderr_tail": r.stderr[-400:],
            }
        except Exception as exc:  # noqa: BLE001
            obs[flag] = {"error": f"{type(exc).__name__}: {exc}"}
    # Time-boxed GUI observation: launch with no arguments (the GUI
    # route), watch what it creates under its data dir, drop an
    # EICAR file into the watched bundle folder, watch again.
    gui: dict = {}
    proc = None
    try:
        proc = subprocess.Popen([str(exe)], env=env)
        gui["pid"] = proc.pid
        time.sleep(45)
        gui["alive_after_45s"] = proc.poll() is None
        data_dir = bundle / "ArgusData"
        gui["data_dir_after_launch"] = (
            sorted(str(p.relative_to(data_dir)) for p in data_dir.rglob("*"))[:50]
            if data_dir.exists() else "ABSENT"
        )
        (bundle / "frozen-eicar-test.txt").write_bytes(EICAR)
        time.sleep(75)
        gui["alive_after_eicar"] = proc.poll() is None
        hits = []
        if data_dir.exists():
            for p in data_dir.rglob("*"):
                if p.is_file() and p.stat().st_size < 5_000_000:
                    try:
                        blob = p.read_bytes()
                    except OSError:
                        continue
                    if b"EICAR" in blob or b"frozen-eicar" in blob:
                        hits.append(str(p.relative_to(data_dir)))
        gui["eicar_mentions_in_data_dir"] = hits
        gui["data_dir_final"] = (
            sorted(str(p.relative_to(data_dir)) for p in data_dir.rglob("*"))[:80]
            if data_dir.exists() else "ABSENT"
        )
    except Exception as exc:  # noqa: BLE001
        gui["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        subprocess.run(["taskkill", "/IM", "Argus.exe", "/F"],
                       capture_output=True, timeout=60)
        if proc is not None:
            try:
                proc.wait(timeout=30)
            except Exception:  # noqa: BLE001
                pass
    obs["gui_experiment"] = gui
    out.write_text(json.dumps(obs, indent=1), encoding="utf-8")


def main() -> int:
    segment = sys.argv[1]
    work = Path(os.environ["PROBE_WORK"])
    work.mkdir(parents=True, exist_ok=True)
    target = Path(sys.argv[2])
    out = Path(sys.argv[3])
    if segment == "anchored":
        seg_anchored(target, work, out)
    elif segment == "variant":
        seg_variant(target, work, out)
    elif segment in ("controls", "unanchored"):
        seg_files(target, work, out)
    elif segment == "frozen":
        seg_frozen(target, work, out)
    else:
        raise SystemExit(f"unknown segment {segment}")
    print(f"{segment} done -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
