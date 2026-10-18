"""
AITA Desktop Client - Runtime Path Resolution
Đóng exe bằng PyInstaller: khi frozen, assets nằm dưới sys._MEIPASS và
sys.executable trỏ tới AITA.exe (không phải trình thông dịch Python thật).
Toàn app phải resolve qua module này thay vì đoán đường dẫn.
"""

import os
import shutil
import sys
from pathlib import Path


def app_assets_dir() -> Path:
    """Thư mục assets của app: dev = apps/desktop-client/assets, frozen = _MEIPASS/assets."""
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidate = Path(meipass) / "assets"
        if candidate.is_dir():
            return candidate
    return Path(__file__).resolve().parents[2] / "assets"


def resolve_python_executable() -> str:
    """Trình thông dịch Python dùng để chạy code sinh viên.

    - Dev: sys.executable (python.exe đang chạy app).
    - Frozen: sys.executable là AITA.exe -> phải tìm python thật theo thứ tự
      biến môi trường AITA_PYTHON -> 'python' trên PATH -> 'python3' -> 'py'.
    """
    if not getattr(sys, "frozen", False):
        return sys.executable
    override = os.environ.get("AITA_PYTHON", "").strip()
    if override and Path(override).is_file():
        return override
    for name in ("python", "python3"):
        found = shutil.which(name)
        if found:
            return found
    launcher = shutil.which("py")
    if launcher:
        return launcher
    return sys.executable
