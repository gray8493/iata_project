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
            # Thư mục dữ liệu ghi được: dev = apps/desktop-client/data,
            # frozen = %LOCALAPPDATA%/AITA/data (không dùng _MEIPASS vì bị xóa mỗi lần chạy).
            from core.app_paths import app_data_dir
            self.db_path = str(app_data_dir() / "local_grading.db")
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

            # 1.1 Bảng local_web_sessions (Quản lý phiên chấm Web)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS local_web_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT NOT NULL,
                course_code TEXT NOT NULL,
                class_name TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_deleted INTEGER DEFAULT 0
            );
            """)

            # 2. Bảng local_student_submissions (Danh sách sinh viên nộp bài,
            #    chỉ lưu MSSV theo chuẩn input 2 cột `MSSV,File`)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS local_student_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                student_mssv TEXT NOT NULL,
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

            # 5. Bảng local_plagiarism_reports (Kết quả quét đạo văn 2 vòng)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS local_plagiarism_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                student_a_mssv TEXT NOT NULL,
                student_b_mssv TEXT NOT NULL,
                similarity_percentage REAL NOT NULL,
                question_key TEXT,
                ai_evidence_details TEXT,
                checked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_deleted INTEGER DEFAULT 0,
                deleted_at DATETIME,
                FOREIGN KEY (class_id) REFERENCES local_classes(id) ON DELETE CASCADE
            );
            """)

            # 6. Bảng local_web_submissions (Danh sách sinh viên & link đồ án Web)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS local_web_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
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
                rubric_log TEXT,
                screenshot_path TEXT,
                ai_feedback TEXT,
                graded_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_deleted INTEGER DEFAULT 0,
                FOREIGN KEY (session_id) REFERENCES local_web_sessions(id) ON DELETE CASCADE
            );
            """)

            # Indexes for optimal querying
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_subs_class_id ON local_student_submissions(class_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_subs_mssv ON local_student_submissions(student_mssv);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_sub_id ON local_grading_results(submission_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_web_subs_mssv ON local_web_submissions(mssv);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tc_class_id ON local_test_cases(class_id);")
            # Removed the direct create index call for idx_web_subs_session because it's now handled in _ensure_web_submission_columns()

            conn.commit()

        self._ensure_web_submission_columns()
        self._ensure_plagiarism_columns()
        self._drop_legacy_student_name_column()
        self._ensure_class_columns()
        self._ensure_submission_unique_mssv()

    def _drop_legacy_student_name_column(self):
        """
        Drops the obsolete `student_name` column from local_student_submissions:
        the standard input only carries `MSSV,File`, so names are not persisted.
        Safe for existing local_grading.db files created before this change.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(local_student_submissions)")
            existing = {row[1] for row in cursor.fetchall()}
            if "student_name" not in existing:
                return
            try:
                cursor.execute("ALTER TABLE local_student_submissions DROP COLUMN student_name")
                conn.commit()
            except Exception:
                # SQLite < 3.35 fallback. Old clients would need app schema upgrade via rescan.
                pass

    def _ensure_class_columns(self):
        """
        Lightweight migration for local_classes metadata columns.
        - sessions_dir_path: kept so 'Quét Lại' resolves the last used submissions folder.
        - config_source_class_id: stamp of the class whose testcase config was copied (preset feature).
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(local_classes)")
            existing = {row[1] for row in cursor.fetchall()}
            additions = {
                "submissions_dir_path": "TEXT",
                "config_source_class_id": "INTEGER",
            }
            for column, ddl in additions.items():
                if column not in existing:
                    cursor.execute(f"ALTER TABLE local_classes ADD COLUMN {column} {ddl}")
            conn.commit()

    def _ensure_submission_unique_mssv(self):
        """
        Chốt trùng MSSV trong một đợt chấm ở mức DB:
        - Dọn đợt thuộc lịch sử có 2 bài của cùng MSSV (giữ bài cũ nhất, ẩn các bài sau).
        - Tạo UNIQUE INDEX (class_id, student_mssv) cho các hàng còn hoạt động.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT class_id, student_mssv, COUNT(*) AS n
                FROM local_student_submissions
                WHERE is_deleted = 0
                GROUP BY class_id, student_mssv
                HAVING n > 1
            """)
            for row in cursor.fetchall():
                cursor.execute("""
                    UPDATE local_student_submissions
                    SET is_deleted = 1, deleted_at = CURRENT_TIMESTAMP
                    WHERE is_deleted = 0 AND class_id = ? AND student_mssv = ?
                      AND id > (
                          SELECT MIN(id) FROM local_student_submissions
                          WHERE is_deleted = 0 AND class_id = ? AND student_mssv = ?
                      )
                """, (row["class_id"], row["student_mssv"], row["class_id"], row["student_mssv"]))
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_submissions_class_mssv_active
                ON local_student_submissions (class_id, student_mssv)
                WHERE is_deleted = 0
            """)
            conn.commit()

    def _ensure_web_submission_columns(self):
        """Lightweight migration for folder-import metadata on local_web_submissions."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(local_web_submissions)")
            existing = {row[1] for row in cursor.fetchall()}
            additions = {
                "mode": "TEXT NOT NULL DEFAULT 'HYBRID'",
                "source_folder_path": "TEXT",
                "is_missing": "INTEGER DEFAULT 0",
                "display_mssv": "TEXT",
                "link_file_name": "TEXT",
                "link_changed": "INTEGER DEFAULT 0",
                "rubric_log": "TEXT",
                "screenshot_path": "TEXT",
                "ai_feedback": "TEXT",
                "graded_at": "DATETIME",
                "session_id": "INTEGER",
            }
            for column, ddl in additions.items():
                if column not in existing:
                    cursor.execute(f"ALTER TABLE local_web_submissions ADD COLUMN {column} {ddl}")
            conn.commit()

            # Ensure the index is created AFTER the column exists
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_web_subs_session ON local_web_submissions(session_id);")
            conn.commit()

    def _ensure_plagiarism_columns(self):
        """
        Lightweight migration for `local_plagiarism_reports`.
        - question_key: câu bị trùng (Q1, Q2, ...) khi quét theo từng câu; NULL với
          bản ghi cũ do đợt quét trước chỉ so cả bài.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(local_plagiarism_reports)")
            existing = {row[1] for row in cursor.fetchall()}
            if "question_key" not in existing:
                cursor.execute("ALTER TABLE local_plagiarism_reports ADD COLUMN question_key TEXT")
            if "ai_evidence_json" not in existing:
                cursor.execute("ALTER TABLE local_plagiarism_reports ADD COLUMN ai_evidence_json TEXT")
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

    def count_active_classes_by_name(self, class_name: str) -> int:
        """Số đợt chấm đang hoạt động (is_deleted=0) mang đúng tên này (bỏ qua hoa/thường)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM local_classes "
                "WHERE is_deleted = 0 AND LOWER(TRIM(class_name)) = LOWER(TRIM(?))",
                (class_name,)
            )
            row = cursor.fetchone()
            return int(row[0]) if row else 0

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

    def bulk_insert_submissions(self, submissions: List[Tuple[int, str, str]]) -> int:
        """
        High-performance bulk insertion for student submissions list.
        Tuple format: (class_id, student_mssv, source_file_path)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT OR IGNORE INTO local_student_submissions (
                    class_id, student_mssv, source_file_path
                ) VALUES (?, ?, ?)
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

    def rescan_and_sync_submissions(self, class_id: int, scanned_submissions: List[Dict[str, Any]]) -> Tuple[int, int]:
        """
        Đồng bộ lại danh sách bài nộp từ thư mục mà KHÔNG làm mất điểm của các bài đã chấm.
        scanned_submissions format: List of dicts with `student_mssv` and `source_file_path`.
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

            for item in scanned_submissions:
                mssv = str(item.get("student_mssv", "")).strip()
                filepath = str(item.get("source_file_path", ""))
                if mssv in existing_map:
                    # Đã tồn tại: giữ nguyên điểm số, chỉ cập nhật đường dẫn file nếu thay đổi
                    cursor.execute("""
                        UPDATE local_student_submissions
                        SET source_file_path = ?
                        WHERE id = ?
                    """, (filepath, existing_map[mssv]))
                    existing_count += 1
                else:
                    # Bài nộp mới: thêm mới với trạng thái PENDING
                    cursor.execute("""
                        INSERT INTO local_student_submissions (
                            class_id, student_mssv, source_file_path, status
                        ) VALUES (?, ?, ?, 'PENDING')
                    """, (class_id, mssv, filepath))
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
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    s.id, s.class_id, s.student_mssv, s.source_file_path, s.status,
                    r.calculated_score, r.final_verdict, r.execution_time_ms, r.memory_used_mb,
                    r.compile_log, r.ai_feedback, r.manual_override_score
                FROM local_student_submissions s
                LEFT JOIN local_grading_results r ON s.id = r.submission_id AND r.is_deleted = 0
                WHERE s.class_id = ? AND s.is_deleted = 0
                ORDER BY s.student_mssv ASC
            """, (class_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_submission_by_id(self, submission_id: int) -> Optional[Dict[str, Any]]:
        """Fetches one active submission record (used by single-submission re-grade)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, class_id, student_mssv, source_file_path, status
                FROM local_student_submissions
                WHERE id = ? AND is_deleted = 0
            """, (submission_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

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

    def copy_testcases_from_class(self, source_class_id: int, target_class_id: int) -> int:
        """
        Preset feature (#10): clones the whole active testcase config of one class
        into a newly created class so instructors do not re-enter data every session.
        Returns the number of copied testcases.
        """
        copied = 0
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT question_number, input_data, expected_output, score_weight,
                       time_limit_ms, memory_limit_mb, matching_strategy, is_hidden
                FROM local_test_cases
                WHERE class_id = ? AND is_deleted = 0 ORDER BY id ASC
            """, (source_class_id,))

            rows = cursor.fetchall()
            for row in rows:
                cursor.execute("""
                    INSERT INTO local_test_cases (
                        class_id, question_number, input_data, expected_output,
                        score_weight, time_limit_ms, memory_limit_mb, matching_strategy, is_hidden
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    target_class_id,
                    row["question_number"],
                    row["input_data"],
                    row["expected_output"],
                    row["score_weight"],
                    row["time_limit_ms"],
                    row["memory_limit_mb"],
                    row["matching_strategy"],
                    row["is_hidden"],
                ))
                copied += 1

            cursor.execute("""
                UPDATE local_classes SET config_source_class_id = ? WHERE id = ?
            """, (source_class_id, target_class_id))
            conn.commit()
        return copied

    def get_preset_source_candidates(self) -> List[Dict[str, Any]]:
        """Lists active classes that have at least one testcase (usable as preset source)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.id, c.class_name, c.course_code, c.programming_language,
                       COUNT(t.id) AS testcase_count
                FROM local_classes c
                JOIN local_test_cases t ON t.class_id = c.id AND t.is_deleted = 0
                WHERE c.is_deleted = 0
                GROUP BY c.id, c.class_name, c.course_code, c.programming_language
                ORDER BY c.created_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

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

    def update_ai_feedback(self, submission_id: int, feedback: str):
        """Updates AI pedagogical feedback for a graded submission."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE local_grading_results
                SET ai_feedback = ?
                WHERE submission_id = ? AND is_deleted = 0
            """, (feedback, submission_id))
            conn.commit()

    # ==========================================================================
    # CRUD OPERATIONS FOR PLAGIARISM REPORTS (UC-17)
    # ==========================================================================
    def clear_plagiarism_reports(self, class_id: int):
        """Soft-deletes previous plagiarism reports of a class before a re-scan."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE local_plagiarism_reports
                SET is_deleted = 1, deleted_at = CURRENT_TIMESTAMP
                WHERE class_id = ? AND is_deleted = 0
            """, (class_id,))
            conn.commit()

    def save_plagiarism_report(
        self,
        class_id: int,
        student_a_mssv: str,
        student_b_mssv: str,
        similarity_percentage: float,
        ai_evidence_details: Optional[str] = None,
        question_key: Optional[str] = None,
        ai_evidence_json: Optional[str] = None
    ) -> int:
        """Persists one flagged plagiarism pair into local_plagiarism_reports."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO local_plagiarism_reports (
                    class_id, student_a_mssv, student_b_mssv,
                    similarity_percentage, question_key, ai_evidence_details, ai_evidence_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (class_id, student_a_mssv, student_b_mssv, similarity_percentage,
                  question_key, ai_evidence_details, ai_evidence_json))
            conn.commit()
            if cursor.lastrowid is None:
                raise RuntimeError("Failed to retrieve row ID from local_plagiarism_reports.")
            return cursor.lastrowid

    def update_plagiarism_report_evidence(
        self,
        class_id: int,
        student_a_mssv: str,
        student_b_mssv: str,
        ai_evidence_details: str,
        ai_evidence_json: Optional[str] = None
    ) -> bool:
        """Attaches Stage-2 AI verification evidence to an existing report row."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE local_plagiarism_reports
                SET ai_evidence_details = ?, ai_evidence_json = COALESCE(?, ai_evidence_json)
                WHERE class_id = ? AND is_deleted = 0
                  AND ((student_a_mssv = ? AND student_b_mssv = ?)
                    OR (student_a_mssv = ? AND student_b_mssv = ?))
            """, (ai_evidence_details, ai_evidence_json, class_id,
                  student_a_mssv, student_b_mssv, student_b_mssv, student_a_mssv))
            conn.commit()
            return cursor.rowcount > 0

    def get_plagiarism_reports(self, class_id: int) -> List[Dict[str, Any]]:
        """Fetches all active plagiarism reports for a class, highest similarity first."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM local_plagiarism_reports
                WHERE class_id = ? AND is_deleted = 0
                ORDER BY similarity_percentage DESC
            """, (class_id,))
            return [dict(row) for row in cursor.fetchall()]

    # ==========================================================================
    # CRUD OPERATIONS FOR WEB SESSIONS (NEW)
    # ==========================================================================
    def create_web_session(self, name: str, course_code: str, class_name: str) -> int:
        """Creates a new web grading session."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO local_web_sessions (session_name, course_code, class_name)
                VALUES (?, ?, ?)
            """, (name.strip(), course_code.strip(), class_name.strip()))
            conn.commit()
            return cursor.lastrowid

    def get_all_web_sessions(self) -> List[Dict[str, Any]]:
        """Fetches all active web grading sessions with total submissions count."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, 
                       COUNT(CASE WHEN sub.is_deleted = 0 THEN 1 END) as total_submissions
                FROM local_web_sessions s
                LEFT JOIN local_web_submissions sub ON s.id = sub.session_id
                WHERE s.is_deleted = 0
                GROUP BY s.id
                ORDER BY s.created_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_web_session_by_id(self, session_id: int) -> Optional[Dict[str, Any]]:
        """Fetches a specific active web grading session by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM local_web_sessions WHERE id = ? AND is_deleted = 0", (session_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_latest_web_session(self) -> Optional[Dict[str, Any]]:
        """Fetches the most recent active web grading session if one exists."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM local_web_sessions WHERE is_deleted = 0 ORDER BY created_at DESC, id DESC LIMIT 1")
            row = cursor.fetchone()
            return dict(row) if row else None

    def ensure_default_web_session(self) -> Optional[int]:
        """
        Migrates any legacy web submissions lacking a session_id into an active session
        if one exists, without automatically creating unwanted dummy sessions.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM local_web_sessions WHERE is_deleted = 0 ORDER BY id ASC LIMIT 1")
            existing = cursor.fetchone()
            if not existing:
                return None
            session_id = existing["id"]
            cursor.execute("""
                UPDATE local_web_submissions
                SET session_id = ?
                WHERE session_id IS NULL AND is_deleted = 0
            """, (session_id,))
            conn.commit()
            return session_id

    def delete_web_session(self, session_id: int):
        """Soft-deletes a web session and cascades to its submissions."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE local_web_sessions SET is_deleted = 1 WHERE id = ?", (session_id,))
            cursor.execute("UPDATE local_web_submissions SET is_deleted = 1 WHERE session_id = ?", (session_id,))
            conn.commit()

    # ==========================================================================
    # CRUD OPERATIONS FOR WEB SUBMISSIONS (WEB STUDIO)
    # ==========================================================================
    def get_all_web_submissions(self, session_id: int) -> List[Dict[str, Any]]:
        """Fetches all active web submissions for the specified session."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM local_web_submissions
                WHERE session_id = ? AND is_deleted = 0
                ORDER BY id ASC
            """, (session_id,))
            return [dict(row) for row in cursor.fetchall()]

    def add_web_submission(
        self,
        mssv: str,
        name: str,
        live_url: str = "",
        repo_url: str = "",
        mode: str = "HYBRID",
        course_code: str = "WEB201c",
        class_name: str = "SE1806",
        session_id: Optional[int] = None,
        source_folder_path: Optional[str] = None,
        display_mssv: Optional[str] = None,
        link_file_name: Optional[str] = None
    ) -> int:
        """Adds a single web assignment submission."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO local_web_submissions (
                    course_code, class_name, mssv, name, live_url, repo_url, mode,
                    source_folder_path, display_mssv, link_file_name, session_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (course_code.strip(), class_name.strip(), mssv.strip(), name.strip(), live_url.strip(),
                  repo_url.strip(), mode.strip(), source_folder_path, display_mssv, link_file_name, session_id))
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

    def update_all_web_submissions_mode(
        self,
        course_code: str,
        class_name: str,
        new_mode: str,
        session_id: Optional[int] = None
    ) -> int:
        """Batch updates the grading mode for all existing active submissions in a course/class or session."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if session_id:
                cursor.execute("""
                    UPDATE local_web_submissions
                    SET mode = ?
                    WHERE session_id = ? AND is_deleted = 0
                """, (new_mode.strip(), session_id))
            else:
                cursor.execute("""
                    UPDATE local_web_submissions
                    SET mode = ?
                    WHERE course_code = ? AND class_name = ? AND is_deleted = 0
                """, (new_mode.strip(), course_code, class_name))
            conn.commit()
            return cursor.rowcount

    def update_web_submission_scores(
        self,
        submission_id: int,
        score_dom: float,
        score_lint: float,
        score_e2e: float,
        score_ui: float,
        total_score: float,
        verdict: str = "PENDING",
        rubric_log: Optional[str] = None,
        screenshot_path: Optional[str] = None,
        ai_feedback: Optional[str] = None
    ) -> bool:
        """Updates grading scores (and optional grading evidence) for a web submission."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE local_web_submissions
                SET score_dom = ?, score_lint = ?, score_e2e = ?, score_ui = ?, total_score = ?, verdict = ?,
                    rubric_log = ?, screenshot_path = ?, ai_feedback = ?, graded_at = CURRENT_TIMESTAMP
                WHERE id = ? AND is_deleted = 0
            """, (
                score_dom, score_lint, score_e2e, score_ui, total_score, verdict,
                rubric_log, screenshot_path, ai_feedback, submission_id
            ))
            conn.commit()
            return cursor.rowcount > 0

    def set_web_submission_missing(self, submission_id: int, missing: bool) -> bool:
        """Flags a folder-imported submission whose source folder is no longer on disk (scores preserved)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE local_web_submissions SET is_missing = ? WHERE id = ? AND is_deleted = 0
            """, (1 if missing else 0, submission_id))
            conn.commit()
            return cursor.rowcount > 0

    def update_web_submission_source(
        self,
        submission_id: int,
        source_folder_path: Optional[str],
        display_mssv: Optional[str] = None,
        name: Optional[str] = None,
        live_url: Optional[str] = None,
        repo_url: Optional[str] = None,
        link_file_name: Optional[str] = None,
        link_changed: Optional[bool] = None
    ) -> bool:
        """Refreshes folder-import metadata (path, link file, name/links) after a re-scan."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE local_web_submissions
                SET source_folder_path = COALESCE(?, source_folder_path),
                    display_mssv = COALESCE(?, display_mssv),
                    name = COALESCE(?, name),
                    live_url = COALESCE(?, live_url),
                    repo_url = COALESCE(?, repo_url),
                    link_file_name = COALESCE(?, link_file_name),
                    link_changed = COALESCE(?, link_changed),
                    is_missing = 0
                WHERE id = ? AND is_deleted = 0
            """, (source_folder_path, display_mssv, name, live_url, repo_url, link_file_name,
                  None if link_changed is None else (1 if link_changed else 0), submission_id))
            conn.commit()
            return cursor.rowcount > 0

    def set_web_submission_link_changed(self, submission_id: int, changed: bool) -> bool:
        """Flags a folder-imported submission whose links changed on disk (recommend re-grading)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE local_web_submissions SET link_changed = ? WHERE id = ? AND is_deleted = 0
            """, (1 if changed else 0, submission_id))
            conn.commit()
            return cursor.rowcount > 0


