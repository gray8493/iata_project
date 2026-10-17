"""Unit tests - DocumentReader (services.document_reader).

Feature: import a problem statement from a file (Word/PDF/text) so the AI
testcase generator can consume it instead of typed text.

Covers the required Normal / Boundary / Exception groups:
- Normal    : .docx (stdlib OOXML), UTF-8 text file.
- Boundary  : empty text file, single-paragraph docx, max problem length constant.
- Exception : corrupted .docx, unsupported extension (.doc), missing file.
"""
import zipfile

import pytest

from services.document_reader import (
    MAX_PROBLEM_CHARS,
    DocumentReadError,
    read_document_text,
)

_WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _write_min_docx(path, paragraphs):
    body = "".join(
        f'<w:p><w:r><w:t xml:space="preserve">{p}</w:t></w:r></w:p>' for p in paragraphs
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{_WORD_NS}"><w:body>{body}</w:body></w:document>'
    )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", xml)


# ------------------------------------------------------------------------------
# Normal
# ------------------------------------------------------------------------------
def test_ut01_documentreader_tc001_reads_utf8_text_file(tmp_path):
    """UT01_DocumentReader_TC001: đọc file đề bài văn bản UTF-8 (tiếng Việt)."""
    f = tmp_path / "de_bai.txt"
    f.write_text("Đếm số nguyên tố nhỏ hơn N.", encoding="utf-8")

    assert read_document_text(f) == "Đếm số nguyên tố nhỏ hơn N."


def test_ut01_documentreader_tc002_reads_docx_with_stdlib_only(tmp_path):
    """UT01_DocumentReader_TC002: đọc file Word .docx bằng thư viện chuẩn."""
    f = tmp_path / "de_bai.docx"
    _write_min_docx(f, ["Bài 1: Tính tổng a và b.", "Input: a b", "Output: a+b"])

    text = read_document_text(f)

    assert "Tính tổng a và b." in text
    assert text.count("\n") == 2


# ------------------------------------------------------------------------------
# Boundary
# ------------------------------------------------------------------------------
def test_ut01_documentreader_tc003_empty_text_file_returns_blank(tmp_path):
    """UT01_DocumentReader_TC003: file rỗng trả về chuỗi rỗng (biên)."""
    f = tmp_path / "rong.txt"
    f.write_text("", encoding="utf-8")

    assert read_document_text(f) == ""


def test_ut01_documentreader_tc004_limit_constant_matches_backend_dto():
    """UT01_DocumentReader_TC004: hằng giới hạn khớp @MaxLength(5000) của backend (biên)."""
    assert MAX_PROBLEM_CHARS == 5000


# ------------------------------------------------------------------------------
# Exception
# ------------------------------------------------------------------------------
def test_ut01_documentreader_tc005_corrupted_docx_raises(tmp_path):
    """UT01_DocumentReader_TC005: file .docx hỏng -> DocumentReadError."""
    f = tmp_path / "hong.docx"
    f.write_bytes(b"not a zip file")

    with pytest.raises(DocumentReadError):
        read_document_text(f)


def test_ut01_documentreader_tc006_unsupported_extension_raises(tmp_path):
    """UT01_DocumentReader_TC006: định dạng .doc cũ không hỗ trợ -> DocumentReadError."""
    f = tmp_path / "de_bai.doc"
    f.write_bytes(b"legacy binary")

    with pytest.raises(DocumentReadError):
        read_document_text(f)


def test_ut01_documentreader_tc007_missing_file_raises():
    """UT01_DocumentReader_TC007: file không tồn tại -> DocumentReadError."""
    with pytest.raises(DocumentReadError):
        read_document_text("khong_ton_tai_abc123.docx")
