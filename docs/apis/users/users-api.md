# Đặc Tả API: Phân Hệ Quản Lý Người Dùng (Users API - Admin Only)

### Thư mục: `docs/apis/users/`
### Phân hệ: Web Server Backend (NestJS Users Module) & Web Admin Dashboard

---

## 1. Danh Sách Endpoints (5 APIs)

| Method | Endpoint | Quyền hạn | Mô tả |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/admin/users` | Admin | Lấy danh sách tài khoản phân trang |
| `POST` | `/api/v1/admin/users` | Admin | Tạo mới tài khoản Giảng viên / Admin |
| `GET` | `/api/v1/admin/users/{id}` | Admin | Xem chi tiết thông tin tài khoản theo ID |
| `PUT` | `/api/v1/admin/users/{id}` | Admin | Cập nhật thông tin / Khóa tài khoản |
| `DELETE` | `/api/v1/admin/users/{id}` | Admin | Xóa tài khoản người dùng |

---

## 2. Chi Tiết Từng API & Ràng Buộc Dữ Liệu

### 2.1. `GET /api/v1/admin/users`
- **Mục đích**: Lấy danh sách tài khoản phục vụ màn hình Admin User Management.
- **Ràng buộc tham số (Query Params)**:
  - `page`: int >= 1 (mặc định 1).
  - `page_size`: int 1-100 (mặc định 10).
  - `role`: enum `["ADMIN", "INSTRUCTOR"]` (tùy chọn).
  - `search`: string max 50 ký tự (tùy chọn).

#### Kịch bản phản hồi:
* **Thành công (`success: true`) - HTTP 200 OK**:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Lấy danh sách người dùng thành công",
  "data": {
    "items": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "admin",
        "full_name": "Quản Trị Viên",
        "email": "admin@fe.edu.vn",
        "role": "ADMIN",
        "is_active": true,
        "created_at": "2026-09-01T00:00:00.000Z"
      }
    ],
    "pagination": { "page": 1, "page_size": 10, "total_items": 1, "total_pages": 1 }
  },
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

* **Thất bại (`success: false`) - HTTP 403 Forbidden**:
```json
{
  "success": false,
  "status_code": 403,
  "error_code": "FORBIDDEN_ADMIN_ONLY",
  "message": "Chỉ Quản trị viên mới có quyền truy cập.",
  "details": null,
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

---

### 2.2. `POST /api/v1/admin/users`
- **Mục đích**: Admin tạo tài khoản cho Giảng viên.
- **Ràng buộc đầu vào (Validation Constraints)**:
  - `username`: 3-30 ký tự, regex `^[a-z0-9_]+$`, duy nhất (`unique`), bắt buộc.
  - `password`: Tối thiểu 8 ký tự, có chữ hoa, thường và số, bắt buộc.
  - `full_name`: 2-100 ký tự, bắt buộc.
  - `email`: Định dạng email RFC 5322, duy nhất (`unique`), bắt buộc.
  - `role`: `"ADMIN"` hoặc `"INSTRUCTOR"`, bắt buộc.
  - `daily_token_quota`: Số nguyên từ 1,000 đến 1,000,000 (mặc định 50,000).

#### Body Input mẫu:
```json
{
  "username": "teacher_lan",
  "password": "LanPassword2026@",
  "full_name": "Trần Thị Lan",
  "email": "lantt@fe.edu.vn",
  "role": "INSTRUCTOR",
  "daily_token_quota": 60000
}
```

#### Kịch bản phản hồi:
* **Thành công (`success: true`) - HTTP 201 Created**:
```json
{
  "success": true,
  "status_code": 201,
  "message": "Tạo tài khoản người dùng mới thành công",
  "data": {
    "id": "a8fdc8b6-c222-4e5d-bc2a-62e28800d247",
    "username": "teacher_lan",
    "full_name": "Trần Thị Lan",
    "email": "lantt@fe.edu.vn",
    "role": "INSTRUCTOR",
    "is_active": true
  },
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

* **Thất bại (`success: false`) - HTTP 409 Conflict (Trùng username/email)**:
```json
{
  "success": false,
  "status_code": 409,
  "error_code": "USER_ALREADY_EXISTS",
  "message": "Tên đăng nhập hoặc email đã tồn tại.",
  "details": [
    { "field": "username", "issue": "Tên 'teacher_lan' đã được sử dụng." }
  ],
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

---

### 2.3. `PUT /api/v1/admin/users/{id}`
- **Mục đích**: Cập nhật thông tin hoặc Khóa/Mở khóa tài khoản.
- **Ràng buộc**: `id` là UUID.
- Các trường `username`, `password`, `full_name`, `email`, `role`, `is_active` và `daily_token_quota` có thể được cập nhật tùy chọn; mật khẩu mới được băm trước khi lưu.
- `daily_token_quota` nếu có phải từ 1000 đến 1000000 token/ngày.

#### Kịch bản phản hồi:
* **Thành công (`success: true`) - HTTP 200 OK**:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Cập nhật tài khoản thành công",
  "data": {
    "id": "a8fdc8b6-c222-4e5d-bc2a-62e28800d247",
    "username": "teacher_lan",
    "is_active": false
  },
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

* **Thất bại (`success: false`) - HTTP 404 Not Found**:
```json
{
  "success": false,
  "status_code": 404,
  "error_code": "USER_NOT_FOUND",
  "message": "Không tìm thấy người dùng với ID đã chỉ định.",
  "details": null,
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

---

### 2.4. `DELETE /api/v1/admin/users/{id}`
- **Mục đích**: Xóa tài khoản khỏi hệ thống.
- **Thành công (`success: true`) - HTTP 200 OK**:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Xóa người dùng thành công",
  "data": null,
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```
