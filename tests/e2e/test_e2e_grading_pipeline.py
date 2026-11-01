"""E2E — grading pipeline thật (E2E01_GradingPipeline).

Toàn bộ pipeline chấm bài chạy thật với compiler thực tế:
fixture bài nộp C/Java/Python -> SQLite -> GradingService (ProcessPoolExecutor)
-> sandbox thật -> kết quả lưu DB -> export results.csv 7 cột.

Test ID: E2E<NN>_<ModulePascalCase>_TC<nnn> — rules/testcase-rules.md chỉ định
nghĩa UT/IT/ST/AT; level e2e dùng prefix E2E theo cùng khuôn mẫu.
"""
import shutil

import pytest

from database.db_manager import DatabaseManager
from services.export_service import CSV_COLUMNS, ExportService
from services.grading_service import GradingService

pytestmark = pytest.mark.e2e


@pytest.fixture
def db():
    return DatabaseManager(":memory:")


def _copy_fixture(fixtures_dir, tmp_path, source_name, dest_name):
    dest = tmp_path / dest_name
    shutil.copyfile(fixtures_dir / "submissions" / source_name, dest)
    return dest


def _make_class(db, tmp_path, name, language):
    return db.create_class_session(name, "PRF", language, str(tmp_path))


def _add_sum_testcases(db, class_id, time_limit_ms=1500, question="Q1"):
    for input_data, expected in (("3 4\n", "7"), ("10 20\n", "30")):
        db.add_testcase(
            class_id,
            input_data,
            expected,
            score_weight=1.0,
            time_limit_ms=time_limit_ms,
            matching_strategy="EXACT_MATCH",
            question_number=question,
        )


def _export_csv(db, class_id, testcase_count, tmp_path):
    subs = db.get_submissions_by_class(class_id)
    rows = ExportService().build_grade_rows(subs, testcase_count)
    csv_path = tmp_path / "results.csv"
    ExportService().export_csv(rows, str(csv_path))
    return subs, csv_path


# ---------------------------------------------------------------------------
# Normal: C đúng -> AC, điểm tối đa, CSV chuẩn 7 cột
# ---------------------------------------------------------------------------
def test_e2e01_gradingpipeline_tc001_c_correct_ac_and_csv_export(db, tmp_path, fixtures_dir, require_c_toolchain):
    src = _copy_fixture(fixtures_dir, tmp_path, "sum_correct.c", "SE180001.c")
    class_id = _make_class(db, tmp_path, "E2E_C_AC", "C")
    db.bulk_insert_submissions([(class_id, "SE180001", str(src))])
    _add_sum_testcases(db, class_id)

    results = GradingService(db).grade_class_batch(class_id, max_workers=2)

    assert len(results) == 1
    assert results[0]["verdict"] == "AC"
    assert results[0]["score"] == 10.0

    subs, csv_path = _export_csv(db, class_id, 2, tmp_path)
    assert subs[0]["final_verdict"] == "AC"

    lines = csv_path.read_text(encoding="utf-8-sig").splitlines()
    assert lines[0].split(",") == list(CSV_COLUMNS)
    body = "\n".join(lines[1:])
    assert "SE180001" in body
    assert "2/2,AC," in body
    assert "10.0" in body


# ---------------------------------------------------------------------------
# Normal: C sai output -> WA, 0 điểm
# ---------------------------------------------------------------------------
def test_e2e01_gradingpipeline_tc002_c_wrong_output_wa(db, tmp_path, fixtures_dir, require_c_toolchain):
    src = _copy_fixture(fixtures_dir, tmp_path, "sum_wrong.c", "SE180002.c")
    class_id = _make_class(db, tmp_path, "E2E_C_WA", "C")
    db.bulk_insert_submissions([(class_id, "SE180002", str(src))])
    _add_sum_testcases(db, class_id)

    results = GradingService(db).grade_class_batch(class_id, max_workers=1)

    assert results[0]["verdict"] == "WA"
    assert results[0]["score"] == 0.0

    subs, csv_path = _export_csv(db, class_id, 2, tmp_path)
    assert subs[0]["final_verdict"] == "WA"
    assert "0/2,WA," in csv_path.read_text(encoding="utf-8-sig")


# ---------------------------------------------------------------------------
# Exception: C lỗi cú pháp -> CE, có compile log
# ---------------------------------------------------------------------------
def test_e2e01_gradingpipeline_tc003_c_syntax_error_ce(db, tmp_path, fixtures_dir, require_c_toolchain):
    src = _copy_fixture(fixtures_dir, tmp_path, "sum_ce.c", "SE180003.c")
    class_id = _make_class(db, tmp_path, "E2E_C_CE", "C")
    db.bulk_insert_submissions([(class_id, "SE180003", str(src))])
    _add_sum_testcases(db, class_id)

    results = GradingService(db).grade_class_batch(class_id, max_workers=1)

    assert results[0]["verdict"] == "CE"
    assert results[0]["score"] == 0.0

    persisted = db.get_submission_result(db.get_submissions_by_class(class_id)[0]["id"])
    assert persisted["final_verdict"] == "CE"
    assert persisted["compile_log"]


# ---------------------------------------------------------------------------
# Boundary: C vòng lặp vô hạn với time_limit 500ms -> TLE
# ---------------------------------------------------------------------------
def test_e2e01_gradingpipeline_tc004_c_infinite_loop_tle(db, tmp_path, fixtures_dir, require_c_toolchain):
    src = _copy_fixture(fixtures_dir, tmp_path, "sum_tle.c", "SE180004.c")
    class_id = _make_class(db, tmp_path, "E2E_C_TLE", "C")
    db.bulk_insert_submissions([(class_id, "SE180004", str(src))])
    _add_sum_testcases(db, class_id, time_limit_ms=500)

    results = GradingService(db).grade_class_batch(class_id, max_workers=1)

    assert results[0]["verdict"] == "TLE"
    assert results[0]["score"] == 0.0
    subs, _ = _export_csv(db, class_id, 2, tmp_path)
    assert subs[0]["final_verdict"] == "TLE"


# ---------------------------------------------------------------------------
# Normal: Python đúng -> AC (interpreter thật, có trừ baseline khởi động)
# ---------------------------------------------------------------------------
def test_e2e01_gradingpipeline_tc005_python_correct_ac(db, tmp_path, fixtures_dir, require_python_toolchain):
    src = _copy_fixture(fixtures_dir, tmp_path, "sum_correct.py", "SE180005.py")
    class_id = _make_class(db, tmp_path, "E2E_PY_AC", "PYTHON")
    db.bulk_insert_submissions([(class_id, "SE180005", str(src))])
    _add_sum_testcases(db, class_id, time_limit_ms=3000)

    results = GradingService(db).grade_class_batch(class_id, max_workers=1)

    assert results[0]["verdict"] == "AC"
    assert results[0]["score"] == 10.0
    subs, _ = _export_csv(db, class_id, 2, tmp_path)
    assert subs[0]["final_verdict"] == "AC"


# ---------------------------------------------------------------------------
# Normal: Java đúng -> AC (javac + java thật; JVM khởi động chậm nên limit rộng)
# ---------------------------------------------------------------------------
def test_e2e01_gradingpipeline_tc006_java_correct_ac(db, tmp_path, fixtures_dir, require_java_toolchain):
    src = _copy_fixture(fixtures_dir, tmp_path, "SumCorrect.java", "SumCorrect.java")
    class_id = _make_class(db, tmp_path, "E2E_JAVA_AC", "JAVA")
    db.bulk_insert_submissions([(class_id, "SE180006", str(src))])
    _add_sum_testcases(db, class_id, time_limit_ms=5000)

    results = GradingService(db).grade_class_batch(class_id, max_workers=1)

    assert results[0]["verdict"] == "AC"
    assert results[0]["score"] == 10.0
    subs, _ = _export_csv(db, class_id, 2, tmp_path)
    assert subs[0]["final_verdict"] == "AC"


# ---------------------------------------------------------------------------
# Boundary: multi-question — thư mục sinh viên chứa Q1.c (đúng) + Q2.c (sai)
# ---------------------------------------------------------------------------
def test_e2e01_gradingpipeline_tc007_multi_question_partial_score(db, tmp_path, fixtures_dir, require_c_toolchain):
    folder = tmp_path / "SE180007"
    folder.mkdir()
    shutil.copyfile(fixtures_dir / "submissions" / "sum_correct.c", folder / "Q1.c")
    shutil.copyfile(fixtures_dir / "submissions" / "sum_wrong.c", folder / "Q2.c")

    class_id = _make_class(db, tmp_path, "E2E_C_MULTIQ", "C")
    db.bulk_insert_submissions([(class_id, "SE180007", str(folder))])
    _add_sum_testcases(db, class_id, question="Q1")
    _add_sum_testcases(db, class_id, question="Q2")

    results = GradingService(db).grade_class_batch(class_id, max_workers=1)

    assert results[0]["verdict"] == "WA"
    assert results[0]["score"] == 5.0  # 1/2 câu đúng
    subs, csv_path = _export_csv(db, class_id, 4, tmp_path)
    assert subs[0]["final_verdict"] == "WA"
    assert "2/4,WA," in csv_path.read_text(encoding="utf-8-sig")
