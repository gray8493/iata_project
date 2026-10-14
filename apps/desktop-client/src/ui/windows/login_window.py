"""
AITA Desktop Client - Instructor Login Window (PyQt6)
Standard Implementation matching DESKTOP APP UI/UX DESIGN SYSTEM
Style: Modern Educational SaaS, 100% Light, Blue-focused (#2F80ED), Clean Modal Card.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor, QPixmap, QIcon
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QCheckBox, QMessageBox
)

SRC_DIR = Path(__file__).resolve().parent.parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ui.styles.theme import (
    LIGHT_THEME_QSS, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_PRIMARY_ACTIVE,
    COLOR_BG, COLOR_SURFACE, COLOR_TEXT_PRIMARY, COLOR_BORDER_DEFAULT,
    RADIUS_BUTTON
)


class LoginWindow(QMainWindow):
    """
    Instructor Authentication Window matching Design System:
    Light Canvas (#F5F8FC), White Card (#FFFFFF, 1px solid #E5EAF0, radius 16px).
    """
    login_successful = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AITA Grader - Đăng Nhập Giảng Viên")
        self.setFixedSize(460, 560)
        self.setStyleSheet(LIGHT_THEME_QSS)
        self._init_ui()

    def _init_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        central.setStyleSheet(f"background-color: {COLOR_BG};")
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Main Card (Radius 16px, border 1px solid #E5EAF0)
        card = QFrame(central)
        card.setObjectName("LoginCard")
        card.setStyleSheet(f"""
            QFrame#LoginCard {{
                background-color: {COLOR_SURFACE};
                border: 1px solid {COLOR_BORDER_DEFAULT};
                border-radius: 16px;
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 28, 32, 28)
        card_layout.setSpacing(0)
        
        # 1. Header & FPT University Logo (Transparent PNG, height 72px, centered)
        candidate_logo_paths = [
            Path(__file__).resolve().parent.parent.parent.parent / "assets" / "images" / "fptulogo_transparent.png",
            Path(__file__).resolve().parents[5] / "assets" / "images" / "fptulogo_transparent.png",
            Path(r"e:\AITA\assets\images\fptulogo_transparent.png"),
            Path(r"e:\AITA\apps\desktop-client\assets\images\fptulogo_transparent.png"),
            Path(r"e:\AITA\assets\images\fptulogo.jpg"),
            Path(r"C:\Users\admin\Downloads\fptulogo.jpg")
        ]
        logo_path = next((p for p in candidate_logo_paths if p.exists()), None)

        logo_layout = QHBoxLayout()
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_logo = QLabel(card)
        if logo_path and logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            if not pixmap.isNull():
                # Chiều cao 72px (trong khoảng 64-80px), scale mượt mà, giữ nguyên tỉ lệ gốc
                scaled_pixmap = pixmap.scaledToHeight(72, Qt.TransformationMode.SmoothTransformation)
                lbl_logo.setPixmap(scaled_pixmap)
                lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl_logo.setStyleSheet("background: transparent;")
        else:
            lbl_logo.setText("FPT UNIVERSITY")
            lbl_logo.setStyleSheet(f"font-size: 18px; font-weight: 800; color: {COLOR_PRIMARY}; background: transparent;")

        logo_layout.addWidget(lbl_logo)
        card_layout.addLayout(logo_layout)
        
        # Khoảng cách 18px giữa Logo và tiêu đề (chuẩn 16-20px)
        card_layout.addSpacing(18)
        
        # Tiêu đề "AITA Grader"
        lbl_title = QLabel("AITA Grader", card)
        lbl_title.setStyleSheet(f"""
            QLabel {{
                font-size: 22px;
                font-weight: 700;
                color: {COLOR_TEXT_PRIMARY};
                background: transparent;
                line-height: 1.4;
            }}
        """)
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(lbl_title)
        
        # Khoảng cách giữa tiêu đề và dòng mô tả: 6-8px
        card_layout.addSpacing(6)
        
        # Dòng mô tả (Màu xám đậm #475569 tăng tương phản rõ rệt)
        lbl_sub = QLabel("Hệ thống chấm thi & đánh giá lập trình cục bộ", card)
        lbl_sub.setStyleSheet("""
            QLabel {{
                font-size: 13px;
                color: #475569;
                background: transparent;
                line-height: 1.4;
            }}
        """)
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(lbl_sub)
        
        # Khoảng cách giữa các nhóm: 20px
        card_layout.addSpacing(20)
        
        # 2. Form Input - Username
        lbl_user = QLabel("Tên Đăng Nhập / Email Giảng Viên:", card)
        lbl_user.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                font-weight: 600;
                color: {COLOR_TEXT_PRIMARY};
                background: transparent;
                line-height: 1.4;
            }}
        """)
        card_layout.addWidget(lbl_user)
        
        # Nhãn cách ô nhập: 8px
        card_layout.addSpacing(8)
        
        self.txt_username = QLineEdit(card)
        self.txt_username.setFixedHeight(40)
        self.txt_username.setPlaceholderText("hungnv@fe.edu.vn")
        self.txt_username.setText("teacher_hung@fe.edu.vn")
        card_layout.addWidget(self.txt_username)
        
        # Khoảng cách giữa các nhóm: 16px
        card_layout.addSpacing(16)
        
        # Form Input - Password
        lbl_pwd = QLabel("Mật Khẩu:", card)
        lbl_pwd.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                font-weight: 600;
                color: {COLOR_TEXT_PRIMARY};
                background: transparent;
                line-height: 1.4;
            }}
        """)
        card_layout.addWidget(lbl_pwd)
        
        # Nhãn cách ô nhập: 8px
        card_layout.addSpacing(8)
        
        self.txt_password = QLineEdit(card)
        self.txt_password.setFixedHeight(40)
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setPlaceholderText("Nhập mật khẩu...")
        self.txt_password.setText("Secret@123")
        
        # Icon mắt hiện/ẩn mật khẩu ở cuối ô nhập
        eye_candidates = [
            Path(__file__).resolve().parent.parent.parent.parent / "assets" / "icons" / "eye.svg",
            Path(r"e:\AITA\assets\icons\eye.svg"),
            Path(r"e:\AITA\apps\desktop-client\assets\icons\eye.svg")
        ]
        eye_path = next((p for p in eye_candidates if p.exists()), Path("eye.svg"))

        eye_off_candidates = [
            Path(__file__).resolve().parent.parent.parent.parent / "assets" / "icons" / "eye_off.svg",
            Path(r"e:\AITA\assets\icons\eye_off.svg"),
            Path(r"e:\AITA\apps\desktop-client\assets\icons\eye_off.svg")
        ]
        eye_off_path = next((p for p in eye_off_candidates if p.exists()), Path("eye_off.svg"))

        self.icon_eye = QIcon(str(eye_path))
        self.icon_eye_off = QIcon(str(eye_off_path))
        
        self.action_toggle_pwd = self.txt_password.addAction(
            self.icon_eye_off,
            QLineEdit.ActionPosition.TrailingPosition
        )
        self.action_toggle_pwd.setToolTip("Hiện mật khẩu")
        self.action_toggle_pwd.triggered.connect(self._toggle_password_visibility)
        card_layout.addWidget(self.txt_password)
        
        # Khoảng cách đến checkbox: 14px
        card_layout.addSpacing(14)
        
        # 3. Checkbox Ghi nhớ phiên làm việc (Khung viền rõ nét, bo góc nhẹ, tick xanh)
        check_candidates = [
            Path(__file__).resolve().parent.parent.parent.parent / "assets" / "icons" / "check_white.svg",
            Path(__file__).resolve().parents[5] / "assets" / "icons" / "check_white.svg",
            Path(r"e:\AITA\assets\icons\check_white.svg"),
            Path(r"e:\AITA\apps\desktop-client\assets\icons\check_white.svg")
        ]
        check_icon_file = next((p for p in check_candidates if p.exists()), None)
        check_icon_path = str(check_icon_file).replace("\\", "/") if check_icon_file else ""
        self.chk_remember = QCheckBox("Ghi nhớ phiên làm việc trên máy trạm này", card)
        self.chk_remember.setChecked(True)
        self.chk_remember.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.chk_remember.setStyleSheet(f"""
            QCheckBox {{
                font-size: 13px;
                color: #334155;
                background: transparent;
                spacing: 8px;
                line-height: 1.4;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 1.5px solid #94A3B8;
                border-radius: 4px;
                background-color: #FFFFFF;
            }}
            QCheckBox::indicator:hover {{
                border-color: {COLOR_PRIMARY};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLOR_PRIMARY};
                border-color: {COLOR_PRIMARY};
                image: url("{check_icon_path}");
            }}
        """)
        card_layout.addWidget(self.chk_remember)
        
        # Khoảng cách đến nút Đăng Nhập: 20px
        card_layout.addSpacing(20)
        
        # 4. Nút Đăng Nhập Duy Nhất (Online, Chiều cao 42px, Rộng đủ chiều ngang card)
        self.btn_login = QPushButton("Đăng Nhập", card)
        self.btn_login.setFixedHeight(42)
        self.btn_login.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_login.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: #FFFFFF;
                border: none;
                border-radius: {RADIUS_BUTTON};
                font-size: 14px;
                font-weight: 600;
                line-height: 1.4;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_PRIMARY_ACTIVE};
            }}
        """)
        self.btn_login.clicked.connect(self._handle_login)
        card_layout.addWidget(self.btn_login)
        
        # Khoảng cách đến footer: 16px
        card_layout.addSpacing(16)
        
        # 5. Dòng phiên bản nhỏ tinh tế ở chân card
        lbl_version = QLabel("Phiên bản 2.4.0 (Build 2026)", card)
        lbl_version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_version.setStyleSheet("""
            QLabel {{
                font-size: 11px;
                color: #94A3B8;
                background: transparent;
                line-height: 1.4;
            }}
        """)
        card_layout.addWidget(lbl_version)
        
        main_layout.addWidget(card)

    def _toggle_password_visibility(self):
        """Toggles password visibility between masked and plain text."""
        if self.txt_password.echoMode() == QLineEdit.EchoMode.Password:
            self.txt_password.setEchoMode(QLineEdit.EchoMode.Normal)
            self.action_toggle_pwd.setIcon(self.icon_eye)
            self.action_toggle_pwd.setToolTip("Ẩn mật khẩu")
        else:
            self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
            self.action_toggle_pwd.setIcon(self.icon_eye_off)
            self.action_toggle_pwd.setToolTip("Hiện mật khẩu")

    def _handle_login(self):
        user = self.txt_username.text().strip()
        pwd = self.txt_password.text().strip()
        if not user or not pwd:
            QMessageBox.warning(self, "Lỗi Nhập Liệu", "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!")
            return
            
        user_base = user.split("@")[0].strip().lower()
        if user_base in ("teacher_hung", "hungnv"):
            disp_name = "GV: Nguyễn Văn Hùng"
        elif user_base in ("admin", "quantri"):
            disp_name = "GV: Quản Trị Hệ Thống"
        else:
            disp_name = f"GV: {user.split('@')[0].strip()}" if user else "GV: Giảng viên"
            
        session_info = {
            "mode": "ONLINE",
            "username": user,
            "display_name": disp_name,
        }
        self.login_successful.emit(session_info)
        self._launch_main_window(session_info)

    def _handle_offline(self):
        """Kept intact for backward compatibility or internal programmatic transitions."""
        session_info = {
            "mode": "OFFLINE",
            "username": "offline_instructor",
            "display_name": "GV: Chế Độ Ngoại Tuyến (Offline)",
        }
        self.login_successful.emit(session_info)
        self._launch_main_window(session_info)

    def _launch_main_window(self, session_info):
        try:
            from .mode_selection_window import ModeSelectionWindow
        except ImportError:
            from ui.windows.mode_selection_window import ModeSelectionWindow
        self.mode_win = ModeSelectionWindow(session_info=session_info)
        self.mode_win.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Inter", 9)
    app.setFont(font)
    
    win = LoginWindow()
    win.show()
    sys.exit(app.exec())
