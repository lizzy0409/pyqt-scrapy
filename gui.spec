# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=[],
    datas=[('mime.types', 'scrapy'), ('VERSION', 'scrapy'), ('scraps/*.py', 'scraps'), ('scraps/spiders/*.py', 'scraps/spiders')],
    hiddenimports=['PyQt5'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['generate_cfg.py'],
    excludes=['pandas', 'numpy'],
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
    name='gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=['vcruntime140.dll'],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['favicon.ico'],
)
