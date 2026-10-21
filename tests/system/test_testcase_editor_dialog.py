"""System tests - Testcase Editor dialog (ui.dialogs.testcase_dialog.TestcaseEditDialog).

Feature: hộp thoại "Thêm/Sửa Testcase" phiên bản nhiều testcase cho một câu hỏi.

- Cột trái: danh sách testcase (Thêm / Nhân Bản / Xóa, kéo thả đổi thứ tự).
- Cột phải: tab "Chi Tiết Testcase" (2 chế độ Văn bản / Theo dòng, hiện ký tự ẩn,
  thống kê "N dòng, M ký tự", cảnh báo không chặn lưu) và tab "Dán Nhiều Testcase".
- Lưu: vẫn ghi 2 chuỗi input_data/expected_output (các dòng nối bằng "\\n"),
  không đổi schema CSDL.

Runs the real PyQt6 dialog (offscreen QApplication) with an in-memory SQLite DB so
the whole add/edit/delete/reorder path is exercised without network or a display.
"""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PyQt6")

from PyQt6.QtWidgets import QLineEdit, QMessageBox, QWidget

from database.db_manager import DatabaseManager
from ui.components.multiline_field import (
    HIDDEN_LINE_END,
    HIDDEN_TRAILING_SPACE,
    line_stats,
    text_warnings,
    visualize_hidden_chars,
)
from ui.components.table_actions import make_action_cell, make_row_button, preview_multiline
from ui.dialogs.testcase_dialog import TestcaseEditDialog

# Tên lớp bắt đầu bằng "Test" nên phải tắt thu thập pytest để tránh cảnh báo.
TestcaseEditDialog.__test__ = False
from ui.styles.theme import LIGHT_THEME_QSS


@pytest.fixture
def db_session():
    """CSDL SQLite trong bộ nhớ + 1 đợt chấm có 3 testcase của Q1 và 1 của Q2."""
    db = DatabaseManager(":memory:")
    class_id = db.create_class_session("SE1801 - SWD392", "SWD392", "C", r"C:\tmp")
    db.add_testcase(class_id, "1 2", "3", 1.0, 1000, 128, "EXACT_MATCH", "Q1")
    db.add_testcase(class_id, "4\n5", "9", 2.0, 1000, 128, "EXACT_MATCH", "Q1")
    db.add_testcase(class_id, "7", "14", 1.0, 1500, 256, "EXACT_MATCH", "Q1")
    db.add_testcase(class_id, "q2-in", "q2-out", 1.0, 1000, 128, "EXACT_MATCH", "Q2")
    return db, class_id


def _silence(monkeypatch, question_answer=QMessageBox.StandardButton.Yes):
    """Chặn hộp thoại chặn (blocking) của Qt trong môi trường test."""
    calls = {"warning": [], "information": [], "question": []}
    monkeypatch.setattr(
        QMessageBox, "warning",
        lambda *a, **k: calls["warning"].append(a) or QMessageBox.StandardButton.Ok,
    )
    monkeypatch.setattr(
        QMessageBox, "information",
        lambda *a, **k: calls["information"].append(a) or QMessageBox.StandardButton.Ok,
    )
    monkeypatch.setattr(
        QMessageBox, "question",
        lambda *a, **k: calls["question"].append(a) or question_answer,
    )
    return calls


def _q1_rows(db, class_id):
    return [
        row for row in db.get_testcases_by_class(class_id)
        if row["question_number"] == "Q1"
    ]


def _type(field_widget, value):
    """Mô phỏng người dùng gõ vào ô dữ liệu (phát signal textChanged như thật)."""
    field_widget.editor.setPlainText(value)


# ------------------------------------------------------------------------------
# Normal
# ------------------------------------------------------------------------------
def test_st05_testcaseeditor_tc001_lists_testcases_of_question(qapp, db_session):
    """ST05_TestcaseEditor_TC001: mở dialog nạp đúng testcase của câu hỏi + tổng trọng số."""
    db, class_id = db_session

    dlg = TestcaseEditDialog(db=db, class_id=class_id, question_number="Q1")

    assert len(dlg.testcases) == 3
    assert dlg.lbl_totals.text() == "3 testcase, tổng trọng số 4.0"
    assert dlg.list_tc.count() == 3
    # Giới hạn thời gian/bộ nhớ không còn nhập trong dialog (đó là cấu hình chung).
    assert not hasattr(dlg, "sp_q_time") and not hasattr(dlg, "chk_override")
    # Testcase đã có vẫn giữ nguyên giới hạn đang lưu.
    assert dlg.testcases[2]["time_limit_ms"] == 1500
    assert dlg.testcases[2]["memory_limit_mb"] == 256


def test_st05_testcaseeditor_tc002_saves_edited_multi_line_content(qapp, db_session, monkeypatch):
    """ST05_TestcaseEditor_TC002: sửa nội dung nhiều dòng rồi Lưu -> CSDL đúng chuỗi."""
    db, class_id = db_session
    _silence(monkeypatch)
    dlg = TestcaseEditDialog(db=db, class_id=class_id, question_number="Q1")

    dlg.list_tc.setCurrentRow(0)
    _type(dlg.f_input, "1\n2\n3")
    _type(dlg.f_output, "6")
    dlg.sp_weight.setValue(2.5)

    assert dlg._save(keep_open=False) is True

    saved = _q1_rows(db, class_id)[0]
    assert saved["input_data"] == "1\n2\n3"
    assert saved["expected_output"] == "6"
    assert saved["score_weight"] == pytest.approx(2.5)


def test_st05_testcaseeditor_tc003_adds_new_testcase(qapp, db_session, monkeypatch):
    """ST05_TestcaseEditor_TC003: "Thêm Testcase" + Lưu -> CSDL có thêm 1 bản ghi."""
    db, class_id = db_session
    _silence(monkeypatch)
    dlg = TestcaseEditDialog(db=db, class_id=class_id, question_number="Q1")

    dlg._add_testcase()
    _type(dlg.f_input, "10")
    _type(dlg.f_output, "20")

    assert dlg._save(keep_open=False) is True

    rows = _q1_rows(db, class_id)
    assert len(rows) == 4
    assert rows[-1]["input_data"] == "10"
    assert rows[-1]["expected_output"] == "20"


def test_st05_testcaseeditor_tc004_deletes_testcase(qapp, db_session, monkeypatch):
    """ST05_TestcaseEditor_TC004: xóa testcase (xác nhận Yes) + Lưu -> bản ghi bị xóa mềm."""
    db, class_id = db_session
    _silence(monkeypatch)
    dlg = TestcaseEditDialog(db=db, class_id=class_id, question_number="Q1")
    removed_id = dlg.testcases[1]["id"]

    dlg.list_tc.setCurrentRow(1)
    dlg._delete_testcase()
    assert len(dlg.testcases) == 2

    assert dlg._save(keep_open=False) is True

    rows = _q1_rows(db, class_id)
    assert len(rows) == 2
    assert removed_id not in [row["id"] for row in rows]


def test_st05_testcaseeditor_tc005_saves_and_keeps_editing(qapp, db_session, monkeypatch):
    """ST05_TestcaseEditor_TC005: "Lưu và Thêm Tiếp" ghi CSDL và để lại ô trống mới."""
    db, class_id = db_session
    _silence(monkeypatch)
    dlg = TestcaseEditDialog(db=db, class_id=class_id, question_number="Q1")

    dlg.list_tc.setCurrentRow(0)
    _type(dlg.f_output, "3")
    assert dlg._save(keep_open=True) is True

    assert len(_q1_rows(db, class_id)) == 3
    assert len(dlg.testcases) == 4  # 3 cũ + 1 ô trống chờ nhập
    assert dlg.testcases[-1]["expected_output"] == ""
    assert dlg.list_tc.currentRow() == 3


# ------------------------------------------------------------------------------
# Boundary
# ------------------------------------------------------------------------------
def test_st05_testcaseeditor_tc006_switching_modes_keeps_data(qapp):
    """ST05_TestcaseEditor_TC006: chuyển Văn bản <-> Theo dòng không mất dữ liệu (biên)."""
    dlg = TestcaseEditDialog()
    original = "5\n4 -3 7 2 11"
    _type(dlg.f_input, original)
    dlg.f_input.set_text(original)

    for _ in range(3):
        dlg.f_input.btn_mode_lines.click()
        assert dlg.f_input.text() == original
        assert dlg.f_input.list_lines.count() == 2
        dlg.f_input.btn_mode_text.click()
        assert dlg.f_input.text() == original
        assert dlg.f_input.editor.toPlainText() == original


def test_st05_testcaseeditor_tc007_line_mode_joins_with_newline(qapp):
    """ST05_TestcaseEditor_TC007: chế độ Theo dòng lưu bằng "\\n", thêm dòng mới (biên)."""
    dlg = TestcaseEditDialog()
    dlg.f_input.set_text("1")
    dlg.f_input.btn_mode_lines.click()

    dlg.f_input._add_line()
    assert dlg.f_input.list_lines.count() == 2
    assert dlg.f_input.text() == "1\n"

    # Gõ vào dòng thứ hai -> chuỗi lưu nối bằng "\n"
    row = dlg.f_input.list_lines.itemWidget(dlg.f_input.list_lines.item(1))
    line_edit = row.findChild(QLineEdit)
    line_edit.setText("2")
    line_edit.textEdited.emit("2")

    assert dlg.f_input.text() == "1\n2"


def test_st05_testcaseeditor_tc008_hidden_chars_is_read_only(qapp):
    """ST05_TestcaseEditor_TC008: "Hiện ký tự ẩn" chỉ để xem, không đổi dữ liệu (biên)."""
    dlg = TestcaseEditDialog()
    original = "a  \nb"
    _type(dlg.f_input, original)

    dlg.f_input.chk_hidden.setChecked(True)

    shown = dlg.f_input.editor.toPlainText()
    assert "·" in shown and HIDDEN_LINE_END in shown
    assert dlg.f_input.editor.isReadOnly() is True
    assert dlg.f_input.text() == original

    dlg.f_input.chk_hidden.setChecked(False)
    assert dlg.f_input.editor.isReadOnly() is False
    assert dlg.f_input.editor.toPlainText() == original


def test_st05_testcaseeditor_tc009_paste_preview_reports_invalid_rows(qapp, monkeypatch):
    """ST05_TestcaseEditor_TC009: dán 2 hợp lệ + 1 lỗi -> chỉ thêm 2, báo rõ dòng lỗi (biên)."""
    calls = _silence(monkeypatch)
    dlg = TestcaseEditDialog()

    dlg.txt_paste.setPlainText(
        '5\n===\nTong = 5\n---\n7\n===\nTong = 7\n---\n9\n'
    )
    dlg._preview_paste()

    assert dlg.lbl_paste_result.text() == "2 testcase hợp lệ, 1 dòng lỗi."
    assert dlg.table_paste.rowCount() == 3
    assert dlg.btn_add_all.isEnabled() is True

    dlg._add_all_pasted()

    assert len(dlg.testcases) == 3  # 1 ô trống ban đầu + 2 testcase hợp lệ
    assert dlg.testcases[1]["expected_output"] == "Tong = 5"
    assert dlg.testcases[2]["expected_output"] == "Tong = 7"
    assert "Bỏ qua 1 dòng lỗi" in calls["information"][0][2]


def test_st05_testcaseeditor_tc010_paste_all_invalid_disables_add(qapp):
    """ST05_TestcaseEditor_TC010: dán toàn dòng lỗi -> nút "Thêm Tất Cả" bị vô hiệu (biên)."""
    dlg = TestcaseEditDialog()

    dlg.txt_paste.setPlainText("[{\"input\": \"1\"}]")
    dlg._preview_paste()

    assert dlg.btn_add_all.isEnabled() is False
    assert dlg.lbl_paste_result.text() == "0 testcase hợp lệ, 1 dòng lỗi."


def test_st05_testcaseeditor_tc011_reorder_is_persisted(qapp, db_session, monkeypatch):
    """ST05_TestcaseEditor_TC011: kéo đổi thứ tự rồi Lưu -> mở lại giữ đúng thứ tự (biên)."""
    db, class_id = db_session
    _silence(monkeypatch)
    dlg = TestcaseEditDialog(db=db, class_id=class_id, question_number="Q1")
    expected = [tc["input_data"] for tc in dlg.testcases][::-1]

    dlg.testcases.reverse()
    dlg._refresh_list(select=0)
    assert [tc["input_data"] for tc in dlg.testcases] == expected

    assert dlg._save(keep_open=False) is True

    reopened = TestcaseEditDialog(db=db, class_id=class_id, question_number="Q1")
    assert [tc["input_data"] for tc in reopened.testcases] == expected


def test_st05_testcaseeditor_tc012_new_testcase_inherits_question_limits(qapp, db_session, monkeypatch):
    """ST05_TestcaseEditor_TC012: testcase mới kế thừa giới hạn phổ biến của câu (biên)."""
    db, class_id = db_session
    _silence(monkeypatch)
    dlg = TestcaseEditDialog(db=db, class_id=class_id, question_number="Q1")

    # Giới hạn phổ biến nhất của Q1 là 1000 ms / 128 MB (2/3 testcase).
    assert (dlg.q_time, dlg.q_mem) == (1000, 128)
    # Testcase đã có giữ nguyên giá trị đang lưu (testcase 3 là 1500 ms / 256 MB).
    assert dlg.testcases[2]["time_limit_ms"] == 1500
    assert dlg.testcases[2]["memory_limit_mb"] == 256

    dlg._add_testcase()
    assert dlg.testcases[-1]["time_limit_ms"] == 1000
    assert dlg.testcases[-1]["memory_limit_mb"] == 128

    _type(dlg.f_input, "10")
    _type(dlg.f_output, "20")
    assert dlg._save(keep_open=False) is True

    rows = {row["input_data"]: row for row in _q1_rows(db, class_id)}
    assert rows["10"]["time_limit_ms"] == 1000
    assert rows["7"]["time_limit_ms"] == 1500


def test_st05_testcaseeditor_tc013_line_stats_and_warnings():
    """ST05_TestcaseEditor_TC013: thống kê dòng/ký tự và cảnh báo không chặn lưu (biên)."""
    assert line_stats("") == (0, 0)
    assert line_stats("a") == (1, 1)
    assert line_stats("a\nb\n") == (2, 4)

    assert text_warnings("a") == ["Dữ liệu: thiếu ký tự xuống dòng ở cuối."]
    warnings = text_warnings("a  \n")
    assert len(warnings) == 1 and "khoảng trắng thừa" in warnings[0]
    assert text_warnings("a\n") == []

    marks = HIDDEN_TRAILING_SPACE * 2
    assert visualize_hidden_chars("a  \nb") == f"a{marks}{HIDDEN_LINE_END}\nb{HIDDEN_LINE_END}"


def test_st05_testcaseeditor_tc014_manager_cell_preview_and_tooltip():
    """ST05_TestcaseEditor_TC014: ô INPUT/OUTPUT hiển thị dòng đầu + "(+N dòng)"."""
    value = "Tong = 21\nMax = 11\nMin = -3"

    display = preview_multiline(value)

    assert display == "Tong = 21  (+2 dòng)"
    assert preview_multiline("") == "(trống)"
    assert preview_multiline("a\n") == "a"
    assert preview_multiline("x" * 80).endswith("...")


# ------------------------------------------------------------------------------
# Exception
# ------------------------------------------------------------------------------
def test_st05_testcaseeditor_tc015_blank_stdout_blocks_save(qapp, db_session, monkeypatch):
    """ST05_TestcaseEditor_TC015: stdout trống -> chặn Lưu, CSDL không đổi (ngoại lệ)."""
    db, class_id = db_session
    calls = _silence(monkeypatch)
    dlg = TestcaseEditDialog(db=db, class_id=class_id, question_number="Q1")

    dlg.list_tc.setCurrentRow(0)
    _type(dlg.f_output, "")
    _type(dlg.f_input, "1 2")

    assert dlg._save(keep_open=False) is False
    assert calls["warning"], "phải hiện cảnh báo dữ liệu không hợp lệ"
    assert "stdout" in calls["warning"][0][2]
    assert db.get_testcases_by_class(class_id)[0]["expected_output"] == "3"


def test_st05_testcaseeditor_tc016_discard_confirmation_blocks_close(qapp, monkeypatch):
    """ST05_TestcaseEditor_TC016: đóng khi có thay đổi chưa lưu -> phải xác nhận (ngoại lệ)."""
    dlg = TestcaseEditDialog()
    _type(dlg.f_input, "1")
    assert dlg._dirty is True

    calls = _silence(monkeypatch, question_answer=QMessageBox.StandardButton.No)
    assert dlg._confirm_discard() is False
    assert calls["question"], "phải hỏi xác nhận trước khi bỏ thay đổi"

    _silence(monkeypatch, question_answer=QMessageBox.StandardButton.Yes)
    assert dlg._confirm_discard() is True


def test_st05_testcaseeditor_tc017_action_buttons_match_requested_height(qapp):
    """ST05_TestcaseEditor_TC017: nút thao tác trong bảng không bị theme kéo cao gây cắt mép."""
    host = QWidget()
    host.setStyleSheet(LIGHT_THEME_QSS)
    host.resize(240, 80)
    host.show()

    edit_btn = make_row_button("Sửa", "#2F80ED", host, width=54, height=26)
    del_btn = make_row_button("Xóa", "#EF4444", host, width=54, height=26)
    cell = make_action_cell([edit_btn, del_btn], host)
    cell.setParent(host)
    host.layout() if host.layout() else None

    qapp.processEvents()

    assert edit_btn.height() == 26 and edit_btn.width() == 54
    assert del_btn.height() == 26
    assert cell.sizeHint().height() <= 34
