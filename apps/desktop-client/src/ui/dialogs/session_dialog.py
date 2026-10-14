"""
AITA Desktop Client - Session Creation & Directory Submissions Ingestion Dialog (PyQt6)
UC-07: Manage Classes & Grading Sessions
Folder-based Ingestion (Directory scan, regex student code extraction, duplicate detection).
Conforms 100% to clean SaaS UI without icons/emojis, line-height >= 1.4.
"""

import sys
import os
import re
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QFileDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QMessageBox
)

SRC_DIR = Path(__file__).resolve().parent.parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ui.styles.theme import (
    LIGHT_THEME_QSS, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_PRIMARY_BG,
    COLOR_BG, COLOR_SURFACE, COLOR_SURFACE_SECONDARY, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED, COLOR_BORDER_DEFAULT,
    COLOR_SUCCESS, COLOR_SUCCESS_BG, COLOR_ERROR, COLOR_ERROR_BG
)
from database.db_manager import DatabaseManager


class SessionDialog(QDialog):
    """
    Dialog for creating a new grading session and importing student submissions via directory scanning.
    """

    def __init__(self, parent=None, existing_class_id: Optional[int] = None):
        super().__init__(parent)
        self.setWindowTitle("Bước 1/3: Khởi Tạo Đợt Chấm Mới & Nạp Bài Nộp")
        self.setMinimumSize(840, 680)
        self.resize(880, 720)
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
        h_layout.setContentsMargins(18, 14, 18, 14)
        h_layout.setSpacing(4)

        lbl_title = QLabel("Khởi Tạo Đợt Chấm & Nạp Thư Mục Bài Nộp", header_card)
        lbl_title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {COLOR_TEXT_PRIMARY}; line-height: 1.4;")
        h_layout.addWidget(lbl_title)

        lbl_desc = QLabel(
            "Nhập thông tin lớp học và chọn thư mục bài làm của sinh viên. "
            "Hệ thống tự động nhận diện MSSV và họ tên từ tên thư mục con hoặc tệp nộp.",
            header_card
        )
        lbl_desc.setStyleSheet(f"font-size: 13px; color: {COLOR_TEXT_SECONDARY}; line-height: 1.4;")
        h_layout.addWidget(lbl_desc)
        layout.addWidget(header_card)

        # 2. Form Section Card
        form_card = QFrame(self)
        form_card.setProperty("class", "Card")
        f_layout = QVBoxLayout(form_card)
        f_layout.setContentsMargins(18, 16, 18, 16)
        f_layout.setSpacing(12)

        # Row 1: Tên Lớp Học & Mã Môn Học
        row1 = QHBoxLayout()
        vbox_class = QVBoxLayout()
        vbox_class.setSpacing(6)
        lbl_cname = QLabel("Tên Lớp Học:")
        lbl_cname.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {COLOR_TEXT_PRIMARY};")
        vbox_class.addWidget(lbl_cname)
        self.txt_class_name = QLineEdit(form_card)
        self.txt_class_name.setFixedHeight(38)
        self.txt_class_name.setPlaceholderText("Ví dụ: SE1801, IA1802...")
        vbox_class.addWidget(self.txt_class_name)
        row1.addLayout(vbox_class, stretch=1)

        vbox_course = QVBoxLayout()
        vbox_course.setSpacing(6)
        lbl_course = QLabel("Mã Môn Học:")
        lbl_course.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {COLOR_TEXT_PRIMARY};")
        vbox_course.addWidget(lbl_course)
        self.cb_course = QComboBox(form_card)
        self.cb_course.setFixedHeight(38)
        self.cb_course.addItems([
            "PRF - Lập trình cơ sở",
            "PRO - Lập trình hướng đối tượng",
            "DSA - Cấu trúc dữ liệu & Giải thuật",
            "PHP - Lập trình Python"
        ])
        self.cb_course.currentIndexChanged.connect(self._on_course_changed)
        vbox_course.addWidget(self.cb_course)
        row1.addLayout(vbox_course, stretch=1)
        f_layout.addLayout(row1)

        # Row 2: Ngôn Ngữ Lập Trình & Tên File Bài Nộp Chuẩn
        row2 = QHBoxLayout()
        vbox_lang = QVBoxLayout()
        vbox_lang.setSpacing(6)
        lbl_lang = QLabel("Ngôn Ngữ Lập Trình:")
        lbl_lang.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {COLOR_TEXT_PRIMARY};")
        vbox_lang.addWidget(lbl_lang)
        self.cb_language = QComboBox(form_card)
        self.cb_language.setFixedHeight(38)
        self.cb_language.currentIndexChanged.connect(self._on_language_changed)
        vbox_lang.addWidget(self.cb_language)
        row2.addLayout(vbox_lang, stretch=1)

        vbox_entry = QVBoxLayout()
        vbox_entry.setSpacing(6)
        lbl_entry = QLabel("Tên File Bài Nộp Mục Tiêu (Trong thư mục con):")
        lbl_entry.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {COLOR_TEXT_PRIMARY};")
        vbox_entry.addWidget(lbl_entry)
        self.txt_entrypoint = QLineEdit(form_card)
        self.txt_entrypoint.setFixedHeight(38)
        self.txt_entrypoint.setText("Q1.c")
        self.txt_entrypoint.textChanged.connect(self._scan_and_refresh_preview)
        vbox_entry.addWidget(self.txt_entrypoint)
        row2.addLayout(vbox_entry, stretch=1)
        f_layout.addLayout(row2)

        # Row 3: Thư Mục Chứa Bài Nộp Sinh Viên
        lbl_folder = QLabel("Thư Mục Chứa Bài Nộp Sinh Viên:")
        lbl_folder.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {COLOR_TEXT_PRIMARY};")
        f_layout.addWidget(lbl_folder)

        folder_row = QHBoxLayout()
        self.txt_folder_path = QLineEdit(form_card)
        self.txt_folder_path.setFixedHeight(38)
        self.txt_folder_path.setPlaceholderText("Chọn thư mục gốc chứa các bài làm sinh viên...")
        self.txt_folder_path.textChanged.connect(self._scan_and_refresh_preview)
        folder_row.addWidget(self.txt_folder_path, stretch=1)

        btn_browse_folder = QPushButton("Duyệt Thư Mục...", form_card)
        btn_browse_folder.setProperty("class", "SecondaryBtn")
        btn_browse_folder.setFixedHeight(38)
        btn_browse_folder.clicked.connect(self._browse_folder)
        folder_row.addWidget(btn_browse_folder)
        f_layout.addLayout(folder_row)

        lbl_folder_hint = QLabel(
            "Quy tắc nạp: Mỗi bài nộp là một thư mục con (ví dụ: SE180001, SE180001_NguyenVanA) "
            "hoặc tệp mã nguồn trực tiếp (ví dụ: SE180001.c, SE180001_NguyenVanA.c).",
            form_card
        )
        lbl_folder_hint.setStyleSheet("color: #64748B; font-size: 12px; line-height: 1.4;")
        f_layout.addWidget(lbl_folder_hint)

        layout.addWidget(form_card)

        # 3. Preview Table Card
        table_card = QFrame(self)
        table_card.setProperty("class", "Card")
        t_layout = QVBoxLayout(table_card)
        t_layout.setContentsMargins(16, 14, 16, 14)
        t_layout.setSpacing(10)

        t_header = QHBoxLayout()
        lbl_preview_title = QLabel("Xem Trước Bài Nộp Nhận Diện Được:", table_card)
        lbl_preview_title.setStyleSheet(f"font-weight: 700; font-size: 13px; color: {COLOR_TEXT_PRIMARY};")
        t_header.addWidget(lbl_preview_title)

        self.lbl_file_count = QLabel("Chưa chọn thư mục bài nộp", table_card)
        self.lbl_file_count.setStyleSheet("color: #64748B; font-weight: 600; font-size: 12px;")
        t_header.addStretch(1)
        t_header.addWidget(self.lbl_file_count)
        t_layout.addLayout(t_header)

        self.table_preview = QTableWidget(table_card)
        self.table_preview.setColumnCount(5)
        self.table_preview.setHorizontalHeaderLabels(["STT", "MSSV", "Họ và Tên", "Tệp Bài Nộp", "Trạng Thái"])
        header = self.table_preview.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
            self.table_preview.setColumnWidth(0, 50)
            self.table_preview.setColumnWidth(1, 120)
            self.table_preview.setColumnWidth(2, 170)
            self.table_preview.setColumnWidth(3, 160)

        # Khởi tạo ngôn ngữ ban đầu
        self._on_course_changed(0)

        t_layout.addWidget(self.table_preview)
        layout.addWidget(table_card, stretch=1)

        # 4. Action Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)

        btn_cancel = QPushButton("Hủy Bỏ", self)
        btn_cancel.setProperty("class", "SecondaryBtn")
        btn_cancel.setFixedHeight(38)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)

        self.btn_save = QPushButton("Tiếp Tục: Cấu Hình Môi Trường (Bước 2/3)", self)
        self.btn_save.setProperty("class", "PrimaryBtn")
        self.btn_save.setFixedHeight(38)
        self.btn_save.clicked.connect(self._save_session)
        btn_row.addWidget(self.btn_save)

        layout.addLayout(btn_row)

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
        course_text = self.cb_course.currentText()
        course_code = course_text.split(" - ")[0].strip()
        langs = self.COURSE_LANG_MAP.get(course_code, [("C (Trình biên dịch GCC - file *.c)", "Q1.c")])

        self.cb_language.blockSignals(True)
        self.cb_language.clear()
        for lang_name, _ in langs:
            self.cb_language.addItem(lang_name)
        self.cb_language.blockSignals(False)

        self._on_language_changed(0)

    def _on_language_changed(self, index: int):
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

    @staticmethod
    def parse_student_entry(name_without_ext: str) -> Tuple[Optional[str], str]:
        """
        Quy tắc tách MSSV: lấy chuỗi đầu tên thư mục/file khớp mẫu mã sinh viên (chữ + số, ví dụ SE180001).
        Phần còn lại sau dấu '_' hoặc '-' là họ tên (có thể trống).
        """
        clean_name = name_without_ext.strip()
        # Khớp định dạng: 2-4 ký tự chữ + 4-8 ký tự số (ví dụ: SE180001, QE17002, IA180003, HE19001)
        match = re.match(r"^([a-zA-Z]{2,4}\d{4,8})(?:[_-](.*))?$", clean_name)
        if match:
            mssv = match.group(1).upper()
            raw_name = match.group(2) or ""
            student_name = raw_name.replace("_", " ").strip()
            return mssv, student_name
        return None, ""

    def _scan_submissions(self) -> List[Dict[str, Any]]:
        """
        Quét thư mục bài nộp của sinh viên theo quy tắc:
        - Mỗi sinh viên là một thư mục con hoặc một file trong thư mục gốc.
        - Tách MSSV và họ tên theo mẫu regex.
        - Phát hiện và gắn cờ các mục không nhận diện được hoặc trùng MSSV.
        """
        folder_path = self.txt_folder_path.text().strip()
        entry_file = self.txt_entrypoint.text().strip() or "Q1.c"
        results: List[Dict[str, Any]] = []

        if not folder_path or not os.path.isdir(folder_path):
            return results

        lang_text = self.cb_language.currentText()
        if "*.c" in lang_text:
            valid_exts = (".c", ".cpp")
        elif "*.java" in lang_text:
            valid_exts = (".java",)
        elif "*.py" in lang_text:
            valid_exts = (".py",)
        else:
            valid_exts = (".c", ".cpp", ".java", ".py")

        try:
            entries = sorted(os.listdir(folder_path))
        except Exception:
            return results

        # 1. Quét lần lượt từng mục trong thư mục gốc
        raw_scanned: List[Dict[str, Any]] = []
        for entry in entries:
            full_p = os.path.join(folder_path, entry)

            if os.path.isdir(full_p):
                # Trường hợp 1: Thư mục con mang tên MSSV
                mssv, student_name = self.parse_student_entry(entry)
                if not mssv:
                    raw_scanned.append({
                        "raw_name": entry,
                        "mssv": entry,
                        "name": "",
                        "filepath": full_p.replace("\\", "/"),
                        "is_valid": False,
                        "reason": "Không khớp mẫu MSSV (cần bắt đầu bằng mã sinh viên, ví dụ SE180001)"
                    })
                    continue

                # Tìm file bài nộp bên trong thư mục con
                target_file = os.path.join(full_p, entry_file)
                found_file = None
                if os.path.isfile(target_file):
                    found_file = target_file
                else:
                    # Tìm file khớp không phân biệt hoa thường hoặc có phần mở rộng hợp lệ
                    for fname in os.listdir(full_p):
                        if fname.lower() == entry_file.lower():
                            found_file = os.path.join(full_p, fname)
                            break
                    if not found_file:
                        for fname in os.listdir(full_p):
                            if fname.lower().endswith(valid_exts):
                                found_file = os.path.join(full_p, fname)
                                break

                if found_file:
                    raw_scanned.append({
                        "raw_name": entry,
                        "mssv": mssv,
                        "name": student_name,
                        "filepath": found_file.replace("\\", "/"),
                        "is_valid": True,
                        "reason": "Hợp lệ"
                    })
                else:
                    raw_scanned.append({
                        "raw_name": entry,
                        "mssv": mssv,
                        "name": student_name,
                        "filepath": full_p.replace("\\", "/"),
                        "is_valid": False,
                        "reason": f"Không tìm thấy file mã nguồn ({entry_file} hoặc tệp {','.join(valid_exts)}) trong thư mục"
                    })

            elif os.path.isfile(full_p):
                # Trường hợp 2: Tệp mã nguồn trực tiếp trong thư mục gốc (ví dụ: SE180001.c, SE180001_NguyenVanA.c)
                stem, ext = os.path.splitext(entry)
                if ext.lower() in valid_exts:
                    mssv, student_name = self.parse_student_entry(stem)
                    if mssv:
                        raw_scanned.append({
                            "raw_name": entry,
                            "mssv": mssv,
                            "name": student_name,
                            "filepath": full_p.replace("\\", "/"),
                            "is_valid": True,
                            "reason": "Hợp lệ (Tệp trực tiếp)"
                        })
                    else:
                        raw_scanned.append({
                            "raw_name": entry,
                            "mssv": stem,
                            "name": "",
                            "filepath": full_p.replace("\\", "/"),
                            "is_valid": False,
                            "reason": "Tên tệp không bắt đầu bằng MSSV chuẩn"
                        })
                else:
                    # Bỏ qua tệp hệ thống ẩn hoặc tệp không liên quan (.DS_Store, thumbs.db)
                    if not entry.startswith("."):
                        raw_scanned.append({
                            "raw_name": entry,
                            "mssv": stem,
                            "name": "",
                            "filepath": full_p.replace("\\", "/"),
                            "is_valid": False,
                            "reason": f"Đuôi tệp không phù hợp với môn học ({ext})"
                        })

        # 2. Kiểm tra trùng MSSV: Cảnh báo, không im lặng ghi đè
        mssv_counts: Dict[str, int] = {}
        for item in raw_scanned:
            if item["is_valid"] and item["mssv"]:
                mssv_counts[item["mssv"]] = mssv_counts.get(item["mssv"], 0) + 1

        for item in raw_scanned:
            if item["is_valid"] and mssv_counts.get(item["mssv"], 0) > 1:
                item["is_valid"] = False
                item["reason"] = f"Trùng lặp MSSV {item['mssv']} với mục khác trong thư mục"

        return raw_scanned

    def _scan_and_refresh_preview(self):
        """Quét và làm mới bảng xem trước sinh viên với dữ liệu thực tế từ đĩa."""
        items = self._scan_submissions()
        self.table_preview.setRowCount(len(items))

        valid_count = sum(1 for it in items if it["is_valid"])
        invalid_count = len(items) - valid_count

        if not items:
            self.lbl_file_count.setText("Chưa tìm thấy bài nộp nào trong thư mục đã chọn")
            self.lbl_file_count.setStyleSheet("color: #64748B; font-weight: 600; font-size: 12px;")
        else:
            if invalid_count == 0:
                self.lbl_file_count.setText(f"Nhận diện được {valid_count} bài nộp hợp lệ")
                self.lbl_file_count.setStyleSheet("color: #16A34A; font-weight: 600; font-size: 12px;")
            else:
                self.lbl_file_count.setText(f"Nhận diện được {valid_count} bài nộp hợp lệ | {invalid_count} mục không hợp lệ")
                self.lbl_file_count.setStyleSheet("color: #DC2626; font-weight: 600; font-size: 12px;")

        for r, item in enumerate(items):
            is_valid = item["is_valid"]
            bg_color = QColor("#FFFFFF") if is_valid else QColor("#FEF2F2")
            text_color = QColor("#0F172A") if is_valid else QColor("#DC2626")

            # 0: STT
            stt_item = QTableWidgetItem(str(r + 1))
            stt_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            stt_item.setBackground(bg_color)
            stt_item.setForeground(text_color)
            self.table_preview.setItem(r, 0, stt_item)

            # 1: MSSV
            m_item = QTableWidgetItem(item["mssv"])
            m_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            m_item.setBackground(bg_color)
            m_item.setForeground(text_color)
            m_item.setFont(QFont("Inter", 10, QFont.Weight.Bold if is_valid else QFont.Weight.Normal))
            self.table_preview.setItem(r, 1, m_item)

            # 2: Họ và Tên
            name_item = QTableWidgetItem(item["name"] if item["name"] else "—")
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            name_item.setBackground(bg_color)
            name_item.setForeground(text_color)
            self.table_preview.setItem(r, 2, name_item)

            # 3: Tên file bài nộp
            fn = os.path.basename(item["filepath"])
            f_item = QTableWidgetItem(fn)
            f_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            f_item.setBackground(bg_color)
            f_item.setForeground(text_color)
            self.table_preview.setItem(r, 3, f_item)

            # 4: Trạng Thái
            status_item = QTableWidgetItem(item["reason"])
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            status_item.setBackground(bg_color)
            status_item.setForeground(QColor("#16A34A") if is_valid else QColor("#DC2626"))
            status_item.setToolTip(item["reason"])
            self.table_preview.setItem(r, 4, status_item)

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

        if not class_name:
            QMessageBox.warning(self, "Thiếu Thông Tin", "Vui lòng nhập tên lớp học!")
            return

        all_items = self._scan_submissions()
        valid_items = [it for it in all_items if it["is_valid"]]
        invalid_items = [it for it in all_items if not it["is_valid"]]

        if invalid_items:
            dup_items = [it for it in invalid_items if "Trùng lặp MSSV" in it["reason"]]
            if dup_items:
                dup_str = ", ".join(set(it["mssv"] for it in dup_items))
                QMessageBox.critical(
                    self,
                    "Phát Hiện Trùng MSSV",
                    f"Có các bài nộp bị trùng lặp MSSV trong thư mục:\n{dup_str}\n\n"
                    "Hệ thống không ghi đè tự động. Vui lòng kiểm tra lại thư mục bài nộp trước khi tiếp tục."
                )
                return

            reply = QMessageBox.question(
                self,
                "Có Mục Không Hợp Lệ",
                f"Phát hiện {len(invalid_items)} mục không nhận diện được hoặc thiếu file mã nguồn.\n"
                f"Hệ thống sẽ chỉ nạp {len(valid_items)} bài nộp hợp lệ.\n\n"
                "Bạn có muốn tiếp tục lưu đợt chấm này không?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        try:
            db = DatabaseManager()
            if self.existing_class_id:
                db.update_class_session(
                    class_id=self.existing_class_id,
                    class_name=class_name,
                    course_code=course_name,
                    programming_language=lang_name,
                    folder_path=folder_path,
                    csv_path=""
                )
                self.created_class_id = self.existing_class_id
            else:
                new_id = db.create_class_session(
                    class_name=class_name,
                    course_code=course_name,
                    programming_language=lang_name,
                    folder_path=folder_path,
                    csv_path=""
                )
                self.created_class_id = new_id

            # Nạp danh sách bài nộp hợp lệ vào SQLite
            if self.created_class_id and valid_items:
                subs_to_insert = [
                    (self.created_class_id, item["mssv"], item.get("name") or None, item["filepath"])
                    for item in valid_items
                ]
                db.bulk_insert_submissions(subs_to_insert)

            self.accept()
        except Exception as ex:
            QMessageBox.critical(self, "Lỗi Lưu CSDL", f"Không thể lưu đợt chấm vào CSDL:\n{str(ex)}")
