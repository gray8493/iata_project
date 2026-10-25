"""AITA Desktop Client - Đóng gói trình duyệt Chromium headless cho bản phát hành.

Tạo thư mục `browsers/` đi kèm AITA.exe để máy giảng viên render trang web
(chấm tiêu chí UI/UX bằng AI Vision) ngay cả khi chưa cài Playwright/Chromium:

    browsers/
      chrome-headless-shell-win64/chrome-headless-shell.exe   (headless shell, ~270 MB)
      winldd-1007/winldd.exe                                  (công cụ DLL của Playwright)

Cách dùng (chạy trên máy dev ĐÃ cài playwright và đã có cache trình duyệt):

    python apps/desktop-client/scripts/build_browsers.py --smoke-test

Cache trình duyệt mặc định nằm ở %LOCALAPPDATA%/ms-playwright (do
`python -m playwright install chromium` tạo). Script idempotent: chạy lại sẽ
dọn thư mục đích trước khi copy.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import List, Optional

# Tên thư mục con + file thực thi cho từng loại browser trong cache ms-playwright.
BROWSER_KINDS = {
    "headless-shell": ("chromium_headless_shell-*", "chrome-headless-shell-win64", "chrome-headless-shell.exe"),
    "chromium": ("chromium-*", "chrome-win64", "chrome.exe"),
}


def _log(message: str) -> None:
    print(f"[browsers] {message}", flush=True)


def _dir_size_mb(path: Path) -> float:
    total = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
    return total / (1024 * 1024)


def _default_cache_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA") or ""
    if base:
        return Path(base) / "ms-playwright"
    return Path.home() / "AppData" / "Local" / "ms-playwright"


def _find_browser_src(cache_dir: Path, kind: str) -> Path:
    """Tìm thư mục browser (chứa .exe) trong cache ms-playwright."""
    dir_pattern, inner_dir, exe_name = BROWSER_KINDS[kind]
    candidates = sorted(
        (d / inner_dir for d in cache_dir.glob(dir_pattern) if d.is_dir()),
        key=lambda p: p.parent.name,
        reverse=True,
    )
    for candidate in candidates:
        if (candidate / exe_name).is_file():
            return candidate
    raise FileNotFoundError(
        f"Không thấy '{kind}' trong cache '{cache_dir}'. "
        "Hãy chạy trước: python -m playwright install chromium"
    )


def build_browsers(cache_dir: Path, out_dir: Path, kind: str) -> Path:
    """Copy browser + winldd từ cache vào thư mục đóng gói."""
    src = _find_browser_src(cache_dir, kind)
    _log(f"{kind} nguồn: {src.parent} ({_dir_size_mb(src.parent):.0f} MB)")

    target = out_dir / src.name
    shutil.copytree(src, target, dirs_exist_ok=True)
    _log(f"Browser đóng gói: {target} ({_dir_size_mb(target):.0f} MB)")

    winldd_dirs = sorted((d for d in cache_dir.glob("winldd-*") if d.is_dir()),
                         key=lambda p: p.name, reverse=True)
    for winldd_dir in winldd_dirs:
        winldd_target = out_dir / winldd_dir.name
        shutil.copytree(winldd_dir, winldd_target, dirs_exist_ok=True)
        _log(f"winldd kèm theo: {winldd_target} ({_dir_size_mb(winldd_target):.1f} MB)")
        break

    return target


def _find_packaged_exe(browsers_dir: Path) -> Optional[Path]:
    """Tìm file .exe browser trong thư mục đã đóng gói (ưu tiên headless shell)."""
    for exe_name in ("chrome-headless-shell.exe", "chrome.exe"):
        matches = sorted(browsers_dir.rglob(exe_name))
        if matches:
            return matches[0]
    return None


def smoke_test_browser(browsers_dir: Path) -> bool:
    """Mở trình duyệt vừa đóng bằng Playwright, đọc trang test, trả True nếu OK."""
    exe = _find_packaged_exe(browsers_dir)
    if not exe:
        _log("FAIL smoke test: không thấy chrome-headless-shell.exe / chrome.exe")
        return False

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                executable_path=str(exe),
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            try:
                page = browser.new_page()
                page.goto("data:text/html,<h1>AITA</h1>")
                heading = page.text_content("h1") or ""
            finally:
                browser.close()
    except Exception as ex:
        _log(f"FAIL smoke test: {ex}")
        return False

    ok = heading.strip() == "AITA"
    _log(f"Smoke test browser ({exe.name}): {'OK' if ok else 'FAIL (' + heading.strip() + ')'}")
    return ok


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Đóng gói Chromium headless cho AITA.exe")
    parser.add_argument("--out", type=Path, default=Path("apps/desktop-client/browsers"),
                        help="Thư mục đích (mặc định: apps/desktop-client/browsers)")
    parser.add_argument("--cache-dir", type=Path, default=None,
                        help="Thư mục cache ms-playwright (mặc định: %LOCALAPPDATA%/ms-playwright)")
    parser.add_argument("--kind", choices=sorted(BROWSER_KINDS), default="headless-shell",
                        help="Loại browser đóng gói (mặc định: headless-shell)")
    parser.add_argument("--no-clean", action="store_true", help="Không xoá thư mục đích trước khi copy")
    parser.add_argument("--smoke-test", action="store_true", help="Mở thử browser sau khi đóng")
    args = parser.parse_args(argv)

    cache_dir = (args.cache_dir or _default_cache_dir()).resolve()
    out_dir = args.out.resolve()

    if out_dir.exists() and not args.no_clean:
        _log(f"Dọn thư mục đích: {out_dir}")
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        build_browsers(cache_dir, out_dir, args.kind)
    except FileNotFoundError as ex:
        _log(f"LỖI: {ex}")
        return 1

    _log(f"Tổng dung lượng browsers/: {_dir_size_mb(out_dir):.0f} MB")

    if args.smoke_test:
        if not smoke_test_browser(out_dir):
            return 1
        _log("Smoke test browser: OK")

    return 0


if __name__ == "__main__":
    sys.exit(main())
