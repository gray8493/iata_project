"""AITA - Monospace editor with a line-number gutter (shared by dialogs).

Dùng chung cho các hộp thoại cần sửa/nhìn văn bản nhiều dòng (stdin/stdout,
mã nguồn). Font monospace có glyph tiếng Việt (Consolas / Cascadia Mono /
Segoe UI Mono) và line-height thật (140%) đặt qua QTextBlockFormat vì Qt
Style Sheet không hỗ trợ thuộc tính `line-height`.
"""

from PyQt6.QtCore import QRect, QSize, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QTextBlockFormat, QTextCursor
from PyQt6.QtWidgets import QPlainTextEdit, QWidget

MONO_FONT_FAMILY = "'Consolas', 'Cascadia Mono', 'Segoe UI Mono', 'Courier New', monospace"
MONO_FONT_SIZE = 13
LINE_HEIGHT_PERCENT = 140


class LineNumberArea(QWidget):
    """Gutter hiển thị số dòng của :class:`CodeEditor`."""

    def __init__(self, editor: "CodeEditor"):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):  # noqa: N802 - Qt API
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):  # noqa: N802 - Qt API
        self.code_editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """QPlainTextEdit + số dòng, font monospace tiếng Việt, line-height 140%."""

    def __init__(self, parent=None, read_only: bool = False, min_height: int = 200,
                 wrap: bool = True):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)

        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        self.setLineWrapMode(
            QPlainTextEdit.LineWrapMode.WidgetWidth if wrap
            else QPlainTextEdit.LineWrapMode.NoWrap
        )
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded if not wrap
            else Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.setReadOnly(read_only)
        self.setMinimumHeight(min_height)
        self.setTabChangesFocus(False)
        self.setStyleSheet(f"""
            QPlainTextEdit {{
                font-family: {MONO_FONT_FAMILY};
                font-size: {MONO_FONT_SIZE}px;
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 6px;
                selection-background-color: #BFDBFE;
                selection-color: #0F172A;
            }}
            QPlainTextEdit:focus {{
                border: 1px solid #2F80ED;
            }}
            QPlainTextEdit[readOnly="true"] {{
                background-color: #F8FAFC;
            }}
        """)
        self._apply_line_height()

    # ------------------------------------------------------------------ gutter
    def line_number_area_width(self) -> int:
        digits = 1
        value = max(1, self.blockCount())
        while value >= 10:
            value //= 10
            digits += 1
        return 16 + self.fontMetrics().horizontalAdvance("9") * digits

    def update_line_number_area_width(self, _block_count):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):  # noqa: N802 - Qt API
        super().resizeEvent(event)
        contents = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(contents.left(), contents.top(),
                  self.line_number_area_width(), contents.height())
        )

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#F8FAFC"))
        painter.setPen(QColor("#E2E8F0"))
        painter.drawLine(event.rect().topRight(), event.rect().bottomRight())

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#94A3B8"))
                painter.setFont(self.font())
                painter.drawText(
                    0, int(top), self.line_number_area.width() - 8,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight, number
                )
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    # --------------------------------------------------------------- line-height
    def _apply_line_height(self):
        """Đặt line-height thật (140%) cho toàn bộ document."""
        cursor = self.textCursor()
        position = cursor.position()
        fmt = QTextBlockFormat()
        fmt.setLineHeight(LINE_HEIGHT_PERCENT,
                          QTextBlockFormat.LineHeightTypes.ProportionalHeight.value)
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.mergeBlockFormat(fmt)
        cursor.clearSelection()
        cursor.setPosition(min(position, max(0, len(self.toPlainText()))))
        self.setTextCursor(cursor)

    def setPlainText(self, text: str):  # noqa: N802 - Qt API
        super().setPlainText(text or "")
        self._apply_line_height()

    def set_display_text(self, text: str):
        """Hiển thị nội dung mới nhất và luôn áp lại line-height."""
        self.setPlainText(text)
