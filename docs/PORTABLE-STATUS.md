# Portable Status — The Living Tracker

**Last audit: 2026-10-20** (fleet-wide portable-mandate audit; every entry below was verified against the tool's live repository and release lists that night — not copied from README claims).

This file tracks one question per medic-kit tool: *what is its portable edition, where does it download, and what is queued next?* It is updated on every audit. If a status here and a tool's own README disagree, this tracker is wrong until re-audited — flag it.

## The labels

| Label | Meaning |
|---|---|
| **SHIPS TODAY** | A real portable artifact is downloadable right now (release asset, verified in the release's asset list). |
| **PACKAGING READY** | The portable build path (spec / script / workflow) is in the repo and verified coherent. The first portable ships with the tool's next release. |
| **ROADMAP** | Pre-release tool. The portable edition is a named, committed deliverable in the tool's own roadmap — not a vague backlog line. |
| **BY DESIGN** | The portable form is the product itself. |

## Summary

| Tool | Label | Portable artifact | Where |
|---|---|---|---|
| Argus | **SHIPS TODAY** | `ArgusPortable.zip` | Argus releases (v1.2.3 and earlier) |
| NitroCore | **PACKAGING READY** | `NitroCorePortable.zip` | Ships with the next release after v1.1.3 |
| VectorZip | **PACKAGING READY** | `VectorZipPortable.zip`, `VectorZipPortable-linux.zip` | Ships with the next tagged release after v1.2.4 |
| Charon | **PACKAGING READY** | `CharonPortable.zip` | Ships with Charon v1.0.1, once its release gate is green |
| Lazarus | **ROADMAP** | Portable edition (Argus Portable pattern) | Named deliverable, Lazarus Phase 5 (packaging) |
| Aegis | **ROADMAP** | Portable edition (Argus Portable pattern) | Named deliverable, Aegis Phase 5 (packaging, after the security audit gate) |
| Beerus | **BY DESIGN** | The bootable Destruct Key Pro USB image itself | Beerus repo — flash it, boot it |

---

## Argus — SHIPS TODAY

- **What the portable is:** `ArgusPortable.zip` — the frozen one-folder Argus app plus its portable launcher/readme, zipped. Unzip anywhere (folder or USB), run it, no install.
- **Verified 2026-10-20:** the v1.2.3 release (published 2026-10-20) carries exactly four assets — `Argus.exe` (55,034,217 B), **`ArgusPortable.zip` (54,671,189 B)**, `Argus.deb` (81,837,140 B), `SHA256SUMS.txt` (236 B). v1.2.2 carries it too (54,665,614 B).
- **Download:** https://github.com/TheRealJesusTheHacker/Argus.exe/releases/tag/v1.2.3
- **Queued:** nothing. Argus is the reference standard the other tools' portables are modeled on.

## NitroCore — PACKAGING READY

- **What the portable will be:** `NitroCorePortable.zip` — a PyInstaller **one-folder** build of NitroCoreOptimizer (exe + `_internal/`) with a `README-PORTABLE.txt` inside, produced by the Windows release workflow.
- **In the repo (2026-10-20):** `NitroCore/nitrocore-portable.spec` (commit `e320466c82`), `NitroCore/portable/README-PORTABLE.txt` (`db30c242c2`), and the extended `.github/workflows/release.yml` (`c6e22443fc`) — it builds both editions on `windows-latest`, and `SHA256SUMS.txt` now covers the exe **and** the portable zip. READMEs and CHANGELOG updated to match (`2e6d9cbe1d`, `36221bc361`, `1713a1f53`).
- **Audit note:** all 7 existing releases (v1.0.0–v1.1.3) carry only `NitroCoreOptimizer.exe` + `SHA256SUMS.txt` — no portable exists yet, and none is claimed. A zipapp was rejected on inspection: NitroCore is a Windows GUI/system tool on pywin32 — a zipapp would not be a credible portable.
- **Honest footprint note:** the portable runs without installing, but NitroCore still writes its logs and registry-undo snapshots to `%APPDATA%\NitroCore`. That is stated plainly in the portable's own readme, not hidden.
- **Next steps to SHIPS TODAY:** (1) one `workflow_dispatch` run of the Release workflow to prove the portable build green on the Windows runner (not yet executed); (2) the next release (after v1.1.3) attaches `NitroCorePortable.zip` automatically; (3) verify it in that release's asset list.

## VectorZip — PACKAGING READY

- **What the portable will be:** `VectorZipPortable.zip` (Windows) and `VectorZipPortable-linux.zip` (Linux) — the standalone VectorZip binary plus `README-PORTABLE.txt`, assembled by a stdlib-only script, `packaging/portable/build-portable.py`, that both release jobs and local builds share.
- **In the repo (2026-10-20):** `packaging/portable/build-portable.py` (`97994dc9fe`), `packaging/portable/README-PORTABLE.txt` (`90299f6afa`), extended `.github/workflows/release.yml` (`298d26fed7`), README (`996bc4dbab`) and CHANGELOG (final HEAD `148aec4fb1`) updated. The assembly script was proven locally end-to-end (valid zip, exec bit preserved), and the tool itself was re-verified from live source with a byte-identical compress/decompress round trip.
- **Audit note:** all 7 releases (v1.0.0–v1.2.4) carry the one-file binaries (`VectorZip.exe`, `VectorZip`) + per-platform checksums — those binaries are already single-file and download-and-run, but there is no portable *package*, and none is claimed. A zipapp was rejected: it could only cover the CLI, never the PyQt6 GUI that is the shipped product.
- **Next step to SHIPS TODAY:** the next tagged release (v1.2.5 or later) — the workflow assembles and uploads both portable zips with checksums and attestations; verify the two names in that release's asset list.

## Charon — PACKAGING READY (release gate currently red — read on)

- **What the portable will be:** `CharonPortable.zip` — a PyInstaller one-folder build of Charon (the HUD app; running it with no arguments opens the window) plus `README-PORTABLE.txt`, with `SHA256SUMS.txt` covering the release.
- **In the repo (2026-10-20, 8 additive commits, HEAD `19fc36e3d1`):** `packaging/Charon.spec` (`14b2ac6d`, corrected `cb0a3345`), `packaging/launch_charon.py` (`4a2e2b3d`), `packaging/requirements-ci.txt` (`e1906fb6`, pins matched to Argus's CI set), `packaging/portable/README-PORTABLE.txt` (`afe0ab1d`), `.github/workflows/build-release.yml` (`34db7b67`) — Windows runner, version-vs-tag check, full test suite offscreen, PyInstaller build, warn-file gate, an offscreen launch smoke test of the staged exe, then zip + checksums attached to the release. Roadmap and README updated (`1ffac125`, `19fc36e3`). No `charon/` package code or tests were touched.
- **Honest differences, stated in the portable's readme:** Charon's ledger stays at `%PROGRAMDATA%\Charon\ledger.json` and restore points belong to the machine — the portable run doesn't move them onto the stick, and the docs don't pretend otherwise.
- **The blocker (verified, reproducible):** the workflow's test gate fails on Windows — `tests/test_toll.py::test_concurrent_ledger_writers_lose_nothing` loses one of 20 concurrent ledger appends (`assert 19 == 20`), in two consecutive runs (39385163751, 39385466686). The suite is green on Linux. Root-cause analysis points at `charon/download.py::_ledger_lock`: on Windows it writes a seed byte *before* `msvcrt.locking`, shifting that fd's offset to byte 1, while other writers lock byte 0 — two writers can hold "the lock" on different bytes and race. POSIX `flock` (whole-file) has no such hole, which fits the Linux-green / Windows-red pattern.
- **Consequence:** v1.0.1 was **not** cut and no release exists — nothing broken is pretending to be good. The build/zip steps past the gate are wired but not yet exercised in CI.
- **Next steps to SHIPS TODAY:** (1) fix the Windows ledger lock (lock from offset 0 consistently — a `charon/` package change, to be done by a crew cleared for package code); (2) re-run `build-release.yml` until the full pipeline (build → smoke test → zip) verifies green; (3) cut v1.0.1 (version bump + changelog + release) and verify `CharonPortable.zip` + `SHA256SUMS.txt` in its asset list.

## Lazarus — ROADMAP

- **What the portable will be:** a portable no-install edition (folder/USB, Argus Portable pattern) shipping alongside the installer.
- **Committed 2026-10-20:** `docs/ROADMAP.md` (`6ae571e2aa`) names the portable edition as a **Phase 5 deliverable** — "a committed Phase 5 deliverable, not a backlog option" — and the README's Status section says so too (`ceeb65e9c8`). The only backlog line left is the later Technician's Toolkit USB *bundling* of that edition.
- **Next step:** Lazarus's build phases proceed in order (restore engine first — it is the flagship); the portable lands with Phase 5 packaging.

## Aegis — ROADMAP

- **What the portable will be:** a portable no-install edition (folder/USB, Argus Portable pattern) shipping alongside the installer at Phase 5 — **including the portable password vault**: your vault on a USB stick, no install, usable on the machine in front of you. The roadmap names that a headline use case, not an afterthought.
- **Committed 2026-10-20:** `docs/ROADMAP.md` (`6b7ff413e4`) names the portable edition as a **Phase 5 packaging deliverable**, explicitly gated on Phase 5's independent security audit passing; the README's Status section carries the same commitment (`abc65b88ea`).
- **Next step:** Aegis's build phases proceed in order; the portable is built and audited with Phase 5 — it does not ship before the audit gate, by design.

## Beerus — BY DESIGN

- **What the portable is:** Beerus's portable form **is** the bootable Destruct Key Pro USB image itself — flash the image to a USB, boot the target machine from it, wipe, verify, certify. There is no separate portable download or installer, and there never will be: a drive-destruction tool you boot *instead of* the suspect OS is portable by construction.
- **Made explicit 2026-10-20:** Beerus's README already described the bootable-USB design unambiguously but never used the word "portable"; one additive commit (`289c510a77`) added the explicit line: *"Beerus's portable edition is the bootable USB image itself — the Destruct Key Pro USB is its portable form, with no separate portable download or installer."*
- **Bundle handling:** the Technician's Toolkit never bundles Beerus as files. The bundle links Beerus's repo/image; the key stays its own image, flashed by Beerus's own process.
- **Next step:** Beerus's own build phases (wipe engine → verification/certificates → bootable image definition → boot UI → hardware validation).

---

*Labels in this tracker are only ever moved on evidence: a release asset list, a verified workflow, or a roadmap commit — never on intention.*
