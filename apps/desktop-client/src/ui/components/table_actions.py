"""AITA - Helpers dùng chung cho cột thao tác và ô văn bản nhiều dòng trong bảng.

Quy ước UI của dự án: mọi bảng có cột "Thao Tác" phải dựng ô bằng
:func:`make_action_cell` để nút luôn canh giữa và cùng khoảng cách 8px, thay vì
mỗi cửa sổ tự tạo QWidget/QHBoxLayout riêng.
"""

from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QWidget

from ui.styles.theme import COLOR_BORDER_DEFAULT, COLOR_TEXT_PRIMARY


def make_action_cell(buttons: List[QPushButton], parent: QWidget) -> QWidget:
    """Bọc các nút thao tác của một hàng vào ô canh giữa, khoảng cách đồng nhất 8px."""
    cell = QWidget(parent)
    cell.setStyleSheet("background: transparent;")
    layout = QHBoxLayout(cell)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    for btn in buttons:
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        layout.addWidget(btn)
    return cell


def make_row_button(text: str, color: str, parent: QWidget = None,
                    width: int = 54, height: int = 26) -> QPushButton:
    """Nút nhỏ dạng viền dùng trong cột thao tác / danh sách dòng.

    `color` là mã màu của chữ + viền (ví dụ #2F80ED cho Sửa, #EF4444 cho Xóa).
    `height` là chiều cao cuối cùng của nút (đã tính cả viền 1px).
    """
    btn = QPushButton(text, parent)
    btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    btn.setFixedSize(width, height)
    # Phải khai báo min/max-height trong QSS: theme chung đặt QPushButton
    # min-height/max-height 40px, nếu không ghi đè thì nút hàng bảng sẽ cao 42px
    # và bị cắt mép dưới trong ô bảng.
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #FFFFFF;
            color: {color};
            border: 1px solid {color};
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            min-height: {max(0, height - 2)}px;
            max-height: {max(0, height - 2)}px;
            height: {max(0, height - 2)}px;
            padding: 0;
        }}
        QPushButton:hover {{
            background-color: {color}14;
        }}
        QPushButton:disabled {{
            color: {COLOR_BORDER_DEFAULT};
            border-color: {COLOR_BORDER_DEFAULT};
            background-color: #F8FAFC;
        }}
    """)
    return btn


def preview_multiline(text: str, limit: int = 60) -> str:
    """Tóm tắt văn bản nhiều dòng cho ô bảng: dòng đầu + "(+N dòng)".

    Dòng rỗng ở cuối (do ký tự xuống dòng cuối chuỗi) không tính vào N.
    """
    normalized = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    if not normalized.strip():
        return "(trống)"
    lines = normalized.split("\n")
    while len(lines) > 1 and lines[-1] == "":
        lines.pop()
    extra = len(lines) - 1
    first = lines[0]
    if len(first) > limit:
        first = first[:limit].rstrip() + "..."
    if not first:
        first = "(dòng đầu trống)"
    return f"{first}  (+{extra} dòng)" if extra > 0 else first


def preview_tooltip(text: str, limit: int = 4000) -> str:
    """Tooltip hiển thị nội dung đầy đủ (cắt bớt nếu quá dài để tooltip không tràn)."""
    normalized = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    if not normalized:
        return "(trống)"
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[:limit]}\n... (còn {len(normalized) - limit} ký tự)"


def text_color_for_value(text: str) -> str:
    """Màu chữ cho ô bảng: nội dung rỗng hiển thị xám, có dữ liệu dùng màu chính."""
    return COLOR_TEXT_PRIMARY if (text or "").strip() else "#94A3B8"
