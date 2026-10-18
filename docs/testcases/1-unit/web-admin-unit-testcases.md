# Bảng Kiểm Thử Unit Test Trọng Tâm Phục Vụ Giao Diện Web Admin (Backend Services)

- **API / Module kiểm thử**: `AuthService`, `UsersService`, `AuditLogsService`
- **Người thực hiện (Tester/Dev)**: AITA Development Team
- **Ngày tạo**: 14/10/2026
- **Cập nhật lần cuối**: 18/10/2026 - 12:30
- **Tài liệu liên quan**:
  - [Quy tắc kiểm thử Testcase](file:///e:/AITA/rules/testcase-rules.md)
  - [Đặc tả API Auth](file:///e:/AITA/docs/apis/auth/auth-api.md)
  - [Đặc tả API Users](file:///e:/AITA/docs/apis/users/users-api.md)
  - [Đặc tả API Reports](file:///e:/AITA/docs/apis/reports/reports-api.md)
- **Đặc tả Jest tương ứng**:
  - `apps/central-backend/src/__tests__/auth.service.spec.ts` → `UT01_Auth_TC001..TC007`
  - `apps/central-backend/src/__tests__/users.service.spec.ts` → `UT02_Users_TC001..TC005`
  - `apps/central-backend/src/__tests__/audit-logs.service.spec.ts` → `UT04_Reports_TC001..TC002`
- **Tổng số Testcase**: 14 Testcases (14 Passed, 00 Failed)

> Bảng này trích xuất các kịch bản unit test cốt lõi phục vụ các màn hình Web Admin (dịch vụ backend `*.service.spec.ts`). Các module AI (`AiQuotaService`, `OpenRouterService`) được kiểm thử riêng trong `docs/testcases/1-unit/AI/AI_testcase.md`.

---

# UT01_Auth_TC001: Đăng nhập thành công với tài khoản Admin hợp lệ

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Tài khoản `admin` tồn tại trong cơ sở dữ liệu, `is_active = true`, `is_deleted = false`.
- Mật khẩu khớp với chuỗi băm Bcrypt.

#### Các bước thực hiện (Test Steps)

1. Gửi payload: `{ username: "admin", password: "ValidPassword123" }`.
2. Gọi hàm `AuthService.login(dto)`.

#### Kết quả kỳ vọng (Expected Result)

- Trả `message = "Đăng nhập thành công"` kèm `data.access_token`, `data.refresh_token` và `data.user` có `username = "admin"`, `role = "ADMIN"`.
- `refreshToken.create` được gọi để lưu refresh token.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Lần 1 | 18/10/2026 | CI/CD Jest Runner | Trả về đủ cặp JWT Token và data user | 12 ms | ✅ PASSED | Đạt yêu cầu |

---

# UT01_Auth_TC002: Đăng nhập thất bại do sai mật khẩu

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Tài khoản `admin` tồn tại trên hệ thống.

#### Các bước thực hiện (Test Steps)

1. Gửi payload: `{ username: "admin", password: "WrongPassword" }`.
2. Gọi hàm `AuthService.login(dto)`.

#### Kết quả kỳ vọng (Expected Result)

- Ném `UnauthorizedException` (HTTP 401), `error_code = "AUTH_INVALID_CREDENTIALS"`, `message = "Tên đăng nhập hoặc mật khẩu không chính xác."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Lần 1 | 18/10/2026 | CI/CD Jest Runner | Ném UnauthorizedException chuẩn xác | 3 ms | ✅ PASSED | Chặn mật khẩu sai |

---

# UT01_Auth_TC003: Đăng nhập thất bại do tài khoản không tồn tại

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Không có bản ghi người dùng khớp `username`.

#### Các bước thực hiện (Test Steps)

1. `user.findFirst` trả `null`.
2. Gọi hàm `AuthService.login(dto)`.

#### Kết quả kỳ vọng (Expected Result)

- Ném `UnauthorizedException` (HTTP 401), `error_code = "AUTH_INVALID_CREDENTIALS"` (không tiết lộ tài khoản có tồn tại hay không).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Lần 1 | 18/10/2026 | CI/CD Jest Runner | Ném UnauthorizedException đồng nhất | 3 ms | ✅ PASSED | Chống dò username |

---

# UT01_Auth_TC004: Đăng nhập thất bại khi tài khoản bị khóa

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Tài khoản có trạng thái `is_active = false`.

#### Các bước thực hiện (Test Steps)

1. Gửi payload hợp lệ về tên và mật khẩu của tài khoản bị khóa.
2. Gọi hàm `AuthService.login(dto)`.

#### Kết quả kỳ vọng (Expected Result)

- Ném `ForbiddenException` (HTTP 403), `error_code = "AUTH_ACCOUNT_DISABLED"`, `message = "Tài khoản của bạn đã bị vô hiệu hóa."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Lần 1 | 18/10/2026 | CI/CD Jest Runner | Ném ForbiddenException chính xác | 4 ms | ✅ PASSED | Khóa truy cập đúng |

---

# UT01_Auth_TC005: Lấy thông tin tài khoản hiện tại (me)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Token hợp lệ, tài khoản còn hoạt động.

#### Các bước thực hiện (Test Steps)

1. Gọi hàm `AuthService.me(userId)` khi `user.findFirst` trả bản ghi hợp lệ.
2. Gọi lại `AuthService.me(userId)` khi `user.findFirst` trả `null` (tài khoản bị khóa/xóa).

#### Kết quả kỳ vọng (Expected Result)

- Trường hợp hợp lệ: `message = "Lấy thông tin tài khoản thành công"`, `data.username`, `data.email` đúng.
- Trường hợp tài khoản không còn hoạt động: ném `UnauthorizedException` (HTTP 401).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Lần 1 | 18/10/2026 | CI/CD Jest Runner | Trả về profile, chặn tài khoản bị khóa | 5 ms | ✅ PASSED | Đạt yêu cầu |

---

# UT01_Auth_TC006: Gia hạn Access Token với Refresh Token hợp lệ

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Refresh token hợp lệ, tồn tại trong `refresh_tokens` và chưa bị thu hồi.

#### Các bước thực hiện (Test Steps)

1. `jwt.verifyAsync` trả payload `token_type = "refresh"`; `refreshToken.findFirst` trả bản ghi hợp lệ.
2. Gọi hàm `AuthService.refresh(rawToken)`.

#### Kết quả kỳ vọng (Expected Result)

- Trả `message = "Gia hạn mã truy cập thành công"` cùng cặp `access_token`/`refresh_token` mới (xoay vòng refresh token).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Lần 1 | 18/10/2026 | CI/CD Jest Runner | Cấp cặp token mới và xoay vòng | 6 ms | ✅ PASSED | Rotation đúng |

---

# UT01_Auth_TC007: Gia hạn thất bại khi Refresh Token không hợp lệ

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Refresh token sai chữ ký hoặc đã hết hạn.

#### Các bước thực hiện (Test Steps)

1. `jwt.verifyAsync` ném lỗi.
2. Gọi hàm `AuthService.refresh(rawToken)`.

#### Kết quả kỳ vọng (Expected Result)

- Ném `UnauthorizedException` (HTTP 401), `error_code = "AUTH_INVALID_REFRESH_TOKEN"`, `message = "Mã refresh token không hợp lệ hoặc đã hết hạn."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Lần 1 | 18/10/2026 | CI/CD Jest Runner | Ném UnauthorizedException khi token sai | 4 ms | ✅ PASSED | Chặn token giả |

---

# UT02_Users_TC001: Lấy danh sách tài khoản người dùng phân trang

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Đã xác thực quyền `ADMIN`.

#### Các bước thực hiện (Test Steps)

1. Thiết lập tham số phân trang: `{ page: 1, page_size: 10, search: "admin" }`.
2. Gọi hàm `UsersService.list(query)`.

#### Kết quả kỳ vọng (Expected Result)

- Trả `message = "Lấy danh sách người dùng thành công"` cùng `data.items` và `data.pagination` (`page`, `page_size`, `total_items`, `total_pages`).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Lần 1 | 18/10/2026 | CI/CD Jest Runner | Trả về danh sách và metadata phân trang | 8 ms | ✅ PASSED | Phân trang mượt |

---

# UT02_Users_TC002: Tạo mới tài khoản Giảng viên kèm hạn mức AI

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Dữ liệu `CreateUserDto` hợp lệ (email và username chưa từng tồn tại).

#### Các bước thực hiện (Test Steps)

1. Gửi thông tin: `{ username: "instructor1", password: "Password123@", full_name: "Thầy Nguyễn Văn An", role: "INSTRUCTOR", daily_token_quota: 50000 }`.
2. Gọi hàm `UsersService.create(dto)`.

#### Kết quả kỳ vọng (Expected Result)

- Trả `message = "Tạo tài khoản người dùng mới thành công"`, `data.username = "instructor1"`.
- Mật khẩu được băm Bcrypt và `aiQuotaConfig.create` được gọi để tạo hạn mức AI.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Lần 1 | 18/10/2026 | CI/CD Jest Runner | Tạo user và quota trong 1 transaction | 15 ms | ✅ PASSED | Đảm bảo tính toàn vẹn |

---

# UT02_Users_TC003: Xem chi tiết tài khoản theo ID

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Đã xác thực quyền `ADMIN`.

#### Các bước thực hiện (Test Steps)

1. Gọi hàm `UsersService.get(id)` khi ID tồn tại (kèm `quotaConfig`).
2. Gọi lại `UsersService.get(id)` khi `user.findFirst` trả `null`.

#### Kết quả kỳ vọng (Expected Result)

- Trường hợp tồn tại: `message = "Lấy thông tin tài khoản thành công"`, `data.id` và `data.daily_token_quota` đúng.
- Trường hợp không tồn tại: ném `NotFoundException` (HTTP 404), `error_code = "USER_NOT_FOUND"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Lần 1 | 18/10/2026 | CI/CD Jest Runner | Trả chi tiết kèm quota, chặn ID sai | 7 ms | ✅ PASSED | Đạt yêu cầu |

---

# UT02_Users_TC004: Cập nhật thông tin tài khoản

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- ID người dùng tồn tại; người thao tác là `actorId` khác với người bị vô hiệu hóa.

#### Các bước thực hiện (Test Steps)

1. Gọi `UsersService.update(id, { full_name: "Thầy Nguyễn Văn An (Updated)", daily_token_quota: 80000 }, actorId)`.
2. Gọi lại `UsersService.update(actorId, { is_active: false }, actorId)` để kiểm tra tự khóa.

#### Kết quả kỳ vọng (Expected Result)

- Trường hợp hợp lệ: `message = "Cập nhật tài khoản thành công"`, `data.full_name` đã đổi; `aiQuotaConfig.upsert` được gọi.
- Trường hợp tự vô hiệu hóa chính mình: ném `ForbiddenException` (HTTP 403), `error_code = "USER_CANNOT_DISABLE_SELF"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Lần 1 | 18/10/2026 | CI/CD Jest Runner | Cập nhật thành công, chặn tự khóa | 11 ms | ✅ PASSED | An toàn thao tác |

---

# UT02_Users_TC005: Xóa mềm tài khoản người dùng

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- ID người dùng tồn tại và không phải là tài khoản của người đang thao tác.

#### Các bước thực hiện (Test Steps)

1. Truyền `id` cần xóa và `actorId` của Admin.
2. Gọi hàm `UsersService.delete(id, actorId)`.
3. Gọi lại `UsersService.delete(actorId, actorId)` để kiểm tra tự xóa.

#### Kết quả kỳ vọng (Expected Result)

- Trường hợp hợp lệ: `message = "Xóa người dùng thành công"`, cập nhật `is_deleted = true`, `is_active = false` và thu hồi refresh token.
- Trường hợp tự xóa chính mình: ném `ForbiddenException` (HTTP 403), `error_code = "USER_CANNOT_DELETE_SELF"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Lần 1 | 18/10/2026 | CI/CD Jest Runner | Xóa mềm an toàn, chặn tự xóa | 9 ms | ✅ PASSED | Tuân thủ soft-delete |

---

# UT04_Reports_TC001: Lấy báo cáo thống kê tổng quan (overview)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Người dùng có quyền `ADMIN`.

#### Các bước thực hiện (Test Steps)

1. Gọi hàm `AuditLogsService.overview()`.

#### Kết quả kỳ vọng (Expected Result)

- Trả `message = "Lấy số liệu thống kê tổng quan thành công"` với `data.total_instructors`, `data.ai_token_usage.total_tokens_consumed_month`, `data.ai_token_usage.top_consuming_feature`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Lần 1 | 18/10/2026 | CI/CD Jest Runner | Trả về đúng số liệu thống kê tổng hợp | 10 ms | ✅ PASSED | Báo cáo chính xác |

---

# UT04_Reports_TC002: Lấy nhật ký sử dụng AI có lọc (listAiUsage)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Người dùng có quyền `ADMIN`; tồn tại log sử dụng AI.

#### Các bước thực hiện (Test Steps)

1. Gọi `AuditLogsService.listAiUsage({ page: 1, page_size: 10 })`.
2. Gọi lại `listAiUsage({ page: 1, page_size: 10, from: "2026-10-20", to: "2026-10-10" })` với khoảng ngày sai.

#### Kết quả kỳ vọng (Expected Result)

- Trường hợp hợp lệ: `message = "Lấy nhật ký sử dụng AI thành công"`, `data.items` kèm `username` và `total_tokens`; `data.pagination`.
- Trường hợp `from > to`: ném `BadRequestException` (HTTP 400), `error_code = "INVALID_DATE_RANGE"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Lần 1 | 18/10/2026 | CI/CD Jest Runner | Trả log kèm phân trang, chặn khoảng ngày sai | 8 ms | ✅ PASSED | Đạt yêu cầu |
