"""
AITA Desktop Client - Java Language Runner (Javac Compiler & JVM)
Compiles Java source (.java) into bytecode (.class) and runs through main() method.
"""

import subprocess
from pathlib import Path
from typing import Tuple, Optional

from .base_runner import BaseRunner
from core.sandbox.runner import SandboxRunner, SandboxResult


class JavaRunner(BaseRunner):
    """Runner for Java language (PRO192, CSD201)."""

    def compile(self, source_path: Path) -> Tuple[bool, str, Optional[str]]:
        if not source_path.exists():
            return False, f"Không tìm thấy file mã nguồn: {source_path}", None

        cmd = ["javac", "-encoding", "UTF-8", str(source_path)]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=12.0)
            if res.returncode != 0:
                return False, res.stderr or res.stdout, None
            
            # The executable target is the class name without .java
            class_name = source_path.stem
            return True, "Biên dịch Java thành công", f"{source_path.parent}:{class_name}"
        except FileNotFoundError:
            return False, "Không tìm thấy trình biên dịch 'javac' (JDK)! Vui lòng kiểm tra biến môi trường JAVA_HOME.", None
        except subprocess.TimeoutExpired:
            return False, "Quá thời gian biên dịch Java", None
        except Exception as ex:
            return False, f"Lỗi biên dịch Java: {str(ex)}", None

    def execute(
        self,
        executable_target: str,
        input_data: str = "",
        time_limit_ms: int = 1500,
        memory_limit_mb: int = 256
    ) -> SandboxResult:
        # executable_target format: "classpath:class_name"
        classpath, class_name = executable_target.split(":", 1)
        cmd = ["java", "-cp", classpath, class_name]

        return SandboxRunner.run_process(
            command=cmd,
            input_data=input_data,
            time_limit_ms=time_limit_ms,
            memory_limit_mb=memory_limit_mb,
            cwd=classpath
        )
