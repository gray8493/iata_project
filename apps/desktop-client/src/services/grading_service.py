"""
AITA Desktop Client - Grading Service Coordinator
Orchestrates compilation, sandbox testcase execution, matching strategies, and database persistence.
"""

from pathlib import Path
from typing import Dict, Any, List, Callable, Optional

from database.db_manager import DatabaseManager
from core.factories.runner_factory import RunnerFactory
from core.strategies.context import MatchingContext


class GradingService:
    """Service orchestrating batch grading for university practical programming exams."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()

    def grade_class_batch(
        self,
        class_id: int,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> List[Dict[str, Any]]:
        """
        Grades all active student submissions for a given class session.
        Args:
            class_id: Target class session ID
            progress_callback: Optional callable(current_idx, total_count, current_student_mssv)
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

        # 2. Resolve Runner and Matching Context
        runner = RunnerFactory.get_runner(language)
        matching_ctx = MatchingContext()
        total_subs = len(submissions)
        results = []

        total_weight = sum(tc.get("score_weight", 1.0) for tc in testcases) or 10.0

        for idx, sub in enumerate(submissions):
            mssv = sub["student_mssv"]
            source_file = Path(sub["source_file_path"])

            if progress_callback:
                progress_callback(idx + 1, total_subs, mssv)

            # Step 2.1: Compile source code
            success, compile_log, exec_target = runner.compile(source_file)
            if not success:
                # Compile Error (CE)
                self.db.save_console_grading_result(
                    submission_id=sub["id"],
                    matching_strategy="EXACT_MATCH",
                    calculated_score=0.0,
                    final_verdict="CE",
                    execution_time_ms=0.0,
                    memory_used_mb=0.0,
                    compile_log=compile_log,
                    diff_details="Lỗi biên dịch mã nguồn cú pháp."
                )
                results.append({"mssv": mssv, "verdict": "CE", "score": 0.0})
                continue

            # Step 2.2: Execute testcases
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

                # Compare output via configured strategy
                match_res = matching_ctx.compare(res.stdout, tc.get("expected_output", ""))
                if match_res.is_matched:
                    earned_weight += tc.get("score_weight", 1.0)
                else:
                    if worst_verdict == "AC":
                        worst_verdict = "WA"
                        first_diff = match_res.diff_details

            # Step 2.3: Compute final 10.0 scaled score
            final_score = round((earned_weight / total_weight) * 10.0, 1) if total_weight > 0 else 0.0
            final_verdict = worst_verdict if final_score < 10.0 else "AC"

            # Step 2.4: Save result
            self.db.save_console_grading_result(
                submission_id=sub["id"],
                matching_strategy=testcases[0].get("matching_strategy", "EXACT_MATCH"),
                calculated_score=final_score,
                final_verdict=final_verdict,
                execution_time_ms=max_exec_time,
                memory_used_mb=max_mem,
                diff_details=first_diff
            )
            results.append({"mssv": mssv, "verdict": final_verdict, "score": final_score})

        return results
