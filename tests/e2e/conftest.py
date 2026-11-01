"""AITA e2e — toolchain availability gates.

E2E tests compile and run real student programs (GCC / JDK / CPython), so each
fixture below skips cleanly when the required toolchain is missing (e.g. a
lightweight CI machine without compilers).
"""
import pytest


@pytest.fixture
def require_c_toolchain():
    from core.adapters.compiler_adapter import find_gcc_executable

    if not find_gcc_executable():
        pytest.skip("Không tìm thấy GCC — bỏ qua e2e C (cần toolchain thật).")


@pytest.fixture
def require_java_toolchain():
    from core.adapters.compiler_adapter import find_java_tool

    if not find_java_tool("javac") or not find_java_tool("java"):
        pytest.skip("Không tìm thấy JDK (javac/java) — bỏ qua e2e Java.")


@pytest.fixture
def require_python_toolchain():
    from core.app_paths import resolve_python_executable

    try:
        resolve_python_executable()
    except RuntimeError:
        pytest.skip("Không tìm thấy Python — bỏ qua e2e Python.")
