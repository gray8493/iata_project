"""GradingService (services.grading_service).

Covers the batch pipeline (IT08/IT10 analogues on Python to stay
compiler-independent): compilation -> sandbox execution per testcase ->
strategy comparison -> 10.0-scaled score persistence, plus the
ProcessPoolExecutor parallel dispatch (ST01_TC001 batch < 30s) and
progress callback semantics.
"""

import json

import pytest

from database.db_manager import DatabaseManager
from services.grading_service import (
    GradingService,
    grade_single_submission,
    SANDBOX_MAX_SCORE,
    AI_RUBRIC_MAX_SCORE,
)

PY_ECHO = "n = int(input())\nprint(n * 2)\n"

PY_FAIL = "print('Wrong AITA')\n"

PY_RUNTIME_ERROR = "raise RuntimeError('boom')\n"

PY_INFINITE_LOOP = "while True:\n    pass\n"

PY_SYNTAX_ERROR = "def broken(:\n    pass\n"


@pytest.fixture
def db():
    return DatabaseManager(":memory:")


def _write_src(tmp_path: "pytest.TempPathFactory", mssv: str, content: str):
    src = tmp_path / f"{mssv}_Q1.py"
    src.write_text(content, encoding="utf-8")
    return {"id": None, "student_mssv": mssv, "source_file_path": str(src)}


# ------------------------------------------------------------------------------
# grade_single_submission (worker-process payload)
# ------------------------------------------------------------------------------
def test_single_submission_full_marks(tmp_path):
    sub = _write_src(tmp_path, "SE180001", PY_ECHO)
    testcases = [
        {"input_data": "5\n", "expected_output": "10", "score_weight": 1.0,
         "time_limit_ms": 1500, "memory_limit_mb": 128, "matching_strategy": "EXACT_MATCH"},
        {"input_data": "7\n", "expected_output": "14", "score_weight": 1.0,
         "time_limit_ms": 1500, "memory_limit_mb": 128, "matching_strategy": "EXACT_MATCH"},
    ]
    res = grade_single_submission(sub, "PYTHON", testcases, total_weight=2.0)
    assert res["verdict"] == "AC" and res["score"] == 10.0
    assert res["execution_time_ms"] > 0
    assert res["memory_used_mb"] > 0


def test_single_submission_partial_score_wa(tmp_path):
    sub = _write_src(tmp_path, "SE180002", PY_ECHO)
    testcases = [
        {"input_data": "5\n", "expected_output": "10", "score_weight": 1.0,
         "time_limit_ms": 1500, "memory_limit_mb": 128, "matching_strategy": "EXACT_MATCH"},
        {"input_data": "7\n", "expected_output": "WRONG", "score_weight": 1.0,
         "time_limit_ms": 1500, "memory_limit_mb": 128, "matching_strategy": "EXACT_MATCH"},
    ]
    res = grade_single_submission(sub, "PYTHON", testcases, total_weight=2.0)
    assert res["verdict"] == "WA"
    assert res["score"] == 5.0
    assert res["diff_details"]  # WA evidence preserved for UI diff view


def test_single_submission_compile_error_ce(tmp_path):
    sub = _write_src(tmp_path, "SE180003", PY_SYNTAX_ERROR)
    testcases = [{"input_data": "", "expected_output": "x", "score_weight": 1.0,
                  "time_limit_ms": 1000, "memory_limit_mb": 128,
                  "matching_strategy": "EXACT_MATCH"}]
    res = grade_single_submission(sub, "PYTHON", testcases, total_weight=1.0)
    assert res["verdict"] == "CE" and res["score"] == 0.0
    assert "Syntax" in res["compile_log"]


def test_single_submission_runtime_error_re(tmp_path):
    sub = _write_src(tmp_path, "SE180004", PY_RUNTIME_ERROR)
    testcases = [{"input_data": "", "expected_output": "x", "score_weight": 1.0,
                  "time_limit_ms": 2000, "memory_limit_mb": 128,
                  "matching_strategy": "EXACT_MATCH"}]
    res = grade_single_submission(sub, "PYTHON", testcases, total_weight=1.0)
    assert res["verdict"] == "RE" and res["score"] == 0.0


def test_single_submission_timeout_tle(tmp_path):
    sub = _write_src(tmp_path, "SE180005", PY_INFINITE_LOOP)
    testcases = [{"input_data": "", "expected_output": "x", "score_weight": 1.0,
                  "time_limit_ms": 260, "memory_limit_mb": 128,
                  "matching_strategy": "EXACT_MATCH"}]
    res = grade_single_submission(sub, "PYTHON", testcases, total_weight=1.0)
    assert res["verdict"] == "TLE" and res["score"] == 0.0


def test_single_submission_unordered_tokens_strategy_applied(tmp_path):
    sub = _write_src(tmp_path, "SE180006", "print('3 2 1')\n")
    testcases = [{"input_data": "", "expected_output": "1 2 3", "score_weight": 1.0,
                  "time_limit_ms": 1500, "memory_limit_mb": 128,
                  "matching_strategy": "UNORDERED_TOKENS"}]
    res = grade_single_submission(sub, "PYTHON", testcases, total_weight=1.0)
    assert res["verdict"] == "AC"


# ------------------------------------------------------------------------------
# grade_single_submission — multi-question mode (source_file_path = student folder)
# ------------------------------------------------------------------------------
def _tc(q, inp, expected, weight=1.0):
    return {"question_number": q, "input_data": inp, "expected_output": expected,
            "score_weight": weight, "time_limit_ms": 1500, "memory_limit_mb": 128,
            "matching_strategy": "EXACT_MATCH"}


def test_multi_question_folder_grades_each_q_file(tmp_path):
    student_dir = tmp_path / "SE180007"
    student_dir.mkdir()
    (student_dir / "Q1.py").write_text(PY_ECHO, encoding="utf-8")
    (student_dir / "Q2.py").write_text(PY_FAIL, encoding="utf-8")
    sub = {"id": 1, "student_mssv": "SE180007", "source_file_path": str(student_dir)}
    testcases = [_tc("Q1", "5\n", "10"), _tc("Q2", "5\n", "10")]

    res = grade_single_submission(sub, "PYTHON", testcases, total_weight=2.0)

    assert res["verdict"] == "WA"
    assert res["score"] == 5.0


def test_multi_question_missing_q_file_is_ce_and_continues(tmp_path):
    student_dir = tmp_path / "SE180008"
    student_dir.mkdir()
    (student_dir / "Q1.py").write_text(PY_ECHO, encoding="utf-8")
    sub = {"id": 2, "student_mssv": "SE180008", "source_file_path": str(student_dir)}
    testcases = [_tc("Q1", "5\n", "10"), _tc("Q2", "5\n", "10")]

    res = grade_single_submission(sub, "PYTHON", testcases, total_weight=2.0)

    assert res["verdict"] == "CE"
    assert res["score"] == 5.0
    assert "Q2" in (res["compile_log"] or "")


def test_multi_question_syntax_error_only_affects_own_question(tmp_path):
    student_dir = tmp_path / "SE180009"
    student_dir.mkdir()
    (student_dir / "Q1.py").write_text(PY_SYNTAX_ERROR, encoding="utf-8")
    (student_dir / "Q2.py").write_text(PY_ECHO, encoding="utf-8")
    sub = {"id": 3, "student_mssv": "SE180009", "source_file_path": str(student_dir)}
    testcases = [_tc("Q1", "5\n", "10"), _tc("Q2", "5\n", "10"), _tc("Q2", "7\n", "14")]

    res = grade_single_submission(sub, "PYTHON", testcases, total_weight=3.0)

    assert res["verdict"] == "CE"
    assert res["score"] == round((2 / 3) * 10.0, 1)


# ------------------------------------------------------------------------------
# grade_class_batch (parallel pool + SQLite persistence)
# ------------------------------------------------------------------------------
def test_batch_grades_and_persists_results(db, tmp_path):
    class_id = db.create_class_session("SE1801_PY_PE", "PHP", "PYTHON", str(tmp_path))
    subs = [
        (class_id, "SE180001", str(tmp_path / "SE180001_Q1.py")),
        (class_id, "SE180002", str(tmp_path / "SE180002_Q1.py")),
    ]
    (tmp_path / "SE180001_Q1.py").write_text(PY_ECHO, encoding="utf-8")
    (tmp_path / "SE180002_Q1.py").write_text(PY_FAIL, encoding="utf-8")
    db.bulk_insert_submissions(subs)
    db.add_testcase(class_id, "5\n", "10", score_weight=1.0, time_limit_ms=1500,
                    matching_strategy="EXACT_MATCH")

    progress = []
    service = GradingService(db)
    results = service.grade_class_batch(
        class_id,
        progress_callback=lambda done, total, mssv: progress.append((done, total, mssv)),
        max_workers=2,
    )

    assert len(results) == 2
    by_mssv = {r["mssv"]: r for r in results}
    assert by_mssv["SE180001"]["verdict"] == "AC" and by_mssv["SE180001"]["score"] == 10.0
    assert by_mssv["SE180002"]["verdict"] == "WA" and by_mssv["SE180002"]["score"] == 0.0

    # Progress callback counts completions, not indexes
    assert [p[0] for p in progress] == [1, 2]
    assert {p[1] for p in progress} == {2}

    persisted = db.get_submissions_by_class(class_id)
    statuses = {s["student_mssv"]: s["final_verdict"] for s in persisted}
    assert statuses["SE180001"] == "AC" and statuses["SE180002"] == "WA"


def test_batch_without_testcases_raises_business_error(db, tmp_path):
    class_id = db.create_class_session("SE1801_EMPTY", "PHP", "PYTHON", str(tmp_path))
    db.bulk_insert_submissions([(class_id, "SE180001", str(tmp_path / "a.py"))])
    (tmp_path / "a.py").write_text(PY_ECHO, encoding="utf-8")

    with pytest.raises(ValueError, match="Cấu Hình Testcase"):
        GradingService(db).grade_class_batch(class_id)


def test_batch_empty_class_returns_empty(db, tmp_path):
    class_id = db.create_class_session("SE1801_NOSTUDENT", "PHP", "PYTHON", str(tmp_path))
    db.add_testcase(class_id, "1\n", "2", score_weight=1.0)
    assert GradingService(db).grade_class_batch(class_id) == []


def test_worker_exception_is_reported_as_re_not_crashed(db, tmp_path, monkeypatch):
    import services.grading_service as grading_service_module

    class_id = db.create_class_session("SE1801_CRASH", "PHP", "PYTHON", str(tmp_path))
    db.bulk_insert_submissions([(class_id, "SE180001", str(tmp_path / "b.py"))])
    (tmp_path / "b.py").write_text(PY_ECHO, encoding="utf-8")
    db.add_testcase(class_id, "", "10", score_weight=1.0, time_limit_ms=1500)

    def explode(submission, language, testcases, total_weight):
        raise RuntimeError("worker crashed inside pool")

    monkeypatch.setattr(grading_service_module, "grade_single_submission", explode)
    results = GradingService(db).grade_class_batch(class_id, max_workers=1)

    assert len(results) == 1
    assert results[0]["verdict"] == "RE" and results[0]["score"] == 0.0
    persisted = db.get_submissions_by_class(class_id)
    assert persisted[0]["final_verdict"] == "RE"


# ------------------------------------------------------------------------------
# Hybrid AI rubric — hành vi khi AI khả dụng / lỗi (UC-15 chấm lại)
# ------------------------------------------------------------------------------
class _FakeAiService:
    """Stub `AiService` cho `_enrich_with_ai_quality` (không gọi mạng)."""

    def __init__(self, success: bool, passes: int = 3):
        self.success = success
        self.passes = passes
        self.calls = 0

    def evaluate_code_quality(self, source_code, language, problem_statement=""):
        self.calls += 1
        if not self.success:
            return {"success": False, "message": "Hết hạn ngạch AI.", "error_code": "QUOTA_EXCEEDED"}
        rubric = {}
        for idx, key in enumerate(("clean_code", "complexity", "structure", "format", "documentation")):
            rubric[key] = {"passed": idx < self.passes, "reason": f"lý do {key}"}
        return {
            "success": True,
            "rubric": rubric,
            "overall_feedback": "Tổng nhận xét.",
            "tokens_consumed": 123,
        }


def _sandbox_result(ratio: float = 1.0) -> dict:
    """Kết quả sandbox tối thiểu (giống payload `grade_single_submission`)."""
    return {
        "submission_id": 1,
        "mssv": "SE180001",
        "verdict": "AC",
        "score": round(ratio * 10.0, 1),
        "sandbox_ratio": ratio,
        "sandbox_score": round(ratio * SANDBOX_MAX_SCORE, 2),
        "diff_details": None,
    }


def test_hybrid_rubric_adds_ai_half_score(db, tmp_path):
    src = tmp_path / "SE180001_Q1.py"
    src.write_text(PY_ECHO, encoding="utf-8")

    result = _sandbox_result(ratio=1.0)  # sandbox 5.0/5.0
    GradingService(db)._enrich_with_ai_quality(
        result, str(src), "PYTHON", "", _FakeAiService(True, passes=3)
    )

    assert result["rubric_available"] is True
    assert result["rubric_score"] == 3.0
    assert result["score"] == 8.0  # 5.0 sandbox + 3.0 rubric
    assert result["rubric_score"] <= AI_RUBRIC_MAX_SCORE


def test_hybrid_rubric_ai_failure_keeps_ten_point_scale(db, tmp_path):
    """AI lỗi/hết quota KHÔNG được kéo điểm xuống 5.0 — giữ nguyên thang 10 của sandbox."""
    src = tmp_path / "SE180001_Q1.py"
    src.write_text(PY_ECHO, encoding="utf-8")

    result = _sandbox_result(ratio=1.0)
    GradingService(db)._enrich_with_ai_quality(
        result, str(src), "PYTHON", "", _FakeAiService(False)
    )

    assert result["rubric_available"] is False
    assert result["rubric_score"] == 0.0
    assert result["score"] == 10.0  # trước đây bị 5.0

    quality = json.loads(result["diff_details"])["quality"]
    assert quality["pending"] is True
    assert quality["sandbox_full_score"] == 10.0


def test_hybrid_rubric_unreadable_source_keeps_ten_point_scale(db):
    """Không đọc được mã nguồn -> rubric PENDING, điểm vẫn theo thang 10."""
    result = _sandbox_result(ratio=0.6)  # sandbox 3.0/5.0 -> thang 10 là 6.0
    fake = _FakeAiService(True)
    GradingService(db)._enrich_with_ai_quality(result, None, "PYTHON", "", fake)

    assert fake.calls == 0  # không gọi AI khi không có source
    assert result["rubric_available"] is False
    assert result["score"] == 6.0


def test_regrade_submission_without_ai_quality_keeps_sandbox_score(db, tmp_path):
    """UC-15 mặc định Sandbox-only: không gọi AI, điểm giữ thang 10."""
    class_id = db.create_class_session("SE1801_REGRADE", "PHP", "PYTHON", str(tmp_path))
    src = tmp_path / "SE180001_Q1.py"
    src.write_text(PY_ECHO, encoding="utf-8")
    db.bulk_insert_submissions([(class_id, "SE180001", str(src))])
    db.add_testcase(class_id, "5\n", "10", score_weight=1.0, time_limit_ms=1500)
    sub_id = db.get_submissions_by_class(class_id)[0]["id"]

    result = GradingService(db).regrade_submission(sub_id, enable_ai_quality=False)

    assert result["verdict"] == "AC"
    assert result["score"] == 10.0
    assert "rubric_available" not in result

    stored = db.get_submission_result(sub_id)
    assert stored["calculated_score"] == 10.0

