"""AiService (services.ai_service) - request shaping and envelope unwrapping.

The desktop client never talks to AI Hub directly; it calls the Central Backend
AI gateway through ApiClient. These tests pin the client-side contract:
payload normalization/clamping and the success/error envelopes the UI relies on.
No network: a fake ApiClient records the calls.
"""

import httpx

from services.ai_service import AiService


class FakeResponse:
    def __init__(self, status_code: int, payload=None):
        self.status_code = status_code
        self._payload = payload
        self.content = b"{}" if payload is not None else b""

    def json(self):
        return self._payload


class FakeApiClient:
    def __init__(self, response=None, raises=None):
        self.response = response
        self.raises = raises
        self.calls = []

    def get(self, path):
        self.calls.append(("GET", path, None))
        if self.raises:
            raise self.raises
        return self.response

    def post(self, path, payload=None, timeout=None):
        self.calls.append(("POST", path, payload))
        if self.raises:
            raise self.raises
        return self.response


def _service(response=None, raises=None):
    api = FakeApiClient(response=response, raises=raises)
    return AiService(api_client=api), api


# ------------------------------------------------------------------------------
# get_quota
# ------------------------------------------------------------------------------
def test_get_quota_success_unwraps_data_envelope():
    response = FakeResponse(200, {
        "success": True,
        "data": {"daily_limit_tokens": 50000, "used_tokens_today": 12000, "remaining_tokens": 38000, "reset_at_utc": "2026-10-18T00:00:00Z"},
        "message": "Lấy hạn ngạch thành công",
    })
    service, api = _service(response)

    result = service.get_quota()

    assert api.calls == [("GET", "ai/quota", None)]
    assert result["success"] is True
    assert result["remaining_tokens"] == 38000


def test_get_quota_non_200_reports_status_code():
    service, _ = _service(FakeResponse(500, {"success": False, "message": "lỗi server"}))

    result = service.get_quota()

    assert result["success"] is False
    assert result["status_code"] == 500


def test_get_quota_connect_error_is_sanitized():
    service, _ = _service(raises=httpx.ConnectError("boom"))

    result = service.get_quota()

    assert result["success"] is False
    assert result["error_code"] == "CONNECT_ERROR"


# ------------------------------------------------------------------------------
# generate_testcases
# ------------------------------------------------------------------------------
def test_generate_testcases_normalizes_language_and_clamps_count():
    response = FakeResponse(201, {
        "success": True,
        "data": {"testcases": [{"input": "1", "expected_output": "1", "explanation": "x", "is_boundary": False}], "tokens_consumed": 42},
        "message": "Sinh testcase thành công!",
    })
    service, api = _service(response)

    result = service.generate_testcases("  Đề bài kiểm tra thuật toán  ", language="cobol", count=99, include_boundary=True)

    _, _, payload = api.calls[0]
    assert payload["language"] == "C"
    assert payload["count"] == 10
    assert payload["problem_description"] == "Đề bài kiểm tra thuật toán"
    assert result["success"] is True
    assert result["tokens_consumed"] == 42


def test_generate_testcases_surfaces_backend_quota_error():
    service, _ = _service(FakeResponse(429, {"success": False, "message": "Hết quota", "error_code": "AI_QUOTA_EXCEEDED"}))

    result = service.generate_testcases("Đề bài", language="C", count=3)

    assert result["success"] is False
    assert result["error_code"] == "AI_QUOTA_EXCEEDED"
    assert result["status_code"] == 429


# ------------------------------------------------------------------------------
# review_code
# ------------------------------------------------------------------------------
def test_review_code_fills_default_failed_testcase_when_missing():
    response = FakeResponse(200, {
        "success": True,
        "data": {"issue_summary": "sai biến đếm", "pedagogical_feedback": "xem lại vòng lặp", "bug_category": "LOGIC_ERROR", "suspected_error_line": 18, "tokens_consumed": 500},
        "message": "Phân tích mã nguồn thành công!",
    })
    service, api = _service(response)

    result = service.review_code("int main(){}", "C", "Đếm số nguyên tố", failed_testcase=None)

    _, _, payload = api.calls[0]
    assert payload["failed_testcase"] == {"input": "N/A", "expected_output": "N/A", "actual_output": "N/A"}
    assert result["success"] is True
    assert result["suspected_error_line"] == 18


# ------------------------------------------------------------------------------
# verify_plagiarism
# ------------------------------------------------------------------------------
def test_verify_plagiarism_clamps_similarity_into_backend_range():
    response = FakeResponse(200, {"success": True, "data": {"is_plagiarized": True, "confidence_percentage": 86, "evidence_summary": "e", "cloned_segments": [], "tokens_consumed": 9}, "message": "ok"})
    low_service, low_api = _service(response)
    high_service, high_api = _service(response)

    low_service.verify_plagiarism("a", "b", ast_similarity_percentage=50, language="C")
    high_service.verify_plagiarism("a", "b", ast_similarity_percentage=150, language="C")

    assert low_api.calls[0][2]["ast_similarity_percentage"] == 80.0
    assert high_api.calls[0][2]["ast_similarity_percentage"] == 100.0


# ------------------------------------------------------------------------------
# evaluate_web_ui
# ------------------------------------------------------------------------------
def test_evaluate_web_ui_returns_score_and_details():
    response = FakeResponse(200, {
        "success": True,
        "data": {"ui_score": 7.5, "evaluation_details": [{"criterion": "layout", "score": 7.5, "verdict": "PARTIAL", "comment": "ok"}], "overall_feedback": "tốt", "tokens_consumed": 100},
        "message": "Đánh giá giao diện Web thành công!",
    })
    service, api = _service(response)

    result = service.evaluate_web_ui("data:image/png;base64,AAAA", ["layout"])

    _, _, payload = api.calls[0]
    assert payload["rubric_requirements"] == ["layout"]
    assert result["success"] is True
    assert result["ui_score"] == 7.5
