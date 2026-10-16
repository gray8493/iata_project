"""
AITA Desktop Client - Primary Workspace Window (PyQt6)
Subsystem: Practical Exam (PE) Grading
Standard Implementation matching DESKTOP APP UI/UX DESIGN SYSTEM
Style: Modern Educational SaaS, 100% Light, Blue-focused (#2F80ED), Clean 240px Sidebar, 64px Header.
Strictly NO emojis/icons in the UI. All text in Vietnamese.
"""

import sys
import re
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from collections import Counter

from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QFont, QColor, QCursor, QGuiApplication, QPixmap, QTextDocument, QDesktopServices
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QProgressBar, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QMessageBox, QDialog,
    QSizePolicy, QStackedWidget, QFileDialog, QMenu, QScrollArea
)

SRC_DIR = Path(__file__).resolve().parent.parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ui.styles.theme import (
    LIGHT_THEME_QSS, COLOR_PRIMARY, COLOR_PRIMARY_BG, COLOR_PRIMARY_HOVER, COLOR_PRIMARY_LIGHT,
    COLOR_BG, COLOR_SURFACE, COLOR_SURFACE_SECONDARY, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED, COLOR_BORDER_DEFAULT, COLOR_BORDER_LIGHT,
    COLOR_SUCCESS, COLOR_SUCCESS_BG, COLOR_ERROR, COLOR_ERROR_BG,
    COLOR_WARNING, COLOR_WARNING_BG, RADIUS_CARD, RADIUS_BUTTON, RADIUS_PILL
)
from ui.dialogs.session_dialog import SessionDialog
from ui.dialogs.history_dialog import HistoryDialog
from ui.dialogs.grading_guide_dialog import GradingGuideDialog
from ui.dialogs.testcase_dialog import TestcaseDialog
from ui.dialogs.settings_dialog import SettingsDialog
from ui.dialogs.submission_detail_dialog import SubmissionDetailDialog
from ui.dialogs.plagiarism_dialog import PlagiarismDialog
from database.db_manager import DatabaseManager
from services.grading_service import GradingService
from services.ai_service import AiService
from services.export_service import ExportService


# ==============================================================================
# HELPER WIDGETS
# ==============================================================================
class VerdictPill(QWidget):
    """Status badge widget matching Design System tokens (Radius 999px, height 26px)."""
    
    PALETTES = {
        "AC": (COLOR_SUCCESS_BG, COLOR_SUCCESS, "AC (Đạt Chuẩn)"),
        "WA": (COLOR_ERROR_BG, COLOR_ERROR, "WA (Sai Kết Quả)"),
        "TLE": (COLOR_WARNING_BG, COLOR_WARNING, "TLE (Quá Giờ)"),
        "MLE": (COLOR_WARNING_BG, COLOR_WARNING, "MLE (Tràn RAM)"),
        "CE": (COLOR_ERROR_BG, COLOR_ERROR, "CE (Lỗi Biên Dịch)"),
        "RE": (COLOR_ERROR_BG, COLOR_ERROR, "RE (Lỗi Thực Thi)"),
        "PENDING": (COLOR_PRIMARY_BG, COLOR_PRIMARY, "Chờ Chấm Điểm")
    }

    def __init__(self, verdict: str = "PENDING", parent: Optional[QWidget] = None):
        super().__init__(parent)
        bg_color, text_color, label = self.PALETTES.get(verdict, self.PALETTES["PENDING"])
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl = QLabel(label, self)
        lbl.setFixedHeight(26)
        lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                font-weight: 500;
                font-size: 12px;
                border-radius: {RADIUS_PILL};
                padding: 4px 10px;
            }}
        """)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)


class MetricCardWidget(QFrame):
    """
    Stat card matching Design System Requirements:
    Pure text and number (no acronym/icon boxes).
    Label at top (13-14px font), number at bottom (26-28px font), descriptive tooltip.
    """

    def __init__(self, value: str, label: str, tooltip_str: str = "", value_color: str = COLOR_TEXT_PRIMARY, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("MetricCard")
        self.setProperty("class", "Card")
        self.setMinimumHeight(115)
        self.setToolTip(tooltip_str)
        self.setStyleSheet(f"""
            QFrame#MetricCard {{
                background-color: {COLOR_SURFACE};
                border: 1px solid {COLOR_BORDER_DEFAULT};
                border-radius: {RADIUS_CARD};
            }}
            QFrame#MetricCard:hover {{
                border-color: {COLOR_PRIMARY};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)
        
        self.lbl_label = QLabel(label, self)
        self.lbl_label.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 500;
            color: {COLOR_TEXT_SECONDARY};
            background: transparent;
            line-height: 1.4;
        """)
        layout.addWidget(self.lbl_label)
        
        layout.addStretch(1)
        
        self.lbl_value = QLabel(value, self)
        self.lbl_value.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 700;
            color: {value_color};
            background: transparent;
        """)
        layout.addWidget(self.lbl_value)

    def set_value(self, val: str):
        self.lbl_value.setText(val)


# ==============================================================================
# BACKGROUND GRADING WORKER (ProcessPoolExecutor behind a QThread, ST01_TC001)
# ==============================================================================
class BatchGradingWorker(QThread):
    """
    Runs the batch grading pipeline off the UI thread.

    `GradingService.grade_class_batch` dispatches work to a `ProcessPoolExecutor`
    (4-8 workers), so the UI stays fully responsive while 45+ submissions are
    compiled and executed in parallel.
    """

    progress = pyqtSignal(int, int, str)
    finished_ok = pyqtSignal(int, float)
    failed = pyqtSignal(str)

    def __init__(self, grading_service: GradingService, class_id: int, parent=None):
        super().__init__(parent)
        self._service = grading_service
        self._class_id = class_id

    def run(self):
        started = time.perf_counter()
        try:
            def on_progress(curr, total, mssv):
                self.progress.emit(curr, total, mssv)

            results = self._service.grade_class_batch(self._class_id, progress_callback=on_progress)
            elapsed = time.perf_counter() - started
            self.finished_ok.emit(len(results), elapsed)
        except Exception as ex:
            self.failed.emit(str(ex))


# ==============================================================================
# MAIN WINDOW IMPLEMENTATION
# ==============================================================================
class AITAMainWindow(QMainWindow):
    """
    Main Application Window for AITA Desktop Client - Practical Exam (PE) Grading Subsystem.
    Layout: 240px Fixed Sidebar + Top Header 64px + Main Content (Scrollable, min 1100x700).
    """

    def __init__(self, session_info: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.session_info = session_info or {
            "mode": "ONLINE",
            "username": "instructor",
            "display_name": "Giảng Viên",
        }
        self.setWindowTitle("AITA - Chấm Thi Thực Hành")
        
        # Responsive sizing: min 1100x700 according to requirement 16
        screen = QGuiApplication.primaryScreen()
        if screen:
            avail = screen.availableGeometry()
            target_w = max(1100, min(1380, avail.width() - 40))
            target_h = max(700, min(840, avail.height() - 40))
            self.setMinimumSize(1100, 700)
            self.resize(target_w, target_h)
            self.move(avail.x() + (avail.width() - target_w) // 2,
                      avail.y() + (avail.height() - target_h) // 2)
        else:
            self.setMinimumSize(1100, 700)
            self.resize(1280, 750)
            
        self.setStyleSheet(LIGHT_THEME_QSS)
        
        # Database & Service
        self.db = DatabaseManager()
        self.grading_service = GradingService(self.db)
        self.current_class_id: Optional[int] = None
        
        self.has_exported_grades = False
        self._setup_desktop_layout()
        self._load_classes_selector()
        self._refresh_ai_quota()

    def _setup_desktop_layout(self):
        """Builds standard layout: 240px Fixed Sidebar + Scrollable Main Content."""
        root_widget = QWidget(self)
        self.setCentralWidget(root_widget)
        
        master_layout = QHBoxLayout(root_widget)
        master_layout.setContentsMargins(0, 0, 0, 0)
        master_layout.setSpacing(0)
        
        # 1. Standard Sidebar (240px)
        sidebar = self._build_sidebar()
        master_layout.addWidget(sidebar)
        
        # 2. Right Container with ScrollArea to guarantee no text clipping at 100%/125%/150% scales
        right_container = QWidget(self)
        rc_layout = QVBoxLayout(right_container)
        rc_layout.setContentsMargins(0, 0, 0, 0)
        rc_layout.setSpacing(0)
        
        # Top Header (64px)
        top_header = self._build_top_header()
        rc_layout.addWidget(top_header)
        
        # Scroll area for canvas content
        scroll = QScrollArea(right_container)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        # Stacked Central Content: Page 0 = Empty State, Page 1 = Active Workspace Canvas
        self.content_stack = QStackedWidget(scroll)
        self.page_empty = self._build_empty_state_view()
        self.page_active = self._build_active_workspace_view()
        
        self.content_stack.addWidget(self.page_empty)    # Index 0
        self.content_stack.addWidget(self.page_active)   # Index 1
        
        scroll.setWidget(self.content_stack)
        rc_layout.addWidget(scroll, stretch=1)
        
        master_layout.addWidget(right_container, stretch=1)

    # --------------------------------------------------------------------------
    # Empty State View (When no class is selected)
    # --------------------------------------------------------------------------
    def _build_empty_state_view(self) -> QWidget:
        """Builds an elegant empty state view encouraging user to create or select a grading session."""
        container = QWidget(self)
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(32, 24, 32, 24)
        c_layout.addStretch(1)
        
        card = QFrame(container)
        card.setProperty("class", "Card")
        card.setMinimumWidth(680)
        card.setMaximumWidth(840)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 36, 40, 36)
        card_layout.setSpacing(20)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title & Subtitle
        lbl_title = QLabel("Chưa Có Đợt Chấm Nào Được Chọn", card)
        lbl_title.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {COLOR_TEXT_PRIMARY}; background: transparent; padding-bottom: 2px;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(lbl_title)
        
        # Yêu cầu 3: Đoạn mô tả chuẩn, bỏ 'CSDL cục bộ', rộng 600px (560-640px)
        lbl_desc = QLabel(
            "Hệ thống chấm theo từng đợt độc lập. Bấm 'Tạo Đợt Chấm Mới' để bắt đầu, hoặc mở lại một đợt đã lưu.", card
        )
        lbl_desc.setWordWrap(True)
        lbl_desc.setFixedWidth(600)
        lbl_desc.setStyleSheet(f"font-size: 14px; color: {COLOR_TEXT_SECONDARY}; line-height: 1.5; background: transparent;")
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(lbl_desc)
        
        # Yêu cầu 2: Khung 'Quy Trình Chấm Thi Chuẩn 6 Bước' tự giãn theo nội dung, padding dọc 6-8px, line-height >= 1.5
        flow_box = QFrame(card)
        flow_box.setStyleSheet("""
            QFrame {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
            QLabel {
                background: transparent;
                border: none;
            }
        """)
        fb_layout = QVBoxLayout(flow_box)
        fb_layout.setContentsMargins(22, 18, 22, 18)
        fb_layout.setSpacing(4)
        
        lbl_flow_title = QLabel("Quy Trình Chấm Thi Chuẩn 6 Bước", flow_box)
        lbl_flow_title.setStyleSheet(f"font-weight: 700; font-size: 15px; color: {COLOR_PRIMARY}; line-height: 1.5; padding: 4px 0 6px 0;")
        fb_layout.addWidget(lbl_flow_title)
        
        steps = [
            "Bước 1: Nạp bài nộp (chọn thư mục bài làm, hệ thống tự động tách MSSV và họ tên theo tên thư mục/file)",
            "Bước 2: Cấu hình Testcase & So khớp (thiết lập bộ dữ liệu kiểm thử và chọn thuật toán so khớp kết quả)",
            "Bước 3: Bắt đầu chấm hàng loạt (biên dịch mã nguồn trong sandbox giám sát RAM và CPU thời gian thực)",
            "Bước 4: Quét đạo văn AST (phân tích cấu trúc cây cú pháp trừu tượng để phát hiện gian lận chép mã)",
            "Bước 5: Xuất bảng điểm (kết xuất file điểm chi tiết ra định dạng Excel .xlsx, PDF hoặc CSV)",
            "Bước 6: Kết thúc phiên chấm (chốt đợt thi, lưu trữ an toàn toàn bộ dữ liệu và đóng phiên làm việc)"
        ]
        for s in steps:
            l = QLabel(s, flow_box)
            l.setStyleSheet("font-size: 13px; color: #334155; line-height: 1.6; padding: 6px 0;")
            l.setWordWrap(True)
            fb_layout.addWidget(l)
        card_layout.addWidget(flow_box)
        
        # Action Buttons Row
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(16)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Yêu cầu 1: Nút 'Tạo Đợt Chấm Mới' nền xanh đặc #2F80ED, chữ trắng, bo góc, cao 40px
        btn_create = QPushButton("Tạo Đợt Chấm Mới", card)
        btn_create.setFixedHeight(40)
        btn_create.setMinimumWidth(180)
        btn_create.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_create.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_HOVER};
            }}
        """)
        btn_create.clicked.connect(self._open_session_dialog)
        btn_layout.addWidget(btn_create)
        
        # Yêu cầu 4: Nút 'Mở Đợt Chấm Từ Lịch Sử' nút viền xanh nền trắng, cùng chiều cao 40px
        btn_history = QPushButton("Mở Đợt Chấm Từ Lịch Sử", card)
        btn_history.setFixedHeight(40)
        btn_history.setMinimumWidth(180)
        btn_history.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_history.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFFFFF;
                color: {COLOR_PRIMARY};
                border: 1.5px solid {COLOR_PRIMARY};
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_BG};
            }}
        """)
        btn_history.clicked.connect(self._open_history_dialog)
        btn_layout.addWidget(btn_history)
        
        card_layout.addLayout(btn_layout)
        c_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
        c_layout.addStretch(1)
        return container

    def _build_active_workspace_view(self) -> QWidget:
        """Builds active grading workspace with 5-Step Action Toolbar, Stats Panel, and Submissions Table."""
        content_canvas = QWidget(self)
        content_canvas.setObjectName("CentralCanvas")
        content_layout = QVBoxLayout(content_canvas)
        content_layout.setContentsMargins(28, 24, 28, 24)
        content_layout.setSpacing(20)
        
        # 5-Step Action Toolbar
        content_layout.addWidget(self._build_action_toolbar())
        
        # Stat Cards (4 columns) + Progress Bar
        content_layout.addWidget(self._build_stats_panel())
        
        # Submissions Table Card (with empty state support)
        content_layout.addWidget(self._build_table_card(), stretch=1)
        return content_canvas

    # --------------------------------------------------------------------------
    # 1. Standard Sidebar (240px) - Grouped into "Chấm điểm" & "Công cụ"
    # --------------------------------------------------------------------------
    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame(self)
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(240)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 16, 12, 20)
        layout.setSpacing(4)
        
        # Logo Area (Height 64px)
        logo_area = QFrame(sidebar)
        logo_area.setFixedHeight(64)
        la_layout = QHBoxLayout(logo_area)
        la_layout.setContentsMargins(6, 0, 6, 0)
        la_layout.setSpacing(12)
        
        logo_icon = QFrame(logo_area)
        logo_icon.setFixedSize(38, 38)
        logo_icon.setStyleSheet(f"""
            background-color: {COLOR_PRIMARY};
            border-radius: 10px;
        """)
        li_layout = QHBoxLayout(logo_icon)
        li_layout.setContentsMargins(0, 0, 0, 0)
        lbl_li = QLabel("A", logo_icon)
        lbl_li.setStyleSheet("color: #FFFFFF; font-size: 18px; font-weight: 800;")
        lbl_li.setAlignment(Qt.AlignmentFlag.AlignCenter)
        li_layout.addWidget(lbl_li)
        la_layout.addWidget(logo_icon)
        
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        lbl_app_name = QLabel("AITA", logo_area)
        lbl_app_name.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {COLOR_TEXT_PRIMARY};")
        lbl_sub_name = QLabel("Chấm Thi Thực Hành", logo_area)
        lbl_sub_name.setStyleSheet(f"font-size: 11px; color: {COLOR_TEXT_SECONDARY};")
        title_box.addWidget(lbl_app_name)
        title_box.addWidget(lbl_sub_name)
        la_layout.addLayout(title_box)
        la_layout.addStretch(1)
        layout.addWidget(logo_area)
        
        layout.addSpacing(10)
        
        # Helper for Sidebar Navigation Items
        def create_nav_item(text: str, is_active: bool = False, on_click=None) -> QPushButton:
            btn = QPushButton(text, sidebar)
            btn.setFixedHeight(40)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            if is_active:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLOR_PRIMARY_BG};
                        color: {COLOR_PRIMARY};
                        font-weight: 600;
                        font-size: 13px;
                        text-align: left;
                        padding-left: 14px;
                        border: none;
                        border-radius: 8px;
                        border-left: 3px solid {COLOR_PRIMARY};
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {COLOR_TEXT_PRIMARY};
                        font-weight: 500;
                        font-size: 13px;
                        text-align: left;
                        padding-left: 14px;
                        border: none;
                        border-radius: 8px;
                    }}
                    QPushButton:hover {{
                        background-color: {COLOR_SURFACE_SECONDARY};
                        color: {COLOR_PRIMARY};
                    }}
                """)
            if on_click:
                btn.clicked.connect(on_click)
            return btn
        
        # Nhóm 1: CHẤM ĐIỂM
        lbl_sec1 = QLabel("CHẤM ĐIỂM", sidebar)
        lbl_sec1.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {COLOR_TEXT_MUTED}; padding-left: 12px; margin-top: 6px; margin-bottom: 2px;")
        layout.addWidget(lbl_sec1)
        
        btn_console = create_nav_item("Bảng Điểm Bài Nộp", is_active=True)
        layout.addWidget(btn_console)
        
        btn_tc = create_nav_item("Quản Lý Testcase", is_active=False, on_click=self._open_testcase_dialog)
        layout.addWidget(btn_tc)
        
        btn_plag = create_nav_item("Quét Đạo Văn AST", is_active=False, on_click=self._open_plagiarism_dialog)
        layout.addWidget(btn_plag)
        
        layout.addSpacing(12)
        
        # Nhóm 2: CÔNG CỤ (Các mục mở hộp thoại đều dùng kiểu không chọn is_active=False)
        lbl_sec2 = QLabel("CÔNG CỤ", sidebar)
        lbl_sec2.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {COLOR_TEXT_MUTED}; padding-left: 12px; margin-top: 6px; margin-bottom: 2px;")
        layout.addWidget(lbl_sec2)
        
        btn_new_session = create_nav_item("Tạo Đợt Chấm Mới", is_active=False, on_click=self._open_session_dialog)
        layout.addWidget(btn_new_session)

        btn_history = create_nav_item("Lịch Sử Đợt Chấm", is_active=False, on_click=self._open_history_dialog)
        layout.addWidget(btn_history)

        btn_guide = create_nav_item("Hướng Dẫn Chấm", is_active=False, on_click=self._open_guide_dialog)
        layout.addWidget(btn_guide)
        
        btn_settings = create_nav_item("Cấu Hình Môi Trường", is_active=False, on_click=self._open_settings_dialog)
        layout.addWidget(btn_settings)
        
        layout.addStretch(1)

        # Logo FPT Education (Chiều cao 32px, giữ tỉ lệ, căn giữa, cách nút 16px)
        fptu_logo_paths = [
            SRC_DIR.parent / "assets" / "images" / "fptulogo_transparent.png",
            Path(r"e:\AITA\apps\desktop-client\assets\images\fptulogo_transparent.png"),
            Path(r"e:\AITA\assets\images\fptulogo_transparent.png")
        ]
        fptu_logo_file = next((p for p in fptu_logo_paths if p.exists()), None)
        if fptu_logo_file:
            lbl_fptu = QLabel(sidebar)
            lbl_fptu.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_fptu.setStyleSheet("background: transparent; border: none;")
            pix = QPixmap(str(fptu_logo_file))
            if not pix.isNull():
                lbl_fptu.setPixmap(pix.scaledToHeight(32, Qt.TransformationMode.SmoothTransformation))
            layout.addWidget(lbl_fptu)
            layout.addSpacing(16)
        
        # Nút Đổi Chế Độ Làm Việc (Viền cùng độ dày 1.5px/màu với nút phụ khác, font 13px)
        btn_back_mode = QPushButton("Đổi Chế Độ Làm Việc", sidebar)
        btn_back_mode.setFixedHeight(40)
        btn_back_mode.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_back_mode.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFFFFF;
                color: #334155;
                font-weight: 600;
                font-size: 13px;
                text-align: center;
                border: 1px solid {COLOR_BORDER_DEFAULT};
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_SURFACE_SECONDARY};
                color: {COLOR_PRIMARY};
                border-color: {COLOR_PRIMARY};
            }}
        """)
        btn_back_mode.clicked.connect(self._back_to_mode_selection)
        layout.addWidget(btn_back_mode)
        
        return sidebar

    # --------------------------------------------------------------------------
    # 2. Top Header Bar (64px) - Bỏ nút Tạo Đợt Chấm Mới trùng lặp
    # --------------------------------------------------------------------------
    def _build_top_header(self) -> QFrame:
        header = QFrame(self)
        header.setObjectName("HeaderBar")
        header.setFixedHeight(64)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(16)
        
        # Page Title
        lbl_page_title = QLabel("Chấm Thi Thực Hành", header)
        lbl_page_title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {COLOR_TEXT_PRIMARY};")
        layout.addWidget(lbl_page_title)
        
        layout.addSpacing(12)
        
        # Course / Class Dropdown Selector
        self.class_selector = QComboBox(header)
        self.class_selector.setFixedHeight(36)
        self.class_selector.setMinimumWidth(260)
        self.class_selector.setMaximumWidth(400)
        self.class_selector.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.class_selector.currentIndexChanged.connect(self._on_class_selected)
        layout.addWidget(self.class_selector)
        
        layout.addStretch(1)
        
        # AI Mode Badge
        badge_bg = "#EFF6FF"
        badge_color = COLOR_PRIMARY
        badge_border = "#BFDBFE"
        badge_text = "Gemini AI: Sẵn Sàng"
        
        status_pill = QFrame(header)
        status_pill.setFixedHeight(32)
        # Yêu cầu 15: Thêm tooltip 'Số token AI còn lại trong tháng'
        status_pill.setToolTip("Số token AI còn lại trong tháng")
        status_pill.setStyleSheet(f"""
            QFrame {{
                background-color: {badge_bg};
                border: 1.5px solid {badge_border};
                border-radius: 16px;
            }}
            QLabel {{
                border: none;
                background: transparent;
                color: {badge_color};
                font-size: 12px;
                font-weight: 600;
            }}
        """)
        sp_layout = QHBoxLayout(status_pill)
        sp_layout.setContentsMargins(14, 0, 14, 0)
        lbl_sp = QLabel(badge_text, status_pill)
        lbl_sp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_sp.setToolTip("Số token AI còn lại trong tháng")
        sp_layout.addWidget(lbl_sp)
        self.lbl_ai_quota = lbl_sp
        layout.addWidget(status_pill, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        # User Avatar & Name
        user_frame = QWidget(header)
        user_frame.setStyleSheet("background: transparent; border: none;")
        uf_layout = QHBoxLayout(user_frame)
        uf_layout.setContentsMargins(0, 0, 0, 0)
        uf_layout.setSpacing(10)
        
        avatar = QLabel("GV", user_frame)
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            QLabel {{
                background-color: {COLOR_PRIMARY_BG};
                color: {COLOR_PRIMARY};
                border: 1.5px solid {COLOR_PRIMARY};
                border-radius: 18px;
                font-size: 13px;
                font-weight: 700;
            }}
        """)
        uf_layout.addWidget(avatar)
        
        d_name = self.session_info.get("display_name", "Giảng viên")
        lbl_user = QLabel(d_name, user_frame)
        lbl_user.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {COLOR_TEXT_PRIMARY}; background: transparent; border: none;")
        uf_layout.addWidget(lbl_user)
        layout.addWidget(user_frame, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        return header

    def _back_to_mode_selection(self):
        from ui.windows.mode_selection_window import ModeSelectionWindow
        self.mode_win = ModeSelectionWindow(session_info=self.session_info)
        self.mode_win.show()
        self.close()

    # --------------------------------------------------------------------------
    # 3. Action Toolbar (6 Steps with State, Highlight, and Rescan Button)
    # --------------------------------------------------------------------------
    def _build_action_toolbar(self) -> QFrame:
        card = QFrame(self)
        card.setProperty("class", "Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)
        
        # 6 Steps Row (Chỉ đúng 6 bước, không để nút phụ nằm ngoài như bước thứ 7)
        steps_row = QHBoxLayout()
        steps_row.setSpacing(10)
        
        # Helper to create a step widget containing button and status text
        def create_step_widget(step_num: int, title: str):
            container = QWidget(card)
            c_layout = QVBoxLayout(container)
            c_layout.setContentsMargins(0, 0, 0, 0)
            c_layout.setSpacing(4)
            
            btn = QPushButton(f"{step_num}. {title}", container)
            btn.setFixedHeight(38)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            c_layout.addWidget(btn)
            
            lbl_status = QLabel("Chưa làm", container)
            lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_status.setStyleSheet("font-size: 11px; font-weight: 500; color: #64748B; background: transparent;")
            c_layout.addWidget(lbl_status)
            
            return container, btn, lbl_status
        
        # Yêu cầu 12: Bước 1 gồm nút "1. Nạp Bài Nộp" và nút viền liền "Quét Lại" đặt cạnh nhau
        self.w_step1 = QWidget(card)
        w1_layout = QVBoxLayout(self.w_step1)
        w1_layout.setContentsMargins(0, 0, 0, 0)
        w1_layout.setSpacing(4)
        
        b1_box = QHBoxLayout()
        b1_box.setContentsMargins(0, 0, 0, 0)
        b1_box.setSpacing(6)
        
        self.btn_step1 = QPushButton("1. Nạp Bài Nộp", self.w_step1)
        self.btn_step1.setFixedHeight(38)
        self.btn_step1.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_step1.clicked.connect(self._handle_step1_ingest)
        b1_box.addWidget(self.btn_step1, stretch=1)
        
        # Nút phụ: Quét Lại Thư Mục (viền liền, đặt cạnh Bước 1)
        self.btn_rescan = QPushButton("Quét Lại", self.w_step1)
        self.btn_rescan.setFixedHeight(38)
        self.btn_rescan.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_rescan.setToolTip("Quét lại thư mục bài nộp để thêm bài mới nộp, giữ nguyên điểm số bài đã chấm")
        self.btn_rescan.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFFFFF;
                color: {COLOR_PRIMARY};
                border: 1.5px solid {COLOR_PRIMARY};
                border-radius: 8px;
                font-size: 12px;
                font-weight: 600;
                padding: 0 10px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_BG};
            }}
            QPushButton:disabled {{
                background-color: #F8FAFC;
                color: #94A3B8;
                border-color: #CBD5E1;
            }}
        """)
        self.btn_rescan.clicked.connect(self._handle_rescan_directory)
        b1_box.addWidget(self.btn_rescan)
        w1_layout.addLayout(b1_box)
        
        self.lbl_step1_status = QLabel("Chưa có bài", self.w_step1)
        self.lbl_step1_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_step1_status.setStyleSheet("font-size: 11px; font-weight: 500; color: #64748B; background: transparent;")
        w1_layout.addWidget(self.lbl_step1_status)
        steps_row.addWidget(self.w_step1)
        
        # Step 2: Cấu Hình Testcase & So Khớp
        self.w_step2, self.btn_step2, self.lbl_step2_status = create_step_widget(2, "Cấu Hình Testcase & So Khớp")
        self.btn_step2.clicked.connect(self._open_testcase_dialog)
        steps_row.addWidget(self.w_step2)
        
        # Step 3: Bắt Đầu Chấm Hàng Loạt
        self.w_step3, self.btn_step3, self.lbl_step3_status = create_step_widget(3, "Bắt Đầu Chấm Hàng Loạt")
        self.btn_step3.clicked.connect(self._start_batch_grade)
        steps_row.addWidget(self.w_step3)
        
        # Step 4: Quét Đạo Văn AST
        self.w_step4, self.btn_step4, self.lbl_step4_status = create_step_widget(4, "Quét Đạo Văn AST")
        self.btn_step4.clicked.connect(self._open_plagiarism_dialog)
        steps_row.addWidget(self.w_step4)
        
        # Step 5: Xuất Bảng Điểm
        self.w_step5, self.btn_step5, self.lbl_step5_status = create_step_widget(5, "Xuất Bảng Điểm")
        self.btn_step5.clicked.connect(self._handle_step5_export_menu)
        steps_row.addWidget(self.w_step5)
        
        # Step 6: Kết Thúc Phiên Chấm
        self.w_step6, self.btn_step6, self.lbl_step6_status = create_step_widget(6, "Kết Thúc Phiên Chấm")
        self.btn_step6.clicked.connect(self._handle_step6_end_session)
        steps_row.addWidget(self.w_step6)
        
        layout.addLayout(steps_row)
        return card

    def _apply_step_button_style(self, btn: QPushButton, is_highlighted: bool, is_enabled: bool, tooltip_text: str):
        """Applies solid blue background for the ONLY next best step, outline style for other enabled steps."""
        btn.setEnabled(is_enabled)
        btn.setToolTip(tooltip_text)
        
        if not is_enabled:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F1F5F9;
                    color: #94A3B8;
                    border: 1px solid #E2E8F0;
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: 500;
                    padding: 0 14px;
                }
            """)
        elif is_highlighted:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_PRIMARY};
                    color: #FFFFFF;
                    border: 1px solid {COLOR_PRIMARY};
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: 700;
                    padding: 0 14px;
                }}
                QPushButton:hover {{
                    background-color: {COLOR_PRIMARY_HOVER};
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #FFFFFF;
                    color: #1E293B;
                    border: 1.5px solid {COLOR_BORDER_DEFAULT};
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: 600;
                    padding: 0 14px;
                }}
                QPushButton:hover {{
                    background-color: {COLOR_PRIMARY_BG};
                    color: {COLOR_PRIMARY};
                    border-color: {COLOR_PRIMARY};
                }}
            """)

    def _update_step_buttons(self, submission_count: int, graded_count: int, testcase_count: int):
        """
        Yêu cầu 10:
        Updates 6-step action buttons based on strict condition rules:
        - Quy ước màu nhãn:
          + Xanh lá (#16A34A): Đã xong
          + Xanh dương (#2563EB): Bước tiếp theo nên làm (chỉ duy nhất bước này được highlight)
          + Xám (#64748B): Chưa đủ điều kiện (kèm nút disable và tooltip nêu rõ lý do)
        - Nổi bật đúng duy nhất 1 bước.
        """
        has_class = (self.current_class_id is not None)
        
        # Conditions
        step1_enabled = has_class
        step2_enabled = has_class
        step3_enabled = has_class and (submission_count > 0) and (testcase_count > 0)
        step4_enabled = has_class and (submission_count > 0)
        step5_enabled = has_class and (graded_count > 0)
        step6_enabled = has_class
        
        # Tooltips explaining why disabled
        step1_tip = "Nạp bài làm của sinh viên từ thư mục" if step1_enabled else "Cần tạo hoặc mở đợt chấm trước khi nạp bài nộp"
        step2_tip = f"Đã có {testcase_count} testcase cấu hình" if testcase_count > 0 else "Thiết lập dữ liệu đầu vào/ra và thuật toán so khớp"
        
        if not step3_enabled:
            if not has_class:
                step3_tip = "Chưa thể chấm: Cần chọn hoặc tạo đợt chấm bài trước"
            elif submission_count == 0:
                step3_tip = "Chưa thể chấm: Cần nạp bài nộp của sinh viên trước (Bước 1)"
            else:
                step3_tip = "Chưa thể chấm: Cần tạo ít nhất 1 Testcase kiểm thử trước (Bước 2)"
        else:
            step3_tip = f"Bắt đầu chấm tự động {submission_count} bài nộp"
            
        step4_tip = "Quét phân tích cấu trúc AST phát hiện đạo văn mã nguồn" if step4_enabled else "Chưa thể quét: Cần nạp bài nộp của sinh viên trước (Bước 1)"
        step5_tip = f"Xuất bảng điểm {graded_count} bài đã chấm (Excel, PDF, CSV)" if step5_enabled else "Chưa thể xuất: Cần có ít nhất 1 bài đã được chấm điểm (Bước 3)"
        step6_tip = "Kết thúc và chốt phiên chấm bài hiện tại, lưu an toàn toàn bộ dữ liệu" if step6_enabled else "Cần chọn hoặc mở đợt chấm bài trước khi kết thúc phiên"

        # Highlight ONLY ONE next best action
        hl1 = False
        hl2 = False
        hl3 = False
        hl4 = False
        hl5 = False
        hl6 = False

        if not has_class:
            pass
        elif submission_count == 0:
            hl1 = True
        elif testcase_count == 0:
            hl2 = True
        elif graded_count < submission_count:
            hl3 = True
        elif not self.has_exported_grades:
            hl5 = True
        else:
            hl6 = True

        # Yêu cầu 10: Màu sắc nhãn trạng thái (xanh lá = đã xong, xanh dương = bước nên làm, xám = chưa đủ điều kiện)
        # Bước 1
        if submission_count > 0:
            self.lbl_step1_status.setText(f"Đã nạp ({submission_count} bài)")
            self.lbl_step1_status.setStyleSheet("font-size: 11px; font-weight: 600; color: #16A34A; background: transparent;")
        elif hl1:
            self.lbl_step1_status.setText("Cần nạp bài nộp")
            self.lbl_step1_status.setStyleSheet("font-size: 11px; font-weight: 700; color: #2563EB; background: transparent;")
        else:
            self.lbl_step1_status.setText("Chưa có phiên")
            self.lbl_step1_status.setStyleSheet("font-size: 11px; font-weight: 500; color: #64748B; background: transparent;")

        # Bước 2
        if testcase_count > 0:
            self.lbl_step2_status.setText(f"Đã xong ({testcase_count} TC)")
            self.lbl_step2_status.setStyleSheet("font-size: 11px; font-weight: 600; color: #16A34A; background: transparent;")
        elif hl2:
            self.lbl_step2_status.setText("Cần cấu hình TC")
            self.lbl_step2_status.setStyleSheet("font-size: 11px; font-weight: 700; color: #2563EB; background: transparent;")
        else:
            self.lbl_step2_status.setText("Chưa cấu hình")
            self.lbl_step2_status.setStyleSheet("font-size: 11px; font-weight: 500; color: #64748B; background: transparent;")

        # Bước 3
        if graded_count == submission_count and submission_count > 0:
            self.lbl_step3_status.setText(f"Hoàn tất ({graded_count}/{submission_count})")
            self.lbl_step3_status.setStyleSheet("font-size: 11px; font-weight: 600; color: #16A34A; background: transparent;")
        elif hl3:
            if graded_count > 0:
                self.lbl_step3_status.setText(f"Đang chấm ({graded_count}/{submission_count})")
            else:
                self.lbl_step3_status.setText("Bắt đầu chấm")
            self.lbl_step3_status.setStyleSheet("font-size: 11px; font-weight: 700; color: #2563EB; background: transparent;")
        else:
            self.lbl_step3_status.setText("Chưa đủ điều kiện")
            self.lbl_step3_status.setStyleSheet("font-size: 11px; font-weight: 500; color: #64748B; background: transparent;")

        # Bước 4
        if step4_enabled:
            self.lbl_step4_status.setText("Sẵn sàng quét")
            self.lbl_step4_status.setStyleSheet("font-size: 11px; font-weight: 600; color: #16A34A; background: transparent;")
        else:
            self.lbl_step4_status.setText("Chưa có bài")
            self.lbl_step4_status.setStyleSheet("font-size: 11px; font-weight: 500; color: #64748B; background: transparent;")

        # Bước 5
        if self.has_exported_grades:
            self.lbl_step5_status.setText(f"Đã xuất ({graded_count} bài)")
            self.lbl_step5_status.setStyleSheet("font-size: 11px; font-weight: 600; color: #16A34A; background: transparent;")
        elif hl5:
            self.lbl_step5_status.setText(f"Nên xuất ({graded_count} bài)")
            self.lbl_step5_status.setStyleSheet("font-size: 11px; font-weight: 700; color: #2563EB; background: transparent;")
        else:
            self.lbl_step5_status.setText("Chưa đủ điều kiện")
            self.lbl_step5_status.setStyleSheet("font-size: 11px; font-weight: 500; color: #64748B; background: transparent;")

        # Bước 6
        if hl6:
            self.lbl_step6_status.setText("Nên chốt đợt")
            self.lbl_step6_status.setStyleSheet("font-size: 11px; font-weight: 700; color: #2563EB; background: transparent;")
        elif has_class:
            self.lbl_step6_status.setText("Đang làm việc")
            self.lbl_step6_status.setStyleSheet("font-size: 11px; font-weight: 500; color: #64748B; background: transparent;")
        else:
            self.lbl_step6_status.setText("Chưa có phiên")
            self.lbl_step6_status.setStyleSheet("font-size: 11px; font-weight: 500; color: #64748B; background: transparent;")

        # Apply styles and tooltips
        self._apply_step_button_style(self.btn_step1, hl1, step1_enabled, step1_tip)
        self._apply_step_button_style(self.btn_step2, hl2, step2_enabled, step2_tip)
        self._apply_step_button_style(self.btn_step3, hl3, step3_enabled, step3_tip)
        self._apply_step_button_style(self.btn_step4, hl4, step4_enabled, step4_tip)
        self._apply_step_button_style(self.btn_step5, hl5, step5_enabled, step5_tip)
        self._apply_step_button_style(self.btn_step6, hl6, step6_enabled, step6_tip)
        
        self.btn_rescan.setEnabled(has_class and submission_count > 0)

    # --------------------------------------------------------------------------
    # 4. Stat Cards (4 Columns) + Clean 12px Progress Bar
    # --------------------------------------------------------------------------
    def _build_stats_panel(self) -> QWidget:
        container = QWidget(self)
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(16)
        
        # 4 Cards Row (Pure text/numbers, no icon boxes)
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)
        
        self.mc_total = MetricCardWidget(
            "0", "Tổng Bài Nộp",
            tooltip_str="Tổng số bài thi của sinh viên đã nạp vào đợt chấm",
            value_color=COLOR_TEXT_PRIMARY
        )
        self.mc_ac = MetricCardWidget(
            "0", "AC (Đạt Chuẩn)",
            tooltip_str="AC = chạy đúng 100% testcase",
            value_color=COLOR_SUCCESS
        )
        self.mc_err = MetricCardWidget(
            "0", "Lỗi (WA / TLE / CE)",
            tooltip_str="Lỗi = WA (sai kết quả), TLE (quá thời gian), CE (lỗi biên dịch)",
            value_color=COLOR_ERROR
        )
        self.mc_avg = MetricCardWidget(
            "— / 10", "Điểm Trung Bình",
            tooltip_str="Điểm trung bình của các bài thi đã được chấm điểm (thang 10)",
            value_color=COLOR_PRIMARY
        )
        
        cards_layout.addWidget(self.mc_total)
        cards_layout.addWidget(self.mc_ac)
        cards_layout.addWidget(self.mc_err)
        cards_layout.addWidget(self.mc_avg)
        c_layout.addLayout(cards_layout)
        
        # Progress Card (Clean 10-12px Progress Bar)
        prog_card = QFrame(container)
        prog_card.setProperty("class", "Card")
        p_layout = QVBoxLayout(prog_card)
        p_layout.setContentsMargins(20, 14, 20, 14)
        p_layout.setSpacing(10)
        
        top_p = QHBoxLayout()
        self.lbl_progress_status = QLabel("Chưa có bài nộp", prog_card)
        self.lbl_progress_status.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {COLOR_TEXT_PRIMARY};")
        top_p.addWidget(self.lbl_progress_status)
        top_p.addStretch(1)
        
        self.lbl_progress_detail = QLabel("0/0 bài", prog_card)
        self.lbl_progress_detail.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {COLOR_PRIMARY};")
        top_p.addWidget(self.lbl_progress_detail)
        p_layout.addLayout(top_p)
        
        self.progress_bar = QProgressBar(prog_card)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(12)
        p_layout.addWidget(self.progress_bar)
        
        c_layout.addWidget(prog_card)
        return container

    # --------------------------------------------------------------------------
    # 5. Submissions DataTable & Table Empty State
    # --------------------------------------------------------------------------
    def _build_table_card(self) -> QFrame:
        card = QFrame(self)
        card.setProperty("class", "Card")
        layout = QVBoxLayout(card)
        # Yêu cầu 14: Thêm padding dưới bảng 12px (từ 16px lên 28px) để không bị cắt nửa nút ở dòng cuối
        layout.setContentsMargins(18, 16, 18, 28)
        layout.setSpacing(12)
        
        # Table Header Row
        header_row = QHBoxLayout()
        lbl_title = QLabel("Danh Sách Bài Nộp & Bảng Điểm Thời Gian Thực", card)
        lbl_title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {COLOR_TEXT_PRIMARY};")
        header_row.addWidget(lbl_title)
        
        header_row.addStretch(1)
        
        # Yêu cầu 14: Dòng gợi ý chữ 13px, #475569, line-height 1.4
        self.lbl_hint = QLabel("Bấm 'Chi Tiết' để xem mã nguồn, log thực thi hoặc kích hoạt AI Code Review", card)
        self.lbl_hint.setStyleSheet("font-size: 13px; color: #475569; line-height: 1.4;")
        header_row.addWidget(self.lbl_hint)
        layout.addLayout(header_row)
        
        # Stacked body: Index 0 = Table, Index 1 = Empty State inside table card
        self.table_stack = QStackedWidget(card)
        
        # Page 0: Table Widget
        self.table = QTableWidget(card)
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "#", "Sinh Viên (MSSV & Họ Tên)", "Tệp Nộp", "Ngôn Ngữ",
            "Thời Gian", "Bộ Nhớ", "Trạng Thái", "Điểm Số", "Chấm Tay", "Thao Tác"
        ])
        
        # Yêu cầu 8: Tiêu đề cùng hướng với nội dung (cột Sinh Viên, Tệp Nộp căn trái; các cột số, trạng thái căn giữa)
        center_cols = [0, 3, 4, 5, 6, 7, 8, 9]
        left_cols = [1, 2]
        for col in center_cols:
            h_it = self.table.horizontalHeaderItem(col)
            if h_it:
                h_it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        for col in left_cols:
            h_it = self.table.horizontalHeaderItem(col)
            if h_it:
                h_it.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # Tooltip for "Chấm Tay" header
        h_chamtay = self.table.horizontalHeaderItem(8)
        if h_chamtay:
            h_chamtay.setToolTip("Điểm được giảng viên chấm thủ công hoặc ghi đè sau phúc khảo")
        
        self.table.setWordWrap(False)
        self.table.setTextElideMode(Qt.TextElideMode.ElideRight)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Student column balanced
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 48)
        self.table.setColumnWidth(2, 130)
        self.table.setColumnWidth(3, 85)
        self.table.setColumnWidth(4, 105)
        self.table.setColumnWidth(5, 105)
        self.table.setColumnWidth(6, 145)
        self.table.setColumnWidth(7, 100)
        self.table.setColumnWidth(8, 105)
        self.table.setColumnWidth(9, 105)
        
        # Table header font size 13px bold
        h_font = QFont("Inter", 10, QFont.Weight.Bold)
        header.setFont(h_font)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # Yêu cầu 6 & 14: Tô nền cả dòng đồng nhất khi chọn (không có viền lặp từng ô), thanh cuộn dọc rõ hơn 11px
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLOR_SURFACE};
                border: 1px solid {COLOR_BORDER_DEFAULT};
                border-radius: 12px;
                gridline-color: transparent;
                outline: none;
                selection-background-color: {COLOR_PRIMARY_BG};
                selection-color: {COLOR_TEXT_PRIMARY};
            }}
            QTableWidget::item {{
                border: none;
                border-bottom: 1px solid {COLOR_BORDER_LIGHT};
                padding: 6px 12px;
            }}
            QTableWidget::item:selected {{
                background-color: {COLOR_PRIMARY_BG};
                color: {COLOR_TEXT_PRIMARY};
                border: none;
                border-bottom: 1px solid {COLOR_BORDER_LIGHT};
            }}
            QTableWidget::item:hover {{
                background-color: {COLOR_SURFACE_SECONDARY};
            }}
            QScrollBar:vertical {{
                border: none;
                background: #F1F5F9;
                width: 11px;
                border-radius: 5px;
                margin: 2px 0 2px 0;
            }}
            QScrollBar::handle:vertical {{
                background: #CBD5E1;
                border-radius: 5px;
                min-height: 32px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #94A3B8;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        self.table_stack.addWidget(self.table)
        
        # Page 1: Empty state inside table card
        self.table_empty_widget = QWidget(card)
        tew_layout = QVBoxLayout(self.table_empty_widget)
        tew_layout.setContentsMargins(40, 48, 40, 48)
        tew_layout.setSpacing(14)
        tew_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_empty_title = QLabel("Chưa có bài nộp", self.table_empty_widget)
        lbl_empty_title.setStyleSheet("font-size: 18px; font-weight: 700; color: #1E293B;")
        lbl_empty_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tew_layout.addWidget(lbl_empty_title)
        
        lbl_empty_sub = QLabel("Bấm 'Nạp Bài Nộp' để chọn thư mục bài làm của sinh viên", self.table_empty_widget)
        lbl_empty_sub.setStyleSheet("font-size: 13px; color: #64748B; line-height: 1.4;")
        lbl_empty_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tew_layout.addWidget(lbl_empty_sub)
        
        btn_table_ingest = QPushButton("Nạp Bài Nộp", self.table_empty_widget)
        btn_table_ingest.setProperty("class", "PrimaryBtn")
        btn_table_ingest.setFixedHeight(40)
        btn_table_ingest.setMinimumWidth(160)
        btn_table_ingest.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_table_ingest.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-weight: 700;
                font-size: 13px;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_HOVER};
            }}
        """)
        btn_table_ingest.clicked.connect(self._handle_step1_ingest)
        tew_layout.addWidget(btn_table_ingest, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.table_stack.addWidget(self.table_empty_widget)
        layout.addWidget(self.table_stack)
        
        return card

    # --------------------------------------------------------------------------
    # 6. Database Loaders & Table Rendering
    # --------------------------------------------------------------------------
    def _load_classes_selector(self, target_class_id: Optional[int] = None):
        """Loads all class sessions from SQLite database into top class_selector."""
        self.class_selector.blockSignals(True)
        self.class_selector.clear()
        classes = self.db.get_all_classes()
        
        if not classes:
            self.class_selector.addItem("-- Chưa có đợt chấm nào --", None)
            self.class_selector.setEnabled(False)  # Yêu cầu 5: disable khi không có đợt nào trong lịch sử
            self.current_class_id = None
            self.table.setRowCount(0)
            self.mc_total.set_value("0")
            self.mc_ac.set_value("0")
            self.mc_err.set_value("0")
            self.mc_avg.set_value("— / 10")
            self.lbl_progress_status.setText("Chưa có bài nộp")
            self.lbl_progress_detail.setText("0/0 bài")
            self.progress_bar.setValue(0)
            self.content_stack.setCurrentIndex(0)
            self._update_step_buttons(0, 0, 0)
            self.class_selector.blockSignals(False)
            return

        self.class_selector.setEnabled(True)  # Yêu cầu 5: enable khi có đợt trong lịch sử
        self.class_selector.addItem("-- Chọn đợt chấm bài --", None)
        target_index = 0
        for idx, c in enumerate(classes, start=1):
            label = f"[{c['course_code']}] {c['class_name']} — Ngôn ngữ: {c['programming_language']}"
            self.class_selector.addItem(label, c["id"])
            if target_class_id is not None and c["id"] == target_class_id:
                target_index = idx

        self.class_selector.setCurrentIndex(target_index)
        self.class_selector.blockSignals(False)
        
        if target_index > 0:
            self._on_class_selected()
        else:
            self.current_class_id = None
            self.content_stack.setCurrentIndex(0)
            self._update_step_buttons(0, 0, 0)

    def _on_class_selected(self):
        """Triggered when user selects a different class session from dropdown."""
        self.has_exported_grades = False
        class_id = self.class_selector.currentData()
        if class_id is None:
            self.current_class_id = None
            self.content_stack.setCurrentIndex(0)
            self._update_step_buttons(0, 0, 0)
        else:
            self.current_class_id = class_id
            self.content_stack.setCurrentIndex(1)
            self._load_submissions_table(class_id)

    def _load_submissions_table(self, class_id: int):
        """Loads and renders student submissions for the specified class from SQLite."""
        submissions = self.db.get_submissions_by_class(class_id)
        testcases = self.db.get_testcases_by_class(class_id)
        testcase_count = len(testcases)
        
        classes = self.db.get_all_classes()
        class_info = next((c for c in classes if c["id"] == class_id), None)
        lang = class_info.get("programming_language", "C") if class_info else "C"
        
        total_ac = 0
        total_errors = 0
        total_score_sum = 0.0
        graded_count = 0
        
        # Check if submissions empty -> show empty state widget inside table card
        if not submissions:
            self.table_stack.setCurrentIndex(1)
            self.lbl_hint.setVisible(False)
            self.table.setRowCount(0)
            self.lbl_progress_status.setText("Chưa có bài nộp")
            self.lbl_progress_detail.setText("0/0 bài")
            self.progress_bar.setValue(0)
            self.mc_total.set_value("0")
            self.mc_ac.set_value("0")
            self.mc_err.set_value("0")
            self.mc_avg.set_value("— / 10")
            self._update_step_buttons(0, 0, testcase_count)
            return

        self.table_stack.setCurrentIndex(0)
        self.lbl_hint.setVisible(True)
        self.table.setRowCount(len(submissions))

        # Yêu cầu 9: Đếm tần suất MSSV để phát hiện trùng
        mssv_list = [str(s.get("student_mssv", "")).strip() for s in submissions if s.get("student_mssv")]
        mssv_counts = Counter(mssv_list)

        for row_idx, sub in enumerate(submissions):
            mssv = str(sub.get("student_mssv", "")).strip()
            raw_name = (sub.get("student_name") or "").strip()
            is_duplicate = (mssv_counts.get(mssv, 0) > 1)
            file_path = sub["source_file_path"]
            fname = Path(file_path).name
            verdict = sub.get("final_verdict") or sub.get("status") or "PENDING"
            
            score_num = sub.get("calculated_score")
            score_str = f"{score_num:.1f} / 10" if score_num is not None and verdict != "PENDING" else "—"
            runtime_str = f"{sub.get('execution_time_ms', 0):.0f} ms" if verdict != "PENDING" else "—"
            ram_str = f"{sub.get('memory_used_mb', 0):.1f} MB" if verdict != "PENDING" else "—"
            if sub.get("manual_override_score") is not None:
                override_text = f"Ghi đè: {sub.get('manual_override_score'):.1f}"
            else:
                override_text = "Tự động"

            if verdict == "AC":
                total_ac += 1
            elif verdict in ("WA", "TLE", "MLE", "CE", "RE"):
                total_errors += 1

            if verdict != "PENDING" and score_num is not None:
                total_score_sum += score_num
                graded_count += 1

            self.table.setRowHeight(row_idx, 52)

            # 0: STT (Center)
            item_stt = QTableWidgetItem(str(row_idx + 1))
            item_stt.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 0, item_stt)

            # 1: Sinh Viên (Left-aligned) - Yêu cầu 9: Hiển thị cảnh báo nhỏ 'MSSV trùng' nếu trùng; cột họ tên rỗng hiển thị '(chưa có tên)' màu xám
            cell_student = QWidget(self.table)
            cell_student.setStyleSheet("background: transparent;")
            cs_layout = QHBoxLayout(cell_student)
            cs_layout.setContentsMargins(12, 0, 12, 0)
            cs_layout.setSpacing(6)
            
            lbl_mssv = QLabel(mssv, cell_student)
            lbl_mssv.setStyleSheet("font-size: 13px; font-weight: 600; color: #1E293B; background: transparent;")
            cs_layout.addWidget(lbl_mssv)
            
            if is_duplicate:
                lbl_dup = QLabel("MSSV trùng", cell_student)
                lbl_dup.setStyleSheet("""
                    background-color: #FEF2F2;
                    color: #DC2626;
                    border: 1px solid #FECACA;
                    border-radius: 4px;
                    font-size: 10px;
                    font-weight: 700;
                    padding: 1px 4px;
                """)
                cs_layout.addWidget(lbl_dup)
                
            lbl_sep = QLabel("—", cell_student)
            lbl_sep.setStyleSheet("font-size: 12px; color: #94A3B8; background: transparent;")
            cs_layout.addWidget(lbl_sep)
            
            if raw_name:
                lbl_name = QLabel(raw_name, cell_student)
                lbl_name.setStyleSheet("font-size: 13px; font-weight: 500; color: #334155; background: transparent;")
            else:
                lbl_name = QLabel("(chưa có tên)", cell_student)
                lbl_name.setStyleSheet("font-size: 12px; font-style: italic; color: #94A3B8; background: transparent;")
            cs_layout.addWidget(lbl_name)
            cs_layout.addStretch(1)
            
            self.table.setCellWidget(row_idx, 1, cell_student)

            # 2: File (Left-aligned)
            item_fname = QTableWidgetItem(fname)
            item_fname.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row_idx, 2, item_fname)

            # 3: Lang (Center-aligned) - Yêu cầu 8: cùng hướng tiêu đề căn giữa
            item_lang = QTableWidgetItem(lang)
            item_lang.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 3, item_lang)

            # 4: Runtime (Center)
            item_runtime = QTableWidgetItem(runtime_str)
            item_runtime.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 4, item_runtime)

            # 5: RAM (Center)
            item_ram = QTableWidgetItem(ram_str)
            item_ram.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 5, item_ram)

            # 6: Verdict Pill (Badge) (Center)
            pill = VerdictPill(verdict)
            self.table.setCellWidget(row_idx, 6, pill)

            # 7: Score (Center)
            item_score = QTableWidgetItem(score_str)
            item_score.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_score.setFont(QFont("Inter", 10, QFont.Weight.Bold))
            if "10.0" in score_str:
                item_score.setForeground(QColor(COLOR_SUCCESS))
            elif score_str != "—":
                item_score.setForeground(QColor(COLOR_PRIMARY))
            self.table.setItem(row_idx, 7, item_score)

            # 8: Chấm Tay (Center) - Yêu cầu 7: Thống nhất màu chữ và nền, bỏ nền xám lẻ
            item_override = QTableWidgetItem(override_text)
            item_override.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if override_text != "Tự động":
                item_override.setForeground(QColor("#D97706"))
                item_override.setFont(QFont("Inter", 9, QFont.Weight.DemiBold))
            else:
                item_override.setForeground(QColor("#64748B"))
                item_override.setFont(QFont("Inter", 9, QFont.Weight.Normal))
            self.table.setItem(row_idx, 8, item_override)

            # 9: Action Button (Center)
            btn_view = QPushButton("Chi Tiết", self.table)
            btn_view.setFixedHeight(32)
            btn_view.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_view.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_SURFACE};
                    color: {COLOR_PRIMARY};
                    border: 1px solid {COLOR_PRIMARY};
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: 600;
                    padding: 0 10px;
                }}
                QPushButton:hover {{
                    background-color: {COLOR_PRIMARY_BG};
                }}
            """)
            btn_view.clicked.connect(lambda checked, s_dict=sub, v=verdict, sc=score_str: self._open_detail_dialog(s_dict, v, sc))
            self.table.setCellWidget(row_idx, 9, btn_view)

        # Update metrics cards
        avg_score = round(total_score_sum / graded_count, 1) if graded_count > 0 else 0.0
        self.mc_total.set_value(str(len(submissions)))
        self.mc_ac.set_value(str(total_ac))
        self.mc_err.set_value(str(total_errors))
        self.mc_avg.set_value(f"{avg_score} / 10" if graded_count > 0 else "— / 10")
        
        # Yêu cầu 13: Cập nhật dòng tiến độ 'Đã chấm X/X bài' khi xong, 'Chưa chấm' khi chưa chấm
        sub_count = len(submissions)
        if sub_count == 0:
            self.lbl_progress_status.setText("Chưa có bài nộp")
            self.lbl_progress_detail.setText("0/0 bài")
            self.progress_bar.setValue(0)
        elif graded_count == 0:
            self.lbl_progress_status.setText("Chưa chấm")
            self.lbl_progress_detail.setText(f"0/{sub_count} bài")
            self.progress_bar.setValue(0)
        elif graded_count == sub_count:
            self.lbl_progress_status.setText(f"Đã chấm {graded_count}/{sub_count} bài")
            self.lbl_progress_detail.setText(f"{graded_count}/{sub_count} bài")
            self.progress_bar.setValue(100)
        else:
            self.lbl_progress_status.setText(f"Đang chấm ({graded_count}/{sub_count} bài)")
            self.lbl_progress_detail.setText(f"{graded_count}/{sub_count} bài")
            percent = int((graded_count / sub_count) * 100)
            self.progress_bar.setValue(percent)

        # Update step buttons states
        self._update_step_buttons(sub_count, graded_count, testcase_count)

    # --------------------------------------------------------------------------
    # 7. Action Handlers (Wizard, Ingest, Rescan, Testcases, Batch Grade, Export)
    # --------------------------------------------------------------------------
    def _open_session_dialog(self):
        """Wizard 3 bước tạo phiên chấm mới."""
        step = 1
        created_class_id = None

        while step in (1, 2, 3):
            if step == 1:
                dlg_session = SessionDialog(self, existing_class_id=created_class_id)
                dlg_session.setWindowTitle("Bước 1/3: Khởi Tạo Đợt Chấm Mới & Nạp Bài Nộp")
                if dlg_session.exec() != QDialog.DialogCode.Accepted:
                    return

                created_class_id = getattr(dlg_session, "created_class_id", None)
                if not created_class_id:
                    return
                step = 2

            elif step == 2:
                dlg_settings = SettingsDialog(self, is_wizard=True)
                dlg_settings.exec()
                if getattr(dlg_settings, "nav_back", False):
                    step = 1
                elif getattr(dlg_settings, "is_saved", False):
                    step = 3
                else:
                    return

            elif step == 3:
                dlg_testcase = TestcaseDialog(self, class_id=created_class_id, is_wizard=True)
                res = dlg_testcase.exec()
                if getattr(dlg_testcase, "nav_back", False):
                    step = 2
                elif res == QDialog.DialogCode.Accepted:
                    break
                else:
                    return

        self._load_classes_selector(target_class_id=created_class_id)

        QMessageBox.information(
            self,
            "Hoàn Tất Thiết Lập",
            "Đã hoàn thành toàn bộ quy trình cấu hình đợt chấm bài!\n\n"
            "• Bước 1: Khởi tạo đợt chấm & nạp mã nguồn thành công\n"
            "• Bước 2: Cấu hình môi trường biên dịch & Sandbox sẵn sàng\n"
            "• Bước 3: Bộ Testcase & thuật toán so khớp đã được thiết lập\n\n"
            "Màn hình chấm bài đã sẵn sàng! Bạn có thể bắt đầu chấm bài ngay."
        )

    def _handle_step1_ingest(self):
        """Step 1: Choose directory and ingest submissions for current session."""
        if not self.current_class_id:
            QMessageBox.information(
                self, "Chưa Chọn Đợt Chấm",
                "Vui lòng chọn hoặc tạo đợt chấm trước khi nạp bài nộp!"
            )
            return

        folder = QFileDialog.getExistingDirectory(self, "Chọn Thư Mục Chứa Bài Nộp Của Sinh Viên")
        if not folder:
            return

        classes = self.db.get_all_classes()
        class_info = next((c for c in classes if c["id"] == self.current_class_id), None)
        lang = class_info.get("programming_language", "C") if class_info else "C"

        scanned = self._scan_submissions_directory(folder, lang)
        valid_items = scanned["valid"]
        if not valid_items:
            QMessageBox.warning(
                self, "Không Tìm Thấy Bài Nộp",
                "Thư mục đã chọn không có file hoặc thư mục bài nộp hợp lệ nào khớp mã sinh viên!"
            )
            return

        # Lưu đường dẫn thư mục vào class
        try:
            with self.db.get_connection() as conn:
                conn.execute(
                    "UPDATE local_classes SET submissions_dir_path = ? WHERE id = ?",
                    (folder, self.current_class_id)
                )
        except Exception:
            pass

        # Đồng bộ vào CSDL (giữ nguyên điểm các bài cũ)
        added, existing = self.db.rescan_and_sync_submissions(self.current_class_id, valid_items)
        self._load_submissions_table(self.current_class_id)

        QMessageBox.information(
            self, "Nạp Bài Nộp Thành Công",
            f"Đã cập nhật bài nộp từ thư mục:\n{folder}\n\n"
            f"• Số bài nhận diện hợp lệ: {len(valid_items)}\n"
            f"• Bài mới được thêm vào: {added}\n"
            f"• Bài đã tồn tại (giữ nguyên điểm): {existing}"
        )

    def _handle_rescan_directory(self):
        """Rescans the existing submission directory without deleting or resetting grades."""
        if not self.current_class_id:
            return

        classes = self.db.get_all_classes()
        class_info = next((c for c in classes if c["id"] == self.current_class_id), None)
        if not class_info:
            return

        folder = class_info.get("submissions_dir_path")
        if not folder or not Path(folder).exists():
            # If not yet set, prompt to select
            self._handle_step1_ingest()
            return

        lang = class_info.get("programming_language", "C")
        scanned = self._scan_submissions_directory(folder, lang)
        valid_items = scanned["valid"]

        added, existing = self.db.rescan_and_sync_submissions(self.current_class_id, valid_items)
        self._load_submissions_table(self.current_class_id)

        msg = (
            f"Quét lại thư mục thành công:\n{folder}\n\n"
            f"• Tổng số bài hiện có trong thư mục: {len(valid_items)}\n"
            f"• Bài mới được thêm vào: {added}\n"
            f"• Bài đã có điểm (được bảo lưu): {existing}"
        )
        if scanned["duplicates"]:
            msg += f"\n• Cảnh báo MSSV trùng: {len(scanned['duplicates'])} bài"
        if scanned["invalid"]:
            msg += f"\n• Mục không nhận diện được: {len(scanned['invalid'])} mục"

        QMessageBox.information(self, "Kết Quả Quét Lại", msg)

    def _scan_submissions_directory(self, folder_path: str, programming_language: str) -> Dict[str, Any]:
        """Scans submissions directory using regex student code extraction."""
        p = Path(folder_path)
        valid = []
        invalid = []
        duplicates = []
        seen_mssv = set()

        ext_map = {
            "C": [".c"],
            "C++": [".cpp", ".cc", ".cxx"],
            "Java": [".java"],
            "Python": [".py"]
        }
        valid_exts = ext_map.get(programming_language, [".c", ".cpp", ".java", ".py"])
        pattern = re.compile(r"^([a-zA-Z]{2,4}\d{4,8})(?:[_-](.*))?$", re.IGNORECASE)

        try:
            for entry in sorted(p.iterdir(), key=lambda x: x.name.lower()):
                if entry.name.startswith("."):
                    continue

                if entry.is_dir():
                    raw_name = entry.name
                    match = pattern.match(raw_name)
                    if not match:
                        invalid.append({"name": raw_name, "reason": "Tên thư mục không bắt đầu bằng MSSV chuẩn (ví dụ: SE180001)"})
                        continue

                    mssv = match.group(1).upper()
                    student_name = (match.group(2) or "").strip().replace("_", " ")

                    source_file = None
                    for ext in valid_exts:
                        candidates = list(entry.glob(f"*{ext}"))
                        if candidates:
                            source_file = candidates[0]
                            break

                    if not source_file:
                        invalid.append({"name": raw_name, "reason": f"Không tìm thấy file mã nguồn {programming_language} ({', '.join(valid_exts)})"})
                        continue

                    if mssv in seen_mssv:
                        duplicates.append(mssv)
                    seen_mssv.add(mssv)

                    valid.append({
                        "student_mssv": mssv,
                        "student_name": student_name,
                        "source_file_path": str(source_file)
                    })

                elif entry.is_file():
                    raw_stem = entry.stem
                    raw_ext = entry.suffix.lower()

                    if raw_ext not in valid_exts:
                        continue

                    match = pattern.match(raw_stem)
                    if not match:
                        invalid.append({"name": entry.name, "reason": "Tên file không bắt đầu bằng MSSV chuẩn (ví dụ: SE180001.c)"})
                        continue

                    mssv = match.group(1).upper()
                    student_name = (match.group(2) or "").strip().replace("_", " ")

                    if mssv in seen_mssv:
                        duplicates.append(mssv)
                    seen_mssv.add(mssv)

                    valid.append({
                        "student_mssv": mssv,
                        "student_name": student_name,
                        "source_file_path": str(entry)
                    })
        except Exception as ex:
            invalid.append({"name": "Thư mục", "reason": f"Lỗi đọc thư mục: {str(ex)}"})

        return {"valid": valid, "invalid": invalid, "duplicates": duplicates}

    def _open_testcase_dialog(self):
        class_id = self.class_selector.currentData() or self.current_class_id
        if not class_id:
            QMessageBox.information(
                self, "Chưa Chọn Đợt Chấm",
                "Vui lòng tạo hoặc chọn một đợt chấm trước khi cấu hình Testcase!"
            )
            return
        dlg = TestcaseDialog(self, class_id=class_id)
        dlg.exec()
        self._load_submissions_table(class_id)

    def _open_history_dialog(self):
        """Opens grading history dialog and syncs session list."""
        dlg = HistoryDialog(self)
        dlg.session_deleted.connect(self._on_history_session_deleted)
        
        result = dlg.exec()
        if result == QDialog.DialogCode.Accepted and dlg.selected_class_id:
            self._load_classes_selector(target_class_id=dlg.selected_class_id)
        else:
            target_id = self.current_class_id
            if target_id and not self.db.get_class_by_id(target_id):
                target_id = None
            self._load_classes_selector(target_class_id=target_id)

    def _on_history_session_deleted(self, deleted_class_id: int):
        """Real-time synchronization when a session is deleted."""
        if self.current_class_id == deleted_class_id:
            self.current_class_id = None
            self.table.setRowCount(0)
            self.mc_total.set_value("0")
            self.mc_ac.set_value("0")
            self.mc_err.set_value("0")
            self.mc_avg.set_value("— / 10")
            self.lbl_progress_status.setText("Chưa có bài nộp")
            self.lbl_progress_detail.setText("0/0 bài")
        self._load_classes_selector(target_class_id=self.current_class_id)

    def _open_guide_dialog(self):
        dlg = GradingGuideDialog(self)
        dlg.exec()

    def _open_settings_dialog(self):
        dlg = SettingsDialog(self)
        dlg.exec()

    def _open_detail_dialog(self, sub_dict, verdict, score):
        dlg = SubmissionDetailDialog(
            submission_id=sub_dict.get("id"),
            mssv=sub_dict.get("student_mssv", "SE180000"),
            file_name=Path(sub_dict.get("source_file_path", "code.c")).name,
            source_file_path=sub_dict.get("source_file_path"),
            verdict=verdict,
            score=score,
            parent=self
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            class_id = self.class_selector.currentData() or self.current_class_id
            if class_id:
                self._load_submissions_table(class_id)

    def _open_plagiarism_dialog(self):
        class_id = self.class_selector.currentData() or self.current_class_id
        if not class_id:
            QMessageBox.warning(self, "Chưa Chọn Đợt Chấm", "Vui lòng chọn đợt chấm bài trước!")
            return
        dlg = PlagiarismDialog(self, class_id=class_id)
        dlg.exec()

    def _start_batch_grade(self):
        class_id = self.class_selector.currentData()
        if not class_id:
            QMessageBox.warning(self, "Chưa Chọn Đợt Chấm", "Vui lòng chọn đợt chấm bài từ danh sách!")
            return

        testcases = self.db.get_testcases_by_class(class_id)
        if not testcases:
            ret = QMessageBox.question(
                self,
                "Chưa Có Testcase",
                "Đợt chấm này chưa được thiết lập bất kỳ Testcase nào để chấm điểm!\n\n"
                "Bạn có muốn mở cửa sổ 'Cấu Hình Testcase & So Khớp' ngay bây giờ để thêm testcase không?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            if ret == QMessageBox.StandardButton.Yes:
                self._open_testcase_dialog()
            return

        submissions = self.db.get_submissions_by_class(class_id)
        if not submissions:
            QMessageBox.warning(self, "Chưa Có Bài Nộp", "Đợt chấm này chưa có sinh viên nộp bài!")
            return

        self.progress_bar.setValue(0)
        total_count = len(submissions)
        self.lbl_progress_detail.setText(f"0/{total_count} bài (0%)")
        self.lbl_progress_status.setText(f"Đang khởi tạo tiến trình chấm song song ({total_count} bài)...")
        self.btn_step3.setEnabled(False)

        self._grading_worker = BatchGradingWorker(self.grading_service, class_id, parent=self)
        self._grading_worker.progress.connect(self._on_batch_grade_progress)
        self._grading_worker.finished_ok.connect(lambda count, secs: self._on_batch_grade_done(class_id, count, secs))
        self._grading_worker.failed.connect(self._on_batch_grade_failed)
        self._grading_worker.start()

    def _on_batch_grade_progress(self, curr: int, total: int, mssv: str):
        percent = int((curr / total) * 100) if total else 0
        self.progress_bar.setValue(percent)
        self.lbl_progress_detail.setText(f"{curr}/{total} bài ({percent}%)")
        self.lbl_progress_status.setText(f"Đang chấm: {mssv}")

    def _on_batch_grade_done(self, class_id: int, count: int, elapsed_seconds: float):
        self.progress_bar.setValue(100)
        self.lbl_progress_status.setText(f"Có {count} bài nộp")
        self.lbl_progress_detail.setText(f"{count}/{count} bài")
        self.btn_step3.setEnabled(True)
        self._load_submissions_table(class_id)

        QMessageBox.information(
            self,
            "Chấm Bài Thành Công",
            f"Chấm xong {count} bài trong {elapsed_seconds:.1f} giây!\n\n"
            f"• Luồng xử lý nền đa tiến trình (ProcessPoolExecutor 4-8 workers) đã hoàn tất.\n"
            f"• Thuật toán so khớp: 7 chế độ tự động\n"
            f"• Giám sát Sandbox: RAM & CPU đo thời gian thực\n"
            f"• CSDL: Toàn bộ điểm số đã được ghi an toàn vào SQLite cục bộ (local_grading.db)."
        )

    def _on_batch_grade_failed(self, message: str):
        self.btn_step3.setEnabled(True)
        self.progress_bar.setValue(0)
        self.lbl_progress_status.setText("Chấm bài thất bại")
        QMessageBox.critical(self, "Lỗi Quá Trình Chấm", f"Có lỗi xảy ra trong quá trình chấm:\n{message}")

    # --------------------------------------------------------------------------
    # 8. Step 5 Export Menu (CSV, Excel, PDF)
    # --------------------------------------------------------------------------
    def _handle_step5_export_menu(self):
        """Shows format chooser popup menu: CSV (.csv), Excel (.xlsx), PDF (.pdf)."""
        class_id = self.class_selector.currentData() or self.current_class_id
        if not class_id:
            return

        submissions = self.db.get_submissions_by_class(class_id)
        graded_count = sum(1 for s in submissions if s.get("calculated_score") is not None and s.get("final_verdict") != "PENDING")
        if graded_count == 0:
            QMessageBox.warning(
                self, "Chưa Có Điểm",
                "Chưa có bài thi nào được chấm điểm để xuất bảng điểm!"
            )
            return

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 6px;
                font-size: 13px;
            }
            QMenu::item {
                padding: 8px 18px;
                border-radius: 4px;
                color: #1E293B;
            }
            QMenu::item:selected {
                background-color: #EFF6FF;
                color: #2F80ED;
            }
        """)

        act_csv = menu.addAction("Xuất File CSV (.csv)")
        act_excel = menu.addAction("Xuất File Excel (.xlsx)")
        act_pdf = menu.addAction("Xuất File Báo Cáo PDF (.pdf)")

        action = menu.exec(QCursor.pos())
        if action == act_csv:
            self._export_to_csv(class_id, submissions)
        elif action == act_excel:
            self._export_to_excel(class_id, submissions)
        elif action == act_pdf:
            self._export_to_pdf(class_id, submissions)

    def _notify_export_success(self, title: str, file_path: str):
        """Shows a success dialog offering to open the containing folder (AT02)."""
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Information)
        box.setWindowTitle("Xuất Thành Công")
        box.setText(title)
        box.setInformativeText(file_path)
        open_btn = box.addButton("Mở Thư Mục", QMessageBox.ButtonRole.ActionRole)
        box.addButton("Đóng", QMessageBox.ButtonRole.AcceptRole)
        box.exec()
        if box.clickedButton() is open_btn:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(file_path).parent)))

    def _export_to_csv(self, class_id: int, submissions: List[Dict[str, Any]]):
        file_path, _ = QFileDialog.getSaveFileName(self, "Lưu Bảng Điểm CSV", "results.csv", "CSV Files (*.csv)")
        if not file_path:
            return

        testcases = self.db.get_testcases_by_class(class_id)
        try:
            export = ExportService()
            rows = export.build_grade_rows(submissions, len(testcases))
            export.export_csv(rows, file_path)
        except PermissionError:
            QMessageBox.critical(
                self, "Không Thể Ghi File",
                "Không thể ghi file. File kết quả đang được mở bởi ứng dụng khác. "
                "Vui lòng đóng file và thử lại."
            )
            return
        except Exception as ex:
            QMessageBox.critical(self, "Lỗi Xuất File", f"Không thể xuất file CSV:\n{str(ex)}")
            return

        self.has_exported_grades = True
        graded = sum(1 for s in submissions if s.get("calculated_score") is not None and s.get("final_verdict") != "PENDING")
        self._update_step_buttons(len(submissions), graded, len(testcases))
        self._notify_export_success("Đã xuất bảng điểm results.csv (7 cột) thành công.", file_path)

    def _export_to_excel(self, class_id: int, submissions: List[Dict[str, Any]]):
        file_path, _ = QFileDialog.getSaveFileName(self, "Lưu Bảng Điểm Excel", "bang_diem.xlsx", "Excel Files (*.xlsx)")
        if not file_path:
            return

        testcases = self.db.get_testcases_by_class(class_id)
        classes = self.db.get_all_classes()
        c_info = next((c for c in classes if c["id"] == class_id), None)
        c_name = c_info.get("class_name", "") if c_info else ""
        c_code = c_info.get("course_code", "") if c_info else ""

        try:
            export = ExportService()
            rows = export.build_grade_rows(submissions, len(testcases))
            export.export_excel(rows, file_path, class_name=c_name, course_code=c_code)
        except PermissionError:
            QMessageBox.critical(
                self, "Không Thể Ghi File",
                "Không thể ghi file. File kết quả đang được mở bởi ứng dụng khác. "
                "Vui lòng đóng file Excel và thử lại."
            )
            return
        except Exception as ex:
            QMessageBox.critical(self, "Lỗi Xuất Excel", f"Không thể xuất file Excel:\n{str(ex)}")
            return

        self.has_exported_grades = True
        graded = sum(1 for s in submissions if s.get("calculated_score") is not None and s.get("final_verdict") != "PENDING")
        self._update_step_buttons(len(submissions), graded, len(testcases))
        self._notify_export_success("Đã xuất bảng điểm Excel (.xlsx) thành công.", file_path)

    def _export_to_pdf(self, class_id: int, submissions: List[Dict[str, Any]]):
        file_path, _ = QFileDialog.getSaveFileName(self, "Lưu Bảng Điểm PDF", "bang_diem.pdf", "PDF Files (*.pdf)")
        if not file_path:
            return

        testcases = self.db.get_testcases_by_class(class_id)
        classes = self.db.get_all_classes()
        c_info = next((c for c in classes if c["id"] == class_id), None)
        c_name = c_info.get("class_name", "") if c_info else ""
        c_code = c_info.get("course_code", "") if c_info else ""
        c_lang = c_info.get("programming_language", "C") if c_info else "C"

        try:
            export = ExportService()
            rows = export.build_grade_rows(submissions, len(testcases))
            html_content = export.build_report_html(rows, class_name=c_name, course_code=c_code, language=c_lang)

            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(file_path)

            doc = QTextDocument()
            doc.setHtml(html_content)
            doc.print(printer)
        except PermissionError:
            QMessageBox.critical(
                self, "Không Thể Ghi File",
                "Không thể ghi file. File kết quả đang được mở bởi ứng dụng khác. "
                "Vui lòng đóng file và thử lại."
            )
            return
        except Exception as ex:
            QMessageBox.critical(self, "Lỗi Xuất PDF", f"Không thể xuất file PDF:\n{str(ex)}")
            return

        self.has_exported_grades = True
        graded = sum(1 for s in submissions if s.get("calculated_score") is not None and s.get("final_verdict") != "PENDING")
        self._update_step_buttons(len(submissions), graded, len(testcases))
        self._notify_export_success("Đã xuất bảng điểm PDF thành công.", file_path)

    def _handle_step6_end_session(self):
        """Step 6: End and finalize the current grading session."""
        if not self.current_class_id:
            QMessageBox.information(
                self, "Chưa Chọn Đợt Chấm",
                "Không có đợt chấm nào đang được mở để kết thúc!"
            )
            return

        classes = self.db.get_all_classes()
        class_info = next((c for c in classes if c["id"] == self.current_class_id), None)
        class_name = class_info.get("class_name", "") if class_info else ""

        # Yêu cầu 11: Hỏi xác nhận và nêu rõ hậu quả chốt đợt, không sửa điểm nữa
        ret = QMessageBox.question(
            self,
            "Xác Nhận Kết Thúc Phiên Chấm",
            f"Bạn có chắc chắn muốn kết thúc và chốt đợt chấm '{class_name}' không?\n\n"
            "Cảnh báo hậu quả:\n"
            "• Đợt thi này sẽ được chốt sổ kết quả; toàn bộ bảng điểm và bài thi sẽ được khóa, không thể chỉnh sửa điểm hay chấm lại sau khi chốt đợt.\n"
            "• Dữ liệu phiên chấm đã được lưu an toàn vào hệ thống và màn hình sẽ quay trở về trạng thái ban đầu.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if ret == QMessageBox.StandardButton.Yes:
            self.current_class_id = None
            self.has_exported_grades = False
            self.class_selector.blockSignals(True)
            self.class_selector.setCurrentIndex(0)
            self.class_selector.blockSignals(False)
            self.content_stack.setCurrentIndex(0)
            self._update_step_buttons(0, 0, 0)

            QMessageBox.information(
                self,
                "Đã Kết Thúc Phiên Chấm",
                f"Đã kết thúc phiên chấm thành công cho đợt '{class_name}'.\n"
                "Bạn có thể mở lại đợt thi này bất kỳ lúc nào từ danh sách đợt chấm hoặc menu Lịch Sử Đợt Chấm."
            )

    def _refresh_ai_quota(self):
        """Fetches live AI quota from Neon Postgres via GET /api/v1/ai/quota asynchronously."""
        class QuotaWorker(QThread):
            quota_received = pyqtSignal(dict)
            def run(self):
                ai_service = AiService()
                res = ai_service.get_quota()
                self.quota_received.emit(res)

        self.quota_worker = QuotaWorker()
        self.quota_worker.quota_received.connect(self._on_quota_received)
        self.quota_worker.start()

    def _on_quota_received(self, res: Dict[str, Any]):
        if hasattr(self, "lbl_ai_quota") and self.lbl_ai_quota:
            if res.get("success"):
                rem = res.get("remaining_tokens", 50000)
                limit = res.get("daily_limit_tokens", 50000)
                self.lbl_ai_quota.setText(f"Gemini AI: Còn {rem:,} / {limit:,} Tokens")
                self.lbl_ai_quota.setToolTip(
                    f"Số token AI còn lại trong tháng:\n"
                    f"• Hạn mức: {limit:,} tokens\n"
                    f"• Còn lại: {rem:,} tokens\n"
                    f"• Đã dùng hôm nay: {res.get('used_tokens_today', 0):,} tokens"
                )
            else:
                self.lbl_ai_quota.setText("Gemini AI: Sẵn Sàng")
                self.lbl_ai_quota.setToolTip("Số token AI còn lại trong tháng")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Inter", 9)
    app.setFont(font)
    
    window = AITAMainWindow()
    window.show()
    sys.exit(app.exec())
