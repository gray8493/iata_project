"""AITA Desktop Client - Đóng gói toolchain portable cho bản phát hành.

Tạo thư mục `toolchains/` đi kèm AITA.exe để máy giảng viên chấm được ngay
cả khi chưa cài MinGW / JDK / Python:

    toolchains/
      mingw64/bin/gcc.exe          (trình biên dịch C, đã cắt bộ tối thiểu)
      jdk/bin/{javac,java}.exe     (jlink runtime, ~45 MB)
      python/python.exe            (Python embeddable, ~11 MB)

Cách dùng (chạy trên máy dev ĐÃ cài sẵn toolchain):

    python apps/desktop-client/scripts/build_toolchains.py \
        --mingw "C:/path/to/mingw64" \
        --jdk "C:/Program Files/Java/jdk-21" \
        --out apps/desktop-client/toolchains

Sau đó build exe với spec `AITA_Grader_v1.spec` (đã trỏ datas tới toolchains/).
Script idempotent: chạy lại sẽ dọn thư mục đích trước khi copy.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Iterable, List, Optional

PYTHON_EMBED_URL = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"

# Chỉ những DLL mà gcc.exe/cc1.exe/collect2.exe thực sự cần để biên dịch C.
MINGW_REQUIRED_BIN = (
    "gcc.exe", "as.exe", "ld.exe", "ar.exe", "ranlib.exe",
    "libisl-23.dll", "libmpc-3.dll", "libmpfr-6.dll", "libgmp-10.dll",
    "libiconv-2.dll", "libzstd.dll", "zlib1.dll",
    "libwinpthread-1.dll", "libgcc_s_seh-1.dll", "libstdc++-6.dll",
)

# Phần libexec cần cho tiền xử lý + sinh mã (bỏ cc1plus/f951/lto1: không chấm C++/Fortran).
MINGW_REQUIRED_LIBEXEC = (
    "cc1.exe", "collect2.exe", "lto-wrapper.exe", "liblto_plugin.dll",
    "libisl-23.dll", "libmpfr-6.dll", "libgmp-10.dll", "libmpc-3.dll",
    "libiconv-2.dll", "libzstd.dll", "zlib1.dll", "libwinpthread-1.dll",
    "libgcc_s_seh-1.dll",
)

# Thư viện import UWP/Store không bao giờ dùng trong bài thi console -> bỏ để giảm ~50 MB.
MINGW_SKIP_IMPORT_LIBS = (
    "libonecoreuap_apiset.a", "libonecore.a", "libonecore_apiset.a",
    "libonecore_downlevel.a", "libwindowscoreheadless_apiset.a",
    "libwindowsapp.a", "libwindowsapp_downlevel.a", "libnanosrv.a",
    "libmincore.a", "libwsmsvc.a", "libmsvcp60.a",
    "libucrtbased.a", "libucrtbase.a", "libmsvcrtd.a", "libmsvcrt-os.a",
)

JDK_MODULES = (
    "java.base,java.compiler,jdk.compiler,java.logging,"
    "jdk.jfr,java.management,jdk.unsupported"
)


def _log(message: str) -> None:
    print(f"[toolchains] {message}", flush=True)


def _dir_size_mb(path: Path) -> float:
    total = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
    return total / (1024 * 1024)


def _copy_files(src_dir: Path, dst_dir: Path, names: Iterable[str], *, missing_ok: bool = True) -> int:
    dst_dir.mkdir(parents=True, exist_ok=True)
    copied = 0
    for name in names:
        src = src_dir / name
        if not src.is_file():
            if not missing_ok:
                raise FileNotFoundError(f"Thiếu tệp bắt buộc: {src}")
            continue
        shutil.copy2(src, dst_dir / name)
        copied += 1
    return copied


def _copy_tree(src: Path, dst: Path) -> None:
    if not src.is_dir():
        raise FileNotFoundError(f"Không thấy thư mục nguồn: {src}")
    shutil.copytree(src, dst, dirs_exist_ok=True)


def build_mingw(mingw_root: Path, out_dir: Path) -> Path:
    """Cắt bộ MinGW xuống tập tối thiểu còn biên dịch được chương trình C."""
    if not (mingw_root / "bin" / "gcc.exe").is_file():
        raise FileNotFoundError(f"Không thấy gcc.exe trong {mingw_root}/bin")

    target = out_dir / "mingw64"
    _log(f"MinGW nguồn: {mingw_root} ({_dir_size_mb(mingw_root):.0f} MB)")

    _copy_files(mingw_root / "bin", target / "bin", MINGW_REQUIRED_BIN, missing_ok=False)

    libexec_versions = sorted((mingw_root / "libexec" / "gcc").glob("*/*"))
    if not libexec_versions:
        raise FileNotFoundError(f"Không thấy libexec/gcc/*/* trong {mingw_root}")
    libexec_src = libexec_versions[-1]
    _copy_files(libexec_src, target / "libexec" / "gcc" / libexec_src.parent.name / libexec_src.name,
                MINGW_REQUIRED_LIBEXEC, missing_ok=False)
    _copy_tree(libexec_src / "plugin", target / "libexec" / "gcc" / libexec_src.parent.name / libexec_src.name / "plugin")

    gcc_lib_src = next((mingw_root / "lib" / "gcc").glob("*/*"))
    _copy_tree(gcc_lib_src, target / "lib" / "gcc" / gcc_lib_src.parent.name / gcc_lib_src.name)

    target_triple = gcc_lib_src.parent.name
    sysroot = mingw_root / target_triple
    _copy_tree(sysroot / "include", target / target_triple / "include")
    for sub in ("lib", "bin"):
        _copy_tree(sysroot / sub, target / target_triple / sub)

    for name in MINGW_SKIP_IMPORT_LIBS:
        for victim in target.rglob(name):
            victim.unlink(missing_ok=True)

    _log(f"MinGW tối thiểu: {target} ({_dir_size_mb(target):.0f} MB)")
    return target


def build_jdk(jdk_root: Path, out_dir: Path) -> Path:
    """Tạo runtime Java rút gọn bằng jlink (javac + java + các module cần thiết)."""
    jlink = jdk_root / "bin" / "jlink.exe"
    if not jlink.is_file():
        raise FileNotFoundError(f"Không thấy jlink.exe trong {jdk_root}/bin (cần JDK 9+)")

    target = out_dir / "jdk"
    if target.exists():
        shutil.rmtree(target)

    cmd = [
        str(jlink),
        "--add-modules", JDK_MODULES,
        "--strip-debug", "--no-man-pages", "--no-header-files",
        "--compress=zip-6",
        "--output", str(target),
    ]
    _log("jlink " + " ".join(cmd[1:]))
    subprocess.run(cmd, check=True)

    for exe in ("javac.exe", "java.exe"):
        if not (target / "bin" / exe).is_file():
            raise RuntimeError(f"jlink không tạo ra {exe} — kiểm tra danh sách module.")

    _log(f"JDK rút gọn: {target} ({_dir_size_mb(target):.0f} MB)")
    return target


def build_python(out_dir: Path, embed_zip: Optional[Path] = None) -> Path:
    """Cài Python embeddable (bản portable chính thức của python.org)."""
    target = out_dir / "python"
    target.mkdir(parents=True, exist_ok=True)

    if embed_zip and embed_zip.is_file():
        archive_path = embed_zip
    else:
        archive_path = Path(tempfile.gettempdir()) / "aita_python_embed.zip"
        if not archive_path.is_file():
            _log(f"Tải Python embeddable: {PYTHON_EMBED_URL}")
            urllib.request.urlretrieve(PYTHON_EMBED_URL, archive_path)

    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(target)

    python_exe = target / "python.exe"
    if not python_exe.is_file():
        raise RuntimeError("Gói Python embeddable không chứa python.exe")

    # Bản embed mặc định tắt import site; bật để script sinh viên import được thư viện chuẩn.
    for pth in target.glob("python*._pth"):
        content = pth.read_text(encoding="utf-8", errors="ignore")
        if "import site" not in content:
            pth.write_text(content.rstrip() + "\nimport site\n", encoding="utf-8")

    _log(f"Python embeddable: {target} ({_dir_size_mb(target):.0f} MB)")
    return target


def smoke_test(toolchains: Path, language: str) -> bool:
    """Chạy thử thật: biên dịch + thực thi hello-world bằng toolchain vừa đóng."""
    env_path = str(toolchains / "mingw64" / "bin")
    import os
    env = os.environ.copy()
    env["PATH"] = env_path + os.pathsep + env.get("PATH", "")

    with tempfile.TemporaryDirectory(prefix="aita_toolchain_smoke_") as tmp:
        tmp_dir = Path(tmp)
        if language == "c":
            src = tmp_dir / "probe.c"
            src.write_text(
                "#include <stdio.h>\nint main(void){int a,b;"
                "if(scanf(\"%d %d\",&a,&b)!=2) return 1;printf(\"%d\\n\",a+b);return 0;}\n",
                encoding="utf-8",
            )
            gcc = toolchains / "mingw64" / "bin" / "gcc.exe"
            out = tmp_dir / "probe.exe"
            res = subprocess.run([str(gcc), str(src), "-o", str(out), "-O2", "-std=c11"],
                                 capture_output=True, text=True, env=env)
            if res.returncode != 0:
                _log(f"FAIL biên dịch C: {res.stderr.strip()[:300]}")
                return False
            run = subprocess.run([str(out)], input="3 4\n", capture_output=True, text=True)
            ok = run.stdout.strip() == "7"
            _log(f"Smoke test C: {'OK' if ok else 'FAIL (' + run.stdout.strip() + ')'}")
            return ok

        if language == "java":
            src = tmp_dir / "Probe.java"
            src.write_text(
                "public class Probe { public static void main(String[] a){"
                "System.out.println(3 + 4); } }\n",
                encoding="utf-8",
            )
            javac = toolchains / "jdk" / "bin" / "javac.exe"
            java = toolchains / "jdk" / "bin" / "java.exe"
            res = subprocess.run([str(javac), "-encoding", "UTF-8", str(src)],
                                 capture_output=True, text=True)
            if res.returncode != 0:
                _log(f"FAIL javac: {res.stderr.strip()[:300]}")
                return False
            run = subprocess.run([str(java), "-cp", str(tmp_dir), "Probe"],
                                 capture_output=True, text=True)
            ok = run.stdout.strip() == "7"
            _log(f"Smoke test Java: {'OK' if ok else 'FAIL (' + run.stdout.strip() + ')'}")
            return ok

        if language == "python":
            src = tmp_dir / "probe.py"
            src.write_text("a, b = map(int, input().split())\nprint(a + b)\n", encoding="utf-8")
            python = toolchains / "python" / "python.exe"
            run = subprocess.run([str(python), "-u", str(src)], input="3 4\n",
                                 capture_output=True, text=True)
            ok = run.stdout.strip() == "7"
            _log(f"Smoke test Python: {'OK' if ok else 'FAIL (' + run.stdout.strip() + ')'}")
            return ok

    _log(f"Ngôn ngữ không hỗ trợ smoke test: {language}")
    return False


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Đóng gói toolchain portable cho AITA.exe")
    parser.add_argument("--mingw", type=Path, help="Thư mục MinGW gốc (chứa bin/gcc.exe)")
    parser.add_argument("--jdk", type=Path, help="Thư mục JDK gốc (chứa bin/jlink.exe)")
    parser.add_argument("--python-zip", type=Path, help="File zip Python embeddable (bỏ trống để tải)")
    parser.add_argument("--out", type=Path, default=Path("apps/desktop-client/toolchains"),
                        help="Thư mục đích (mặc định: apps/desktop-client/toolchains)")
    parser.add_argument("--skip-python", action="store_true", help="Không đóng gói Python")
    parser.add_argument("--no-clean", action="store_true", help="Không xoá thư mục đích trước khi copy")
    parser.add_argument("--smoke-test", action="store_true", help="Chạy thử C/Java/Python sau khi đóng")
    args = parser.parse_args(argv)

    if not args.mingw and not args.jdk and args.skip_python:
        parser.error("Cần ít nhất một trong --mingw / --jdk / (Python)")

    out_dir = args.out.resolve()
    if out_dir.exists() and not args.no_clean:
        _log(f"Dọn thư mục đích: {out_dir}")
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.mingw:
        build_mingw(args.mingw.resolve(), out_dir)
    if args.jdk:
        build_jdk(args.jdk.resolve(), out_dir)
    if not args.skip_python:
        build_python(out_dir, args.python_zip.resolve() if args.python_zip else None)

    _log(f"Tổng dung lượng toolchains/: {_dir_size_mb(out_dir):.0f} MB")

    if args.smoke_test:
        failures = [
            lang for lang in ("c", "java", "python")
            if not smoke_test(out_dir, lang)
        ]
        if failures:
            _log(f"Smoke test thất bại: {', '.join(failures)}")
            return 1
        _log("Smoke test toàn bộ: OK")

    return 0


if __name__ == "__main__":
    sys.exit(main())
