"""Gradebook Export (services.export_service).

Covers IT14 / AT02_SubmissionIngestion_TC002 boundary: the 7-column
`results.csv` with UTF-8 BOM, score/passed normalization with manual-score
override, Excel conditional coloring, chart worksheet and the
PermissionError propagation when the destination file is locked.
"""

import csv

import pytest

from services.export_service import CSV_COLUMNS, ExportService, GRADE_COLUMNS

SAMPLE_SUBMISSIONS = [
    {
        "student_mssv": "SE180001",
        "source_file_path": "D:/Sub/SE180001_Q1.c",
        "calculated_score": 10.0,
        "final_verdict": "AC",
        "execution_time_ms": 35.4,
        "ai_feedback": "Tốt.",
    },
    {
        "student_mssv": "SE180002",
        "source_file_path": "D:/Sub/SE180002_Q1.c",
        "calculated_score": 5.0,
        "manual_override_score": 7.5,
        "final_verdict": "WA",
        "execution_time_ms": 42.9,
        "ai_feedback": "Đã sửa for(i=1; i<=n; i++).",
    },
    {
        "student_mssv": "SE180003",
        "source_file_path": "D:/Sub/SE180003_Q1.c",
        "final_verdict": "CE",
        "execution_time_ms": None,
        "ai_feedback": None,
    },
]


def test_build_grade_rows_normalizes_the_seven_fields():
    rows = ExportService().build_grade_rows(SAMPLE_SUBMISSIONS, testcase_count=10)
    assert len(rows) == 3

    first = rows[0]
    assert first["mssv"] == "SE180001"
    assert first["file_name"] == "SE180001_Q1.c"  # only basename survives
    assert first["score"] == 10.0
    assert first["passed_label"] == "10/10"
    assert first["verdict"] == "AC"
    assert first["runtime_ms"] == 35.4
    assert first["comment"] == "Tốt."


def test_build_grade_rows_manual_override_wins_over_calculated():
    rows = ExportService().build_grade_rows(SAMPLE_SUBMISSIONS, testcase_count=10)
    overridden = rows[1]
    assert overridden["score"] == 7.5
    assert overridden["passed_label"] == "8/10"  # round(7.5/10*10) clamps to int


def test_build_grade_rows_missing_score_and_count_fall_back_to_zero():
    rows = ExportService().build_grade_rows(SAMPLE_SUBMISSIONS, testcase_count=0)
    row = rows[2]
    assert row["score"] == 0.0
    assert row["passed"] == 0 and row["passed_label"] == "0/0"
    assert row["verdict"] == "CE"


def test_export_csv_writes_seven_columns_with_utf8_bom(tmp_path):
    rows = ExportService().build_grade_rows(SAMPLE_SUBMISSIONS, testcase_count=10)
    out = tmp_path / "results.csv"

    ExportService().export_csv(rows, str(out))

    raw = out.read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf")  # UTF-8 BOM so Excel renders Vietnamese

    with open(out, "r", encoding="utf-8-sig", newline="") as handle:
        table = list(csv.reader(handle))

    assert table[0] == list(CSV_COLUMNS)
    assert len(table) == 4  # header + 3 students
    assert table[1] == ["SE180001", "SE180001_Q1.c", "10.0", "10/10", "AC", "35ms", "Tốt."]
    assert table[2] == ["SE180002", "SE180002_Q1.c", "7.5", "8/10", "WA", "43ms",
                        "Đã sửa for(i=1; i<=n; i++)."]
    assert table[3][5] == "0ms"


def test_export_csv_creates_header_only_file_for_empty_gradebook(tmp_path):
    out = tmp_path / "empty.csv"
    ExportService().export_csv([], str(out))
    with open(out, "r", encoding="utf-8-sig", newline="") as handle:
        table = list(csv.reader(handle))
    assert table == [list(CSV_COLUMNS)]


def test_export_excel_writes_rows_colors_and_chart_sheet(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")

    rows = ExportService().build_grade_rows(SAMPLE_SUBMISSIONS, testcase_count=10)
    out = tmp_path / "BangDiem.xlsx"

    ExportService().export_excel(rows, str(out), class_name="SE1801", course_code="PRF192")

    workbook = openpyxl.load_workbook(out)
    sheet = workbook["BangDiem"]
    assert [c.value for c in sheet[1]] == list(GRADE_COLUMNS)

    second_row = [c.value for c in sheet[2]]
    assert second_row[0] == "SE180001" and second_row[3] == "10/10" and second_row[4] == "AC"

    # AC + 10.0 -> green fill; WA (failed verdict) and CE/0-score -> red fill
    assert sheet.cell(row=2, column=1).fill.start_color.rgb == "00C6EFCE"
    assert sheet.cell(row=2, column=1).fill.fill_type == "solid"
    assert sheet.cell(row=3, column=1).fill.start_color.rgb == "00FFC7CE"
    assert sheet.cell(row=4, column=1).fill.start_color.rgb == "00FFC7CE"

    assert "ThongKe" in workbook.sheetnames  # score distribution chart sheet
    stats = workbook["ThongKe"]
    assert stats.cell(row=1, column=1).value == "MSSV"
    assert stats.cell(row=2, column=2).value == 10.0


def test_export_excel_propagates_permission_error_when_file_locked(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(
        "openpyxl.Workbook.save",
        lambda self, path: (_ for _ in ()).throw(PermissionError(13, "other app holds the file")),
    )
    rows = ExportService().build_grade_rows(SAMPLE_SUBMISSIONS, testcase_count=10)
    with pytest.raises(PermissionError):
        ExportService().export_excel(rows, str(tmp_path / "locked.xlsx"))


def test_build_report_html_flags_verdict_colors():
    rows = ExportService().build_grade_rows(SAMPLE_SUBMISSIONS, testcase_count=10)
    html = ExportService().build_report_html(
        rows, class_name="SE1801", course_code="PRF192", language="C"
    )
    assert "BẢNG ĐIỂM" in html and "SE1801" in html and "PRF192" in html
    assert "#16A34A" in html  # AC green
    assert "#DC2626" in html  # CE red


def test_build_report_html_escapes_html_in_ai_comment():
    rows = ExportService().build_grade_rows(
        [{**SAMPLE_SUBMISSIONS[0], "ai_feedback": "<script>alert('x')</script>"}],
        testcase_count=1,
    )
    html = ExportService().build_report_html(rows)
    assert "<script" not in html
    assert "&lt;script&gt;alert('x')&lt;/script&gt;" in html
