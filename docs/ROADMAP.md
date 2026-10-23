# Technician's Toolkit — Bundle Roadmap

How the bundle comes together, how it versions, and how a USB gets assembled. The live per-tool portable status lives in [PORTABLE-STATUS.md](PORTABLE-STATUS.md); this file is the bundle's own plan.

## The carrying idea

One download, one USB, the whole kit. A bundle release is **assembled** — pulled from each tool's own official release, hash-verified, laid out in a fixed tree, and shipped with a manifest that records exactly what's inside. Nothing in a bundle is copied by hand, and no tool binary is ever committed to this repository.

**The bundle's form (owner's clarification, 2026-10-20):** one zip that opens to **one folder**, with everything in that folder together. Every bundled tool sits in the folder in its portable form, usable standalone, and the **suite launcher app** sits in the same folder as a single file, giving one GUI over the whole kit. The bundle adds no per-tool folders of its own — a tool keeps only the structure its own portable edition ships with (Charon's `Charon/` folder, NitroCore's `_internal/`). The launcher is a front door, never a replacement for the standalone tools: it is bundle infrastructure, not a tool of the kit.

## Bundle milestones

- **M0 — Bundle home (done, 2026-10-20).** This repo: flagship README, the living portable-status tracker, this roadmap, the bundle layout index, and the launcher stub (`toolkit/` v0.1.0). The fleet-wide portable audit behind the tracker: Argus ships today; NitroCore, VectorZip, and Charon are packaging-ready; Lazarus and Aegis carry the portable edition as a named roadmap deliverable; Beerus is portable by design.
- **M1 — First assembled bundle (v0.1.0) — DONE, 2026-10-20.** Trigger: the packaging-ready tools cut their next releases. **Trigger met 2026-10-20:** NitroCore v1.1.4, VectorZip v1.2.5, and Charon v1.0.1 all shipped with their portables. The first bundle assembles the four portables that exist — Argus v1.2.3, NitroCore v1.1.4, VectorZip v1.2.5, Charon v1.0.1 — in the flat one-folder form, with a full manifest and checksums, **plus the suite launcher's first version** (pulled forward from M3 by the owner's bundle-form clarification: the launcher is part of the bundle's shape, not a later extra). Tools still in roadmap state are accounted for in the manifest as absent, not faked; Beerus is linked.
- **M2 — Assembly tooling — DONE, 2026-10-20.** The pull → verify → lay out → manifest steps are one scripted, repeatable process in this repo (`bundle/assemble_bundle.py`, pins in `bundle/tools.json`), with a `verify` pass that re-opens the built zip and proves it, and a CI workflow (`.github/workflows/build-bundle.yml`) that tests the launcher, builds it on Windows, assembles the bundle, verifies it, runs the shipped launcher's own `--check` against the shipped bundle, and publishes the release. Unverified assembly never ships.
- **M3 — The launcher (first version shipped with M1; growth continues).** The launcher lives in `launcher/` and ships inside the bundle as the single file `TechniciansToolkit.exe` in the bundle folder: it reads the bundle manifest, lists every tool in the kit with its version and job, and launches the tool the technician picks — starting only the manifest's entrypoint, inside the bundle folder, with the entry's fixed arguments and environment. The tools keep working without it — the launcher is a front door, not a lock. Growth with bundle v0.2.0: the launcher (v0.2.0) gained a two-forms presentation for Beerus — Beerus Portable as a bundled, launchable card and the Destruct Key Pro as its own linked card, told apart by name, with the About box telling both forms — and the kit's first dual-form manifest entries are pinned by tests. Growth landed with launcher 1.0.5 (2026-10-21, on `main`): on-demand bundle hash verification inside the window — a **Check bundle files** button that re-proves the folder against its own `SHA256SUMS.txt` and reports in plain language (files a working bundle gains, like a tool's data folder, are counted, never condemned). Still ahead in this milestone: polish as the kit grows.
- **M4 — Full kit (bundle v1.0) — DONE (2026-10-20).** Every tool has a portable form in the bundle: Lazarus and Aegis joined as files with their portable editions, and Beerus is represented by its app as files plus the Live Boot stick as a link. Bundle v1.0.0 shipped on that set (see docs/PORTABLE-STATUS.md).
- **M5 — The kit grows to eight (2026-10-21).** Sphinx — Sentinel's free system-wide ad & tracker blocker — joins the kit as its eighth member, **tracked, not yet bundled**: it has no published release (Android v0.4.1 feature-complete behind its release gate and the owner's device smoke pass; Windows Phases 1–3 complete with the Phase 3 audit closed, its portable existing as CI artifacts only; Debian Phases 1–2 landed and audited), and the bundle assembles only from published releases. The manifest accounts for it under `absent`, the launcher shows its card as not in this bundle, and the tracker carries its per-edition record. The next bundle release ingests Sphinx once Sphinx publishes its first release; how the Android edition is represented in a Windows bundle is the owner's call for that day.

- **M6 — The kit is complete at eight (2026-10-23).** Sphinx published its first release (**v1.0.0**) and was ingested the same day: **bundle v1.1.0** carries all eight members as files — the manifest's `absent` list is empty for the first time, and only Beerus's Live Boot remains a link, as it must. From here the bundle's work is the standing sync rule: every member release moves its pin in the same change-set.

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
  "bundle_version": "0.2.0",
  "assembled": "2026-10-20",
  "launcher": {"file": "TechniciansToolkit.exe", "version": "0.2.0"},
  "tools": [
    {
      "name": "Argus",
      "job": "Scans the computer for viruses and other malware, and locks away what it finds.",
      "repo": "TheRealJesusTheHacker/Argus.exe",
      "version": "1.2.3",
      "artifact": "ArgusPortable.zip",
      "sha256": "<sha256 of the artifact as downloaded>",
      "source_release": "https://github.com/TheRealJesusTheHacker/Argus.exe/releases/tag/v1.2.3",
      "path": ".",
      "readme": "README-PORTABLE-Argus.txt",
      "entrypoint": "Argus.exe",
      "args": [],
      "env": {"ARGUS_DATA_DIR": "{bundle}/ArgusData"},
      "prepare_dirs": ["ArgusData"]
    },
    {
      "name": "Beerus",
      "job": "Securely destroys whole drives, picked files and folders, and free space — and proves what was done.",
      "repo": "TheRealJesusTheHacker/Beerus.exe",
      "version": "0.4.0",
      "artifact": "BeerusPortable.zip",
      "sha256": "<sha256 of the artifact as downloaded>",
      "source_release": "https://github.com/TheRealJesusTheHacker/Beerus.exe/releases/tag/v0.4.0",
      "path": "Beerus",
      "readme": "README-PORTABLE-Beerus.txt",
      "entrypoint": "Beerus/Beerus.exe",
      "args": []
    }
  ],
  "linked": [
    {
      "name": "Beerus — Live Boot",
      "job": "Wipes drives completely, with proof it was done.",
      "repo": "TheRealJesusTheHacker/Beerus.exe",
      "note": "Beerus's other form: a bootable USB stick of its own. Get the image from the Beerus repo."
    }
  ],
  "absent": [
    {
      "name": "Lazarus",
      "job": "Brings files back — restore by date, undelete, and rescue from dying drives.",
      "repo": "TheRealJesusTheHacker/Lazarus.exe",
      "note": "Not in this bundle yet — it joins when its portable edition ships."
    }
  ],
  "notes": ["<bundle-level notes, e.g. the README-PORTABLE collision resolution>"]
}
```

Rules:

- Every tool in the kit is accounted for: bundled tools under `tools`, bootable forms under `linked`, tools whose portable hasn't shipped under `absent` — listed as absent, never faked as present. A tool with two forms is accounted for once per form: Beerus's app sits under `tools` and its bootable Live Boot under `linked`, the two entries told apart by name.
- `sha256` is taken from the artifact **and** cross-checked against the checksums file published with that tool's own release. A mismatch stops assembly.
- `path` is the tool's base inside the bundle folder (`.` when its files sit at the folder's level, as the flat layout intends); `entrypoint` is the file the launcher starts, bundle-relative. The launcher resolves it inside the bundle folder only — an entrypoint (or `env`/`prepare_dirs` path) that points outside is refused.
- `args` is a fixed list (usually empty); `env` is a fixed map whose values may start with the `{bundle}` placeholder for the bundle folder's own path; `prepare_dirs` lists bundle-relative folders to create before a start (portable Argus's data folder). The manifest is **data** — it is validated field by field and never executed, evaluated, or passed to a shell.
- `readme` names the tool's portable readme as it sits in the bundle folder (see the collision rule in the layout index).

**`SHA256SUMS.txt`** — one line per file in the bundle folder (`<sha256>  <path relative to the bundle folder>`), covering every file except the checksums file itself — the manifest included — so an extracted bundle can be verified end-to-end with `sha256sum -c` (or per-file with `certutil -hashfile` on Windows). The release additionally publishes a `SHA256SUMS.txt` asset covering the bundle zip itself.

## USB assembly notes

- **Layout:** the bundle zip contains exactly one folder — extract it to the root of the stick and that folder is the kit. Inside it, everything sits at one level (see [../tools/README.md](../tools/README.md)): the tools' files together, the launcher `TechniciansToolkit.exe` beside them, and the manifest and checksums at the same level.
- **Two sticks, two jobs, on purpose:** the Toolkit USB is a normal file-system stick you plug into a *running* machine. The Beerus Live Boot is a *bootable* stick you boot a machine *from*. They are different media by nature — the bundle links Beerus and documents its flashing process, but never merges the two. A technician carries both.
- **Field hygiene:** rebuild sticks from a verified bundle download rather than copying stick-to-stick; verify `SHA256SUMS.txt` after every rebuild; a stick whose hashes don't match the manifest is wiped and rebuilt, not trusted.

## What this repo will never do

- Commit a tool's binary, zip, or disk image (see `.gitignore` — they are ignored by design).
- List a tool's portable as available before its own release asset list proves it.
- Merge the bootable Beerus image into the file bundle.
