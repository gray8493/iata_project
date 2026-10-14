"""
AITA Desktop Client - Session & Student CSV Import Dialog (PyQt6)
UC-07: Manage Classes & Grading Sessions
UC-08: Import Submissions via students.csv
"""

import sys
import os
import csv
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QFileDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QMessageBox
)

SRC_DIR = Path(__file__).resolve().parent.parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ui.styles.theme import LIGHT_THEME_QSS
from database.db_manager import DatabaseManager



class SessionDialog(QDialog):
    """
    Dialog for creating a new grading session and importing students.csv.
    """

    def __init__(self, parent=None, existing_class_id: Optional[int] = None):
        super().__init__(parent)
        self.setWindowTitle("Bước 1/3: Khởi Tạo Đợt Chấm Mới & Nạp Bài Nộp")
        self.setFixedSize(780, 640)
        self.setStyleSheet(LIGHT_THEME_QSS)
        self.existing_class_id = existing_class_id
        self.created_class_id = existing_class_id
        self._init_ui()
        if self.existing_class_id:
            self._load_existing_session_data()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # 1. Header Card
        header_card = QFrame(self)
        header_card.setProperty("class", "Card")
        h_layout = QVBoxLayout(header_card)
        h_layout.setContentsMargins(16, 12, 16, 12)
        
        lbl_title = QLabel("Khởi Tạo Đợt Chấm & Nạp Bài Nộp", header_card)
        lbl_title.setProperty("class", "Heading1")
        h_layout.addWidget(lbl_title)
        
        lbl_desc = QLabel("Nhập thông tin lớp học, chọn thư mục bài nộp và nạp file students.csv chuẩn 2 cột (MSSV, File).", header_card)
        lbl_desc.setProperty("class", "SubText")
        h_layout.addWidget(lbl_desc)
        layout.addWidget(header_card)
        
        # 2. Form Section Card
        form_card = QFrame(self)
        form_card.setProperty("class", "Card")
        f_layout = QVBoxLayout(form_card)
        f_layout.setContentsMargins(18, 16, 18, 16)
        f_layout.setSpacing(12)
        
        # Row 1: Class Name & Course Code (Chỉ đúng 4 môn theo docs: PRF, PRO, DSA, PHP)
        row1 = QHBoxLayout()
        vbox_class = QVBoxLayout()
        vbox_class.addWidget(QLabel("Tên Lớp Học:"))
        self.txt_class_name = QLineEdit(form_card)
        self.txt_class_name.setPlaceholderText("VD: SE1801, IA1802...")
        vbox_class.addWidget(self.txt_class_name)
        row1.addLayout(vbox_class)
        
        vbox_course = QVBoxLayout()
        vbox_course.addWidget(QLabel("Mã Môn Học (Theo Docs):"))
        self.cb_course = QComboBox(form_card)
        self.cb_course.addItems([
            "PRF - Lập trình cơ sở",
            "PRO - Lập trình hướng đối tượng",
            "DSA - Cấu trúc dữ liệu & Giải thuật",
            "PHP - Lập trình Python"
        ])
        self.cb_course.currentIndexChanged.connect(self._on_course_changed)
        vbox_course.addWidget(self.cb_course)
        row1.addLayout(vbox_course)
        f_layout.addLayout(row1)

        # Row 2: Programming Language & Entrypoint Filename
        row2 = QHBoxLayout()
        vbox_lang = QVBoxLayout()
        vbox_lang.addWidget(QLabel("Ngôn Ngữ Lập Trình:"))
        self.cb_language = QComboBox(form_card)
        self.cb_language.currentIndexChanged.connect(self._on_language_changed)
        vbox_lang.addWidget(self.cb_language)
        row2.addLayout(vbox_lang)

        vbox_entry = QVBoxLayout()
        vbox_entry.addWidget(QLabel("Tên File Bài Nộp Chuẩn:"))
        self.txt_entrypoint = QLineEdit(form_card)
        self.txt_entrypoint.setText("Q1.c")
        self.txt_entrypoint.textChanged.connect(self._scan_and_refresh_preview)
        vbox_entry.addWidget(self.txt_entrypoint)
        row2.addLayout(vbox_entry)
        f_layout.addLayout(row2)
        
        # Root Folder Selector Row
        f_layout.addWidget(QLabel("Thư Mục Chứa Bài Nộp Sinh Viên (Mỗi thư mục con là 1 MSSV):"))
        folder_row = QHBoxLayout()
        self.txt_folder_path = QLineEdit(form_card)
        self.txt_folder_path.setPlaceholderText("Chọn thư mục chứa bài nộp sinh viên (VD: D:/PRF192_Submissions)...")
        self.txt_folder_path.textChanged.connect(self._scan_and_refresh_preview)
        folder_row.addWidget(self.txt_folder_path)
        
        btn_browse_folder = QPushButton("Duyệt Thư Mục...", form_card)
        btn_browse_folder.setProperty("class", "SecondaryBtn")
        btn_browse_folder.clicked.connect(self._browse_folder)
        folder_row.addWidget(btn_browse_folder)
        f_layout.addLayout(folder_row)
        
        lbl_folder_hint = QLabel("Hệ thống sẽ tự động quét các thư mục con (VD: SE180001, SE180002...) để lấy bài nộp chấm điểm.", form_card)
        lbl_folder_hint.setStyleSheet("color: #64748B; font-size: 11px;")
        f_layout.addWidget(lbl_folder_hint)
        
        layout.addWidget(form_card)
        
        # 3. Preview Table Card
        table_card = QFrame(self)
        table_card.setProperty("class", "Card")
        t_layout = QVBoxLayout(table_card)
        t_layout.setContentsMargins(14, 12, 14, 12)
        
        t_header = QHBoxLayout()
        lbl_preview_title = QLabel("Xem Trước Dữ Liệu Sinh Viên & Kiểm Tra Đĩa (Preview):", table_card)
        lbl_preview_title.setStyleSheet("font-weight: 700; font-size: 12px;")
        t_header.addWidget(lbl_preview_title)
        
        self.lbl_file_count = QLabel("Chưa chọn bài nộp", table_card)
        self.lbl_file_count.setStyleSheet("color: #475569; font-weight: 600; font-size: 11px;")
        t_header.addStretch(1)
        t_header.addWidget(self.lbl_file_count)
        t_layout.addLayout(t_header)
        
        self.table_preview = QTableWidget(table_card)
        self.table_preview.setColumnCount(4)
        self.table_preview.setHorizontalHeaderLabels(["STT", "MSSV", "Tên File Bài Nộp", "Kiểm Tra Đĩa"])
        self.table_preview.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Cập nhật danh sách ngôn ngữ và preview ban đầu cho PRF
        self._on_course_changed(0)
                
        t_layout.addWidget(self.table_preview)
        layout.addWidget(table_card, stretch=1)
        
        # 4. Action Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        
        btn_cancel = QPushButton("Hủy Bỏ", self)
        btn_cancel.setProperty("class", "SecondaryBtn")
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)
        
        btn_save = QPushButton("Tiếp Tục: Cấu Hình Môi Trường (Bước 2/3)", self)
        btn_save.setProperty("class", "PrimaryBtn")
        btn_save.clicked.connect(self._save_session)
        btn_row.addWidget(btn_save)
        
        layout.addLayout(btn_row)

    # Định nghĩa chính xác 4 môn học và ngôn ngữ hỗ trợ theo tài liệu đặc tả (Docs)
    COURSE_LANG_MAP = {
        "PRF": [
            ("C (Trình biên dịch GCC - file *.c)", "Q1.c")
        ],
        "PRO": [
            ("Java (Trình biên dịch OpenJDK - file *.java)", "Q1.java"),
            ("Python (Python 3.x Runtime - file *.py)", "q1.py")
        ],
        "DSA": [
            ("Java (Trình biên dịch OpenJDK - file *.java)", "Q1.java"),
            ("Python (Python 3.x Runtime - file *.py)", "q1.py")
        ],
        "PHP": [
            ("Python (Python 3.x Runtime - file *.py)", "q1.py")
        ]
    }

    def _on_course_changed(self, index: int):
        """Populates valid programming languages for the selected core course based on docs."""
        course_text = self.cb_course.currentText()
        course_code = course_text.split(" - ")[0].strip()
        
        langs = self.COURSE_LANG_MAP.get(course_code, [("C (Trình biên dịch GCC - file *.c)", "Q1.c")])
        
        self.cb_language.blockSignals(True)
        self.cb_language.clear()
        for lang_name, _ in langs:
            self.cb_language.addItem(lang_name)
        self.cb_language.blockSignals(False)
        
        # Cập nhật ngôn ngữ và file bài nộp đầu tiên
        self._on_language_changed(0)

    def _on_language_changed(self, index: int):
        """Updates the default entrypoint file name and preview table when language changes."""
        lang_text = self.cb_language.currentText()
        if "*.c" in lang_text or "GCC" in lang_text:
            default_file = "Q1.c"
        elif "*.java" in lang_text or "OpenJDK" in lang_text:
            default_file = "Q1.java"
        elif "*.py" in lang_text or "Python" in lang_text:
            default_file = "q1.py"
        else:
            default_file = "Q1.c"
            
        self.txt_entrypoint.setText(default_file)
        self._scan_and_refresh_preview()

    def _scan_submissions(self) -> List[Dict[str, Any]]:
        """
        Quét dữ liệu bài nộp thật:
        Duyệt qua tất cả các thư mục con trong folder_path (mỗi thư mục con là 1 MSSV).
        """
        folder_path = self.txt_folder_path.text().strip()
        entry_file = self.txt_entrypoint.text().strip() or "Q1.c"
        results: List[Dict[str, Any]] = []

        if folder_path and os.path.isdir(folder_path):
            try:
                for entry in sorted(os.listdir(folder_path)):
                    full_p = os.path.join(folder_path, entry)
                    if os.path.isdir(full_p):
                        mssv = entry
                        target_file = os.path.join(full_p, entry_file)
                        exists = False
                        if os.path.isfile(target_file):
                            exists = True
                        else:
                            for fname in os.listdir(full_p):
                                if fname.lower() == entry_file.lower():
                                    target_file = os.path.join(full_p, fname)
                                    exists = True
                                    break
                        results.append({
                            "mssv": mssv,
                            "name": "",
                            "filepath": target_file.replace("\\", "/"),
                            "exists": exists
                        })
            except Exception:
                pass

        return results

    def _scan_and_refresh_preview(self):
        """Quét và làm mới bảng xem trước sinh viên với dữ liệu thực tế từ đĩa."""
        entry_file = self.txt_entrypoint.text().strip() or "Q1.c"
        items = self._scan_submissions()
        
        self.table_preview.setRowCount(len(items))
        valid_count = sum(1 for it in items if it["exists"])
        missing_count = len(items) - valid_count
        
        if not items:
            self.lbl_file_count.setText("Chưa tìm thấy bài nộp nào (Hãy chọn thư mục chứa bài nộp sinh viên)")
            self.lbl_file_count.setStyleSheet("color: #64748B; font-weight: 600; font-size: 11px;")
        else:
            self.lbl_file_count.setText(f"{valid_count} sinh viên hợp lệ | {missing_count} chưa có file")
            color_style = "#16a34a" if missing_count == 0 else "#D97706"
            self.lbl_file_count.setStyleSheet(f"color: {color_style}; font-weight: 600; font-size: 11px;")
            
        for r, item in enumerate(items):
            stt_item = QTableWidgetItem(str(r + 1))
            stt_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_preview.setItem(r, 0, stt_item)
            
            label_mssv = item["mssv"]
            m_item = QTableWidgetItem(label_mssv)
            m_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table_preview.setItem(r, 1, m_item)
            
            fn = os.path.basename(item["filepath"]) or entry_file
            f_item = QTableWidgetItem(fn)
            f_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_preview.setItem(r, 2, f_item)
            
            if item["exists"]:
                status_item = QTableWidgetItem("✅ Tồn tại trên đĩa")
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            else:
                status_item = QTableWidgetItem("⚠️ Chưa có file")
                status_item.setForeground(Qt.GlobalColor.darkRed)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_preview.setItem(r, 3, status_item)

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Chọn Thư Mục Chứa Bài Nộp")
        if folder:
            self.txt_folder_path.setText(folder)
            self._scan_and_refresh_preview()

    def _load_existing_session_data(self):
        """Pre-populates form with previously entered session info when going back from step 2."""
        try:
            db = DatabaseManager()
            c = db.get_class_by_id(self.existing_class_id)
            if c:
                self.txt_class_name.setText(c.get("class_name", ""))
                self.txt_folder_path.setText(c.get("session_folder_path", ""))
                
                c_code = c.get("course_code", "")
                for idx in range(self.cb_course.count()):
                    if self.cb_course.itemText(idx).startswith(c_code):
                        self.cb_course.setCurrentIndex(idx)
                        break
                self._scan_and_refresh_preview()
        except Exception:
            pass

    def _save_session(self):
        class_name = self.txt_class_name.text().strip()
        course_name = self.cb_course.currentText().split(" - ")[0].strip()
        lang_name = self.cb_language.currentText().split(" (")[0].strip()
        folder_path = self.txt_folder_path.text().strip()
        entry_file = self.txt_entrypoint.text().strip()

        if not class_name:
            QMessageBox.warning(self, "Thiếu Thông Tin", "Vui lòng nhập tên lớp học!")
            return

        try:
            db = DatabaseManager()
            if self.existing_class_id:
                # Cập nhật đợt chấm hiện tại nếu quay lại bước 1
                db.update_class_session(
                    class_id=self.existing_class_id,
                    class_name=class_name,
                    course_code=course_name,
                    programming_language=lang_name,
                    folder_path=folder_path,
                    csv_path=""
                )
                self.created_class_id = self.existing_class_id
                self.accept()
                return

            new_id = db.create_class_session(
                class_name=class_name,
                course_code=course_name,
                programming_language=lang_name,
                folder_path=folder_path,
                csv_path=""
            )

            # HOÀN TOÀN KHÔNG TỰ SINH TESTCASE MẪU - ĐỂ BƯỚC 3 GIẢNG VIÊN TỰ CẤU HÌNH

            # Quét và lưu bài nộp thực tế từ đĩa / CSV
            real_items = self._scan_submissions()
            if real_items:
                subs_to_insert = [
                    (new_id, item["mssv"], item.get("name") or None, item["filepath"])
                    for item in real_items
                ]
                db.bulk_insert_submissions(subs_to_insert)

            self.created_class_id = new_id
            self.accept()
        except Exception as ex:
            QMessageBox.critical(self, "Lỗi Lưu CSDL", f"Không thể lưu đợt chấm vào CSDL:\n{str(ex)}")
