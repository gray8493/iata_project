"""
AITA Desktop Client - Central Backend API Client
Handles HTTP communications with Central Backend (NestJS) on Render.
Supports automatic token injection, timeout handling, and server health checks.
"""

import os
from typing import Optional, Dict, Any
import httpx

# Default Backend URL on Render
DEFAULT_BACKEND_URL = "https://iata-project.onrender.com/api/v1"


class ApiClient:
    """
    Central API Client for AITA Desktop Client.
    Manages HTTP sessions, base URL, timeout, and authentication tokens.
    """
    _instance: Optional["ApiClient"] = None

    def __init__(self, base_url: Optional[str] = None):
        env_url = os.getenv("AITA_BACKEND_URL")
        if base_url:
            self.base_url = base_url.rstrip("/")
        elif env_url:
            self.base_url = env_url.rstrip("/")
        else:
            # Ưu tiên kết nối backend local nếu đang chạy, nếu không kết nối Render
            self.base_url = DEFAULT_BACKEND_URL
            try:
                with httpx.Client(timeout=0.6) as client:
                    if client.get("http://localhost:3000/api/v1/health").status_code == 200:
                        self.base_url = "http://localhost:3000/api/v1"
            except Exception:
                self.base_url = DEFAULT_BACKEND_URL
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
            "User-Agent": "AITA-Desktop-Client/2.4.0"
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
                "data": resp.json() if resp.status_code == 200 else None
            }

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> httpx.Response:
        """Sends a POST request to the specified endpoint."""
        endpoint = endpoint.lstrip("/")
        url = f"{self.base_url}/{endpoint}"
        with httpx.Client(timeout=self.timeout) as client:
            return client.post(url, json=data or {}, headers=self.get_headers())

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> httpx.Response:
        """Sends a GET request to the specified endpoint."""
        endpoint = endpoint.lstrip("/")
        url = f"{self.base_url}/{endpoint}"
        with httpx.Client(timeout=self.timeout) as client:
            return client.get(url, params=params, headers=self.get_headers())
