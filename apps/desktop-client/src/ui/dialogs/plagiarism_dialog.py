"""
AITA Desktop Client - Two-Stage Plagiarism Forensic Viewer (PyQt6)
UC-17: Two-Stage Plagiarism Detection (AST + AI Verification)
100% Real Submissions & Cross-Comparison - Zero Mock Data
"""

import sys
import csv
import itertools
from pathlib import Path
from typing import Optional, Dict, Any, List, Set

from PyQt6.QtCore import Qt, QRect, QSize, QThread, pyqtSignal
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QTextFormat, QTextCursor,
    QGuiApplication
)
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QPlainTextEdit, QTextEdit, QSplitter, QMessageBox, QComboBox, QSpinBox,
    QProgressBar, QApplication
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
    finished = pyqtSignal(dict)

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
        self.finished.emit(result)


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
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
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

        self.setWindowTitle("Hệ Thống Quét Đạo Văn 2 Vòng (Two-Stage Plagiarism Detection)")
        self.setStyleSheet(LIGHT_THEME_QSS)

        # Tính toán chiều cao và độ rộng cửa sổ theo vùng làm việc thực tế (tránh bị taskbar che)
        screen = QGuiApplication.primaryScreen()
        if screen:
            avail = screen.availableGeometry()
            target_w = min(1360, avail.width() - 40)
            target_h = min(840, avail.height() - 50)
            self.setMinimumSize(min(1080, target_w), min(640, target_h))
            self.resize(target_w, target_h)
            self.setMaximumHeight(avail.height() - 30)
            self.move(avail.x() + (avail.width() - target_w) // 2,
                      avail.y() + (avail.height() - target_h) // 2)
        else:
            self.setMinimumSize(1080, 640)
            self.resize(1280, 780)

        self._init_ui()
        self._load_classes_into_selector()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(12)

        # ----------------------------------------------------------------------
        # 0. Selection & Control Bar
        # ----------------------------------------------------------------------
        ctrl_card = QFrame(self)
        ctrl_card.setProperty("class", "Card")
        c_layout = QVBoxLayout(ctrl_card)
        c_layout.setContentsMargins(16, 12, 16, 12)
        c_layout.setSpacing(8)

        row_ctrl = QHBoxLayout()
        row_ctrl.setSpacing(12)

        lbl_select_class = QLabel("Chọn Đợt Chấm / Lớp Cần Quét:", ctrl_card)
        lbl_select_class.setStyleSheet("font-weight: 600; font-size: 13px; color: #1E293B;")
        row_ctrl.addWidget(lbl_select_class)

        self.combo_class = QComboBox(ctrl_card)
        self.combo_class.setMinimumWidth(320)
        self.combo_class.setFixedHeight(36)
        self.combo_class.view().setTextElideMode(Qt.TextElideMode.ElideRight)
        self.combo_class.currentIndexChanged.connect(self._on_combo_class_changed)
        row_ctrl.addWidget(self.combo_class)

        row_ctrl.addSpacing(12)
        lbl_thresh = QLabel("Ngưỡng Báo Động (%):", ctrl_card)
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
        self.btn_run_scan.setMinimumWidth(190)
        self.btn_run_scan.setFixedHeight(36)
        self.btn_run_scan.clicked.connect(self._run_real_plagiarism_scan)
        row_ctrl.addWidget(self.btn_run_scan)

        row_ctrl.addStretch(1)
        c_layout.addLayout(row_ctrl)

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
        # 1. Summary Status Banner Card (Tách rõ tiêu đề và dòng trạng thái)
        # ----------------------------------------------------------------------
        top_card = QFrame(self)
        top_card.setProperty("class", "Card")
        t_layout = QHBoxLayout(top_card)
        t_layout.setContentsMargins(18, 14, 18, 14)

        v_header = QVBoxLayout()
        v_header.setSpacing(4)
        self.lbl_header_title = QLabel("Hệ Thống Quét Đạo Văn 2 Vòng", top_card)
        self.lbl_header_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #0F172A;")

        self.lbl_status_subtitle = QLabel("Chưa có kết quả quét. Vui lòng chọn lớp và bấm 'Bắt Đầu Quét Đạo Văn'", top_card)
        self.lbl_status_subtitle.setStyleSheet("font-size: 13px; font-weight: 500; color: #64748B; line-height: 1.4;")
        v_header.addWidget(self.lbl_header_title)
        v_header.addWidget(self.lbl_status_subtitle)
        t_layout.addLayout(v_header)

        t_layout.addStretch(1)

        # Thẻ Vòng 1 và Vòng 2 có bo góc đồng nhất và tooltip
        self.lbl_v1 = QLabel("Vòng 1 (Nghi vấn): 0 cặp", top_card)
        self.lbl_v1.setStyleSheet("""
            color: #B45309;
            background-color: #FEF3C7;
            border: 1px solid #FDE68A;
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 13px;
            font-weight: 600;
        """)
        self.lbl_v1.setToolTip("Vòng 1 = so khớp cú pháp AST")
        t_layout.addWidget(self.lbl_v1)

        t_layout.addSpacing(8)

        self.lbl_v2 = QLabel("Vòng 2 (Báo động đỏ): 0 cặp", top_card)
        self.lbl_v2.setStyleSheet("""
            color: #B91C1C;
            background-color: #FEE2E2;
            border: 1px solid #FECACA;
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 13px;
            font-weight: 600;
        """)
        self.lbl_v2.setToolTip("Vòng 2 = đối soát ngữ nghĩa")
        t_layout.addWidget(self.lbl_v2)

        layout.addWidget(top_card)

        # ----------------------------------------------------------------------
        # 2. Main Splitter: Bảng Cặp Nghi Vấn (Trái) | Hai Khung Diff (Phải)
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

        lbl_table_head = QLabel("Danh Sách Cặp Bài Nghi Vấn:", left_widget)
        lbl_table_head.setStyleSheet("font-weight: 600; font-size: 13px; color: #1E293B;")
        l_layout.addWidget(lbl_table_head)

        self.table_pairs = QTableWidget(left_widget)
        self.table_pairs.setColumnCount(5)
        self.table_pairs.setHorizontalHeaderLabels(["SV A", "SV B", "% Trùng Lặp", "Câu", "Đánh Giá"])
        self.table_pairs.verticalHeader().setVisible(False)
        self.table_pairs.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_pairs.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table_pairs.setSortingEnabled(True)

        header = self.table_pairs.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table_pairs.setColumnWidth(0, 95)
        self.table_pairs.setColumnWidth(1, 95)
        self.table_pairs.setColumnWidth(2, 110)
        self.table_pairs.setColumnWidth(3, 70)

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

        # RIGHT WIDGET: Side-by-side Code Diff + Semantic Evidence
        right_widget = QWidget(main_splitter)
        r_layout = QVBoxLayout(right_widget)
        r_layout.setContentsMargins(0, 0, 0, 0)
        r_layout.setSpacing(10)

        diff_splitter = QSplitter(Qt.Orientation.Horizontal, right_widget)
        diff_splitter.setStyleSheet("""
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

        # Editor A
        w_a = QWidget(diff_splitter)
        la = QVBoxLayout(w_a)
        la.setContentsMargins(0, 0, 0, 0)
        la.setSpacing(6)
        self.lbl_sv_a = QLabel("Sinh viên A", w_a)
        self.lbl_sv_a.setStyleSheet("font-weight: 700; color: #1E40AF; font-size: 13px;")
        la.addWidget(self.lbl_sv_a)
        self.txt_code_a = CodeEditor(w_a)
        self.txt_code_a.setPlainText("Chọn một cặp bài nghi vấn để xem mã nguồn")
        la.addWidget(self.txt_code_a)
        diff_splitter.addWidget(w_a)

        # Editor B
        w_b = QWidget(diff_splitter)
        lb = QVBoxLayout(w_b)
        lb.setContentsMargins(0, 0, 0, 0)
        lb.setSpacing(6)
        self.lbl_sv_b = QLabel("Sinh viên B", w_b)
        self.lbl_sv_b.setStyleSheet("font-weight: 700; color: #B91C1C; font-size: 13px;")
        lb.addWidget(self.lbl_sv_b)
        self.txt_code_b = CodeEditor(w_b)
        self.txt_code_b.setPlainText("Chọn một cặp bài nghi vấn để xem mã nguồn")
        lb.addWidget(self.txt_code_b)
        diff_splitter.addWidget(w_b)

        # Cuộn đồng bộ giữa Editor A và Editor B
        self.txt_code_a.verticalScrollBar().valueChanged.connect(self._sync_scroll_a_to_b)
        self.txt_code_b.verticalScrollBar().valueChanged.connect(self._sync_scroll_b_to_a)
        self.txt_code_a.horizontalScrollBar().valueChanged.connect(self._sync_hscroll_a_to_b)
        self.txt_code_b.horizontalScrollBar().valueChanged.connect(self._sync_hscroll_b_to_a)

        r_layout.addWidget(diff_splitter, stretch=3)

        # Khung Phân Tích Bằng Chứng Ngữ Nghĩa (Tiêu đề sát đầu, có thanh cuộn)
        ai_card = QFrame(right_widget)
        ai_card.setProperty("class", "Card")
        ac_layout = QVBoxLayout(ai_card)
        ac_layout.setContentsMargins(14, 10, 14, 10)
        ac_layout.setSpacing(6)

        ai_head_row = QHBoxLayout()
        lbl_ai_t = QLabel("Phân Tích Bằng Chứng Ngữ Nghĩa (AI Vòng 2):", ai_card)
        lbl_ai_t.setStyleSheet("font-weight: 700; color: #0F172A; font-size: 13px;")
        ai_head_row.addWidget(lbl_ai_t)
        ai_head_row.addStretch(1)

        self.btn_run_ai_plag = QPushButton("Kích Hoạt AI Thẩm Định Chuyên Sâu", ai_card)
        self.btn_run_ai_plag.setProperty("class", "AIBtn")
        self.btn_run_ai_plag.setFixedHeight(28)
        self.btn_run_ai_plag.setStyleSheet("""
            QPushButton {
                background-color: #EFF6FF;
                color: #2563EB;
                border: 1px solid #BFDBFE;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
                padding: 0 10px;
            }
            QPushButton:hover {
                background-color: #DBEAFE;
            }
        """)
        self.btn_run_ai_plag.clicked.connect(self._run_ai_plagiarism_verification)
        ai_head_row.addWidget(self.btn_run_ai_plag)
        ac_layout.addLayout(ai_head_row)

        self.txt_ai_evidence = QTextEdit(ai_card)
        self.txt_ai_evidence.setReadOnly(True)
        self.txt_ai_evidence.setMinimumHeight(75)
        self.txt_ai_evidence.setText("Chọn một cặp bài nghi vấn ở bảng bên trái để xem đối soát mã nguồn và kết luận.")
        self.txt_ai_evidence.setStyleSheet("""
            QTextEdit {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                font-size: 13px;
                line-height: 1.45;
                color: #334155;
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        ac_layout.addWidget(self.txt_ai_evidence)

        r_layout.addWidget(ai_card, stretch=1)
        main_splitter.addWidget(right_widget)

        main_splitter.setSizes([420, 880])
        layout.addWidget(main_splitter, stretch=1)

        # ----------------------------------------------------------------------
        # 3. Footer Actions (Cách đáy tối thiểu 16px, lề trái phải bằng nhau)
        # ----------------------------------------------------------------------
        footer = QHBoxLayout()
        footer.setContentsMargins(0, 8, 0, 0)

        self.btn_export_report = QPushButton("Xuất Biên Bản Đạo Văn", self)
        self.btn_export_report.setProperty("class", "PrimaryBtn")
        self.btn_export_report.setFixedHeight(40)
        self.btn_export_report.setEnabled(False)
        self.btn_export_report.clicked.connect(self._export_report)
        footer.addWidget(self.btn_export_report)

        footer.addStretch(1)

        btn_close = QPushButton("Đóng", self)
        btn_close.setProperty("class", "SecondaryBtn")
        btn_close.setFixedHeight(40)
        btn_close.setMinimumWidth(100)
        btn_close.clicked.connect(self.accept)
        footer.addWidget(btn_close)

        layout.addLayout(footer)

    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        if hasattr(self, 'lbl_table_empty') and hasattr(self, 'table_pairs'):
            self.lbl_table_empty.setGeometry(self.table_pairs.rect())
            self.lbl_table_empty.setVisible(self.table_pairs.rowCount() == 0)

    # ==========================================================================
    # CÁC HÀM XỬ LÝ CUỘN ĐỒNG BỘ
    # ==========================================================================
    def _sync_scroll_a_to_b(self, val):
        if not self._syncing_scroll:
            self._syncing_scroll = True
            self.txt_code_b.verticalScrollBar().setValue(val)
            self._syncing_scroll = False

    def _sync_scroll_b_to_a(self, val):
        if not self._syncing_scroll:
            self._syncing_scroll = True
            self.txt_code_a.verticalScrollBar().setValue(val)
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
        subs = self.db.get_submissions_by_class(self.class_id)
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

        # Vòng 1: Chuẩn hoá token + Winnowing theo từng câu, chạy 100% offline
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
                self.db.save_plagiarism_report(
                    self.class_id, m["sv_a"], m["sv_b"], m["sim"],
                    question_key=", ".join(m["questions"])
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
            "code_b": m["code_b"]
        } for m in raw_matches]
        # Vòng 2 (AI) chỉ nhận các cặp đủ điều kiện tối thiểu 80% theo hợp đồng API
        v2_red_alert = sum(1 for p in pairs_found if p["sim"] >= 80.0)

        self.progress_bar.setValue(100)
        QApplication.processEvents()
        self._finish_scan()

        self.pairs_data = pairs_found
        scope = f"{len(questions_checked)} câu" if questions_checked else "1 câu"
        filter_note = " Đã loại mã khung sườn dùng chung của lớp." if report.get("boilerplate_filtered") else ""
        if pairs_found:
            self.lbl_status_subtitle.setText(
                f"Đã đối soát {total_pairs_checked} lượt so sánh theo {scope}. "
                f"Phát hiện {len(pairs_found)} cặp vượt ngưỡng {int(red_threshold)}%.{filter_note}"
            )
            self.lbl_status_subtitle.setStyleSheet("font-size: 13px; font-weight: 500; color: #DC2626; line-height: 1.4;")
        else:
            self.lbl_status_subtitle.setText(
                f"Đã đối soát {total_pairs_checked} lượt so sánh theo {scope}. "
                f"Không có cặp bài nào vượt ngưỡng {int(red_threshold)}%.{filter_note}"
            )
            self.lbl_status_subtitle.setStyleSheet("font-size: 13px; font-weight: 500; color: #0284C7; line-height: 1.4;")

        self.lbl_v1.setText(f"Vòng 1 (Offline theo từng câu): {len(pairs_found)} cặp nghi vấn")
        self.lbl_v2.setText(f"Vòng 2 (Đủ điều kiện AI ≥80%): {v2_red_alert} cặp")

        # Cập nhật bảng dữ liệu
        self.table_pairs.setSortingEnabled(False)
        self.table_pairs.setRowCount(len(pairs_found))

        for r, p in enumerate(pairs_found):
            item_a = QTableWidgetItem(p["sv_a"])
            item_b = QTableWidgetItem(p["sv_b"])
            # Cột % căn giữa và hỗ trợ sắp xếp số
            item_sim = NumericTableWidgetItem(f"{p['sim']:.1f}%", p["sim"])
            item_q = QTableWidgetItem(", ".join(p["questions"]))
            item_v = QTableWidgetItem(p["verdict"])

            item_a.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_b.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_sim.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_q.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_v.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

            item_sim.setForeground(QColor("#DC2626"))
            item_v.setForeground(QColor("#DC2626"))
            item_q.setForeground(QColor("#B45309"))
            item_v.setToolTip(self._metrics_tooltip(p))

            self.table_pairs.setItem(r, 0, item_a)
            self.table_pairs.setItem(r, 1, item_b)
            self.table_pairs.setItem(r, 2, item_sim)
            self.table_pairs.setItem(r, 3, item_q)
            self.table_pairs.setItem(r, 4, item_v)

        self.table_pairs.setSortingEnabled(True)
        self.table_pairs.sortItems(2, Qt.SortOrder.DescendingOrder)

        self._update_empty_state_visibility()
        self.btn_export_report.setEnabled(len(pairs_found) > 0)

        if pairs_found:
            self.table_pairs.selectRow(0)
            self._load_diff(0)
        else:
            self.lbl_sv_a.setText("Sinh viên A")
            self.lbl_sv_b.setText("Sinh viên B")
            self.txt_code_a.setPlainText(f"// Không phát hiện cặp bài nào có độ trùng lặp vượt ngưỡng {int(red_threshold)}%.")
            self.txt_code_b.setPlainText("// Toàn bộ sinh viên làm bài độc lập trong ngưỡng an toàn.")
            self.txt_ai_evidence.setText(f"Hệ thống đã đối soát toàn bộ {total_pairs_checked} cặp mã nguồn. Không có cặp bài nào đạt độ trùng lặp từ {int(red_threshold)}% trở lên.")
            self.lbl_table_empty.setText(f"Không có cặp bài nào đạt độ trùng lặp từ {int(red_threshold)}% trở lên.")
            self.lbl_table_empty.show()

    def _finish_scan(self):
        self.btn_run_scan.setText("Bắt Đầu Quét Đạo Văn")
        self.btn_run_scan.setEnabled(True)
        self.progress_bar.hide()

    def _show_empty_state(self, message: str):
        self.lbl_status_subtitle.setText(message)
        self.lbl_status_subtitle.setStyleSheet("font-size: 13px; font-weight: 500; color: #DC2626; line-height: 1.4;")
        self.lbl_v1.setText("Vòng 1 (Nghi vấn): 0 cặp")
        self.lbl_v2.setText("Vòng 2 (Báo động đỏ): 0 cặp")
        self.table_pairs.setRowCount(0)
        self.lbl_sv_a.setText("Sinh viên A")
        self.lbl_sv_b.setText("Sinh viên B")
        self.txt_code_a.setPlainText("Chọn một cặp bài nghi vấn để xem mã nguồn")
        self.txt_code_b.setPlainText("Chọn một cặp bài nghi vấn để xem mã nguồn")
        self.txt_ai_evidence.setText(message)
        self.btn_export_report.setEnabled(False)
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

        # 9. Tiêu đề hiển thị chuẩn "Sinh viên A: <MSSV>" và "Sinh viên B: <MSSV>"
        self.lbl_sv_a.setText(f"Sinh viên A: {pair['sv_a']}")
        self.lbl_sv_b.setText(f"Sinh viên B: {pair['sv_b']}")

        self.txt_code_a.setPlainText(pair["code_a"])
        self.txt_code_b.setPlainText(pair["code_b"])

        # Tô nền các dòng giống nhau ở cả 2 bên
        self._highlight_matching_lines(pair["code_a"], pair["code_b"])

        sim = pair["sim"]
        questions = pair.get("questions") or []
        question_label = ", ".join(questions) if questions else (pair.get("question") or DEFAULT_QUESTION_KEY)
        metrics_line = (
            f"Chỉ số: Jaccard {pair.get('jaccard', sim):.1f}% · "
            f"Độ bao phủ (containment) {pair.get('containment', 0.0):.1f}%."
        )
        if sim >= float(self.spin_thresh.value()):
            evidence = (
                f"Phát hiện mức độ trùng lặp cao ({sim:.1f}%) giữa {pair['sv_a']} và {pair['sv_b']} ở câu {question_label}.\n"
                f"{metrics_line}\n"
                f"Các hàm chính, thứ tự khai báo biến và cấu trúc vòng lặp có độ tương đồng vượt ngưỡng cho phép.\n"
                f"Bấm nút 'Kích Hoạt AI Thẩm Định Chuyên Sâu' phía trên để gọi AI Gateway thẩm định cấu trúc AST và bằng chứng cụ thể."
            )
        else:
            evidence = (
                f"Mức độ tương đồng {sim:.1f}% giữa {pair['sv_a']} và {pair['sv_b']} ở câu {question_label}.\n"
                f"{metrics_line}\n"
                f"Nghi vấn sử dụng chung mẫu khung giải thuật cơ bản của đề bài.\n"
                f"Kiến nghị: Xem xét đánh giá thêm để loại trừ việc trùng template mẫu."
            )
        self.txt_ai_evidence.setText(evidence)

    def _run_ai_plagiarism_verification(self):
        """Calls Central Backend AI Gateway for Stage 2 deep plagiarism forensics."""
        row = self.table_pairs.currentRow()
        if row < 0 or not self.pairs_data:
            QMessageBox.warning(self, "Chưa Chọn Cặp Bài", "Vui lòng chọn một cặp bài nghi vấn trong bảng trước khi thẩm định!")
            return

        item_a = self.table_pairs.item(row, 0)
        item_b = self.table_pairs.item(row, 1)
        if not item_a or not item_b:
            return

        sv_a, sv_b = item_a.text(), item_b.text()
        current_pair = next((p for p in self.pairs_data if (p["sv_a"] == sv_a and p["sv_b"] == sv_b) or (p["sv_a"] == sv_b and p["sv_b"] == sv_a)), None)
        if not current_pair:
            return

        cls_info = self.db.get_class_by_id(self.class_id) if self.class_id else None
        lang = cls_info.get("programming_language", "C") if cls_info else "C"

        self._ai_pair = (sv_a, sv_b)
        self.btn_run_ai_plag.setEnabled(False)
        self.btn_run_ai_plag.setText("Đang kết nối AI Gateway...")
        self.txt_ai_evidence.setText(f"// Đang gửi mã nguồn cặp bài ({sv_a} vs {sv_b}) lên Central Backend để AI đối soát chuyên sâu...")

        self.ai_plag_worker = AiPlagiarismWorker(
            code_a=current_pair["code_a"],
            code_b=current_pair["code_b"],
            similarity=float(current_pair["sim"]),
            language=lang
        )
        self.ai_plag_worker.finished.connect(self._on_ai_plag_finished)
        self.ai_plag_worker.start()

    def _on_ai_plag_finished(self, result: Dict[str, Any]):
        self.btn_run_ai_plag.setEnabled(True)
        self.btn_run_ai_plag.setText("Kích Hoạt AI Thẩm Định Chuyên Sâu")

        if result.get("success"):
            is_plag = result.get("is_plagiarized", False)
            conf = result.get("confidence_percentage", 0.0)
            evidence = result.get("evidence_summary", "")
            clones = result.get("cloned_segments", [])
            tokens = result.get("tokens_consumed", 0)

            verdict_str = "KẾT LUẬN: CÓ DẤU HIỆU ĐẠO VĂN RÕ RỆT" if is_plag else "KẾT LUẬN: KHÔNG ĐỦ BẰNG CHỨNG XÁC ĐỊNH ĐẠO VĂN (Trùng Boilerplate/Mẫu)"
            
            detail_lines = []
            for idx, c in enumerate(clones, 1):
                detail_lines.append(f"  • Đoạn {idx}: SV A ({c.get('student_a_lines')}) ⟷ SV B ({c.get('student_b_lines')}) - Kỹ thuật: {c.get('technique')}")

            clone_str = "\n".join(detail_lines) if detail_lines else "  • Không có đoạn sao chép nguyên khối."

            report_text = f"""[KẾT QUẢ THẨM ĐỊNH AI VÒNG 2 - CENTRAL AI GATEWAY]:
• {verdict_str}
• Độ tin cậy thuật toán AI: {conf:.1f}%

1. Bằng chứng phân tích cấu trúc:
   {evidence}

2. Chi tiết các đoạn mã sao chép nghi vấn:
{clone_str}

(Dữ liệu thực tế từ Neon DB & AI Gateway - Tiêu thụ: {tokens} tokens)
"""
            self.txt_ai_evidence.setText(report_text)

            # Lưu bằng chứng Vòng 2 vào báo cáo đạo văn cục bộ
            try:
                pair = getattr(self, "_ai_pair", None)
                if pair and self.class_id:
                    self.db.update_plagiarism_report_evidence(
                        self.class_id, pair[0], pair[1], report_text.strip()
                    )
            except Exception:
                pass

            QMessageBox.information(
                self,
                "AI Thẩm Định Hoàn Tất",
                f"Đã hoàn thành đối soát AI vòng 2!\nĐộ tin cậy: {conf:.1f}%\n(Hạn ngạch tiêu thụ: {tokens} tokens)"
            )
        else:
            msg = result.get("message", "Máy chủ AI không thể xử lý đối soát.")
            err_code = result.get("error_code", "")
            self.txt_ai_evidence.setText(f"// Lỗi AI Gateway: {msg}\n// Mã lỗi: {err_code}")
            QMessageBox.warning(
                self,
                "Lỗi Thẩm Định AI",
                f"Không thể thẩm định qua AI Gateway:\n{msg}\n\nMã lỗi: {err_code}"
            )

    def _highlight_matching_lines(self, code_a: str, code_b: str):
        """Highlights identical non-empty logic lines in soft yellow on both sides."""
        lines_a = [l.strip() for l in code_a.splitlines()]
        lines_b = [l.strip() for l in code_b.splitlines()]

        # Lọc các dòng code có ý nghĩa (tránh dòng trống hoặc dấu ngoặc đơn độc)
        common_lines: Set[str] = set()
        trivial = {"", "{", "}", ";", "return 0;", "int main()", "int main(void)", "#include <stdio.h>"}
        for la in lines_a:
            if la and len(la) >= 4 and la not in trivial:
                if la in lines_b:
                    common_lines.add(la)

        self._apply_editor_highlights(self.txt_code_a, common_lines)
        self._apply_editor_highlights(self.txt_code_b, common_lines)

    def _apply_editor_highlights(self, editor: CodeEditor, target_lines: Set[str]):
        extra_selections = []
        highlight_color = QColor("#FEF3C7")  # Vàng cảnh báo trùng lặp dịu mắt

        block = editor.document().firstBlock()
        while block.isValid():
            text = block.text().strip()
            if text in target_lines:
                sel = QTextEdit.ExtraSelection()
                sel.format.setBackground(highlight_color)
                sel.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
                sel.cursor = QTextCursor(block)
                extra_selections.append(sel)
            block = block.next()

        editor.setExtraSelections(extra_selections)

    def _export_report(self):
        if not self.pairs_data:
            QMessageBox.warning(self, "Chưa Có Dữ Liệu", "Không có cặp bài nghi vấn nào để xuất biên bản!")
            return

        export_path = Path(__file__).resolve().parent.parent.parent.parent / "plagiarism_report.csv"
        try:
            with open(export_path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Sinh viên A", "Sinh viên B", "Câu trùng", "% Trùng lặp",
                    "Jaccard (%)", "Bao phủ (%)", "Kết luận"
                ])
                for p in self.pairs_data:
                    writer.writerow([
                        p["sv_a"],
                        p["sv_b"],
                        ", ".join(p.get("questions") or []),
                        f"{p['sim']:.1f}%",
                        f"{p.get('jaccard', p['sim']):.1f}%",
                        f"{p.get('containment', 0.0):.1f}%",
                        p["verdict"]
                    ])

            QMessageBox.information(
                self, "Xuất Báo Cáo Thành Công",
                f"Đã xuất biên bản đối chiếu đạo văn thành công ra tệp:\n{export_path}"
            )
        except Exception as ex:
            QMessageBox.critical(self, "Lỗi Xuất File", f"Không thể xuất file biên bản:\n{str(ex)}")
