"""
AITA Desktop Client - Application Entry Point
Starts the application and launches Login Window or Main Workspace.
"""

import sys
import multiprocessing
from pathlib import Path

# Thêm thư mục src vào sys.path
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QIcon

from ui.windows.login_window import LoginWindow
from ui.windows.main_window import AITAMainWindow


def main():
    app = QApplication(sys.argv)
    
    # Set default modern SaaS font (Inter fallback to Segoe UI / Arial)
    font = QFont("Inter", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)

    # Avatar của app (biểu tượng AITA) làm icon cho mọi cửa sổ
    app_icon_path = Path(__file__).resolve().parent / "assets" / "images" / "aita-avatar.png"
    if app_icon_path.exists():
        app.setWindowIcon(QIcon(str(app_icon_path)))

    # Khởi động màn hình Đăng Nhập
    login_win = LoginWindow()
    login_win.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
