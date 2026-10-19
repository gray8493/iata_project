"""Offline Plagiarism Engine (services.plagiarism_engine).

Covers IT13 / ST03_TC001: lexical normalization defeats variable renaming,
Winnowing fingerprints are position-stable, Jaccard similarity is 0-100%,
and scan_class flags only pairs at/above the suspicion threshold (< 1s).
"""

import pytest

from services.plagiarism_engine import (
    PlagiarismEngine,
    adaptive_gram_size,
    common_boilerplate,
    containment_similarity,
    filter_boilerplate,
    jaccard_similarity,
    normalize_tokens,
    question_sort_key,
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


# ------------------------------------------------------------------------------
# Per-question units (UC-17): so từng câu thay vì gộp cả gói bài
# ------------------------------------------------------------------------------
Q2_FIB = """
#include <stdio.h>
int fib(int k) {
    if (k <= 1) { return k; }
    return fib(k - 1) + fib(k - 2);
}
int main() {
    int k;
    scanf("%d", &k);
    printf("%d\\n", fib(k));
    return 0;
}
"""


def test_question_sort_key_orders_questions_numerically():
    assert sorted(["Q10", "Q2", "Q1"], key=question_sort_key) == ["Q1", "Q2", "Q10"]


def test_adaptive_gram_size_shrinks_window_for_short_answers():
    assert adaptive_gram_size(200) == (5, 4)
    assert adaptive_gram_size(40) == (3, 3)


def test_scan_units_flags_single_copied_question_that_whole_file_comparison_misses():
    docs = [
        {"mssv": "SE180001", "units": {"Q1": C_A, "Q2": C_B_DIFFERENT}},
        {"mssv": "SE180002", "units": {"Q1": C_A_RENAMED, "Q2": Q2_FIB}},
    ]

    per_question = PlagiarismEngine().scan_class(docs, language="C", threshold=80.0)

    assert per_question["questions"] == ["Q1", "Q2"]
    assert per_question["total_pairs"] == 2          # 1 cặp × 2 câu
    assert len(per_question["matches"]) == 1         # chỉ Q1 bị trùng
    match = per_question["matches"][0]
    assert {match["sv_a"], match["sv_b"]} == {"SE180001", "SE180002"}
    assert match["questions"] == ["Q1"]
    assert match["question"] == "Q1"
    assert match["sim"] == 100.0
    assert match["jaccard"] == 100.0 and match["containment"] == 100.0
    assert match["code_a"] == C_A                    # mã nguồn của câu bị trùng
    assert set(match["question_scores"]) == {"Q1"}

    # Hành vi cũ (gộp cả gói bài thành 1 chuỗi) bị pha loãng nên BỎ SÓT chính cặp này.
    whole_file = PlagiarismEngine().scan_class(
        [{"mssv": d["mssv"], "content": d["units"]["Q1"] + d["units"]["Q2"]} for d in docs],
        language="C",
        threshold=80.0,
    )
    assert whole_file["matches"] == []


def test_scan_units_merges_multiple_matching_questions_into_one_pair_row():
    docs = [
        {"mssv": "SE180001", "units": {"Q1": C_A, "Q2": Q2_FIB}},
        {"mssv": "SE180002", "units": {"Q1": C_A_RENAMED, "Q2": Q2_FIB}},
    ]

    report = PlagiarismEngine().scan_class(docs, language="C", threshold=80.0)

    assert len(report["matches"]) == 1                # 1 dòng cho 1 cặp sinh viên
    match = report["matches"][0]
    assert match["questions"] == ["Q1", "Q2"]         # cả 2 câu đều bị trùng
    assert set(match["question_scores"]) == {"Q1", "Q2"}
    assert set(match["question_codes"]) == {"Q1", "Q2"}
    assert match["sim"] == 100.0


def test_scan_units_containment_catches_partial_copy_inside_a_bigger_answer():
    docs = [
        {"mssv": "SE180001", "units": {"Q1": C_A}},
        {"mssv": "SE180002", "units": {"Q1": C_A + "\n" + Q2_FIB}},   # copy nguyên C_A rồi viết thêm
    ]

    report = PlagiarismEngine().scan_class(docs, language="C", threshold=80.0)

    assert len(report["matches"]) == 1
    match = report["matches"][0]
    # Jaccard bị pha loãng vì bài B dài hơn, nhưng độ bao phủ (containment) bắt được.
    assert match["jaccard"] < 80.0
    assert match["containment"] >= 80.0
    assert match["sim"] == match["containment"]


def test_scan_units_skips_answers_below_minimum_tokens():
    stub = "int main() { return 0; }"                 # 9 token -> dưới ngưỡng tối thiểu
    report = PlagiarismEngine().scan_class(
        [
            {"mssv": "SE180001", "units": {"Q1": stub, "Q2": C_A}},
            {"mssv": "SE180002", "units": {"Q1": stub, "Q2": C_B_DIFFERENT}},
        ],
        language="C",
        threshold=80.0,
    )
    assert report["total_pairs"] == 1                 # Q1 bị bỏ, chỉ còn Q2
    assert report["matches"] == []


def test_scan_units_drops_submission_whose_answers_are_all_too_short():
    report = PlagiarismEngine().scan_class(
        [
            {"mssv": "SE180001", "units": {"Q1": "int main() { return 0; }"}},
            {"mssv": "SE180002", "units": {"Q1": C_A}},
        ],
        language="C",
        threshold=80.0,
    )
    assert report["students_compared"] == 1
    assert report["total_pairs"] == 0 and report["matches"] == []


# ------------------------------------------------------------------------------
# Boilerplate toàn lớp + độ bao phủ (containment)
# ------------------------------------------------------------------------------
def test_containment_similarity_is_coverage_of_the_smaller_set():
    assert containment_similarity({1, 2, 3, 4}, {1, 2}) == 100.0   # tập nhỏ nằm trọn trong tập lớn
    assert containment_similarity({1, 2}, {3, 4}) == 0.0
    assert containment_similarity(set(), {1}) == 0.0
    assert containment_similarity({1, 2, 3}, {2, 3, 4, 5}) == pytest.approx(66.67, abs=0.01)


def test_common_boilerplate_keeps_only_grams_shared_by_most_documents():
    doc_fingerprints = [{1, 2, 3}, {1, 2, 4}, {1, 5, 6}, {1, 5, 7}, {1, 5, 8}]
    # gram 1: 5/5 bài, gram 5: 3/5 bài (60% > 50%), gram 2: chỉ 2/5 bài
    assert common_boilerplate(doc_fingerprints, 0.5) == {1, 5}


def test_filter_boilerplate_removes_common_grams_from_every_document():
    filtered = filter_boilerplate([{1, 2, 3}, {1, 5, 6}, {1, 5, 7}, {1, 5, 8}, {1, 5, 9}], 0.5)
    assert filtered[0] == {2, 3}
    assert all(1 not in fps and 5 not in fps for fps in filtered)


def test_scan_class_applies_boilerplate_filter_when_class_is_large_enough():
    skeleton = C_A                                     # khung sườn ai cũng viết
    bodies = [Q2_FIB, C_B_DIFFERENT, "int main() { int a; a = 1; printf(\"%d\", a); return 0; }",
              "int main() { int b; b = b + 1; printf(\"%d\", b); return 0; }",
              "int main() { int c; while (c < 2) { c++; } return 0; }"]
    docs = [
        {"mssv": f"SE18000{i + 1}", "units": {"Q1": skeleton + "\n" + body}}
        for i, body in enumerate(bodies)
    ]

    unfiltered = PlagiarismEngine(boilerplate_filter=False).scan_class(
        docs, language="C", threshold=0.0
    )
    filtered = PlagiarismEngine().scan_class(docs, language="C", threshold=0.0)

    assert unfiltered["boilerplate_filtered"] is False
    assert filtered["boilerplate_filtered"] is True

    best_before = unfiltered["matches"][0]["sim"]
    best_after = filtered["matches"][0]["sim"] if filtered["matches"] else 0.0
    # Loại khung sườn chung -> điểm trùng lặp giảm (hoặc hết cặp nghi vấn).
    assert best_after < best_before
    assert best_before >= 60.0


def test_scan_class_skips_boilerplate_filter_for_small_classes():
    docs = [
        {"mssv": "SE180001", "units": {"Q1": C_A}},
        {"mssv": "SE180002", "units": {"Q1": C_A_RENAMED}},
        {"mssv": "SE180003", "units": {"Q1": C_B_DIFFERENT}},
    ]
    report = PlagiarismEngine().scan_class(docs, language="C", threshold=80.0)
    assert report["boilerplate_filtered"] is False
    assert len(report["matches"]) == 1                 # cặp sao chép vẫn được giữ
