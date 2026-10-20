# Bundle Layout — the One Folder

This is the index for the assembled bundle's layout: what sits in the bundle folder, and how to run each tool from it.

**In this repository, this folder contains only this README.** The bundle itself is created at assembly time from each tool's own release (see [../docs/ROADMAP.md](../docs/ROADMAP.md) and [../bundle/README.md](../bundle/README.md)), and `.gitignore` keeps every assembled binary out of git — the bundle assembles from releases; it is never committed.

## The layout

The bundle zip contains exactly **one folder**. Inside it, everything is together at one level — the bundle adds no per-tool folders of its own:

```
TechniciansToolkit/
  TechniciansToolkit.exe     the suite launcher (one file) — the front door
  MANIFEST.json              what's in this bundle, per tool (the launcher's source of truth)
  SHA256SUMS.txt             a checksum for every file in this folder

  Argus.exe                  Argus — run it, or use Argus-Portable.bat (see below)
  Argus-Portable.bat         Argus's portable-mode starter (keeps Argus's data in ArgusData/)
  README-PORTABLE-Argus.txt

  NitroCoreOptimizer.exe     NitroCore — needs its _internal/ beside it, as shipped
  _internal/                 NitroCore's own support folder (part of the tool)
  README-PORTABLE-NitroCore.txt

  VectorZip.exe              VectorZip
  README-PORTABLE-VectorZip.txt

  Charon/                    Charon's own folder, exactly as its portable ships
    Charon.exe               Charon
    _internal/               Charon's support folder (part of the tool)
  README-PORTABLE-Charon.txt
```

Lazarus and Aegis have no files here yet — the manifest lists them as not in this bundle, and their files land when their portable editions ship (their packaging phases). Beerus never appears as files at all (see below).

**The one rename, stated openly:** every portable edition carries a file named `README-PORTABLE.txt`, each with different contents. In the bundle each is kept as `README-PORTABLE-<Tool>.txt` — contents byte-identical to the tool's own readme; only the name is qualified, so nothing overwrites anything. The manifest records the final name per tool, and the bundle's manifest notes say the same. Nothing else is renamed, moved, or added.

## Running each tool

- **The launcher** — run `TechniciansToolkit.exe`. One window, the whole kit, a **Launch** button per bundled tool. It is a front door only: everything below also works with the launcher closed or deleted.
- **Argus** — for portable mode, start it the way its own readme directs: `Argus-Portable.bat`, which points Argus at the `ArgusData/` folder in this folder (created on first run) so settings, scan history, and the quarantine vault travel with the stick. Starting Argus from the launcher does exactly the same thing. Running `Argus.exe` directly instead offers the installed, always-on edition — Argus's own choice screen explains it.
- **NitroCore** — run `NitroCoreOptimizer.exe` **as administrator** (right-click → Run as administrator; the exe requests elevation itself). Keep `_internal/` beside it — it's part of the app. Note: NitroCore writes its logs and registry-undo snapshots to `%APPDATA%\NitroCore` on the host, as its own portable readme states.
- **VectorZip** — run `VectorZip.exe` from the folder. Archives are written next to the files you choose, nowhere hidden.
- **Charon** — open the `Charon` folder and run `Charon.exe`; with no arguments it opens the window. Two things stay with the machine, by design: Charon's ledger lives at `%PROGRAMDATA%\Charon\ledger.json`, and the restore point — the toll — is created on the machine being serviced, as it must be.
- **Lazarus / Aegis** — not in the bundle yet; nothing to run until their portable editions ship.
- **Beerus** — intentionally never files here. Beerus is the bootable Destruct Key Pro: get the image from [Beerus's repo](https://github.com/TheRealJesusTheHacker/Beerus.exe), flash a **separate** USB with it, and boot the target machine from that stick.

## Rules of the folder

- One level: no suite-added subfolders. A tool keeps exactly the structure its own portable zip ships (that's why Charon has its `Charon/` folder and NitroCore its `_internal/` — those are the tools' own, not the bundle's filing system).
- Every file is hash-verified against the bundle's `MANIFEST.json`/`SHA256SUMS.txt` at assembly time; the build aborts on any collision it doesn't have a documented answer for.
- If a tool isn't in the manifest's bundled list, its files don't ship. No placeholders.
