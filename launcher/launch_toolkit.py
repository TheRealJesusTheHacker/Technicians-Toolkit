"""PyInstaller entry point for the Technician's Toolkit launcher.

Deliberately thin: all behavior lives in the toolkit_launcher package
so the same code runs under ``python -m toolkit_launcher``, in the
test suite, and frozen into TechniciansToolkit.exe.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from toolkit_launcher.app import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
