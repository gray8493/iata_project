"""
AITA Desktop Client - Problem Statement Document Reader
Extracts plain text from a problem-statement file so the AI testcase generator
can consume an uploaded document instead of typed text.

Supported formats:
- .docx (Word)      -> read with the standard library only (OOXML is a ZIP of XML)
- .txt/.md/.csv/... -> read with automatic encoding detection
- .pdf              -> best-effort via an optional library (pypdf / PyPDF2 / pdfminer)

No mandatory third-party dependency is introduced.
"""

import zipfile
from pathlib import Path
from typing import Union
from xml.etree import ElementTree as ET

_WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

TEXT_EXTENSIONS = {
    ".txt", ".text", ".md", ".markdown", ".csv", ".tsv", ".log",
    ".json", ".xml", ".html", ".htm",
}
DOCX_EXTENSIONS = {".docx"}
PDF_EXTENSIONS = {".pdf"}
SUPPORTED_EXTENSIONS = TEXT_EXTENSIONS | DOCX_EXTENSIONS | PDF_EXTENSIONS

# Backend GenerateTestcasesDto caps problem_description at 5000 characters.
MAX_PROBLEM_CHARS = 5000


class DocumentReadError(Exception):
    """Raised when a document cannot be read or its format is unsupported."""


def read_document_text(path: Union[str, Path]) -> str:
    """Returns the plain text content of a supported problem-statement file.

    Raises DocumentReadError for unsupported/corrupted files so callers can show
    a friendly message instead of an internal traceback.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise DocumentReadError(f"Không tìm thấy file: {file_path.name}")

    ext = file_path.suffix.lower()
    if ext in DOCX_EXTENSIONS:
        text = _read_docx(file_path)
    elif ext in PDF_EXTENSIONS:
        text = _read_pdf(file_path)
    elif ext in TEXT_EXTENSIONS:
        text = _read_text(file_path)
    else:
        shown = ext or "không xác định"
        raise DocumentReadError(
            f"Định dạng '{shown}' chưa được hỗ trợ. "
            "Vui lòng dùng file Word (.docx), PDF (.pdf) hoặc văn bản (.txt, .md)."
        )
    return text.strip()


def _read_docx(path: Path) -> str:
    try:
        with zipfile.ZipFile(path) as archive:
            if "word/document.xml" not in archive.namelist():
                raise DocumentReadError("File .docx không hợp lệ (thiếu word/document.xml).")
            xml_bytes = archive.read("word/document.xml")
    except DocumentReadError:
        raise
    except zipfile.BadZipFile:
        raise DocumentReadError("File .docx bị hỏng hoặc không phải định dạng Word hợp lệ.")
    except OSError as ex:
        raise DocumentReadError(f"Không đọc được file .docx: {ex}")

    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as ex:
        raise DocumentReadError(f"Không phân tích được nội dung .docx: {ex}")

    lines = []
    for paragraph in root.iter(f"{_WORD_NS}p"):
        chunks = [node.text or "" for node in paragraph.iter(f"{_WORD_NS}t")]
        lines.append("".join(chunks).strip())
    return "\n".join(lines)


def _read_pdf(path: Path) -> str:
    pdf_reader = None
    try:
        from pypdf import PdfReader as pdf_reader  # type: ignore
    except ImportError:
        try:
            from PyPDF2 import PdfReader as pdf_reader  # type: ignore
        except ImportError:
            pdf_reader = None

    if pdf_reader is not None:
        try:
            reader = pdf_reader(str(path))
            return "\n".join((page.extract_text() or "") for page in reader.pages)
        except Exception as ex:
            raise DocumentReadError(f"Không đọc được nội dung PDF: {ex}")

    try:
        from pdfminer.high_level import extract_text  # type: ignore
    except ImportError:
        raise DocumentReadError(
            "Chưa cài thư viện đọc PDF. Cài bằng lệnh: pip install pypdf, "
            "hoặc lưu đề bài dưới dạng .docx / .txt."
        )
    try:
        return extract_text(str(path))
    except Exception as ex:
        raise DocumentReadError(f"Không đọc được nội dung PDF: {ex}")


def _read_text(path: Path) -> str:
    data = path.read_bytes()
    if not data:
        return ""
    for encoding in ("utf-8-sig", "utf-8", "cp1258", "cp1252", "utf-16"):
        try:
            return data.decode(encoding)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return data.decode("utf-8", errors="ignore")
