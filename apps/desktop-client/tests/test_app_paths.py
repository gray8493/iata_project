"""Runtime path resolution (core.app_paths) + toolchain discovery.

Covers the portable-toolchain contract that lets a packaged AITA.exe grade
without MinGW/JDK/Python installed on the instructor machine:

- `bundled_toolchains_dir()` prefers `_MEIPASS` -> exe dir -> dev folder.
- `find_gcc_executable()` / `find_java_tool()` honour bundled tools first,
  then `config.json`, then PATH/JAVA_HOME.
- `resolve_python_executable()` skips the Microsoft Store python alias and
  raises a friendly error instead of returning a broken path.
- `app_data_dir()` never writes into the ephemeral `_MEIPASS` folder.
"""

import sys
from pathlib import Path

import pytest

from core import app_paths
from core.adapters import compiler_adapter


@pytest.fixture
def fake_bundle(tmp_path, monkeypatch):
    """Giả lập bản đóng gói: exe dir + toolchains/ + _MEIPASS."""
    exe_dir = tmp_path / "dist"
    exe_dir.mkdir()
    toolchains = exe_dir / "toolchains"
    toolchains.mkdir()

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(exe_dir / "AITA.exe"), raising=False)
    monkeypatch.delenv("AITA_PYTHON", raising=False)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "localappdata"))
    return toolchains


def _touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"MZ")
    return path


# ------------------------------------------------------------------------------
# bundled_toolchains_dir
# ------------------------------------------------------------------------------
def test_bundled_toolchains_dir_prefers_meipass(tmp_path, fake_bundle, monkeypatch):
    meipass = tmp_path / "meipass"
    (meipass / "toolchains").mkdir(parents=True)
    monkeypatch.setattr(sys, "_MEIPASS", str(meipass), raising=False)

    assert app_paths.bundled_toolchains_dir() == meipass / "toolchains"


def test_bundled_toolchains_dir_falls_back_to_exe_directory(fake_bundle, monkeypatch):
    monkeypatch.delattr(sys, "_MEIPASS", raising=False)
    assert app_paths.bundled_toolchains_dir() == fake_bundle


def test_bundled_toolchains_dir_returns_none_when_absent(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(tmp_path / "AITA.exe"), raising=False)
    monkeypatch.delattr(sys, "_MEIPASS", raising=False)
    monkeypatch.setattr(app_paths, "__file__", str(tmp_path / "src" / "core" / "app_paths.py"))

    assert app_paths.bundled_toolchains_dir() is None


# ------------------------------------------------------------------------------
# find_gcc_executable - bundled tool wins over everything else
# ------------------------------------------------------------------------------
def test_find_gcc_prefers_bundled_toolchain(fake_bundle, monkeypatch):
    gcc = _touch(fake_bundle / "mingw64" / "bin" / "gcc.exe")
    monkeypatch.setattr(
        compiler_adapter.shutil, "which",
        lambda name: pytest.fail("không được dò PATH khi đã có toolchain đóng kèm"),
    )

    assert compiler_adapter.find_gcc_executable() == str(gcc)


def test_find_gcc_uses_saved_config_before_path(tmp_path, fake_bundle, monkeypatch):
    configured = _touch(tmp_path / "custom" / "gcc.exe")
    monkeypatch.setattr(app_paths, "load_config", lambda: {"gcc_path": str(configured)})
    monkeypatch.setattr(compiler_adapter, "load_config", lambda: {"gcc_path": str(configured)})
    monkeypatch.setattr(
        compiler_adapter.shutil, "which",
        lambda name: pytest.fail("không được dò PATH khi config.json đã chỉ định"),
    )

    assert compiler_adapter.find_gcc_executable() == str(configured)


def test_find_gcc_ignores_config_pointing_to_missing_file(fake_bundle, monkeypatch):
    monkeypatch.setattr(
        compiler_adapter, "load_config",
        lambda: {"gcc_path": "Z:/khong/ton/tai/gcc.exe"},
    )
    on_path = _touch(Path(fake_bundle).parent / "pathbin" / "gcc.exe")
    monkeypatch.setattr(compiler_adapter.shutil, "which", lambda name: str(on_path))

    assert compiler_adapter.find_gcc_executable() == str(on_path)


# ------------------------------------------------------------------------------
# find_java_tool
# ------------------------------------------------------------------------------
def test_find_java_tool_prefers_bundled_jdk(fake_bundle, monkeypatch):
    javac = _touch(fake_bundle / "jdk" / "bin" / "javac.exe")
    monkeypatch.setattr(
        compiler_adapter.shutil, "which",
        lambda name: pytest.fail("không được dò PATH khi đã có JDK đóng kèm"),
    )

    assert compiler_adapter.find_java_tool("javac") == str(javac)


def test_find_java_tool_uses_java_home(fake_bundle, tmp_path, monkeypatch):
    jdk = tmp_path / "jdk-custom"
    java = _touch(jdk / "bin" / "java.exe")
    monkeypatch.setenv("JAVA_HOME", str(jdk))
    monkeypatch.setattr(compiler_adapter, "load_config", lambda: {})
    monkeypatch.setattr(compiler_adapter.shutil, "which", lambda name: None)

    assert compiler_adapter.find_java_tool("java") == str(java)


def test_find_java_tool_returns_none_when_missing(fake_bundle, monkeypatch):
    monkeypatch.delenv("JAVA_HOME", raising=False)
    monkeypatch.setattr(compiler_adapter, "load_config", lambda: {})
    monkeypatch.setattr(compiler_adapter.shutil, "which", lambda name: None)

    assert compiler_adapter.find_java_tool("javac") is None


# ------------------------------------------------------------------------------
# resolve_python_executable
# ------------------------------------------------------------------------------
def test_resolve_python_prefers_bundled_embeddable(fake_bundle, monkeypatch):
    python_exe = _touch(fake_bundle / "python" / "python.exe")
    monkeypatch.setattr(
        app_paths.shutil, "which",
        lambda name: pytest.fail("không được dò PATH khi đã có Python đóng kèm"),
    )

    assert app_paths.resolve_python_executable() == str(python_exe)


def test_resolve_python_skips_windows_store_alias(fake_bundle, tmp_path, monkeypatch):
    stub = tmp_path / "Microsoft" / "WindowsApps" / "python.exe"
    real = _touch(tmp_path / "Python311" / "python.exe")

    def fake_which(name):
        return str(stub) if name == "python" else str(real)

    monkeypatch.setattr(app_paths.shutil, "which", fake_which)
    monkeypatch.setattr(app_paths, "load_config", lambda: {})

    # Alias Microsoft Store bị bỏ qua -> rơi xuống 'python3'.
    assert app_paths.resolve_python_executable() == str(real)


def test_resolve_python_raises_actionable_error_when_absent(fake_bundle, monkeypatch):
    monkeypatch.setattr(app_paths.shutil, "which", lambda name: None)
    monkeypatch.setattr(app_paths, "load_config", lambda: {})

    with pytest.raises(RuntimeError, match="toolchains/python"):
        app_paths.resolve_python_executable()


def test_resolve_python_returns_sys_executable_in_dev(monkeypatch):
    monkeypatch.setattr(sys, "frozen", False, raising=False)
    assert app_paths.resolve_python_executable() == sys.executable


# ------------------------------------------------------------------------------
# app_data_dir / config.json
# ------------------------------------------------------------------------------
def test_app_data_dir_never_writes_into_meipass(tmp_path, fake_bundle, monkeypatch):
    meipass = tmp_path / "meipass"
    meipass.mkdir()
    monkeypatch.setattr(sys, "_MEIPASS", str(meipass), raising=False)

    data_dir = app_paths.app_data_dir()

    assert meipass not in data_dir.parents
    assert data_dir == tmp_path / "localappdata" / "AITA" / "data"
    assert data_dir.is_dir()


def test_config_round_trip(tmp_path, fake_bundle, monkeypatch):
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path / "meipass"), raising=False)
    monkeypatch.setattr(app_paths, "app_data_dir", lambda: tmp_path / "data")

    assert app_paths.save_config({"gcc_path": "C:/mingw/bin/gcc.exe"}) is True
    assert app_paths.load_config()["gcc_path"] == "C:/mingw/bin/gcc.exe"

    # Ghi bổ sung phải giữ khóa cũ.
    app_paths.save_config({"python_path": "C:/py/python.exe"})
    config = app_paths.load_config()
    assert config["gcc_path"] == "C:/mingw/bin/gcc.exe"
    assert config["python_path"] == "C:/py/python.exe"


def test_load_config_tolerates_corrupt_json(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / app_paths.CONFIG_FILE_NAME).write_text("{ khong phai json", encoding="utf-8")
    monkeypatch.setattr(app_paths, "app_data_dir", lambda: data_dir)

    assert app_paths.load_config() == {}
