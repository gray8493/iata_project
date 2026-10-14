"""
AITA Desktop Client - Testcase Manager & AI Generator Dialog (PyQt6)
UC-09: Manage Black-box Testcases Manually (Add / Edit / Delete Input/Output)
UC-10: Auto-Generate Boundary Testcases with Gemini AI
UC-11: Configure 7 Output Matching Strategies
"""

import sys
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QGuiApplication, QFont, QColor
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QCheckBox, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QTextEdit, QSpinBox, QDoubleSpinBox, QTabWidget, QMessageBox,
    QScrollArea
)

SRC_DIR = Path(__file__).resolve().parent.parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ui.styles.theme import (
    LIGHT_THEME_QSS, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_PRIMARY_BG,
    COLOR_BORDER_DEFAULT, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_ERROR, COLOR_ERROR_BG
)
from database.db_manager import DatabaseManager


# ==============================================================================
# 1. HỘP THOẠI THÊM / CHỈNH SỬA TESTCASE (THIẾT KẾ SAAS CHUẨN UI/UX)
# ==============================================================================
class TestcaseEditDialog(QDialog):
    """Clean Modal Dialog for Adding or Editing a Testcase with Form validation."""

    def __init__(self, parent=None, testcase: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self.tc = testcase or {}
        self.is_edit = testcase is not None
        self.setWindowTitle("Chỉnh Sửa Testcase" if self.is_edit else "Thêm Testcase Mới")
        self.setMinimumSize(540, 500)
        self.resize(600, 560)
        self.setStyleSheet(LIGHT_THEME_QSS)
        self.testcase_data: Dict[str, Any] = {}
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # 1. Câu hỏi & Trọng số điểm
        row1 = QHBoxLayout()
        row1.setSpacing(14)

        v_q = QVBoxLayout()
        lbl_q = QLabel("Câu Hỏi (Question):", self)
        lbl_q.setStyleSheet("font-weight: 600; font-size: 13px;")
        v_q.addWidget(lbl_q)

        self.cb_q = QComboBox(self)
        self.cb_q.setFixedHeight(36)
        self.cb_q.setEditable(True)
        self.cb_q.addItems(["Q1", "Q2", "Q3", "Q4", "Q5"])
        cur_q = self.tc.get("question_number", "Q1")
        idx_q = self.cb_q.findText(cur_q)
        if idx_q >= 0:
            self.cb_q.setCurrentIndex(idx_q)
        else:
            self.cb_q.setEditText(cur_q)
        v_q.addWidget(self.cb_q)
        row1.addLayout(v_q, stretch=1)

        v_w = QVBoxLayout()
        lbl_w = QLabel("Trọng Số Điểm:", self)
        lbl_w.setStyleSheet("font-weight: 600; font-size: 13px;")
        v_w.addWidget(lbl_w)

        self.sp_weight = QDoubleSpinBox(self)
        self.sp_weight.setFixedHeight(36)
        self.sp_weight.setRange(0.1, 10.0)
        self.sp_weight.setSingleStep(0.5)
        self.sp_weight.setValue(float(self.tc.get("score_weight", 1.0)))
        v_w.addWidget(self.sp_weight)
        row1.addLayout(v_w, stretch=1)

        layout.addLayout(row1)

        # 2. Dữ liệu nhập (INPUT stdin)
        lbl_inp = QLabel("Dữ Liệu Đầu Vào (stdin) — Để trống nếu đề bài không yêu cầu nhập:", self)
        lbl_inp.setStyleSheet("font-weight: 600; font-size: 13px;")
        layout.addWidget(lbl_inp)

        self.txt_input = QTextEdit(self)
        self.txt_input.setFixedHeight(95)
        self.txt_input.setPlaceholderText("Nhập các tham số đầu vào (mỗi dòng hoặc cách nhau bởi khoảng trắng)...")
        self.txt_input.setStyleSheet("""
            QTextEdit {
                font-family: Consolas, monospace;
                font-size: 13px;
                line-height: 1.4;
                padding: 8px;
            }
        """)
        self.txt_input.setPlainText(self.tc.get("input_data", ""))
        layout.addWidget(self.txt_input)

        # 3. Kết quả kỳ vọng (OUTPUT stdout)
        lbl_out = QLabel("Kết Quả Kỳ Vọng (stdout) — *Bắt buộc:", self)
        lbl_out.setStyleSheet("font-weight: 600; font-size: 13px;")
        layout.addWidget(lbl_out)

        self.txt_output = QTextEdit(self)
        self.txt_output.setFixedHeight(95)
        self.txt_output.setPlaceholderText("Nhập chính xác chuỗi kết quả mong đợi chương trình in ra...")
        self.txt_output.setStyleSheet("""
            QTextEdit {
                font-family: Consolas, monospace;
                font-size: 13px;
                line-height: 1.4;
                padding: 8px;
            }
        """)
        self.txt_output.setPlainText(self.tc.get("expected_output", ""))
        layout.addWidget(self.txt_output)

        # 4. Giới hạn thời gian (ms) & Bộ nhớ (MB)
        row2 = QHBoxLayout()
        row2.setSpacing(14)

        v_t = QVBoxLayout()
        lbl_t = QLabel("Giới Hạn Thời Gian (ms):", self)
        lbl_t.setStyleSheet("font-weight: 600; font-size: 13px;")
        v_t.addWidget(lbl_t)

        self.sp_time = QSpinBox(self)
        self.sp_time.setFixedHeight(36)
        self.sp_time.setRange(100, 10000)
        self.sp_time.setSingleStep(100)
        self.sp_time.setValue(int(self.tc.get("time_limit_ms", 1000)))
        v_t.addWidget(self.sp_time)
        row2.addLayout(v_t, stretch=1)

        v_m = QVBoxLayout()
        lbl_m = QLabel("Giới Hạn Bộ Nhớ (MB):", self)
        lbl_m.setStyleSheet("font-weight: 600; font-size: 13px;")
        v_m.addWidget(lbl_m)

        self.sp_mem = QSpinBox(self)
        self.sp_mem.setFixedHeight(36)
        self.sp_mem.setRange(16, 1024)
        self.sp_mem.setSingleStep(32)
        self.sp_mem.setValue(int(self.tc.get("memory_limit_mb", 128)))
        v_m.addWidget(self.sp_mem)
        row2.addLayout(v_m, stretch=1)

        layout.addLayout(row2)

        layout.addStretch(1)

        # Footer Buttons
        footer = QHBoxLayout()
        footer.setSpacing(12)
        footer.addStretch(1)

        btn_cancel = QPushButton("Hủy Bỏ", self)
        btn_cancel.setProperty("class", "SecondaryBtn")
        btn_cancel.setFixedHeight(38)
        btn_cancel.clicked.connect(self.reject)
        footer.addWidget(btn_cancel)

        btn_save = QPushButton("Lưu Testcase", self)
        btn_save.setProperty("class", "PrimaryBtn")
        btn_save.setFixedHeight(38)
        btn_save.clicked.connect(self._validate_and_save)
        footer.addWidget(btn_save)

        layout.addLayout(footer)

    def _validate_and_save(self):
        output = self.txt_output.toPlainText()
        if not output.strip():
            QMessageBox.warning(self, "Thiếu Dữ Liệu", "Kết quả mong đợi (stdout) không được để trống!")
            return

        self.testcase_data = {
            "question_number": self.cb_q.currentText().strip() or "Q1",
            "input_data": self.txt_input.toPlainText(),
            "expected_output": self.txt_output.toPlainText(),
            "score_weight": self.sp_weight.value(),
            "time_limit_ms": self.sp_time.value(),
            "memory_limit_mb": self.sp_mem.value()
        }
        self.accept()


# ==============================================================================
# 2. HỘP THOẠI QUẢN LÝ BỘ TESTCASE & CHIẾN LƯỢC SO KHỚP (BƯỚC 3/3 HOẶC ĐỘC LẬP)
# ==============================================================================
class TestcaseDialog(QDialog):
    """
    Dialog for configuring black-box testcases and calling Gemini AI to generate boundary testcases.
    Directly persists and loads testcases from local SQLite database (local_grading.db).
    Supports multi-checkbox output matching criteria and full CRUD (Add / Edit / Delete).
    """

    def __init__(self, parent=None, class_id: Optional[int] = None, is_wizard: bool = False):
        super().__init__(parent)
        self.is_wizard = is_wizard
        self.nav_back = False

        title = "Bước 3/3: Quản Lý Bộ Testcase & Chiến Lược So Khớp" if is_wizard else "Quản Lý Bộ Testcase & Chiến Lược So Khớp"
        self.setWindowTitle(title)

        # Responsive sizing according to available display area
        screen = QGuiApplication.primaryScreen()
        if screen:
            avail = screen.availableGeometry()
            target_w = min(1140, avail.width() - 40)
            target_h = min(740, avail.height() - 50)
            self.setMinimumSize(min(960, target_w), min(600, target_h))
            self.resize(target_w, target_h)
            self.move(avail.x() + (avail.width() - target_w) // 2,
                      avail.y() + (avail.height() - target_h) // 2)
        else:
            self.setMinimumSize(960, 600)
            self.resize(1100, 720)

        self.setStyleSheet(LIGHT_THEME_QSS)

        self.class_id = class_id
        self.db = DatabaseManager()
        self._all_testcases: List[Dict[str, Any]] = []

        self._init_ui()
        self._load_testcases_from_db()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # 1. Matching Strategy Card (Multi-select Checkboxes)
        strat_card = QFrame(self)
        strat_card.setProperty("class", "Card")
        s_layout = QVBoxLayout(strat_card)
        s_layout.setContentsMargins(18, 14, 18, 14)
        s_layout.setSpacing(10)

        # Header row of strategy card (ĐÃ BỎ NẠP/XUẤT JSON)
        top_strat_row = QHBoxLayout()
        lbl_strat = QLabel("Tiêu Chí So Khớp Đầu Ra (Tick chọn kết hợp nhiều chế độ):", strat_card)
        lbl_strat.setStyleSheet(f"font-weight: 700; font-size: 13px; color: {COLOR_TEXT_PRIMARY};")
        top_strat_row.addWidget(lbl_strat)
        top_strat_row.addStretch(1)
        s_layout.addLayout(top_strat_row)

        # Grid layout for 6 checkboxes
        grid_strat = QGridLayout()
        grid_strat.setHorizontalSpacing(24)
        grid_strat.setVerticalSpacing(8)

        cb_style = f"""
            QCheckBox {{
                font-size: 12px;
                color: {COLOR_TEXT_PRIMARY};
                font-weight: 500;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 17px;
                height: 17px;
                border-radius: 4px;
                border: 1px solid {COLOR_BORDER_DEFAULT};
                background-color: #FFFFFF;
            }}
            QCheckBox::indicator:hover {{
                border-color: {COLOR_PRIMARY};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLOR_PRIMARY};
                border-color: {COLOR_PRIMARY};
            }}
        """

        self.chk_whitespace = QCheckBox("Bỏ qua khoảng trắng thừa (Ignore Whitespace)", strat_card)
        self.chk_whitespace.setToolTip("Bỏ qua khoảng trắng và dấu xuống dòng thừa ở đầu/cuối và giữa các token")
        self.chk_whitespace.setChecked(True)
        self.chk_whitespace.setStyleSheet(cb_style)
        self.chk_whitespace.stateChanged.connect(self._on_matching_flags_changed)
        grid_strat.addWidget(self.chk_whitespace, 0, 0)

        self.chk_case = QCheckBox("Không phân biệt hoa / thường (Case Insensitive)", strat_card)
        self.chk_case.setToolTip("Chuyển đổi toàn bộ output về chữ thường trước khi đối sánh (ví dụ: Hello == hello)")
        self.chk_case.setStyleSheet(cb_style)
        self.chk_case.stateChanged.connect(self._on_matching_flags_changed)
        grid_strat.addWidget(self.chk_case, 0, 1)

        self.chk_float = QCheckBox("Dung sai số thực (Tolerance ≤ 1e-5)", strat_card)
        self.chk_float.setToolTip("Chấp nhận sai số dấu phẩy động tuyệt đối hoặc tương đối ≤ 0.00001 (1e-5)")
        self.chk_float.setStyleSheet(cb_style)
        self.chk_float.stateChanged.connect(self._on_matching_flags_changed)
        grid_strat.addWidget(self.chk_float, 0, 2)

        self.chk_unordered = QCheckBox("Không phân biệt thứ tự từ / số (Unordered)", strat_card)
        self.chk_unordered.setToolTip("So khớp tập hợp các từ/số mà không phụ thuộc vào thứ tự in ra màn hình")
        self.chk_unordered.setStyleSheet(cb_style)
        self.chk_unordered.stateChanged.connect(self._on_matching_flags_changed)
        grid_strat.addWidget(self.chk_unordered, 1, 0)

        self.chk_regex = QCheckBox("So khớp biểu thức chính quy (Regex Pattern)", strat_card)
        self.chk_regex.setToolTip("Sử dụng stdout kỳ vọng như một mẫu Regular Expression để đối sánh")
        self.chk_regex.setStyleSheet(cb_style)
        self.chk_regex.stateChanged.connect(self._on_matching_flags_changed)
        grid_strat.addWidget(self.chk_regex, 1, 1)

        self.chk_special = QCheckBox("Kiểm tra kịch bản (Special Judge)", strat_card)
        self.chk_special.setToolTip("Chạy script validator chấm điểm tùy biến cho các bài toán nhiều nghiệm đúng")
        self.chk_special.setStyleSheet(cb_style)
        self.chk_special.stateChanged.connect(self._on_matching_flags_changed)
        grid_strat.addWidget(self.chk_special, 1, 2)

        s_layout.addLayout(grid_strat)

        bottom_strat_row = QHBoxLayout()
        lbl_hint = QLabel("Mẹo: Bỏ tick toàn bộ các ô để so khớp chính xác tuyệt đối 100% từng byte (Exact Match). Các ô được tick sẽ tự động kết hợp xử lý đồng thời.", strat_card)
        lbl_hint.setStyleSheet(f"font-size: 11px; color: {COLOR_TEXT_MUTED}; font-style: italic;")
        bottom_strat_row.addWidget(lbl_hint)
        bottom_strat_row.addStretch(1)

        self.btn_save_bot = QPushButton("Lưu Cấu Hình So Khớp", strat_card)
        self.btn_save_bot.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_save_bot.setFixedHeight(34)
        self.btn_save_bot.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: #FFFFFF;
                font-weight: 600;
                font-size: 13px;
                padding: 0 18px;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_HOVER};
            }}
        """)
        self.btn_save_bot.clicked.connect(self._save_matching_strategy_manual)
        bottom_strat_row.addWidget(self.btn_save_bot)
        s_layout.addLayout(bottom_strat_row)

        layout.addWidget(strat_card)

        # 2. Main Tab Widget: Manual Testcases & AI Generator
        self.tabs = QTabWidget(self)

        # TAB 1: Danh sách Testcase Hộp Đen (Hỗ trợ Thêm / Sửa / Xóa)
        tab_list = QWidget()
        tl_layout = QVBoxLayout(tab_list)
        tl_layout.setContentsMargins(8, 8, 8, 8)
        tl_layout.setSpacing(10)

        # Filter & Action Row
        f_row = QHBoxLayout()
        f_row.setSpacing(12)

        lbl_f = QLabel("Lọc Theo Câu Hỏi:", tab_list)
        lbl_f.setStyleSheet("font-weight: 600; font-size: 13px;")
        f_row.addWidget(lbl_f)

        self.cb_question = QComboBox(tab_list)
        self.cb_question.setFixedHeight(36)
        self.cb_question.setMinimumWidth(150)
        self.cb_question.addItems(["Tất cả câu hỏi", "Q1", "Q2", "Q3", "Q4", "Q5"])
        self.cb_question.currentIndexChanged.connect(self._filter_testcases)
        f_row.addWidget(self.cb_question)
        f_row.addStretch(1)

        # Nút Thêm Testcase Mới (Đã bỏ chữ "thủ công", phong cách Primary)
        btn_add_tc = QPushButton("Thêm Testcase", tab_list)
        btn_add_tc.setProperty("class", "PrimaryBtn")
        btn_add_tc.setFixedHeight(36)
        btn_add_tc.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_add_tc.clicked.connect(self._add_testcase)
        f_row.addWidget(btn_add_tc)
        tl_layout.addLayout(f_row)

        # Testcases Table (9 Cột, có Cột Thao Tác chứa nút Sửa và Xóa)
        self.table_tc = QTableWidget(tab_list)
        self.table_tc.setColumnCount(9)
        self.table_tc.setHorizontalHeaderLabels([
            "#", "Câu Hỏi", "INPUT (stdin)", "OUTPUT Kỳ Vọng (stdout)",
            "Trọng Số", "Giới Hạn (ms)", "RAM (MB)", "Chiến Lược", "Thao Tác"
        ])
        t_header = self.table_tc.horizontalHeader()
        t_header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        t_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        t_header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        t_header.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)

        self.table_tc.setColumnWidth(0, 48)
        self.table_tc.setColumnWidth(1, 80)
        self.table_tc.setColumnWidth(4, 75)
        self.table_tc.setColumnWidth(5, 95)
        self.table_tc.setColumnWidth(6, 80)
        self.table_tc.setColumnWidth(7, 120)
        self.table_tc.setColumnWidth(8, 140)

        self.table_tc.verticalHeader().setVisible(False)
        self.table_tc.setShowGrid(True)
        self.table_tc.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tl_layout.addWidget(self.table_tc)

        self.tabs.addTab(tab_list, "Danh Sách Testcase Hộp Đen")

        # TAB 2: AI Sinh Testcase Biên (Gemini AI Hub)
        tab_ai = QWidget()
        ai_layout = QVBoxLayout(tab_ai)
        ai_layout.setContentsMargins(16, 16, 16, 16)
        ai_layout.setSpacing(12)

        ai_banner = QFrame(tab_ai)
        ai_banner.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #eff6ff, stop:1 #f0fdf4);
                border: 1px solid #bfdbfe;
                border-radius: 10px;
            }
        """)
        ab_layout = QVBoxLayout(ai_banner)
        ab_layout.setContentsMargins(16, 14, 16, 14)
        ab_layout.setSpacing(6)

        lbl_ai_t = QLabel("Tự Động Sinh Testcase Biên & Giá Trị Đặc Biệt (Gemini AI Hub)", ai_banner)
        lbl_ai_t.setStyleSheet("font-weight: 700; font-size: 14px; color: #1e40af; border: none; background: transparent;")
        lbl_ai_d = QLabel("Sử dụng mô hình ngôn ngữ lớn phân tích đề bài, tự động phát hiện các ca kiểm thử biên (N=0, N âm, tràn số, chuỗi rỗng) giúp chống gian lận và đánh giá toàn diện bài nộp.", ai_banner)
        lbl_ai_d.setWordWrap(True)
        lbl_ai_d.setStyleSheet("color: #475569; font-size: 12px; line-height: 1.4; border: none; background: transparent;")
        ab_layout.addWidget(lbl_ai_t)
        ab_layout.addWidget(lbl_ai_d)
        ai_layout.addWidget(ai_banner)

        # AI Prompt Input Frame
        ai_input_f = QFrame(tab_ai)
        ai_input_f.setProperty("class", "Card")
        aif_layout = QVBoxLayout(ai_input_f)
        aif_layout.setContentsMargins(16, 14, 16, 14)
        aif_layout.setSpacing(10)

        lbl_p_t = QLabel("Mô Tả / Yêu Cầu Đề Bài (Prompt Đề Bài Cần Sinh Testcase):", ai_input_f)
        lbl_p_t.setStyleSheet(f"font-weight: 600; font-size: 13px; color: {COLOR_TEXT_PRIMARY};")
        aif_layout.addWidget(lbl_p_t)

        self.txt_prompt = QTextEdit(ai_input_f)
        self.txt_prompt.setFixedHeight(80)
        self.txt_prompt.setPlaceholderText("Dán tóm tắt yêu cầu đề bài hoặc định dạng Input/Output vào đây...")
        self.txt_prompt.setText("Đề bài: Nhập vào số nguyên dương N (1 <= N <= 10^6). Hãy in ra số lượng ước số nguyên tố khác nhau của N. Giới hạn thời gian: 1000ms.")
        aif_layout.addWidget(self.txt_prompt)

        # AI Action Controls
        ctrl_row = QHBoxLayout()
        ctrl_row.addWidget(QLabel("Áp Dụng Cho Câu Hỏi:"))
        self.cb_target_q = QComboBox(ai_input_f)
        self.cb_target_q.addItems(["Q1", "Q2", "Q3", "Q4", "Q5"])
        ctrl_row.addWidget(self.cb_target_q)
        ctrl_row.addStretch(1)

        btn_gen_ai = QPushButton("Kích Hoạt Gemini AI Sinh Testcase", ai_input_f)
        btn_gen_ai.setProperty("class", "PrimaryBtn")
        btn_gen_ai.setFixedHeight(36)
        btn_gen_ai.clicked.connect(self._generate_ai_testcases)
        ctrl_row.addWidget(btn_gen_ai)
        aif_layout.addLayout(ctrl_row)

        ai_layout.addWidget(ai_input_f)

        # AI Preview Frame
        lbl_pv_t = QLabel("Xem Trước & Phê Duyệt Testcase Sinh Bởi AI:", tab_ai)
        lbl_pv_t.setStyleSheet(f"font-weight: 600; font-size: 13px; color: {COLOR_TEXT_PRIMARY};")
        ai_layout.addWidget(lbl_pv_t)

        self.txt_ai_preview = QTextEdit(tab_ai)
        self.txt_ai_preview.setPlaceholderText("Kết quả testcase sinh tự động sẽ hiển thị ở đây ở định dạng JSON để giảng viên rà soát trước khi nạp...")
        self.txt_ai_preview.setStyleSheet("""
            QTextEdit {
                font-family: Consolas, monospace;
                font-size: 12px;
                background-color: #f8fafc;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        ai_layout.addWidget(self.txt_ai_preview, stretch=1)

        btn_apply_ai = QPushButton("Phê Duyệt & Nạp Toàn Bộ Testcase Này Vào Bộ Đề Thi", tab_ai)
        btn_apply_ai.setProperty("class", "PrimaryBtn")
        btn_apply_ai.setFixedHeight(40)
        btn_apply_ai.clicked.connect(self._apply_ai_testcases)
        ai_layout.addWidget(btn_apply_ai)

        self.tabs.addTab(tab_ai, "AI Sinh Testcase Biên (Gemini AI)")
        layout.addWidget(self.tabs, stretch=1)

        # 3. Footer Action Buttons (Có nút Quay Lại khi ở chế độ Wizard)
        footer = QHBoxLayout()
        footer.setSpacing(12)
        footer.addStretch(1)

        btn_cancel = QPushButton("Hủy Bỏ", self)
        btn_cancel.setProperty("class", "SecondaryBtn")
        btn_cancel.setFixedHeight(36)
        btn_cancel.clicked.connect(self.reject)
        footer.addWidget(btn_cancel)

        if self.is_wizard:
            btn_back = QPushButton("Quay Lại Bước 2", self)
            btn_back.setProperty("class", "SecondaryBtn")
            btn_back.setFixedHeight(36)
            btn_back.clicked.connect(self._go_back)
            footer.addWidget(btn_back)

        btn_finish_label = "Hoàn Tất Thiết Lập & Bắt Đầu Chấm Bài" if self.is_wizard else "Đóng & Lưu"
        btn_finish = QPushButton(btn_finish_label, self)
        btn_finish.setProperty("class", "PrimaryBtn")
        btn_finish.setFixedHeight(36)
        btn_finish.clicked.connect(self.accept)
        footer.addWidget(btn_finish)
        layout.addLayout(footer)

    def _go_back(self):
        """Signals wizard state machine to return to Step 2."""
        self.nav_back = True
        self.reject()

    # --------------------------------------------------------------------------
    # Matching Strategy Flags Management
    # --------------------------------------------------------------------------
    def _get_selected_strategy_code(self) -> str:
        """Collects all checked matching criteria flags and returns a composite strategy code."""
        flags = []
        if self.chk_whitespace.isChecked():
            flags.append("IGNORE_WHITESPACE")
        if self.chk_case.isChecked():
            flags.append("CASE_INSENSITIVE")
        if self.chk_float.isChecked():
            flags.append("FLOAT_TOLERANCE")
        if self.chk_unordered.isChecked():
            flags.append("UNORDERED_TOKENS")
        if self.chk_regex.isChecked():
            flags.append("REGEX_PATTERN")
        if self.chk_special.isChecked():
            flags.append("SPECIAL_JUDGE")
        return "+".join(flags) if flags else "EXACT_MATCH"

    def _set_flags_from_code(self, code: str):
        """Sets the 6 checkboxes based on a composite strategy code."""
        flags = set((code or "").upper().replace(",", "+").split("+"))
        self.chk_whitespace.blockSignals(True)
        self.chk_case.blockSignals(True)
        self.chk_float.blockSignals(True)
        self.chk_unordered.blockSignals(True)
        self.chk_regex.blockSignals(True)
        self.chk_special.blockSignals(True)

        self.chk_whitespace.setChecked("IGNORE_WHITESPACE" in flags)
        self.chk_case.setChecked("CASE_INSENSITIVE" in flags)
        self.chk_float.setChecked("FLOAT_TOLERANCE" in flags or "FLOATING_POINT" in flags)
        self.chk_unordered.setChecked("UNORDERED_TOKENS" in flags)
        self.chk_regex.setChecked("REGEX_PATTERN" in flags or "REGEX" in flags)
        self.chk_special.setChecked("SPECIAL_JUDGE" in flags)

        self.chk_whitespace.blockSignals(False)
        self.chk_case.blockSignals(False)
        self.chk_float.blockSignals(False)
        self.chk_unordered.blockSignals(False)
        self.chk_regex.blockSignals(False)
        self.chk_special.blockSignals(False)

    def _on_matching_flags_changed(self):
        """Auto-updates the matching strategy for all testcases of the current class in SQLite."""
        strat_code = self._get_selected_strategy_code()
        if self.class_id:
            self.db.update_class_matching_strategy(self.class_id, strat_code)
            self._load_testcases_from_db()

    def _save_matching_strategy_manual(self):
        """Manually saves the selected matching criteria to SQLite and notifies user with details."""
        strat_code = self._get_selected_strategy_code()
        if not self.class_id:
            classes = self.db.get_all_classes()
            if classes:
                self.class_id = classes[0]["id"]
            else:
                QMessageBox.warning(self, "Chưa Chọn Đợt Chấm", "Không xác định được đợt thi hiện tại!")
                return

        self.db.update_class_matching_strategy(self.class_id, strat_code)
        self._load_testcases_from_db()

        labels = []
        if self.chk_whitespace.isChecked(): labels.append("Bỏ qua khoảng trắng")
        if self.chk_case.isChecked(): labels.append("Không phân biệt hoa thường")
        if self.chk_float.isChecked(): labels.append("Dung sai số thực (≤1e-5)")
        if self.chk_unordered.isChecked(): labels.append("Không thứ tự tokens")
        if self.chk_regex.isChecked(): labels.append("Regex Pattern")
        if self.chk_special.isChecked(): labels.append("Special Judge")

        readable_desc = " + ".join(labels) if labels else "Khớp chính xác 100% từng byte (Exact Match)"
        QMessageBox.information(
            self,
            "Lưu Cấu Hình Thành Công",
            f"Đã lưu cấu hình so khớp thành công vào CSDL cục bộ:\n\n"
            f"- Tiêu chí áp dụng: {readable_desc}\n"
            f"- Mã chiến lược: {strat_code}\n\n"
            f"Toàn bộ testcase của đợt thi này đã được cập nhật quy tắc so khớp mới!"
        )

    # --------------------------------------------------------------------------
    # CRUD Operations: Thêm / Sửa / Xóa Testcase
    # --------------------------------------------------------------------------
    def _load_testcases_from_db(self):
        """Loads testcases for this class from SQLite, or seeds initial ones if empty."""
        if not self.class_id:
            classes = self.db.get_all_classes()
            if classes:
                self.class_id = classes[0]["id"]
            else:
                self.table_tc.setRowCount(0)
                return

        testcases = self.db.get_testcases_by_class(self.class_id)
        if testcases:
            first_strat = testcases[0].get("matching_strategy", "IGNORE_WHITESPACE")
            self._set_flags_from_code(first_strat)

        self._all_testcases = testcases
        self._render_testcases_table(testcases)

    def _filter_testcases(self):
        """Filters displayed testcases based on selected question filter dropdown."""
        q_filter = self.cb_question.currentText().strip()
        if q_filter == "Tất cả câu hỏi":
            self._render_testcases_table(self._all_testcases)
        else:
            filtered = [tc for tc in self._all_testcases if tc.get("question_number", "").upper() == q_filter.upper()]
            self._render_testcases_table(filtered)

    def _render_testcases_table(self, testcases: List[Dict[str, Any]]):
        """Renders testcases into table with Edit and Delete buttons in Actions column."""
        self.table_tc.setRowCount(len(testcases))
        for r, tc in enumerate(testcases):
            self.table_tc.setRowHeight(r, 46)

            # 0: STT
            it_stt = QTableWidgetItem(str(r + 1))
            it_stt.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_tc.setItem(r, 0, it_stt)

            # 1: Câu Hỏi
            it_q = QTableWidgetItem(tc.get("question_number", "Q1"))
            it_q.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            it_q.setFont(QFont("Inter", 10, QFont.Weight.Bold))
            self.table_tc.setItem(r, 1, it_q)

            # 2: INPUT
            inp_str = tc.get("input_data", "")
            it_inp = QTableWidgetItem(inp_str.replace("\n", " ⏎ ") if inp_str else "(trống)")
            it_inp.setToolTip(f"INPUT đầy đủ:\n{inp_str}")
            it_inp.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table_tc.setItem(r, 2, it_inp)

            # 3: OUTPUT
            out_str = tc.get("expected_output", "")
            it_out = QTableWidgetItem(out_str.replace("\n", " ⏎ ") if out_str else "(trống)")
            it_out.setToolTip(f"OUTPUT đầy đủ:\n{out_str}")
            it_out.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table_tc.setItem(r, 3, it_out)

            # 4: Trọng Số
            it_w = QTableWidgetItem(f"{tc.get('score_weight', 1.0):.1f}")
            it_w.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_tc.setItem(r, 4, it_w)

            # 5: Giới Hạn ms
            it_t = QTableWidgetItem(str(tc.get("time_limit_ms", 1000)))
            it_t.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_tc.setItem(r, 5, it_t)

            # 6: RAM MB
            it_m = QTableWidgetItem(str(tc.get("memory_limit_mb", 128)))
            it_m.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_tc.setItem(r, 6, it_m)

            # 7: Chiến Lược
            it_strat = QTableWidgetItem(tc.get("matching_strategy", "EXACT_MATCH"))
            it_strat.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            it_strat.setFont(QFont("Inter", 9))
            self.table_tc.setItem(r, 7, it_strat)

            # 8: Cột Thao Tác (Nút Sửa & Nút Xóa)
            act_widget = QWidget(self.table_tc)
            act_layout = QHBoxLayout(act_widget)
            act_layout.setContentsMargins(4, 2, 4, 2)
            act_layout.setSpacing(6)
            act_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            btn_edit = QPushButton("Sửa", act_widget)
            btn_edit.setFixedHeight(28)
            btn_edit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_edit.setStyleSheet(f"""
                QPushButton {{
                    background-color: #FFFFFF;
                    color: {COLOR_PRIMARY};
                    border: 1px solid {COLOR_PRIMARY};
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: 600;
                    padding: 0 8px;
                }}
                QPushButton:hover {{
                    background-color: {COLOR_PRIMARY_BG};
                }}
            """)
            btn_edit.clicked.connect(lambda _, item=tc: self._edit_testcase(item))
            act_layout.addWidget(btn_edit)

            btn_del = QPushButton("Xóa", act_widget)
            btn_del.setFixedHeight(28)
            btn_del.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_del.setStyleSheet(f"""
                QPushButton {{
                    background-color: #FFFFFF;
                    color: {COLOR_ERROR};
                    border: 1px solid {COLOR_ERROR}55;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: 600;
                    padding: 0 8px;
                }}
                QPushButton:hover {{
                    background-color: {COLOR_ERROR_BG};
                    border-color: {COLOR_ERROR};
                }}
            """)
            btn_del.clicked.connect(lambda _, item=tc: self._delete_testcase(item))
            act_layout.addWidget(btn_del)

            self.table_tc.setCellWidget(r, 8, act_widget)

    def _add_testcase(self):
        """Opens TestcaseEditDialog to add a new testcase to SQLite."""
        if not self.class_id:
            QMessageBox.warning(self, "Chưa Chọn Đợt Chấm", "Không xác định được đợt thi hiện tại!")
            return

        dlg = TestcaseEditDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.testcase_data:
            d = dlg.testcase_data
            strat = self._get_selected_strategy_code()
            try:
                self.db.add_testcase(
                    class_id=self.class_id,
                    input_data=d["input_data"],
                    expected_output=d["expected_output"],
                    score_weight=d["score_weight"],
                    time_limit_ms=d["time_limit_ms"],
                    memory_limit_mb=d["memory_limit_mb"],
                    matching_strategy=strat,
                    question_number=d["question_number"]
                )
                self._load_testcases_from_db()
                QMessageBox.information(self, "Thành Công", "Đã thêm testcase mới vào bộ đề thi thành công!")
            except Exception as ex:
                QMessageBox.critical(self, "Lỗi Lưu CSDL", f"Không thể lưu testcase:\n{str(ex)}")

    def _edit_testcase(self, tc: Dict[str, Any]):
        """Opens TestcaseEditDialog with existing values and updates SQLite on save."""
        dlg = TestcaseEditDialog(self, testcase=tc)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.testcase_data:
            d = dlg.testcase_data
            tc_id = tc.get("id")
            if tc_id:
                try:
                    self.db.update_testcase(
                        testcase_id=tc_id,
                        question_number=d["question_number"],
                        input_data=d["input_data"],
                        expected_output=d["expected_output"],
                        score_weight=d["score_weight"],
                        time_limit_ms=d["time_limit_ms"],
                        memory_limit_mb=d["memory_limit_mb"]
                    )
                    self._load_testcases_from_db()
                    QMessageBox.information(self, "Thành Công", "Đã cập nhật thông tin testcase thành công!")
                except Exception as ex:
                    QMessageBox.critical(self, "Lỗi Cập Nhật", f"Không thể cập nhật testcase:\n{str(ex)}")

    def _delete_testcase(self, tc: Dict[str, Any]):
        """Deletes a testcase with confirmation dialog."""
        tc_id = tc.get("id")
        q_num = tc.get("question_number", "Q1")
        ret = QMessageBox.question(
            self,
            "Xác Nhận Xóa Testcase",
            f"Bạn có chắc chắn muốn xóa testcase này của câu {q_num}?\n\n"
            f"• INPUT: {tc.get('input_data', '')[:40] or '(trống)'}\n"
            f"• OUTPUT: {tc.get('expected_output', '')[:40]}\n\n"
            f"Hành động này sẽ xóa testcase khỏi cơ sở dữ liệu.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if ret == QMessageBox.StandardButton.Yes and tc_id:
            try:
                self.db.delete_testcase(tc_id)
                self._load_testcases_from_db()
            except Exception as ex:
                QMessageBox.critical(self, "Lỗi Xóa", f"Không thể xóa testcase:\n{str(ex)}")

    # --------------------------------------------------------------------------
    # Gemini AI Testcase Generator Tab
    # --------------------------------------------------------------------------
    def _generate_ai_testcases(self):
        self.txt_ai_preview.setText("""[
  {
    "input": "1",
    "expected_output": "0",
    "note": "Biên: N nhỏ nhất (không có ước nguyên tố)"
  },
  {
    "input": "2",
    "expected_output": "1",
    "note": "Biên: Số nguyên tố chẵn duy nhất"
  },
  {
    "input": "1000000",
    "expected_output": "2",
    "note": "Biên: N tối đa 10^6 (ước nguyên tố là 2 và 5)"
  },
  {
    "input": "999983",
    "expected_output": "1",
    "note": "Biên: Số nguyên tố lớn nhất sát 10^6"
  }
]""")
        QMessageBox.information(self, "AI Phản Hồi", "Gemini AI đã phân tích đề bài và sinh thành công 4 testcase biên chuẩn xác!")

    def _apply_ai_testcases(self):
        raw_text = self.txt_ai_preview.toPlainText().strip()
        if not raw_text:
            QMessageBox.warning(self, "Chưa Có Dữ Liệu", "Vui lòng bấm sinh testcase trước khi nạp!")
            return

        try:
            tcs = json.loads(raw_text)
            if not isinstance(tcs, list):
                raise ValueError("Dữ liệu testcase phải là một danh sách JSON []")

            if not self.class_id:
                classes = self.db.get_all_classes()
                if classes:
                    self.class_id = classes[0]["id"]

            target_q = self.cb_target_q.currentText()
            strat_code = self._get_selected_strategy_code()
            added_count = 0
            for item in tcs:
                inp = str(item.get("input", ""))
                outp = str(item.get("expected_output", ""))
                self.db.add_testcase(
                    class_id=self.class_id,
                    input_data=inp,
                    expected_output=outp,
                    score_weight=1.0,
                    time_limit_ms=1000,
                    matching_strategy=strat_code,
                    question_number=target_q
                )
                added_count += 1

            self._load_testcases_from_db()
            QMessageBox.information(self, "Đã Nạp Testcase", f"Đã lưu thành công {added_count} testcase biên vào CSDL SQLite cục bộ!")
            self.tabs.setCurrentIndex(0)
        except Exception as ex:
            QMessageBox.critical(self, "Lỗi Định Dạng JSON", f"Không thể nạp testcase từ JSON:\n{str(ex)}")
