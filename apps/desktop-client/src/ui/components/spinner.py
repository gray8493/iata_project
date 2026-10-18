"""
AITA Desktop Client - Circular Loading Spinner
Legacy overlay hiển thị vòng tròn xoay + thông điệp trong lúc task dài
(quét thư mục, chấm lại bài, AI nhận xét...). Không chặn luồngQt chính.

API:
    start_spinner(parent, "Đang nạp bài nộp...")   -> hiển thị trên parent
    stop_spinner(parent)                           -> gỡ overlay
"""
from typing import Dict, Optional

from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from PyQt6.QtWidgets import QFrame

# Registry: parent -> overlay đang chạy
_ACTIVE_SPINNERS: Dict[int, "SpinnerOverlay"] = {}


class CircularSpinner(QWidget):
    """Vòng tròn xoay vẽ bằng QPainter (track xám + cung xanh trượt quanh)."""

    def __init__(self, size: int = 48, color: str = "#2563EB", thickness: int = 4, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._angle = 0
        self._color = QColor(color)
        self._thickness = thickness
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(16)

    def _tick(self):
        self._angle = (self._angle + 6) % 360
        if self.isVisible():
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(
            self._thickness / 2,
            self._thickness / 2,
            self.width() - self._thickness,
            self.height() - self._thickness,
        )
        track_pen = QPen(QColor("#E2E8F0"), self._thickness, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.drawArc(rect, 0, 360 * 16)
        arc_pen = QPen(self._color, self._thickness, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(arc_pen)
        painter.drawArc(rect, -self._angle * 16, 110 * 16)


class SpinnerOverlay(QWidget):
    """Lớp phủ bán trong suốt trên parent, giữa hiển thị spinner + thông điệp."""

    def __init__(self, parent: QWidget, message: str = "Đang xử lý..."):
        super().__init__(parent)
        self.setAutoFillBackground(False)
        self.setStyleSheet("background-color: rgba(248, 250, 252, 150);")

        card = QFrame(self)
        card.setObjectName("SpinnerCard")
        card.setStyleSheet("""
            QFrame#SpinnerCard {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)

        self.lbl_message = QLabel(message, card)
        self.lbl_message.setObjectName("SpinnerMessage")
        self.lbl_message.setStyleSheet("""
            QLabel#SpinnerMessage {
                color: #334155;
                font-size: 13px;
                font-weight: 600;
                background: transparent;
                border: none;
            }
        """)
        self.lbl_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_message.setWordWrap(True)

        self.spinner = CircularSpinner(38, color="#2563EB", thickness=4, parent=card)

        inner = QVBoxLayout(card)
        inner.setContentsMargins(22, 20, 22, 18)
        inner.setSpacing(12)
        inner.addWidget(self.spinner, alignment=Qt.AlignmentFlag.AlignHCenter)
        inner.addWidget(self.lbl_message, alignment=Qt.AlignmentFlag.AlignHCenter)

        card.adjustSize()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch(1)
        layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch(2)

        self.setMinimumSize(120, 120)
        if parent is not None:
            self.setGeometry(0, 0, parent.width(), parent.height())
            parent.installEventFilter(self)

    def eventFilter(self, watched, event):
        from PyQt6.QtCore import QEvent
        if watched is self.parent() and event.type() == QEvent.Type.Resize:
            parent = self.parent()
            if parent is not None:
                self.setGeometry(0, 0, parent.width(), parent.height())
        return super().eventFilter(watched, event)


def start_spinner(parent: QWidget, message: str = "Đang xử lý...") -> Optional[SpinnerOverlay]:
    """Hiển thị (hoặc cập nhật) overlay spinner trên parent và trả về overlay."""
    if parent is None:
        return None
    existing = _ACTIVE_SPINNERS.get(id(parent))
    if existing is not None:
        existing.lbl_message.setText(message)
        existing.raise_()
        return existing
    overlay = SpinnerOverlay(parent, message)
    overlay.show()
    overlay.raise_()
    _ACTIVE_SPINNERS[id(parent)] = overlay
    return overlay


def stop_spinner(parent: QWidget) -> None:
    """Gỡ overlay spinner gắn với parent (không lỗi nếu chưa có)."""
    overlay = _ACTIVE_SPINNERS.pop(id(parent), None)
    if overlay is not None:
        overlay.hide()
        overlay.deleteLater()
