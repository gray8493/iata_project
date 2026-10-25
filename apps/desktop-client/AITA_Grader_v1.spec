# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec - AITA Desktop Client (bản phát hành cho giảng viên).

Đóng gói kèm `toolchains/` (MinGW + JDK rút gọn + Python embeddable) để máy
giảng viên chấm được ngay cả khi chưa cài GCC/JDK/Python.

Trước khi build, tạo toolchains/ bằng:
    python apps/desktop-client/scripts/build_toolchains.py \
        --mingw <mingw64> --jdk <jdk> --smoke-test

Build (onedir, khuyến nghị vì toolchain nặng):
    pyinstaller apps/desktop-client/AITA_Grader_v1.spec --noconfirm

Kết quả: dist/AITA_Grader_v1/ chứa AITA_Grader_v1.exe + toolchains/ + assets/.
"""

import os
from pathlib import Path

APP_DIR = Path(SPECPATH).resolve()          # apps/desktop-client
REPO_ROOT = APP_DIR.parent.parent           # repo root

# toolchains/ đặt cạnh spec (do build_toolchains.py tạo ra).
TOOLCHAINS_DIR = APP_DIR / "toolchains"
# browsers/ đặt cạnh spec (do build_browsers.py tạo ra) - Chromium headless cho chấm web.
BROWSERS_DIR = APP_DIR / "browsers"
# assets: ưu tiên bản của desktop-client, fallback về assets/ ở repo root.
ASSETS_DIR = APP_DIR / "assets"
if not ASSETS_DIR.is_dir():
    ASSETS_DIR = REPO_ROOT / "assets"

datas = [(str(ASSETS_DIR), "assets")]
if TOOLCHAINS_DIR.is_dir():
    datas.append((str(TOOLCHAINS_DIR), "toolchains"))
else:
    print("[spec] CẢNH BÁO: không thấy toolchains/ - exe sẽ cần GCC/JDK/Python trên máy đích.")
if BROWSERS_DIR.is_dir():
    datas.append((str(BROWSERS_DIR), "browsers"))
else:
    print("[spec] CẢNH BÁO: không thấy browsers/ - chấm web sẽ dùng fallback HTTP (không có UI/UX).")

hiddenimports = [
    # PyQt6 backends + plugin động mà PyInstaller không tự suy ra.
    "PyQt6.QtPrintSupport",
    "PyQt6.QtSvg",
    "PyQt6.QtNetwork",
    "psutil",
    "openpyxl",
    "httpx",
    "pypdf",
    # Module nội bộ nạp bằng import động (services.<x> bên trong hàm).
    "services.ai_service",
    "services.web_rubric_service",
    "services.update_service",
    "services.document_reader",
    "core.adapters.compiler_adapter",
    "core.app_paths",
    # Playwright nạp lười trong web_rubric_service._render - kê rõ để driver luôn được gom.
    "playwright.sync_api",
]

excludes = [
    # Không dùng trong app -> cắt hàng chục MB khỏi bundle.
    "tkinter", "test", "unittest", "pydoc_data",
    "matplotlib", "numpy", "pandas", "scipy",
    "PyQt6.QtQml", "PyQt6.QtQuick", "PyQt6.Qt3DCore", "PyQt6.QtWebEngineCore",
]

a = Analysis(
    [str(APP_DIR / 'main.py')],
    pathex=[str(APP_DIR / 'src')],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AITA_Grader_v1',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,          # UPX làm hỏng DLL MinGW/JDK đã ký -> tắt.
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ASSETS_DIR / "images" / "aita-avatar.png")
    if (ASSETS_DIR / "images" / "aita-avatar.png").is_file() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='AITA_Grader_v1',
)
