"""Offline Plagiarism Engine (services.plagiarism_engine).

Covers IT13 / ST03_TC001: lexical normalization defeats variable renaming,
Winnowing fingerprints are position-stable, Jaccard similarity is 0-100%,
and scan_class flags only pairs at/above the suspicion threshold (< 1s).
"""

import pytest

from services.plagiarism_engine import (
    PlagiarismEngine,
    jaccard_similarity,
    normalize_tokens,
    scan_submissions,
    winnow_fingerprints,
)

C_A = """
#include <stdio.h>
int main() {
    int n = 10;
    int sum = 0;
    for (int i = 1; i <= n; i++) { sum += i; }
    printf("%d\\n", sum);
    return 0;
}
"""

C_A_RENAMED = """
#include <stdio.h>
int main() {
    int m = 10;          /* renamed n -> m */
    int total = 0;       // renamed sum -> total
    for (int j = 1; j <= m; j++) { total += j; }
    printf("%d\\n", total);
    return 0;
}
"""

C_B_DIFFERENT = """
#include <stdio.h>
int main() {
    double base = 2.5;
    while (base < 1000) { base *= base; }
    printf("%f\\n", base);
    return 0;
}
"""


# ------------------------------------------------------------------------------
# Lexical normalization (AST-style token stream)
# ------------------------------------------------------------------------------
def test_normalize_tokens_masks_literals_and_ranks_users_identifiers():
    tokens = normalize_tokens(C_A, "C")
    assert "int" in tokens and "include" in tokens      # language keywords kept
    assert "ID" in tokens                               # user identifiers collapsed
    assert "NUM" in tokens                              # numbers masked
    assert "STR" in tokens                              # string literals masked
    assert "printf" not in tokens                       # "printf" is a user identifier
    assert "10" not in tokens                           # literal value removed


def test_normalize_tokens_strips_comments():
    tokens_a = normalize_tokens(C_A, "C")
    tokens_renamed = normalize_tokens(C_A_RENAMED, "C")
    # comments do not survive either stream
    assert all(tok not in tokens_a for tok in ("renamed", "total"))
    assert all(tok not in tokens_renamed for tok in ("renamed", "total"))


def test_normalize_tokens_defeats_variable_renaming():
    assert normalize_tokens(C_A, "C") == normalize_tokens(C_A_RENAMED, "C")


def test_normalize_tokens_python_language_branch():
    tokens = normalize_tokens("def solve(n):\n    return n * 2  # double it\n", "Python")
    assert "def" in tokens and "return" in tokens
    assert "solve" not in tokens and "NUM" in tokens  # identifiers collapse; 2 -> NUM


def test_normalize_language_variants():
    engine = PlagiarismEngine()
    assert engine.compare_pair("int x;", "int y;", language="JAVA") is not None
    assert isinstance(engine.compare_pair("x = 1", "y = 2", language="python"), float)


# ------------------------------------------------------------------------------
# Winnowing fingerprints + Jaccard
# ------------------------------------------------------------------------------
def test_fingerprints_identical_code_share_identical_fingerprints():
    assert winnow_fingerprints(normalize_tokens(C_A, "C")) == \
           winnow_fingerprints(normalize_tokens(C_A_RENAMED, "C"))


def test_fingerprints_short_fragments_fall_back_to_single_hash():
    assert winnow_fingerprints(["int"]) == winnow_fingerprints(["int"])
    assert winnow_fingerprints([]) == set()


def test_jaccard_similarity_bounds():
    same = {1, 2, 3}
    assert jaccard_similarity(same, same) == 100.0
    assert jaccard_similarity(set(), set()) == 0.0
    assert jaccard_similarity({1}, {2}) == 0.0
    half = jaccard_similarity({1, 2}, {2, 3})
    assert 0.0 < half < 100.0


def test_compare_pair_identical_sources_score_100():
    assert PlagiarismEngine().compare_pair(C_A, C_A_RENAMED, language="C") == 100.0


def test_compare_pair_different_sources_score_low():
    sim = PlagiarismEngine().compare_pair(C_A, C_B_DIFFERENT, language="C")
    assert sim < 40.0


# ------------------------------------------------------------------------------
# Class-wide scan (threshold filtering + reporting)
# ------------------------------------------------------------------------------
def _submissions(*bodies):
    return [
        {"mssv": f"SE18000{i + 1}", "name": f"SV{i + 1}", "content": body}
        for i, body in enumerate(bodies)
    ]


def test_scan_class_flags_only_pairs_over_threshold():
    report = PlagiarismEngine().scan_class(
        _submissions(C_A, C_A_RENAMED, C_B_DIFFERENT), language="C", threshold=80.0
    )
    assert report["engine"] == "AST_WINNOWING"
    assert report["total_pairs"] == 3
    assert report["students_compared"] == 3
    assert len(report["matches"]) == 1
    match = report["matches"][0]
    assert {match["sv_a"], match["sv_b"]} == {"SE180001", "SE180002"}
    assert match["sim"] >= 80.0
    assert "80" in match["verdict"]


def test_scan_class_below_threshold_has_no_matches():
    report = PlagiarismEngine().scan_class(
        _submissions(C_A, C_B_DIFFERENT), language="C", threshold=80.0
    )
    assert report["matches"] == [] and report["total_pairs"] == 1


def test_scan_class_matches_sorted_by_similarity_desc(tmp_path):
    clone = C_A + "\n// tiny comment\n"
    report = scan_submissions(
        _submissions(C_A, clone, C_A_RENAMED, C_B_DIFFERENT), language="C", threshold=90.0
    )
    sims = [m["sim"] for m in report["matches"]]
    assert sims == sorted(sims, reverse=True)
    assert sims[0] == 100.0  # byte-level clone is the strongest match


def test_scan_class_skips_missing_content_without_growing_pairs():
    report = scan_submissions(
        [{"mssv": "SE180001"}, {"mssv": "SE180002", "content": C_A}], language="C"
    )
    assert report["total_pairs"] == 0 and report["matches"] == []


def test_scan_class_reads_content_from_path(tmp_path):
    src = tmp_path / "SE180003_Q1.c"
    src.write_text(C_A_RENAMED, encoding="utf-8")
    report = scan_submissions(
        [{"mssv": "SE180001", "content": C_A},
         {"mssv": "SE180003", "path": str(src)}],
        language="C",
        threshold=80.0,
    )
    assert report["total_pairs"] == 1 and len(report["matches"]) == 1
