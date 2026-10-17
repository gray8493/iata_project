"""
AITA Desktop Client - Mode Selection Window (PyQt6)
Standard Implementation matching DESKTOP APP UI/UX DESIGN SYSTEM
Style: Modern Educational SaaS, 100% Light, Blue-focused (#2F80ED), Clean Cards.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QCursor, QGuiApplication
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame
)

SRC_DIR = Path(__file__).resolve().parent.parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ui.styles.theme import (
    LIGHT_THEME_QSS, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_PRIMARY_ACTIVE,
    COLOR_PRIMARY_LIGHT, COLOR_PRIMARY_BG, COLOR_BG, COLOR_SURFACE, COLOR_SURFACE_SECONDARY,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_BORDER_DEFAULT, COLOR_BORDER_LIGHT, RADIUS_CARD, RADIUS_BUTTON, RADIUS_PILL
)
from services.ai_service import AiService



class ModeCard(QFrame):
    """
    Interactive card widget for selecting a grading mode matching Design System:
    Clean educational SaaS, 100% Light, uniform card height, no icons/emojis,
    subtle border on default with primary border on hover/focus.
    """
    clicked = pyqtSignal()

    def __init__(
        self,
        title: str,
        badge_text: str,
        description: str,
        features: List[str],
        btn_text: str,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.setObjectName("ModeCard")
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Mặc định viền xám nhạt (#E2E8F0); chỉ đổi viền xanh (#2F80ED) khi hover hoặc focus bàn phím
        self.setStyleSheet(f"""
            QFrame#ModeCard {{
                background-color: {COLOR_SURFACE};
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }}
            QFrame#ModeCard:hover, QFrame#ModeCard:focus {{
                border: 1.5px solid {COLOR_PRIMARY};
                background-color: #FFFFFF;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(28, 26, 28, 26)
        
        # 1. Badge phân hệ: bo góc 6px, padding đều 4px 10px, không chạm mép, lề trái bằng lề card
        badge_row = QHBoxLayout()
        badge_row.setContentsMargins(0, 0, 0, 0)
        lbl_badge = QLabel(badge_text, self)
        lbl_badge.setStyleSheet(f"""
            QLabel {{
                background-color: #EFF6FF;
                color: {COLOR_PRIMARY};
                font-weight: 700;
                font-size: 11px;
                letter-spacing: 0.5px;
                padding: 4px 10px;
                border: 1px solid #DBEAFE;
                border-radius: 6px;
                line-height: 1.4;
            }}
        """)
        badge_row.addWidget(lbl_badge)
        badge_row.addStretch(1)
        layout.addLayout(badge_row)
        
        layout.addSpacing(14)
        
        # 2. Tiêu đề card (Cố định min-height 32px để căn thẳng hàng ngang giữa 2 card)
        lbl_title = QLabel(title, self)
        lbl_title.setWordWrap(True)
        lbl_title.setMinimumHeight(32)
        lbl_title.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: 700;
                color: {COLOR_TEXT_PRIMARY};
                line-height: 1.4;
                background: transparent;
            }}
        """)
        layout.addWidget(lbl_title)
        
        layout.addSpacing(8)
        
        # 3. Mô tả ngắn (Cố định min-height 60px để danh sách tính năng bắt đầu tại CÙNG một mốc dọc)
        lbl_desc = QLabel(description, self)
        lbl_desc.setWordWrap(True)
        lbl_desc.setMinimumHeight(60)
        lbl_desc.setStyleSheet("""
            QLabel {
                color: #475569;
                font-size: 13px;
                line-height: 1.45;
                background: transparent;
            }
        """)
        layout.addWidget(lbl_desc)
        
        layout.addSpacing(18)
        
        # 4. Danh sách tính năng (Dùng chấm tròn nhỏ "•" thay cho dấu check, chữ 14px, line-height >= 1.4)
        features_frame = QFrame(self)
        features_frame.setStyleSheet("background: transparent; border: none;")
        feat_layout = QVBoxLayout(features_frame)
        feat_layout.setContentsMargins(0, 0, 0, 0)
        feat_layout.setSpacing(10)
        for feat in features:
            f_lbl = QLabel(f"•  {feat}", features_frame)
            f_lbl.setWordWrap(True)
            f_lbl.setStyleSheet("""
                QLabel {
                    color: #1E293B;
                    font-size: 14px;
                    line-height: 1.45;
                    background: transparent;
                }
            """)
            feat_layout.addWidget(f_lbl)
        layout.addWidget(features_frame)
        
        # Stretch đẩy nút xuống đáy
        layout.addStretch(1)
        
        # Khoảng cách cố định 24px giữa danh sách tính năng và nút đáy
        layout.addSpacing(24)
        
        # 5. Nút Chọn phân hệ (Chiều cao 42px, radius 8px, không dùng icon)
        self.btn_select = QPushButton(btn_text, self)
        self.btn_select.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_select.setFixedHeight(42)
        self.btn_select.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: #FFFFFF;
                font-size: 14px;
                font-weight: 600;
                border: none;
                border-radius: {RADIUS_BUTTON};
                line-height: 1.4;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_PRIMARY_ACTIVE};
            }}
        """)
        self.btn_select.clicked.connect(self.clicked.emit)
        layout.addWidget(self.btn_select)

    def mousePressEvent(self, a0):
        if a0 and a0.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(a0)


class ModeSelectionWindow(QMainWindow):
    """Window presented immediately after login for selecting the working subsystem."""

    def __init__(self, session_info: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.session_info = session_info or {
            "mode": "ONLINE",
            "username": "instructor",
            "display_name": "Giảng Viên",
        }
        
        self.setWindowTitle("AITA - Chọn Chế Độ Làm Việc")
        screen = QGuiApplication.primaryScreen()
        if screen:
            avail = screen.availableGeometry()
            target_w = min(1120, avail.width() - 40)
            target_h = min(720, avail.height() - 40)
            self.setMinimumSize(min(980, target_w), min(640, target_h))
            self.resize(target_w, target_h)
            self.move(avail.x() + (avail.width() - target_w) // 2,
                      avail.y() + (avail.height() - target_h) // 2)
        else:
            self.setMinimumSize(980, 640)
            self.resize(1120, 720)
        self.setStyleSheet(LIGHT_THEME_QSS)
        
        self._init_ui()
        self._refresh_ai_quota()

    def _init_ui(self):
        from PyQt6.QtGui import QPixmap

        central = QWidget(self)
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(36, 24, 36, 28)
        main_layout.setSpacing(20)
        
        # 1. Top Header Bar
        header = QFrame(central)
        header.setFixedHeight(48)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(14)
        
        # 1.1 Logo FPT University (Cao 32-34px, giữ đúng tỷ lệ)
        fptu_logo_paths = [
            SRC_DIR.parent / "assets" / "images" / "fptulogo_transparent.png",
            Path(r"e:\AITA\apps\desktop-client\assets\images\fptulogo_transparent.png"),
            Path(r"e:\AITA\assets\images\fptulogo_transparent.png"),
            Path(r"e:\AITA\assets\images\fptulogo.jpg")
        ]
        fptu_logo_file = next((p for p in fptu_logo_paths if p.exists()), None)
        if fptu_logo_file:
            lbl_fptu = QLabel(header)
            lbl_fptu.setStyleSheet("background: transparent; border: none;")
            pix = QPixmap(str(fptu_logo_file))
            if not pix.isNull():
                lbl_fptu.setPixmap(pix.scaledToHeight(32, Qt.TransformationMode.SmoothTransformation))
                header_layout.addWidget(lbl_fptu)
                
                # Vạch ngăn cách nhẹ giữa logo trường và logo app
                sep = QFrame(header)
                sep.setFixedSize(1, 24)
                sep.setStyleSheet("background-color: #CBD5E1; border: none;")
                header_layout.addWidget(sep)
        
        # 1.2 Ô vuông xanh chữ "A" thay cho biểu tượng
        logo_box = QLabel("A", header)
        logo_box.setFixedSize(28, 28)
        logo_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_box.setStyleSheet(f"""
            QLabel {{
                background-color: {COLOR_PRIMARY};
                color: #FFFFFF;
                font-weight: 700;
                font-size: 15px;
                border-radius: 6px;
            }}
        """)
        header_layout.addWidget(logo_box)
        
        # App Title (Không dùng emoji)
        app_title = QLabel("AITA", header)
        app_title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {COLOR_TEXT_PRIMARY}; line-height: 1.4;")
        header_layout.addWidget(app_title)
        
        header_layout.addStretch(1)
        
        # 1.3 Nút "Gemini AI: Sẵn Sàng": Đơn viền bo góc, cùng chiều cao 34px, bỏ icon
        ai_badge = QLabel("Gemini AI: Sẵn Sàng", header)
        ai_badge.setFixedHeight(34)
        ai_badge.setStyleSheet(f"""
            QLabel {{
                background-color: #EFF6FF;
                color: {COLOR_PRIMARY};
                font-size: 12px;
                font-weight: 600;
                border: 1px solid #BFDBFE;
                border-radius: 8px;
                padding: 0 14px;
                line-height: 1.4;
            }}
        """)
        header_layout.addWidget(ai_badge)
        self.lbl_ai_badge = ai_badge
        
        # 1.4 Nút "GV: Nguyễn Văn Hùng": Bỏ khung lồng và icon, đơn viền bo góc, cùng chiều cao 34px
        d_name = self.session_info.get("display_name", "Nguyễn Văn Hùng")
        if not d_name.startswith("GV:"):
            d_name = f"GV: {d_name}"
            
        user_badge = QLabel(d_name, header)
        user_badge.setFixedHeight(34)
        user_badge.setStyleSheet("""
            QLabel {
                background-color: #FFFFFF;
                color: #1E293B;
                font-size: 12px;
                font-weight: 600;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 0 14px;
                line-height: 1.4;
            }
        """)
        header_layout.addWidget(user_badge)
        
        # 1.5 Nút Đăng Xuất (Chiều cao 34px, bo góc 8px đồng bộ)
        btn_logout = QPushButton("Đăng Xuất", header)
        btn_logout.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_logout.setFixedHeight(34)
        btn_logout.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_SURFACE};
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 0 14px;
                color: #475569;
                font-weight: 600;
                font-size: 12px;
                line-height: 1.4;
            }}
            QPushButton:hover {{
                background-color: #FEF2F2;
                color: #EF4444;
                border-color: #FCA5A5;
            }}
        """)
        btn_logout.clicked.connect(self._handle_logout)
        header_layout.addWidget(btn_logout)
        
        main_layout.addWidget(header)
        
        # 2. Hero Headline
        hero_layout = QVBoxLayout()
        hero_layout.setSpacing(6)
        
        title_lbl = QLabel("Vui Lòng Chọn Phân Hệ Chấm Điểm", central)
        title_lbl.setStyleSheet(f"""
            QLabel {{
                font-size: 22px;
                font-weight: 700;
                color: {COLOR_TEXT_PRIMARY};
                line-height: 1.4;
            }}
        """)
        hero_layout.addWidget(title_lbl)
        
        # Dòng mô tả dưới tiêu đề: giới hạn chiều rộng 640-720px, màu đậm hơn (#475569)
        subtitle_lbl = QLabel(
            "Hệ thống cung cấp hai môi trường chấm điểm chuyên biệt và hoàn toàn tách rời nhau. "
            "Chọn chế độ phù hợp với đợt thi hoặc bài tập bạn muốn chấm:",
            central
        )
        subtitle_lbl.setWordWrap(True)
        subtitle_lbl.setMaximumWidth(700)
        subtitle_lbl.setStyleSheet("""
            QLabel {
                color: #475569;
                font-size: 13.5px;
                line-height: 1.45;
            }
        """)
        hero_layout.addWidget(subtitle_lbl)
        main_layout.addLayout(hero_layout)
        
        # 3. Hai Card Phân Hệ Chấm Điểm (Bằng nhau về chiều cao, không có icon/emoji)
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(24)
        
        # Card 1: Practical Exam
        self.card_practical = ModeCard(
            title="Chấm Thi Thực Hành (Practical Exam)",
            badge_text="CONSOLE / ALGORITHMS",
            description="Phân hệ chuyên trách bài thi lập trình Console. Biên dịch, thực thi qua hàm main() trong môi trường Sandbox cô lập và so khớp bộ testcase đa dạng.",
            features=[
                "4 Môn học cốt lõi: PRF (C), PRO (Java/Python), DSA (Java/Python), PHP (Python)",
                "Chấm tự động qua hàm main() với 7 chiến lược so khớp",
                "Sandbox Runner đo CPU, RAM, bắt lỗi TLE & MLE thời gian thực",
                "AI Gemini tự động sinh Testcase biên chuẩn xác",
                "Quét đạo văn 2 vòng: Cây cú pháp AST và Đối soát ngữ nghĩa"
            ],
            btn_text="Vào Chấm Thi Thực Hành",
            parent=central
        )
        self.card_practical.clicked.connect(self._open_practical_exam)
        cards_layout.addWidget(self.card_practical, stretch=1)
        
        # Card 2: Web Assignment
        self.card_web = ModeCard(
            title="Chấm Bài Tập & Đồ Án Web (Web Assignment)",
            badge_text="FRONTEND & BACKEND WEB",
            description="Phân hệ chuyên trách chấm bài tập giao diện và ứng dụng web từ thư mục bài nộp; mỗi bài gồm link Live URL và link GitHub Repo.",
            features=[
                "Nạp bài nộp từ thư mục: mỗi thư mục đặt tên là MSSV, chứa file .txt có Live URL và GitHub",
                "Chấm đồng thời cả Live Website và GitHub Repo cho mọi bài",
                "Playwright Headless Browser kiểm thử tương tác E2E và Responsive",
                "Thẩm định cây DOM ngữ nghĩa và quét W3C CSS/HTML Linting",
                "AI Gemini thẩm định bố cục thẩm mỹ và đối soát gian lận chéo"
            ],
            btn_text="Vào Phân Hệ Chấm Web",
            parent=central
        )
        self.card_web.clicked.connect(self._open_web_grading)
        cards_layout.addWidget(self.card_web, stretch=1)
        
        main_layout.addLayout(cards_layout, stretch=1)
        
        # 4. Dòng mẹo cuối trang (Chữ xám đậm #5B6B82, bỏ icon, nội dung chuẩn)
        footer_lbl = QLabel(
            "Mẹo: Bạn có thể bấm 'Đổi Chế Độ Làm Việc' ở thanh bên bất cứ lúc nào để chuyển phân hệ.",
            central
        )
        footer_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_lbl.setStyleSheet("""
            QLabel {
                color: #5B6B82;
                font-size: 13px;
                font-weight: 500;
                line-height: 1.4;
            }
        """)
        main_layout.addWidget(footer_lbl)

    def _open_practical_exam(self):
        """Launches the dedicated Practical Exam MainWindow."""
        from ui.windows.main_window import AITAMainWindow
        self.practical_win = AITAMainWindow(session_info=self.session_info)
        self.practical_win.show()
        self.close()

    def _open_web_grading(self):
        """Launches the dedicated Web Grading MainWindow."""
        from ui.windows.web_grading_window import WebGradingMainWindow
        self.web_win = WebGradingMainWindow(session_info=self.session_info)
        self.web_win.show()
        self.close()

    def _handle_logout(self):
        """Returns back to login screen."""
        from ui.windows.login_window import LoginWindow
        self.login_win = LoginWindow()
        self.login_win.show()
        self.close()

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
        if hasattr(self, "lbl_ai_badge") and self.lbl_ai_badge:
            if res.get("success"):
                rem = res.get("remaining_tokens", 50000)
                limit = res.get("daily_limit_tokens", 50000)
                self.lbl_ai_badge.setText(f"Gemini AI: Còn {rem:,} / {limit:,} Tokens")
                self.lbl_ai_badge.setToolTip(
                    f"Hạn ngạch AI từ CSDL Neon Postgres:\n"
                    f"• Đã dùng hôm nay: {res.get('used_tokens_today', 0):,} tokens\n"
                    f"• Hạn mức ngày: {limit:,} tokens\n"
                    f"• Còn lại: {rem:,} tokens"
                )
            else:
                self.lbl_ai_badge.setText("Gemini AI: Sẵn Sàng")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Inter", 9)
    app.setFont(font)
    
    win = ModeSelectionWindow()
    win.show()
    sys.exit(app.exec())

