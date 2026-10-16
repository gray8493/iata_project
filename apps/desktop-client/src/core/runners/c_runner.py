"""
AITA Desktop Client - C Language Runner (GCC Compiler)
Compiles C source (.c) into executable and runs through main() function.
Compilation is delegated to the GccCompilerAdapter (Adapter Pattern).
"""

from pathlib import Path
from typing import Tuple, Optional

from .base_runner import BaseRunner
from core.sandbox.runner import SandboxRunner, SandboxResult
from core.adapters.compiler_adapter import GccCompilerAdapter, find_gcc_executable

__all__ = ["CRunner", "find_gcc_executable"]


class CRunner(BaseRunner):
    """Runner for C language (PRF192)."""

    def __init__(self):
        self.adapter = GccCompilerAdapter()

    def compile(self, source_path: Path) -> Tuple[bool, str, Optional[str]]:
        result = self.adapter.compile(source_path)
        return result.success, result.log, result.target

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
