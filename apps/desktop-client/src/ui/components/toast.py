"""
AITA Toast Notification (pain #3): thông báo không chặn thay cho QMessageBox.information.

- Toast chỉ "dán" trên cửa sổ (widget con của parent), không khóa thao tác của giảng viên:
  trong khi toast hiển thị, vẫn click được nút, kéo được bảng bài nộp v.v.
- Hết ~4.5s tự mờ dần (fade out) rồi tự hủy; click vào toast để đóng ngay.
- Nhiều toast liên tiếp xếp chồng (cascade) vì nạp bài / chấm/báo lỗi thường đến dồn dập.
- Không dùng icon: nhất quán với quy ước "no emojis/icons" của desktop client.
"""

from typing import List, Optional

from PyQt6.QtCore import QPropertyAnimation, Qt, QTimer
from PyQt6.QtWidgets import QFrame, QGraphicsOpacityEffect, QLabel, QVBoxLayout, QWidget

# Bảng màu khớp design system (theme.py) + accent đậm hơn để chữ đọc rõ trên nền tint
_KIND_STYLES = {
    "success": {"bg": "#ECFDF3", "text": "#166534", "border": "#A7F3D0"},
    "warning": {"bg": "#FFF7E6", "text": "#92400E", "border": "#FDE68A"},
    "error": {"bg": "#FEF2F2", "text": "#B91C1C", "border": "#FECACA"},
    "info": {"bg": "#EFF6FF", "text": "#1E4FD8", "border": "#BFDBFE"},
}

_TOAST_MARGIN = 24
_TOAST_GAP = 8
_TOAST_MAX_CHARS = 260  # giữ toast ngắn gọn; chi tiết dài vẫn là việc của dialog
_AMDIN_WAIT_MS = 4500

_ACTIVE_TOASTS: List["ToastNotification"] = []


class ToastNotification(QFrame):
    """Một toast duy nhất: định vị + fade in + tự đóng, không chặn parent."""

    def __init__(self, parent: QWidget, message: str, kind: str = "info"):
        super().__init__(parent)
        self.setObjectName("AitaToast")
        palette = _KIND_STYLES.get(kind) or _KIND_STYLES["info"]

        text = (message or "").strip()
        if len(text) > _TOAST_MAX_CHARS:
            text = text[: _TOAST_MAX_CHARS - 1].rstrip() + "…"

        label = QLabel(text, self)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        label.setStyleSheet(
            f"color: {palette['text']}; background: transparent; font-weight: 600; border: none;"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.addWidget(label)

        self.setStyleSheet(f"""
            QFrame#AitaToast {{
                background-color: {palette['bg']};
                border: 1px solid {palette['border']};
                border-radius: 10px;
            }}
        """)

        outer = parent.width() - 2 * _TOAST_MARGIN
        self.setFixedWidth(max(280, min(460, outer)))

    def start(self, duration_ms: int = _AMDIN_WAIT_MS, stack_index: int = 0) -> None:
        """Đặt vị trí theo hàng đợi hiện có, raise + fade in, hẹn giờ tự đóng."""
        self.adjustSize()
        x = self.parentWidget().width() - self.width() - _TOAST_MARGIN
        y = _TOAST_MARGIN + stack_index * (self.height() + _TOAST_GAP)
        self.move(x, y)
        self.show()
        self.raise_()

        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        fade_in = QPropertyAnimation(effect, b"opacity", self)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setDuration(150)
        fade_in.start()

        QTimer.singleShot(max(500, duration_ms), self.close_toast)

    def mousePressEvent(self, event) -> None:
        self.close_toast()
        super().mousePressEvent(event)

    def close_toast(self) -> None:
        if self in _ACTIVE_TOASTS:
            _ACTIVE_TOASTS.remove(self)
        # Xếp lại vị trí các toast còn lại của cùng cửa sổ, không để lỗ hổng trên màn hình
        siblings = [t for t in _ACTIVE_TOASTS if t.parent() is self.parent()]
        for idx, mate in enumerate(siblings):
            mate.move(
                mate.parentWidget().width() - mate.width() - _TOAST_MARGIN,
                _TOAST_MARGIN + idx * (mate.height() + _TOAST_GAP),
            )

        effect = self.graphicsEffect()
        if effect is None:
            self.deleteLater()
            return
        fade_out = QPropertyAnimation(effect, b"opacity", self)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setDuration(200)
        fade_out.finished.connect(self.deleteLater)
        fade_out.start()


def show_toast(parent: Optional[QWidget], message: str, kind: str = "info", duration_ms: int = _AMDIN_WAIT_MS) -> None:
    """
    API chính: show_toast(window, "Đã nạp 32 bài nộp", kind="success").
    Không tạo cửa sổ modal, không chặn luồng công việc của giảng viên.
    """
    if parent is None or not (message or "").strip():
        return
    # Dọn các toast đã mờ/ẩn trước khi xếp hàng cho toast mới
    _ACTIVE_TOASTS[:] = [t for t in _ACTIVE_TOASTS if t.isVisible()]
    same_parent = [t for t in _ACTIVE_TOASTS if t.parent() is parent]
    toast = ToastNotification(parent, message, kind)
    _ACTIVE_TOASTS.append(toast)
    toast.start(duration_ms, stack_index=len(same_parent))
