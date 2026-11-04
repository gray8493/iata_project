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


from ui.dialogs.testcase_dialog import split_problem_by_question  # noqa: E402


def test_split_problem_by_question_keeps_preamble_and_each_question():
    text = (
        "Đề chung: đọc số nguyên từ stdin.\n"
        "Câu 1: Tính tổng hai số.\nInput: a b\n"
        "Câu 2: Tìm số lớn nhất.\nInput: n\n"
        "Câu 10: Đảo ngược chuỗi.\n"
    )
    preamble, sections = split_problem_by_question(text)
    assert preamble.startswith("Đề chung")
    assert list(sections) == ["Q1", "Q2", "Q10"]
    assert sections["Q1"].startswith("Câu 1") and "Tìm số" not in sections["Q1"]
    assert "Input: n" in sections["Q2"]


def test_split_problem_without_headers_returns_empty():
    assert split_problem_by_question("Tính tổng hai số nguyên.") == ("", {})


def test_split_problem_accepts_q_and_question_headers():
    _, sections = split_problem_by_question("Q1 tổng\nQuestion 2: tích\n")
    assert list(sections) == ["Q1", "Q2"]
