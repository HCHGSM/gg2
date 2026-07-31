# -*- mode: python ; coding: utf-8 -*-
# NOTE: minimal working spec targeting the canonical desktop entry point (main.py).
# Icons, versioning, and full build hardening are addressed in Phase 9 (Packaging).

block_cipher = None

# Bundle the app icon (and any future assets under assets/) so it's available
# at runtime from the frozen exe, not just for the exe's own icon resource.
added_datas = [
    ('assets', 'assets'),
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=added_datas,
    hiddenimports=['bcrypt', 'sqlite3'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ERP',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,               # windowed mode, no console popup
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/app_icon.ico',
    version='version_info.txt',
)
