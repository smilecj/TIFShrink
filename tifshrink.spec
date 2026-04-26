# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import os

block_cipher = None

# 收集 Pillow 的所有数据文件和子模块（关键步骤）
datas = collect_data_files('PIL')
datas += collect_data_files('PIL._imaging')
datas += collect_data_files('PIL._imagingft')
datas += collect_data_files('PIL._imagingmath')
datas += collect_data_files('PIL._imagingtk')

# 收集 Pillow 子模块
hiddenimports_pil = collect_submodules('PIL')

a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath('.')],
    binaries=[
        # 关键：显式包含 Pillow 的二进制依赖
        # 这些是 Pillow C 扩展依赖的 DLL 文件
    ],
    datas=[
        ('index.html', '.'),
        ('server.py', '.'),
    ] + datas,
    hiddenimports=[
        # Flask 相关
        'server', 'flask', 'flask_cors',
        # Pillow 相关 - 关键依赖
        'PIL', 'PIL.Image', 'PIL.TiffImagePlugin',
        'PIL._imaging', 'PIL._imagingft', 'PIL._imagingmath',
        'PIL._tkinter_finder', 'PIL.ImageFont', 'PIL.ImageDraw',
        'PIL.ImageFilter', 'PIL.ImageEnhance', 'PIL.ImageOps',
        # 其他库
        'numpy', 'numpy.core', 'numpy.random',
        'werkzeug', 'jinja2', 'itsdangerous',
        'markupsafe', 'click', 'blinker', 'certifi',
        'idna', 'urllib3', 'charset_normalizer', 'requests',
        # 标准库
        'socketserver', 'http.server',
        'webbrowser', 'urllib.parse', 'zipfile',
    ] + hiddenimports_pil,
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
    [],
    exclude_binaries=True,
    name='TIFShrink',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,  # 禁用 UPX 以避免 DLL 问题
    upx_exclude=[],
    name='TIFShrink',
)