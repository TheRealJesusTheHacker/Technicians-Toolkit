# Technician's Toolkit — Bundle Roadmap

How the bundle comes together, how it versions, and how a USB gets assembled. The live per-tool portable status lives in [PORTABLE-STATUS.md](PORTABLE-STATUS.md); this file is the bundle's own plan.

## The carrying idea

One download, one USB, the whole kit. A bundle release is **assembled** — pulled from each tool's own official release, hash-verified, laid out in a fixed tree, and shipped with a manifest that records exactly what's inside. Nothing in a bundle is copied by hand, and no tool binary is ever committed to this repository.

## Bundle milestones

- **M0 — Bundle home (done, 2026-10-20).** This repo: flagship README, the living portable-status tracker, this roadmap, the bundle layout index, and the launcher stub (`toolkit/` v0.1.0). The fleet-wide portable audit behind the tracker: Argus ships today; NitroCore, VectorZip, and Charon are packaging-ready; Lazarus and Aegis carry the portable edition as a named roadmap deliverable; Beerus is portable by design.
- **M1 — First assembled bundle (v0.1.0).** Trigger: the packaging-ready tools cut their next releases (NitroCore after v1.1.3, VectorZip's next tag, Charon v1.0.1 once its Windows release gate is green). **Trigger met 2026-10-20:** NitroCore v1.1.4, VectorZip v1.2.5, and Charon v1.0.1 all shipped with their portables — the first bundle assembly is unblocked. The bundle assembles the portables that exist at that point — Argus plus whichever have shipped — with a full manifest and checksums. Tools still in roadmap state are listed in the manifest as absent, not faked.
- **M2 — Assembly tooling.** The pull → verify → lay out → manifest steps become one scripted, repeatable process in this repo (and, when it earns its keep, a CI workflow that assembles a bundle release from a list of tool releases). Manual assembly with verified hashes is acceptable until then; unverified assembly never is.
- **M3 — The launcher.** `toolkit/` grows from stub to app: reads the bundle manifest, lists the tools on the stick with their versions, verifies bundle hashes on demand, and launches the tool the technician picks. The tools keep working without it — the launcher is a front door, not a lock.
- **M4 — Full kit (bundle v1.0).** Every tool has a portable form in the bundle: Lazarus and Aegis portables ship with their packaging phases, and Beerus is represented by its link and flashing notes. Only then does the bundle take version 1.0.

## Bundle versioning

- The bundle has its own version (`v0.1.0`, `v0.2.0`, …) that increments on every assembled release.
- **A bundle version is exactly a manifest:** it names the version of every tool inside it. Two bundles with the same version are identical by construction — same tools, same versions, same hashes.
- Bundle **1.0** is reserved for the first bundle in which all seven tools have a portable presence (six as files, Beerus by link/image notes).
- A tool's own release never forces a bundle re-release the same day; bundles assemble on their own cadence and say plainly which tool versions they carry.

## The manifest format

Every bundle ships two files at its root:

**`MANIFEST.json`** — machine-readable, the launcher's source of truth:

```json
{
  "bundle": "TechniciansToolkit",
  "bundle_version": "0.1.0",
  "assembled": "2026-10-20",
  "tools": [
    {
      "name": "Argus",
      "repo": "TheRealJesusTheHacker/Argus.exe",
      "version": "1.2.3",
      "artifact": "ArgusPortable.zip",
      "path": "tools/argus/",
      "sha256": "<sha256 of the artifact as downloaded>",
      "source_release": "https://github.com/TheRealJesusTheHacker/Argus.exe/releases/tag/v1.2.3"
    }
  ],
  "linked": [
    {
      "name": "Beerus",
      "repo": "TheRealJesusTheHacker/Beerus.exe",
      "note": "Bootable image — not bundled as files. Flash the Destruct Key Pro from Beerus's own release."
    }
  ]
}
```

Rules:

- One entry per tool: bundled tools under `tools`, Beerus (and any future bootable) under `linked`.
- `sha256` is taken from the artifact **and** cross-checked against the `SHA256SUMS.txt` published with that tool's own release. A mismatch stops assembly.
- A tool that hasn't shipped a portable yet is simply absent from `tools` — the manifest never lists what isn't in the bundle.

**`SHA256SUMS.txt`** — one line per file at the bundle root (`<sha256>  <filename>`), covering the bundle zip's contents list and the manifest itself, so a downloaded bundle can be verified end-to-end with `certutil -hashfile` (Windows) or `sha256sum -c` (Linux).

## USB assembly notes

- **Layout:** the bundle zip *is* the USB layout — extract it to the root of the stick and it's ready. Tools live under `tools/<tool>/` (see [../tools/README.md](../tools/README.md)); the manifest and checksums sit at the root; the launcher, when it lands (M3), sits at the root too.
- **Two sticks, two jobs, on purpose:** the Toolkit USB is a normal file-system stick you plug into a *running* machine. The Beerus Destruct Key Pro is a *bootable* stick you boot a machine *from*. They are different media by nature — the bundle links Beerus and documents its flashing process, but never merges the two. A technician carries both.
- **Field hygiene:** rebuild sticks from a verified bundle download rather than copying stick-to-stick; verify `SHA256SUMS.txt` after every rebuild; a stick whose hashes don't match the manifest is wiped and rebuilt, not trusted.

## What this repo will never do

- Commit a tool's binary, zip, or disk image (see `.gitignore` — they are ignored by design).
- List a tool's portable as available before its own release asset list proves it.
- Merge the bootable Beerus image into the file bundle.
