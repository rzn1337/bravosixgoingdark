# -*- mode: python ; coding: utf-8 -*-
# Builds a single-file `b6gd` executable (b6gd.exe on Windows).
#   pyinstaller b6gd.spec
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules("pynput")

a = Analysis(
    ["b6gd_main.py"],
    pathex=["src"],
    binaries=[],
    datas=[("assets/corpus", "assets/corpus")],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="b6gd",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
