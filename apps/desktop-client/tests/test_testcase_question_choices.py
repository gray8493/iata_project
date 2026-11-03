"""Hồi quy: danh sách câu không bị gõ cứng Q1..Q5 (đề có thể có 9 câu)."""

from database.db_manager import DatabaseManager
from ui.dialogs.testcase_dialog import QUESTION_MIN_CHOICES, _question_choices


def test_minimum_choices_without_db():
    assert _question_choices(None, None) == [f"Q{i}" for i in range(1, QUESTION_MIN_CHOICES + 1)]


def test_choices_grow_to_highest_existing_question():
    db = DatabaseManager(":memory:")
    cid = db.create_class_session("T", "C", "C", "x", "")
    db.add_testcase(cid, "1", "1", question_number="Q12")
    choices = _question_choices(db, cid)
    assert choices[-1] == "Q12"
    assert len(choices) == 12
