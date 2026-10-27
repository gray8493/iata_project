# -*- coding: utf-8 -*-
"""
AITA Desktop Client - Chấm thử 5 trang web chỉ bằng URL (chế độ LIVE_ONLY):

    - Tạo phiên chấm web DEMO_WEB_URL_5 (WEB201c / SE1806)
    - 5 bài nộp giả định, mỗi bài chỉ có Live URL
    - Chấm thật bằng WebRubricEngine (Chromium đóng gói + AI Vision qua AI Gateway)
    - Lưu điểm 4 tiêu chí vào local_web_submissions và in bảng tổng kết

Cách chạy (từ thư mục gốc repo):
    python apps/desktop-client/scripts/seed_web_url_demo.py
"""

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from database.db_manager import DatabaseManager  # noqa: E402
from services.web_rubric_service import WebRubricEngine  # noqa: E402

PURGE_PREFIX = "DEMO_WEB_URL_"
SESSION_NAME = "DEMO_WEB_URL_5"

STUDENTS = [
    ("SE180001", "Nguyen Van An", "https://example.com"),
    ("SE180002", "Tran Thi Binh", "https://www.wikipedia.org"),
    ("SE180003", "Le Minh Chau", "https://news.ycombinator.com"),
    ("SE180004", "Pham Duc Duy", "https://www.python.org"),
    ("SE180005", "Vu Hong Em", "https://developer.mozilla.org/en-US/"),
]


def purge_old_sessions(db: DatabaseManager) -> int:
    purged = 0
    for sess in db.get_all_web_sessions():
        if not str(sess.get("session_name", "")).startswith(PURGE_PREFIX):
            continue
        for sub in db.get_all_web_submissions(int(sess["id"])):
            db.delete_web_submission(int(sub["id"]))
        db.delete_web_session(int(sess["id"]))
        purged += 1
    return purged


def main() -> None:
    db = DatabaseManager()
    purged = purge_old_sessions(db)
    if purged:
        print(f"[purge] Đã xóa {purged} phiên chấm web DEMO_WEB_URL_* cũ.")

    session_id = db.create_web_session(SESSION_NAME, course_code="WEB201c", class_name="SE1806")
    sub_ids = {}
    for mssv, name, url in STUDENTS:
        sub_id = db.add_web_submission(
            mssv=mssv, name=name, live_url=url, mode="LIVE_ONLY",
            course_code="WEB201c", class_name="SE1806", session_id=session_id,
        )
        sub_ids[mssv] = sub_id
    print(f"[seed] Phiên '{SESSION_NAME}' (session_id={session_id}): {len(STUDENTS)} bài nộp, chế độ LIVE_ONLY.\n")

    engine = WebRubricEngine(screenshots_dir=Path("apps/desktop-client/data/web_screenshots"))

    print("=" * 96)
    print(f"{'MSSV':<10} {'URL':<38} {'DOM':>5} {'Lint':>5} {'Func':>5} {'UI':>5} {'Tổng':>6} {'Verdict':<9}")
    print("-" * 96)
    for i, (mssv, _name, url) in enumerate(STUDENTS, 1):
        print(f"[{i}/5] Đang thẩm định {url} ...", flush=True)
        res = engine.grade(live_url=url, mssv=mssv, mode="LIVE_ONLY")
        db.update_web_submission_scores(
            submission_id=sub_ids[mssv],
            score_dom=res.score_dom or 0.0,
            score_lint=res.score_lint or 0.0,
            score_e2e=res.score_func or 0.0,
            score_ui=res.score_ui or 0.0,
            total_score=res.total_score,
            verdict=res.verdict,
            rubric_log=res.rubric_log,
            screenshot_path=res.screenshot_path,
            ai_feedback=res.ai_feedback,
        )
        dom = res.score_dom if res.score_dom is not None else "-"
        lint = res.score_lint if res.score_lint is not None else "-"
        func = res.score_func if res.score_func is not None else "-"
        ui = res.score_ui if res.score_ui is not None else "-"
        dom_s = f"{dom:>5}" if isinstance(dom, float) else f"{dom:>5}"
        lint_s = f"{lint:>5}" if isinstance(lint, float) else f"{lint:>5}"
        func_s = f"{func:>5}" if isinstance(func, float) else f"{func:>5}"
        ui_s = f"{ui:>5}" if isinstance(ui, float) else f"{ui:>5}"
        print(f"{mssv:<10} {url:<38} {dom_s} {lint_s} {func_s} {ui_s} {res.total_score:>6.2f} {res.verdict:<9}")
        if res.error:
            print(f"           Lỗi: {res.error}")
        if res.ui_error:
            print(f"           AI Vision: {res.ui_error}")
        print()
    print("=" * 96)
    print("Xem kết quả trong app: Chấm Bài Tập & Đồ Án Web > phiên 'DEMO_WEB_URL_5'.")


if __name__ == "__main__":
    main()
