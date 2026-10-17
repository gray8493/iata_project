# Thông Tin Chung Kiểm Thử Unit Test

- **Phân hệ kiểm thử**: Phân hệ Quản trị Người dùng (Admin Users API - UC-04)
- **Danh sách API kiểm thử**:
  - `GET /api/v1/admin/users` (Danh sách tài khoản có phân trang/tìm kiếm)
  - `POST /api/v1/admin/users` (Tạo tài khoản kèm hạn mức AI)
  - `GET /api/v1/admin/users/:id` (Chi tiết tài khoản)
  - `PUT /api/v1/admin/users/:id` (Cập nhật tài khoản)
  - `DELETE /api/v1/admin/users/:id` (Xóa mềm tài khoản)
- **Người thực hiện (Tester/Dev)**: Kim Chi Ha
- **Ngày tạo**: 05/10/2026
- **Cập nhật lần cuối**: 17/10/2026 - 09:00
- **Tài liệu liên quan**:
  - [Đặc tả API Phân hệ Người dùng (Markdown)](file:///e:/AITA/docs/apis/users/users-api.md)
  - [Đặc tả OpenAPI Phân hệ Người dùng (YAML)](file:///e:/AITA/docs/apis/users/users.yaml)
  - [Quy tắc kiểm thử Testcase](file:///e:/AITA/rules/testcase-rules.md)
- **Tổng số Testcase**: 64 Testcases (Phân loại: 13 Normal, 17 Boundary, 34 Exception)
  - `GET /admin/users`: 13 Testcases (03 Normal, 04 Boundary, 06 Exception)
  - `POST /admin/users`: 22 Testcases (03 Normal, 08 Boundary, 11 Exception)
  - `GET /admin/users/:id`: 07 Testcases (02 Normal, 00 Boundary, 05 Exception)
  - `PUT /admin/users/:id`: 14 Testcases (04 Normal, 02 Boundary, 08 Exception)
  - `DELETE /admin/users/:id`: 08 Testcases (01 Normal, 03 Boundary, 04 Exception)

> **Ghi chú thiết kế (khớp mã nguồn `UsersService`, `CreateUserDto`, `UpdateUserDto`, `ListUsersDto`)**:
> - Toàn bộ controller dùng `JwtAuthGuard, RolesGuard, AdaptiveThrottlerGuard` và `@Roles('ADMIN')`. `:id` bắt buộc qua `ParseUUIDPipe` (sai UUID ⇒ 400 `BAD_REQUEST`).
> - `CreateUserDto.username`: chuỗi `3..30`, khớp `^[a-z0-9_]+$`. `password`: `8..100`, khớp `^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$`. `full_name`: `2..100`. `email`: `@IsEmail`, tối đa 120. `role`: `{ ADMIN, INSTRUCTOR }`. `daily_token_quota`: số nguyên `>= 0` (KHÔNG có giới hạn trên).
> - `UpdateUserDto`: mọi trường tùy chọn, cùng ràng buộc; thêm `is_active` (boolean).
> - `ListUsersDto`: `page >= 1`; `page_size` `1..100`; `role` trong enum; `search` tối đa 50 ký tự.
> - Lỗi nghiệp vụ: `USER_ALREADY_EXISTS` (409, mã Prisma P2002), `USER_NOT_FOUND` (404), `USER_CANNOT_DISABLE_SELF` (403), `USER_CANNOT_DELETE_SELF` (403), `LAST_ACTIVE_ADMIN` (409).
> - `daily_token_quota` mặc định `50000` khi tạo/tra cứu thiếu cấu hình.

---

# ==============================================================================

# PHẦN 1: API GET /api/v1/admin/users (DANH SÁCH TÀI KHOẢN)

# ==============================================================================

# UT02_UsersList_TC001: Người gọi chưa đăng nhập (Không cung cấp Token xác thực)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Khách vãng lai chưa đăng nhập.

#### Dữ liệu kiểm thử (Test Data)

- Header `Authorization` bỏ trống.

#### Các bước thực hiện (Test Steps)

1. Gọi `JwtAuthGuard.handleRequest(null, false, undefined)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401`, `error_code = "AUTH_INVALID_TOKEN"`, `message = "Token không hợp lệ."`, `details = null`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersList_TC002: Token đã hết hạn sử dụng

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Passport trả `info.name = "TokenExpiredError"`.

#### Dữ liệu kiểm thử (Test Data)

- Header `Authorization: Bearer <EXPIRED_TOKEN>`.

#### Các bước thực hiện (Test Steps)

1. Gọi `JwtAuthGuard.handleRequest(null, false, { name: 'TokenExpiredError' })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401`, `error_code = "AUTH_TOKEN_EXPIRED"`, `message = "Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersList_TC003: Giảng viên (INSTRUCTOR) không có quyền xem danh sách

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Người gọi xác thực hợp lệ với `role = "INSTRUCTOR"`.

#### Dữ liệu kiểm thử (Test Data)

- `request.user.role = "INSTRUCTOR"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `RolesGuard.canActivate(context)` với yêu cầu `@Roles('ADMIN')`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `403`, `error_code = "FORBIDDEN_ADMIN_ONLY"`, `message = "Bạn không có quyền thực hiện thao tác này."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersList_TC004: Tài khoản trong Token đã bị vô hiệu hóa

#### Loại test

Exception

#### Tiền đều kiện (Pre-condition)

- Token hợp lệ nhưng `id` không còn hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- `prisma.user.findFirst` trả `null`.

#### Các bước thực hiện (Test Steps)

1. Gọi `JwtStrategy.validate({ id, token_type: 'access' })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401`, `error_code = "AUTH_ACCOUNT_DISABLED"`, `message = "Tài khoản không còn hoạt động."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersList_TC005: Tham số page vi phạm biên dưới (page = 0)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Query: `{ page: 0, page_size: 10 }`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform({ page: 0, page_size: 10 }, { type: 'query', metatype: ListUsersDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `error_code = "VALIDATION_FAILED"`, `details` chứa `{ field: "page", issues: ["page must not be less than 1"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersList_TC006: Tham số page_size vượt biên trên (page_size = 101)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Query: `{ page: 1, page_size: 101 }`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform({ page: 1, page_size: 101 }, { type: 'query', metatype: ListUsersDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "page_size", issues: ["page_size must not be greater than 100"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersList_TC007: Tham số role không thuộc enum hợp lệ

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Query: `{ role: "STUDENT" }`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform({ role: 'STUDENT' }, { type: 'query', metatype: ListUsersDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "role", issues: ["role must be one of the following values: ADMIN, INSTRUCTOR"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersList_TC008: Từ khóa search vượt quá 50 ký tự (search = 51 ký tự)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Query: `{ search: "a".repeat(51) }`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform({ search: 'a'.repeat(51) }, { type: 'query', metatype: ListUsersDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "search", issues: ["search must be shorter than or equal to 50 characters"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersList_TC009: Lỗi máy chủ khi truy vấn danh sách

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- CSDL bị ngắt kết nối giả lập.

#### Dữ liệu kiểm thử (Test Data)

- `prisma.$transaction` ném `Error('Connection refused')`.

#### Các bước thực hiện (Test Steps)

1. Gọi `UsersService.list({ page: 1, page_size: 10 })`; cho `ApiExceptionFilter` bắt ngoại lệ.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `500`, `error_code = "INTERNAL_SERVER_ERROR"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersList_TC010: Danh sách rỗng / trang không có dữ liệu (Biên 0)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Không có bản ghi khớp bộ lọc.

#### Dữ liệu kiểm thử (Test Data)

- `findMany` trả `[]`, `count` trả `0`.

#### Các bước thực hiện (Test Steps)

1. Gọi `UsersService.list({ page: 1, page_size: 10 })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200`, `data.items = []`, `data.pagination.total_items = 0`, `data.pagination.total_pages = 0`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersList_TC011: Lấy danh sách với tham số phân trang mặc định

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Đã xác thực quyền `ADMIN`.

#### Dữ liệu kiểm thử (Test Data)

- `findMany` trả 2 user, `count` trả `2`.

#### Các bước thực hiện (Test Steps)

1. Gọi `UsersService.list({ page: 1, page_size: 10 })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200`, `message = "Lấy danh sách người dùng thành công"`.
- `data.items` gồm `id, username, full_name, email, role, is_active, created_at, daily_token_quota, used_tokens_today`.
- `data.pagination = { page: 1, page_size: 10, total_items: 2, total_pages: 1 }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersList_TC012: Lấy danh sách kèm bộ lọc vai trò (role = INSTRUCTOR)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Đã xác thực quyền `ADMIN`.

#### Dữ liệu kiểm thử (Test Data)

- Query: `{ page: 1, page_size: 10, role: "INSTRUCTOR" }`.

#### Các bước thực hiện (Test Steps)

1. Gọi `UsersService.list({ page: 1, page_size: 10, role: 'INSTRUCTOR' })`.

#### Kết quả kỳ vọng (Expected Result)

- Điều kiện `where` truyền vào `findMany` chứa `isDeleted: false` và `role: 'INSTRUCTOR'`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersList_TC013: Tìm kiếm theo từ khóa (search = "hung")

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Đã xác thực quyền `ADMIN`.

#### Dữ liệu kiểm thử (Test Data)

- Query: `{ search: "hung" }`.

#### Các bước thực hiện (Test Steps)

1. Gọi `UsersService.list({ page: 1, page_size: 10, search: 'hung' })`.

#### Kết quả kỳ vọng (Expected Result)

- Điều kiện `where.OR` chứa 3 nhánh tìm kiếm `contains` (không phân biệt hoa thường) trên `username`, `fullName`, `email`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# ==============================================================================

# PHẦN 2: API POST /api/v1/admin/users (TẠO TÀI KHOẢN)

# ==============================================================================

# UT02_UsersCreate_TC001: Người gọi chưa đăng nhập

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Header `Authorization` bỏ trống.

#### Dữ liệu kiểm thử (Test Data)

- Không có.

#### Các bước thực hiện (Test Steps)

1. Gọi `JwtAuthGuard.handleRequest(null, false, undefined)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401`, `error_code = "AUTH_INVALID_TOKEN"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC002: Giảng viên không có quyền tạo tài khoản

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `role = "INSTRUCTOR"`.

#### Dữ liệu kiểm thử (Test Data)

- `request.user.role = "INSTRUCTOR"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `RolesGuard.canActivate(context)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `403`, `error_code = "FORBIDDEN_ADMIN_ONLY"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC003: Request Body rỗng thiếu toàn bộ trường bắt buộc

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{}`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform({}, { type: 'body', metatype: CreateUserDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa các `field`: `username`, `password`, `full_name`, `email`, `role`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC004: username dài 2 ký tự (dưới minLength = 3)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Body hợp lệ nhưng `username = "ab"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform({ username: 'ab', password: 'Password1', full_name: 'Thầy An', email: 'an@fe.edu.vn', role: 'INSTRUCTOR' }, { type: 'body', metatype: CreateUserDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "username", issues: ["username must be longer than or equal to 3 characters"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC005: username dài đúng 3 ký tự (biên dưới hợp lệ)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- username/email chưa tồn tại.

#### Dữ liệu kiểm thử (Test Data)

- `username = "abc"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(...)` — không ném lỗi.
2. `bcrypt.hash` mock; `prisma.user.create`/`aiQuotaConfig.create` mock; gọi `UsersService.create(dto)`.

#### Kết quả kỳ vọng (Expected Result)

- Validation hợp lệ, HTTP `200`, tạo tài khoản thành công.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC006: username dài đúng 30 ký tự (biên trên hợp lệ)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- username/email chưa tồn tại.

#### Dữ liệu kiểm thử (Test Data)

- `username = "a".repeat(30)`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(...)` — không ném lỗi.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200`, tạo thành công.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC007: username dài 31 ký tự (vượt maxLength = 30)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- `username = "a".repeat(31)`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(...)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "username", issues: ["username must be shorter than or equal to 30 characters"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC008: username chứa ký tự không hợp lệ (chữ hoa / ký tự đặc biệt)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- `username = "Teacher Hung!"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(...)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `field = "username"` với issue khớp regex `^[a-z0-9_]+$`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC009: password dài 7 ký tự (dưới minLength = 8)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- `password = "Pass12a"` (7 ký tự).

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(...)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "password", issues: ["password must be longer than or equal to 8 characters"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC010: password không đủ độ phức tạp (thiếu chữ hoa và chữ số)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- `password = "password"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(...)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `field = "password"` với issue khớp regex `^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC011: password dài đúng 8 ký tự và đủ độ phức tạp (biên dưới hợp lệ)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- `password = "Passw0rd"` (8 ký tự, có hoa + thường + số).

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(...)` — không ném lỗi.

#### Kết quả kỳ vọng (Expected Result)

- Validation hợp lệ, HTTP `200`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC012: full_name dài 1 ký tự (dưới minLength = 2)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- `full_name = "A"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(...)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "full_name", issues: ["full_name must be longer than or equal to 2 characters"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC013: full_name dài đúng 2 ký tự (biên dưới hợp lệ)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- `full_name = "An"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(...)` — không ném lỗi.

#### Kết quả kỳ vọng (Expected Result)

- Validation hợp lệ, HTTP `200`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC014: email sai định dạng

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- `email = "not-an-email"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(...)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "email", issues: ["email must be an email"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC015: role sai giá trị ngoài enum

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- `role = "STUDENT"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(...)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "role", issues: ["role must be one of the following values: ADMIN, INSTRUCTOR"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC016: daily_token_quota mang giá trị số âm (quota = -1)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- `daily_token_quota = -1`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(...)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "daily_token_quota", issues: ["daily_token_quota must not be less than 0"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC017: daily_token_quota bằng 0 (biên dưới hợp lệ) và bỏ trống (mặc định 50000)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Trường hợp A: `daily_token_quota = 0`. Trường hợp B: không truyền `daily_token_quota`.

#### Các bước thực hiện (Test Steps)

1. `ValidationPipe.transform(...)` với `daily_token_quota = 0` — không ném lỗi.
2. Gọi `UsersService.create` với `daily_token_quota` bỏ trống; kiểm tra giá trị truyền vào `aiQuotaConfig.create`.

#### Kết quả kỳ vọng (Expected Result)

- `0` hợp lệ; khi bỏ trống, quota được tạo với `dailyTokenLimit = 50000`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC018: Trùng tên đăng nhập hoặc email (lỗi Prisma P2002)

#### Loại test

Exception

#### Tiền đều kiện (Pre-condition)

- `username` hoặc `email` đã tồn tại.

#### Dữ liệu kiểm thử (Test Data)

- `prisma.$transaction` ném `PrismaClientKnownRequestError` với `code = "P2002"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `UsersService.create(dto)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `409 Conflict`, `error_code = "USER_ALREADY_EXISTS"`, `message = "Tên đăng nhập hoặc email đã tồn tại."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC019: Lỗi máy chủ khi tạo người dùng mới

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- CSDL bị ngắt kết nối giả lập (lỗi không phải P2002).

#### Dữ liệu kiểm thử (Test Data)

- `prisma.$transaction` ném `Error('Connection refused')`.

#### Các bước thực hiện (Test Steps)

1. Gọi `UsersService.create(dto)`; cho `ApiExceptionFilter` bắt ngoại lệ.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `500`, `error_code = "INTERNAL_SERVER_ERROR"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC020: Tạo mới thành công tài khoản Giảng viên (INSTRUCTOR)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Dữ liệu hợp lệ, username/email chưa tồn tại.

#### Dữ liệu kiểm thử (Test Data)

- `{ username: "teacher_lan", password: "Password1", full_name: "Thầy An", email: "lan@fe.edu.vn", role: "INSTRUCTOR", daily_token_quota: 50000 }`.

#### Các bước thực hiện (Test Steps)

1. `bcrypt.hash` mock trả `hashed`; `user.create` trả user; `aiQuotaConfig.create` mock; gọi `UsersService.create(dto)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200`, `message = "Tạo tài khoản người dùng mới thành công"`.
- Mật khẩu được băm với `bcrypt.hash(password, 12)`; `email` được hạ chữ thường; tạo kèm `aiQuotaConfig` trong cùng transaction.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC021: Tạo mới thành công tài khoản Quản trị viên phụ (ADMIN)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Dữ liệu hợp lệ, chưa tồn tại.

#### Dữ liệu kiểm thử (Test Data)

- `role = "ADMIN"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `UsersService.create(dto)` với mock hợp lệ.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200`, `data.role = "ADMIN"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC022: Tạo thành công và tự sinh hạn mức AI mặc định

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Dữ liệu hợp lệ, `daily_token_quota` không truyền.

#### Dữ liệu kiểm thử (Test Data)

- Body không có `daily_token_quota`.

#### Các bước thực hiện (Test Steps)

1. Gọi `UsersService.create(dto)`; kiểm tra `aiQuotaConfig.create`.

#### Kết quả kỳ vọng (Expected Result)

- `aiQuotaConfig.create` được gọi với `dailyTokenLimit = 50000` và `lastResetDate` là đầu ngày UTC.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# ==============================================================================

# PHẦN 3: API GET /api/v1/admin/users/:id (CHI TIẾT TÀI KHOẢN)

# ==============================================================================

# UT02_UsersGetDetail_TC001: Người gọi chưa đăng nhập

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Header `Authorization` bỏ trống.

#### Dữ liệu kiểm thử (Test Data)

- Không có.

#### Các bước thực hiện (Test Steps)

1. Gọi `JwtAuthGuard.handleRequest(null, false, undefined)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401`, `error_code = "AUTH_INVALID_TOKEN"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersGetDetail_TC002: Giảng viên không có quyền xem chi tiết

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `role = "INSTRUCTOR"`.

#### Dữ liệu kiểm thử (Test Data)

- `request.user.role = "INSTRUCTOR"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `RolesGuard.canActivate(context)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `403`, `error_code = "FORBIDDEN_ADMIN_ONLY"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersGetDetail_TC003: Tham số id không đúng định dạng UUID

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `:id` không phải UUID.

#### Dữ liệu kiểm thử (Test Data)

- `id = "abc"` (hoặc `"0"`).

#### Các bước thực hiện (Test Steps)

1. Cho `ParseUUIDPipe.transform('abc', { type: 'param', data: 'id' })` xử lý.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `400`, `error_code = "BAD_REQUEST"`, `message = "Validation failed (uuid is expected)"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersGetDetail_TC004: Không tìm thấy người dùng với ID đã chỉ định

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- ID hợp lệ nhưng không tồn tại hoặc đã bị xóa mềm.

#### Dữ liệu kiểm thử (Test Data)

- `prisma.user.findFirst` trả `null`.

#### Các bước thực hiện (Test Steps)

1. Gọi `UsersService.get('550e8400-e29b-41d4-a716-446655440000')`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `404 Not Found`, `error_code = "USER_NOT_FOUND"`, `message = "Không tìm thấy người dùng với ID đã chỉ định."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersGetDetail_TC005: Lỗi máy chủ khi truy vấn chi tiết

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- CSDL bị ngắt kết nối giả lập.

#### Dữ liệu kiểm thử (Test Data)

- `prisma.user.findFirst` ném `Error('Connection refused')`.

#### Các bước thực hiện (Test Steps)

1. Gọi `UsersService.get(id)`; cho `ApiExceptionFilter` bắt ngoại lệ.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `500`, `error_code = "INTERNAL_SERVER_ERROR"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersGetDetail_TC006: Xem chi tiết thành công tài khoản Giảng viên

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- ID tồn tại, chưa xóa mềm.

#### Dữ liệu kiểm thử (Test Data)

- User `role = "INSTRUCTOR"`, quota `dailyTokenLimit = 50000`.

#### Các bước thực hiện (Test Steps)

1. `prisma.user.findFirst` trả user kèm `quotaConfig`; gọi `UsersService.get(id)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200`, `message = "Lấy thông tin tài khoản thành công"`.
- `data.role = "INSTRUCTOR"`, `data.daily_token_quota = 50000`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersGetDetail_TC007: Xem chi tiết thành công tài khoản Quản trị viên

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- ID tồn tại, chưa xóa mềm.

#### Dữ liệu kiểm thử (Test Data)

- User `role = "ADMIN"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `UsersService.get(id)` với mock user ADMIN.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200`, `data.role = "ADMIN"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# ==============================================================================

# PHẦN 4: API PUT /api/v1/admin/users/:id (CẬP NHẬT TÀI KHOẢN)

# ==============================================================================

# UT02_UsersUpdate_TC001: Người gọi chưa đăng nhập

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Header `Authorization` bỏ trống.

#### Dữ liệu kiểm thử (Test Data)

- Không có.

#### Các bước thực hiện (Test Steps)

1. Gọi `JwtAuthGuard.handleRequest(null, false, undefined)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401`, `error_code = "AUTH_INVALID_TOKEN"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersUpdate_TC002: Giảng viên không có quyền cập nhật

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `role = "INSTRUCTOR"`.

#### Dữ liệu kiểm thử (Test Data)

- `request.user.role = "INSTRUCTOR"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `RolesGuard.canActivate(context)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `403`, `error_code = "FORBIDDEN_ADMIN_ONLY"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersUpdate_TC003: Cập nhật tài khoản không tồn tại

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- ID hợp lệ nhưng không tồn tại.

#### Dữ liệu kiểm thử (Test Data)

- `prisma.user.findFirst` trả `null`.

#### Các bước thực hiện (Test Steps)

1. Gọi `UsersService.update(id, { full_name: 'X' }, actorId)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `404`, `error_code = "USER_NOT_FOUND"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersUpdate_TC004: Quản trị viên tự khóa tài khoản của chính mình

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `id === actorId`.

#### Dữ liệu kiểm thử (Test Data)

- `input = { is_active: false }`.

#### Các bước thực hiện (Test Steps)

1. `prisma.user.findFirst` trả user ADMIN; gọi `UsersService.update(id, { is_active: false }, id)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `403`, `error_code = "USER_CANNOT_DISABLE_SELF"`, `message = "Bạn không thể tự vô hiệu hóa tài khoản đang sử dụng."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersUpdate_TC005: Tham số id trên đường dẫn không hợp lệ (id = 0)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `:id` không phải UUID.

#### Dữ liệu kiểm thử (Test Data)

- `id = "0"`.

#### Các bước thực hiện (Test Steps)

1. Cho `ParseUUIDPipe.transform('0', { type: 'param', data: 'id' })` xử lý.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `400`, `error_code = "BAD_REQUEST"`, `message = "Validation failed (uuid is expected)"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersUpdate_TC006: Cập nhật email sai định dạng

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- `{ email: "invalid-email" }`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform({ email: 'invalid-email' }, { type: 'body', metatype: UpdateUserDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "email", issues: ["email must be an email"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersUpdate_TC007: Cập nhật role sai giá trị ngoài ADMIN/INSTRUCTOR

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- `{ role: "SUPERADMIN" }`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform({ role: 'SUPERADMIN' }, { type: 'body', metatype: UpdateUserDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "role", issues: ["role must be one of the following values: ADMIN, INSTRUCTOR"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersUpdate_TC008: Cập nhật daily_token_quota mang giá trị số âm

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- `{ daily_token_quota: -1 }`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform({ daily_token_quota: -1 }, { type: 'body', metatype: UpdateUserDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "daily_token_quota", issues: ["daily_token_quota must not be less than 0"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersUpdate_TC009: is_active sai kiểu dữ liệu (chuỗi thay vì boolean)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- `{ is_active: "false" }`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform({ is_active: 'false' }, { type: 'body', metatype: UpdateUserDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "is_active", issues: ["is_active must be a boolean value"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersUpdate_TC010: Cập nhật email bị trùng với tài khoản khác (lỗi P2002)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Email mới đã thuộc về tài khoản khác.

#### Dữ liệu kiểm thử (Test Data)

- `prisma.$transaction` ném lỗi `code = "P2002"`.

#### Các bước thực hiện (Test Steps)

1. `prisma.user.findFirst` trả user; gọi `UsersService.update(...)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `409`, `error_code = "USER_ALREADY_EXISTS"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersUpdate_TC011: Vô hiệu hóa Admin hoạt động cuối cùng

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Bản ghi hiện tại là ADMIN đang hoạt động; `count` ADMIN hoạt động trả `1`.

#### Dữ liệu kiểm thử (Test Data)

- `input = { is_active: false }`.

#### Các bước thực hiện (Test Steps)

1. `prisma.user.findFirst` trả ADMIN active; `prisma.user.count` trả `1`; gọi `UsersService.update(id, { is_active: false }, otherActor)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `409 Conflict`, `error_code = "LAST_ACTIVE_ADMIN"`, `message = "Không thể vô hiệu hóa hoặc hạ quyền Admin hoạt động cuối cùng."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersUpdate_TC012: Lỗi máy chủ khi cập nhật tài khoản

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- CSDL bị ngắt kết nối giả lập.

#### Dữ liệu kiểm thử (Test Data)

- `prisma.$transaction` ném `Error('Connection refused')`.

#### Các bước thực hiện (Test Steps)

1. `findFirst` trả user; gọi `UsersService.update(...)`; cho `ApiExceptionFilter` bắt ngoại lệ.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `500`, `error_code = "INTERNAL_SERVER_ERROR"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersUpdate_TC013: Cập nhật thành công hồ sơ và hạn mức AI của Giảng viên

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- ID tồn tại.

#### Dữ liệu kiểm thử (Test Data)

- `{ full_name: "Thầy An (Updated)", daily_token_quota: 80000 }`.

#### Các bước thực hiện (Test Steps)

1. `findFirst` trả user INSTRUCTOR; `$transaction` cập nhật và `aiQuotaConfig.upsert`; gọi `UsersService.update(id, input, actorId)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200`, `message = "Cập nhật tài khoản thành công"`, `data.full_name = "Thầy An (Updated)"`.
- `aiQuotaConfig.upsert` được gọi với `dailyTokenLimit = 80000`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersUpdate_TC014: Khóa tài khoản Giảng viên thành công (is_active = false)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- ID tồn tại, không phải tài khoản đang thao tác.

#### Dữ liệu kiểm thử (Test Data)

- `{ is_active: false }`.

#### Các bước thực hiện (Test Steps)

1. `findFirst` trả user INSTRUCTOR; gọi `UsersService.update(id, { is_active: false }, actorId)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200`, `data.is_active = false`.
- `refreshToken.updateMany` thu hồi toàn bộ refresh token chưa revoke của người dùng.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersUpdate_TC015: Mở khóa tài khoản Giảng viên thành công (is_active = true)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- ID tồn tại.

#### Dữ liệu kiểm thử (Test Data)

- `{ is_active: true }`.

#### Các bước thực hiện (Test Steps)

1. `findFirst` trả user INSTRUCTOR; gọi `UsersService.update(id, { is_active: true }, actorId)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200`, `data.is_active = true`; điều kiện thu hồi refresh token KHÔNG kích hoạt (chỉ khi `is_active = false`).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# ==============================================================================

# PHẦN 5: API DELETE /api/v1/admin/users/:id (XÓA MỀM TÀI KHOẢN)

# ==============================================================================

# UT02_UsersDelete_TC001: Người gọi chưa đăng nhập

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Header `Authorization` bỏ trống.

#### Dữ liệu kiểm thử (Test Data)

- Không có.

#### Các bước thực hiện (Test Steps)

1. Gọi `JwtAuthGuard.handleRequest(null, false, undefined)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401`, `error_code = "AUTH_INVALID_TOKEN"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersDelete_TC002: Giảng viên không có quyền xóa tài khoản

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `role = "INSTRUCTOR"`.

#### Dữ liệu kiểm thử (Test Data)

- `request.user.role = "INSTRUCTOR"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `RolesGuard.canActivate(context)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `403`, `error_code = "FORBIDDEN_ADMIN_ONLY"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersDelete_TC003: Tham số id không hợp lệ (id = 0 hoặc chuỗi)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `:id` không phải UUID.

#### Dữ liệu kiểm thử (Test Data)

- `id = "0"`.

#### Các bước thực hiện (Test Steps)

1. Cho `ParseUUIDPipe.transform('0', { type: 'param', data: 'id' })` xử lý.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `400`, `error_code = "BAD_REQUEST"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersDelete_TC004: Xóa tài khoản không tồn tại

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- ID hợp lệ nhưng không tồn tại.

#### Dữ liệu kiểm thử (Test Data)

- `prisma.user.findFirst` trả `null`.

#### Các bước thực hiện (Test Steps)

1. Gọi `UsersService.delete(id, actorId)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `404`, `error_code = "USER_NOT_FOUND"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersDelete_TC005: Quản trị viên tự xóa tài khoản của chính mình

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `id === actorId`.

#### Dữ liệu kiểm thử (Test Data)

- `actorId = id`.

#### Các bước thực hiện (Test Steps)

1. `findFirst` trả user; gọi `UsersService.delete(id, id)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `403`, `error_code = "USER_CANNOT_DELETE_SELF"`, `message = "Bạn không thể xóa tài khoản đang sử dụng."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersDelete_TC006: Xóa Admin hoạt động cuối cùng

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Bản ghi là ADMIN hoạt động; `count` ADMIN hoạt động trả `1`.

#### Dữ liệu kiểm thử (Test Data)

- `findFirst` trả ADMIN active; `count` trả `1`.

#### Các bước thực hiện (Test Steps)

1. Gọi `UsersService.delete(id, otherActor)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `409`, `error_code = "LAST_ACTIVE_ADMIN"`, `message = "Không thể xóa Admin hoạt động cuối cùng."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersDelete_TC007: Lỗi máy chủ khi xóa người dùng

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- CSDL bị ngắt kết nối giả lập.

#### Dữ liệu kiểm thử (Test Data)

- `prisma.$transaction` ném `Error('Connection refused')`.

#### Các bước thực hiện (Test Steps)

1. `findFirst` trả user INSTRUCTOR; gọi `UsersService.delete(id, actorId)`; cho `ApiExceptionFilter` bắt ngoại lệ.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `500`, `error_code = "INTERNAL_SERVER_ERROR"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersDelete_TC008: Xóa mềm tài khoản Giảng viên thành công

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- ID tồn tại, không phải ADMIN hoạt động cuối cùng, không phải chính mình.

#### Dữ liệu kiểm thử (Test Data)

- `findFirst` trả user INSTRUCTOR; `$transaction` mock.

#### Các bước thực hiện (Test Steps)

1. Gọi `UsersService.delete(id, actorId)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200`, `message = "Xóa người dùng thành công"`, `data = null`.
- `user.update` đặt `isDeleted = true, isActive = false, deletedAt`; `aiQuotaConfig.updateMany` xóa mềm quota; `refreshToken.updateMany` thu hồi token.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |            |                                     |                  |              |          |
