"""E2E smoke — khởi động toàn bộ app offscreen (E2E02_AppBoot).

Luồng thật: LoginWindow -> ModeSelectionWindow -> click card "Chấm Thi Thực
Hành" -> AITAMainWindow hiển thị. Mọi network (AI quota, backend probe) được
thay bằng stub; database thay bằng `:memory:` để không ghi vào `data/`.
"""
import pytest

pytest.importorskip("PyQt6")

import ui.windows.main_window as main_window_module
import ui.windows.mode_selection_window as mode_module
from database.db_manager import DatabaseManager
from ui.windows.login_window import LoginWindow
from ui.windows.main_window import AITAMainWindow
from ui.windows.mode_selection_window import ModeSelectionWindow

pytestmark = pytest.mark.e2e

SESSION_INFO = {
    "mode": "ONLINE",
    "username": "e2e_instructor",
    "display_name": "GV: E2E Instructor",
    "full_name": "E2E Instructor",
    "role": "INSTRUCTOR",
    "email": "e2e@fpt.edu.vn",
    "user_id": 1,
    "token": "e2e-token",
    "refresh_token": "e2e-refresh",
}


class _StubAiService:
    """Thay AiService trong QuotaWorker — không gọi mạng, trả ngay."""

    def __init__(self, *args, **kwargs):
        pass

    def get_quota(self):
        return {
            "success": True,
            "remaining_tokens": 1000,
            "daily_limit_tokens": 1000,
            "used_tokens_today": 0,
        }


@pytest.fixture
def offline_env(monkeypatch):
    """Chặn network + cô lập database cho mọi window trong app."""
    monkeypatch.setattr(mode_module, "AiService", _StubAiService)
    monkeypatch.setattr(main_window_module, "AiService", _StubAiService)
    monkeypatch.setattr(
        main_window_module, "DatabaseManager", lambda: DatabaseManager(":memory:")
    )


def _wait_quota_worker(window):
    worker = getattr(window, "quota_worker", None)
    if worker is not None:
        worker.wait(5000)


# ---------------------------------------------------------------------------
# Normal: login -> chọn chế độ -> main window mở đúng
# ---------------------------------------------------------------------------
def test_e2e02_appboot_tc001_login_mode_selection_practical_main_window(qapp, offline_env):
    login_win = LoginWindow()
    login_win.show()
    assert login_win.windowTitle() == "AITA - Đăng Nhập Giảng Viên"
    assert login_win.btn_login.text() == "Đăng Nhập"

    # Bỏ qua gõ form + QThread đăng nhập thật: đi thẳng bước chuyển window
    login_win._launch_main_window(SESSION_INFO)
    mode_win = login_win.mode_win
    assert isinstance(mode_win, ModeSelectionWindow)
    assert mode_win.isVisible()
    _wait_quota_worker(mode_win)

    # 2 phân hệ đều render
    assert mode_win.card_practical.btn_select.text() != ""
    assert mode_win.card_web.btn_select.text() != ""

    # Click nút thật trên card "Chấm Thi Thực Hành"
    mode_win.card_practical.btn_select.click()
    qapp.processEvents()
    assert isinstance(mode_win.practical_win, AITAMainWindow)
    assert mode_win.practical_win.isVisible()
    assert mode_win.practical_win.windowTitle() == "AITA - Chấm Thi Thực Hành"
    _wait_quota_worker(mode_win.practical_win)

    # Main window dùng DB :memory: đã monkeypatch — không ghi vào data/
    assert mode_win.practical_win.db.get_all_classes() == []

    mode_win.practical_win.close()
    mode_win.close()
    login_win.close()
    qapp.processEvents()


# ---------------------------------------------------------------------------
# Boundary: session_info rỗng -> cửa sổ chọn chế độ vẫn dùng thông tin mặc định
# ---------------------------------------------------------------------------
def test_e2e02_appboot_tc002_mode_selection_without_session_info(qapp, offline_env):
    win = ModeSelectionWindow(session_info=None)
    win.show()
    _wait_quota_worker(win)
    qapp.processEvents()

    assert win.windowTitle() == "AITA - Chọn Chế Độ Làm Việc"
    assert win.session_info["username"] == "instructor"
    assert win.card_practical is not None and win.card_web is not None
    assert "AI Hub" in win.lbl_ai_badge.text()

    win.close()
    qapp.processEvents()
