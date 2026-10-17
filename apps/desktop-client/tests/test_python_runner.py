"""PythonRunner (core.runners.python_runner) - compile + sandbox execute wiring.

Verifies the Factory-produced Python runner drives the interpreter adapter for
compilation and the SandboxRunner for execution (the C/Java runners share this
contract, covered separately by test_compiler_adapter.py).
"""

from core.factories.runner_factory import RunnerFactory


def test_factory_returns_python_runner_for_python_language():
    runner = RunnerFactory.get_runner("PYTHON")
    assert type(runner).__name__ == "PythonRunner"


def test_compile_valid_python_and_execute_through_sandbox(tmp_path):
    src = tmp_path / "SE180001_Q1.py"
    src.write_text("n = int(input())\nprint(n * 2)\n", encoding="utf-8")
    runner = RunnerFactory.get_runner("PYTHON")

    success, log, target = runner.compile(src)

    assert success is True and target
    res = runner.execute(target, input_data="6\n", time_limit_ms=5000, memory_limit_mb=256)
    assert res.verdict == "OK"
    assert res.stdout.strip() == "12"


def test_compile_syntax_error_is_reported_as_ce(tmp_path):
    src = tmp_path / "broken.py"
    src.write_text("def broken(:\n    pass\n", encoding="utf-8")

    success, log, target = RunnerFactory.get_runner("PYTHON").compile(src)

    assert success is False and target is None
    assert "Syntax" in log or "syntax" in log
