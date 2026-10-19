"""
AITA Desktop Client - Central AI Service
Connects to Central Backend (NestJS / Render / Neon Postgres) for AI features:
- AI Quota inspection (GET /api/v1/ai/quota)
- AI Boundary Testcase Generation (POST /api/v1/ai/generate-testcases)
- AI Code Pedagogical Review (POST /api/v1/ai/review-code)
- AI Two-Stage Plagiarism Deep Verification (POST /api/v1/ai/verify-plagiarism)
- AI Web UI Evaluation (POST /api/v1/ai/evaluate-web-ui)
- AI PE Code Quality Evaluation (POST /api/v1/ai/evaluate-pe-code)
"""

from typing import Dict, Any, Optional, List
import httpx
from .api_client import ApiClient


class AiService:
    """
    Service client for interacting with Central Backend AI Gateway.
    Uses ApiClient singleton with active JWT session tokens.
    """

    def __init__(self, api_client: Optional[ApiClient] = None):
        self.api_client = api_client or ApiClient.get_instance()

    def get_quota(self) -> Dict[str, Any]:
        """
        Retrieves live daily AI token quota from Neon Postgres database via GET /ai/quota.
        Returns:
            Dict containing success, daily_limit_tokens, used_tokens_today, remaining_tokens.
        """
        try:
            resp = self.api_client.get("ai/quota")
            resp_data = resp.json() if resp.content else {}

            if resp.status_code == 200 and resp_data.get("success"):
                data = resp_data.get("data", {})
                return {
                    "success": True,
                    "daily_limit_tokens": data.get("daily_limit_tokens", 50000),
                    "used_tokens_today": data.get("used_tokens_today", 0),
                    "remaining_tokens": data.get("remaining_tokens", 50000),
                    "reset_at_utc": data.get("reset_at_utc"),
                    "message": resp_data.get("message", "Lấy hạn ngạch thành công")
                }
            return {
                "success": False,
                "message": resp_data.get("message", "Không thể lấy hạn ngạch AI"),
                "status_code": resp.status_code
            }
        except httpx.ConnectTimeout:
            return {"success": False, "message": "Hết thời gian kết nối máy chủ AI.", "error_code": "CONNECT_TIMEOUT"}
        except httpx.ConnectError:
            return {"success": False, "message": "Không thể kết nối đến máy chủ AI.", "error_code": "CONNECT_ERROR"}
        except Exception as e:
            return {"success": False, "message": f"Lỗi truy vấn hạn ngạch: {str(e)}", "error_code": "EXCEPTION"}

    def generate_testcases(
        self,
        problem_description: str,
        language: str = "C",
        count: int = 4,
        include_boundary: bool = True
    ) -> Dict[str, Any]:
        """
        Calls Central Backend AI Gateway to generate high-quality boundary testcases.
        Endpoint: POST /api/v1/ai/generate-testcases
        """
        # Chuẩn hóa ngôn ngữ theo enum ['C', 'JAVA', 'PYTHON', 'WEB']
        lang_upper = language.upper().strip()
        if lang_upper not in ["C", "JAVA", "PYTHON", "WEB"]:
            lang_upper = "C"

        # Đảm bảo problem_description đáp ứng MinLength(20) của Backend
        description = problem_description.strip()
        if len(description) < 20:
            # Pad mô tả nếu quá ngắn để tránh VALIDATION_FAILED từ class-validator
            description = description.ljust(20, ' ')

        payload = {
            "problem_description": description,
            "language": lang_upper,
            "count": max(1, min(10, count)),
            "include_boundary": include_boundary
        }

        try:
            resp = self.api_client.post("ai/generate-testcases", payload)
            resp_data = resp.json() if resp.content else {}

            if resp.status_code in (200, 201) and resp_data.get("success"):
                data = resp_data.get("data", {})
                return {
                    "success": True,
                    "testcases": data.get("testcases", []),
                    "tokens_consumed": data.get("tokens_consumed", 0),
                    "message": resp_data.get("message", "Sinh testcase thành công!")
                }

            error_msg = resp_data.get("message", "Máy chủ AI chưa xử lý được yêu cầu.")
            error_code = resp_data.get("error_code", f"HTTP_{resp.status_code}")
            return {
                "success": False,
                "message": error_msg,
                "error_code": error_code,
                "status_code": resp.status_code
            }
        except httpx.ConnectTimeout:
            return {"success": False, "message": "Hết thời gian kết nối khi sinh testcase.", "error_code": "CONNECT_TIMEOUT"}
        except Exception as e:
            return {"success": False, "message": f"Lỗi kết nối AI: {str(e)}", "error_code": "EXCEPTION"}

    def review_code(
        self,
        source_code: str,
        language: str,
        problem_statement: str,
        failed_testcase: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Calls Central Backend AI Gateway to analyze student code logic and pedagogical feedback.
        Endpoint: POST /api/v1/ai/review-code
        """
        lang_upper = language.upper().strip()
        if lang_upper not in ["C", "JAVA", "PYTHON", "PHP"]:
            lang_upper = "C"

        tc = failed_testcase or {
            "input": "N/A",
            "expected_output": "N/A",
            "actual_output": "N/A"
        }

        payload = {
            "source_code": source_code,
            "language": lang_upper,
            "problem_statement": problem_statement or "Bài tập lập trình căn bản.",
            "failed_testcase": {
                "input": str(tc.get("input", "")),
                "expected_output": str(tc.get("expected_output", "")),
                "actual_output": str(tc.get("actual_output", ""))
            }
        }

        try:
            resp = self.api_client.post("ai/review-code", payload)
            resp_data = resp.json() if resp.content else {}

            if resp.status_code in (200, 201) and resp_data.get("success"):
                data = resp_data.get("data", {})
                return {
                    "success": True,
                    "issue_summary": data.get("issue_summary", ""),
                    "pedagogical_feedback": data.get("pedagogical_feedback", ""),
                    "bug_category": data.get("bug_category", "LOGIC_ERROR"),
                    "suspected_error_line": data.get("suspected_error_line"),
                    "tokens_consumed": data.get("tokens_consumed", 0),
                    "message": resp_data.get("message", "Phân tích mã nguồn thành công!")
                }

            error_msg = resp_data.get("message", "Máy chủ AI không thể phân tích mã nguồn.")
            return {
                "success": False,
                "message": error_msg,
                "error_code": resp_data.get("error_code", f"HTTP_{resp.status_code}")
            }
        except httpx.ConnectTimeout:
            return {"success": False, "message": "Hết thời gian kết nối AI Review.", "error_code": "CONNECT_TIMEOUT"}
        except Exception as e:
            return {"success": False, "message": f"Lỗi gọi AI Review: {str(e)}", "error_code": "EXCEPTION"}

    def verify_plagiarism(
        self,
        student_a_code: str,
        student_b_code: str,
        ast_similarity_percentage: float,
        language: str = "C"
    ) -> Dict[str, Any]:
        """
        Calls Central Backend AI Gateway for Stage 2 deep plagiarism forensics.
        Endpoint: POST /api/v1/ai/verify-plagiarism
        """
        lang_upper = language.upper().strip()
        if lang_upper not in ["C", "JAVA", "PYTHON", "PHP"]:
            lang_upper = "C"

        # Backend requires 80 <= ast_similarity_percentage <= 100
        clamped_sim = max(80.0, min(100.0, float(ast_similarity_percentage)))

        payload = {
            "student_a_code": student_a_code,
            "student_b_code": student_b_code,
            "ast_similarity_percentage": clamped_sim,
            "language": lang_upper
        }

        try:
            resp = self.api_client.post("ai/verify-plagiarism", payload)
            resp_data = resp.json() if resp.content else {}

            if resp.status_code in (200, 201) and resp_data.get("success"):
                data = resp_data.get("data", {})
                return {
                    "success": True,
                    "is_plagiarized": data.get("is_plagiarized", False),
                    "confidence_percentage": data.get("confidence_percentage", 0.0),
                    "evidence_summary": data.get("evidence_summary", ""),
                    "cloned_segments": data.get("cloned_segments", []),
                    "tokens_consumed": data.get("tokens_consumed", 0),
                    "message": resp_data.get("message", "Thẩm định đạo văn thành công!")
                }

            return {
                "success": False,
                "message": resp_data.get("message", "Không thể thẩm định đạo văn qua AI."),
                "error_code": resp_data.get("error_code", f"HTTP_{resp.status_code}")
            }
        except Exception as e:
            return {"success": False, "message": f"Lỗi thẩm định AI: {str(e)}", "error_code": "EXCEPTION"}

    def evaluate_web_ui(
        self,
        screenshot_base64: str,
        rubric_requirements: List[str]
    ) -> Dict[str, Any]:
        """
        Calls Central Backend AI Gateway for multimodal UI layout & rubric evaluation.
        Endpoint: POST /api/v1/ai/evaluate-web-ui
        """
        payload = {
            "screenshot_base64": screenshot_base64,
            "rubric_requirements": rubric_requirements
        }

        try:
            resp = self.api_client.post("ai/evaluate-web-ui", payload)
            resp_data = resp.json() if resp.content else {}

            if resp.status_code in (200, 201) and resp_data.get("success"):
                data = resp_data.get("data", {})
                return {
                    "success": True,
                    "ui_score": data.get("ui_score", 0.0),
                    "evaluation_details": data.get("evaluation_details", []),
                    "overall_feedback": data.get("overall_feedback", ""),
                    "tokens_consumed": data.get("tokens_consumed", 0),
                    "message": resp_data.get("message", "Đánh giá giao diện Web thành công!")
                }

            return {
                "success": False,
                "message": resp_data.get("message", "Không thể đánh giá UI qua AI."),
                "error_code": resp_data.get("error_code", f"HTTP_{resp.status_code}")
            }
        except Exception as e:
            return {"success": False, "message": f"Lỗi đánh giá Web UI: {str(e)}", "error_code": "EXCEPTION"}

    def evaluate_code_quality(
        self,
        source_code: str,
        language: str,
        problem_statement: str = ""
    ) -> Dict[str, Any]:
        """
        Calls Central Backend AI Gateway to grade code quality against the mandatory PE rubric
        (Clean Code, Complexity, Structure, Format, Documentation) - 1.0 point per criterion.
        Endpoint: POST /api/v1/ai/evaluate-pe-code
        """
        lang_upper = language.upper().strip()
        if lang_upper not in ["C", "JAVA", "PYTHON", "PHP"]:
            lang_upper = "C"

        # Đảm bảo đáp ứng ràng buộc DTO: 10 <= len(source_code) <= 20000
        code = (source_code or "").strip()
        if len(code) < 10:
            return {
                "success": False,
                "message": "Mã nguồn quá ngắn (< 10 ký tự) để chấm chất lượng.",
                "error_code": "SOURCE_TOO_SHORT"
            }
        code = code[:20000]

        payload = {
            "source_code": code,
            "language": lang_upper,
            "problem_statement": (problem_statement or "")[:5000]
        }

        try:
            resp = self.api_client.post("ai/evaluate-pe-code", payload)
            resp_data = resp.json() if resp.content else {}

            if resp.status_code in (200, 201) and resp_data.get("success"):
                data = resp_data.get("data", {}) or {}
                return {
                    "success": True,
                    "rubric": data.get("rubric", {}) or {},
                    "overall_feedback": data.get("overall_feedback", ""),
                    "tokens_consumed": data.get("tokens_consumed", 0),
                    "message": resp_data.get("message", "Đánh giá chất lượng mã nguồn thành công!")
                }

            return {
                "success": False,
                "message": resp_data.get("message", "Máy chủ AI không thể đánh giá chất lượng mã nguồn."),
                "error_code": resp_data.get("error_code", f"HTTP_{resp.status_code}")
            }
        except httpx.ConnectTimeout:
            return {"success": False, "message": "Hết thời gian kết nối khi chấm chất lượng mã.", "error_code": "CONNECT_TIMEOUT"}
        except Exception as e:
            return {"success": False, "message": f"Lỗi chấm chất lượng mã nguồn: {str(e)}", "error_code": "EXCEPTION"}
