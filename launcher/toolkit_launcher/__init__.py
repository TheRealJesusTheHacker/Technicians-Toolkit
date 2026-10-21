"""The Technician's Toolkit suite launcher.

One window over the whole medic-kit bundle: reads the bundle's
MANIFEST.json, shows every tool in the kit with its version and its
job in plain language, and starts the tool the technician picks.

The launcher is a front door, never a replacement: every tool in the
bundle also runs on its own, straight from the bundle folder, with
the launcher closed or deleted.
"""

__version__ = "1.0.4"
