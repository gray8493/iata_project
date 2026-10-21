"""
AITA Desktop Client - Two-Stage Plagiarism Forensic Viewer (PyQt6)
UC-17: Two-Stage Plagiarism Detection (AST + AI Verification)
100% Real Submissions & Cross-Comparison - Zero Mock Data
"""

import sys
import html
import json
import logging
import difflib
import itertools
from pathlib import Path
from typing import Optional, Dict, Any, List, Set

from PyQt6.QtCore import Qt, QRect, QSize, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QTextFormat, QTextCursor,
    QGuiApplication
)
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QPlainTextEdit, QTextEdit, QTextBrowser, QTabWidget, QSplitter, QMessageBox,
    QComboBox, QSpinBox, QProgressBar, QApplication, QFileDialog
)

SRC_DIR = Path(__file__).resolve().parent.parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ui.styles.theme import LIGHT_THEME_QSS
from database.db_manager import DatabaseManager
from services.ai_service import AiService
from services.grading_service import read_submission_source, resolve_question_file
from services.plagiarism_engine import (
    DEFAULT_QUESTION_KEY,
    PlagiarismEngine,
    question_sort_key,
)


class AiPlagiarismWorker(QThread):
    result_ready = pyqtSignal(dict)

    def __init__(self, code_a: str, code_b: str, similarity: float, language: str):
        super().__init__()
        self.code_a = code_a
        self.code_b = code_b
        self.similarity = similarity
        self.language = language

    def run(self):
        ai_service = AiService()
        result = ai_service.verify_plagiarism(
            student_a_code=self.code_a,
            student_b_code=self.code_b,
            ast_similarity_percentage=self.similarity,
            language=self.language
        )
        self.result_ready.emit(result)


class AiQuotaWorker(QThread):
    result_ready = pyqtSignal(dict)

    def run(self):
        self.result_ready.emit(AiService().get_quota())


# ==============================================================================
# 1. BỘ SẮP XẾP SỐ CHO CỘT % TRÙNG LẶP TRONG BẢNG
# ==============================================================================
class NumericTableWidgetItem(QTableWidgetItem):
    """Table item with true numeric comparison for percentage sorting."""
    def __init__(self, text: str, sort_value: float):
        super().__init__(text)
        self.sort_value = sort_value

    def __lt__(self, other):
        if isinstance(other, NumericTableWidgetItem):
            return self.sort_value < other.sort_value
        return super().__lt__(other)


# ==============================================================================
# 2. KHUNG HIỂN THỊ MÃ NGUỒN CÓ SỐ DÒNG (CODE EDITOR WITH LINE NUMBERS)
# ==============================================================================
class LineNumberArea(QWidget):
    """Line number gutter widget for CodeEditor."""
    def __init__(self, editor: 'CodeEditor'):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, a0):
        self.code_editor.line_number_area_paint_event(a0)


class CodeEditor(QPlainTextEdit):
    """Monospace code editor supporting line numbers and identical line highlights."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)

        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setReadOnly(True)
        self.setStyleSheet("""
            QPlainTextEdit {
                font-family: 'Consolas', 'Cascadia Mono', 'Courier New', monospace;
                font-size: 13px;
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                line-height: 1.45;
            }
        """)

    def line_number_area_width(self) -> int:
        digits = 1
        m = max(1, self.blockCount())
        while m >= 10:
            m //= 10
            digits += 1
        return 16 + self.fontMetrics().horizontalAdvance('9') * digits

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, e):
        super().resizeEvent(e)
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


# ==============================================================================
# 3. CỬA SỔ QUẢN LÝ QUÉT ĐẠO VĂN 2 VÒNG
# ==============================================================================
class PlagiarismDialog(QDialog):
    """
    Forensic plagiarism investigation dialog with Side-by-side Diff Viewer,
    synchronized scrolling, line numbers, and semantic evidence verification.
    """

    def __init__(self, parent=None, class_id: Optional[int] = None):
        super().__init__(parent)
        self.class_id = class_id
        self.db = DatabaseManager()
        self.pairs_data: List[Dict[str, Any]] = []
        self._syncing_scroll = False
        self._selected_pair: Optional[Dict[str, Any]] = None
        self._ai_running = False
        self._ai_tokens_available: Optional[int] = None
        self._ai_quota_loaded = False

        self.setWindowTitle("Hệ Thống Quét Đạo Văn 2 Vòng")
        self.setStyleSheet(LIGHT_THEME_QSS)

        # Kích thước tối thiểu theo yêu cầu; có thể phóng lớn theo vùng màn hình.
        screen = QGuiApplication.primaryScreen()
        if screen:
            avail = screen.availableGeometry()
            target_w = max(1100, min(1440, avail.width() - 40))
            target_h = max(700, min(900, avail.height() - 50))
            self.setMinimumSize(1100, 700)
            self.resize(target_w, target_h)
            self.move(avail.x() + (avail.width() - target_w) // 2,
                      avail.y() + (avail.height() - target_h) // 2)
        else:
            self.setMinimumSize(1100, 700)
            self.resize(1320, 820)

        self._init_ui()
        self._load_classes_into_selector()
        self._update_ai_button_state()
        self._quota_worker = AiQuotaWorker(self)
        self._quota_worker.result_ready.connect(self._on_quota_loaded)
        self._quota_worker.start()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 14)
        layout.setSpacing(10)

        # ----------------------------------------------------------------------
        # 0. Selection & Control Bar
        # ----------------------------------------------------------------------
        ctrl_card = QFrame(self)
        ctrl_card.setProperty("class", "Card")
        c_layout = QVBoxLayout(ctrl_card)
        c_layout.setContentsMargins(14, 10, 14, 10)
        c_layout.setSpacing(6)

        row_ctrl = QHBoxLayout()
        row_ctrl.setSpacing(12)

        lbl_select_class = QLabel("Đợt chấm:", ctrl_card)
        lbl_select_class.setStyleSheet("font-weight: 600; font-size: 13px; color: #1E293B;")
        row_ctrl.addWidget(lbl_select_class)

        self.combo_class = QComboBox(ctrl_card)
        self.combo_class.setMinimumWidth(240)
        self.combo_class.setFixedHeight(36)
        self.combo_class.view().setTextElideMode(Qt.TextElideMode.ElideRight)
        self.combo_class.currentIndexChanged.connect(self._on_combo_class_changed)
        row_ctrl.addWidget(self.combo_class)

        row_ctrl.addSpacing(12)
        lbl_thresh = QLabel("Ngưỡng báo động:", ctrl_card)
        lbl_thresh.setStyleSheet("font-weight: 500; font-size: 13px; color: #475569;")
        row_ctrl.addWidget(lbl_thresh)

        # 1. Ô Ngưỡng báo động mở rộng, nút tăng giảm phẳng bo góc
        self.spin_thresh = QSpinBox(ctrl_card)
        self.spin_thresh.setRange(30, 95)
        self.spin_thresh.setValue(70)
        self.spin_thresh.setSuffix(" %")
        self.spin_thresh.setMinimumWidth(100)
        self.spin_thresh.setFixedHeight(36)
        self.spin_thresh.setStyleSheet("""
            QSpinBox {
                font-size: 13px;
                font-weight: 600;
                color: #0F172A;
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 4px 8px;
            }
            QSpinBox:hover {
                border-color: #94A3B8;
            }
            QSpinBox:focus {
                border-color: #0284C7;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                border: none;
                background: #F1F5F9;
                border-radius: 4px;
                margin: 2px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background: #E2E8F0;
            }
        """)
        row_ctrl.addWidget(self.spin_thresh)

        row_ctrl.addSpacing(12)
        self.btn_run_scan = QPushButton("Bắt Đầu Quét Đạo Văn", ctrl_card)
        self.btn_run_scan.setProperty("class", "PrimaryBtn")
        self.btn_run_scan.setMinimumWidth(185)
        self.btn_run_scan.setFixedHeight(36)
        self.btn_run_scan.clicked.connect(self._run_real_plagiarism_scan)
        row_ctrl.addWidget(self.btn_run_scan)

        c_layout.addLayout(row_ctrl)

        summary_row = QHBoxLayout()
        self.lbl_status_subtitle = QLabel("Chưa có kết quả quét.", ctrl_card)
        self.lbl_status_subtitle.setWordWrap(True)
        self.lbl_status_subtitle.setStyleSheet("font-size: 12px; color: #475569; line-height: 1.4;")
        summary_row.addWidget(self.lbl_status_subtitle, stretch=1)

        self.lbl_v1 = QLabel("Vòng 1: 0 cặp nghi vấn", ctrl_card)
        self.lbl_v1.setStyleSheet("font-size: 12px; font-weight: 600; color: #475569; padding: 4px 8px;")
        self.lbl_v1.setToolTip("Vòng 1 (Đối soát cấu trúc theo từng câu)")
        summary_row.addWidget(self.lbl_v1)
        self.lbl_v2 = QLabel("Vòng 2: 0 cặp báo động", ctrl_card)
        self.lbl_v2.setStyleSheet("font-size: 12px; font-weight: 600; color: #475569; padding: 4px 8px;")
        self.lbl_v2.setToolTip("Vòng 2 (AI thẩm định, từ 80% trở lên)")
        summary_row.addWidget(self.lbl_v2)
        c_layout.addLayout(summary_row)

        # Thanh tiến độ trong lúc quét (ẩn mặc định)
        self.progress_bar = QProgressBar(ctrl_card)
        self.progress_bar.setFixedHeight(5)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #E2E8F0;
                border: none;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #0284C7;
                border-radius: 2px;
            }
        """)
        self.progress_bar.hide()
        c_layout.addWidget(self.progress_bar)

        layout.addWidget(ctrl_card)

        # ----------------------------------------------------------------------
        # Bảng nghi vấn 30% | chi tiết cặp 70% (splitter kéo được)
        # ----------------------------------------------------------------------
        main_splitter = QSplitter(Qt.Orientation.Horizontal, self)
        main_splitter.setStyleSheet("""
            QSplitter::handle:horizontal {
                background-color: #E2E8F0;
                width: 6px;
                border-radius: 3px;
                margin: 0px 2px;
            }
            QSplitter::handle:horizontal:hover {
                background-color: #0284C7;
            }
        """)

        # LEFT WIDGET: Pairs Table
        left_widget = QWidget(main_splitter)
        l_layout = QVBoxLayout(left_widget)
        l_layout.setContentsMargins(0, 0, 0, 0)
        l_layout.setSpacing(8)

        lbl_table_head = QLabel("Cặp nghi vấn", left_widget)
        lbl_table_head.setStyleSheet("font-weight: 600; font-size: 13px; color: #1E293B;")
        l_layout.addWidget(lbl_table_head)

        self.table_pairs = QTableWidget(left_widget)
        self.table_pairs.setColumnCount(5)
        self.table_pairs.setHorizontalHeaderLabels(["SV A", "SV B", "Câu", "% Trùng Lặp", "Đánh Giá"])
        self.table_pairs.verticalHeader().setVisible(False)
        self.table_pairs.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_pairs.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table_pairs.setSortingEnabled(True)
        self.table_pairs.setStyleSheet("""
            QTableWidget::item { padding: 4px 3px; border-bottom: 1px solid #E2E8F0; }
            QTableWidget::item:selected { background-color: #DBEAFE; color: #0F172A; border: none; }
            QTableWidget::item:hover { background-color: #EFF6FF; }
            QTableWidget::item:selected:hover { background-color: #DBEAFE; }
        """)

        header = self.table_pairs.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table_pairs.setColumnWidth(0, 61)
        self.table_pairs.setColumnWidth(1, 61)
        self.table_pairs.setColumnWidth(2, 40)
        self.table_pairs.setColumnWidth(3, 84)
        self.table_pairs.setMinimumWidth(310)

        self.table_pairs.cellClicked.connect(self._on_pair_selected)
        l_layout.addWidget(self.table_pairs)

        # Nhãn empty state cho bảng
        self.lbl_table_empty = QLabel(
            "Chưa có kết quả quét. Chọn lớp và bấm 'Bắt Đầu Quét Đạo Văn'",
            self.table_pairs
        )
        self.lbl_table_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_table_empty.setStyleSheet("color: #64748B; font-size: 13px; font-weight: 500; background: transparent; padding: 20px;")
        self.lbl_table_empty.setWordWrap(True)

        main_splitter.addWidget(left_widget)

        # RIGHT WIDGET: summary card and two full-height detail tabs
        right_widget = QWidget(main_splitter)
        r_layout = QVBoxLayout(right_widget)
        r_layout.setContentsMargins(0, 0, 0, 0)
        r_layout.setSpacing(10)

        summary_card = QFrame(right_widget)
        summary_card.setProperty("class", "Card")
        summary_row = QHBoxLayout(summary_card)
        summary_row.setContentsMargins(12, 10, 12, 10)
        summary_row.setSpacing(10)
        summary_text = QVBoxLayout()
        self.lbl_pair_summary = QLabel("Chọn một cặp ở bảng bên trái", summary_card)
        self.lbl_pair_summary.setStyleSheet("font-size: 15px; font-weight: 700; color: #0F172A; line-height: 1.4;")
        self.lbl_pair_summary.setWordWrap(True)
        self.lbl_pair_verdict = QLabel("Chưa kết luận", summary_card)
        self.lbl_pair_verdict.setStyleSheet("font-size: 13px; font-weight: 600; color: #475569;")
        summary_text.addWidget(self.lbl_pair_summary)
        summary_text.addWidget(self.lbl_pair_verdict)
        summary_row.addLayout(summary_text, stretch=1)

        self.btn_run_ai_plag = QPushButton("Kích Hoạt AI Thẩm Định Chuyên Sâu", summary_card)
        self.btn_run_ai_plag.setFixedHeight(36)
        self.btn_run_ai_plag.setMinimumWidth(205)
        self.btn_run_ai_plag.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #1D4ED8;
                border: 1px solid #2563EB;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
                padding: 0 12px;
            }
            QPushButton:hover {
                background-color: #EFF6FF;
            }
            QPushButton:disabled {
                color: #94A3B8;
                border-color: #CBD5E1;
                background-color: #F8FAFC;
            }
        """)
        self.btn_run_ai_plag.clicked.connect(self._run_ai_plagiarism_verification)
        summary_row.addWidget(self.btn_run_ai_plag)
        r_layout.addWidget(summary_card)

        self.detail_tabs = QTabWidget(right_widget)
        self.ai_review_browser = QTextBrowser(self.detail_tabs)
        self.ai_review_browser.setOpenLinks(False)
        self.ai_review_browser.anchorClicked.connect(self._on_evidence_link_clicked)
        self.ai_review_browser.setStyleSheet("""
            QTextBrowser { font-size: 14px; color: #1E293B; line-height: 1.6;
                background: #FFFFFF; border: none; padding: 14px; }
        """)
        self.ai_review_browser.setHtml(self._empty_ai_html("Chọn một cặp ở bảng bên trái"))
        self.detail_tabs.addTab(self.ai_review_browser, "Nhận xét của AI")

        code_tab = QWidget(self.detail_tabs)
        code_layout = QVBoxLayout(code_tab)
        code_layout.setContentsMargins(8, 8, 8, 8)
        code_layout.setSpacing(6)
        self.lbl_highlight_legend = QLabel("Đoạn giống nhau được tô màu riêng theo từng khối.", code_tab)
        self.lbl_highlight_legend.setTextFormat(Qt.TextFormat.RichText)
        self.lbl_highlight_legend.setStyleSheet("font-size: 12px; color: #475569; line-height: 1.4;")
        code_layout.addWidget(self.lbl_highlight_legend)

        diff_splitter = QSplitter(Qt.Orientation.Horizontal, code_tab)
        self.lbl_sv_a = QLabel("Sinh viên A", diff_splitter)
        self.lbl_sv_b = QLabel("Sinh viên B", diff_splitter)
        self.txt_code_a = CodeEditor(diff_splitter)
        self.txt_code_b = CodeEditor(diff_splitter)
        self.txt_code_a.setPlainText("Chọn một cặp ở bảng bên trái")
        self.txt_code_b.setPlainText("Chọn một cặp ở bảng bên trái")
        for label in (self.lbl_sv_a, self.lbl_sv_b):
            label.setStyleSheet("font-weight: 700; color: #1E293B; font-size: 13px;")
        # Editor headings and editors share the two equal columns through a small wrapper.
        left_code = QWidget(diff_splitter)
        left_layout = QVBoxLayout(left_code)
        left_layout.setContentsMargins(0, 0, 4, 0)
        left_layout.addWidget(self.lbl_sv_a)
        left_layout.addWidget(self.txt_code_a, stretch=1)
        right_code = QWidget(diff_splitter)
        right_layout = QVBoxLayout(right_code)
        right_layout.setContentsMargins(4, 0, 0, 0)
        right_layout.addWidget(self.lbl_sv_b)
        right_layout.addWidget(self.txt_code_b, stretch=1)
        diff_splitter.addWidget(left_code)
        diff_splitter.addWidget(right_code)
        diff_splitter.setSizes([1, 1])
        self.txt_code_a.verticalScrollBar().valueChanged.connect(self._sync_scroll_a_to_b)
        self.txt_code_b.verticalScrollBar().valueChanged.connect(self._sync_scroll_b_to_a)
        code_layout.addWidget(diff_splitter, stretch=1)
        self.detail_tabs.addTab(code_tab, "So sánh mã nguồn")
        r_layout.addWidget(self.detail_tabs, stretch=1)
        main_splitter.addWidget(right_widget)

        main_splitter.setStretchFactor(0, 3)
        main_splitter.setStretchFactor(1, 7)
        main_splitter.setSizes([340, 790])
        layout.addWidget(main_splitter, stretch=1)

        # ----------------------------------------------------------------------
        # 3. Footer Actions (Cách đáy tối thiểu 16px, lề trái phải bằng nhau)
        # ----------------------------------------------------------------------
        footer = QHBoxLayout()
        footer.setContentsMargins(0, 8, 0, 0)

        self.btn_export_report = QPushButton("Xuất Biên Bản Đạo Văn", self)
        self.btn_export_report.setProperty("class", "PrimaryBtn")
        self.btn_export_report.setFixedHeight(38)
        self.btn_export_report.setEnabled(False)
        self.btn_export_report.clicked.connect(self._export_report)
        footer.addWidget(self.btn_export_report)

        footer.addStretch(1)

        btn_close = QPushButton("Đóng", self)
        btn_close.setProperty("class", "SecondaryBtn")
        btn_close.setFixedHeight(38)
        btn_close.setMinimumWidth(100)
        btn_close.clicked.connect(self.accept)
        footer.addWidget(btn_close)

        layout.addLayout(footer)

    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        if hasattr(self, 'lbl_table_empty') and hasattr(self, 'table_pairs'):
            self.lbl_table_empty.setGeometry(self.table_pairs.rect())
            self.lbl_table_empty.setVisible(self.table_pairs.rowCount() == 0)

    def closeEvent(self, event):
        # Chờ các worker đồng bộ kết thúc trước khi QWidget hủy QThread con.
        for worker_name in ("_quota_worker", "ai_plag_worker"):
            worker = getattr(self, worker_name, None)
            if worker is not None and worker.isRunning():
                worker.wait()
        super().closeEvent(event)

    # ==========================================================================
    # CÁC HÀM XỬ LÝ CUỘN ĐỒNG BỘ
    # ==========================================================================
    def _sync_scroll_a_to_b(self, val):
        if not self._syncing_scroll:
            self._syncing_scroll = True
            source = self.txt_code_a.verticalScrollBar()
            target = self.txt_code_b.verticalScrollBar()
            ratio = val / source.maximum() if source.maximum() else 0
            target.setValue(round(ratio * target.maximum()))
            self._syncing_scroll = False

    def _sync_scroll_b_to_a(self, val):
        if not self._syncing_scroll:
            self._syncing_scroll = True
            source = self.txt_code_b.verticalScrollBar()
            target = self.txt_code_a.verticalScrollBar()
            ratio = val / source.maximum() if source.maximum() else 0
            target.setValue(round(ratio * target.maximum()))
            self._syncing_scroll = False

    def _sync_hscroll_a_to_b(self, val):
        if not self._syncing_scroll:
            self._syncing_scroll = True
            self.txt_code_b.horizontalScrollBar().setValue(val)
            self._syncing_scroll = False

    def _sync_hscroll_b_to_a(self, val):
        if not self._syncing_scroll:
            self._syncing_scroll = True
            self.txt_code_a.horizontalScrollBar().setValue(val)
            self._syncing_scroll = False

    # ==========================================================================
    # QUẢN LÝ DỮ LIỆU & QUÉT ĐẠO VĂN
    # ==========================================================================
    def _on_combo_class_changed(self, index: int):
        cur_text = self.combo_class.currentText()
        self.combo_class.setToolTip(cur_text)
        self.btn_run_scan.setEnabled(self.combo_class.count() > 0)

    def _load_classes_into_selector(self):
        """Populates class selector dropdown with all existing classes."""
        self.combo_class.clear()
        classes = self.db.get_all_classes()
        selected_index = 0
        for idx, c in enumerate(classes):
            label = f"[{c['course_code']}] {c['class_name']} — {c['programming_language']}"
            self.combo_class.addItem(label, c["id"])
            if self.class_id and c["id"] == self.class_id:
                selected_index = idx

        if classes:
            self.combo_class.setCurrentIndex(selected_index)
            self.combo_class.setToolTip(self.combo_class.currentText())
            self.btn_run_scan.setEnabled(True)
        else:
            self.combo_class.setToolTip("Chưa có lớp học nào trong hệ thống")
            self.btn_run_scan.setEnabled(False)

        self._update_empty_state_visibility()

    def _update_empty_state_visibility(self):
        is_empty = self.table_pairs.rowCount() == 0
        self.lbl_table_empty.setVisible(is_empty)
        if hasattr(self, 'table_pairs'):
            self.lbl_table_empty.setGeometry(self.table_pairs.rect())

    def _class_question_keys(self) -> List[str]:
        """Danh sách câu (Q1, Q2, ...) của lớp, lấy từ cấu hình testcase."""
        try:
            testcases = self.db.get_testcases_by_class(self.class_id)
        except Exception:
            return []
        keys: List[str] = []
        for tc in testcases or []:
            key = (tc.get("question_number") or "").strip() or DEFAULT_QUESTION_KEY
            if key not in keys:
                keys.append(key)
        keys.sort(key=question_sort_key)
        return keys

    def _collect_question_units(
        self, source_path: Path, question_keys: List[str], language: str
    ) -> Dict[str, str]:
        """
        Trả về {tên câu: mã nguồn} của một bài nộp.
        - Bài 1 file      -> coi cả file là một câu (Q1).
        - Bài nộp thư mục -> dò từng `Q<nn>.<ext>` giống hệt lúc chấm điểm
          (multi-question), nhờ đó chỉ copy câu Q1 vẫn bị phát hiện thay vì bị
          pha loãng bởi các câu khác. Nếu không dò được thì gộp toàn bộ file.
        """
        if source_path.is_file():
            try:
                return {
                    DEFAULT_QUESTION_KEY: source_path.read_text(encoding="utf-8", errors="replace")
                }
            except Exception:
                return {}

        if not source_path.is_dir():
            return {}

        units: Dict[str, str] = {}
        for key in question_keys:
            found = resolve_question_file(source_path, key, language)
            if not found:
                continue
            try:
                units[key] = found.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
        if units:
            return units

        fallback = read_submission_source(str(source_path))
        if fallback and fallback.strip():
            return {DEFAULT_QUESTION_KEY: fallback}
        return {}

    @staticmethod
    def _metrics_tooltip(pair: Dict[str, Any]) -> str:
        """Tooltip chi tiết Jaccard / độ bao phủ theo từng câu của một cặp bài."""
        scores = pair.get("question_scores") or {}
        if not scores:
            return (
                f"Jaccard {pair.get('jaccard', pair.get('sim', 0.0)):.1f}% · "
                f"Bao phủ {pair.get('containment', 0.0):.1f}%"
            )
        lines = [
            f"{key}: trùng {value.get('sim', 0.0):.1f}% "
            f"(Jaccard {value.get('jaccard', 0.0):.1f}%, bao phủ {value.get('containment', 0.0):.1f}%)"
            for key, value in scores.items()
        ]
        return "Độ trùng lặp theo từng câu:\n" + "\n".join(lines)

    def _run_real_plagiarism_scan(self):
        """Scans real student code files using token/Jaccard similarity."""
        selected_class_id = self.combo_class.currentData()
        if not selected_class_id:
            self._show_empty_state("Vui lòng chọn một lớp học trong danh sách để bắt đầu quét.")
            return

        self.class_id = selected_class_id
        existing_reports = self.db.get_plagiarism_reports(self.class_id)
        old_notes = {
            frozenset((row.get("student_a_mssv", ""), row.get("student_b_mssv", ""))): row
            for row in existing_reports
        }
        subs = self.db.get_submissions_by_class(self.class_id)
        # DB cũ có thể chứa nhiều kết quả đang hoạt động cho một bài, khiến JOIN
        # lặp dòng và tạo cặp tự so sánh MSSV với chính nó. Chọn bài có ID mới nhất.
        latest_submission_by_mssv: Dict[str, Dict[str, Any]] = {}
        for submission in subs:
            mssv = str(submission.get("student_mssv", "")).strip().upper()
            if not mssv:
                continue
            current = latest_submission_by_mssv.get(mssv)
            if current is None or int(submission.get("id", 0) or 0) >= int(current.get("id", 0) or 0):
                latest_submission_by_mssv[mssv] = submission
        duplicate_rows_removed = len(subs) - len(latest_submission_by_mssv)
        subs = sorted(latest_submission_by_mssv.values(), key=lambda item: item["student_mssv"].upper())
        if len(subs) < 2:
            self._show_empty_state(f"Đợt chấm này hiện có {len(subs)} bài nộp. Cần tối thiểu 2 bài để đối soát chéo.")
            return

        # Đổi trạng thái nút bấm và hiển thị thanh tiến độ
        self.btn_run_scan.setText("Đang quét...")
        self.btn_run_scan.setEnabled(False)
        self.progress_bar.show()
        self.progress_bar.setValue(10)
        QApplication.processEvents()

        cls_info = self.db.get_class_by_id(self.class_id)
        language = (cls_info or {}).get("programming_language", "C")

        # Mỗi bài nộp được tách theo từng câu (Q1, Q2, ...) để so đúng câu với nhau
        question_keys = self._class_question_keys()

        # Đọc mã nguồn thật từ đĩa (hỗ trợ cả bài 1 file và bài nộp dạng thư mục)
        scan_items = []
        for s in subs:
            raw_path = s.get("source_file_path")
            if not raw_path:
                continue
            units = self._collect_question_units(Path(raw_path), question_keys, language)
            if not units:
                continue
            scan_items.append({
                "mssv": s["student_mssv"],
                "name": s["student_mssv"],
                "units": units
            })

        self.progress_bar.setValue(40)
        QApplication.processEvents()

        if len(scan_items) < 2:
            self._finish_scan()
            self._show_empty_state("Không tìm thấy đủ tệp mã nguồn hợp lệ trên đĩa để quét.")
            return

        # Ngưỡng phát hiện do người dùng cấu hình (Cách 1: Lọc triệt để theo ngưỡng đã chọn)
        red_threshold = float(self.spin_thresh.value())

        # Vòng 1: giữ nguyên thuật toán chuẩn hoá token + Winnowing theo từng câu.
        engine = PlagiarismEngine()
        report = engine.scan_class(scan_items, language=language, threshold=red_threshold)
        total_pairs_checked = report["total_pairs"]
        raw_matches = report["matches"]
        questions_checked = report.get("questions") or []

        self.progress_bar.setValue(80)
        QApplication.processEvents()

        # Lưu báo cáo Vòng 1 vào CSDL cục bộ (local_plagiarism_reports)
        try:
            self.db.clear_plagiarism_reports(self.class_id)
            for m in raw_matches:
                previous = old_notes.get(frozenset((m["sv_a"], m["sv_b"]))) or {}
                self.db.save_plagiarism_report(
                    self.class_id, m["sv_a"], m["sv_b"], m["sim"],
                    ai_evidence_details=previous.get("ai_evidence_details"),
                    question_key=", ".join(m["questions"]),
                    ai_evidence_json=previous.get("ai_evidence_json"),
                )
        except Exception:
            pass

        pairs_found = [{
            "sv_a": m["sv_a"],
            "sv_b": m["sv_b"],
            "sim": m["sim"],
            "jaccard": m["jaccard"],
            "containment": m["containment"],
            "question": m["question"],
            "questions": m["questions"],
            "question_scores": m["question_scores"],
            "verdict": m["verdict"],
            "code_a": m["code_a"],
            "code_b": m["code_b"],
            "ai_evidence_details": (old_notes.get(frozenset((m["sv_a"], m["sv_b"]))) or {}).get("ai_evidence_details"),
            "ai_evidence_json": (old_notes.get(frozenset((m["sv_a"], m["sv_b"]))) or {}).get("ai_evidence_json"),
        } for m in raw_matches]
        for pair in pairs_found:
            saved = self._saved_ai_data(pair)
            if saved.get("structured"):
                pair["ai_review"] = saved["structured"]
            elif saved.get("legacy"):
                pair["ai_legacy"] = saved["legacy"]
        # Vòng 2 (AI) chỉ nhận các cặp đủ điều kiện tối thiểu 80% theo hợp đồng API
        v2_red_alert = sum(1 for p in pairs_found if p["sim"] >= 80.0)

        self.progress_bar.setValue(100)
        QApplication.processEvents()
        self._finish_scan()

        self.pairs_data = pairs_found
        scope = f"{len(questions_checked)} câu" if questions_checked else "1 câu"
        filter_note = " Đã loại mã khung sườn dùng chung của lớp." if report.get("boilerplate_filtered") else ""
        if duplicate_rows_removed:
            filter_note += f" Đã gộp {duplicate_rows_removed} dòng dữ liệu MSSV trùng."
        if pairs_found:
            self.lbl_status_subtitle.setText(
                f"Đã đối soát {total_pairs_checked} lượt so sánh theo {scope}. "
                f"Phát hiện {len(pairs_found)} cặp vượt ngưỡng {int(red_threshold)}%.{filter_note}"
            )
            self.lbl_status_subtitle.setStyleSheet("font-size: 12px; color: #475569; line-height: 1.4;")
        else:
            self.lbl_status_subtitle.setText(
                f"Đã đối soát {total_pairs_checked} lượt so sánh theo {scope}. "
                f"Không có cặp bài nào vượt ngưỡng {int(red_threshold)}%.{filter_note}"
            )
            self.lbl_status_subtitle.setStyleSheet("font-size: 12px; color: #475569; line-height: 1.4;")

        self.lbl_v1.setText(f"Vòng 1: {len(pairs_found)} cặp nghi vấn")
        self.lbl_v2.setText(f"Vòng 2: {v2_red_alert} cặp báo động")

        # Cập nhật bảng dữ liệu
        self.table_pairs.setSortingEnabled(False)
        self.table_pairs.setRowCount(len(pairs_found))

        for r, p in enumerate(pairs_found):
            item_a = QTableWidgetItem(p["sv_a"])
            item_b = QTableWidgetItem(p["sv_b"])
            # Cột % căn giữa và hỗ trợ sắp xếp số
            sim_label, sim_color = self._similarity_label(p["sim"])
            item_q = QTableWidgetItem(p.get("question") or DEFAULT_QUESTION_KEY)
            item_sim = NumericTableWidgetItem(f"{p['sim']:.1f}% · {sim_label}", p["sim"])
            item_v = QTableWidgetItem(self._pair_assessment(p))

            item_a.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_b.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_sim.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_q.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_v.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

            item_sim.setForeground(QColor(sim_color))
            item_v.setForeground(QColor("#B91C1C" if item_v.text() in ("Báo động", "AI xác nhận") else "#475569"))
            item_v.setToolTip(self._metrics_tooltip(p))

            self.table_pairs.setItem(r, 0, item_a)
            self.table_pairs.setItem(r, 1, item_b)
            self.table_pairs.setItem(r, 2, item_q)
            self.table_pairs.setItem(r, 3, item_sim)
            self.table_pairs.setItem(r, 4, item_v)

        self.table_pairs.setSortingEnabled(True)
        self.table_pairs.sortItems(3, Qt.SortOrder.DescendingOrder)

        self._update_empty_state_visibility()
        self.btn_export_report.setEnabled(len(pairs_found) > 0)

        if pairs_found:
            self.table_pairs.selectRow(0)
            self._load_diff(0)
        else:
            self.lbl_pair_summary.setText("Chưa có cặp vượt ngưỡng")
            self.lbl_pair_verdict.setText("Chưa kết luận")
            self.txt_code_a.setPlainText(f"Không có cặp bài nào đạt ngưỡng {int(red_threshold)}%.")
            self.txt_code_b.setPlainText(f"Đã đối soát {total_pairs_checked} lượt so sánh.")
            self.ai_review_browser.setHtml(self._empty_ai_html("Chọn một cặp ở bảng bên trái"))
            self.lbl_table_empty.setText(f"Không có cặp bài nào đạt độ trùng lặp từ {int(red_threshold)}% trở lên.")
            self.lbl_table_empty.show()

    def _finish_scan(self):
        self.btn_run_scan.setText("Bắt Đầu Quét Đạo Văn")
        self.btn_run_scan.setEnabled(True)
        self.progress_bar.hide()

    def _show_empty_state(self, message: str):
        self.lbl_status_subtitle.setText(message)
        self.lbl_status_subtitle.setStyleSheet("font-size: 12px; color: #475569; line-height: 1.4;")
        self.lbl_v1.setText("Vòng 1: 0 cặp nghi vấn")
        self.lbl_v2.setText("Vòng 2: 0 cặp báo động")
        self.table_pairs.setRowCount(0)
        self.pairs_data = []
        self._selected_pair = None
        self.lbl_pair_summary.setText("Chọn một cặp ở bảng bên trái")
        self.lbl_pair_verdict.setText("Chưa kết luận")
        self.lbl_sv_a.setText("Sinh viên A")
        self.lbl_sv_b.setText("Sinh viên B")
        self.txt_code_a.setPlainText("Chọn một cặp ở bảng bên trái")
        self.txt_code_b.setPlainText("Chọn một cặp ở bảng bên trái")
        self.ai_review_browser.setHtml(self._empty_ai_html("Chọn một cặp ở bảng bên trái"))
        self.btn_export_report.setEnabled(False)
        self._update_ai_button_state()
        self._update_empty_state_visibility()

    def _on_pair_selected(self, row, col):
        # Lấy theo mssv được chọn trên bảng để tránh lệch index khi sắp xếp
        if self.table_pairs.rowCount() == 0:
            return
        item_a = self.table_pairs.item(row, 0)
        item_b = self.table_pairs.item(row, 1)
        if not item_a or not item_b:
            return
        sv_a = item_a.text()
        sv_b = item_b.text()

        for idx, p in enumerate(self.pairs_data):
            if (p["sv_a"] == sv_a and p["sv_b"] == sv_b) or (p["sv_a"] == sv_b and p["sv_b"] == sv_a):
                self._load_diff(idx)
                break

    def _load_diff(self, idx: int):
        if not (0 <= idx < len(self.pairs_data)):
            return
        pair = self.pairs_data[idx]
        self._selected_pair = pair
        self.lbl_sv_a.setText(f"Sinh viên A: {pair['sv_a']}")
        self.lbl_sv_b.setText(f"Sinh viên B: {pair['sv_b']}")
        self.txt_code_a.setPlainText(pair["code_a"])
        self.txt_code_b.setPlainText(pair["code_b"])
        question = pair.get("question") or DEFAULT_QUESTION_KEY
        self.lbl_pair_summary.setText(
            f"{pair['sv_a']} và {pair['sv_b']} | Câu {question} | Trùng lặp {pair['sim']:.1f}%"
        )
        self.lbl_pair_verdict.setText(self._summary_assessment(pair))
        saved = self._saved_ai_data(pair)
        if saved.get("structured"):
            pair["ai_review"] = saved["structured"]
            self._render_ai_review(saved["structured"])
            self.btn_run_ai_plag.setText("Kích Hoạt AI Thẩm Định Chuyên Sâu")
        elif saved.get("legacy"):
            pair["ai_legacy"] = saved["legacy"]
            self._render_legacy_review(saved["legacy"])
            self.btn_run_ai_plag.setText("Thẩm Định Lại Bằng Tiếng Việt")
        else:
            self.ai_review_browser.setHtml(self._empty_ai_html("Chưa có nhận xét AI cho cặp này. Bấm nút thẩm định để bắt đầu."))
            self.btn_run_ai_plag.setText("Kích Hoạt AI Thẩm Định Chuyên Sâu")
        self._highlight_matching_lines(pair)
        self._update_ai_button_state()

    @staticmethod
    def _similarity_label(similarity: float):
        if similarity >= 90:
            return "Rất cao", "#991B1B"
        if similarity >= 80:
            return "Cao", "#DC2626"
        if similarity >= 70:
            return "Đáng chú ý", "#C2410C"
        return "Nghi vấn", "#475569"

    def _summary_assessment(self, pair: Dict[str, Any]) -> str:
        review = pair.get("ai_review")
        if review:
            confidence = float(review.get("do_tin_cay", 0) or 0)
            conclusion = str(review.get("ket_luan", "")).casefold()
            negative = any(word in conclusion for word in ("không đủ bằng chứng", "chưa kết luận", "chưa đủ cơ sở", "không thể xác định"))
            positive = any(word in conclusion for word in ("có dấu hiệu đạo văn", "đạo văn rõ", "sao chép đáng kể", "có khả năng sao chép"))
            if negative:
                label = "Chưa kết luận"
            elif positive and confidence >= 80:
                label = "Nghi vấn cao"
            else:
                label = "Nghi vấn" if confidence < 80 else "Nghi vấn cao"
            return f"{label} · Độ tin cậy AI {confidence:.0f}%"
        label = "Nghi vấn cao" if pair["sim"] >= 90 else "Nghi vấn"
        return f"{label} · AI chưa thẩm định"

    def _pair_assessment(self, pair: Dict[str, Any]) -> str:
        review = pair.get("ai_review")
        if review:
            conclusion = str(review.get("ket_luan", "")).casefold()
            confidence = float(review.get("do_tin_cay", 0) or 0)
            negative = any(word in conclusion for word in ("không đủ bằng chứng", "chưa kết luận", "chưa đủ cơ sở", "không thể xác định"))
            positive = any(word in conclusion for word in ("có dấu hiệu đạo văn", "đạo văn rõ", "sao chép đáng kể", "có khả năng sao chép"))
            if positive and confidence >= 80:
                return "AI xác nhận"
            if negative:
                return "Chưa kết luận"
        return "Báo động" if pair["sim"] >= 90 else "Nghi vấn"

    @staticmethod
    def _empty_ai_html(message: str) -> str:
        return (
            '<html><body style="font-family:Segoe UI, sans-serif; font-size:14px; line-height:1.6; color:#475569">'
            f'<p>{html.escape(message)}</p></body></html>'
        )

    @staticmethod
    def _is_structured_review(value: Any) -> bool:
        if not isinstance(value, dict):
            return False
        if not isinstance(value.get("ket_luan"), str) or not isinstance(value.get("do_tin_cay"), (int, float)):
            return False
        if not isinstance(value.get("bang_chung"), list) or not isinstance(value.get("khac_biet"), list) or not isinstance(value.get("de_xuat"), list):
            return False
        for evidence in value["bang_chung"]:
            if not isinstance(evidence, dict) or not isinstance(evidence.get("mo_ta"), str):
                return False
            for key in ("dong_a", "dong_b"):
                line_range = evidence.get(key)
                if (not isinstance(line_range, list) or len(line_range) != 2
                        or any(not isinstance(line, int) or isinstance(line, bool) or line < 1 for line in line_range)
                        or line_range[0] > line_range[1]):
                    return False
        if not all(isinstance(item, str) for item in value["khac_biet"] + value["de_xuat"]):
            return False
        return True

    def _saved_ai_data(self, pair: Dict[str, Any]) -> Dict[str, Any]:
        raw_json = pair.get("ai_evidence_json")
        if raw_json:
            try:
                parsed = json.loads(raw_json) if isinstance(raw_json, str) else raw_json
                if self._is_structured_review(parsed):
                    return {"structured": parsed}
            except (TypeError, ValueError):
                pass
        raw_text = pair.get("ai_evidence_details")
        if raw_text:
            try:
                parsed = json.loads(raw_text)
                if self._is_structured_review(parsed):
                    return {"structured": parsed}
            except (TypeError, ValueError):
                pass
            return {"legacy": str(raw_text)}
        return {}

    def _render_ai_review(self, review: Dict[str, Any]):
        pair = self._selected_pair or {}
        esc = lambda value: html.escape(str(value or ""))
        chunks = ['<html><body style="font-family:Segoe UI,sans-serif;font-size:14px;line-height:1.65;color:#1E293B">']
        chunks.append(f'<h3 style="font-size:15px;margin:4px 0 2px">Kết luận</h3><p>{esc(review.get("ket_luan"))}</p>')
        chunks.append(f'<h3 style="font-size:15px;margin:14px 0 2px">Bằng chứng</h3>')
        evidence = review.get("bang_chung") or []
        if evidence:
            chunks.append('<ul style="margin-top:4px">')
            for idx, item in enumerate(evidence):
                if not isinstance(item, dict):
                    continue
                a_range = item.get("dong_a") or []
                b_range = item.get("dong_b") or []
                if len(a_range) != 2 or len(b_range) != 2:
                    continue
                desc = esc(item.get("mo_ta"))
                link = (
                    f'<a href="evidence:{idx}">Xem dòng {a_range[0]}-{a_range[1]} '
                    f'({esc(pair.get("sv_a", "SV A"))}) / {b_range[0]}-{b_range[1]} '
                    f'({esc(pair.get("sv_b", "SV B"))})</a>'
                )
                chunks.append(f'<li>{desc}<br>{link}</li>')
            chunks.append('</ul>')
        else:
            chunks.append('<p>AI không nêu đoạn mã cụ thể.</p>')
        for title, key in (("Điểm khác biệt", "khac_biet"), ("Đề xuất cho giảng viên", "de_xuat")):
            chunks.append(f'<h3 style="font-size:15px;margin:14px 0 2px">{title}</h3>')
            values = review.get(key) or []
            if values:
                chunks.append('<ul style="margin-top:4px">' + ''.join(f'<li>{esc(item)}</li>' for item in values) + '</ul>')
            else:
                chunks.append('<p>Không có nội dung bổ sung.</p>')
        chunks.append('<p style="font-size:12px;color:#64748B;margin-top:20px">Nhận xét do AI tạo, giảng viên là người quyết định cuối cùng.</p>')
        chunks.append('</body></html>')
        self.ai_review_browser.setHtml(''.join(chunks))
        self.lbl_pair_verdict.setText(self._summary_assessment(pair))

    def _render_legacy_review(self, raw_text: str):
        content = html.escape(raw_text)
        self.ai_review_browser.setHtml(
            '<html><body style="font-family:Segoe UI,sans-serif;font-size:14px;line-height:1.65;color:#1E293B">'
            '<h3 style="font-size:15px">Nhận xét cũ (tiếng Anh/không cấu trúc)</h3>'
            f'<pre style="white-space:pre-wrap;font-family:Segoe UI,sans-serif">{content}</pre>'
            '<p style="font-size:12px;color:#64748B">Nhận xét do AI tạo, giảng viên là người quyết định cuối cùng.</p>'
            '</body></html>'
        )

    def _on_evidence_link_clicked(self, url: QUrl):
        target = url.toString()
        if not target.startswith("evidence:") or not self._selected_pair:
            return
        try:
            evidence_index = int(target.split(":", 1)[1])
            review = self._selected_pair.get("ai_review") or {}
            item = review.get("bang_chung", [])[evidence_index]
            range_a, range_b = item["dong_a"], item["dong_b"]
        except (ValueError, IndexError, KeyError, TypeError):
            return
        self.detail_tabs.setCurrentIndex(1)
        self._highlight_matching_lines(self._selected_pair)
        self._scroll_editor_to_line(self.txt_code_a, int(range_a[0]))
        self._scroll_editor_to_line(self.txt_code_b, int(range_b[0]))

    @staticmethod
    def _scroll_editor_to_line(editor: CodeEditor, line: int):
        block = editor.document().findBlockByLineNumber(max(0, line - 1))
        if block.isValid():
            cursor = QTextCursor(block)
            editor.setTextCursor(cursor)
            editor.ensureCursorVisible()

    def _update_ai_button_state(self):
        if not self._selected_pair:
            self.btn_run_ai_plag.setEnabled(False)
            self.btn_run_ai_plag.setToolTip("Chọn một cặp ở bảng bên trái")
        elif self._selected_pair["sv_a"].strip().upper() == self._selected_pair["sv_b"].strip().upper():
            self.btn_run_ai_plag.setText("Không thể thẩm định")
            self.btn_run_ai_plag.setEnabled(False)
            self.btn_run_ai_plag.setToolTip("Không thể thẩm định một MSSV với chính mình. Hãy quét lại đợt chấm.")
        elif float(self._selected_pair.get("sim", 0)) < 80:
            self.btn_run_ai_plag.setEnabled(False)
            self.btn_run_ai_plag.setToolTip("AI thẩm định áp dụng cho cặp có độ trùng lặp từ 80% trở lên.")
        elif self._ai_running:
            self.btn_run_ai_plag.setText("Đang thẩm định...")
            self.btn_run_ai_plag.setEnabled(False)
            self.btn_run_ai_plag.setToolTip("")
        elif not self._ai_quota_loaded:
            self.btn_run_ai_plag.setEnabled(False)
            self.btn_run_ai_plag.setToolTip("Đang kiểm tra hạn ngạch AI")
        elif self._ai_tokens_available == 0:
            self.btn_run_ai_plag.setEnabled(False)
            self.btn_run_ai_plag.setToolTip("Bạn đã hết hạn ngạch AI. Thử lại sau khi hạn ngạch được làm mới.")
        else:
            self.btn_run_ai_plag.setEnabled(True)
            self.btn_run_ai_plag.setToolTip("Thẩm định cặp mã nguồn đang chọn bằng AI")

    def _on_quota_loaded(self, result: Dict[str, Any]):
        self._ai_quota_loaded = True
        if result.get("success"):
            self._ai_tokens_available = max(0, int(result.get("remaining_tokens", 0) or 0))
        self._update_ai_button_state()

    def _run_ai_plagiarism_verification(self):
        pair = self._selected_pair
        if not pair:
            return
        if pair["sv_a"].strip().upper() == pair["sv_b"].strip().upper():
            logging.error("Refusing AI plagiarism review for a self-pair (%s).", pair["sv_a"])
            self.ai_review_browser.setHtml(self._empty_ai_html("Cặp có MSSV trùng nhau nên không thể thẩm định. Hãy bấm 'Bắt Đầu Quét Đạo Văn' để làm mới danh sách cặp."))
            self._update_ai_button_state()
            return
        if float(pair.get("sim", 0)) < 80:
            self._update_ai_button_state()
            return
        if self._ai_tokens_available == 0:
            self._update_ai_button_state()
            return
        cls_info = self.db.get_class_by_id(self.class_id) if self.class_id else None
        lang = cls_info.get("programming_language", "C") if cls_info else "C"
        self._ai_pair = (pair["sv_a"], pair["sv_b"])
        self._ai_running = True
        self.btn_run_ai_plag.setText("Đang thẩm định...")
        self._update_ai_button_state()
        self.ai_review_browser.setHtml(self._empty_ai_html("Đang thẩm định..."))
        self.ai_plag_worker = AiPlagiarismWorker(
            code_a=pair["code_a"], code_b=pair["code_b"],
            similarity=float(pair["sim"]), language=lang
        )
        self.ai_plag_worker.result_ready.connect(self._on_ai_plag_finished)
        self.ai_plag_worker.start()

    @staticmethod
    def _legacy_text(review: Dict[str, Any]) -> str:
        lines = [f"Kết luận: {review.get('ket_luan', '')}", f"Độ tin cậy AI: {review.get('do_tin_cay', 0)}%", "Bằng chứng:"]
        for item in review.get("bang_chung", []) or []:
            lines.append(f"- {item.get('mo_ta', '')} (SV A {item.get('dong_a')}, SV B {item.get('dong_b')})")
        lines.append("Điểm khác biệt:")
        lines.extend(f"- {item}" for item in review.get("khac_biet", []) or [])
        lines.append("Đề xuất cho giảng viên:")
        lines.extend(f"- {item}" for item in review.get("de_xuat", []) or [])
        return "\n".join(lines)

    def _on_ai_plag_finished(self, result: Dict[str, Any]):
        self._ai_running = False
        pair_key = getattr(self, "_ai_pair", None)
        pair = next((p for p in self.pairs_data if pair_key and (p["sv_a"], p["sv_b"]) == pair_key), None)
        if not pair:
            self._update_ai_button_state()
            return
        if result.get("success") and self._is_structured_review(result):
            review = {
                "ket_luan": result["ket_luan"],
                "do_tin_cay": float(result["do_tin_cay"]),
                "bang_chung": result.get("bang_chung", []),
                "khac_biet": result.get("khac_biet", []),
                "de_xuat": result.get("de_xuat", []),
            }
            pair["ai_review"] = review
            pair["ai_evidence_json"] = json.dumps(review, ensure_ascii=False)
            pair["ai_evidence_details"] = self._legacy_text(review)
            try:
                self.db.update_plagiarism_report_evidence(
                    self.class_id, pair["sv_a"], pair["sv_b"],
                    pair["ai_evidence_details"], pair["ai_evidence_json"]
                )
            except Exception:
                logging.exception("Không lưu được kết quả AI đạo văn vào SQLite")
            if self._selected_pair is pair:
                self._render_ai_review(review)
                self.btn_run_ai_plag.setText("Kích Hoạt AI Thẩm Định Chuyên Sâu")
                self.lbl_pair_verdict.setText(self._summary_assessment(pair))
        else:
            logging.error("AI plagiarism verification failed: %s", result.get("error_code", "UNKNOWN"))
            if self._selected_pair is pair:
                self.ai_review_browser.setHtml(self._empty_ai_html("Không lấy được nhận xét từ AI. Thử lại."))
                self.btn_run_ai_plag.setText("Thử Lại")
        self._update_ai_button_state()
        self._quota_worker = AiQuotaWorker(self)
        self._quota_worker.result_ready.connect(self._on_quota_loaded)
        self._quota_worker.start()

    def _highlight_matching_lines(self, pair: Dict[str, Any]):
        """Highlights AI line evidence and visual AST text matches, without changing scores."""
        source_a = pair.get("code_a", "")
        source_b = pair.get("code_b", "")
        lines_a = source_a.splitlines()
        lines_b = source_b.splitlines()
        ranges_a: List[tuple] = []
        ranges_b: List[tuple] = []
        review = pair.get("ai_review") or {}
        evidence = review.get("bang_chung") or []
        colors = ["#FEF3C7", "#DBEAFE", "#DCFCE7", "#FCE7F3", "#EDE9FE", "#FFEDD5"]
        for idx, item in enumerate(evidence):
            if isinstance(item, dict) and len(item.get("dong_a", [])) == 2 and len(item.get("dong_b", [])) == 2:
                ranges_a.append((item["dong_a"][0], item["dong_a"][1], colors[idx % len(colors)]))
                ranges_b.append((item["dong_b"][0], item["dong_b"][1], colors[idx % len(colors)]))
        matcher = difflib.SequenceMatcher(None, lines_a, lines_b, autojunk=False)
        ast_color_offset = len(ranges_a)
        for idx, block in enumerate(matcher.get_matching_blocks()):
            if block.size < 2:
                continue
            color = colors[(ast_color_offset + idx) % len(colors)]
            ranges_a.append((block.a + 1, block.a + block.size, color))
            ranges_b.append((block.b + 1, block.b + block.size, color))
        if evidence:
            legend = [f'<span style="background:{colors[i % len(colors)]};padding:2px 7px">Bằng chứng {i + 1}</span>' for i in range(len(evidence))]
            legend.append(f'<span style="background:{colors[(len(evidence)) % len(colors)]};padding:2px 7px">Đoạn giống theo đối soát cấu trúc</span>')
            self.lbl_highlight_legend.setText("Chú giải: " + "　".join(legend))
        else:
            self.lbl_highlight_legend.setText(
                "Chú giải: các đoạn giống theo đối soát cấu trúc được tô màu khác nhau."
            )
        self._apply_line_highlights(self.txt_code_a, ranges_a)
        self._apply_line_highlights(self.txt_code_b, ranges_b)

    @staticmethod
    def _apply_line_highlights(editor: CodeEditor, ranges: List[tuple]):
        selections = []
        for start, end, color in ranges:
            for line_number in range(max(1, int(start)), min(editor.blockCount(), int(end)) + 1):
                block = editor.document().findBlockByLineNumber(line_number - 1)
                if not block.isValid():
                    continue
                selection = QTextEdit.ExtraSelection()
                selection.format.setBackground(QColor(color))
                selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
                selection.cursor = QTextCursor(block)
                selections.append(selection)
        editor.setExtraSelections(selections)

    def _export_report(self):
        if not self.pairs_data:
            QMessageBox.warning(self, "Chưa Có Dữ Liệu", "Không có kết quả quét để xuất biên bản.")
            return
        export_path, _ = QFileDialog.getSaveFileName(
            self, "Xuất Biên Bản Đạo Văn", "bien_ban_doi_soat_dao_van.md",
            "Biên bản Markdown (*.md);;Văn bản UTF-8 (*.txt)"
        )
        if not export_path:
            return
        try:
            lines = ["# Biên bản đối soát đạo văn", ""]
            lines.append(f"Số cặp nghi vấn: {len(self.pairs_data)}")
            lines.append(f"Ngưỡng báo động: {self.spin_thresh.value()}%")
            lines.append("")
            for idx, pair in enumerate(self.pairs_data, 1):
                lines.extend([
                    f"## Cặp {idx}: {pair['sv_a']} và {pair['sv_b']}",
                    f"Câu: {pair.get('question') or DEFAULT_QUESTION_KEY}",
                    f"Trùng lặp: {pair['sim']:.1f}% ({self._similarity_label(pair['sim'])[0]})",
                    f"Đánh giá: {self._pair_assessment(pair)}",
                    "",
                ])
                review = pair.get("ai_review")
                legacy = pair.get("ai_legacy")
                if not review:
                    saved = self._saved_ai_data(pair)
                    review, legacy = saved.get("structured"), saved.get("legacy")
                if review:
                    lines.extend(["### Kết luận", str(review.get("ket_luan", "")),
                                  f"Độ tin cậy AI: {float(review.get('do_tin_cay', 0) or 0):.0f}%", "",
                                  "### Bằng chứng"])
                    for evidence in review.get("bang_chung", []) or []:
                        lines.append(
                            f"- {evidence.get('mo_ta', '')} — dòng {evidence.get('dong_a')} ({pair['sv_a']}) / "
                            f"{evidence.get('dong_b')} ({pair['sv_b']})"
                        )
                    lines.append("\n### Điểm khác biệt")
                    lines.extend(f"- {item}" for item in review.get("khac_biet", []) or [])
                    lines.append("\n### Đề xuất cho giảng viên")
                    lines.extend(f"- {item}" for item in review.get("de_xuat", []) or [])
                elif legacy:
                    lines.extend(["### Nhận xét cũ (tiếng Anh/không cấu trúc)", str(legacy)])
                else:
                    lines.extend(["### Nhận xét của AI", "Chưa có nhận xét AI cho cặp này."])
                lines.extend(["", "---", ""])
            lines.append("Nhận xét do AI tạo, giảng viên là người quyết định cuối cùng.")
            Path(export_path).write_text("\n".join(lines), encoding="utf-8")

            QMessageBox.information(
                self, "Xuất Báo Cáo Thành Công",
                f"Đã xuất biên bản đối chiếu đạo văn ra tệp:\n{export_path}"
            )
        except Exception as ex:
            QMessageBox.critical(self, "Lỗi Xuất File", f"Không thể xuất file biên bản:\n{str(ex)}")
