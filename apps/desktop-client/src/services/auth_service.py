"""
AITA Desktop Client - Authentication Service
Handles login, token management, session validation with the Central Backend.
"""

from typing import Dict, Any, Optional
import httpx
from .api_client import ApiClient, parse_json


class AuthService:
    """
    Manages user authentication against the Central Backend API.
    """

    def __init__(self, api_client: Optional[ApiClient] = None):
        self.api_client = api_client or ApiClient.get_instance()

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticates a user (Instructor / Admin) with the Central Backend.
        
        Returns:
            Dict containing:
                - success: bool
                - message: str
                - data: dict (access_token, user, etc.) if success
                - error_code: str (if failed)
        """
        payload_login = {
            "username": username.strip(),
            "password": password
        }
        attempt = 0
        resp = None
        resp_data = None
        while True:
            attempt += 1
            try:
                resp = self.api_client.post("auth/login", payload_login)
            except httpx.ConnectTimeout:
                return {
                    "success": False,
                    "message": "Hết thời gian kết nối tới máy chủ. Vui lòng kiểm tra mạng và thử lại.",
                    "error_code": "CONNECT_TIMEOUT"
                }
            except httpx.ConnectError:
                return {
                    "success": False,
                    "message": "Không kết nối được tới máy chủ xác thực. Vui lòng kiểm tra kết nối mạng.",
                    "error_code": "CONNECT_ERROR"
                }
            resp_data = parse_json(resp)
            if resp_data is not None or attempt >= 2:
                break
            # Body không phải JSON: có thể phiên trước ghim vào nhầm máy chủ 404.
            # Đo lại địa chỉ; chỉ thử thêm lần nữa NẾU địa chỉ thật sự đổi (VD: local vừa bật).
            before = self.api_client.base_url
            self.api_client.reprobe_backend()
            if self.api_client.base_url == before:
                break

        if resp_data is None:
            # Body không phải JSON (thường gặp: server Render trả 'Not Found' HTML/plain khi
            # chưa deploy đúng bản backend, hoặc proxy 5xx trả trang lỗi).
            if resp.status_code == 404:
                message = (
                    "Không tìm thấy dịch vụ đăng nhập trên máy chủ "
                    f"({self.api_client.base_url}).\n"
                    "Máy chủ có thể chưa được triển khai đúng bản backend — "
                    "vui lòng báo quản trị hệ thống, hoặc bật backend local ở cổng 3000."
                )
            elif resp.status_code >= 500:
                message = (
                    "Máy chủ AITA đang gặp sự cố hoặc đang thức dậy sau thời gian nghỉ.\n"
                    "Vui lòng chờ khoảng 30 giây rồi bấm 'Thử Lại'."
                )
            else:
                message = (
                    f"Máy chủ trả về phản hồi không hợp lệ (mã {resp.status_code}).\n"
                    "Vui lòng thử lại hoặc báo quản trị hệ thống."
                )
            return {
                "success": False,
                "message": message,
                "error_code": f"HTTP_{resp.status_code}",
                "status_code": resp.status_code
            }

        if resp.status_code in (200, 201):
            # Backend envelope wraps output in 'data'
            payload = resp_data.get("data", resp_data)
            access_token = payload.get("access_token")
            refresh_token = payload.get("refresh_token")
            user_info = payload.get("user", {})

            if access_token:
                self.api_client.set_tokens(
                    access_token=access_token,
                    refresh_token=refresh_token,
                    user=user_info
                )

            return {
                "success": True,
                "message": resp_data.get("message", "Đăng nhập thành công!"),
                "data": payload,
                "user": user_info
            }
        # Xử lý lỗi trả về từ máy chủ Backend
        error_msg = resp_data.get("message", "Đăng nhập không thành công.")
        error_code = resp_data.get("error_code", f"HTTP_{resp.status_code}")
        return {
            "success": False,
            "message": error_msg,
            "error_code": error_code,
            "status_code": resp.status_code
        }

    def get_profile(self) -> Dict[str, Any]:
        """Fetches the current user profile from /auth/me."""
        try:
            resp = self.api_client.get("auth/me")
            if resp.status_code == 200:
                data = parse_json(resp)
                if data is not None:
                    return {"success": True, "data": data.get("data", data)}
            return {"success": False, "message": "Không thể lấy thông tin tài khoản."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def logout(self):
        """Clears local authentication state."""
        self.api_client.clear_tokens()

    def refresh_session(self) -> bool:
        """
        Manually rotates the token pair through the backend (IT22).
        Returns True when a fresh access token was obtained.
        """
        return self.api_client.refresh_access_token()
