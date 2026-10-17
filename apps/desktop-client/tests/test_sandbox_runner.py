"""SandboxRunner (core.sandbox.runner) - ST01 batch-grading resource guard.

Directly exercises the psutil-based resource monitor that produces the
sandbox verdicts consumed by the batch grading pipeline:

- OK  : clean exit within limits
- TLE : job outruns ``time_limit_ms`` (infinite loop gets killed)
- MLE : RSS crosses ``memory_limit_mb`` (process gets killed)
- RE  : non-zero exit code
- RE  : command cannot be launched at all
"""

import sys

from core.sandbox.runner import SandboxRunner


def test_clean_run_returns_ok_and_echoes_stdout():
    res = SandboxRunner.run_process(
        command=[sys.executable, "-u", "-c", "n = int(input()); print(n * 2)"],
        input_data="5\n",
        time_limit_ms=5000,
        memory_limit_mb=256,
    )

    assert res.verdict == "OK"
    assert res.return_code == 0
    assert res.stdout.strip() == "10"


def test_infinite_loop_is_killed_as_tle():
    res = SandboxRunner.run_process(
        command=[sys.executable, "-u", "-c", "while True:\n    pass"],
        time_limit_ms=250,
        memory_limit_mb=256,
    )

    assert res.verdict == "TLE"
    assert res.return_code == -1
    assert res.error_message and "giới hạn thời gian" in res.error_message


def test_memory_hog_is_killed_as_mle():
    script = "buf = bytearray(200 * 1024 * 1024)\nimport time\ntime.sleep(3)\n"

    res = SandboxRunner.run_process(
        command=[sys.executable, "-u", "-c", script],
        time_limit_ms=8000,
        memory_limit_mb=64,
    )

    assert res.verdict == "MLE"
    assert res.memory_used_mb > 64


def test_nonzero_exit_is_runtime_error():
    res = SandboxRunner.run_process(
        command=[sys.executable, "-u", "-c", "import sys; sys.exit(3)"],
        time_limit_ms=5000,
        memory_limit_mb=256,
    )

    assert res.verdict == "RE"
    assert res.return_code == 3


def test_unlaunchable_command_is_runtime_error():
    res = SandboxRunner.run_process(
        command=["aita-definitely-not-a-real-binary-xyz"],
        time_limit_ms=1000,
        memory_limit_mb=64,
    )

    assert res.verdict == "RE"
    assert res.return_code == -1
    assert res.error_message and "Không thể khởi chạy" in res.error_message


def test_execution_time_is_measured():
    res = SandboxRunner.run_process(
        command=[sys.executable, "-u", "-c", "import time; time.sleep(0.05); print('ok')"],
        time_limit_ms=5000,
        memory_limit_mb=256,
    )

    assert res.verdict == "OK"
    assert res.execution_time_ms >= 40
