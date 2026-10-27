"""Acceptance — luồng nghiệp vụ cấp người dùng (AT<NN>_<Module>_TC<nnn>).

Mỗi module kiểm thử đủ 3 nhóm Normal / Boundary / Exception theo rules:
- AT01 SessionWizard: tạo đợt chấm từ thư mục bài nộp (Normal), trùng MSSV
  (Boundary), thư mục rỗng (Exception).
- AT02 GradingWorkflow: chấm toàn bộ đợt + export results.csv chuẩn 7 cột.
- AT03 SessionHistory: kết thúc đợt chấm (soft-delete), dữ liệu kết quả giữ lại.

Qt chạy offscreen; mọi hộp thoại xác nhận được ghi lại thay vì hiển thị thật.
"""
import shutil

import pytest

pytest.importorskip("PyQt6")

from PyQt6.QtWidgets import QDialog, QMessageBox

import ui.dialogs.session_dialog as session_module
from database.db_manager import DatabaseManager
from services.export_service import CSV_COLUMNS, ExportService
from services.grading_service import GradingService
from ui.dialogs.session_dialog import SessionDialog

pytestmark = pytest.mark.acceptance

PY_ECHO = "n = int(input())\nprint(n * 2)\n"
PY_FAIL = "print('Wrong AITA')\n"


@pytest.fixture
def memory_db(monkeypatch):
    """SessionDialog hard-codes DatabaseManager() — redirect về cùng một DB :memory:."""
    db = DatabaseManager(":memory:")
    monkeypatch.setattr(session_module, "DatabaseManager", lambda: db)
    return db


@pytest.fixture
def silent_messages(monkeypatch):
    """Ghi lại hộp thoại xác nhận thay vì hiển thị (tránh treo test offscreen)."""
    calls = []

    def _record(kind):
        def recorder(*args, **kwargs):
            calls.append((kind, args[1] if len(args) > 1 else ""))
            return QMessageBox.StandardButton.Yes
        return recorder

    monkeypatch.setattr(QMessageBox, "warning", _record("warning"))
    monkeypatch.setattr(QMessageBox, "information", _record("information"))
    monkeypatch.setattr(QMessageBox, "question", _record("question"))

    def _fake_exec(self):
        calls.append(("critical", self.windowTitle()))
        return 0

    monkeypatch.setattr(QMessageBox, "exec", _fake_exec)
    return calls


def _session_dialog(folder_path, class_name="SE1801"):
    dlg = SessionDialog()
    dlg.txt_class_name.setText(class_name)
    # setText kích hoạt textChanged -> _scan_and_refresh_preview (đúng luồng thật)
    dlg.txt_folder_path.setText(str(folder_path))
    return dlg


# ---------------------------------------------------------------------------
# AT01 SessionWizard — Normal: tạo đợt chấm từ thư mục bài nộp
# ---------------------------------------------------------------------------
def test_at01_sessionwizard_tc001_create_session_from_folder_scan(
    qapp, memory_db, silent_messages, tmp_path, fixtures_dir
):
    for mssv in ("SE180001", "SE180002"):
        shutil.copyfile(
            fixtures_dir / "submissions" / "sum_correct.c", tmp_path / f"{mssv}.c"
        )

    dlg = _session_dialog(tmp_path)
    assert dlg.table_preview.rowCount() == 2
    assert "Nhận diện được 2 bài nộp hợp lệ" in dlg.lbl_file_count.text()

    dlg._save_session()

    assert silent_messages == []
    assert dlg.result() == QDialog.DialogCode.Accepted
    assert dlg.created_class_id is not None

    classes = memory_db.get_all_classes()
    assert len(classes) == 1
    assert classes[0]["class_name"] == "SE1801"
    assert classes[0]["programming_language"] == "C"
    assert classes[0]["session_folder_path"] == str(tmp_path)

    subs = memory_db.get_submissions_by_class(dlg.created_class_id)
    assert {s["student_mssv"] for s in subs} == {"SE180001", "SE180002"}


# ---------------------------------------------------------------------------
# AT01 SessionWizard — Boundary: trùng MSSV chặn lưu đợt chấm
# ---------------------------------------------------------------------------
def test_at01_sessionwizard_tc002_duplicate_mssv_blocks_save(
    qapp, memory_db, silent_messages, tmp_path, fixtures_dir
):
    shutil.copyfile(
        fixtures_dir / "submissions" / "sum_correct.c", tmp_path / "SE180001.c"
    )
    shutil.copyfile(
        fixtures_dir / "submissions" / "sum_wrong.c", tmp_path / "SE180001_NguyenVanA.c"
    )

    dlg = _session_dialog(tmp_path)
    assert dlg.table_preview.rowCount() == 2
    statuses = [dlg.table_preview.item(r, 4).text() for r in range(2)]
    assert all("Trùng lặp MSSV SE180001" in s for s in statuses)

    dlg._save_session()

    assert any(kind == "critical" and "Trùng Mã Sinh Viên" in title for kind, title in silent_messages)
    assert dlg.result() != QDialog.DialogCode.Accepted
    assert memory_db.get_all_classes() == []


# ---------------------------------------------------------------------------
# AT01 SessionWizard — Exception: thư mục rỗng không tạo đợt chấm
# ---------------------------------------------------------------------------
def test_at01_sessionwizard_tc003_empty_folder_blocks_save(
    qapp, memory_db, silent_messages, tmp_path
):
    dlg = _session_dialog(tmp_path)
    assert dlg.table_preview.rowCount() == 0
    assert "Chưa tìm thấy bài nộp nào" in dlg.lbl_file_count.text()

    dlg._save_session()

    assert any(kind == "warning" and "Không Có Bài Nộp Hợp Lệ" in title for kind, title in silent_messages)
    assert dlg.result() != QDialog.DialogCode.Accepted
    assert memory_db.get_all_classes() == []


# ---------------------------------------------------------------------------
# AT02 GradingWorkflow — Normal: chấm cả đợt + lịch sử + export CSV 7 cột
# ---------------------------------------------------------------------------
def test_at02_gradingworkflow_tc001_grade_batch_and_export_csv(qapp, memory_db, tmp_path):
    from core.app_paths import resolve_python_executable
    try:
        resolve_python_executable()
    except RuntimeError:
        pytest.skip("Không tìm thấy Python — bỏ qua acceptance chấm Python.")

    class_id = memory_db.create_class_session("SE1801_PY_AT", "PHP", "PYTHON", str(tmp_path))
    subs = []
    for mssv, code in (("SE180001", PY_ECHO), ("SE180002", PY_FAIL)):
        src = tmp_path / f"{mssv}_Q1.py"
        src.write_text(code, encoding="utf-8")
        subs.append((class_id, mssv, str(src)))
    memory_db.bulk_insert_submissions(subs)
    for input_data, expected in (("5\n", "10"), ("7\n", "14")):
        memory_db.add_testcase(
            class_id, input_data, expected, score_weight=1.0,
            time_limit_ms=3000, matching_strategy="EXACT_MATCH",
        )

    results = GradingService(memory_db).grade_class_batch(class_id, max_workers=1)
    assert len(results) == 2
    by_mssv = {r["mssv"]: r for r in results}
    assert by_mssv["SE180001"]["verdict"] == "AC"
    assert by_mssv["SE180002"]["verdict"] == "WA"

    # Lịch sử chấm phản ánh đúng số bài đã chấm
    history = memory_db.get_grading_history_summary()
    session_row = next(h for h in history if h["id"] == class_id)
    assert session_row["total_students"] == 2
    assert session_row["graded_students"] == 2
    assert session_row["ac_count"] == 1
    assert session_row["fail_count"] == 1

    # Export chuẩn 7 cột theo AGENTS.md
    rows = ExportService().build_grade_rows(
        memory_db.get_submissions_by_class(class_id), testcase_count=2
    )
    csv_path = tmp_path / "results.csv"
    ExportService().export_csv(rows, str(csv_path))
    lines = csv_path.read_text(encoding="utf-8-sig").splitlines()
    assert lines[0].split(",") == list(CSV_COLUMNS)
    body = "\n".join(lines[1:])
    assert "SE180001" in body and "SE180002" in body
    assert "2/2,AC," in body and "0/2,WA," in body


# ---------------------------------------------------------------------------
# AT03 SessionHistory — Normal: kết thúc đợt chấm (soft-delete giữ kết quả)
# ---------------------------------------------------------------------------
def test_at03_sessionhistory_tc001_end_session_keeps_results(qapp, memory_db, tmp_path):
    class_id = memory_db.create_class_session("SE1801_END", "PRF", "C", str(tmp_path))
    memory_db.bulk_insert_submissions([(class_id, "SE180001", str(tmp_path / "a.c"))])
    sub_id = memory_db.get_submissions_by_class(class_id)[0]["id"]
    memory_db.save_console_grading_result(sub_id, "EXACT_MATCH", 10.0, "AC")

    memory_db.delete_class_session(class_id)

    assert memory_db.get_class_by_id(class_id) is None
    assert memory_db.get_all_classes() == []
    assert all(h["id"] != class_id for h in memory_db.get_grading_history_summary())

    # Kết quả chấm vẫn còn để tra cứu (audit)
    result = memory_db.get_submission_result(sub_id)
    assert result is not None
    assert result["final_verdict"] == "AC"
