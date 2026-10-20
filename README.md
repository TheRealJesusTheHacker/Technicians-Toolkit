# The Technician's Toolkit

**Sentinel Safeguard's medic-kit line — every tool in portable, no-install form, in one bundle built to live on a USB stick.**

**Security For Everyone.**

![License: Proprietary](https://img.shields.io/badge/License-Proprietary-2ee06f?style=flat-square)
![Tools](https://img.shields.io/badge/Tools-7-2ee06f?style=flat-square)
[![Bundle](https://img.shields.io/badge/Bundle-v0.2.0-2ee06f?style=flat-square)](https://github.com/TheRealJesusTheHacker/Technicians-Toolkit/releases/tag/v0.2.0)
![Portable status](https://img.shields.io/badge/Portable%20status-Live%20tracker-2ee06f?style=flat-square)

---

## What this is

One download. One USB stick. The whole kit.

Every Sentinel Safeguard medic-kit tool has a portable edition — no installer, no setup, nothing written into a Start menu. Unzip it, run it from the folder, pull the stick when you're done. The Technician's Toolkit is the bundle that carries all of them together: a technician walks up to any Windows machine with one USB and has the full line in hand.

### The bundle's shape

One zip. It opens to **one folder**, and everything is in that folder together:

- **Every bundled tool, in its portable form, at one level** — not sorted into per-tool suite folders. A tool keeps only the structure its own portable edition ships with (Charon's `Charon` folder, NitroCore's `_internal`); the bundle adds no folders of its own.
- **The suite launcher, `TechniciansToolkit.exe`, in the same folder** — one app that shows the whole kit in a single window and starts any tool in it. It's a front door, never a replacement: every tool also runs on its own from the folder, with the launcher closed or deleted.
- **`MANIFEST.json` + `SHA256SUMS.txt`** at the same level, accounting for every tool in the kit — bundled, linked, or honestly not in this bundle yet.

Beerus comes in two forms, and the bundle treats them differently, on purpose. Beerus Portable, the app edition, is an ordinary portable and sits in the folder as files — in a `Beerus` folder of its own, because its support folder shares NitroCore's `_internal` name and two of those can't share a level (see the collision notes under [How a bundle is built](#how-a-bundle-is-built)). The Destruct Key Pro image is the deliberate exception: a bootable image can't be a file in a folder, so the bundle links it and it stays its own flashed USB.

This repository is the bundle's home — its documentation, its live portable-status tracker, its assembly tooling, and the suite launcher app. **The binaries are never committed here.** Every bundle release is *assembled* from each tool's own official release, and every file in it is hash-verified against that tool's published checksums before it ships (see [How a bundle is built](#how-a-bundle-is-built)).

## The kit

| Tool | Job | Portable status | Get it |
|---|---|---|---|
| **Argus** | Scan — antivirus & malware detection | ✅ **Ships today** | [ArgusPortable.zip in v1.2.3](https://github.com/TheRealJesusTheHacker/Argus.exe/releases/tag/v1.2.3) |
| **NitroCore** | Tune — system optimization | ✅ **Ships today** | [NitroCorePortable.zip in v1.1.5](https://github.com/TheRealJesusTheHacker/NitroCore/releases/tag/v1.1.5) |
| **VectorZip** | Pack — file archives & compression | ✅ **Ships today** | [VectorZipPortable.zip in v1.2.6](https://github.com/TheRealJesusTheHacker/VectorZip/releases/tag/v1.2.6) |
| **Charon** | Update — driver updates, restore point first | ✅ **Ships today** | [CharonPortable.zip in v1.0.1](https://github.com/TheRealJesusTheHacker/Charon.exe/releases/tag/v1.0.1) |
| **Lazarus** | Restore — file recovery, undelete, drive rescue & decrypt | ✅ **Ships today** | [LazarusPortable.zip in v1.0.1](https://github.com/TheRealJesusTheHacker/Lazarus.exe/releases/tag/v1.0.1) |
| **Aegis** | Protect — file encryption & password vault | ✅ **Ships today** | [AegisPortable.zip in v1.0.1](https://github.com/TheRealJesusTheHacker/Aegis.exe/releases/tag/v1.0.1) |
| **Beerus** | Destroy — secure drive destruction | ✅ **Ships today** — Beerus Portable, the app edition, is in this bundle; the Destruct Key Pro USB is 💾 by design | [BeerusPortable.zip in v0.4.0](https://github.com/TheRealJesusTheHacker/Beerus.exe/releases/tag/v0.4.0) |

The detailed, dated tracker — what each portable is, where it downloads, and what's queued next — lives in **[docs/PORTABLE-STATUS.md](docs/PORTABLE-STATUS.md)**. It is updated on every audit, not on a schedule of good intentions.

### Meet the kit

- **Argus** — the hundred-eyed watcher. Sentinel's antivirus and malware detector: signature database, heuristic engine, real-time watcher, encrypted quarantine vault, and a full GUI. Its portable edition, `ArgusPortable.zip`, already ships in every Argus release.
- **NitroCore** — the tune-up tool. Windows system optimization with an undo trail. Its portable edition (a one-folder edition zipped as `NitroCorePortable.zip`) ships as of v1.1.4; the current release is [v1.1.5](https://github.com/TheRealJesusTheHacker/NitroCore/releases/tag/v1.1.5) — a field fix so it also starts when a launcher starts it, not only from Explorer (the program now asks for elevation itself).
- **VectorZip** — the pack tool. A fast archive and compression utility with its own `.vzip` format. Its release workflow now assembles `VectorZipPortable.zip` (and a Linux variant) for every future tagged release.
- **Charon** — the ferryman. A Windows driver updater with one non-negotiable rule: *nobody crosses without paying the toll* — a system restore point is created **and verified** before any driver is applied. Its portable edition, `CharonPortable.zip`, ships as of [v1.0.1](https://github.com/TheRealJesusTheHacker/Charon.exe/releases/tag/v1.0.1).
- **Lazarus** — the recovery tool. *"Dead isn't gone."* Restore files and folders by date, undelete with honest per-file odds, clone and salvage dying drives, and unlock encrypted volumes with the owner's own key. Its portable edition ships today. Phases 1–4 are complete (v0.5.0, 2026-10-20): the snapshot store and restore engine; undelete for FAT and NTFS drives with honest per-file recovery odds and the drive-rescue clone engine; decrypt & unlock — owner-key BitLocker unlock through Windows' own tools, a six-entry verified registry of published ransomware decryptors that Lazarus runs only on copies, honest family identification, and a one-screen options assessment; and backup automation — one-click and scheduled backups into the versioned store with honest catch-up after missed runs, loud target status before disaster, a run history that survives restarts, and retention that never touches the newest backup — 411 tests, with each phase's audit cycle closed. **v1.0.0 is Lazarus's first public release (2026-10-20)**: all five phases complete — Phase 5 put the full animated interface over the whole engine (restore front and center, every refusal in the engine's own plain words, real progress on worker threads) and shipped the self-install and this portable edition, closed by the phase's audit cycle (three independent rounds over the new surface, every finding fixed and re-probed) and a tag-gated Windows release run that caught and fixed the engine's Windows read/write calls before anything published — 546 tests, green on Linux and on Windows CI alike. Get it from the [v1.0.0 release](https://github.com/TheRealJesusTheHacker/Lazarus.exe/releases/tag/v1.0.0). **v1.0.1 followed the same day (2026-10-20)**: the kit-wide Windows bug-hunt patch — the backup-lock process check could have killed the running backup on Windows, Windows-tool calls are now bounded and decode-safe, Windows filename traps (data streams, device names, trailing dots/spaces, case-only collisions) are refused before a restore writes, junctions are never written through, and a drive rescue refuses to land on the drive it is rescuing — every fix pinned by a regression test that fails against v1.0.0, the Windows release gate fully green. Get it from the [v1.0.1 release](https://github.com/TheRealJesusTheHacker/Lazarus.exe/releases/tag/v1.0.1).
- **Aegis** — the shield. *"It does not open."* AES-256 file vaults and a local-first password manager on one crypto core. Its portable edition — your password vault on a USB stick, no install — is a headline use case, and it ships today. **v1.0.0 is Aegis's first public release (2026-10-20)**: all five phases complete — the Vault core, the password vault, the Strongbox with Lock-and-send and Lazarus's armor, the full animated interface (one Lock, one Unlock, plain language throughout), and Phase 5's hardening and packaging, closed by the independent security audit gate (verdict: PASS WITH DOCUMENTED RESIDUALS — no critical or high findings in Round 1; the one medium and three low findings fixed and re-probed closed in Round 2) — 453 tests. **v1.0.1 followed the same day (2026-10-20)**: the first-run install offer moved into the window itself — once per run on the locked screen, never a gate, running the very installer the launcher uses — and the installer's failure messages now state exactly what happened instead of claiming nothing changed; the patch was independently audited before release (one low finding fixed and re-probed clean) — 471 tests. Get it from the [v1.0.1 release](https://github.com/TheRealJesusTheHacker/Aegis.exe/releases/tag/v1.0.1).
- **Beerus** — the destroyer. Two forms, one engine: the bootable Destruct Key Pro USB that securely wipes drives with verification and certificates of destruction, and **Beerus Portable** — the same destruction as a no-install Windows app for a machine that's already running, which also wipes individual files & folders (overwritten and verified *before* their entries are removed — never mere deletion) and free space. The image is carried by link, never bundled as files; the app is an ordinary portable and is in the bundle as files from bundle v0.2.0 — in a `Beerus` folder of its own, because its support folder is named `_internal`, the same name NitroCore's carries, and two different support folders can't share one level. Beerus Portable ships at [v0.4.0](https://github.com/TheRealJesusTheHacker/Beerus.exe/releases/tag/v0.4.0) (2026-10-20): whole-drive mode refuses the Windows system drive and the app's own drive at the gate and engine layers and ships disarmed, as the engine prescribes — 331 tests, with the portable surface's independent audit cycle (2 HIGH, 6 MEDIUM, 3 LOW, plus four smaller re-audit findings) fixed and regression-tested before release.

## How a bundle is built

A bundle release is assembled, never hand-copied:

1. **Pull** each tool's portable artifact from that tool's own GitHub release (pinned in [bundle/tools.json](bundle/tools.json)).
2. **Verify** every artifact's SHA-256 against the checksums file published with that release. A mismatch stops the build — no exceptions.
3. **Lay out** the one bundle folder: every tool's files together at one level, plus the suite launcher as a single file in the same folder (layout in [tools/README.md](tools/README.md)). Nothing overwrites anything — the two known collisions are resolved openly and the manifest records both: every portable carries a `README-PORTABLE.txt`, kept as `README-PORTABLE-<Tool>.txt` with contents unchanged; and Beerus Portable's support folder is named `_internal` — the same name NitroCore's carries — so Beerus sits in a `Beerus` folder of its own, its files byte for byte as released.
4. **Write the manifest** — `MANIFEST.json` + `SHA256SUMS.txt` in the bundle folder, recording every tool, its version, its source release, its hash, and the file the launcher starts for it (format specified in [docs/ROADMAP.md](docs/ROADMAP.md)). The checksums cover every file in the folder.
5. **Verify the built zip** in a fresh folder (checksums re-checked, the launcher's own manifest code finds every bundled tool ready), then **ship** it as a release of this repo: one zip, one manifest, one set of checksums.

**Beerus's boot image is the one exception, by nature:** a bootable image can't be a folder in a zip. The bundle links Beerus's repo and image for that form — the Destruct Key Pro stays its own flashed USB. Beerus Portable, the app edition, is pulled from Beerus's release and hash-verified like every other tool, and the manifest accounts for Beerus once per form: the app as a bundled tool, the stick as a link.

## Verify your bundle

Every bundle ships with `SHA256SUMS.txt`. On Windows:

```powershell
certutil -hashfile TechniciansToolkit-vX.Y.Z.zip SHA256
```

Compare the output to the bundle's published checksum before you trust the stick. Inside the bundle, `MANIFEST.json` lets you check any single tool the same way.

## Repository layout

| Path | What lives there |
|---|---|
| `README.md` | This file — the suite presentation |
| `CHANGELOG.md` | The bundle repo's dated change record |
| `docs/PORTABLE-STATUS.md` | The living tracker: per-tool portable status, evidence, and next steps |
| `docs/ROADMAP.md` | Bundle roadmap: assembly, versioning, manifest format, USB notes |
| `tools/README.md` | The bundle layout index — the one-folder layout, and how to run each tool |
| `launcher/` | The suite launcher app (`toolkit_launcher` package + PyInstaller spec) |
| `bundle/` | The assembly tooling: the pinned tool list (`tools.json`) + `assemble_bundle.py` |
| `toolkit/` | The bundle support package (v0.1.0 stub) |
| `LICENSE` | Proprietary — see below |

## Status

**The current bundle is [v0.2.0](https://github.com/TheRealJesusTheHacker/Technicians-Toolkit/releases/tag/v0.2.0) (2026-10-20)** — one zip (255,766,429 B, SHA-256 `d862467094b31b071cb97afb45020ecaacf7a45db750b1217f6735d3b93e438a`) that opens to one folder carrying the five released portables as files (Argus v1.2.3, NitroCore v1.1.4, VectorZip v1.2.5, Charon v1.0.1, Beerus Portable v0.4.0) plus the suite launcher v0.2.0, with a full manifest and checksums covering 1,434 files. The first bundle, v0.1.0, shipped the same day with the four then-released portables and launcher v0.1.0. Seven tools' portables ship today (the three former packaging-ready tools all shipped on 2026-10-20: NitroCore v1.1.4, VectorZip v1.2.5, Charon v1.0.1 — Beerus Portable, the app edition of Beerus, shipped at Beerus v0.4.0 the same day, Aegis shipped at v1.0.0 the same day, through its independent security audit gate, and Lazarus shipped at v1.0.0 the same day, through its own audit cycle and Windows release gate), and Beerus's other form, the bootable Destruct Key Pro image, is portable by design and stays linked, never bundled as files. Aegis (v1.0.1) and Lazarus (v1.0.0) are both published; this bundle was assembled before either shipped, so neither is in this bundle — both join at the next assembly. The roadmap in [docs/ROADMAP.md](docs/ROADMAP.md) defines how bundle versions track the manifest of tool versions they carry.

## License

Proprietary — Copyright © 2026 Sentinel Safeguard LLC. All rights reserved. See [LICENSE](LICENSE).

---

*Built by **Sentinel Safeguard LLC** — Kansas City, Missouri. Security For Everyone.*
