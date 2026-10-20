# Changelog

All notable changes to the Technician's Toolkit — the bundle, its launcher, and its assembly tooling. Bundle versions are manifests: a version names exactly the tool versions inside it (see docs/ROADMAP.md).

## [0.1.0] - 2026-10-20

### Added

- **The first bundle release (v0.1.0):** one zip that opens to one folder — Argus v1.2.3, NitroCore v1.1.4, VectorZip v1.2.5, and Charon v1.0.1 in portable form, every artifact verified against its own release's published checksums before assembly; `MANIFEST.json` + `SHA256SUMS.txt` covering every file in the folder; a release-level `SHA256SUMS.txt` covering the zip. Lazarus and Aegis are accounted for in the manifest as not in this bundle yet; Beerus is linked (its portable form is the bootable Destruct Key Pro stick).
- **The suite launcher (`launcher/`, v0.1.0):** a PySide6 app shipped inside the bundle as the single file `TechniciansToolkit.exe`, in the same folder as the tools. It reads the manifest and presents the whole kit — one card per tool with its version and its job in one plain sentence; **Launch** starts a bundled tool's own program (manifest entrypoints only, resolved inside the bundle folder, fixed arguments/environment, no shell). Not-in-bundle tools and Beerus get honest cards without a button. Designed states throughout: missing/damaged manifest, missing tool files, and failed starts all explain themselves in plain language. Sentinel green/black, every text pairing ≥4.5:1, no purple; a rendered-palette test pins the theme. Headless `--check` mode for build smoke tests and support.
- **Assembly tooling (`bundle/`):** `tools.json` (the pinned tool list) + `assemble_bundle.py` — pull → verify → lay out → manifest → zip, plus a `verify` pass that re-opens the built zip and proves it (single folder, all checksums, the launcher's own code finds every tool ready). The CI workflow (`.github/workflows/build-bundle.yml`) runs the whole path on Windows — launcher tests, launcher build, assembly, bundle verification, the shipped launcher's `--check` against the shipped bundle — and publishes the release.

### Notes

- **The bundle's flat form** (owner's clarification, 2026-10-20): the tools sit together in the one folder — no per-tool suite folders. A tool keeps only the structure its own portable ships with (Charon's `Charon/` folder, NitroCore's `_internal/`).
- **One collision, resolved openly:** all four portable editions carry a `README-PORTABLE.txt` with different contents. Each is kept in the bundle as `README-PORTABLE-<Tool>.txt`, contents unchanged; the manifest records the final name per tool, and the assembler aborts on any other overwrite rather than resolving it silently.
- The launcher is bundle infrastructure, not a tool in the kit: the kit is still seven tools, and the tracker in `docs/PORTABLE-STATUS.md` remains the record of their portable status.
