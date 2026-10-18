"""AuthService (services.auth_service) - login, profile, logout, refresh.

Pins the client-side authentication contract against the Central Backend
(envelope unwrapping + token persistence on the shared ApiClient). No network:
a fake ApiClient records the calls.
"""

import httpx

from services.auth_service import AuthService


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
        self.saved = None
        self.cleared = False
        self.refresh_calls = 0

    def post(self, path, payload=None):
        if self.raises:
            raise self.raises
        return self.response

    def get(self, path):
        if self.raises:
            raise self.raises
        return self.response

    def set_tokens(self, access_token=None, refresh_token=None, user=None):
        self.saved = {"access": access_token, "refresh": refresh_token, "user": user}

    def clear_tokens(self):
        self.cleared = True

    def refresh_access_token(self):
        self.refresh_calls += 1
        return True


def _service(response=None, raises=None):
    api = FakeApiClient(response=response, raises=raises)
    return AuthService(api_client=api), api


def test_login_success_persists_tokens_and_returns_user():
    response = FakeResponse(200, {
        "data": {"access_token": "access-1", "refresh_token": "refresh-1", "user": {"username": "gv1", "role": "INSTRUCTOR"}},
        "message": "Đăng nhập thành công!",
    })
    service, api = _service(response)

    result = service.login("  gv1  ", "Abc12345")

    assert result["success"] is True
    assert result["user"]["username"] == "gv1"
    assert api.saved == {"access": "access-1", "refresh": "refresh-1", "user": {"username": "gv1", "role": "INSTRUCTOR"}}


def test_login_failure_returns_backend_error_code():
    service, api = _service(FakeResponse(401, {"success": False, "message": "Sai tài khoản", "error_code": "AUTH_INVALID_CREDENTIALS"}))

    result = service.login("gv1", "wrong")

    assert result["success"] is False
    assert result["error_code"] == "AUTH_INVALID_CREDENTIALS"
    assert result["status_code"] == 401
    assert api.saved is None


def test_login_connect_timeout_is_sanitized():
    service, _ = _service(raises=httpx.ConnectTimeout("slow"))

    result = service.login("gv1", "Abc12345")

    assert result["success"] is False
    assert result["error_code"] == "CONNECT_TIMEOUT"


def test_get_profile_unwraps_data_envelope():
    service, _ = _service(FakeResponse(200, {"data": {"id": "u1", "username": "gv1"}}))

    result = service.get_profile()

    assert result["success"] is True
    assert result["data"]["username"] == "gv1"


def test_get_profile_failure_is_reported():
    service, _ = _service(FakeResponse(500))

    result = service.get_profile()

    assert result["success"] is False


def test_logout_clears_local_session():
    service, api = _service()

    service.logout()

    assert api.cleared is True


def test_refresh_session_delegates_to_api_client():
    service, api = _service()

    assert service.refresh_session() is True
    assert api.refresh_calls == 1
