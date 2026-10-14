"""
AITA Desktop Client - Sandbox Process Runner & Resource Monitor
Monitors subprocess execution in real-time using psutil.
Enforces:
- Time Limit Exceeded (TLE)
- Memory Limit Exceeded (MLE)
- Runtime Error (RE)
"""

import time
import subprocess
import psutil
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class SandboxResult:
    """Execution metrics and standard streams output."""
    stdout: str
    stderr: str
    return_code: int
    execution_time_ms: float
    memory_used_mb: float
    verdict: str  # "OK", "TLE", "MLE", "RE"
    error_message: Optional[str] = None


class SandboxRunner:
    """Safely executes binaries or scripts within tight CPU and RAM constraints."""

    @staticmethod
    def run_process(
        command: List[str],
        input_data: str = "",
        time_limit_ms: int = 2000,
        memory_limit_mb: int = 128,
        cwd: Optional[str] = None
    ) -> SandboxResult:
        """
        Launches subprocess with piped I/O, feeds input_data to stdin,
        and polls CPU/RAM via psutil until completion or limits exceeded.
        """
        start_time = time.perf_counter()
        time_limit_sec = time_limit_ms / 1000.0
        max_memory_mb = 0.0

        try:
            proc = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd
            )
        except Exception as ex:
            return SandboxResult(
                stdout="",
                stderr=str(ex),
                return_code=-1,
                execution_time_ms=0.0,
                memory_used_mb=0.0,
                verdict="RE",
                error_message=f"Không thể khởi chạy tiến trình: {str(ex)}"
            )

        ps_proc = None
        try:
            ps_proc = psutil.Process(proc.pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

        # Send input immediately to stdin so process does not hang waiting
        try:
            if input_data:
                proc.stdin.write(input_data)
                proc.stdin.flush()
            proc.stdin.close()
        except Exception:
            pass

        try:
            # Check resource periodically
            while True:
                elapsed_sec = time.perf_counter() - start_time
                if elapsed_sec > time_limit_sec:
                    # TLE triggered
                    try:
                        proc.kill()
                    except Exception:
                        pass
                    return SandboxResult(
                        stdout="",
                        stderr="Time Limit Exceeded",
                        return_code=-1,
                        execution_time_ms=elapsed_sec * 1000.0,
                        memory_used_mb=max_memory_mb,
                        verdict="TLE",
                        error_message=f"Vượt quá giới hạn thời gian chạy ({time_limit_ms}ms)"
                    )

                # Monitor RAM
                if ps_proc and ps_proc.is_running():
                    try:
                        mem_info = ps_proc.memory_info()
                        mem_mb = mem_info.rss / (1024 * 1024)
                        if mem_mb > max_memory_mb:
                            max_memory_mb = mem_mb

                        if max_memory_mb > memory_limit_mb:
                            # MLE triggered
                            try:
                                proc.kill()
                            except Exception:
                                pass
                            return SandboxResult(
                                stdout="",
                                stderr="Memory Limit Exceeded",
                                return_code=-1,
                                execution_time_ms=elapsed_sec * 1000.0,
                                memory_used_mb=max_memory_mb,
                                verdict="MLE",
                                error_message=f"Vượt quá giới hạn bộ nhớ RAM ({memory_limit_mb}MB)"
                            )
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

                # Check if finished
                if proc.poll() is not None:
                    break

                time.sleep(0.005)  # 5ms polling resolution

            # Process completed within limits: read streams
            stdout = proc.stdout.read() if proc.stdout else ""
            stderr = proc.stderr.read() if proc.stderr else ""
            total_time_ms = (time.perf_counter() - start_time) * 1000.0

            if proc.returncode != 0:
                return SandboxResult(
                    stdout=stdout,
                    stderr=stderr,
                    return_code=proc.returncode,
                    execution_time_ms=total_time_ms,
                    memory_used_mb=max_memory_mb,
                    verdict="RE",
                    error_message=f"Chương trình kết thúc với mã lỗi {proc.returncode}"
                )

            return SandboxResult(
                stdout=stdout,
                stderr=stderr,
                return_code=0,
                execution_time_ms=total_time_ms,
                memory_used_mb=max_memory_mb,
                verdict="OK"
            )

        except Exception as ex:
            try:
                proc.kill()
            except Exception:
                pass
            return SandboxResult(
                stdout="",
                stderr=str(ex),
                return_code=-1,
                execution_time_ms=(time.perf_counter() - start_time) * 1000.0,
                memory_used_mb=max_memory_mb,
                verdict="RE",
                error_message=str(ex)
            )
