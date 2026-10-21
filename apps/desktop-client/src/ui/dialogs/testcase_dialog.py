"""
AITA Desktop Client - Testcase Manager & AI Generator Dialog (PyQt6)
UC-09: Manage Black-box Testcases Manually (Add / Edit / Delete Input/Output)
UC-10: Auto-Generate Boundary Testcases with AI Hub
UC-11: Configure 7 Output Matching Strategies
"""

import sys
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QCursor, QGuiApplication, QFont, QColor
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QCheckBox, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QTextEdit, QSpinBox, QDoubleSpinBox, QTabWidget, QMessageBox, QFileDialog,
    QSplitter, QListWidget, QListWidgetItem, QStackedWidget, QAbstractItemView, QScrollArea
)

SRC_DIR = Path(__file__).resolve().parent.parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ui.styles.theme import (
    LIGHT_THEME_QSS, COLOR_PRIMARY, COLOR_PRIMARY_BG,
    COLOR_BORDER_DEFAULT, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_ERROR, COLOR_ERROR_BG, COLOR_SUCCESS, COLOR_SURFACE_SECONDARY,
    COLOR_TEXT_MUTED
)
from ui.components.code_editor import CodeEditor
from ui.components.multiline_field import MultiLineField
from ui.components.table_actions import (
    make_action_cell, make_row_button, preview_multiline, preview_tooltip, text_color_for_value
)
from database.db_manager import DatabaseManager
from services.ai_service import AiService
from services.testcase_paste_parser import parse_testcase_text
from services.document_reader import (
    MAX_PROBLEM_CHARS, DocumentReadError, read_document_text
)

logger = logging.getLogger("AITA.TestcaseDialog")


# ==============================================================================
# WORKER LUỒNG PHỤ GỌI AI HUB (OPENROUTER ĐA TÀI KHOẢN) QUA CENTRAL BACKEND
# ==============================================================================
class AiTestcaseWorker(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, problem_desc: str, language: str, count: int, include_boundary: bool):
        super().__init__()
        self.problem_desc = problem_desc
        self.language = language
        self.count = count
        self.include_boundary = include_boundary

    def run(self):
        ai_service = AiService()
        result = ai_service.generate_testcases(
            problem_description=self.problem_desc,
            language=self.language,
            count=self.count,
            include_boundary=self.include_boundary
        )
        self.finished.emit(result)


# ==============================================================================
# 1. HỘP THOẠI THÊM / CHỈNH SỬA BỘ TESTCASE CỦA MỘT CÂU HỎI
# ==============================================================================
DEFAULT_TIME_LIMIT_MS = 1000
DEFAULT_MEMORY_LIMIT_MB = 128
MAX_DATA_BYTES = 256 * 1024
LIST_ROW_HEIGHT = 54


def _style_spinbox(widget: QWidget):
    """Áp style chung cho QSpinBox/QDoubleSpinBox.

    Chiều cao 38px + chừa 24px bên phải để hai nút mũi tên không bị cắt mép.
    """
    widget.setMinimumHeight(38)
    widget.setMinimumWidth(140)
    widget.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    widget.setStyleSheet(f"""
        QSpinBox, QDoubleSpinBox {{
            min-height: 36px;
            padding: 4px 4px 4px 10px;
            border: 1px solid {COLOR_BORDER_DEFAULT};
            border-radius: 8px;
            background-color: #FFFFFF;
            font-size: 13px;
        }}
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 1px solid {COLOR_PRIMARY};
        }}
        QSpinBox:disabled, QDoubleSpinBox:disabled {{
            color: {COLOR_TEXT_MUTED};
            background-color: {COLOR_SURFACE_SECONDARY};
        }}
        QSpinBox::up-button, QDoubleSpinBox::up-button {{
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 22px;
            height: 18px;
            border-left: 1px solid {COLOR_BORDER_DEFAULT};
            border-top-right-radius: 8px;
            background-color: {COLOR_SURFACE_SECONDARY};
        }}
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            width: 22px;
            height: 18px;
            border-left: 1px solid {COLOR_BORDER_DEFAULT};
            border-bottom-right-radius: 8px;
            background-color: {COLOR_SURFACE_SECONDARY};
        }}
        QSpinBox::up-arrow, QDoubleSpinBox::up-arrow,
        QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
            width: 7px;
            height: 7px;
        }}
        QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
        QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
            background-color: {COLOR_PRIMARY_BG};
        }}
    """)


def _field_label(text: str, parent: QWidget) -> QLabel:
    label = QLabel(text, parent)
    label.setStyleSheet(
        f"font-weight: 600; font-size: 13px; line-height: 1.4; color: {COLOR_TEXT_PRIMARY};"
    )
    label.setContentsMargins(0, 0, 0, 0)
    return label


class TestcaseEditDialog(QDialog):
    """Thêm/sửa bộ testcase của một câu hỏi (nhiều testcase trong cùng cửa sổ).

    - Cột trái: danh sách testcase (Thêm Testcase / Nhân Bản / Xóa, kéo thả đổi thứ tự).
    - Cột phải: tab "Chi Tiết Testcase" và tab "Dán Nhiều Testcase".
    - Chân: Hủy / Lưu và Thêm Tiếp / Lưu.

    Kiểu lưu CSDL KHÔNG đổi: mỗi testcase vẫn là cặp chuỗi `input_data` /
    `expected_output` với các dòng nối bằng "\\n"; giới hạn thời gian/bộ nhớ vẫn
    lưu trên từng testcase như trước (testcase không ghi đè thì lưu đúng giá trị
    mặc định của câu hỏi).
    """

    def __init__(self, parent=None, testcase: Optional[Dict[str, Any]] = None,
                 db: Optional[DatabaseManager] = None, class_id: Optional[int] = None,
                 question_number: Optional[str] = None,
                 matching_strategy: str = "EXACT_MATCH",
                 start_new: bool = False):
        super().__init__(parent)
        self.db = db
        self.class_id = class_id
        self.matching_strategy = matching_strategy or "EXACT_MATCH"
        self._legacy_single = db is None

        self.testcases: List[Dict[str, Any]] = []
        self.testcase_data: Dict[str, Any] = {}
        self.saved_count = 0

        self._deleted_ids: List[int] = []
        self._uid_counter = 0
        self._dirty = False
        self._loading = False
        self._current = -1
        self._paste_rows: List[Any] = []

        initial = testcase or {}
        self.question_number = (question_number or initial.get("question_number") or "Q1").strip() or "Q1"
        self.q_time = DEFAULT_TIME_LIMIT_MS
        self.q_mem = DEFAULT_MEMORY_LIMIT_MB

        self.setWindowTitle("Thêm Testcase" if start_new or not initial else "Chỉnh Sửa Testcase")
        self.setStyleSheet(LIGHT_THEME_QSS)
        self.setMinimumSize(960, 640)
        screen = QGuiApplication.primaryScreen()
        if screen:
            avail = screen.availableGeometry()
            target_w = min(1180, avail.width() - 40)
            target_h = min(800, avail.height() - 24)
            self.resize(target_w, target_h)
            self.move(avail.x() + (avail.width() - target_w) // 2,
                      avail.y() + (avail.height() - target_h) // 2)
        else:
            self.resize(1120, 720)

        self._init_ui()
        self._load_testcases(initial, start_new)

    # ================================================================== khởi tạo
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        lbl_title = QLabel("Bộ Testcase Của Câu Hỏi", self)
        lbl_title.setStyleSheet(
            f"font-size: 17px; font-weight: 700; line-height: 1.4; color: {COLOR_TEXT_PRIMARY};"
        )
        layout.addWidget(lbl_title)

        lbl_sub = QLabel(
            "Chọn testcase ở cột trái để sửa nội dung, hoặc dán hàng loạt ở tab bên cạnh.",
            self,
        )
        lbl_sub.setWordWrap(True)
        lbl_sub.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_SECONDARY}; line-height: 1.4;")
        layout.addWidget(lbl_sub)

        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.addWidget(self._build_left_panel())
        self.splitter.addWidget(self._build_right_panel())
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 7)
        self.splitter.setSizes([300, 720])
        layout.addWidget(self.splitter, 1)

        layout.addLayout(self._build_footer())

    def _build_left_panel(self) -> QWidget:
        panel = QWidget(self)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 12, 0)
        layout.setSpacing(8)

        lbl = QLabel("Danh Sách Testcase", panel)
        lbl.setStyleSheet(f"font-weight: 600; font-size: 13px; color: {COLOR_TEXT_PRIMARY};")
        layout.addWidget(lbl)

        self.list_tc = QListWidget(panel)
        self.list_tc.setMinimumWidth(260)
        self.list_tc.setMinimumHeight(240)
        self.list_tc.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.list_tc.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.list_tc.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list_tc.setStyleSheet(f"""
            QListWidget {{
                border: 1px solid {COLOR_BORDER_DEFAULT}; border-radius: 10px;
                background-color: #FFFFFF; padding: 4px;
            }}
            QListWidget::item {{ border-bottom: 1px solid #F1F5F9; }}
            QListWidget::item:selected {{ background-color: {COLOR_PRIMARY_BG}; }}
        """)
        self.list_tc.currentRowChanged.connect(self._on_row_changed)
        self.list_tc.model().rowsMoved.connect(self._on_rows_moved)
        layout.addWidget(self.list_tc, 1)

        self.lbl_totals = QLabel("0 testcase, tổng trọng số 0.0", panel)
        self.lbl_totals.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_SECONDARY};")
        layout.addWidget(self.lbl_totals)

        buttons = QHBoxLayout()
        buttons.setSpacing(8)

        self.btn_add = QPushButton("Thêm Testcase", panel)
        self.btn_add.setProperty("class", "PrimaryBtn")
        self.btn_add.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_add.clicked.connect(self._add_testcase)
        buttons.addWidget(self.btn_add)

        self.btn_duplicate = QPushButton("Nhân Bản", panel)
        self.btn_duplicate.setProperty("class", "SecondaryBtn")
        self.btn_duplicate.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_duplicate.clicked.connect(self._duplicate_testcase)
        buttons.addWidget(self.btn_duplicate)

        self.btn_delete = QPushButton("Xóa", panel)
        self.btn_delete.setProperty("class", "SecondaryBtn")
        self.btn_delete.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_delete.setStyleSheet(
            f"QPushButton {{ color: {COLOR_ERROR}; border: 1px solid {COLOR_ERROR}55;"
            " background-color: #FFFFFF; border-radius: 8px; font-weight: 600; }}"
            f"QPushButton:hover {{ background-color: {COLOR_ERROR_BG};"
            f" border: 1px solid {COLOR_ERROR}; }}"
        )
        self.btn_delete.clicked.connect(self._delete_testcase)
        buttons.addWidget(self.btn_delete)

        layout.addLayout(buttons)
        return panel

    def _build_right_panel(self) -> QWidget:
        self.tabs = QTabWidget(self)
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLOR_BORDER_DEFAULT}; border-radius: 10px;
                background-color: #FFFFFF; top: -1px;
            }}
            QTabBar::tab {{
                font-size: 13px; font-weight: 600; padding: 8px 16px; margin-right: 4px;
                color: {COLOR_TEXT_SECONDARY}; border: 1px solid transparent;
                border-top-left-radius: 8px; border-top-right-radius: 8px;
            }}
            QTabBar::tab:selected {{
                color: {COLOR_PRIMARY}; background-color: #FFFFFF;
                border: 1px solid {COLOR_BORDER_DEFAULT}; border-bottom: 2px solid {COLOR_PRIMARY};
            }}
            QTabBar::tab:hover:!selected {{ color: {COLOR_TEXT_PRIMARY}; background-color: #F8FAFC; }}
        """)
        self.tabs.addTab(self._scrollable(self._build_detail_tab()), "Chi Tiết Testcase")
        self.tabs.addTab(self._build_paste_tab(), "Dán Nhiều Testcase")
        return self.tabs

    def _scrollable(self, page: QWidget) -> QScrollArea:
        """Bọc tab Chi Tiết trong vùng cuộn: cửa sổ thấp (scale 150%) vẫn đủ 200px cho ô dữ liệu."""
        area = QScrollArea(self)
        area.setWidgetResizable(True)
        area.setFrameShape(QFrame.Shape.NoFrame)
        area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        area.setWidget(page)
        area.setStyleSheet("QScrollArea { background-color: #FFFFFF; border: none; }")
        page.setStyleSheet("background-color: #FFFFFF;")
        return area

    def _build_detail_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(6)
        titles = [
            "Câu Hỏi:", "Trọng Số Điểm:", "Giới Hạn Thời Gian (ms):", "Giới Hạn Bộ Nhớ (MB):",
        ]
        for column, title in enumerate(titles):
            label = _field_label(title, page)
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            grid.addWidget(label, 0, column)
            grid.setColumnStretch(column, 1)

        self.cb_q = QComboBox(page)
        self.cb_q.setEditable(True)
        self.cb_q.setMinimumHeight(38)
        self.cb_q.addItems(["Q1", "Q2", "Q3", "Q4", "Q5"])
        self.cb_q.setStyleSheet(
            f"QComboBox {{ min-height: 36px; padding: 4px 10px; font-size: 13px;"
            f" border: 1px solid {COLOR_BORDER_DEFAULT}; border-radius: 8px; background-color: #FFFFFF; }}"
        )
        self.cb_q.currentTextChanged.connect(self._on_question_changed)
        grid.addWidget(self.cb_q, 1, 0)

        self.sp_weight = QDoubleSpinBox(page)
        self.sp_weight.setRange(0.1, 10.0)
        self.sp_weight.setSingleStep(0.5)
        self.sp_weight.setDecimals(1)
        _style_spinbox(self.sp_weight)
        self.sp_weight.valueChanged.connect(self._on_field_changed)
        grid.addWidget(self.sp_weight, 1, 1)

        self.sp_q_time = QSpinBox(page)
        self.sp_q_time.setRange(100, 60000)
        self.sp_q_time.setSingleStep(100)
        _style_spinbox(self.sp_q_time)
        self.sp_q_time.setToolTip(
            "Giới hạn thời gian mặc định của câu hỏi.\n"
            "Áp dụng cho mọi testcase không bật \"Ghi đè giới hạn\"."
        )
        self.sp_q_time.valueChanged.connect(self._on_question_limits_changed)
        grid.addWidget(self.sp_q_time, 1, 2)

        self.sp_q_mem = QSpinBox(page)
        self.sp_q_mem.setRange(16, 4096)
        self.sp_q_mem.setSingleStep(32)
        _style_spinbox(self.sp_q_mem)
        self.sp_q_mem.setToolTip(
            "Giới hạn bộ nhớ mặc định của câu hỏi.\n"
            "Áp dụng cho mọi testcase không bật \"Ghi đè giới hạn\"."
        )
        self.sp_q_mem.valueChanged.connect(self._on_question_limits_changed)
        grid.addWidget(self.sp_q_mem, 1, 3)

        layout.addLayout(grid)

        override_row = QHBoxLayout()
        override_row.setSpacing(10)
        self.chk_override = QCheckBox("Ghi đè giới hạn", page)
        self.chk_override.setStyleSheet(
            f"font-size: 12px; font-weight: 600; color: {COLOR_TEXT_PRIMARY};"
        )
        self.chk_override.toggled.connect(self._on_override_toggled)
        override_row.addWidget(self.chk_override)

        self.lbl_case_time = QLabel("Thời gian:", page)
        self.lbl_case_time.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_SECONDARY};")
        override_row.addWidget(self.lbl_case_time)

        self.sp_time = QSpinBox(page)
        self.sp_time.setRange(100, 60000)
        self.sp_time.setSingleStep(100)
        self.sp_time.setSuffix(" ms")
        self.sp_time.setMinimumWidth(118)
        _style_spinbox(self.sp_time)
        self.sp_time.valueChanged.connect(self._on_field_changed)
        override_row.addWidget(self.sp_time)

        self.lbl_case_mem = QLabel("Bộ nhớ:", page)
        self.lbl_case_mem.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_SECONDARY};")
        override_row.addWidget(self.lbl_case_mem)

        self.sp_mem = QSpinBox(page)
        self.sp_mem.setRange(16, 4096)
        self.sp_mem.setSingleStep(32)
        self.sp_mem.setSuffix(" MB")
        self.sp_mem.setMinimumWidth(118)
        _style_spinbox(self.sp_mem)
        self.sp_mem.valueChanged.connect(self._on_field_changed)
        override_row.addWidget(self.sp_mem)

        override_row.addStretch(1)
        layout.addLayout(override_row)

        data_row = QHBoxLayout()
        data_row.setSpacing(16)

        self.f_input = MultiLineField(
            "Đầu Vào (stdin)",
            "Dữ liệu đưa vào chương trình (để trống nếu bài không đọc stdin)",
            page, required=False, min_height=200,
        )
        self.f_input.changed.connect(self._on_field_changed)
        data_row.addWidget(self.f_input, 1)

        self.f_output = MultiLineField(
            "Kết Quả Kỳ Vọng (stdout)",
            "Kết quả đúng mà chương trình phải in ra",
            page, required=True, min_height=200,
        )
        self.f_output.changed.connect(self._on_field_changed)
        data_row.addWidget(self.f_output, 1)

        layout.addLayout(data_row, 1)
        return page

    def _build_paste_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        lbl_hint = QLabel(
            "Dán JSON: [{\"input\": \"...\", \"output\": \"...\"}, ...] — hoặc dán khối văn bản: "
            "phần input, một dòng \"===\", phần output; các testcase cách nhau bằng dòng \"---\".",
            page,
        )
        lbl_hint.setWordWrap(True)
        lbl_hint.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_SECONDARY}; line-height: 1.4;")
        layout.addWidget(lbl_hint)

        self.txt_paste = CodeEditor(page, read_only=False, min_height=170)
        self.txt_paste.setPlaceholderText(
            "5\n4 -3 7 2 11\n===\nTong = 21\nMax = 11\nMin = -3\nSo nguyen to = 3\n"
            "---\n1\n7\n===\nTong = 7\nMax = 7\nMin = 7\nSo nguyen to = 1"
        )
        layout.addWidget(self.txt_paste, 1)

        action_row = QHBoxLayout()
        action_row.setSpacing(12)
        self.btn_preview = QPushButton("Xem Trước", page)
        self.btn_preview.setProperty("class", "SecondaryBtn")
        self.btn_preview.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_preview.clicked.connect(self._preview_paste)
        action_row.addWidget(self.btn_preview)

        self.lbl_paste_result = QLabel("", page)
        self.lbl_paste_result.setWordWrap(True)
        self.lbl_paste_result.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_SECONDARY};")
        action_row.addWidget(self.lbl_paste_result, 1)

        self.btn_add_all = QPushButton("Thêm Tất Cả", page)
        self.btn_add_all.setProperty("class", "PrimaryBtn")
        self.btn_add_all.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_add_all.setEnabled(False)
        self.btn_add_all.clicked.connect(self._add_all_pasted)
        action_row.addWidget(self.btn_add_all)
        layout.addLayout(action_row)

        self.table_paste = QTableWidget(0, 4, page)
        self.table_paste.setHorizontalHeaderLabels(
            ["#", "Đầu Vào (dòng đầu)", "Kết Quả Kỳ Vọng (dòng đầu)", "Trạng thái"]
        )
        header = self.table_paste.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table_paste.setColumnWidth(0, 46)
        self.table_paste.verticalHeader().setVisible(False)
        self.table_paste.setMinimumHeight(180)
        layout.addWidget(self.table_paste, 1)
        return page

    def _build_footer(self) -> QHBoxLayout:
        footer = QHBoxLayout()
        footer.setSpacing(12)
        footer.addStretch(1)

        self.btn_cancel = QPushButton("Hủy", self)
        self.btn_cancel.setProperty("class", "SecondaryBtn")
        self.btn_cancel.setMinimumWidth(96)
        self.btn_cancel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_cancel.clicked.connect(self.reject)
        footer.addWidget(self.btn_cancel)

        self.btn_save_more = QPushButton("Lưu và Thêm Tiếp", self)
        self.btn_save_more.setProperty("class", "SecondaryBtn")
        self.btn_save_more.setMinimumWidth(150)
        self.btn_save_more.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_save_more.clicked.connect(lambda: self._save(keep_open=True))
        footer.addWidget(self.btn_save_more)

        self.btn_save = QPushButton("Lưu", self)
        self.btn_save.setProperty("class", "PrimaryBtn")
        self.btn_save.setMinimumWidth(120)
        self.btn_save.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_save.clicked.connect(lambda: self._save(keep_open=False))
        footer.addWidget(self.btn_save)
        return footer

    # ================================================================== nạp dữ liệu
    def _next_uid(self) -> int:
        self._uid_counter += 1
        return self._uid_counter

    def _from_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "uid": self._next_uid(),
            "id": row.get("id"),
            "question_number": str(row.get("question_number") or self.question_number),
            "input_data": row.get("input_data") or "",
            "expected_output": row.get("expected_output") or "",
            "score_weight": float(row.get("score_weight") or 1.0),
            "time_limit_ms": int(row.get("time_limit_ms") or DEFAULT_TIME_LIMIT_MS),
            "memory_limit_mb": int(row.get("memory_limit_mb") or DEFAULT_MEMORY_LIMIT_MB),
            "override_limits": False,
            "matching_strategy": row.get("matching_strategy") or self.matching_strategy,
            "is_hidden": int(row.get("is_hidden") or 0),
        }

    def _blank_testcase(self) -> Dict[str, Any]:
        return {
            "uid": self._next_uid(),
            "id": None,
            "question_number": self.question_number,
            "input_data": "",
            "expected_output": "",
            "score_weight": 1.0,
            "time_limit_ms": self.q_time,
            "memory_limit_mb": self.q_mem,
            "override_limits": False,
            "matching_strategy": self.matching_strategy,
            "is_hidden": 0,
        }

    def _load_testcases(self, initial: Dict[str, Any], start_new: bool):
        loaded: List[Dict[str, Any]] = []
        if self.db is not None and self.class_id:
            rows = [
                row for row in self.db.get_testcases_by_class(self.class_id)
                if str(row.get("question_number", "")).upper() == self.question_number.upper()
            ]
            loaded = [self._from_row(row) for row in rows]
        elif initial:
            loaded = [self._from_row(initial)]

        self.q_time, self.q_mem = self._detect_defaults(loaded)
        for testcase in loaded:
            testcase["override_limits"] = (
                testcase["time_limit_ms"] != self.q_time
                or testcase["memory_limit_mb"] != self.q_mem
            )

        self.testcases = loaded
        if start_new or not self.testcases:
            self.testcases.append(self._blank_testcase())

        self._loading = True
        try:
            self.cb_q.setEditText(self.question_number)
            self.sp_q_time.setValue(self.q_time)
            self.sp_q_mem.setValue(self.q_mem)
        finally:
            self._loading = False

        self._refresh_list(select=len(self.testcases) - 1 if start_new else 0)

    @staticmethod
    def _is_placeholder(testcase: Dict[str, Any]) -> bool:
        """Testcase trống hoàn toàn (chưa nhập gì) chỉ là chỗ chờ, không lưu/báo lỗi."""
        return not (testcase.get("input_data") or "").strip() \
            and not (testcase.get("expected_output") or "").strip()

    @staticmethod
    def _detect_defaults(rows: List[Dict[str, Any]]) -> tuple:
        """Giới hạn của câu hỏi = giá trị xuất hiện nhiều nhất trong các testcase đã có."""
        if not rows:
            return DEFAULT_TIME_LIMIT_MS, DEFAULT_MEMORY_LIMIT_MB
        times = [row["time_limit_ms"] for row in rows]
        mems = [row["memory_limit_mb"] for row in rows]
        return max(set(times), key=times.count), max(set(mems), key=mems.count)

    # ================================================================== danh sách
    def _build_list_row(self, index: int, testcase: Dict[str, Any]) -> QWidget:
        row = QWidget(self.list_tc)
        row.setStyleSheet("background: transparent;")
        row.setFixedHeight(LIST_ROW_HEIGHT)
        layout = QVBoxLayout(row)
        layout.setContentsMargins(8, 5, 8, 5)
        layout.setSpacing(2)

        head = QHBoxLayout()
        head.setSpacing(6)
        lbl_title = QLabel(row)
        lbl_title.setStyleSheet(
            f"font-weight: 600; font-size: 13px; color: {COLOR_TEXT_PRIMARY};"
        )
        head.addWidget(lbl_title)
        head.addStretch(1)
        lbl_missing = QLabel("Thiếu kết quả", row)
        lbl_missing.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {COLOR_ERROR};")
        head.addWidget(lbl_missing)
        layout.addLayout(head)

        lbl_summary = QLabel(row)
        lbl_summary.setStyleSheet(f"font-size: 11px; color: {COLOR_TEXT_SECONDARY};")
        layout.addWidget(lbl_summary)

        # Giữ tham chiếu để cập nhật tại chỗ (tránh tạo lại widget mỗi lần gõ phím).
        row.title_label = lbl_title
        row.missing_label = lbl_missing
        row.summary_label = lbl_summary
        self._apply_row_texts(row, index, testcase)
        return row

    def _apply_row_texts(self, row: QWidget, index: int, testcase: Dict[str, Any]):
        row.title_label.setText(f"Testcase {index + 1}")
        row.missing_label.setVisible(not (testcase.get("expected_output") or "").strip())

        summary = preview_multiline(testcase.get("input_data") or "", 46)
        if summary == "(trống)":
            summary = "(stdin trống)"
        row.summary_label.setText(summary)

    def _refresh_list(self, select: Optional[int] = None):
        target = self._current if select is None else select
        self.list_tc.blockSignals(True)
        try:
            for index in reversed(range(self.list_tc.count())):
                old_widget = self.list_tc.itemWidget(self.list_tc.item(index))
                if old_widget is not None:
                    old_widget.setParent(None)
                    old_widget.deleteLater()
            self.list_tc.clear()
            for index, testcase in enumerate(self.testcases):
                item = QListWidgetItem()
                item.setFlags(
                    Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
                    | Qt.ItemFlag.ItemIsDragEnabled
                )
                item.setData(Qt.ItemDataRole.UserRole, testcase["uid"])
                self.list_tc.addItem(item)
                widget = self._build_list_row(index, testcase)
                item.setSizeHint(QSize(0, LIST_ROW_HEIGHT))
                self.list_tc.setItemWidget(item, widget)
        finally:
            self.list_tc.blockSignals(False)

        if self.testcases:
            target = max(0, min(target if target >= 0 else 0, len(self.testcases) - 1))
            self.list_tc.setCurrentRow(target)
        self._current = self.list_tc.currentRow()
        self._show_current_testcase()
        self._refresh_totals()

    def _refresh_totals(self):
        total_weight = sum(float(tc.get("score_weight") or 0.0) for tc in self.testcases)
        self.lbl_totals.setText(
            f"{len(self.testcases)} testcase, tổng trọng số {total_weight:.1f}"
        )

    def _refresh_current_row(self):
        if not (0 <= self._current < len(self.testcases)):
            return
        item = self.list_tc.item(self._current)
        if item is None:
            return
        widget = self.list_tc.itemWidget(item)
        if widget is not None and hasattr(widget, "summary_label"):
            self._apply_row_texts(widget, self._current, self.testcases[self._current])
            return
        widget = self._build_list_row(self._current, self.testcases[self._current])
        item.setSizeHint(QSize(0, LIST_ROW_HEIGHT))
        self.list_tc.setItemWidget(item, widget)

    def _on_rows_moved(self, *_args):
        QTimer.singleShot(0, self._apply_new_order)

    def _apply_new_order(self):
        """Đọc lại thứ tự sau khi người dùng kéo thả item trong danh sách."""
        order = []
        for index in range(self.list_tc.count()):
            item = self.list_tc.item(index)
            order.append(item.data(Qt.ItemDataRole.UserRole))
        by_uid = {testcase["uid"]: testcase for testcase in self.testcases}
        if len(order) != len(self.testcases) or any(uid not in by_uid for uid in order):
            self._refresh_list()
            return
        current_uid = (
            self.testcases[self._current]["uid"]
            if 0 <= self._current < len(self.testcases) else None
        )
        self.testcases = [by_uid[uid] for uid in order]
        new_index = next(
            (i for i, tc in enumerate(self.testcases) if tc["uid"] == current_uid), 0
        )
        self._mark_dirty()
        self._refresh_list(select=new_index)

    # ================================================================== form
    def _current_testcase(self) -> Optional[Dict[str, Any]]:
        if 0 <= self._current < len(self.testcases):
            return self.testcases[self._current]
        return None

    def _on_row_changed(self, row: int):
        if self._loading:
            return
        self._current = row
        self._show_current_testcase()

    def _show_current_testcase(self):
        testcase = self._current_testcase()
        self._loading = True
        try:
            for widget in (self.cb_q, self.sp_weight, self.chk_override,
                           self.f_input, self.f_output):
                widget.setEnabled(testcase is not None)
            if testcase is not None:
                self.sp_weight.setValue(float(testcase["score_weight"]))
                self.chk_override.setChecked(bool(testcase["override_limits"]))
                self.sp_time.setValue(int(testcase["time_limit_ms"]))
                self.sp_mem.setValue(int(testcase["memory_limit_mb"]))
                self.f_input.set_text(testcase["input_data"])
                self.f_output.set_text(testcase["expected_output"])
        finally:
            self._loading = False
        self._refresh_override_state()

    def _refresh_override_state(self):
        testcase = self._current_testcase()
        enabled = bool(testcase and testcase.get("override_limits"))
        self.sp_time.setEnabled(enabled)
        self.sp_mem.setEnabled(enabled)
        self.lbl_case_time.setEnabled(enabled)
        self.lbl_case_mem.setEnabled(enabled)
        if testcase is not None and not enabled:
            self._loading = True
            try:
                self.sp_time.setValue(self.q_time)
                self.sp_mem.setValue(self.q_mem)
            finally:
                self._loading = False

    def _on_override_toggled(self, checked: bool):
        if self._loading:
            return
        self._on_field_changed()

    def _on_question_changed(self, text: str):
        if self._loading:
            return
        value = (text or "").strip() or "Q1"
        self.question_number = value
        for testcase in self.testcases:
            testcase["question_number"] = value
        self._mark_dirty()

    def _on_question_limits_changed(self):
        if self._loading:
            return
        self.q_time = int(self.sp_q_time.value())
        self.q_mem = int(self.sp_q_mem.value())
        for testcase in self.testcases:
            if not testcase["override_limits"]:
                testcase["time_limit_ms"] = self.q_time
                testcase["memory_limit_mb"] = self.q_mem
        self._mark_dirty()
        self._refresh_override_state()

    def _on_field_changed(self):
        if self._loading:
            return
        testcase = self._current_testcase()
        if testcase is None:
            return
        testcase["override_limits"] = self.chk_override.isChecked()
        if testcase["override_limits"]:
            testcase["time_limit_ms"] = int(self.sp_time.value())
            testcase["memory_limit_mb"] = int(self.sp_mem.value())
        else:
            testcase["time_limit_ms"] = self.q_time
            testcase["memory_limit_mb"] = self.q_mem
        testcase["score_weight"] = float(self.sp_weight.value())
        testcase["question_number"] = self.question_number
        testcase["input_data"] = self.f_input.text()
        testcase["expected_output"] = self.f_output.text()
        self._mark_dirty()
        self._refresh_current_row()
        self._refresh_totals()
        self._refresh_override_state()

    # ================================================================== thao tác
    def _mark_dirty(self):
        self._dirty = True

    def _add_testcase(self):
        self.testcases.append(self._blank_testcase())
        self.tabs.setCurrentIndex(0)
        self._refresh_list(select=len(self.testcases) - 1)
        self.f_input.setFocus()

    def _duplicate_testcase(self):
        testcase = self._current_testcase()
        if testcase is None:
            return
        clone = dict(testcase)
        clone["uid"] = self._next_uid()
        clone["id"] = None
        position = self._current + 1
        self.testcases.insert(position, clone)
        self.tabs.setCurrentIndex(0)
        self._refresh_list(select=position)

    def _delete_testcase(self):
        testcase = self._current_testcase()
        if testcase is None:
            return
        answer = QMessageBox.question(
            self,
            "Xác Nhận Xóa Testcase",
            f"Bạn có chắc chắn muốn xóa Testcase {self._current + 1}?\n\n"
            f"- INPUT: {preview_multiline(testcase['input_data'], 60)}\n"
            f"- OUTPUT: {preview_multiline(testcase['expected_output'], 60)}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        if testcase.get("id"):
            self._deleted_ids.append(int(testcase["id"]))
        position = self._current
        del self.testcases[position]
        if not self.testcases:
            self.testcases.append(self._blank_testcase())
            position = 0
        self._mark_dirty()
        self._refresh_list(select=min(position, len(self.testcases) - 1))

    # ================================================================== dán nhiều
    def _preview_paste(self):
        rows = parse_testcase_text(self.txt_paste.toPlainText())
        self._paste_rows = rows
        valid = sum(1 for row in rows if row.is_valid)
        invalid = len(rows) - valid

        self.table_paste.setRowCount(len(rows))
        for index, row in enumerate(rows):
            self.table_paste.setRowHeight(index, 40)
            first = QTableWidgetItem(str(row.index))
            first.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_paste.setItem(index, 0, first)

            input_item = QTableWidgetItem(preview_multiline(row.input_data, 50))
            input_item.setToolTip(preview_tooltip(row.input_data))
            self.table_paste.setItem(index, 1, input_item)

            output_item = QTableWidgetItem(preview_multiline(row.expected_output, 50))
            output_item.setToolTip(preview_tooltip(row.expected_output))
            self.table_paste.setItem(index, 2, output_item)

            status_item = QTableWidgetItem("Hợp lệ" if row.is_valid else row.error)
            status_item.setToolTip(row.error or "Có thể dùng ngay.")
            self.table_paste.setItem(index, 3, status_item)

            if not row.is_valid:
                for column in range(4):
                    cell = self.table_paste.item(index, column)
                    if cell is not None:
                        cell.setBackground(QColor(COLOR_ERROR_BG))
                        cell.setForeground(QColor(COLOR_ERROR))

        self.lbl_paste_result.setText(
            f"{valid} testcase hợp lệ, {invalid} dòng lỗi." if rows else "Chưa có dữ liệu."
        )
        self.lbl_paste_result.setStyleSheet(
            f"font-size: 12px; color: {COLOR_ERROR if invalid else COLOR_SUCCESS};"
        )
        self.btn_add_all.setEnabled(valid > 0)

    def _add_all_pasted(self):
        valid_rows = [row for row in self._paste_rows if row.is_valid]
        if not valid_rows:
            QMessageBox.warning(
                self, "Không Có Testcase Hợp Lệ",
                "Chưa có testcase hợp lệ nào. Bấm \"Xem Trước\" và sửa các dòng báo lỗi trước.",
            )
            return
        for row in valid_rows:
            testcase = self._blank_testcase()
            testcase["input_data"] = row.input_data
            testcase["expected_output"] = row.expected_output
            self.testcases.append(testcase)
        skipped = len(self._paste_rows) - len(valid_rows)
        self._mark_dirty()
        self.tabs.setCurrentIndex(0)
        self._refresh_list(select=len(self.testcases) - len(valid_rows))
        message = f"Đã thêm {len(valid_rows)} testcase."
        if skipped:
            message += (f"\nBỏ qua {skipped} dòng lỗi — xem lại bảng ở tab "
                        "\"Dán Nhiều Testcase\".")
        QMessageBox.information(self, "Đã Thêm Testcase", message)
        self.txt_paste.setPlainText("")
        self.table_paste.setRowCount(0)
        self._paste_rows = []
        self.btn_add_all.setEnabled(False)
        self.lbl_paste_result.setText("")

    # ================================================================== lưu
    def _validate(self):
        errors: List[str] = []
        first_invalid = -1
        saveable = [(i, tc) for i, tc in enumerate(self.testcases) if not self._is_placeholder(tc)]
        if not saveable:
            return ["Chưa có testcase nào — hãy nhập đầu vào/kết quả kỳ vọng trước khi lưu."], 0
        for index, testcase in saveable:
            prefix = f"Testcase {index + 1}"
            if not (testcase["expected_output"] or "").strip():
                errors.append(f"{prefix}: Kết quả kỳ vọng (stdout) không được để trống.")
                if first_invalid < 0:
                    first_invalid = index
            if float(testcase["score_weight"]) <= 0:
                errors.append(f"{prefix}: Trọng số điểm phải lớn hơn 0.")
                if first_invalid < 0:
                    first_invalid = index
            for key, label in (("time_limit_ms", "Giới hạn thời gian"),
                               ("memory_limit_mb", "Giới hạn bộ nhớ")):
                if int(testcase[key]) <= 0:
                    errors.append(f"{prefix}: {label} phải lớn hơn 0.")
                    if first_invalid < 0:
                        first_invalid = index
            for key, label in (("input_data", "Dữ liệu đầu vào"),
                               ("expected_output", "Kết quả kỳ vọng")):
                if len((testcase[key] or "").encode("utf-8")) > MAX_DATA_BYTES:
                    errors.append(f"{prefix}: {label} vượt quá giới hạn 256 KB.")
                    if first_invalid < 0:
                        first_invalid = index
        return errors, first_invalid

    def _save(self, keep_open: bool) -> bool:
        errors, first_invalid = self._validate()
        if errors:
            if first_invalid >= 0:
                self._refresh_list(select=first_invalid)
            shown = errors[:10]
            if len(errors) > len(shown):
                shown.append(f"... và {len(errors) - len(shown)} lỗi khác.")
            QMessageBox.warning(
                self, "Dữ Liệu Không Hợp Lệ",
                "Vui lòng kiểm tra lại cấu hình testcase:\n\n• " + "\n• ".join(shown),
            )
            return False

        self._remember_current()

        if self._legacy_single:
            testcase = self.testcases[0]
            self.testcase_data = {
                "question_number": self.question_number,
                "input_data": testcase["input_data"],
                "expected_output": testcase["expected_output"],
                "score_weight": float(testcase["score_weight"]),
                "time_limit_ms": int(testcase["time_limit_ms"]),
                "memory_limit_mb": int(testcase["memory_limit_mb"]),
            }
            self._dirty = False
            self.accept()
            return True

        try:
            self._persist()
        except Exception as ex:  # pragma: no cover - phụ thuộc SQLite
            logger.error("Lỗi lưu testcase: %s", ex)
            QMessageBox.critical(self, "Lỗi Lưu CSDL", f"Không thể lưu testcase:\n{ex}")
            return False

        self._dirty = False
        self.saved_count = len(self._saveable_testcases())
        if self.testcases:
            self.testcase_data = dict(self.testcases[0])
        if keep_open:
            self.testcases.append(self._blank_testcase())
            self._refresh_list(select=len(self.testcases) - 1)
            self.f_input.setFocus()
            return True
        self.accept()
        return True

    def _remember_current(self):
        """Đồng bộ testcase đang chọn lần cuối trước khi ghi CSDL."""
        testcase = self._current_testcase()
        if testcase is None:
            return
        testcase["input_data"] = self.f_input.text()
        testcase["expected_output"] = self.f_output.text()
        testcase["score_weight"] = float(self.sp_weight.value())
        testcase["override_limits"] = self.chk_override.isChecked()
        if testcase["override_limits"]:
            testcase["time_limit_ms"] = int(self.sp_time.value())
            testcase["memory_limit_mb"] = int(self.sp_mem.value())
        else:
            testcase["time_limit_ms"] = int(self.q_time)
            testcase["memory_limit_mb"] = int(self.q_mem)

    def _persist(self):
        for testcase_id in self._deleted_ids:
            self.db.delete_testcase(testcase_id)
        self._deleted_ids = []

        for testcase in self._saveable_testcases():
            if testcase.get("id"):
                self.db.update_testcase(
                    testcase_id=int(testcase["id"]),
                    question_number=self.question_number,
                    input_data=testcase["input_data"],
                    expected_output=testcase["expected_output"],
                    score_weight=float(testcase["score_weight"]),
                    time_limit_ms=int(testcase["time_limit_ms"]),
                    memory_limit_mb=int(testcase["memory_limit_mb"]),
                )
            else:
                testcase["id"] = self.db.add_testcase(
                    class_id=self.class_id,
                    input_data=testcase["input_data"],
                    expected_output=testcase["expected_output"],
                    score_weight=float(testcase["score_weight"]),
                    time_limit_ms=int(testcase["time_limit_ms"]),
                    memory_limit_mb=int(testcase["memory_limit_mb"]),
                    matching_strategy=self.matching_strategy,
                    question_number=self.question_number,
                )
        self._apply_display_order()

    def _saveable_testcases(self) -> List[Dict[str, Any]]:
        return [testcase for testcase in self.testcases if not self._is_placeholder(testcase)]

    def _apply_display_order(self):
        """Ghi lại thứ tự hiển thị vào CSDL mà KHÔNG thêm cột mới.

        Bảng `local_test_cases` không có cột thứ tự và `get_testcases_by_class`
        sắp theo id, nên nếu người dùng kéo thả đổi thứ tự, ta ghi nội dung theo
        đúng dãy id hiện có của câu hỏi; số bản ghi không đổi nên không ảnh
        hưởng dữ liệu khác.
        """
        saveable = self._saveable_testcases()
        rows = [
            row for row in self.db.get_testcases_by_class(self.class_id)
            if str(row.get("question_number", "")).upper() == self.question_number.upper()
        ]
        ids = [int(row["id"]) for row in rows]
        if len(ids) != len(saveable):
            return
        if ids == [int(tc["id"]) for tc in saveable if tc.get("id")]:
            return

        current = {int(row["id"]): row for row in rows}
        for row_id, testcase in zip(ids, saveable):
            if not self._same_content(current.get(row_id, {}), testcase):
                self.db.update_testcase(
                    testcase_id=row_id,
                    question_number=self.question_number,
                    input_data=testcase["input_data"],
                    expected_output=testcase["expected_output"],
                    score_weight=float(testcase["score_weight"]),
                    time_limit_ms=int(testcase["time_limit_ms"]),
                    memory_limit_mb=int(testcase["memory_limit_mb"]),
                )
            testcase["id"] = row_id

    def _same_content(self, row: Dict[str, Any], testcase: Dict[str, Any]) -> bool:
        """So sánh nhanh một bản ghi CSDL với testcase trong bộ nhớ."""
        if not row:
            return False
        return (
            str(row.get("question_number", "")).upper() == self.question_number.upper()
            and (row.get("input_data") or "") == testcase["input_data"]
            and (row.get("expected_output") or "") == testcase["expected_output"]
            and float(row.get("score_weight") or 0.0) == float(testcase["score_weight"])
            and int(row.get("time_limit_ms") or 0) == int(testcase["time_limit_ms"])
            and int(row.get("memory_limit_mb") or 0) == int(testcase["memory_limit_mb"])
        )

    # ================================================================== đóng
    def _confirm_discard(self) -> bool:
        if not self._dirty:
            return True
        answer = QMessageBox.question(
            self,
            "Thay Đổi Chưa Lưu",
            "Bạn có thay đổi chưa lưu trong bộ testcase này.\n\n"
            "Chọn \"Yes\" để thoát và bỏ các thay đổi, \"No\" để quay lại lưu tiếp.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return answer == QMessageBox.StandardButton.Yes

    def reject(self):  # noqa: D401 - Qt API
        if self._confirm_discard():
            super().reject()

    def closeEvent(self, event):  # noqa: N802 - Qt API
        if self._confirm_discard():
            event.accept()
        else:
            event.ignore()


# ==============================================================================
# 2. HỘP THOẠI SINH TESTCASE BẰNG AI (MODAL RIÊNG BIỆT)
# ==============================================================================
class AiTestcaseDialog(QDialog):
    """
    Hộp thoại sinh testcase bằng AI.
    Giao diện tinh gọn:
    - Ô Đề bài
    - Số lượng testcase
    - Nút chính: Sinh Testcase
    - Nút phụ: Hủy
    - Tùy chọn thu gọn: Câu hỏi, Ngôn ngữ
    - Bảng kết quả kèm checkbox từng dòng
    - Thông báo lỗi thân thiện, không lộ mã nội bộ
    """

    def __init__(
        self,
        parent=None,
        class_id: Optional[int] = None,
        default_question: str = "Q1",
        default_language: str = "C",
        matching_strategy: str = "IGNORE_WHITESPACE"
    ):
        super().__init__(parent)
        self.class_id = class_id
        self.matching_strategy = matching_strategy
        self.db = DatabaseManager()

        # Xác định ngôn ngữ mặc định từ thông tin đợt chấm
        self.default_language = default_language
        if self.class_id:
            cls_info = self.db.get_class_by_id(self.class_id)
            if cls_info and cls_info.get("programming_language"):
                self.default_language = cls_info["programming_language"]

        self.default_question = default_question or "Q1"
        self.generated_testcases: List[Dict[str, Any]] = []
        self.ai_worker: Optional[AiTestcaseWorker] = None

        self.setWindowTitle("Sinh Testcase Bằng AI")
        self.setMinimumSize(720, 560)
        self.resize(780, 620)
        self.setStyleSheet(LIGHT_THEME_QSS)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # 1. Ô Đề bài
        v_prompt = QVBoxLayout()
        v_prompt.setSpacing(8)

        prompt_head = QHBoxLayout()
        prompt_head.setSpacing(8)

        lbl_prompt = QLabel("Đề bài:", self)
        lbl_prompt.setStyleSheet(f"font-weight: 600; font-size: 13px; line-height: 1.4; color: {COLOR_TEXT_PRIMARY};")
        prompt_head.addWidget(lbl_prompt)
        prompt_head.addStretch(1)

        # Nút nhập đề bài từ file Word / PDF / văn bản để AI sinh testcase
        self.btn_import_doc = QPushButton("Nhập Từ File Đề Bài", self)
        self.btn_import_doc.setProperty("class", "SecondaryBtn")
        self.btn_import_doc.setFixedHeight(32)
        self.btn_import_doc.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_import_doc.setToolTip(
            "Nhập đề bài từ file Word (.docx), PDF (.pdf) hoặc văn bản (.txt, .md) "
            "để AI sinh testcase."
        )
        self.btn_import_doc.clicked.connect(self._import_problem_document)
        prompt_head.addWidget(self.btn_import_doc)

        v_prompt.addLayout(prompt_head)

        self.txt_prompt = QTextEdit(self)
        self.txt_prompt.setFixedHeight(85)
        self.txt_prompt.setPlaceholderText("Dán nội dung đề bài hoặc định dạng đầu vào và đầu ra cần sinh testcase...")
        self.txt_prompt.setStyleSheet("""
            QTextEdit {
                font-family: Consolas, monospace;
                font-size: 13px;
                line-height: 1.4;
                padding: 8px;
            }
        """)
        v_prompt.addWidget(self.txt_prompt)

        self.lbl_doc_name = QLabel("", self)
        self.lbl_doc_name.setStyleSheet(f"font-size: 11px; color: {COLOR_TEXT_SECONDARY};")
        self.lbl_doc_name.setWordWrap(True)
        self.lbl_doc_name.setVisible(False)
        v_prompt.addWidget(self.lbl_doc_name)

        layout.addLayout(v_prompt)

        # 2. Hàng điều khiển: Số lượng testcase + Tùy chọn thu gọn + Nút Sinh / Hủy
        row_ctrl = QHBoxLayout()
        row_ctrl.setSpacing(12)
        row_ctrl.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        lbl_count = QLabel("Số lượng testcase:", self)
        lbl_count.setStyleSheet(f"font-size: 13px; line-height: 1.4; color: {COLOR_TEXT_PRIMARY};")
        row_ctrl.addWidget(lbl_count)

        self.spin_count = QSpinBox(self)
        self.spin_count.setFixedHeight(36)
        self.spin_count.setRange(1, 10)
        self.spin_count.setValue(4)
        self.spin_count.setStyleSheet("QSpinBox { min-height: 36px; padding: 4px 8px; font-size: 13px; }")
        row_ctrl.addWidget(self.spin_count)

        self.btn_toggle_opt = QPushButton("Tùy chọn", self)
        self.btn_toggle_opt.setProperty("class", "SecondaryBtn")
        self.btn_toggle_opt.setFixedHeight(36)
        self.btn_toggle_opt.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_toggle_opt.setCheckable(True)
        self.btn_toggle_opt.toggled.connect(self._toggle_options)
        row_ctrl.addWidget(self.btn_toggle_opt)

        row_ctrl.addStretch(1)

        # Nút Thử Lại (ẩn mặc định, chỉ hiện khi lỗi)
        self.btn_retry = QPushButton("Thử Lại", self)
        self.btn_retry.setProperty("class", "SecondaryBtn")
        self.btn_retry.setFixedHeight(36)
        self.btn_retry.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_retry.setVisible(False)
        self.btn_retry.clicked.connect(self._start_generation)
        row_ctrl.addWidget(self.btn_retry)

        # Nút Hủy
        btn_cancel = QPushButton("Hủy", self)
        btn_cancel.setProperty("class", "SecondaryBtn")
        btn_cancel.setFixedHeight(36)
        btn_cancel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_cancel.clicked.connect(self.reject)
        row_ctrl.addWidget(btn_cancel)

        # Nút chính Sinh Testcase
        self.btn_submit = QPushButton("Sinh Testcase", self)
        self.btn_submit.setProperty("class", "PrimaryBtn")
        self.btn_submit.setFixedHeight(36)
        self.btn_submit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_submit.clicked.connect(self._start_generation)
        row_ctrl.addWidget(self.btn_submit)

        layout.addLayout(row_ctrl)

        # 3. Khung Tùy chọn thu gọn (Ngôn ngữ & Câu hỏi)
        self.frame_options = QFrame(self)
        self.frame_options.setProperty("class", "Card")
        self.frame_options.setVisible(False)
        opt_layout = QHBoxLayout(self.frame_options)
        opt_layout.setContentsMargins(14, 10, 14, 10)
        opt_layout.setSpacing(16)

        lbl_opt_q = QLabel("Câu hỏi áp dụng:", self.frame_options)
        lbl_opt_q.setStyleSheet(f"font-size: 13px; color: {COLOR_TEXT_PRIMARY};")
        opt_layout.addWidget(lbl_opt_q)

        self.cb_question = QComboBox(self.frame_options)
        self.cb_question.setFixedHeight(34)
        self.cb_question.addItems(["Q1", "Q2", "Q3", "Q4", "Q5"])
        q_idx = self.cb_question.findText(self.default_question)
        if q_idx >= 0:
            self.cb_question.setCurrentIndex(q_idx)
        opt_layout.addWidget(self.cb_question)

        lbl_opt_lang = QLabel("Ngôn ngữ lập trình:", self.frame_options)
        lbl_opt_lang.setStyleSheet(f"font-size: 13px; color: {COLOR_TEXT_PRIMARY};")
        opt_layout.addWidget(lbl_opt_lang)

        self.cb_language = QComboBox(self.frame_options)
        self.cb_language.setFixedHeight(34)
        self.cb_language.addItems(["C", "Java", "Python", "Web"])
        lang_idx = self.cb_language.findText(self.default_language, Qt.MatchFlag.MatchFixedString)
        if lang_idx >= 0:
            self.cb_language.setCurrentIndex(lang_idx)
        opt_layout.addWidget(self.cb_language)

        opt_layout.addStretch(1)
        layout.addWidget(self.frame_options)

        # 4. Dòng trạng thái / Thông báo lỗi thân thiện
        self.lbl_status = QLabel("", self)
        self.lbl_status.setStyleSheet(f"font-size: 13px; line-height: 1.4; color: {COLOR_TEXT_SECONDARY};")
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setVisible(False)
        layout.addWidget(self.lbl_status)

        # 5. Bảng hiển thị kết quả AI (Input, Expected Output, Checkbox)
        v_table = QVBoxLayout()
        v_table.setSpacing(8)

        lbl_tbl_title = QLabel("Kết quả testcase đề xuất:", self)
        lbl_tbl_title.setStyleSheet(f"font-weight: 600; font-size: 13px; line-height: 1.4; color: {COLOR_TEXT_PRIMARY};")
        v_table.addWidget(lbl_tbl_title)

        self.table_result = QTableWidget(self)
        self.table_result.setColumnCount(3)
        self.table_result.setHorizontalHeaderLabels(["Chọn", "Input (Đầu vào)", "Expected Output (Đầu ra kỳ vọng)"])
        r_header = self.table_result.horizontalHeader()
        r_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        r_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        r_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table_result.setColumnWidth(0, 56)
        self.table_result.verticalHeader().setVisible(False)
        self.table_result.setShowGrid(True)
        self.table_result.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        v_table.addWidget(self.table_result)

        layout.addLayout(v_table, stretch=1)

        # 6. Chân hộp thoại AI: Thao tác chọn & Nút Thêm Các Testcase Đã Chọn
        footer_ai = QHBoxLayout()
        footer_ai.setSpacing(12)

        self.btn_select_all = QPushButton("Chọn Tất Cả", self)
        self.btn_select_all.setProperty("class", "SecondaryBtn")
        self.btn_select_all.setFixedHeight(34)
        self.btn_select_all.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_select_all.setEnabled(False)
        self.btn_select_all.clicked.connect(self._select_all_rows)
        footer_ai.addWidget(self.btn_select_all)

        self.btn_deselect_all = QPushButton("Bỏ Chọn Tất Cả", self)
        self.btn_deselect_all.setProperty("class", "SecondaryBtn")
        self.btn_deselect_all.setFixedHeight(34)
        self.btn_deselect_all.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_deselect_all.setEnabled(False)
        self.btn_deselect_all.clicked.connect(self._deselect_all_rows)
        footer_ai.addWidget(self.btn_deselect_all)

        footer_ai.addStretch(1)

        # Nút Thêm Các Testcase Đã Chọn (disable khi chưa có kết quả)
        self.btn_add_selected = QPushButton("Thêm Các Testcase Đã Chọn", self)
        self.btn_add_selected.setProperty("class", "PrimaryBtn")
        self.btn_add_selected.setFixedHeight(36)
        self.btn_add_selected.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_add_selected.setEnabled(False)
        self.btn_add_selected.clicked.connect(self._add_selected_testcases)
        footer_ai.addWidget(self.btn_add_selected)

        layout.addLayout(footer_ai)

    def _toggle_options(self, checked: bool):
        self.frame_options.setVisible(checked)

    def _import_problem_document(self):
        """Loads a problem statement from a Word/PDF/text file into the prompt box."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn File Đề Bài",
            str(Path.home()),
            "Đề bài (*.docx *.pdf *.txt *.md *.csv *.log);;"
            "Word (*.docx);;PDF (*.pdf);;Văn bản (*.txt *.md *.csv *.log);;Tất cả (*.*)"
        )
        if not file_path:
            return

        try:
            text = read_document_text(file_path)
        except DocumentReadError as ex:
            QMessageBox.warning(self, "Không Đọc Được File", str(ex))
            return
        except Exception as ex:
            QMessageBox.warning(self, "Lỗi Đọc File", f"Không thể đọc file đề bài:\n{ex}")
            return

        if not text.strip():
            QMessageBox.warning(
                self, "File Rỗng",
                "Không tìm thấy nội dung văn bản trong file đã chọn."
            )
            return

        existing = self.txt_prompt.toPlainText().strip()
        if existing:
            choice = QMessageBox.question(
                self,
                "Ô Đề Bài Đã Có Nội Dung",
                "Ô đề bài hiện đang có nội dung.\n\n"
                "Chọn 'Yes' để THAY THẾ bằng nội dung file vừa chọn.\n"
                "Chọn 'No' để NỐI THÊM vào cuối nội dung hiện tại.",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes
            )
            if choice == QMessageBox.StandardButton.Cancel:
                return
            if choice == QMessageBox.StandardButton.No:
                text = f"{existing}\n\n{text}"

        note = ""
        if len(text) > MAX_PROBLEM_CHARS:
            text = text[:MAX_PROBLEM_CHARS]
            note = f" — chỉ dùng {MAX_PROBLEM_CHARS:,} ký tự đầu (giới hạn máy chủ AI)"
            QMessageBox.information(
                self,
                "Đề Bài Quá Dài",
                f"Nội dung file vượt quá {MAX_PROBLEM_CHARS:,} ký tự.\n"
                "Chỉ phần đầu được đưa vào để sinh testcase."
            )

        self.txt_prompt.setPlainText(text)
        self.lbl_doc_name.setText(
            f"Đã nhập đề bài từ: {Path(file_path).name} ({len(text):,} ký tự){note}"
        )
        self.lbl_doc_name.setVisible(True)

    def _start_generation(self):
        prompt = self.txt_prompt.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Thiếu Thông Tin", "Vui lòng nhập mô tả hoặc yêu cầu đề bài trước khi sinh testcase.")
            return

        lang = self.cb_language.currentText()
        count = self.spin_count.value()

        self.btn_submit.setEnabled(False)
        self.btn_submit.setText("Đang Sinh...")
        self.btn_retry.setVisible(False)
        self.btn_add_selected.setEnabled(False)
        self.btn_select_all.setEnabled(False)
        self.btn_deselect_all.setEnabled(False)

        self.lbl_status.setVisible(True)
        self.lbl_status.setText("Đang kết nối dịch vụ AI để phân tích đề bài và sinh testcase...")
        self.lbl_status.setStyleSheet(f"font-size: 13px; line-height: 1.4; color: {COLOR_PRIMARY};")

        self.table_result.setRowCount(0)
        self.generated_testcases.clear()

        self.ai_worker = AiTestcaseWorker(prompt, lang, count, True)
        self.ai_worker.finished.connect(self._on_generation_finished)
        self.ai_worker.start()

    def _on_generation_finished(self, result: Dict[str, Any]):
        self.btn_submit.setEnabled(True)
        self.btn_submit.setText("Sinh Testcase")

        if result.get("success"):
            tcs = result.get("testcases", [])
            self.generated_testcases = tcs
            self._render_results_table(tcs)

            self.lbl_status.setVisible(True)
            self.lbl_status.setText(f"Đã sinh thành công {len(tcs)} testcase. Hãy đánh dấu chọn các testcase phù hợp để thêm vào đợt chấm.")
            self.lbl_status.setStyleSheet("font-size: 13px; line-height: 1.4; color: #15803d;")

            self.btn_retry.setVisible(False)
            has_data = len(tcs) > 0
            self.btn_select_all.setEnabled(has_data)
            self.btn_deselect_all.setEnabled(has_data)
            self._update_add_button_state()
        else:
            err_code = result.get("error_code", "")
            err_detail = result.get("message", "")
            logger.warning("Lỗi dịch vụ AI sinh testcase: code=%s, detail=%s", err_code, err_detail)

            # Nói rõ nguyên nhân thay vì câu chung "không kết nối được": trước đây mọi
            # lỗi (hết hạn mức, server thiếu API key, token hết hạn...) đều hiện cùng
            # một câu nên giảng viên không biết phải làm gì.
            self.lbl_status.setVisible(True)
            self.lbl_status.setText(self._ai_error_message(result))
            self.lbl_status.setStyleSheet("font-size: 13px; line-height: 1.4; color: #b91c1c;")

            self.btn_retry.setVisible(True)
            self.btn_add_selected.setEnabled(False)
            self.btn_select_all.setEnabled(False)
            self.btn_deselect_all.setEnabled(False)

    # Mã lỗi backend -> lời giải thích cho giảng viên (kèm cách xử lý).
    _AI_ERROR_HINTS = {
        "AI_NOT_CONFIGURED": "Máy chủ chưa cấu hình API key AI (OPENROUTER_API_KEYS). Báo quản trị viên backend.",
        "AI_QUOTA_NOT_CONFIGURED": "Tài khoản chưa được cấp hạn mức AI. Báo quản trị viên cấu hình quota.",
        "AI_QUOTA_EXCEEDED": "Đã dùng hết hạn mức token AI trong ngày. Thử lại vào ngày mai hoặc nhập testcase thủ công.",
        "AI_PROVIDER_RATE_LIMITED": "Nhà cung cấp AI đang giới hạn số yêu cầu. Chờ 1-2 phút rồi thử lại.",
        "AI_PROVIDER_ERROR": "Nhà cung cấp AI không phản hồi (model có thể đang quá tải). Thử lại hoặc đổi model.",
        "AI_INVALID_RESPONSE": "AI trả về dữ liệu không đúng định dạng. Thử lại với đề bài rõ ràng hơn.",
        "CONNECT_ERROR": "Không kết nối được máy chủ backend. Kiểm tra mạng, hoặc server đang khởi động lại.",
        "CONNECT_TIMEOUT": "Máy chủ backend phản hồi quá chậm (server có thể đang ngủ). Thử lại sau ~30 giây.",
        "AUTH_INVALID_TOKEN": "Phiên đăng nhập đã hết hạn. Đăng nhập lại rồi thử lại.",
        "AUTH_TOKEN_EXPIRED": "Phiên đăng nhập đã hết hạn. Đăng nhập lại rồi thử lại.",
        "VALIDATION_FAILED": "Đề bài chưa đủ dài hoặc sai định dạng yêu cầu.",
        "TOO_MANY_REQUESTS": "Bạn thao tác quá nhanh. Chờ vài giây rồi thử lại.",
    }

    @classmethod
    def _ai_error_message(cls, result: Dict[str, Any]) -> str:
        """Dịch kết quả lỗi của backend thành câu tiếng Việt chỉ rõ nguyên nhân."""
        code = str(result.get("error_code", "") or "").strip().upper()
        hint = cls._AI_ERROR_HINTS.get(code)
        if not hint:
            hint = str(result.get("message", "") or "").strip() or "Không rõ nguyên nhân."
        return f"Không sinh được testcase: {hint} (mã lỗi: {code or 'UNKNOWN'})"

    def _render_results_table(self, testcases: List[Dict[str, Any]]):
        self.table_result.setRowCount(len(testcases))
        for r, tc in enumerate(testcases):
            self.table_result.setRowHeight(r, 44)

            # Cột 0: Checkbox chọn dòng
            chk_widget = QWidget(self.table_result)
            chk_layout = QHBoxLayout(chk_widget)
            chk_layout.setContentsMargins(0, 0, 0, 0)
            chk_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            chk = QCheckBox(chk_widget)
            chk.setChecked(True)
            chk.stateChanged.connect(self._update_add_button_state)
            chk_layout.addWidget(chk)
            self.table_result.setCellWidget(r, 0, chk_widget)

            # Cột 1: Input (Đầu vào)
            inp_text = str(tc.get("input", ""))
            it_inp = QTableWidgetItem(inp_text if inp_text else "(trống)")
            it_inp.setToolTip(inp_text)
            it_inp.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table_result.setItem(r, 1, it_inp)

            # Cột 2: Expected Output (Đầu ra kỳ vọng)
            out_text = str(tc.get("expected_output", ""))
            it_out = QTableWidgetItem(out_text if out_text else "(trống)")
            it_out.setToolTip(out_text)
            it_out.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table_result.setItem(r, 2, it_out)

    def _get_checkbox_at(self, row: int) -> Optional[QCheckBox]:
        w = self.table_result.cellWidget(row, 0)
        if w:
            return w.findChild(QCheckBox)
        return None

    def _select_all_rows(self):
        for r in range(self.table_result.rowCount()):
            chk = self._get_checkbox_at(r)
            if chk:
                chk.setChecked(True)
        self._update_add_button_state()

    def _deselect_all_rows(self):
        for r in range(self.table_result.rowCount()):
            chk = self._get_checkbox_at(r)
            if chk:
                chk.setChecked(False)
        self._update_add_button_state()

    def _update_add_button_state(self):
        selected_count = 0
        for r in range(self.table_result.rowCount()):
            chk = self._get_checkbox_at(r)
            if chk and chk.isChecked():
                selected_count += 1
        self.btn_add_selected.setEnabled(selected_count > 0)

    def _add_selected_testcases(self):
        if not self.class_id:
            classes = self.db.get_all_classes()
            if classes:
                self.class_id = classes[0]["id"]

        if not self.class_id:
            QMessageBox.warning(self, "Chưa Chọn Đợt Chấm", "Không xác định được đợt thi hiện tại để lưu testcase.")
            return

        target_q = self.cb_question.currentText().strip() or "Q1"
        added_count = 0

        for r in range(self.table_result.rowCount()):
            chk = self._get_checkbox_at(r)
            if chk and chk.isChecked() and r < len(self.generated_testcases):
                tc = self.generated_testcases[r]
                inp = str(tc.get("input", ""))
                outp = str(tc.get("expected_output", ""))
                try:
                    self.db.add_testcase(
                        class_id=self.class_id,
                        input_data=inp,
                        expected_output=outp,
                        score_weight=1.0,
                        time_limit_ms=1000,
                        matching_strategy=self.matching_strategy,
                        question_number=target_q
                    )
                    added_count += 1
                except Exception as ex:
                    logger.error("Lỗi khi thêm testcase vào CSDL: %s", str(ex))

        if added_count > 0:
            QMessageBox.information(
                self,
                "Đã Thêm Testcase",
                f"Đã thêm thành công {added_count} testcase vào câu {target_q}."
            )
            self.accept()
        else:
            QMessageBox.warning(self, "Chưa Chọn", "Vui lòng chọn ít nhất một testcase để thêm.")


# ==============================================================================
# 3. HỘP THOẠI QUẢN LÝ BỘ TESTCASE & CHIẾN LƯỢC SO KHỚP (2 TAB NGANG HÀNG)
# ==============================================================================
class TestcaseDialog(QDialog):
    """
    Cửa sổ Quản Lý Bộ Testcase & Chiến Lược So Khớp.
    Cấu trúc:
    - Tab 1: Testcase (mặc định mở)
    - Tab 2: So Khớp Đầu Ra (6 tiêu chí thuần tiếng Việt kèm tooltip)
    - Chân trang: Duy nhất 1 nút chính "Lưu" (nền xanh đặc), các nút khác dùng kiểu viền.
    """

    def __init__(self, parent=None, class_id: Optional[int] = None, is_wizard: bool = False):
        super().__init__(parent)
        self.is_wizard = is_wizard
        self.nav_back = False

        title = "Bước 3/3: Quản Lý Bộ Testcase & Chiến Lược So Khớp" if is_wizard else "Quản Lý Bộ Testcase & Chiến Lược So Khớp"
        self.setWindowTitle(title)

        screen = QGuiApplication.primaryScreen()
        if screen:
            avail = screen.availableGeometry()
            target_w = min(1140, avail.width() - 40)
            target_h = min(740, avail.height() - 50)
            self.setMinimumSize(min(960, target_w), min(600, target_h))
            self.resize(target_w, target_h)
            self.move(
                avail.x() + (avail.width() - target_w) // 2,
                avail.y() + (avail.height() - target_h) // 2
            )
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
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Hai tab ngang hàng: Testcase và So Khớp Đầu Ra
        self.tabs = QTabWidget(self)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: #ffffff;
                top: -1px;
            }
            QTabBar::tab {
                font-size: 13px;
                font-weight: 600;
                line-height: 1.4;
                padding: 10px 20px;
                margin-right: 4px;
                color: #475569;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                border: 1px solid transparent;
            }
            QTabBar::tab:selected {
                color: #0284c7;
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-bottom: 2px solid #0284c7;
            }
            QTabBar::tab:hover:!selected {
                color: #0f172a;
                background-color: #f8fafc;
            }
        """)

        # TAB 1: Testcase (mặc định mở)
        tab_tc = QWidget()
        tl_layout = QVBoxLayout(tab_tc)
        tl_layout.setContentsMargins(16, 16, 16, 16)
        tl_layout.setSpacing(16)

        # Thanh công cụ đầu tab Testcase
        tool_row = QHBoxLayout()
        tool_row.setSpacing(12)
        tool_row.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        lbl_f = QLabel("Lọc theo câu hỏi:", tab_tc)
        lbl_f.setStyleSheet(f"font-size: 13px; line-height: 1.4; color: {COLOR_TEXT_PRIMARY};")
        tool_row.addWidget(lbl_f)

        self.cb_question = QComboBox(tab_tc)
        self.cb_question.setFixedHeight(36)
        self.cb_question.setMinimumWidth(150)
        self.cb_question.addItems(["Tất cả câu hỏi", "Q1", "Q2", "Q3", "Q4", "Q5"])
        self.cb_question.currentIndexChanged.connect(self._filter_testcases)
        tool_row.addWidget(self.cb_question)

        tool_row.addStretch(1)

        # Nút viền: Sinh Testcase Bằng AI
        self.btn_ai_gen = QPushButton("Sinh Testcase Bằng AI", tab_tc)
        self.btn_ai_gen.setProperty("class", "SecondaryBtn")
        self.btn_ai_gen.setFixedHeight(36)
        self.btn_ai_gen.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_ai_gen.clicked.connect(self._open_ai_dialog)
        tool_row.addWidget(self.btn_ai_gen)

        # Nút viền: Thêm Testcase
        self.btn_add_tc = QPushButton("Thêm Testcase", tab_tc)
        self.btn_add_tc.setProperty("class", "SecondaryBtn")
        self.btn_add_tc.setFixedHeight(36)
        self.btn_add_tc.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_add_tc.clicked.connect(self._add_testcase)
        tool_row.addWidget(self.btn_add_tc)

        tl_layout.addLayout(tool_row)

        # UX tổng trọng số: GV thấy ngay bảng quy đổi về thang 10 mà không phải chấm thử
        total_row = QHBoxLayout()
        total_row.addStretch(1)
        self.lbl_tc_total = QLabel("", tab_tc)
        self.lbl_tc_total.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_SECONDARY}; line-height: 1.4;")
        total_row.addWidget(self.lbl_tc_total)
        tl_layout.addLayout(total_row)

        # Bảng danh sách Testcase
        self.table_tc = QTableWidget(tab_tc)
        self.table_tc.setColumnCount(9)
        self.table_tc.setHorizontalHeaderLabels([
            "#", "Câu Hỏi", "INPUT (stdin)", "OUTPUT (stdout)",
            "Trọng Số", "Giới Hạn (ms)", "RAM (MB)", "Chiến Lược", "Thao Tác"
        ])
        t_header = self.table_tc.horizontalHeader()
        t_header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        t_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        t_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        t_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        t_header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        t_header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        t_header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        t_header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        t_header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        t_header.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)

        self.table_tc.setColumnWidth(0, 44)
        self.table_tc.setColumnWidth(1, 75)
        self.table_tc.setColumnWidth(4, 80)
        self.table_tc.setColumnWidth(5, 115)
        self.table_tc.setColumnWidth(6, 90)
        self.table_tc.setColumnWidth(7, 130)
        self.table_tc.setColumnWidth(8, 150)

        # Căn lề tiêu đề cột khớp với nội dung
        for col_idx in range(9):
            it_hdr = self.table_tc.horizontalHeaderItem(col_idx)
            if it_hdr:
                if col_idx in (2, 3):
                    it_hdr.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                else:
                    it_hdr.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        # Đặt tooltip cho cột OUTPUT
        it_out_hdr = self.table_tc.horizontalHeaderItem(3)
        if it_out_hdr:
            it_out_hdr.setToolTip("Kết quả kỳ vọng (stdout)")

        self.table_tc.verticalHeader().setVisible(False)
        self.table_tc.verticalHeader().setDefaultSectionSize(52)
        self.table_tc.setShowGrid(True)
        self.table_tc.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tl_layout.addWidget(self.table_tc)

        self.tabs.addTab(tab_tc, "Testcase")

        # TAB 2: So Khớp Đầu Ra
        tab_match = QWidget()
        tm_layout = QVBoxLayout(tab_match)
        tm_layout.setContentsMargins(20, 20, 20, 20)
        tm_layout.setSpacing(16)

        strat_card = QFrame(tab_match)
        strat_card.setProperty("class", "Card")
        s_layout = QVBoxLayout(strat_card)
        s_layout.setContentsMargins(20, 18, 20, 18)
        s_layout.setSpacing(16)

        lbl_strat_title = QLabel("Tiêu chí so khớp đầu ra chương trình:", strat_card)
        lbl_strat_title.setStyleSheet(f"font-weight: 600; font-size: 14px; line-height: 1.4; color: {COLOR_TEXT_PRIMARY};")
        s_layout.addWidget(lbl_strat_title)

        # Dòng mẹo viết lại ngắn, chữ #475569, 13px, line-height 1.4
        lbl_hint = QLabel(
            "Mẹo: Bỏ chọn tất cả để so khớp chính xác tuyệt đối từng ký tự. Các tiêu chí được chọn sẽ tự động kết hợp xử lý.",
            strat_card
        )
        lbl_hint.setStyleSheet("font-size: 13px; color: #475569; line-height: 1.4;")
        lbl_hint.setWordWrap(True)
        s_layout.addWidget(lbl_hint)

        # Lưới 6 checkbox thuần tiếng Việt, tooltip chi tiết
        grid_strat = QGridLayout()
        grid_strat.setHorizontalSpacing(24)
        grid_strat.setVerticalSpacing(16)

        cb_style = f"""
            QCheckBox {{
                font-size: 13px;
                color: {COLOR_TEXT_PRIMARY};
                font-weight: 500;
                line-height: 1.4;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
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

        # 1. Bỏ qua khoảng trắng (mặc định chọn)
        self.chk_whitespace = QCheckBox("Bỏ qua khoảng trắng", strat_card)
        self.chk_whitespace.setToolTip("Bỏ qua khoảng trắng thừa và ký tự xuống dòng ở đầu, cuối và giữa các từ (Ignore Whitespace)")
        self.chk_whitespace.setChecked(True)
        self.chk_whitespace.setStyleSheet(cb_style)
        self.chk_whitespace.stateChanged.connect(self._on_matching_flags_changed)
        grid_strat.addWidget(self.chk_whitespace, 0, 0)

        # 2. Không phân biệt chữ hoa, chữ thường
        self.chk_case = QCheckBox("Không phân biệt chữ hoa, chữ thường", strat_card)
        self.chk_case.setToolTip("Không phân biệt ký tự in hoa và in thường (Case Insensitive)")
        self.chk_case.setStyleSheet(cb_style)
        self.chk_case.stateChanged.connect(self._on_matching_flags_changed)
        grid_strat.addWidget(self.chk_case, 0, 1)

        # 3. Chấp nhận dung sai số thực
        self.chk_float = QCheckBox("Chấp nhận dung sai số thực", strat_card)
        self.chk_float.setToolTip("Chấp nhận sai số dấu phẩy động với độ lệch cho phép nhỏ hơn hoặc bằng 1e-5 (Float Tolerance)")
        self.chk_float.setStyleSheet(cb_style)
        self.chk_float.stateChanged.connect(self._on_matching_flags_changed)
        grid_strat.addWidget(self.chk_float, 0, 2)

        # 4. Không phân biệt thứ tự từ hoặc số
        self.chk_unordered = QCheckBox("Không phân biệt thứ tự từ hoặc số", strat_card)
        self.chk_unordered.setToolTip("So khớp các từ hoặc số mà không phụ thuộc vào thứ tự xuất hiện (Unordered Tokens)")
        self.chk_unordered.setStyleSheet(cb_style)
        self.chk_unordered.stateChanged.connect(self._on_matching_flags_changed)
        grid_strat.addWidget(self.chk_unordered, 1, 0)

        # 5. So khớp biểu thức chính quy
        self.chk_regex = QCheckBox("So khớp biểu thức chính quy", strat_card)
        self.chk_regex.setToolTip("Sử dụng chuỗi đầu ra kỳ vọng như mẫu regex để kiểm tra (Regex Pattern)")
        self.chk_regex.setStyleSheet(cb_style)
        self.chk_regex.stateChanged.connect(self._on_matching_flags_changed)
        grid_strat.addWidget(self.chk_regex, 1, 1)

        # 6. Kiểm tra kịch bản chấm tùy biến
        self.chk_special = QCheckBox("Kiểm tra kịch bản chấm tùy biến", strat_card)
        self.chk_special.setToolTip("Chạy script chấm điểm riêng biệt cho bài toán nhiều đáp án (Special Judge)")
        self.chk_special.setStyleSheet(cb_style)
        self.chk_special.stateChanged.connect(self._on_matching_flags_changed)
        grid_strat.addWidget(self.chk_special, 1, 2)

        s_layout.addLayout(grid_strat)
        tm_layout.addWidget(strat_card)
        tm_layout.addStretch(1)

        self.tabs.addTab(tab_match, "So Khớp Đầu Ra")

        main_layout.addWidget(self.tabs, stretch=1)

        # Chân cửa sổ: Chỉ MỘT nút chính "Lưu" (nền xanh đặc), các nút khác dùng viền
        footer = QHBoxLayout()
        footer.setSpacing(12)
        footer.addStretch(1)

        # Nút viền Hủy Bỏ
        btn_cancel = QPushButton("Hủy Bỏ", self)
        btn_cancel.setProperty("class", "SecondaryBtn")
        btn_cancel.setFixedHeight(36)
        btn_cancel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_cancel.clicked.connect(self.reject)
        footer.addWidget(btn_cancel)

        # Nếu là Wizard: có nút viền Quay Lại Bước 2
        if self.is_wizard:
            btn_back = QPushButton("Quay Lại Bước 2", self)
            btn_back.setProperty("class", "SecondaryBtn")
            btn_back.setFixedHeight(36)
            btn_back.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_back.clicked.connect(self._go_back)
            footer.addWidget(btn_back)

        # Duy nhất một nút chính nền xanh đặc: "Lưu"
        self.btn_save = QPushButton("Lưu", self)
        self.btn_save.setProperty("class", "PrimaryBtn")
        self.btn_save.setFixedHeight(36)
        self.btn_save.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_save.clicked.connect(self._save_and_close)
        footer.addWidget(self.btn_save)

        main_layout.addLayout(footer)

    def _go_back(self):
        self.nav_back = True
        self.reject()

    def _save_and_close(self):
        """Lưu cấu hình so khớp vào CSDL và đóng hộp thoại."""
        strat_code = self._get_selected_strategy_code()
        if self.class_id:
            try:
                self.db.update_class_matching_strategy(self.class_id, strat_code)
            except Exception as ex:
                logger.error("Lỗi cập nhật chiến lược so khớp: %s", str(ex))
        self.accept()

    def _open_ai_dialog(self):
        """Mở hộp thoại sinh testcase bằng AI."""
        current_q = self.cb_question.currentText().strip()
        if current_q == "Tất cả câu hỏi":
            current_q = "Q1"

        strat_code = self._get_selected_strategy_code()
        dlg = AiTestcaseDialog(
            parent=self,
            class_id=self.class_id,
            default_question=current_q,
            matching_strategy=strat_code
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._load_testcases_from_db()

    # --------------------------------------------------------------------------
    # Quản Lý Tiêu Chí So Khớp Đầu Ra
    # --------------------------------------------------------------------------
    def _get_selected_strategy_code(self) -> str:
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
        strat_code = self._get_selected_strategy_code()
        if self.class_id:
            try:
                self.db.update_class_matching_strategy(self.class_id, strat_code)
                self._load_testcases_from_db()
            except Exception as ex:
                logger.error("Lỗi cập nhật cờ so khớp: %s", str(ex))

    # --------------------------------------------------------------------------
    # CRUD Operations: Thêm / Sửa / Xóa Testcase
    # --------------------------------------------------------------------------
    def _load_testcases_from_db(self):
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
        self._filter_testcases()

    def _filter_testcases(self):
        q_filter = self.cb_question.currentText().strip()
        if q_filter == "Tất cả câu hỏi":
            self._render_testcases_table(self._all_testcases)
        else:
            filtered = [tc for tc in self._all_testcases if tc.get("question_number", "").upper() == q_filter.upper()]
            self._render_testcases_table(filtered)

    def _update_tc_total_label(self):
        """Hiển thị tổng trọng số testcases của đợt để hiểu quy đổi thang điểm 10."""
        cases = getattr(self, "_all_testcases", []) or []
        total_weight = sum(float(tc.get("score_weight", 1.0) or 0.0) for tc in cases)
        if total_weight <= 0:
            self.lbl_tc_total.setText("Chưa có testcase nào — hãy thêm testcase trước khi bắt đầu chấm.")
            self.lbl_tc_total.setStyleSheet(f"font-size: 12px; color: #DC2626; line-height: 1.4;")
            return
        per_unit = 10.0 / total_weight
        self.lbl_tc_total.setText(
            f"Tổng trọng số: {total_weight:.1f} — đạt đủ mới được 10/10; mỗi 1 trọng số tương đương {per_unit:.1f} điểm."
        )
        self.lbl_tc_total.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_SECONDARY}; line-height: 1.4;")

    def _render_testcases_table(self, testcases: List[Dict[str, Any]]):
        self._update_tc_total_label()
        self.table_tc.setRowCount(len(testcases))
        for r, tc in enumerate(testcases):
            self.table_tc.setRowHeight(r, 52)

            # 0: STT
            it_stt = QTableWidgetItem(str(r + 1))
            it_stt.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_tc.setItem(r, 0, it_stt)

            # 1: Câu Hỏi
            it_q = QTableWidgetItem(tc.get("question_number", "Q1"))
            it_q.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            it_q.setFont(QFont("Inter", 10, QFont.Weight.Bold))
            self.table_tc.setItem(r, 1, it_q)

            # 2: INPUT (dòng đầu + "(+N dòng)", tooltip đầy đủ)
            inp_str = tc.get("input_data", "") or ""
            it_inp = QTableWidgetItem(preview_multiline(inp_str, 60))
            it_inp.setToolTip(f"INPUT:\n{preview_tooltip(inp_str)}")
            it_inp.setForeground(QColor(text_color_for_value(inp_str)))
            it_inp.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table_tc.setItem(r, 2, it_inp)

            # 3: OUTPUT (dòng đầu + "(+N dòng)", tooltip đầy đủ)
            out_str = tc.get("expected_output", "") or ""
            it_out = QTableWidgetItem(preview_multiline(out_str, 60))
            it_out.setToolTip(f"OUTPUT:\n{preview_tooltip(out_str)}")
            it_out.setForeground(QColor(text_color_for_value(out_str)))
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

            # 8: Thao Tác - dựng bằng helper dùng chung make_action_cell
            btn_edit = make_row_button("Sửa", COLOR_PRIMARY, self.table_tc)
            btn_edit.clicked.connect(lambda _, item=tc: self._edit_testcase(item))

            btn_del = make_row_button("Xóa", COLOR_ERROR, self.table_tc)
            btn_del.clicked.connect(lambda _, item=tc: self._delete_testcase(item))

            self.table_tc.setCellWidget(r, 8, make_action_cell([btn_edit, btn_del], self.table_tc))

    def _current_question_filter(self) -> str:
        """Câu hỏi đang lọc ở cửa sổ quản lý (mặc định Q1 khi đang xem tất cả)."""
        question = self.cb_question.currentText().strip()
        if not question or question == "Tất cả câu hỏi":
            return "Q1"
        return question

    def _add_testcase(self):
        if not self.class_id:
            QMessageBox.warning(self, "Chưa Chọn Đợt Chấm", "Không xác định được đợt thi hiện tại.")
            return

        dlg = TestcaseEditDialog(
            self,
            db=self.db,
            class_id=self.class_id,
            question_number=self._current_question_filter(),
            matching_strategy=self._get_selected_strategy_code(),
            start_new=True,
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._load_testcases_from_db()

    def _edit_testcase(self, tc: Dict[str, Any]):
        dlg = TestcaseEditDialog(
            self,
            testcase=tc,
            db=self.db,
            class_id=self.class_id,
            question_number=tc.get("question_number") or "Q1",
            matching_strategy=self._get_selected_strategy_code(),
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._load_testcases_from_db()

    def _delete_testcase(self, tc: Dict[str, Any]):
        tc_id = tc.get("id")
        q_num = tc.get("question_number", "Q1")
        ret = QMessageBox.question(
            self,
            "Xác Nhận Xóa Testcase",
            f"Bạn có chắc chắn muốn xóa testcase này của câu {q_num}?\n\n"
            f"- INPUT: {preview_multiline(tc.get('input_data', ''), 60)}\n"
            f"- OUTPUT: {preview_multiline(tc.get('expected_output', ''), 60)}\n\n"
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
