"""API Client auth resilience (services.api_client).

Covers IT22 (Token Expired -> Refresh Rotation) and the client-side echo of
IT02 (403 AUTH_ACCOUNT_DISABLED clears the local session), plus the single
retry-once semantics of get/post. HTTP calls are served by an httpx
MockTransport - no network needed.
"""

import httpx
import pytest

import services.api_client as api_client_module
from services.api_client import ApiClient


@pytest.fixture
def backend(monkeypatch):
    """Installs a token-aware mock transport and returns the recorder."""
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        calls.append((request.method, str(request.url)))
        if path.endswith("/auth/refresh"):
            return httpx.Response(
                200,
                json={"data": {"access_token": "new-access", "refresh_token": "new-refresh"}},
            )
        auth = request.headers.get("Authorization", "")
        if auth == "Bearer old-access":
            return httpx.Response(401, json={"error_code": "AUTH_TOKEN_EXPIRED"})
        if auth == "Bearer new-access":
            return httpx.Response(200, json={"data": {"ok": True}})
        return httpx.Response(401)

    monkeypatch.setattr(api_client_module.httpx, "Client", _client_factory(handler))
    return calls


def _client_factory(handler):
    real_client = httpx.Client  # captured BEFORE the module attr is monkeypatched

    def factory(*args, **kwargs):
        kwargs.pop("base_url", None)
        timeout = kwargs.pop("timeout", 5.0)
        return real_client(transport=httpx.MockTransport(handler), timeout=timeout, **kwargs)
    return factory


@pytest.fixture
def client(monkeypatch) -> ApiClient:
    monkeypatch.delenv("AITA_BACKEND_URL", raising=False)
    api = ApiClient(base_url="http://test.local/api/v1")
    api.set_tokens(access_token="old-access", refresh_token="old-refresh")
    return api


# ------------------------------------------------------------------------------
# refresh_access_token (IT22)
# ------------------------------------------------------------------------------
def test_refresh_access_token_rotates_both_tokens(client, backend):
    assert client.refresh_access_token() is True
    assert client.access_token == "new-access"
    assert client.refresh_token == "new-refresh"


def test_refresh_without_stored_refresh_token_is_noop(client):
    client.refresh_token = None
    assert client.refresh_access_token() is False


def test_refresh_failure_clears_session(client, monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error_code": "AUTH_INVALID_REFRESH_TOKEN"})

    monkeypatch.setattr(api_client_module.httpx, "Client", _client_factory(handler))
    assert client.refresh_access_token() is False
    assert client.access_token is None and client.refresh_token is None


# ------------------------------------------------------------------------------
# Transport-wide auto-refresh (single retry on 401)
# ------------------------------------------------------------------------------
def test_get_refreshes_expired_token_once_and_succeeds(client, backend):
    resp = client.get("auth/me")
    assert resp.status_code == 200
    assert client.access_token == "new-access"

    endpoints = [method for method, _ in backend]
    assert endpoints.count("POST") == 1  # exactly one refresh rotation
    assert endpoints.count("GET") == 2   # failed attempt + retried attempt


def test_post_also_refreshes_and_retries(client, backend):
    resp = client.post("ai/generate-testcases", data={"prompt": "de bai"})
    assert resp.status_code == 200


def test_401_without_refresh_token_is_returned_as_is(client, backend):
    client.refresh_token = None
    resp = client.get("auth/me")
    assert resp.status_code == 401
    assert [m for m, _ in backend].count("POST") == 0


def test_refresh_endpoint_itself_never_retries(client, monkeypatch):
    refresh_calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/auth/refresh"):
            refresh_calls.append(1)
            return httpx.Response(401)
        return httpx.Response(200)

    monkeypatch.setattr(api_client_module.httpx, "Client", _client_factory(handler))
    resp = client.post("auth/refresh", data={"refresh_token": "t"})
    assert resp.status_code == 401  # no retry loop inside refresh endpoint
    assert len(refresh_calls) == 1


# ------------------------------------------------------------------------------
# 403 handling (IT02: disabled account revokes access instantly)
# ------------------------------------------------------------------------------
def test_403_account_disabled_clears_local_session(client, monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, json={"error_code": "AUTH_ACCOUNT_DISABLED"})

    monkeypatch.setattr(api_client_module.httpx, "Client", _client_factory(handler))
    resp = client.get("auth/me")
    assert resp.status_code == 403
    assert client.access_token is None and client.refresh_token is None


def test_403_other_error_codes_keep_session(client, monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, json={"error_code": "FORBIDDEN_ADMIN_ONLY"})

    monkeypatch.setattr(api_client_module.httpx, "Client", _client_factory(handler))
    resp = client.get("admin/reports/overview")
    assert resp.status_code == 403
    assert client.access_token == "old-access"


# ------------------------------------------------------------------------------
# Headers & token setters
# ------------------------------------------------------------------------------
def test_get_headers_inject_bearer_and_default_ua(client):
    headers = client.get_headers()
    assert headers["Authorization"] == "Bearer old-access"
    assert headers["User-Agent"].startswith("AITA-Desktop-Client")
    headers2 = client.get_headers({"X-Custom": "1"})
    assert headers2["X-Custom"] == "1"


def test_clear_tokens_removes_user_context(client):
    client.current_user = {"username": "gv1"}
    client.clear_tokens()
    assert client.current_user is None and client.access_token is None


def test_backend_url_resolution_env_beats_default(monkeypatch):
    monkeypatch.setenv("AITA_BACKEND_URL", "http://env-backend/api/v1/")
    api = ApiClient()
    assert api.base_url == "http://env-backend/api/v1"
