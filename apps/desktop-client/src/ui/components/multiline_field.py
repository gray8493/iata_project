"""AITA - Ô nhập dữ liệu nhiều dòng dùng cho stdin/stdout của testcase.

Hai chế độ trên cùng một nguồn dữ liệu (chuỗi, các dòng nối bằng "\\n"):

- "Văn bản": QPlainTextEdit có số dòng (chế độ mặc định).
- "Theo dòng": mỗi dòng là một hàng có số thứ tự, ô nhập riêng, nút "Xóa" và
  kéo thả để đổi thứ tự; nút "Thêm dòng" ở dưới cùng.

Chuyển qua lại giữa hai chế độ KHÔNG làm mất dữ liệu vì cả hai đều đọc/ghi vào
cùng một chuỗi `self._text`. Kiểu lưu trong CSDL không đổi: vẫn là một chuỗi,
các dòng nối bằng "\\n".
"""

import re
from typing import List, Tuple

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractItemView, QButtonGroup, QCheckBox, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QPushButton, QSizePolicy, QStackedWidget,
    QVBoxLayout, QWidget,
)

from ui.components.code_editor import CodeEditor
from ui.components.table_actions import make_row_button
from ui.styles.theme import (
    COLOR_BORDER_DEFAULT, COLOR_ERROR, COLOR_PRIMARY, COLOR_PRIMARY_BG,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_WARNING_BG,
)

HIDDEN_TRAILING_SPACE = "·"
HIDDEN_LINE_END = "↵"
WARNING_TEXT_COLOR = "#B45309"

_TRAILING_BLANKS = re.compile(r"[ \t]+$")


# ==============================================================================
# HÀM THUẦN (không phụ thuộc widget) - dễ kiểm thử
# ==============================================================================
def visualize_hidden_chars(text: str) -> str:
    """Hiện khoảng trắng thừa cuối dòng bằng '·' và cuối mỗi dòng bằng '↵'."""
    lines = (text or "").split("\n")
    out = []
    for line in lines:
        stripped = _TRAILING_BLANKS.sub("", line)
        out.append(stripped + HIDDEN_TRAILING_SPACE * (len(line) - len(stripped)) + HIDDEN_LINE_END)
    return "\n".join(out)


def unvisualize_line(text: str) -> str:
    """Khôi phục khoảng trắng thật từ một dòng đang hiện ký tự ẩn."""
    value = text or ""
    if value.endswith(HIDDEN_LINE_END):
        value = value[: -len(HIDDEN_LINE_END)]
    stripped = value.rstrip(HIDDEN_TRAILING_SPACE)
    return stripped + " " * (len(value) - len(stripped))


def line_stats(text: str) -> Tuple[int, int]:
    """Trả về (số dòng, số ký tự). Dòng trống do ký tự xuống dòng cuối không tính."""
    if not text:
        return 0, 0
    lines = text.count("\n")
    if not text.endswith("\n"):
        lines += 1
    return lines, len(text)


def text_warnings(text: str, label: str = "Dữ liệu") -> List[str]:
    """Cảnh báo không chặn lưu: khoảng trắng thừa cuối dòng, thiếu xuống dòng cuối."""
    if not text:
        return []
    warnings: List[str] = []
    lines = text.split("\n")
    trailing_rows = [str(i + 1) for i, line in enumerate(lines) if _TRAILING_BLANKS.search(line)]
    if trailing_rows:
        shown = ", ".join(trailing_rows[:5])
        more = "" if len(trailing_rows) <= 5 else f" và {len(trailing_rows) - 5} dòng khác"
        warnings.append(
            f"{label}: {len(trailing_rows)} dòng có khoảng trắng thừa cuối dòng (dòng {shown}{more})."
        )
    if not text.endswith("\n"):
        warnings.append(f"{label}: thiếu ký tự xuống dòng ở cuối.")
    return warnings


# ==============================================================================
# WIDGET
# ==============================================================================
class MultiLineField(QWidget):
    """Ô nhập nhiều dòng 2 chế độ (Văn bản / Theo dòng) + thống kê + cảnh báo."""

    changed = pyqtSignal()

    def __init__(self, title: str, placeholder: str = "", parent=None,
                 required: bool = False, min_height: int = 200):
        super().__init__(parent)
        self._title = title
        self._placeholder = placeholder
        self._required = required
        self._text = ""
        self._mode = "text"
        self._lines: List[str] = []
        self._updating = False

        self._build_ui(min_height)
        self._refresh_meta()

    # ------------------------------------------------------------------- build
    def _build_ui(self, min_height: int):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        header = QHBoxLayout()
        header.setSpacing(8)
        self.lbl_title = QLabel(self._title, self)
        self.lbl_title.setStyleSheet(
            f"font-weight: 600; font-size: 13px; line-height: 1.4; color: {COLOR_TEXT_PRIMARY};"
        )
        header.addWidget(self.lbl_title)
        header.addStretch(1)

        self.btn_mode_text = QPushButton("Văn bản", self)
        self.btn_mode_lines = QPushButton("Theo dòng", self)
        self.group_mode = QButtonGroup(self)
        self.group_mode.setExclusive(True)
        for index, btn in enumerate((self.btn_mode_text, self.btn_mode_lines)):
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #FFFFFF; color: {COLOR_TEXT_SECONDARY};
                    border: 1px solid {COLOR_BORDER_DEFAULT}; border-radius: 6px;
                    font-size: 12px; padding: 0 10px;
                    min-height: 28px; max-height: 28px; height: 28px;
                }}
                QPushButton:checked {{
                    background-color: {COLOR_PRIMARY_BG}; color: {COLOR_PRIMARY};
                    border: 1px solid {COLOR_PRIMARY}; font-weight: 600;
                }}
            """)
            self.group_mode.addButton(btn, index)
            header.addWidget(btn)
        self.btn_mode_text.setChecked(True)
        self.group_mode.idClicked.connect(self._on_mode_clicked)

        layout.addLayout(header)

        self.chk_hidden = QCheckBox("Hiện ký tự ẩn", self)
        self.chk_hidden.setToolTip(
            "Hiện khoảng trắng thừa cuối dòng bằng dấu chấm (·) và ký tự xuống dòng bằng mũi tên (↵).\n"
            "Khi bật, ô dữ liệu chỉ để xem; tắt đi để sửa tiếp."
        )
        self.chk_hidden.setStyleSheet(f"font-size: 11px; color: {COLOR_TEXT_SECONDARY};")
        self.chk_hidden.toggled.connect(self._on_hidden_toggled)

        self.stack = QStackedWidget(self)
        self.stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Trang 1: văn bản
        self.editor = CodeEditor(self, read_only=False, min_height=min_height)
        self.editor.setPlaceholderText(self._placeholder)
        self.editor.textChanged.connect(self._on_editor_text_changed)
        self.stack.addWidget(self.editor)

        # Trang 2: theo dòng
        self.page_lines = QWidget(self)
        lines_layout = QVBoxLayout(self.page_lines)
        lines_layout.setContentsMargins(0, 0, 0, 0)
        lines_layout.setSpacing(6)

        self.list_lines = QListWidget(self.page_lines)
        self.list_lines.setMinimumHeight(min_height - 44)
        self.list_lines.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.list_lines.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.list_lines.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list_lines.setStyleSheet(f"""
            QListWidget {{
                border: 1px solid {COLOR_BORDER_DEFAULT}; border-radius: 8px;
                background-color: #FFFFFF; padding: 4px;
            }}
            QListWidget::item {{ border-bottom: 1px solid #F1F5F9; }}
            QListWidget::item:selected {{ background-color: {COLOR_PRIMARY_BG}; }}
        """)
        self.list_lines.model().rowsMoved.connect(self._on_rows_moved)
        lines_layout.addWidget(self.list_lines, 1)

        line_buttons = QHBoxLayout()
        line_buttons.setSpacing(8)
        self.btn_add_line = QPushButton("Thêm dòng", self.page_lines)
        self.btn_add_line.setProperty("class", "SecondaryBtn")
        self.btn_add_line.setFixedHeight(32)
        self.btn_add_line.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_line.clicked.connect(self._add_line)
        line_buttons.addWidget(self.btn_add_line)
        line_buttons.addStretch(1)
        self.lbl_line_hint = QLabel("Kéo thả để đổi thứ tự dòng.", self.page_lines)
        self.lbl_line_hint.setStyleSheet(f"font-size: 11px; color: {COLOR_TEXT_SECONDARY};")
        line_buttons.addWidget(self.lbl_line_hint)
        lines_layout.addLayout(line_buttons)

        self.stack.addWidget(self.page_lines)
        layout.addWidget(self.stack, 1)

        self.lbl_meta = QLabel("0 dòng, 0 ký tự", self)
        self.lbl_meta.setStyleSheet(f"font-size: 11px; color: {COLOR_TEXT_SECONDARY};")
        meta_row = QHBoxLayout()
        meta_row.setSpacing(8)
        meta_row.addWidget(self.lbl_meta)
        meta_row.addStretch(1)
        meta_row.addWidget(self.chk_hidden)
        layout.addLayout(meta_row)

        self.lbl_warning = QLabel("", self)
        self.lbl_warning.setWordWrap(True)
        self.lbl_warning.setStyleSheet(
            f"font-size: 11px; color: {WARNING_TEXT_COLOR}; background-color: {COLOR_WARNING_BG};"
            "border: 1px solid #FDE68A; border-radius: 6px; padding: 4px 6px; line-height: 1.4;"
        )
        self.lbl_warning.setVisible(False)
        layout.addWidget(self.lbl_warning)

        self.lbl_error = QLabel("", self)
        self.lbl_error.setWordWrap(True)
        self.lbl_error.setStyleSheet(f"font-size: 11px; color: {COLOR_ERROR}; line-height: 1.4;")
        self.lbl_error.setVisible(False)
        layout.addWidget(self.lbl_error)

    # --------------------------------------------------------------------- API
    def text(self) -> str:
        """Luôn trả về dữ liệu thật (chuỗi nhiều dòng), kể cả khi đang hiện ký tự ẩn."""
        return self._text

    def set_text(self, value: str):
        """Nạp dữ liệu mới (không phát signal `changed`)."""
        self._text = value or ""
        self._lines = self._text.split("\n") if self._text else [""]
        self._updating = True
        try:
            self._set_editor_text(self._display_text_for_editor(self._text))
            if self._mode == "lines":
                self._rebuild_line_rows()
        finally:
            self._updating = False
        self._refresh_meta()

    def set_required(self, required: bool):
        self._required = required
        self._refresh_meta()

    def validation_error(self) -> str:
        if self._required and not self.text().strip():
            return "Kết quả kỳ vọng (stdout) không được để trống."
        return ""

    def mode(self) -> str:
        return self._mode

    # ----------------------------------------------------------------- helpers
    def _display_text_for_editor(self, text: str) -> str:
        return visualize_hidden_chars(text) if self.chk_hidden.isChecked() else text

    def _set_editor_text(self, text: str):
        self.editor.blockSignals(True)
        try:
            self.editor.setPlainText(text)
        finally:
            self.editor.blockSignals(False)

    def _refresh_meta(self):
        lines, chars = line_stats(self._text)
        self.lbl_meta.setText(f"{lines} dòng, {chars} ký tự")

        warnings = text_warnings(self._text, self._title)
        self.lbl_warning.setText(" ".join(warnings))
        self.lbl_warning.setVisible(bool(warnings))

        error = self.validation_error()
        self.lbl_error.setText(error)
        self.lbl_error.setVisible(bool(error))

    # -------------------------------------------------------------- text mode
    def _on_editor_text_changed(self):
        if self._updating or self.chk_hidden.isChecked():
            return
        self._text = self.editor.toPlainText()
        if self._mode == "lines":
            self._lines = self._text.split("\n") if self._text else [""]
        self._refresh_meta()
        self.changed.emit()

    # -------------------------------------------------------------- line mode
    def _on_mode_clicked(self, index: int):
        mode = "text" if index == 0 else "lines"
        if mode == self._mode:
            return
        if self._mode == "text" and not self.chk_hidden.isChecked():
            self._text = self.editor.toPlainText()
        self._mode = mode
        if mode == "lines":
            self._lines = self._text.split("\n") if self._text else [""]
            self._rebuild_line_rows()
            self.stack.setCurrentWidget(self.page_lines)
        else:
            self._set_editor_text(self._display_text_for_editor(self._text))
            self.stack.setCurrentWidget(self.editor)
        self._refresh_meta()

    def _rebuild_line_rows(self):
        self.list_lines.blockSignals(True)
        try:
            for index in reversed(range(self.list_lines.count())):
                old_widget = self.list_lines.itemWidget(self.list_lines.item(index))
                if old_widget is not None:
                    old_widget.setParent(None)
                    old_widget.deleteLater()
            self.list_lines.clear()
            for index, line in enumerate(self._lines):
                item = QListWidgetItem()
                item.setFlags(
                    Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
                    | Qt.ItemFlag.ItemIsDragEnabled
                )
                self.list_lines.addItem(item)
                row = self._build_line_row(index, line)
                item.setSizeHint(row.sizeHint())
                self.list_lines.setItemWidget(item, row)
        finally:
            self.list_lines.blockSignals(False)

    def _build_line_row(self, index: int, line: str) -> QWidget:
        row = QWidget(self.list_lines)
        row.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(6, 3, 6, 3)
        layout.setSpacing(8)

        lbl_no = QLabel(f"{index + 1}.", row)
        lbl_no.setFixedWidth(32)
        lbl_no.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        lbl_no.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_SECONDARY};")
        layout.addWidget(lbl_no)

        edit = QLineEdit(row)
        edit.setFixedHeight(30)
        edit.setPlaceholderText("(dòng trống)")
        edit.setStyleSheet(f"""
            QLineEdit {{
                font-family: 'Consolas', 'Cascadia Mono', 'Segoe UI Mono', monospace;
                font-size: 13px; padding: 2px 8px;
                border: 1px solid {COLOR_BORDER_DEFAULT}; border-radius: 6px;
                background-color: #FFFFFF;
            }}
            QLineEdit:focus {{ border: 1px solid {COLOR_PRIMARY}; }}
        """)
        if self.chk_hidden.isChecked():
            edit.setText(visualize_hidden_chars(line))
            edit.setReadOnly(True)
        else:
            edit.setText(line)
        edit.textEdited.connect(lambda value, editor=edit: self._on_line_edited(editor, value))
        layout.addWidget(edit, 1)

        btn_del = make_row_button("Xóa", COLOR_ERROR, row, width=46, height=26)
        btn_del.clicked.connect(lambda _=False, editor=edit: self._delete_line_of(editor))
        layout.addWidget(btn_del)

        return row

    def _row_of_editor(self, editor: QLineEdit) -> int:
        for index in range(self.list_lines.count()):
            row = self.list_lines.itemWidget(self.list_lines.item(index))
            if row is not None and row.findChild(QLineEdit) is editor:
                return index
        return -1

    def _on_line_edited(self, editor: QLineEdit, value: str):
        index = self._row_of_editor(editor)
        if index < 0:
            return
        self._lines[index] = value
        self._sync_text_from_lines()

    def _delete_line_of(self, editor: QLineEdit):
        index = self._row_of_editor(editor)
        if index < 0:
            return
        del self._lines[index]
        if not self._lines:
            self._lines = [""]
        self._rebuild_line_rows()
        self._sync_text_from_lines()

    def _add_line(self):
        self._lines.append("")
        self._rebuild_line_rows()
        self.list_lines.setCurrentRow(self.list_lines.count() - 1)
        self._sync_text_from_lines()

    def _on_rows_moved(self, *_args):
        # Đọc lại nội dung theo thứ tự mới sau khi Qt hoàn tất việc di chuyển item.
        QTimer.singleShot(0, self._apply_new_line_order)

    def _apply_new_line_order(self):
        texts: List[str] = []
        for index in range(self.list_lines.count()):
            row = self.list_lines.itemWidget(self.list_lines.item(index))
            edit = row.findChild(QLineEdit) if row is not None else None
            value = edit.text() if edit is not None else ""
            texts.append(unvisualize_line(value) if self.chk_hidden.isChecked() else value)
        if not texts:
            texts = [""]
        self._lines = texts
        self._rebuild_line_rows()
        self._sync_text_from_lines()

    def _sync_text_from_lines(self):
        self._text = "\n".join(self._lines)
        self._refresh_meta()
        self.changed.emit()

    # ------------------------------------------------------------ hidden chars
    def _on_hidden_toggled(self, checked: bool):
        self._updating = True
        try:
            if self._mode == "text":
                self.editor.setReadOnly(checked)
                self._set_editor_text(self._display_text_for_editor(self._text))
            else:
                self._rebuild_line_rows()
        finally:
            self._updating = False
        self._refresh_meta()

