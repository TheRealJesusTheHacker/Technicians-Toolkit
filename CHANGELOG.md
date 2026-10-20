# Changelog

All notable changes to the Technician's Toolkit — the bundle, its launcher, and its assembly tooling. Bundle versions are manifests: a version names exactly the tool versions inside it (see docs/ROADMAP.md).

## [0.2.0] - 2026-10-20

### Added

- **Beerus Portable joins the bundle as files:** the second bundle carries five portables — the v0.1.0 four (Argus v1.2.3, NitroCore v1.1.4, VectorZip v1.2.5, Charon v1.0.1, unchanged) plus **Beerus Portable v0.4.0**, its artifact verified against Beerus's own release checksums before assembly like every other tool's. The manifest now accounts for Beerus once per form: the app as a bundled tool (start file `Beerus/Beerus.exe`), and the bootable Destruct Key Pro as a link — never bundled as files. Lazarus and Aegis remain accounted for as not in this bundle yet.
- **Launcher v0.2.0:** the cards and the About box tell Beerus's two forms apart — Beerus Portable launchable from its card, "Beerus — Destruct Key Pro" as an honest no-button card for the bootable stick, and the About text now describes both forms (including where Beerus Portable keeps its certificates and reports: a `certificates` folder beside its start file). The dual-form manifest shape is pinned by new tests (39 in the suite, up from 34).

### Notes

- **A second collision, resolved openly:** Beerus Portable and NitroCore are both one-folder apps whose support folder is named `_internal`, and both zips put it at the bundle's top level — two different support folders cannot share one name in one folder. Beerus therefore sits in a `Beerus/` folder inside the bundle (the same shape Charon ships in), its files byte for byte as released; only where they sit is different. The assembler gained a per-tool `folder` pin in `bundle/tools.json` for exactly this — one plain folder name, never claimed by two tools, refused before layout otherwise — and the answer is recorded in the bundle's manifest notes so it travels with the bundle. The assembler still aborts on any other overwrite.
- The v0.1.0 entry below stands as written: in that bundle Beerus was linked only, and `tools/README.md`'s layout index has been rewritten for the two-forms reality with this release.

## [0.1.0] - 2026-10-20

### Added

- **The first bundle release (v0.1.0):** one zip that opens to one folder — Argus v1.2.3, NitroCore v1.1.4, VectorZip v1.2.5, and Charon v1.0.1 in portable form, every artifact verified against its own release's published checksums before assembly; `MANIFEST.json` + `SHA256SUMS.txt` covering every file in the folder; a release-level `SHA256SUMS.txt` covering the zip. Lazarus and Aegis are accounted for in the manifest as not in this bundle yet; Beerus is linked (its portable form is the bootable Destruct Key Pro stick).
- **The suite launcher (`launcher/`, v0.1.0):** a PySide6 app shipped inside the bundle as the single file `TechniciansToolkit.exe`, in the same folder as the tools. It reads the manifest and presents the whole kit — one card per tool with its version and its job in one plain sentence; **Launch** starts a bundled tool's own program (manifest entrypoints only, resolved inside the bundle folder, fixed arguments/environment, no shell). Not-in-bundle tools and Beerus get honest cards without a button. Designed states throughout: missing/damaged manifest, missing tool files, and failed starts all explain themselves in plain language. Sentinel green/black, every text pairing ≥4.5:1, no purple; a rendered-palette test pins the theme. Headless `--check` mode for build smoke tests and support.
- **Assembly tooling (`bundle/`):** `tools.json` (the pinned tool list) + `assemble_bundle.py` — pull → verify → lay out → manifest → zip, plus a `verify` pass that re-opens the built zip and proves it (single folder, all checksums, the launcher's own code finds every tool ready). The CI workflow (`.github/workflows/build-bundle.yml`) runs the whole path on Windows — launcher tests, launcher build, assembly, bundle verification, the shipped launcher's `--check` against the shipped bundle — and publishes the release.

### Notes

- **The bundle's flat form** (owner's clarification, 2026-10-20): the tools sit together in the one folder — no per-tool suite folders. A tool keeps only the structure its own portable ships with (Charon's `Charon/` folder, NitroCore's `_internal/`).
- **One collision, resolved openly:** all four portable editions carry a `README-PORTABLE.txt` with different contents. Each is kept in the bundle as `README-PORTABLE-<Tool>.txt`, contents unchanged; the manifest records the final name per tool, and the assembler aborts on any other overwrite rather than resolving it silently.
- The launcher is bundle infrastructure, not a tool in the kit: the kit is still seven tools, and the tracker in `docs/PORTABLE-STATUS.md` remains the record of their portable status.
