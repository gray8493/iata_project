"""
AITA Desktop Client - Application Entry Point
Starts the application and launches Login Window or Main Workspace.

Chạy `AITA_Grader_v1.exe --selftest` để kiểm tra môi trường chấm bài trên máy
mà không cần mở giao diện (hữu ích khi hỗ trợ giảng viên qua điện thoại).
"""

import sys
import multiprocessing
from pathlib import Path

# Thêm thư mục src vào sys.path
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


class _Tee:
    """Ghi đồng thời ra console và buffer (để lưu báo cáo ra file)."""

    def __init__(self, *streams):
        self._streams = streams

    def write(self, data):
        for stream in self._streams:
            try:
                stream.write(data)
            except Exception:
                pass
        return len(data)

    def flush(self):
        for stream in self._streams:
            try:
                stream.flush()
            except Exception:
                pass


def _attach_parent_console() -> bool:
    """Gắn vào console của cmd/PowerShell đang gọi exe để thấy được output."""
    if not sys.platform.startswith("win"):
        return True
    try:
        import ctypes

        if not ctypes.windll.kernel32.AttachConsole(-1):  # ATTACH_PARENT_PROCESS
            return False
        sys.stdout = open("CONOUT$", "w", encoding="utf-8", buffering=1)
        sys.stderr = sys.stdout
        return True
    except Exception:
        return False


def run_selftest() -> int:
    """Chạy `--selftest`, in ra console và luôn lưu `aita_selftest.txt` cạnh exe.

    Trả 0 khi cả GCC/JDK/Python đều chạy được.
    """
    import io

    has_console = _attach_parent_console()
    buffer = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = _Tee(original_stdout, buffer)
    try:
        code = _run_selftest_body()
    finally:
        sys.stdout = original_stdout

    report = buffer.getvalue()
    if getattr(sys, "frozen", False):
        report_dir = Path(sys.executable).resolve().parent
    else:
        # Dev: lưu ngay trong apps/desktop-client, không ghi vào thư mục Python.
        report_dir = Path(__file__).resolve().parent
    report_path = report_dir / "aita_selftest.txt"
    try:
        report_path.write_text(report, encoding="utf-8")
    except OSError:
        report_path = None

    if report_path is not None:
        print(f"\nĐã lưu báo cáo: {report_path}")
        # Không có console (người dùng double-click) -> mở báo cáo bằng Notepad.
        if not has_console:
            try:
                import os

                os.startfile(str(report_path))  # type: ignore[attr-defined]
            except Exception:
                pass
    return code


def _run_selftest_body() -> int:
    """Phần thân của `--selftest`: chạy thử thật GCC/JDK/Python."""
    import subprocess
    import tempfile

    from core.app_paths import bundled_toolchains_dir, resolve_python_executable
    from core.adapters.compiler_adapter import find_gcc_executable, find_java_tool

    print("AITA - Kiểm tra môi trường chấm bài")
    print("=" * 60)

    bundled = bundled_toolchains_dir()
    print(f"Toolchain đóng kèm : {bundled if bundled else 'KHÔNG CÓ'}")
    print(f"Chương trình       : {sys.executable}")

    results = []

    gcc = find_gcc_executable()
    print(f"\n[GCC]  {gcc or 'KHÔNG TÌM THẤY'}")
    if gcc:
        with tempfile.TemporaryDirectory(prefix="aita_selftest_") as tmp:
            src = Path(tmp) / "probe.c"
            out = Path(tmp) / "probe.exe"
            src.write_text(
                "#include <stdio.h>\nint main(void){int a,b;"
                "if(scanf(\"%d %d\",&a,&b)!=2) return 1;printf(\"%d\\n\",a+b);return 0;}\n",
                encoding="utf-8",
            )
            build = subprocess.run([gcc, str(src), "-o", str(out), "-O2", "-std=c11"],
                                   capture_output=True, text=True)
            if build.returncode == 0 and out.is_file():
                run = subprocess.run([str(out)], input="3 4\n", capture_output=True, text=True)
                ok = run.stdout.strip() == "7"
                print(f"       Biên dịch + chạy: {'OK (3+4=7)' if ok else 'LỖI'}")
                results.append(("GCC", ok))
            else:
                print(f"       Biên dịch thất bại: {(build.stderr or '').strip()[:200]}")
                results.append(("GCC", False))
    else:
        results.append(("GCC", False))

    javac = find_java_tool("javac")
    java = find_java_tool("java")
    print(f"\n[JDK]  javac={javac or 'KHÔNG TÌM THẤY'}  java={java or 'KHÔNG TÌM THẤY'}")
    if javac and java:
        with tempfile.TemporaryDirectory(prefix="aita_selftest_") as tmp:
            src = Path(tmp) / "Probe.java"
            src.write_text(
                "public class Probe { public static void main(String[] a){"
                "System.out.println(3 + 4); } }\n",
                encoding="utf-8",
            )
            build = subprocess.run([javac, "-encoding", "UTF-8", str(src)],
                                   capture_output=True, text=True)
            if build.returncode == 0:
                run = subprocess.run([java, "-cp", tmp, "Probe"], capture_output=True, text=True)
                ok = run.stdout.strip() == "7"
                print(f"       javac + java: {'OK (3+4=7)' if ok else 'LỖI'}")
                results.append(("JDK", ok))
            else:
                print(f"       javac thất bại: {(build.stderr or '').strip()[:200]}")
                results.append(("JDK", False))
    else:
        results.append(("JDK", False))

    print("\n[Python]")
    try:
        python_bin = resolve_python_executable()
        print(f"       {python_bin}")
        with tempfile.TemporaryDirectory(prefix="aita_selftest_") as tmp:
            src = Path(tmp) / "probe.py"
            src.write_text("a, b = map(int, input().split())\nprint(a + b)\n", encoding="utf-8")
            run = subprocess.run([python_bin, "-u", str(src)], input="3 4\n",
                                 capture_output=True, text=True)
            ok = run.stdout.strip() == "7"
            print(f"       Chạy script: {'OK (3+4=7)' if ok else 'LỖI'}")
            results.append(("Python", ok))
    except RuntimeError as ex:
        print(f"       {ex}")
        results.append(("Python", False))

    print("\n[Chromium]")
    exe = None
    try:
        from services.web_rubric_service import WebRubricEngine

        exe = WebRubricEngine._bundled_chromium_executable()
    except Exception:
        exe = None

    if not exe:
        print("       CẢNH BÁO: không có Chromium đóng kèm (browsers/) - chấm web sẽ dùng fallback HTTP.")
    else:
        print(f"       {exe}")
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as pw:
                browser = pw.chromium.launch(
                    headless=True,
                    executable_path=str(exe),
                    args=["--no-sandbox", "--disable-dev-shm-usage"],
                )
                try:
                    page = browser.new_page()
                    page.goto("data:text/html,<h1>AITA</h1>")
                    heading = (page.text_content("h1") or "").strip()
                finally:
                    browser.close()
            ok = heading == "AITA"
            print(f"       Render trang test: {'OK (Chromium web render)' if ok else 'LỖI'}")
            results.append(("Chromium", ok))
        except Exception as exc:
            print(f"       Lỗi khởi động Chromium: {exc}")
            results.append(("Chromium", False))

    print("\n" + "=" * 60)
    failed = [name for name, ok in results if not ok]
    if failed:
        print(f"KẾT QUẢ: LỖI ở {', '.join(failed)}")
        print("Cách xử lý: mở app -> 'Cấu Hình Môi Trường' -> chọn đúng file .exe,")
        print("hoặc dùng bản phát hành có kèm thư mục toolchains/ cạnh AITA_Grader_v1.exe.")
        return 1
    web_tested = any(name == "Chromium" for name, _ in results)
    print(f"KẾT QUẢ: Môi trường sẵn sàng chấm C / Java / Python{' / Web' if web_tested else ''}.")
    return 0


def main():
    # Windows: nhóm taskbar riêng cho AITA để taskbar/tiêu đề dùng icon của app
    # thay vì icon Python mặc định. Phải đặt trước khi tạo QApplication.
    if sys.platform.startswith("win"):
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("AITA.DesktopClient.1")
        except Exception:
            pass

    if "--selftest" in sys.argv:
        sys.exit(run_selftest())

    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtGui import QFont, QIcon

    from ui.windows.login_window import LoginWindow
    from ui.dialogs.update_dialog import maybe_prompt_update

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

    # Kiểm tra bản cập nhật trong nền (không chặn UI đăng nhập)
    update_controller = maybe_prompt_update(login_win)
    _ = update_controller

    sys.exit(app.exec())


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
