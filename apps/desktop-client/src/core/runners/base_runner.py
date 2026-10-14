"""
AITA Desktop Client - Abstract Base Runner
Defines compilation and execution contract for student source code.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Tuple, Optional
from core.sandbox.runner import SandboxRunner, SandboxResult


class BaseRunner(ABC):
    """Abstract Product in Factory Method Pattern."""

    @abstractmethod
    def compile(self, source_path: Path) -> Tuple[bool, str, Optional[str]]:
        """
        Compiles the student source file.
        Returns:
            (success: bool, compile_log: str, binary_executable_path: Optional[str])
        """
        pass

    @abstractmethod
    def execute(
        self,
        executable_target: str,
        input_data: str = "",
        time_limit_ms: int = 1000,
        memory_limit_mb: int = 128
    ) -> SandboxResult:
        """
        Executes the compiled binary or script via SandboxRunner.
        """
        pass
