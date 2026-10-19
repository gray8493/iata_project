"""Kiểm thử hiển thị tab "Chấm Chất Lượng (AI)" của hộp thoại chi tiết bài nộp.

Trọng tâm: khi AI lỗi/hết hạn ngạch (rubric PENDING) thì bảng tiêu chí KHÔNG được
hiển thị FAIL — tránh gây hiểu nhầm là sinh viên trượt cả 5 tiêu chí.
"""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PyQt6")

from PyQt6.QtWidgets import QApplication, QLabel, QPlainTextEdit, QTableWidget

from ui.dialogs.submission_detail_dialog import SubmissionDetailDialog


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def _make_dialog():
    """Dựng dialog tối thiểu: chỉ 3 widget mà `_render_quality` cần chạm tới."""
    dialog = SubmissionDetailDialog.__new__(SubmissionDetailDialog)
    dialog.lbl_quality_summary = QLabel()
    dialog.table_quality = QTableWidget(0, 3)
    dialog.txt_quality_feedback = QPlainTextEdit()
    return dialog


def _pending_quality() -> dict:
    return {
        "available": False,
        "pending": True,
        "score": 0.0,
        "max": 5.0,
        "sandbox_score": 2.9,
        "sandbox_max": 5.0,
        "criteria": {},
        "message": "Dịch vụ AI trả về dữ liệu không đúng định dạng.",
    }


def test_pending_rubric_shows_dash_instead_of_fail(qapp):
    dialog = _make_dialog()

    dialog._render_quality(_pending_quality(), {"calculated_score": 5.7})

    assert dialog.table_quality.rowCount() == 5
    assert dialog.table_quality.item(0, 1).text() == "—"
    assert dialog.table_quality.item(0, 2).text() == "Chưa chấm được bằng AI."
    assert "PENDING" in dialog.lbl_quality_summary.text()
    assert "5.7" in dialog.lbl_quality_summary.text()


def test_available_rubric_still_shows_pass_and_fail(qapp):
    dialog = _make_dialog()
    quality = {
        "available": True,
        "pending": False,
        "score": 3.0,
        "max": 5.0,
        "sandbox_score": 4.0,
        "sandbox_max": 5.0,
        "criteria": {
            "clean_code": {"label": "Clean Code (đặt tên biến/hàm)", "passed": True, "reason": "ổn"},
            "structure": {"label": "Structure (chia hàm/module hóa)", "passed": False, "reason": "gộp trong main"},
        },
        "overall_feedback": "Cần tách hàm.",
    }

    dialog._render_quality(quality, {"calculated_score": 7.0})

    assert dialog.table_quality.item(0, 1).text() == "PASS"
    assert dialog.table_quality.item(2, 1).text() == "FAIL"
    assert dialog.table_quality.item(2, 2).text() == "gộp trong main"
    assert dialog.txt_quality_feedback.toPlainText() == "Cần tách hàm."
    assert "Tổng: 7.0/10" in dialog.lbl_quality_summary.text()
