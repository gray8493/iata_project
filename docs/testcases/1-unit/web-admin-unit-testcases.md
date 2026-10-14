# Thông Tin Chung Kiểm Thử Unit Test - Phân Hệ Web Admin (Backend API)

- **API / Module kiểm thử**: `AuthService`, `UsersService`, `AuditLogsService`, `AiQuotaService`
- **Người thực hiện (Tester/Dev)**: AITA Development Team
- **Ngày tạo**: 14/10/2026
- **Cập nhật lần cuối**: 14/10/2026 - 15:00
- **Tài liệu liên quan**:
  - [Quy tắc kiểm thử Testcase](file:///d:/Source/AITA/rules/testcase-rules.md)
  - [Đặc tả API Auth](file:///d:/Source/AITA/docs/apis/auth/auth-api.md)
  - [Đặc tả API Users](file:///d:/Source/AITA/docs/apis/users/users-api.md)
  - [Đặc tả API Reports](file:///d:/Source/AITA/docs/apis/reports/reports-api.md)
- **Tổng số Testcase**: 24 Testcases (24 Passed, 00 Failed)

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

Trả về HTTP 200 kèm `access_token`, `refresh_token` và thông tin `user` có quyền `ADMIN`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Lần 1 | 14/10/2026 | CI/CD Jest Runner | Trả về đủ cặp JWT Token và data user | 12 ms | ✅ PASSED | Đạt yêu cầu |

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

Ném lỗi `UnauthorizedException` với mã lỗi `AUTH_INVALID_CREDENTIALS`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Lần 1 | 14/10/2026 | CI/CD Jest Runner | Ném UnauthorizedException chuẩn xác | 3 ms | ✅ PASSED | Chặn mật khẩu sai |

---

# UT01_Auth_TC003: Đăng nhập thất bại khi tài khoản bị khóa

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Tài khoản có trạng thái `is_active = false`.

#### Các bước thực hiện (Test Steps)

1. Gửi payload hợp lệ về tên và mật khẩu của tài khoản bị khóa.
2. Gọi hàm `AuthService.login(dto)`.

#### Kết quả kỳ vọng (Expected Result)

Ném lỗi `ForbiddenException` với mã lỗi `AUTH_ACCOUNT_DISABLED`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Lần 1 | 14/10/2026 | CI/CD Jest Runner | Ném ForbiddenException chính xác | 4 ms | ✅ PASSED | Khóa truy cập đúng |

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

Trả về danh sách `items` kèm đối tượng `pagination` (`page`, `page_size`, `total_items`, `total_pages`).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Lần 1 | 14/10/2026 | CI/CD Jest Runner | Trả về danh sách và metadata phân trang | 8 ms | ✅ PASSED | Phân trang mượt |

---

# UT02_Users_TC002: Tạo mới tài khoản Giảng viên kèm hạn mức AI

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Dữ liệu `CreateUserDto` hợp lệ (email và username chưa từng tồn tại).

#### Các bước thực hiện (Test Steps)

1. Gửi thông tin: `{ username: "instructor1", password: "Password123@", full_name: "Thầy An", role: "INSTRUCTOR", daily_token_quota: 50000 }`.
2. Gọi hàm `UsersService.create(dto)`.

#### Kết quả kỳ vọng (Expected Result)

Tạo người dùng mới với mật khẩu băm Bcrypt 12 rounds và tự động sinh bản ghi `AiQuotaConfig` tương ứng.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Lần 1 | 14/10/2026 | CI/CD Jest Runner | Tạo user và quota trong 1 transaction | 15 ms | ✅ PASSED | Đảm bảo tính toàn vẹn |

---

# UT02_Users_TC003: Xóa mềm tài khoản Giảng viên

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- ID người dùng tồn tại và không phải là tài khoản của người đang thao tác.

#### Các bước thực hiện (Test Steps)

1. Truyền `id` cần xóa và `actorId` của Admin.
2. Gọi hàm `UsersService.delete(id, actorId)`.

#### Kết quả kỳ vọng (Expected Result)

Đánh dấu `is_deleted = true`, `is_active = false`, cập nhật `deleted_at`, và thu hồi toàn bộ refresh token.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Lần 1 | 14/10/2026 | CI/CD Jest Runner | Xóa mềm an toàn, không xóa cứng DB | 9 ms | ✅ PASSED | Tuân thủ soft-delete |

---

# UT03_Reports_TC001: Lấy báo cáo thống kê tổng quan (Overview)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Người dùng có quyền `ADMIN`.

#### Các bước thực hiện (Test Steps)

1. Gọi hàm `AuditLogsService.overview()`.

#### Kết quả kỳ vọng (Expected Result)

Trả về `total_instructors`, `total_tokens_consumed_month`, và `top_consuming_feature`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Lần 1 | 14/10/2026 | CI/CD Jest Runner | Trả về đúng số liệu thống kê tổng hợp | 10 ms | ✅ PASSED | Báo cáo chính xác |

---

# UT04_AiQuota_TC001: Lấy snapshot hạn mức AI trong ngày

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- User đã được cấp cấu hình hạn mức AI trong `ai_quota_configs`.

#### Các bước thực hiện (Test Steps)

1. Truyền `userId`.
2. Gọi hàm `AiQuotaService.snapshot(userId)`.

#### Kết quả kỳ vọng (Expected Result)

Trả về `daily_limit_tokens`, `used_tokens_today`, và `remaining_tokens` cùng thời điểm reset UTC.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Lần 1 | 14/10/2026 | CI/CD Jest Runner | Tính toán số token còn lại chính xác | 5 ms | ✅ PASSED | Đạt yêu cầu |
