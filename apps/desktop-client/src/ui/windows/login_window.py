"""
AITA Desktop Client - Instructor Login Window (PyQt6)
Standard Implementation matching DESKTOP APP UI/UX DESIGN SYSTEM
Style: Modern Educational SaaS, 100% Light, Blue-focused (#2F80ED), Clean Modal Card.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any

from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtBoundSignal
from PyQt6.QtGui import QFont, QCursor, QPixmap, QIcon, QAction
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QCheckBox, QMessageBox
)

SRC_DIR = Path(__file__).resolve().parent.parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.auth_service import AuthService
from ui.styles.theme import (
    LIGHT_THEME_QSS, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_PRIMARY_ACTIVE,
    COLOR_BG, COLOR_SURFACE, COLOR_TEXT_PRIMARY, COLOR_BORDER_DEFAULT,
    RADIUS_BUTTON
)


class LoginWorker(QThread):
    """Worker thread performing asynchronous login call to Central Backend."""
    login_finished: pyqtBoundSignal = pyqtSignal(dict)  # type: ignore[assignment]

    def __init__(self, username: str, password: str):
        super().__init__()
        self.username = username
        self.password = password

    def run(self):
        auth_service = AuthService()
        result = auth_service.login(self.username, self.password)
        self.login_finished.emit(result)


class LoginWindow(QMainWindow):
    """
    Instructor Authentication Window matching Design System:
    Light Canvas (#F5F8FC), White Card (#FFFFFF, 1px solid #E5EAF0, radius 16px).
    """
    login_successful: pyqtBoundSignal = pyqtSignal(dict)  # type: ignore[assignment]

    def __init__(self):
        super().__init__()
        self.action_toggle_pwd: Optional[QAction] = None
        self.setWindowTitle("AITA - Đăng Nhập Giảng Viên")
        self.setFixedSize(460, 500)
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
                dpr = self.devicePixelRatioF() if hasattr(self, "devicePixelRatioF") else 1.0
                target_height = 52
                scaled_pixmap = pixmap.scaledToHeight(
                    int(target_height * dpr),
                    Qt.TransformationMode.SmoothTransformation
                )
                scaled_pixmap.setDevicePixelRatio(dpr)
                lbl_logo.setPixmap(scaled_pixmap)
                display_w = int(scaled_pixmap.width() / dpr)
                display_h = int(scaled_pixmap.height() / dpr)
                lbl_logo.setFixedSize(display_w, display_h)
                lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl_logo.setStyleSheet("background: transparent; border: none;")
        else:
            lbl_logo.setText("FPT UNIVERSITY")
            lbl_logo.setStyleSheet(f"font-size: 18px; font-weight: 800; color: {COLOR_PRIMARY}; background: transparent; border: none;")

        logo_layout.addWidget(lbl_logo)
        card_layout.addLayout(logo_layout)
        
        # Khoảng cách 18px giữa Logo và tiêu đề (chuẩn 16-20px)
        card_layout.addSpacing(18)
        
        # Tiêu đề "AITA"
        lbl_title = QLabel("AITA", card)
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
        lbl_sub = QLabel("Hệ thống chấm thi & đánh giá lập trình", card)
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
        self.txt_username.setPlaceholderText("Nhập tên đăng nhập hoặc email...")
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
        if self.action_toggle_pwd is not None:
            self.action_toggle_pwd.setToolTip("Hiện mật khẩu")
            self.action_toggle_pwd.triggered.connect(self._toggle_password_visibility)
        card_layout.addWidget(self.txt_password)

        # Phím Enter: ô Tài khoản nhảy sang ô Mật khẩu, ô Mật khẩu đăng nhập luôn
        self.txt_username.returnPressed.connect(self.txt_password.setFocus)
        self.txt_password.returnPressed.connect(self._handle_login)
        
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
        lbl_version = QLabel("Phiên bản 1.0.0 (Build 2026)", card)
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
            if self.action_toggle_pwd is not None:
                self.action_toggle_pwd.setIcon(self.icon_eye)
                self.action_toggle_pwd.setToolTip("Ẩn mật khẩu")
        else:
            self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
            if self.action_toggle_pwd is not None:
                self.action_toggle_pwd.setIcon(self.icon_eye_off)
                self.action_toggle_pwd.setToolTip("Hiện mật khẩu")

    def _handle_login(self):
        user = self.txt_username.text().strip()
        pwd = self.txt_password.text().strip()
        if not user or not pwd:
            QMessageBox.warning(self, "Lỗi Nhập Liệu", "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!")
            return
            
        # Hiển thị trạng thái đang kết nối máy chủ
        self.btn_login.setEnabled(False)
        self.btn_login.setText("Đang kết nối máy chủ...")
        self.txt_username.setEnabled(False)
        self.txt_password.setEnabled(False)

        # Gọi đăng nhập bất đồng bộ qua QThread
        self.login_worker = LoginWorker(user, pwd)
        self.login_worker.login_finished.connect(self._on_login_finished)
        self.login_worker.start()

    def _on_login_finished(self, result: Dict[str, Any]):
        """Xử lý kết quả trả về từ Backend Render."""
        self.btn_login.setEnabled(True)
        self.btn_login.setText("Đăng Nhập")
        self.txt_username.setEnabled(True)
        self.txt_password.setEnabled(True)

        if result.get("success"):
            user_info = result.get("user", {})
            data = result.get("data", {})
            raw_username = self.txt_username.text().strip()
            username = user_info.get("username", raw_username)
            full_name = user_info.get("full_name") or username
            role = user_info.get("role", "INSTRUCTOR")
            
            session_info = {
                "mode": "ONLINE",
                "username": username,
                "display_name": f"GV: {full_name}",
                "full_name": full_name,
                "role": role,
                "email": user_info.get("email"),
                "user_id": user_info.get("id"),
                "token": data.get("access_token"),
                "refresh_token": data.get("refresh_token"),
            }
            self.login_successful.emit(session_info)
            self._launch_main_window(session_info)
        else:
            msg = result.get("message", "Đăng nhập không thành công.")
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("Lỗi Kết Nối Máy Chủ" if "Không kết nối" in msg else "Đăng Nhập Thất Bại")
            msg_box.setText(msg)
            btn_retry = msg_box.addButton("Thử Lại", QMessageBox.ButtonRole.AcceptRole)
            btn_close = msg_box.addButton("Đóng", QMessageBox.ButtonRole.RejectRole)
            msg_box.exec()
            if msg_box.clickedButton() == btn_retry:
                self._handle_login()

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
