# PyInstaller spec for the Technician's Toolkit suite launcher.
#
# Build (from this folder):  pyinstaller TechniciansToolkit.spec
# Produces a single self-contained executable named TechniciansToolkit
# (TechniciansToolkit.exe on Windows) in dist/.
#
# ONE FILE, on purpose: the bundle is one flat folder, and a one-file
# launcher adds no folder and no support tree of its own to it — it
# sits in the bundle folder as one file alongside the tools, exactly
# like the fleet's other one-file builds (Argus.exe, VectorZip.exe).
# Windowed (no console window) to match the fleet's premium standard.

from pathlib import Path

HERE = Path(SPECPATH)

a = Analysis(
    [str(HERE / "launch_toolkit.py")],
    pathex=[str(HERE)],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # The launcher needs QtCore/QtGui/QtWidgets only. Everything
        # below is heavy and unused; excluding it keeps the file lean.
        "PySide6.QtWebEngineCore",
        "PySide6.QtWebEngineWidgets",
        "PySide6.QtPdf",
        "PySide6.QtPdfWidgets",
        "PySide6.QtQuick",
        "PySide6.QtQuickWidgets",
        "PySide6.QtQml",
        "PySide6.QtMultimedia",
        "PySide6.QtMultimediaWidgets",
        "PySide6.QtCharts",
        "PySide6.QtDataVisualization",
        "PySide6.QtBluetooth",
        "PySide6.QtNfc",
        "PySide6.QtPositioning",
        "PySide6.QtSensors",
        "PySide6.QtSerialPort",
        "PySide6.QtWebSockets",
        "PySide6.QtWebChannel",
        "tkinter",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="TechniciansToolkit",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
