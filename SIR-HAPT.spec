import os
import kivymd

kivymd_path = os.path.dirname(kivymd.__file__)

# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_data_files
import os
import kivymd

kivymd_path = os.path.dirname(kivymd.__file__)

kivymd_datas, kivymd_binaries, kivymd_hiddenimports = collect_all('kivymd')

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[] + kivymd_binaries,
    datas=[
        ('app.kv', '.'),
        ('serviceAccountKey_mrgame-pefii-v2-firebase-adminsdk.json', '.'),
        ('sir-hapt-firebase-adminsdk-fbsvc-baadfe4250.json', '.'),
        ('logo.ico', '.'),
        # Forzar inclusion de icon_definitions
        (os.path.join(kivymd_path, 'icon_definitions.py'), 'kivymd'),
    ] + kivymd_datas + collect_data_files('kivy'),
    hiddenimports=[
        'kivymd.icon_definitions',
        'kivy',
        'kivy.core.window',
        'kivy.core.image',
        'kivy.core.text',
        'kivy.lang',
        'kivy.clock',
        'kivy_garden.matplotlib',
        'kivy_garden.matplotlib.backend_kivyagg',
        'kivy_garden.matplotlib.backend_kivy',
        'kivymd.uix.label',
        'kivymd.uix.button',
        'kivymd.uix.list',
        'kivymd.uix.card',
        'kivymd.uix.dialog',
        'kivymd.uix.boxlayout',
        'kivymd.uix.screen',
        'kivymd.uix.navigationrail',
        'matplotlib',
        'matplotlib.backends.backend_agg',
        'mpl_toolkits.mplot3d',
        'numpy',
    ] + kivymd_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='SIR-HAPT',
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
    icon=['logo.ico'],
)