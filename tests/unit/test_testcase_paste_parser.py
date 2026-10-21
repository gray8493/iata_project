"""Unit tests - Paste parser (services.testcase_paste_parser).

Feature: tab "Dán Nhiều Testcase" nhận dữ liệu dán vào (JSON hoặc khối văn bản
ngăn bằng dòng `---`, trong khối dùng dòng `===` để tách input/output) và trả về
danh sách testcase kèm lý do lỗi cho từng dòng.

Covers the required Normal / Boundary / Exception groups:
- Normal    : JSON hợp lệ, khối văn bản hợp lệ.
- Boundary  : dòng trống đầu/cuối, JSON bọc trong khoá "testcases", tên khoá
              thay thế (input_data/expected_output), một khối duy nhất.
- Exception : JSON sai cú pháp, thiếu dòng `===`, output rỗng, dữ liệu trống.
"""
import pytest

from services.testcase_paste_parser import (
    FIELD_SEPARATOR,
    parse_testcase_text,
)


def _valid(rows):
    return [row for row in rows if row.is_valid]


# ------------------------------------------------------------------------------
# Normal
# ------------------------------------------------------------------------------
def test_ut02_testcasepasteparser_tc001_parses_json_array():
    """UT02_TestcasePasteParser_TC001: JSON mảng {"input","output"} -> 2 testcase."""
    rows = parse_testcase_text(
        '[{"input": "1 2", "output": "3"}, {"input": "4", "output": "8"}]'
    )

    assert len(rows) == 2
    assert all(row.is_valid for row in rows)
    assert rows[0].input_data == "1 2"
    assert rows[0].expected_output == "3"
    assert rows[1].index == 2


def test_ut02_testcasepasteparser_tc002_parses_delimited_blocks():
    """UT02_TestcasePasteParser_TC002: khối văn bản ---/=== tách đúng input/output."""
    text = "5\n4 -3 7\n===\nTong = 13\n---\n1\n===\nTong = 1\n"

    rows = parse_testcase_text(text)

    assert len(rows) == 2
    assert [row.input_data for row in rows] == ["5\n4 -3 7", "1"]
    assert [row.expected_output for row in rows] == ["Tong = 13", "Tong = 1"]


def test_ut02_testcasepasteparser_tc003_keeps_multi_line_output():
    """UT02_TestcasePasteParser_TC003: output nhiều dòng giữ nguyên thứ tự dòng."""
    text = "3\n1 2 3\n===\nTong = 6\nMax = 3\nMin = 1"

    rows = parse_testcase_text(text)

    assert rows[0].expected_output == "Tong = 6\nMax = 3\nMin = 1"


# ------------------------------------------------------------------------------
# Boundary
# ------------------------------------------------------------------------------
def test_ut02_testcasepasteparser_tc004_trims_blank_edges_of_block():
    """UT02_TestcasePasteParser_TC004: dòng trống đầu/cuối mỗi khối bị cắt (biên)."""
    text = "\n\n1 2\n\n===\n\n3\n\n---\n\n4\n===\n8\n\n"

    rows = parse_testcase_text(text)

    assert len(rows) == 2
    assert rows[0].input_data == "1 2"
    assert rows[0].expected_output == "3"
    assert rows[1].input_data == "4"
    assert rows[1].expected_output == "8"


def test_ut02_testcasepasteparser_tc005_accepts_wrapped_json_and_alias_keys():
    """UT02_TestcasePasteParser_TC005: JSON bọc "testcases" + khoá input_data/expected_output (biên)."""
    text = (
        '{"testcases": ['
        '{"input_data": "a", "expected_output": "b"},'
        '{"stdin": ["1", "2"], "stdout": "3"}]}'
    )

    rows = parse_testcase_text(text)

    assert [row.input_data for row in rows] == ["a", "1\n2"]
    assert [row.expected_output for row in rows] == ["b", "3"]


def test_ut02_testcasepasteparser_tc006_single_block_without_separator():
    """UT02_TestcasePasteParser_TC006: chỉ một testcase, không cần dòng `---` (biên)."""
    rows = parse_testcase_text("7\n===\n14")

    assert len(rows) == 1
    assert rows[0].input_data == "7"
    assert rows[0].expected_output == "14"


def test_ut02_testcasepasteparser_tc007_allows_empty_input():
    """UT02_TestcasePasteParser_TC007: input rỗng vẫn hợp lệ (bài không đọc stdin) (biên)."""
    rows = parse_testcase_text('[{"input": "", "output": "Hello"}]')

    assert rows[0].is_valid
    assert rows[0].input_data == ""


# ------------------------------------------------------------------------------
# Exception
# ------------------------------------------------------------------------------
def test_ut02_testcasepasteparser_tc008_invalid_json_reports_line():
    """UT02_TestcasePasteParser_TC008: JSON sai cú pháp -> 1 dòng lỗi kèm vị trí."""
    rows = parse_testcase_text('[{"input": "1", "output": }]')

    assert len(rows) == 1
    assert not rows[0].is_valid
    assert "JSON không hợp lệ" in rows[0].error


def test_ut02_testcasepasteparser_tc009_missing_field_separator_reports_error():
    """UT02_TestcasePasteParser_TC009: khối thiếu dòng `===` -> báo lỗi, không nạp."""
    rows = parse_testcase_text("1 2\n3")

    assert len(rows) == 1
    assert not rows[0].is_valid
    assert FIELD_SEPARATOR in rows[0].error


def test_ut02_testcasepasteparser_tc010_empty_output_reports_error():
    """UT02_TestcasePasteParser_TC010: output rỗng -> dòng lỗi, không nạp im lặng."""
    text = "1\n===\n2\n---\n3\n===\n"

    rows = parse_testcase_text(text)

    assert rows[0].is_valid
    assert not rows[1].is_valid
    assert "output" in rows[1].error


def test_ut02_testcasepasteparser_tc011_blank_input_reports_error():
    """UT02_TestcasePasteParser_TC011: dữ liệu dán trống -> báo lỗi rõ ràng."""
    rows = parse_testcase_text("   \n\n")

    assert len(rows) == 1
    assert not rows[0].is_valid
    assert "Chưa có dữ liệu" in rows[0].error


def test_ut02_testcasepasteparser_tc012_partial_json_keeps_valid_rows():
    """UT02_TestcasePasteParser_TC012: 1 phần tử lỗi không làm mất các phần tử hợp lệ."""
    rows = parse_testcase_text(
        '[{"input": "1", "output": "2"}, {"input": "3"}, {"input": "4", "output": "8"}]'
    )

    assert len(_valid(rows)) == 2
    assert not rows[1].is_valid
    assert "thiếu khoá" in rows[1].error
