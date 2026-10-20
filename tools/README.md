# Bundle Layout — tools/

This is the index for the assembled bundle's `tools/` tree: where each tool's portable edition lands, and how to run it from the stick.

**In this repository, this folder contains only this README.** The folders below are created at bundle assembly time from each tool's own release (see [../docs/ROADMAP.md](../docs/ROADMAP.md)), and `.gitignore` keeps every assembled binary out of git — the bundle assembles from releases; it is never committed.

## The layout

```
tools/
  argus/       ArgusPortable.zip, extracted
  nitrocore/   NitroCorePortable.zip, extracted (NitroCoreOptimizer/ folder inside)
  vectorzip/   VectorZipPortable.zip, extracted
  charon/      CharonPortable.zip, extracted
  lazarus/     Lazarus portable — arrives with Lazarus's packaging phase
  aegis/       Aegis portable — arrives with Aegis's packaging phase, after its audit gate
  beerus/      Never a folder — Beerus is a bootable image (see below)
```

## Running each tool

- **argus/** — run `Argus.exe` from the extracted folder. No install; that's the portable edition that ships in every Argus release today.
- **nitrocore/** — open the `NitroCoreOptimizer/` folder and run `NitroCoreOptimizer.exe` **as administrator** (tuning needs it). Keep the `_internal/` folder beside the exe — it's part of the app. Note: NitroCore writes its logs and registry-undo snapshots to `%APPDATA%\NitroCore` on the host, as its own portable readme states.
- **vectorzip/** — run `VectorZip.exe` from the extracted folder (the Linux variant runs `./VectorZip`). Archives are written next to the files you choose, nowhere hidden.
- **charon/** — run the Charon app from the extracted folder; with no arguments it opens the HUD window. Two things stay with the machine, by design: Charon's ledger lives at `%PROGRAMDATA%\Charon\ledger.json`, and the restore point — the toll — is created on the machine being serviced, as it must be.
- **lazarus/** — lands when Lazarus ships its portable edition (a named deliverable of its packaging phase). Nothing to run until then — this folder won't exist in early bundles.
- **aegis/** — lands when Aegis ships its portable edition (a named deliverable of its packaging phase, after its independent security audit). The headline use: your password vault on the stick, no install.
- **beerus/** — intentionally never a folder. Beerus is the bootable Destruct Key Pro: get the image from [Beerus's repo](https://github.com/TheRealJesusTheHacker/Beerus.exe), flash a **separate** USB with it, and boot the target machine from that stick.

## Rules of the tree

- One folder per tool, named in lowercase, containing exactly what that tool's portable zip contains — no hand-added files.
- Every folder's contents are hash-verified against the bundle's `MANIFEST.json` at assembly time.
- If a tool isn't in the manifest, its folder doesn't ship. No placeholders.
