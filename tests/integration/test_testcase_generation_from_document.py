"""Integration tests - AI Testcase generation from an imported document.

Feature: the problem statement read from a file by `services.document_reader`
is POSTed by `services.ai_service.AiService` to the Central Backend AI Gateway
(`POST /api/v1/ai/generate-testcases`).

The HTTP layer is served by an httpx.MockTransport, so no network is needed
while still exercising the real ApiClient -> AiService integration.
"""
import json

import httpx
import pytest

import services.api_client as api_client_module
from services.ai_service import AiService
from services.api_client import ApiClient
from services.document_reader import read_document_text

ENDPOINT_SUFFIX = "/ai/generate-testcases"


def _install_transport(monkeypatch, handler):
    """Routes every httpx.Client created by ApiClient through a mock transport."""
    real_client = httpx.Client

    def factory(*args, **kwargs):
        kwargs.pop("base_url", None)
        timeout = kwargs.pop("timeout", 5.0)
        return real_client(transport=httpx.MockTransport(handler), timeout=timeout, **kwargs)

    monkeypatch.setattr(api_client_module.httpx, "Client", factory)


@pytest.fixture
def ai_service():
    return AiService(api_client=ApiClient(base_url="http://test.local/api/v1"))


# ------------------------------------------------------------------------------
# Normal
# ------------------------------------------------------------------------------
def test_it05_aitestcasegeneration_tc001_document_text_is_sent_to_ai(monkeypatch, tmp_path, ai_service):
    """IT05_AiTestcaseGeneration_TC001: nội dung file đề bài được gửi tới AI Gateway."""
    f = tmp_path / "de_bai.txt"
    f.write_text(
        "Đếm số nguyên tố nhỏ hơn N. Input: số nguyên N. Output: số lượng nguyên tố.",
        encoding="utf-8",
    )
    document_text = read_document_text(f)
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(
            200,
            json={
                "success": True,
                "data": {"testcases": [{"input": "5", "expected_output": "3"}], "tokens_consumed": 42},
                "message": "Sinh testcase thành công!",
            },
        )

    _install_transport(monkeypatch, handler)
    result = ai_service.generate_testcases(problem_description=document_text, language="python", count=2)

    assert result["success"] is True
    assert result["testcases"][0]["expected_output"] == "3"
    assert result["tokens_consumed"] == 42
    assert captured["body"]["problem_description"] == document_text
    assert captured["body"]["language"] == "PYTHON"


# ------------------------------------------------------------------------------
# Boundary
# ------------------------------------------------------------------------------
def test_it05_aitestcasegeneration_tc002_clamps_count_and_language(monkeypatch, ai_service):
    """IT05_AiTestcaseGeneration_TC002: count bị kẹp về 10, ngôn ngữ lạ -> 'C' (biên)."""
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(200, json={"success": True, "data": {"testcases": []}, "message": "ok"})

    _install_transport(monkeypatch, handler)
    ai_service.generate_testcases(problem_description="x" * 30, language="rust", count=99)

    assert captured["body"]["count"] == 10
    assert captured["body"]["language"] == "C"


# ------------------------------------------------------------------------------
# Exception
# ------------------------------------------------------------------------------
def test_it05_aitestcasegeneration_tc003_surfaces_backend_error(monkeypatch, ai_service):
    """IT05_AiTestcaseGeneration_TC003: backend trả lỗi -> AiService trả success=False."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            429,
            json={
                "success": False,
                "message": "Đã dùng hết token AI.",
                "error_code": "AI_QUOTA_EXCEEDED",
            },
        )

    _install_transport(monkeypatch, handler)
    result = ai_service.generate_testcases(
        problem_description="Đề bài đủ dài để vượt qua kiểm tra tối thiểu.",
        language="C",
        count=1,
    )

    assert result["success"] is False
    assert result["error_code"] == "AI_QUOTA_EXCEEDED"
