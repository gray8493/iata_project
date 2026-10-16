"""
AITA Desktop Client - Grading Service Coordinator
Orchestrates compilation, sandbox testcase execution, matching strategies, and database persistence.

Batch grading runs on a process pool (`ProcessPoolExecutor`, 4-8 workers) so the UI thread
stays responsive while submissions are compiled and executed in parallel.
"""

import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Any, List, Callable, Optional

from database.db_manager import DatabaseManager
from core.factories.runner_factory import RunnerFactory
from core.strategies.context import MatchingContext

MIN_WORKERS = 4
MAX_WORKERS = 8


def grade_single_submission(
    submission: Dict[str, Any],
    language: str,
    testcases: List[Dict[str, Any]],
    total_weight: float
) -> Dict[str, Any]:
    """
    Compiles and grades one submission in a worker process (no DB access here).

    Top-level function so it is picklable for `ProcessPoolExecutor` on Windows (spawn).
    Returns a result dict ready to be persisted by the parent process.
    """
    runner = RunnerFactory.get_runner(language)
    matching_ctx = MatchingContext()
    mssv = submission.get("student_mssv", "")
    submission_id = submission.get("id")
    matching_strategy = testcases[0].get("matching_strategy", "EXACT_MATCH") if testcases else "EXACT_MATCH"
    source_file = Path(submission["source_file_path"])

    result = {
        "submission_id": submission_id,
        "mssv": mssv,
        "verdict": "RE",
        "score": 0.0,
        "execution_time_ms": 0.0,
        "memory_used_mb": 0.0,
        "compile_log": None,
        "diff_details": None,
        "matching_strategy": matching_strategy
    }

    # Step 1: Compile source code
    success, compile_log, exec_target = runner.compile(source_file)
    if not success or not exec_target:
        result["verdict"] = "CE"
        result["compile_log"] = compile_log
        result["diff_details"] = "Lỗi biên dịch mã nguồn cú pháp."
        return result

    # Step 2: Execute testcases
    earned_weight = 0.0
    worst_verdict = "AC"
    max_exec_time = 0.0
    max_mem = 0.0
    first_diff = None

    for tc in testcases:
        matching_ctx.set_strategy_by_name(tc.get("matching_strategy", "EXACT_MATCH"))
        res = runner.execute(
            executable_target=exec_target,
            input_data=tc.get("input_data", ""),
            time_limit_ms=tc.get("time_limit_ms", 1500),
            memory_limit_mb=tc.get("memory_limit_mb", 128)
        )

        max_exec_time = max(max_exec_time, res.execution_time_ms)
        max_mem = max(max_mem, res.memory_used_mb)

        if res.verdict != "OK":
            worst_verdict = res.verdict  # TLE, MLE, or RE
            first_diff = res.error_message
            break

        match_res = matching_ctx.compare(res.stdout, tc.get("expected_output", ""))
        if match_res.is_matched:
            earned_weight += tc.get("score_weight", 1.0)
        else:
            if worst_verdict == "AC":
                worst_verdict = "WA"
                first_diff = match_res.diff_details

    # Step 3: Compute final 10.0 scaled score
    final_score = round((earned_weight / total_weight) * 10.0, 1) if total_weight > 0 else 0.0
    result.update({
        "verdict": worst_verdict if final_score < 10.0 else "AC",
        "score": final_score,
        "execution_time_ms": max_exec_time,
        "memory_used_mb": max_mem,
        "diff_details": first_diff
    })
    return result


class GradingService:
    """Service orchestrating batch grading for university practical programming exams."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()

    def grade_class_batch(
        self,
        class_id: int,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        max_workers: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Grades all active student submissions for a given class session in parallel.

        Args:
            class_id: Target class session ID
            progress_callback: Optional callable(completed_count, total_count, current_student_mssv)
            max_workers: Optional override for the process pool size (defaults to 4-8)
        """
        # 1. Fetch class info, submissions and testcases
        classes = self.db.get_all_classes()
        class_info = next((c for c in classes if c["id"] == class_id), None)
        if not class_info:
            raise ValueError(f"Không tìm thấy đợt chấm có ID = {class_id}")

        language = class_info.get("programming_language", "C")
        submissions = self.db.get_submissions_by_class(class_id)
        testcases = self.db.get_testcases_by_class(class_id)

        if not testcases:
            raise ValueError(
                f"Đợt chấm '{class_info.get('class_name', '')}' hiện chưa có testcase nào! "
                "Vui lòng vào 'Cấu Hình Testcase' để thêm ít nhất 1 testcase trước khi bắt đầu chấm."
            )

        total_subs = len(submissions)
        results: List[Optional[Dict[str, Any]]] = [None] * total_subs
        if total_subs == 0:
            return []

        total_weight = sum(tc.get("score_weight", 1.0) for tc in testcases) or 10.0

        # 2. Resolve pool size: honour documented 4-8 workers, bounded by workload
        if max_workers is None:
            cpu = os.cpu_count() or MIN_WORKERS
            max_workers = min(MAX_WORKERS, max(MIN_WORKERS, cpu))
        num_workers = max(1, min(max_workers, total_subs))

        # 3. Dispatch submissions to the worker pool and persist results as they complete
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            future_to_index = {
                executor.submit(grade_single_submission, sub, language, testcases, total_weight): idx
                for idx, sub in enumerate(submissions)
            }

            completed = 0
            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                sub = submissions[idx]
                try:
                    res = future.result()
                except Exception as ex:
                    res = {
                        "submission_id": sub.get("id"),
                        "mssv": sub.get("student_mssv", ""),
                        "verdict": "RE",
                        "score": 0.0,
                        "execution_time_ms": 0.0,
                        "memory_used_mb": 0.0,
                        "compile_log": f"Lỗi tiến trình chấm song song: {ex}",
                        "diff_details": None,
                        "matching_strategy": testcases[0].get("matching_strategy", "EXACT_MATCH")
                    }

                self._save_result(res)
                results[idx] = {"mssv": res["mssv"], "verdict": res["verdict"], "score": res["score"]}

                completed += 1
                if progress_callback:
                    progress_callback(completed, total_subs, res["mssv"])

        return [r for r in results if r is not None]

    def _save_result(self, res: Dict[str, Any]) -> None:
        """Persists one graded submission to local SQLite (serialized in the parent process)."""
        try:
            self.db.save_console_grading_result(
                submission_id=res["submission_id"],
                matching_strategy=res.get("matching_strategy", "EXACT_MATCH"),
                calculated_score=res["score"],
                final_verdict=res["verdict"],
                execution_time_ms=res.get("execution_time_ms", 0.0),
                memory_used_mb=res.get("memory_used_mb", 0.0),
                compile_log=res.get("compile_log"),
                diff_details=res.get("diff_details")
            )
        except Exception:
            pass
