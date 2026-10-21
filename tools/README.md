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

  Beerus/                    Beerus Portable's folder (why it has one: below)
    Beerus.exe               Beerus Portable
    _internal/               Beerus's support folder (part of the tool)
  README-PORTABLE-Beerus.txt

  Lazarus.exe                Lazarus
  README-PORTABLE-Lazarus.txt

  Aegis/                     Aegis's own folder, exactly as its portable ships
    Aegis.exe                Aegis
    _internal/               Aegis's support folder (part of the tool)
    README-PORTABLE.txt      Aegis's own readme, inside its folder as shipped
```

Beerus appears in both its forms: the Portable app as files (the `Beerus` folder above), and the Live Boot image not at all — it is a separate stick, accounted for in the manifest as a link (see below).

**The one rename, stated openly:** every portable edition carries a file named `README-PORTABLE.txt`, each with different contents. In the bundle each is kept as `README-PORTABLE-<Tool>.txt` — contents byte-identical to the tool's own readme; only the name is qualified, so nothing overwrites anything. The manifest records the final name per tool, and the bundle's manifest notes say the same. Nothing else is renamed, moved, or added.

## Running each tool

- **The launcher** — run `TechniciansToolkit.exe`. One window, the whole kit, a **Launch** button per bundled tool. It is a front door only: everything below also works with the launcher closed or deleted.
- **Argus** — for portable mode, start it the way its own readme directs: `Argus-Portable.bat`, which points Argus at the `ArgusData/` folder in this folder (created on first run) so settings, scan history, and the quarantine vault travel with the stick. Starting Argus from the launcher does exactly the same thing. Running `Argus.exe` directly instead offers the installed, always-on edition — Argus's own choice screen explains it.
- **NitroCore** — run `NitroCoreOptimizer.exe` **as administrator** (right-click → Run as administrator; the exe requests elevation itself). Keep `_internal/` beside it — it's part of the app. Note: NitroCore writes its logs and registry-undo snapshots to `%APPDATA%\NitroCore` on the host, as its own portable readme states.
- **VectorZip** — run `VectorZip.exe` from the folder. Archives are written next to the files you choose, nowhere hidden.
- **Charon** — open the `Charon` folder and run `Charon.exe`; with no arguments it opens the window. Two things stay with the machine, by design: Charon's ledger lives at `%PROGRAMDATA%\Charon\ledger.json`, and the restore point — the toll — is created on the machine being serviced, as it must be.
- **Lazarus** — run `Lazarus.exe` from the folder. It writes only where you point it and keeps no data of its own beyond its backup configuration, as its own portable readme states.
- **Aegis** — open the `Aegis` folder and run `Aegis.exe`. Aegis keeps nothing anywhere else: its vaults are single sealed files you name and place yourself.
- **Beerus Portable** — run `Beerus/Beerus.exe`. It keeps its work records beside its start file, inside this folder: certificates of destruction land in `Beerus/certificates/`, and its file, folder, and free-space wipe reports in `Beerus/certificates/reports/` — your job records, and they travel with the folder. Whole-drive mode ships disarmed: arming it is a deployment act by Sentinel, not a setting in the app (its own readme, `README-PORTABLE-Beerus.txt`, explains). The file/folder and free-space modes are live behind their consent gates.
- **Beerus — Live Boot** — the bootable form, intentionally never files here: get the image from [Beerus's repo](https://github.com/TheRealJesusTheHacker/Beerus.exe), flash a **separate** USB with it, and boot the target machine from that stick.
- **Sphinx** — the kit's eighth member is **not in this bundle yet**: it has no published release to assemble files from, so no Sphinx files sit in this folder. The manifest accounts for it as absent and the launcher shows its card as not in this bundle; it joins at the next assembly after its first release ships.

## Rules of the folder

- One level: no suite-added subfolders. A tool keeps exactly the structure its own portable zip ships (that's why Charon has its `Charon/` folder and NitroCore its `_internal/` — those are the tools' own, not the bundle's filing system). Beerus's `Beerus/` folder is the one stated exception, and its reason is different: Beerus Portable's own support folder is also named `_internal`, and it can't share the top level with NitroCore's — so the bundle keeps Beerus's app together in one folder, its files byte for byte as released, rather than letting two support folders collide.
- Every file is hash-verified against the bundle's `MANIFEST.json`/`SHA256SUMS.txt` at assembly time; the build aborts on any collision it doesn't have a documented answer for.
- If a tool isn't in the manifest's bundled list, its files don't ship. No placeholders.
