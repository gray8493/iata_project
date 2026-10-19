"""
AITA Desktop Client - Auto-Update Dialog.

Hiển thị khi phát hiện bản mới, cho phép:
- Xem ghi chú phát hành (release notes).
- Tải về kèm thanh tiến trình.
- "Cập nhật ngay" (đóng app -> update.bat thay file -> mở lại) hoặc "Nhắc lại sau".
"""

from __future__ import annotations

import tempfile
import time
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, QSettings, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QDialog, QFrame, QHBoxLayout, QLabel, QMessageBox, QProgressBar,
    QPushButton, QTextEdit, QVBoxLayout, QWidget,
)

from core.version import APP_VERSION
from services.update_service import UpdateInfo, UpdateService, is_frozen
from ui.styles.theme import (
    COLOR_BORDER_DEFAULT, COLOR_PRIMARY, COLOR_SURFACE, COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, RADIUS_BUTTON,
)

_CHECK_INTERVAL_SECONDS = 24 * 60 * 60


class CheckUpdateWorker(QThread):
    """Truy vấn backend trong nền để không chặn khởi động app."""

    finished_check = pyqtSignal(object)  # Optional[UpdateInfo]

    def run(self):
        info = UpdateService().check_for_update()
        self.finished_check.emit(info)


class DownloadWorker(QThread):
    """Tải artifact về thư mục tạm, báo tiến trình và xác minh checksum."""

    progress = pyqtSignal(int, int)
    completed = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, update_info: UpdateInfo, dest_dir: Path):
        super().__init__()
        self.update_info = update_info
        self.dest_dir = dest_dir
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def _on_progress(self, downloaded: int, total: int):
        self.progress.emit(downloaded, total)

    def run(self):
        try:
            path = UpdateService().download(
                self.update_info.artifact,
                self.dest_dir,
                progress_cb=self._on_progress,
                cancel_check=lambda: self._cancelled,
            )
            self.completed.emit(str(path))
        except Exception as exc:  # noqa: BLE001 - đẩy thông báo lên UI
            self.failed.emit(str(exc))


def _human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


class UpdateDialog(QDialog):
    """Modal thông báo bản cập nhật mới với nút Cập nhật ngay / Nhắc lại sau."""

    def __init__(self, update_info: UpdateInfo, settings: QSettings, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.update_info = update_info
        self.settings = settings
        self.download_worker: Optional[DownloadWorker] = None
        self._downloaded_path: Optional[Path] = None

        self.setWindowTitle("Cập nhật AITA")
        self.setFixedWidth(520)
        self.setModal(True)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(14)

        card = QFrame(self)
        card.setStyleSheet(
            f"QFrame {{ background-color: {COLOR_SURFACE}; border: 1px solid {COLOR_BORDER_DEFAULT}; border-radius: 16px; }}"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 20, 22, 20)
        card_layout.setSpacing(10)

        title = QLabel("Có bản cập nhật mới", card)
        title.setStyleSheet(f"font-size: 19px; font-weight: 700; color: {COLOR_TEXT_PRIMARY}; background: transparent;")
        card_layout.addWidget(title)

        version_line = QLabel(
            f"Phiên bản hiện tại: {APP_VERSION}   →   Phiên bản mới: {self.update_info.latest_version}",
            card,
        )
        version_line.setStyleSheet(f"font-size: 13px; color: {COLOR_TEXT_SECONDARY}; background: transparent;")
        card_layout.addWidget(version_line)

        if self.update_info.mandatory:
            badge = QLabel("Bản cập nhật bắt buộc", card)
            badge.setStyleSheet(
                "font-size: 12px; font-weight: 600; color: #B45309; background: #FFF7E6;"
                "border-radius: 8px; padding: 4px 10px;"
            )
            badge.setAlignment(Qt.AlignmentFlag.AlignLeft)
            card_layout.addWidget(badge)

        notes = self.update_info.notes.strip() or "Không có ghi chú phát hành."
        notes_view = QTextEdit(card)
        notes_view.setReadOnly(True)
        notes_view.setPlainText(notes)
        notes_view.setFixedHeight(120)
        notes_view.setStyleSheet(
            f"QTextEdit {{ background: {COLOR_SURFACE}; border: 1px solid {COLOR_BORDER_DEFAULT};"
            f"border-radius: 10px; padding: 8px 10px; font-size: 13px; color: {COLOR_TEXT_PRIMARY}; }}"
        )
        card_layout.addWidget(notes_view)

        self.lbl_status = QLabel("", card)
        self.lbl_status.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_MUTED}; background: transparent;")
        card_layout.addWidget(self.lbl_status)

        self.progress_bar = QProgressBar(card)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        card_layout.addWidget(self.progress_bar)

        button_row = QHBoxLayout()
        button_row.setSpacing(10)
        button_row.addStretch(1)

        self.btn_later = QPushButton("Nhắc lại sau", card)
        self.btn_later.setStyleSheet(
            f"QPushButton {{ background: {COLOR_SURFACE}; color: {COLOR_TEXT_SECONDARY};"
            f"border: 1px solid {COLOR_BORDER_DEFAULT}; border-radius: {RADIUS_BUTTON};"
            "min-height: 40px; padding: 0 16px; font-weight: 600; }}"
            "QPushButton:hover { background: #F1F5F9; }"
        )
        self.btn_later.clicked.connect(self._on_later)
        if self.update_info.mandatory:
            self.btn_later.setVisible(False)
        button_row.addWidget(self.btn_later)

        self.btn_update = QPushButton("Cập nhật ngay", card)
        self.btn_update.setStyleSheet(
            f"QPushButton {{ background: {COLOR_PRIMARY}; color: #FFFFFF; border: none;"
            f"border-radius: {RADIUS_BUTTON}; min-height: 40px; padding: 0 18px; font-weight: 600; }}"
            "QPushButton:hover { background: #1F6FDB; }"
            "QPushButton:disabled { background: #CBD5E1; }"
        )
        self.btn_update.clicked.connect(self._on_update_clicked)
        button_row.addWidget(self.btn_update)

        card_layout.addLayout(button_row)
        layout.addWidget(card)

    # ----------------------------------------------------------- interactions
    def _on_later(self):
        self.settings.setValue("skipped_version", self.update_info.latest_version)
        self.reject()

    def _on_update_clicked(self):
        if self.download_worker is not None and self.download_worker.isRunning():
            return
        self.btn_update.setEnabled(False)
        self.btn_later.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.lbl_status.setText("Đang tải bản cập nhật...")

        dest_dir = Path(tempfile.gettempdir()) / "AITA_update" / self.update_info.latest_version
        self.download_worker = DownloadWorker(self.update_info, dest_dir)
        self.download_worker.progress.connect(self._on_progress)
        self.download_worker.completed.connect(self._on_downloaded)
        self.download_worker.failed.connect(self._on_failed)
        self.download_worker.start()

    def _on_progress(self, downloaded: int, total: int):
        if total > 0:
            percent = int(downloaded * 100 / total)
            self.progress_bar.setValue(percent)
            self.lbl_status.setText(f"Đang tải... {percent}% ({_human_size(downloaded)}/{_human_size(total)})")
        else:
            self.lbl_status.setText(f"Đang tải... {_human_size(downloaded)}")

    def _on_downloaded(self, path_str: str):
        self._downloaded_path = Path(path_str)
        self.lbl_status.setText("Đã tải xong. Đang chuẩn bị cập nhật...")
        self.progress_bar.setValue(100)

        if not is_frozen() and not self._dev_update_allowed():
            QMessageBox.information(
                self,
                "Chế độ nhà phát triển",
                "Đã tải bản cập nhật nhưng không thể tự thay thế khi chạy từ mã nguồn.\n"
                "Tính năng này chỉ hoạt động trên bản cài đặt (đã đóng gói).",
            )
            self._reset_buttons()
            return

        confirm = QMessageBox.question(
            self,
            "Hoàn tất cập nhật",
            "Ứng dụng sẽ đóng và khởi động lại để hoàn tất cập nhật. Tiếp tục?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            self._reset_buttons()
            return

        try:
            applied = UpdateService().apply_update(self.update_info.artifact, self._downloaded_path)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Lỗi cập nhật", str(exc))
            self._reset_buttons()
            return

        if applied:
            QApplication.quit()

    def _on_failed(self, message: str):
        if message == "Đã hủy tải bản cập nhật.":
            self.lbl_status.setText("Đã hủy tải.")
        else:
            QMessageBox.warning(self, "Không thể cập nhật", message)
            self.lbl_status.setText("Cập nhật thất bại.")
        self._reset_buttons()

    def _reset_buttons(self):
        self.btn_update.setEnabled(True)
        self.btn_later.setEnabled(True)
        self.progress_bar.setVisible(False)

    @staticmethod
    def _dev_update_allowed() -> bool:
        import os

        return os.getenv("AITA_ALLOW_DEV_UPDATE") == "1"


class UpdateController:
    """Giữ tham chiếu worker (tránh GC) và điều phối luồng kiểm tra cập nhật."""

    def __init__(self, parent: Optional[QWidget] = None):
        self.parent = parent
        self.settings = QSettings("AITA", "Updater")
        self.worker: Optional[CheckUpdateWorker] = None

    def check(self, force: bool = False) -> None:
        last_check = self.settings.value("last_check_ts", 0, type=int)
        if not force and (time.time() - last_check) < _CHECK_INTERVAL_SECONDS:
            return

        self.worker = CheckUpdateWorker()
        self.worker.finished_check.connect(self._on_checked)
        self.worker.start()

    def _on_checked(self, info: Optional[UpdateInfo]) -> None:
        self.settings.setValue("last_check_ts", int(time.time()))
        if info is None:
            return
        # Không làm phiền lại với phiên bản người dùng đã chọn bỏ qua.
        if self.settings.value("skipped_version", "", type=str) == info.latest_version:
            return
        dialog = UpdateDialog(info, self.settings, self.parent)
        dialog.exec()


def maybe_prompt_update(parent: Optional[QWidget] = None, force: bool = False) -> UpdateController:
    """Điểm vào cho main.py: kiểm tra cập nhật trong nền (không chặn UI)."""
    controller = UpdateController(parent)
    controller.check(force=force)
    return controller
