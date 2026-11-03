"""Hồi quy: đọc phản hồi quá hạn khi đăng nhập không được làm rơi exception ra khỏi thread."""

import httpx

from services.auth_service import AuthService, LOGIN_TIMEOUT_SECONDS


class _TimeoutClient:
    base_url = "https://example.invalid/api/v1"

    def __init__(self, exc):
        self._exc = exc
        self.timeouts = []

    def post(self, endpoint, data=None, timeout=None):
        self.timeouts.append(timeout)
        raise self._exc

    def reprobe_backend(self):
        return self.base_url


def test_read_timeout_returns_failure_instead_of_raising():
    client = _TimeoutClient(httpx.ReadTimeout("slow"))
    result = AuthService(api_client=client).login("u", "p")
    assert result["success"] is False
    assert result["error_code"] == "READ_TIMEOUT"
    assert client.timeouts == [LOGIN_TIMEOUT_SECONDS]


def test_connect_error_keeps_its_own_error_code():
    client = _TimeoutClient(httpx.ConnectError("refused"))
    result = AuthService(api_client=client).login("u", "p")
    assert result["error_code"] == "CONNECT_ERROR"
