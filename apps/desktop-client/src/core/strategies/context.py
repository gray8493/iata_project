"""
AITA Desktop Client - Matching Context (Strategy Pattern)
Provides dynamic strategy resolution and execution for black-box testcases.
"""

from typing import Dict, Type, Optional
from .base_strategy import IMatchingStrategy, MatchResult
from .builtins import (
    ExactMatchStrategy,
    IgnoreWhitespaceStrategy,
    CaseInsensitiveStrategy,
    FloatingPointToleranceStrategy,
    UnorderedTokensStrategy,
    RegexPatternStrategy,
    SpecialJudgeStrategy,
    FlexibleMatchingStrategy
)


class MatchingContext:
    """Strategy Context to dynamically execute configured matching algorithms."""

    STRATEGY_REGISTRY: Dict[str, Type[IMatchingStrategy]] = {
        "EXACT_MATCH": ExactMatchStrategy,
        "IGNORE_WHITESPACE": IgnoreWhitespaceStrategy,
        "CASE_INSENSITIVE": CaseInsensitiveStrategy,
        "FLOAT_TOLERANCE": FloatingPointToleranceStrategy,
        "UNORDERED_TOKENS": UnorderedTokensStrategy,
        "REGEX_PATTERN": RegexPatternStrategy,
        "SPECIAL_JUDGE": SpecialJudgeStrategy,
        "FLEXIBLE": FlexibleMatchingStrategy
    }

    def __init__(self, strategy: Optional[IMatchingStrategy] = None):
        self._strategy = strategy or ExactMatchStrategy()

    def set_strategy(self, strategy: IMatchingStrategy):
        """Swaps the active matching strategy at runtime."""
        self._strategy = strategy

    def set_strategy_by_name(self, strategy_name: str, **kwargs):
        """
        Resolves strategy by name or combined flags string (e.g. 'IGNORE_WHITESPACE+CASE_INSENSITIVE').
        If multiple flags or '+' is present, delegates to FlexibleMatchingStrategy.
        """
        raw = (strategy_name or "").strip().upper()

        # If combined flags or composite pattern
        if "+" in raw or "," in raw or raw.startswith("FLAG_") or raw == "FLEXIBLE":
            flags_set = set(raw.replace(",", "+").split("+"))
            self._strategy = FlexibleMatchingStrategy(
                ignore_whitespace=("IGNORE_WHITESPACE" in flags_set),
                case_insensitive=("CASE_INSENSITIVE" in flags_set),
                floating_tolerance=("FLOAT_TOLERANCE" in flags_set or "FLOATING_POINT" in flags_set),
                unordered_tokens=("UNORDERED_TOKENS" in flags_set),
                regex_pattern=("REGEX_PATTERN" in flags_set or "REGEX" in flags_set),
                special_judge=("SPECIAL_JUDGE" in flags_set),
                **kwargs
            )
            return

        # Direct registry lookup for single strategy
        strategy_cls = self.STRATEGY_REGISTRY.get(raw, ExactMatchStrategy)
        self._strategy = strategy_cls(**kwargs)

    def compare(self, actual: str, expected: str) -> MatchResult:
        """Executes comparison using the active strategy."""
        return self._strategy.compare(actual, expected)
