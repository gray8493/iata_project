"""
AITA Desktop Client - C Language Runner (GCC Compiler)
Compiles C source (.c) into executable and runs through main() function.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Tuple, Optional

from .base_runner import BaseRunner
from core.sandbox.runner import SandboxRunner, SandboxResult


def find_gcc_executable() -> Optional[str]:
    """Tự động tìm kiếm đường dẫn thực thi của gcc trên hệ thống Windows."""
    # 1. Kiểm tra PATH hiện tại
    cand = shutil.which("gcc")
    if cand:
        return cand

    # 2. Kiểm tra PATH từ Windows Registry (khi vừa cài đặt mà tiến trình chưa refresh PATH)
    try:
        import winreg
        for root, sub in [
            (winreg.HKEY_CURRENT_USER, r"Environment"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
        ]:
            try:
                with winreg.OpenKey(root, sub) as key:
                    path_val, _ = winreg.QueryValueEx(key, "PATH")
                    for p in str(path_val).split(";"):
                        p_expanded = os.path.expandvars(p.strip())
                        gcc_p = Path(p_expanded) / "gcc.exe"
                        if gcc_p.is_file():
                            return str(gcc_p)
            except Exception:
                pass
    except Exception:
        pass

    # 3. Quét các thư mục WinGet Packages và Links
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        winget_links = Path(local_app_data) / "Microsoft" / "WinGet" / "Links" / "gcc.exe"
        if winget_links.is_file():
            return str(winget_links)

        winget_pkgs = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
        if winget_pkgs.exists():
            for g in winget_pkgs.glob("**/bin/gcc.exe"):
                return str(g)

    # 4. Các thư mục cài đặt MinGW / MSYS thông dụng
    common_paths = [
        Path("C:/mingw64/bin/gcc.exe"),
        Path("C:/msys64/ucrt64/bin/gcc.exe"),
        Path("C:/msys64/mingw64/bin/gcc.exe"),
        Path("C:/Program Files/mingw64/bin/gcc.exe"),
        Path("C:/MinGW/bin/gcc.exe"),
    ]
    for cp in common_paths:
        if cp.is_file():
            return str(cp)

    return None


class CRunner(BaseRunner):
    """Runner for C language (PRF192)."""

    def compile(self, source_path: Path) -> Tuple[bool, str, Optional[str]]:
        if not source_path.exists():
            return False, f"Không tìm thấy file mã nguồn: {source_path}", None

        gcc_bin = find_gcc_executable()
        if not gcc_bin:
            return False, "Không tìm thấy trình biên dịch 'gcc' trên hệ thống! Vui lòng cài đặt MinGW/GCC.", None

        # Build output binary target
        output_exe = source_path.parent / f"{source_path.stem}_build.exe"
        cmd = [gcc_bin, str(source_path), "-o", str(output_exe), "-O2", "-std=c11", "-Wall"]

        # Đảm bảo thư mục bin của gcc có trong PATH để các công cụ như cc1.exe hoạt động đúng
        gcc_dir = str(Path(gcc_bin).parent)
        env = os.environ.copy()
        env["PATH"] = gcc_dir + os.pathsep + env.get("PATH", "")

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10.0, env=env)
            if res.returncode != 0:
                return False, res.stderr or res.stdout, None
            return True, "Biên dịch thành công", str(output_exe)
        except FileNotFoundError:
            return False, "Không tìm thấy trình biên dịch 'gcc' trên hệ thống! Vui lòng cài đặt MinGW/GCC.", None
        except subprocess.TimeoutExpired:
            return False, "Quá thời gian biên dịch (Compile Timeout)", None
        except Exception as ex:
            return False, f"Lỗi biên dịch: {str(ex)}", None

    def execute(
        self,
        executable_target: str,
        input_data: str = "",
        time_limit_ms: int = 1000,
        memory_limit_mb: int = 128
    ) -> SandboxResult:
        exe_path = Path(executable_target)
        return SandboxRunner.run_process(
            command=[str(exe_path)],
            input_data=input_data,
            time_limit_ms=time_limit_ms,
            memory_limit_mb=memory_limit_mb,
            cwd=str(exe_path.parent)
        )
