"""
AITA Desktop Client - Offline Plagiarism Engine (Stage 1)
========================================================
Implements UC-17 / IT13 / ST03_TC001: a 100% offline, MOSS-like plagiarism
detector based on source-code normalization, k-gram fingerprinting and the
Winnowing algorithm.

Pipeline:
  1. Lexical normalization  -> strip comments/string/number literals, collapse
     all user identifiers to a canonical placeholder (catches variable renaming
     such as `n -> m`, `sum -> total`), keep language keywords & operators.
  2. k-gram shingling       -> sliding window of `k` normalized tokens. `k`
     shrinks for short answers (exam questions are often < 80 tokens) so a
     single answer still yields a usable fingerprint set.
  3. Winnowing              -> select the minimum hash per window `w` to obtain
     a compact, position-independent fingerprint set.
  4. Per-question units     -> multi-question submissions (folder with
     `Q1.<ext>`, `Q2.<ext>`, ...) are compared question by question. Copying a
     single answer is therefore NOT diluted by the rest of the folder, which is
     what a whole-folder comparison gets wrong (Q1 identical + Q2 different
     collapses to ~50% Jaccard and slips under the alert threshold).
  5. Class boilerplate drop -> grams appearing in most submissions of the class
     (`#include <stdio.h>`, `int main()`, `Scanner sc = ...`) are removed, the
     way MOSS ignores common templates, to cut false positives on short answers.
  6. Similarity             -> Jaccard index (%) + containment/coverage (%).
     Jaccard is fair when both answers are of similar size; containment is the
     one that catches "paste a function of a classmate into my answer". The
     headline score is the higher of the two (`sim`).

This module has no network / AI dependency; Stage 2 (AI semantic
verification) stays in `services.ai_service`.
"""

import hashlib
import itertools
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

K_GRAM = 5
WINDOW_SIZE = 4

# Bài kiểm tra trên lớp thường rất ngắn: dùng k/w nhỏ hơn để fingerprint còn đủ dày.
SHORT_DOC_TOKENS = 80
SHORT_K_GRAM = 3
SHORT_WINDOW = 3

# Bỏ qua câu quá ngắn (bài trống / stub `int main() {}`) để Jaccard không bị nhiễu.
MIN_UNIT_TOKENS = 30

# Một cặp chỉ bị coi là nghi vấn khi có đủ số gram chung, tránh báo động giả trên bài cụt.
MIN_SHARED_FINGERPRINTS = 15

# Lọc boilerplate toàn lớp: chỉ áp dụng khi lớp đủ đông để "tần suất" có ý nghĩa.
BOILERPLATE_RATIO = 0.5
BOILERPLATE_MIN_DOCS = 5

# Khóa câu mặc định cho bài nộp 1 file (đồng bộ với `question_number` mặc định trong DB).
DEFAULT_QUESTION_KEY = "Q1"

IDENTIFIER_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b")

KEYWORDS = {
    "c": {
        "auto", "break", "case", "char", "const", "continue", "default", "do",
        "double", "else", "enum", "extern", "float", "for", "goto", "if",
        "int", "long", "register", "return", "short", "signed", "sizeof",
        "static", "struct", "switch", "typedef", "union", "unsigned", "void",
        "volatile", "while", "include", "define", "NULL", "true", "false"
    },
    "java": {
        "abstract", "assert", "boolean", "break", "byte", "case", "catch",
        "char", "class", "const", "continue", "default", "do", "double",
        "else", "enum", "extends", "final", "finally", "float", "for", "goto",
        "if", "implements", "import", "instanceof", "int", "interface", "long",
        "native", "new", "package", "private", "protected", "public", "return",
        "short", "static", "strictfp", "super", "switch", "synchronized",
        "this", "throw", "throws", "transient", "try", "void", "volatile",
        "while", "String", "System", "true", "false", "null"
    },
    "python": {
        "and", "as", "assert", "async", "await", "break", "class", "continue",
        "def", "del", "elif", "else", "except", "finally", "for", "from",
        "global", "if", "import", "in", "is", "lambda", "None", "nonlocal",
        "not", "or", "pass", "raise", "return", "True", "False", "try",
        "while", "with", "yield", "print", "input", "len", "range", "int",
        "float", "str", "list", "dict", "set", "tuple", "self"
    },
}


def _normalize_language(language: str) -> str:
    low = (language or "C").lower()
    if "java" in low:
        return "java"
    if "python" in low or "py" in low:
        return "python"
    return "c"


def _strip_comments(code: str, language: str) -> str:
    """Removes line and block comments (language aware)."""
    if language == "python":
        # Remove # comments (naive but effective: not inside a quoted string).
        code = re.sub(r"(?m)#.*$", " ", code)
        return code
    code = re.sub(r"//[^\n]*", " ", code)
    code = re.sub(r"/\*.*?\*/", " ", code, flags=re.DOTALL)
    return code


_STRING_RE = re.compile(r'"(?:\\.|[^"\\])*"' r"|'(?:\\.|[^'\\])*'")
_CHAR_RE = re.compile(r"'(?:\\.|[^'\\])*'")


def _mask_literals(code: str) -> str:
    code = _STRING_RE.sub(" STR ", code)
    code = _CHAR_RE.sub(" CHR ", code)
    code = NUMBER_RE.sub(" NUM ", code)
    return code


def normalize_tokens(code: str, language: str = "C") -> List[str]:
    """
    Produces a normalized token stream:
    - comments removed, literals masked,
    - every non-keyword identifier collapsed to `ID` (defeats renaming),
    - operators / punctuation preserved as their own tokens.
    """
    lang = _normalize_language(language)
    keywords = KEYWORDS[lang]

    cleaned = _strip_comments(code, lang)
    cleaned = _mask_literals(cleaned)

    # Split identifiers while keeping operators/punctuation separate
    raw_tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*|\d+|[^\sA-Za-z0-9_]", cleaned)

    tokens: List[str] = []
    for tok in raw_tokens:
        if tok == "ID" or tok == "STR" or tok == "CHR" or tok == "NUM":
            tokens.append(tok)
        elif tok[0].isalpha() or tok[0] == "_":
            if tok in keywords:
                tokens.append(tok)
            else:
                tokens.append("ID")
        elif tok[0].isdigit():
            tokens.append("NUM")
        elif tok.strip():
            tokens.append(tok)
    return tokens


def _hash_kgram(gram: Tuple[str, ...]) -> int:
    digest = hashlib.md5("".join(gram).encode("utf-8", errors="replace")).hexdigest()
    return int(digest[:8], 16)


def adaptive_gram_size(token_count: int, k: int = K_GRAM, window: int = WINDOW_SIZE) -> Tuple[int, int]:
    """
    Chọn (k, window) theo độ dài bài làm: bài ngắn dùng cửa sổ nhỏ hơn để không
    bị mất fingerprint (k=5, w=4 trên bài ~40 token chỉ còn vài gram).
    """
    if token_count < SHORT_DOC_TOKENS:
        return min(SHORT_K_GRAM, k), min(SHORT_WINDOW, window)
    return k, window


def winnow_fingerprints(tokens: List[str], k: int = K_GRAM, window: int = WINDOW_SIZE) -> set:
    """
    Returns the set of Winnowing fingerprints (document fingerprint) for a token
    stream. Position-independent, so reordered / renamed copies still match.
    """
    if len(tokens) < k:
        # Too short to shingle: fall back to a single hash of the whole stream.
        if not tokens:
            return set()
        return {_hash_kgram(tuple(tokens))}

    hashes = [_hash_kgram(tuple(tokens[i:i + k])) for i in range(len(tokens) - k + 1)]
    if len(hashes) <= window:
        return set(hashes)

    fingerprints = set()
    for i in range(len(hashes) - window + 1):
        fingerprints.add(min(hashes[i:i + window]))
    return fingerprints


def jaccard_similarity(a: set, b: set) -> float:
    """Jaccard index (0-100 %)."""
    if not a and not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return (len(a & b) / len(union)) * 100.0


def containment_similarity(a: set, b: set) -> float:
    """
    Tỷ lệ % của tập fingerprint nhỏ hơn được tập kia bao phủ (MOSS coverage).
    Chỉ số này bắt được kiểu "copypaste một hàm / nửa bài của bạn" mà Jaccard
    thường bỏ sót vì mẫu số (phần hợp) bị phình to.
    """
    if not a or not b:
        return 0.0
    smaller = a if len(a) <= len(b) else b
    if not smaller:
        return 0.0
    return (len(a & b) / len(smaller)) * 100.0


def common_boilerplate(fingerprint_sets: Sequence[set], ratio: float = BOILERPLATE_RATIO) -> set:
    """
    Tập gram xuất hiện ở hơn `ratio` tỉ lệ bài nộp của lớp — tức khung sườn /
    boilerplate ai cũng viết (`#include <stdio.h>`, `int main()`, ...).
    """
    total = len(fingerprint_sets)
    if total < 2:
        return set()
    counts: Dict[int, int] = {}
    for fps in fingerprint_sets:
        for fp in fps:
            counts[fp] = counts.get(fp, 0) + 1
    limit = ratio * total
    return {fp for fp, df in counts.items() if df > limit}


def filter_boilerplate(fingerprint_sets: Sequence[set], ratio: float = BOILERPLATE_RATIO) -> List[set]:
    """Loại bỏ boilerplate chung của lớp khỏi từng tập fingerprint."""
    common = common_boilerplate(fingerprint_sets, ratio)
    if not common:
        return [set(fps) for fps in fingerprint_sets]
    return [set(fps) - common for fps in fingerprint_sets]


def question_sort_key(question_key: Optional[str]) -> Tuple[int, str]:
    """Sắp xếp 'Q1' < 'Q2' < ... < 'Q10' theo số câu thay vì theo chuỗi."""
    match = re.search(r"(\d+)", question_key or "")
    return (int(match.group(1)) if match else 0, question_key or "")


class PlagiarismEngine:
    """Offline whole-class plagiarism engine (Winnowing + Jaccard/containment)."""

    def __init__(
        self,
        k: int = K_GRAM,
        window: int = WINDOW_SIZE,
        adaptive: bool = True,
        boilerplate_filter: bool = True,
    ):
        self.k = k
        self.window = window
        self.adaptive = adaptive
        self.boilerplate_filter = boilerplate_filter

    def _params_for(self, token_count: int) -> Tuple[int, int]:
        if not self.adaptive:
            return self.k, self.window
        return adaptive_gram_size(token_count, self.k, self.window)

    def fingerprints_of(self, code: str, language: str = "C") -> set:
        tokens = normalize_tokens(code, language)
        k, window = self._params_for(len(tokens))
        return winnow_fingerprints(tokens, k, window)

    def _pair_fingerprints(self, code_a: str, code_b: str, language: str) -> Tuple[set, set]:
        """
        Băm fingerprint cho 2 mã nguồn dùng CÙNG tham số (k, window) — lấy theo bài
        ngắn hơn. Nếu mỗi bài tự chọn k riêng thì hai bài dài ngắn khác nhau sẽ
        không bao giờ khớp gram với nhau.
        """
        tokens_a = normalize_tokens(code_a, language)
        tokens_b = normalize_tokens(code_b, language)
        k, window = self._params_for(min(len(tokens_a), len(tokens_b)))
        return (
            winnow_fingerprints(tokens_a, k, window),
            winnow_fingerprints(tokens_b, k, window),
        )

    @staticmethod
    def _public_metrics(metrics: Dict[str, float]) -> Dict[str, float]:
        """Bỏ khóa `shared` (số gram chung) trước khi trả ra ngoài."""
        return {name: value for name, value in metrics.items() if name != "shared"}

    @staticmethod
    def compare_fingerprints(fa: set, fb: set) -> Dict[str, float]:
        """Trả về 3 chỉ số của một cặp fingerprint (đều là %)."""
        jaccard = round(jaccard_similarity(fa, fb), 2)
        containment = round(containment_similarity(fa, fb), 2)
        return {
            "jaccard": jaccard,
            "containment": containment,
            "sim": max(jaccard, containment),
            "shared": float(len(fa & fb)),
        }

    def similarity_metrics(self, code_a: str, code_b: str, language: str = "C") -> Dict[str, float]:
        """Chỉ số tương đồng của 2 mã nguồn đơn lẻ (không có ngữ cảnh toàn lớp)."""
        fa, fb = self._pair_fingerprints(code_a, code_b, language)
        metrics = self.compare_fingerprints(fa, fb)
        if metrics["shared"] < MIN_SHARED_FINGERPRINTS:
            # Quá ít gram chung (bài cụt / chỉ trùng boilerplate) -> hạ về 0.
            return {"jaccard": metrics["jaccard"], "containment": metrics["containment"],
                    "sim": 0.0, "shared": metrics["shared"]}
        return metrics

    def compare_pair(self, code_a: str, code_b: str, language: str = "C") -> float:
        """
        Điểm tương đồng Jaccard (%) giữa hai mã nguồn — dùng khi chỉ có 1 cặp bài
        và không có ngữ cảnh toàn lớp. Chỉ số containment chỉ đáng tin sau khi đã
        lọc boilerplate của lớp, nên `scan_class` mới là nơi dùng `sim` tổng hợp.
        """
        return self.similarity_metrics(code_a, code_b, language)["jaccard"]

    # --------------------------------------------------------------------------
    # Chuẩn bị dữ liệu quét
    # --------------------------------------------------------------------------
    def _prepare_documents(
        self, submissions: List[Dict[str, Any]], language: str
    ) -> List[Dict[str, Any]]:
        """
        Chuẩn hóa danh sách bài nộp thành `documents` với từng câu (unit) riêng.

        Mỗi bài nộp nhận:
          - `units`: {"Q1": code, "Q2": code, ...}  (bài nhiều câu)
          - hoặc `content` / `path` (bài 1 file) -> quy về một unit `Q1`.
        """
        documents: List[Dict[str, Any]] = []
        for sub in submissions:
            units_raw: Dict[str, str] = {}
            raw_units = sub.get("units")
            if raw_units:
                units_raw = {str(key): value for key, value in raw_units.items()}
            else:
                content = sub.get("content")
                if content is None:
                    path = sub.get("path")
                    if path and Path(path).is_file():
                        content = Path(path).read_text(encoding="utf-8", errors="replace")
                    else:
                        continue
                units_raw = {DEFAULT_QUESTION_KEY: content}

            units: Dict[str, Dict[str, Any]] = {}
            for key, text in units_raw.items():
                if not text or not str(text).strip():
                    continue
                tokens = normalize_tokens(str(text), language)
                if len(tokens) < MIN_UNIT_TOKENS:
                    continue
                units[key] = {
                    "code": str(text),
                    "tokens": tokens,
                }

            if units:
                documents.append({
                    "mssv": sub.get("mssv", ""),
                    "name": sub.get("name", "Sinh viên"),
                    "units": units,
                })
        return documents

    def _assign_fingerprints(self, documents: List[Dict[str, Any]]) -> None:
        """
        Băm fingerprint cho mọi bài, dùng CÙNG (k, window) cho tất cả bài cùng câu
        (lấy theo bài ngắn nhất của câu đó). Nếu mỗi bài tự chọn tham số riêng thì
        hai bài chênh lệch độ dài sẽ không thể khớp gram với nhau.
        """
        min_tokens: Dict[str, int] = {}
        for doc in documents:
            for key, unit in doc["units"].items():
                size = len(unit["tokens"])
                min_tokens[key] = min(min_tokens.get(key, size), size)

        for doc in documents:
            for key, unit in doc["units"].items():
                k, window = self._params_for(min_tokens.get(key, 0))
                unit["fingerprints"] = winnow_fingerprints(unit["tokens"], k, window)

    @staticmethod
    def _apply_boilerplate_filter(documents: List[Dict[str, Any]]) -> bool:
        """
        Loại boilerplate chung của lớp theo từng câu. Chỉ chạy khi lớp đủ đông
        (`BOILERPLATE_MIN_DOCS`) để không xóa mất chính cặp bài sao chép.
        """
        by_question: Dict[str, List[set]] = {}
        for doc in documents:
            for key, unit in doc["units"].items():
                by_question.setdefault(key, []).append(unit["fingerprints"])

        filtered = False
        for key, fps_list in by_question.items():
            if len(fps_list) < BOILERPLATE_MIN_DOCS:
                continue
            common = common_boilerplate(fps_list, BOILERPLATE_RATIO)
            if not common:
                continue
            filtered = True
            for doc in documents:
                unit = doc["units"].get(key)
                if unit is not None:
                    unit["fingerprints"] = unit["fingerprints"] - common
        return filtered

    # --------------------------------------------------------------------------
    # Quét toàn lớp
    # --------------------------------------------------------------------------
    def scan_class(
        self,
        submissions: List[Dict[str, Any]],
        language: str = "C",
        threshold: float = 80.0
    ) -> Dict[str, Any]:
        """
        Cross-compares every pair of submissions of a class, question by question.

        Args:
            submissions: list of dicts, mỗi dict là một bài nộp:
                - bài nhiều câu: {"mssv", "units": {"Q1": code, "Q2": code}}
                - bài 1 file:   {"mssv", "content" | "path"}
            language: source language.
            threshold: minimum similarity (%) considered a red alert.

        Returns:
            {
              "total_pairs": int,          # số lượt so (cặp SV × câu)
              "students_compared": int,
              "questions": [...],          # các câu được đối soát
              "boilerplate_filtered": bool,
              "engine": "AST_WINNOWING",
              "matches": [ {
                  sv_a, sv_b, name_a, name_b,
                  sim, jaccard, containment,
                  question, questions, question_scores, question_codes,
                  code_a, code_b, verdict, engine
              }, ... ]                    # 1 dòng / cặp sinh viên, giảm dần theo `sim`
            }
        """
        documents = self._prepare_documents(submissions, language)
        self._assign_fingerprints(documents)
        boilerplate_filtered = (
            self._apply_boilerplate_filter(documents) if self.boilerplate_filter else False
        )

        question_keys = sorted(
            {key for doc in documents for key in doc["units"].keys()},
            key=question_sort_key,
        )

        aggregated: Dict[Tuple[str, str], Dict[str, Any]] = {}
        total_pairs = 0
        for key in question_keys:
            units = [(doc, doc["units"][key]) for doc in documents if key in doc["units"]]
            for (doc_a, unit_a), (doc_b, unit_b) in itertools.combinations(units, 2):
                total_pairs += 1
                metrics = self.compare_fingerprints(
                    unit_a["fingerprints"], unit_b["fingerprints"]
                )
                if metrics["shared"] < MIN_SHARED_FINGERPRINTS:
                    continue
                if metrics["sim"] < threshold:
                    continue

                pair_key = (doc_a["mssv"], doc_b["mssv"])
                entry = aggregated.get(pair_key)
                if entry is None:
                    entry = {
                        "sv_a": doc_a["mssv"],
                        "sv_b": doc_b["mssv"],
                        "name_a": doc_a["name"],
                        "name_b": doc_b["name"],
                        "sim": metrics["sim"],
                        "jaccard": metrics["jaccard"],
                        "containment": metrics["containment"],
                        "question": key,
                        "questions": [key],
                        "question_scores": {key: self._public_metrics(metrics)},
                        "question_codes": {key: (unit_a["code"], unit_b["code"])},
                        "code_a": unit_a["code"],
                        "code_b": unit_b["code"],
                        "verdict": f"Báo động đỏ (≥{int(threshold)}%)",
                        "engine": "AST_WINNOWING",
                    }
                    aggregated[pair_key] = entry
                    continue

                entry["questions"].append(key)
                entry["question_scores"][key] = self._public_metrics(metrics)
                entry["question_codes"][key] = (unit_a["code"], unit_b["code"])
                if metrics["sim"] > entry["sim"]:
                    entry.update({
                        "sim": metrics["sim"],
                        "jaccard": metrics["jaccard"],
                        "containment": metrics["containment"],
                        "question": key,
                        "code_a": unit_a["code"],
                        "code_b": unit_b["code"],
                    })

        matches = list(aggregated.values())
        matches.sort(key=lambda m: m["sim"], reverse=True)
        return {
            "total_pairs": total_pairs,
            "students_compared": len(documents),
            "questions": question_keys,
            "boilerplate_filtered": boilerplate_filtered,
            "matches": matches,
            "engine": "AST_WINNOWING",
        }


def scan_submissions(
    submissions: List[Dict[str, Any]],
    language: str = "C",
    threshold: float = 80.0
) -> Dict[str, Any]:
    """Convenience module-level wrapper around `PlagiarismEngine.scan_class`."""
    return PlagiarismEngine().scan_class(submissions, language=language, threshold=threshold)
