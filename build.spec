# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files

ROOT = os.path.abspath(os.getcwd())

# ---------- 收集 PyQt6 所有資料檔案 ----------
pyqt_datas = collect_data_files("PyQt6")

# ---------- 我哋自己嘅資料檔案 ----------
my_datas = [
    (os.path.join(ROOT, "assets"), "assets"),
]

datas = pyqt_datas + my_datas

# ---------- 外部 exe（放去 _internal/）----------
binaries = [
    (os.path.join(ROOT, "yt-dlp.exe"), "."),
    (os.path.join(ROOT, "ffmpeg.exe"), "."),
    (os.path.join(ROOT, "ffprobe.exe"), "."),
    (os.path.join(ROOT, "mkvmerge.exe"), "."),
]

a = Analysis(
    ["main.py"],
    pathex=[ROOT],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "psutil",
        "requests",
        "biliass",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="蜂鳥下載器 Hummingbirds Downloader v1.0.2",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(ROOT, "assets", "icon.ico"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="蜂鳥下載器 Hummingbirds Downloader v1.0.2",
)
