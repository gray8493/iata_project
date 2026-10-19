# -*- coding: utf-8 -*-
"""
AITA Desktop Client - Script test AI Hub (chạy tay, không cần mở GUI).

Mục đích: kiểm tra nhanh đường ống AI thật (login -> JWT -> Central Backend AI Gateway)
để trả lời câu hỏi "vì sao AI không dùng được" mà không phải chấm cả lớp.

Nó tái sử dụng đúng các client mà app desktop dùng:
    services.api_client.ApiClient   (chọn backend + timeout)
    services.auth_service.AuthService
    services.ai_service.AiService

Cách chạy (từ thư mục gốc repo):

    # 1) Chỉ kiểm tra kết nối + hạn ngạch
    python apps/desktop-client/scripts/test_ai.py --username teacher_an --password 'Abc12345' --feature quota

    # 2) Chấm thử rubric PE (mặc định) bằng code mẫu có sẵn
    python apps/desktop-client/scripts/test_ai.py --username teacher_an --password 'Abc12345'

    # 3) Chấm rubric PE từ file/thư mục bài nộp thật
    python apps/desktop-client/scripts/test_ai.py -u teacher_an -p 'Abc12345' \
        --file E:\\AITA\\submissions\\Java_Demo\\SE180001 --language JAVA

    # 4) Smoke test nhiều tính năng
    python apps/desktop-client/scripts/test_ai.py -u teacher_an -p 'Abc12345' --feature all

Có thể đặt biến môi trường thay cho tham số:
    AITA_USERNAME, AITA_PASSWORD, AITA_BACKEND_URL, AITA_AI_TIMEOUT

Mã thoát: 0 = mọi kiểm tra đã chọn đều thành công; 1 = có kiểm tra thất bại.
"""

import argparse
import os
import sys
import time
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from services.api_client import ApiClient  # noqa: E402
from services.auth_service import AuthService  # noqa: E402
from services.ai_service import AiService, AI_REQUEST_TIMEOUT  # noqa: E402

OK = "[PASS]"
BAD = "[FAIL]"
INFO = "[INFO]"


SAMPLES = {
    "C": (
        "#include <stdio.h>\n"
        "int main(){\n"
        "  int a,b; scanf(\"%d %d\",&a,&b);\n"
        "  int s=a+b; printf(\"%d\",s);\n"
        "  return 0;\n"
        "}\n"
    ),
    "JAVA": (
        "import java.util.Scanner;\n"
        "public class Main {\n"
        "  public static void main(String[] args){\n"
        "    Scanner sc=new Scanner(System.in);\n"
        "    int a=sc.nextInt(), b=sc.nextInt();\n"
        "    System.out.println(a+b);\n"
        "  }\n"
        "}\n"
    ),
    "PYTHON": (
        "def Add(a, b):\n"
        "    return a + b\n\n"
        "if __name__ == \"__main__\":\n"
        "    x, y = map(int, input().split())\n"
        "    print(Add(x, y))\n"
    ),
    "PHP": (
        "<?php\n"
        "$parts = explode(\" \", trim(fgets(STDIN)));\n"
        "$a = (int)$parts[0]; $b = (int)$parts[1];\n"
        "echo $a + $b;\n"
    ),
}

DEFAULT_PROBLEM = "Đọc hai số nguyên a, b từ stdin và in ra tổng a + b."


def _resolve_source(args) -> str:
    """Đọc mã nguồn cần chấm: ưu tiên --file (file hoặc thư mục bài nộp), else code mẫu."""
    if args.file:
        from services.grading_service import read_submission_source  # noqa: E402
        source = read_submission_source(args.file)
        if not source.strip():
            raise SystemExit(f"{BAD} Không đọc được mã nguồn từ: {args.file}")
        return source
    return SAMPLES.get(args.language.upper(), SAMPLES["C"])


def _print_rubric(rubric: dict) -> int:
    """In bảng rubric 5 tiêu chí; trả về số tiêu chí PASS (điểm rubric /5)."""
    labels = {
        "clean_code": "Clean Code",
        "complexity": "Complexity",
        "structure": "Structure",
        "format": "Format",
        "documentation": "Documentation",
    }
    passes = 0
    for key, label in labels.items():
        item = rubric.get(key) or {}
        passed = bool(item.get("passed"))
        passes += int(passed)
        mark = "PASS" if passed else "FAIL"
        reason = str(item.get("reason", "") or "").replace("\n", " ").strip()
        print(f"   - {label:<14} {mark:<5} {reason[:160]}")
    return passes


def _run_quota(ai: AiService) -> bool:
    print(f"\n{INFO} Kiểm tra hạn ngạch AI (GET /ai/quota)...")
    res = ai.get_quota()
    if res.get("success"):
        print(f"{OK} Hạn ngạch: còn {res.get('remaining_tokens'):,}/"
              f"{res.get('daily_limit_tokens'):,} tokens "
              f"(đã dùng {res.get('used_tokens_today'):,})")
        return True
    print(f"{BAD} Không lấy được hạn ngạch: {res.get('message')} "
          f"(error_code={res.get('error_code')})")
    return False


def _run_pe_code(ai: AiService, args) -> bool:
    print(f"\n{INFO} Chấm rubric PE (POST /ai/evaluate-pe-code) | language={args.language}...")
    source = _resolve_source(args)
    print(f"{INFO} Độ dài mã nguồn gửi lên: {len(source)} ký tự")
    started = time.time()
    res = ai.evaluate_code_quality(source, args.language, args.problem)
    elapsed = time.time() - started

    if not res.get("success"):
        print(f"{BAD} AI thất bại sau {elapsed:.1f}s: {res.get('message')} "
              f"(error_code={res.get('error_code')})")
        if res.get("error_code") == "CONNECT_TIMEOUT":
            print(f"{INFO} Gợi ý: backend chậm (Render cold start / openrouter/free). "
                  f"Tăng AITA_AI_TIMEOUT (đang = {AI_REQUEST_TIMEOUT:.0f}s).")
        return False

    passes = _print_rubric(res.get("rubric") or {})
    print(f"{OK} Rubric: {passes}/5 điểm | tokens={res.get('tokens_consumed')} "
          f"| thời gian={elapsed:.1f}s")
    feedback = str(res.get("overall_feedback", "") or "").strip()
    if feedback:
        print(f"{INFO} Nhận xét tổng quan: {feedback[:400]}")
    return True


def _run_review_code(ai: AiService, args) -> bool:
    print(f"\n{INFO} AI review lỗi logic (POST /ai/review-code) | language={args.language}...")
    source = _resolve_source(args)
    res = ai.review_code(source, args.language, args.problem)
    if not res.get("success"):
        print(f"{BAD} AI review thất bại: {res.get('message')} (error_code={res.get('error_code')})")
        return False
    print(f"{OK} bug_category={res.get('bug_category')} line={res.get('suspected_error_line')}")
    print(f"{INFO} Tóm tắt: {str(res.get('issue_summary', ''))[:300]}")
    print(f"{INFO} Góp ý: {str(res.get('pedagogical_feedback', ''))[:300]}")
    return True


def _run_generate_testcases(ai: AiService, args) -> bool:
    print(f"\n{INFO} Sinh testcase (POST /ai/generate-testcases) | language={args.language}...")
    res = ai.generate_testcases(args.problem, language=args.language, count=3, include_boundary=True)
    if not res.get("success"):
        print(f"{BAD} Sinh testcase thất bại: {res.get('message')} (error_code={res.get('error_code')})")
        return False
    tcs = res.get("testcases", [])
    print(f"{OK} Sinh được {len(tcs)} testcase | tokens={res.get('tokens_consumed')}")
    for i, tc in enumerate(tcs, 1):
        print(f"   {i}. input={tc.get('input')!r} -> expected={tc.get('expected_output')!r} "
              f"(boundary={tc.get('is_boundary')})")
    return True


def _run_verify_plagiarism(ai: AiService, args) -> bool:
    print(f"\n{INFO} Thẩm định đạo văn 2 bài (POST /ai/verify-plagiarism)...")
    a = SAMPLES["C"]
    b = SAMPLES["C"].replace("int s=a+b;", "int s = b + a; // copy")
    res = ai.verify_plagiarism(a, b, ast_similarity_percentage=90, language="C")
    if not res.get("success"):
        print(f"{BAD} Thẩm định thất bại: {res.get('message')} (error_code={res.get('error_code')})")
        return False
    print(f"{OK} is_plagiarized={res.get('is_plagiarized')} "
          f"confidence={res.get('confidence_percentage')}% "
          f"| tokens={res.get('tokens_consumed')}")
    print(f"{INFO} Bằng chứng: {str(res.get('evidence_summary', ''))[:300]}")
    return True


def _run_evaluate_web_ui(ai: AiService, args) -> bool:
    if not args.screenshot:
        print(f"\n{INFO} Bỏ qua evaluate-web-ui (cần --screenshot <path.png>)")
        return True
    shot = Path(args.screenshot)
    if not shot.is_file():
        print(f"\n{BAD} Không tìm thấy ảnh --screenshot: {shot}")
        return False
    print(f"\n{INFO} Đánh giá UI web (POST /ai/evaluate-web-ui)...")
    import base64
    raw = shot.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    mime = "image/png" if raw[:8] == b"\x89PNG\r\n\x1a\n" else "image/jpeg"
    res = ai.evaluate_web_ui(f"data:{mime};base64,{b64}",
                             ["Bố cục rõ ràng", "Màu sắc hài hoà", "Điều hướng trực quan"])
    if not res.get("success"):
        print(f"{BAD} Đánh giá UI thất bại: {res.get('message')} (error_code={res.get('error_code')})")
        return False
    print(f"{OK} ui_score={res.get('ui_score')} | tokens={res.get('tokens_consumed')}")
    print(f"{INFO} {str(res.get('overall_feedback', ''))[:300]}")
    return True


def _login(username: str, password: str) -> bool:
    api = ApiClient.get_instance()
    print(f"{INFO} Backend đang dùng: {api.base_url}")
    print(f"\n{INFO} Đăng nhập {username} (POST /auth/login)...")
    auth = AuthService(api)
    res = auth.login(username, password)
    if not res.get("success"):
        print(f"{BAD} Đăng nhập thất bại: {res.get('message')} (error_code={res.get('error_code')})")
        return False
    user = res.get("user", {}) or {}
    print(f"{OK} Đăng nhập thành công: {user.get('full_name', username)} "
          f"[role={user.get('role')}]")
    if user.get("role") not in (None, "INSTRUCTOR", "instructor"):
        print(f"{INFO} Lưu ý: AI Gateway yêu cầu role INSTRUCTOR; role hiện tại = {user.get('role')}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Test AI Hub của AITA (không cần GUI).")
    parser.add_argument("-u", "--username", default=os.getenv("AITA_USERNAME"), help="Tài khoản Instructor")
    parser.add_argument("-p", "--password", default=os.getenv("AITA_PASSWORD"), help="Mật khẩu")
    parser.add_argument("--backend", default=os.getenv("AITA_BACKEND_URL"),
                        help="Ghim backend URL (mặc định: tự dò localhost:3000 rồi tới Render)")
    parser.add_argument("--feature",
                        choices=["quota", "pe-code", "review-code", "generate-testcases",
                                 "verify-plagiarism", "web-ui", "all"],
                        default="pe-code", help="Kiểm tra nào cần chạy (mặc định: pe-code)")
    parser.add_argument("--file", help="File hoặc thư mục bài nộp để chấm thay cho code mẫu")
    parser.add_argument("--language", default="C", help="C | JAVA | PYTHON | PHP (mặc định C)")
    parser.add_argument("--problem", default=DEFAULT_PROBLEM, help="Đề bài gửi kèm (tùy chọn)")
    parser.add_argument("--screenshot", help="Ảnh PNG/JPEG cho --feature web-ui")
    args = parser.parse_args()

    if not args.username or not args.password:
        print(f"{BAD} Thiếu thông tin đăng nhập. Dùng --username/--password "
              f"hoặc đặt AITA_USERNAME/AITA_PASSWORD.")
        return 1

    args.language = str(args.language).upper()
    if args.language not in SAMPLES:
        print(f"{INFO} Ngôn ngữ '{args.language}' không thuộc mẫu có sẵn, dùng C làm mẫu.")
        args.language = "C"

    if args.backend:
        os.environ["AITA_BACKEND_URL"] = args.backend
        ApiClient._instance = None  # buộc tạo mới để áp dụng URL vừa ghim

    if not _login(args.username, args.password):
        return 1

    ai = AiService()

    if args.feature == "quota":
        return 0 if _run_quota(ai) else 1

    if args.feature == "all":
        checks = [
            ("quota", _run_quota),
            ("pe-code", _run_pe_code),
            ("review-code", _run_review_code),
            ("generate-testcases", _run_generate_testcases),
            ("verify-plagiarism", _run_verify_plagiarism),
            ("web-ui", _run_evaluate_web_ui),
        ]
    else:
        dispatch = {
            "pe-code": _run_pe_code,
            "review-code": _run_review_code,
            "generate-testcases": _run_generate_testcases,
            "verify-plagiarism": _run_verify_plagiarism,
            "web-ui": _run_evaluate_web_ui,
        }
        checks = [(args.feature, dispatch[args.feature])]

    results = []
    for name, fn in checks:
        if name == "quota":
            passed = fn(ai)
        else:
            passed = fn(ai, args)
        results.append((name, passed))

    print("\n===================== TỔNG KẾT =====================")
    for name, passed in results:
        print(f"  {OK if passed else BAD} {name}")
    ok = all(passed for _, passed in results)
    print("====================================================")
    print("Kết luận:", "AI HOẠT ĐỘNG BÌNH THƯỜNG" if ok else "CÓ LỖI — xem chi tiết phía trên")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
