"""
AITA Desktop Client - Runner Factory (Factory Method Pattern)
Dynamically creates appropriate runner based on programming language.
"""

from typing import Dict, Type
from core.runners.base_runner import BaseRunner
from core.runners.c_runner import CRunner
from core.runners.java_runner import JavaRunner
from core.runners.python_runner import PythonRunner


class RunnerFactory:
    """Factory creating BaseRunner instances for different programming languages."""

    _REGISTRY: Dict[str, Type[BaseRunner]] = {
        "C": CRunner,
        "JAVA": JavaRunner,
        "PYTHON": PythonRunner
    }

    @classmethod
    def register_runner(cls, language_key: str, runner_cls: Type[BaseRunner]):
        """Allows runtime extension for new languages (OCP compliant)."""
        cls._REGISTRY[language_key.upper()] = runner_cls

    @classmethod
    def get_runner(cls, language: str) -> BaseRunner:
        """
        Resolves language string and returns concrete BaseRunner.
        Normalizes names like 'C (Trình biên dịch GCC)' -> 'C'.
        """
        lang_upper = language.upper()
        if "JAVA" in lang_upper:
            return cls._REGISTRY["JAVA"]()
        elif "PYTHON" in lang_upper or "PY" in lang_upper:
            return cls._REGISTRY["PYTHON"]()
        elif "C" in lang_upper and "C++" not in lang_upper:
            return cls._REGISTRY["C"]()
        else:
            # Default fallback to C runner
            return cls._REGISTRY["C"]()
