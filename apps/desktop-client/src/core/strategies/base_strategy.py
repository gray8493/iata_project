"""
AITA Desktop Client - Strategy Pattern for Output Matching
Defines the base interface IMatchingStrategy and MatchResult dataclass.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class MatchResult:
    """Encapsulates the verdict and details of an output comparison."""
    is_matched: bool
    verdict: str  # "AC" or "WA"
    score_ratio: float  # 0.0 to 1.0
    diff_details: Optional[str] = None
    message: Optional[str] = None


class IMatchingStrategy(ABC):
    """Abstract Strategy Interface for comparing program output with expected output."""

    @abstractmethod
    def compare(self, actual: str, expected: str) -> MatchResult:
        """
        Compares actual standard output with expected output.
        Returns MatchResult with verdict and diff explanation.
        """
        pass
