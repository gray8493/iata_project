"""
AITA Desktop Client - Python Language Runner (Python 3.x Runtime)
Validates Python syntax via py_compile and runs script through main execution.
"""

import sys
from pathlib import Path
from typing import Tuple, Optional

from .base_runner import BaseRunner
from core.sandbox.runner import SandboxRunner, SandboxResult
from core.adapters.compiler_adapter import PythonInterpreterAdapter


class PythonRunner(BaseRunner):
    """Runner for Python language (PHP, PRO, DSA)."""

    def __init__(self):
        self.adapter = PythonInterpreterAdapter()

    def compile(self, source_path: Path) -> Tuple[bool, str, Optional[str]]:
        result = self.adapter.compile(source_path)
        return result.success, result.log, result.target

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
