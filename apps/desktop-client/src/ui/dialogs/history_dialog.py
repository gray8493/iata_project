"""
AITA Desktop Client - Grading Sessions History Dialog (PyQt6)
UC-07: Manage Classes & Grading Sessions (View History & Switch Sessions)
Matches DESKTOP APP UI/UX DESIGN SYSTEM (Clean Cards, Precise Layout).
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCursor, QFont
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QMessageBox
)

SRC_DIR = Path(__file__).resolve().parent.parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ui.styles.theme import (
    LIGHT_THEME_QSS, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_PRIMARY_BG,
    COLOR_SURFACE, COLOR_SURFACE_SECONDARY,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_BORDER_DEFAULT, COLOR_SUCCESS, COLOR_SUCCESS_BG,
    COLOR_ERROR, COLOR_ERROR_BG
)
from database.db_manager import DatabaseManager


class HistoryDialog(QDialog):
    """
    Hộp thoại xem lại lịch sử các đợt chấm thi theo từng lớp và môn học.
    Hỗ trợ tìm kiếm, lọc theo môn, mở lại đợt chấm hoặc xóa đợt chấm.
    """

    session_selected = pyqtSignal(int)  # Phát tín hiệu class_id khi chọn mở đợt chấm
    session_deleted = pyqtSignal(int)   # Phát tín hiệu class_id khi xóa đợt chấm

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Lịch Sử & Quản Lý Đợt Chấm Điểm")
        self.setMinimumSize(1080, 680)
        self.resize(1140, 720)
        self.setStyleSheet(LIGHT_THEME_QSS)

        self.db = DatabaseManager()
        self.selected_class_id: Optional[int] = None
        self._all_history: List[Dict[str, Any]] = []

        self._init_ui()
        self._load_history_data()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        # 1. Khung tiêu đề đầu trang
        header_card = QFrame(self)
        header_card.setProperty("class", "Card")
        h_layout = QHBoxLayout(header_card)
        h_layout.setContentsMargins(20, 16, 20, 16)
        h_layout.setSpacing(16)

        title_box = QVBoxLayout()
        title_box.setSpacing(6)
        lbl_title = QLabel("Lịch Sử & Quản Lý Các Đợt Chấm Thi", header_card)
        lbl_title.setStyleSheet(f"font-size: 18px; font-weight: 700; line-height: 1.4; color: {COLOR_TEXT_PRIMARY};")
        title_box.addWidget(lbl_title)

        # Dòng mô tả chuẩn hóa theo yêu cầu
        lbl_desc = QLabel(
            "Xem lại các đợt chấm theo lớp. Bấm 'Mở Đợt Chấm' để tải đợt đó lên màn hình chính.",
            header_card
        )
        lbl_desc.setStyleSheet(f"font-size: 13px; line-height: 1.4; color: {COLOR_TEXT_SECONDARY};")
        title_box.addWidget(lbl_desc)
        h_layout.addLayout(title_box)

        h_layout.addStretch(1)

        btn_new_session = QPushButton("Tạo Đợt Chấm Mới", header_card)
        btn_new_session.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_new_session.setFixedHeight(38)
        btn_new_session.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: #FFFFFF;
                font-weight: 600;
                font-size: 13px;
                line-height: 1.4;
                padding: 0 18px;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_HOVER};
            }}
        """)
        btn_new_session.clicked.connect(self._open_new_session_dialog)
        h_layout.addWidget(btn_new_session)

        main_layout.addWidget(header_card)

        # 2. Khung bảng lịch sử & thanh tìm kiếm
        table_card = QFrame(self)
        table_card.setProperty("class", "Card")
        t_layout = QVBoxLayout(table_card)
        t_layout.setContentsMargins(18, 16, 18, 16)
        t_layout.setSpacing(14)

        # Hàng tìm kiếm theo mã lớp, lọc theo môn & dòng tóm tắt số lượng
        filter_row = QHBoxLayout()
        filter_row.setSpacing(12)
        filter_row.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Ô tìm kiếm theo mã lớp
        lbl_search = QLabel("Tìm kiếm:", table_card)
        lbl_search.setStyleSheet(f"font-size: 13px; line-height: 1.4; color: {COLOR_TEXT_PRIMARY}; font-weight: 500;")
        filter_row.addWidget(lbl_search)

        self.txt_search = QLineEdit(table_card)
        self.txt_search.setPlaceholderText("Nhập mã lớp để tìm kiếm...")
        self.txt_search.setFixedHeight(36)
        self.txt_search.setMinimumWidth(220)
        self.txt_search.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {COLOR_BORDER_DEFAULT};
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 13px;
                line-height: 1.4;
                background-color: #FFFFFF;
                color: {COLOR_TEXT_PRIMARY};
            }}
            QLineEdit:focus {{
                border-color: {COLOR_PRIMARY};
            }}
        """)
        self.txt_search.textChanged.connect(self._apply_filter)
        filter_row.addWidget(self.txt_search)

        # Bộ lọc theo môn học
        lbl_filter_course = QLabel("Môn học:", table_card)
        lbl_filter_course.setStyleSheet(f"font-size: 13px; line-height: 1.4; color: {COLOR_TEXT_PRIMARY}; font-weight: 500;")
        filter_row.addWidget(lbl_filter_course)

        self.cb_course_filter = QComboBox(table_card)
        self.cb_course_filter.setFixedHeight(36)
        self.cb_course_filter.setMinimumWidth(150)
        self.cb_course_filter.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {COLOR_BORDER_DEFAULT};
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 13px;
                line-height: 1.4;
                background-color: #FFFFFF;
                color: {COLOR_TEXT_PRIMARY};
            }}
            QComboBox:focus {{
                border-color: {COLOR_PRIMARY};
            }}
        """)
        self.cb_course_filter.addItem("Tất cả môn học")
        self.cb_course_filter.currentIndexChanged.connect(self._apply_filter)
        filter_row.addWidget(self.cb_course_filter)

        filter_row.addStretch(1)

        # Dòng tổng số đợt chấm và bài nộp: chữ rõ hơn #475569, 13px, bỏ dấu "|"
        self.lbl_summary_bar = QLabel("", table_card)
        self.lbl_summary_bar.setStyleSheet("font-size: 13px; font-weight: 500; color: #475569; line-height: 1.4;")
        filter_row.addWidget(self.lbl_summary_bar)

        t_layout.addLayout(filter_row)

        # Bảng hiển thị lịch sử
        self.table = QTableWidget(table_card)
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Mã Lớp / Đợt Chấm", "Môn Học", "Ngôn Ngữ", "Số Bài Nộp",
            "Tiến Độ Chấm", "Tỷ Lệ Đạt (AC)", "Điểm Trung Bình", "Thao Tác"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(54)

        # Căn lề tiêu đề khớp chính xác với nội dung từng cột
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 100)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 100)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 110)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(4, 160)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(5, 130)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(6, 130)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(7, 210)

        # Căn lề tiêu đề cột: Cột 0 căn trái, các cột còn lại căn giữa
        it_h0 = self.table.horizontalHeaderItem(0)
        if it_h0:
            it_h0.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        for col in range(1, 8):
            it_h = self.table.horizontalHeaderItem(col)
            if it_h:
                it_h.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        t_layout.addWidget(self.table)

        # Khung hiển thị khi bảng trống hoàn toàn
        self.empty_widget = QWidget(table_card)
        empty_layout = QVBoxLayout(self.empty_widget)
        empty_layout.setContentsMargins(20, 48, 20, 48)
        empty_layout.setSpacing(16)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_empty_msg = QLabel("Chưa có đợt chấm nào", self.empty_widget)
        lbl_empty_msg.setStyleSheet("font-size: 15px; font-weight: 500; color: #64748b; line-height: 1.4;")
        lbl_empty_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(lbl_empty_msg)

        btn_empty_create = QPushButton("Tạo Đợt Chấm Mới", self.empty_widget)
        btn_empty_create.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_empty_create.setFixedHeight(38)
        btn_empty_create.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {COLOR_PRIMARY};
                border-radius: 8px;
                padding: 0 20px;
                color: {COLOR_PRIMARY};
                font-weight: 600;
                font-size: 13px;
                line-height: 1.4;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_BG};
            }}
        """)
        btn_empty_create.clicked.connect(self._open_new_session_dialog)
        empty_layout.addWidget(btn_empty_create, alignment=Qt.AlignmentFlag.AlignCenter)

        self.empty_widget.setVisible(False)
        t_layout.addWidget(self.empty_widget)

        main_layout.addWidget(table_card, stretch=1)

        # 3. Chân trang: Nút Đóng (viền xanh như nút phụ khác, cách mép >= 16px)
        footer = QHBoxLayout()
        footer.setContentsMargins(0, 0, 16, 16)
        footer.addStretch(1)

        btn_close = QPushButton("Đóng", self)
        btn_close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_close.setFixedHeight(36)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {COLOR_PRIMARY};
                border-radius: 8px;
                padding: 0 24px;
                color: {COLOR_PRIMARY};
                font-weight: 600;
                font-size: 13px;
                line-height: 1.4;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_BG};
            }}
        """)
        btn_close.clicked.connect(self.reject)
        footer.addWidget(btn_close)

        main_layout.addLayout(footer)

    def _load_history_data(self):
        """Lấy dữ liệu tổng hợp lịch sử từ SQLite và nạp vào bộ nhớ."""
        self._all_history = self.db.get_grading_history_summary()

        # Cập nhật danh sách môn học vào combobox lọc
        current_course = self.cb_course_filter.currentText()
        self.cb_course_filter.blockSignals(True)
        self.cb_course_filter.clear()
        self.cb_course_filter.addItem("Tất cả môn học")

        courses = sorted({item.get("course_code", "").strip() for item in self._all_history if item.get("course_code")})
        for c in courses:
            self.cb_course_filter.addItem(c)

        idx = self.cb_course_filter.findText(current_course)
        if idx >= 0:
            self.cb_course_filter.setCurrentIndex(idx)
        else:
            self.cb_course_filter.setCurrentIndex(0)
        self.cb_course_filter.blockSignals(False)

        self._apply_filter()

    def _apply_filter(self):
        """Lọc danh sách đợt chấm theo từ khóa mã lớp và môn học được chọn."""
        search_kw = self.txt_search.text().strip().lower()
        selected_course = self.cb_course_filter.currentText()

        filtered: List[Dict[str, Any]] = []
        for item in self._all_history:
            class_name = str(item.get("class_name", "")).lower()
            course_code = str(item.get("course_code", ""))

            # Lọc từ khóa mã lớp
            if search_kw and search_kw not in class_name:
                continue

            # Lọc môn học
            if selected_course != "Tất cả môn học" and course_code != selected_course:
                continue

            filtered.append(item)

        self._render_table(filtered)

    def _render_table(self, history_list: List[Dict[str, Any]]):
        """Vẽ dữ liệu vào bảng và cập nhật dòng tổng quan hoặc hiển thị trạng thái trống."""
        # Kiểm tra trạng thái trống hoàn toàn (cả hệ thống chưa có đợt nào)
        if len(self._all_history) == 0:
            self.table.setVisible(False)
            self.empty_widget.setVisible(True)
            self.lbl_summary_bar.setText("0 đợt chấm, 0 bài nộp đã xử lý")
            return
        else:
            self.table.setVisible(True)
            self.empty_widget.setVisible(False)

        total_classes = len(history_list)
        total_graded = sum(h.get("graded_students", 0) for h in history_list)

        # Định dạng dòng tổng quan theo yêu cầu 8: "1 đợt chấm, 12 bài nộp đã xử lý"
        self.lbl_summary_bar.setText(f"{total_classes} đợt chấm, {total_graded} bài nộp đã xử lý")

        self.table.setRowCount(total_classes)

        for r, item in enumerate(history_list):
            class_id = item["id"]
            class_name = item.get("class_name", "Chưa đặt tên")
            course_code = item.get("course_code", "PRF")
            language = item.get("programming_language", "C")
            total_students = item.get("total_students", 0)
            graded_students = item.get("graded_students", 0)
            ac_count = item.get("ac_count", 0)
            avg_score = item.get("avg_score")

            # Cột 0: Mã Lớp / Đợt Chấm (căn trái)
            it_name = QTableWidgetItem(f"  {class_name}")
            it_name.setFont(QFont("Inter", 10, QFont.Weight.DemiBold))
            it_name.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(r, 0, it_name)

            # Cột 1: Môn Học (chữ trơn, căn giữa - thống nhất với Ngôn Ngữ)
            it_course = QTableWidgetItem(course_code)
            it_course.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            it_course.setFont(QFont("Inter", 10))
            self.table.setItem(r, 1, it_course)

            # Cột 2: Ngôn Ngữ (chữ trơn, căn giữa - thống nhất với Môn Học)
            it_lang = QTableWidgetItem(language)
            it_lang.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            it_lang.setFont(QFont("Inter", 10))
            self.table.setItem(r, 2, it_lang)

            # Cột 3: Số Bài Nộp (căn giữa)
            it_subs = QTableWidgetItem(f"{total_students} bài")
            it_subs.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 3, it_subs)

            # Cột 4: Tiến Độ Chấm (căn giữa)
            if graded_students == 0:
                prog_text = "Chưa chấm"
                p_bg = "#F1F5F9"
                p_fg = COLOR_TEXT_MUTED
            elif graded_students < total_students:
                prog_text = f"Đang chấm ({graded_students}/{total_students})"
                p_bg = "#FEF3C7"
                p_fg = "#D97706"
            else:
                prog_text = f"Hoàn tất ({graded_students}/{total_students})"
                p_bg = COLOR_SUCCESS_BG
                p_fg = COLOR_SUCCESS

            prog_widget = QWidget()
            prog_widget.setStyleSheet("background: transparent;")
            pw_layout = QHBoxLayout(prog_widget)
            pw_layout.setContentsMargins(0, 0, 0, 0)
            pw_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            lbl_prog = QLabel(prog_text, prog_widget)
            lbl_prog.setStyleSheet(f"""
                background-color: {p_bg};
                color: {p_fg};
                font-weight: 600;
                font-size: 11px;
                border-radius: 6px;
                padding: 4px 10px;
            """)
            pw_layout.addWidget(lbl_prog)
            self.table.setCellWidget(r, 4, prog_widget)

            # Cột 5: Tỷ Lệ Đạt (AC) (căn giữa)
            if graded_students > 0:
                rate = (ac_count / graded_students) * 100
                rate_text = f"{ac_count}/{graded_students} ({rate:.0f}%)"
            else:
                rate_text = "--"
            it_rate = QTableWidgetItem(rate_text)
            it_rate.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 5, it_rate)

            # Cột 6: Điểm Trung Bình (căn giữa)
            if avg_score is not None:
                score_text = f"{avg_score:.1f} / 10.0"
            else:
                score_text = "--"
            it_score = QTableWidgetItem(score_text)
            it_score.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            it_score.setFont(QFont("Inter", 10, QFont.Weight.Bold))
            self.table.setItem(r, 6, it_score)

            # Cột 7: Thao Tác (Nút Mở Đợt Chấm và Xóa)
            action_widget = QWidget()
            action_widget.setStyleSheet("background: transparent;")
            act_layout = QHBoxLayout(action_widget)
            act_layout.setContentsMargins(6, 0, 6, 0)
            act_layout.setSpacing(14)  # Khoảng cách giữa 2 nút >= 12px
            act_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Nút Mở Đợt Chấm: chiều cao 30px, nằm giữa dòng theo chiều dọc
            btn_open = QPushButton("Mở Đợt Chấm", action_widget)
            btn_open.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_open.setFixedHeight(30)
            btn_open.setFixedWidth(108)
            btn_open.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLOR_PRIMARY};
                    font-weight: 600;
                    font-size: 12px;
                    line-height: 1.4;
                    padding: 0 10px;
                    border: 1px solid {COLOR_PRIMARY};
                    border-radius: 6px;
                }}
                QPushButton:hover {{
                    background-color: {COLOR_PRIMARY_BG};
                }}
            """)
            btn_open.clicked.connect(lambda checked, cid=class_id: self._select_and_open_session(cid))
            act_layout.addWidget(btn_open)

            # Nút Xóa: chữ đỏ viền mảnh, chiều cao 30px, nằm giữa dòng theo chiều dọc
            btn_del = QPushButton("Xóa", action_widget)
            btn_del.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_del.setFixedHeight(30)
            btn_del.setFixedWidth(54)
            btn_del.setToolTip("Xóa đợt chấm này khỏi hệ thống")
            btn_del.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #dc2626;
                    font-weight: 500;
                    font-size: 12px;
                    line-height: 1.4;
                    padding: 0 8px;
                    border: 1px solid #fca5a5;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #fef2f2;
                    border-color: #ef4444;
                }
            """)
            btn_del.clicked.connect(
                lambda checked, cid=class_id, cname=class_name, cnt=total_students:
                self._confirm_delete_session(cid, cname, cnt)
            )
            act_layout.addWidget(btn_del)

            self.table.setCellWidget(r, 7, action_widget)

    def _select_and_open_session(self, class_id: int):
        """Mở đợt chấm được chọn và đóng hộp thoại lịch sử."""
        self.selected_class_id = class_id
        self.session_selected.emit(class_id)
        self.accept()

    def _confirm_delete_session(self, class_id: int, class_name: str, total_students: int):
        """
        Hiện hộp thoại xác nhận xóa đợt chấm với hai nút Xóa (nền đỏ) và Hủy.
        Nội dung ghi rõ tên đợt và số bài nộp sẽ bị xóa.
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Xác Nhận Xóa Đợt Chấm")
        msg_box.setText(
            f"Xóa đợt {class_name} cùng {total_students} bài nộp và toàn bộ kết quả chấm? "
            f"Thao tác này không thể hoàn tác."
        )

        btn_delete = msg_box.addButton("Xóa", QMessageBox.ButtonRole.DestructiveRole)
        btn_delete.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #dc2626;
                color: #ffffff;
                font-weight: 600;
                font-size: 13px;
                padding: 6px 18px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #b91c1c;
            }
        """)

        btn_cancel = msg_box.addButton("Hủy", QMessageBox.ButtonRole.RejectRole)
        btn_cancel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #475569;
                font-weight: 500;
                font-size: 13px;
                padding: 6px 18px;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #f8fafc;
            }
        """)

        msg_box.setDefaultButton(btn_cancel)
        msg_box.exec()

        if msg_box.clickedButton() == btn_delete:
            self.db.delete_class_session(class_id)
            self.session_deleted.emit(class_id)
            self._load_history_data()

    def _open_new_session_dialog(self):
        """Mở hộp thoại tạo đợt chấm mới."""
        from ui.dialogs.session_dialog import SessionDialog
        dlg = SessionDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._load_history_data()
