"""Performance — kiểm thử ngưỡng thời gian (PF<NN>_<Module>_TC<nnn>).

Dùng `time.perf_counter` + ngưỡng rộng (CI-safe, không flaky), không thêm
dependency. Dữ liệu sinh deterministic bằng `random.Random(seed)` để mọi lần
chạy đều đo cùng khối lượng công việc.
"""
import random
import time

import pytest

from database.db_manager import DatabaseManager
from services.export_service import ExportService
from services.grading_service import GradingService
from services.plagiarism_engine import (
    PlagiarismEngine,
    normalize_tokens,
    winnow_fingerprints,
)

pytestmark = pytest.mark.performance

# Ngưỡng (giây) — rộng rãi để không vỡ trên máy CI chậm
SCAN_BUDGET_S = 10.0
TOKENIZE_BUDGET_S = 2.0
DB_BULK_BUDGET_S = 2.0
EXPORT_BUDGET_S = 5.0
GRADE_BATCH_BUDGET_S = 60.0

PY_ECHO = "n = int(input())\nprint(n * 2)\n"

_TEMPLATES = [
    "int main(void) {{\n    int a = {a}, b = {b};\n    int total = a + b;\n    for (int i = 0; i < 3; i++) {{\n        total += 0;\n    }}\n    printf(\"%d\\n\", total);\n    return 0;\n}}\n",
    "int main(void) {{\n    int x = {a};\n    int y = {b};\n    int sum = x + y;\n    for (int i = 0; i < 3; i++) {{\n        sum += 0;\n    }}\n    printf(\"%d\\n\", sum);\n    return 0;\n}}\n",
    "int main(void) {{\n    int p = {a}, q = {b};\n    int result = p + q;\n    for (int i = 0; i < 3; i++) {{\n        result += 0;\n    }}\n    printf(\"%d\\n\", result);\n    return 0;\n}}\n",
    "int main(void) {{\n    int m = {a};\n    int n = {b};\n    int ans = m + n;\n    for (int i = 0; i < 3; i++) {{\n        ans += 0;\n    }}\n    printf(\"%d\\n\", ans);\n    return 0;\n}}\n",
]


def _timed(fn):
    start = time.perf_counter()
    result = fn()
    return result, time.perf_counter() - start


def _gen_c_submissions(count: int, seed: int = 2026) -> list:
    rng = random.Random(seed)
    subs = []
    for i in range(count):
        template = _TEMPLATES[i % len(_TEMPLATES)]
        subs.append({
            "mssv": f"SE{i + 1:06d}",
            "name": f"Sinh Vien {i + 1}",
            "content": template.format(a=rng.randint(1, 999), b=rng.randint(1, 999)),
        })
    return subs


# ---------------------------------------------------------------------------
# PF01 PlagiarismEngine — Normal: quét đạo văn 60 bài C trong ngân sách
# ---------------------------------------------------------------------------
def test_pf01_plagiarismengine_tc001_scan_60_submissions_under_budget():
    engine = PlagiarismEngine()
    subs = _gen_c_submissions(60)

    report, elapsed = _timed(lambda: engine.scan_class(subs, language="C", threshold=80.0))

    assert report["students_compared"] == 60
    assert report["total_pairs"] >= 60 * 59 // 2
    assert report["engine"] == "AST_WINNOWING"
    assert isinstance(report["matches"], list)
    assert elapsed < SCAN_BUDGET_S, f"Quét 60 bài mất {elapsed:.2f}s (ngân sách {SCAN_BUDGET_S}s)"


# ---------------------------------------------------------------------------
# PF01 PlagiarismEngine — Boundary: file ~50KB vẫn xử lý trong ngân sách
# ---------------------------------------------------------------------------
def test_pf01_plagiarismengine_tc002_large_file_tokenize_under_budget():
    rng = random.Random(7)
    big_code = "\n".join(
        f"int var_{i}_{rng.randint(0, 999)} = {rng.randint(0, 999)};"
        for i in range(2500)
    )
    assert len(big_code) > 40_000

    tokens, elapsed = _timed(lambda: normalize_tokens(big_code, language="C"))
    fingerprints, fp_elapsed = _timed(lambda: winnow_fingerprints(tokens, 5, 4))

    assert len(tokens) > 3000
    assert isinstance(fingerprints, set)
    assert elapsed < TOKENIZE_BUDGET_S, f"normalize_tokens mất {elapsed:.2f}s"
    assert fp_elapsed < TOKENIZE_BUDGET_S, f"winnow_fingerprints mất {fp_elapsed:.2f}s"


# ---------------------------------------------------------------------------
# PF02 Database — Normal: nạp hàng loạt 500 bài + 200 testcase trong ngân sách
# ---------------------------------------------------------------------------
def test_pf02_database_tc001_bulk_inserts_under_budget(tmp_path):
    db = DatabaseManager(":memory:")
    class_id = db.create_class_session("PERF_DB", "PRF", "C", str(tmp_path))

    submissions = [
        (class_id, f"SE{i + 1:06d}", str(tmp_path / f"SE{i + 1:06d}.c"))
        for i in range(500)
    ]
    inserted, elapsed = _timed(lambda: db.bulk_insert_submissions(submissions))
    assert inserted == 500
    assert elapsed < DB_BULK_BUDGET_S, f"bulk_insert 500 bài mất {elapsed:.2f}s"

    def _add_many():
        for i in range(200):
            db.add_testcase(class_id, f"{i}\n", f"{i * 2}", score_weight=1.0)

    _, tc_elapsed = _timed(_add_many)
    assert len(db.get_testcases_by_class(class_id)) == 200
    assert tc_elapsed < DB_BULK_BUDGET_S, f"add_testcase 200 lần mất {tc_elapsed:.2f}s"


# ---------------------------------------------------------------------------
# PF03 ExportService — Normal: 1000 dòng CSV + HTML trong ngân sách
# ---------------------------------------------------------------------------
def test_pf03_exportservice_tc001_export_1000_rows_under_budget(tmp_path):
    service = ExportService()
    rng = random.Random(11)
    submissions = [
        {
            "student_mssv": f"SE{i + 1:06d}",
            "source_file_path": f"C:/subs/SE{i + 1:06d}.c",
            "calculated_score": round(rng.uniform(0, 10), 1),
            "final_verdict": rng.choice(["AC", "WA", "CE", "TLE"]),
            "execution_time_ms": rng.uniform(5, 900),
            "ai_feedback": "Bài làm ổn định.",
        }
        for i in range(1000)
    ]

    rows, build_elapsed = _timed(lambda: service.build_grade_rows(submissions, 5))
    assert len(rows) == 1000

    csv_path = tmp_path / "perf_results.csv"
    _, csv_elapsed = _timed(lambda: service.export_csv(rows, str(csv_path)))
    assert csv_path.stat().st_size > 50_000

    _, html_elapsed = _timed(lambda: service.build_report_html(rows, "PERF", "PRF", "C"))
    assert build_elapsed + csv_elapsed < EXPORT_BUDGET_S, (
        f"build+csv mất {build_elapsed + csv_elapsed:.2f}s"
    )
    assert html_elapsed < EXPORT_BUDGET_S, f"build_report_html mất {html_elapsed:.2f}s"


# ---------------------------------------------------------------------------
# PF04 GradingService — Normal: chấm song song 20 bài Python trong ngân sách
# ---------------------------------------------------------------------------
def test_pf04_gradingservice_tc001_batch_20_python_under_budget(tmp_path):
    db = DatabaseManager(":memory:")
    class_id = db.create_class_session("PERF_GRADE", "PHP", "PYTHON", str(tmp_path))

    submissions = []
    for i in range(20):
        src = tmp_path / f"SE{i + 1:06d}_Q1.py"
        src.write_text(PY_ECHO, encoding="utf-8")
        submissions.append((class_id, f"SE{i + 1:06d}", str(src)))
    db.bulk_insert_submissions(submissions)
    for input_data, expected in (("5\n", "10"), ("9\n", "18")):
        db.add_testcase(
            class_id, input_data, expected, score_weight=1.0,
            time_limit_ms=3000, matching_strategy="EXACT_MATCH",
        )

    service = GradingService(db)
    results, elapsed = _timed(lambda: service.grade_class_batch(class_id, max_workers=4))

    assert len(results) == 20
    assert all(r["verdict"] == "AC" and r["score"] == 10.0 for r in results)
    assert elapsed < GRADE_BATCH_BUDGET_S, (
        f"Chấm 20 bài Python mất {elapsed:.2f}s (ngân sách {GRADE_BATCH_BUDGET_S}s)"
    )
