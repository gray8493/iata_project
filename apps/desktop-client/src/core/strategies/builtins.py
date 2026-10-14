"""
AITA Desktop Client - Concrete Matching Strategies (7 Modes)
Implements all 7 matching algorithms required by UC-11 and design-patterns.md.
"""

import re
import math
import difflib
from collections import Counter
from typing import Optional, List

from .base_strategy import IMatchingStrategy, MatchResult


def _generate_diff(actual: str, expected: str) -> str:
    """Helper to produce unified diff lines."""
    act_lines = actual.splitlines(keepends=True)
    exp_lines = expected.splitlines(keepends=True)
    diff = difflib.unified_diff(exp_lines, act_lines, fromfile="Expected", tofile="Actual", lineterm="")
    return "".join(diff)


class ExactMatchStrategy(IMatchingStrategy):
    """Strategy 1: 100% strict character-by-character equality."""

    def compare(self, actual: str, expected: str) -> MatchResult:
        act_norm = actual.replace("\r\n", "\n").rstrip()
        exp_norm = expected.replace("\r\n", "\n").rstrip()
        if act_norm == exp_norm:
            return MatchResult(is_matched=True, verdict="AC", score_ratio=1.0, message="Khớp chính xác 100%")
        diff = _generate_diff(actual, expected)
        return MatchResult(is_matched=False, verdict="WA", score_ratio=0.0, diff_details=diff, message="Sai khác ký tự")


class IgnoreWhitespaceStrategy(IMatchingStrategy):
    """Strategy 2: Trims leading/trailing whitespace and normalizes space/newlines."""

    def compare(self, actual: str, expected: str) -> MatchResult:
        act_norm = re.sub(r"\s+", " ", actual.strip())
        exp_norm = re.sub(r"\s+", " ", expected.strip())
        if act_norm == exp_norm:
            return MatchResult(is_matched=True, verdict="AC", score_ratio=1.0, message="Khớp (bỏ qua khoảng trắng)")
        diff = _generate_diff(act_norm, exp_norm)
        return MatchResult(is_matched=False, verdict="WA", score_ratio=0.0, diff_details=diff, message="Sai khác nội dung")


class CaseInsensitiveStrategy(IMatchingStrategy):
    """Strategy 3: Ignores lowercase and uppercase differences."""

    def compare(self, actual: str, expected: str) -> MatchResult:
        act_norm = re.sub(r"\s+", " ", actual.strip().lower())
        exp_norm = re.sub(r"\s+", " ", expected.strip().lower())
        if act_norm == exp_norm:
            return MatchResult(is_matched=True, verdict="AC", score_ratio=1.0, message="Khớp (không phân biệt hoa thường)")
        diff = _generate_diff(act_norm, exp_norm)
        return MatchResult(is_matched=False, verdict="WA", score_ratio=0.0, diff_details=diff, message="Sai khác nội dung")


class FloatingPointToleranceStrategy(IMatchingStrategy):
    """Strategy 4: Compares numeric tokens with epsilon tolerance <= 1e-5."""

    def __init__(self, tolerance: float = 1e-5):
        self.tolerance = tolerance

    def compare(self, actual: str, expected: str) -> MatchResult:
        act_tokens = actual.strip().split()
        exp_tokens = expected.strip().split()

        if len(act_tokens) != len(exp_tokens):
            diff = f"Số lượng tokens không khớp: Thực tế có {len(act_tokens)}, Kỳ vọng có {len(exp_tokens)}"
            return MatchResult(is_matched=False, verdict="WA", score_ratio=0.0, diff_details=diff)

        for a, e in zip(act_tokens, exp_tokens):
            try:
                num_a = float(a)
                num_e = float(e)
                if not math.isclose(num_a, num_e, abs_tol=self.tolerance, rel_tol=self.tolerance):
                    diff = f"Giá trị số thực lệch ngoài hạn mức ({self.tolerance}): Thực tế = {num_a}, Kỳ vọng = {num_e}"
                    return MatchResult(is_matched=False, verdict="WA", score_ratio=0.0, diff_details=diff)
            except ValueError:
                # Text token fallback
                if a != e:
                    return MatchResult(is_matched=False, verdict="WA", score_ratio=0.0, diff_details=f"Token chuỗi không khớp: '{a}' != '{e}'")

        return MatchResult(is_matched=True, verdict="AC", score_ratio=1.0, message=f"Khớp số thực (sai số <= {self.tolerance})")


class UnorderedTokensStrategy(IMatchingStrategy):
    """Strategy 5: Ignores order of space-delimited words/tokens."""

    def compare(self, actual: str, expected: str) -> MatchResult:
        act_counter = Counter(actual.strip().split())
        exp_counter = Counter(expected.strip().split())

        if act_counter == exp_counter:
            return MatchResult(is_matched=True, verdict="AC", score_ratio=1.0, message="Khớp tập hợp tokens (không phân biệt thứ tự)")
        
        diff = f"Tập hợp từ không khớp:\nThực tế: {dict(act_counter)}\nKỳ vọng: {dict(exp_counter)}"
        return MatchResult(is_matched=False, verdict="WA", score_ratio=0.0, diff_details=diff)


class RegexPatternStrategy(IMatchingStrategy):
    """Strategy 6: Expected output is treated as a regular expression pattern."""

    def compare(self, actual: str, expected: str) -> MatchResult:
        try:
            pattern = re.compile(expected.strip(), re.MULTILINE | re.DOTALL)
            if pattern.search(actual.strip()):
                return MatchResult(is_matched=True, verdict="AC", score_ratio=1.0, message="Khớp biểu thức chính quy (Regex Match)")
            return MatchResult(is_matched=False, verdict="WA", score_ratio=0.0, diff_details=f"Đầu ra thực tế không khớp Regex: {expected}")
        except re.error as e:
            return MatchResult(is_matched=False, verdict="WA", score_ratio=0.0, diff_details=f"Mẫu Regex đề bài không hợp lệ: {str(e)}")


class SpecialJudgeStrategy(IMatchingStrategy):
    """Strategy 7: Evaluates output using a custom python validation script or rule."""

    def __init__(self, judge_func=None):
        self.judge_func = judge_func

    def compare(self, actual: str, expected: str) -> MatchResult:
        if self.judge_func and callable(self.judge_func):
            try:
                res = self.judge_func(actual, expected)
                if isinstance(res, bool):
                    return MatchResult(is_matched=res, verdict="AC" if res else "WA", score_ratio=1.0 if res else 0.0)
                elif isinstance(res, MatchResult):
                    return res
            except Exception as ex:
                return MatchResult(is_matched=False, verdict="WA", score_ratio=0.0, diff_details=f"Lỗi Special Judge script: {str(ex)}")

        # Default fallback: compare lines presence
        act_lines = set(actual.strip().splitlines())
        exp_lines = set(expected.strip().splitlines())
        if exp_lines.issubset(act_lines):
            return MatchResult(is_matched=True, verdict="AC", score_ratio=1.0, message="Special Judge: Chứa đầy đủ các dòng kỳ vọng")
        return MatchResult(is_matched=False, verdict="WA", score_ratio=0.0, diff_details="Thiếu các dòng nghiệm bắt buộc")


class FlexibleMatchingStrategy(IMatchingStrategy):
    """
    Composite/Flexible Matching Strategy:
    Supports combining multiple checkboxes simultaneously (e.g. IgnoreWhitespace + CaseInsensitive).
    If no flags are checked, defaults to ExactMatch (100% strict equality).
    """

    def __init__(
        self,
        ignore_whitespace: bool = False,
        case_insensitive: bool = False,
        floating_tolerance: bool = False,
        tolerance_epsilon: float = 1e-5,
        unordered_tokens: bool = False,
        regex_pattern: bool = False,
        special_judge: bool = False,
        judge_func = None
    ):
        self.ignore_whitespace = ignore_whitespace
        self.case_insensitive = case_insensitive
        self.floating_tolerance = floating_tolerance
        self.tolerance_epsilon = tolerance_epsilon
        self.unordered_tokens = unordered_tokens
        self.regex_pattern = regex_pattern
        self.special_judge = special_judge
        self.judge_func = judge_func

    def compare(self, actual: str, expected: str) -> MatchResult:
        # 1. Regex Mode
        if self.regex_pattern:
            flags = re.MULTILINE | re.DOTALL
            if self.case_insensitive:
                flags |= re.IGNORECASE
            try:
                pattern = re.compile(expected.strip(), flags)
                if pattern.search(actual.strip() if self.ignore_whitespace else actual):
                    return MatchResult(is_matched=True, verdict="AC", score_ratio=1.0, message="Khớp Regex thành công")
                return MatchResult(is_matched=False, verdict="WA", score_ratio=0.0, diff_details=f"Không khớp mẫu Regex: {expected}")
            except re.error as e:
                return MatchResult(is_matched=False, verdict="WA", score_ratio=0.0, diff_details=f"Mẫu Regex lỗi: {e}")

        # 2. Special Judge Mode
        if self.special_judge:
            sj = SpecialJudgeStrategy(judge_func=self.judge_func)
            return sj.compare(actual, expected)

        # 3. Unordered Tokens Mode
        if self.unordered_tokens:
            act_text = actual.strip().lower() if self.case_insensitive else actual.strip()
            exp_text = expected.strip().lower() if self.case_insensitive else expected.strip()
            act_tokens = act_text.split()
            exp_tokens = exp_text.split()

            if self.floating_tolerance:
                # Numeric tolerance matching without order
                if len(act_tokens) != len(exp_tokens):
                    return MatchResult(is_matched=False, verdict="WA", score_ratio=0.0,
                                       diff_details=f"Số lượng tokens không khớp: {len(act_tokens)} != {len(exp_tokens)}")
                act_nums = []
                exp_nums = []
                for a, e in zip(act_tokens, exp_tokens):
                    try:
                        act_nums.append(float(a))
                        exp_nums.append(float(e))
                    except ValueError:
                        pass
                if len(act_nums) == len(act_tokens) and len(exp_nums) == len(exp_tokens):
                    act_nums.sort()
                    exp_nums.sort()
                    for an, en in zip(act_nums, exp_nums):
                        if not math.isclose(an, en, abs_tol=self.tolerance_epsilon, rel_tol=self.tolerance_epsilon):
                            return MatchResult(is_matched=False, verdict="WA", score_ratio=0.0,
                                               diff_details=f"Số thực lệch ngưỡng ({self.tolerance_epsilon}): {an} != {en}")
                    return MatchResult(is_matched=True, verdict="AC", score_ratio=1.0, message="Khớp số thực không phân biệt thứ tự")

            if Counter(act_tokens) == Counter(exp_tokens):
                return MatchResult(is_matched=True, verdict="AC", score_ratio=1.0, message="Khớp tập hợp tokens (không phân biệt thứ tự)")
            diff = f"Tập hợp tokens không khớp:\nThực tế: {dict(Counter(act_tokens))}\nKỳ vọng: {dict(Counter(exp_tokens))}"
            return MatchResult(is_matched=False, verdict="WA", score_ratio=0.0, diff_details=diff)

        # 4. Floating Point Tolerance Mode
        if self.floating_tolerance:
            fp = FloatingPointToleranceStrategy(tolerance=self.tolerance_epsilon)
            res = fp.compare(actual, expected)
            if res.is_matched or not self.case_insensitive:
                return res

        # 5. Text Normalization (Ignore Whitespace & Case Insensitive & Exact)
        act_proc = actual
        exp_proc = expected

        if self.ignore_whitespace:
            act_proc = re.sub(r"\s+", " ", act_proc.strip())
            exp_proc = re.sub(r"\s+", " ", exp_proc.strip())

        if self.case_insensitive:
            act_proc = act_proc.lower()
            exp_proc = exp_proc.lower()

        if act_proc == exp_proc:
            msg_parts = []
            if self.ignore_whitespace: msg_parts.append("bỏ qua khoảng trắng")
            if self.case_insensitive: msg_parts.append("không phân biệt hoa thường")
            msg = f"Khớp tiêu chí ({', '.join(msg_parts)})" if msg_parts else "Khớp chính xác 100%"
            return MatchResult(is_matched=True, verdict="AC", score_ratio=1.0, message=msg)

        diff = _generate_diff(act_proc, exp_proc)
        return MatchResult(is_matched=False, verdict="WA", score_ratio=0.0, diff_details=diff, message="Sai khác kết quả đầu ra")
