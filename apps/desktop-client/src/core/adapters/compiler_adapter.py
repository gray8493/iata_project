"""
AITA Desktop Client - Compiler Adapter (Adapter Pattern)
Adapts the heterogeneous C/Java/Python toolchains (GCC, Javac, CPython) behind a single
`CompilerAdapter.compile()` contract that always returns a normalized `CompileResult`.
This isolates the runners from compiler-specific command syntax and error output.
"""

import os
import shutil
import subprocess
import py_compile
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Type


@dataclass
class CompileResult:
    """Normalized outcome shared by every adapted toolchain."""
    success: bool
    log: str
    target: Optional[str] = None
    compiler: str = ""
    timed_out: bool = False

    @property
    def verdict(self) -> str:
        """CE when compilation failed, otherwise OK."""
        return "OK" if self.success else "CE"


def find_gcc_executable() -> Optional[str]:
    """Tự động tìm kiếm đường dẫn thực thi của gcc trên hệ thống Windows."""
    cand = shutil.which("gcc")
    if cand:
        return cand

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

    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        winget_links = Path(local_app_data) / "Microsoft" / "WinGet" / "Links" / "gcc.exe"
        if winget_links.is_file():
            return str(winget_links)

        winget_pkgs = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
        if winget_pkgs.exists():
            for g in winget_pkgs.glob("**/bin/gcc.exe"):
                return str(g)

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


class CompilerAdapter(ABC):
    """Target interface: unify toolchain-specific compilation into CompileResult."""

    name = "compiler"
    source_extension = ""

    def __init__(self, timeout: float = 12.0):
        self.timeout = timeout

    @abstractmethod
    def compile(self, source_path: Path) -> CompileResult:
        """Compiles the source file and returns a normalized CompileResult."""
        raise NotImplementedError

    def _missing_source(self, source_path: Path) -> CompileResult:
        return CompileResult(False, f"Không tìm thấy file mã nguồn: {source_path}", compiler=self.name)


class GccCompilerAdapter(CompilerAdapter):
    """Adapts the GCC toolchain (C) to the unified interface."""

    name = "GCC"
    source_extension = ".c"

    def compile(self, source_path: Path) -> CompileResult:
        if not source_path.exists():
            return self._missing_source(source_path)

        gcc_bin = find_gcc_executable()
        if not gcc_bin:
            return CompileResult(
                False,
                "Không tìm thấy trình biên dịch 'gcc' trên hệ thống! Vui lòng cài đặt MinGW/GCC.",
                compiler=self.name
            )

        output_exe = source_path.parent / f"{source_path.stem}_build.exe"
        cmd = [gcc_bin, str(source_path), "-o", str(output_exe), "-O2", "-std=c11", "-Wall"]

        gcc_dir = str(Path(gcc_bin).parent)
        env = os.environ.copy()
        env["PATH"] = gcc_dir + os.pathsep + env.get("PATH", "")

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout, env=env)
            if res.returncode != 0:
                return CompileResult(False, res.stderr or res.stdout, compiler=self.name)
            return CompileResult(True, "Biên dịch thành công", str(output_exe), self.name)
        except FileNotFoundError:
            return CompileResult(
                False,
                "Không tìm thấy trình biên dịch 'gcc' trên hệ thống! Vui lòng cài đặt MinGW/GCC.",
                compiler=self.name
            )
        except subprocess.TimeoutExpired:
            return CompileResult(False, "Quá thời gian biên dịch (Compile Timeout)", compiler=self.name, timed_out=True)
        except Exception as ex:
            return CompileResult(False, f"Lỗi biên dịch: {str(ex)}", compiler=self.name)


class JavacCompilerAdapter(CompilerAdapter):
    """Adapts the OpenJDK `javac` toolchain (Java) to the unified interface."""

    name = "JAVAC"
    source_extension = ".java"

    def compile(self, source_path: Path) -> CompileResult:
        if not source_path.exists():
            return self._missing_source(source_path)

        cmd = ["javac", "-encoding", "UTF-8", str(source_path)]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout)
            if res.returncode != 0:
                return CompileResult(False, res.stderr or res.stdout, compiler=self.name)

            class_name = source_path.stem
            return CompileResult(True, "Biên dịch Java thành công", f"{source_path.parent}:{class_name}", self.name)
        except FileNotFoundError:
            return CompileResult(
                False,
                "Không tìm thấy trình biên dịch 'javac' (JDK)! Vui lòng kiểm tra biến môi trường JAVA_HOME.",
                compiler=self.name
            )
        except subprocess.TimeoutExpired:
            return CompileResult(False, "Quá thời gian biên dịch Java", compiler=self.name, timed_out=True)
        except Exception as ex:
            return CompileResult(False, f"Lỗi biên dịch Java: {str(ex)}", compiler=self.name)


class PythonInterpreterAdapter(CompilerAdapter):
    """Adapts the CPython runtime (syntax validation via py_compile) to the unified interface."""

    name = "PYTHON"
    source_extension = ".py"

    def compile(self, source_path: Path) -> CompileResult:
        if not source_path.exists():
            return self._missing_source(source_path)

        try:
            py_compile.compile(str(source_path), doraise=True)
            return CompileResult(True, "Cú pháp Python hợp lệ", str(source_path), self.name)
        except py_compile.PyCompileError as err:
            return CompileResult(False, f"Lỗi cú pháp Python (Syntax Error):\n{str(err)}", compiler=self.name)
        except Exception as ex:
            return CompileResult(False, f"Lỗi kiểm tra mã nguồn: {str(ex)}", compiler=self.name)


class CompilerAdapterFactory:
    """Resolves the correct CompilerAdapter implementation from a language label."""

    ADAPTERS: Dict[str, Type[CompilerAdapter]] = {
        "C": GccCompilerAdapter,
        "GCC": GccCompilerAdapter,
        "JAVA": JavacCompilerAdapter,
        "PYTHON": PythonInterpreterAdapter,
        "PY": PythonInterpreterAdapter,
    }

    @classmethod
    def get_adapter(cls, language: str, timeout: float = 12.0) -> CompilerAdapter:
        key = (language or "").strip().upper()
        for alias, adapter_cls in cls.ADAPTERS.items():
            if alias in key:
                return adapter_cls(timeout=timeout)
        return GccCompilerAdapter(timeout=timeout)


def get_compiler_adapter(language: str, timeout: float = 12.0) -> CompilerAdapter:
    """Convenience wrapper around CompilerAdapterFactory.get_adapter."""
    return CompilerAdapterFactory.get_adapter(language, timeout=timeout)
