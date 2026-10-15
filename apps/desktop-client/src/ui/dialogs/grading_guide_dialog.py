"""
AITA Desktop Client - Grading Guide Dialog (PyQt6)
UC-07 & UC-11: Practical Exam Grading Guidelines & Strategy Specifications.
Clean Typography, Light Theme, Text-only (no decorative emoji/icons per user request).
"""

import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView
)

SRC_DIR = Path(__file__).resolve().parent.parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ui.styles.theme import (
    LIGHT_THEME_QSS, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_PRIMARY_BG,
    COLOR_SURFACE, COLOR_SURFACE_SECONDARY, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED, COLOR_BORDER_DEFAULT
)


class GradingGuideDialog(QDialog):
    """
    Dialog displaying comprehensive grading instructions, matching rules, and verdict explanations.
    Accessible directly from the main workspace window.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hướng Dẫn Chấm Thi Thực Hành")
        self.setMinimumSize(960, 680)
        self.resize(1020, 740)
        self.setStyleSheet(LIGHT_THEME_QSS)

        self._init_ui()

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

        lbl_title = QLabel("Quy Chuẩn Chấm Điểm & Hướng Dẫn Vận Hành", header_card)
        lbl_title.setStyleSheet("font-size: 18px; font-weight: 700; color: #0F172A; border: none; background: transparent;")
        h_layout.addWidget(lbl_title)

        lbl_desc = QLabel(
            "Tài liệu quy chuẩn quy trình 4 bước chấm tự động, 7 tiêu chí so khớp đầu ra "
            "và bảng tra cứu các mã phán quyết trong hệ thống AITA.",
            header_card
        )
        lbl_desc.setStyleSheet("font-size: 14px; color: #475569; line-height: 1.45; border: none; background: transparent;")
        lbl_desc.setWordWrap(True)
        h_layout.addWidget(lbl_desc)

        main_layout.addWidget(header_card)

        # ----------------------------------------------------------------------
        # 2. Vùng nội dung cuộn (Scrollable Area)
        # ----------------------------------------------------------------------
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #F8FAFC;
            }
            QScrollBar:vertical {
                background-color: #F1F5F9;
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #94A3B8;
                min-height: 36px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #64748B;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        container = QWidget()
        container.setStyleSheet("background-color: #F8FAFC;")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(0, 16, 8, 16)
        c_layout.setSpacing(14)

        # ======================================================================
        # PHẦN 1: QUY TRÌNH CHẤM THI THỰC HÀNH KHÉP KÍN (6 BƯỚC CHUẨN)
        # ======================================================================
        lbl_flow_title = QLabel("Quy Trình Chấm Thi Thực Hành Khép Kín (6 Bước Chuẩn)", container)
        lbl_flow_title.setStyleSheet("font-size: 19px; font-weight: 700; color: #0284C7; margin-bottom: 2px;")
        c_layout.addWidget(lbl_flow_title)

        flow_steps = [
            ("Bước 1: Nạp bài nộp từ thư mục",
             "Nhấn nút [1. Nạp Bài Nộp] hoặc [Tạo Đợt Chấm Mới] trên thanh điều hướng và chọn thư mục bài làm của sinh viên. "
             "Hệ thống tự động quét và nhận diện theo quy tắc: mỗi sinh viên là một thư mục con hoặc một tệp mã nguồn có tên bắt đầu bằng MSSV "
             "(ví dụ: SE180001, SE180001_NguyenVanA, SE180001.c). Phần còn lại sau dấu gạch dưới hoặc gạch ngang là họ tên. "
             "Hệ thống tự động cảnh báo nếu phát hiện trùng lặp MSSV và không nạp các mục không hợp lệ."),
            ("Bước 2: Cấu hình testcase và tiêu chí so khớp",
             "Nhấn [2. Cấu Hình Testcase & So Khớp] để thiết lập các bộ dữ liệu vào (stdin) và kết quả kỳ vọng (stdout) cho từng câu hỏi. "
             "Bạn có thể nhập thủ công hoặc kích hoạt Gemini AI để tự động suy luận sinh 5 đến 10 testcase biên "
             "mà không cần viết mã giải mẫu. Sau đó tick chọn các tiêu chí so khớp phù hợp và nhấn [Lưu Testcase]."),
            ("Bước 3: Bắt đầu chấm hàng loạt",
             "Nhấn nút [3. Bắt Đầu Chấm Hàng Loạt]. Động cơ Sandbox Runner sẽ tự động biên dịch và thực thi an toàn từng bài làm "
             "trong môi trường cách ly độc lập, kiểm soát chặt chẽ giới hạn thời gian (ms) và bộ nhớ RAM (MB)."),
            ("Bước 4: Quét đạo văn AST",
             "Nhấn nút [4. Quét Đạo Văn AST] để phân tích cây cú pháp trừu tượng, đối soát gian lận chép mã nguồn chéo "
             "giữa tất cả sinh viên trong đợt chấm."),
            ("Bước 5: Xuất bảng điểm",
             "Nhấn nút [5. Xuất Bảng Điểm] để xuất kết quả hoàn chỉnh ra bảng tính Excel (.xlsx), tệp báo cáo PDF hoặc CSV theo yêu cầu."),
            ("Bước 6: Kết thúc phiên chấm",
             "Nhấn nút [6. Kết Thúc Phiên Chấm] để chốt đợt thi, toàn bộ bảng điểm và nhật ký thực thi được lưu trữ an toàn trong CSDL cục bộ và đưa hệ thống trở về màn hình chờ ban đầu.")
        ]

        for step_title, step_desc in flow_steps:
            card_step = QFrame(container)
            card_step.setStyleSheet("""
                QFrame {
                    background-color: #FFFFFF;
                    border: 1px solid #E2E8F0;
                    border-radius: 10px;
                }
            """)
            cs_layout = QVBoxLayout(card_step)
            cs_layout.setContentsMargins(18, 16, 18, 16)
            cs_layout.setSpacing(6)

            lbl_st = QLabel(step_title, card_step)
            lbl_st.setStyleSheet("font-size: 15px; font-weight: 700; color: #0F172A; border: none; background: transparent;")
            cs_layout.addWidget(lbl_st)

            lbl_sd = QLabel(step_desc, card_step)
            lbl_sd.setStyleSheet("font-size: 14px; color: #475569; line-height: 1.45; border: none; background: transparent;")
            lbl_sd.setWordWrap(True)
            cs_layout.addWidget(lbl_sd)

            c_layout.addWidget(card_step)

        # ======================================================================
        # PHẦN 2: HƯỚNG DẪN 7 TIÊU CHÍ SO KHỚP ĐẦU RA
        # ======================================================================
        c_layout.addSpacing(16)
        lbl_strat_t = QLabel("Hướng Dẫn 7 Tiêu Chí So Khớp Đầu Ra", container)
        lbl_strat_t.setStyleSheet("font-size: 19px; font-weight: 700; color: #0284C7; margin-bottom: 2px;")
        c_layout.addWidget(lbl_strat_t)

        card_strat = QFrame(container)
        card_strat.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
            }
        """)
        strat_layout = QVBoxLayout(card_strat)
        strat_layout.setContentsMargins(20, 18, 20, 18)
        strat_layout.setSpacing(12)

        strat_items = [
            ("1. Bỏ qua khoảng trắng (Ignore Whitespace)",
             "Khuyên dùng mặc định. Bỏ qua khoảng trắng thừa, ký tự tab và các dấu xuống dòng ở cuối luồng ra. Phù hợp với phần lớn bài tập lập trình cơ bản."),
            ("2. Không phân biệt chữ hoa / chữ thường (Case Insensitive)",
             "Chấp nhận cả 'YES', 'Yes', 'yes' hoặc 'TRUE', 'True'. Áp dụng khi đề bài chỉ yêu cầu kiểm tra tính đúng đắn ngữ nghĩa của kết quả."),
            ("3. Dung sai số thực (Floating Tolerance)",
             "Áp dụng khi đầu ra là số thực có sai số phép tính dấu phẩy động (dung sai mặc định <= 1e-5, ví dụ 3.14159 so với 3.141592)."),
            ("4. Không phân biệt thứ tự (Unordered Tokens)",
             "Áp dụng khi đề bài yêu cầu in ra tập hợp các số hoặc từ mà thứ tự xuất hiện không quan trọng (ví dụ: in ra danh sách các ước số của N)."),
            ("5. Biểu thức chính quy (Regex Pattern)",
             "Đầu ra kỳ vọng là một mẫu biểu thức chính quy (Regex) để kiểm tra cấu trúc chuỗi định dạng đặc biệt (ví dụ ngày tháng DD/MM/YYYY hoặc địa chỉ email)."),
            ("6. Trình kiểm tra tùy biến (Special Judge)",
             "Dành cho bài toán có nhiều nghiệm thỏa mãn, hệ thống kiểm tra tính hợp lệ qua kịch bản thẩm định chuyên biệt."),
            ("7. Khớp chính xác tuyệt đối (Exact Match)",
             "Bỏ tick toàn bộ các tiêu chí nới lỏng để bắt buộc đầu ra thực tế phải trùng khớp 100% từng ký tự so với kết quả kỳ vọng.")
        ]

        for idx, (s_name, s_detail) in enumerate(strat_items):
            lbl_item = QLabel(card_strat)
            lbl_item.setText(f"<b style='color: #0F172A;'>{s_name}</b>: <span style='color: #475569;'>{s_detail}</span>")
            lbl_item.setStyleSheet("font-size: 14px; line-height: 1.45; border: none; background: transparent;")
            lbl_item.setWordWrap(True)
            strat_layout.addWidget(lbl_item)

            # Thêm đường phân cách mảnh giữa các mục
            if idx < len(strat_items) - 1:
                line = QFrame(card_strat)
                line.setFrameShape(QFrame.Shape.HLine)
                line.setFrameShadow(QFrame.Shadow.Plain)
                line.setStyleSheet("color: #F1F5F9; background-color: #F1F5F9; height: 1px; border: none;")
                strat_layout.addWidget(line)

        c_layout.addWidget(card_strat)

        # ======================================================================
        # PHẦN 3: BẢNG TRA CỨU CÁC PHÁN QUYẾT CHẤM ĐIỂM (VERDICTS)
        # ======================================================================
        c_layout.addSpacing(16)
        lbl_verd_t = QLabel("Bảng Tra Cứu Các Phán Quyết Chấm Điểm (Verdicts)", container)
        lbl_verd_t.setStyleSheet("font-size: 19px; font-weight: 700; color: #0284C7; margin-bottom: 2px;")
        c_layout.addWidget(lbl_verd_t)

        card_verd = QFrame(container)
        card_verd.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
            }
        """)
        cv_layout = QVBoxLayout(card_verd)
        cv_layout.setContentsMargins(16, 16, 16, 16)

        table_verdicts = QTableWidget(6, 2, card_verd)
        table_verdicts.setHorizontalHeaderLabels(["Mã Phán Quyết", "Ý Nghĩa & Nguyên Nhân Xử Lý"])
        v_header = table_verdicts.verticalHeader()
        if v_header is not None:
            v_header.setVisible(False)
        table_verdicts.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table_verdicts.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table_verdicts.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        table_verdicts.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                gridline-color: #F1F5F9;
                background-color: #FFFFFF;
            }
            QHeaderView::section {
                background-color: #F8FAFC;
                color: #0F172A;
                font-weight: 700;
                font-size: 13px;
                padding: 10px 12px;
                border: none;
                border-bottom: 1px solid #E2E8F0;
            }
            QTableWidget::item {
                padding: 10px 12px;
                border-bottom: 1px solid #F1F5F9;
            }
        """)

        header_v = table_verdicts.horizontalHeader()
        if header_v is not None:
            header_v.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
            header_v.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table_verdicts.setColumnWidth(0, 240)

        verdicts_data = [
            ("[AC] ACCEPTED — ĐẠT CHUẨN",
             "Mã nguồn chạy đúng 100% testcase và tuân thủ đầy đủ các giới hạn thời gian, bộ nhớ được cấu hình.",
             "#16A34A"),
            ("[WA] WRONG ANSWER — SAI KẾT QUẢ",
             "Chương trình thực thi thành công nhưng kết quả in ra màn hình khác với kết quả kỳ vọng.",
             "#DC2626"),
            ("[CE] COMPILE ERROR — LỖI BIÊN DỊCH",
             "Lỗi cú pháp mã nguồn hoặc thiếu thư viện liên kết. Hệ thống tự động ghi nhận 0 điểm và cung cấp nhật ký biên dịch chi tiết.",
             "#BE123C"),
            ("[TLE] TIME LIMIT EXCEEDED — QUÁ THỜI GIAN",
             "Chương trình chạy vượt quá giới hạn thời gian quy định (mặc định 1000ms), thường do vòng lặp vô tận hoặc thuật toán chưa tối ưu.",
             "#D97706"),
            ("[MLE] MEMORY LIMIT EXCEEDED — QUÁ BỘ NHỚ",
             "Chương trình cấp phát bộ nhớ RAM vượt quá hạn mức cho phép (mặc định 256MB hoặc theo cấu hình trong Cấu Hình Môi Trường).",
             "#7E22CE"),
            ("[RE] RUNTIME ERROR — LỖI THỰC THI",
             "Chương trình bị dừng đột ngột khi đang chạy (chia cho 0, truy cập mảng ngoài giới hạn vùng nhớ, lỗi phân đoạn segfault).",
             "#9A3412")
        ]

        table_verdicts.setFixedHeight(340)

        for row_idx, (v_tag, v_explanation, v_color) in enumerate(verdicts_data):
            item_tag = QTableWidgetItem(v_tag)
            item_tag.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            font_tag = QFont()
            font_tag.setBold(True)
            font_tag.setPointSize(10)
            item_tag.setFont(font_tag)
            item_tag.setForeground(Qt.GlobalColor.black)
            # Dùng màu chuyên biệt cho từng loại phán quyết

            # Đặt widget label để có màu và wrap text hoàn hảo
            lbl_tag_cell = QLabel(v_tag, table_verdicts)
            lbl_tag_cell.setStyleSheet(f"color: {v_color}; font-weight: 700; font-size: 13px; padding-left: 6px;")
            table_verdicts.setCellWidget(row_idx, 0, lbl_tag_cell)

            lbl_desc_cell = QLabel(v_explanation, table_verdicts)
            lbl_desc_cell.setStyleSheet("color: #475569; font-size: 14px; line-height: 1.45;")
            lbl_desc_cell.setWordWrap(True)
            table_verdicts.setCellWidget(row_idx, 1, lbl_desc_cell)
            table_verdicts.setRowHeight(row_idx, 52)

        cv_layout.addWidget(table_verdicts)
        c_layout.addWidget(card_verd)

        c_layout.addStretch(1)
        scroll.setWidget(container)
        main_layout.addWidget(scroll, stretch=1)

        # ----------------------------------------------------------------------
        # 3. Footer Bar (Nút Đóng viền xanh, cách mép dưới & mép phải >= 16px)
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
