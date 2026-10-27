"""
AITA Desktop Client - Web Grading Guide Dialog (PyQt6)
Hướng dẫn vận hành phần Chấm Bài Tập & Đồ Án Web:
quy trình 5 bước, 3 chế độ chấm, 4 tiêu chí rubric, tính năng AI Vision và bảng phán quyết.
"""

import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea
)

SRC_DIR = Path(__file__).resolve().parent.parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ui.styles.theme import LIGHT_THEME_QSS  # noqa: E402


class WebGradingGuideDialog(QDialog):
    """Hướng dẫn chi tiết quy trình chấm web, các chế độ, tiêu chí rubric và AI Vision."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hướng Dẫn Chấm Bài Tập & Đồ Án Web")
        self.setMinimumSize(960, 680)
        self.resize(1020, 740)
        self.setStyleSheet(LIGHT_THEME_QSS)
        self._init_ui()

    def _card(self, parent: QWidget) -> QFrame:
        card = QFrame(parent)
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
            }
        """)
        return card

    def _section_title(self, text: str, parent: QWidget) -> QLabel:
        lbl = QLabel(text, parent)
        lbl.setStyleSheet("font-size: 19px; font-weight: 700; color: #0284C7; margin-bottom: 2px;")
        return lbl

    def _add_items_card(self, c_layout: QVBoxLayout, items):
        """Thẻ chứa danh sách (tiêu đề + mô tả), có đường phân cách mảnh."""
        card = self._card(c_layout.parentWidget())
        v_layout = QVBoxLayout(card)
        v_layout.setContentsMargins(20, 18, 20, 18)
        v_layout.setSpacing(10)

        for idx, (name, detail) in enumerate(items):
            lbl = QLabel(card)
            lbl.setText(f"<b style='color: #0F172A;'>{name}</b>: <span style='color: #475569;'>{detail}</span>")
            lbl.setStyleSheet("font-size: 14px; line-height: 1.45; border: none; background: transparent;")
            lbl.setWordWrap(True)
            v_layout.addWidget(lbl)
            if idx < len(items) - 1:
                line = QFrame(card)
                line.setFrameShape(QFrame.Shape.HLine)
                line.setFrameShadow(QFrame.Shadow.Plain)
                line.setStyleSheet("color: #F1F5F9; background-color: #F1F5F9; height: 1px; border: none;")
                v_layout.addWidget(line)
        c_layout.addWidget(card)

    def _add_steps(self, c_layout: QVBoxLayout, steps):
        """Mỗi bước là một thẻ riêng (tiêu đề + mô tả nhiều dòng)."""
        for step_title, step_desc in steps:
            card = self._card(c_layout.parentWidget())
            cs_layout = QVBoxLayout(card)
            cs_layout.setContentsMargins(18, 16, 18, 16)
            cs_layout.setSpacing(6)

            lbl_st = QLabel(step_title, card)
            lbl_st.setStyleSheet("font-size: 15px; font-weight: 700; color: #0F172A; border: none; background: transparent;")
            cs_layout.addWidget(lbl_st)

            lbl_sd = QLabel(step_desc, card)
            lbl_sd.setStyleSheet("font-size: 14px; color: #475569; line-height: 1.45; border: none; background: transparent;")
            lbl_sd.setWordWrap(True)
            cs_layout.addWidget(lbl_sd)

            c_layout.addWidget(card)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # ----------------------------------------------------------------------
        # 1. Thẻ tiêu đề cố định phía trên (không cuộn theo)
        # ----------------------------------------------------------------------
        header_card = QFrame(self)
        header_card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
            }
        """)
        h_layout = QVBoxLayout(header_card)
        h_layout.setContentsMargins(20, 16, 20, 16)
        h_layout.setSpacing(6)

        lbl_title = QLabel("Quy Chuẩn Chấm Bài Tập & Đồ Án Web", header_card)
        lbl_title.setStyleSheet("font-size: 18px; font-weight: 700; color: #0F172A; border: none; background: transparent;")
        h_layout.addWidget(lbl_title)

        lbl_desc = QLabel(
            "Tài liệu quy chuẩn quy trình 5 bước thẩm định web, 3 chế độ chấm, 4 tiêu chí rubric "
            "(thang 10) và hướng dẫn tính năng AI Vision trong hệ thống AITA.",
            header_card
        )
        lbl_desc.setStyleSheet("font-size: 14px; color: #475569; line-height: 1.45; border: none; background: transparent;")
        lbl_desc.setWordWrap(True)
        h_layout.addWidget(lbl_desc)
        main_layout.addWidget(header_card)

        # ----------------------------------------------------------------------
        # 2. Vùng nội dung cuộn
        # ----------------------------------------------------------------------
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background-color: #F8FAFC; }
            QScrollBar:vertical { background-color: #F1F5F9; width: 12px; margin: 0px; border-radius: 6px; }
            QScrollBar::handle:vertical { background-color: #94A3B8; min-height: 36px; border-radius: 6px; }
            QScrollBar::handle:vertical:hover { background-color: #64748B; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

        container = QWidget()
        container.setStyleSheet("background-color: #F8FAFC;")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(0, 16, 8, 16)
        c_layout.setSpacing(14)

        # ======================================================================
        # PHẦN 1: QUY TRÌNH CHẤM WEB (5 BƯỚC)
        # ======================================================================
        c_layout.addWidget(self._section_title("Quy Trình Chấm Web Khép Kín (5 Bước Chuẩn)", container))

        flow_steps = [
            ("Bước 1: Tạo hoặc chọn phiên chấm web",
             "Nhấn nút [Quản Lý Phiên] trên thanh công cụ để tạo phiên chấm mới (tên phiên, mã khóa học, tên lớp) "
             "hoặc chuyển đổi giữa các phiên đã có. Mỗi phiên chứa danh sách bài nộp và kết quả riêng."),
            ("Bước 2: Thêm bài nộp",
             "Nhấn [Thêm Bài Nộp] để nhập từng bài (MSSV, họ tên, link theo chế độ) hoặc dán nhiều dòng cùng lúc; "
             "cũng có thể nhập danh sách từ file CSV qua nút [Nhập File CSV]. Hệ thống tự cảnh báo trùng MSSV."),
            ("Bước 3: Chọn chế độ chấm",
             "Tick chọn chế độ phù hợp ở thanh công cụ: Live URL (chấm trang đang chạy), GitHub (chấm mã nguồn repo) "
             "hoặc Hybrid (kết hợp cả hai). Bài nộp thiếu link theo chế độ sẽ bị đánh dấu 'Thiếu link'."),
            ("Bước 4: Bắt đầu thẩm định",
             "Nhấn [Bắt Đầu Thẩm Định Web]. Hệ thống tải trang bằng Chromium đi kèm ứng dụng, chấm 4 tiêu chí rubric "
             "(DOM, Lint, Chức Năng, UI/UX), chụp ảnh toàn trang (viewport desktop 1440px) và ghi nhận xét AI Vision."),
            ("Bước 5: Xem chi tiết, điều chỉnh và xuất bảng điểm",
             "Bấm vào từng bài nộp để xem điểm từng tiêu chí, ảnh chụp màn hình và nhận xét của AI Vision. "
             "Dùng [Sửa Điểm Thủ Công] hoặc [Chấm Lại Bài Này] khi cần phúc khảo. Cuối cùng bấm [Xuất Bảng Điểm] "
             "để lưu bảng điểm ra Excel (.xlsx) hoặc PDF.")
        ]
        self._add_steps(c_layout, flow_steps)

        # ======================================================================
        # PHẦN 2: 3 CHẾ ĐỘ CHẤM
        # ======================================================================
        c_layout.addSpacing(16)
        c_layout.addWidget(self._section_title("Ba Chế Độ Chấm Web", container))
        self._add_items_card(c_layout, [
            ("Live URL",
             "Chấm trang web đang chạy công khai (Vercel, GitHub Pages...). Thẩm định đủ 4 tiêu chí, gồm cả UI/UX "
             "qua ảnh chụp trình duyệt. Cần nhập live URL."),
            ("GitHub",
             "Chấm mã nguồn repository (tải mã tĩnh về phân tích). Chỉ thẩm định 3 tiêu chí DOM, Lint và Chức Năng — "
             "không có tiêu chí UI/UX vì không chụp được giao diện. Cần nhập repo URL."),
            ("Hybrid",
             "Kết hợp cả hai: đối chiếu mã repo với trang live. Yêu cầu nhập đủ cả live URL lẫn GitHub repo URL.")
        ])

        # ======================================================================
        # PHẦN 3: 4 TIÊU CHÍ RUBRIC (THANG 10)
        # ======================================================================
        c_layout.addSpacing(16)
        c_layout.addWidget(self._section_title("Bốn Tiêu Chí Rubric Chấm Web (Thang Điểm 10)", container))
        self._add_items_card(c_layout, [
            ("1. Cấu Trúc HTML & DOM (2.0đ)",
             "Kiểm tra thẻ ngữ nghĩa (header, nav, main, footer), thuộc tính alt của ảnh và cấp bậc tiêu đề (heading hierarchy)."),
            ("2. Lint Chất Lượng Mã (2.0đ)",
             "Phân tích tĩnh mã HTML/CSS/JS để phát hiện lỗi cú pháp, mã rác và các vấn đề chất lượng nguồn."),
            ("3. Chức Năng / E2E (3.0đ)",
             "Kiểm tra trang hoạt động đúng chức năng theo yêu cầu đồ án (tương tác cơ bản, liên kết, dữ liệu hiển thị)."),
            ("4. UI/UX Qua AI Vision (3.0đ)",
             "AI Vision đánh giá ảnh chụp toàn trang (viewport desktop 1440px) theo tiêu chí thẩm mỹ: bố cục, màu sắc, "
             "khoảng trắng, tính nhất quán. Chỉ áp dụng cho chế độ Live URL và Hybrid.")
        ])

        # ======================================================================
        # PHẦN 4: HƯỚNG DẪN TÍNH NĂNG AI VISION
        # ======================================================================
        c_layout.addSpacing(16)
        c_layout.addWidget(self._section_title("Hướng Dẫn Tính Năng AI Vision", container))
        self._add_items_card(c_layout, [
            ("AI Vision chấm UI/UX",
             "Gửi ảnh chụp màn hình qua AI Gateway để chấm tiêu chí UI/UX (3.0đ) và soạn nhận xét riêng cho từng bài. "
             "Nhận xét hiển thị trong cửa sổ chi tiết bài nộp."),
            ("Pill trạng thái AI Vision",
             "Góc trên phải màn hình hiển thị hạn mức: 'AI Vision: Còn X / Y Tokens', 'AI Vision: Hết token' "
             "hoặc 'AI Vision: Chưa đăng nhập' khi phiên đăng nhập hết hạn."),
            ("Khi không có AI Vision",
             "Hệ thống cảnh báo trước khi chấm và vẫn cho phép tiếp tục; tiêu chí UI/UX được tính 0.0đ (mất 3.0đ) "
             "nhưng 3 tiêu chí còn lại vẫn chấm bình thường."),
            ("Chuỗi render dự phòng",
             "Chromium đi kèm ứng dụng được ưu tiên; nếu thiếu, hệ thống tự hạ cấp về tải trang bằng HTTP thuần, "
             "cuối cùng là phân tích tĩnh. Trang không có nội dung HTML sẽ được gợi ý chuyển sang chế độ Hybrid.")
        ])

        # ======================================================================
        # PHẦN 5: BẢNG PHÁN QUYẾT WEB
        # ======================================================================
        c_layout.addSpacing(16)
        c_layout.addWidget(self._section_title("Bảng Tra Cứu Phán Quyết Chấm Web", container))
        self._add_items_card(c_layout, [
            ("PENDING",
             "Bài nộp chưa được thẩm định hoặc đang chờ trong hàng đợi chấm."),
            ("PASSED",
             "Điểm tổng đạt từ 7.0/10.0 trở lên — đồ án đạt yêu cầu."),
            ("PARTIAL",
             "Điểm tổng từ 5.0 đến dưới 7.0 — đạt một phần yêu cầu, cần cải thiện."),
            ("FAILED",
             "Điểm tổng dưới 5.0/10.0 — chưa đạt yêu cầu đồ án."),
            ("Thiếu link",
             "Bài nộp không có đủ link (live URL hoặc repo URL) theo chế độ chấm đang chọn.")
        ])

        c_layout.addStretch(1)
        scroll.setWidget(container)
        main_layout.addWidget(scroll, stretch=1)

        # ----------------------------------------------------------------------
        # 3. Footer Bar
        # ----------------------------------------------------------------------
        footer = QHBoxLayout()
        footer.setContentsMargins(0, 10, 0, 0)
        footer.addStretch(1)

        btn_close = QPushButton("Đóng", self)
        btn_close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_close.setFixedHeight(38)
        btn_close.setMinimumWidth(110)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #0284C7;
                border-radius: 6px;
                padding: 0 24px;
                color: #0284C7;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #F0F9FF;
                border-color: #0369A1;
                color: #0369A1;
            }
            QPushButton:focus {
                outline: 2px solid #BAE6FD;
            }
        """)
        btn_close.clicked.connect(self.accept)
        footer.addWidget(btn_close)
        main_layout.addLayout(footer)
