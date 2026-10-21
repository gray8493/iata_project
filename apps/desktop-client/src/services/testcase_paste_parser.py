"""AITA - Bộ phân tích dữ liệu testcase dán hàng loạt (dùng cho tab "Dán Nhiều Testcase").

Hai định dạng được chấp nhận:

1. JSON: ``[{"input": "...", "output": "..."}, ...]`` (cũng nhận ``input_data`` /
   ``expected_output`` / ``stdin`` / ``stdout``, hoặc object bọc ``{"testcases": [...]}``).
2. Văn bản phân tách: mỗi testcase là một khối, các khối ngăn nhau bằng dòng ``---``;
   trong khối, phần trước dòng ``===`` là stdin và phần sau là stdout.

Mọi dòng lỗi đều được trả về kèm lý do để giao diện hiển thị - dữ liệu sai không
bao giờ được nạp im lặng.
"""

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

INPUT_KEYS = ("input", "input_data", "stdin", "dau_vao")
OUTPUT_KEYS = ("output", "expected_output", "stdout", "dau_ra")
BLOCK_SEPARATOR = "---"
FIELD_SEPARATOR = "==="


@dataclass
class ParsedTestcase:
    """Một testcase đọc được từ dữ liệu dán vào (có thể là dòng lỗi)."""

    index: int
    input_data: str = ""
    expected_output: str = ""
    error: str = ""
    source_line: int = 0

    @property
    def is_valid(self) -> bool:
        return not self.error


def _to_text(value: Any) -> Optional[str]:
    """Chuyển giá trị JSON thành chuỗi; trả None nếu không phải kiểu vô hướng."""
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        parts = []
        for item in value:
            text = _to_text(item)
            if text is None:
                return None
            parts.append(text)
        return "\n".join(parts)
    return None


def _pick(item: Dict[str, Any], keys: Sequence[str]) -> Optional[str]:
    for key in keys:
        if key in item:
            return _to_text(item[key])
    return None


def _trim_blank_edges(lines: List[str]) -> List[str]:
    start = 0
    end = len(lines)
    while start < end and not lines[start].strip():
        start += 1
    while end > start and not lines[end - 1].strip():
        end -= 1
    return lines[start:end]


def _parse_json(raw: str) -> List[ParsedTestcase]:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as ex:
        return [ParsedTestcase(
            index=1,
            error=f"JSON không hợp lệ: {ex.msg} (dòng {ex.lineno}, cột {ex.colno}).",
            source_line=ex.lineno,
        )]

    if isinstance(payload, dict):
        for key in ("testcases", "test_cases", "tests", "cases"):
            if isinstance(payload.get(key), list):
                payload = payload[key]
                break
        else:
            return [ParsedTestcase(
                index=1,
                error='JSON phải là mảng testcase hoặc object có khoá "testcases".',
            )]

    if not isinstance(payload, list):
        return [ParsedTestcase(index=1, error="JSON phải là một mảng các testcase.")]

    rows: List[ParsedTestcase] = []
    for position, item in enumerate(payload, start=1):
        if not isinstance(item, dict):
            rows.append(ParsedTestcase(
                index=position,
                error=f"Phần tử {position} không phải object {{\"input\": ..., \"output\": ...}}.",
            ))
            continue
        input_text = _pick(item, INPUT_KEYS)
        output_text = _pick(item, OUTPUT_KEYS)
        if input_text is None or output_text is None:
            rows.append(ParsedTestcase(
                index=position,
                error=f"Phần tử {position} thiếu khoá \"input\" hoặc \"output\" (hoặc sai kiểu dữ liệu).",
            ))
            continue
        if not output_text.strip():
            rows.append(ParsedTestcase(index=position, error=f"Phần tử {position} có output rỗng."))
            continue
        rows.append(ParsedTestcase(index=position, input_data=input_text, expected_output=output_text))
    return rows


def _parse_blocks(raw: str) -> List[ParsedTestcase]:
    lines = raw.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    blocks: List[List[str]] = [[]]
    for line in lines:
        if line.strip() == BLOCK_SEPARATOR:
            blocks.append([])
        else:
            blocks[-1].append(line)

    rows: List[ParsedTestcase] = []
    for block in blocks:
        trimmed = _trim_blank_edges(block)
        if not trimmed:
            continue
        separator_at = next(
            (i for i, line in enumerate(trimmed) if line.strip() == FIELD_SEPARATOR), -1
        )
        if separator_at < 0:
            rows.append(ParsedTestcase(
                index=len(rows) + 1,
                error=f"Khối thứ {len(rows) + 1} thiếu dòng \"{FIELD_SEPARATOR}\" ngăn cách input và output.",
            ))
            continue
        input_lines = _trim_blank_edges(trimmed[:separator_at])
        output_lines = _trim_blank_edges(trimmed[separator_at + 1:])
        input_text = "\n".join(input_lines)
        output_text = "\n".join(output_lines)
        if not output_text.strip():
            rows.append(ParsedTestcase(
                index=len(rows) + 1,
                error=f"Khối thứ {len(rows) + 1} không có output sau dòng \"{FIELD_SEPARATOR}\".",
            ))
            continue
        rows.append(ParsedTestcase(
            index=len(rows) + 1,
            input_data=input_text,
            expected_output=output_text,
        ))
    if not rows:
        rows.append(ParsedTestcase(index=1, error="Không tìm thấy testcase nào trong nội dung đã dán."))
    return rows


def parse_testcase_text(raw: str) -> List[ParsedTestcase]:
    """Phân tích dữ liệu dán vào thành danh sách testcase (kèm dòng lỗi)."""
    text = (raw or "").strip()
    if not text:
        return [ParsedTestcase(index=1, error="Chưa có dữ liệu để phân tích.")]
    if text[0] in "[{":
        return _parse_json(text)
    return _parse_blocks(text)
