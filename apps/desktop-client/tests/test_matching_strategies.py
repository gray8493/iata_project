"""Matching Strategies (Strategy Pattern / core.strategies).

Covers the black-box output diffing required by IT08 (C exact match),
IT09 (Java floating point tolerance 1e-5) and IT10 (Python unordered tokens)
including boundary values: trailing whitespace, case-insensitive flags,
byte-exact default, and null/undefined inputs.
"""

import pytest

from core.strategies import (
    ExactMatchStrategy,
    IgnoreWhitespaceStrategy,
    CaseInsensitiveStrategy,
    FloatingPointToleranceStrategy,
    UnorderedTokensStrategy,
    RegexPatternStrategy,
    SpecialJudgeStrategy,
    FlexibleMatchingStrategy,
    MatchingStrategy,
    MatchingContext,
)


# ------------------------------------------------------------------------------
# Strategy 1: ExactMatch (IT08 - C baseline, byte-exact)
# ------------------------------------------------------------------------------
def test_exact_match_ac_on_identical_output():
    res = ExactMatchStrategy().compare("Hello AITA\n", "Hello AITA")
    assert res.is_matched and res.verdict == "AC" and res.score_ratio == 1.0


def test_exact_match_tolerates_crlf_and_trailing_newline_only():
    assert ExactMatchStrategy().compare("out\r\n", "out\n").is_matched


def test_exact_match_wa_on_any_character_difference():
    res = ExactMatchStrategy().compare("Hello Aita", "Hello AITA")
    assert not res.is_matched and res.verdict == "WA" and res.diff_details


def test_exact_match_wa_on_internal_or_leading_difference():
    # rstrip tolerates trailing spaces; leading/internal content stays byte-exact.
    assert not ExactMatchStrategy().compare("  out", "out").is_matched
    assert not ExactMatchStrategy().compare("o u t", "out").is_matched


# ------------------------------------------------------------------------------
# Strategy 2/3: IgnoreWhitespace / CaseInsensitive
# ------------------------------------------------------------------------------
def test_ignore_whitespace_ac_across_blank_lines_and_indentation():
    res = IgnoreWhitespaceStrategy().compare("a  b\n\nc", "a b c")
    assert res.is_matched and res.verdict == "AC"


def test_case_insensitive_ac_on_case_mismatch():
    res = CaseInsensitiveStrategy().compare("YES", "yes")
    assert res.is_matched


def test_case_insensitive_wa_when_letters_differ():
    assert not CaseInsensitiveStrategy().compare("YESO", "YES").is_matched


# ------------------------------------------------------------------------------
# Strategy 4: FloatingPointTolerance (IT09 - Java DSA, delta <= 10**-5)
# ------------------------------------------------------------------------------
def test_float_tolerance_ac_within_epsilon():
    res = FloatingPointToleranceStrategy().compare("3.141592 2.0", "3.14159 2.0")
    assert res.is_matched and res.verdict == "AC"


def test_float_tolerance_wa_outside_epsilon():
    res = FloatingPointToleranceStrategy().compare("0.00001", "0.00003")
    assert not res.is_matched and res.verdict == "WA"


def test_float_tolerance_wa_on_token_count_mismatch():
    assert not FloatingPointToleranceStrategy().compare("1.0 2.0", "1.0").is_matched


def test_float_tolerance_custom_configured_epsilon():
    assert FloatingPointToleranceStrategy(tolerance=0.5).compare("3.3", "3.1").is_matched


# ------------------------------------------------------------------------------
# Strategy 5: UnorderedTokens (IT10 - Python list output, order-independent)
# ------------------------------------------------------------------------------
def test_unordered_tokens_ac_on_reordered_list():
    res = UnorderedTokensStrategy().compare("12 6 4 3 2 1", "1 2 3 4 6 12")
    assert res.is_matched and res.verdict == "AC"


def test_unordered_tokens_wa_on_duplicate_count_mismatch():
    assert not UnorderedTokensStrategy().compare("a a b", "a b b").is_matched


# ------------------------------------------------------------------------------
# Strategy 6/7: Regex + SpecialJudge
# ------------------------------------------------------------------------------
def test_regex_pattern_ac_on_partial_search_match():
    assert RegexPatternStrategy().compare("MSSV: SE180001 done", r"SE18\d+").is_matched


def test_regex_pattern_wa_on_invalid_pattern():
    res = RegexPatternStrategy().compare("x", r"[unclosed")
    assert not res.is_matched and res.diff_details


def test_special_judge_uses_custom_judge_function():
    res = SpecialJudgeStrategy(judge_func=lambda act, exp: float(act) > float(exp)) \
        .compare("9.5", "8.0")
    assert res.is_matched and res.verdict == "AC"


def test_special_judge_captures_judge_exception_as_wa():
    def boom(_a, _e):
        raise ValueError("checker crash")

    res = SpecialJudgeStrategy(judge_func=boom).compare("x", "y")
    assert not res.is_matched and "Special Judge" in res.diff_details


def test_special_judge_fallback_checks_required_line_subset():
    res = SpecialJudgeStrategy().compare("line1\nline2\nextra", "line1\nline2")
    assert res.is_matched


# ------------------------------------------------------------------------------
# Strategy: FlexibleMatchingStrategy (multi-flag composite)
# ------------------------------------------------------------------------------
def test_flexible_combines_ignore_whitespace_and_case_insensitive():
    flex = FlexibleMatchingStrategy(ignore_whitespace=True, case_insensitive=True)
    assert flex.compare("  HE  LLO  ", "he llo").is_matched
    assert not flex.compare("abc", "abd").is_matched


def test_flexible_defaults_to_exact_when_no_flags():
    flex = FlexibleMatchingStrategy()
    assert flex.compare("out", "out").is_matched
    assert not flex.compare("out\n", "outx").is_matched


# ------------------------------------------------------------------------------
# MatchingContext (Strategy Context, runtime swapping)
# ------------------------------------------------------------------------------
def test_context_default_strategy_is_exact_match():
    ctx = MatchingContext()
    assert ctx.compare("a", "b").verdict == "WA"
    assert ctx.compare("a", "a").verdict == "AC"


def test_context_resolves_single_strategy_by_name():
    ctx = MatchingContext()
    ctx.set_strategy_by_name("CASE_INSENSITIVE")
    assert ctx.compare("YES", "yes").is_matched


def test_context_resolves_combined_flags_via_flexible():
    ctx = MatchingContext()
    ctx.set_strategy_by_name("IGNORE_WHITESPACE+CASE_INSENSITIVE")
    assert ctx.compare("  A  B ", "a b").is_matched


def test_context_unknown_name_falls_back_to_exact_match():
    ctx = MatchingContext()
    ctx.set_strategy_by_name("NOT_A_STRATEGY")
    # Falls back to byte-exact: identical content passes after rstrip, others WA.
    assert ctx.compare("out", "out\n").is_matched
    assert ctx.compare("out", "other").verdict == "WA"


# ------------------------------------------------------------------------------
# MatchingStrategy facade (options-driven public API)
# ------------------------------------------------------------------------------
def test_facade_exact_match_default():
    assert MatchingStrategy("EXACT_MATCH").compare("1 2", "1 2") is True
    assert MatchingStrategy("EXACT_MATCH").compare("1 2", "2 1") is False


def test_facade_float_tolerance_via_options():
    res = MatchingStrategy().compare_detailed("3.141592", "3.14159", {"floatTolerance": True})
    assert res.is_matched and res.verdict == "AC"


def test_facade_unordered_tokens_via_options():
    assert MatchingStrategy().compare("b a", "a b", {"unorderedTokens": True}) is True


def test_facade_wa_on_null_actual_or_expected():
    for actual, expected in ((None, "out"), ("out", None)):
        res = MatchingStrategy().compare_detailed(actual, expected)
        assert res.verdict == "WA" and not res.is_matched


def test_facade_unknown_strategy_name_falls_back_to_exact():
    assert MatchingStrategy("WHATEVER").compare("a\n", "b") is False
    assert MatchingStrategy("WHATEVER").compare("a", "a") is True
