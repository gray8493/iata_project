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
  2. k-gram shingling       -> sliding window of `k` normalized tokens.
  3. Winnowing              -> select the minimum hash per window `w` to obtain
     a compact, position-independent fingerprint set.
  4. Similarity             -> Jaccard index over the two fingerprint sets (%).

This module has no network / AI dependency; Stage 2 (Gemini semantic
verification) stays in `services.ai_service`.
"""

import hashlib
import itertools
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

K_GRAM = 5
WINDOW_SIZE = 4

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


class PlagiarismEngine:
    """Offline two-file / whole-class AST-style Winnowing plagiarism engine."""

    def __init__(self, k: int = K_GRAM, window: int = WINDOW_SIZE):
        self.k = k
        self.window = window

    def fingerprints_of(self, code: str, language: str = "C") -> set:
        return winnow_fingerprints(normalize_tokens(code, language), self.k, self.window)

    def compare_pair(self, code_a: str, code_b: str, language: str = "C") -> float:
        """Returns the AST/Winnowing similarity percentage between two sources."""
        fa = self.fingerprints_of(code_a, language)
        fb = self.fingerprints_of(code_b, language)
        return round(jaccard_similarity(fa, fb), 2)

    def scan_class(
        self,
        submissions: List[Dict[str, Any]],
        language: str = "C",
        threshold: float = 80.0
    ) -> Dict[str, Any]:
        """
        Cross-compares every pair of submissions of a class.

        Args:
            submissions: list of dicts with keys `mssv`, `content` (and optional
                `path`/`name`).
            language: source language.
            threshold: minimum similarity (%) considered a red alert.

        Returns:
            {
              "total_pairs": int,
              "matches": [ {sv_a, sv_b, sim, code_a, code_b, verdict}, ... ],
              "engine": "AST_WINNOWING"
            }
        """
        prepared = []
        for sub in submissions:
            content = sub.get("content")
            if content is None:
                path = sub.get("path")
                if path and Path(path).is_file():
                    content = Path(path).read_text(encoding="utf-8", errors="replace")
                else:
                    continue
            tokens = normalize_tokens(content, language)
            prepared.append({
                "mssv": sub.get("mssv", ""),
                "name": sub.get("name", "Sinh viên"),
                "content": content,
                "fingerprints": winnow_fingerprints(tokens, self.k, self.window)
            })

        matches: List[Dict[str, Any]] = []
        total_pairs = 0
        for s1, s2 in itertools.combinations(prepared, 2):
            total_pairs += 1
            sim = round(jaccard_similarity(s1["fingerprints"], s2["fingerprints"]), 2)
            if sim >= threshold:
                matches.append({
                    "sv_a": s1["mssv"],
                    "sv_b": s2["mssv"],
                    "name_a": s1["name"],
                    "name_b": s2["name"],
                    "sim": sim,
                    "code_a": s1["content"],
                    "code_b": s2["content"],
                    "verdict": f"Báo động đỏ (≥{int(threshold)}%)",
                    "engine": "AST_WINNOWING"
                })

        matches.sort(key=lambda m: m["sim"], reverse=True)
        return {
            "total_pairs": total_pairs,
            "students_compared": len(prepared),
            "matches": matches,
            "engine": "AST_WINNOWING"
        }


def scan_submissions(
    submissions: List[Dict[str, Any]],
    language: str = "C",
    threshold: float = 80.0
) -> Dict[str, Any]:
    """Convenience module-level wrapper around `PlagiarismEngine.scan_class`."""
    return PlagiarismEngine().scan_class(submissions, language=language, threshold=threshold)
