# The Technician's Toolkit

**Sentinel Safeguard's medic-kit line — every tool in portable, no-install form, in one bundle built to live on a USB stick.**

**Security For Everyone.**

![License: Proprietary](https://img.shields.io/badge/License-Proprietary-2ee06f?style=flat-square)
![Tools](https://img.shields.io/badge/Tools-8-2ee06f?style=flat-square)
[![Bundle](https://img.shields.io/badge/Bundle-v1.3.2-2ee06f?style=flat-square)](https://github.com/TheRealJesusTheHacker/Technicians-Toolkit/releases/tag/v1.3.2)
![Portable status](https://img.shields.io/badge/Portable%20status-Live%20tracker-2ee06f?style=flat-square)

---

## What this is

One download. One USB stick. The whole kit.

Every Sentinel Safeguard medic-kit tool has a portable edition — no installer, no setup, nothing written into a Start menu. Unzip it, run it from the folder, pull the stick when you're done. The Technician's Toolkit is the bundle that carries them together: a technician walks up to any Windows machine with one USB and has the kit in hand.

### The bundle's shape

One zip. It opens to **one folder**, and everything is in that folder together:

- **Every bundled tool, in its portable form, at one level** — not sorted into per-tool suite folders. A tool keeps only the structure its own portable edition ships with (Charon's `Charon` folder, NitroCore's `_internal`); the bundle adds no folders of its own.
- **The suite launcher, `TechniciansToolkit.exe`, in the same folder** — one app that shows the whole kit in a single window and starts any tool in it. It's a front door, never a replacement: every tool also runs on its own from the folder, with the launcher closed or deleted.
- **`MANIFEST.json` + `SHA256SUMS.txt`** at the same level, accounting for every tool in the kit — bundled, linked, or honestly not in this bundle yet.

Beerus comes in two forms, and the bundle treats them differently, on purpose. Beerus Portable, the app edition, is an ordinary portable and sits in the folder as files — in a `Beerus` folder of its own, because its support folder shares NitroCore's `_internal` name and two of those can't share a level (see the collision notes under [How a bundle is built](#how-a-bundle-is-built)). The Live Boot image is the deliberate exception: a bootable image can't be a file in a folder, so the bundle links it and it stays its own flashed USB.

This repository is the bundle's home — its documentation, its live portable-status tracker, its assembly tooling, and the suite launcher app. **The binaries are never committed here.** Every bundle release is *assembled* from each tool's own official release, and every file in it is hash-verified against that tool's published checksums before it ships (see [How a bundle is built](#how-a-bundle-is-built)).

## The kit

| Tool | Job | Portable status | Get it |
|---|---|---|---|
| **Argus** | Scan — antivirus & malware detection | ✅ **Ships today** | [ArgusPortable.zip in v1.2.14](https://github.com/TheRealJesusTheHacker/Argus.exe/releases/tag/v1.2.14) |
| **NitroCore** | Tune — system optimization | ✅ **Ships today** | [NitroCorePortable.zip in v1.1.7](https://github.com/TheRealJesusTheHacker/NitroCore/releases/tag/v1.1.7) |
| **VectorZip** | Pack — file archives & compression | ✅ **Ships today** | [VectorZipPortable.zip in v1.2.12](https://github.com/TheRealJesusTheHacker/VectorZip/releases/tag/v1.2.12) |
| **Charon** | Update — driver updates, restore point first | ✅ **Ships today** | [CharonPortable.zip in v1.0.6](https://github.com/TheRealJesusTheHacker/Charon.exe/releases/tag/v1.0.6) |
| **Lazarus** | Restore — file recovery, undelete, drive rescue & decrypt | ✅ **Ships today** | [LazarusPortable.zip in v1.0.5](https://github.com/TheRealJesusTheHacker/Lazarus.exe/releases/tag/v1.0.5) |
| **Aegis** | Protect — file encryption & password vault | ✅ **Ships today** | [AegisPortable.zip in v1.0.6](https://github.com/TheRealJesusTheHacker/Aegis.exe/releases/tag/v1.0.6) |
| **Beerus** | Destroy — secure drive destruction | ✅ **Ships today** — Beerus Portable, the app edition, is in this bundle; the Live Boot USB is 💾 by design | [BeerusPortable.zip in v0.6.4](https://github.com/TheRealJesusTheHacker/Beerus.exe/releases/tag/v0.6.4) |
| **Sphinx** | Block — system-wide ad & tracker blocking | ✅ **In the bundle (from v1.1.0)** — the eighth tool of the kit (joined 2026-10-21). Released as v1.0.0 on 2026-10-23 and ingested the same day: its portable folder, `SphinxPortable/`, ships in the bundle like every member's files | [The Sphinx repo](https://github.com/TheRealJesusTheHacker/Sphinx) |

The detailed, dated tracker — what each portable is, where it downloads, and what's queued next — lives in **[docs/PORTABLE-STATUS.md](docs/PORTABLE-STATUS.md)**. It is updated on every audit, not on a schedule of good intentions.

### Meet the kit

- **Argus** — the hundred-eyed watcher. Sentinel's antivirus and malware detector: signature database, heuristic engine, real-time watcher, encrypted quarantine vault, and a full GUI. Its portable edition, `ArgusPortable.zip`, already ships in every Argus release.
- **NitroCore** — the tune-up tool. Windows system optimization with an undo trail. Its portable edition (a one-folder edition zipped as `NitroCorePortable.zip`) ships as of v1.1.4; the current release is [v1.1.6](https://github.com/TheRealJesusTheHacker/NitroCore/releases/tag/v1.1.6) — a visual release: the interface now wears NitroCore's own nitrous-azure palette (colors only, no behavior changes). v1.1.5 fixed starting from a launcher, not only from Explorer (the program now asks for elevation itself).
- **VectorZip** — the pack tool. A fast archive and compression utility with its own `.vzip` format. Its release workflow now assembles `VectorZipPortable.zip` (and a Linux variant) for every future tagged release.
- **Charon** — the ferryman. A Windows driver updater with one non-negotiable rule: *nobody crosses without paying the toll* — a system restore point is created **and verified** before any driver is applied. Its portable edition, `CharonPortable.zip`, ships as of [v1.0.3](https://github.com/TheRealJesusTheHacker/Charon.exe/releases/tag/v1.0.3); the current release is [v1.0.5](https://github.com/TheRealJesusTheHacker/Charon.exe/releases/tag/v1.0.5).
- **Lazarus** — the recovery tool. *"Dead isn't gone."* Restore files and folders by date, undelete with honest per-file odds, clone and salvage dying drives, and unlock encrypted volumes with the owner's own key. Its portable edition ships today. Phases 1–4 are complete (v0.5.0, 2026-10-20): the snapshot store and restore engine; undelete for FAT and NTFS drives with honest per-file recovery odds and the drive-rescue clone engine; decrypt & unlock — owner-key BitLocker unlock through Windows' own tools, a six-entry verified registry of published ransomware decryptors that Lazarus runs only on copies, honest family identification, and a one-screen options assessment; and backup automation — one-click and scheduled backups into the versioned store with honest catch-up after missed runs, loud target status before disaster, a run history that survives restarts, and retention that never touches the newest backup — 411 tests, with each phase's audit cycle closed. **v1.0.0 is Lazarus's first public release (2026-10-20)**: all five phases complete — Phase 5 put the full animated interface over the whole engine (restore front and center, every refusal in the engine's own plain words, real progress on worker threads) and shipped the self-install and this portable edition, closed by the phase's audit cycle (three independent rounds over the new surface, every finding fixed and re-probed) and a tag-gated Windows release run that caught and fixed the engine's Windows read/write calls before anything published — 546 tests, green on Linux and on Windows CI alike. Get it from the [v1.0.0 release](https://github.com/TheRealJesusTheHacker/Lazarus.exe/releases/tag/v1.0.0). **v1.0.1 followed the same day (2026-10-20)**: the kit-wide Windows bug-hunt patch — the backup-lock process check could have killed the running backup on Windows, Windows-tool calls are now bounded and decode-safe, Windows filename traps (data streams, device names, trailing dots/spaces, case-only collisions) are refused before a restore writes, junctions are never written through, and a drive rescue refuses to land on the drive it is rescuing — every fix pinned by a regression test that fails against v1.0.0, the Windows release gate fully green. Get it from the [v1.0.1 release](https://github.com/TheRealJesusTheHacker/Lazarus.exe/releases/tag/v1.0.1). **v1.0.2 followed the same day (2026-10-20)**: the namesake-palette release — Lazarus's own dawn identity, colors only, the v1.0.1 hunt fixes standing byte-for-byte — 574 tests. **v1.0.3 followed (2026-10-21)**: the fleet sweep #3 patch closing the Phase 5 audit's recorded residuals — pipe/socket sources refused before any open can hang the engine, shortcut loops refused in plain words, an unlock's recovery key no longer kept reachable after the attempt, large-file recovery streamed instead of loaded whole, and a backup run that reports its own outcome even when its history line cannot be written — 588 tests. Get it from the [v1.0.3 release](https://github.com/TheRealJesusTheHacker/Lazarus.exe/releases/tag/v1.0.3). **v1.0.4 followed (2026-10-24)**: the fleet sweep #5 performance patch — verify and restore now cache hash verdicts instead of re-hashing the same stored copy once per snapshot or entry, and snapshotting hashes first, so an unchanged file is never copied only to be discarded (full-store verify 4.31 s → 0.55 s on the sweep bench; a first snapshot of new content gains one read pass, stated in its changelog) — 594 tests. Get the current release from the [v1.0.4 release](https://github.com/TheRealJesusTheHacker/Lazarus.exe/releases/tag/v1.0.4).
- **Aegis** — the shield. *"It does not open."* AES-256 file vaults and a local-first password manager on one crypto core. Its portable edition — your password vault on a USB stick, no install — is a headline use case, and it ships today. **v1.0.0 is Aegis's first public release (2026-10-20)**: all five phases complete — the Vault core, the password vault, the Strongbox with Lock-and-send and Lazarus's armor, the full animated interface (one Lock, one Unlock, plain language throughout), and Phase 5's hardening and packaging, closed by the independent security audit gate (verdict: PASS WITH DOCUMENTED RESIDUALS — no critical or high findings in Round 1; the one medium and three low findings fixed and re-probed closed in Round 2) — 453 tests. **v1.0.1 followed the same day (2026-10-20)**: the first-run install offer moved into the window itself — once per run on the locked screen, never a gate, running the very installer the launcher uses — and the installer's failure messages now state exactly what happened instead of claiming nothing changed; the patch was independently audited before release (one low finding fixed and re-probed clean) — 471 tests. **v1.0.2 followed the same day (2026-10-20)**: the kit-wide clean-machine bug-hunt patch — creating vaults and sealed files now works on drives that can't hold links (USB sticks above all), a save that meets a briefly busy file waits and tries again, names carrying a colon are refused wherever Aegis reads or writes a name and sealing refuses them up front, and install detection is no longer fooled by an alternate spelling of the installed home — 502 tests, green on Windows CI through the tag-gated release run. **v1.0.3 followed the same day (2026-10-20)**: Aegis's namesake palette — the shared kit green retired for its own shield bronze and polished steel on near-black; screens, words, and behavior unchanged (colors only), every text pairing re-measured at 4.5:1 or better (worst 5.62:1) and the destructive red untouched — 500 tests, green on Windows CI through the tag-gated release run. Get it from the [v1.0.3 release](https://github.com/TheRealJesusTheHacker/Aegis.exe/releases/tag/v1.0.3). **v1.0.4 followed (2026-10-21)**: the fleet sweep #3 patch — the window refuses to close while a background job is still running, the final lock no longer races work in flight, and the two timing settings are saved between runs — 512 tests collected. **v1.0.5 followed the same day (2026-10-21)**: the rollback tripwire — Aegis remembers the newest state of each vault outside the vault file (check values only) and refuses a vault file that comes back as a state it has seen and moved past, checked before any password work — and the browser-autofill question closed for good — 529 tests collected. Get the current release from the [v1.0.5 release](https://github.com/TheRealJesusTheHacker/Aegis.exe/releases/tag/v1.0.5).
- **Beerus** — the destroyer. Two forms, one engine: the bootable Live Boot USB that securely wipes drives with verification and certificates of destruction, and **Beerus Portable** — the same destruction as a no-install Windows app for a machine that's already running, which also wipes individual files & folders (overwritten and verified *before* their entries are removed — never mere deletion) and free space. The image is carried by link, never bundled as files; the app is an ordinary portable and is in the bundle as files from bundle v0.2.0 — in a `Beerus` folder of its own, because its support folder is named `_internal`, the same name NitroCore's carries, and two different support folders can't share one level. Beerus Portable first shipped at [v0.4.0](https://github.com/TheRealJesusTheHacker/Beerus.exe/releases/tag/v0.4.0) (2026-10-20): whole-drive mode refuses the Windows system drive and the app's own drive at the gate and engine layers and ships disarmed, as the engine prescribes — 331 tests, with the portable surface's independent audit cycle (2 HIGH, 6 MEDIUM, 3 LOW, plus four smaller re-audit findings) fixed and regression-tested before release. The current portable release is [v0.6.3](https://github.com/TheRealJesusTheHacker/Beerus.exe/releases/tag/v0.6.3) (2026-10-24): the fleet sweep #5 patch — the portable's progress bar renders real percentages instead of overflowing on any real-sized drive, free-space filler writes can no longer spin forever on a zero-progress write, and wipe reports claim their filenames exclusively — over the Phase 4 boot-environment interface and the portable's own namesake palette it took at v0.6.2.
- **Sphinx** — the gatekeeper, and the kit's eighth member (joined 2026-10-21). *"Every request gets questioned."* Sentinel's free system-wide ad & tracker blocker: filtering happens on the device itself — no root, no remote servers, the traffic never leaves the machine. One repo, three editions over one shared filter brain: Android (feature-complete at v0.4.1, behind its release gate and a real-device smoke pass on the owner's phone), Windows (Phases 1–3 complete, Phase 3 audit closed — the loopback DNS filter, the tray host and installer built, profiles and the Sphinx palette; its portable ships as `SphinxPortable.zip` in the v1.0.0 release), and Debian (shipped in v1.0.0 as `sphinx_0.2.0_all.deb` — the loopback daemon, engage/restore guard and .deb, with list updates, rule stores, profiles and resumption). **Sphinx shipped its first public release, v1.0.0, on 2026-10-23**, and the bundle assembles only from published releases — so it joined the bundle at that day's assembly (bundle v1.1.0) as its eighth bundled member: its `SphinxPortable/` folder ships in the folder, its manifest entry is a bundled tool like every other member's, and its launcher card carries a working Launch. Its per-edition record lives in the [tracker](docs/PORTABLE-STATUS.md).

## How a bundle is built

A bundle release is assembled, never hand-copied:

1. **Pull** each tool's portable artifact from that tool's own GitHub release (pinned in [bundle/tools.json](bundle/tools.json)).
2. **Verify** every artifact's SHA-256 against the checksums file published with that release. A mismatch stops the build — no exceptions.
3. **Lay out** the one bundle folder: every tool's files together at one level, plus the suite launcher as a single file in the same folder (layout in [tools/README.md](tools/README.md)). Nothing overwrites anything — the two known collisions are resolved openly and the manifest records both: every portable carries a `README-PORTABLE.txt`, kept as `README-PORTABLE-<Tool>.txt` with contents unchanged; and Beerus Portable's support folder is named `_internal` — the same name NitroCore's carries — so Beerus sits in a `Beerus` folder of its own, its files byte for byte as released.
4. **Write the manifest** — `MANIFEST.json` + `SHA256SUMS.txt` in the bundle folder, recording every tool, its version, its source release, its hash, and the file the launcher starts for it (format specified in [docs/ROADMAP.md](docs/ROADMAP.md)). The checksums cover every file in the folder.
5. **Verify the built zip** in a fresh folder (checksums re-checked, the launcher's own manifest code finds every bundled tool ready), then **ship** it as a release of this repo: one zip, one manifest, one set of checksums.

**Beerus's boot image is the one exception, by nature:** a bootable image can't be a folder in a zip. The bundle links Beerus's repo and image for that form — Live Boot stays its own flashed USB. Beerus Portable, the app edition, is pulled from Beerus's release and hash-verified like every other tool, and the manifest accounts for Beerus once per form: the app as a bundled tool, the stick as a link.

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

**The current bundle is [v1.3.1](https://github.com/TheRealJesusTheHacker/Technicians-Toolkit/releases/tag/v1.3.1) (2026-10-25)** — one zip (409,666,663 B, SHA-256 `a603f5c25f43cb4dc0accd0d4bfc338e1aef6189db41b9014076c6f32feba553`) that opens to one folder carrying all eight members' portables as files (Argus v1.2.13, NitroCore v1.1.7, VectorZip v1.2.12, Charon v1.0.6, Lazarus v1.0.5, Aegis v1.0.6, Beerus Portable v0.6.4, Sphinx v1.0.1) plus the suite launcher v1.0.7, with a full manifest and checksums covering 1,670 files. Bundle v1.3.0 (2026-10-25) carried VectorZip v1.2.11 with the same other pins and launcher (409,668,395 B). Bundle v1.2.0 (2026-10-23) carried Argus v1.2.9 and Sphinx v1.0.1 with launcher v1.0.7 (409,664,299 B). Bundle v1.1.0 (2026-10-23) carried Argus v1.2.7 and Sphinx v1.0.0 with launcher v1.0.6 (409,669,306 B, 1,670 files). Bundle v1.0.0 (2026-10-20) carried the seven then-released portables plus launcher v1.0.2 (359,216,273 B, 1,668 files). The first bundle, v0.1.0, shipped the same day with the four then-released portables and launcher v0.1.0; v0.2.0 followed it with five. **The kit has eight members since 2026-10-21:** Sphinx joined as a tracked member, published its first release on 2026-10-23, and entered the bundle the same day (v1.1.0) — the first bundle with the whole kit in the folder, its manifest's absent list empty. Beerus's other form, the bootable Live Boot image, is portable by design and stays linked, never bundled as files. The roadmap in [docs/ROADMAP.md](docs/ROADMAP.md) defines how bundle versions track the manifest of tool versions they carry.

## License

Proprietary — Copyright © 2026 Sentinel Safeguard LLC. All rights reserved. See [LICENSE](LICENSE).

---

*Built by **Sentinel Safeguard LLC** — Kansas City, Missouri. Security For Everyone.*
