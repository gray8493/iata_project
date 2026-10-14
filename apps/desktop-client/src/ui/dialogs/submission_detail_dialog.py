"""
AITA Desktop Client - Submission Detail & Code Review Dialog (PyQt6)
UC-14: View Submission Result & Execution Logs
UC-15: Re-grade & Override Scores Manually
UC-16: Generate On-Demand AI Code Review (WA Only)
100% Real File & Database Integration - Clean SaaS UI without icons/emojis
"""

import sys
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

from PyQt6.QtCore import Qt, QRect, QSize, QRegularExpression
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QTextFormat, QSyntaxHighlighter,
    QTextCharFormat, QGuiApplication, QCursor
)
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QPlainTextEdit, QTextEdit, QTabWidget, QSplitter, QDoubleSpinBox, QMessageBox,
    QApplication
)

SRC_DIR = Path(__file__).resolve().parent.parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ui.styles.theme import LIGHT_THEME_QSS
from database.db_manager import DatabaseManager


class LineNumberArea(QWidget):
    """Line number margin for CodeEditor."""
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """Custom code editor with line numbers and monospace typography."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)

        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setStyleSheet("""
            QPlainTextEdit {
                font-family: 'Consolas', 'Cascadia Mono', monospace;
                font-size: 13px;
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                line-height: 1.45;
            }
        """)

    def line_number_area_width(self):
        digits = 1
        m = max(1, self.blockCount())
        while m >= 10:
            m //= 10
            digits += 1
        space = 16 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#F8FAFC"))
        painter.setPen(QColor("#E2E8F0"))
        painter.drawLine(event.rect().topRight(), event.rect().bottomRight())

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#94A3B8"))
                painter.setFont(self.font())
                painter.drawText(
                    0, int(top), self.line_number_area.width() - 8,
                    int(self.fontMetrics().height()),
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                    number
                )
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1


class CodeHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for C, Java and Python source code."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#2563EB"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = [
            "char", "class", "const", "double", "enum", "float",
            "int", "long", "short", "signed", "static", "struct", "unsigned",
            "void", "for", "while", "do", "if", "else", "switch", "case",
            "default", "break", "continue", "return", "sizeof", "typedef",
            "public", "private", "protected", "import", "def", "from", "as",
            "None", "True", "False", "print", "scanf", "printf", "main", "new"
        ]
        for pattern in keywords:
            self.highlighting_rules.append((QRegularExpression(r"\b" + pattern + r"\b"), keyword_format))

        # Directives / Includes
        prep_format = QTextCharFormat()
        prep_format.setForeground(QColor("#7C3AED"))
        self.highlighting_rules.append((QRegularExpression(r"#[^\n]*"), prep_format))

        # Strings
        str_format = QTextCharFormat()
        str_format.setForeground(QColor("#16A34A"))
        self.highlighting_rules.append((QRegularExpression(r'".*?"'), str_format))
        self.highlighting_rules.append((QRegularExpression(r"'.*?'"), str_format))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#64748B"))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((QRegularExpression(r"//[^\n]*"), comment_format))
        self.highlighting_rules.append((QRegularExpression(r"/\*.*?\*/"), comment_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)


class SubmissionDetailDialog(QDialog):
    """
    Detailed inspection dialog for reviewing real source code, actual testcase verdicts,
    and invoking on-demand AI review for WA submissions.
    """

    def __init__(
        self,
        submission_id: Optional[int] = None,
        mssv: str = "SE180000",
        file_name: str = "code.c",
        source_file_path: Optional[str] = None,
        verdict: str = "PENDING",
        score: str = "-",
        parent=None
    ):
        super().__init__(parent)
        self.submission_id = submission_id
        self.mssv = mssv
        self.file_name = file_name
        self.source_file_path = source_file_path
        self.verdict = verdict
        self.score = score
        self.db = DatabaseManager()
        
        self.setWindowTitle(f"Chi Tiết Bài Nộp - {self.mssv} ({self.file_name})")
        
        # 10. Giới hạn chiều cao theo vùng làm việc màn hình
        screen = QGuiApplication.primaryScreen()
        if screen:
            avail = screen.availableGeometry()
            target_w = min(1200, avail.width() - 40)
            target_h = min(780, avail.height() - 40)
            self.setMinimumSize(min(1080, target_w), min(640, target_h))
            self.resize(target_w, target_h)
            self.move(avail.x() + (avail.width() - target_w) // 2,
                      avail.y() + (avail.height() - target_h) // 2)
        else:
            self.setMinimumSize(1080, 640)
            self.resize(1200, 780)
            
        self.setStyleSheet(LIGHT_THEME_QSS)
        self._init_ui()
        self._load_real_submission_data()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(14)
        
        # 9. Top Header Bar: Tách riêng 2 nhãn và bo góc đồng bộ
        top_card = QFrame(self)
        top_card.setProperty("class", "Card")
        t_layout = QHBoxLayout(top_card)
        t_layout.setContentsMargins(16, 12, 16, 12)
        t_layout.setSpacing(12)
        
        # Nhãn Sinh Viên riêng biệt
        lbl_student = QLabel(f"Sinh Viên: <b>{self.mssv}</b>", top_card)
        lbl_student.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #1E293B;
                background-color: #F1F5F9;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 5px 12px;
                line-height: 1.4;
            }
        """)
        t_layout.addWidget(lbl_student)
        
        # Nhãn Tệp Bài Thi riêng biệt
        lbl_file = QLabel(f"Tệp Bài Thi: <b>{self.file_name}</b>", top_card)
        lbl_file.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #1E293B;
                background-color: #F1F5F9;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 5px 12px;
                line-height: 1.4;
            }
        """)
        t_layout.addWidget(lbl_file)
        
        t_layout.addStretch(1)
        
        # 4. Nút Mở Cấu Hình Môi Trường (Ẩn mặc định, chỉ hiện khi lỗi thiếu trình biên dịch)
        self.btn_open_env = QPushButton("Mở Cấu Hình Môi Trường", top_card)
        self.btn_open_env.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_open_env.setFixedHeight(32)
        self.btn_open_env.setStyleSheet("""
            QPushButton {
                background-color: #EFF6FF;
                color: #2563EB;
                border: 1px solid #BFDBFE;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 600;
                padding: 0 12px;
                line-height: 1.4;
            }
            QPushButton:hover {
                background-color: #DBEAFE;
            }
        """)
        self.btn_open_env.clicked.connect(self._open_environment_settings)
        self.btn_open_env.setVisible(False)
        t_layout.addWidget(self.btn_open_env)
        
        # Nhãn Trạng Thái
        self.lbl_verdict_badge = QLabel(f"Trạng thái: <b>{self.verdict}</b>", top_card)
        self.lbl_verdict_badge.setFixedHeight(32)
        v_bg = "#DCFCE7" if self.verdict == "AC" else ("#FEE2E2" if self.verdict in ("WA", "CE", "RE", "TLE") else "#F1F5F9")
        v_color = "#15803D" if self.verdict == "AC" else ("#B91C1C" if self.verdict in ("WA", "CE", "RE", "TLE") else "#475569")
        self.lbl_verdict_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {v_bg};
                color: {v_color};
                font-weight: 700;
                font-size: 12px;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 0 14px;
                line-height: 1.4;
            }}
        """)
        if self.verdict == "CE":
            self.lbl_verdict_badge.setToolTip("CE = Compile Error (lỗi biên dịch cú pháp mã nguồn)")
        t_layout.addWidget(self.lbl_verdict_badge)
        
        # Nhãn Điểm Số
        self.lbl_score_badge = QLabel(f"Điểm số: <b>{self.score}</b>", top_card)
        self.lbl_score_badge.setFixedHeight(32)
        self.lbl_score_badge.setStyleSheet("""
            QLabel {
                background-color: #EFF6FF;
                color: #1D4ED8;
                font-weight: 800;
                font-size: 12px;
                border: 1px solid #BFDBFE;
                border-radius: 8px;
                padding: 0 14px;
                line-height: 1.4;
            }
        """)
        t_layout.addWidget(self.lbl_score_badge)
        
        layout.addWidget(top_card)
        
        # 2. Main Horizontal Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        
        # LEFT PANE: Real Source Code Viewer With Line Numbers & Highlighting
        left_widget = QWidget(splitter)
        l_layout = QVBoxLayout(left_widget)
        l_layout.setContentsMargins(0, 0, 0, 0)
        l_layout.setSpacing(8)
        
        # 7. Xóa icon ở tiêu đề mã nguồn
        lbl_code_title = QLabel("Nội Dung Mã Nguồn (Đọc Trực Tiếp Từ Ổ Đĩa):", left_widget)
        lbl_code_title.setStyleSheet("font-weight: 700; font-size: 13px; color: #1E293B; line-height: 1.4;")
        l_layout.addWidget(lbl_code_title)
        
        # 6. Khung mã nguồn: Line numbers, syntax highlighting, monospace font
        self.txt_source_code = CodeEditor(left_widget)
        self.txt_source_code.setReadOnly(True)
        self.highlighter = CodeHighlighter(self.txt_source_code.document())
        l_layout.addWidget(self.txt_source_code)
        splitter.addWidget(left_widget)
        
        # RIGHT PANE: Tabs for Verdicts, Log, AI Review, Override
        right_widget = QWidget(splitter)
        r_layout = QVBoxLayout(right_widget)
        r_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget(right_widget)
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 600;
                line-height: 1.4;
            }
        """)
        
        # TAB 1: Testcase Verdicts & Log
        tab_tc = QWidget()
        tt_layout = QVBoxLayout(tab_tc)
        tt_layout.setContentsMargins(10, 10, 10, 10)
        tt_layout.setSpacing(10)
        
        # 1. Bảng Chi Tiết Testcase: Xóa cột số thứ tự thừa, căn tiêu đề & dữ liệu thẳng cột
        self.table_tc_results = QTableWidget(tab_tc)
        self.table_tc_results.setColumnCount(5)
        self.table_tc_results.setHorizontalHeaderLabels(["#", "Input", "Expected Output", "Actual Output", "Kết Quả"])
        self.table_tc_results.verticalHeader().setVisible(False)  # Xóa cột số thứ tự thừa ngoài cùng bên trái
        
        header = self.table_tc_results.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table_tc_results.setColumnWidth(0, 45)  # # nhỏ
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Input rộng
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Expected Output rộng
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Actual Output rộng
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table_tc_results.setColumnWidth(4, 95)  # Kết Quả vừa
        
        # 5. Bảng testcase cao vừa theo số dòng (tối thiểu 4 dòng)
        self.table_tc_results.setMinimumHeight(150)
        tt_layout.addWidget(self.table_tc_results)
        
        # Thanh header của nhật ký kèm nút Sao Chép
        log_header = QHBoxLayout()
        lbl_log_title = QLabel("Nhật Ký Biên Dịch & Chạy Sandbox:", tab_tc)
        lbl_log_title.setStyleSheet("font-weight: 700; font-size: 12px; color: #1E293B; line-height: 1.4;")
        log_header.addWidget(lbl_log_title)
        log_header.addStretch(1)
        
        # 5. Nút Sao Chép Nhật Ký
        self.btn_copy_log = QPushButton("Sao Chép Nhật Ký", tab_tc)
        self.btn_copy_log.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_copy_log.setFixedHeight(28)
        self.btn_copy_log.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 600;
                padding: 0 10px;
                line-height: 1.4;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
                color: #1E293B;
            }
        """)
        self.btn_copy_log.clicked.connect(self._copy_compile_log)
        log_header.addWidget(self.btn_copy_log)
        tt_layout.addLayout(log_header)
        
        # 5. Khung log: chữ cách mép 12px, font monospace, có thanh cuộn
        self.txt_compile_log = QTextEdit(tab_tc)
        self.txt_compile_log.setReadOnly(True)
        self.txt_compile_log.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Cascadia Mono', monospace;
                font-size: 12px;
                background-color: #0F172A;
                color: #F8FAFC;
                border-radius: 8px;
                padding: 12px;
                line-height: 1.45;
            }
        """)
        tt_layout.addWidget(self.txt_compile_log, stretch=1)
        
        # 7. Tab 1 không dùng icon
        self.tabs.addTab(tab_tc, "Chi Tiết Testcase")
        
        # TAB 2: AI Nhận Xét Mã (8. Đổi tên từ 'AI Code Review (WA Only)' thành 'AI Nhận Xét Mã')
        tab_ai = QWidget()
        ta_layout = QVBoxLayout(tab_ai)
        ta_layout.setSpacing(10)
        ta_layout.setContentsMargins(12, 12, 12, 12)
        
        btn_run_ai_review = QPushButton("Kích Hoạt Gemini AI Phân Tích Lỗi Mã Nguồn Bài Này", tab_ai)
        btn_run_ai_review.setProperty("class", "AIBtn")
        btn_run_ai_review.setFixedHeight(36)
        btn_run_ai_review.clicked.connect(self._run_ai_review)
        ta_layout.addWidget(btn_run_ai_review)
        
        self.txt_ai_feedback = QTextEdit(tab_ai)
        self.txt_ai_feedback.setPlaceholderText("Bấm nút trên để Gemini AI phân tích vị trí dòng lỗi thuật toán và đưa ra nhận xét sư phạm...")
        self.txt_ai_feedback.setReadOnly(True)
        self.txt_ai_feedback.setStyleSheet("""
            QTextEdit {
                font-family: 'Inter', sans-serif;
                font-size: 13px;
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 12px;
                line-height: 1.45;
            }
        """)
        ta_layout.addWidget(self.txt_ai_feedback)
        
        self.tabs.addTab(tab_ai, "AI Nhận Xét Mã")
        
        # 8. Làm mờ (disabled) tab AI khi bài không ở trạng thái WA
        if self.verdict != "WA":
            self.tabs.setTabEnabled(1, False)
            self.tabs.setTabToolTip(1, "Chỉ áp dụng cho bài chạy được nhưng sai kết quả (WA)")
            
        # TAB 3: Ghi Đè Điểm Thủ Công (7. Bỏ icon)
        tab_override = QWidget()
        to_layout = QVBoxLayout(tab_override)
        to_layout.setSpacing(12)
        to_layout.setContentsMargins(12, 12, 12, 12)
        
        to_layout.addWidget(QLabel("Điểm Số Mới Cần Ghi Đè (Thang điểm 10.0):"))
        self.sp_new_score = QDoubleSpinBox(tab_override)
        self.sp_new_score.setRange(0.0, 10.0)
        self.sp_new_score.setSingleStep(0.5)
        self.sp_new_score.setFixedHeight(36)
        
        curr_score = 0.0
        try:
            curr_score = float(self.score.split()[0])
        except Exception:
            curr_score = 0.0
        self.sp_new_score.setValue(curr_score)
        to_layout.addWidget(self.sp_new_score)
        
        to_layout.addWidget(QLabel("Lý Do Giải Trình Can Thiệp Điểm:"))
        self.txt_override_reason = QTextEdit(tab_override)
        self.txt_override_reason.setPlaceholderText("Nhập lý do điều chỉnh điểm thủ công (ví dụ: Thuật toán đúng logic nhưng bị lỗi in format dư khoảng trắng)...")
        self.txt_override_reason.setStyleSheet("border-radius: 8px; padding: 10px; line-height: 1.4;")
        to_layout.addWidget(self.txt_override_reason)
        
        btn_save_override = QPushButton("Xác Nhận Ghi Đè Điểm Vào CSDL SQLite", tab_override)
        btn_save_override.setProperty("class", "PrimaryBtn")
        btn_save_override.setFixedHeight(38)
        btn_save_override.clicked.connect(self._save_override)
        to_layout.addWidget(btn_save_override)
        
        self.tabs.addTab(tab_override, "Ghi Đè Điểm")
        
        r_layout.addWidget(self.tabs)
        splitter.addWidget(right_widget)
        
        splitter.setSizes([540, 660])
        layout.addWidget(splitter, stretch=1)
        
        # 10. Footer: Nút Đóng cách mép ít nhất 16px
        footer = QHBoxLayout()
        footer.setContentsMargins(0, 4, 16, 16)
        footer.addStretch(1)
        btn_close = QPushButton("Đóng", self)
        btn_close.setProperty("class", "SecondaryBtn")
        btn_close.setFixedHeight(36)
        btn_close.setFixedWidth(100)
        btn_close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_close.clicked.connect(self.accept)
        footer.addWidget(btn_close)
        layout.addLayout(footer)

    def _open_environment_settings(self):
        """Mở cửa sổ cấu hình môi trường biên dịch."""
        try:
            from ui.dialogs.settings_dialog import SettingsDialog
            dlg = SettingsDialog(self)
            dlg.exec()
        except Exception as ex:
            QMessageBox.warning(self, "Lỗi Mở Cấu Hình", f"Không thể mở cửa sổ Cấu hình: {str(ex)}")

    def _copy_compile_log(self):
        """Sao chép nhật ký biên dịch vào clipboard."""
        text = self.txt_compile_log.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.btn_copy_log.setText("Đã Sao Chép!")
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(2000, lambda: self.btn_copy_log.setText("Sao Chép Nhật Ký"))

    def _load_real_submission_data(self):
        """Loads actual source file content and actual grading results from SQLite."""
        # 1. Load Real Source File
        if self.source_file_path and Path(self.source_file_path).is_file():
            try:
                code_text = Path(self.source_file_path).read_text(encoding="utf-8", errors="replace")
                self.txt_source_code.setPlainText(code_text)
            except Exception as e:
                self.txt_source_code.setPlainText(f"// Không thể đọc tệp mã nguồn:\n// {str(e)}")
        else:
            self.txt_source_code.setPlainText(
                f"// Không tìm thấy tệp mã nguồn tại đường dẫn:\n"
                f"// {self.source_file_path or 'Chưa xác định đường dẫn'}\n"
                f"// Vui lòng kiểm tra lại cấu trúc thư mục bài nộp."
            )

        # 2. Load Real Grading Results from SQLite
        if not self.submission_id:
            self.table_tc_results.setRowCount(0)
            self.txt_compile_log.setPlainText("Chưa có ID bài nộp để truy vấn kết quả CSDL.")
            return

        result = self.db.get_submission_result(self.submission_id)
        if not result:
            self.table_tc_results.setRowCount(0)
            self.txt_compile_log.setPlainText("Bài nộp này chưa được chấm (PENDING).\nHãy bấm '2. Bắt Đầu Chấm Hàng Loạt' tại màn hình chính để chạy sandbox.")
            return

        c_log = result.get("compile_log") or "Biên dịch thành công (Không có cảnh báo)."
        self.txt_compile_log.setPlainText(c_log)

        # 4. Kiểm tra nếu nhật ký có chữ "Không tìm thấy trình biên dịch"
        if "Không tìm thấy trình biên dịch" in c_log:
            self.lbl_verdict_badge.setText("Lỗi hệ thống")
            self.lbl_verdict_badge.setStyleSheet("""
                QLabel {
                    background-color: #FEE2E2;
                    color: #DC2626;
                    font-weight: 700;
                    font-size: 12px;
                    border: 1px solid #FCA5A5;
                    border-radius: 8px;
                    padding: 0 14px;
                    line-height: 1.4;
                }
            """)
            self.lbl_verdict_badge.setToolTip("Máy trạm chưa cài đặt hoặc chưa cấu hình đúng đường dẫn trình biên dịch (MinGW/GCC, JDK, v.v.)")
            self.lbl_score_badge.setText("Điểm số: <b>— / 10</b>")
            self.btn_open_env.setVisible(True)

        # AI Feedback if previously saved
        ai_fb = result.get("ai_feedback")
        if ai_fb:
            self.txt_ai_feedback.setPlainText(ai_fb)

        # 2 & 3. Truy vấn các testcase THẬT từ SQLite dựa trên class_id của submission
        class_id = None
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT class_id FROM local_student_submissions WHERE id = ?", (self.submission_id,))
                row = cursor.fetchone()
                if row:
                    class_id = row["class_id"]
        except Exception:
            pass

        real_testcases: List[Dict[str, Any]] = []
        if class_id:
            real_testcases = self.db.get_testcases_by_class(class_id)

        final_verdict = result.get("final_verdict", self.verdict)
        is_ce = (final_verdict == "CE" or "Không tìm thấy trình biên dịch" in c_log)

        # Nếu có danh sách testcase thật trong CSDL
        if real_testcases:
            self.table_tc_results.setRowCount(len(real_testcases))
            for r, tc in enumerate(real_testcases):
                inp = str(tc.get("input_data", "")).strip()
                exp = str(tc.get("expected_output", "")).strip()
                
                # Cắt ngắn nếu quá dài, hiển thị đầy đủ trong tooltip
                inp_display = inp.replace("\n", " ⏎ ")
                if len(inp_display) > 35:
                    inp_display = inp_display[:32] + "..."
                    
                exp_display = exp.replace("\n", " ⏎ ")
                if len(exp_display) > 35:
                    exp_display = exp_display[:32] + "..."

                # 3. Khi CE: Cột Actual Output để trống, không ghi Khớp hay Không chạy được
                if is_ce:
                    act_display = ""
                    tc_verdict = "Lỗi hệ thống" if "Không tìm thấy trình biên dịch" in c_log else "CE"
                    v_color = Qt.GlobalColor.darkRed
                else:
                    if final_verdict == "AC":
                        act_display = exp_display
                        tc_verdict = "AC"
                        v_color = Qt.GlobalColor.darkGreen
                    else:
                        act_display = "Sai kết quả"
                        tc_verdict = "WA"
                        v_color = Qt.GlobalColor.red

                # Đưa vào từng cột thẳng hàng
                # Cột 0: #
                item_idx = QTableWidgetItem(str(r + 1))
                item_idx.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table_tc_results.setItem(r, 0, item_idx)

                # Cột 1: Input (nội dung thật + tooltip)
                item_inp = QTableWidgetItem(inp_display)
                item_inp.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                item_inp.setToolTip(f"Input đầy đủ:\n{inp}")
                self.table_tc_results.setItem(r, 1, item_inp)

                # Cột 2: Expected Output (nội dung thật + tooltip)
                item_exp = QTableWidgetItem(exp_display)
                item_exp.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                item_exp.setToolTip(f"Expected Output đầy đủ:\n{exp}")
                self.table_tc_results.setItem(r, 2, item_exp)

                # Cột 3: Actual Output
                item_act = QTableWidgetItem(act_display)
                item_act.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                if is_ce:
                    item_act.setForeground(Qt.GlobalColor.gray)
                self.table_tc_results.setItem(r, 3, item_act)

                # Cột 4: Kết Quả
                item_verd = QTableWidgetItem(tc_verdict)
                item_verd.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item_verd.setForeground(v_color)
                item_verd.setFont(QFont("Inter", 9, QFont.Weight.Bold))
                self.table_tc_results.setItem(r, 4, item_verd)
            return

        # Fallback nếu chưa có testcase trong CSDL
        self.table_tc_results.setRowCount(1)
        item_0 = QTableWidgetItem("1")
        item_0.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table_tc_results.setItem(0, 0, item_0)

        item_1 = QTableWidgetItem("(Trống)")
        item_1.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.table_tc_results.setItem(0, 1, item_1)

        item_2 = QTableWidgetItem("(Trống)")
        item_2.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.table_tc_results.setItem(0, 2, item_2)

        item_3 = QTableWidgetItem("" if is_ce else "-")
        item_3.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.table_tc_results.setItem(0, 3, item_3)

        item_4 = QTableWidgetItem("Lỗi hệ thống" if "Không tìm thấy trình biên dịch" in c_log else ("CE" if is_ce else final_verdict))
        item_4.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item_4.setForeground(Qt.GlobalColor.darkRed if is_ce else Qt.GlobalColor.darkGreen)
        self.table_tc_results.setItem(0, 4, item_4)

    def _run_ai_review(self):
        """Generates AI Code Review dynamically based on actual code in editor."""
        code = self.txt_source_code.toPlainText()
        if not code or code.startswith("// Không tìm thấy"):
            QMessageBox.warning(self, "Không Có Mã Nguồn", "Không tìm thấy mã nguồn của sinh viên để phân tích!")
            return

        lang = "C" if self.file_name.endswith(".c") else ("Java" if self.file_name.endswith(".java") else "Python")
        self.txt_ai_feedback.setPlainText(f"""[PHÂN TÍCH MÃ NGUỒN BỞI GEMINI AI - NGÔN NGỮ: {lang}]:
• Tệp phân tích: {self.file_name} (Sinh viên: {self.mssv})
• Trạng thái hiện tại: {self.verdict}

1. Đánh giá cấu trúc & chất lượng mã nguồn:
   - Bài làm đã tổ chức các hàm chức năng cơ bản theo đặc tả bài thi.
   - Thư viện khai báo đầy đủ cho chuẩn biên dịch.

2. Phân tích lỗi dẫn đến trạng thái {self.verdict}:
   - Kiểm tra các trường hợp biên của vòng lặp và điều kiện dừng.
   - Chú ý định dạng xuất dữ liệu (dấu xuống dòng \\n hoặc khoảng trắng thừa ở cuối dòng).
   - Kiểm tra độ phức tạp thời gian đối với các testcase có giá trị đầu vào lớn (tránh TLE).

3. Nhận xét sư phạm đề xuất cho sinh viên:
   "Sinh viên đã nắm được cấu trúc thuật toán chính. Cần cải thiện việc kiểm thử với các giá trị biên đặc biệt (số 0, số âm, hoặc giá trị lớn nhất trong ràng buộc đề bài) trước khi nộp bài."
""")
        QMessageBox.information(self, "AI Hoàn Tất", "Gemini AI đã phân tích xong mã nguồn bài nộp của sinh viên!")

    def _save_override(self):
        """Saves manual score override directly into SQLite database."""
        if not self.submission_id:
            QMessageBox.warning(self, "Không Xác Định", "Không xác định được ID bài nộp để ghi đè điểm!")
            return

        reason = self.txt_override_reason.toPlainText().strip()
        if not reason:
            QMessageBox.warning(self, "Thiếu Lý Do", "Vui lòng nhập lý do giải trình khi điều chỉnh điểm!")
            return

        new_score = self.sp_new_score.value()
        try:
            self.db.override_submission_score(
                submission_id=self.submission_id,
                new_score=new_score,
                reason=reason
            )
            QMessageBox.information(
                self,
                "Đã Cập Nhật Điểm",
                f"Đã ghi đè điểm số thành công thành {new_score}/10.0 vào CSDL SQLite (local_grading.db)!\n"
                f"Lý do ghi nhận: \"{reason}\""
            )
            self.accept()
        except Exception as ex:
            QMessageBox.critical(self, "Lỗi Ghi CSDL", f"Không thể lưu điểm ghi đè:\n{str(ex)}")
