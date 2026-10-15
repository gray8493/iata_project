"""
AITA Desktop Client - Authentication Service
Handles login, token management, session validation with the Central Backend.
"""

from typing import Dict, Any, Optional
import httpx
from .api_client import ApiClient


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
        try:
            resp = self.api_client.post("auth/login", {
                "username": username.strip(),
                "password": password
            })
            
            resp_data = resp.json() if resp.content else {}
            
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
        except Exception as e:
            return {
                "success": False,
                "message": f"Lỗi hệ thống khi đăng nhập: {str(e)}",
                "error_code": "INTERNAL_EXCEPTION"
            }

    def get_profile(self) -> Dict[str, Any]:
        """Fetches the current user profile from /auth/me."""
        try:
            resp = self.api_client.get("auth/me")
            if resp.status_code == 200:
                data = resp.json()
                return {"success": True, "data": data.get("data", data)}
            return {"success": False, "message": "Không thể lấy thông tin tài khoản."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def logout(self):
        """Clears local authentication state."""
        self.api_client.clear_tokens()
