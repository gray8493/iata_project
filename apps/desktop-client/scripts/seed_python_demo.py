# -*- coding: utf-8 -*-
"""
AITA Desktop Client - Seeding bộ demo chấm (Python / C / Java, 1 đợt mỗi ngôn ngữ, 5 câu hỏi):

    submissions/<Lang>_Demo/SE180001..005/Q1..Q5.<ext>   (mỗi SV 1 thư mục con, mỗi câu 1 file)
    submissions/<Lang>_Demo/testcases_<lang>_demo.json   (25 testcase: Q1..Q5 x 5)

Quy ước bài nộp giống PRF192_Sample / PHP_Sample: main() có sẵn,
sinh viên chỉ viết hàm con. Chế độ chấm multi-question: source_file_path
trỏ vào THƯ MỤC sinh viên; mỗi testcase tự ánh xạ file `Q<nn>` của câu đó
theo question_number (grade_single_submission).

Cách chạy (từ thư mục gốc repo):
    python apps/desktop-client/scripts/seed_python_demo.py

Script làm sạch (purge) các đợt DEMO_PY_*, DEMO_C_*, DEMO_JAVA_* cũ rồi nạp lại từ đầu.
"""

import json
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from database.db_manager import DatabaseManager  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]
DEMO_ROOTS = {
    "Python": REPO_ROOT / "submissions" / "Python_Demo",
    "C": REPO_ROOT / "submissions" / "C_Demo",
    "Java": REPO_ROOT / "submissions" / "Java_Demo",
}
DEMO_PURGE_PREFIXES = ("DEMO_PY_", "DEMO_C_", "DEMO_JAVA_")


def purge_old_demo_sessions(db: DatabaseManager) -> int:
    """Soft-deletes every active DEMO_* class, its testcases and submissions."""
    purged = 0
    for cls in db.get_all_classes():
        if not any(str(cls.get("class_name", "")).startswith(p) for p in DEMO_PURGE_PREFIXES):
            continue
        for tc_row in db.get_testcases_by_class(int(cls["id"])):
            db.delete_testcase(int(tc_row["id"]))
        db.delete_class_session(int(cls["id"]))
        purged += 1
    return purged


def seed_one_language(db: DatabaseManager, lang: str, spec_path: Path) -> None:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    demo_dir = spec_path.parent

    language = spec.get("language", lang)
    class_name = spec.get("class_name", f"DEMO_{lang.upper()}_5CAU")

    class_id = db.create_class_session(
        class_name=class_name,
        course_code=language,
        programming_language=language,
        folder_path=str(demo_dir),
        csv_path="",
    )

    n_tc = 0
    for q in spec["questions"]:
        for tcase in q["testcases"]:
            db.add_testcase(
                class_id=class_id,
                input_data=tcase["input_data"],
                expected_output=tcase["expected_output"],
                score_weight=float(tcase.get("score_weight", 1.0)),
                time_limit_ms=int(tcase.get("time_limit_ms", 1000)),
                memory_limit_mb=int(tcase.get("memory_limit_mb", 128)),
                matching_strategy=tcase.get("matching_strategy", "EXACT_MATCH"),
                question_number=tcase.get("question_number", "Q1"),
            )
            n_tc += 1

    items = []
    for s in spec["students"]:
        folder = demo_dir / s["mssv"]
        if folder.is_dir():
            # path trỏ vào THƯ MỤC sinh viên -> bật chế độ chấm multi-question
            items.append((class_id, s["mssv"], str(folder)))
    if items:
        db.bulk_insert_submissions(items)

    n_sub = len(db.get_submissions_by_class(class_id))
    print(f"[OK] {class_name}: {n_tc} testcase (5 câu x 5), {n_sub} bài nộp "
          f"(class_id={class_id}, chế độ multi-question)")


def iter_specs():
    for lang, root in DEMO_ROOTS.items():
        spec_path = root / ("testcases_%s_demo.json" % lang.lower())
        if spec_path.is_file():
            yield lang, spec_path


def main() -> None:
    db = DatabaseManager()

    purged = purge_old_demo_sessions(db)
    if purged:
        print(f"Đã xóa {purged} đợt chấm DEMO_* cũ (kết quả cũ bị đánh dấu ẩn).")

    for lang, spec_path in iter_specs():
        seed_one_language(db, lang, spec_path)


if __name__ == "__main__":
    main()
