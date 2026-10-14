"""
AITA Desktop Client - Local SQLite Database Manager (PyQt6 Client)
Manages local_grading.db conforming 100% to docs/architecture/database_schema.md.
Features:
- High performance WAL mode (PRAGMA journal_mode = WAL)
- Full Foreign Key enforcement (PRAGMA foreign_keys = ON)
- Strict SQLite Typing & Indexing
- Independent tables for Console Grading and Web Grading
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple


class DatabaseManager:
    """Singleton-ready SQLite Database Manager for AITA Desktop Client."""

    def __init__(self, db_path: Optional[str] = None):
        self._mem_conn = None
        if db_path is None:
            # Default to local app storage directory
            data_dir = Path(__file__).resolve().parent.parent.parent / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = str(data_dir / "local_grading.db")
        else:
            self.db_path = db_path
            if self.db_path == ":memory:":
                self._mem_conn = sqlite3.connect(":memory:")
                self._mem_conn.row_factory = sqlite3.Row
            
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Returns a configured SQLite connection with row factory and WAL mode enabled."""
        if self._mem_conn is not None:
            return self._mem_conn
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA mmap_size = 268435456;")  # 256MB memory-mapped I/O
        return conn

    def _init_db(self):
        """Initializes all local tables according to database_schema.md specifications."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Bảng local_classes (Đợt chấm bài / Lớp học)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS local_classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_name TEXT NOT NULL,
                course_code TEXT NOT NULL,
                programming_language TEXT NOT NULL DEFAULT 'C',
                session_folder_path TEXT NOT NULL,
                students_csv_path TEXT,
                total_submissions INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_deleted INTEGER DEFAULT 0,
                deleted_at DATETIME
            );
            """)

            # 2. Bảng local_student_submissions (Danh sách sinh viên nộp bài)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS local_student_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                student_mssv TEXT NOT NULL,
                student_name TEXT,
                source_file_path TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_deleted INTEGER DEFAULT 0,
                deleted_at DATETIME,
                FOREIGN KEY (class_id) REFERENCES local_classes(id) ON DELETE CASCADE
            );
            """)

            # 3. Bảng local_test_cases (Bộ testcase câu hỏi bài thi)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS local_test_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                question_number TEXT NOT NULL DEFAULT 'Q1',
                input_data TEXT NOT NULL,
                expected_output TEXT NOT NULL,
                score_weight REAL NOT NULL DEFAULT 1.0,
                time_limit_ms INTEGER NOT NULL DEFAULT 1000,
                memory_limit_mb INTEGER NOT NULL DEFAULT 128,
                matching_strategy TEXT NOT NULL DEFAULT 'EXACT_MATCH',
                is_hidden INTEGER DEFAULT 0,
                is_deleted INTEGER DEFAULT 0,
                deleted_at DATETIME,
                FOREIGN KEY (class_id) REFERENCES local_classes(id) ON DELETE CASCADE
            );
            """)

            # 4. Bảng local_grading_results (Kết quả chấm Console: C/Java/Python)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS local_grading_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id INTEGER NOT NULL,
                matching_strategy TEXT NOT NULL,
                calculated_score REAL NOT NULL DEFAULT 0.0,
                final_verdict TEXT NOT NULL,
                execution_time_ms REAL DEFAULT 0.0,
                memory_used_mb REAL DEFAULT 0.0,
                compile_log TEXT,
                diff_details TEXT,
                ai_feedback TEXT,
                manual_override_score REAL,
                manual_override_reason TEXT,
                graded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_deleted INTEGER DEFAULT 0,
                deleted_at DATETIME,
                FOREIGN KEY (submission_id) REFERENCES local_student_submissions(id) ON DELETE CASCADE
            );
            """)

            # 5. Bảng local_web_grading_results (Kết quả chấm Web riêng biệt)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS local_web_grading_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id INTEGER NOT NULL,
                website_url TEXT,
                github_url TEXT,
                grading_mode TEXT NOT NULL DEFAULT 'HYBRID',
                entrypoint_file TEXT NOT NULL DEFAULT 'index.html',
                score_dom REAL NOT NULL DEFAULT 0.0,
                score_lint REAL NOT NULL DEFAULT 0.0,
                score_func REAL NOT NULL DEFAULT 0.0,
                score_ui REAL NOT NULL DEFAULT 0.0,
                final_score REAL NOT NULL DEFAULT 0.0,
                final_verdict TEXT NOT NULL,
                screenshot_path TEXT,
                rubric_log TEXT,
                ai_feedback TEXT,
                graded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_deleted INTEGER DEFAULT 0,
                deleted_at DATETIME,
                FOREIGN KEY (submission_id) REFERENCES local_student_submissions(id) ON DELETE CASCADE
            );
            """)

            # 6. Bảng local_plagiarism_reports (Kết quả quét đạo văn 2 vòng)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS local_plagiarism_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                student_a_mssv TEXT NOT NULL,
                student_b_mssv TEXT NOT NULL,
                similarity_percentage REAL NOT NULL,
                ai_evidence_details TEXT,
                checked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_deleted INTEGER DEFAULT 0,
                deleted_at DATETIME,
                FOREIGN KEY (class_id) REFERENCES local_classes(id) ON DELETE CASCADE
            );
            """)

            # 7. Bảng local_web_submissions (Danh sách sinh viên & link đồ án Web)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS local_web_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_code TEXT NOT NULL DEFAULT 'WEB201c',
                class_name TEXT NOT NULL DEFAULT 'SE1806',
                mssv TEXT NOT NULL,
                name TEXT NOT NULL,
                live_url TEXT,
                repo_url TEXT,
                mode TEXT NOT NULL DEFAULT 'HYBRID',
                score_dom REAL,
                score_lint REAL,
                score_e2e REAL,
                score_ui REAL,
                total_score REAL,
                verdict TEXT DEFAULT 'PENDING',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_deleted INTEGER DEFAULT 0
            );
            """)

            # Indexes for optimal querying
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_subs_class_id ON local_student_submissions(class_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_subs_mssv ON local_student_submissions(student_mssv);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_sub_id ON local_grading_results(submission_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_web_results_sub_id ON local_web_grading_results(submission_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_web_subs_mssv ON local_web_submissions(mssv);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tc_class_id ON local_test_cases(class_id);")
            
            conn.commit()

    # ==========================================================================
    # CRUD OPERATIONS FOR SESSIONS & SUBMISSIONS
    # ==========================================================================
    def create_class_session(
        self,
        class_name: str,
        course_code: str,
        programming_language: str,
        folder_path: str,
        csv_path: Optional[str] = None
    ) -> int:
        """Creates a new grading session record and returns its ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO local_classes (
                    class_name, course_code, programming_language, session_folder_path, students_csv_path
                ) VALUES (?, ?, ?, ?, ?)
            """, (class_name, course_code, programming_language, folder_path, csv_path))
            conn.commit()
            if cursor.lastrowid is None:
                raise RuntimeError("Failed to retrieve row ID from local_classes.")
            return cursor.lastrowid

    def get_all_classes(self) -> List[Dict[str, Any]]:
        """Fetches all active (non-deleted) grading sessions."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM local_classes WHERE is_deleted = 0 ORDER BY created_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_class_by_id(self, class_id: int) -> Optional[Dict[str, Any]]:
        """Fetches a specific class session by its ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM local_classes WHERE id = ? AND is_deleted = 0
            """, (class_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_class_session(
        self,
        class_id: int,
        class_name: str,
        course_code: str,
        programming_language: str,
        folder_path: str,
        csv_path: Optional[str] = None
    ) -> bool:
        """Updates an existing class session record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE local_classes
                SET class_name = ?, course_code = ?, programming_language = ?, session_folder_path = ?, students_csv_path = ?
                WHERE id = ? AND is_deleted = 0
            """, (class_name, course_code, programming_language, folder_path, csv_path, class_id))
            conn.commit()
            return cursor.rowcount > 0

    def get_grading_history_summary(self) -> List[Dict[str, Any]]:
        """
        Retrieves comprehensive grading history for all classes:
        Class name, Course code, Language, Submissions count, Graded count, AC count, Fail count, Average score.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    c.id, c.class_name, c.course_code, c.programming_language, 
                    c.session_folder_path, c.students_csv_path, c.created_at,
                    COUNT(s.id) as total_students,
                    COUNT(r.id) as graded_students,
                    SUM(CASE WHEN r.final_verdict = 'AC' THEN 1 ELSE 0 END) as ac_count,
                    SUM(CASE WHEN r.final_verdict IN ('WA', 'TLE', 'MLE', 'CE', 'RE') THEN 1 ELSE 0 END) as fail_count,
                    AVG(COALESCE(r.manual_override_score, r.calculated_score)) as avg_score
                FROM local_classes c
                LEFT JOIN local_student_submissions s ON c.id = s.class_id AND s.is_deleted = 0
                LEFT JOIN local_grading_results r ON s.id = r.submission_id AND r.is_deleted = 0
                WHERE c.is_deleted = 0
                GROUP BY c.id
                ORDER BY c.created_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def delete_class_session(self, class_id: int):
        """Soft-deletes a grading session and cascades to its submissions."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE local_classes SET is_deleted = 1, deleted_at = CURRENT_TIMESTAMP WHERE id = ?
            """, (class_id,))
            cursor.execute("""
                UPDATE local_student_submissions SET is_deleted = 1, deleted_at = CURRENT_TIMESTAMP WHERE class_id = ?
            """, (class_id,))
            conn.commit()

    def bulk_insert_submissions(self, submissions: List[Tuple[int, str, Optional[str], str]]) -> int:
        """
        High-performance bulk insertion for student submissions list.
        Tuple format: (class_id, student_mssv, student_name, source_file_path)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT INTO local_student_submissions (
                    class_id, student_mssv, student_name, source_file_path
                ) VALUES (?, ?, ?, ?)
            """, submissions)
            
            # Update class total submissions count
            if submissions:
                class_id = submissions[0][0]
                cursor.execute("""
                    UPDATE local_classes SET total_submissions = (
                        SELECT COUNT(*) FROM local_student_submissions WHERE class_id = ? AND is_deleted = 0
                    ) WHERE id = ?
                """, (class_id, class_id))
                
            conn.commit()
            return len(submissions)

    def rescan_and_sync_submissions(
        self,
        class_id: int,
        scanned_submissions: List[Tuple[str, Optional[str], str]]
    ) -> Tuple[int, int]:
        """
        Đồng bộ lại danh sách bài nộp từ thư mục mà KHÔNG làm mất điểm của các bài đã chấm.
        scanned_submissions format: List of (student_mssv, student_name, source_file_path)
        Returns:
            (added_count, existing_count)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, student_mssv FROM local_student_submissions
                WHERE class_id = ? AND is_deleted = 0
            """, (class_id,))
            existing_map = {row["student_mssv"]: row["id"] for row in cursor.fetchall()}

            added_count = 0
            existing_count = 0

            for mssv, name, filepath in scanned_submissions:
                if mssv in existing_map:
                    # Đã tồn tại: giữ nguyên điểm số, chỉ cập nhật đường dẫn file nếu thay đổi
                    cursor.execute("""
                        UPDATE local_student_submissions
                        SET source_file_path = ?, student_name = COALESCE(?, student_name)
                        WHERE id = ?
                    """, (filepath, name, existing_map[mssv]))
                    existing_count += 1
                else:
                    # Bài nộp mới: thêm mới với trạng thái PENDING
                    cursor.execute("""
                        INSERT INTO local_student_submissions (
                            class_id, student_mssv, student_name, source_file_path, status
                        ) VALUES (?, ?, ?, ?, 'PENDING')
                    """, (class_id, mssv, name, filepath))
                    added_count += 1

            # Cập nhật tổng số bài nộp trong local_classes
            cursor.execute("""
                UPDATE local_classes SET total_submissions = (
                    SELECT COUNT(*) FROM local_student_submissions WHERE class_id = ? AND is_deleted = 0
                ) WHERE id = ?
            """, (class_id, class_id))
            conn.commit()

            return added_count, existing_count

    def get_submissions_by_class(self, class_id: int) -> List[Dict[str, Any]]:
        """Retrieves all student submissions with their current grading verdict."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    s.id, s.class_id, s.student_mssv, s.student_name, s.source_file_path, s.status,
                    r.calculated_score, r.final_verdict, r.execution_time_ms, r.memory_used_mb,
                    r.compile_log, r.ai_feedback, r.manual_override_score
                FROM local_student_submissions s
                LEFT JOIN local_grading_results r ON s.id = r.submission_id AND r.is_deleted = 0
                WHERE s.class_id = ? AND s.is_deleted = 0
                ORDER BY s.student_mssv ASC
            """, (class_id,))
            return [dict(row) for row in cursor.fetchall()]

    # ==========================================================================
    # CRUD OPERATIONS FOR TESTCASES
    # ==========================================================================
    def add_testcase(
        self,
        class_id: int,
        input_data: str,
        expected_output: str,
        score_weight: float = 1.0,
        time_limit_ms: int = 1000,
        memory_limit_mb: int = 128,
        matching_strategy: str = "EXACT_MATCH",
        question_number: str = "Q1"
    ) -> int:
        """Adds a testcase to a grading session."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO local_test_cases (
                    class_id, question_number, input_data, expected_output,
                    score_weight, time_limit_ms, memory_limit_mb, matching_strategy
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (class_id, question_number, input_data, expected_output, score_weight, time_limit_ms, memory_limit_mb, matching_strategy))
            conn.commit()
            if cursor.lastrowid is None:
                raise RuntimeError("Failed to retrieve row ID from local_test_cases.")
            return cursor.lastrowid

    def get_testcases_by_class(self, class_id: int) -> List[Dict[str, Any]]:
        """Fetches all testcases configured for a grading session."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM local_test_cases WHERE class_id = ? AND is_deleted = 0 ORDER BY id ASC
            """, (class_id,))
            return [dict(row) for row in cursor.fetchall()]

    def update_class_matching_strategy(self, class_id: int, strategy: str):
        """Updates the default matching strategy for all active testcases of a class session."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE local_test_cases 
                SET matching_strategy = ? 
                WHERE class_id = ? AND is_deleted = 0
            """, (strategy, class_id))
            conn.commit()

    def update_testcase(
        self,
        testcase_id: int,
        question_number: str,
        input_data: str,
        expected_output: str,
        score_weight: float = 1.0,
        time_limit_ms: int = 1000,
        memory_limit_mb: int = 128
    ) -> bool:
        """Updates an existing testcase."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE local_test_cases
                SET question_number = ?, input_data = ?, expected_output = ?,
                    score_weight = ?, time_limit_ms = ?, memory_limit_mb = ?
                WHERE id = ? AND is_deleted = 0
            """, (question_number.strip(), input_data, expected_output, score_weight, time_limit_ms, memory_limit_mb, testcase_id))
            conn.commit()
            return cursor.rowcount > 0

    def delete_testcase(self, testcase_id: int) -> bool:
        """Soft-deletes a testcase."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE local_test_cases
                SET is_deleted = 1, deleted_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (testcase_id,))
            conn.commit()
            return cursor.rowcount > 0

    # ==========================================================================
    # CRUD OPERATIONS FOR GRADING RESULTS (CONSOLE & WEB)
    # ==========================================================================
    def save_console_grading_result(
        self,
        submission_id: int,
        matching_strategy: str,
        calculated_score: float,
        final_verdict: str,
        execution_time_ms: float = 0.0,
        memory_used_mb: float = 0.0,
        compile_log: Optional[str] = None,
        diff_details: Optional[str] = None,
        ai_feedback: Optional[str] = None
    ) -> int:
        """Saves or updates console execution result."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO local_grading_results (
                    submission_id, matching_strategy, calculated_score, final_verdict,
                    execution_time_ms, memory_used_mb, compile_log, diff_details, ai_feedback
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (submission_id, matching_strategy, calculated_score, final_verdict, execution_time_ms, memory_used_mb, compile_log, diff_details, ai_feedback))
            
            # Update submission status
            cursor.execute("UPDATE local_student_submissions SET status = ? WHERE id = ?", (final_verdict, submission_id))
            conn.commit()
            if cursor.lastrowid is None:
                raise RuntimeError("Failed to retrieve row ID from local_grading_results.")
            return cursor.lastrowid

    def save_web_grading_result(
        self,
        submission_id: int,
        grading_mode: str,
        score_dom: float,
        score_lint: float,
        score_func: float,
        score_ui: float,
        final_score: float,
        final_verdict: str,
        website_url: Optional[str] = None,
        github_url: Optional[str] = None,
        screenshot_path: Optional[str] = None,
        rubric_log: Optional[str] = None,
        ai_feedback: Optional[str] = None
    ) -> int:
        """Saves or updates independent web assignment grading result."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO local_web_grading_results (
                    submission_id, website_url, github_url, grading_mode,
                    score_dom, score_lint, score_func, score_ui, final_score,
                    final_verdict, screenshot_path, rubric_log, ai_feedback
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                submission_id, website_url, github_url, grading_mode,
                score_dom, score_lint, score_func, score_ui, final_score,
                final_verdict, screenshot_path, rubric_log, ai_feedback
            ))
            
            cursor.execute("UPDATE local_student_submissions SET status = ? WHERE id = ?", (final_verdict, submission_id))
            conn.commit()
            if cursor.lastrowid is None:
                raise RuntimeError("Failed to retrieve row ID from local_web_grading_results.")
            return cursor.lastrowid

    def override_submission_score(
        self,
        submission_id: int,
        new_score: float,
        reason: str
    ):
        """Overrides submission score manually by instructor."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM local_grading_results WHERE submission_id = ? AND is_deleted = 0", (submission_id,))
            row = cursor.fetchone()
            if row:
                cursor.execute("""
                    UPDATE local_grading_results 
                    SET calculated_score = ?, manual_override_score = ?, manual_override_reason = ?
                    WHERE submission_id = ?
                """, (new_score, new_score, reason, submission_id))
            else:
                cursor.execute("""
                    INSERT INTO local_grading_results (
                        submission_id, matching_strategy, calculated_score, final_verdict,
                        manual_override_score, manual_override_reason
                    ) VALUES (?, 'MANUAL_OVERRIDE', ?, 'MANUAL_OVERRIDE', ?, ?)
                """, (submission_id, new_score, new_score, reason))
            cursor.execute("UPDATE local_student_submissions SET status = 'OVERRIDDEN' WHERE id = ?", (submission_id,))
            conn.commit()

    def get_submission_result(self, submission_id: int) -> Optional[Dict[str, Any]]:
        """Gets grading result details for a specific submission."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM local_grading_results WHERE submission_id = ? AND is_deleted = 0 ORDER BY id DESC LIMIT 1
            """, (submission_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    # ==========================================================================
    # CRUD OPERATIONS FOR WEB SUBMISSIONS (WEB STUDIO)
    # ==========================================================================
    def get_all_web_submissions(self, course_code: str = "WEB201c", class_name: str = "SE1806") -> List[Dict[str, Any]]:
        """Fetches all active web submissions for the specified course and class."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM local_web_submissions 
                WHERE course_code = ? AND class_name = ? AND is_deleted = 0
                ORDER BY id ASC
            """, (course_code, class_name))
            return [dict(row) for row in cursor.fetchall()]

    def add_web_submission(
        self,
        mssv: str,
        name: str,
        live_url: str = "",
        repo_url: str = "",
        mode: str = "HYBRID",
        course_code: str = "WEB201c",
        class_name: str = "SE1806"
    ) -> int:
        """Adds a single web assignment submission."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO local_web_submissions (
                    course_code, class_name, mssv, name, live_url, repo_url, mode
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (course_code, class_name, mssv.strip(), name.strip(), live_url.strip(), repo_url.strip(), mode.strip()))
            conn.commit()
            if cursor.lastrowid is None:
                raise RuntimeError("Failed to retrieve row ID from local_web_submissions.")
            return cursor.lastrowid

    def update_web_submission(
        self,
        submission_id: int,
        mssv: str,
        name: str,
        live_url: str = "",
        repo_url: str = "",
        mode: str = "HYBRID"
    ) -> bool:
        """Updates an existing web assignment submission."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE local_web_submissions
                SET mssv = ?, name = ?, live_url = ?, repo_url = ?, mode = ?
                WHERE id = ? AND is_deleted = 0
            """, (mssv.strip(), name.strip(), live_url.strip(), repo_url.strip(), mode.strip(), submission_id))
            conn.commit()
            return cursor.rowcount > 0

    def delete_web_submission(self, submission_id: int) -> bool:
        """Soft-deletes a web assignment submission."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE local_web_submissions
                SET is_deleted = 1
                WHERE id = ?
            """, (submission_id,))
            conn.commit()
            return cursor.rowcount > 0

    def update_web_submission_scores(
        self,
        submission_id: int,
        score_dom: float,
        score_lint: float,
        score_e2e: float,
        score_ui: float,
        total_score: float,
        verdict: str = "PASSED"
    ) -> bool:
        """Updates grading scores for a web submission."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE local_web_submissions
                SET score_dom = ?, score_lint = ?, score_e2e = ?, score_ui = ?, total_score = ?, verdict = ?
                WHERE id = ? AND is_deleted = 0
            """, (score_dom, score_lint, score_e2e, score_ui, total_score, verdict, submission_id))
            conn.commit()
            return cursor.rowcount > 0


