"""DatabaseManager (database.db_manager) on an in-memory SQLite.

Covers UC-17 plagiarism report persistence (save / update evidence /
soft-delete on re-scan / ranked listing), grading result persistence and
status propagation, submission override, and the lightweight web-submission
column migration + missing-folder flags (web studio folder import).
"""

import pytest

from database.db_manager import DatabaseManager


@pytest.fixture
def db() -> DatabaseManager:
    return DatabaseManager(":memory:")


@pytest.fixture
def class_id(db) -> int:
    return db.create_class_session("SE1801_PRF192_PE", "PRF", "C", "D:/Sub")


def _persist_pair(db, submissions):
    for s in submissions:
        db.save_console_grading_result(
            submission_id=s["submission_id"],
            matching_strategy="EXACT_MATCH",
            calculated_score=s["score"],
            final_verdict=s["verdict"],
            execution_time_ms=s["time"],
        )


# ------------------------------------------------------------------------------
# Sessions & submissions
# ------------------------------------------------------------------------------
def test_create_class_session_roundtrip(db, class_id):
    cls = db.get_class_by_id(class_id)
    assert cls["class_name"] == "SE1801_PRF192_PE"
    assert cls["programming_language"] == "C"


def test_bulk_insert_updates_total_submissions(db, class_id):
    added = db.bulk_insert_submissions([
        (class_id, "SE180001", "D:/Sub/SE180001_Q1.c"),
        (class_id, "SE180002", "D:/Sub/SE180002_Q1.c"),
    ])
    assert added == 2
    subs = db.get_submissions_by_class(class_id)
    assert [s["student_mssv"] for s in subs] == ["SE180001", "SE180002"]
    assert all(s["status"] == "PENDING" for s in subs)
    assert db.get_class_by_id(class_id)["total_submissions"] == 2


def test_delete_class_session_is_soft(db, class_id):
    db.delete_class_session(class_id)
    assert db.get_class_by_id(class_id) is None


# ------------------------------------------------------------------------------
# Testcases & grading results
# ------------------------------------------------------------------------------
def test_testcase_crud_and_strategy_update(db, class_id):
    tc_id = db.add_testcase(class_id, "1\n", "2", score_weight=2.0, matching_strategy="EXACT_MATCH")
    rows = db.get_testcases_by_class(class_id)
    assert len(rows) == 1 and rows[0]["expected_output"] == "2"

    assert db.update_testcase(tc_id, "Q1", "3\n", "6", score_weight=2.0) is True
    assert db.update_class_matching_strategy(class_id, "FLOAT_TOLERANCE") is None
    assert db.get_testcases_by_class(class_id)[0]["matching_strategy"] == "FLOAT_TOLERANCE"

    assert db.delete_testcase(tc_id) is True
    assert db.get_testcases_by_class(class_id) == []


def test_save_console_result_updates_submission_status(db, class_id):
    db.bulk_insert_submissions([(class_id, "SE180001", "D:/Sub/a.c")])
    sub_id = db.get_submissions_by_class(class_id)[0]["id"]

    db.save_console_grading_result(
        submission_id=sub_id, matching_strategy="EXACT_MATCH",
        calculated_score=8.0, final_verdict="WA",
        execution_time_ms=123.0, memory_used_mb=11.5,
        diff_details="- Expected 2, got 3",
    )
    result = db.get_submission_result(sub_id)
    assert result["calculated_score"] == 8.0 and result["final_verdict"] == "WA"
    status = db.get_submissions_by_class(class_id)[0]["status"]
    assert status == "WA"


def test_override_score_creates_manual_result(db, class_id):
    db.bulk_insert_submissions([(class_id, "SE180001", "D:/Sub/a.c")])
    sub_id = db.get_submissions_by_class(class_id)[0]["id"]

    db.override_submission_score(sub_id, 4.5, "Sua for(i=1;i<=n;i++) de quay lai")
    result = db.get_submission_result(sub_id)
    assert result["manual_override_score"] == 4.5
    assert result["manual_override_reason"].startswith("Sua for")
    assert db.get_submissions_by_class(class_id)[0]["status"] == "OVERRIDDEN"


def test_update_ai_feedback_writes_latest_result(db, class_id):
    db.bulk_insert_submissions([(class_id, "SE180001", "D:/Sub/a.c")])
    sub_id = db.get_submissions_by_class(class_id)[0]["id"]
    db.save_console_grading_result(sub_id, "EXACT_MATCH", 10.0, "AC")
    db.update_ai_feedback(sub_id, "Em da dung thuat toan DP.")
    assert db.get_submission_result(sub_id)["ai_feedback"] == "Em da dung thuat toan DP."


# ------------------------------------------------------------------------------
# Plagiarism reports (UC-17 / IT13)
# ------------------------------------------------------------------------------
def test_get_plagiarism_reports_orders_by_similarity_desc(db, class_id):
    db.save_plagiarism_report(class_id, "SE180001", "SE180002", 82.5)
    db.save_plagiarism_report(class_id, "SE180003", "SE180004", 95.1)
    reports = db.get_plagiarism_reports(class_id)
    assert [r["similarity_percentage"] for r in reports] == [95.1, 82.5]
    assert all(r["is_deleted"] == 0 for r in reports)


def test_update_plagiarism_report_evidence_matches_pair_in_any_order(db, class_id):
    db.save_plagiarism_report(class_id, "SE180001", "SE180002", 88.0)
    updated = db.update_plagiarism_report_evidence(
        class_id, "SE180002", "SE180001", "Vong 2: AI Hub xac minh renamed bi-ops."
    )
    assert updated is True
    assert db.get_plagiarism_reports(class_id)[0]["ai_evidence_details"].startswith("Vong 2")


def test_update_evidence_on_unknown_pair_returns_false(db, class_id):
    assert db.update_plagiarism_report_evidence(
        class_id, "SE180003", "SE180004", "no report row"
    ) is False


def test_clear_plagiarism_reports_soft_deletes_before_rescan(db, class_id):
    db.save_plagiarism_report(class_id, "SE180001", "SE180002", 90.0)
    db.clear_plagiarism_reports(class_id)
    assert db.get_plagiarism_reports(class_id) == []


def test_rescan_after_clear_saves_fresh_reports(db, class_id):
    db.save_plagiarism_report(class_id, "SE180001", "SE180002", 90.0)
    db.clear_plagiarism_reports(class_id)
    db.save_plagiarism_report(class_id, "SE180001", "SE180002", 17.0)
    reports = db.get_plagiarism_reports(class_id)
    assert [r["similarity_percentage"] for r in reports] == [17.0]


# ------------------------------------------------------------------------------
# Web submissions (WEB Studio) + lightweight migration
# ------------------------------------------------------------------------------
def test_web_submission_columns_exist_after_migration(db):
    with db.get_connection() as conn:
        cols = {row[1] for row in conn.execute("PRAGMA table_info(local_web_submissions)")}
    assert {"source_folder_path", "is_missing", "display_mssv", "rubric_log", "screenshot_path", "ai_feedback", "graded_at"} <= cols


def test_add_web_submission_with_folder_metadata(db):
    id_ = db.add_web_submission(
        mssv="SE180001", name="Nguyen Van A", live_url="http://site.dev",
        course_code="WEB201c", class_name="SE1806",
        source_folder_path="D:/WebSub/SE180001", display_mssv="SE180001",
    )
    rows = db.get_all_web_submissions()
    assert len(rows) == 1
    assert rows[0]["source_folder_path"] == "D:/WebSub/SE180001"
    assert rows[0]["display_mssv"] == "SE180001"


def test_set_web_submission_missing_flags_without_scores(db):
    id_ = db.add_web_submission(
        mssv="SE180001", name="NV A", live_url="http://site.dev",
        course_code="WEB201c", class_name="SE1806",
        source_folder_path="D:/WebSub/SE180001",
    )
    assert db.set_web_submission_missing(id_, True) is True
    assert db.get_all_web_submissions()[0]["is_missing"] == 1
    assert db.set_web_submission_missing(id_, False) is True
    assert db.get_all_web_submissions()[0]["is_missing"] == 0


def test_update_web_submission_source_refreshes_metadata(db):
    id_ = db.add_web_submission(
        mssv="SE180001", name="NV A", live_url="", repo_url="",
        course_code="WEB201c", class_name="SE1806",
        source_folder_path="D:/old/SE180001", display_mssv="SE180001",
    )
    db.set_web_submission_missing(id_, True)

    assert db.update_web_submission_source(
        id_, source_folder_path="D:/new/SE180001", display_mssv="SE180001",
        name="Nguyen Van A", live_url="http://live.dev", repo_url="http://repo.dev",
    ) is True

    row = db.get_all_web_submissions()[0]
    assert row["source_folder_path"] == "D:/new/SE180001"
    assert row["name"] == "Nguyen Van A"
    assert row["is_missing"] == 0


def test_update_web_submission_source_keeps_fields_when_none_given(db):
    id_ = db.add_web_submission(
        mssv="SE180001", name="NV A", live_url="http://old.dev",
        course_code="WEB201c", class_name="SE1806",
    )
    db.update_web_submission_source(id_, source_folder_path=None)
    row = db.get_all_web_submissions()[0]
    assert row["live_url"] == "http://old.dev" and row["is_missing"] == 0


def test_update_web_submission_scores_persists_evidence(db):
    id_ = db.add_web_submission(
        mssv="SE180002", name="NV B", live_url="http://site.dev",
        course_code="WEB201c", class_name="SE1806",
    )
    assert db.update_web_submission_scores(
        submission_id=id_, score_dom=8.0, score_lint=7.5, score_e2e=6.0,
        score_ui=9.0, total_score=7.7, verdict="PASSED",
        rubric_log="[DOM]: 8/8 thẻ -> 8.0/10", screenshot_path="D:/shots/SE180002.png",
        ai_feedback="Bố cục cân đối",
    ) is True

    row = db.get_all_web_submissions()[0]
    assert row["total_score"] == 7.7 and row["verdict"] == "PASSED"
    assert row["rubric_log"] == "[DOM]: 8/8 thẻ -> 8.0/10"
    assert row["screenshot_path"] == "D:/shots/SE180002.png"
    assert row["ai_feedback"] == "Bố cục cân đối"
    assert row["graded_at"] is not None

