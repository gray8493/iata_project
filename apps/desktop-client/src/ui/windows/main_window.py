"""
AITA Desktop Client - Primary Workspace Window (PyQt6)
Standard Implementation matching DESKTOP APP UI/UX DESIGN SYSTEM
Style: Modern Educational SaaS, 100% Light, Blue-focused (#2F80ED), Clean 240px Sidebar, 64px Header.
"""

import sys
import csv
from pathlib import Path
from typing import Optional, Dict, Any, List

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QCursor, QPainter, QBrush, QGuiApplication, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QProgressBar, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QMessageBox, QDialog,
    QSizePolicy, QStackedWidget
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
    Stat card matching Design System Section 14:
    min-height 120px, 40x40px icon box, big number 26px 700, description 13px #64748B.
    """

    def __init__(self, value: str, label: str, icon_str: str = "📊", value_color: str = COLOR_TEXT_PRIMARY, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("MetricCard")
        self.setProperty("class", "Card")
        self.setMinimumHeight(115)
        self.setStyleSheet(f"""
            QFrame#MetricCard {{
                background-color: {COLOR_SURFACE};
                border: 1px solid {COLOR_BORDER_DEFAULT};
                border-radius: {RADIUS_CARD};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)
        
        top_row = QHBoxLayout()
        top_row.setSpacing(12)
        
        icon_box = QFrame(self)
        icon_box.setFixedSize(40, 40)
        icon_box.setStyleSheet(f"""
            background-color: {COLOR_PRIMARY_BG};
            border-radius: 10px;
        """)
        ib_layout = QHBoxLayout(icon_box)
        ib_layout.setContentsMargins(0, 0, 0, 0)
        lbl_icon = QLabel(icon_str, icon_box)
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icon.setStyleSheet(f"font-size: 16px; color: {COLOR_PRIMARY}; background: transparent;")
        ib_layout.addWidget(lbl_icon)
        top_row.addWidget(icon_box)
        
        self.lbl_label = QLabel(label, self)
        self.lbl_label.setStyleSheet(f"font-size: 13px; font-weight: 500; color: {COLOR_TEXT_SECONDARY}; background: transparent;")
        top_row.addWidget(self.lbl_label)
        top_row.addStretch(1)
        layout.addLayout(top_row)
        
        self.lbl_value = QLabel(value, self)
        self.lbl_value.setStyleSheet(f"font-size: 26px; font-weight: 700; color: {value_color}; background: transparent;")
        layout.addWidget(self.lbl_value)

    def set_value(self, val: str):
        self.lbl_value.setText(val)


# ==============================================================================
# MAIN WINDOW IMPLEMENTATION
# ==============================================================================
class AITAMainWindow(QMainWindow):
    """
    Main Application Window for AITA Desktop Client - Practical Exam Grading Subsystem.
    Layout: 240px Fixed Sidebar + Top Header 64px + Main Content (1440px+ optimized).
    """

    def __init__(self, session_info: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.session_info = session_info or {
            "mode": "ONLINE",
            "username": "instructor",
            "display_name": "GV: Nguyễn Văn Hùng",
        }
        self.setWindowTitle("AITA Grader - Chấm Thi Thực Hành (Console)")
        
        # Responsive sizing according to available screen geometry (prevents Windows Taskbar clipping)
        screen = QGuiApplication.primaryScreen()
        if screen:
            avail = screen.availableGeometry()
            target_w = min(1380, avail.width() - 40)
            target_h = min(820, avail.height() - 40)
            self.setMinimumSize(min(1060, target_w), min(640, target_h))
            self.resize(target_w, target_h)
            self.move(avail.x() + (avail.width() - target_w) // 2,
                      avail.y() + (avail.height() - target_h) // 2)
        else:
            self.setMinimumSize(1060, 640)
            self.resize(1280, 750)
            
        self.setStyleSheet(LIGHT_THEME_QSS)
        
        # Kết nối CSDL SQLite cục bộ thật & Dịch vụ Chấm Điểm
        self.db = DatabaseManager()
        self.grading_service = GradingService(self.db)
        self.current_class_id: Optional[int] = None
        
        self._setup_desktop_layout()
        self._load_classes_selector()

    def _setup_desktop_layout(self):
        """Builds standard layout: 240px Fixed Sidebar + Main Content (Header + Stacked Canvas)."""
        root_widget = QWidget(self)
        self.setCentralWidget(root_widget)
        
        master_layout = QHBoxLayout(root_widget)
        master_layout.setContentsMargins(0, 0, 0, 0)
        master_layout.setSpacing(0)
        
        # 1. Standard Sidebar (240px)
        sidebar = self._build_sidebar()
        master_layout.addWidget(sidebar)
        
        # 2. Right Container (Top Header + Stacked Canvas)
        right_container = QWidget(self)
        rc_layout = QVBoxLayout(right_container)
        rc_layout.setContentsMargins(0, 0, 0, 0)
        rc_layout.setSpacing(0)
        
        # Top Header (64px)
        top_header = self._build_top_header()
        rc_layout.addWidget(top_header)
        
        # Stacked Central Content: Page 0 = Empty State, Page 1 = Active Workspace Canvas
        self.content_stack = QStackedWidget(self)
        self.page_empty = self._build_empty_state_view()
        self.page_active = self._build_active_workspace_view()
        
        self.content_stack.addWidget(self.page_empty)    # Index 0
        self.content_stack.addWidget(self.page_active)   # Index 1
        
        rc_layout.addWidget(self.content_stack, stretch=1)
        master_layout.addWidget(right_container, stretch=1)

    def _build_empty_state_view(self) -> QWidget:
        """Builds an elegant empty state view encouraging user to create or select a grading session."""
        container = QWidget(self)
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(32, 24, 32, 24)
        c_layout.addStretch(1)  # Căn giữa dọc: khoảng co giãn trên
        
        card = QFrame(container)
        card.setProperty("class", "Card")
        card.setMinimumWidth(680)
        card.setMaximumWidth(820)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 36, 40, 36)
        card_layout.setSpacing(20)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title & Subtitle
        lbl_title = QLabel("Chưa Có Đợt Chấm Nào Được Chọn", card)
        lbl_title.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {COLOR_TEXT_PRIMARY}; background: transparent;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(lbl_title)
        
        lbl_desc = QLabel(
            "Hệ thống vận hành theo từng phiên chấm bài độc lập. Để bắt đầu, vui lòng khởi tạo phiên chấm mới "
            "hoặc mở lại đợt chấm đã lưu trong lịch sử CSDL cục bộ.", card
        )
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet(f"font-size: 14px; color: {COLOR_TEXT_SECONDARY}; line-height: 140%; background: transparent;")
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(lbl_desc)
        
        # Flow steps info box (Một lớp nền duy nhất, không nét đứt, không lồng nền con)
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
        fb_layout.setSpacing(10)
        
        lbl_flow_title = QLabel("Quy Trình Chấm Thi Chuẩn:", flow_box)
        lbl_flow_title.setStyleSheet(f"font-weight: 700; font-size: 14px; color: {COLOR_PRIMARY};")
        fb_layout.addWidget(lbl_flow_title)
        
        steps = [
            "Bước 1: Khởi tạo đợt chấm bài (chọn môn thi, ngôn ngữ lập trình, thư mục bài nộp hoặc nạp file students.csv)",
            "Bước 2: Cấu hình Testcase (thiết lập bộ dữ liệu kiểm thử và lựa chọn thuật toán so khớp kết quả phù hợp)",
            "Bước 3: Chấm bài tự động (hệ thống biên dịch và chạy sandbox giám sát RAM / CPU thời gian thực)",
            "Bước 4: Quét đạo văn 2 vòng (đối soát chéo cấu trúc mã nguồn AST và token để phát hiện gian lận)",
            "Bước 5: Xuất bảng điểm (kết xuất file kết quả chi tiết ra định dạng chuẩn results.csv)"
        ]
        for s in steps:
            l = QLabel(s, flow_box)
            l.setStyleSheet("font-size: 13px; color: #334155; line-height: 1.4;")
            l.setWordWrap(True)
            fb_layout.addWidget(l)
        card_layout.addWidget(flow_box)
        
        # Action Buttons Row
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(14)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn_create = QPushButton("Tạo Đợt Chấm Mới", card)
        btn_create.setProperty("class", "PrimaryBtn")
        btn_create.setFixedHeight(44)
        btn_create.setMinimumWidth(180)
        btn_create.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_create.clicked.connect(self._open_session_dialog)
        btn_layout.addWidget(btn_create)
        
        btn_history = QPushButton("Mở Đợt Chấm Từ Lịch Sử", card)
        btn_history.setProperty("class", "SecondaryBtn")
        btn_history.setFixedHeight(44)
        btn_history.setMinimumWidth(180)
        btn_history.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_history.clicked.connect(self._open_history_dialog)
        btn_layout.addWidget(btn_history)
        
        card_layout.addLayout(btn_layout)
        c_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
        c_layout.addStretch(1)  # Căn giữa dọc: khoảng co giãn dưới
        return container

    def _build_active_workspace_view(self) -> QWidget:
        """Builds active grading workspace with Toolbar, Stats Panel, and Submissions Table."""
        content_canvas = QWidget(self)
        content_canvas.setObjectName("CentralCanvas")
        content_layout = QVBoxLayout(content_canvas)
        content_layout.setContentsMargins(28, 24, 28, 24)
        content_layout.setSpacing(20)
        
        # Action Toolbar (Primary + Secondary Actions)
        content_layout.addWidget(self._build_action_toolbar())
        
        # Stat Cards (4 columns per row) + Clean Progress Bar
        content_layout.addWidget(self._build_stats_panel())
        
        # Submissions Table Card
        content_layout.addWidget(self._build_table_card(), stretch=1)
        return content_canvas

    # --------------------------------------------------------------------------
    # 1. Standard Sidebar (240px)
    # --------------------------------------------------------------------------
    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame(self)
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(240)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 16, 12, 20)
        layout.setSpacing(6)
        
        # Logo Area (Height 72px)
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
        lbl_app_name = QLabel("AITA Grader", logo_area)
        lbl_app_name.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {COLOR_TEXT_PRIMARY};")
        lbl_sub_name = QLabel("Hệ Thống Chấm Thi", logo_area)
        lbl_sub_name.setStyleSheet(f"font-size: 11px; color: {COLOR_TEXT_SECONDARY};")
        title_box.addWidget(lbl_app_name)
        title_box.addWidget(lbl_sub_name)
        la_layout.addLayout(title_box)
        la_layout.addStretch(1)
        layout.addWidget(logo_area)
        
        layout.addSpacing(12)
        
        # Section Label
        lbl_sec = QLabel("ĐIỀU HƯỚNG", sidebar)
        lbl_sec.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {COLOR_TEXT_MUTED}; padding-left: 12px; margin-bottom: 4px;")
        layout.addWidget(lbl_sec)
        
        # Nav Item Helper
        def create_nav_item(text: str, is_active: bool = False, on_click=None) -> QPushButton:
            btn = QPushButton(text, sidebar)
            btn.setFixedHeight(44)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            if is_active:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLOR_PRIMARY_BG};
                        color: {COLOR_PRIMARY};
                        font-weight: 600;
                        font-size: 14px;
                        text-align: left;
                        padding-left: 14px;
                        border: none;
                        border-radius: 10px;
                        border-left: 3px solid {COLOR_PRIMARY};
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {COLOR_TEXT_PRIMARY};
                        font-weight: 500;
                        font-size: 14px;
                        text-align: left;
                        padding-left: 16px;
                        border: none;
                        border-radius: 10px;
                    }}
                    QPushButton:hover {{
                        background-color: {COLOR_SURFACE_SECONDARY};
                        color: {COLOR_PRIMARY};
                    }}
                """)
            if on_click:
                btn.clicked.connect(on_click)
            return btn
        
        # Navigation Items (Practical Exam dedicated)
        btn_console = create_nav_item("Bảng Điểm & Bài Nộp", is_active=True)
        layout.addWidget(btn_console)

        btn_new_session = create_nav_item("Tạo Đợt Chấm Mới", is_active=False, on_click=self._open_session_dialog)
        layout.addWidget(btn_new_session)

        btn_history = create_nav_item("Lịch Sử Đợt Chấm", is_active=False, on_click=self._open_history_dialog)
        layout.addWidget(btn_history)

        btn_guide = create_nav_item("Hướng Dẫn Chấm", is_active=False, on_click=self._open_guide_dialog)
        layout.addWidget(btn_guide)
        
        btn_tc = create_nav_item("Quản Lý Testcase", is_active=False, on_click=self._open_testcase_dialog)
        layout.addWidget(btn_tc)
        
        btn_plag = create_nav_item("Quét Đạo Văn AST", is_active=False, on_click=self._open_plagiarism_dialog)
        layout.addWidget(btn_plag)
        
        btn_settings = create_nav_item("Cấu Hình Môi Trường", is_active=False, on_click=self._open_settings_dialog)
        layout.addWidget(btn_settings)
        
        layout.addStretch(1)

        # Logo FPT University (Chiều cao 30px, giữ đúng tỉ lệ, căn giữa sidebar, cách nút 16px)
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
                lbl_fptu.setPixmap(pix.scaledToHeight(30, Qt.TransformationMode.SmoothTransformation))
            layout.addWidget(lbl_fptu)
            layout.addSpacing(16)
        
        # Bottom Navigation Action: Switch Mode
        btn_back_mode = create_nav_item("Đổi Chế Độ Làm Việc", is_active=False, on_click=self._back_to_mode_selection)
        btn_back_mode.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFFFFF;
                color: #1E293B;
                font-weight: 600;
                font-size: 13px;
                text-align: left;
                padding-left: 16px;
                border: 1.5px solid #CBD5E1;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_BG};
                color: {COLOR_PRIMARY};
                border-color: {COLOR_PRIMARY};
            }}
        """)
        layout.addWidget(btn_back_mode)
        
        return sidebar

    # --------------------------------------------------------------------------
    # 2. Top Header Bar (64px)
    # --------------------------------------------------------------------------
    def _build_top_header(self) -> QFrame:
        header = QFrame(self)
        header.setObjectName("HeaderBar")
        header.setFixedHeight(64)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(16)
        
        # Page Title / Breadcrumb
        lbl_page_title = QLabel("Chấm Thi Thực Hành", header)
        lbl_page_title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {COLOR_TEXT_PRIMARY};")
        layout.addWidget(lbl_page_title)
        
        layout.addSpacing(12)
        
        # Course / Class Dropdown Selector (flexible min-width, ellipsis with tooltip)
        self.class_selector = QComboBox(header)
        self.class_selector.setFixedHeight(36)
        self.class_selector.setMinimumWidth(220)
        self.class_selector.setMaximumWidth(360)
        self.class_selector.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.class_selector.currentIndexChanged.connect(self._on_class_selected)
        layout.addWidget(self.class_selector)

        # Nút Tạo Đợt Chấm Mới ngay cạnh Selector
        self.btn_header_new = QPushButton("Tạo Đợt Chấm Mới", header)
        self.btn_header_new.setProperty("class", "PrimaryBtn")
        self.btn_header_new.setFixedHeight(36)
        self.btn_header_new.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_header_new.clicked.connect(self._open_session_dialog)
        layout.addWidget(self.btn_header_new)
        
        layout.addStretch(1)
        
        # AI Mode Badge (Clean pill, fixed 32px height, vertically centered, rounded 16px)
        is_offline = (self.session_info.get("mode") == "OFFLINE")
        badge_bg = "#F1F5F9" if is_offline else "#EFF6FF"
        badge_color = COLOR_TEXT_SECONDARY if is_offline else COLOR_PRIMARY
        badge_border = "#E2E8F0" if is_offline else "#BFDBFE"
        badge_text = "Ngoại Tuyến (Offline)" if is_offline else "Gemini AI: Sẵn Sàng"
        
        status_pill = QFrame(header)
        status_pill.setFixedHeight(32)
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
        sp_layout.addWidget(lbl_sp)
        layout.addWidget(status_pill, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        # User Avatar & Name (Single clean circle border, no nested rectangle)
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
    # 3. Action Toolbar (Clean Desktop SaaS - Step-by-step Flow)
    # --------------------------------------------------------------------------
    def _build_action_toolbar(self) -> QFrame:
        card = QFrame(self)
        card.setProperty("class", "Card")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Bước 1: Cấu hình Testcase & Thuật toán So Khớp (Cần làm trước khi chấm)
        self.btn_manage_testcases = QPushButton("1. Cấu Hình Testcase & So Khớp", card)
        self.btn_manage_testcases.setProperty("class", "ToolbarActionBtn")
        self.btn_manage_testcases.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_manage_testcases.clicked.connect(self._open_testcase_dialog)
        layout.addWidget(self.btn_manage_testcases)
        
        # Bước 2: Bắt Đầu Chấm Hàng Loạt (Primary Action Button - Blue #2F80ED, 40px)
        self.btn_batch_grade = QPushButton("2. Bắt Đầu Chấm Hàng Loạt", card)
        self.btn_batch_grade.setObjectName("BatchGradeBtn")
        self.btn_batch_grade.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_batch_grade.clicked.connect(self._start_batch_grade)
        layout.addWidget(self.btn_batch_grade)
        
        # Bước 3: Quét Đạo Văn (Thực hiện sau khi đã nạp bài hoặc đã chấm)
        self.btn_plagiarism = QPushButton("3. Quét Đạo Văn AST", card)
        self.btn_plagiarism.setProperty("class", "ToolbarActionBtn")
        self.btn_plagiarism.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_plagiarism.clicked.connect(self._open_plagiarism_dialog)
        layout.addWidget(self.btn_plagiarism)
        
        # Bước 4: Xuất Bảng Điểm (Kết xuất kết quả cuối cùng)
        self.btn_export = QPushButton("4. Xuất Bảng Điểm (results.csv)", card)
        self.btn_export.setProperty("class", "ToolbarActionBtn")
        self.btn_export.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_export.clicked.connect(self._export_gradebook)
        layout.addWidget(self.btn_export)
        
        layout.addStretch(1)
        return card

    # --------------------------------------------------------------------------
    # 4. Stat Cards (4 Columns) + Clean 8px Progress Bar
    # --------------------------------------------------------------------------
    def _build_stats_panel(self) -> QWidget:
        container = QWidget(self)
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(16)
        
        # 4 Cards Row (Mục 14: 3-4 cards/row, min-height 115px)
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)
        
        self.mc_total = MetricCardWidget("0", "Tổng Bài Nộp", "ALL", COLOR_TEXT_PRIMARY)
        self.mc_ac = MetricCardWidget("0", "AC (Đạt Chuẩn)", "AC", COLOR_SUCCESS)
        self.mc_err = MetricCardWidget("0", "Lỗi (WA / TLE / CE)", "ERR", COLOR_ERROR)
        self.mc_avg = MetricCardWidget("- / 10", "Điểm Trung Bình", "AVG", COLOR_PRIMARY)
        
        cards_layout.addWidget(self.mc_total)
        cards_layout.addWidget(self.mc_ac)
        cards_layout.addWidget(self.mc_err)
        cards_layout.addWidget(self.mc_avg)
        c_layout.addLayout(cards_layout)
        
        # Progress Card (Clean 8px Progress Bar, textVisible False)
        prog_card = QFrame(container)
        prog_card.setProperty("class", "Card")
        p_layout = QVBoxLayout(prog_card)
        p_layout.setContentsMargins(20, 14, 20, 14)
        p_layout.setSpacing(10)
        
        top_p = QHBoxLayout()
        lbl_pt = QLabel("TIẾN ĐỘ THỰC THI CHẤM TỰ ĐỘNG", prog_card)
        lbl_pt.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {COLOR_TEXT_PRIMARY};")
        top_p.addWidget(lbl_pt)
        top_p.addStretch(1)
        
        self.lbl_progress_detail = QLabel("Sẵn sàng chấm bài. Vui lòng chọn đợt chấm hoặc nạp file sinh viên.", prog_card)
        self.lbl_progress_detail.setStyleSheet(f"font-size: 13px; font-weight: 500; color: {COLOR_PRIMARY};")
        top_p.addWidget(self.lbl_progress_detail)
        p_layout.addLayout(top_p)
        
        self.progress_bar = QProgressBar(prog_card)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        p_layout.addWidget(self.progress_bar)
        
        c_layout.addWidget(prog_card)
        return container

    # --------------------------------------------------------------------------
    # 5. Submissions DataTable (Row height 52px, Clean Light Theme)
    # --------------------------------------------------------------------------
    def _build_table_card(self) -> QFrame:
        card = QFrame(self)
        card.setProperty("class", "Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)
        
        # Table Header Row
        header_row = QHBoxLayout()
        lbl_title = QLabel("Danh Sách Bài Nộp & Bảng Điểm Thời Gian Thực", card)
        lbl_title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {COLOR_TEXT_PRIMARY};")
        header_row.addWidget(lbl_title)
        
        header_row.addStretch(1)
        
        lbl_hint = QLabel("Bấm 'Chi Tiết' để xem mã nguồn, log thực thi hoặc kích hoạt AI Code Review", card)
        lbl_hint.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_SECONDARY};")
        header_row.addWidget(lbl_hint)
        layout.addLayout(header_row)
        
        # Table Widget
        self.table = QTableWidget(card)
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "#", "Sinh Viên (MSSV & Tên)", "Tệp Nộp", "Ngôn Ngữ",
            "Thời Gian", "Bộ Nhớ", "Trạng Thái", "Điểm Số", "Can Thiệp", "Thao Tác"
        ])
        
        # Center align headers for numerical and action columns
        for col_idx in [0, 2, 3, 4, 5, 6, 7, 8, 9]:
            h_it = self.table.horizontalHeaderItem(col_idx)
            if h_it:
                h_it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.table.setWordWrap(False)
        self.table.setTextElideMode(Qt.TextElideMode.ElideRight)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 48)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 90)
        self.table.setColumnWidth(4, 110)
        self.table.setColumnWidth(5, 110)
        self.table.setColumnWidth(6, 140)
        self.table.setColumnWidth(7, 110)
        self.table.setColumnWidth(8, 110)
        self.table.setColumnWidth(9, 110)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)
        
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
            self.current_class_id = None
            self.content_stack.setCurrentIndex(0)
            self.class_selector.blockSignals(False)
            return

        self.class_selector.addItem("-- Chọn đợt chấm bài --", None)
        target_index = 0
        for idx, c in enumerate(classes, start=1):
            label = f"[{c['course_code']}] {c['class_name']} — Ngôn ngữ: {c['programming_language']}"
            self.class_selector.addItem(label, c["id"])
            if target_class_id is not None and c["id"] == target_class_id:
                target_index = idx

        # Tùy chọn tạo phiên chấm mới trực tiếp từ combobox
        self.class_selector.addItem("+ Tạo Đợt Chấm Mới...", "__NEW__")

        self.class_selector.setCurrentIndex(target_index)
        self.class_selector.blockSignals(False)
        
        if target_index > 0:
            self._on_class_selected()
        else:
            self.current_class_id = None
            self.content_stack.setCurrentIndex(0)

    def _on_class_selected(self):
        """Triggered when user selects a different class session from dropdown."""
        class_id = self.class_selector.currentData()
        if class_id == "__NEW__":
            # Khôi phục index về phiên hiện tại trước khi mở dialog
            if self.current_class_id:
                idx = self.class_selector.findData(self.current_class_id)
                if idx >= 0:
                    self.class_selector.blockSignals(True)
                    self.class_selector.setCurrentIndex(idx)
                    self.class_selector.blockSignals(False)
            self._open_session_dialog()
            return
            
        if class_id is None:
            self.current_class_id = None
            self.content_stack.setCurrentIndex(0)
        else:
            self.current_class_id = class_id
            self.content_stack.setCurrentIndex(1)
            self._load_submissions_table(class_id)

    def _load_submissions_table(self, class_id: int):
        """Loads and renders student submissions for the specified class from SQLite."""
        submissions = self.db.get_submissions_by_class(class_id)
        self.table.setRowCount(len(submissions))
        
        classes = self.db.get_all_classes()
        class_info = next((c for c in classes if c["id"] == class_id), None)
        lang = class_info.get("programming_language", "C") if class_info else "C"
        
        total_ac = 0
        total_errors = 0
        total_score_sum = 0.0
        graded_count = 0

        for row_idx, sub in enumerate(submissions):
            mssv = sub["student_mssv"]
            s_name = sub.get("student_name") or "Sinh viên"
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

            # Row height 52px (Design System section 16)
            self.table.setRowHeight(row_idx, 52)

            # 0: STT
            item_stt = QTableWidgetItem(str(row_idx + 1))
            item_stt.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 0, item_stt)

            # 1: MSSV & Name
            item_mssv = QTableWidgetItem(f"{mssv} — {s_name}")
            item_mssv.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            item_mssv.setFont(QFont("Inter", 10, QFont.Weight.Medium))
            self.table.setItem(row_idx, 1, item_mssv)

            # 2: File
            item_fname = QTableWidgetItem(fname)
            item_fname.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 2, item_fname)

            # 3: Lang
            item_lang = QTableWidgetItem(lang)
            item_lang.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 3, item_lang)

            # 4: Runtime
            item_runtime = QTableWidgetItem(runtime_str)
            item_runtime.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 4, item_runtime)

            # 5: RAM
            item_ram = QTableWidgetItem(ram_str)
            item_ram.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 5, item_ram)

            # 6: Verdict Pill (Badge)
            pill = VerdictPill(verdict)
            self.table.setCellWidget(row_idx, 6, pill)

            # 7: Score
            item_score = QTableWidgetItem(score_str)
            item_score.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_score.setFont(QFont("Inter", 10, QFont.Weight.Bold))
            if "10.0" in score_str:
                item_score.setForeground(QColor(COLOR_SUCCESS))
            elif score_str != "—":
                item_score.setForeground(QColor(COLOR_PRIMARY))
            self.table.setItem(row_idx, 7, item_score)

            # 8: Can Thiệp (Manual Override status)
            item_override = QTableWidgetItem(override_text)
            item_override.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if override_text != "Tự động":
                item_override.setForeground(QColor("#D97706"))
                item_override.setFont(QFont("Inter", 9, QFont.Weight.DemiBold))
            else:
                item_override.setForeground(QColor(COLOR_TEXT_MUTED))
            self.table.setItem(row_idx, 8, item_override)

            # 9: Action Button (Design System Secondary Button 32px)
            btn_view = QPushButton("Chi Tiết", self.table)
            btn_view.setFixedHeight(32)
            btn_view.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_view.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_SURFACE};
                    color: {COLOR_PRIMARY};
                    border: 1px solid {COLOR_PRIMARY};
                    border-radius: 8px;
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
        self.lbl_progress_detail.setText(f"Đã nạp {len(submissions)} bài nộp từ CSDL SQLite.")

    # --------------------------------------------------------------------------
    # 7. Action Handlers & Batch Grading Execution
    # --------------------------------------------------------------------------
    def _open_session_dialog(self):
        """
        Quy trình hướng dẫn liên hoàn 3 bước (Wizard):
        Bước 1: Tạo đợt chấm (SessionDialog)
        <-> Bước 2: Cấu hình môi trường (SettingsDialog)
        <-> Bước 3: Cấu hình Testcase (TestcaseDialog)
        Có đầy đủ nút 'Quay Lại' ở Bước 2 và Bước 3 để giảng viên chỉnh sửa lại thông tin!
        Chỉ khi hoàn tất xong cả 3 bước thì mới nạp và hiển thị màn hình chấm bài.
        """
        step = 1
        created_class_id = None

        while step in (1, 2, 3):
            if step == 1:
                dlg_session = SessionDialog(self, existing_class_id=created_class_id)
                dlg_session.setWindowTitle("Bước 1/3: Khởi Tạo Đợt Chấm Mới & Nạp Bài Nộp")
                if dlg_session.exec() != QDialog.DialogCode.Accepted:
                    return  # Giảng viên hủy bỏ -> Dừng wizard

                created_class_id = getattr(dlg_session, "created_class_id", None)
                if not created_class_id:
                    return
                step = 2

            elif step == 2:
                dlg_settings = SettingsDialog(self, is_wizard=True)
                dlg_settings.exec()
                if getattr(dlg_settings, "nav_back", False):
                    # Giảng viên bấm 'Quay Lại Bước 1'
                    step = 1
                elif getattr(dlg_settings, "is_saved", False):
                    # Giảng viên bấm 'Tiếp Tục: Cấu Hình Testcase (Bước 3/3)'
                    step = 3
                else:
                    return  # Giảng viên bấm 'Hủy Bỏ' -> Dừng wizard

            elif step == 3:
                dlg_testcase = TestcaseDialog(self, class_id=created_class_id, is_wizard=True)
                res = dlg_testcase.exec()
                if getattr(dlg_testcase, "nav_back", False):
                    # Giảng viên bấm 'Quay Lại Bước 2'
                    step = 2
                elif res == QDialog.DialogCode.Accepted:
                    # Giảng viên bấm 'Hoàn Tất Thiết Lập & Bắt Đầu Chấm Bài'
                    break
                else:
                    return  # Giảng viên bấm 'Hủy Bỏ' -> Dừng wizard

        # Bước 4: Sau khi hoàn tất cả 3 bước -> MỚI NẠP VÀ HIỂN THỊ MÀN HÌNH CHẤM BÀI!
        self._load_classes_selector(target_class_id=created_class_id)

        QMessageBox.information(
            self,
            "Hoàn Tất Thiết Lập",
            "Đã hoàn thành toàn bộ quy trình cấu hình đợt chấm bài!\n\n"
            "• Bước 1: Khởi tạo đợt chấm & nạp mã nguồn thành công\n"
            "• Bước 2: Cấu hình môi trường biên dịch & Sandbox sẵn sàng\n"
            "• Bước 3: Bộ Testcase & thuật toán so khớp đã được thiết lập\n\n"
            "Màn hình chấm bài đã sẵn sàng! Bạn có thể bấm '2. Bắt Đầu Chấm Hàng Loạt' để chấm bài."
        )

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

    def _open_history_dialog(self):
        """Opens the grading history dialog and switches to the chosen session."""
        dlg = HistoryDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.selected_class_id:
            self._load_classes_selector(target_class_id=dlg.selected_class_id)

    def _open_guide_dialog(self):
        """Opens the comprehensive grading guide dialog from main window."""
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
        dlg = PlagiarismDialog(self, class_id=class_id)
        dlg.exec()

    def _start_batch_grade(self):
        class_id = self.class_selector.currentData()
        if not class_id:
            QMessageBox.warning(self, "Chưa Chọn Đợt Chấm", "Vui lòng chọn đợt chấm bài từ danh sách!")
            return

        # Kiểm tra điều kiện tiên quyết: Phải có Testcase trước khi chấm
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
        
        def update_progress(curr, total, mssv):
            percent = int((curr / total) * 100)
            self.progress_bar.setValue(percent)
            self.lbl_progress_detail.setText(f"Đang chấm: {mssv} ({curr}/{total} bài — {percent}%)")
            QApplication.processEvents()

        try:
            results = self.grading_service.grade_class_batch(class_id, progress_callback=update_progress)
            self.progress_bar.setValue(100)
            self.lbl_progress_detail.setText(f"Hoàn tất: Đã chấm xong {len(results)} bài nộp!")
            self._load_submissions_table(class_id)
            
            QMessageBox.information(
                self,
                "Chấm Bài Thành Công",
                f"Đã hoàn thành chấm tự động toàn bộ {len(results)} bài thi!\n"
                f"• Thuật toán so khớp: 7 chế độ tự động\n"
                f"• Giám sát Sandbox: RAM & CPU đo thời gian thực\n"
                f"• CSDL: Toàn bộ điểm số đã được ghi an toàn vào SQLite cục bộ (local_grading.db)."
            )
        except Exception as ex:
            QMessageBox.critical(self, "Lỗi Quá Trình Chấm", f"Có lỗi xảy ra trong quá trình chấm:\n{str(ex)}")

    def _export_gradebook(self):
        class_id = self.class_selector.currentData()
        if not class_id:
            return
        submissions = self.db.get_submissions_by_class(class_id)
        
        export_path = Path(__file__).resolve().parent.parent.parent.parent / "results.csv"
        try:
            with open(export_path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["MSSV", "Họ và tên", "Tên File", "Thời gian (ms)", "Bộ nhớ (MB)", "Trạng thái", "Điểm số"])
                for s in submissions:
                    score = s.get("calculated_score") or 0.0
                    writer.writerow([
                        s['student_mssv'],
                        s.get('student_name', ''),
                        Path(s['source_file_path']).name,
                        f"{s.get('execution_time_ms', 0):.0f}",
                        f"{s.get('memory_used_mb', 0):.1f}",
                        s.get('final_verdict', 'PENDING'),
                        f"{score:.1f}"
                    ])

            QMessageBox.information(
                self,
                "Xuất Báo Cáo Thành Công",
                f"Đã xuất bảng điểm chuẩn thành công ra file:\n📁 {export_path}"
            )
        except Exception as ex:
            QMessageBox.critical(self, "Lỗi Xuất File", f"Không thể xuất file bảng điểm:\n{str(ex)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Inter", 9)
    app.setFont(font)
    
    window = AITAMainWindow()
    window.show()
    sys.exit(app.exec())
