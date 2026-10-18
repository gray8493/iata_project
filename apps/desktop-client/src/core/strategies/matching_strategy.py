"""
AITA Desktop Client - MatchingStrategy Options Facade (Strategy Pattern)
Exposes the public `MatchingStrategy.compare(actual, expected, options)` API documented by
UT01_MatchingStrategy testcases. Options are translated into the appropriate concrete
IMatchingStrategy implementation (Exact / IgnoreWhitespace / CaseInsensitive /
FloatingPointTolerance / UnorderedTokens / RegexPattern / SpecialJudge / Flexible).
"""

from typing import Any, Dict, Optional, Type

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

DEFAULT_EPSILON = 1e-5
NULL_INPUT_MESSAGE = "Đầu ra thực tế hoặc kết quả kỳ vọng bị null/undefined."


class MatchingStrategy:
    """Options-driven façade around the concrete matching strategies."""

    NAME_TO_CLASS: Dict[str, Type[IMatchingStrategy]] = {
        "EXACT_MATCH": ExactMatchStrategy,
        "IGNORE_WHITESPACE": IgnoreWhitespaceStrategy,
        "CASE_INSENSITIVE": CaseInsensitiveStrategy,
        "FLOAT_TOLERANCE": FloatingPointToleranceStrategy,
        "FLOATING_POINT": FloatingPointToleranceStrategy,
        "UNORDERED_TOKENS": UnorderedTokensStrategy,
        "REGEX_PATTERN": RegexPatternStrategy,
        "REGEX": RegexPatternStrategy,
        "SPECIAL_JUDGE": SpecialJudgeStrategy,
        "FLEXIBLE": FlexibleMatchingStrategy
    }

    def __init__(self, strategy_name: str = "EXACT_MATCH", **kwargs):
        self.strategy_name = (strategy_name or "EXACT_MATCH").strip().upper()
        self.kwargs = kwargs

    def compare(self, actual: Optional[str], expected: Optional[str], options: Optional[Dict[str, Any]] = None) -> bool:
        """Returns True (AC) when the actual output matches the expected output, else False (WA)."""
        return self.compare_detailed(actual, expected, options).is_matched

    def compare_detailed(
        self,
        actual: Optional[str],
        expected: Optional[str],
        options: Optional[Dict[str, Any]] = None
    ) -> MatchResult:
        """Same as compare() but returns the full MatchResult (verdict, diff details, message)."""
        opts = dict(options or {})

        if actual is None or expected is None:
            return MatchResult(
                is_matched=False,
                verdict="WA",
                score_ratio=0.0,
                diff_details=NULL_INPUT_MESSAGE,
                message=NULL_INPUT_MESSAGE
            )

        actual_text = actual if isinstance(actual, str) else str(actual)
        expected_text = expected if isinstance(expected, str) else str(expected)

        if opts.get("ignoreTrailingWhitespace"):
            actual_text = actual_text.rstrip()
            expected_text = expected_text.rstrip()

        strategy = self._build_strategy(opts)
        return strategy.compare(actual_text, expected_text)

    def _build_strategy(self, options: Dict[str, Any]) -> IMatchingStrategy:
        ignore_ws = bool(options.get("ignoreWhitespace") or options.get("trimWhitespace"))
        case_insensitive = bool(options.get("caseInsensitive"))
        unordered = bool(options.get("unorderedTokens"))
        regex = bool(options.get("regex") or options.get("regexPattern"))
        special = bool(options.get("specialJudge"))
        epsilon = options.get("epsilon", options.get("tolerance"))
        float_tolerance = epsilon is not None or bool(options.get("floatTolerance"))
        resolved_epsilon = float(epsilon) if epsilon is not None else DEFAULT_EPSILON

        if regex or special or unordered:
            return FlexibleMatchingStrategy(
                ignore_whitespace=ignore_ws,
                case_insensitive=case_insensitive,
                floating_tolerance=float_tolerance,
                tolerance_epsilon=resolved_epsilon,
                unordered_tokens=unordered,
                regex_pattern=regex,
                special_judge=special
            )

        if float_tolerance:
            return FloatingPointToleranceStrategy(tolerance=resolved_epsilon)

        if ignore_ws and case_insensitive:
            return FlexibleMatchingStrategy(ignore_whitespace=True, case_insensitive=True)
        if ignore_ws:
            return IgnoreWhitespaceStrategy()
        if case_insensitive:
            return CaseInsensitiveStrategy()

        strategy_cls = self.NAME_TO_CLASS.get(self.strategy_name)
        if strategy_cls is None:
            return ExactMatchStrategy()

        try:
            return strategy_cls(**self.kwargs)
        except TypeError:
            return strategy_cls()
