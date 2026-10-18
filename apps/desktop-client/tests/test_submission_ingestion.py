"""Submission ingestion / folder re-scan (database.db_manager.rescan_and_sync_submissions).

Covers AT01 (folder ingestion discovers students) and the re-scan semantics:
existing students keep their grades and only get their source path refreshed,
brand-new students are added as PENDING, and class total_submissions stays in
sync. Pure SQLite - no Qt, no filesystem.
"""

import pytest

from database.db_manager import DatabaseManager


@pytest.fixture
def db() -> DatabaseManager:
    return DatabaseManager(":memory:")


def test_rescan_adds_new_students_and_updates_existing_paths(db):
    class_id = db.create_class_session("SE1801_PRF192_PE", "PRF", "C", "D:/Sub")
    db.bulk_insert_submissions([(class_id, "SE180001", "D:/Sub/old/SE180001_Q1.c")])
    sub_id = db.get_submissions_by_class(class_id)[0]["id"]
    db.save_console_grading_result(
        submission_id=sub_id, matching_strategy="EXACT_MATCH",
        calculated_score=8.5, final_verdict="WA", execution_time_ms=120.0,
    )

    added, existing = db.rescan_and_sync_submissions(class_id, [
        {"student_mssv": "SE180001", "source_file_path": "D:/Sub/new/SE180001_Q1.c"},
        {"student_mssv": "SE180002", "source_file_path": "D:/Sub/new/SE180002_Q1.c"},
    ])

    assert (added, existing) == (1, 1)
    subs = {s["student_mssv"]: s for s in db.get_submissions_by_class(class_id)}
    assert set(subs) == {"SE180001", "SE180002"}
    assert subs["SE180001"]["source_file_path"] == "D:/Sub/new/SE180001_Q1.c"
    assert subs["SE180001"]["calculated_score"] == 8.5  # grade preserved on re-scan
    assert subs["SE180002"]["status"] == "PENDING"
    assert db.get_class_by_id(class_id)["total_submissions"] == 2


def test_rescan_with_only_existing_students_reports_no_additions(db):
    class_id = db.create_class_session("SE1801_RESCAN", "PRF", "C", "D:/Sub")
    db.bulk_insert_submissions([(class_id, "SE180001", "D:/Sub/SE180001_Q1.c")])

    added, existing = db.rescan_and_sync_submissions(class_id, [
        {"student_mssv": "SE180001", "source_file_path": "D:/Sub/SE180001_Q1.c"},
    ])

    assert (added, existing) == (0, 1)


def test_rescan_empty_directory_keeps_existing_students(db):
    class_id = db.create_class_session("SE1801_EMPTY", "PRF", "C", "D:/Sub")
    db.bulk_insert_submissions([(class_id, "SE180001", "D:/Sub/SE180001_Q1.c")])

    added, existing = db.rescan_and_sync_submissions(class_id, [])

    assert (added, existing) == (0, 0)
    assert len(db.get_submissions_by_class(class_id)) == 1  # nothing silently deleted
