"""
AITA Desktop Client - Python Language Runner (Python 3.x Runtime)
Validates Python syntax via py_compile and runs script through main execution.
"""

import sys
import py_compile
from pathlib import Path
from typing import Tuple, Optional

from .base_runner import BaseRunner
from core.sandbox.runner import SandboxRunner, SandboxResult


class PythonRunner(BaseRunner):
    """Runner for Python language (PHP, PRO, DSA)."""

    def compile(self, source_path: Path) -> Tuple[bool, str, Optional[str]]:
        if not source_path.exists():
            return False, f"Không tìm thấy file mã nguồn: {source_path}", None

        # Check Python syntax offline using py_compile
        try:
            py_compile.compile(str(source_path), doraise=True)
            return True, "Cú pháp Python hợp lệ", str(source_path)
        except py_compile.PyCompileError as err:
            return False, f"Lỗi cú pháp Python (Syntax Error):\n{str(err)}", None
        except Exception as ex:
            return False, f"Lỗi kiểm tra mã nguồn: {str(ex)}", None

    def execute(
        self,
        executable_target: str,
        input_data: str = "",
        time_limit_ms: int = 2000,
        memory_limit_mb: int = 128
    ) -> SandboxResult:
        script_path = Path(executable_target)
        cmd = [sys.executable, "-u", str(script_path)]

        return SandboxRunner.run_process(
            command=cmd,
            input_data=input_data,
            time_limit_ms=time_limit_ms,
            memory_limit_mb=memory_limit_mb,
            cwd=str(script_path.parent)
        )
