# Changelog

All notable changes to the Technician's Toolkit — the bundle, its launcher, and its assembly tooling. Bundle versions are manifests: a version names exactly the tool versions inside it (see docs/ROADMAP.md).

## [Unreleased]

Nothing yet — the next bundle assembles when a member tool ships a new portable release.

## [1.0.0] — 2026-10-20

**Bundle 1.0.0 — the full kit.** The first bundle with every medic-kit tool in it as files: Argus 1.2.6, NitroCore 1.1.6, VectorZip 1.2.7, Charon 1.0.3, Lazarus 1.0.2, Aegis 1.0.3, and Beerus Portable 0.6.2, plus the Beerus — Live Boot stick accounted for as the separate bootable medium it is. Release `418949983`: `TechniciansToolkit-v1.0.0.zip` (359,216,273 B, SHA-256 `2d4f898d5e89cb58d573aff0aef128cfce1897484cf51ef6073884cb93a81786`), `SHA256SUMS.txt` (97 B), one zip opening to one folder, 1,668 files inside, every internal checksum verified after publishing by a fresh download and re-extraction (7 tools ready, the stick separate, zero not in this bundle).

### Suite launcher 1.0.2

- Every card now carries a slim **namesake identity stripe** in its tool's own primary — peacock emerald for Argus, nitrous azure for NitroCore, blueprint cyan for VectorZip, Styx aqua for Charon, ember for Lazarus, shield bronze for Aegis, and Beerus's canonical violet (the owner's namesake exception) on both Beerus cards. The stripes are pinned by the launcher's theme and render tests; the window itself stays Sentinel green on black, and the state accent, status text, and launch behavior are unchanged.
- The bootable stick's card is renamed **"Beerus — Live Boot"** everywhere it is a current-state surface (`bundle/tools.json`, the About box, the tests that pin them, and this repo's docs). The retired name survives only in dated history entries.

### Argus witness (measured 2026-10-20, Windows runner, witness run `39505362893`)

Anchored on the bundle (its data folder placed in the bundle, the launcher's own contract), Argus's engine scanned all 1,669 files and returned Clean for every one — each tool fingerprint-verified against the bundle's own `SHA256SUMS.txt`, its packaging traits listed but not scored. On a copy, a planted EICAR test file was caught by signature, and VectorZip.exe with one byte changed was flagged Malicious (score 105) with the bundle-tamper signal — trust suppresses nothing. Stranger controls with the same engine: fresh PyInstaller hello-world programs (plain and PySide6) scored Suspicious 59 — the v1.2.5 calibration cap, not convicted — a stock `cmd.exe` copy Suspicious 30, `notepad.exe` Clean 20. Copies of Argus.exe, the launcher, and VectorZip.exe scanned with no bundle around them scored Suspicious 59: not Clean, not Malicious — the trust travels with the bundle's integrity record, nowhere else. The shipped frozen Argus.exe, run from inside the bundle, passed its `--self-check` and `--self-check-qt` (exit 0) and its GUI started on the runner, created its data store inside the bundle's ArgusData folder, and stayed resident; a scan verdict from the frozen program itself remains unproven — the packaged program exposes no scan command, and its realtime pickup of a dropped test file was not observed within 75 seconds.

### Kit-hunt launcher fixes (landed on main earlier today; they ship in this bundle)

#### Fixed

- **NitroCore could not be started from the launcher at all (field defect, bundle v0.2.0).** NitroCore's program asks Windows for administrator permission — its own manifest requests it, and its portable readme says to run it as administrator. Windows' plain start route (CreateProcess, which the launcher used) refuses such a program outright (error 740), while a double-click asks the user and starts it; the launcher reported that refusal as "Its files may be damaged — re-download the bundle", which was never true. The launcher (now v1.0.1) retries an elevation refusal through the same ask-the-user route a double-click takes (ShellExecute "runas", the manifest's fixed arguments only, still no shell), and if permission is not granted the card says exactly that. Access-denied and network-path refusals likewise get their own plain-language messages instead of the damaged-files claim.
- **Folder tools were started in the wrong working folder.** Every tool used to be started with the bundle root as its working folder; a tool that lives in a folder of its own (Charon, Aegis, Beerus) now starts in that folder — the same folder it runs from when started by hand, as the About text promises.
- **"Started" was announced before anyone knew.** A start counted as started the moment Windows created the process, so a tool whose support files were damaged died straight away while its card said "started.". A start now has to survive a short settling moment; a process that fails inside it is reported as the failure it is. A process that ends cleanly inside the moment (a starter that hands off) still counts as started.
- **A gutted tool still showed "Ready."** Discovery checked only the start file, so a one-folder tool whose `_internal` support folder was lost (an interrupted unzip) looked ready. The manifest can now carry a per-tool `requires` list; the pins name each one-folder tool's `_internal`, and without it the card says what is missing instead of "Ready.".

#### Assembly

- **Case-only filename collisions now stop assembly.** The collision guard compared names case-sensitively, so two files differing only by letter case assembled cleanly on Linux and overwrote each other when the bundle was unzipped on Windows. The guard now folds case across the whole bundle (the current kit has no such pair — this closes the class). A tool file using one of the bundle's own names (the launcher file, `MANIFEST.json`, `SHA256SUMS.txt`, any letter case) likewise stops assembly instead of being overwritten. The assembler gained its own test suite (`bundle/tests`), run by CI next to the launcher's (launcher suite now 59 tests, assembler 7).

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
