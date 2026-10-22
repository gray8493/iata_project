# Thông Tin Chung Kiểm Thử Unit Test

- **Phân hệ kiểm thử**: Phân hệ Xác thực Tài khoản & Quản lý Phiên làm việc (Authentication API)
- **Danh sách API kiểm thử**:
  - `POST /api/v1/auth/login` (UC-01: Đăng nhập tài khoản, trả về JWT Access Token & Refresh Token)
  - `GET /api/v1/auth/me` (UC-02: Lấy thông tin tài khoản đang đăng nhập từ Access Token)
  - `POST /api/v1/auth/refresh` (UC-03: Cấp mới Access Token bằng Refresh Token)
- **Người thực hiện (Tester/Dev)**: Kim Chi Ha
- **Ngày tạo**: 05/10/2026
- **Cập nhật lần cuối**: 17/10/2026 - 09:00
- **Tài liệu liên quan**:
  - [Đặc tả API Phân hệ Xác thực (Markdown)](file:///e:/AITA/docs/apis/auth/auth-api.md)
  - [Đặc tả OpenAPI Phân hệ Xác thực (YAML)](file:///e:/AITA/docs/apis/auth/auth.yaml)
  - [Bảng Danh mục Mã lỗi Phản hồi Hệ thống](file:///e:/AITA/docs/architecture/api-response-codes.md)
  - [Quy tắc kiểm thử Testcase](file:///e:/AITA/rules/testcase-rules.md)
- **Tổng số Testcase**: 42 Testcases (Phân loại: 06 Normal, 10 Boundary, 26 Exception)
  - `POST /api/v1/auth/login`: 20 Testcases (02 Normal, 08 Boundary, 10 Exception)
  - `GET /api/v1/auth/me`: 10 Testcases (02 Normal, 01 Boundary, 07 Exception)
  - `POST /api/v1/auth/refresh`: 12 Testcases (02 Normal, 01 Boundary, 09 Exception)

> **Ghi chú thiết kế (khớp mã nguồn `AuthService`, `LoginDto`, `RefreshTokenDto`)**:
>
> - `LoginDto`: `username` là chuỗi, độ dài `3..50`; `password` là chuỗi, độ dài `6..100`. Mọi thông điệp validation là **mặc định của class-validator (tiếng Anh)**.
> - `RefreshTokenDto`: chỉ có `refresh_token` với ràng buộc `@IsJWT()`.
> - Thứ tự kiểm tra trong `login`: tìm user → `bcrypt.compare` → nếu sai ném `AUTH_INVALID_CREDENTIALS` (401) → nếu đúng nhưng `is_active = false` ném `AUTH_ACCOUNT_DISABLED` (403).
> - `JWT_ACCESS_EXPIRES_IN` mặc định `15m` ⇒ `expires_in = 900` (refresh dùng `JWT_REFRESH_EXPIRES_IN` mặc định `7d`).
> - `refresh` dùng chung một mã lỗi `AUTH_INVALID_REFRESH_TOKEN` (401) cho mọi trường hợp thất bại (token sai, hết hạn, đã thu hồi, tài khoản bị xóa/khóa).
> - Guard lỗi xác thực: thiếu/sai token ⇒ `AUTH_INVALID_TOKEN`; hết hạn ⇒ `AUTH_TOKEN_EXPIRED`; tài khoản không hoạt động ⇒ `AUTH_ACCOUNT_DISABLED`.

---

# ==============================================================================

# PHẦN 1: API POST /api/v1/auth/login (UC-01: ĐĂNG NHẬP HỆ THỐNG)

# ==============================================================================

# UT01_AuthLogin_TC001: Đăng nhập thành công với tài khoản Quản trị viên (ADMIN)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Tài khoản `admin` tồn tại, `is_active = true`, `is_deleted = false`, `role = "ADMIN"`.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ "username": "admin", "password": "AdminPassword2026@" }`

#### Các bước thực hiện (Test Steps)

1. Thiết lập `prisma.user.findFirst` trả user ADMIN; `bcrypt.compare` trả `true`.
2. Gọi hàm `AuthService.login(dto)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200 OK`, `message = "Đăng nhập thành công"`.
- `data.access_token`, `data.refresh_token` được cấp; `data.token_type = "Bearer"`; `data.expires_in = 900` (mặc định `15m`).
- `data.user.role = "ADMIN"`, `data.user.is_active = true`.
- Một bản ghi `refreshToken` được tạo trong CSDL.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthLogin_TC002: Đăng nhập thành công với tài khoản Giảng viên (INSTRUCTOR)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Tài khoản `teacher_hung` tồn tại, `is_active = true`, `role = "INSTRUCTOR"`.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ "username": "teacher_hung", "password": "Password123@" }`

#### Các bước thực hiện (Test Steps)

1. Thiết lập `prisma.user.findFirst` trả user INSTRUCTOR; `bcrypt.compare` trả `true`.
2. Gọi hàm `AuthService.login(dto)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200 OK`; `data.user.role = "INSTRUCTOR"`; cấp đủ cặp token.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthLogin_TC003: Đăng nhập thất bại do sai mật khẩu

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Tài khoản `teacher_hung` tồn tại, đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ "username": "teacher_hung", "password": "WrongPassword999@" }`

#### Các bước thực hiện (Test Steps)

1. Thiết lập `prisma.user.findFirst` trả user; `bcrypt.compare` trả `false`.
2. Gọi hàm `AuthService.login(dto)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401 Unauthorized`.
- `error_code = "AUTH_INVALID_CREDENTIALS"`, `message = "Tên đăng nhập hoặc mật khẩu không chính xác."`, `details = null`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthLogin_TC004: Đăng nhập thất bại do tên đăng nhập không tồn tại

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Tên `nonexistent_user` không tồn tại trong bảng `users`.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ "username": "nonexistent_user", "password": "Password123@" }`

#### Các bước thực hiện (Test Steps)

1. Thiết lập `prisma.user.findFirst` trả `null`.
2. Gọi hàm `AuthService.login(dto)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401 Unauthorized`, `error_code = "AUTH_INVALID_CREDENTIALS"`, `message = "Tên đăng nhập hoặc mật khẩu không chính xác."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthLogin_TC005: Đăng nhập thất bại do tài khoản đã bị khóa (mật khẩu đúng)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Tài khoản `teacher_locked` tồn tại, `is_active = false`; mật khẩu khớp hash.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ "username": "teacher_locked", "password": "CorrectPassword123@" }`

#### Các bước thực hiện (Test Steps)

1. Thiết lập `prisma.user.findFirst` trả user `is_active = false`; `bcrypt.compare` trả `true`.
2. Gọi hàm `AuthService.login(dto)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `403 Forbidden`, `error_code = "AUTH_ACCOUNT_DISABLED"`, `message = "Tài khoản của bạn đã bị vô hiệu hóa."`, `details = null`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthLogin_TC006: Tài khoản bị khóa nhưng mật khẩu sai (ưu tiên sai thông tin đăng nhập)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Tài khoản `teacher_locked` tồn tại, `is_active = false`.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ "username": "teacher_locked", "password": "WrongPassword999@" }`

#### Các bước thực hiện (Test Steps)

1. Thiết lập `prisma.user.findFirst` trả user `is_active = false`; `bcrypt.compare` trả `false`.
2. Gọi hàm `AuthService.login(dto)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401 Unauthorized`, `error_code = "AUTH_INVALID_CREDENTIALS"` (do mật khẩu được kiểm tra TRƯỚC trạng thái khóa).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthLogin_TC007: Lỗi máy chủ nội bộ khi truy vấn CSDL đăng nhập

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Dịch vụ CSDL bị ngắt kết nối giả lập.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ "username": "teacher_hung", "password": "Password123@" }`

#### Các bước thực hiện (Test Steps)

1. Thiết lập `prisma.user.findFirst` ném `Error('Connection refused')`.
2. Gọi hàm `AuthService.login(dto)`; cho `ApiExceptionFilter` bắt ngoại lệ.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `500 Internal Server Error`, `error_code = "INTERNAL_SERVER_ERROR"`, `message = "Đã xảy ra lỗi hệ thống."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthLogin_TC008: Request Body rỗng thiếu cả username và password

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{}`

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform({}, { type: 'body', metatype: LoginDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422 Unprocessable Entity`, `error_code = "VALIDATION_FAILED"`.
- `details` chứa `field = "username"` và `field = "password"` với `issues` là thông điệp mặc định (`"username must be a string"`, `"password must be a string"`).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthLogin_TC009: Thiếu trường bắt buộc username

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ "password": "Password123@" }`

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform({ password: 'Password123@' }, { type: 'body', metatype: LoginDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details = [{ field: "username", issues: ["username must be a string"] }]`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthLogin_TC010: Thiếu trường bắt buộc password

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ "username": "teacher_hung" }`

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform({ username: 'teacher_hung' }, { type: 'body', metatype: LoginDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details = [{ field: "password", issues: ["password must be a string"] }]`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthLogin_TC011: Trường username sai kiểu dữ liệu (gửi số)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ "username": 123456, "password": "Password123@" }`

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform({ username: 123456, password: 'Password123@' }, { type: 'body', metatype: LoginDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "username", issues: ["username must be a string"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthLogin_TC012: Trường password sai kiểu dữ liệu (gửi mảng)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ "username": "teacher_hung", "password": ["Pass123", "Secret"] }`

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform({ username: 'teacher_hung', password: ['Pass123', 'Secret'] }, { type: 'body', metatype: LoginDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "password", issues: ["password must be a string"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthLogin_TC013: username dài 2 ký tự (vi phạm biên dưới minLength = 3)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ "username": "th", "password": "Password123@" }`

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform({ username: 'th', password: 'Password123@' }, { type: 'body', metatype: LoginDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "username", issues: ["username must be longer than or equal to 3 characters"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthLogin_TC014: username dài đúng 3 ký tự (biên dưới hợp lệ)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Tài khoản `adm` tồn tại, `is_active = true`.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ "username": "adm", "password": "Adm12@" }`

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(...)` — không ném lỗi.
2. `prisma.user.findFirst` trả user; `bcrypt.compare` trả `true`; gọi `AuthService.login(dto)`.

#### Kết quả kỳ vọng (Expected Result)

- Validation hợp lệ, HTTP `200 OK`, cấp token và `data.user.username = "adm"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthLogin_TC015: username dài đúng 50 ký tự (biên trên hợp lệ)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Tài khoản với username 50 ký tự tồn tại, `is_active = true`.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ "username": "teacher_hung_exact_fifty_characters_username_aita", "password": "Password123@" }` (username đúng 50 ký tự)

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(...)` — không ném lỗi.
2. `prisma.user.findFirst` trả user; `bcrypt.compare` trả `true`; gọi `AuthService.login(dto)`.

#### Kết quả kỳ vọng (Expected Result)

- Validation hợp lệ, HTTP `200 OK`, cấp token thành công.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthLogin_TC016: username dài 51 ký tự (vi phạm biên trên maxLength = 50)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Body: username 51 ký tự, password `"Password123@"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform({ username: 'a'.repeat(51), password: 'Password123@' }, { type: 'body', metatype: LoginDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "username", issues: ["username must be shorter than or equal to 50 characters"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthLogin_TC017: password dài 5 ký tự (vi phạm biên dưới minLength = 6)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ "username": "teacher_hung", "password": "12345" }`

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform({ username: 'teacher_hung', password: '12345' }, { type: 'body', metatype: LoginDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "password", issues: ["password must be longer than or equal to 6 characters"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthLogin_TC018: password dài đúng 6 ký tự (biên dưới hợp lệ)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Tài khoản `adm` tồn tại, `is_active = true`.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ "username": "adm", "password": "Adm12@" }`

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(...)` — không ném lỗi.
2. Gọi `AuthService.login(dto)` với user/bcrypt mock hợp lệ.

#### Kết quả kỳ vọng (Expected Result)

- Validation hợp lệ, HTTP `200 OK`, cấp token thành công.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthLogin_TC019: password dài đúng 100 ký tự (biên trên hợp lệ)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Tài khoản `teacher_hung` tồn tại, `is_active = true`.

#### Dữ liệu kiểm thử (Test Data)

- Body: password gồm 100 ký tự, username `"teacher_hung"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform({ username: 'teacher_hung', password: 'P'.repeat(100) }, { type: 'body', metatype: LoginDto })` — không ném lỗi.
2. Gọi `AuthService.login(dto)` với mock hợp lệ.

#### Kết quả kỳ vọng (Expected Result)

- Validation hợp lệ, HTTP `200 OK`, cấp token thành công.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthLogin_TC020: password dài 101 ký tự (vi phạm biên trên maxLength = 100)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Body: password gồm 101 ký tự, username `"teacher_hung"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform({ username: 'teacher_hung', password: 'P'.repeat(101) }, { type: 'body', metatype: LoginDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "password", issues: ["password must be shorter than or equal to 100 characters"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# ==============================================================================

# PHẦN 2: API GET /api/v1/auth/me (UC-02: LẤY THÔNG TIN TÀI KHOẢN ĐANG ĐĂNG NHẬP)

# ==============================================================================

# UT01_AuthMe_TC001: Không gửi Header Authorization

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Client gửi request không đính kèm Header `Authorization`.

#### Dữ liệu kiểm thử (Test Data)

- Không có Body.

#### Các bước thực hiện (Test Steps)

1. Gọi `JwtAuthGuard.handleRequest(null, false, undefined)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401 Unauthorized`, `error_code = "AUTH_INVALID_TOKEN"`, `message = "Token không hợp lệ."`, `details = null`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthMe_TC002: Access Token đã hết hạn (Expired Token)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Passport trả `info.name = "TokenExpiredError"`.

#### Dữ liệu kiểm thử (Test Data)

- Header: `Authorization: Bearer <EXPIRED_TOKEN>`.

#### Các bước thực hiện (Test Steps)

1. Gọi `JwtAuthGuard.handleRequest(null, false, { name: 'TokenExpiredError' })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401`, `error_code = "AUTH_TOKEN_EXPIRED"`, `message = "Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthMe_TC003: Token có chữ ký sai hoặc bị can thiệp

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Token giả mạo có chữ ký không khớp khóa bí mật.

#### Dữ liệu kiểm thử (Test Data)

- Header: `Authorization: Bearer <INVALID_SIGNATURE_TOKEN>`.

#### Các bước thực hiện (Test Steps)

1. Gọi `JwtAuthGuard.handleRequest(null, false, { name: 'JsonWebTokenError' })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401`, `error_code = "AUTH_INVALID_TOKEN"`, `message = "Token không hợp lệ."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthMe_TC004: Header Authorization sai định dạng Scheme (Basic thay vì Bearer)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Header không có tiền tố `Bearer`.

#### Dữ liệu kiểm thử (Test Data)

- Header: `Authorization: Basic YWRtaW46UGFzc3dvcmRAMTIz`.

#### Các bước thực hiện (Test Steps)

1. Gọi `JwtAuthGuard.handleRequest(null, false, undefined)` (Passport không trích xuất được token → user false).

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401`, `error_code = "AUTH_INVALID_TOKEN"`, `message = "Token không hợp lệ."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthMe_TC005: Dùng Refresh Token làm Access Token (token_type = "refresh")

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Payload token có `token_type = "refresh"`.

#### Dữ liệu kiểm thử (Test Data)

- Header: `Authorization: Bearer <REFRESH_TOKEN>`.

#### Các bước thực hiện (Test Steps)

1. Gọi `JwtStrategy.validate({ id: 'u1', username: 'admin', role: 'ADMIN', token_type: 'refresh' })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401`, `error_code = "AUTH_INVALID_TOKEN"`, `message = "Token không hợp lệ."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthMe_TC006: Token hợp lệ nhưng tài khoản đã bị xóa hoặc bị vô hiệu hóa

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Token hợp lệ mang `id` của tài khoản không còn hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Header: `Authorization: Bearer <VALID_BUT_DISABLED_TOKEN>`.

#### Các bước thực hiện (Test Steps)

1. Thiết lập `prisma.user.findFirst` trả `null`.
2. Gọi `JwtStrategy.validate({ id: 'gone', username: 'x', role: 'ADMIN', token_type: 'access' })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401`, `error_code = "AUTH_ACCOUNT_DISABLED"`, `message = "Tài khoản không còn hoạt động."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthMe_TC007: Lỗi máy chủ nội bộ khi truy vấn hồ sơ

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- CSDL bị mất kết nối giả lập.

#### Dữ liệu kiểm thử (Test Data)

- Header: `Authorization: Bearer <VALID_TOKEN>`.

#### Các bước thực hiện (Test Steps)

1. Thiết lập `prisma.user.findFirst` ném `Error('Connection refused')`.
2. Gọi `AuthService.me('u1')`; cho `ApiExceptionFilter` bắt ngoại lệ.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `500`, `error_code = "INTERNAL_SERVER_ERROR"`, `message = "Đã xảy ra lỗi hệ thống."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthMe_TC008: Lấy thông tin tài khoản thành công với Giảng viên (INSTRUCTOR)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Giảng viên `teacher_hung` đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Header: `Authorization: Bearer <VALID_INSTRUCTOR_TOKEN>`.

#### Các bước thực hiện (Test Steps)

1. Thiết lập `prisma.user.findFirst` trả user INSTRUCTOR đang hoạt động.
2. Gọi `AuthService.me(userId)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200 OK`, `message = "Lấy thông tin tài khoản thành công"`.
- `data` gồm `id, username, full_name, email, role, is_active, created_at` (ISO-8601), `role = "INSTRUCTOR"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthMe_TC009: Lấy thông tin tài khoản thành công với Quản trị viên (ADMIN)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Header: `Authorization: Bearer <VALID_ADMIN_TOKEN>`.

#### Các bước thực hiện (Test Steps)

1. Thiết lập `prisma.user.findFirst` trả user ADMIN đang hoạt động.
2. Gọi `AuthService.me(userId)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200 OK`, `data.role = "ADMIN"`, `data.username = "admin"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthMe_TC010: Bản ghi CSDL chứa vai trò không được hỗ trợ (role = "SUPERADMIN")

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Bản ghi người dùng có `role` ngoài tập `{ ADMIN, INSTRUCTOR }`.

#### Dữ liệu kiểm thử (Test Data)

- Bản ghi `role = "SUPERADMIN"`.

#### Các bước thực hiện (Test Steps)

1. Thiết lập `prisma.user.findFirst` trả user với `role = "SUPERADMIN"`.
2. Gọi `AuthService.me(userId)`; cho `ApiExceptionFilter` bắt ngoại lệ.

#### Kết quả kỳ vọng (Expected Result)

- `toAppRole` ném `Error('Database contains an unsupported user role.')` ⇒ HTTP `500`, `error_code = "INTERNAL_SERVER_ERROR"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# ==============================================================================

# PHẦN 3: API POST /api/v1/auth/refresh (UC-03: GIA HẠN ACCESS TOKEN)

# ==============================================================================

# UT01_AuthRefresh_TC001: Gia hạn thành công với Refresh Token của Giảng viên

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Refresh token hợp lệ, còn hạn của `teacher_hung` (`is_active = true`).

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ "refresh_token": "<VALID_INSTRUCTOR_REFRESH_JWT>" }`

#### Các bước thực hiện (Test Steps)

1. `jwt.verifyAsync` trả payload `{ id, username, role: 'INSTRUCTOR', token_type: 'refresh', jti }`.
2. `tx.refreshToken.findFirst` trả bản ghi còn hạn kèm user đang hoạt động; `updateMany` trả `{ count: 1 }`.
3. Gọi `AuthService.refresh(rawToken)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200 OK`, `message = "Gia hạn mã truy cập thành công"`.
- Cấp `access_token` và `refresh_token` mới (rotate); `data.token_type = "Bearer"`.
- `updateMany` đánh dấu `revokedAt` cho token cũ (count = 1).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthRefresh_TC002: Gia hạn thành công với Refresh Token của Quản trị viên

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Refresh token hợp lệ, còn hạn của `admin`.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ "refresh_token": "<VALID_ADMIN_REFRESH_JWT>" }`

#### Các bước thực hiện (Test Steps)

1. `jwt.verifyAsync` trả payload ADMIN; `tx.refreshToken.findFirst` trả bản ghi còn hạn; `updateMany` trả `{ count: 1 }`.
2. Gọi `AuthService.refresh(rawToken)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200 OK`; cấp cặp token mới cho tài khoản ADMIN.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthRefresh_TC003: Refresh Token sai chữ ký hoặc hết hạn

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `jwt.verifyAsync` ném lỗi.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ "refresh_token": "<INVALID_SIGNATURE_JWT>" }`

#### Các bước thực hiện (Test Steps)

1. Thiết lập `jwt.verifyAsync` `mockRejectedValue(new Error('invalid signature'))`.
2. Gọi `AuthService.refresh(rawToken)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401`, `error_code = "AUTH_INVALID_REFRESH_TOKEN"`, `message = "Mã refresh token không hợp lệ hoặc đã hết hạn."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthRefresh_TC004: Token hợp lệ nhưng không phải Refresh Token (token_type = "access")

#### Loại test

Exception

#### Tiền đều kiện (Pre-condition)

- Payload token có `token_type = "access"`.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ "refresh_token": "<ACCESS_TOKEN>" }`

#### Các bước thực hiện (Test Steps)

1. `jwt.verifyAsync` trả payload `{ id, token_type: 'access', jti }`.
2. Gọi `AuthService.refresh(rawToken)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401`, `error_code = "AUTH_INVALID_REFRESH_TOKEN"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthRefresh_TC005: Token không tồn tại trong kho phiên (hoặc đã hết hạn lưu trữ)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `tx.refreshToken.findFirst` trả `null`.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ "refresh_token": "<UNKNOWN_REFRESH_JWT>" }`

#### Các bước thực hiện (Test Steps)

1. `jwt.verifyAsync` trả payload hợp lệ; `tx.refreshToken.findFirst` trả `null`.
2. Gọi `AuthService.refresh(rawToken)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401`, `error_code = "AUTH_INVALID_REFRESH_TOKEN"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthRefresh_TC006: Token đã bị thu hồi do xoay vòng (updateMany count = 0)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Token đã bị vô hiệu hóa bởi cơ chế rotation trước đó.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ "refresh_token": "<PREVIOUSLY_ROTATED_JWT>" }`

#### Các bước thực hiện (Test Steps)

1. `findFirst` trả bản ghi nhưng `updateMany` trả `{ count: 0 }`.
2. Gọi `AuthService.refresh(rawToken)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401`, `error_code = "AUTH_INVALID_REFRESH_TOKEN"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthRefresh_TC007: Tài khoản gắn với Refresh Token đã bị xóa hoặc vô hiệu hóa

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Bản ghi token còn hạn nhưng `user.isActive = false` hoặc `user.isDeleted = true`.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ "refresh_token": "<TOKEN_OF_DISABLED_USER>" }`

#### Các bước thực hiện (Test Steps)

1. `findFirst` trả bản ghi kèm `user` bị khóa/xóa.
2. Gọi `AuthService.refresh(rawToken)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401`, `error_code = "AUTH_INVALID_REFRESH_TOKEN"`, `message = "Mã refresh token không hợp lệ hoặc đã hết hạn."` (KHÔNG trả `AUTH_ACCOUNT_DISABLED`).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthRefresh_TC008: Lỗi máy chủ khi xử lý giao dịch gia hạn

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- CSDL bị mất kết nối giả lập trong transaction.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ "refresh_token": "<VALID_REFRESH_JWT>" }`

#### Các bước thực hiện (Test Steps)

1. `jwt.verifyAsync` trả payload hợp lệ; `prisma.$transaction` ném `Error('Connection refused')`.
2. Gọi `AuthService.refresh(rawToken)`; cho `ApiExceptionFilter` bắt ngoại lệ.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `500`, `error_code = "INTERNAL_SERVER_ERROR"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthRefresh_TC009: Request Body thiếu trường refresh_token

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{}`

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform({}, { type: 'body', metatype: RefreshTokenDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `error_code = "VALIDATION_FAILED"`, `details = [{ field: "refresh_token", issues: ["refresh_token must be a jwt string"] }]`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthRefresh_TC010: refresh_token là chuỗi chỉ chứa khoảng trắng

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ "refresh_token": "   " }`

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform({ refresh_token: '   ' }, { type: 'body', metatype: RefreshTokenDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details = [{ field: "refresh_token", issues: ["refresh_token must be a jwt string"] }]`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthRefresh_TC011: refresh_token sai kiểu dữ liệu (gửi số)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ "refresh_token": 987654321 }`

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform({ refresh_token: 987654321 }, { type: 'body', metatype: RefreshTokenDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details = [{ field: "refresh_token", issues: ["refresh_token must be a jwt string"] }]`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT01_AuthRefresh_TC012: refresh_token là chuỗi ngẫu nhiên không đúng định dạng JWT

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ "refresh_token": "random_fake_token_not_jwt" }`

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform({ refresh_token: 'random_fake_token_not_jwt' }, { type: 'body', metatype: RefreshTokenDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details = [{ field: "refresh_token", issues: ["refresh_token must be a jwt string"] }]`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |
