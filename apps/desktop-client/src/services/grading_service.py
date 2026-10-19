"""
AITA Desktop Client - Grading Service Coordinator
Orchestrates compilation, sandbox testcase execution, matching strategies, and database persistence.

Batch grading runs on a process pool (`ProcessPoolExecutor`, 4-8 workers) so the UI thread
stays responsive while submissions are compiled and executed in parallel.
"""

import json
import os
import re
import sys
import threading
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Any, List, Callable, Optional, Tuple

from database.db_manager import DatabaseManager
from core.factories.runner_factory import RunnerFactory
from core.strategies.context import MatchingContext
from core.sandbox.runner import SandboxRunner
from core.app_paths import resolve_python_executable

MIN_WORKERS = 4
MAX_WORKERS = 8

# Severity ranking khi một bài nộp gặp nhiều loại lỗi khác nhau (multi-question mode)
VERDICT_SEVERITY: Dict[str, int] = {"AC": 0, "WA": 1, "CE": 2, "TLE": 3, "MLE": 3, "RE": 4}

# Cache 1 lần/batch: thời gian khởi động trình thông dịch Python (pass trống).
# Dùng để cộng thêm vào time_limit và trừ ra khỏi thời gian ghi nhận (chấm công bằng - pain #5).
_PY_STARTUP_CACHE: Optional[float] = None

# Giới hạn mỗi trường bằng chứng lưu vào JSON để DB payload không phình vô hạn
_EVIDENCE_FIELD_CAP = 4000

# Điểm tối đa cho mỗi nửa của thang 10 (Hybrid: Sandbox 5đ + AI Rubric 5đ)
SANDBOX_MAX_SCORE = 5.0
AI_RUBRIC_MAX_SCORE = 5.0
# 5 tiêu chí chất lượng AI chấm, mỗi tiêu chí PASS = 1.0 điểm
AI_RUBRIC_CRITERIA: Tuple[str, ...] = ("clean_code", "complexity", "structure", "format", "documentation")
AI_RUBRIC_LABELS: Dict[str, str] = {
    "clean_code": "Clean Code (đặt tên biến/hàm)",
    "complexity": "Complexity (độ phức tạp thuật toán)",
    "structure": "Structure (chia hàm/module hóa)",
    "format": "Format (thụt lề, code rác)",
    "documentation": "Documentation (comment, tiêu đề bài làm)",
}

# Đuôi mã nguồn nhận diện khi bài nộp là thư mục (dùng để đọc code cho AI)
_SOURCE_EXTENSIONS = (".py", ".java", ".c", ".cpp", ".cc", ".h", ".hpp", ".cs")


def read_submission_source(source_file_path: Optional[str]) -> str:
    """
    Reads the student's source code for AI quality grading.
    - Single-question layout: `source_file_path` is a source file.
    - Multi-question layout: `source_file_path` is a folder -> concatenate all source files.
    Returns "" when nothing readable is found.
    """
    if not source_file_path:
        return ""
    base = Path(source_file_path)
    if base.is_file():
        try:
            return base.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return ""
    if base.is_dir():
        parts: List[str] = []
        for f in sorted(base.iterdir()):
            if f.is_file() and f.suffix.lower() in _SOURCE_EXTENSIONS:
                try:
                    body = f.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    body = ""
                parts.append(f"// ===== {f.name} =====\n{body}".rstrip())
        return "\n\n".join(parts)
    return ""


def _attach_quality_payload(diff_details: Any, quality: Dict[str, Any]) -> str:
    """
    Merges the AI quality rubric into the per-testcase evidence JSON (cột diff_details).
    Falls back to a JSON wrapper when diff_details is legacy plain text or empty.
    """
    payload: Dict[str, Any]
    if isinstance(diff_details, str) and diff_details:
        try:
            parsed = json.loads(diff_details)
        except (TypeError, ValueError):
            parsed = None
        if isinstance(parsed, dict) and "items" in parsed:
            payload = parsed
        else:
            payload = {"items": [], "legacy_diff": diff_details}
    else:
        payload = {"items": [], "legacy_diff": diff_details}
    payload["quality"] = quality
    return json.dumps(payload, ensure_ascii=False)


def _is_python_language(language: str) -> bool:
    return "PY" in (language or "").strip().upper()


def measure_python_startup_baseline() -> float:
    """
    Fairness (#5): đo thời gian chỉ để khởi chạy trình thông dịch Python.
    Giá trị này được cộng thêm vào time_limit của từng testcase trước khi chạy
    và trừ ra khỏi execution_time ghi nhận, để con số hiển thị phản ánh mã sinh viên
    thay vì chi phí boot interpreter (tránh TLE oan oải hàng loạt bài Python).
    """
    global _PY_STARTUP_CACHE
    if _PY_STARTUP_CACHE is not None:
        return _PY_STARTUP_CACHE
    value = 0.0
    try:
        res = SandboxRunner.run_process(
            command=[resolve_python_executable(), "-u", "-c", "pass"],
            input_data="",
            time_limit_ms=15000,
            memory_limit_mb=128,
        )
        if res.verdict == "OK":
            value = float(res.execution_time_ms)
    except Exception:
        value = 0.0
    _PY_STARTUP_CACHE = value
    return value


def _cap_field(value: Any) -> str:
    text = "" if value is None else str(value)
    return text[:_EVIDENCE_FIELD_CAP]


def _build_evidence_payload(
    language: str,
    python_baseline_ms: float,
    items: List[Dict[str, Any]]
) -> str:
    """Chứng cứ per-testcase (pain #4): JSON chuẩn được lưu vào cột diff_details."""
    payload = {
        "language": language,
        "python_baseline_ms": round(python_baseline_ms, 2) if _is_python_language(language) else 0.0,
        "items": items,
    }
    return json.dumps(payload, ensure_ascii=False)


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
    total_weight: float,
    python_baseline_ms: float = 0.0
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
    is_py = _is_python_language(language)

    result = {
        "submission_id": submission_id,
        "mssv": mssv,
        "verdict": "RE",
        "score": 0.0,
        "sandbox_score": 0.0,
        "sandbox_ratio": 0.0,
        "language": language,
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
    evidence: List[Dict[str, Any]] = []

    def record_diff(message: str) -> None:
        nonlocal first_diff
        if first_diff is None:
            first_diff = message

    def new_evidence(q_label: str, tc: Dict[str, Any]) -> Dict[str, Any]:
        """One per-testcase evidence row (pain #4): later filled after execution."""
        return {
            "q": q_label,
            "input": _cap_field(tc.get("input_data", "")),
            "expected": _cap_field(tc.get("expected_output", "")),
            "actual": "",
            "stderr": "",
            "verdict": "SKIP",
            "time_ms": 0.0,
            "memory_mb": 0.0,
            "strategy": tc.get("matching_strategy", "EXACT_MATCH"),
            "weight": tc.get("score_weight", 1.0),
            "passed": False,
        }

    if source_root.is_dir():
        # —— Multi-question mode: file bài làm `Q<nn>.<ext>` theo question_number ——
        # CE/TLE/RE của một câu không dừng các câu khác (chỉ RE/TLE dừng vì runtime treo).
        compile_cache: Dict[str, Tuple[bool, str, Optional[str]]] = {}

        for tc in testcases:
            qnum = tc.get("question_number", "Q1")
            qfile = _resolve_question_file(source_root, qnum, language)
            if qfile is None:
                logs.append(f"{qnum}: Không tìm thấy file bài làm trong thư mục sinh viên.")
                entry = new_evidence(str(qnum), tc)
                entry["verdict"] = "CE"
                entry["stderr"] = f"Thiếu file bài làm {qnum} trong thư mục sinh viên."
                evidence.append(entry)
                record_diff(f"({qnum}) Thiếu file bài làm {qnum} trong thư mục sinh viên.")
                worst_verdict = _pick_worse(worst_verdict, "CE")
                continue

            cache_key = str(qfile)
            if cache_key not in compile_cache:
                compile_cache[cache_key] = runner.compile(qfile)
            success, compile_log, exec_target = compile_cache[cache_key]

            if not success or not exec_target:
                logs.append(f"{qnum}: CE - {compile_log or 'Lỗi biên dịch.'}")
                entry = new_evidence(str(qnum), tc)
                entry["verdict"] = "CE"
                entry["stderr"] = _cap_field(compile_log or "Lỗi biên dịch.")
                evidence.append(entry)
                record_diff(f"({qnum}) Lỗi biên dịch: {compile_log or ''}")
                worst_verdict = _pick_worse(worst_verdict, "CE")
                continue

            matching_ctx.set_strategy_by_name(tc.get("matching_strategy", "EXACT_MATCH"))
            # Fairness (#5): Python cộng thêm baseline khởi động interpreter vào time_limit
            base_limit = int(tc.get("time_limit_ms", 1500) or 1500)
            limit_ms = base_limit + (int(python_baseline_ms) if (is_py and python_baseline_ms > 0) else 0)
            res = runner.execute(
                executable_target=exec_target,
                input_data=tc.get("input_data", ""),
                time_limit_ms=limit_ms,
                memory_limit_mb=tc.get("memory_limit_mb", 128)
            )
            # Thời gian hiệu dụng: trừ phần boot interpreter (chỉ áp dụng Python)
            effective_ms = res.execution_time_ms
            if is_py and python_baseline_ms > 0:
                effective_ms = max(0.0, float(res.execution_time_ms) - python_baseline_ms)
            max_exec_time = max(max_exec_time, effective_ms)
            max_mem = max(max_mem, res.memory_used_mb)

            entry = new_evidence(str(qnum), tc)
            entry["time_ms"] = round(effective_ms, 2)
            entry["memory_mb"] = res.memory_used_mb
            evidence.append(entry)

            if res.verdict != "OK":
                # TLE, MLE, or RE stops the run (old semantics preserved)
                worst_verdict = res.verdict
                entry["verdict"] = res.verdict
                entry["actual"] = _cap_field(res.stdout)
                entry["stderr"] = _cap_field(res.stderr or res.error_message)
                record_diff(f"({qnum}) {res.error_message}")
                logs.append(f"{qnum}: dừng sớm ({res.verdict}).")
                break

            match_res = matching_ctx.compare(res.stdout, tc.get("expected_output", ""))
            entry["actual"] = _cap_field(res.stdout)
            entry["verdict"] = "PASS" if match_res.is_matched else "WA"
            entry["passed"] = bool(match_res.is_matched)
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
            # Fairness (#5): Python cộng thêm baseline khởi động interpreter vào time_limit
            base_limit = int(tc.get("time_limit_ms", 1500) or 1500)
            limit_ms = base_limit + (int(python_baseline_ms) if (is_py and python_baseline_ms > 0) else 0)
            res = runner.execute(
                executable_target=exec_target,
                input_data=tc.get("input_data", ""),
                time_limit_ms=limit_ms,
                memory_limit_mb=tc.get("memory_limit_mb", 128)
            )
            effective_ms = res.execution_time_ms
            if is_py and python_baseline_ms > 0:
                effective_ms = max(0.0, float(res.execution_time_ms) - python_baseline_ms)
            max_exec_time = max(max_exec_time, effective_ms)
            max_mem = max(max_mem, res.memory_used_mb)

            entry = new_evidence("", tc)
            entry["time_ms"] = round(effective_ms, 2)
            entry["memory_mb"] = res.memory_used_mb
            evidence.append(entry)

            if res.verdict != "OK":
                # TLE, MLE, or RE stops the whole run (old semantics preserved)
                worst_verdict = res.verdict
                entry["verdict"] = res.verdict
                entry["actual"] = _cap_field(res.stdout)
                entry["stderr"] = _cap_field(res.stderr or res.error_message)
                record_diff(res.error_message)
                break

            match_res = matching_ctx.compare(res.stdout, tc.get("expected_output", ""))
            entry["actual"] = _cap_field(res.stdout)
            entry["verdict"] = "PASS" if match_res.is_matched else "WA"
            entry["passed"] = bool(match_res.is_matched)
            if match_res.is_matched:
                earned_weight += tc.get("score_weight", 1.0)
            else:
                worst_verdict = _pick_worse(worst_verdict, "WA")
                record_diff(match_res.diff_details)
        result["compile_log"] = compile_log

    # Điểm Sandbox (tối đa 5.0) = tỷ lệ testcase PASS * 5.0 (Hybrid: nửa còn lại do AI rubric chấm)
    ratio = (earned_weight / total_weight) if total_weight > 0 else 0.0
    sandbox_score = round(ratio * SANDBOX_MAX_SCORE, 2)
    result.update({
        "verdict": worst_verdict if ratio < 1.0 else "AC",
        "score": sandbox_score,
        "sandbox_ratio": ratio,
        "sandbox_score": sandbox_score,
        "language": language,
        "execution_time_ms": max_exec_time,
        "memory_used_mb": max_mem,
    })
    # Chứng cứ per-testcase (pain #4): JSON chuẩn thay thế diff text rời rạc.
    # Fallback: nếu không có evidence nào (ví dụ CE sớm) giữ nguyên diff text cũ cho UI.
    if evidence:
        result["diff_details"] = _build_evidence_payload(language, python_baseline_ms, evidence)
    else:
        result["diff_details"] = first_diff
    return result


def _kill_process_tree(pid: int) -> None:
    """
    Hủy chấm (#2): terminate worker + toàn bộ tiến trình con của nó (sandbox, compiler,
    tiến trình sinh viên đang chạy). Tránh rơi orphan process khi batch bị hủy giữa đường.
    """
    try:
        import psutil
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            try:
                child.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        try:
            parent.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    except Exception:
        pass


class GradingService:
    """Service orchestrating batch grading for university practical programming exams."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()

    def grade_class_batch(
        self,
        class_id: int,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        max_workers: Optional[int] = None,
        submission_ids: Optional[List[int]] = None,
        cancel_event: Optional[threading.Event] = None,
        enable_ai_quality: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Grades active student submissions for a given class session in parallel.

        Args:
            class_id: Target class session ID
            progress_callback: Optional callable(completed_count, total_count, current_student_mssv)
            max_workers: Optional override for the process pool size (defaults to 4-8)
            submission_ids: Optional whitelist — chỉ chấm các bài này (dùng cho "Chấm Tiếp": resume PENDING).
            cancel_event: Optional threading.Event — khi được set, đợt chấm dừng khỏe ngang:
                bài đang chạy bị terminate hẳn (giữ PENDING), bài chưa chạy bị hủy khỏi queue,
                để lần sau "Chấm Tiếp" chọn đúng các bài còn PENDING.
        """
        # 1. Fetch class info, submissions and testcases
        classes = self.db.get_all_classes()
        class_info = next((c for c in classes if c["id"] == class_id), None)
        if not class_info:
            raise ValueError(f"Không tìm thấy đợt chấm có ID = {class_id}")

        language = class_info.get("programming_language", "C")
        submissions = self.db.get_submissions_by_class(class_id)
        testcases = self.db.get_testcases_by_class(class_id)

        # Resume mode (#2): chỉ chấm lô con được chỉ định
        if submission_ids:
            wanted = {int(sid) for sid in submission_ids}
            submissions = [s for s in submissions if s.get("id") in wanted]

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

        # Hybrid grading (tuỳ chọn): AI rubric chạy trong tiến trình cha vì worker spawn (Windows)
        # không mang theo JWT/ApiClient. Nếu chưa bật, điểm = sandbox quy đổi thang 10 như cũ.
        problem_statement = (
            f"Bài thi thực hành lập trình môn {class_info.get('course_code', '')}"
            f" - lớp {class_info.get('class_name', '')}."
        )
        ai_service = None
        if enable_ai_quality:
            try:
                from services.ai_service import AiService
                ai_service = AiService()
            except Exception:
                ai_service = None

        # Fairness (#5): đo baseline khởi động interpreter một lần cho cả batch (Python only)
        python_baseline_ms = measure_python_startup_baseline() if _is_python_language(language) else 0.0

        # 2. Resolve pool size: honour documented 4-8 workers, bounded by workload
        if max_workers is None:
            cpu = os.cpu_count() or MIN_WORKERS
            max_workers = min(MAX_WORKERS, max(MIN_WORKERS, cpu))
        num_workers = max(1, min(max_workers, total_subs))

        # 3. Dispatch submissions to the worker pool and persist results as they complete.
        #    Dùng executor thủ công (không dùng with) để còn hủy können batch giữa đường bằng
        #    terminate worker processes - future.cancel() là vô dụng vì worker nhặt việc gần như tức thời.
        executor = ProcessPoolExecutor(max_workers=num_workers)
        try:
            future_to_index = {
                executor.submit(
                    grade_single_submission, sub, language, testcases,
                    total_weight, python_baseline_ms
                ): idx
                for idx, sub in enumerate(submissions)
            }

            completed = 0
            cancel_applied = False
            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                sub = submissions[idx]
                try:
                    res = future.result()
                except Exception as ex:
                    if cancel_event is not None and cancel_event.is_set():
                        # Future bị hủy/terminate khi có yêu cầu hủy: giữ PENDING cho lần sau
                        continue
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

                # Hybrid (tuỳ chọn): sandbox xong -> gọi AI rubric trong tiến trình cha.
                # Không bật (hoặc đã yêu cầu hủy): quy đổi sandbox về thang 10 như hành vi cũ.
                if ai_service is not None and not (cancel_event is not None and cancel_event.is_set()):
                    self._enrich_with_ai_quality(
                        res,
                        sub.get("source_file_path"),
                        language,
                        problem_statement,
                        ai_service,
                    )
                else:
                    res["score"] = round(float(res.get("sandbox_score", 0.0)) * 2.0, 1)

                # Lưu kết quả bài vừa hoàn tất (kể cả trong phiên hợp lệ khi yêu cầu hủy đã bật)
                self._save_result(res)
                results[idx] = {
                    "submission_id": res["submission_id"],
                    "mssv": res["mssv"],
                    "verdict": res["verdict"],
                    "score": res["score"],
                }

                completed += 1
                if progress_callback:
                    progress_callback(completed, total_subs, res["mssv"])

                # Cancel propagation (#2): dừng hẳn batch sau khi lưu xong bài đang nắm:
                # - hủy future chưa chạy (cancel_futures=True)
                # - terminate worker đang chạy + cây tiến trình con của nó
                if cancel_event is not None and cancel_event.is_set() and not cancel_applied:
                    cancel_applied = True
                    # Snapshot trước shutdown vì executor._processes triệt tiêu về None sau đó
                    worker_procs = list((getattr(executor, "_processes", None) or {}).values())
                    try:
                        executor.shutdown(wait=False, cancel_futures=True)
                    except Exception:
                        pass
                    for proc in worker_procs:
                        try:
                            if proc.is_alive():
                                _kill_process_tree(proc.pid)
                        except Exception:
                            pass
                    break
        finally:
            try:
                executor.shutdown(wait=not cancel_applied, cancel_futures=True)
            except Exception:
                pass

        return [r for r in results if r is not None]

    def regrade_submission(self, submission_id: int, enable_ai_quality: bool = False) -> Dict[str, Any]:
        """
        Re-grades exactly one submission (UC-15) using the current testcase set:
        compile -> sandbox execute -> strategy compare -> persist fresh result.
        When `enable_ai_quality` is set, the AI rubric (5đ) is also applied in this process.
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
        python_baseline_ms = measure_python_startup_baseline() if _is_python_language(language) else 0.0
        result = grade_single_submission(sub, language, testcases, total_weight, python_baseline_ms)

        if enable_ai_quality:
            try:
                from services.ai_service import AiService
                info = class_info or {}
                problem_statement = (
                    f"Bài thi thực hành lập trình môn {info.get('course_code', '')}"
                    f" - lớp {info.get('class_name', '')}."
                )
                self._enrich_with_ai_quality(result, sub.get("source_file_path"), language, problem_statement, AiService())
            except Exception:
                result["score"] = round(float(result.get("sandbox_score", 0.0)) * 2.0, 1)
        else:
            result["score"] = round(float(result.get("sandbox_score", 0.0)) * 2.0, 1)

        self._save_result(result)
        return result

    def _enrich_with_ai_quality(
        self,
        result: Dict[str, Any],
        source_file_path: Optional[str],
        language: str,
        problem_statement: str,
        ai_service: Any
    ) -> None:
        """
        Adds the AI quality rubric (max 5.0) to a sandbox result and recomputes the total.
        On AI failure the sandbox score is preserved and the rubric is flagged as PENDING,
        so a student is never silently penalized for infrastructure/quota problems.
        """
        sandbox_score = float(result.get("sandbox_score", 0.0) or 0.0)
        quality: Dict[str, Any] = {
            "enabled": True,
            "available": False,
            "pending": True,
            "score": 0.0,
            "max": AI_RUBRIC_MAX_SCORE,
            "sandbox_score": sandbox_score,
            "sandbox_max": SANDBOX_MAX_SCORE,
            "criteria": {},
            "overall_feedback": "",
            "tokens_consumed": 0,
            "message": "Chưa chấm chất lượng bằng AI.",
        }

        source = read_submission_source(source_file_path)
        if not source.strip():
            quality["message"] = "Không đọc được mã nguồn để chấm chất lượng bằng AI."
        else:
            res = ai_service.evaluate_code_quality(source, language, problem_statement)
            if res.get("success"):
                rubric = res.get("rubric") or {}
                criteria: Dict[str, Any] = {}
                passes = 0
                for key in AI_RUBRIC_CRITERIA:
                    item = rubric.get(key) or {}
                    passed = bool(item.get("passed"))
                    criteria[key] = {
                        "label": AI_RUBRIC_LABELS.get(key, key),
                        "passed": passed,
                        "reason": str(item.get("reason", "") or ""),
                    }
                    if passed:
                        passes += 1
                quality.update({
                    "available": True,
                    "pending": False,
                    "score": float(passes),
                    "criteria": criteria,
                    "overall_feedback": str(res.get("overall_feedback", "") or ""),
                    "tokens_consumed": int(res.get("tokens_consumed", 0) or 0),
                    "message": "Đã chấm chất lượng bằng AI.",
                })
            else:
                quality["message"] = res.get("message", "Không thể chấm chất lượng bằng AI.")

        rubric_score = float(quality["score"]) if quality["available"] else 0.0
        result["rubric_score"] = rubric_score
        result["rubric_available"] = bool(quality["available"])
        result["score"] = round(sandbox_score + rubric_score, 1)
        result["diff_details"] = _attach_quality_payload(result.get("diff_details"), quality)

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
