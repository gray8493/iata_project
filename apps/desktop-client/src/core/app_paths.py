"""
AITA Desktop Client - Runtime Path Resolution
Đóng exe bằng PyInstaller: khi frozen, assets nằm dưới sys._MEIPASS và
sys.executable trỏ tới AITA.exe (không phải trình thông dịch Python thật).
Toàn app phải resolve qua module này thay vì đoán đường dẫn.

Bản đóng gói mang theo thư mục `toolchains/` (MinGW, JDK rút gọn, Python
embeddable) đặt cạnh AITA.exe để máy giảng viên chấm được ngay cả khi chưa
cài GCC/JDK/Python.
"""

import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Thư mục con chứa toolchain portable đi kèm bản đóng gói.
TOOLCHAINS_DIR_NAME = "toolchains"

# Tên file cấu hình do hộp thoại "Cấu Hình Môi Trường" ghi ra.
CONFIG_FILE_NAME = "config.json"

# Khóa cấu hình cho từng công cụ.
CONFIG_KEYS = ("gcc_path", "javac_path", "java_path", "python_path")


def is_frozen() -> bool:
    """True khi chạy từ bản PyInstaller (không phải `python main.py`)."""
    return bool(getattr(sys, "frozen", False))


def app_assets_dir() -> Path:
    """Thư mục assets của app: dev = apps/desktop-client/assets, frozen = _MEIPASS/assets."""
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidate = Path(meipass) / "assets"
        if candidate.is_dir():
            return candidate
    return Path(__file__).resolve().parents[2] / "assets"


def bundled_toolchains_dir() -> Optional[Path]:
    """Thư mục toolchain portable đi kèm (nếu có).

    Thứ tự dò:
    1. `_MEIPASS/toolchains` (khi nhúng thẳng vào bundle).
    2. `<thư mục chứa AITA.exe>/toolchains` (khuyến nghị cho bản onedir/zip).
    3. `apps/desktop-client/toolchains` (khi chạy dev).
    """
    candidates = []
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.append(Path(meipass) / TOOLCHAINS_DIR_NAME)
    if is_frozen():
        candidates.append(Path(sys.executable).resolve().parent / TOOLCHAINS_DIR_NAME)
    candidates.append(Path(__file__).resolve().parents[2] / TOOLCHAINS_DIR_NAME)

    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return None


def app_data_dir() -> Path:
    """Thư mục dữ liệu ghi được của app (SQLite, ảnh chụp, config).

    - Dev: `apps/desktop-client/data` (giữ nguyên hành vi cũ).
    - Frozen: `%LOCALAPPDATA%/AITA/data` — KHÔNG dùng `_MEIPASS` vì đó là thư mục
      tạm bị xóa sau mỗi lần chạy, sẽ làm mất CSDL điểm của giảng viên.
    """
    if is_frozen():
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        data_dir = Path(base) / "AITA" / "data"
    else:
        data_dir = Path(__file__).resolve().parents[2] / "data"
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
    return data_dir


def app_config_path() -> Path:
    """Đường dẫn `config.json` lưu đường dẫn toolchain do giảng viên chọn tay."""
    return app_data_dir() / CONFIG_FILE_NAME


def load_config() -> Dict[str, Any]:
    """Đọc `config.json`; trả {} nếu chưa có hoặc hỏng."""
    path = app_config_path()
    try:
        if not path.is_file():
            return {}
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def save_config(updates: Dict[str, Any]) -> bool:
    """Ghi bổ sung các khóa cấu hình vào `config.json` (giữ khóa cũ)."""
    config = load_config()
    config.update({k: v for k, v in updates.items() if v is not None})
    path = app_config_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    except OSError:
        return False


def _configured(key: str) -> Optional[Path]:
    """Đường dẫn toolchain do giảng viên cấu hình tay (nếu file còn tồn tại)."""
    raw = str(load_config().get(key, "") or "").strip()
    if not raw:
        return None
    candidate = Path(raw)
    return candidate if candidate.is_file() else None


def _is_windows_store_stub(path: Path) -> bool:
    """`WindowsApps\\python.exe` là alias mở Microsoft Store, không chạy được script."""
    return "windowsapps" in str(path).lower()


def resolve_python_executable() -> str:
    """Trình thông dịch Python dùng để chạy code sinh viên.

    - Dev: sys.executable (python.exe đang chạy app).
    - Frozen: sys.executable là AITA.exe -> phải tìm python thật theo thứ tự
      toolchain đóng kèm -> config.json -> AITA_PYTHON -> PATH -> 'py'.
    """
    if not is_frozen():
        return sys.executable

    bundled = bundled_toolchains_dir()
    if bundled:
        for rel in ("python/python.exe", "python.exe", "bin/python.exe"):
            candidate = bundled / rel
            if candidate.is_file():
                return str(candidate)

    configured = _configured("python_path")
    if configured:
        return str(configured)

    override = os.environ.get("AITA_PYTHON", "").strip()
    if override and Path(override).is_file():
        return override

    for name in ("python", "python3"):
        found = shutil.which(name)
        if found and not _is_windows_store_stub(Path(found)):
            return found
    launcher = shutil.which("py")
    if launcher:
        return launcher

    raise RuntimeError(
        "Không tìm thấy Python Runtime để chấm bài! "
        "Hãy cài Python 3.11+ hoặc đặt thư mục toolchains/python cạnh AITA.exe."
    )
