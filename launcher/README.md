# The Suite Launcher

**One window over the whole Technician's Toolkit bundle.**

The launcher is the bundle's front door: a single app that sits in the bundle folder alongside the tools, reads the bundle's `MANIFEST.json`, shows every tool in the kit with its version and its job in one plain sentence, and starts the tool the technician picks.

It is a front door, never a replacement. Every tool in the bundle also runs on its own, straight from the bundle folder, with the launcher closed or deleted. The launcher adds convenience; it takes away nothing.

## What it shows

- **Bundled tools** — name, version, one plain sentence about the job, and a **Launch** button that starts the tool's own program from this folder.
- **Tools not in this bundle yet** — honest cards (no button) saying when they join. The kit's completeness is shown, never faked.
- **Beerus, twice — once per form.** Beerus Portable, the app, is a bundled tool with a **Launch** button like any other. Live Boot, its bootable form, gets its own card ("Beerus — Live Boot") explaining it lives on its own bootable USB stick — a drive is wiped by booting from that stick, for machines that are off or being decommissioned whole. The two cards are told apart by name, and the About box tells both forms.
- **The bundle's version**, the date it was put together, and an **About** box in plain language.
- **Check bundle files** — a button that re-proves every file in the folder against the bundle's own `SHA256SUMS.txt`, on demand, and reports the result in plain language (roadmap M3, launcher 1.0.5). Files a working bundle gains on the job — a tool's data folder, certificates — are counted and reported, never condemned as damage.

Every state is designed: if the manifest is missing or damaged the window says so plainly and what to do; if a tool's files are missing its card says so; if a start fails, the card explains it. There are no placeholder buttons and no dead ends.

## Design rules

- **The manifest is data, never code.** It is parsed as JSON and validated field by field. A tool is started only from the entrypoint path its manifest entry carries, resolved inside the bundle folder — a path that points outside the folder is refused. Arguments are the entry's fixed list, passed to the operating system as a list: no shell, no command strings, nothing typed by a user is ever executed.
- **Fixed environment, prepared folders.** An entry may carry fixed environment variables (portable Argus's `ARGUS_DATA_DIR`, which substitutes the `{bundle}` placeholder with the bundle folder's own path and must stay inside it) and folders to create before starting (`prepare_dirs`, bundle-relative, confined the same way). That is the whole of the launcher's power, and it is exercised only through the validated manifest.
- **House palette, namesake stripes.** Sentinel green on black (`#2ee06f` on `#060a07`/`#0c130d`), every text pairing at least 4.5:1 contrast. Each card also carries a slim identity stripe in its tool's own namesake primary (peacock emerald, nitrous azure, blueprint cyan, Styx aqua, ember, shield bronze, guardian bronze-gold — and Beerus's canonical violet, the owner's single namesake exception). Sphinx, the eighth member, carries its guardian bronze-gold (`#cf9a3e`): its namesake palette — basalt black, sandstone, bronze-gold — shipped canonical in its Windows Phase 3 (v0.3.0), and until it did, its card wore the quiet panel edge; no color was improvised for it in the meantime. Tests render the window and audit the pixels — palette and stripe colors present, the red problem-accent only where a problem state asks for it, and purple only as Beerus's violet stripe.
- **Plain language.** No jargon on any card, panel, or error.

## Build

```powershell
python -m venv .venv
.venv\Scripts\pip install --require-hashes -r requirements-ci.lock.txt
.venv\Scripts\python -m pytest tests -q          # offscreen; no display needed
.venv\Scripts\pyinstaller TechniciansToolkit.spec
```

The spec produces **one file** — `TechniciansToolkit.exe` — on purpose: the bundle is one flat folder, and a one-file launcher adds no folder and no support tree of its own to it. It sits in the bundle folder as one file alongside the tools, the same pattern as the fleet's other one-file builds (Argus.exe, VectorZip.exe). The window is windowed (no console window behind it).

`--check` runs the discovery without a window and prints each tool's state (exit 0, or 2 when the bundle's manifest is missing/damaged) — the bundle build's smoke tests use it against the shipped executable.

In development, `python -m toolkit_launcher [--root <bundle folder>] [--check]` runs the same code unfrozen.

## Layout

| Path | What |
|---|---|
| `toolkit_launcher/manifest.py` | Manifest parsing + validation (pure Python, no Qt) |
| `toolkit_launcher/discovery.py` | Bundle-root location + per-tool states |
| `toolkit_launcher/launching.py` | The launch seam: confinement, fixed args/env, runner |
| `toolkit_launcher/app.py` | The window, the About box, `--check` |
| `toolkit_launcher/integrity.py` | The on-demand bundle file check against `SHA256SUMS.txt` (pure Python, no Qt) |
| `toolkit_launcher/theme.py` | The palette + stylesheet |
| `tests/` | Manifest/discovery/launch/GUI-smoke/rendered-palette tests |

## Honest limits

- The launcher starts tools; it does not elevate them. Tools that need administrator rights ask Windows themselves (NitroCore's exe requests it; Charon explains when the toll needs it) — the launcher never holds privileges of its own.
- Discovery checks that a tool's start file is present. It does not re-verify bundle hashes at launch time; hash verification is the manifest/checksum layer's job at assembly, plus the window's on-demand **Check bundle files** button (M3, landed in launcher 1.0.5) whenever the technician wants the folder re-proved where it stands.
