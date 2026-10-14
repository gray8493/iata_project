"""
AITA Desktop Client - Multimodal Web Assignment Grading Dashboard (PyQt6)
UC-19: Automated Web Assignment Grading & Scoring (Playwright + Gemini Vision)
"""

import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QTabWidget, QSplitter, QTextEdit, QMessageBox
)

from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ui.styles.theme import LIGHT_THEME_QSS



class WebGradingDialog(QDialog):
    """
    Grading Dashboard for Web Development assignments (HTML5, CSS3, JS, PHP)
    with 4-component Rubric and Playwright screenshots.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chấm Điểm Bài Tập Web Tự Động (Playwright & Gemini Vision)")
        self.setMinimumSize(1260, 780)
        self.resize(1320, 820)
        self.setStyleSheet(LIGHT_THEME_QSS)
        self._init_ui()
        self._populate_web_submissions()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        
        # 1. Mode Switcher & Header Card
        top_card = QFrame(self)
        top_card.setProperty("class", "Card")
        t_layout = QHBoxLayout(top_card)
        t_layout.setContentsMargins(16, 12, 16, 12)
        
        lbl_title = QLabel("Phân Hệ Chấm Điểm Web Đa Thành Phần (Rubric 4 Tiêu Chí)", top_card)
        lbl_title.setProperty("class", "Heading2")
        t_layout.addWidget(lbl_title)
        
        t_layout.addStretch(1)
        
        lbl_mode = QLabel("Chế Độ Chấm:", top_card)
        lbl_mode.setStyleSheet("font-weight: 700; font-size: 11px;")
        t_layout.addWidget(lbl_mode)
        
        btn_hybrid = QPushButton("Chế Độ Kết Hợp (HYBRID)", top_card)
        btn_hybrid.setStyleSheet("background-color: #2563eb; color: #ffffff; font-weight: 700; border-radius: 8px; padding: 6px 14px;")
        t_layout.addWidget(btn_hybrid)
        
        layout.addWidget(top_card)
        
        # 2. Main Horizontal Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        
        # LEFT: Web Submissions Table
        left_widget = QWidget(splitter)
        l_layout = QVBoxLayout(left_widget)
        l_layout.setContentsMargins(0, 0, 0, 0)
        
        self.table_web = QTableWidget(left_widget)
        self.table_web.setColumnCount(8)
        self.table_web.setHorizontalHeaderLabels([
            "MSSV", "Domain Website", "DOM", "Lint", "Playwright", "Gemini UI", "Tổng Điểm", "Kết Quả"
        ])
        self.table_web.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table_web.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_web.cellClicked.connect(self._on_row_selected)
        l_layout.addWidget(self.table_web)
        splitter.addWidget(left_widget)
        
        # RIGHT: Rubric Details & Dual Viewport Screenshots
        right_widget = QWidget(splitter)
        r_layout = QVBoxLayout(right_widget)
        r_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget(right_widget)
        
        # TAB 1: Rubric Breakdown
        tab_rubric = QWidget()
        tr_layout = QVBoxLayout(tab_rubric)
        tr_layout.setSpacing(8)
        
        self.txt_rubric_log = QTextEdit(tab_rubric)
        self.txt_rubric_log.setReadOnly(True)
        self.txt_rubric_log.setText("""CHI TIẾT ĐIỂM RUBRIC 4 THÀNH PHẦN:

1. [2.0 / 2.5] Cấu Trúc DOM & Thẻ Ngữ Nghĩa HTML5:
   - Sử dụng đúng thẻ semantic: <header>, <nav>, <main>, <section>, <footer>.
   - Thiếu thuộc tính alt trong 2 thẻ <img>.

2. [2.5 / 2.5] Chuẩn W3C Validator & CSS Linting:
   - 0 lỗi cú pháp HTML W3C.
   - CSS đạt chuẩn Flexbox/Grid hiện đại, không dùng !important bừa bãi.

3. [2.5 / 2.5] Playwright E2E Tương Tác Hành Vi:
   - Tự động click "Thêm vào giỏ hàng" -> Số lượng giỏ hàng nhảy từ 0 lên 1.
   - Kiểm tra responsive: Ẩn desktop navbar, hiển thị hamburger menu ở mobile viewport.

4. [2.0 / 2.5] Đánh Giá Thẩm Mỹ Giao Diện (Gemini Vision AI):
   - Điểm thẩm mỹ: 8.5/10. Màu sắc hài hòa, độ tương phản text/background đạt WCAG AA.
   - Khoảng cách lề (padding) phần Banner Hero trên mobile hơi sát viền mép.""")
        tr_layout.addWidget(self.txt_rubric_log)
        self.tabs.addTab(tab_rubric, "Chi Tiết Rubric")
        
        # TAB 2: Screenshots Preview
        tab_shots = QWidget()
        ts_layout = QVBoxLayout(tab_shots)
        
        lbl_shot_info = QLabel("Ảnh Chụp Màn Hình Headless Playwright (Desktop 1920x1080 & Mobile 375x667):", tab_shots)
        lbl_shot_info.setStyleSheet("font-weight: 700; font-size: 11px;")
        ts_layout.addWidget(lbl_shot_info)
        
        shots_container = QHBoxLayout()
        # Mock Desktop viewport box
        shot_dt = QLabel("Desktop Viewport\n(1920 x 1080)\n\n[Ảnh chụp giao diện web hoàn chỉnh]", tab_shots)
        shot_dt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        shot_dt.setStyleSheet("background-color: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 8px; color: #475569; padding: 30px;")
        shots_container.addWidget(shot_dt, stretch=2)
        
        # Mock Mobile viewport box
        shot_mb = QLabel("Mobile Viewport\n(375 x 667)\n\n[Responsive]", tab_shots)
        shot_mb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        shot_mb.setStyleSheet("background-color: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 8px; color: #475569; padding: 30px;")
        shots_container.addWidget(shot_mb, stretch=1)
        
        ts_layout.addLayout(shots_container)
        self.tabs.addTab(tab_shots, "Ảnh Chụp Giao Diện")
        
        r_layout.addWidget(self.tabs)
        splitter.addWidget(right_widget)
        
        splitter.setSizes([650, 610])
        layout.addWidget(splitter, stretch=1)
        
        # 3. Footer
        footer = QHBoxLayout()
        footer.addStretch(1)
        btn_close = QPushButton("Đóng", self)
        btn_close.setProperty("class", "SecondaryBtn")
        btn_close.clicked.connect(self.accept)
        footer.addWidget(btn_close)
        layout.addLayout(footer)

    def _populate_web_submissions(self):
        web_data = [
            ("SE180012", "https://se180012-shop.vercel.app", "9.0", "10.0", "10.0", "8.5", "9.4 / 10", "PASSED"),
            ("SE180045", "https://se180045-web.netlify.app", "8.0", "9.0", "10.0", "8.0", "8.8 / 10", "PASSED"),
            ("SE180078", "https://se180078-portfolio.vercel.app", "6.0", "7.0", "6.0", "6.5", "6.4 / 10", "PARTIAL"),
            ("SE180091", "http://localhost:3000", "0.0", "0.0", "0.0", "0.0", "0.0 / 10", "FAILED (404)"),
        ]
        self.table_web.setRowCount(len(web_data))
        for r, row in enumerate(web_data):
            for c, val in enumerate(row):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if val == "PASSED":
                    item.setForeground(Qt.GlobalColor.darkGreen)
                elif "FAILED" in val:
                    item.setForeground(Qt.GlobalColor.red)
                self.table_web.setItem(r, c, item)

    def _on_row_selected(self, r, c):
        pass
