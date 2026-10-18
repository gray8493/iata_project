"""System tests - AI Testcase Import dialog (ui.dialogs.testcase_dialog.AiTestcaseDialog).

Feature: the "Nhập Từ File Đề Bài" button loads a problem statement from a
file into the prompt box that feeds the AI testcase generator.

Runs the real PyQt6 dialog (offscreen QApplication) with the file picker and
message boxes stubbed, so the whole import path is exercised without a display
and without network.
"""
import os
import zipfile

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PyQt6")

from PyQt6.QtWidgets import QFileDialog, QMessageBox

from ui.dialogs.testcase_dialog import AiTestcaseDialog

_WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _write_docx(path, paragraphs):
    body = "".join(
        f'<w:p><w:r><w:t xml:space="preserve">{p}</w:t></w:r></w:p>' for p in paragraphs
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{_WORD_NS}"><w:body>{body}</w:body></w:document>'
    )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", xml)


def _pick_file(monkeypatch, path):
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: (str(path), ""))


def _pick_no_file(monkeypatch):
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: ("", ""))


# ------------------------------------------------------------------------------
# Normal
# ------------------------------------------------------------------------------
def test_st01_testcaseimport_tc001_imports_docx_into_prompt(qapp, tmp_path, monkeypatch):
    """ST01_TestcaseImport_TC001: nút nạp file đổ nội dung .docx vào ô đề bài."""
    f = tmp_path / "de_bai.docx"
    _write_docx(f, ["Bài 1: Tính tổng a và b.", "Input: a b", "Output: a+b"])
    _pick_file(monkeypatch, f)

    dlg = AiTestcaseDialog()
    dlg._import_problem_document()

    assert "Tính tổng a và b." in dlg.txt_prompt.toPlainText()
    assert f.name in dlg.lbl_doc_name.text()


# ------------------------------------------------------------------------------
# Boundary
# ------------------------------------------------------------------------------
def test_st01_testcaseimport_tc002_appends_when_prompt_not_empty(qapp, tmp_path, monkeypatch):
    """ST01_TestcaseImport_TC002: chọn 'No' -> nối thêm vào nội dung hiện có (biên)."""
    f = tmp_path / "de_bai.txt"
    f.write_text("Đề mới bổ sung.", encoding="utf-8")
    _pick_file(monkeypatch, f)
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.No)

    dlg = AiTestcaseDialog()
    dlg.txt_prompt.setPlainText("Đề cũ đang có.")
    dlg._import_problem_document()

    text = dlg.txt_prompt.toPlainText()
    assert text.startswith("Đề cũ đang có.")
    assert "Đề mới bổ sung." in text


def test_st01_testcaseimport_tc003_truncates_to_backend_limit(qapp, tmp_path, monkeypatch):
    """ST01_TestcaseImport_TC003: đề bài > 5000 ký tự bị cắt còn 5000 và cảnh báo (biên)."""
    f = tmp_path / "de_dai.txt"
    f.write_text("A" * 6000, encoding="utf-8")
    _pick_file(monkeypatch, f)
    info_calls = []
    monkeypatch.setattr(
        QMessageBox, "information",
        lambda *a, **k: info_calls.append(a) or QMessageBox.StandardButton.Ok,
    )

    dlg = AiTestcaseDialog()
    dlg._import_problem_document()

    assert len(dlg.txt_prompt.toPlainText()) == 5000
    assert info_calls  # "Đề Bài Quá Dài" đã được thông báo


# ------------------------------------------------------------------------------
# Exception
# ------------------------------------------------------------------------------
def test_st01_testcaseimport_tc004_unsupported_file_shows_warning(qapp, tmp_path, monkeypatch):
    """ST01_TestcaseImport_TC004: file .doc không hỗ trợ -> cảnh báo, ô đề bài giữ nguyên."""
    f = tmp_path / "de_bai.doc"
    f.write_bytes(b"legacy binary")
    _pick_file(monkeypatch, f)
    warns = []
    monkeypatch.setattr(
        QMessageBox, "warning",
        lambda *a, **k: warns.append(a) or QMessageBox.StandardButton.Ok,
    )

    dlg = AiTestcaseDialog()
    dlg._import_problem_document()

    assert warns
    assert dlg.txt_prompt.toPlainText() == ""


def test_st01_testcaseimport_tc005_cancel_file_dialog_is_noop(qapp, monkeypatch):
    """ST01_TestcaseImport_TC005: hủy hộp chọn file -> không thay đổi gì."""
    _pick_no_file(monkeypatch)
    dlg = AiTestcaseDialog()
    dlg._import_problem_document()

    assert dlg.txt_prompt.toPlainText() == ""
    assert dlg.lbl_doc_name.text() == ""
