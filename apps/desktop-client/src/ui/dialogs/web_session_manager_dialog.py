"""
AITA Desktop Client - Web Grading Session Management Dialog (PyQt6)
UC: Manage Web Grading Sessions / Batches
Allows instructors to create, switch, and delete web grading sessions.
Conforms 100% to clean SaaS UI without icons/emojis, line-height >= 1.4.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QFont, QColor
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QMessageBox, QFormLayout, QAbstractItemView
)

SRC_DIR = Path(__file__).resolve().parent.parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ui.styles.theme import (
    LIGHT_THEME_QSS, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_PRIMARY_BG,
    COLOR_PRIMARY_LIGHT, COLOR_BG, COLOR_SURFACE, COLOR_SURFACE_SECONDARY,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_BORDER_DEFAULT, COLOR_BORDER_LIGHT, COLOR_SUCCESS, COLOR_SUCCESS_BG,
    COLOR_ERROR, COLOR_ERROR_BG, RADIUS_CARD, RADIUS_BUTTON
)
from database.db_manager import DatabaseManager


class WebSessionManagerDialog(QDialog):
    """Modal dialog for creating, choosing, and managing web grading sessions."""

    def __init__(self, current_session_id: Optional[int] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Quản Lý Phiên Chấm Bài Web")
        self.setMinimumSize(860, 600)
        self.resize(920, 640)
        self.setStyleSheet(LIGHT_THEME_QSS)

        self.db = DatabaseManager()
        self.current_session_id = current_session_id
        self.selected_session_id: Optional[int] = current_session_id
        self.selected_session_name: str = ""
        self.selected_course_code: str = "WEB201c"
        self.selected_class_name: str = "SE1806"

        self._sessions: List[Dict[str, Any]] = []
        self._init_ui()
        self._load_sessions()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(18)

        # 1. Header Card
        header = QFrame(self)
        header.setProperty("class", "Card")
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(18, 14, 18, 14)
        h_layout.setSpacing(4)

        lbl_title = QLabel("Danh Sách Phiên Chấm Đồ Án Web", header)
        lbl_title.setStyleSheet(f"font-size: 17px; font-weight: 700; color: {COLOR_TEXT_PRIMARY};")
        lbl_sub = QLabel(
            "Mỗi phiên là một đợt chấm riêng biệt độc lập. Bạn có thể chọn phiên để tiếp tục chấm hoặc tạo phiên mới.",
            header
        )
        lbl_sub.setStyleSheet(f"font-size: 13px; color: {COLOR_TEXT_SECONDARY}; line-height: 1.4;")

        h_layout.addWidget(lbl_title)
        h_layout.addWidget(lbl_sub)
        main_layout.addWidget(header)

        # 2. Form Tạo Phiên Mới
        create_card = QFrame(self)
        create_card.setProperty("class", "Card")
        cc_layout = QVBoxLayout(create_card)
        cc_layout.setContentsMargins(18, 14, 18, 14)
        cc_layout.setSpacing(10)

        lbl_create_title = QLabel("Tạo Phiên Chấm Mới:", create_card)
        lbl_create_title.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {COLOR_TEXT_PRIMARY};")
        cc_layout.addWidget(lbl_create_title)

        form_layout = QHBoxLayout()
        form_layout.setSpacing(12)

        v_name = QVBoxLayout()
        v_name.setSpacing(4)
        lbl_fn = QLabel("Tên Phiên Chấm (*):", create_card)
        lbl_fn.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {COLOR_TEXT_PRIMARY};")
        self.ed_session_name = QLineEdit(create_card)
        self.ed_session_name.setPlaceholderText("Ví dụ: Bài Tập Cuối Kỳ - Nhóm 1")
        self.ed_session_name.setFixedHeight(36)
        v_name.addWidget(lbl_fn)
        v_name.addWidget(self.ed_session_name)
        form_layout.addLayout(v_name, stretch=3)

        v_course = QVBoxLayout()
        v_course.setSpacing(4)
        lbl_fc = QLabel("Mã Môn Học:", create_card)
        lbl_fc.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {COLOR_TEXT_PRIMARY};")
        self.ed_course_code = QLineEdit("WEB201c", create_card)
        self.ed_course_code.setPlaceholderText("WEB201c")
        self.ed_course_code.setFixedHeight(36)
        v_course.addWidget(lbl_fc)
        v_course.addWidget(self.ed_course_code)
        form_layout.addLayout(v_course, stretch=2)

        v_class = QVBoxLayout()
        v_class.setSpacing(4)
        lbl_fcl = QLabel("Lớp Học:", create_card)
        lbl_fcl.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {COLOR_TEXT_PRIMARY};")
        self.ed_class_name = QLineEdit("SE1806", create_card)
        self.ed_class_name.setPlaceholderText("SE1806")
        self.ed_class_name.setFixedHeight(36)
        v_class.addWidget(lbl_fcl)
        v_class.addWidget(self.ed_class_name)
        form_layout.addLayout(v_class, stretch=2)

        v_btn = QVBoxLayout()
        v_btn.setSpacing(4)
        lbl_dummy = QLabel("", create_card)
        lbl_dummy.setFixedHeight(16)
        btn_create = QPushButton("Tạo Phiên Mới", create_card)
        btn_create.setProperty("class", "PrimaryBtn")
        btn_create.setFixedHeight(36)
        btn_create.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_create.clicked.connect(self._create_new_session)
        v_btn.addWidget(lbl_dummy)
        v_btn.addWidget(btn_create)
        form_layout.addLayout(v_btn, stretch=2)

        cc_layout.addLayout(form_layout)
        main_layout.addWidget(create_card)

        # 3. Bảng Danh Sách Phiên
        table_card = QFrame(self)
        table_card.setProperty("class", "Card")
        tc_layout = QVBoxLayout(table_card)
        tc_layout.setContentsMargins(18, 14, 18, 14)
        tc_layout.setSpacing(10)

        lbl_tbl_title = QLabel("Các Phiên Hiện Có:", table_card)
        lbl_tbl_title.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {COLOR_TEXT_PRIMARY};")
        tc_layout.addWidget(lbl_tbl_title)

        self.table_sessions = QTableWidget(table_card)
        self.table_sessions.setColumnCount(7)
        self.table_sessions.setHorizontalHeaderLabels([
            "ID", "Tên Phiên Chấm", "Mã Môn", "Lớp", "Số Bài Nộp", "Ngày Tạo", "Thao Tác"
        ])
        self.table_sessions.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_sessions.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_sessions.setShowGrid(False)
        self.table_sessions.verticalHeader().setVisible(False)
        self.table_sessions.verticalHeader().setDefaultSectionSize(48)
        self.table_sessions.itemDoubleClicked.connect(self._on_table_double_clicked)

        header = self.table_sessions.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)

        self.table_sessions.setColumnWidth(0, 50)
        self.table_sessions.setColumnWidth(2, 110)
        self.table_sessions.setColumnWidth(3, 110)
        self.table_sessions.setColumnWidth(4, 90)
        self.table_sessions.setColumnWidth(5, 140)
        self.table_sessions.setColumnWidth(6, 170)

        tc_layout.addWidget(self.table_sessions)
        main_layout.addWidget(table_card, stretch=1)

        # 4. Footer
        footer = QHBoxLayout()
        footer.addStretch(1)

        btn_close = QPushButton("Đóng", self)
        btn_close.setProperty("class", "SecondaryBtn")
        btn_close.setFixedHeight(36)
        btn_close.setFixedWidth(100)
        btn_close.clicked.connect(self.reject)
        footer.addWidget(btn_close)

        main_layout.addLayout(footer)

    def _load_sessions(self):
        """Fetches and renders all active web sessions from SQLite."""
        try:
            self._sessions = self.db.get_all_web_sessions()
        except Exception as ex:
            self._sessions = []
            QMessageBox.critical(self, "Lỗi Tải Dữ Liệu", f"Không thể tải danh sách phiên:\n{str(ex)}")

        self.table_sessions.setRowCount(len(self._sessions))

        for row, s in enumerate(self._sessions):
            self.table_sessions.setRowHeight(row, 48)
            s_id = s.get("id")
            s_name = s.get("session_name", "")
            course = s.get("course_code", "")
            klass = s.get("class_name", "")
            count = s.get("total_submissions", 0)
            created_at = str(s.get("created_at") or "")[:16]

            is_active = (s_id == self.current_session_id)

            # Col 0: ID
            it_id = QTableWidgetItem(str(s_id))
            it_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_sessions.setItem(row, 0, it_id)

            # Col 1: Name
            name_display = f"{s_name} (Đang mở)" if is_active else s_name
            it_name = QTableWidgetItem(name_display)
            it_name.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            if is_active:
                it_name.setForeground(QColor(COLOR_PRIMARY))
                it_name.setFont(QFont("Inter", 10, QFont.Weight.Bold))
            self.table_sessions.setItem(row, 1, it_name)

            # Col 2: Course
            it_course = QTableWidgetItem(course)
            it_course.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_sessions.setItem(row, 2, it_course)

            # Col 3: Class
            it_class = QTableWidgetItem(klass)
            it_class.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_sessions.setItem(row, 3, it_class)

            # Col 4: Submissions count
            it_count = QTableWidgetItem(str(count))
            it_count.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            it_count.setFont(QFont("Inter", 9, QFont.Weight.Bold))
            self.table_sessions.setItem(row, 4, it_count)

            # Col 5: Created at
            it_time = QTableWidgetItem(created_at)
            it_time.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_sessions.setItem(row, 5, it_time)

            # Col 6: Actions (Chọn / Xóa)
            btn_choose = QPushButton("Chọn Phiên" if not is_active else "Đang Mở")
            btn_choose.setFixedHeight(28)
            btn_choose.setFixedWidth(82)
            btn_choose.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            if is_active:
                btn_choose.setEnabled(False)
                btn_choose.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLOR_PRIMARY_BG};
                        color: {COLOR_PRIMARY};
                        border: 1px solid {COLOR_PRIMARY_LIGHT};
                        border-radius: 6px;
                        font-size: 11px;
                        font-weight: 600;
                    }}
                """)
            else:
                btn_choose.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLOR_PRIMARY};
                        color: #FFFFFF;
                        border: none;
                        border-radius: 6px;
                        font-size: 11px;
                        font-weight: 600;
                    }}
                    QPushButton:hover {{
                        background-color: {COLOR_PRIMARY_HOVER};
                    }}
                """)
                btn_choose.clicked.connect(lambda _, item=s: self._select_session(item))

            btn_del = QPushButton("Xóa")
            btn_del.setFixedHeight(28)
            btn_del.setFixedWidth(54)
            btn_del.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_del.setStyleSheet(f"""
                QPushButton {{
                    background-color: #FFFFFF;
                    color: {COLOR_ERROR};
                    border: 1px solid {COLOR_ERROR}55;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: {COLOR_ERROR_BG};
                    border-color: {COLOR_ERROR};
                }}
            """)
            btn_del.clicked.connect(lambda _, item=s: self._delete_session(item))

            cell_widget = QWidget(self.table_sessions)
            cell_widget.setStyleSheet("background: transparent;")
            cell_layout = QHBoxLayout(cell_widget)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            cell_layout.setSpacing(6)
            cell_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cell_layout.addWidget(btn_choose)
            cell_layout.addWidget(btn_del)
            self.table_sessions.setCellWidget(row, 6, cell_widget)

    def _create_new_session(self):
        """Creates a new web session in SQLite and immediately activates it."""
        name = self.ed_session_name.text().strip()
        course = self.ed_course_code.text().strip() or "WEB201c"
        klass = self.ed_class_name.text().strip() or "SE1806"

        if not name:
            QMessageBox.warning(self, "Thiếu Thông Tin", "Vui lòng nhập Tên Phiên Chấm.")
            self.ed_session_name.setFocus()
            return

        try:
            new_id = self.db.create_web_session(name, course, klass)
            self.selected_session_id = new_id
            self.selected_session_name = name
            self.selected_course_code = course
            self.selected_class_name = klass
            self.accept()
        except Exception as ex:
            QMessageBox.critical(self, "Lỗi Tạo Phiên", f"Không thể tạo phiên mới:\n{str(ex)}")

    def _select_session(self, session_dict: Dict[str, Any]):
        """Selects a session and closes the dialog with Accepted code."""
        self.selected_session_id = session_dict.get("id")
        self.selected_session_name = session_dict.get("session_name", "")
        self.selected_course_code = session_dict.get("course_code", "WEB201c")
        self.selected_class_name = session_dict.get("class_name", "SE1806")
        self.accept()

    def _on_table_double_clicked(self, item: QTableWidgetItem):
        row = item.row()
        if 0 <= row < len(self._sessions):
            self._select_session(self._sessions[row])

    def _delete_session(self, session_dict: Dict[str, Any]):
        """Soft-deletes a session and prompts the instructor for confirmation."""
        s_id = session_dict.get("id")
        s_name = session_dict.get("session_name", "")
        count = session_dict.get("total_submissions", 0)

        ret = QMessageBox.question(
            self, "Xác Nhận Xóa Phiên",
            f"Bạn có chắc chắn muốn xóa phiên '{s_name}'?\n\n"
            f"Lưu ý: Toàn bộ {count} bài nộp thuộc phiên này sẽ bị xóa khỏi hệ thống.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if ret == QMessageBox.StandardButton.Yes and s_id:
            try:
                self.db.delete_web_session(s_id)
                if self.selected_session_id == s_id:
                    self.selected_session_id = None
                self._load_sessions()
            except Exception as ex:
                QMessageBox.critical(self, "Lỗi Xóa Phiên", f"Không thể xóa phiên:\n{str(ex)}")
