# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['xlsxwriter', 'xlsxwriter.workbook', 'xlsxwriter.worksheet', 'xlsxwriter.format', 'fpdf', 'fpdf.fpdf', 'fpdf.html', 'fpdf.fonts']
hiddenimports += collect_submodules('xlsxwriter')
hiddenimports += collect_submodules('fpdf')


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('icon.ico', '.'), ('gui.py', '.'), ('expense_table.py', '.'), ('export_data.py', '.'), ('error_logger.py', '.')],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter.test', 'test', 'setuptools', 'setuptools._vendor', 'pkg_resources'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LiteFinPad_v',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LiteFinPad_v',
)
