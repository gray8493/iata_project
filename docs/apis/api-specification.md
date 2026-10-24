# Tài Liệu Đặc Tả API Chi Tiết (API Specification Document)

# Hệ Sinh Thái AITA (Automated Grading & Assessment Tool)

### Áp dụng cho: Web Server Backend (NestJS), Web Admin Dashboard (Next.js), Desktop App Client (PyQt6)

---

## 1. Nguyên Tắc Thiết Kế API & Chuẩn Dữ Liệu

### 1.1. Giao thức & Định dạng
- **Giao thức**: HTTPS / RESTful API chuẩn RFC 9110.
- **Định dạng dữ liệu**: `application/json; charset=utf-8`.
- **Mã hóa URL**: UTF-8.
- **Tiêu chuẩn phiên bản**: `/api/v1/...`.

### 1.2. Cơ Chế Xác Thực (Authentication Header)
Tất cả các endpoint (ngoại trừ các endpoint Public như Đăng nhập) đều yêu cầu đính kèm JSON Web Token trong Header:
```http
Authorization: Bearer <access_token>
```

### 1.2.1. Giới hạn tần suất yêu cầu
- API đã xác thực thông thường: tối đa 80 request/phút/User.
- Năm API tạo nội dung AI Hub (`generate-testcases`, `review-code`, `verify-plagiarism`, `evaluate-web-ui`, `evaluate-pe-code`): tối đa 15 request/phút/User.
- Đăng nhập: 10 request/phút/IP; refresh token: 30 request/phút/IP.
- Khi vượt giới hạn, backend trả HTTP 429 với `error_code: RATE_LIMIT_EXCEEDED`. Giới hạn này tách biệt với quota token AI theo ngày.

### 1.3. Cấu Trúc Khung Phản Hồi Chuẩn (Standard Response Envelope)
Mọi phản hồi từ hệ thống đều tuân thủ 2 mẫu vỏ bọc nhất quán:

#### Trường hợp THÀNH CÔNG (`success: true`) - HTTP 200, 201:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Thao tác thành công",
  "data": { ... },
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

#### Trường hợp THẤT BẠI / LỖI (`success: false`) - HTTP 400, 401, 403, 404, 422, 429, 500:
```json
{
  "success": false,
  "status_code": 400,
  "error_code": "ERROR_IDENTIFIER_CODE",
  "message": "Thông báo lỗi tiếng Việt hiển thị cho người dùng",
  "details": [
    {
      "field": "tên_trường",
      "issue": "Mô tả vi phạm ràng buộc dữ liệu"
    }
  ],
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

---

## 2. Danh Mục Các API Theo Phân Hệ

```text
+----------------------------------------------------------------------------------------------------+
| METHOD | ENDPOINT                             | PHÂN HỆ   | MÔ TẢ                                  |
+--------+--------------------------------------+-----------+----------------------------------------+
| POST   | /api/v1/auth/login                   | Auth      | Đăng nhập tài khoản & Nhận JWT Token   |
| GET    | /api/v1/auth/me                      | Auth      | Lấy thông tin tài khoản hiện tại       |
| POST   | /api/v1/auth/refresh                 | Auth      | Cấp lại Access Token mới               |
+--------+--------------------------------------+-----------+----------------------------------------+
| GET    | /api/v1/admin/users                  | Users     | Lấy danh sách tài khoản (Phân trang)   |
| POST   | /api/v1/admin/users                  | Users     | Tạo mới tài khoản Giảng viên           |
| GET    | /api/v1/admin/users/{id}             | Users     | Xem chi tiết tài khoản theo ID         |
| PUT    | /api/v1/admin/users/{id}             | Users     | Cập nhật thông tin / Khóa tài khoản    |
| DELETE | /api/v1/admin/users/{id}             | Users     | Xóa tài khoản người dùng               |
+--------+--------------------------------------+-----------+----------------------------------------+
| GET    | /api/v1/ai/quota                     | AI Hub    | Kiểm tra hạn ngạch Token AI hôm nay    |
| POST   | /api/v1/ai/generate-testcases        | AI Hub    | Sinh testcase biên tự động (UC-10)     |
| POST   | /api/v1/ai/review-code               | AI Hub    | Phân tích lỗi sư phạm On-Demand (UC-16)|
| POST   | /api/v1/ai/verify-plagiarism         | AI Hub    | Xác thực nghi vấn đạo văn >80% (UC-17) |
| POST   | /api/v1/ai/evaluate-web-ui           | AI Hub    | Đánh giá thẩm mỹ giao diện Web (UC-19) |
| POST   | /api/v1/ai/evaluate-pe-code          | AI Hub    | Chấm chất lượng code PE White-box (UC-19) |
+--------+--------------------------------------+-----------+----------------------------------------+
| GET    | /api/v1/admin/reports/overview       | Reports   | Thống kê kiểm toán người dùng & AI     |
| GET    | /api/v1/admin/reports/ai-usage       | Reports   | Nhật ký AI có lọc theo User/thời gian  |
+--------+--------------------------------------+-----------+----------------------------------------+
| GET    | /api/v1/ai/provider-status           | AI Hub    | Trạng thái key/model OpenRouter (Admin) |
| GET    | /api/v1/health                       | Health    | Kiểm tra API, PostgreSQL & rate-limit   |
| GET    | /api/v1/system/version               | System    | Manifest cập nhật Desktop App (Public)  |
+----------------------------------------------------------------------------------------------------+
```

---

## 3. Đặc Tả Chi Tiết Từng API

---

### 3.1. Phân Hệ Xác Thực (Authentication)

#### 3.1.1. `POST /api/v1/auth/login`
* **Mô tả**: Xác thực định danh tài khoản Quản trị viên hoặc Giảng viên, trả về cặp JWT tokens.
* **Xác thực**: Public (Không cần token).
* **Ràng buộc đầu vào (Input Constraints)**:
  - `username`: Kiểu chuỗi, độ dài từ 3 đến 50 ký tự, không chứa ký tự đặc biệt nguy hiểm, bắt buộc (`required`).
  - `password`: Kiểu chuỗi, độ dài từ 6 đến 100 ký tự, bắt buộc (`required`).

##### Body Input mẫu:
```json
{
  "username": "teacher_hung",
  "password": "Password123@"
}
```

##### Kịch bản THÀNH CÔNG (`success: true`) - HTTP 200 OK:
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

##### Kịch bản THẤT BẠI (`success: false`):
* **Sai mật khẩu hoặc tên đăng nhập** - HTTP 401 Unauthorized:
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

* **Tài khoản bị khóa bởi Admin** - HTTP 403 Forbidden:
```json
{
  "success": false,
  "status_code": 403,
  "error_code": "AUTH_ACCOUNT_DISABLED",
  "message": "Tài khoản của bạn đã bị vô hiệu hóa. Vui lòng liên hệ Quản trị viên.",
  "details": null,
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

* **Dữ liệu đầu vào không hợp lệ** - HTTP 422 Unprocessable Entity:
```json
{
  "success": false,
  "status_code": 422,
  "error_code": "VALIDATION_FAILED",
  "message": "Dữ liệu gửi lên không đúng định dạng.",
  "details": [
    {
      "field": "username",
      "issue": "Tên đăng nhập phải có ít nhất 3 ký tự."
    }
  ],
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

---

#### 3.1.2. `GET /api/v1/auth/me`
* **Mô tả**: Trả về thông tin hồ sơ của người dùng đang sở hữu Bearer token hiện tại.
* **Xác thực**: Yêu cầu `Authorization: Bearer <access_token>`.

##### Kịch bản THÀNH CÔNG (`success: true`) - HTTP 200 OK:
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

##### Kịch bản THẤT BẠI (`success: false`):
* **Token không hợp lệ hoặc hết hạn** - HTTP 401 Unauthorized:
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

#### 3.1.3. `POST /api/v1/auth/refresh`
* **Mô tả**: Sử dụng Refresh Token để gia hạn cặp Token mới mà không cần bắt người dùng đăng nhập lại.
* **Ràng buộc đầu vào (Input Constraints)**:
  - `refresh_token`: Kiểu chuỗi, bắt buộc (`required`).

##### Body Input mẫu:
```json
{
  "refresh_token": "def502005a76c8e3..."
}
```

##### Kịch bản THÀNH CÔNG (`success: true`) - HTTP 200 OK:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Gia hạn mã truy cập thành công",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "def502005a76c8e4...",
    "token_type": "Bearer",
    "expires_in": 900,
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "teacher_hung",
      "role": "INSTRUCTOR"
    }
  },
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

##### Kịch bản THẤT BẠI (`success: false`) - HTTP 401 Unauthorized:
```json
{
  "success": false,
  "status_code": 401,
  "error_code": "AUTH_INVALID_REFRESH_TOKEN",
  "message": "Mã gia hạn không hợp lệ hoặc đã bị thu hồi.",
  "details": null,
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

---

### 3.2. Phân Hệ Quản Lý Người Dùng (User Management - Admin Only)

#### 3.2.1. `GET /api/v1/admin/users`
* **Mô tả**: Lấy danh sách toàn bộ người dùng kèm phân trang và bộ lọc.
* **Xác thực**: Quyền Admin (`role == 'ADMIN'`).
* **Tham số Query (Query Constraints)**:
  - `page`: Số nguyên, tối thiểu 1, mặc định 1.
  - `page_size`: Số nguyên, từ 1 đến 100, mặc định 10.
  - `role`: Kiểu chuỗi, giá trị thuộc `["ADMIN", "INSTRUCTOR"]`, tùy chọn.
  - `search`: Kiểu chuỗi, tối đa 50 ký tự, tùy chọn (tìm theo username, email, full_name).

##### Kịch bản THÀNH CÔNG (`success: true`) - HTTP 200 OK:
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
        "full_name": "Quản Trị Viên Hệ Thống",
        "email": "admin@fe.edu.vn",
        "role": "ADMIN",
        "is_active": true,
        "daily_token_quota": 50000,
        "used_tokens_today": 0,
        "created_at": "2026-09-01T00:00:00.000Z"
      },
      {
        "id": "a8fdc8b6-c222-4e5d-bc2a-62e28800d247",
        "username": "teacher_hung",
        "full_name": "Nguyễn Văn Hùng",
        "email": "hungnv@fe.edu.vn",
        "role": "INSTRUCTOR",
        "is_active": true,
        "daily_token_quota": 50000,
        "used_tokens_today": 12450,
        "created_at": "2026-09-10T08:30:00.000Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total_items": 2,
      "total_pages": 1
    }
  },
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

##### Kịch bản THẤT BẠI (`success: false`):
* **Không đủ quyền truy cập** - HTTP 403 Forbidden:
```json
{
  "success": false,
  "status_code": 403,
  "error_code": "FORBIDDEN_ADMIN_ONLY",
  "message": "Bạn không có quyền truy cập vào chức năng quản trị này.",
  "details": null,
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

---

#### 3.2.2. `POST /api/v1/admin/users`
* **Mô tả**: Tạo mới tài khoản Giảng viên hoặc Quản trị viên.
* **Xác thực**: Quyền Admin (`role == 'ADMIN'`).
* **Ràng buộc đầu vào (Input Constraints)**:
  - `username`: Kiểu chuỗi, độ dài 3-30 ký tự, chỉ gồm chữ cái thường, số và gạch dưới `^[a-z0-9_]+$`, bắt buộc (`required`), là duy nhất.
  - `password`: Kiểu chuỗi, tối thiểu 8 ký tự, phải chứa ít nhất 1 chữ hoa, 1 chữ thường và 1 số, bắt buộc (`required`).
  - `full_name`: Kiểu chuỗi, độ dài 2-100 ký tự, bắt buộc (`required`).
  - `email`: Kiểu chuỗi, đúng định dạng email RFC 5322, bắt buộc (`required`), là duy nhất.
  - `role`: Kiểu chuỗi, giá trị hợp lệ: `"ADMIN"` hoặc `"INSTRUCTOR"`, bắt buộc (`required`).
  - `daily_token_quota`: Số nguyên, từ 0 trở lên, mặc định 50000.

##### Body Input mẫu:
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

##### Kịch bản THÀNH CÔNG (`success: true`) - HTTP 201 Created:
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
    "is_active": true,
    "created_at": "2026-09-30T12:00:00.000Z"
  },
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

##### Kịch bản THẤT BẠI (`success: false`):
* **Tên đăng nhập hoặc Email đã tồn tại** - HTTP 409 Conflict:
```json
{
  "success": false,
  "status_code": 409,
  "error_code": "USER_ALREADY_EXISTS",
  "message": "Tên đăng nhập hoặc địa chỉ email đã được sử dụng.",
  "details": [
    {
      "field": "username",
      "issue": "Tên đăng nhập 'teacher_lan' đã tồn tại."
    }
  ],
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

---

#### 3.2.3. `PUT /api/v1/admin/users/{id}`
* **Mô tả**: Chỉnh sửa thông tin hồ sơ, phân quyền hoặc khóa/mở khóa tài khoản.
* **Xác thực**: Quyền Admin (`role == 'ADMIN'`).
* **Tham số Path**: `id` (UUID, bắt buộc).
* **Ràng buộc đầu vào (Input Constraints)**:
  - `full_name`: Kiểu chuỗi, độ dài 2-100 ký tự, tùy chọn.
  - `email`: Định dạng email chuẩn, tùy chọn.
  - `role`: Giá trị thuộc `["ADMIN", "INSTRUCTOR"]`, tùy chọn.
  - `is_active`: Kiểu boolean (`true` / `false`), tùy chọn.
  - `daily_token_quota`: Số nguyên từ 0 trở lên, tùy chọn.

##### Body Input mẫu:
```json
{
  "full_name": "Trần Thị Lan (TS)",
  "is_active": false
}
```

##### Kịch bản THÀNH CÔNG (`success: true`) - HTTP 200 OK:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Cập nhật tài khoản thành công",
  "data": {
    "id": "a8fdc8b6-c222-4e5d-bc2a-62e28800d247",
    "username": "teacher_lan",
    "full_name": "Trần Thị Lan (TS)",
    "email": "lantt@fe.edu.vn",
    "role": "INSTRUCTOR",
    "is_active": false,
    "updated_at": "2026-09-30T12:05:00.000Z"
  },
  "timestamp": "2026-09-30T12:05:00.000Z"
}
```

##### Kịch bản THẤT BẠI (`success: false`):
* **Không tìm thấy người dùng** - HTTP 404 Not Found:
```json
{
  "success": false,
  "status_code": 404,
  "error_code": "USER_NOT_FOUND",
  "message": "Không tìm thấy người dùng với mã ID đã chỉ định.",
  "details": null,
  "timestamp": "2026-09-30T12:05:00.000Z"
}
```

---

### 3.3. Phân Hệ AI Gateway & Quản Lý Hạn Ngạch (AI Hub API)

#### 3.3.1. `GET /api/v1/ai/quota`
* **Mô tả**: Trả về thống kê hạn ngạch tiêu thụ Token AI hôm nay của Giảng viên.
* **Xác thực**: Yêu cầu Bearer Token.

##### Kịch bản THÀNH CÔNG (`success: true`) - HTTP 200 OK:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Lấy thông tin hạn ngạch AI thành công",
  "data": {
    "daily_limit_tokens": 50000,
    "used_tokens_today": 12450,
    "remaining_tokens": 37550,
    "reset_at_utc": "2026-10-01T00:00:00.000Z"
  },
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

---

#### 3.3.2. `POST /api/v1/ai/generate-testcases` (UC-10)
* **Mô tả**: Gọi AI Hub để tự động sinh testcase biên (Boundary Testcases) dựa trên đề bài.
* **Xác thực**: Giảng viên (`role == 'INSTRUCTOR'`).
* **Ràng buộc đầu vào (Input Constraints)**:
  - `problem_description`: Kiểu chuỗi, độ dài từ 20 đến 5000 ký tự, bắt buộc (`required`).
  - `language`: Giá trị hợp lệ: `"C"`, `"JAVA"`, `"PYTHON"`, `"WEB"`, bắt buộc (`required`).
  - `count`: Số nguyên, từ 1 đến 10 testcase, mặc định 3.
  - `include_boundary`: Kiểu boolean, mặc định `true`.

##### Body Input mẫu:
```json
{
  "problem_description": "Viết chương trình nhập vào số nguyên dương N (1 <= N <= 10^6). Tính tổng các ước số của N.",
  "language": "C",
  "count": 3,
  "include_boundary": true
}
```

##### Kịch bản THÀNH CÔNG (`success: true`) - HTTP 200 OK:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Sinh testcase tự động bằng AI thành công",
  "data": {
    "tokens_consumed": 420,
    "testcases": [
      {
        "input": "1",
        "expected_output": "1",
        "explanation": "Biên dưới nhỏ nhất N = 1",
        "is_boundary": true
      },
      {
        "input": "1000000",
        "expected_output": "2480437",
        "explanation": "Biên trên tối đa N = 10^6",
        "is_boundary": true
      },
      {
        "input": "999983",
        "expected_output": "999984",
        "explanation": "Số nguyên tố lớn (chỉ có ước là 1 và chính nó)",
        "is_boundary": true
      }
    ]
  },
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

##### Kịch bản THẤT BẠI (`success: false`):
* **Hết hạn ngạch Token trong ngày** - HTTP 429 Too Many Requests:
```json
{
  "success": false,
  "status_code": 429,
  "error_code": "AI_QUOTA_EXCEEDED",
  "message": "Tài khoản của bạn đã sử dụng hết hạn ngạch Token AI trong ngày (50,000/50,000 tokens). Vui lòng liên hệ Quản trị viên để cấp thêm quota hoặc đợi sang ngày hôm sau.",
  "details": {
    "daily_limit": 50000,
    "current_usage": 50000,
    "reset_at": "2026-10-01T00:00:00.000Z"
  },
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

---

#### 3.3.3. `POST /api/v1/ai/review-code` (UC-16)
* **Mô tả**: Phân tích nguyên nhân lỗi và sinh nhận xét sư phạm On-Demand cho bài nộp bị `WA` (Wrong Answer).
* **Xác thực**: Giảng viên (`role == 'INSTRUCTOR'`).
* **Ràng buộc đầu vào (Input Constraints)**:
  - `source_code`: Mã nguồn sinh viên, độ dài 10 đến 10000 ký tự, bắt buộc (`required`).
  - `language`: `"C"`, `"JAVA"`, `"PYTHON"`, `"PHP"`, bắt buộc.
  - `problem_statement`: Đề bài, tối đa 3000 ký tự, bắt buộc.
  - `failed_testcase`: Object chứa `input`, `expected_output`, `actual_output`, bắt buộc.

##### Body Input mẫu:
```json
{
  "source_code": "#include <stdio.h>\nint main() {\n  int n; scanf(\"%d\", &n);\n  int sum = 0;\n  for(int i=1; i<n; i++) if(n%i==0) sum+=i;\n  printf(\"%d\", sum);\n  return 0;\n}",
  "language": "C",
  "problem_statement": "Tính tổng tất cả các ước số của số nguyên dương N (bao gồm cả N).",
  "failed_testcase": {
    "input": "6",
    "expected_output": "12",
    "actual_output": "6"
  }
}
```

##### Kịch bản THÀNH CÔNG (`success: true`) - HTTP 200 OK:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Phân tích mã nguồn bằng AI thành công",
  "data": {
    "tokens_consumed": 380,
    "suspected_error_line": 5,
    "issue_summary": "Thiếu ước số chính là N do điều kiện dừng vòng lặp là i < n thay vì i <= n.",
    "pedagogical_feedback": "Em đã xử lý đúng thuật toán duyệt ước, tuy nhiên đề bài yêu cầu tính cả chính số N. Em hãy kiểm tra lại điều kiện vòng for(i=1; i<=n; i++) nhé.",
    "bug_category": "OFF_BY_ONE_ERROR"
  },
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

---

#### 3.3.4. `POST /api/v1/ai/verify-plagiarism` (UC-17 Vòng 2)
* **Mô tả**: Phân tích ngữ nghĩa chuyên sâu cặp bài nộp có độ tương đồng AST > 80% để trích xuất bằng chứng sao chép.
* **Xác thực**: Giảng viên (`role == 'INSTRUCTOR'`).
* **Ràng buộc đầu vào (Input Constraints)**:
  - `student_a_code`: Mã nguồn bài nộp 1 (string, 10 - 10000 ký tự).
  - `student_b_code`: Mã nguồn bài nộp 2 (string, 10 - 10000 ký tự).
  - `ast_similarity_percentage`: Số thực, từ 80.0 đến 100.0, bắt buộc.
  - `language`: Ngôn ngữ lập trình, thuộc enum `["C", "JAVA", "PYTHON", "PHP"]`, bắt buộc.

##### Kịch bản THÀNH CÔNG (`success: true`) - HTTP 200 OK:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Đối soát đạo văn bằng AI hoàn tất",
  "data": {
    "tokens_consumed": 510,
    "ket_luan": "Hai đoạn mã có nhiều dấu hiệu sao chép có chủ đích.",
    "do_tin_cay": 94.8,
    "bang_chung": [
      {
        "mo_ta": "Cùng đổi tên biến n -> m, sum -> total nhưng cấu trúc lặp giống hệt.",
        "dong_a": [5, 9],
        "dong_b": [6, 10]
      }
    ],
    "khac_biet": ["Phần xử lý lỗi đầu vào ở cuối hai chương trình khác nhau."],
    "de_xuat": ["Yêu cầu sinh viên giải thích thuật toán trước hội đồng."]
  },
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

---

#### 3.3.5. `POST /api/v1/ai/evaluate-web-ui` (UC-19 Web Multimodal)
* **Mô tả**: Đánh giá thẩm mỹ và độ tương thích giao diện trang web bài thi qua ảnh chụp màn hình bằng AI Vision (Central AI Gateway gọi OpenRouter).
* **Xác thực**: Giảng viên (`role == 'INSTRUCTOR'`).
* **Ràng buộc đầu vào (Input Constraints)**:
  - `screenshot_base64`: Chuỗi base64 ảnh chụp màn hình (PNG/JPEG, tối đa 5MB), bắt buộc (`required`).
  - `rubric_requirements`: Mảng các chuỗi tiêu chí đề bài, tối thiểu 1 tiêu chí, bắt buộc.

##### Body Input mẫu:
```json
{
  "screenshot_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "rubric_requirements": [
    "Bố cục cân đối có thanh điều hướng navbar trên đầu",
    "Form đăng ký gồm 3 input và nút bấm nổi bật",
    "Phối màu hài hòa, có độ tương phản văn bản tốt"
  ]
}
```

##### Kịch bản THÀNH CÔNG (`success: true`) - HTTP 200 OK:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Đánh giá giao diện Web bằng AI thành công",
  "data": {
    "tokens_consumed": 720,
    "ui_score": 8.5,
    "evaluation_details": [
      {
        "criterion": "Bố cục cân đối có thanh điều hướng navbar trên đầu",
        "score": 10.0,
        "verdict": "PASS",
        "comment": "Navbar thiết kế rõ ràng, logo bên trái và link bên phải chuẩn mực.",
        "bounding_box": [0, 0, 1280, 64]
      },
      {
        "criterion": "Form đăng ký gồm 3 input và nút bấm nổi bật",
        "score": 8.0,
        "verdict": "PASS",
        "comment": "Có đủ input nhưng khoảng cách padding giữa các trường hơi sát nhau.",
        "bounding_box": [320, 240, 640, 320]
      }
    ],
    "overall_feedback": "Trang web có bố cục hài hòa, màu sắc nhã nhặn, đáp ứng tốt yêu cầu đề thi."
  },
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

---

#### 3.3.6. `POST /api/v1/ai/evaluate-pe-code` (Chấm chất lượng mã nguồn PE)
* **Mô tả**: Đánh giá mã nguồn bài thực hành theo 5 tiêu chí Rubric White-box (`clean_code`, `complexity`, `structure`, `format`, `documentation`) — mỗi tiêu chí PASS = 1.0 điểm, tối đa 5.0.
* **Xác thực**: Yêu cầu Bearer Token; giới hạn 15 request/phút.
* **Ràng buộc đầu vào (Input Constraints)**:
  - `source_code`: Mã nguồn sinh viên, chuỗi 10 - 20000 ký tự, bắt buộc (`required`).
  - `language`: Thuộc enum `["C", "JAVA", "PYTHON", "PHP"]`, bắt buộc (`required`).
  - `problem_statement`: mô tả đề bài, tùy chọn (tối đa 5000 ký tự).

##### Kịch bản THÀNH CÔNG (`success: true`) - HTTP 200 OK:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Đánh giá chất lượng code PE thành công",
  "data": {
    "tokens_consumed": 950,
    "rubric": {
      "clean_code": { "passed": true, "reason": "Không có biến/hàm đặt tên trùng lặp." },
      "complexity": { "passed": false, "reason": "Vòng lặp lồng 3 cấp ở hàm main." },
      "structure": { "passed": true, "reason": "Tách hàm xử lý đầu vào và tính toán rõ ràng." },
      "format": { "passed": true, "reason": "Thụt lề và ngoặc nhất quán." },
      "documentation": { "passed": false, "reason": "Thiếu chú thích hàm chính." }
    },
    "overall_feedback": "Bài làm đạt 3/5 tiêu chí, cần giảm độ phức tạp lồng nhau và bổ sung chú thích."
  },
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

---

#### 3.3.7. `GET /api/v1/ai/provider-status` (Chỉ ADMIN)
* **Mô tả**: Trạng thái nhà cung cấp AI (OpenRouter): model chính, model dự phòng, danh sách account key kèm trạng thái `READY`/`COOLDOWN` và thời gian cooldown còn lại.
* **Xác thực**: Quyền Admin (`role == 'ADMIN'`).

##### Kịch bản THÀNH CÔNG (`success: true`) - HTTP 200 OK:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Lấy trạng thái AI Hub thành công",
  "data": {
    "provider": "openrouter",
    "model": "google/gemma-4-31b-it:free",
    "fallback_models": ["google/gemma-4-26b-a4b-it:free"],
    "accounts_configured": 3,
    "structured_outputs_supported": true,
    "accounts": [
      { "account": "ACC-01", "key_hint": "sk-or-v1-…fbea", "state": "READY", "cooldown_remaining_seconds": 0 },
      { "account": "ACC-02", "key_hint": "sk-or-v1-…81ac", "state": "COOLDOWN", "cooldown_remaining_seconds": 42 }
    ]
  },
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

---

### 3.4. Phân Hệ Báo Cáo & Kiểm Toán Hệ Thống (Audit & Reports API - Admin Only)

#### 3.4.1. `GET /api/v1/admin/reports/overview`
* **Mô tả**: Trả về số liệu thống kê tổng thể toàn trường cho Quản trị viên trên Web Admin Dashboard (UC-05).
* **Xác thực**: Quyền Admin (`role == 'ADMIN'`).

##### Kịch bản THÀNH CÔNG (`success: true`) - HTTP 200 OK:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Lấy số liệu thống kê tổng quan thành công",
  "data": {
    "total_instructors": 24,
    "ai_token_usage": {
      "total_tokens_consumed_month": 1285000,
      "total_budget_limit": 5000000,
      "top_consuming_feature": "TESTCASE_GEN"
    }
  },
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

##### Kịch bản THẤT BẠI (`success: false`) - HTTP 403 Forbidden:
```json
{
  "success": false,
  "status_code": 403,
  "error_code": "FORBIDDEN_ADMIN_ONLY",
  "message": "Chỉ Quản trị viên mới có quyền xem báo cáo thống kê này.",
  "details": null,
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

---

### 3.5. Phân Hệ Sức Khỏe & Hệ Thống (Health & System API - Công khai)

#### 3.5.1. `GET /api/v1/health`
* **Mô tả**: Kiểm tra trạng thái API, kết nối PostgreSQL (`SELECT 1`) và kho rate-limit. Public, không cần Bearer Token.
* **Mã lỗi kèm theo**: `503` `RATE_LIMIT_STORAGE_UNAVAILABLE` khi kho rate-limit (Redis) không khả dụng.

##### Kịch bản THÀNH CÔNG (`success: true`) - HTTP 200 OK:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Dịch vụ đang hoạt động",
  "data": {
    "status": "ok",
    "database": "ok",
    "rate_limit_storage": "memory"
  },
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

#### 3.5.2. `GET /api/v1/system/version`
* **Mô tả**: Trả về manifest cập nhật cho Desktop Client (Auto-Update). Public, không cần Bearer Token. Nguồn ưu tiên là release mới nhất trên GitHub (`APP_UPDATE_SOURCE=github`), fallback về biến môi trường `APP_UPDATE_*`.

##### Kịch bản THÀNH CÔNG (`success: true`) - HTTP 200 OK:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Lấy thông tin phiên bản thành công",
  "data": {
    "latest_version": "1.0.0",
    "min_supported_version": "1.0.0",
    "mandatory": false,
    "notes": "- Sửa lỗi chấm bài Java",
    "published_at": "2026-10-19T00:00:00Z",
    "platforms": {
      "windows": {
        "artifact_type": "zip",
        "url": "https://github.com/gray8493/iata_project/releases/download/v1.0.0/AITA_Grader_v1.zip",
        "sha256": "6f1c0f0e1a2b3c4d5e6f70819293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5",
        "size_bytes": 157286400,
        "entrypoint": "AITA_Grader_v1.exe"
      }
    }
  },
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```
