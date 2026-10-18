"""
Unit tests - Grading Service fixes (UT level)
Phạm vi: chấm công bằng Python (baseline startup), chứng cứ JSON per-testcase (diff_details),
và cơ chế cancel/resume của batch grading.
Không cần GUI (pytest chạy headless, không import PyQt).
"""

import json
import os
import sys
import threading
from pathlib import Path

import pytest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.grading_service import (  # noqa: E402
    grade_single_submission,
    measure_python_startup_baseline,
    _is_python_language,
)


@pytest.fixture(scope="module")
def python_submission(tmp_path_factory):
    """Tạo 1 bài nộp Python in 2 số từ stdin."""
    folder = tmp_path_factory.mktemp("submissions")
    sub_dir = folder / "SE180001"
    sub_dir.mkdir()
    source = sub_dir / "main.py"
    source.write_text(
        "values = input().split()\n" "a, b = int(values[0]), int(values[1])\n" "print(a + b)\n",
        encoding="utf-8",
    )
    return {"student_mssv": "SE180001", "id": 1, "source_file_path": str(source)}


TESTCASES = [
    {"input_data": "3 4\n", "expected_output": "7", "score_weight": 1.0,
     "time_limit_ms": 800, "memory_limit_mb": 64, "matching_strategy": "EXACT_MATCH"},
    {"input_data": "10 20\n", "expected_output": "30", "score_weight": 1.0,
     "time_limit_ms": 800, "memory_limit_mb": 64, "matching_strategy": "EXACT_MATCH"},
]


def test_python_language_detection():
    assert _is_python_language("Python") is True
    assert _is_python_language("python (Python 3.x Runtime - file *.py)") is True
    assert _is_python_language("C") is False
    assert _is_python_language("") is False


def test_python_baseline_measured_once():
    first = measure_python_startup_baseline()
    assert first > 0.0
    assert measure_python_startup_baseline() == first


def test_python_ac_wins_over_slow_interpreter_boot(python_submission):
    """
    Fairness #5: time_limit 800ms là đủ cho bài cực ngắn dù interpreter khởi động chậm.
    Trên máy chậm, baseline > 800ms -> không cộng thêm sẽ TLE oan -> test này thắt chặt nghĩa.
    """
    baseline = measure_python_startup_baseline()
    total_weight = 2.0
    result = grade_single_submission(
        python_submission, "Python", TESTCASES, total_weight, python_baseline_ms=baseline
    )
    assert result["verdict"] == "AC"
    assert result["score"] == pytest.approx(10.0)
    assert result["execution_time_ms"] <= 1500.0


def test_wa_case_partial_and_verdict(python_submission):
    wrong_testcases = [
        {"input_data": "3 4\n", "expected_output": "999", "score_weight": 1.0,
         "time_limit_ms": 800, "memory_limit_mb": 64, "matching_strategy": "EXACT_MATCH"},
    ]
    result = grade_single_submission(python_submission, "Python", wrong_testcases, 1.0)
    assert result["verdict"] == "WA"
    assert result["score"] == pytest.approx(0.0)


def test_diff_details_json_contains_per_testcase_actual(python_submission):
    """Pain #4: diff_details là JSON mới với output thật theo từng testcase."""
    baseline = measure_python_startup_baseline()
    result = grade_single_submission(
        python_submission, "Python", TESTCASES, 2.0, python_baseline_ms=baseline
    )
    payload = json.loads(result["diff_details"])
    assert payload["language"].startswith("PY") or payload["language"] == "Python" or "Python" in payload["language"]
    items = payload["items"]
    assert len(items) == 2
    assert items[0]["actual"].strip() == "7"
    assert items[0]["verdict"] == "PASS"
    assert items[0]["passed"] is True
    assert abs(payload["python_baseline_ms"] - baseline) < 1.0


def test_tle_recorded_in_evidence(tmp_path):
    """Pain #4+#5: TLE phải được ghi dạng bằng chứng, actual có thể trống."""
    slow_dir = tmp_path / "SE180002"
    slow_dir.mkdir()
    slow_src = slow_dir / "main.py"
    slow_src.write_text("import time\ntime.sleep(3)\n", encoding="utf-8")
    slow_sub = {"student_mssv": "SE180002", "id": 2, "source_file_path": str(slow_src)}
    tc = [{"input_data": "", "expected_output": "x", "score_weight": 1.0,
           "time_limit_ms": 200, "memory_limit_mb": 64, "matching_strategy": "EXACT_MATCH"}]
    result = grade_single_submission(slow_sub, "Python", tc, 1.0)
    assert result["verdict"] in ("TLE", "RE")  # Sandbox kill có thể sinh RE nếu shell của Windows hành khác
    payload = json.loads(result["diff_details"])
    assert payload["items"][0]["verdict"] in ("TLE", "RE")


def test_batch_cancel_keeps_unstarted_pending(tmp_path):
    """
    Pain #2: cancel_event set -> batch dừng ngay sau bài đang nắm:
    - Bài đã hoàn tất được cứu (lưu 1 bài), bài còn lại tất cả giữ PENDING.
    - Không orphan process, DB không ghi đè lên bài chưa chấm.
    """
    from database.db_manager import DatabaseManager
    from services.grading_service import GradingService

    db = DatabaseManager(db_path=str(tmp_path / "cancel_test.db"))
    class_id = db.create_class_session(
        class_name="CN-CancelTest", course_code="PRF",
        programming_language="C", folder_path=str(tmp_path), csv_path=""
    )
    db.add_testcase(class_id, input_data="", expected_output="ok", score_weight=1.0)

    subs = []
    for n in range(1, 7):
        sub_dir = tmp_path / f"SE00000{n}"
        sub_dir.mkdir()
        src = sub_dir / "main.py"
        src.write_text("import time\ntime.sleep(0.3)\nprint('ok')\n", encoding="utf-8")
        subs.append((f"SE00000{n}", str(src)))
    db.bulk_insert_submissions([(class_id, mssv, path) for mssv, path in subs])

    service = GradingService(db_manager=db)
    cancel = threading.Event()
    cancel.set()
    results = service.grade_class_batch(class_id, max_workers=2, cancel_event=cancel)

    # Cancel dừng ngay ở bài hoàn tất đầu tiên: chỉ 1 bài được cứu
    assert len(results) == 1

    rows = db.get_submissions_by_class(class_id)
    graded_rows = [r for r in rows if (r.get("final_verdict") or "PENDING").strip().upper() != "PENDING"]
    assert len(graded_rows) == 1                    # DB khớp đúng phần đã chấm
    assert len(rows) == 6                           # không mất bài
    pending_rows = [r for r in rows if (r.get("final_verdict") or "PENDING").strip().upper() == "PENDING"]
    assert len(pending_rows) == 5
    got_ids = {res["submission_id"] for res in results}
    pending_ids = {r["id"] for r in pending_rows}
    assert got_ids.isdisjoint(pending_ids)          # cancel không giẫm đè kết quả đã có


def test_resume_only_pending(tmp_path):
    """Pain #2 - chấm tiếp: chỉ chọn đúng các bài PENDING cho lần 'chấm tiếp'."""
    import time
    from database.db_manager import DatabaseManager
    from services.grading_service import GradingService

    db = DatabaseManager(db_path=str(tmp_path / "resume_test.db"))
    class_id = db.create_class_session(
        class_name="CN-ResumeTest", course_code="PRF",
        programming_language="C", folder_path=str(tmp_path), csv_path=""
    )
    db.add_testcase(class_id, input_data="", expected_output="ok", score_weight=1.0)

    subs = []
    for n in range(1, 5):
        sub_dir = tmp_path / f"SE10000{n}"
        sub_dir.mkdir()
        src = sub_dir / "main.py"
        src.write_text("import time\ntime.sleep(0.2)\nprint('ok')\n", encoding="utf-8")
        subs.append((f"SE10000{n}", str(src)))
    db.bulk_insert_submissions([(class_id, mssv, path) for mssv, path in subs])

    service = GradingService(db_manager=db)
    submit_count = 2
    rows = db.get_submissions_by_class(class_id)
    all_ids = [r["id"] for r in rows]
    partial_ids = all_ids[:submit_count]
    results = service.grade_class_batch(class_id, max_workers=2, submission_ids=partial_ids)
    assert len(results) == submit_count  # chỉ phần whitelist được chấm

    rows = db.get_submissions_by_class(class_id)
    untouched = [r for r in rows if r["id"] not in partial_ids]
    assert all((r.get("final_verdict") or "PENDING").strip().upper() == "PENDING" for r in untouched)


def test_copy_testcases_presets(tmp_path):
    """Pain #10: database.copy_testcases_from_class sao chép đủ testcase."""
    from database.db_manager import DatabaseManager

    db = DatabaseManager(db_path=str(tmp_path / "copy_test.db"))
    src_id = db.create_class_session(
        class_name="CopySrc", course_code="PRF", programming_language="C",
        folder_path=str(tmp_path), csv_path=""
    )
    dst_id = db.create_class_session(
        class_name="CopyDst", course_code="PRF", programming_language="C",
        folder_path=str(tmp_path), csv_path=""
    )
    db.add_testcase(src_id, input_data="a\n", expected_output="a", score_weight=2.0)
    db.add_testcase(src_id, input_data="b\n", expected_output="b", score_weight=3.0)

    copied = db.copy_testcases_from_class(src_id, dst_id)
    assert copied == 2
    assert len(db.get_testcases_by_class(dst_id)) == 2
    assert src_id in [c["id"] for c in db.get_preset_source_candidates()]
