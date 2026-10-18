"""
AITA Desktop Client - ExportService (Gradebook Export)
Implements UC-18 / AT02 / IT14: builds the standardized gradebook rows from local
grading data and renders them to a CSV file (`results.csv`), an Excel workbook
(.xlsx) or a printable report.

CSV gradebook columns (IT14, UTF-8 BOM):
`MSSV`, `File`, `Điểm số`, `Số testcase đạt`, `Trạng thái`,
`Thời gian chạy (ms)`, `Nhận xét từ AI`.
"""

import csv
from pathlib import Path
from typing import Any, Dict, List

GRADE_COLUMNS = (
    "MSSV",
    "Tên File",
    "Điểm số",
    "Số test đạt",
    "Trạng thái",
    "Thời gian chạy (ms)",
    "Nhận xét AI"
)

CSV_COLUMNS = (
    "MSSV",
    "File",
    "Điểm số",
    "Số testcase đạt",
    "Trạng thái",
    "Thời gian chạy (ms)",
    "Nhận xét từ AI"
)

FAILED_VERDICTS = ("WA", "TLE", "MLE", "CE", "RE")


class ExportService:
    """Builds gradebook rows and exports them to Excel / printable report."""

    def build_grade_rows(
        self,
        submissions: List[Dict[str, Any]],
        testcase_count: int
    ) -> List[Dict[str, Any]]:
        """Normalizes graded submissions into the 7 standard gradebook fields."""
        total = int(testcase_count or 0)
        rows: List[Dict[str, Any]] = []

        for submission in submissions:
            score = submission.get("manual_override_score")
            if score is None:
                score = submission.get("calculated_score") or 0.0
            score = float(score)

            verdict = submission.get("final_verdict") or "PENDING"
            passed = int(round((score / 10.0) * total)) if total else 0
            passed = max(0, min(passed, total))

            rows.append({
                "mssv": submission.get("student_mssv", ""),
                "file_name": Path(submission.get("source_file_path") or "").name,
                "score": score,
                "passed": passed,
                "passed_label": f"{passed}/{total}",
                "verdict": verdict,
                "runtime_ms": float(submission.get("execution_time_ms") or 0.0),
                "comment": submission.get("ai_feedback") or ""
            })

        return rows

    def export_csv(self, rows: List[Dict[str, Any]], file_path: str) -> str:
        """
        Writes the 7-column `results.csv` gradebook with UTF-8 BOM (IT14) so that
        Vietnamese text renders correctly in Microsoft Excel.
        """
        with open(file_path, "w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(list(CSV_COLUMNS))
            for row in rows:
                writer.writerow([
                    row["mssv"],
                    row["file_name"],
                    round(row["score"], 1),
                    row["passed_label"],
                    row["verdict"],
                    f"{row['runtime_ms']:.0f}ms",
                    row["comment"]
                ])
        return str(file_path)

    def export_excel(
        self,
        rows: List[Dict[str, Any]],
        file_path: str,
        class_name: str = "",
        course_code: str = ""
    ) -> str:
        """
        Writes a formatted .xlsx gradebook with conditional coloring and a score chart.
        Propagates PermissionError when the target file is locked (AT02_TC002).
        """
        import openpyxl
        from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
        from openpyxl.utils import get_column_letter

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "BangDiem"

        header_fill = PatternFill(start_color="2F80ED", end_color="2F80ED", fill_type="solid")
        header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
        body_font = Font(name="Arial", size=11)
        green_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
        red_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
        thin_border = Border(
            left=Side(style="thin", color="CBD5E1"),
            right=Side(style="thin", color="CBD5E1"),
            top=Side(style="thin", color="CBD5E1"),
            bottom=Side(style="thin", color="CBD5E1")
        )

        sheet.append(list(GRADE_COLUMNS))
        for col_idx in range(1, len(GRADE_COLUMNS) + 1):
            cell = sheet.cell(row=1, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border
        sheet.freeze_panes = "A2"

        for row_idx, row in enumerate(rows, start=2):
            score = row["score"]
            verdict = row["verdict"]
            values = [
                row["mssv"],
                row["file_name"],
                round(score, 1),
                row["passed_label"],
                verdict,
                round(row["runtime_ms"], 0),
                row["comment"]
            ]
            sheet.append(values)

            fill = None
            if verdict == "AC" and score >= 10.0:
                fill = green_fill
            elif score <= 0.0 or verdict in FAILED_VERDICTS:
                fill = red_fill

            for col_idx in range(1, len(values) + 1):
                cell = sheet.cell(row=row_idx, column=col_idx)
                cell.border = thin_border
                cell.font = body_font
                if fill is not None:
                    cell.fill = fill
                if col_idx in (1, 3, 4, 5, 6):
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                else:
                    cell.alignment = Alignment(horizontal="left", vertical="center")

        for col in sheet.columns:
            letter = get_column_letter(col[0].column)
            max_len = max(len(str(cell.value or "")) for cell in col)
            sheet.column_dimensions[letter].width = max(max_len + 4, 12)

        self._append_score_chart(workbook, rows)

        workbook.save(file_path)
        return str(file_path)

    def build_report_html(
        self,
        rows: List[Dict[str, Any]],
        class_name: str = "",
        course_code: str = "",
        language: str = ""
    ) -> str:
        """Builds the printable HTML report (rendered to PDF by the UI layer)."""
        from datetime import datetime

        body_rows = ""
        for idx, row in enumerate(rows, start=1):
            verdict = row["verdict"]
            color = "#16A34A" if verdict == "AC" else ("#DC2626" if verdict in FAILED_VERDICTS else "#2563EB")
            comment = (row["comment"] or "").replace("<", "&lt;").replace(">", "&gt;")
            body_rows += f"""
                <tr>
                    <td align="center">{idx}</td>
                    <td>{row['mssv']}</td>
                    <td>{row['file_name']}</td>
                    <td align="center" style="font-weight: bold;">{row['score']:.1f}</td>
                    <td align="center">{row['passed_label']}</td>
                    <td align="center" style="color: {color}; font-weight: bold;">{verdict}</td>
                    <td align="center">{row['runtime_ms']:.0f} ms</td>
                    <td>{comment}</td>
                </tr>
            """

        generated_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; font-size: 11px; color: #1E293B; }}
                h2 {{ color: #2F80ED; text-align: center; margin-bottom: 4px; }}
                .meta {{ text-align: center; font-size: 12px; color: #64748B; margin-bottom: 18px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                th {{ background-color: #2F80ED; color: white; padding: 6px; font-size: 11px; text-align: center; }}
                td {{ border: 1px solid #CBD5E1; padding: 5px; font-size: 10px; }}
                tr:nth-child(even) {{ background-color: #F8FAFC; }}
            </style>
        </head>
        <body>
            <h2>BẢNG ĐIỂM THI THỰC HÀNH - AITA</h2>
            <div class="meta">Lớp: {class_name} | Mã môn: {course_code} | Ngôn ngữ: {language} | Xuất lúc: {generated_at}</div>
            <table>
                <thead>
                    <tr>
                        <th>STT</th>
                        <th>MSSV</th>
                        <th>Tên File</th>
                        <th>Điểm số</th>
                        <th>Số test đạt</th>
                        <th>Trạng thái</th>
                        <th>Thời gian chạy (ms)</th>
                        <th>Nhận xét AI</th>
                    </tr>
                </thead>
                <tbody>{body_rows}</tbody>
            </table>
        </body>
        </html>
        """

    @staticmethod
    def _append_score_chart(workbook, rows: List[Dict[str, Any]]) -> None:
        """Adds a score-distribution bar chart on a separate worksheet."""
        try:
            from openpyxl.chart import BarChart, Reference
        except Exception:
            return

        stats = workbook.create_sheet("ThongKe")
        stats.append(["MSSV", "Điểm số"])
        for row in rows:
            stats.append([row["mssv"], round(row["score"], 1)])

        if not rows:
            return

        chart = BarChart()
        chart.title = "Phân phối điểm số"
        chart.x_axis.title = "Sinh viên"
        chart.y_axis.title = "Điểm (thang 10)"
        data = Reference(stats, min_col=2, min_row=1, max_row=len(rows) + 1)
        categories = Reference(stats, min_col=1, min_row=2, max_row=len(rows) + 1)
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(categories)
        chart.height = 8
        chart.width = 22
        stats.add_chart(chart, "D2")
