# Đặc Tả API: Phân Hệ Xác Thực (Authentication API)

### Thư mục: `docs/apis/auth/`
### Phân hệ: Web Server Backend (NestJS Auth Module)

---

## 1. Danh Sách Endpoints (3 APIs)

| Method | Endpoint | Quyền hạn | Mô tả |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/login` | Public | Đăng nhập tài khoản, trả về JWT Access Token & Refresh Token |
| `GET` | `/api/v1/auth/me` | Bearer Token | Lấy thông tin tài khoản đang đăng nhập |
| `POST` | `/api/v1/auth/refresh` | Public | Cấp mới Access Token bằng Refresh Token |

---

## 2. Chi Tiết Từng API

### 2.1. `POST /api/v1/auth/login`
- **Mục đích**: Xác thực thông tin đăng nhập của Admin hoặc Giảng viên.
- **Headers**: `Content-Type: application/json`
- **Ràng buộc đầu vào (Validation Rules)**:
  - `username`: String, min 3, max 50 ký tự, bắt buộc (`required`).
  - `password`: String, min 6, max 100 ký tự, bắt buộc (`required`).

#### Body Input mẫu:
```json
{
  "username": "teacher_hung",
  "password": "Password123@"
}
```

#### Kịch bản phản hồi:
* **Thành công (`success: true`) - HTTP 200 OK**:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Đăng nhập thành công",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "def502005a76c8e3...",
    "token_type": "Bearer",
    "expires_in": 900,
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "teacher_hung",
      "full_name": "Nguyễn Văn Hùng",
      "email": "hungnv@fe.edu.vn",
      "role": "INSTRUCTOR",
      "is_active": true
    }
  },
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

* **Thất bại (`success: false`) - HTTP 401 Unauthorized**:
```json
{
  "success": false,
  "status_code": 401,
  "error_code": "AUTH_INVALID_CREDENTIALS",
  "message": "Tên đăng nhập hoặc mật khẩu không chính xác.",
  "details": null,
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

* **Thất bại (`success: false`) - HTTP 403 Forbidden (Tài khoản bị khóa)**:
```json
{
  "success": false,
  "status_code": 403,
  "error_code": "AUTH_ACCOUNT_DISABLED",
  "message": "Tài khoản của bạn đã bị vô hiệu hóa.",
  "details": null,
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

---

### 2.2. `GET /api/v1/auth/me`
- **Mục đích**: Lấy thông tin tài khoản hiện tại từ Token.
- **Headers**: `Authorization: Bearer <access_token>`

#### Kịch bản phản hồi:
* **Thành công (`success: true`) - HTTP 200 OK**:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Lấy thông tin tài khoản thành công",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "teacher_hung",
    "full_name": "Nguyễn Văn Hùng",
    "email": "hungnv@fe.edu.vn",
    "role": "INSTRUCTOR",
    "is_active": true,
    "created_at": "2026-09-01T08:00:00.000Z"
  },
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

* **Thất bại (`success: false`) - HTTP 401 Unauthorized**:
```json
{
  "success": false,
  "status_code": 401,
  "error_code": "AUTH_TOKEN_EXPIRED",
  "message": "Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại.",
  "details": null,
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

---

### 2.3. `POST /api/v1/auth/refresh`
- **Mục đích**: Cấp mới Access Token.
- **Ràng buộc đầu vào**: `refresh_token` (string, bắt buộc).

#### Kịch bản phản hồi:
* **Thành công (`success: true`) - HTTP 200 OK**:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Gia hạn mã truy cập thành công",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "def502005a76c8e4...",
    "token_type": "Bearer",
    "expires_in": 900
  },
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

* **Thất bại (`success: false`) - HTTP 401 Unauthorized**:
```json
{
  "success": false,
  "status_code": 401,
  "error_code": "AUTH_INVALID_REFRESH_TOKEN",
  "message": "Mã refresh token không hợp lệ hoặc đã hết hạn.",
  "details": null,
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```
