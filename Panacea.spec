# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['game.py'],
    pathex=[],
    binaries=[],
    datas=[('data', 'data'), ('shaders', 'shaders')],
    hiddenimports=['glcontext'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pkg_resources'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Panacea',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
