"""
AITA Desktop Client - Central Backend API Client
Handles HTTP communications with Central Backend (NestJS) on Render.
Supports automatic token injection, timeout handling, and server health checks.
"""

import os
from typing import Optional, Dict, Any
import httpx

from core.version import APP_VERSION

# Default Backend URL on Render
DEFAULT_BACKEND_URL = "https://iata-project-o4z6.onrender.com/api/v1"


def parse_json(resp: httpx.Response) -> Optional[Dict[str, Any]]:
    """Trả về dict nếu body là JSON, ngược lại None (server/proxy trả HTML hoặc plain text)."""
    if not resp.content:
        return None
    try:
        data = resp.json()
    except Exception:
        return None
    return data if isinstance(data, dict) else None


class ApiClient:
    """
    Central API Client for AITA Desktop Client.
    Manages HTTP sessions, base URL, timeout, and authentication tokens.
    """
    _instance: Optional["ApiClient"] = None

    def __init__(self, base_url: Optional[str] = None):
        env_url = os.getenv("AITA_BACKEND_URL")
        self._fixed_base = bool(base_url)
        if base_url:
            self.base_url = base_url.rstrip("/")
        elif env_url:
            self.base_url = env_url.rstrip("/")
        else:
            # Ưu tiên kết nối backend local nếu đang chạy, nếu không kết nối Render
            self.base_url = DEFAULT_BACKEND_URL
            self.reprobe_backend()
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.current_user: Optional[Dict[str, Any]] = None
        # Timeout 25s to gracefully handle Render.com free-tier cold starts
        self.timeout = 25.0

    @classmethod
    def get_instance(cls) -> "ApiClient":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def reprobe_backend(self) -> str:
        """Thăm dò lại backend local (dev). Khi bị ghim base_url/env thì giữ nguyên.

        Dùng khi phiên phiên trước chọn Render vì backend local chưa kịp bật:
        nút 'Thử Lại' gọi lại hàm này để tự chuyển về localhost mà không cần khởi động app.
        """
        if self._fixed_base or os.getenv("AITA_BACKEND_URL"):
            return self.base_url
        try:
            with httpx.Client(timeout=0.6) as client:
                if client.get("http://localhost:3000/api/v1/health").status_code == 200:
                    self.base_url = "http://localhost:3000/api/v1"
        except Exception:
            pass
        return self.base_url

    def set_tokens(self, access_token: str, refresh_token: Optional[str] = None, user: Optional[Dict[str, Any]] = None):
        """Sets the active authentication session."""
        self.access_token = access_token
        if refresh_token:
            self.refresh_token = refresh_token
        if user:
            self.current_user = user

    def clear_tokens(self):
        """Clears the session tokens upon logout."""
        self.access_token = None
        self.refresh_token = None
        self.current_user = None

    def get_headers(self, custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Constructs headers with Bearer token if present."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"AITA-Desktop-Client/{APP_VERSION}"
        }
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        if custom_headers:
            headers.update(custom_headers)
        return headers

    def check_health(self) -> Dict[str, Any]:
        """
        Pings /health endpoint to check server availability and cold-start wake up.
        """
        url = f"{self.base_url}/health"
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(url, headers=self.get_headers())
            return {
                "status_code": resp.status_code,
                "is_ok": resp.status_code == 200,
                "data": parse_json(resp) if resp.status_code == 200 else None
            }

    def refresh_access_token(self) -> bool:
        """
        Rotates the token pair via POST /auth/refresh using the stored refresh token.
        Returns True when a new access token was issued (IT22).
        """
        if not self.refresh_token:
            return False
        url = f"{self.base_url}/auth/refresh"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(
                    url,
                    json={"refresh_token": self.refresh_token},
                    headers=self.get_headers()
                )
            if resp.status_code in (200, 201):
                data = parse_json(resp) or {}
                payload = data.get("data", data)
                access_token = payload.get("access_token")
                new_refresh = payload.get("refresh_token")
                if access_token:
                    self.set_tokens(access_token=access_token, refresh_token=new_refresh or self.refresh_token)
                    return True
            self.clear_tokens()
        except Exception:
            pass
        return False

    def _handle_auth_failure(self, resp: httpx.Response):
        """Clears the local session when the backend reports a disabled/revoked account."""
        if resp.status_code != 403:
            return
        try:
            error_code = (resp.json() or {}).get("error_code")
        except Exception:
            return
        if error_code in ("AUTH_ACCOUNT_DISABLED", "AUTH_INVALID_REFRESH_TOKEN", "AUTH_TOKEN_EXPIRED"):
            self.clear_tokens()

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> httpx.Response:
        """Sends a POST request, transparently refreshing an expired token once on HTTP 401."""
        endpoint = endpoint.lstrip("/")
        url = f"{self.base_url}/{endpoint}"
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, json=data or {}, headers=self.get_headers())
            if resp.status_code == 401 and self.refresh_token and endpoint != "auth/refresh":
                if self.refresh_access_token():
                    resp = client.post(url, json=data or {}, headers=self.get_headers())
            self._handle_auth_failure(resp)
            return resp

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> httpx.Response:
        """Sends a GET request, transparently refreshing an expired token once on HTTP 401."""
        endpoint = endpoint.lstrip("/")
        url = f"{self.base_url}/{endpoint}"
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(url, params=params, headers=self.get_headers())
            if resp.status_code == 401 and self.refresh_token and endpoint != "auth/refresh":
                if self.refresh_access_token():
                    resp = client.get(url, params=params, headers=self.get_headers())
            self._handle_auth_failure(resp)
            return resp
