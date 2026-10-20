# Bundle Assembly

This folder is the bundle's build shop: the pinned list of tool releases a bundle is assembled from, and the script that assembles it.

## The process (one command)

```
python assemble_bundle.py assemble --launcher-file <TechniciansToolkit.exe>
python assemble_bundle.py verify   --zip dist/TechniciansToolkit-vX.Y.Z.zip
```

`assemble`:

1. **Pull** — downloads each tool's portable artifact from its own GitHub release, exactly as pinned in `tools.json` (repo, tag, artifact name, checksums file).
2. **Verify** — every artifact's SHA-256 must match the entry in the checksums file published with that tool's own release. A mismatch stops the build; there is no override.
3. **Lay out** — extracts each portable into the ONE bundle folder, flat: every tool's files together at one level. The bundle adds no folders of its own; a tool keeps only the structure its own portable ships with (Charon's `Charon/` folder, NitroCore's `_internal/`). The one exception is a tool pinned with a `folder` in `tools.json` — Beerus, whose answer to the `_internal` collision below is a folder of its own.
4. **Manifest + checksums** — writes `MANIFEST.json` (every tool accounted for: bundled, linked, or honestly absent) and a `SHA256SUMS.txt` covering every file in the folder.
5. **Ship** — zips the single folder and writes the release-level `SHA256SUMS.txt` next to the zip.

`verify` re-opens the built zip in a fresh folder and proves it: exactly one top folder, every checksum line verifies, no unlisted files, and the launcher's own manifest code finds every bundled tool ready.

## The collision rule

Collisions are resolved **on purpose, never by overwrite** — the assembler aborts on any overwrite it doesn't have a documented answer for. Two collisions are known, and both answers are written into the bundle's own manifest notes, so they travel with the bundle:

1. **The portable readmes.** Every portable edition carries a `README-PORTABLE.txt`, each with different contents. In the bundle each is kept as `README-PORTABLE-<Tool>.txt` (contents byte-identical; only the name is qualified), and the manifest records the final name per tool.
2. **The `_internal` support folders (new in bundle v0.2.0).** Beerus Portable and NitroCore are both one-folder apps whose support folder is named `_internal`, and both zips put it at the top level — two different support folders cannot share one name in one folder. Beerus is therefore pinned with `"folder": "Beerus"` in `tools.json`: the assembler lays its files out under a `Beerus/` folder (the same shape Charon ships in), byte for byte as released — only where they sit differs — and its manifest entry records `path: "Beerus"` and the start file `Beerus/Beerus.exe`. The readme still lands at the bundle's level under its qualified name. A `folder` pin must be one plain folder name, and two tools may never claim the same one — the assembler refuses both cases before laying anything out.

## Updating a bundle

Edit `tools.json` (the pin list — tool versions, tags, jobs, entrypoints) and re-run. Per the standing sync rule, a member tool's update lands here in the same change-set: when a tool cuts a new portable release, its pin moves, the tracker (`docs/PORTABLE-STATUS.md`) is updated, and the next bundle carries it.
