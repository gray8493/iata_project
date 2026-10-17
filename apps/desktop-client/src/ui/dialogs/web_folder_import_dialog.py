"""
AITA Desktop Client - Web Submission Folder Import Dialog (PyQt6)
UC-19 (Web Studio): recognize students when loading a submissions folder.

Recognition rules (Web page only):
  - Each immediate sub-folder name IS the MSSV (e.g. SE180001); normalized trim + UPPERCASE.
  - Folder names must match MSSV_PATTERN (configurable); non-matching folders are surfaced
    in the preview (red) with a choice to "Vẫn nạp" or "Bỏ qua".
  - System/hidden folders (".*", __MACOSX, node_modules) and loose files directly in the
    root are skipped and reported.
  - Inside each student folder a single .txt file holds the links. When several exist we
    prefer links.txt, link.txt, readme.txt in that order; otherwise the folder is flagged
    as "Thiếu file link".
  - The .txt is read as UTF-8 (with/without BOM) or UTF-16; label prefixes ("Live:",
    "GitHub:", "Link 1:" ...) are ignored and every http(s) URL is captured (several
    links per line allowed).
  - The GitHub repo link is normalized to https://github.com/<user>/<repo>; every other
    link is treated as the Live URL. Extra links beyond the first of each kind are kept
    as warnings only.

This module performs recognition and display only. It never changes grading logic.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

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

# Priority order used when a student folder contains several .txt files.
LINK_FILE_PRIORITY = ("links.txt", "link.txt", "readme.txt")

# "Họ tên: ...", "Họ và tên: ...", "Tên: ...", "Name: ..."
NAME_LINE_PATTERN = re.compile(
    r"^\s*(?:h[oọ]\s*(?:v[àa]\s*)?t[êe]n|t[êe]n|name)\s*[:\-]\s*(.+?)\s*$",
    re.IGNORECASE
)
# Every http/https URL (several per line allowed); trailing punctuation trimmed later.
URL_PATTERN = re.compile(r"https?://[^\s,\)\]\"'<>]+", re.IGNORECASE)

GITHUB_HOST = "github.com"


# ------------------------------------------------------------------------------
# Small pure helpers (recognition only)
# ------------------------------------------------------------------------------
def read_text_file(path: Path) -> str:
    """Reads a .txt file as UTF-8 (with/without BOM) or UTF-16, tolerating bad bytes."""
    try:
        raw = path.read_bytes()
    except Exception:
        return ""
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        try:
            return raw.decode("utf-16")
        except Exception:
            pass
    if raw.startswith(b"\xef\xbb\xbf"):
        try:
            return raw.decode("utf-8-sig")
        except Exception:
            pass
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return raw.decode("utf-16")
        except Exception:
            return raw.decode("utf-8", errors="replace")


def select_link_file(folder: Path) -> Tuple[Optional[Path], str]:
    """
    Picks the .txt file that holds the links.
    Returns (path, status) where status is "" on success, "no_txt" or "ambiguous".
    """
    try:
        txt_files = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".txt"]
    except Exception:
        return None, "no_txt"
    if not txt_files:
        return None, "no_txt"
    if len(txt_files) == 1:
        return txt_files[0], ""
    by_name = {p.name.lower(): p for p in txt_files}
    for candidate in LINK_FILE_PRIORITY:
        if candidate in by_name:
            return by_name[candidate], ""
    return None, "ambiguous"


def classify_url(raw_url: str) -> Tuple[Optional[str], str, str]:
    """
    Classifies a single link.
    Returns (kind, normalized, error) where kind is "repo", "live" or None.
    A github.com/<user>/<repo> link is normalized (drops /tree/..., .git and trailing "/").
    """
    url = raw_url.strip().rstrip(".,;:!?)\"]'")
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    if host.startswith("www."):
        host = host[4:]
    if host == GITHUB_HOST or host.endswith("." + GITHUB_HOST):
        parts = [p for p in parsed.path.split("/") if p]
        if len(parts) >= 2:
            user, repo = parts[0], parts[1]
            if repo.lower().endswith(".git"):
                repo = repo[:-4]
            return "repo", f"https://{GITHUB_HOST}/{user}/{repo}", ""
        return None, url, "Link GitHub không đúng dạng github.com/<user>/<repo>"
    if host:
        return "live", url, ""
    return None, url, "Link không đúng định dạng http:// hoặc https://"


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

        self.setWindowTitle("Chọn Thư Mục Bài Nộp")
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
            info = self._read_links(entry)

            self.scanned.append({
                "folder_name": folder_name,
                "mssv": mssv,
                "mssv_valid": is_valid,
                "local_dir": str(entry),
                "link_file": str(info["link_file"]) if info["link_file"] else "",
                "link_file_name": Path(info["link_file"]).name if info["link_file"] else "",
                "link_file_status": info["link_file_status"],
                "name": info["name"],
                "live_url": info["live_url"],
                "repo_url": info["repo_url"],
                "extras": info["extras"],
                "errors": info["errors"],
            })

    def _read_links(self, folder: Path) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "link_file": None,
            "link_file_status": "",
            "name": "",
            "live_url": "",
            "repo_url": "",
            "extras": [],
            "errors": [],
        }

        link_file, file_status = select_link_file(folder)
        if link_file is None:
            result["link_file_status"] = file_status
            return result

        result["link_file"] = link_file
        text = read_text_file(link_file)
        if not text:
            return result

        for line in text.splitlines():
            m = NAME_LINE_PATTERN.match(line)
            if m and not result["name"]:
                result["name"] = m.group(1).strip()

        live_candidates: List[str] = []
        repo_candidates: List[str] = []
        for raw_url in URL_PATTERN.findall(text):
            kind, normalized, error = classify_url(raw_url)
            if error:
                result["errors"].append(f"{normalized}: {error}")
            elif kind == "repo":
                repo_candidates.append(normalized)
            elif kind == "live":
                live_candidates.append(normalized)

        result["live_url"] = live_candidates[0] if live_candidates else ""
        result["repo_url"] = repo_candidates[0] if repo_candidates else ""
        result["extras"] = live_candidates[1:] + repo_candidates[1:]
        return result

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        lbl_rule = QLabel(
            "Quy ước nhận diện: tên mỗi thư mục con CHÍNH LÀ MSSV của sinh viên "
            f"(mẫu hợp lệ: {MSSV_PATTERN_LABEL}). Mỗi thư mục cần một file .txt chứa "
            "link Live URL và link GitHub Repo.",
            self
        )
        lbl_rule.setWordWrap(True)
        lbl_rule.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 13px; line-height: 1.4;")
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
        footer.setSpacing(12)
        footer.addStretch(1)

        btn_cancel = QPushButton("Hủy", self)
        btn_cancel.setProperty("class", "SecondaryBtn")
        btn_cancel.setFixedHeight(38)
        btn_cancel.clicked.connect(self.reject)
        footer.addWidget(btn_cancel)

        self.btn_import_all = QPushButton("Nạp Tất Cả (kể cả bài thiếu link)", self)
        self.btn_import_all.setProperty("class", "SecondaryBtn")
        self.btn_import_all.setFixedHeight(38)
        self.btn_import_all.clicked.connect(lambda: self._on_accept(load_all=True))
        footer.addWidget(self.btn_import_all)

        self.btn_import_valid = QPushButton("Nạp Các Bài Hợp Lệ", self)
        self.btn_import_valid.setProperty("class", "PrimaryBtn")
        self.btn_import_valid.setFixedHeight(38)
        self.btn_import_valid.clicked.connect(lambda: self._on_accept(load_all=False))
        footer.addWidget(self.btn_import_valid)
        layout.addLayout(footer)

    # ------------------------------------------------------------------
    # Preview computation
    # ------------------------------------------------------------------
    def _compute_selection(self) -> List[Dict[str, Any]]:
        """Applies invalid/duplicate policies and returns the rows to import (ordered)."""
        load_invalid = self.cb_invalid.currentText() == self.INVALID_LOAD
        dup_policy = self.cb_duplicate.currentText()

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

        counters: Dict[str, int] = {}
        for item in selected:
            counters[item["mssv"]] = counters.get(item["mssv"], 0) + 1
            nth = counters[item["mssv"]]
            item["display_mssv"] = item["mssv"] if nth == 1 else f"{item['mssv']} ({nth})"
        return selected

    def _link_status(self, item: Dict[str, Any]) -> Tuple[str, str, bool]:
        """Returns (text, color, is_complete) for the link part of a folder."""
        if item["link_file_status"]:
            return "Thiếu file link", COLOR_WARNING, False
        if item["errors"]:
            return "Cảnh báo", COLOR_WARNING, False
        missing_live = not item["live_url"]
        missing_repo = not item["repo_url"]
        if missing_live and missing_repo:
            return "Thiếu Live URL & GitHub", COLOR_ERROR, False
        if missing_live:
            return "Thiếu Live URL", COLOR_ERROR, False
        if missing_repo:
            return "Thiếu GitHub", COLOR_ERROR, False
        if item["extras"]:
            return "Đủ link (có link thừa)", COLOR_WARNING, True
        return "Đủ link", COLOR_SUCCESS, True

    def _is_valid(self, item: Dict[str, Any]) -> bool:
        return (
            not item["link_file_status"]
            and not item["errors"]
            and bool(item["live_url"])
            and bool(item["repo_url"])
        )

    def _refresh_preview(self):
        selected = self._compute_selection()
        selected_ids = {id(x) for x in selected}
        self._selected = selected

        # Group sizes for duplicate status text
        group_sizes: Dict[str, int] = {}
        for item in self.scanned:
            group_sizes[item["mssv"]] = group_sizes.get(item["mssv"], 0) + 1

        any_name = any(x["name"].strip() for x in self.scanned)

        headers = ["MSSV", "File link", "Live URL", "GitHub Repo", "Trạng Thái"]
        if any_name:
            headers.insert(1, "Họ và Tên")

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

            if any_name:
                item_name = QTableWidgetItem(item["name"] or "")
                item_name.setToolTip(item["name"] or "")
                self.table.setItem(r, col, item_name)
                col += 1

            item_file = QTableWidgetItem(item["link_file_name"] or "—")
            if item["link_file"]:
                item_file.setToolTip(item["link_file"])
            elif item["link_file_status"] == "ambiguous":
                item_file.setToolTip("Có nhiều file .txt nhưng không xác định được file link (ưu tiên links.txt, link.txt, readme.txt).")
            else:
                item_file.setToolTip("Không tìm thấy file .txt trong thư mục.")
            self.table.setItem(r, col, item_file)
            col += 1

            item_live = QTableWidgetItem(item["live_url"] or "—")
            item_live.setToolTip(item["live_url"] or "")
            if item["errors"] or not item["live_url"]:
                item_live.setForeground(QColor(COLOR_ERROR if not item["errors"] else COLOR_WARNING))
            self.table.setItem(r, col, item_live)
            col += 1

            item_repo = QTableWidgetItem(item["repo_url"] or "—")
            item_repo.setToolTip(item["repo_url"] or "")
            if item["errors"] or not item["repo_url"]:
                item_repo.setForeground(QColor(COLOR_ERROR if not item["errors"] else COLOR_WARNING))
            self.table.setItem(r, col, item_repo)
            col += 1

            status, color = self._row_status(item, group_sizes, selected_ids)
            item_status = QTableWidgetItem(status)
            item_status.setForeground(QColor(color))
            item_status.setToolTip(self._status_tooltip(item))
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
        valid_count = sum(1 for x in selected if self._is_valid(x))
        self.btn_import_valid.setEnabled(valid_count > 0)
        self.btn_import_all.setEnabled(len(selected) > 0)

    def _row_status(self, item: Dict[str, Any], group_sizes: Dict[str, int], selected_ids: set) -> Tuple[str, str]:
        if not item["mssv_valid"]:
            if id(item) in selected_ids:
                return "Tên thư mục không phải MSSV hợp lệ — vẫn nạp", COLOR_WARNING
            return "Tên thư mục không phải MSSV hợp lệ — bỏ qua", COLOR_ERROR

        if group_sizes.get(item["mssv"], 1) > 1:
            if id(item) in selected_ids:
                return f"Trùng MSSV — giữ bản này ({item.get('display_mssv', item['mssv'])})", COLOR_WARNING
            return f"Trùng MSSV {item['mssv']} — bỏ qua", COLOR_ERROR

        text, color, _ = self._link_status(item)
        return text, color

    def _status_tooltip(self, item: Dict[str, Any]) -> str:
        tips: List[str] = []
        if item["link_file_status"] == "no_txt":
            tips.append("Không có file .txt chứa link trong thư mục.")
        elif item["link_file_status"] == "ambiguous":
            tips.append("Có nhiều file .txt; hãy đặt tên links.txt, link.txt hoặc readme.txt.")
        if item["errors"]:
            tips.append("Link sai định dạng: " + "; ".join(item["errors"]))
        if item["extras"]:
            tips.append("Link thừa (chỉ dùng link đầu tiên mỗi loại): " + "; ".join(item["extras"]))
        return "\n".join(tips)

    def _update_report(self, group_sizes: Dict[str, int], selected: List[Dict[str, Any]]):
        lines: List[str] = []
        valid_count = sum(1 for x in selected if self._is_valid(x))
        lines.append(f"Nhận diện {len(self.scanned)} thư mục; sẽ nạp {valid_count} bài đủ link (hoặc tất cả nếu chọn 'Nạp Tất Cả').")
        lines.append(f"Bỏ qua {len(self.skipped_dirs)} thư mục hệ thống/ẩn"
                     + (f": {', '.join(self.skipped_dirs)}" if self.skipped_dirs else "."))
        lines.append(f"Bỏ qua {len(self.skipped_files)} file lẻ ở thư mục gốc"
                     + (f": {', '.join(self.skipped_files)}" if self.skipped_files else "."))

        invalid = [
            f"{x['folder_name']} (đọc là '{x['mssv'] or 'trống'}')"
            for x in self.scanned if not x["mssv_valid"]
        ]
        lines.append("Thư mục không khớp mẫu MSSV: " + (", ".join(invalid) if invalid else "không có."))

        dup_groups = {m: c for m, c in group_sizes.items() if c > 1}
        if dup_groups:
            dup_text = "; ".join(f"{m} ({c} thư mục)" for m, c in dup_groups.items())
            lines.append(f"MSSV trùng: {dup_text}.")
        else:
            lines.append("MSSV trùng: không có.")

        missing_link = [x["folder_name"] for x in self.scanned
                        if x["link_file_status"] or not x["live_url"] or not x["repo_url"] or x["errors"]]
        lines.append("Bài thiếu/cần lưu ý về link: "
                     + (", ".join(missing_link) if missing_link else "không có."))

        self.txt_report.setPlainText("\n".join(lines))

    # ------------------------------------------------------------------
    # Accept
    # ------------------------------------------------------------------
    def _on_accept(self, load_all: bool):
        selection = getattr(self, "_selected", [])
        items = selection if load_all else [x for x in selection if self._is_valid(x)]
        if not items:
            QMessageBox.warning(
                self, "Không Có Dữ Liệu",
                "Không có bài nộp nào phù hợp để nạp với lựa chọn hiện tại."
            )
            return

        self.import_items = [{
            "mssv": x["mssv"],
            "display_mssv": x.get("display_mssv", x["mssv"]),
            "name": x["name"],
            "live_url": x["live_url"],
            "repo_url": x["repo_url"],
            "local_dir": x["local_dir"],
            "source_folder_path": x["local_dir"],
            "folder_name": x["folder_name"],
            "link_file_name": x["link_file_name"],
            "has_link": self._is_valid(x),
        } for x in items]
        self.accept()
