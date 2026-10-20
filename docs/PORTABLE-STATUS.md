# Portable Status — The Living Tracker

**Last audit: 2026-10-20** (fleet-wide portable-mandate audit; every entry below was verified against the tool's live repository and release lists that night — not copied from README claims). **Round-2 update, later the same day:** the three packaging-ready tools shipped their portables — NitroCore v1.1.4, VectorZip v1.2.5, Charon v1.0.1 (the last also carrying the Windows ledger-lock fix) — each verified against its live release asset list below.

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
| NitroCore | **SHIPS TODAY** | `NitroCorePortable.zip` | NitroCore releases (v1.1.4) |
| VectorZip | **SHIPS TODAY** | `VectorZipPortable.zip`, `VectorZipPortable-linux.zip` | VectorZip releases (v1.2.5) |
| Charon | **SHIPS TODAY** | `CharonPortable.zip` | Charon releases (v1.0.1) |
| Lazarus | **ROADMAP** | Portable edition (Argus Portable pattern) | Named deliverable, Lazarus Phase 5 (packaging) |
| Aegis | **ROADMAP** | Portable edition (Argus Portable pattern) | Named deliverable, Aegis Phase 5 (packaging, after the security audit gate) |
| Beerus | **BY DESIGN** | The bootable Destruct Key Pro USB image itself | Beerus repo — flash it, boot it |

---

## Argus — SHIPS TODAY

- **What the portable is:** `ArgusPortable.zip` — the frozen one-folder Argus app plus its portable launcher/readme, zipped. Unzip anywhere (folder or USB), run it, no install.
- **Verified 2026-10-20:** the v1.2.3 release (published 2026-10-20) carries exactly four assets — `Argus.exe` (55,034,217 B), **`ArgusPortable.zip` (54,671,189 B)**, `Argus.deb` (81,837,140 B), `SHA256SUMS.txt` (236 B). v1.2.2 carries it too (54,665,614 B).
- **Download:** https://github.com/TheRealJesusTheHacker/Argus.exe/releases/tag/v1.2.3
- **Queued:** nothing. Argus is the reference standard the other tools' portables are modeled on.

## NitroCore — SHIPS TODAY

- **What the portable is:** `NitroCorePortable.zip` — a PyInstaller **one-folder** build of NitroCoreOptimizer (exe + `_internal/`) with a `README-PORTABLE.txt` inside, produced by the Windows release workflow. Unzip anywhere (folder or USB), run it, no install.
- **Verified 2026-10-20:** the v1.1.4 release (published 2026-10-20) carries exactly three assets — `NitroCoreOptimizer.exe` (12,314,890 B), **`NitroCorePortable.zip` (12,619,284 B)**, `SHA256SUMS.txt` (179 B), and `SHA256SUMS.txt` covers the portable zip as well as the exe. A proof `workflow_dispatch` run of the Release workflow (run 39386879947) went green before the tag, and the v1.1.4 tag run (39387160608) succeeded.
- **Download:** https://github.com/TheRealJesusTheHacker/NitroCore/releases/tag/v1.1.4
- **In the repo (2026-10-20):** `NitroCore/nitrocore-portable.spec` (commit `e320466c82`), `NitroCore/portable/README-PORTABLE.txt` (`db30c242c2`), and the extended `.github/workflows/release.yml` (`c6e22443fc`) — it builds both editions on `windows-latest`, and `SHA256SUMS.txt` covers the exe **and** the portable zip. READMEs and CHANGELOG updated to match. A zipapp was rejected on inspection: NitroCore is a Windows GUI/system tool on pywin32 — a zipapp would not be a credible portable.
- **Audit note:** the 7 earlier releases (v1.0.0–v1.1.3) carry only `NitroCoreOptimizer.exe` + `SHA256SUMS.txt` — v1.1.4 is the first release with the portable zip.
- **Honest footprint note:** the portable runs without installing, but NitroCore still writes its logs and registry-undo snapshots to `%APPDATA%\NitroCore`. That is stated plainly in the portable's own readme, not hidden.
- **Queued:** nothing for the portable. NitroCore's portable ships today.

## VectorZip — SHIPS TODAY

- **What the portable is:** `VectorZipPortable.zip` (Windows) and `VectorZipPortable-linux.zip` (Linux) — the standalone VectorZip binary plus `README-PORTABLE.txt`, assembled by a stdlib-only script, `packaging/portable/build-portable.py`, that both release jobs and local builds share. Unzip anywhere (folder or USB), run it, no install.
- **Verified 2026-10-20:** the v1.2.5 release (published 2026-10-20) carries exactly six assets — `VectorZip.exe` (36,818,617 B), **`VectorZipPortable.zip` (36,819,731 B)**, `SHA256SUMS-windows.txt` (170 B), `VectorZip` (68,134,464 B), **`VectorZipPortable-linux.zip` (68,135,547 B)**, `SHA256SUMS-linux.txt` (170 B) — and each platform's `SHA256SUMS-*.txt` covers its portable zip as well as the binary. The Release workflow run for the tag (39387374046; Windows and Linux jobs) completed success.
- **Download:** https://github.com/TheRealJesusTheHacker/VectorZip/releases/tag/v1.2.5
- **Audit note:** all 7 earlier releases (v1.0.0–v1.2.4) carried only the one-file binaries (`VectorZip.exe`, `VectorZip`) + per-platform checksums — no portable *package* was claimed for them. v1.2.5 is the first release with the portable zips.
- **Queued:** nothing for the portable. VectorZip's portable ships today.

## Charon — SHIPS TODAY

- **What the portable is:** `CharonPortable.zip` — a PyInstaller one-folder build of Charon (the HUD app; running it with no arguments opens the window) plus `README-PORTABLE.txt`, with `SHA256SUMS.txt` covering the zip. Unzip anywhere (folder or USB), run it, no install.
- **Verified 2026-10-20:** the v1.0.1 release (published 2026-10-20, Charon's first published release) carries exactly two assets — **`CharonPortable.zip` (55,026,898 B)** and `SHA256SUMS.txt` (86 B). A proof `workflow_dispatch` dry run of `build-release.yml` (run 39387325705) went fully green before the tag, and the v1.0.1 release run (39387731242) succeeded — tag-vs-version check, full test suite, build, warn-file gate, smoke test, zip, and asset attach all green.
- **Download:** https://github.com/TheRealJesusTheHacker/Charon.exe/releases/tag/v1.0.1
- **The lock fix that unblocked it (2026-10-20):** the earlier Windows test-gate failure was confirmed firsthand — `tests/test_toll.py::test_concurrent_ledger_writers_lose_nothing` lost one of 20 concurrent ledger appends (`assert 19 == 20`, runs 39385163751 / 39385466686) because `charon/download.py::_ledger_lock`'s Windows branch wrote a seed byte before `msvcrt.locking`, leaving that fd at offset 1 while other writers locked byte 0. Fixed in `cfbb1c82` (every writer rewinds to offset 0 before locking and unlocking); the suite then passed on Windows — 215 passed, 2 skipped, up from 1 failed / 214 passed / 2 skipped, with the same 2 skips. A second fix (`6776212c`) anchored the workflow's warn-file gate to exact missing modules only, after it false-failed on the benign missing `win32com.gen_py` submodule. Version bump + changelog: `6eee88f9`; README/ROADMAP shipped wording: `bc7b1847`.
- **In the repo:** the portable packaging committed 2026-10-20 — `packaging/Charon.spec` (`14b2ac6d`, corrected `cb0a3345`, version resource aligned to 1.0.1 in `6eee88f9`), `packaging/launch_charon.py` (`4a2e2b3d`), `packaging/requirements-ci.txt` (`e1906fb6`, pins matched to Argus's CI set), `packaging/portable/README-PORTABLE.txt` (`afe0ab1d`), `.github/workflows/build-release.yml` (`34db7b67`, warn gate corrected `6776212c`) — Windows runner, version-vs-tag check, full test suite offscreen, PyInstaller build, warn-file gate, an offscreen launch smoke test of the staged exe, then zip + checksums attached to the release.
- **Honest differences, stated in the portable's readme:** Charon's ledger stays at `%PROGRAMDATA%\Charon\ledger.json` and restore points belong to the machine — the portable run doesn't move them onto the stick, and the docs don't pretend otherwise.
- **Queued:** nothing for the portable. Charon's portable ships today.

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
