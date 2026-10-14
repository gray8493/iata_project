"""
AITA Desktop Client - Grading Sessions History Dialog (PyQt6)
UC-07: Manage Classes & Grading Sessions (View History & Switch Sessions)
Matches DESKTOP APP UI/UX DESIGN SYSTEM (SaaS Blue #2F80ED, Clean Cards, 52px table rows).
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCursor, QFont
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QMessageBox
)

SRC_DIR = Path(__file__).resolve().parent.parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ui.styles.theme import (
    LIGHT_THEME_QSS, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_PRIMARY_BG,
    COLOR_BG, COLOR_SURFACE, COLOR_SURFACE_SECONDARY,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_BORDER_DEFAULT, COLOR_SUCCESS, COLOR_SUCCESS_BG,
    COLOR_ERROR, COLOR_ERROR_BG, RADIUS_CARD, RADIUS_BUTTON, RADIUS_PILL
)
from database.db_manager import DatabaseManager


class HistoryDialog(QDialog):
    """
    Dialog for viewing previous grading sessions history across classes and courses.
    Allows instructors to review stats and switch the active working session.
    """

    session_selected = pyqtSignal(int)  # Emits class_id when user picks a session to open
    session_deleted = pyqtSignal(int)   # Emits class_id when a session is deleted

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Lịch Sử & Quản Lý Đợt Chấm Điểm")
        self.setMinimumSize(1080, 680)
        self.resize(1140, 720)
        self.setStyleSheet(LIGHT_THEME_QSS)

        self.db = DatabaseManager()
        self.selected_class_id: Optional[int] = None

        self._init_ui()
        self._load_history_data()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(18)

        # 1. Header Card
        header_card = QFrame(self)
        header_card.setProperty("class", "Card")
        h_layout = QHBoxLayout(header_card)
        h_layout.setContentsMargins(20, 16, 20, 16)
        h_layout.setSpacing(16)

        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        lbl_title = QLabel("Lịch Sử & Quản Lý Các Đợt Chấm Thi", header_card)
        lbl_title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {COLOR_TEXT_PRIMARY};")
        title_box.addWidget(lbl_title)

        lbl_desc = QLabel(
            "Xem lại danh sách tất cả các đợt chấm theo từng lớp và môn học (PRF, PRO, DSA, PHP). "
            "Nhấp [Mở Đợt Chấm] để tải phiên làm việc lên màn hình chính.",
            header_card
        )
        lbl_desc.setStyleSheet(f"font-size: 13px; color: {COLOR_TEXT_SECONDARY};")
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

        # 2. History Table Card
        table_card = QFrame(self)
        table_card.setProperty("class", "Card")
        t_layout = QVBoxLayout(table_card)
        t_layout.setContentsMargins(18, 16, 18, 16)
        t_layout.setSpacing(12)

        # Stats bar inside card
        self.lbl_summary_bar = QLabel("Đang tải dữ liệu lịch sử...", table_card)
        self.lbl_summary_bar.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {COLOR_TEXT_SECONDARY};")
        t_layout.addWidget(self.lbl_summary_bar)

        # Table
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

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 90)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 100)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 100)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(4, 160)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(5, 130)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(6, 130)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(7, 210)

        t_layout.addWidget(self.table)
        main_layout.addWidget(table_card, stretch=1)

        # 3. Footer Bar
        footer = QHBoxLayout()
        footer.addStretch(1)

        btn_close = QPushButton("Đóng", self)
        btn_close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_close.setFixedHeight(36)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_SURFACE};
                border: 1px solid {COLOR_BORDER_DEFAULT};
                border-radius: 8px;
                padding: 0 20px;
                color: {COLOR_TEXT_PRIMARY};
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_SURFACE_SECONDARY};
                color: {COLOR_PRIMARY};
            }}
        """)
        btn_close.clicked.connect(self.reject)
        footer.addWidget(btn_close)

        main_layout.addLayout(footer)

    def _load_history_data(self):
        """Fetches grading history summary from SQLite and populates the table."""
        history = self.db.get_grading_history_summary()
        self.table.setRowCount(len(history))

        total_classes = len(history)
        total_graded = sum(h.get("graded_students", 0) for h in history)
        self.lbl_summary_bar.setText(f"Tổng cộng: {total_classes} đợt chấm bài | Đã xử lý {total_graded} bài nộp của sinh viên")

        for r, item in enumerate(history):
            class_id = item["id"]
            class_name = item.get("class_name", "Chưa đặt tên")
            course_code = item.get("course_code", "PRF")
            language = item.get("programming_language", "C")
            total_students = item.get("total_students", 0)
            graded_students = item.get("graded_students", 0)
            ac_count = item.get("ac_count", 0)
            avg_score = item.get("avg_score")

            # Col 0: Class Name
            it_name = QTableWidgetItem(f"  {class_name}")
            it_name.setFont(QFont("Inter", 10, QFont.Weight.DemiBold))
            it_name.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(r, 0, it_name)

            # Col 1: Course Code Badge
            course_widget = QWidget()
            course_widget.setStyleSheet("background: transparent;")
            cw_layout = QHBoxLayout(course_widget)
            cw_layout.setContentsMargins(0, 0, 0, 0)
            cw_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_course = QLabel(course_code, course_widget)
            lbl_course.setStyleSheet(f"""
                background-color: {COLOR_PRIMARY_BG};
                color: {COLOR_PRIMARY};
                font-weight: 700;
                font-size: 11px;
                border-radius: 6px;
                padding: 4px 10px;
            """)
            cw_layout.addWidget(lbl_course)
            self.table.setCellWidget(r, 1, course_widget)

            # Col 2: Language
            it_lang = QTableWidgetItem(language)
            it_lang.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 2, it_lang)

            # Col 3: Submissions count
            it_subs = QTableWidgetItem(f"{total_students} bài")
            it_subs.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 3, it_subs)

            # Col 4: Progress / Status Badge
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

            # Col 5: AC Rate
            if graded_students > 0:
                rate = (ac_count / graded_students) * 100
                rate_text = f"{ac_count}/{graded_students} ({rate:.0f}%)"
            else:
                rate_text = "--"
            it_rate = QTableWidgetItem(rate_text)
            it_rate.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 5, it_rate)

            # Col 6: Average Score
            if avg_score is not None:
                score_text = f"{avg_score:.1f} / 10.0"
            else:
                score_text = "--"
            it_score = QTableWidgetItem(score_text)
            it_score.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            it_score.setFont(QFont("Inter", 10, QFont.Weight.Bold))
            self.table.setItem(r, 6, it_score)

            # Col 7: Actions (Open & Delete)
            action_widget = QWidget()
            action_widget.setStyleSheet("background: transparent;")
            act_layout = QHBoxLayout(action_widget)
            act_layout.setContentsMargins(4, 4, 4, 4)
            act_layout.setSpacing(8)
            act_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            btn_open = QPushButton("Mở Đợt Chấm", action_widget)
            btn_open.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_open.setFixedHeight(32)
            btn_open.setFixedWidth(112)
            btn_open.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_PRIMARY_BG};
                    color: {COLOR_PRIMARY};
                    font-weight: 600;
                    font-size: 12px;
                    padding: 0 8px;
                    border: 1px solid {COLOR_PRIMARY};
                    border-radius: 6px;
                }}
                QPushButton:hover {{
                    background-color: {COLOR_PRIMARY};
                    color: #FFFFFF;
                }}
            """)
            btn_open.clicked.connect(lambda checked, cid=class_id: self._select_and_open_session(cid))
            act_layout.addWidget(btn_open)

            btn_del = QPushButton("Xóa", action_widget)
            btn_del.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_del.setFixedHeight(32)
            btn_del.setFixedWidth(54)
            btn_del.setToolTip("Xóa đợt chấm này khỏi hệ thống")
            btn_del.setStyleSheet("""
                QPushButton {
                    background-color: #FEF2F2;
                    color: #EF4444;
                    font-weight: 600;
                    font-size: 12px;
                    padding: 0 4px;
                    border: 1px solid #FCA5A5;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #EF4444;
                    color: #FFFFFF;
                }
            """)
            btn_del.clicked.connect(lambda checked, cid=class_id, cname=class_name: self._confirm_delete_session(cid, cname))
            act_layout.addWidget(btn_del)

            self.table.setCellWidget(r, 7, action_widget)

    def _select_and_open_session(self, class_id: int):
        """Handles opening the selected session and closes the history dialog."""
        self.selected_class_id = class_id
        self.session_selected.emit(class_id)
        self.accept()

    def _confirm_delete_session(self, class_id: int, class_name: str):
        """Asks for user confirmation before deleting a session from SQLite."""
        reply = QMessageBox.question(
            self,
            "Xác Nhận Xóa Đợt Chấm",
            f"Bạn có chắc chắn muốn xóa đợt chấm: '{class_name}'?\n\n"
            f"Hành động này sẽ xóa toàn bộ bài nộp và kết quả chấm của lớp này khỏi SQLite.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_class_session(class_id)
            self.session_deleted.emit(class_id)
            self._load_history_data()
            QMessageBox.information(self, "Đã Xóa", f"Đã xóa đợt chấm '{class_name}' thành công!")

    def _open_new_session_dialog(self):
        """Opens the standard session creation dialog."""
        from ui.dialogs.session_dialog import SessionDialog
        dlg = SessionDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._load_history_data()
