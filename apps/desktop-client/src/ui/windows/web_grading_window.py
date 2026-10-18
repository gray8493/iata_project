"""
AITA Desktop Client - Dedicated Web Grading Workspace Window (PyQt6)
UC-19: Automated Web Assignment Grading & Scoring (Web Studio)
Standard Implementation matching DESKTOP APP UI/UX DESIGN SYSTEM
Style: Modern Educational SaaS, 100% Light, Blue-focused (#2F80ED), Clean 240px Sidebar, 64px Header.
"""

import sys
import re
import html
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal, QSettings, QUrl
from PyQt6.QtGui import (
    QFont, QColor, QCursor, QPixmap, QGuiApplication, QDesktopServices,
    QTextDocument, QPageSize, QPageLayout
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QProgressBar, QMessageBox, QFileDialog,
    QDialog, QSplitter, QTextEdit, QDoubleSpinBox, QFormLayout,
    QLineEdit, QTabWidget, QScrollArea, QMenu, QRadioButton,
    QButtonGroup, QComboBox
)

SRC_DIR = Path(__file__).resolve().parent.parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from database.db_manager import DatabaseManager
from services.ai_service import AiService
from services.web_rubric_service import WebRubricEngine, classify_url
from ui.components import make_aita_avatar_pixmap
from ui.styles.theme import (
    LIGHT_THEME_QSS, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_PRIMARY_ACTIVE,
    COLOR_PRIMARY_BG, COLOR_PRIMARY_LIGHT, COLOR_BG, COLOR_SURFACE,
    COLOR_SURFACE_SECONDARY, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED, COLOR_TEXT_DISABLED, COLOR_BORDER_DEFAULT, COLOR_BORDER_LIGHT,
    COLOR_SUCCESS, COLOR_SUCCESS_BG, COLOR_ERROR, COLOR_ERROR_BG,
    COLOR_WARNING, COLOR_WARNING_BG, RADIUS_CARD, RADIUS_BUTTON, RADIUS_PILL
)


# ==============================================================================
# SHARED UI HELPERS (rule 21: action column built by a shared helper)
# ==============================================================================
def make_action_cell(buttons: List[QPushButton], parent: QWidget) -> QWidget:
    """Wraps row action buttons in a vertically-centered container with a uniform 8px gap."""
    cell = QWidget(parent)
    layout = QHBoxLayout(cell)
    layout.setContentsMargins(4, 4, 4, 4)
    layout.setSpacing(8)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    for btn in buttons:
        btn.setFixedHeight(30)
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        layout.addWidget(btn)
    return cell


# ==============================================================================
# 0. WORKER THẨM ĐỊNH WEB THẬT (PLAYWRIGHT + BEAUTIFULSOUP + TINYCSS2 + AI HUB VISION)
# ==============================================================================
class WebGradingWorker(QThread):
    """Runs the real 4-criteria web rubric engine off the UI thread."""

    progress = pyqtSignal(int, str)
    graded_one = pyqtSignal(dict)
    all_done = pyqtSignal(int)

    def __init__(self, students: List[Dict[str, Any]], engine: WebRubricEngine, parent=None):
        super().__init__(parent)
        self._students = students
        self._engine = engine
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        total = len(self._students)
        for idx, st in enumerate(self._students):
            if self._cancelled:
                break
            percent = int((idx / total) * 100) if total else 0
            self.progress.emit(percent, f"Đang thẩm định: {st.get('mssv', '')} ({idx + 1}/{total} bài — {percent}%)")

            local_dir = (
                st.get("local_dir") or st.get("source_file_path")
                or st.get("source_folder_path") or st.get("path")
            )
            result = self._engine.grade(
                live_url=st.get("live_url"),
                local_dir=local_dir,
                repo_url=st.get("repo_url"),
                mssv=st.get("mssv", ""),
                mode=st.get("mode", "HYBRID")
            )

            st["score_dom"] = result.score_dom
            st["score_lint"] = result.score_lint
            st["score_e2e"] = result.score_func
            st["score_ui"] = result.score_ui
            st["total_score"] = result.total_score
            st["verdict"] = result.verdict
            st["rubric_log"] = result.rubric_log
            st["ai_feedback"] = result.ai_feedback
            st["screenshot_path"] = result.screenshot_path
            self.graded_one.emit(st)

        self.all_done.emit(total)


# ==============================================================================
# 1. PILL HIỂN THỊ KẾT QUẢ ĐẠT / CHƯA ĐẠT (CHUẨN CHỮ THUẦN, KHÔNG DÙNG EMOJI)
# ==============================================================================
class WebVerdictPill(QWidget):
    """Custom pill widget to display Web assignment verdict matching Design System."""

    PALETTES = {
        "PASSED": (COLOR_SUCCESS_BG, COLOR_SUCCESS, "PASSED (Đạt Chuẩn)"),
        "PARTIAL": (COLOR_WARNING_BG, COLOR_WARNING, "PARTIAL (Một Phần)"),
        "FAILED": (COLOR_ERROR_BG, COLOR_ERROR, "FAILED (Chưa Đạt)"),
        "MISMATCH": (COLOR_WARNING_BG, COLOR_WARNING, "Lệch Mã Nguồn"),
        "PENDING": (COLOR_PRIMARY_BG, COLOR_PRIMARY, "Chờ Chấm Điểm")
    }

    def __init__(self, verdict: str = "PENDING", parent: Optional[QWidget] = None):
        super().__init__(parent)
        bg_color, text_color, label = self.PALETTES.get(verdict, self.PALETTES["PENDING"])

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl = QLabel(label, self)
        lbl.setFixedHeight(26)
        lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                font-weight: 600;
                font-size: 12px;
                border-radius: {RADIUS_PILL};
                padding: 4px 12px;
                border: 1px solid {text_color}33;
            }}
        """)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)


# ==============================================================================
# 2. HỘP THOẠI XEM CHI TIẾT THẨM ĐỊNH (CHUẨN CHỮ THUẦN, KHÔNG ICON)
# ==============================================================================
class WebDetailDialog(QDialog):
    """Clean Inspector Dialog for viewing rubric scores, screenshots and DOM logs."""

    def __init__(self, student_info: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.st = student_info
        self.regrade_requested = False
        self.score_override: Optional[Dict[str, float]] = None
        self.setWindowTitle(f"Chi Tiết Thẩm Định Web - {self.st.get('mssv')}")

        screen = QGuiApplication.primaryScreen()
        avail = screen.availableGeometry() if screen else None
        target_w = min(1040, (avail.width() - 40) if avail is not None else 1040)
        target_h = min(720, (avail.height() - 50) if avail is not None else 720)
        self.setMinimumSize(880, 560)
        self.resize(target_w, target_h)
        self.setStyleSheet(LIGHT_THEME_QSS)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header Info Card
        header = QFrame(self)
        header.setProperty("class", "Card")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(20, 16, 20, 16)
        h_layout.setSpacing(14)

        info_v = QVBoxLayout()
        info_v.setSpacing(6)
        mode_val = self.st.get("mode") or "HYBRID"
        mode_label = {"LIVE_ONLY": "Live URL", "REPO_ONLY": "GitHub", "HYBRID": "Hybrid"}.get(mode_val, mode_val)
        lbl_name = QLabel(f"Mã Số Sinh Viên: {self.st.get('mssv')}  |  Chế Độ: {mode_label}", header)
        lbl_name.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {COLOR_TEXT_PRIMARY};")

        live_val = self.st.get('live_url') or 'Chưa có'
        repo_val = self.st.get('repo_url') or 'Chưa có'
        lbl_links = QLabel(f"Live Website: {live_val} | GitHub Repo: {repo_val}", header)
        lbl_links.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 13px; line-height: 1.4;")

        info_v.addWidget(lbl_name)
        info_v.addWidget(lbl_links)
        h_layout.addLayout(info_v)
        h_layout.addStretch(1)

        # Verdict Badge
        h_layout.addWidget(WebVerdictPill(self.st.get("verdict") or "PENDING"))
        layout.addWidget(header)

        # Splitter: Rubric Criteria & Screenshot
        splitter = QSplitter(Qt.Orientation.Horizontal, self)

        # Left: 4 Criteria Breakdown Card
        left_card = QFrame(splitter)
        left_card.setProperty("class", "Card")
        lc_layout = QVBoxLayout(left_card)
        lc_layout.setContentsMargins(18, 16, 18, 16)
        lc_layout.setSpacing(12)

        lbl_r_t = QLabel("Bảng Điểm Chi Tiết Theo 4 Tiêu Chí:", left_card)
        lbl_r_t.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {COLOR_TEXT_PRIMARY};")
        lc_layout.addWidget(lbl_r_t)

        def add_criterion_row(name, score, desc, is_na=False):
            f = QFrame(left_card)
            f.setStyleSheet(f"background: {COLOR_SURFACE_SECONDARY}; border: 1px solid {COLOR_BORDER_LIGHT}; border-radius: 10px; padding: 10px;")
            fl = QVBoxLayout(f)
            fl.setContentsMargins(10, 8, 10, 8)
            fl.setSpacing(4)

            top_f = QHBoxLayout()
            lbl_cn = QLabel(name, f)
            lbl_cn.setStyleSheet(f"font-weight: 600; font-size: 13px; color: {COLOR_TEXT_PRIMARY};")
            if is_na:
                lbl_cs = QLabel("Không áp dụng", f)
                lbl_cs.setStyleSheet(f"font-weight: 600; font-size: 13px; color: {COLOR_TEXT_MUTED};")
            else:
                lbl_cs = QLabel(f"{score:.1f} / 10" if score is not None else "—", f)
                lbl_cs.setStyleSheet(f"font-weight: 700; font-size: 14px; color: {COLOR_PRIMARY};")
            top_f.addWidget(lbl_cn)
            top_f.addStretch(1)
            top_f.addWidget(lbl_cs)
            fl.addLayout(top_f)

            lbl_cd = QLabel(desc, f)
            lbl_cd.setWordWrap(True)
            lbl_cd.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 12px; line-height: 1.4;")
            fl.addWidget(lbl_cd)
            lc_layout.addWidget(f)

        is_repo_only = (mode_val == "REPO_ONLY")
        add_criterion_row("1. Cấu Trúc HTML & DOM", self.st.get("score_dom"), "Thẻ ngữ nghĩa (header, nav, main, footer), alt ảnh, heading hierarchy.")
        add_criterion_row("2. Chuẩn Hóa CSS / HTML Linting", self.st.get("score_lint"), "Kiểm tra cú pháp CSS bằng tinycss2, hạn chế inline-style, có media query responsive.")
        add_criterion_row("3. Chỉ Số Tương Tác JS", self.st.get("score_e2e"), "Thống kê script, addEventListener, onclick và các thành phần tương tác trong HTML (không chạy E2E thật).")
        add_criterion_row(
            "4. Thẩm Định Giao Diện UI/UX",
            self.st.get("score_ui"),
            "Chế độ GitHub không thẩm định UI/UX giao diện trình duyệt." if is_repo_only else "AI Vision đánh giá ảnh chụp toàn trang (viewport desktop 1440px) theo 4 tiêu chí thẩm mỹ.",
            is_na=is_repo_only
        )

        ai_feedback = (self.st.get("ai_feedback") or "").strip()
        if ai_feedback:
            fb = QFrame(left_card)
            fb.setStyleSheet(f"background: {COLOR_PRIMARY_BG}; border: 1px solid {COLOR_PRIMARY_LIGHT}; border-radius: 10px; padding: 10px;")
            fbl = QVBoxLayout(fb)
            fbl.setContentsMargins(10, 8, 10, 8)
            fbl.setSpacing(4)
            lbl_fb_t = QLabel("Nhận Xét Của AI Vision", fb)
            lbl_fb_t.setStyleSheet(f"font-weight: 700; font-size: 13px; color: {COLOR_PRIMARY};")
            lbl_fb_b = QLabel(ai_feedback, fb)
            lbl_fb_b.setWordWrap(True)
            lbl_fb_b.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 12px; line-height: 1.4;")
            fbl.addWidget(lbl_fb_t)
            fbl.addWidget(lbl_fb_b)
            lc_layout.addWidget(fb)
        lc_layout.addStretch(1)
        splitter.addWidget(left_card)

        # Right: Log & Visual Evidence
        right_card = QFrame(splitter)
        right_card.setProperty("class", "Card")
        rc_layout = QVBoxLayout(right_card)
        rc_layout.setContentsMargins(18, 16, 18, 16)
        rc_layout.setSpacing(10)

        lbl_sc_t = QLabel("Ảnh Chụp Giao Diện & Nhật Ký Thẩm Định:", right_card)
        lbl_sc_t.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {COLOR_TEXT_PRIMARY};")
        rc_layout.addWidget(lbl_sc_t)

        screenshot_path = self.st.get("screenshot_path")
        has_shot = bool(screenshot_path and Path(screenshot_path).is_file())
        if has_shot:
            shot_row = QHBoxLayout()
            shot_row.addStretch(1)
            btn_open_shot = QPushButton("Mở Ảnh Chụp Gốc", right_card)
            btn_open_shot.setProperty("class", "SecondaryBtn")
            btn_open_shot.setFixedHeight(30)
            btn_open_shot.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_open_shot.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(screenshot_path)))
            shot_row.addWidget(btn_open_shot)
            rc_layout.addLayout(shot_row)

        lbl_shot = QLabel(right_card)
        lbl_shot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_shot.setStyleSheet(f"background: {COLOR_SURFACE_SECONDARY}; border: 1px solid {COLOR_BORDER_LIGHT}; border-radius: 8px;")
        lbl_shot.setMinimumHeight(150)
        if has_shot:
            pm = QPixmap(screenshot_path)
            if not pm.isNull():
                lbl_shot.setPixmap(pm.scaled(520, 260, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                lbl_shot.setText("Không đọc được ảnh chụp màn hình.")
        else:
            lbl_shot.setText("Chưa có ảnh chụp màn hình (chấm bằng Playwright Chromium để sinh ảnh).")
            lbl_shot.setWordWrap(True)
            lbl_shot.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px; background: {COLOR_SURFACE_SECONDARY}; border: 1px solid {COLOR_BORDER_LIGHT}; border-radius: 8px; padding: 12px;")
        rc_layout.addWidget(lbl_shot)

        txt_log = QTextEdit(right_card)
        txt_log.setReadOnly(True)
        txt_log.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLOR_SURFACE_SECONDARY};
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid {COLOR_BORDER_DEFAULT};
                border-radius: 8px;
                font-family: Consolas, monospace;
                font-size: 12px;
                line-height: 1.5;
                padding: 10px;
            }}
        """)
        txt_log.setPlainText(
            self.st.get("rubric_log")
            or "Chưa có nhật ký thẩm định. Hãy chạy 'Bắt Đầu Thẩm Định Web' để sinh nhật ký."
        )
        rc_layout.addWidget(txt_log)
        splitter.addWidget(right_card)

        splitter.setSizes([480, 500])
        layout.addWidget(splitter, stretch=1)

        # Footer
        footer = QHBoxLayout()
        footer.setSpacing(10)
        footer.addStretch(1)

        btn_override = QPushButton("Sửa Điểm Thủ Công", self)
        btn_override.setProperty("class", "SecondaryBtn")
        btn_override.setFixedHeight(36)
        btn_override.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_override.clicked.connect(self._request_override)
        footer.addWidget(btn_override)

        btn_regrade = QPushButton("Chấm Lại Bài Này", self)
        btn_regrade.setProperty("class", "SecondaryBtn")
        btn_regrade.setFixedHeight(36)
        btn_regrade.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_regrade.clicked.connect(self._request_regrade)
        footer.addWidget(btn_regrade)

        btn_close = QPushButton("Đóng", self)
        btn_close.setProperty("class", "PrimaryBtn")
        btn_close.setFixedHeight(36)
        btn_close.clicked.connect(self.accept)
        footer.addWidget(btn_close)
        layout.addLayout(footer)

    def _request_override(self):
        dlg = WebScoreOverrideDialog(self.st, self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.scores:
            self.score_override = dlg.scores
            self.accept()

    def _request_regrade(self):
        self.regrade_requested = True
        self.accept()


# ==============================================================================
# 4. HỘP THOẠI SỬA ĐIỂM THỦ CÔNG (GIẢNG VIÊN GHI ĐÈ ĐIỂM RUBRIC)
# ==============================================================================
class WebScoreOverrideDialog(QDialog):
    """Lets an instructor override the 4 rubric scores; total & verdict are recomputed live."""

    WEIGHTS = {"dom": 0.2, "lint": 0.2, "func": 0.3, "ui": 0.3}

    def __init__(self, student_info: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.st = student_info
        self.scores: Optional[Dict[str, float]] = None
        self.mode = self.st.get("mode") or "HYBRID"
        self.setWindowTitle(f"Sửa Điểm Thủ Công - {self.st.get('mssv')}")
        self.setMinimumWidth(460)
        self.setStyleSheet(LIGHT_THEME_QSS)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(14)

        if self.mode == "REPO_ONLY":
            note_text = (
                "Chế độ GitHub: Tiêu chí UI/UX không áp dụng. "
                "Tổng điểm quy đổi thang 10 theo trọng số DOM 20% / Lint 20% / Function 30% (chia 0.7)."
            )
        else:
            note_text = (
                "Điểm do giảng viên nhập sẽ ghi đè điểm rubric tự động. "
                "Tổng điểm và kết quả (PASSED/PARTIAL/FAILED) được tính theo trọng số "
                "DOM 20% / Lint 20% / Function 30% / UI 30%."
            )
        note = QLabel(note_text, self)
        note.setWordWrap(True)
        note.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 12px; line-height: 1.4;")
        layout.addWidget(note)

        form = QFormLayout()
        form.setSpacing(10)
        self.spin_dom = self._make_spin(self.st.get("score_dom"))
        self.spin_lint = self._make_spin(self.st.get("score_lint"))
        self.spin_func = self._make_spin(self.st.get("score_e2e"))
        self.spin_ui = self._make_spin(self.st.get("score_ui"))
        if self.mode == "REPO_ONLY":
            self.spin_ui.setEnabled(False)
            self.spin_ui.setToolTip("Không áp dụng cho chế độ GitHub (không tính vào tổng điểm)")

        form.addRow("1. Cấu trúc HTML & DOM:", self.spin_dom)
        form.addRow("2. Chuẩn hóa CSS / Lint:", self.spin_lint)
        form.addRow("3. Chỉ số tương tác JS:", self.spin_func)
        form.addRow("4. Giao diện UI/UX:", self.spin_ui)
        layout.addLayout(form)

        self.lbl_total = QLabel(self)
        self.lbl_total.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {COLOR_PRIMARY};")
        layout.addWidget(self.lbl_total)

        footer = QHBoxLayout()
        footer.addStretch(1)
        btn_cancel = QPushButton("Hủy", self)
        btn_cancel.setProperty("class", "SecondaryBtn")
        btn_cancel.setFixedHeight(36)
        btn_cancel.clicked.connect(self.reject)
        footer.addWidget(btn_cancel)

        btn_save = QPushButton("Lưu Điểm", self)
        btn_save.setProperty("class", "PrimaryBtn")
        btn_save.setFixedHeight(36)
        btn_save.clicked.connect(self._save)
        footer.addWidget(btn_save)
        layout.addLayout(footer)

        self._recompute()

    def _make_spin(self, value) -> QDoubleSpinBox:
        spin = QDoubleSpinBox(self)
        spin.setRange(0.0, 10.0)
        spin.setDecimals(1)
        spin.setSingleStep(0.5)
        spin.setValue(float(value) if value is not None else 0.0)
        spin.valueChanged.connect(self._recompute)
        return spin

    def _recompute(self):
        dom = self.spin_dom.value()
        lint = self.spin_lint.value()
        func = self.spin_func.value()
        ui = self.spin_ui.value()
        if self.mode == "REPO_ONLY":
            total = round((dom * 0.2 + lint * 0.2 + func * 0.3) / 0.7, 2)
        else:
            total = round(dom * 0.2 + lint * 0.2 + func * 0.3 + ui * 0.3, 2)
        verdict = "PASSED" if total >= 7.0 else ("PARTIAL" if total >= 5.0 else "FAILED")
        self.lbl_total.setText(f"Tổng điểm: {total:.1f} / 10  →  {verdict}")

    def _save(self):
        self.scores = {
            "score_dom": self.spin_dom.value(),
            "score_lint": self.spin_lint.value(),
            "score_func": self.spin_func.value(),
            "score_ui": None if self.mode == "REPO_ONLY" else self.spin_ui.value(),
        }
        self.accept()


# ==============================================================================
# 5. HỘP THOẠI THÊM / SỬA BÀI NỘP & DÁN NHIỀU LINK (KHÔNG DÙNG CSV)
# ==============================================================================
class WebSubmissionDialog(QDialog):
    """
    Dialog for adding/editing a single web submission or pasting multiple links from Excel/Sheets.
    Strictly conforms to rules:
    - No student name (MSSV only).
    - Titles display current grading mode: 'Live URL', 'GitHub', 'Hybrid'.
    - Single tab: only fields belonging to the current mode are shown; others are hidden completely.
    - Bulk tab: format strictly adapted to the mode, with preview table, red rows on error, and Add All button.
    - Real-time inline validation with descriptive messages below inputs.
    """

    MODE_NAMES = {
        "LIVE_ONLY": "Live URL",
        "REPO_ONLY": "GitHub",
        "HYBRID": "Hybrid"
    }

    def __init__(
        self,
        parent=None,
        current_mode: str = "HYBRID",
        existing_item: Optional[Dict[str, Any]] = None,
        existing_mssvs: Optional[List[str]] = None,
        open_bulk_tab: bool = False
    ):
        super().__init__(parent)
        self.current_mode = (current_mode or "HYBRID").upper()
        if self.current_mode not in self.MODE_NAMES:
            self.current_mode = "HYBRID"
        self.existing_item = existing_item
        self.is_edit_mode = existing_item is not None
        self.existing_mssvs = set(m.upper() for m in (existing_mssvs or []))
        if self.existing_item and self.existing_item.get("mssv"):
            self.existing_mssvs.discard(self.existing_item.get("mssv", "").upper())

        self.added_submissions: List[Dict[str, Any]] = []

        mode_label = self.MODE_NAMES.get(self.current_mode, "Hybrid")
        title = f"Sửa Bài Nộp - Chế độ: {mode_label}" if self.is_edit_mode else f"Thêm Bài Nộp - Chế độ: {mode_label}"
        self.setWindowTitle(title)

        screen = QGuiApplication.primaryScreen()
        avail = screen.availableGeometry() if screen else None
        target_w = min(820, (avail.width() - 40) if avail is not None else 820)
        target_h = min(640, (avail.height() - 50) if avail is not None else 640)
        self.setMinimumSize(720, 520)
        self.resize(target_w, target_h)
        self.setStyleSheet(LIGHT_THEME_QSS)

        self._init_ui(open_bulk_tab)

    def _init_ui(self, open_bulk_tab: bool):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        self.tabs = QTabWidget(self)
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLOR_BORDER_DEFAULT};
                border-radius: 8px;
                background-color: #FFFFFF;
                padding: 12px;
            }}
            QTabBar::tab {{
                background: {COLOR_SURFACE_SECONDARY};
                color: {COLOR_TEXT_SECONDARY};
                font-size: 13px;
                font-weight: 600;
                padding: 8px 18px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 4px;
            }}
            QTabBar::tab:selected {{
                background: #FFFFFF;
                color: {COLOR_PRIMARY};
                border: 1px solid {COLOR_BORDER_DEFAULT};
                border-bottom: 2px solid {COLOR_PRIMARY};
            }}
        """)

        # Tab 1: Form Thêm / Sửa đơn lẻ
        tab_single = QWidget()
        self._init_single_tab(tab_single)
        tab_label = "Sửa Thông Tin Bài Nộp" if self.is_edit_mode else "Thêm Từng Bài"
        self.tabs.addTab(tab_single, tab_label)

        # Tab 2: Dán nhiều dòng (chỉ hiển thị khi thêm mới)
        if not self.is_edit_mode:
            tab_bulk = QWidget()
            self._init_bulk_tab(tab_bulk)
            self.tabs.addTab(tab_bulk, "Dán Nhiều Dòng")
            if open_bulk_tab:
                self.tabs.setCurrentIndex(1)

        layout.addWidget(self.tabs, stretch=1)

    def _init_single_tab(self, parent: QWidget):
        vbox = QVBoxLayout(parent)
        vbox.setContentsMargins(12, 12, 12, 12)
        vbox.setSpacing(12)

        # Khi sửa bài: cho phép đổi chế độ của bài nộp đó
        if self.is_edit_mode:
            lbl_m = QLabel("Chế Độ Chấm:", parent)
            lbl_m.setStyleSheet(f"font-weight: 600; font-size: 13px; color: {COLOR_TEXT_PRIMARY};")
            self.combo_mode = QComboBox(parent)
            self.combo_mode.setFixedHeight(36)
            self.combo_mode.addItem("Live URL", "LIVE_ONLY")
            self.combo_mode.addItem("GitHub", "REPO_ONLY")
            self.combo_mode.addItem("Hybrid", "HYBRID")

            # Set current selection
            idx = 2
            if self.current_mode == "LIVE_ONLY":
                idx = 0
            elif self.current_mode == "REPO_ONLY":
                idx = 1
            self.combo_mode.setCurrentIndex(idx)
            self.combo_mode.currentIndexChanged.connect(self._on_single_mode_changed)

            vbox.addWidget(lbl_m)
            vbox.addWidget(self.combo_mode)

        # 1. Ô MSSV
        lbl_mssv = QLabel("Mã Số Sinh Viên (MSSV):", parent)
        lbl_mssv.setStyleSheet(f"font-weight: 600; font-size: 13px; color: {COLOR_TEXT_PRIMARY};")
        self.txt_mssv = QLineEdit(parent)
        self.txt_mssv.setFixedHeight(38)
        self.txt_mssv.setPlaceholderText("Ví dụ: SE180123")
        self.lbl_err_mssv = QLabel("", parent)
        self.lbl_err_mssv.setStyleSheet(f"color: {COLOR_ERROR}; font-size: 11px;")
        self.lbl_err_mssv.setVisible(False)
        self.txt_mssv.textChanged.connect(self._validate_single_form)
        vbox.addWidget(lbl_mssv)
        vbox.addWidget(self.txt_mssv)
        vbox.addWidget(self.lbl_err_mssv)

        # 2. Ô Live URL (chỉ hiện khi thuộc chế độ)
        self.lbl_live = QLabel("Live Website URL:", parent)
        self.lbl_live.setStyleSheet(f"font-weight: 600; font-size: 13px; color: {COLOR_TEXT_PRIMARY};")
        self.txt_live = QLineEdit(parent)
        self.txt_live.setFixedHeight(38)
        self.txt_live.setPlaceholderText("https://ten-du-an.vercel.app")
        self.lbl_err_live = QLabel("", parent)
        self.lbl_err_live.setStyleSheet(f"color: {COLOR_ERROR}; font-size: 11px;")
        self.lbl_err_live.setVisible(False)
        self.txt_live.textChanged.connect(self._validate_single_form)
        vbox.addWidget(self.lbl_live)
        vbox.addWidget(self.txt_live)
        vbox.addWidget(self.lbl_err_live)

        # 3. Ô GitHub Repo (chỉ hiện khi thuộc chế độ)
        self.lbl_repo = QLabel("GitHub Repository URL:", parent)
        self.lbl_repo.setStyleSheet(f"font-weight: 600; font-size: 13px; color: {COLOR_TEXT_PRIMARY};")
        self.txt_repo = QLineEdit(parent)
        self.txt_repo.setFixedHeight(38)
        self.txt_repo.setPlaceholderText("https://github.com/username/repository")
        self.lbl_err_repo = QLabel("", parent)
        self.lbl_err_repo.setStyleSheet(f"color: {COLOR_ERROR}; font-size: 11px;")
        self.lbl_err_repo.setVisible(False)
        self.txt_repo.textChanged.connect(self._validate_single_form)
        vbox.addWidget(self.lbl_repo)
        vbox.addWidget(self.txt_repo)
        vbox.addWidget(self.lbl_err_repo)

        vbox.addStretch(1)

        # Nút Lưu và Hủy
        btn_box = QHBoxLayout()
        btn_box.setSpacing(12)
        btn_box.addStretch(1)

        btn_cancel = QPushButton("Hủy", parent)
        btn_cancel.setProperty("class", "SecondaryBtn")
        btn_cancel.setFixedHeight(38)
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_cancel)

        self.btn_save_single = QPushButton("Lưu", parent)
        self.btn_save_single.setProperty("class", "PrimaryBtn")
        self.btn_save_single.setFixedHeight(38)
        self.btn_save_single.clicked.connect(self._save_single_submission)
        btn_box.addWidget(self.btn_save_single)
        vbox.addLayout(btn_box)

        # Nạp dữ liệu cũ nếu ở chế độ sửa
        if self.is_edit_mode and self.existing_item:
            self.txt_mssv.setText(self.existing_item.get("mssv", ""))
            self.txt_live.setText(self.existing_item.get("live_url", ""))
            self.txt_repo.setText(self.existing_item.get("repo_url", ""))

        self._update_single_field_visibility()
        self._validate_single_form()

    def _on_single_mode_changed(self):
        new_mode = self.combo_mode.currentData()
        if new_mode:
            self.current_mode = new_mode
            mode_label = self.MODE_NAMES.get(self.current_mode, "Hybrid")
            self.setWindowTitle(f"Sửa Bài Nộp - Chế độ: {mode_label}")
            self._update_single_field_visibility()
            self._validate_single_form()

    def _update_single_field_visibility(self):
        show_live = (self.current_mode in ("LIVE_ONLY", "HYBRID"))
        show_repo = (self.current_mode in ("REPO_ONLY", "HYBRID"))

        self.lbl_live.setVisible(show_live)
        self.txt_live.setVisible(show_live)
        if not show_live:
            self.lbl_err_live.setVisible(False)
            self.txt_live.setStyleSheet("")

        self.lbl_repo.setVisible(show_repo)
        self.txt_repo.setVisible(show_repo)
        if not show_repo:
            self.lbl_err_repo.setVisible(False)
            self.txt_repo.setStyleSheet("")

    def _validate_single_form(self) -> bool:
        """Real-time validation for single entry form."""
        is_valid = True

        # 1. Validate MSSV
        raw_mssv = self.txt_mssv.text().strip().upper()
        if not raw_mssv:
            self.lbl_err_mssv.setText("Mã số sinh viên không được để trống.")
            self.lbl_err_mssv.setVisible(True)
            self.txt_mssv.setStyleSheet(f"border: 1.5px solid {COLOR_ERROR};")
            is_valid = False
        elif raw_mssv in self.existing_mssvs:
            self.lbl_err_mssv.setText("MSSV này đã tồn tại trong danh sách bài nộp.")
            self.lbl_err_mssv.setVisible(True)
            self.txt_mssv.setStyleSheet(f"border: 1.5px solid {COLOR_ERROR};")
            is_valid = False
        else:
            self.lbl_err_mssv.setVisible(False)
            self.txt_mssv.setStyleSheet("")

        # 2. Validate Live URL
        show_live = (self.current_mode in ("LIVE_ONLY", "HYBRID"))
        if show_live:
            live_url = self.txt_live.text().strip()
            if not live_url:
                self.lbl_err_live.setText("Vui lòng nhập Live Website URL.")
                self.lbl_err_live.setVisible(True)
                self.txt_live.setStyleSheet(f"border: 1.5px solid {COLOR_ERROR};")
                is_valid = False
            elif not (live_url.startswith("http://") or live_url.startswith("https://")):
                self.lbl_err_live.setText("URL phải bắt đầu bằng http:// hoặc https://")
                self.lbl_err_live.setVisible(True)
                self.txt_live.setStyleSheet(f"border: 1.5px solid {COLOR_ERROR};")
                is_valid = False
            else:
                self.lbl_err_live.setVisible(False)
                self.txt_live.setStyleSheet("")

        # 3. Validate GitHub Repo
        show_repo = (self.current_mode in ("REPO_ONLY", "HYBRID"))
        if show_repo:
            repo_url = self.txt_repo.text().strip()
            kind, _, err_msg = classify_url(repo_url)
            if not repo_url:
                self.lbl_err_repo.setText("Vui lòng nhập GitHub Repository URL.")
                self.lbl_err_repo.setVisible(True)
                self.txt_repo.setStyleSheet(f"border: 1.5px solid {COLOR_ERROR};")
                is_valid = False
            elif kind != "repo":
                self.lbl_err_repo.setText(err_msg or "GitHub Repo phải đúng dạng github.com/<user>/<repo>")
                self.lbl_err_repo.setVisible(True)
                self.txt_repo.setStyleSheet(f"border: 1.5px solid {COLOR_ERROR};")
                is_valid = False
            else:
                self.lbl_err_repo.setVisible(False)
                self.txt_repo.setStyleSheet("")

        self.btn_save_single.setEnabled(is_valid)
        return is_valid

    def _save_single_submission(self):
        if not self._validate_single_form():
            return

        live_url = self.txt_live.text().strip() if self.current_mode in ("LIVE_ONLY", "HYBRID") else ""
        repo_url = self.txt_repo.text().strip() if self.current_mode in ("REPO_ONLY", "HYBRID") else ""
        if repo_url:
            _, normalized_repo, _ = classify_url(repo_url)
            repo_url = normalized_repo

        item = {
            "mssv": self.txt_mssv.text().strip().upper(),
            "name": "",
            "live_url": live_url,
            "repo_url": repo_url,
            "mode": self.current_mode,
            "score_dom": self.existing_item.get("score_dom") if self.existing_item else None,
            "score_lint": self.existing_item.get("score_lint") if self.existing_item else None,
            "score_e2e": self.existing_item.get("score_e2e") if self.existing_item else None,
            "score_ui": self.existing_item.get("score_ui") if self.existing_item else None,
            "total_score": self.existing_item.get("total_score") if self.existing_item else None,
            "verdict": self.existing_item.get("verdict", "PENDING") if self.existing_item else "PENDING"
        }
        if self.is_edit_mode and self.existing_item and "id" in self.existing_item:
            item["id"] = self.existing_item["id"]

        self.added_submissions = [item]
        self.accept()

    # --------------------------------------------------------------------------
    # Tab 2: Dán Nhiều Dòng
    # --------------------------------------------------------------------------
    def _init_bulk_tab(self, parent: QWidget):
        vbox = QVBoxLayout(parent)
        vbox.setContentsMargins(12, 12, 12, 12)
        vbox.setSpacing(12)

        # Hướng dẫn theo chế độ
        if self.current_mode == "LIVE_ONLY":
            instruct_text = (
                "Dán danh sách sinh viên: mỗi dòng một sinh viên gồm MSSV, Live URL (phân tách bởi dấu phẩy hoặc tab).\n"
                "Định dạng mẫu: MSSV, link web"
            )
            placeholder_text = "SE180001, https://my-web.vercel.app\nSE180002, https://my-shop.netlify.app"
        elif self.current_mode == "REPO_ONLY":
            instruct_text = (
                "Dán danh sách sinh viên: mỗi dòng một sinh viên gồm MSSV, GitHub Repo (phân tách bởi dấu phẩy hoặc tab).\n"
                "Định dạng mẫu: MSSV, link repo"
            )
            placeholder_text = "SE180001, https://github.com/sinhvien/web-project\nSE180002, https://github.com/sinhvien/ecommerce"
        else: # HYBRID
            instruct_text = (
                "Dán danh sách sinh viên: mỗi dòng gồm MSSV, link web, link repo (phân tách bởi dấu phẩy hoặc tab).\n"
                "Hệ thống tự nhận diện link github.com là repo, link còn lại là web (không phụ thuộc thứ tự)."
            )
            placeholder_text = (
                "SE180001, https://my-web.vercel.app, https://github.com/sinhvien/web-project\n"
                "SE180002, https://github.com/sinhvien/ecommerce, https://my-shop.netlify.app"
            )

        lbl_instruct = QLabel(instruct_text, parent)
        lbl_instruct.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 13px; line-height: 1.4;")
        vbox.addWidget(lbl_instruct)

        self.txt_bulk = QTextEdit(parent)
        self.txt_bulk.setPlaceholderText(placeholder_text)
        self.txt_bulk.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLOR_SURFACE_SECONDARY};
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid {COLOR_BORDER_DEFAULT};
                border-radius: 8px;
                font-family: Consolas, monospace;
                font-size: 13px;
                line-height: 1.4;
                padding: 10px;
            }}
        """)
        vbox.addWidget(self.txt_bulk, stretch=2)

        # Hàng nút Xem trước & tóm tắt
        preview_bar = QHBoxLayout()
        preview_bar.setSpacing(12)
        btn_preview = QPushButton("Xem Trước", parent)
        btn_preview.setProperty("class", "SecondaryBtn")
        btn_preview.setFixedHeight(36)
        btn_preview.clicked.connect(self._preview_bulk_entries)
        preview_bar.addWidget(btn_preview)

        self.lbl_bulk_summary = QLabel("Chưa phân tích nội dung.", parent)
        self.lbl_bulk_summary.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px; font-weight: 500;")
        preview_bar.addWidget(self.lbl_bulk_summary)
        preview_bar.addStretch(1)
        vbox.addLayout(preview_bar)

        # Bảng xem trước kết quả
        self.tbl_preview = QTableWidget(parent)
        if self.current_mode == "LIVE_ONLY":
            headers = ["MSSV", "Live URL", "Trạng Thái"]
        elif self.current_mode == "REPO_ONLY":
            headers = ["MSSV", "GitHub Repo", "Trạng Thái"]
        else:
            headers = ["MSSV", "Live URL", "GitHub Repo", "Trạng Thái"]

        self.tbl_preview.setColumnCount(len(headers))
        self.tbl_preview.setHorizontalHeaderLabels(headers)
        p_header = self.tbl_preview.horizontalHeader()
        p_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.tbl_preview.setColumnWidth(0, 110)
        if len(headers) == 3:
            p_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            p_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
            self.tbl_preview.setColumnWidth(2, 220)
        else:
            p_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            p_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            p_header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
            self.tbl_preview.setColumnWidth(3, 220)

        self.tbl_preview.verticalHeader().setVisible(False)
        self.tbl_preview.setShowGrid(True)
        vbox.addWidget(self.tbl_preview, stretch=3)

        # Hàng nút lưu
        footer = QHBoxLayout()
        footer.setSpacing(12)
        footer.addStretch(1)

        btn_cancel = QPushButton("Hủy", parent)
        btn_cancel.setProperty("class", "SecondaryBtn")
        btn_cancel.setFixedHeight(38)
        btn_cancel.clicked.connect(self.reject)
        footer.addWidget(btn_cancel)

        self.btn_add_all = QPushButton("Thêm Tất Cả", parent)
        self.btn_add_all.setProperty("class", "PrimaryBtn")
        self.btn_add_all.setFixedHeight(38)
        self.btn_add_all.setEnabled(False)
        self.btn_add_all.clicked.connect(self._commit_bulk_entries)
        footer.addWidget(self.btn_add_all)
        vbox.addLayout(footer)

    def _preview_bulk_entries(self):
        raw_text = self.txt_bulk.toPlainText().strip()
        if not raw_text:
            QMessageBox.information(
                self, "Chưa Nhập Dữ Liệu",
                "Vui lòng dán danh sách sinh viên vào ô trước khi bấm 'Xem Trước'!"
            )
            return

        lines = raw_text.splitlines()
        self.tbl_preview.setRowCount(0)
        parsed_valid: List[Dict[str, Any]] = []
        seen_mssvs_in_batch = set()
        error_count = 0

        for line_idx, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            if "\t" in line:
                parts = [p.strip() for p in line.split("\t") if p.strip()]
            else:
                parts = [p.strip() for p in line.split(",") if p.strip()]

            raw_mssv = parts[0].upper() if len(parts) > 0 else ""
            row_errs = []

            # 1. Check MSSV
            if not raw_mssv:
                row_errs.append("Thiếu MSSV")
            elif raw_mssv in self.existing_mssvs:
                row_errs.append("Trùng MSSV trong bảng")
            elif raw_mssv in seen_mssvs_in_batch:
                row_errs.append("Trùng MSSV trong danh sách dán")

            live_url = ""
            repo_url = ""

            if self.current_mode == "LIVE_ONLY":
                if len(parts) < 2:
                    row_errs.append("Thiếu Live URL")
                else:
                    live_candidate = parts[1]
                    if not (live_candidate.startswith("http://") or live_candidate.startswith("https://")):
                        row_errs.append("Live URL sai định dạng")
                    else:
                        live_url = live_candidate

            elif self.current_mode == "REPO_ONLY":
                if len(parts) < 2:
                    row_errs.append("Thiếu GitHub Repo")
                else:
                    repo_candidate = parts[1]
                    kind, normalized, err_msg = classify_url(repo_candidate)
                    if kind != "repo":
                        row_errs.append(err_msg or "GitHub Repo sai dạng")
                    else:
                        repo_url = normalized

            else: # HYBRID
                links = parts[1:]
                if len(links) < 2:
                    row_errs.append("Cần cả Live URL và GitHub Repo")
                else:
                    for lk in links[:2]:
                        kind, norm, _ = classify_url(lk)
                        if kind == "repo" and not repo_url:
                            repo_url = norm
                        elif (lk.startswith("http://") or lk.startswith("https://")) and not live_url:
                            live_url = lk
                    if not live_url:
                        row_errs.append("Thiếu Live URL")
                    if not repo_url:
                        row_errs.append("Thiếu GitHub Repo")

            r = self.tbl_preview.rowCount()
            self.tbl_preview.insertRow(r)
            self.tbl_preview.setRowHeight(r, 36)

            item_mssv = QTableWidgetItem(raw_mssv)
            row_items = [item_mssv]

            if self.current_mode == "LIVE_ONLY":
                item_live = QTableWidgetItem(live_url or (parts[1] if len(parts) > 1 else ""))
                row_items.append(item_live)
            elif self.current_mode == "REPO_ONLY":
                item_repo = QTableWidgetItem(repo_url or (parts[1] if len(parts) > 1 else ""))
                row_items.append(item_repo)
            else:
                item_live = QTableWidgetItem(live_url)
                item_repo = QTableWidgetItem(repo_url)
                row_items.extend([item_live, item_repo])

            if row_errs:
                error_count += 1
                err_text = "Lỗi: " + ", ".join(row_errs)
                item_status = QTableWidgetItem(err_text)
                item_status.setForeground(QColor(COLOR_ERROR))
                for itm in row_items:
                    itm.setForeground(QColor(COLOR_ERROR))
            else:
                seen_mssvs_in_batch.add(raw_mssv)
                item_status = QTableWidgetItem("Hợp lệ")
                item_status.setForeground(QColor(COLOR_SUCCESS))
                parsed_valid.append({
                    "mssv": raw_mssv,
                    "name": "",
                    "live_url": live_url,
                    "repo_url": repo_url,
                    "mode": self.current_mode,
                    "score_dom": None,
                    "score_lint": None,
                    "score_e2e": None,
                    "score_ui": None,
                    "total_score": None,
                    "verdict": "PENDING"
                })

            row_items.append(item_status)
            for c_idx, itm in enumerate(row_items):
                self.tbl_preview.setItem(r, c_idx, itm)

        self.added_submissions = parsed_valid
        if error_count > 0:
            self.lbl_bulk_summary.setText(
                f"Phát hiện {len(parsed_valid)} dòng hợp lệ, {error_count} dòng lỗi (tô đỏ). Vui lòng sửa lỗi trước khi thêm!"
            )
            self.lbl_bulk_summary.setStyleSheet(f"color: {COLOR_ERROR}; font-size: 12px; font-weight: 600;")
            self.btn_add_all.setEnabled(False)
        else:
            self.lbl_bulk_summary.setText(f"Hoàn hảo: Toàn bộ {len(parsed_valid)} bài nộp đều hợp lệ sẵn sàng thêm.")
            self.lbl_bulk_summary.setStyleSheet(f"color: {COLOR_SUCCESS}; font-size: 12px; font-weight: 600;")
            self.btn_add_all.setEnabled(len(parsed_valid) > 0)

    def _commit_bulk_entries(self):
        if not self.added_submissions:
            return
        self.accept()


# ==============================================================================
# 4. CỬA SỔ CHÍNH - WEB STUDIO (CHẤM BÀI TẬP & ĐỒ ÁN WEB)
# ==============================================================================
class WebGradingMainWindow(QMainWindow):
    """
    Dedicated Web Assignment Studio Window matching Design System:
    Clean 240px Sidebar + Top Header 64px + Link-based Submissions + Responsive Layout.
    Conforms 100% to rules A -> H.
    """

    def __init__(self, session_info: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.session_info = session_info or {
            "mode": "ONLINE",
            "username": "instructor",
            "display_name": "Giảng Viên",
        }

        self.setWindowTitle("AITA - Chấm Bài Tập & Đồ Án Web")

        # Căn chỉnh kích thước cửa sổ dựa theo vùng hiển thị thực tế của màn hình (tránh taskbar che)
        screen = QGuiApplication.primaryScreen()
        avail = screen.availableGeometry() if screen else None
        target_w = min(1380, (avail.width() - 30) if avail is not None else 1380)
        target_h = min(840, (avail.height() - 40) if avail is not None else 840)
        self.setMinimumSize(1100, 700)
        self.resize(target_w, target_h)
        if avail is not None:
            self.move(avail.x() + (avail.width() - target_w) // 2,
                      avail.y() + (avail.height() - target_h) // 2)

        self.setStyleSheet(LIGHT_THEME_QSS)

        # Giữ context môn học / đợt chấm; nhớ lại giữa các phiên qua QSettings
        self.current_assignment_title = "Đồ Án Thiết Kế Web Responsive (HTML/CSS/JS)"

        self.db = DatabaseManager()
        self._web_students: List[Dict[str, Any]] = []
        self._settings = QSettings("AITA", "WebGrading")
        self.current_course_code = self._settings.value("course_code", "WEB201c") or "WEB201c"
        self.current_class_name = self._settings.value("class_name", "SE1806") or "SE1806"
        self._web_root_folder: Optional[str] = self._settings.value("root_folder") or None

        self._init_ui()
        if self._web_root_folder:
            self.btn_rescan_folder.setVisible(True)
        self._update_class_button()
        self._load_submissions_from_db()
        self._refresh_ai_quota()

    # --------------------------------------------------------------------------
    # Khởi tạo giao diện chính
    # --------------------------------------------------------------------------
    def _init_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        master_layout = QHBoxLayout(central)
        master_layout.setContentsMargins(0, 0, 0, 0)
        master_layout.setSpacing(0)

        # 1. Sidebar (240px)
        master_layout.addWidget(self._build_sidebar())

        # 2. Right Content Area (Bao bọc trong QScrollArea để chống cắt chữ / tràn màn hình)
        right_container = QWidget(self)
        rc_layout = QVBoxLayout(right_container)
        rc_layout.setContentsMargins(0, 0, 0, 0)
        rc_layout.setSpacing(0)

        # Top Header (64px)
        rc_layout.addWidget(self._build_top_header())

        # Main Scrollable Canvas
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { background-color: #F8FAFC; border: none; }")

        content_canvas = QWidget()
        content_canvas.setObjectName("CentralCanvas")
        c_layout = QVBoxLayout(content_canvas)
        c_layout.setContentsMargins(24, 20, 24, 20)
        c_layout.setSpacing(16)

        # Action Toolbar (Controls & 3 Modes)
        c_layout.addWidget(self._build_toolbar())

        # Progress Card (Thanh tiến độ 10-12px)
        c_layout.addWidget(self._build_progress_card())

        # Submissions Table Card (Chứa Table + Empty State Overlay)
        c_layout.addWidget(self._build_table_card(), stretch=1)

        scroll_area.setWidget(content_canvas)
        rc_layout.addWidget(scroll_area, stretch=1)

        master_layout.addWidget(right_container, stretch=1)

    # --------------------------------------------------------------------------
    # G. Sidebar: Logo W, Logo FPT University, Bảng Điểm Đồ Án Web, Đổi Chế Độ
    # --------------------------------------------------------------------------
    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame(self)
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(240)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(8)

        # 1. Logo W & Web Studio Area
        logo_area = QFrame(sidebar)
        logo_area.setFixedHeight(64)
        la_layout = QHBoxLayout(logo_area)
        la_layout.setContentsMargins(6, 0, 6, 0)
        la_layout.setSpacing(12)

        _avatar_pm = make_aita_avatar_pixmap(38, 10)
        if _avatar_pm is not None:
            avatar_label = QLabel(logo_area)
            avatar_label.setPixmap(_avatar_pm)
            avatar_label.setFixedSize(38, 38)
            la_layout.addWidget(avatar_label)
        else:
            logo_icon = QFrame(logo_area)
            logo_icon.setFixedSize(38, 38)
            logo_icon.setStyleSheet(f"background-color: {COLOR_PRIMARY}; border-radius: 10px;")
            li_layout = QHBoxLayout(logo_icon)
            li_layout.setContentsMargins(0, 0, 0, 0)
            lbl_li = QLabel("W", logo_icon)
            lbl_li.setStyleSheet("color: #FFFFFF; font-size: 18px; font-weight: 800;")
            lbl_li.setAlignment(Qt.AlignmentFlag.AlignCenter)
            li_layout.addWidget(lbl_li)
            la_layout.addWidget(logo_icon)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        lbl_app = QLabel("Web Studio", logo_area)
        lbl_app.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {COLOR_TEXT_PRIMARY};")
        lbl_sub = QLabel("Chấm Đồ Án Web", logo_area)
        lbl_sub.setStyleSheet(f"font-size: 11px; color: {COLOR_TEXT_SECONDARY};")
        title_box.addWidget(lbl_app)
        title_box.addWidget(lbl_sub)
        la_layout.addLayout(title_box)
        la_layout.addStretch(1)
        layout.addWidget(logo_area)

        layout.addSpacing(10)

        # 2. Section Label
        lbl_sec = QLabel("PHÂN HỆ", sidebar)
        lbl_sec.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {COLOR_TEXT_MUTED}; padding-left: 12px; margin-bottom: 2px;")
        layout.addWidget(lbl_sec)

        # 3. Item Điều hướng (Xóa icon quả địa cầu, chỉ giữ chữ thuần)
        btn_nav_web = QPushButton("Bảng Điểm Đồ Án Web", sidebar)
        btn_nav_web.setFixedHeight(42)
        btn_nav_web.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_nav_web.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY_BG};
                color: {COLOR_PRIMARY};
                font-weight: 600;
                font-size: 13px;
                text-align: left;
                padding-left: 16px;
                border: none;
                border-radius: 8px;
                border-left: 3px solid {COLOR_PRIMARY};
            }}
        """)
        layout.addWidget(btn_nav_web)

        layout.addStretch(1)

        # 4. Logo FPT University (Trước nút Đổi Chế Độ Làm Việc, cao 28-32px, căn giữa, cách nút 16px)
        fptu_logo_paths = [
            SRC_DIR.parent / "assets" / "images" / "fptulogo_transparent.png",
            Path(r"e:\AITA\apps\desktop-client\assets\images\fptulogo_transparent.png"),
            Path(r"e:\AITA\assets\images\fptulogo_transparent.png")
        ]
        fptu_logo_file = next((p for p in fptu_logo_paths if p.exists()), None)
        if fptu_logo_file:
            lbl_fptu = QLabel(sidebar)
            lbl_fptu.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_fptu.setStyleSheet("background: transparent; border: none;")
            pix = QPixmap(str(fptu_logo_file))
            if not pix.isNull():
                lbl_fptu.setPixmap(pix.scaledToHeight(32, Qt.TransformationMode.SmoothTransformation))
            layout.addWidget(lbl_fptu)
            layout.addSpacing(16)

        # 5. Nút Đổi Chế Độ Làm Việc (Viền và chữ rõ ràng, bỏ icon mũi tên)
        btn_back_mode = QPushButton("Đổi Chế Độ Làm Việc", sidebar)
        btn_back_mode.setFixedHeight(40)
        btn_back_mode.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_back_mode.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_SURFACE};
                color: {COLOR_PRIMARY};
                font-weight: 600;
                font-size: 13px;
                text-align: center;
                border: 1.5px solid {COLOR_PRIMARY};
                border-radius: {RADIUS_BUTTON};
                padding: 0 12px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_BG};
            }}
            QPushButton:focus {{
                border-color: {COLOR_PRIMARY_ACTIVE};
            }}
            QPushButton:disabled {{
                background-color: {COLOR_SURFACE};
                color: {COLOR_TEXT_DISABLED};
                border-color: {COLOR_BORDER_DEFAULT};
            }}
        """)
        btn_back_mode.clicked.connect(self._back_to_mode_selection)
        layout.addWidget(btn_back_mode)

        return sidebar

    # --------------------------------------------------------------------------
    # B. Thanh trên cùng (Top Header): Tiêu đề, Pill AI viền đơn, Avatar GV
    # --------------------------------------------------------------------------
    def _build_top_header(self) -> QFrame:
        header = QFrame(self)
        header.setObjectName("HeaderBar")
        header.setFixedHeight(64)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(16)

        # Tiêu đề bên trái
        lbl_title = QLabel("Chấm Bài Tập & Đồ Án Web", header)
        lbl_title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {COLOR_TEXT_PRIMARY};")
        layout.addWidget(lbl_title)

        layout.addStretch(1)

        # Status Badge AI (mục 7: 1 lớp viền bo góc, cao 32px, số liệu thật, không icon)
        self._ai_quota_exhausted = False
        self.lbl_ai_quota = QLabel("AI Vision: Đang tải...", header)
        self.lbl_ai_quota.setFixedHeight(32)
        self.lbl_ai_quota.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_ai_quota)
        self._style_ai_pill()

        # User Avatar & Name (Avatar chỉ 1 lớp viền, không lồng 2 viền)
        user_frame = QFrame(header)
        user_frame.setStyleSheet("background: transparent; border: none;")
        uf_layout = QHBoxLayout(user_frame)
        uf_layout.setContentsMargins(0, 0, 0, 0)
        uf_layout.setSpacing(10)

        avatar = QLabel("GV", user_frame)
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            QLabel {{
                background-color: {COLOR_PRIMARY_BG};
                color: {COLOR_PRIMARY};
                border: 1.5px solid {COLOR_PRIMARY};
                border-radius: 18px;
                font-size: 13px;
                font-weight: 700;
            }}
        """)
        uf_layout.addWidget(avatar)

        d_name = self.session_info.get("display_name", "Giảng viên")
        lbl_user = QLabel(d_name, user_frame)
        lbl_user.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {COLOR_TEXT_PRIMARY}; background: transparent; border: none;")
        uf_layout.addWidget(lbl_user)

        layout.addWidget(user_frame)
        return header

    def _style_ai_pill(self):
        """Applies the normal (blue) or warning (orange, hết token) style to the AI pill."""
        if self._ai_quota_exhausted:
            bg, color = COLOR_WARNING_BG, COLOR_WARNING
        else:
            bg, color = COLOR_PRIMARY_BG, COLOR_PRIMARY
        self.lbl_ai_quota.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                color: {color};
                border: 1px solid {color};
                border-radius: 16px;
                padding: 0 14px;
                font-size: 12px;
                font-weight: 600;
            }}
        """)

    # --------------------------------------------------------------------------
    # C & D. Thanh công cụ: Chọn Thư Mục Bài Nộp, Quét Lại, Bắt Đầu Thẩm Định, Xuất
    # --------------------------------------------------------------------------
    def _build_toolbar(self) -> QFrame:
        card = QFrame(self)
        card.setProperty("class", "Card")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        # 1. Nhóm Chế Độ Chấm (Mục 1)
        lbl_m = QLabel("Chế Độ Chấm:", card)
        lbl_m.setStyleSheet(f"font-weight: 600; font-size: 13px; color: {COLOR_TEXT_PRIMARY};")
        layout.addWidget(lbl_m)

        rb_style = f"""
            QRadioButton {{
                font-size: 13px;
                font-weight: 500;
                color: {COLOR_TEXT_PRIMARY};
                background: transparent;
                border: none;
                spacing: 6px;
            }}
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 1.5px solid {COLOR_BORDER_DEFAULT};
                background-color: #FFFFFF;
            }}
            QRadioButton::indicator:hover {{
                border-color: {COLOR_PRIMARY};
            }}
            QRadioButton::indicator:checked {{
                border: 5px solid {COLOR_PRIMARY};
                background-color: #FFFFFF;
            }}
        """

        self.btn_group_mode = QButtonGroup(self)
        self.rb_live = QRadioButton("Live URL", card)
        self.rb_repo = QRadioButton("GitHub", card)
        self.rb_hybrid = QRadioButton("Hybrid", card)
        self.rb_hybrid.setChecked(True)

        for idx, rb in enumerate([self.rb_live, self.rb_repo, self.rb_hybrid], start=1):
            rb.setStyleSheet(rb_style)
            rb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            self.btn_group_mode.addButton(rb, idx)
            layout.addWidget(rb)

        self.btn_group_mode.idClicked.connect(self._on_mode_radio_changed)

        layout.addSpacing(10)

        # 2. MỘT nút "Thêm Bài Nộp" duy nhất (Mục 2)
        self.btn_add = QPushButton("Thêm Bài Nộp", card)
        self.btn_add.setProperty("class", "PrimaryBtn")
        self.btn_add.setFixedHeight(38)
        self.btn_add.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_add.setToolTip("Thêm bài nộp bằng tay hoặc dán nhiều link theo chế độ đang chọn.")
        self.btn_add.clicked.connect(self._open_add_submission_dialog)
        layout.addWidget(self.btn_add)

        layout.addStretch(1)

        # 3. Xuất Bảng Điểm (disable khi chưa có điểm)
        self.btn_export = QPushButton("Xuất Bảng Điểm", card)
        self.btn_export.setProperty("class", "ToolbarActionBtn")
        self.btn_export.setFixedHeight(38)
        self.btn_export.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_export.clicked.connect(self._show_export_menu)
        layout.addWidget(self.btn_export)

        # 4. Nút chính: Bắt Đầu Thẩm Định Web (disable khi chưa có bài nộp)
        self.btn_start = QPushButton("Bắt Đầu Thẩm Định Web", card)
        self.btn_start.setObjectName("BatchGradeBtn")
        self.btn_start.setFixedHeight(38)
        self.btn_start.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_start.clicked.connect(self._start_batch_web_grading)
        layout.addWidget(self.btn_start)

        return card

    def _get_current_grading_mode_code(self) -> str:
        checked_id = self.btn_group_mode.checkedId()
        if checked_id == 1:
            return "LIVE_ONLY"
        elif checked_id == 2:
            return "REPO_ONLY"
        return "HYBRID"

    def _on_mode_radio_changed(self, button_id: int):
        new_mode = self._get_current_grading_mode_code()
        if not self._web_students:
            return

        mode_name = {"LIVE_ONLY": "Live URL", "REPO_ONLY": "GitHub", "HYBRID": "Hybrid"}.get(new_mode, "Hybrid")
        reply = QMessageBox.question(
            self,
            "Đổi Chế Độ Chấm",
            f"Bạn vừa đổi chế độ trên thanh công cụ thành '{mode_name}'.\n\n"
            f"Bạn có muốn áp dụng chế độ '{mode_name}' cho toàn bộ bài nộp hiện có không?\n\n"
            f"(Nếu chọn 'Yes': Tất cả bài cũ sẽ chuyển sang chế độ '{mode_name}'. Bài nào thiếu link theo chế độ mới sẽ được đánh dấu 'Thiếu link'.)\n"
            f"(Nếu chọn 'No': Chế độ mới chỉ áp dụng cho các bài nộp thêm mới về sau.)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.update_all_web_submissions_mode(
                self.current_course_code, self.current_class_name, new_mode
            )
            self._load_submissions_from_db()

    def _apply_action_states(self):
        """Mục 9 & 25: disable + tooltip cho các nút trên thanh công cụ."""
        has_data = bool(self._web_students)
        has_scores = any(s.get("total_score") is not None for s in self._web_students)

        self.btn_start.setEnabled(has_data)
        self.btn_start.setToolTip("" if has_data else "Cần có ít nhất một bài nộp để bắt đầu thẩm định.")

        self.btn_export.setEnabled(has_scores)
        self.btn_export.setToolTip(
            "" if has_scores else "Chưa có điểm. Hãy thẩm định bài trước khi xuất bảng điểm."
        )

    def _update_class_button(self):
        self.btn_class.setText(f"Lớp: {self.current_class_name} · {self.current_course_code}")

    def _change_class_course(self):
        """Small dialog to switch the course code / class used to filter and label the gradebook."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Đổi Môn Học / Lớp")
        dlg.setStyleSheet(LIGHT_THEME_QSS)
        dlg.setMinimumWidth(400)
        v = QVBoxLayout(dlg)
        v.setContentsMargins(20, 20, 20, 20)
        v.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)
        ed_course = QLineEdit(self.current_course_code, dlg)
        ed_class = QLineEdit(self.current_class_name, dlg)
        ed_course.setFixedHeight(36)
        ed_class.setFixedHeight(36)
        form.addRow("Mã môn học:", ed_course)
        form.addRow("Lớp:", ed_class)
        v.addLayout(form)

        row = QHBoxLayout()
        row.addStretch(1)
        b_cancel = QPushButton("Hủy", dlg)
        b_cancel.setProperty("class", "SecondaryBtn")
        b_cancel.setFixedHeight(36)
        b_cancel.clicked.connect(dlg.reject)
        b_ok = QPushButton("Áp Dụng", dlg)
        b_ok.setProperty("class", "PrimaryBtn")
        b_ok.setFixedHeight(36)
        b_ok.clicked.connect(dlg.accept)
        row.addWidget(b_cancel)
        row.addWidget(b_ok)
        v.addLayout(row)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        course = ed_course.text().strip() or "WEB201c"
        klass = ed_class.text().strip() or "SE1806"
        if course == self.current_course_code and klass == self.current_class_name:
            return

        self.current_course_code = course
        self.current_class_name = klass
        self._settings.setValue("course_code", course)
        self._settings.setValue("class_name", klass)
        self._update_class_button()
        self._web_root_folder = None
        self.btn_rescan_folder.setVisible(False)
        self._load_submissions_from_db()

    # --------------------------------------------------------------------------
    # E. Khu tiến độ: Dày 10-12px, cách tiêu đề 8px, trạng thái rõ ràng
    # --------------------------------------------------------------------------
    def _build_progress_card(self) -> QFrame:
        card = QFrame(self)
        card.setProperty("class", "Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(8)

        top_l = QHBoxLayout()
        lbl_t = QLabel("Tiến độ chấm", card)
        lbl_t.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {COLOR_TEXT_PRIMARY};")
        top_l.addWidget(lbl_t)
        top_l.addStretch(1)

        # Bên phải: "0/0 bài" hoặc "Đã chấm N/M bài" (mục 24), không lặp câu hướng dẫn
        self.lbl_progress_status = QLabel("0/0 bài", card)
        self.lbl_progress_status.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {COLOR_TEXT_SECONDARY};")
        top_l.addWidget(self.lbl_progress_status)
        layout.addLayout(top_l)

        # Thanh tiến độ dày 11px
        self.progress_bar = QProgressBar(card)
        self.progress_bar.setFixedHeight(11)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLOR_SURFACE_SECONDARY};
                border: 1px solid {COLOR_BORDER_LIGHT};
                border-radius: 5px;
            }}
            QProgressBar::chunk {{
                background-color: {COLOR_PRIMARY};
                border-radius: 4px;
            }}
        """)
        layout.addWidget(self.progress_bar)

        return card

    # --------------------------------------------------------------------------
    # F. Bảng điểm & Empty State (mục 20-23)
    # --------------------------------------------------------------------------
    def _build_table_card(self) -> QFrame:
        self.table_card = QFrame(self)
        self.table_card.setProperty("class", "Card")
        layout = QVBoxLayout(self.table_card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        # Table Header Row
        self.table_header_row = QHBoxLayout()
        lbl_title = QLabel("Bảng Điểm Thẩm Định Web & Kết Quả Rubric", self.table_card)
        lbl_title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {COLOR_TEXT_PRIMARY};")
        self.table_header_row.addWidget(lbl_title)
        self.table_header_row.addStretch(1)

        # Gợi ý (mục 22): chỉ hiện khi có dữ liệu, 13px, màu #475569
        self.lbl_hint = QLabel("Bấm 'Xem Chi Tiết' để xem điểm 4 tiêu chí, ảnh chụp giao diện và nhật ký thẩm định.", self.table_card)
        self.lbl_hint.setStyleSheet("font-size: 13px; color: #475569;")
        self.lbl_hint.setVisible(False)
        self.table_header_row.addWidget(self.lbl_hint)

        self.txt_search = QLineEdit(self.table_card)
        self.txt_search.setPlaceholderText("Tìm theo MSSV hoặc tên...")
        self.txt_search.setFixedHeight(34)
        self.txt_search.setFixedWidth(240)
        self.txt_search.setClearButtonEnabled(True)
        self.txt_search.textChanged.connect(lambda _: self._populate_table())
        self.txt_search.setVisible(False)
        self.table_header_row.addWidget(self.txt_search)
        layout.addLayout(self.table_header_row)

        # 1. Empty State (mục 9): một khối căn giữa, viền liền nhạt
        self.empty_state_frame = QFrame(self.table_card)
        self.empty_state_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid {COLOR_BORDER_LIGHT};
                border-radius: 12px;
            }}
        """)
        es_layout = QVBoxLayout(self.empty_state_frame)
        es_layout.setContentsMargins(32, 40, 32, 40)
        es_layout.setSpacing(14)
        es_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_es_title = QLabel("Chưa có bài nộp", self.empty_state_frame)
        lbl_es_title.setStyleSheet(f"font-size: 17px; font-weight: 700; color: {COLOR_TEXT_PRIMARY}; background: transparent; border: none;")
        lbl_es_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        es_layout.addWidget(lbl_es_title)

        lbl_es_sub = QLabel(
            "Chọn chế độ chấm, rồi bấm 'Thêm Bài Nộp' để dán link",
            self.empty_state_frame
        )
        lbl_es_sub.setWordWrap(True)
        lbl_es_sub.setStyleSheet(f"font-size: 13px; color: {COLOR_TEXT_SECONDARY}; line-height: 1.4; background: transparent; border: none;")
        lbl_es_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        es_layout.addWidget(lbl_es_sub)

        btn_es_add = QPushButton("Thêm Bài Nộp", self.empty_state_frame)
        btn_es_add.setProperty("class", "PrimaryBtn")
        btn_es_add.setFixedHeight(38)
        btn_es_add.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_es_add.clicked.connect(self._open_add_submission_dialog)
        es_layout.addWidget(btn_es_add, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.empty_state_frame, stretch=1)

        # 2. Table Widget: chuẩn 11 cột (mục 7)
        self.table = QTableWidget(self.table_card)
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "MSSV", "Chế Độ", "Live URL", "GitHub Repo",
            "DOM", "Lint", "Function", "UI/UX", "Tổng Điểm", "Kết Quả", "Thao Tác"
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(10, QHeaderView.ResizeMode.Fixed)
        for col, width in {0: 110, 1: 95, 4: 65, 5: 65, 6: 78, 7: 100, 8: 88, 9: 145, 10: 240}.items():
            self.table.setColumnWidth(col, width)

        # Tiêu đề căn cùng nội dung: chữ căn trái, điểm và trạng thái căn giữa
        for col in (0, 2, 3):
            it = self.table.horizontalHeaderItem(col)
            if it:
                it.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        for col in (1, 4, 5, 6, 7, 8, 9, 10):
            it = self.table.horizontalHeaderItem(col)
            if it:
                it.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)

        # Tooltips giải thích cho các cột
        tooltip_map = {
            4: "Cấu trúc HTML5 ngữ nghĩa, thẻ SEO, alt ảnh, heading hierarchy",
            5: "Kiểm tra cú pháp CSS bằng tinycss2, hạn chế inline-style, responsive media queries",
            6: "Chỉ số tương tác JS và các thành phần tương tác trong HTML",
            7: "AI Vision đánh giá ảnh chụp màn hình theo tiêu chí thẩm mỹ (Không áp dụng cho chế độ GitHub)",
            8: "Tổng điểm theo rubric các tiêu chí áp dụng (thang 10)",
            9: "PASSED ≥ 7.0, PARTIAL ≥ 5.0, FAILED < 5.0"
        }
        for col, tip in tooltip_map.items():
            item = self.table.horizontalHeaderItem(col)
            if item:
                item.setToolTip(tip)

        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Sắp xếp khi bấm tiêu đề cột (bỏ qua cột Thao Tác)
        self._sort_key: Optional[str] = None
        self._sort_desc = False
        header.setSectionsClickable(True)
        header.sectionClicked.connect(self._on_header_clicked)

        self.table.setVisible(False)
        layout.addWidget(self.table, stretch=1)

        return self.table_card

    SORT_KEYS = {
        0: "mssv", 1: "mode", 2: "live_url", 3: "repo_url",
        4: "score_dom", 5: "score_lint", 6: "score_e2e", 7: "score_ui",
        8: "total_score", 9: "verdict",
    }

    def _on_header_clicked(self, col: int):
        key = self.SORT_KEYS.get(col)
        if not key:
            return
        if self._sort_key == key:
            self._sort_desc = not self._sort_desc
        else:
            self._sort_key = key
            self._sort_desc = False
        self._web_students.sort(key=self._sort_key_func(key), reverse=self._sort_desc)
        self._populate_table()

    @staticmethod
    def _sort_key_func(key: str):
        def _k(item: Dict[str, Any]):
            v = item.get(key)
            if v is None:
                return (1, "")
            if isinstance(v, (int, float)):
                return (0, v)
            return (0, str(v).lower())
        return _k

    # --------------------------------------------------------------------------
    # Nạp dữ liệu từ CSDL SQLite và hiển thị bảng
    # --------------------------------------------------------------------------
    def _load_submissions_from_db(self):
        """Fetches stored web submissions from SQLite and updates UI state."""
        try:
            records = self.db.get_all_web_submissions(self.current_course_code, self.current_class_name)
            self._web_students = records
        except Exception as ex:
            self._web_students = []

        self._populate_table()

    def _populate_table(self):
        """Renders table rows (with optional search filter) or toggles empty state."""
        total = len(self._web_students)
        has_data = (total > 0)

        self.empty_state_frame.setVisible(not has_data)
        self.table.setVisible(has_data)
        self.lbl_hint.setVisible(has_data)
        if hasattr(self, "txt_search"):
            self.txt_search.setVisible(has_data)
        self._apply_action_states()

        if not has_data:
            self.lbl_progress_status.setText("0/0 bài")
            self.progress_bar.setValue(0)
            self.table.setRowCount(0)
            return

        graded = sum(1 for s in self._web_students if s.get("total_score") is not None)
        self.lbl_progress_status.setText(f"Đã chấm {graded}/{total} bài")

        # Search filter by MSSV
        query = self.txt_search.text().strip().lower() if hasattr(self, "txt_search") else ""
        if query:
            rows = [
                s for s in self._web_students
                if query in (s.get("mssv") or "").lower()
            ]
        else:
            rows = list(self._web_students)

        self.table.setRowCount(len(rows))

        mode_name_map = {
            "LIVE_ONLY": "Live URL",
            "REPO_ONLY": "GitHub",
            "HYBRID": "Hybrid"
        }

        for r, item in enumerate(rows):
            self.table.setRowHeight(r, 48)
            mode = (item.get("mode") or "HYBRID").upper()
            live_url = (item.get("live_url") or "").strip()
            repo_url = (item.get("repo_url") or "").strip()

            # Kiểm tra trạng thái thiếu link theo chế độ
            is_missing_link = False
            if mode == "LIVE_ONLY" and not live_url:
                is_missing_link = True
            elif mode == "REPO_ONLY" and not repo_url:
                is_missing_link = True
            elif mode == "HYBRID" and (not live_url or not repo_url):
                is_missing_link = True

            # 0. Cột MSSV (mục 4: chuẩn hóa, hiển thị cảnh báo nếu thiếu link)
            display_mssv = item.get("mssv", "")
            mssv_text = f"{display_mssv} — Thiếu link" if is_missing_link else display_mssv
            item_mssv = QTableWidgetItem(mssv_text)
            item_mssv.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            if is_missing_link:
                item_mssv.setForeground(QColor(COLOR_ERROR))
                item_mssv.setToolTip("Bài nộp chưa có đủ link cho chế độ chấm đã chọn.")
            self.table.setItem(r, 0, item_mssv)

            # 1. Cột Chế Độ (mục 7)
            mode_display = mode_name_map.get(mode, "Hybrid")
            item_mode = QTableWidgetItem(mode_display)
            item_mode.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_mode.setFont(QFont("Inter", 9, QFont.Weight.Medium))
            self.table.setItem(r, 1, item_mode)

            # 2. Cột Live URL (mục 7: nếu không thuộc chế độ hiển thị "-")
            if mode == "REPO_ONLY":
                item_live = QTableWidgetItem("-")
                item_live.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item_live.setForeground(QColor(COLOR_TEXT_MUTED))
            else:
                live_text = live_url if live_url else "Thiếu link"
                item_live = QTableWidgetItem(live_text)
                item_live.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                if not live_url:
                    item_live.setForeground(QColor(COLOR_ERROR))
                else:
                    item_live.setToolTip(live_url)
            self.table.setItem(r, 2, item_live)

            # 3. Cột GitHub Repo (mục 7: nếu không thuộc chế độ hiển thị "-")
            if mode == "LIVE_ONLY":
                item_repo = QTableWidgetItem("-")
                item_repo.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item_repo.setForeground(QColor(COLOR_TEXT_MUTED))
            else:
                repo_text = repo_url if repo_url else "Thiếu link"
                item_repo = QTableWidgetItem(repo_text)
                item_repo.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                if not repo_url:
                    item_repo.setForeground(QColor(COLOR_ERROR))
                else:
                    item_repo.setToolTip(repo_url)
            self.table.setItem(r, 3, item_repo)

            # 4. Cột DOM (align Center)
            val_dom = item.get("score_dom")
            dom_str = f"{val_dom:.1f}" if val_dom is not None else "—"
            item_dom = QTableWidgetItem(dom_str)
            item_dom.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 4, item_dom)

            # 5. Cột Lint (align Center)
            val_lint = item.get("score_lint")
            lint_str = f"{val_lint:.1f}" if val_lint is not None else "—"
            item_lint = QTableWidgetItem(lint_str)
            item_lint.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 5, item_lint)

            # 6. Cột Function (align Center)
            val_func = item.get("score_e2e")
            func_str = f"{val_func:.1f}" if val_func is not None else "—"
            item_func = QTableWidgetItem(func_str)
            item_func.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 6, item_func)

            # 7. Cột UI/UX (mục 6, 7: Không áp dụng cho REPO_ONLY)
            if mode == "REPO_ONLY":
                item_ui = QTableWidgetItem("Không áp dụng")
                item_ui.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item_ui.setForeground(QColor(COLOR_TEXT_MUTED))
                item_ui.setToolTip("Chế độ chỉ chấm GitHub Repo không áp dụng tiêu chí UI/UX Vision.")
            else:
                val_ui = item.get("score_ui")
                ui_str = f"{val_ui:.1f}" if val_ui is not None else "—"
                item_ui = QTableWidgetItem(ui_str)
                item_ui.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 7, item_ui)

            # 8. Cột Tổng Điểm (align Center, in đậm)
            tot = item.get("total_score")
            tot_str = f"{tot:.1f}" if tot is not None else "—"
            tot_item = QTableWidgetItem(tot_str)
            tot_item.setFont(QFont("Inter", 10, QFont.Weight.Bold))
            tot_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if tot is not None:
                if tot >= 8.0:
                    tot_item.setForeground(QColor(COLOR_SUCCESS))
                elif tot >= 5.0:
                    tot_item.setForeground(QColor(COLOR_WARNING))
                else:
                    tot_item.setForeground(QColor(COLOR_ERROR))
            self.table.setItem(r, 8, tot_item)

            # 9. Cột Kết Quả (verdict pill)
            verdict = item.get("verdict") or "PENDING"
            self.table.setCellWidget(r, 9, WebVerdictPill(verdict, self.table))

            # 10. Cột Thao Tác (Xem Chi Tiết, Sửa, Xóa)
            btn_view = QPushButton("Xem Chi Tiết")
            btn_view.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_PRIMARY_BG};
                    color: {COLOR_PRIMARY};
                    border: 1px solid {COLOR_PRIMARY_LIGHT};
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: 600;
                    padding: 0 10px;
                }}
                QPushButton:hover {{
                    background-color: {COLOR_PRIMARY};
                    color: #FFFFFF;
                }}
            """)
            btn_view.clicked.connect(lambda _, st=item: self._view_student_detail(st))

            btn_edit = QPushButton("Sửa")
            btn_edit.setStyleSheet(f"""
                QPushButton {{
                    background-color: #FFFFFF;
                    color: {COLOR_TEXT_PRIMARY};
                    border: 1px solid {COLOR_BORDER_DEFAULT};
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: 600;
                    padding: 0 10px;
                }}
                QPushButton:hover {{
                    background-color: {COLOR_SURFACE_SECONDARY};
                    border-color: {COLOR_PRIMARY};
                    color: {COLOR_PRIMARY};
                }}
            """)
            btn_edit.clicked.connect(lambda _, st=item: self._edit_student_submission(st))

            btn_del = QPushButton("Xóa")
            btn_del.setStyleSheet(f"""
                QPushButton {{
                    background-color: #FFFFFF;
                    color: {COLOR_ERROR};
                    border: 1px solid {COLOR_ERROR}55;
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: 600;
                    padding: 0 10px;
                }}
                QPushButton:hover {{
                    background-color: {COLOR_ERROR_BG};
                    border-color: {COLOR_ERROR};
                }}
            """)
            btn_del.clicked.connect(lambda _, st=item: self._delete_student_submission(st))

            self.table.setCellWidget(r, 10, make_action_cell([btn_view, btn_edit, btn_del], self.table))

    # --------------------------------------------------------------------------
    # Thao tác Thêm / Sửa / Xóa bài nộp
    # --------------------------------------------------------------------------
    def _open_add_submission_dialog(self):
        """Mục 2 & 3: Mở hộp thoại nhập link theo chế độ đang chọn trên toolbar."""
        existing_mssvs = [s.get("mssv", "") for s in self._web_students]
        current_mode = self._get_current_grading_mode_code()
        dlg = WebSubmissionDialog(
            parent=self,
            current_mode=current_mode,
            existing_mssvs=existing_mssvs,
            open_bulk_tab=False
        )
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.added_submissions:
            for item in dlg.added_submissions:
                try:
                    sub_id = self.db.add_web_submission(
                        mssv=item["mssv"],
                        name="",
                        live_url=item.get("live_url", ""),
                        repo_url=item.get("repo_url", ""),
                        mode=item.get("mode", current_mode),
                        course_code=self.current_course_code,
                        class_name=self.current_class_name
                    )
                    item["id"] = sub_id
                except Exception:
                    pass
            self._load_submissions_from_db()

    def _edit_student_submission(self, student_info: Dict[str, Any]):
        """Mục 8: Mở hộp thoại sửa bài nộp, cho đổi link và chế độ của bài đó."""
        existing_mssvs = [s.get("mssv", "") for s in self._web_students]
        dlg = WebSubmissionDialog(
            parent=self,
            current_mode=student_info.get("mode", "HYBRID"),
            existing_item=student_info,
            existing_mssvs=existing_mssvs
        )
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.added_submissions:
            updated = dlg.added_submissions[0]
            sub_id = student_info.get("id")
            if sub_id:
                try:
                    self.db.update_web_submission(
                        submission_id=sub_id,
                        mssv=updated["mssv"],
                        name="",
                        live_url=updated.get("live_url", ""),
                        repo_url=updated.get("repo_url", ""),
                        mode=updated.get("mode", "HYBRID")
                    )
                except Exception:
                    pass
            self._load_submissions_from_db()

    def _delete_student_submission(self, student_info: Dict[str, Any]):
        """Mục 8: Xóa bài nộp khỏi danh sách với hộp thoại xác nhận."""
        mssv = student_info.get("mssv", "")
        ret = QMessageBox.question(
            self,
            "Xác Nhận Xóa Bài Nộp",
            f"Bạn có chắc chắn muốn gỡ bài nộp của sinh viên {mssv} khỏi danh sách?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if ret == QMessageBox.StandardButton.Yes:
            sub_id = student_info.get("id")
            if sub_id:
                try:
                    self.db.delete_web_submission(sub_id)
                except Exception:
                    pass
            self._load_submissions_from_db()
        if ret == QMessageBox.StandardButton.Yes:
            sub_id = student_info.get("id")
            if sub_id:
                try:
                    self.db.delete_web_submission(sub_id)
                except Exception:
                    pass
            self._load_submissions_from_db()

    def _view_student_detail(self, student_info: Dict[str, Any]):
        dlg = WebDetailDialog(student_info, self)
        dlg.exec()
        if dlg.score_override:
            self._apply_score_override(student_info, dlg.score_override)
        elif dlg.regrade_requested:
            self._regrade_single(student_info)

    def _apply_score_override(self, student_info: Dict[str, Any], scores: Dict[str, float]):
        """Persists a manual score override; total & verdict are recomputed from the rubric weights."""
        dom = float(scores["score_dom"])
        lint = float(scores["score_lint"])
        func = float(scores["score_func"])
        ui = float(scores["score_ui"])
        total = round(dom * 0.2 + lint * 0.2 + func * 0.3 + ui * 0.3, 2)
        verdict = "PASSED" if total >= 7.0 else ("PARTIAL" if total >= 5.0 else "FAILED")
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sub_id = student_info.get("id")
        if sub_id:
            try:
                self.db.update_web_submission_scores(
                    submission_id=sub_id,
                    score_dom=dom, score_lint=lint, score_e2e=func, score_ui=ui,
                    total_score=total, verdict=verdict,
                    rubric_log=(student_info.get("rubric_log") or "")
                    + f"\n[MANUAL]: Giảng viên ghi đè điểm lúc {stamp} -> {total:.1f}/10 ({verdict}).",
                    screenshot_path=student_info.get("screenshot_path"),
                    ai_feedback=student_info.get("ai_feedback")
                )
            except Exception:
                pass
        self._load_submissions_from_db()

    # --------------------------------------------------------------------------
    # Thẩm định hàng loạt / chấm lại từng bài (logic chấm Playwright / DOM / Lint / UI)
    # --------------------------------------------------------------------------
    def _start_batch_web_grading(self):
        if not self._web_students:
            return
        self._start_grading(list(self._web_students))

    def _regrade_single(self, student_info: Dict[str, Any]):
        self._start_grading([student_info])

    def _start_grading(self, students: List[Dict[str, Any]]):
        if not students:
            return

        self.btn_start.setEnabled(False)
        self.progress_bar.setValue(0)
        self.lbl_progress_status.setText("Đang khởi tạo Playwright Chromium & BeautifulSoup...")

        self._web_engine = WebRubricEngine(ai_service=AiService())
        self._web_worker = WebGradingWorker(students, self._web_engine, parent=self)
        self._web_worker.progress.connect(self._on_web_grading_progress)
        self._web_worker.graded_one.connect(self._on_web_submission_graded)
        self._web_worker.all_done.connect(self._on_web_grading_done)
        self._web_worker.start()

    def _on_web_grading_progress(self, percent: int, detail: str):
        self.progress_bar.setValue(percent)
        self.lbl_progress_status.setText(detail)

    def _on_web_submission_graded(self, st: Dict[str, Any]):
        """Persists one freshly graded submission and refreshes the row."""
        sub_id = st.get("id")
        if sub_id:
            try:
                self.db.update_web_submission_scores(
                    submission_id=sub_id,
                    score_dom=st["score_dom"],
                    score_lint=st["score_lint"],
                    score_e2e=st["score_e2e"],
                    score_ui=st["score_ui"],
                    total_score=st["total_score"],
                    verdict=st["verdict"],
                    rubric_log=st.get("rubric_log"),
                    screenshot_path=st.get("screenshot_path"),
                    ai_feedback=st.get("ai_feedback")
                )
                self.db.set_web_submission_link_changed(sub_id, False)
                st["link_changed"] = 0
                st["graded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                pass

    def _on_web_grading_done(self, total: int):
        self._populate_table()
        self.progress_bar.setValue(100)
        self.lbl_progress_status.setText(f"Đã chấm {total}/{total} bài")
        self.btn_start.setEnabled(True)

        QMessageBox.information(
            self,
            "Chấm Điểm Hoàn Tất",
            f"Đã thẩm định thành công toàn bộ {total} bài tập Web!\n"
            "• Điểm số 4 tiêu chí (DOM, Lint, Function, UI) đã được tính toán thực tế.\n"
            "• Dữ liệu đã được lưu an toàn vào CSDL SQLite.\n"
            "• Bạn có thể bấm 'Xuất Bảng Điểm' để lưu file Excel (.xlsx) hoặc PDF."
        )

    # --------------------------------------------------------------------------
    # Xuất Bảng Điểm: Hỗ trợ Excel (.xlsx) và PDF (Bỏ hoàn toàn CSV)
    # --------------------------------------------------------------------------
    def _show_export_menu(self):
        """Displays menu to choose between Excel (.xlsx) and PDF export."""
        if not any(s.get("total_score") is not None for s in self._web_students):
            QMessageBox.warning(
                self, "Chưa Có Điểm",
                "Chưa có điểm. Hãy thẩm định bài trước khi xuất bảng điểm!"
            )
            return

        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: #FFFFFF;
                border: 1px solid {COLOR_BORDER_DEFAULT};
                border-radius: 8px;
                padding: 6px;
            }}
            QMenu::item {{
                padding: 8px 16px;
                font-size: 13px;
                color: {COLOR_TEXT_PRIMARY};
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {COLOR_PRIMARY_BG};
                color: {COLOR_PRIMARY};
            }}
        """)
        action_excel = menu.addAction("Xuất File Excel (.xlsx)")
        action_pdf = menu.addAction("Xuất File Báo Cáo PDF (.pdf)")

        chosen = menu.exec(QCursor.pos())
        if chosen == action_excel:
            self._export_excel()
        elif chosen == action_pdf:
            self._export_pdf()

    def _export_excel(self):
        """Exports gradebook to modern formatted Excel file (.xlsx) via openpyxl."""
        default_name = f"Bang_Diem_Web_{self.current_class_name}.xlsx"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Lưu Bảng Điểm Excel", default_name, "Excel Files (*.xlsx)"
        )
        if not file_path:
            return

        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
            from openpyxl.utils import get_column_letter

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Bảng Điểm Đồ Án Web"

            # Tiêu đề bảng: Chuẩn 11 cột (bỏ Họ và Tên, thêm Chế Độ)
            headers = [
                "MSSV", "Chế Độ", "Live Website URL", "GitHub Repo URL",
                "DOM (10)", "Lint (10)", "Function (10)", "UI/UX (10)", "Tổng Điểm (10)", "Kết Quả", "Ngày Chấm"
            ]
            last_col_letter = get_column_letter(len(headers))
            ws.merge_cells(f"A1:{last_col_letter}1")
            title_cell = ws["A1"]
            title_cell.value = f"BẢNG ĐIỂM THẨM ĐỊNH ĐỒ ÁN WEB — LỚP {self.current_class_name} ({self.current_course_code})"
            title_cell.font = Font(name="Arial", size=14, bold=True, color="1E3A8A")
            title_cell.alignment = Alignment(horizontal="center", vertical="center")
            ws.row_dimensions[1].height = 36

            ws.append([])  # Dòng trống A2
            ws.append(headers)  # Dòng header A3

            header_fill = PatternFill(start_color="2F80ED", end_color="2F80ED", fill_type="solid")
            header_font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
            thin_border = Border(
                left=Side(style='thin', color="CBD5E1"),
                right=Side(style='thin', color="CBD5E1"),
                top=Side(style='thin', color="CBD5E1"),
                bottom=Side(style='thin', color="CBD5E1")
            )

            for col_num in range(1, len(headers) + 1):
                cell = ws.cell(row=3, column=col_num)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = thin_border
            ws.row_dimensions[3].height = 28

            # Dữ liệu
            left_align_cols = {1, 3, 4}
            for st in self._web_students:
                st_mode = st.get("mode", "HYBRID")
                mode_name = {"LIVE_ONLY": "Live URL", "REPO_ONLY": "GitHub", "HYBRID": "Hybrid"}.get(st_mode, "Hybrid")
                live_val = st.get("live_url", "") if st_mode in ("LIVE_ONLY", "HYBRID") else "—"
                repo_val = st.get("repo_url", "") if st_mode in ("REPO_ONLY", "HYBRID") else "—"
                ui_val = "K/A" if st_mode == "REPO_ONLY" else (st.get("score_ui") if st.get("score_ui") is not None else "")

                row_data = [
                    st.get("display_mssv") or st.get("mssv", ""),
                    mode_name,
                    live_val,
                    repo_val,
                    st.get("score_dom") if st.get("score_dom") is not None else "",
                    st.get("score_lint") if st.get("score_lint") is not None else "",
                    st.get("score_e2e") if st.get("score_e2e") is not None else "",
                    ui_val,
                    st.get("total_score") if st.get("total_score") is not None else "",
                    st.get("verdict", "PENDING"),
                    str(st.get("graded_at"))[:16] if st.get("graded_at") else ""
                ]
                ws.append(row_data)
                curr_row = ws.max_row
                ws.row_dimensions[curr_row].height = 22

                for col_num in range(1, len(row_data) + 1):
                    c = ws.cell(row=curr_row, column=col_num)
                    c.font = Font(name="Arial", size=10)
                    c.border = thin_border
                    if col_num in left_align_cols:
                        c.alignment = Alignment(horizontal="left", vertical="center")
                    else:
                        c.alignment = Alignment(horizontal="center", vertical="center")

            # Tự động điều chỉnh độ rộng cột
            col_widths = [14, 12, 34, 34, 12, 12, 14, 12, 14, 16, 18]
            for idx, width in enumerate(col_widths, start=1):
                col_letter = get_column_letter(idx)
                ws.column_dimensions[col_letter].width = width

            wb.save(file_path)
            QMessageBox.information(
                self, "Xuất Excel Thành Công",
                f"Đã xuất bảng điểm thành công ra tệp Excel:\n{file_path}"
            )
        except Exception as ex:
            QMessageBox.critical(self, "Lỗi Xuất Excel", f"Không thể xuất file Excel:\n{str(ex)}")

    def _export_pdf(self):
        """Exports gradebook to a clean formatted PDF report via QTextDocument & QPageLayout."""
        default_name = f"Bang_Diem_Web_{self.current_class_name}.pdf"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Lưu Bảng Điểm PDF", default_name, "PDF Files (*.pdf)"
        )
        if not file_path:
            return

        try:
            from PyQt6.QtGui import QPdfWriter

            pdf_writer = QPdfWriter(file_path)
            pdf_writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            pdf_writer.setPageOrientation(QPageLayout.Orientation.Landscape)

            html_rows = ""

            def _sfmt(v):
                return f"{v:.1f}" if isinstance(v, (int, float)) else "—"

            for idx, st in enumerate(self._web_students, start=1):
                tot = st.get("total_score")
                tot_str = f"{tot:.1f}" if tot is not None else "—"
                mssv_display = html.escape(str(st.get("display_mssv") or st.get("mssv", "")))
                st_mode = st.get("mode", "HYBRID")
                mode_name = {"LIVE_ONLY": "Live URL", "REPO_ONLY": "GitHub", "HYBRID": "Hybrid"}.get(st_mode, "Hybrid")
                live_text = (st.get('live_url') or '—') if st_mode in ("LIVE_ONLY", "HYBRID") else '—'
                repo_text = (st.get('repo_url') or '—') if st_mode in ("REPO_ONLY", "HYBRID") else '—'
                live_html = html.escape(str(live_text))
                repo_html = html.escape(str(repo_text))
                ui_html = "K/A" if st_mode == "REPO_ONLY" else _sfmt(st.get('score_ui'))
                verdict_html = html.escape(str(st.get('verdict', 'PENDING')))
                graded_str = str(st.get("graded_at"))[:16] if st.get("graded_at") else "—"
                html_rows += f"""
                <tr style="background-color: {'#F8FAFC' if idx % 2 == 0 else '#FFFFFF'};">
                    <td align="center" style="padding: 6px; border: 1px solid #CBD5E1;">{idx}</td>
                    <td style="padding: 6px; border: 1px solid #CBD5E1;"><b>{mssv_display}</b></td>
                    <td align="center" style="padding: 6px; border: 1px solid #CBD5E1;">{mode_name}</td>
                    <td style="padding: 6px; border: 1px solid #CBD5E1; font-size: 9px;">{live_html}</td>
                    <td style="padding: 6px; border: 1px solid #CBD5E1; font-size: 9px;">{repo_html}</td>
                    <td align="center" style="padding: 6px; border: 1px solid #CBD5E1;">{_sfmt(st.get('score_dom'))}</td>
                    <td align="center" style="padding: 6px; border: 1px solid #CBD5E1;">{_sfmt(st.get('score_lint'))}</td>
                    <td align="center" style="padding: 6px; border: 1px solid #CBD5E1;">{_sfmt(st.get('score_e2e'))}</td>
                    <td align="center" style="padding: 6px; border: 1px solid #CBD5E1;">{ui_html}</td>
                    <td align="center" style="padding: 6px; border: 1px solid #CBD5E1; font-weight: bold; color: #2F80ED;">{tot_str}</td>
                    <td align="center" style="padding: 6px; border: 1px solid #CBD5E1;">{verdict_html}</td>
                    <td align="center" style="padding: 6px; border: 1px solid #CBD5E1;">{graded_str}</td>
                </tr>
                """

            doc_html = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 10px; color: #1E293B; }}
                    h2 {{ color: #1E3A8A; margin-bottom: 4px; text-align: center; }}
                    p.sub {{ color: #64748B; margin-top: 0; text-align: center; font-size: 11px; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 14px; }}
                    th {{ background-color: #2F80ED; color: #FFFFFF; font-weight: bold; padding: 8px 4px; border: 1px solid #CBD5E1; }}
                </style>
            </head>
            <body>
                <h2>BẢNG ĐIỂM THẨM ĐỊNH BÀI TẬP & ĐỒ ÁN WEB</h2>
                <p class="sub">Môn học: {html.escape(str(self.current_course_code))} | Lớp: {html.escape(str(self.current_class_name))} | Đề tài: {html.escape(str(self.current_assignment_title))}</p>
                <table>
                    <thead>
                        <tr>
                            <th width="3%">STT</th>
                            <th width="9%">MSSV</th>
                            <th width="8%">Chế Độ</th>
                            <th width="20%">Live Website</th>
                            <th width="20%">GitHub Repo</th>
                            <th width="5%">DOM</th>
                            <th width="5%">Lint</th>
                            <th width="5%">Function</th>
                            <th width="5%">UI/UX</th>
                            <th width="6%">Tổng Điểm</th>
                            <th width="6%">Kết Quả</th>
                            <th width="8%">Ngày Chấm</th>
                        </tr>
                    </thead>
                    <tbody>
                        {html_rows}
                    </tbody>
                </table>
            </body>
            </html>
            """

            doc = QTextDocument()
            doc.setHtml(doc_html)
            doc.print(pdf_writer)

            QMessageBox.information(
                self, "Xuất PDF Thành Công",
                f"Đã xuất bảng điểm thành công ra tệp PDF:\n{file_path}"
            )
        except Exception as ex:
            QMessageBox.critical(self, "Lỗi Xuất PDF", f"Không thể xuất file PDF:\n{str(ex)}")

    # --------------------------------------------------------------------------
    # Quay lại màn hình chọn chế độ
    # --------------------------------------------------------------------------
    def _back_to_mode_selection(self):
        from ui.windows.mode_selection_window import ModeSelectionWindow
        self.mode_win = ModeSelectionWindow(session_info=self.session_info)
        self.mode_win.show()
        self.close()

    def _refresh_ai_quota(self):
        """Fetches live AI quota from Neon Postgres via GET /api/v1/ai/quota asynchronously."""
        class QuotaWorker(QThread):
            quota_received = pyqtSignal(dict)
            def run(self):
                ai_service = AiService()
                res = ai_service.get_quota()
                self.quota_received.emit(res)

        self.quota_worker = QuotaWorker()
        self.quota_worker.quota_received.connect(self._on_quota_received)
        self.quota_worker.start()

    def _on_quota_received(self, res: Dict[str, Any]):
        """Applies live AI quota to the AI pill (mục 7: never display '0 / 0')."""
        if not (hasattr(self, "lbl_ai_quota") and self.lbl_ai_quota):
            return
        if not res.get("success"):
            self.lbl_ai_quota.setText("AI Vision: Chưa có dữ liệu")
            self.lbl_ai_quota.setToolTip(
                "Chưa đọc được hạn ngạch AI từ máy chủ. Chức năng chấm vẫn hoạt động bình thường."
            )
            return

        rem = int(res.get("remaining_tokens", 0) or 0)
        limit = int(res.get("daily_limit_tokens", 0) or 0)
        used = int(res.get("used_tokens_today", 0) or 0)

        if rem <= 0:
            self._ai_quota_exhausted = True
            self.lbl_ai_quota.setText("AI Vision: Hết token")
            self.lbl_ai_quota.setToolTip(
                "Đã dùng hết token AI. Các chức năng chấm không dùng AI vẫn hoạt động."
            )
        else:
            self._ai_quota_exhausted = False
            self.lbl_ai_quota.setText(f"AI Vision: Còn {rem:,} / {limit:,} Tokens")
            self.lbl_ai_quota.setToolTip(
                f"Hạn ngạch AI từ máy chủ:\n"
                f"• Đã dùng hôm nay: {used:,} tokens\n"
                f"• Hạn mức ngày: {limit:,} tokens\n"
                f"• Còn lại: {rem:,} tokens"
            )
        self._style_ai_pill()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Inter", 9)
    app.setFont(font)

    win = WebGradingMainWindow()
    win.show()
    sys.exit(app.exec())
