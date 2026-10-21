"""
AITA Desktop Client - Testcase Manager & AI Generator Dialog (PyQt6)
UC-09: Manage Black-box Testcases Manually (Add / Edit / Delete Input/Output)
UC-10: Auto-Generate Boundary Testcases with AI Hub
UC-11: Configure 7 Output Matching Strategies
"""

import sys
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QCursor, QGuiApplication, QFont
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QCheckBox, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QTextEdit, QSpinBox, QDoubleSpinBox, QTabWidget, QMessageBox, QFileDialog
)

SRC_DIR = Path(__file__).resolve().parent.parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ui.styles.theme import (
    LIGHT_THEME_QSS, COLOR_PRIMARY, COLOR_PRIMARY_BG,
    COLOR_BORDER_DEFAULT, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_ERROR, COLOR_ERROR_BG
)
from database.db_manager import DatabaseManager
from services.ai_service import AiService
from services.document_reader import (
    MAX_PROBLEM_CHARS, DocumentReadError, read_document_text
)

logger = logging.getLogger("AITA.TestcaseDialog")


# ==============================================================================
# WORKER LUỒNG PHỤ GỌI AI HUB (OPENROUTER ĐA TÀI KHOẢN) QUA CENTRAL BACKEND
# ==============================================================================
class AiTestcaseWorker(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, problem_desc: str, language: str, count: int, include_boundary: bool):
        super().__init__()
        self.problem_desc = problem_desc
        self.language = language
        self.count = count
        self.include_boundary = include_boundary

    def run(self):
        ai_service = AiService()
        result = ai_service.generate_testcases(
            problem_description=self.problem_desc,
            language=self.language,
            count=self.count,
            include_boundary=self.include_boundary
        )
        self.finished.emit(result)


# ==============================================================================
# 1. HỘP THOẠI THÊM / CHỈNH SỬA TESTCASE THỦ CÔNG
# ==============================================================================
class TestcaseEditDialog(QDialog):
    """Hộp thoại thêm hoặc sửa một ca kiểm thử."""

    def __init__(self, parent=None, testcase: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self.tc = testcase or {}
        self.is_edit = testcase is not None
        self.setWindowTitle("Chỉnh Sửa Testcase" if self.is_edit else "Thêm Testcase Mới")
        self.setMinimumSize(540, 520)
        self.resize(600, 560)
        self.setStyleSheet(LIGHT_THEME_QSS)
        self.testcase_data: Dict[str, Any] = {}
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Hàng 1: Câu hỏi & Trọng số điểm
        row1 = QHBoxLayout()
        row1.setSpacing(16)

        v_q = QVBoxLayout()
        v_q.setSpacing(8)
        lbl_q = QLabel("Câu Hỏi:", self)
        lbl_q.setStyleSheet(f"font-weight: 600; font-size: 13px; line-height: 1.4; color: {COLOR_TEXT_PRIMARY};")
        v_q.addWidget(lbl_q)

        self.cb_q = QComboBox(self)
        self.cb_q.setFixedHeight(36)
        self.cb_q.setEditable(True)
        self.cb_q.addItems(["Q1", "Q2", "Q3", "Q4", "Q5"])
        cur_q = self.tc.get("question_number", "Q1")
        idx_q = self.cb_q.findText(cur_q)
        if idx_q >= 0:
            self.cb_q.setCurrentIndex(idx_q)
        else:
            self.cb_q.setEditText(cur_q)
        v_q.addWidget(self.cb_q)
        row1.addLayout(v_q, stretch=1)

        v_w = QVBoxLayout()
        v_w.setSpacing(8)
        lbl_w = QLabel("Trọng Số Điểm:", self)
        lbl_w.setStyleSheet(f"font-weight: 600; font-size: 13px; line-height: 1.4; color: {COLOR_TEXT_PRIMARY};")
        v_w.addWidget(lbl_w)

        self.sp_weight = QDoubleSpinBox(self)
        self.sp_weight.setFixedHeight(36)
        self.sp_weight.setRange(0.1, 10.0)
        self.sp_weight.setSingleStep(0.5)
        self.sp_weight.setValue(float(self.tc.get("score_weight", 1.0)))
        self.sp_weight.setStyleSheet("QDoubleSpinBox { min-height: 36px; padding: 4px 8px; font-size: 13px; }")
        v_w.addWidget(self.sp_weight)
        row1.addLayout(v_w, stretch=1)

        layout.addLayout(row1)

        # Hàng 2: Dữ liệu nhập (INPUT stdin)
        v_inp = QVBoxLayout()
        v_inp.setSpacing(8)
        lbl_inp = QLabel("Dữ Liệu Đầu Vào (stdin) - Để trống nếu không yêu cầu:", self)
        lbl_inp.setStyleSheet(f"font-weight: 600; font-size: 13px; line-height: 1.4; color: {COLOR_TEXT_PRIMARY};")
        v_inp.addWidget(lbl_inp)

        self.txt_input = QTextEdit(self)
        self.txt_input.setFixedHeight(95)
        self.txt_input.setPlaceholderText("Nhập các giá trị đầu vào...")
        self.txt_input.setStyleSheet("""
            QTextEdit {
                font-family: Consolas, monospace;
                font-size: 13px;
                line-height: 1.4;
                padding: 8px;
            }
        """)
        self.txt_input.setPlainText(self.tc.get("input_data", ""))
        v_inp.addWidget(self.txt_input)
        layout.addLayout(v_inp)

        # Hàng 3: Kết quả kỳ vọng (OUTPUT stdout)
        v_out = QVBoxLayout()
        v_out.setSpacing(8)
        lbl_out = QLabel("Kết Quả Kỳ Vọng (stdout) - Bắt buộc:", self)
        lbl_out.setStyleSheet(f"font-weight: 600; font-size: 13px; line-height: 1.4; color: {COLOR_TEXT_PRIMARY};")
        v_out.addWidget(lbl_out)

        self.txt_output = QTextEdit(self)
        self.txt_output.setFixedHeight(95)
        self.txt_output.setPlaceholderText("Nhập kết quả mong đợi chương trình in ra...")
        self.txt_output.setStyleSheet("""
            QTextEdit {
                font-family: Consolas, monospace;
                font-size: 13px;
                line-height: 1.4;
                padding: 8px;
            }
        """)
        self.txt_output.setPlainText(self.tc.get("expected_output", ""))
        v_out.addWidget(self.txt_output)
        layout.addLayout(v_out)

        # Hàng 4: Giới hạn thời gian (ms) & Bộ nhớ (MB)
        row2 = QHBoxLayout()
        row2.setSpacing(16)

        v_t = QVBoxLayout()
        v_t.setSpacing(8)
        lbl_t = QLabel("Giới Hạn Thời Gian (ms):", self)
        lbl_t.setStyleSheet(f"font-weight: 600; font-size: 13px; line-height: 1.4; color: {COLOR_TEXT_PRIMARY};")
        v_t.addWidget(lbl_t)

        self.sp_time = QSpinBox(self)
        self.sp_time.setFixedHeight(36)
        self.sp_time.setRange(100, 10000)
        self.sp_time.setSingleStep(100)
        self.sp_time.setValue(int(self.tc.get("time_limit_ms", 1000)))
        self.sp_time.setStyleSheet("QSpinBox { min-height: 36px; padding: 4px 8px; font-size: 13px; }")
        v_t.addWidget(self.sp_time)
        row2.addLayout(v_t, stretch=1)

        v_m = QVBoxLayout()
        v_m.setSpacing(8)
        lbl_m = QLabel("Giới Hạn Bộ Nhớ (MB):", self)
        lbl_m.setStyleSheet(f"font-weight: 600; font-size: 13px; line-height: 1.4; color: {COLOR_TEXT_PRIMARY};")
        v_m.addWidget(lbl_m)

        self.sp_mem = QSpinBox(self)
        self.sp_mem.setFixedHeight(36)
        self.sp_mem.setRange(16, 1024)
        self.sp_mem.setSingleStep(32)
        self.sp_mem.setValue(int(self.tc.get("memory_limit_mb", 128)))
        self.sp_mem.setStyleSheet("QSpinBox { min-height: 36px; padding: 4px 8px; font-size: 13px; }")
        v_m.addWidget(self.sp_mem)
        row2.addLayout(v_m, stretch=1)

        layout.addLayout(row2)
        layout.addStretch(1)

        # Footer Buttons
        footer = QHBoxLayout()
        footer.setSpacing(12)
        footer.addStretch(1)

        btn_cancel = QPushButton("Hủy Bỏ", self)
        btn_cancel.setProperty("class", "SecondaryBtn")
        btn_cancel.setFixedHeight(36)
        btn_cancel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_cancel.clicked.connect(self.reject)
        footer.addWidget(btn_cancel)

        btn_save = QPushButton("Lưu Testcase", self)
        btn_save.setProperty("class", "PrimaryBtn")
        btn_save.setFixedHeight(36)
        btn_save.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_save.clicked.connect(self._validate_and_save)
        footer.addWidget(btn_save)

        layout.addLayout(footer)

    def _validate_and_save(self):
        # IT06: validate the manual black-box testcase before persisting to LOCAL_TESTCASES
        question_number = self.cb_q.currentText().strip() or "Q1"
        input_data = self.txt_input.toPlainText()
        output = self.txt_output.toPlainText()
        score_weight = float(self.sp_weight.value())
        time_limit_ms = int(self.sp_time.value())
        memory_limit_mb = int(self.sp_mem.value())

        errors = []
        if not output.strip():
            errors.append("Kết quả mong đợi (stdout) không được để trống.")
        if score_weight <= 0:
            errors.append("Trọng số điểm phải lớn hơn 0.")
        if time_limit_ms <= 0:
            errors.append("Giới hạn thời gian phải lớn hơn 0 ms.")
        if memory_limit_mb <= 0:
            errors.append("Giới hạn bộ nhớ phải lớn hơn 0 MB.")
        if len(input_data.encode("utf-8")) > 256 * 1024:
            errors.append("Dữ liệu đầu vào (stdin) vượt quá giới hạn 256 KB.")
        if len(output.encode("utf-8")) > 256 * 1024:
            errors.append("Kết quả mong đợi (stdout) vượt quá giới hạn 256 KB.")

        if errors:
            QMessageBox.warning(
                self,
                "Dữ Liệu Không Hợp Lệ",
                "Vui lòng kiểm tra lại cấu hình testcase:\n\n• " + "\n• ".join(errors)
            )
            return

        self.testcase_data = {
            "question_number": question_number,
            "input_data": input_data,
            "expected_output": output,
            "score_weight": score_weight,
            "time_limit_ms": time_limit_ms,
            "memory_limit_mb": memory_limit_mb
        }
        self.accept()


# ==============================================================================
# 2. HỘP THOẠI SINH TESTCASE BẰNG AI (MODAL RIÊNG BIỆT)
# ==============================================================================
class AiTestcaseDialog(QDialog):
    """
    Hộp thoại sinh testcase bằng AI.
    Giao diện tinh gọn:
    - Ô Đề bài
    - Số lượng testcase
    - Nút chính: Sinh Testcase
    - Nút phụ: Hủy
    - Tùy chọn thu gọn: Câu hỏi, Ngôn ngữ
    - Bảng kết quả kèm checkbox từng dòng
    - Thông báo lỗi thân thiện, không lộ mã nội bộ
    """

    def __init__(
        self,
        parent=None,
        class_id: Optional[int] = None,
        default_question: str = "Q1",
        default_language: str = "C",
        matching_strategy: str = "IGNORE_WHITESPACE"
    ):
        super().__init__(parent)
        self.class_id = class_id
        self.matching_strategy = matching_strategy
        self.db = DatabaseManager()

        # Xác định ngôn ngữ mặc định từ thông tin đợt chấm
        self.default_language = default_language
        if self.class_id:
            cls_info = self.db.get_class_by_id(self.class_id)
            if cls_info and cls_info.get("programming_language"):
                self.default_language = cls_info["programming_language"]

        self.default_question = default_question or "Q1"
        self.generated_testcases: List[Dict[str, Any]] = []
        self.ai_worker: Optional[AiTestcaseWorker] = None

        self.setWindowTitle("Sinh Testcase Bằng AI")
        self.setMinimumSize(720, 560)
        self.resize(780, 620)
        self.setStyleSheet(LIGHT_THEME_QSS)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # 1. Ô Đề bài
        v_prompt = QVBoxLayout()
        v_prompt.setSpacing(8)

        prompt_head = QHBoxLayout()
        prompt_head.setSpacing(8)

        lbl_prompt = QLabel("Đề bài:", self)
        lbl_prompt.setStyleSheet(f"font-weight: 600; font-size: 13px; line-height: 1.4; color: {COLOR_TEXT_PRIMARY};")
        prompt_head.addWidget(lbl_prompt)
        prompt_head.addStretch(1)

        # Nút nhập đề bài từ file Word / PDF / văn bản để AI sinh testcase
        self.btn_import_doc = QPushButton("Nhập Từ File Đề Bài", self)
        self.btn_import_doc.setProperty("class", "SecondaryBtn")
        self.btn_import_doc.setFixedHeight(32)
        self.btn_import_doc.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_import_doc.setToolTip(
            "Nhập đề bài từ file Word (.docx), PDF (.pdf) hoặc văn bản (.txt, .md) "
            "để AI sinh testcase."
        )
        self.btn_import_doc.clicked.connect(self._import_problem_document)
        prompt_head.addWidget(self.btn_import_doc)

        v_prompt.addLayout(prompt_head)

        self.txt_prompt = QTextEdit(self)
        self.txt_prompt.setFixedHeight(85)
        self.txt_prompt.setPlaceholderText("Dán nội dung đề bài hoặc định dạng đầu vào và đầu ra cần sinh testcase...")
        self.txt_prompt.setStyleSheet("""
            QTextEdit {
                font-family: Consolas, monospace;
                font-size: 13px;
                line-height: 1.4;
                padding: 8px;
            }
        """)
        v_prompt.addWidget(self.txt_prompt)

        self.lbl_doc_name = QLabel("", self)
        self.lbl_doc_name.setStyleSheet(f"font-size: 11px; color: {COLOR_TEXT_SECONDARY};")
        self.lbl_doc_name.setWordWrap(True)
        self.lbl_doc_name.setVisible(False)
        v_prompt.addWidget(self.lbl_doc_name)

        layout.addLayout(v_prompt)

        # 2. Hàng điều khiển: Số lượng testcase + Tùy chọn thu gọn + Nút Sinh / Hủy
        row_ctrl = QHBoxLayout()
        row_ctrl.setSpacing(12)
        row_ctrl.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        lbl_count = QLabel("Số lượng testcase:", self)
        lbl_count.setStyleSheet(f"font-size: 13px; line-height: 1.4; color: {COLOR_TEXT_PRIMARY};")
        row_ctrl.addWidget(lbl_count)

        self.spin_count = QSpinBox(self)
        self.spin_count.setFixedHeight(36)
        self.spin_count.setRange(1, 10)
        self.spin_count.setValue(4)
        self.spin_count.setStyleSheet("QSpinBox { min-height: 36px; padding: 4px 8px; font-size: 13px; }")
        row_ctrl.addWidget(self.spin_count)

        self.btn_toggle_opt = QPushButton("Tùy chọn", self)
        self.btn_toggle_opt.setProperty("class", "SecondaryBtn")
        self.btn_toggle_opt.setFixedHeight(36)
        self.btn_toggle_opt.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_toggle_opt.setCheckable(True)
        self.btn_toggle_opt.toggled.connect(self._toggle_options)
        row_ctrl.addWidget(self.btn_toggle_opt)

        row_ctrl.addStretch(1)

        # Nút Thử Lại (ẩn mặc định, chỉ hiện khi lỗi)
        self.btn_retry = QPushButton("Thử Lại", self)
        self.btn_retry.setProperty("class", "SecondaryBtn")
        self.btn_retry.setFixedHeight(36)
        self.btn_retry.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_retry.setVisible(False)
        self.btn_retry.clicked.connect(self._start_generation)
        row_ctrl.addWidget(self.btn_retry)

        # Nút Hủy
        btn_cancel = QPushButton("Hủy", self)
        btn_cancel.setProperty("class", "SecondaryBtn")
        btn_cancel.setFixedHeight(36)
        btn_cancel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_cancel.clicked.connect(self.reject)
        row_ctrl.addWidget(btn_cancel)

        # Nút chính Sinh Testcase
        self.btn_submit = QPushButton("Sinh Testcase", self)
        self.btn_submit.setProperty("class", "PrimaryBtn")
        self.btn_submit.setFixedHeight(36)
        self.btn_submit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_submit.clicked.connect(self._start_generation)
        row_ctrl.addWidget(self.btn_submit)

        layout.addLayout(row_ctrl)

        # 3. Khung Tùy chọn thu gọn (Ngôn ngữ & Câu hỏi)
        self.frame_options = QFrame(self)
        self.frame_options.setProperty("class", "Card")
        self.frame_options.setVisible(False)
        opt_layout = QHBoxLayout(self.frame_options)
        opt_layout.setContentsMargins(14, 10, 14, 10)
        opt_layout.setSpacing(16)

        lbl_opt_q = QLabel("Câu hỏi áp dụng:", self.frame_options)
        lbl_opt_q.setStyleSheet(f"font-size: 13px; color: {COLOR_TEXT_PRIMARY};")
        opt_layout.addWidget(lbl_opt_q)

        self.cb_question = QComboBox(self.frame_options)
        self.cb_question.setFixedHeight(34)
        self.cb_question.addItems(["Q1", "Q2", "Q3", "Q4", "Q5"])
        q_idx = self.cb_question.findText(self.default_question)
        if q_idx >= 0:
            self.cb_question.setCurrentIndex(q_idx)
        opt_layout.addWidget(self.cb_question)

        lbl_opt_lang = QLabel("Ngôn ngữ lập trình:", self.frame_options)
        lbl_opt_lang.setStyleSheet(f"font-size: 13px; color: {COLOR_TEXT_PRIMARY};")
        opt_layout.addWidget(lbl_opt_lang)

        self.cb_language = QComboBox(self.frame_options)
        self.cb_language.setFixedHeight(34)
        self.cb_language.addItems(["C", "Java", "Python", "Web"])
        lang_idx = self.cb_language.findText(self.default_language, Qt.MatchFlag.MatchFixedString)
        if lang_idx >= 0:
            self.cb_language.setCurrentIndex(lang_idx)
        opt_layout.addWidget(self.cb_language)

        opt_layout.addStretch(1)
        layout.addWidget(self.frame_options)

        # 4. Dòng trạng thái / Thông báo lỗi thân thiện
        self.lbl_status = QLabel("", self)
        self.lbl_status.setStyleSheet(f"font-size: 13px; line-height: 1.4; color: {COLOR_TEXT_SECONDARY};")
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setVisible(False)
        layout.addWidget(self.lbl_status)

        # 5. Bảng hiển thị kết quả AI (Input, Expected Output, Checkbox)
        v_table = QVBoxLayout()
        v_table.setSpacing(8)

        lbl_tbl_title = QLabel("Kết quả testcase đề xuất:", self)
        lbl_tbl_title.setStyleSheet(f"font-weight: 600; font-size: 13px; line-height: 1.4; color: {COLOR_TEXT_PRIMARY};")
        v_table.addWidget(lbl_tbl_title)

        self.table_result = QTableWidget(self)
        self.table_result.setColumnCount(3)
        self.table_result.setHorizontalHeaderLabels(["Chọn", "Input (Đầu vào)", "Expected Output (Đầu ra kỳ vọng)"])
        r_header = self.table_result.horizontalHeader()
        r_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        r_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        r_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table_result.setColumnWidth(0, 56)
        self.table_result.verticalHeader().setVisible(False)
        self.table_result.setShowGrid(True)
        self.table_result.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        v_table.addWidget(self.table_result)

        layout.addLayout(v_table, stretch=1)

        # 6. Chân hộp thoại AI: Thao tác chọn & Nút Thêm Các Testcase Đã Chọn
        footer_ai = QHBoxLayout()
        footer_ai.setSpacing(12)

        self.btn_select_all = QPushButton("Chọn Tất Cả", self)
        self.btn_select_all.setProperty("class", "SecondaryBtn")
        self.btn_select_all.setFixedHeight(34)
        self.btn_select_all.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_select_all.setEnabled(False)
        self.btn_select_all.clicked.connect(self._select_all_rows)
        footer_ai.addWidget(self.btn_select_all)

        self.btn_deselect_all = QPushButton("Bỏ Chọn Tất Cả", self)
        self.btn_deselect_all.setProperty("class", "SecondaryBtn")
        self.btn_deselect_all.setFixedHeight(34)
        self.btn_deselect_all.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_deselect_all.setEnabled(False)
        self.btn_deselect_all.clicked.connect(self._deselect_all_rows)
        footer_ai.addWidget(self.btn_deselect_all)

        footer_ai.addStretch(1)

        # Nút Thêm Các Testcase Đã Chọn (disable khi chưa có kết quả)
        self.btn_add_selected = QPushButton("Thêm Các Testcase Đã Chọn", self)
        self.btn_add_selected.setProperty("class", "PrimaryBtn")
        self.btn_add_selected.setFixedHeight(36)
        self.btn_add_selected.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_add_selected.setEnabled(False)
        self.btn_add_selected.clicked.connect(self._add_selected_testcases)
        footer_ai.addWidget(self.btn_add_selected)

        layout.addLayout(footer_ai)

    def _toggle_options(self, checked: bool):
        self.frame_options.setVisible(checked)

    def _import_problem_document(self):
        """Loads a problem statement from a Word/PDF/text file into the prompt box."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn File Đề Bài",
            str(Path.home()),
            "Đề bài (*.docx *.pdf *.txt *.md *.csv *.log);;"
            "Word (*.docx);;PDF (*.pdf);;Văn bản (*.txt *.md *.csv *.log);;Tất cả (*.*)"
        )
        if not file_path:
            return

        try:
            text = read_document_text(file_path)
        except DocumentReadError as ex:
            QMessageBox.warning(self, "Không Đọc Được File", str(ex))
            return
        except Exception as ex:
            QMessageBox.warning(self, "Lỗi Đọc File", f"Không thể đọc file đề bài:\n{ex}")
            return

        if not text.strip():
            QMessageBox.warning(
                self, "File Rỗng",
                "Không tìm thấy nội dung văn bản trong file đã chọn."
            )
            return

        existing = self.txt_prompt.toPlainText().strip()
        if existing:
            choice = QMessageBox.question(
                self,
                "Ô Đề Bài Đã Có Nội Dung",
                "Ô đề bài hiện đang có nội dung.\n\n"
                "Chọn 'Yes' để THAY THẾ bằng nội dung file vừa chọn.\n"
                "Chọn 'No' để NỐI THÊM vào cuối nội dung hiện tại.",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes
            )
            if choice == QMessageBox.StandardButton.Cancel:
                return
            if choice == QMessageBox.StandardButton.No:
                text = f"{existing}\n\n{text}"

        note = ""
        if len(text) > MAX_PROBLEM_CHARS:
            text = text[:MAX_PROBLEM_CHARS]
            note = f" — chỉ dùng {MAX_PROBLEM_CHARS:,} ký tự đầu (giới hạn máy chủ AI)"
            QMessageBox.information(
                self,
                "Đề Bài Quá Dài",
                f"Nội dung file vượt quá {MAX_PROBLEM_CHARS:,} ký tự.\n"
                "Chỉ phần đầu được đưa vào để sinh testcase."
            )

        self.txt_prompt.setPlainText(text)
        self.lbl_doc_name.setText(
            f"Đã nhập đề bài từ: {Path(file_path).name} ({len(text):,} ký tự){note}"
        )
        self.lbl_doc_name.setVisible(True)

    def _start_generation(self):
        prompt = self.txt_prompt.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Thiếu Thông Tin", "Vui lòng nhập mô tả hoặc yêu cầu đề bài trước khi sinh testcase.")
            return

        lang = self.cb_language.currentText()
        count = self.spin_count.value()

        self.btn_submit.setEnabled(False)
        self.btn_submit.setText("Đang Sinh...")
        self.btn_retry.setVisible(False)
        self.btn_add_selected.setEnabled(False)
        self.btn_select_all.setEnabled(False)
        self.btn_deselect_all.setEnabled(False)

        self.lbl_status.setVisible(True)
        self.lbl_status.setText("Đang kết nối dịch vụ AI để phân tích đề bài và sinh testcase...")
        self.lbl_status.setStyleSheet(f"font-size: 13px; line-height: 1.4; color: {COLOR_PRIMARY};")

        self.table_result.setRowCount(0)
        self.generated_testcases.clear()

        self.ai_worker = AiTestcaseWorker(prompt, lang, count, True)
        self.ai_worker.finished.connect(self._on_generation_finished)
        self.ai_worker.start()

    def _on_generation_finished(self, result: Dict[str, Any]):
        self.btn_submit.setEnabled(True)
        self.btn_submit.setText("Sinh Testcase")

        if result.get("success"):
            tcs = result.get("testcases", [])
            self.generated_testcases = tcs
            self._render_results_table(tcs)

            self.lbl_status.setVisible(True)
            self.lbl_status.setText(f"Đã sinh thành công {len(tcs)} testcase. Hãy đánh dấu chọn các testcase phù hợp để thêm vào đợt chấm.")
            self.lbl_status.setStyleSheet("font-size: 13px; line-height: 1.4; color: #15803d;")

            self.btn_retry.setVisible(False)
            has_data = len(tcs) > 0
            self.btn_select_all.setEnabled(has_data)
            self.btn_deselect_all.setEnabled(has_data)
            self._update_add_button_state()
        else:
            err_code = result.get("error_code", "")
            err_detail = result.get("message", "")
            logger.warning("Lỗi dịch vụ AI sinh testcase: code=%s, detail=%s", err_code, err_detail)

            # Nói rõ nguyên nhân thay vì câu chung "không kết nối được": trước đây mọi
            # lỗi (hết hạn mức, server thiếu API key, token hết hạn...) đều hiện cùng
            # một câu nên giảng viên không biết phải làm gì.
            self.lbl_status.setVisible(True)
            self.lbl_status.setText(self._ai_error_message(result))
            self.lbl_status.setStyleSheet("font-size: 13px; line-height: 1.4; color: #b91c1c;")

            self.btn_retry.setVisible(True)
            self.btn_add_selected.setEnabled(False)
            self.btn_select_all.setEnabled(False)
            self.btn_deselect_all.setEnabled(False)

    # Mã lỗi backend -> lời giải thích cho giảng viên (kèm cách xử lý).
    _AI_ERROR_HINTS = {
        "AI_NOT_CONFIGURED": "Máy chủ chưa cấu hình API key AI (OPENROUTER_API_KEYS). Báo quản trị viên backend.",
        "AI_QUOTA_NOT_CONFIGURED": "Tài khoản chưa được cấp hạn mức AI. Báo quản trị viên cấu hình quota.",
        "AI_QUOTA_EXCEEDED": "Đã dùng hết hạn mức token AI trong ngày. Thử lại vào ngày mai hoặc nhập testcase thủ công.",
        "AI_PROVIDER_RATE_LIMITED": "Nhà cung cấp AI đang giới hạn số yêu cầu. Chờ 1-2 phút rồi thử lại.",
        "AI_PROVIDER_ERROR": "Nhà cung cấp AI không phản hồi (model có thể đang quá tải). Thử lại hoặc đổi model.",
        "AI_INVALID_RESPONSE": "AI trả về dữ liệu không đúng định dạng. Thử lại với đề bài rõ ràng hơn.",
        "CONNECT_ERROR": "Không kết nối được máy chủ backend. Kiểm tra mạng, hoặc server đang khởi động lại.",
        "CONNECT_TIMEOUT": "Máy chủ backend phản hồi quá chậm (server có thể đang ngủ). Thử lại sau ~30 giây.",
        "AUTH_INVALID_TOKEN": "Phiên đăng nhập đã hết hạn. Đăng nhập lại rồi thử lại.",
        "AUTH_TOKEN_EXPIRED": "Phiên đăng nhập đã hết hạn. Đăng nhập lại rồi thử lại.",
        "VALIDATION_FAILED": "Đề bài chưa đủ dài hoặc sai định dạng yêu cầu.",
        "TOO_MANY_REQUESTS": "Bạn thao tác quá nhanh. Chờ vài giây rồi thử lại.",
    }

    @classmethod
    def _ai_error_message(cls, result: Dict[str, Any]) -> str:
        """Dịch kết quả lỗi của backend thành câu tiếng Việt chỉ rõ nguyên nhân."""
        code = str(result.get("error_code", "") or "").strip().upper()
        hint = cls._AI_ERROR_HINTS.get(code)
        if not hint:
            hint = str(result.get("message", "") or "").strip() or "Không rõ nguyên nhân."
        return f"Không sinh được testcase: {hint} (mã lỗi: {code or 'UNKNOWN'})"

    def _render_results_table(self, testcases: List[Dict[str, Any]]):
        self.table_result.setRowCount(len(testcases))
        for r, tc in enumerate(testcases):
            self.table_result.setRowHeight(r, 44)

            # Cột 0: Checkbox chọn dòng
            chk_widget = QWidget(self.table_result)
            chk_layout = QHBoxLayout(chk_widget)
            chk_layout.setContentsMargins(0, 0, 0, 0)
            chk_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            chk = QCheckBox(chk_widget)
            chk.setChecked(True)
            chk.stateChanged.connect(self._update_add_button_state)
            chk_layout.addWidget(chk)
            self.table_result.setCellWidget(r, 0, chk_widget)

            # Cột 1: Input (Đầu vào)
            inp_text = str(tc.get("input", ""))
            it_inp = QTableWidgetItem(inp_text if inp_text else "(trống)")
            it_inp.setToolTip(inp_text)
            it_inp.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table_result.setItem(r, 1, it_inp)

            # Cột 2: Expected Output (Đầu ra kỳ vọng)
            out_text = str(tc.get("expected_output", ""))
            it_out = QTableWidgetItem(out_text if out_text else "(trống)")
            it_out.setToolTip(out_text)
            it_out.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table_result.setItem(r, 2, it_out)

    def _get_checkbox_at(self, row: int) -> Optional[QCheckBox]:
        w = self.table_result.cellWidget(row, 0)
        if w:
            return w.findChild(QCheckBox)
        return None

    def _select_all_rows(self):
        for r in range(self.table_result.rowCount()):
            chk = self._get_checkbox_at(r)
            if chk:
                chk.setChecked(True)
        self._update_add_button_state()

    def _deselect_all_rows(self):
        for r in range(self.table_result.rowCount()):
            chk = self._get_checkbox_at(r)
            if chk:
                chk.setChecked(False)
        self._update_add_button_state()

    def _update_add_button_state(self):
        selected_count = 0
        for r in range(self.table_result.rowCount()):
            chk = self._get_checkbox_at(r)
            if chk and chk.isChecked():
                selected_count += 1
        self.btn_add_selected.setEnabled(selected_count > 0)

    def _add_selected_testcases(self):
        if not self.class_id:
            classes = self.db.get_all_classes()
            if classes:
                self.class_id = classes[0]["id"]

        if not self.class_id:
            QMessageBox.warning(self, "Chưa Chọn Đợt Chấm", "Không xác định được đợt thi hiện tại để lưu testcase.")
            return

        target_q = self.cb_question.currentText().strip() or "Q1"
        added_count = 0

        for r in range(self.table_result.rowCount()):
            chk = self._get_checkbox_at(r)
            if chk and chk.isChecked() and r < len(self.generated_testcases):
                tc = self.generated_testcases[r]
                inp = str(tc.get("input", ""))
                outp = str(tc.get("expected_output", ""))
                try:
                    self.db.add_testcase(
                        class_id=self.class_id,
                        input_data=inp,
                        expected_output=outp,
                        score_weight=1.0,
                        time_limit_ms=1000,
                        matching_strategy=self.matching_strategy,
                        question_number=target_q
                    )
                    added_count += 1
                except Exception as ex:
                    logger.error("Lỗi khi thêm testcase vào CSDL: %s", str(ex))

        if added_count > 0:
            QMessageBox.information(
                self,
                "Đã Thêm Testcase",
                f"Đã thêm thành công {added_count} testcase vào câu {target_q}."
            )
            self.accept()
        else:
            QMessageBox.warning(self, "Chưa Chọn", "Vui lòng chọn ít nhất một testcase để thêm.")


# ==============================================================================
# 3. HỘP THOẠI QUẢN LÝ BỘ TESTCASE & CHIẾN LƯỢC SO KHỚP (2 TAB NGANG HÀNG)
# ==============================================================================
class TestcaseDialog(QDialog):
    """
    Cửa sổ Quản Lý Bộ Testcase & Chiến Lược So Khớp.
    Cấu trúc:
    - Tab 1: Testcase (mặc định mở)
    - Tab 2: So Khớp Đầu Ra (6 tiêu chí thuần tiếng Việt kèm tooltip)
    - Chân trang: Duy nhất 1 nút chính "Lưu" (nền xanh đặc), các nút khác dùng kiểu viền.
    """

    def __init__(self, parent=None, class_id: Optional[int] = None, is_wizard: bool = False):
        super().__init__(parent)
        self.is_wizard = is_wizard
        self.nav_back = False

        title = "Bước 3/3: Quản Lý Bộ Testcase & Chiến Lược So Khớp" if is_wizard else "Quản Lý Bộ Testcase & Chiến Lược So Khớp"
        self.setWindowTitle(title)

        screen = QGuiApplication.primaryScreen()
        if screen:
            avail = screen.availableGeometry()
            target_w = min(1140, avail.width() - 40)
            target_h = min(740, avail.height() - 50)
            self.setMinimumSize(min(960, target_w), min(600, target_h))
            self.resize(target_w, target_h)
            self.move(
                avail.x() + (avail.width() - target_w) // 2,
                avail.y() + (avail.height() - target_h) // 2
            )
        else:
            self.setMinimumSize(960, 600)
            self.resize(1100, 720)

        self.setStyleSheet(LIGHT_THEME_QSS)

        self.class_id = class_id
        self.db = DatabaseManager()
        self._all_testcases: List[Dict[str, Any]] = []

        self._init_ui()
        self._load_testcases_from_db()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Hai tab ngang hàng: Testcase và So Khớp Đầu Ra
        self.tabs = QTabWidget(self)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: #ffffff;
                top: -1px;
            }
            QTabBar::tab {
                font-size: 13px;
                font-weight: 600;
                line-height: 1.4;
                padding: 10px 20px;
                margin-right: 4px;
                color: #475569;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                border: 1px solid transparent;
            }
            QTabBar::tab:selected {
                color: #0284c7;
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-bottom: 2px solid #0284c7;
            }
            QTabBar::tab:hover:!selected {
                color: #0f172a;
                background-color: #f8fafc;
            }
        """)

        # TAB 1: Testcase (mặc định mở)
        tab_tc = QWidget()
        tl_layout = QVBoxLayout(tab_tc)
        tl_layout.setContentsMargins(16, 16, 16, 16)
        tl_layout.setSpacing(16)

        # Thanh công cụ đầu tab Testcase
        tool_row = QHBoxLayout()
        tool_row.setSpacing(12)
        tool_row.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        lbl_f = QLabel("Lọc theo câu hỏi:", tab_tc)
        lbl_f.setStyleSheet(f"font-size: 13px; line-height: 1.4; color: {COLOR_TEXT_PRIMARY};")
        tool_row.addWidget(lbl_f)

        self.cb_question = QComboBox(tab_tc)
        self.cb_question.setFixedHeight(36)
        self.cb_question.setMinimumWidth(150)
        self.cb_question.addItems(["Tất cả câu hỏi", "Q1", "Q2", "Q3", "Q4", "Q5"])
        self.cb_question.currentIndexChanged.connect(self._filter_testcases)
        tool_row.addWidget(self.cb_question)

        tool_row.addStretch(1)

        # Nút viền: Sinh Testcase Bằng AI
        self.btn_ai_gen = QPushButton("Sinh Testcase Bằng AI", tab_tc)
        self.btn_ai_gen.setProperty("class", "SecondaryBtn")
        self.btn_ai_gen.setFixedHeight(36)
        self.btn_ai_gen.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_ai_gen.clicked.connect(self._open_ai_dialog)
        tool_row.addWidget(self.btn_ai_gen)

        # Nút viền: Thêm Testcase
        self.btn_add_tc = QPushButton("Thêm Testcase", tab_tc)
        self.btn_add_tc.setProperty("class", "SecondaryBtn")
        self.btn_add_tc.setFixedHeight(36)
        self.btn_add_tc.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_add_tc.clicked.connect(self._add_testcase)
        tool_row.addWidget(self.btn_add_tc)

        tl_layout.addLayout(tool_row)

        # UX tổng trọng số: GV thấy ngay bảng quy đổi về thang 10 mà không phải chấm thử
        total_row = QHBoxLayout()
        total_row.addStretch(1)
        self.lbl_tc_total = QLabel("", tab_tc)
        self.lbl_tc_total.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_SECONDARY}; line-height: 1.4;")
        total_row.addWidget(self.lbl_tc_total)
        tl_layout.addLayout(total_row)

        # Bảng danh sách Testcase
        self.table_tc = QTableWidget(tab_tc)
        self.table_tc.setColumnCount(9)
        self.table_tc.setHorizontalHeaderLabels([
            "#", "Câu Hỏi", "INPUT (stdin)", "OUTPUT (stdout)",
            "Trọng Số", "Giới Hạn (ms)", "RAM (MB)", "Chiến Lược", "Thao Tác"
        ])
        t_header = self.table_tc.horizontalHeader()
        t_header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        t_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        t_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        t_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        t_header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        t_header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        t_header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        t_header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        t_header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        t_header.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)

        self.table_tc.setColumnWidth(0, 44)
        self.table_tc.setColumnWidth(1, 75)
        self.table_tc.setColumnWidth(4, 80)
        self.table_tc.setColumnWidth(5, 115)
        self.table_tc.setColumnWidth(6, 90)
        self.table_tc.setColumnWidth(7, 130)
        self.table_tc.setColumnWidth(8, 150)

        # Căn lề tiêu đề cột khớp với nội dung
        for col_idx in range(9):
            it_hdr = self.table_tc.horizontalHeaderItem(col_idx)
            if it_hdr:
                if col_idx in (2, 3):
                    it_hdr.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                else:
                    it_hdr.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        # Đặt tooltip cho cột OUTPUT
        it_out_hdr = self.table_tc.horizontalHeaderItem(3)
        if it_out_hdr:
            it_out_hdr.setToolTip("Kết quả kỳ vọng (stdout)")

        self.table_tc.verticalHeader().setVisible(False)
        self.table_tc.verticalHeader().setDefaultSectionSize(52)
        self.table_tc.setShowGrid(True)
        self.table_tc.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tl_layout.addWidget(self.table_tc)

        self.tabs.addTab(tab_tc, "Testcase")

        # TAB 2: So Khớp Đầu Ra
        tab_match = QWidget()
        tm_layout = QVBoxLayout(tab_match)
        tm_layout.setContentsMargins(20, 20, 20, 20)
        tm_layout.setSpacing(16)

        strat_card = QFrame(tab_match)
        strat_card.setProperty("class", "Card")
        s_layout = QVBoxLayout(strat_card)
        s_layout.setContentsMargins(20, 18, 20, 18)
        s_layout.setSpacing(16)

        lbl_strat_title = QLabel("Tiêu chí so khớp đầu ra chương trình:", strat_card)
        lbl_strat_title.setStyleSheet(f"font-weight: 600; font-size: 14px; line-height: 1.4; color: {COLOR_TEXT_PRIMARY};")
        s_layout.addWidget(lbl_strat_title)

        # Dòng mẹo viết lại ngắn, chữ #475569, 13px, line-height 1.4
        lbl_hint = QLabel(
            "Mẹo: Bỏ chọn tất cả để so khớp chính xác tuyệt đối từng ký tự. Các tiêu chí được chọn sẽ tự động kết hợp xử lý.",
            strat_card
        )
        lbl_hint.setStyleSheet("font-size: 13px; color: #475569; line-height: 1.4;")
        lbl_hint.setWordWrap(True)
        s_layout.addWidget(lbl_hint)

        # Lưới 6 checkbox thuần tiếng Việt, tooltip chi tiết
        grid_strat = QGridLayout()
        grid_strat.setHorizontalSpacing(24)
        grid_strat.setVerticalSpacing(16)

        cb_style = f"""
            QCheckBox {{
                font-size: 13px;
                color: {COLOR_TEXT_PRIMARY};
                font-weight: 500;
                line-height: 1.4;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid {COLOR_BORDER_DEFAULT};
                background-color: #FFFFFF;
            }}
            QCheckBox::indicator:hover {{
                border-color: {COLOR_PRIMARY};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLOR_PRIMARY};
                border-color: {COLOR_PRIMARY};
            }}
        """

        # 1. Bỏ qua khoảng trắng (mặc định chọn)
        self.chk_whitespace = QCheckBox("Bỏ qua khoảng trắng", strat_card)
        self.chk_whitespace.setToolTip("Bỏ qua khoảng trắng thừa và ký tự xuống dòng ở đầu, cuối và giữa các từ (Ignore Whitespace)")
        self.chk_whitespace.setChecked(True)
        self.chk_whitespace.setStyleSheet(cb_style)
        self.chk_whitespace.stateChanged.connect(self._on_matching_flags_changed)
        grid_strat.addWidget(self.chk_whitespace, 0, 0)

        # 2. Không phân biệt chữ hoa, chữ thường
        self.chk_case = QCheckBox("Không phân biệt chữ hoa, chữ thường", strat_card)
        self.chk_case.setToolTip("Không phân biệt ký tự in hoa và in thường (Case Insensitive)")
        self.chk_case.setStyleSheet(cb_style)
        self.chk_case.stateChanged.connect(self._on_matching_flags_changed)
        grid_strat.addWidget(self.chk_case, 0, 1)

        # 3. Chấp nhận dung sai số thực
        self.chk_float = QCheckBox("Chấp nhận dung sai số thực", strat_card)
        self.chk_float.setToolTip("Chấp nhận sai số dấu phẩy động với độ lệch cho phép nhỏ hơn hoặc bằng 1e-5 (Float Tolerance)")
        self.chk_float.setStyleSheet(cb_style)
        self.chk_float.stateChanged.connect(self._on_matching_flags_changed)
        grid_strat.addWidget(self.chk_float, 0, 2)

        # 4. Không phân biệt thứ tự từ hoặc số
        self.chk_unordered = QCheckBox("Không phân biệt thứ tự từ hoặc số", strat_card)
        self.chk_unordered.setToolTip("So khớp các từ hoặc số mà không phụ thuộc vào thứ tự xuất hiện (Unordered Tokens)")
        self.chk_unordered.setStyleSheet(cb_style)
        self.chk_unordered.stateChanged.connect(self._on_matching_flags_changed)
        grid_strat.addWidget(self.chk_unordered, 1, 0)

        # 5. So khớp biểu thức chính quy
        self.chk_regex = QCheckBox("So khớp biểu thức chính quy", strat_card)
        self.chk_regex.setToolTip("Sử dụng chuỗi đầu ra kỳ vọng như mẫu regex để kiểm tra (Regex Pattern)")
        self.chk_regex.setStyleSheet(cb_style)
        self.chk_regex.stateChanged.connect(self._on_matching_flags_changed)
        grid_strat.addWidget(self.chk_regex, 1, 1)

        # 6. Kiểm tra kịch bản chấm tùy biến
        self.chk_special = QCheckBox("Kiểm tra kịch bản chấm tùy biến", strat_card)
        self.chk_special.setToolTip("Chạy script chấm điểm riêng biệt cho bài toán nhiều đáp án (Special Judge)")
        self.chk_special.setStyleSheet(cb_style)
        self.chk_special.stateChanged.connect(self._on_matching_flags_changed)
        grid_strat.addWidget(self.chk_special, 1, 2)

        s_layout.addLayout(grid_strat)
        tm_layout.addWidget(strat_card)
        tm_layout.addStretch(1)

        self.tabs.addTab(tab_match, "So Khớp Đầu Ra")

        main_layout.addWidget(self.tabs, stretch=1)

        # Chân cửa sổ: Chỉ MỘT nút chính "Lưu" (nền xanh đặc), các nút khác dùng viền
        footer = QHBoxLayout()
        footer.setSpacing(12)
        footer.addStretch(1)

        # Nút viền Hủy Bỏ
        btn_cancel = QPushButton("Hủy Bỏ", self)
        btn_cancel.setProperty("class", "SecondaryBtn")
        btn_cancel.setFixedHeight(36)
        btn_cancel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_cancel.clicked.connect(self.reject)
        footer.addWidget(btn_cancel)

        # Nếu là Wizard: có nút viền Quay Lại Bước 2
        if self.is_wizard:
            btn_back = QPushButton("Quay Lại Bước 2", self)
            btn_back.setProperty("class", "SecondaryBtn")
            btn_back.setFixedHeight(36)
            btn_back.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_back.clicked.connect(self._go_back)
            footer.addWidget(btn_back)

        # Duy nhất một nút chính nền xanh đặc: "Lưu"
        self.btn_save = QPushButton("Lưu", self)
        self.btn_save.setProperty("class", "PrimaryBtn")
        self.btn_save.setFixedHeight(36)
        self.btn_save.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_save.clicked.connect(self._save_and_close)
        footer.addWidget(self.btn_save)

        main_layout.addLayout(footer)

    def _go_back(self):
        self.nav_back = True
        self.reject()

    def _save_and_close(self):
        """Lưu cấu hình so khớp vào CSDL và đóng hộp thoại."""
        strat_code = self._get_selected_strategy_code()
        if self.class_id:
            try:
                self.db.update_class_matching_strategy(self.class_id, strat_code)
            except Exception as ex:
                logger.error("Lỗi cập nhật chiến lược so khớp: %s", str(ex))
        self.accept()

    def _open_ai_dialog(self):
        """Mở hộp thoại sinh testcase bằng AI."""
        current_q = self.cb_question.currentText().strip()
        if current_q == "Tất cả câu hỏi":
            current_q = "Q1"

        strat_code = self._get_selected_strategy_code()
        dlg = AiTestcaseDialog(
            parent=self,
            class_id=self.class_id,
            default_question=current_q,
            matching_strategy=strat_code
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._load_testcases_from_db()

    # --------------------------------------------------------------------------
    # Quản Lý Tiêu Chí So Khớp Đầu Ra
    # --------------------------------------------------------------------------
    def _get_selected_strategy_code(self) -> str:
        flags = []
        if self.chk_whitespace.isChecked():
            flags.append("IGNORE_WHITESPACE")
        if self.chk_case.isChecked():
            flags.append("CASE_INSENSITIVE")
        if self.chk_float.isChecked():
            flags.append("FLOAT_TOLERANCE")
        if self.chk_unordered.isChecked():
            flags.append("UNORDERED_TOKENS")
        if self.chk_regex.isChecked():
            flags.append("REGEX_PATTERN")
        if self.chk_special.isChecked():
            flags.append("SPECIAL_JUDGE")
        return "+".join(flags) if flags else "EXACT_MATCH"

    def _set_flags_from_code(self, code: str):
        flags = set((code or "").upper().replace(",", "+").split("+"))
        self.chk_whitespace.blockSignals(True)
        self.chk_case.blockSignals(True)
        self.chk_float.blockSignals(True)
        self.chk_unordered.blockSignals(True)
        self.chk_regex.blockSignals(True)
        self.chk_special.blockSignals(True)

        self.chk_whitespace.setChecked("IGNORE_WHITESPACE" in flags)
        self.chk_case.setChecked("CASE_INSENSITIVE" in flags)
        self.chk_float.setChecked("FLOAT_TOLERANCE" in flags or "FLOATING_POINT" in flags)
        self.chk_unordered.setChecked("UNORDERED_TOKENS" in flags)
        self.chk_regex.setChecked("REGEX_PATTERN" in flags or "REGEX" in flags)
        self.chk_special.setChecked("SPECIAL_JUDGE" in flags)

        self.chk_whitespace.blockSignals(False)
        self.chk_case.blockSignals(False)
        self.chk_float.blockSignals(False)
        self.chk_unordered.blockSignals(False)
        self.chk_regex.blockSignals(False)
        self.chk_special.blockSignals(False)

    def _on_matching_flags_changed(self):
        strat_code = self._get_selected_strategy_code()
        if self.class_id:
            try:
                self.db.update_class_matching_strategy(self.class_id, strat_code)
                self._load_testcases_from_db()
            except Exception as ex:
                logger.error("Lỗi cập nhật cờ so khớp: %s", str(ex))

    # --------------------------------------------------------------------------
    # CRUD Operations: Thêm / Sửa / Xóa Testcase
    # --------------------------------------------------------------------------
    def _load_testcases_from_db(self):
        if not self.class_id:
            classes = self.db.get_all_classes()
            if classes:
                self.class_id = classes[0]["id"]
            else:
                self.table_tc.setRowCount(0)
                return

        testcases = self.db.get_testcases_by_class(self.class_id)
        if testcases:
            first_strat = testcases[0].get("matching_strategy", "IGNORE_WHITESPACE")
            self._set_flags_from_code(first_strat)

        self._all_testcases = testcases
        self._filter_testcases()

    def _filter_testcases(self):
        q_filter = self.cb_question.currentText().strip()
        if q_filter == "Tất cả câu hỏi":
            self._render_testcases_table(self._all_testcases)
        else:
            filtered = [tc for tc in self._all_testcases if tc.get("question_number", "").upper() == q_filter.upper()]
            self._render_testcases_table(filtered)

    def _update_tc_total_label(self):
        """Hiển thị tổng trọng số testcases của đợt để hiểu quy đổi thang điểm 10."""
        cases = getattr(self, "_all_testcases", []) or []
        total_weight = sum(float(tc.get("score_weight", 1.0) or 0.0) for tc in cases)
        if total_weight <= 0:
            self.lbl_tc_total.setText("Chưa có testcase nào — hãy thêm testcase trước khi bắt đầu chấm.")
            self.lbl_tc_total.setStyleSheet(f"font-size: 12px; color: #DC2626; line-height: 1.4;")
            return
        per_unit = 10.0 / total_weight
        self.lbl_tc_total.setText(
            f"Tổng trọng số: {total_weight:.1f} — đạt đủ mới được 10/10; mỗi 1 trọng số tương đương {per_unit:.1f} điểm."
        )
        self.lbl_tc_total.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_SECONDARY}; line-height: 1.4;")

    def _render_testcases_table(self, testcases: List[Dict[str, Any]]):
        self._update_tc_total_label()
        self.table_tc.setRowCount(len(testcases))
        for r, tc in enumerate(testcases):
            self.table_tc.setRowHeight(r, 52)

            # 0: STT
            it_stt = QTableWidgetItem(str(r + 1))
            it_stt.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_tc.setItem(r, 0, it_stt)

            # 1: Câu Hỏi
            it_q = QTableWidgetItem(tc.get("question_number", "Q1"))
            it_q.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            it_q.setFont(QFont("Inter", 10, QFont.Weight.Bold))
            self.table_tc.setItem(r, 1, it_q)

            # 2: INPUT
            inp_str = tc.get("input_data", "")
            it_inp = QTableWidgetItem(inp_str.replace("\n", " / ") if inp_str else "(trống)")
            it_inp.setToolTip(f"INPUT:\n{inp_str}")
            it_inp.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table_tc.setItem(r, 2, it_inp)

            # 3: OUTPUT
            out_str = tc.get("expected_output", "")
            it_out = QTableWidgetItem(out_str.replace("\n", " / ") if out_str else "(trống)")
            it_out.setToolTip(f"OUTPUT:\n{out_str}")
            it_out.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table_tc.setItem(r, 3, it_out)

            # 4: Trọng Số
            it_w = QTableWidgetItem(f"{tc.get('score_weight', 1.0):.1f}")
            it_w.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_tc.setItem(r, 4, it_w)

            # 5: Giới Hạn ms
            it_t = QTableWidgetItem(str(tc.get("time_limit_ms", 1000)))
            it_t.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_tc.setItem(r, 5, it_t)

            # 6: RAM MB
            it_m = QTableWidgetItem(str(tc.get("memory_limit_mb", 128)))
            it_m.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_tc.setItem(r, 6, it_m)

            # 7: Chiến Lược
            it_strat = QTableWidgetItem(tc.get("matching_strategy", "EXACT_MATCH"))
            it_strat.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            it_strat.setFont(QFont("Inter", 9))
            self.table_tc.setItem(r, 7, it_strat)

            # 8: Thao Tác (Nút Sửa & Nút Xóa) - căn giữa tuyệt đối theo chiều dọc và ngang
            act_widget = QWidget()
            act_widget.setStyleSheet("background: transparent; border: none;")
            act_layout = QHBoxLayout(act_widget)
            act_layout.setContentsMargins(0, 0, 0, 0)
            act_layout.setSpacing(8)
            act_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            btn_edit = QPushButton("Sửa", act_widget)
            btn_edit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_edit.setStyleSheet(f"""
                QPushButton {{
                    background-color: #FFFFFF;
                    color: {COLOR_PRIMARY};
                    border: 1px solid {COLOR_PRIMARY};
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: 600;
                    min-height: 26px;
                    max-height: 26px;
                    height: 26px;
                    min-width: 50px;
                    max-width: 50px;
                    width: 50px;
                    padding: 0;
                }}
                QPushButton:hover {{
                    background-color: {COLOR_PRIMARY_BG};
                }}
            """)
            btn_edit.clicked.connect(lambda _, item=tc: self._edit_testcase(item))
            act_layout.addWidget(btn_edit)

            btn_del = QPushButton("Xóa", act_widget)
            btn_del.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_del.setStyleSheet(f"""
                QPushButton {{
                    background-color: #FFFFFF;
                    color: {COLOR_ERROR};
                    border: 1px solid {COLOR_ERROR}55;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: 600;
                    min-height: 26px;
                    max-height: 26px;
                    height: 26px;
                    min-width: 50px;
                    max-width: 50px;
                    width: 50px;
                    padding: 0;
                }}
                QPushButton:hover {{
                    background-color: {COLOR_ERROR_BG};
                    border-color: {COLOR_ERROR};
                }}
            """)
            btn_del.clicked.connect(lambda _, item=tc: self._delete_testcase(item))
            act_layout.addWidget(btn_del)

            self.table_tc.setCellWidget(r, 8, act_widget)

    def _add_testcase(self):
        if not self.class_id:
            QMessageBox.warning(self, "Chưa Chọn Đợt Chấm", "Không xác định được đợt thi hiện tại.")
            return

        dlg = TestcaseEditDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.testcase_data:
            d = dlg.testcase_data
            strat = self._get_selected_strategy_code()
            try:
                self.db.add_testcase(
                    class_id=self.class_id,
                    input_data=d["input_data"],
                    expected_output=d["expected_output"],
                    score_weight=d["score_weight"],
                    time_limit_ms=d["time_limit_ms"],
                    memory_limit_mb=d["memory_limit_mb"],
                    matching_strategy=strat,
                    question_number=d["question_number"]
                )
                self._load_testcases_from_db()
                QMessageBox.information(self, "Thành Công", "Đã thêm testcase mới thành công.")
            except Exception as ex:
                QMessageBox.critical(self, "Lỗi Lưu CSDL", f"Không thể lưu testcase:\n{str(ex)}")

    def _edit_testcase(self, tc: Dict[str, Any]):
        dlg = TestcaseEditDialog(self, testcase=tc)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.testcase_data:
            d = dlg.testcase_data
            tc_id = tc.get("id")
            if tc_id:
                try:
                    self.db.update_testcase(
                        testcase_id=tc_id,
                        question_number=d["question_number"],
                        input_data=d["input_data"],
                        expected_output=d["expected_output"],
                        score_weight=d["score_weight"],
                        time_limit_ms=d["time_limit_ms"],
                        memory_limit_mb=d["memory_limit_mb"]
                    )
                    self._load_testcases_from_db()
                    QMessageBox.information(self, "Thành Công", "Đã cập nhật thông tin testcase thành công.")
                except Exception as ex:
                    QMessageBox.critical(self, "Lỗi Cập Nhật", f"Không thể cập nhật testcase:\n{str(ex)}")

    def _delete_testcase(self, tc: Dict[str, Any]):
        tc_id = tc.get("id")
        q_num = tc.get("question_number", "Q1")
        ret = QMessageBox.question(
            self,
            "Xác Nhận Xóa Testcase",
            f"Bạn có chắc chắn muốn xóa testcase này của câu {q_num}?\n\n"
            f"- INPUT: {tc.get('input_data', '')[:40] or '(trống)'}\n"
            f"- OUTPUT: {tc.get('expected_output', '')[:40]}\n\n"
            f"Hành động này sẽ xóa testcase khỏi cơ sở dữ liệu.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if ret == QMessageBox.StandardButton.Yes and tc_id:
            try:
                self.db.delete_testcase(tc_id)
                self._load_testcases_from_db()
            except Exception as ex:
                QMessageBox.critical(self, "Lỗi Xóa", f"Không thể xóa testcase:\n{str(ex)}")
