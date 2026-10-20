# The Technician's Toolkit

**Sentinel Safeguard's medic-kit line — every tool in portable, no-install form, in one bundle built to live on a USB stick.**

**Security For Everyone.**

![License: Proprietary](https://img.shields.io/badge/License-Proprietary-2ee06f?style=flat-square)
![Tools](https://img.shields.io/badge/Tools-7-2ee06f?style=flat-square)
[![Bundle](https://img.shields.io/badge/Bundle-v0.1.0-2ee06f?style=flat-square)](https://github.com/TheRealJesusTheHacker/Technicians-Toolkit/releases/tag/v0.1.0)
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

Beerus is the one deliberate exception — in part: a bootable image can't be a file in a folder, so the bundle links the Destruct Key Pro image and it stays its own flashed USB. Beerus Portable, the app edition, is an ordinary portable and will join the bundle as files at the next assembly (see the roadmap).

This repository is the bundle's home — its documentation, its live portable-status tracker, its assembly tooling, and the suite launcher app. **The binaries are never committed here.** Every bundle release is *assembled* from each tool's own official release, and every file in it is hash-verified against that tool's published checksums before it ships (see [How a bundle is built](#how-a-bundle-is-built)).

## The kit

| Tool | Job | Portable status | Get it |
|---|---|---|---|
| **Argus** | Scan — antivirus & malware detection | ✅ **Ships today** | [ArgusPortable.zip in v1.2.3](https://github.com/TheRealJesusTheHacker/Argus.exe/releases/tag/v1.2.3) |
| **NitroCore** | Tune — system optimization | ✅ **Ships today** | [NitroCorePortable.zip in v1.1.4](https://github.com/TheRealJesusTheHacker/NitroCore/releases/tag/v1.1.4) |
| **VectorZip** | Pack — file archives & compression | ✅ **Ships today** | [VectorZipPortable.zip in v1.2.5](https://github.com/TheRealJesusTheHacker/VectorZip/releases/tag/v1.2.5) |
| **Charon** | Update — driver updates, restore point first | ✅ **Ships today** | [CharonPortable.zip in v1.0.1](https://github.com/TheRealJesusTheHacker/Charon.exe/releases/tag/v1.0.1) |
| **Lazarus** | Restore — file recovery, undelete, drive rescue & decrypt | 🗺️ **Roadmap** — named deliverable of its packaging phase | [Lazarus](https://github.com/TheRealJesusTheHacker/Lazarus.exe) |
| **Aegis** | Protect — file encryption & password vault | 🗺️ **Roadmap** — named deliverable of its packaging phase, after its security audit gate | [Aegis](https://github.com/TheRealJesusTheHacker/Aegis.exe) |
| **Beerus** | Destroy — secure drive destruction | ✅ **Ships today** — Beerus Portable, the app edition; the Destruct Key Pro USB is 💾 by design | [BeerusPortable.zip in v0.4.0](https://github.com/TheRealJesusTheHacker/Beerus.exe/releases/tag/v0.4.0) |

The detailed, dated tracker — what each portable is, where it downloads, and what's queued next — lives in **[docs/PORTABLE-STATUS.md](docs/PORTABLE-STATUS.md)**. It is updated on every audit, not on a schedule of good intentions.

### Meet the kit

- **Argus** — the hundred-eyed watcher. Sentinel's antivirus and malware detector: signature database, heuristic engine, real-time watcher, encrypted quarantine vault, and a full GUI. Its portable edition, `ArgusPortable.zip`, already ships in every Argus release.
- **NitroCore** — the tune-up tool. Windows system optimization with an undo trail. Its portable edition (a one-folder edition zipped as `NitroCorePortable.zip`) ships as of [v1.1.4](https://github.com/TheRealJesusTheHacker/NitroCore/releases/tag/v1.1.4).
- **VectorZip** — the pack tool. A fast archive and compression utility with its own `.vzip` format. Its release workflow now assembles `VectorZipPortable.zip` (and a Linux variant) for every future tagged release.
- **Charon** — the ferryman. A Windows driver updater with one non-negotiable rule: *nobody crosses without paying the toll* — a system restore point is created **and verified** before any driver is applied. Its portable edition, `CharonPortable.zip`, ships as of [v1.0.1](https://github.com/TheRealJesusTheHacker/Charon.exe/releases/tag/v1.0.1).
- **Lazarus** — the recovery tool. *"Dead isn't gone."* Restore files and folders by date, undelete with honest per-file odds, clone and salvage dying drives, and unlock encrypted volumes with the owner's own key. Its portable edition is a named deliverable of its packaging phase. Phases 1–3 are complete (v0.4.0, 2026-10-20): the snapshot store and restore engine; undelete for FAT and NTFS drives with honest per-file recovery odds and the drive-rescue clone engine; and decrypt & unlock — owner-key BitLocker unlock through Windows' own tools, a six-entry verified registry of published ransomware decryptors that Lazarus runs only on copies, honest family identification, and a one-screen options assessment — 290 tests, with each phase's audit cycle closed.
- **Aegis** — the shield. *"It does not open."* AES-256 file vaults and a local-first password manager on one crypto core. Its portable edition — your password vault on a USB stick, no install — is a headline use case and a named deliverable of its packaging phase, gated on its independent security audit. Phases 1–2 are complete (v0.3.0, 2026-10-20): the Vault core and the password vault are built on the one crypto core — 257 tests, and a full self-audit cycle closed on each phase; the Strongbox and Lock-and-send follow in Phase 3.
- **Beerus** — the destroyer. Two forms, one engine: the bootable Destruct Key Pro USB that securely wipes drives with verification and certificates of destruction, and **Beerus Portable** — the same destruction as a no-install Windows app for a machine that's already running, which also wipes individual files & folders (overwritten and verified *before* their entries are removed — never mere deletion) and free space. The image is carried by link, never bundled as files; the app is an ordinary portable and joins the bundle as files at the next assembly. Beerus Portable ships at [v0.4.0](https://github.com/TheRealJesusTheHacker/Beerus.exe/releases/tag/v0.4.0) (2026-10-20): whole-drive mode refuses the Windows system drive and the app's own drive at the gate and engine layers and ships disarmed, as the engine prescribes — 331 tests, with the portable surface's independent audit cycle (2 HIGH, 6 MEDIUM, 3 LOW, plus four smaller re-audit findings) fixed and regression-tested before release.

## How a bundle is built

A bundle release is assembled, never hand-copied:

1. **Pull** each tool's portable artifact from that tool's own GitHub release (pinned in [bundle/tools.json](bundle/tools.json)).
2. **Verify** every artifact's SHA-256 against the checksums file published with that release. A mismatch stops the build — no exceptions.
3. **Lay out** the one bundle folder: every tool's files together at one level, plus the suite launcher as a single file in the same folder (layout in [tools/README.md](tools/README.md)). Nothing overwrites anything — the one known collision (every portable carries a `README-PORTABLE.txt`) is resolved by keeping each as `README-PORTABLE-<Tool>.txt`, contents unchanged, and the manifest records it.
4. **Write the manifest** — `MANIFEST.json` + `SHA256SUMS.txt` in the bundle folder, recording every tool, its version, its source release, its hash, and the file the launcher starts for it (format specified in [docs/ROADMAP.md](docs/ROADMAP.md)). The checksums cover every file in the folder.
5. **Verify the built zip** in a fresh folder (checksums re-checked, the launcher's own manifest code finds every bundled tool ready), then **ship** it as a release of this repo: one zip, one manifest, one set of checksums.

**Beerus's boot image is the one exception, by nature:** a bootable image can't be a folder in a zip. The bundle links Beerus's repo and image for that form — the Destruct Key Pro stays its own flashed USB. Beerus Portable, the app edition, is pulled from Beerus's release and hash-verified like every other tool.

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

**The first bundle has shipped: [v0.1.0](https://github.com/TheRealJesusTheHacker/Technicians-Toolkit/releases/tag/v0.1.0) (2026-10-20)** — one zip that opens to one folder carrying the four released portables (Argus v1.2.3, NitroCore v1.1.4, VectorZip v1.2.5, Charon v1.0.1) plus the suite launcher v0.1.0, with a full manifest and checksums. Five tools' portables ship today (the three former packaging-ready tools all shipped on 2026-10-20: NitroCore v1.1.4, VectorZip v1.2.5, Charon v1.0.1 — and Beerus Portable, the app edition of Beerus, shipped at Beerus v0.4.0 the same day), two are committed roadmap deliverables (Lazarus, Aegis — the bundle lists them honestly as not in this bundle yet, and they join when their portable editions ship), and Beerus's other form, the bootable Destruct Key Pro image, is portable by design and stays linked, never bundled as files. Lazarus (v0.4.0) and Aegis (v0.3.0) are mid-build, not yet published releases; their portable editions still arrive at their packaging phases. Beerus Portable joins the bundle as files at the next bundle assembly. The roadmap in [docs/ROADMAP.md](docs/ROADMAP.md) defines how bundle versions track the manifest of tool versions they carry.

## License

Proprietary — Copyright © 2026 Sentinel Safeguard LLC. All rights reserved. See [LICENSE](LICENSE).

---

*Built by **Sentinel Safeguard LLC** — Kansas City, Missouri. Security For Everyone.*
