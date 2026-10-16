"""
AITA Desktop Client - Web Submission Folder Import Dialog (PyQt6)
UC-19 (Web Studio): recognize students when loading a submissions folder.

Recognition rules (Web page only):
  - Each immediate sub-folder name IS the MSSV (e.g. SE180001); no name parsing from folder name.
  - MSSV is normalized (trim + UPPERCASE) for case-insensitive duplicate detection.
  - Folder names must match MSSV_PATTERN (configurable); non-matching folders are surfaced
    in the preview (red) with a choice to "Vẫn nạp" or "Bỏ qua".
  - System/hidden folders and loose files directly in the root are skipped and reported.

This module performs recognition and display only. It never changes grading logic.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit, QMessageBox
)

from ui.styles.theme import (
    LIGHT_THEME_QSS, COLOR_PRIMARY, COLOR_PRIMARY_BG, COLOR_PRIMARY_LIGHT,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_SURFACE, COLOR_SURFACE_SECONDARY, COLOR_BORDER_DEFAULT, COLOR_BORDER_LIGHT,
    COLOR_SUCCESS, COLOR_ERROR, COLOR_WARNING, RADIUS_CARD, RADIUS_BUTTON
)

# ------------------------------------------------------------------------------
# CONFIGURABLE RECOGNITION RULES
# ------------------------------------------------------------------------------
# MSSV format: 2 letters followed by 6 digits (e.g. SE180001). Adjust here to change the rule.
MSSV_PATTERN = r"^[A-Za-z]{2}\d{6}$"
MSSV_PATTERN_LABEL = "2 chữ cái + 6 chữ số (ví dụ SE180001)"

# Folders that are never treated as student submissions.
SKIP_DIR_NAMES = {"__MACOSX", "node_modules"}

# Candidate entry pages inside a student folder (first match wins).
ENTRY_FILE_CANDIDATES = ("index.html", "Index.html", "index.htm", "index.HTML", "default.html")

# Candidate metadata text files that may carry the student's name / links.
INFO_FILE_CANDIDATES = (
    "links.txt", "link.txt", "info.txt", "thongtin.txt", "thong-tin.txt",
    "README.txt", "readme.txt", "submission.txt"
)

# "Họ tên: ...", "Họ và tên: ...", "Tên: ...", "Name: ..."
NAME_LINE_PATTERN = re.compile(
    r"^\s*(?:h[oọ]\s*(?:v[àa]\s*)?t[êe]n|t[êe]n|name)\s*[:\-]\s*(.+?)\s*$",
    re.IGNORECASE
)
URL_PATTERN = re.compile(r"https?://[^\s,\)\]\"']+")


class WebFolderImportDialog(QDialog):
    """Scans a root folder and previews recognized web submissions before importing."""

    DUP_KEEP_ALL = "Đánh số và giữ tất cả"
    DUP_KEEP_FIRST = "Chỉ giữ thư mục đầu tiên"
    DUP_KEEP_LAST = "Chỉ giữ thư mục cuối cùng"

    INVALID_LOAD = "Vẫn nạp"
    INVALID_SKIP = "Bỏ qua"

    def __init__(self, parent, root_dir: str, existing_mssvs: Optional[List[str]] = None):
        super().__init__(parent)
        self.root_dir = root_dir
        self.existing_mssvs = {m.strip().upper() for m in (existing_mssvs or []) if m}

        self.scanned: List[Dict[str, Any]] = []
        self.skipped_dirs: List[str] = []
        self.skipped_files: List[str] = []
        self.import_items: List[Dict[str, Any]] = []

        self.setWindowTitle("Nạp Danh Sách Bài Nộp Từ Thư Mục")
        self.setMinimumSize(980, 640)
        self.resize(1040, 700)
        self.setStyleSheet(LIGHT_THEME_QSS)

        self._scan_root()
        self._init_ui()
        self._refresh_preview()

    # ------------------------------------------------------------------
    # Scanning
    # ------------------------------------------------------------------
    def _scan_root(self):
        root = Path(self.root_dir)
        self.scanned = []
        self.skipped_dirs = []
        self.skipped_files = []

        if not root.is_dir():
            return

        for entry in sorted(root.iterdir(), key=lambda p: p.name.lower()):
            if entry.is_file():
                self.skipped_files.append(entry.name)
                continue
            if not entry.is_dir():
                continue

            folder_name = entry.name
            if folder_name.startswith(".") or folder_name in SKIP_DIR_NAMES:
                self.skipped_dirs.append(folder_name)
                continue

            mssv = folder_name.strip().upper()
            is_valid = bool(re.match(MSSV_PATTERN, mssv))
            info = self._read_info(entry)

            self.scanned.append({
                "folder_name": folder_name,
                "mssv": mssv,
                "mssv_valid": is_valid,
                "local_dir": str(entry),
                "entry_file": self._find_entry_file(entry),
                "name": info.get("name", ""),
                "live_url": info.get("live_url", ""),
                "repo_url": info.get("repo_url", ""),
            })

    def _find_entry_file(self, folder: Path) -> str:
        for candidate in ENTRY_FILE_CANDIDATES:
            direct = folder / candidate
            if direct.is_file():
                return str(direct)
        for candidate in ENTRY_FILE_CANDIDATES:
            found = next(folder.rglob(candidate), None)
            if found and found.is_file():
                return str(found)
        return ""

    def _read_info(self, folder: Path) -> Dict[str, str]:
        text = ""
        for candidate in INFO_FILE_CANDIDATES:
            f = folder / candidate
            if f.is_file():
                try:
                    text = f.read_text(encoding="utf-8", errors="replace")
                    break
                except Exception:
                    continue
        if not text:
            txt_files = sorted(folder.glob("*.txt"))
            if txt_files:
                try:
                    text = txt_files[0].read_text(encoding="utf-8", errors="replace")
                except Exception:
                    text = ""

        name = ""
        live_url = ""
        repo_url = ""
        if text:
            for line in text.splitlines():
                m = NAME_LINE_PATTERN.match(line)
                if m and not name:
                    name = m.group(1).strip()
                for url in URL_PATTERN.findall(line):
                    url = url.rstrip(".,;")
                    if "github.com" in url.lower():
                        if not repo_url:
                            repo_url = url
                    elif not live_url:
                        live_url = url
        return {"name": name, "live_url": live_url, "repo_url": repo_url}

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        lbl_rule = QLabel(
            "Quy ước nhận diện: tên mỗi thư mục con CHÍNH LÀ MSSV của sinh viên "
            f"(mẫu hợp lệ: {MSSV_PATTERN_LABEL}). Họ tên chỉ đọc từ file .txt nếu có.",
            self
        )
        lbl_rule.setWordWrap(True)
        lbl_rule.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 13px;")
        layout.addWidget(lbl_rule)

        lbl_root = QLabel(f"Thư mục gốc: {self.root_dir}", self)
        lbl_root.setWordWrap(True)
        lbl_root.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 13px; font-weight: 600;")
        layout.addWidget(lbl_root)

        # Options row
        options = QHBoxLayout()
        options.setSpacing(12)

        options.addWidget(QLabel("Thư mục sai mẫu MSSV:", self))
        self.cb_invalid = QComboBox(self)
        self.cb_invalid.addItems([self.INVALID_SKIP, self.INVALID_LOAD])
        self.cb_invalid.currentIndexChanged.connect(self._refresh_preview)
        options.addWidget(self.cb_invalid)

        options.addSpacing(16)
        options.addWidget(QLabel("Xử lý MSSV trùng:", self))
        self.cb_duplicate = QComboBox(self)
        self.cb_duplicate.addItems([self.DUP_KEEP_ALL, self.DUP_KEEP_FIRST, self.DUP_KEEP_LAST])
        self.cb_duplicate.currentIndexChanged.connect(self._refresh_preview)
        options.addWidget(self.cb_duplicate)
        options.addStretch(1)
        layout.addLayout(options)

        # Preview table
        self.table = QTableWidget(self)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table, stretch=3)

        # Report area
        lbl_report = QLabel("Báo cáo nhận diện (mục đã bỏ qua và thư mục sai mẫu):", self)
        lbl_report.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 12px; font-weight: 600;")
        layout.addWidget(lbl_report)

        self.txt_report = QTextEdit(self)
        self.txt_report.setReadOnly(True)
        self.txt_report.setFixedHeight(110)
        self.txt_report.setStyleSheet(
            f"QTextEdit {{ background-color: {COLOR_SURFACE_SECONDARY}; color: {COLOR_TEXT_SECONDARY};"
            f" border: 1px solid {COLOR_BORDER_DEFAULT}; border-radius: 8px; font-size: 12px; padding: 8px; }}"
        )
        layout.addWidget(self.txt_report)

        # Footer
        footer = QHBoxLayout()
        footer.addStretch(1)

        btn_cancel = QPushButton("Hủy", self)
        btn_cancel.setProperty("class", "SecondaryBtn")
        btn_cancel.setFixedHeight(38)
        btn_cancel.clicked.connect(self.reject)
        footer.addWidget(btn_cancel)

        self.btn_import = QPushButton("Nạp Vào Danh Sách", self)
        self.btn_import.setProperty("class", "PrimaryBtn")
        self.btn_import.setFixedHeight(38)
        self.btn_import.clicked.connect(self._on_accept)
        footer.addWidget(self.btn_import)
        layout.addLayout(footer)

    # ------------------------------------------------------------------
    # Preview computation
    # ------------------------------------------------------------------
    def _compute_selection(self) -> List[Dict[str, Any]]:
        """Applies invalid/duplicate policies and returns the rows to import (ordered)."""
        load_invalid = self.cb_invalid.currentText() == self.INVALID_LOAD
        dup_policy = self.cb_duplicate.currentText()

        # Group by normalized MSSV to detect duplicates
        groups: Dict[str, List[Dict[str, Any]]] = {}
        for item in self.scanned:
            groups.setdefault(item["mssv"], []).append(item)

        selected: List[Dict[str, Any]] = []
        for item in self.scanned:
            if not item["mssv_valid"] and not load_invalid:
                continue
            group = groups[item["mssv"]]
            if len(group) > 1:
                if dup_policy == self.DUP_KEEP_FIRST and item is not group[0]:
                    continue
                if dup_policy == self.DUP_KEEP_LAST and item is not group[-1]:
                    continue
            selected.append(item)

        # Assign display labels (suffix for duplicates when keeping all)
        counters: Dict[str, int] = {}
        for item in selected:
            counters[item["mssv"]] = counters.get(item["mssv"], 0) + 1
            nth = counters[item["mssv"]]
            item["display_mssv"] = item["mssv"] if nth == 1 else f"{item['mssv']} ({nth})"
        return selected

    def _refresh_preview(self):
        selected = self._compute_selection()
        selected_ids = {id(x) for x in selected}

        # Reset imported items to the current selection
        self.import_items = [{
            "mssv": x["mssv"],
            "display_mssv": x["display_mssv"],
            "name": x["name"],
            "live_url": x["live_url"],
            "repo_url": x["repo_url"],
            "local_dir": x["local_dir"],
            "source_folder_path": x["local_dir"],
            "folder_name": x["folder_name"],
        } for x in selected]

        # Group sizes for duplicate status text
        group_sizes: Dict[str, int] = {}
        for item in self.scanned:
            group_sizes[item["mssv"]] = group_sizes.get(item["mssv"], 0) + 1

        any_name = any(x["name"].strip() for x in self.scanned)

        headers = ["MSSV", "File", "Live URL", "GitHub Repo", "Trạng Thái"]
        name_col = None
        if any_name:
            headers.insert(1, "Họ và Tên")
            name_col = 1

        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(0)

        for item in self.scanned:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setRowHeight(r, 40)

            col = 0
            item_mssv = QTableWidgetItem(item["folder_name"])
            item_mssv.setToolTip(f"Tên thư mục gốc: {item['folder_name']}")
            self.table.setItem(r, col, item_mssv)
            col += 1

            if name_col is not None:
                item_name = QTableWidgetItem(item["name"] or "")
                self.table.setItem(r, col, item_name)
                col += 1

            entry = item["entry_file"]
            item_file = QTableWidgetItem(Path(entry).name if entry else "—")
            if entry:
                item_file.setToolTip(entry)
            self.table.setItem(r, col, item_file)
            col += 1

            item_live = QTableWidgetItem(item["live_url"] or "—")
            item_live.setToolTip(item["live_url"] or "")
            self.table.setItem(r, col, item_live)
            col += 1

            item_repo = QTableWidgetItem(item["repo_url"] or "—")
            item_repo.setToolTip(item["repo_url"] or "")
            self.table.setItem(r, col, item_repo)
            col += 1

            status, color = self._row_status(item, group_sizes, selected_ids)
            item_status = QTableWidgetItem(status)
            item_status.setForeground(QColor(color))
            self.table.setItem(r, col, item_status)

        hdr = self.table.horizontalHeader()
        for c in range(self.table.columnCount()):
            hdr.setSectionResizeMode(c, QHeaderView.ResizeMode.Interactive)
        if self.table.columnCount() >= 5:
            hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(0, 130)
        self.table.setColumnWidth(self.table.columnCount() - 1, 260)

        self._update_report(group_sizes, selected)
        self.btn_import.setEnabled(len(self.import_items) > 0)

    def _row_status(self, item: Dict[str, Any], group_sizes: Dict[str, int], selected_ids: set):
        if not item["mssv_valid"]:
            if id(item) in selected_ids:
                return "Tên thư mục không phải MSSV hợp lệ — vẫn nạp", COLOR_WARNING
            return "Tên thư mục không phải MSSV hợp lệ — bỏ qua", COLOR_ERROR

        if group_sizes.get(item["mssv"], 1) > 1:
            if id(item) in selected_ids:
                return f"Trùng MSSV — giữ bản này ({item.get('display_mssv', item['mssv'])})", COLOR_WARNING
            return f"Trùng MSSV {item['mssv']} — bỏ qua", COLOR_ERROR

        return "Hợp lệ", COLOR_SUCCESS

    def _update_report(self, group_sizes: Dict[str, int], selected: List[Dict[str, Any]]):
        lines: List[str] = []
        lines.append(f"Nhận diện {len(self.scanned)} thư mục; sẽ nạp {len(selected)} bài.")
        lines.append(f"Bỏ qua {len(self.skipped_dirs)} thư mục hệ thống/ẩn"
                     + (f": {', '.join(self.skipped_dirs)}" if self.skipped_dirs else "."))
        lines.append(f"Bỏ qua {len(self.skipped_files)} file lẻ ở thư mục gốc"
                     + (f": {', '.join(self.skipped_files)}" if self.skipped_files else "."))

        invalid = [
            f"{x['folder_name']} (đọc là '{x['mssv'] or 'trống'}')"
            for x in self.scanned if not x["mssv_valid"]
        ]
        lines.append(
            "Thư mục không khớp mẫu MSSV: " + (", ".join(invalid) if invalid else "không có.")
        )

        dup_groups = {m: c for m, c in group_sizes.items() if c > 1}
        if dup_groups:
            dup_text = "; ".join(f"{m} ({c} thư mục)" for m, c in dup_groups.items())
            lines.append(f"MSSV trùng: {dup_text}.")
        else:
            lines.append("MSSV trùng: không có.")

        self.txt_report.setPlainText("\n".join(lines))

    # ------------------------------------------------------------------
    # Accept
    # ------------------------------------------------------------------
    def _on_accept(self):
        if not self.import_items:
            QMessageBox.warning(self, "Không Có Dữ Liệu", "Không có bài nộp nào hợp lệ để nạp.")
            return
        self.accept()
