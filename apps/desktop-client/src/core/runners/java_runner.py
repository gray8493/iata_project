"""
AITA Desktop Client - Java Language Runner (Javac Compiler & JVM)
Compiles Java source (.java) into bytecode (.class) and runs through main() method.
"""

from pathlib import Path
from typing import Tuple, Optional

from .base_runner import BaseRunner
from core.sandbox.runner import SandboxRunner, SandboxResult
from core.adapters.compiler_adapter import JavacCompilerAdapter


class JavaRunner(BaseRunner):
    """Runner for Java language (PRO192, CSD201)."""

    def __init__(self):
        self.adapter = JavacCompilerAdapter()

    def compile(self, source_path: Path) -> Tuple[bool, str, Optional[str]]:
        result = self.adapter.compile(source_path)
        return result.success, result.log, result.target

    def execute(
        self,
        executable_target: str,
        input_data: str = "",
        time_limit_ms: int = 1500,
        memory_limit_mb: int = 256
    ) -> SandboxResult:
        # executable_target format: "classpath:class_name"
        classpath, class_name = executable_target.split(":", 1)
        cmd = ["java", "-cp", classpath, class_name]

        return SandboxRunner.run_process(
            command=cmd,
            input_data=input_data,
            time_limit_ms=time_limit_ms,
            memory_limit_mb=memory_limit_mb,
            cwd=classpath
        )
