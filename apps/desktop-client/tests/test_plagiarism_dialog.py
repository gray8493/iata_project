"""Hộp thoại Quét Đạo Văn (ui.dialogs.plagiarism_dialog) — phần tách bài theo từng câu.

Trọng tâm: một bài nộp dạng thư mục (nhiều câu Q1/Q2) phải được tách thành từng
câu để so đúng câu với nhau, thay vì gộp cả gói (làm sai lệch điểm tương đồng).
"""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PyQt6")

from ui.dialogs.plagiarism_dialog import PlagiarismDialog
from services.plagiarism_engine import PlagiarismEngine

C_ONE = "#include <stdio.h>\nint main() { printf(\"1\"); return 0; }\n"
C_TWO = "#include <stdio.h>\nint main() { printf(\"2\"); return 0; }\n"


class _StubDb:
    """DB giả: chỉ trả về danh sách testcase (question_number)."""

    def __init__(self, testcases=None, boom=False):
        self._testcases = testcases or []
        self._boom = boom

    def get_testcases_by_class(self, class_id):
        if self._boom:
            raise RuntimeError("db down")
        return self._testcases


def _dialog(db=None) -> PlagiarismDialog:
    """Dựng dialog tối thiểu (bỏ qua __init__ đồ họa) cho các helper thuần logic."""
    dialog = PlagiarismDialog.__new__(PlagiarismDialog)
    dialog.class_id = 1
    dialog.db = db or _StubDb()
    return dialog


# ------------------------------------------------------------------------------
# _class_question_keys
# ------------------------------------------------------------------------------
def test_class_question_keys_dedupes_and_sorts_numerically():
    dialog = _dialog(_StubDb([
        {"question_number": "Q2"},
        {"question_number": "Q1"},
        {"question_number": "Q10"},
        {"question_number": "Q1"},
    ]))
    assert dialog._class_question_keys() == ["Q1", "Q2", "Q10"]


def test_class_question_keys_defaults_blank_question_to_q1():
    dialog = _dialog(_StubDb([{"question_number": "  "}]))
    assert dialog._class_question_keys() == ["Q1"]


def test_class_question_keys_returns_empty_when_db_fails():
    assert _dialog(_StubDb(boom=True))._class_question_keys() == []


# ------------------------------------------------------------------------------
# _collect_question_units
# ------------------------------------------------------------------------------
def test_collect_units_splits_folder_submission_by_question(tmp_path):
    folder = tmp_path / "SE180001"
    folder.mkdir()
    (folder / "Q1.c").write_text(C_ONE, encoding="utf-8")
    (folder / "Q2.c").write_text(C_TWO, encoding="utf-8")

    units = _dialog()._collect_question_units(folder, ["Q1", "Q2"], "C")

    assert set(units) == {"Q1", "Q2"}
    assert "printf(\"1\")" in units["Q1"]
    assert "printf(\"2\")" in units["Q2"]


def test_collect_units_accepts_lowercase_question_file_names(tmp_path):
    folder = tmp_path / "SE180002"
    folder.mkdir()
    (folder / "q1.py").write_text("print('mot')\n", encoding="utf-8")

    units = _dialog()._collect_question_units(folder, ["Q1"], "PYTHON")

    assert set(units) == {"Q1"} and "print('mot')" in units["Q1"]


def test_collect_units_keeps_only_questions_the_student_submitted(tmp_path):
    folder = tmp_path / "SE180003"
    folder.mkdir()
    (folder / "Q2.c").write_text(C_TWO, encoding="utf-8")

    units = _dialog()._collect_question_units(folder, ["Q1", "Q2"], "C")

    assert set(units) == {"Q2"}


def test_collect_units_falls_back_to_whole_folder_when_no_q_file_matches(tmp_path):
    folder = tmp_path / "SE180004"
    folder.mkdir()
    (folder / "main.c").write_text(C_ONE, encoding="utf-8")
    (folder / "utils.c").write_text(C_TWO, encoding="utf-8")

    units = _dialog()._collect_question_units(folder, ["Q1", "Q2"], "C")

    assert set(units) == {"Q1"}
    assert "main.c" in units["Q1"] and "utils.c" in units["Q1"]


def test_collect_units_treats_single_file_submission_as_one_question(tmp_path):
    src = tmp_path / "SE180005_Q1.c"
    src.write_text(C_ONE, encoding="utf-8")

    units = _dialog()._collect_question_units(src, ["Q1", "Q2"], "C")

    assert set(units) == {"Q1"} and units["Q1"] == C_ONE


def test_collect_units_returns_empty_for_missing_path(tmp_path):
    assert _dialog()._collect_question_units(tmp_path / "khong-ton-tai", ["Q1"], "C") == {}


def test_collect_units_returns_empty_for_folder_without_source_code(tmp_path):
    folder = tmp_path / "SE180006"
    folder.mkdir()
    (folder / "readme.txt").write_text("khong phai ma nguon", encoding="utf-8")

    assert _dialog()._collect_question_units(folder, [], "C") == {}


# ------------------------------------------------------------------------------
# Ghép trọn luồng: tách từng câu -> máy quét Winnowing
# ------------------------------------------------------------------------------
Q1_BODY = """#include <stdio.h>
int main() {
    int n; int sum = 0;
    scanf("%d", &n);
    for (int i = 1; i <= n; i++) { sum += i; }
    printf("%d\\n", sum);
    return 0;
}
"""

Q1_BODY_RENAMED = """#include <stdio.h>
int main() {
    int m; int total = 0;
    scanf("%d", &m);
    for (int j = 1; j <= m; j++) { total += j; }   /* doi ten bien */
    printf("%d\\n", total);
    return 0;
}
"""

Q2_FIB = """#include <stdio.h>
int fib(int k) {
    if (k <= 1) { return k; }
    return fib(k - 1) + fib(k - 2);
}
int main() {
    int k;
    scanf("%d", &k);
    printf("%d\\n", fib(k));
    return 0;
}
"""

Q2_WHILE = """#include <stdio.h>
int main() {
    double x;
    scanf("%lf", &x);
    while (x < 1000) { x *= x; }
    printf("%f\\n", x);
    return 0;
}
"""

Q2_SORT = """#include <stdio.h>
int main() {
    int arr[3]; int t;
    for (int i = 0; i < 3; i++) { scanf("%d", &arr[i]); }
    if (arr[0] > arr[1]) { t = arr[0]; arr[0] = arr[1]; arr[1] = t; }
    printf("%d\\n", arr[0]);
    return 0;
}
"""


def test_pipeline_flags_copied_q1_of_folder_submissions(tmp_path):
    """Đúng kịch bản UC-17: chỉ sao chép câu Q1, các câu khác làm khác nhau."""
    layout = {
        "SE180001": {"Q1": Q1_BODY, "Q2": Q2_FIB},
        "SE180002": {"Q1": Q1_BODY_RENAMED, "Q2": Q2_WHILE},
        "SE180003": {"Q1": Q2_WHILE, "Q2": Q2_SORT},
    }
    dialog = _dialog()
    documents = []
    for mssv, answers in layout.items():
        folder = tmp_path / mssv
        folder.mkdir()
        for question, body in answers.items():
            (folder / f"{question}.c").write_text(body, encoding="utf-8")
        units = dialog._collect_question_units(folder, ["Q1", "Q2"], "C")
        assert set(units) == {"Q1", "Q2"}
        documents.append({"mssv": mssv, "units": units})

    report = PlagiarismEngine().scan_class(documents, language="C", threshold=80.0)

    cloned = [
        m for m in report["matches"]
        if {m["sv_a"], m["sv_b"]} == {"SE180001", "SE180002"}
    ]
    assert len(cloned) == 1
    assert cloned[0]["questions"] == ["Q1"]
    assert cloned[0]["sim"] == 100.0
    assert "sum" in cloned[0]["code_a"] and "total" in cloned[0]["code_b"]
