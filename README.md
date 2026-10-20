# The Technician's Toolkit

**Sentinel Safeguard's medic-kit line — every tool in portable, no-install form, in one bundle built to live on a USB stick.**

**Security For Everyone.**

![License: Proprietary](https://img.shields.io/badge/License-Proprietary-2ee06f?style=flat-square)
![Tools](https://img.shields.io/badge/Tools-7-2ee06f?style=flat-square)
![Portable status](https://img.shields.io/badge/Portable%20status-Live%20tracker-2ee06f?style=flat-square)

---

## What this is

One download. One USB stick. The whole kit.

Every Sentinel Safeguard medic-kit tool has a portable edition — no installer, no setup, nothing written into a Start menu. Unzip it, run it from the folder, pull the stick when you're done. The Technician's Toolkit is the bundle that carries all of them together: a technician walks up to any Windows machine with one USB and has the full line in hand.

This repository is the bundle's home — its documentation, its live portable-status tracker, its manifest tooling, and its future launcher app. **The binaries are never committed here.** Every bundle release is *assembled* from each tool's own official release, and every file in it is hash-verified against that tool's published checksums before it ships (see [How a bundle is built](#how-a-bundle-is-built)).

## The kit

| Tool | Job | Portable status | Get it |
|---|---|---|---|
| **Argus** | Scan — antivirus & malware detection | ✅ **Ships today** | [ArgusPortable.zip in v1.2.3](https://github.com/TheRealJesusTheHacker/Argus.exe/releases/tag/v1.2.3) |
| **NitroCore** | Tune — system optimization | ✅ **Ships today** | [NitroCorePortable.zip in v1.1.4](https://github.com/TheRealJesusTheHacker/NitroCore/releases/tag/v1.1.4) |
| **VectorZip** | Pack — file archives & compression | ✅ **Ships today** | [VectorZipPortable.zip in v1.2.5](https://github.com/TheRealJesusTheHacker/VectorZip/releases/tag/v1.2.5) |
| **Charon** | Update — driver updates, restore point first | ✅ **Ships today** | [CharonPortable.zip in v1.0.1](https://github.com/TheRealJesusTheHacker/Charon.exe/releases/tag/v1.0.1) |
| **Lazarus** | Restore — file recovery, undelete, drive rescue & decrypt | 🗺️ **Roadmap** — named deliverable of its packaging phase | [Lazarus](https://github.com/TheRealJesusTheHacker/Lazarus.exe) |
| **Aegis** | Protect — file encryption & password vault | 🗺️ **Roadmap** — named deliverable of its packaging phase, after its security audit gate | [Aegis](https://github.com/TheRealJesusTheHacker/Aegis.exe) |
| **Beerus** | Destroy — secure drive destruction | 💾 **By design** — the portable form *is* the bootable USB image | [Beerus](https://github.com/TheRealJesusTheHacker/Beerus.exe) |

The detailed, dated tracker — what each portable is, where it downloads, and what's queued next — lives in **[docs/PORTABLE-STATUS.md](docs/PORTABLE-STATUS.md)**. It is updated on every audit, not on a schedule of good intentions.

### Meet the kit

- **Argus** — the hundred-eyed watcher. Sentinel's antivirus and malware detector: signature database, heuristic engine, real-time watcher, encrypted quarantine vault, and a full GUI. Its portable edition, `ArgusPortable.zip`, already ships in every Argus release.
- **NitroCore** — the tune-up tool. Windows system optimization with an undo trail. Its portable edition (a one-folder edition zipped as `NitroCorePortable.zip`) ships as of [v1.1.4](https://github.com/TheRealJesusTheHacker/NitroCore/releases/tag/v1.1.4).
- **VectorZip** — the pack tool. A fast archive and compression utility with its own `.vzip` format. Its release workflow now assembles `VectorZipPortable.zip` (and a Linux variant) for every future tagged release.
- **Charon** — the ferryman. A Windows driver updater with one non-negotiable rule: *nobody crosses without paying the toll* — a system restore point is created **and verified** before any driver is applied. Its portable edition, `CharonPortable.zip`, ships as of [v1.0.1](https://github.com/TheRealJesusTheHacker/Charon.exe/releases/tag/v1.0.1).
- **Lazarus** — the recovery tool. *"Dead isn't gone."* Restore files and folders by date, undelete with honest per-file odds, clone and salvage dying drives, and unlock encrypted volumes with the owner's own key. Its portable edition is a named deliverable of its packaging phase. Phase 1 is complete (v0.2.0, 2026-10-20): the snapshot store and restore engine are built, with a 63-test suite and the phase's audit cycle closed; undelete, drive rescue, and decrypt follow in later phases.
- **Aegis** — the shield. *"It does not open."* AES-256 file vaults and a local-first password manager on one crypto core. Its portable edition — your password vault on a USB stick, no install — is a headline use case and a named deliverable of its packaging phase, gated on its independent security audit. Phases 1–2 are complete (v0.3.0, 2026-10-20): the Vault core and the password vault are built on the one crypto core — 257 tests, and a full self-audit cycle closed on each phase; the Strongbox and Lock-and-send follow in Phase 3.
- **Beerus** — the destroyer. A bootable USB that securely wipes drives, with verification and sanitization certificates. Beerus doesn't have a portable *edition* — the bootable Destruct Key Pro USB **is** the product, so it is carried by link, never bundled as files (see the roadmap). Phase 1 is complete (v0.2.0, 2026-10-20): drive inventory, NIST 800-88 method selection, and the consent gates are built — 188 tests, with the safety audit's findings fixed and re-audited; verification and certificates are Phase 2.

## How a bundle is built

A bundle release is assembled, never hand-copied:

1. **Pull** each tool's portable artifact from that tool's own latest GitHub release.
2. **Verify** every artifact's SHA-256 against the `SHA256SUMS.txt` published with that release. A mismatch stops the build — no exceptions.
3. **Lay out** the bundle tree: one folder per tool under `tools/` (layout in [tools/README.md](tools/README.md)).
4. **Write the manifest** — `MANIFEST.json` + `SHA256SUMS.txt` at the bundle root, recording every tool, its version, its source release, and its hash (format specified in [docs/ROADMAP.md](docs/ROADMAP.md)).
5. **Ship** the bundle as a release of this repo: one zip, one manifest, one set of checksums.

**Beerus is the one exception, by nature:** a bootable image can't be a folder in a zip. The bundle links Beerus's own repo and image instead — the Destruct Key Pro stays its own flashed USB.

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
| `docs/PORTABLE-STATUS.md` | The living tracker: per-tool portable status, evidence, and next steps |
| `docs/ROADMAP.md` | Bundle roadmap: assembly, versioning, manifest format, USB notes |
| `tools/README.md` | The bundle layout index — where each tool lands and how to run it |
| `toolkit/` | The future launcher app (v0.1.0 stub today) |
| `LICENSE` | Proprietary — see below |

## Status

The bundle is in assembly. Four tools' portables ship today (Argus, NitroCore, VectorZip, Charon — the three former packaging-ready tools all shipped on 2026-10-20: NitroCore v1.1.4, VectorZip v1.2.5, Charon v1.0.1), two are committed roadmap deliverables (Lazarus, Aegis), and one is portable by design (Beerus). The three in-development tools each completed Phase 1 on 2026-10-20 (Lazarus and Beerus at v0.2.0; Aegis at v0.3.0, with Phase 2 also complete; none yet a published release); their portable editions still arrive at their packaging phases. Bundle releases begin now that the shipping tools have current releases; the roadmap in [docs/ROADMAP.md](docs/ROADMAP.md) defines how bundle versions track the manifest of tool versions they carry.

## License

Proprietary — Copyright © 2026 Sentinel Safeguard LLC. All rights reserved. See [LICENSE](LICENSE).

---

*Built by **Sentinel Safeguard LLC** — Kansas City, Missouri. Security For Everyone.*
