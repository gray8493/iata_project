"""RunnerFactory (Factory Method Pattern / core.factories.runner_factory).

Covers language -> runner resolution (including UI label variants), the
default fallback, and the runtime `register_runner` extension point (OCP).
"""

import pytest

from core.factories.runner_factory import RunnerFactory
from core.runners.base_runner import BaseRunner
from core.runners.c_runner import CRunner
from core.runners.java_runner import JavaRunner
from core.runners.python_runner import PythonRunner


@pytest.mark.parametrize(
    "language,expected_cls",
    [
        ("C", CRunner),
        ("c", CRunner),
        ("C (Biên dịch GCC)", CRunner),
        ("JAVA", JavaRunner),
        ("Java (jbuild)", JavaRunner),
        ("PYTHON", PythonRunner),
        ("Python 3.11", PythonRunner),
        ("PY (PRF PHP)", PythonRunner),
    ],
)
def test_get_runner_resolves_by_language(language, expected_cls):
    assert isinstance(RunnerFactory.get_runner(language), expected_cls)


def test_get_runner_unknown_language_falls_back_to_c():
    assert isinstance(RunnerFactory.get_runner("RUST"), CRunner)


def test_get_runner_returns_fresh_instances_per_call():
    first = RunnerFactory.get_runner("PYTHON")
    second = RunnerFactory.get_runner("PYTHON")
    assert first is not second and type(first) is type(second)


def test_register_runner_overrides_existing_language_at_runtime():
    class InstrumentedJavaRunner(JavaRunner):
        trace = True

    RunnerFactory.register_runner("JAVA", InstrumentedJavaRunner)
    try:
        assert RunnerFactory.get_runner("JAVA").trace is True
    finally:
        RunnerFactory.register_runner("JAVA", JavaRunner)

    assert isinstance(RunnerFactory.get_runner("JAVA"), JavaRunner)


def test_registered_runner_still_satisfies_base_runner_contract():
    class DummyRunner(BaseRunner):
        def compile(self, source_path):
            return False, "no compile in dummy", None

        def execute(self, executable_target, input_data="", time_limit_ms=1000,
                    memory_limit_mb=128):
            raise NotImplementedError

    RunnerFactory.register_runner("PYTHON", DummyRunner)
    try:
        assert isinstance(RunnerFactory.get_runner("PYTHON"), DummyRunner)
    finally:
        RunnerFactory.register_runner("PYTHON", PythonRunner)


def test_runners_delegate_compile_to_compiler_adapter():
    # Adapter Pattern wiring: every concrete runner owns an adapter instance.
    assert RunnerFactory.get_runner("C").adapter is not None
    assert RunnerFactory.get_runner("JAVA").adapter is not None
    assert RunnerFactory.get_runner("PYTHON").adapter is not None
