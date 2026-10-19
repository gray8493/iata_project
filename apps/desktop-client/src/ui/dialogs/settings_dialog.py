"""
AITA Desktop Client - Environment & Sandbox Settings Dialog (PyQt6)
UC-06: Configure Local Compilers & Sandbox Settings
"""

import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSpinBox, QSlider, QFrame, QFileDialog, QMessageBox,
    QScrollArea
)

from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ui.styles.theme import LIGHT_THEME_QSS
from core.app_paths import load_config, save_config, resolve_python_executable
from core.adapters.compiler_adapter import find_gcc_executable, find_java_tool



class SettingsDialog(QDialog):
    """
    Dialog for configuring local compilers and sandbox isolation settings.
    """

    def __init__(self, parent=None, is_wizard: bool = False):
        super().__init__(parent)
        self.is_wizard = is_wizard
        self.nav_back = False
        self.is_saved = False
        
        title = "Bước 2/3: Cấu Hình Môi Trường Biên Dịch & Sandbox Cục Bộ" if is_wizard else "Cấu Hình Môi Trường Biên Dịch & Sandbox Cục Bộ"
        self.setWindowTitle(title)
        self.setMinimumSize(780, 620)
        self.resize(840, 680)
        self.setStyleSheet(LIGHT_THEME_QSS)
        self._init_ui()
        self._load_saved_paths()

    def _load_saved_paths(self) -> None:
        """Nạp đường dẫn đã lưu (hoặc toolchain đóng kèm) vào các ô nhập."""
        config = load_config()
        gcc = config.get("gcc_path") or find_gcc_executable() or ""
        javac = config.get("javac_path") or find_java_tool("javac") or ""
        python_path = config.get("python_path") or ""
        if not python_path:
            try:
                python_path = resolve_python_executable()
            except RuntimeError:
                python_path = ""
        self.txt_gcc.setText(str(gcc))
        self.txt_java.setText(str(javac))
        self.txt_py.setText(str(python_path))

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)
        
        # 1. Header Card
        header_card = QFrame(self)
        header_card.setProperty("class", "Card")
        h_layout = QVBoxLayout(header_card)
        h_layout.setContentsMargins(18, 14, 18, 14)
        h_layout.setSpacing(4)
        
        lbl_title = QLabel("Cấu Hình Môi Trường Thực Thi Cục Bộ", header_card)
        lbl_title.setProperty("class", "Heading1")
        h_layout.addWidget(lbl_title)
        
        lbl_desc = QLabel("Thiết lập đường dẫn trình biên dịch và các tham số kiểm soát tài nguyên Sandbox.", header_card)
        lbl_desc.setProperty("class", "SubText")
        h_layout.addWidget(lbl_desc)
        main_layout.addWidget(header_card)
        
        # 2. Scrollable Body
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        body_widget = QWidget()
        b_layout = QVBoxLayout(body_widget)
        b_layout.setContentsMargins(0, 0, 4, 0)
        b_layout.setSpacing(14)
        
        # Section 1: Compilers Section Card
        comp_card = QFrame(body_widget)
        comp_card.setProperty("class", "Card")
        c_layout = QVBoxLayout(comp_card)
        c_layout.setContentsMargins(20, 18, 20, 18)
        c_layout.setSpacing(14)
        
        lbl_sec1 = QLabel("1. Đường Dẫn Trình Biên Dịch & Runtimes:", comp_card)
        lbl_sec1.setProperty("class", "Heading2")
        c_layout.addWidget(lbl_sec1)
        
        # GCC Path Block
        block_gcc = QVBoxLayout()
        block_gcc.setSpacing(6)
        lbl_gcc = QLabel("Trình biên dịch C/C++ (GCC / MinGW):", comp_card)
        lbl_gcc.setStyleSheet("font-weight: 600; font-size: 13px;")
        block_gcc.addWidget(lbl_gcc)
        
        gcc_row = QHBoxLayout()
        gcc_row.setSpacing(10)
        self.txt_gcc = QLineEdit(comp_card)
        self.txt_gcc.setFixedHeight(38)
        self.txt_gcc.setPlaceholderText("Chọn đường dẫn đến gcc.exe...")
        gcc_row.addWidget(self.txt_gcc)
        
        btn_gcc = QPushButton("Duyệt...", comp_card)
        btn_gcc.setProperty("class", "SecondaryBtn")
        btn_gcc.setFixedHeight(38)
        btn_gcc.setFixedWidth(90)
        btn_gcc.clicked.connect(lambda: self._browse_exe(self.txt_gcc))
        gcc_row.addWidget(btn_gcc)
        block_gcc.addLayout(gcc_row)
        c_layout.addLayout(block_gcc)
        
        # Javac Path Block
        block_java = QVBoxLayout()
        block_java.setSpacing(6)
        lbl_java = QLabel("Trình biên dịch Java (Javac):", comp_card)
        lbl_java.setStyleSheet("font-weight: 600; font-size: 13px;")
        block_java.addWidget(lbl_java)
        
        java_row = QHBoxLayout()
        java_row.setSpacing(10)
        self.txt_java = QLineEdit(comp_card)
        self.txt_java.setFixedHeight(38)
        self.txt_java.setPlaceholderText("Chọn đường dẫn đến javac.exe...")
        java_row.addWidget(self.txt_java)
        
        btn_java = QPushButton("Duyệt...", comp_card)
        btn_java.setProperty("class", "SecondaryBtn")
        btn_java.setFixedHeight(38)
        btn_java.setFixedWidth(90)
        btn_java.clicked.connect(lambda: self._browse_exe(self.txt_java))
        java_row.addWidget(btn_java)
        block_java.addLayout(java_row)
        c_layout.addLayout(block_java)
        
        # Python Path Block
        block_py = QVBoxLayout()
        block_py.setSpacing(6)
        lbl_py = QLabel("Python Runtime (python.exe):", comp_card)
        lbl_py.setStyleSheet("font-weight: 600; font-size: 13px;")
        block_py.addWidget(lbl_py)
        
        py_row = QHBoxLayout()
        py_row.setSpacing(10)
        self.txt_py = QLineEdit(comp_card)
        self.txt_py.setFixedHeight(38)
        self.txt_py.setPlaceholderText("Chọn đường dẫn đến python.exe...")
        py_row.addWidget(self.txt_py)
        
        btn_py = QPushButton("Duyệt...", comp_card)
        btn_py.setProperty("class", "SecondaryBtn")
        btn_py.setFixedHeight(38)
        btn_py.setFixedWidth(90)
        btn_py.clicked.connect(lambda: self._browse_exe(self.txt_py))
        py_row.addWidget(btn_py)
        block_py.addLayout(py_row)
        c_layout.addLayout(block_py)
        
        # Test Environment Button (Separate row with margin)
        c_layout.addSpacing(4)
        btn_test_env = QPushButton("Kiểm Tra Môi Trường (Test Subprocess)", comp_card)
        btn_test_env.setProperty("class", "SecondaryBtn")
        btn_test_env.setFixedHeight(38)
        btn_test_env.clicked.connect(self._test_environment)
        c_layout.addWidget(btn_test_env)
        
        b_layout.addWidget(comp_card)
        
        # Section 2: Sandbox Settings Card
        sb_card = QFrame(body_widget)
        sb_card.setProperty("class", "Card")
        s_layout = QVBoxLayout(sb_card)
        s_layout.setContentsMargins(20, 18, 20, 18)
        s_layout.setSpacing(14)
        
        lbl_sec2 = QLabel("2. Giới Hạn Tài Nguyên Sandbox Mặc Định:", sb_card)
        lbl_sec2.setProperty("class", "Heading2")
        s_layout.addWidget(lbl_sec2)
        
        # 3 Columns with balanced stretch (1:1:1)
        row_params = QHBoxLayout()
        row_params.setSpacing(18)
        
        # Col 1: Time limit
        v_tl = QVBoxLayout()
        v_tl.setSpacing(6)
        lbl_tl = QLabel("Thời Gian Tối Đa (ms):", sb_card)
        lbl_tl.setStyleSheet("font-weight: 600; font-size: 13px;")
        v_tl.addWidget(lbl_tl)
        self.sp_tl = QSpinBox(sb_card)
        self.sp_tl.setFixedHeight(38)
        self.sp_tl.setRange(200, 10000)
        self.sp_tl.setValue(1000)
        self.sp_tl.setSingleStep(100)
        v_tl.addWidget(self.sp_tl)
        row_params.addLayout(v_tl, stretch=1)
        
        # Col 2: Memory limit
        v_ml = QVBoxLayout()
        v_ml.setSpacing(6)
        lbl_ml = QLabel("Bộ Nhớ Tối Đa (MB):", sb_card)
        lbl_ml.setStyleSheet("font-weight: 600; font-size: 13px;")
        v_ml.addWidget(lbl_ml)
        self.sp_ml = QSpinBox(sb_card)
        self.sp_ml.setFixedHeight(38)
        self.sp_ml.setRange(64, 2048)
        self.sp_ml.setValue(256)
        self.sp_ml.setSingleStep(64)
        v_ml.addWidget(self.sp_ml)
        row_params.addLayout(v_ml, stretch=1)
        
        # Col 3: Concurrency
        v_cc = QVBoxLayout()
        v_cc.setSpacing(6)
        lbl_cc = QLabel("Luồng Chấm Song Song:", sb_card)
        lbl_cc.setStyleSheet("font-weight: 600; font-size: 13px;")
        v_cc.addWidget(lbl_cc)
        self.sp_cc = QSpinBox(sb_card)
        self.sp_cc.setFixedHeight(38)
        self.sp_cc.setRange(1, 16)
        self.sp_cc.setValue(4)
        v_cc.addWidget(self.sp_cc)
        row_params.addLayout(v_cc, stretch=1)
        
        s_layout.addLayout(row_params)
        b_layout.addWidget(sb_card)
        
        scroll.setWidget(body_widget)
        main_layout.addWidget(scroll, stretch=1)
        
        # 4. Action Buttons Footer
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.addStretch(1)

        btn_cancel = QPushButton("Hủy Bỏ", self)
        btn_cancel.setProperty("class", "SecondaryBtn")
        btn_cancel.setFixedHeight(38)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)

        if self.is_wizard:
            btn_back = QPushButton("Quay Lại Bước 1", self)
            btn_back.setProperty("class", "SecondaryBtn")
            btn_back.setFixedHeight(38)
            btn_back.clicked.connect(self._go_back)
            btn_row.addWidget(btn_back)

        btn_label = "Tiếp Tục: Cấu Hình Testcase (Bước 3/3)" if self.is_wizard else "Lưu Cấu Hình"
        btn_save = QPushButton(btn_label, self)
        btn_save.setProperty("class", "PrimaryBtn")
        btn_save.setFixedHeight(38)
        btn_save.clicked.connect(self._save_settings)
        btn_row.addWidget(btn_save)

        main_layout.addLayout(btn_row)

    def _go_back(self):
        """Signals wizard state machine to return to Step 1."""
        self.nav_back = True
        self.reject()

    def _browse_exe(self, target_line_edit):
        exe, _ = QFileDialog.getOpenFileName(self, "Chọn File Thực Thi", "", "Executable Files (*.exe);;All Files (*)")
        if exe:
            target_line_edit.setText(exe)

    def _probe_tool(self, exe_path: str, version_args: list) -> tuple:
        """Chạy thử `<exe> --version` và trả (ok, mô tả)."""
        import subprocess

        path = (exe_path or "").strip()
        if not path:
            return False, "chưa cấu hình"
        if not Path(path).is_file():
            return False, "không tìm thấy tệp"
        try:
            res = subprocess.run(
                [path] + version_args,
                capture_output=True,
                text=True,
                timeout=10,
            )
        except Exception as ex:
            return False, f"không chạy được ({ex})"
        if res.returncode != 0:
            return False, "trả mã lỗi khi chạy thử"
        first_line = ((res.stdout or res.stderr or "").strip().splitlines() or ["OK"])[0]
        return True, first_line[:80]

    def _test_environment(self):
        """Kiểm tra thật: chạy `--version` cho gcc/javac/python và thử biên dịch C."""
        import subprocess
        import tempfile

        lines = ["Kết quả kiểm tra môi trường:"]
        all_ok = True

        gcc_ok, gcc_info = self._probe_tool(self.txt_gcc.text(), ["--version"])
        all_ok &= gcc_ok
        lines.append(f"- GCC: {'OK' if gcc_ok else 'LỖI'} ({gcc_info})")

        javac_ok, javac_info = self._probe_tool(self.txt_java.text(), ["-version"])
        all_ok &= javac_ok
        lines.append(f"- Javac: {'OK' if javac_ok else 'LỖI'} ({javac_info})")

        py_ok, py_info = self._probe_tool(self.txt_py.text(), ["--version"])
        all_ok &= py_ok
        lines.append(f"- Python: {'OK' if py_ok else 'LỖI'} ({py_info})")

        # Biên dịch thử một chương trình C tối giản để chắc chắn toolchain liên kết được.
        if gcc_ok:
            try:
                with tempfile.TemporaryDirectory(prefix="aita_envcheck_") as tmp:
                    src = Path(tmp) / "probe.c"
                    out = Path(tmp) / "probe.exe"
                    src.write_text("int main(void){return 0;}\n", encoding="utf-8")
                    res = subprocess.run(
                        [self.txt_gcc.text().strip(), str(src), "-o", str(out)],
                        capture_output=True, text=True, timeout=30,
                    )
                    ok = res.returncode == 0 and out.is_file()
                    all_ok &= ok
                    lines.append(f"- Biên dịch thử C: {'OK' if ok else 'LỖI'}"
                                 + ("" if ok else f" ({(res.stderr or '').strip()[:120]})"))
            except Exception as ex:
                all_ok = False
                lines.append(f"- Biên dịch thử C: LỖI ({ex})")
        else:
            all_ok = False
            lines.append("- Biên dịch thử C: BỎ QUA (chưa có GCC)")

        lines.append("")
        lines.append("Môi trường sẵn sàng chấm bài." if all_ok
                     else "Còn công cụ lỗi — hãy chọn đúng đường dẫn .exe hoặc dùng bản đóng gói kèm toolchains/.")
        QMessageBox.information(
            self,
            "Kiểm Tra Môi Trường" if all_ok else "Môi Trường Chưa Sẵn Sàng",
            "\n".join(lines),
        )

    def _save_settings(self):
        """Lưu đường dẫn toolchain vào config.json (thực sự được app đọc khi chấm)."""
        saved = save_config({
            "gcc_path": self.txt_gcc.text().strip(),
            "javac_path": self.txt_java.text().strip(),
            "java_path": str(Path(self.txt_java.text().strip()).with_name("java.exe"))
            if self.txt_java.text().strip() else "",
            "python_path": self.txt_py.text().strip(),
            "default_time_limit_ms": self.sp_tl.value(),
            "default_memory_limit_mb": self.sp_ml.value(),
            "parallel_workers": self.sp_cc.value(),
        })
        if not saved:
            QMessageBox.warning(
                self, "Không Lưu Được Cấu Hình",
                "Không ghi được tệp config.json. Vui lòng kiểm tra quyền ghi thư mục dữ liệu.",
            )
            return
        self.is_saved = True
        self.accept()
