"""Nạp bài nộp nhiều câu: thư mục sinh viên có Q1.c..Q5.c phải được nhận là một bài nộp."""

from ui.dialogs.session_dialog import find_multi_question_files


def test_finds_all_question_files_in_numeric_order(tmp_path):
    for name in ["Q10.c", "Q2.c", "Q1.c", "Q5.c", "Q3.c", "notes.txt"]:
        (tmp_path / name).write_text("x", encoding="utf-8")
    assert find_multi_question_files(str(tmp_path), (".c", ".cpp")) == ["Q1.c", "Q2.c", "Q3.c", "Q5.c", "Q10.c"]


def test_ignores_other_extensions_and_plain_entry_file(tmp_path):
    (tmp_path / "Q1.java").write_text("x", encoding="utf-8")
    (tmp_path / "main.c").write_text("x", encoding="utf-8")
    assert find_multi_question_files(str(tmp_path), (".c", ".cpp")) == []


def test_missing_folder_returns_empty(tmp_path):
    assert find_multi_question_files(str(tmp_path / "khong_co"), (".c",)) == []
