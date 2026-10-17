"""
AITA Desktop Client - Grading Service Coordinator
Orchestrates compilation, sandbox testcase execution, matching strategies, and database persistence.

Batch grading runs on a process pool (`ProcessPoolExecutor`, 4-8 workers) so the UI thread
stays responsive while submissions are compiled and executed in parallel.
"""

import os
import re
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Any, List, Callable, Optional, Tuple

from database.db_manager import DatabaseManager
from core.factories.runner_factory import RunnerFactory
from core.strategies.context import MatchingContext

MIN_WORKERS = 4
MAX_WORKERS = 8

# Severity ranking khi một bài nộp gặp nhiều loại lỗi khác nhau (multi-question mode)
VERDICT_SEVERITY: Dict[str, int] = {"AC": 0, "WA": 1, "CE": 2, "TLE": 3, "MLE": 3, "RE": 4}


def _pick_worse(a: str, b: str) -> str:
    """Returns the more severe verdict (used when one question fails differently than another)."""
    return a if VERDICT_SEVERITY.get(a, 0) >= VERDICT_SEVERITY.get(b, 0) else b

LANG_EXTS: Dict[str, List[str]] = {
    "PY": [".py"],
    "JAVA": [".java"],
    "C": [".c", ".cpp"],
}


def _allowed_exts(language: str) -> List[str]:
    """Valid source extensions for the class language (multi-question file lookup)."""
    key = (language or "").strip().upper()
    if "PY" in key:
        return LANG_EXTS["PY"]
    if "JAVA" in key or "PHP" in key:
        return LANG_EXTS["JAVA"]
    return LANG_EXTS["C"]


def _resolve_question_file(
    student_root: Path,
    question_number: str,
    language: str
) -> Optional[Path]:
    """
    Resolves `Q<nn>.<ext>` inside a student folder from a testcase's question_number.
    Used for multi-question grading when source_file_path points to the student folder.
    """
    match = re.search(r"[Qq]\s*(\d+)", question_number or "")
    if not match:
        return None
    qnum = int(match.group(1))
    for ext in _allowed_exts(language):
        candidate = student_root / f"Q{qnum}{ext}"
        if candidate.is_file():
            return candidate
    return None


def grade_single_submission(
    submission: Dict[str, Any],
    language: str,
    testcases: List[Dict[str, Any]],
    total_weight: float
) -> Dict[str, Any]:
    """
    Compiles and grades one submission in a worker process (no DB access here).

    Two supported layouts:
    - Single question: `source_file_path` is a source file -> every testcase runs that file.
    - Multi question:  `source_file_path` is a student folder with `Q<nn>.<ext>` files ->
      each testcase runs the file matching its `question_number` (compiler per file).

    Top-level function so it is picklable for `ProcessPoolExecutor` on Windows (spawn).
    Returns a result dict ready to be persisted by the parent process.
    """
    runner = RunnerFactory.get_runner(language)
    matching_ctx = MatchingContext()
    mssv = submission.get("student_mssv", "")
    submission_id = submission.get("id")
    matching_strategy = testcases[0].get("matching_strategy", "EXACT_MATCH") if testcases else "EXACT_MATCH"
    source_root = Path(submission["source_file_path"])

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

    earned_weight = 0.0
    worst_verdict = "AC"
    max_exec_time = 0.0
    max_mem = 0.0
    first_diff: Optional[str] = None
    logs: List[str] = []

    def record_diff(message: str) -> None:
        nonlocal first_diff
        if first_diff is None:
            first_diff = message

    if source_root.is_dir():
        # —— Multi-question mode: file bài làm `Q<nn>.<ext>` theo question_number ——
        # CE/TLE/RE của một câu không dừng các câu khác (chỉ RE/TLE dừng vì runtime treo).
        compile_cache: Dict[str, Tuple[bool, str, Optional[str]]] = {}

        for tc in testcases:
            qnum = tc.get("question_number", "Q1")
            qfile = _resolve_question_file(source_root, qnum, language)
            if qfile is None:
                logs.append(f"{qnum}: Không tìm thấy file bài làm trong thư mục sinh viên.")
                record_diff(f"({qnum}) Thiếu file bài làm {qnum} trong thư mục sinh viên.")
                worst_verdict = _pick_worse(worst_verdict, "CE")
                continue

            cache_key = str(qfile)
            if cache_key not in compile_cache:
                compile_cache[cache_key] = runner.compile(qfile)
            success, compile_log, exec_target = compile_cache[cache_key]

            if not success or not exec_target:
                logs.append(f"{qnum}: CE - {compile_log or 'Lỗi biên dịch.'}")
                record_diff(f"({qnum}) Lỗi biên dịch: {compile_log or ''}")
                worst_verdict = _pick_worse(worst_verdict, "CE")
                continue

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
                # TLE, MLE, or RE stops the run (old semantics preserved)
                worst_verdict = res.verdict
                record_diff(f"({qnum}) {res.error_message}")
                logs.append(f"{qnum}: dừng sớm ({res.verdict}).")
                break

            match_res = matching_ctx.compare(res.stdout, tc.get("expected_output", ""))
            if match_res.is_matched:
                earned_weight += tc.get("score_weight", 1.0)
            else:
                worst_verdict = _pick_worse(worst_verdict, "WA")
                record_diff(f"({qnum}) {match_res.diff_details}")
        result["compile_log"] = "\n".join(logs) if logs else None
    else:
        # —— Single-question mode (classic layout, one source file per submission) ——
        source_file = source_root
        success, compile_log, exec_target = runner.compile(source_file)
        if not success or not exec_target:
            result["verdict"] = "CE"
            result["compile_log"] = compile_log
            result["diff_details"] = "Lỗi biên dịch mã nguồn cú pháp."
            return result

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
                # TLE, MLE, or RE stops the whole run (old semantics preserved)
                worst_verdict = res.verdict
                record_diff(res.error_message)
                break

            match_res = matching_ctx.compare(res.stdout, tc.get("expected_output", ""))
            if match_res.is_matched:
                earned_weight += tc.get("score_weight", 1.0)
            else:
                worst_verdict = _pick_worse(worst_verdict, "WA")
                record_diff(match_res.diff_details)
        result["compile_log"] = compile_log

    # Final 10.0 scaled score
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

    def regrade_submission(self, submission_id: int) -> Dict[str, Any]:
        """
        Re-grades exactly one submission (UC-15) using the current testcase set:
        compile -> sandbox execute -> strategy compare -> persist fresh result.
        """
        sub = self.db.get_submission_by_id(submission_id)
        if not sub:
            raise ValueError(f"Không tìm thấy bài nộp có ID = {submission_id}")

        class_info = self.db.get_class_by_id(sub["class_id"])
        language = (class_info or {}).get("programming_language", "C")
        testcases = self.db.get_testcases_by_class(sub["class_id"])
        if not testcases:
            raise ValueError(
                "Đợt chấm hiện chưa có testcase nào! "
                "Vui lòng vào 'Cấu Hình Testcase' để thêm ít nhất 1 testcase trước khi chấm lại."
            )

        total_weight = sum(tc.get("score_weight", 1.0) for tc in testcases) or 10.0
        result = grade_single_submission(sub, language, testcases, total_weight)
        self._save_result(result)
        return result

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
