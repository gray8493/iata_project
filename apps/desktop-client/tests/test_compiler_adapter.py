"""CompilerAdapter (Adapter Pattern / core.adapters).

Covers UT01_CompilerAdapter: normalized CompileResult across the GCC/Javac/
py_compile toolchains, missing-source -> CE mapping, subprocess timeout and
failure mapping, and CompilerAdapterFactory resolution by language label.
Subprocess calls of external toolchains are mocked to stay CI-safe.
"""

from pathlib import Path
from subprocess import TimeoutExpired
from unittest.mock import patch

import pytest

from core.adapters.compiler_adapter import (
    CompileResult,
    CompilerAdapterFactory,
    GccCompilerAdapter,
    JavacCompilerAdapter,
    PythonInterpreterAdapter,
    find_gcc_executable,
    get_compiler_adapter,
)


@pytest.fixture
def valid_py_file(tmp_path) -> Path:
    src = tmp_path / "SE180001_Q1.py"
    src.write_text("def main():\n    print('ok')\nmain()\n", encoding="utf-8")
    return src


@pytest.fixture
def broken_py_file(tmp_path) -> Path:
    src = tmp_path / "SE180002_Q1.py"
    src.write_text("def broken(:\n    pass\n", encoding="utf-8")
    return src


# ------------------------------------------------------------------------------
# CompileResult contract
# ------------------------------------------------------------------------------
def test_compile_result_verdict_maps_success_to_ok_and_failure_to_ce():
    ok = CompileResult(success=True, log="")
    fail = CompileResult(success=False, log="error")
    assert ok.verdict == "OK"
    assert fail.verdict == "CE"


# ------------------------------------------------------------------------------
# Factory resolution
# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    "language,expected_cls",
    [
        ("C", GccCompilerAdapter),
        ("GCC", GccCompilerAdapter),
        ("Practical C (Biên dịch GCC)", GccCompilerAdapter),
        ("JAVA", JavacCompilerAdapter),
        ("JAVA (JDK 17)", JavacCompilerAdapter),
        ("PYTHON", PythonInterpreterAdapter),
        ("Python 3.11", PythonInterpreterAdapter),
    ],
)
def test_factory_resolves_adapter_by_language(language, expected_cls):
    assert isinstance(CompilerAdapterFactory.get_adapter(language), expected_cls)


def test_factory_unknown_language_falls_back_to_gcc_with_default_timeout():
    adapter = CompilerAdapterFactory.get_adapter("", timeout=7.5)
    assert isinstance(adapter, GccCompilerAdapter)
    assert adapter.timeout == 7.5


def test_convenience_wrapper_delegates_to_factory():
    assert isinstance(get_compiler_adapter("PYTHON"), PythonInterpreterAdapter)


# ------------------------------------------------------------------------------
# Missing source -> CE (ST01_TC004 supports skipping AI on CE)
# ------------------------------------------------------------------------------
def test_missing_source_compiles_to_ce_for_every_adapter(tmp_path):
    ghost = tmp_path / "ghost.c"
    for adapter in (GccCompilerAdapter(), JavacCompilerAdapter(), PythonInterpreterAdapter()):
        res = adapter.compile(ghost)
        assert res.success is False and res.verdict == "CE"
        assert "Không tìm thấy file mã nguồn" in res.log


# ------------------------------------------------------------------------------
# PythonInterpreterAdapter (real py_compile, offline & instant)
# ------------------------------------------------------------------------------
def test_python_adapter_accepts_valid_syntax(valid_py_file):
    res = PythonInterpreterAdapter().compile(valid_py_file)
    assert res.success is True and res.verdict == "OK"
    assert res.target == str(valid_py_file)


def test_python_adapter_reports_syntax_error_as_ce(broken_py_file):
    res = PythonInterpreterAdapter().compile(broken_py_file)
    assert res.success is False and res.verdict == "CE"
    assert "Syntax Error" in res.log


# ------------------------------------------------------------------------------
# GccCompilerAdapter (subprocess mocked)
# ------------------------------------------------------------------------------
def test_gcc_adapter_builds_target_path_on_success(tmp_path):
    src = tmp_path / "SE180001_Q1.c"
    src.write_text("int main(){return 0;}\n", encoding="utf-8")
    with patch("core.adapters.compiler_adapter.find_gcc_executable", return_value="C:/gcc/bin/gcc.exe"), \
         patch("core.adapters.compiler_adapter.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        res = GccCompilerAdapter().compile(src)

    assert res.success is True and res.verdict == "OK"
    assert res.target == str(tmp_path / "SE180001_Q1_build.exe")
    cmd = mock_run.call_args.args[0]
    assert "-std=c11" in cmd and "-Wall" in cmd and cmd[0] == "C:/gcc/bin/gcc.exe"


def test_gcc_adapter_maps_compiler_stderr_to_ce(tmp_path):
    src = tmp_path / "broken.c"
    src.write_text("int main(){\n", encoding="utf-8")
    with patch("core.adapters.compiler_adapter.find_gcc_executable", return_value="gcc"), \
         patch("core.adapters.compiler_adapter.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "broken.c:1:12: error: expected '}'"
        res = GccCompilerAdapter().compile(src)

    assert res.success is False and res.verdict == "CE"
    assert "error:" in res.log and res.target is None


def test_gcc_adapter_report_compile_timeout(tmp_path):
    src = tmp_path / "slow.c"
    src.write_text("int main(){return 0;}\n", encoding="utf-8")
    with patch("core.adapters.compiler_adapter.find_gcc_executable", return_value="gcc"), \
         patch("core.adapters.compiler_adapter.subprocess.run",
               side_effect=TimeoutExpired(cmd="gcc", timeout=12.0)):
        res = GccCompilerAdapter().compile(src)

    assert res.success is False and res.timed_out is True
    assert "Quá thời gian biên dịch" in res.log


def test_gcc_adapter_without_gcc_binary_reports_install_hint(tmp_path):
    src = tmp_path / "any.c"
    src.write_text("int main(){return 0;}\n", encoding="utf-8")
    with patch("core.adapters.compiler_adapter.find_gcc_executable", return_value=None):
        res = GccCompilerAdapter().compile(src)
    assert res.success is False and "gcc" in res.log


# ------------------------------------------------------------------------------
# JavacCompilerAdapter (subprocess mocked)
# ------------------------------------------------------------------------------
def test_javac_adapter_processed_target_includes_class_name(tmp_path):
    src = tmp_path / "MainErr.java"
    src.write_text("public class MainErr{public static void main(String[] a){}}\n", encoding="utf-8")
    with patch("core.adapters.compiler_adapter.subprocess.run") as mock_run:
        mock_run.run = None  # harmless attribute guard
        mock_run.return_value.returncode = 0
        res = JavacCompilerAdapter().compile(src)

    assert res.success is True
    assert res.target == f"{src.parent}:MainErr"
    cmd = mock_run.call_args.args[0]
    assert cmd[:2] == ["javac", "-encoding"]


def test_javac_adapter_maps_stderr_to_ce(tmp_path):
    src = tmp_path / "MainErr.java"
    src.write_text("class MainErr{\n", encoding="utf-8")
    with patch("core.adapters.compiler_adapter.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "MainErr.java:1: error: reached end of file"
        res = JavacCompilerAdapter().compile(src)
    assert res.success is False and res.verdict == "CE" and "error:" in res.log


# ------------------------------------------------------------------------------
# WinGet/registry gcc discovery fallbacks (no compiler needed)
# ------------------------------------------------------------------------------
def test_find_gcc_executable_returns_none_when_everything_is_missing(tmp_path, monkeypatch):
    # Pin down every discovery branch so the probe is deterministic:
    # shutil.which scans a PATH without gcc, the registry raises, and no
    # WinGet/common install directory reports an existing gcc.exe.
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "no_such_dir"))
    monkeypatch.setattr("core.adapters.compiler_adapter.bundled_toolchains_dir", lambda: None)
    monkeypatch.setattr("core.adapters.compiler_adapter.load_config", lambda: {})
    monkeypatch.setattr(
        "winreg.OpenKey",
        lambda *a, **kw: (_ for _ in ()).throw(OSError("registry sandboxed")),
    )
    monkeypatch.setattr(Path, "is_file", lambda self: False)
    monkeypatch.setattr(Path, "exists", lambda self: False)
    assert find_gcc_executable() is None


def test_find_gcc_executable_scans_winget_packages(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    winget_bin = tmp_path / "Microsoft" / "WinGet" / "Packages" / "WinLibs" / "bin"
    winget_bin.mkdir(parents=True)
    gcc = winget_bin / "gcc.exe"
    gcc.write_bytes(b"MZ")

    with patch("winreg.OpenKey", side_effect=OSError("sandbox")):
        found = find_gcc_executable()

    assert found == str(gcc)
