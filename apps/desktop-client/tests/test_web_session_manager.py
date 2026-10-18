"""Unit tests for Web Grading Session Management System.

Covers:
- Session CRUD operations (create, retrieve, delete)
- Submission isolation per session
- Legacy orphaned submissions auto-migration into default session
- Cascading soft-delete of session and its linked submissions
- Scoped mode updates per session
"""

import pytest
from database.db_manager import DatabaseManager


@pytest.fixture
def db() -> DatabaseManager:
    return DatabaseManager(":memory:")


def test_create_and_get_web_session(db: DatabaseManager):
    """Verifies creating a session and fetching it by ID or in list."""
    s_id = db.create_web_session("Do An Cuoi Ky", "WEB201c", "SE1806")
    assert s_id > 0

    session = db.get_web_session_by_id(s_id)
    assert session is not None
    assert session["session_name"] == "Do An Cuoi Ky"
    assert session["course_code"] == "WEB201c"
    assert session["class_name"] == "SE1806"
    assert session["is_deleted"] == 0

    all_sessions = db.get_all_web_sessions()
    assert len(all_sessions) >= 1
    matching = [s for s in all_sessions if s["id"] == s_id]
    assert len(matching) == 1
    assert matching[0]["total_submissions"] == 0


def test_session_submissions_isolation(db: DatabaseManager):
    """Verifies that submissions added to Session A are isolated from Session B."""
    s_a = db.create_web_session("Session A", "WEB201c", "SE1806")
    s_b = db.create_web_session("Session B", "WEB201c", "SE1807")

    sub_a1 = db.add_web_submission(
        mssv="SE180001", name="Nguyen Van A",
        live_url="https://a1.vercel.app", repo_url="https://github.com/a1/repo",
        mode="HYBRID", course_code="WEB201c", class_name="SE1806",
        session_id=s_a
    )
    sub_a2 = db.add_web_submission(
        mssv="SE180002", name="Nguyen Van B",
        live_url="https://a2.vercel.app", repo_url="https://github.com/a2/repo",
        mode="HYBRID", course_code="WEB201c", class_name="SE1806",
        session_id=s_a
    )
    sub_b1 = db.add_web_submission(
        mssv="SE180003", name="Nguyen Van C",
        live_url="https://b1.vercel.app", repo_url="https://github.com/b1/repo",
        mode="HYBRID", course_code="WEB201c", class_name="SE1807",
        session_id=s_b
    )

    subs_a = db.get_all_web_submissions(s_a)
    subs_b = db.get_all_web_submissions(s_b)

    assert len(subs_a) == 2
    assert {s["mssv"] for s in subs_a} == {"SE180001", "SE180002"}

    assert len(subs_b) == 1
    assert {s["mssv"] for s in subs_b} == {"SE180003"}

    # Check total_submissions count aggregation
    sessions = {s["id"]: s["total_submissions"] for s in db.get_all_web_sessions()}
    assert sessions[s_a] == 2
    assert sessions[s_b] == 1


def test_ensure_default_web_session_migrates_orphans(db: DatabaseManager):
    """Verifies that orphaned submissions are only migrated when an active session exists."""
    # When no sessions exist, ensure_default_web_session returns None and does not invent dummy sessions
    assert db.ensure_default_web_session() is None
    assert len(db.get_all_web_sessions()) == 0

    # Insert legacy submissions with session_id=None
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO local_web_submissions (
                course_code, class_name, mssv, name, live_url, repo_url, mode, session_id
            ) VALUES ('WEB201c', 'SE1806', 'SE189999', 'Old Student', 'https://old.vercel.app', 'https://github.com/old/repo', 'HYBRID', NULL)
        """)
        conn.commit()

    # Now create a legitimate session
    s_id = db.create_web_session("Do An Nhom 1", "WEB201c", "SE1806")

    migrated_id = db.ensure_default_web_session()
    assert migrated_id == s_id

    subs = db.get_all_web_submissions(s_id)
    assert len(subs) == 1
    assert subs[0]["mssv"] == "SE189999"
    assert subs[0]["session_id"] == s_id


def test_get_latest_web_session(db: DatabaseManager):
    """Verifies get_latest_web_session returns None if empty, or the most recent session."""
    assert db.get_latest_web_session() is None

    s1 = db.create_web_session("Session 1", "WEB201c", "SE1806")
    s2 = db.create_web_session("Session 2", "WEB201c", "SE1806")

    latest = db.get_latest_web_session()
    assert latest is not None
    assert latest["id"] == s2


def test_delete_web_session_cascades_soft_delete(db: DatabaseManager):
    """Verifies that soft-deleting a session cascades to its submissions."""
    s_id = db.create_web_session("Temp Session", "WEB201c", "SE1806")
    db.add_web_submission(
        mssv="SE180010", name="Student Temp",
        live_url="https://temp.vercel.app", repo_url="https://github.com/temp/repo",
        mode="HYBRID", course_code="WEB201c", class_name="SE1806",
        session_id=s_id
    )

    assert len(db.get_all_web_submissions(s_id)) == 1

    db.delete_web_session(s_id)

    # Session is marked as deleted
    assert db.get_web_session_by_id(s_id) is None
    all_active_sessions = db.get_all_web_sessions()
    assert not any(s["id"] == s_id for s in all_active_sessions)

    # Linked submissions are also marked as deleted
    assert len(db.get_all_web_submissions(s_id)) == 0


def test_update_all_web_submissions_mode_scoped_to_session(db: DatabaseManager):
    """Verifies that update_all_web_submissions_mode with session_id only alters that session."""
    s1 = db.create_web_session("Session 1", "WEB201c", "SE1806")
    s2 = db.create_web_session("Session 2", "WEB201c", "SE1806")

    db.add_web_submission("SE10", "", live_url="https://a.com", repo_url="https://github.com/a/b", mode="HYBRID", course_code="WEB201c", class_name="SE1806", session_id=s1)
    db.add_web_submission("SE20", "", live_url="https://b.com", repo_url="https://github.com/b/c", mode="HYBRID", course_code="WEB201c", class_name="SE1806", session_id=s2)

    db.update_all_web_submissions_mode("WEB201c", "SE1806", "LIVE_ONLY", session_id=s1)

    s1_subs = db.get_all_web_submissions(s1)
    s2_subs = db.get_all_web_submissions(s2)

    assert s1_subs[0]["mode"] == "LIVE_ONLY"
    assert s2_subs[0]["mode"] == "HYBRID"
