"""
AITA Desktop Client - Auto-Update Service.

Luồng: kiểm tra phiên bản qua backend (/system/version) -> tải artifact
(.exe hoặc .zip) từ GitHub Release -> xác minh SHA-256 -> thay thế qua
"cầu nối" update.bat (vì Windows không cho ghi đè file đang chạy).

An toàn:
- Chỉ chấp nhận URL https.
- Nếu manifest có SHA-256 thì bắt buộc khớp mới tiến hành cập nhật.
- Không thay thế file khi chạy ở chế độ dev (chưa đóng gói), trừ khi bật cờ
  môi trường AITA_ALLOW_DEV_UPDATE=1.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import httpx

from core.version import APP_VERSION
from services.api_client import ApiClient, parse_json

ProgressCallback = Callable[[int, int], None]
CancelCheck = Callable[[], bool]

_DOWNLOAD_CHUNK = 256 * 1024
_MAX_WAIT_LOOPS = 120


class UpdateError(Exception):
    """Lỗi trong quá trình kiểm tra/tải/cập nhật."""


class UpdateCancelled(UpdateError):
    """Người dùng hủy tải."""


@dataclass
class UpdateArtifact:
    artifact_type: str  # "exe" | "zip"
    url: str
    sha256: str
    size_bytes: int
    entrypoint: str


@dataclass
class UpdateInfo:
    latest_version: str
    min_supported_version: str
    mandatory: bool
    notes: str
    published_at: str
    artifact: UpdateArtifact


def parse_version(value: str) -> tuple[int, ...]:
    """Chuyển chuỗi version thành tuple số để so sánh (vd '2.5.0' -> (2,5,0))."""
    parts: list[int] = []
    for token in str(value or "").strip().split("."):
        digits = "".join(ch for ch in token if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def is_newer(remote: str, current: str = APP_VERSION) -> bool:
    """True nếu `remote` mới hơn `current` (so sánh kiểu semantic, cắt đuôi 0)."""
    r = parse_version(remote)
    c = parse_version(current)
    length = max(len(r), len(c))
    r = r + (0,) * (length - len(r))
    c = c + (0,) * (length - len(c))
    return r > c


def is_frozen() -> bool:
    """Đang chạy bản đóng gói (PyInstaller) hay môi trường dev."""
    return bool(getattr(sys, "frozen", False))


def _sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_sha256(path: Path, expected: str) -> bool:
    """So khớp checksum; nếu manifest không cung cấp expected thì trả True."""
    if not expected:
        return True
    return _sha256_of(path).lower() == expected.strip().lower()


def build_update_script(
    *,
    artifact_type: str,
    install_dir: str,
    exe_name: str,
    pid: int,
    artifact_path: Optional[str] = None,
    payload_dir: Optional[str] = None,
) -> str:
    """Sinh nội dung update.bat dùng để thay file sau khi app thoát.

    - artifact_type == "exe": copy đè file exe mới.
    - artifact_type == "zip": robocopy thư mục payload (đã giải nén) đè lên
      thư mục cài đặt, loại trừ dữ liệu người dùng (data/, *.db).
    """
    wait_block = (
        "set /a TRIES=0\r\n"
        ":wait\r\n"
        "tasklist /FI \"PID eq %PID%\" 2>nul | find \"%PID%\" >nul\r\n"
        "if not errorlevel 1 (\r\n"
        "  set /a TRIES+=1\r\n"
        "  if %TRIES% GEQ " + str(_MAX_WAIT_LOOPS) + " goto proceed\r\n"
        "  timeout /t 1 /nobreak >nul\r\n"
        "  goto wait\r\n"
        ")\r\n"
        ":proceed\r\n"
    )

    if artifact_type == "exe":
        target = str(Path(install_dir) / exe_name)
        body = (
            'copy /Y "%NEW%" "%TARGET%" >nul\r\n'
            'start "" "%TARGET%"\r\n'
        ).format(NEW=artifact_path, TARGET=target)
        head = (
            "set \"PID={pid}\"\r\n"
            "set \"NEW={new}\"\r\n"
            "set \"TARGET={target}\"\r\n"
        ).format(pid=pid, new=artifact_path, target=target)
    else:
        target_exe = str(Path(install_dir) / exe_name)
        body = (
            'robocopy "%SRC%" "%TARGET%" /E /XF *.db *.db-wal *.db-shm /XD data '
            "/R:3 /W:1 >nul\r\n"
            'start "" "%TARGET_EXE%"\r\n'
        ).format(SRC=payload_dir, TARGET=install_dir, TARGET_EXE=target_exe)
        head = (
            "set \"PID={pid}\"\r\n"
            "set \"SRC={src}\"\r\n"
            "set \"TARGET={target}\"\r\n"
            "set \"TARGET_EXE={target_exe}\"\r\n"
        ).format(pid=pid, src=payload_dir, target=install_dir, target_exe=target_exe)

    return (
        "@echo off\r\n"
        "setlocal\r\n"
        + head
        + wait_block
        + body
        + 'del "%~f0"\r\n'
        + "endlocal\r\n"
    )


class UpdateService:
    """Client cho endpoint /system/version + tải và thay thế artifact."""

    def __init__(self, api_client: Optional[ApiClient] = None, current_version: str = APP_VERSION):
        self.api_client = api_client or ApiClient.get_instance()
        self.current_version = current_version

    # ------------------------------------------------------------------ check
    def check_for_update(self) -> Optional[UpdateInfo]:
        """Trả UpdateInfo nếu có bản mới hơn; None nếu đã mới nhất hoặc lỗi mạng."""
        try:
            resp = self.api_client.get("system/version")
        except Exception:
            return None
        if resp.status_code != 200:
            return None

        payload = parse_json(resp)
        if not payload:
            return None
        data = payload.get("data", payload) or {}
        info = self._parse_manifest(data)
        if info is None:
            return None
        return info if is_newer(info.latest_version, self.current_version) else None

    @staticmethod
    def _parse_manifest(data: Dict[str, Any]) -> Optional[UpdateInfo]:
        windows = (data.get("platforms") or {}).get("windows") or {}
        artifact_type = str(windows.get("artifact_type") or "exe").lower()
        if artifact_type not in ("exe", "zip"):
            artifact_type = "exe"

        artifact = UpdateArtifact(
            artifact_type=artifact_type,
            url=str(windows.get("url") or ""),
            sha256=str(windows.get("sha256") or ""),
            size_bytes=int(windows.get("size_bytes") or 0),
            entrypoint=str(windows.get("entrypoint") or "AITA.exe"),
        )
        return UpdateInfo(
            latest_version=str(data.get("latest_version") or "0.0.0"),
            min_supported_version=str(data.get("min_supported_version") or "0.0.0"),
            mandatory=bool(data.get("mandatory")),
            notes=str(data.get("notes") or ""),
            published_at=str(data.get("published_at") or ""),
            artifact=artifact,
        )

    # --------------------------------------------------------------- download
    def download(
        self,
        artifact: UpdateArtifact,
        dest_dir: Path,
        progress_cb: Optional[ProgressCallback] = None,
        cancel_check: Optional[CancelCheck] = None,
    ) -> Path:
        """Tải artifact về dest_dir, xác minh SHA-256, trả đường dẫn file."""
        if not artifact.url.lower().startswith("https://"):
            raise UpdateError("Chỉ chấp nhận URL tải an toàn (https).")

        dest_dir.mkdir(parents=True, exist_ok=True)
        filename = self._filename_for(artifact)
        final_path = dest_dir / filename
        part_path = final_path.with_suffix(final_path.suffix + ".part")

        downloaded = 0
        timeout = httpx.Timeout(30.0, read=180.0)
        try:
            with httpx.Client(timeout=timeout, follow_redirects=True) as client:
                with client.stream("GET", artifact.url) as resp:
                    resp.raise_for_status()
                    total = int(resp.headers.get("Content-Length") or artifact.size_bytes or 0)
                    with open(part_path, "wb") as handle:
                        for chunk in resp.iter_bytes(chunk_size=_DOWNLOAD_CHUNK):
                            if cancel_check and cancel_check():
                                raise UpdateCancelled("Đã hủy tải bản cập nhật.")
                            handle.write(chunk)
                            downloaded += len(chunk)
                            if progress_cb:
                                progress_cb(downloaded, total)
        except UpdateError:
            part_path.unlink(missing_ok=True)
            raise
        except httpx.HTTPError as exc:
            part_path.unlink(missing_ok=True)
            raise UpdateError(f"Tải thất bại: {exc}") from exc

        if not verify_sha256(part_path, artifact.sha256):
            part_path.unlink(missing_ok=True)
            raise UpdateError("Checksum SHA-256 không khớp. Đã hủy cập nhật để bảo đảm an toàn.")

        part_path.replace(final_path)
        return final_path

    @staticmethod
    def _filename_for(artifact: UpdateArtifact) -> str:
        raw = artifact.url.rstrip("/").split("/")[-1].split("?")[0]
        if not raw:
            raw = artifact.entrypoint if artifact.artifact_type == "exe" else "AITA-update.zip"
        return raw

    # ------------------------------------------------------------------ apply
    def apply_update(
        self,
        artifact: UpdateArtifact,
        artifact_path: Path,
        install_dir: Optional[Path] = None,
        pid: Optional[int] = None,
    ) -> bool:
        """Tạo update.bat và khởi chạy nó (detached). Trả True nếu đã kích hoạt.

        Caller phải gọi QApplication.quit() ngay sau khi hàm này trả True.
        """
        if not is_frozen() and os.getenv("AITA_ALLOW_DEV_UPDATE") != "1":
            raise UpdateError("Tính năng tự cập nhật chỉ khả dụng trên bản cài đặt (đã đóng gói).")

        target_dir = Path(install_dir) if install_dir else Path(sys.executable).resolve().parent
        exe_name = artifact.entrypoint or Path(sys.executable).name
        current_pid = pid if pid is not None else os.getpid()

        work_dir = Path(tempfile.mkdtemp(prefix="AITA_update_"))
        payload_dir: Optional[Path] = None
        if artifact.artifact_type == "zip":
            payload_dir = work_dir / "payload"
            self._extract_zip(artifact_path, payload_dir)

        script = build_update_script(
            artifact_type=artifact.artifact_type,
            install_dir=str(target_dir),
            exe_name=exe_name,
            pid=current_pid,
            artifact_path=str(artifact_path),
            payload_dir=str(payload_dir) if payload_dir else None,
        )
        script_path = work_dir / "update.bat"
        script_path.write_text(script, encoding="utf-8")

        creationflags = 0
        if sys.platform.startswith("win"):
            creationflags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(
                subprocess, "CREATE_NEW_PROCESS_GROUP", 0
            )
        subprocess.Popen(
            ["cmd", "/c", str(script_path)],
            creationflags=creationflags,
            close_fds=True,
        )
        return True

    @staticmethod
    def _extract_zip(archive: Path, dest_dir: Path) -> None:
        dest_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive) as zf:
            for member in zf.namelist():
                member_path = Path(member)
                if member_path.is_absolute() or ".." in member_path.parts:
                    raise UpdateError("Gói cập nhật chứa đường dẫn không hợp lệ.")
            zf.extractall(dest_dir)
