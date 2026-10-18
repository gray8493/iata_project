"""
AITA Desktop Client - Shared App Avatar Pixmap
Avatar bo góc dùng chung cho sidebar/header, đọc assets qua core.app_paths
(đúng cả khi chạy dev lẫn bản PyInstaller đóng exe).
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath

from core.app_paths import app_assets_dir


def make_aita_avatar_pixmap(size: int, radius: int) -> "QPixmap | None":
    """Avatar AITA bo góc heo gốc (mép với mép). None nếu thiếu tệp ảnh (UI tự fallback)."""
    tight_path = app_assets_dir() / "images" / "aita-avatar-tight.png"
    source_path = tight_path if tight_path.is_file() else app_assets_dir() / "images" / "aita-avatar.png"
    if not source_path.is_file():
        return None
    source = QPixmap(str(source_path))
    if source.isNull():
        return None
    out = QPixmap(size, size)
    out.fill(Qt.GlobalColor.transparent)
    painter = QPainter(out)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    stroke = QPainterPath()
    stroke.addRoundedRect(0, 0, size, size, radius, radius)
    painter.setClipPath(stroke)
    painter.drawPixmap(0, 0, size, size, source)
    painter.end()
    return out
