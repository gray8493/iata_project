# Thông Tin Chung Kiểm Thử Unit Test

- **Phân hệ kiểm thử**: Phân hệ Báo Cáo & Kiểm Toán Hệ Thống (Audit & Reports API - UC-05)
- **Danh sách API kiểm thử**:
  - `GET /api/v1/admin/reports/overview` (UC-05: Thống kê số lượng giảng viên và tiêu thụ token AI trong tháng hiện tại)
  - `GET /api/v1/admin/reports/ai-usage` (UC-05: Tra cứu nhật ký sử dụng AI, lọc theo giảng viên/thời gian và phân trang)
- **Người thực hiện (Tester/Dev)**: Kim Chi Ha
- **Ngày tạo**: 05/10/2026
- **Cập nhật lần cuối**: 17/10/2026 - 09:00
- **Tài liệu liên quan**:
  - [Đặc tả API Phân hệ Báo cáo & Kiểm toán (Markdown)](file:///e:/AITA/docs/apis/reports/reports-api.md)
  - [Đặc tả OpenAPI Phân hệ Báo cáo & Kiểm toán (YAML)](file:///e:/AITA/docs/apis/reports/reports.yaml)
  - [Bảng Danh mục Mã lỗi Phản hồi Hệ thống](file:///e:/AITA/docs/architecture/api-response-codes.md)
  - [Quy tắc kiểm thử Testcase](file:///e:/AITA/rules/testcase-rules.md)
- **Tổng số Testcase**: 23 Testcases (Phân loại: 05 Normal, 06 Boundary, 12 Exception; 100% có bước truyền Token xác thực)
  - `GET /api/v1/admin/reports/overview`: 11 Testcases (02 Normal, 02 Boundary, 07 Exception)
  - `GET /api/v1/admin/reports/ai-usage`: 12 Testcases (03 Normal, 04 Boundary, 05 Exception)

> **Ghi chú thiết kế (khớp mã nguồn)**: Cả hai endpoint đều được bảo vệ bởi chuỗi guard `JwtAuthGuard → RolesGuard → AdaptiveThrottlerGuard` và yêu cầu duy nhất vai trò `ADMIN`.
> - `overview` **không nhận tham số truy vấn**. Số liệu luôn được tính theo tháng UTC hiện tại (`now`). `total_budget_limit = Σ(daily_token_limit của Instructor đang hoạt động) × số ngày của tháng UTC hiện tại`.
> - `ai-usage` nhận các tham số `page`, `page_size`, `user_id`, `from`, `to` với ràng buộc DTO `ListAiUsageDto`.
> - Kết quả `overview` được cache Redis 45 giây (khóa `reports:overview:v1`).

---

# ==============================================================================

# PHẦN 1: API GET /api/v1/admin/reports/overview (UC-05: THỐNG KÊ BÁO CÁO TỔNG QUAN)

# ==============================================================================

# UT04_ReportsOverview_TC001: Lấy báo cáo tổng quan khi hệ thống đang vận hành bình thường

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- `AuditLogsService` khởi tạo với `PrismaService` (mock) và `RedisService` (mock, trả về cache rỗng lần đầu).
- Người gọi có token hợp lệ của Quản trị viên (`role = "ADMIN"`, `is_active = true`).

#### Các bước thực hiện (Test Steps)

1. Thiết lập `prisma.user.count` trả `24`.
2. Thiết lập `prisma.aiQuotaConfig.aggregate` trả `_sum.dailyTokenLimit = 200000`.
3. Thiết lập `prisma.aiQuotaLog.aggregate` trả `_sum.totalTokens = 1285000`.
4. Thiết lập `prisma.aiQuotaLog.groupBy` trả `[{ featureType: "TESTCASE_GEN", _sum: { totalTokens: 750000 } }]`.
5. Gọi hàm `AuditLogsService.overview()`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200 OK`, `message = "Lấy số liệu thống kê tổng quan thành công"`.
- `data.total_instructors = 24`.
- `data.ai_token_usage.total_tokens_consumed_month = 1285000`.
- `data.ai_token_usage.top_consuming_feature = "TESTCASE_GEN"`.
- `data.ai_token_usage.total_budget_limit = 200000 × số ngày của tháng UTC hiện tại` (công thức trong mã nguồn).
- Bản ghi tổng quan được ghi lại vào cache Redis (`setJson`, TTL 45 giây).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsOverview_TC002: Lấy báo cáo khi hệ thống mới khởi tạo, chưa có dữ liệu (Biên 0)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- CSDL Mock rỗng: không có Instructor và không có bản ghi `ai_quota_logs`.

#### Các bước thực hiện (Test Steps)

1. Thiết lập `prisma.user.count` trả `0`.
2. Thiết lập `prisma.aiQuotaConfig.aggregate` trả `{ _sum: { dailyTokenLimit: null } }`.
3. Thiết lập `prisma.aiQuotaLog.aggregate` trả `{ _sum: { totalTokens: null } }`.
4. Thiết lập `prisma.aiQuotaLog.groupBy` trả `[]`.
5. Gọi hàm `AuditLogsService.overview()`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200 OK`.
- `data.total_instructors = 0`.
- `data.ai_token_usage.total_tokens_consumed_month = 0` (giá trị `null` được quy về `0`).
- `data.ai_token_usage.total_budget_limit = 0` (`null × số ngày = 0`).
- `data.ai_token_usage.top_consuming_feature = null` (mảng `groupBy` rỗng).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsOverview_TC003: Hạn mức tháng chỉ tính quota của Giảng viên đang hoạt động

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- CSDL có Instructor đang hoạt động, Instructor bị khóa (`is_active = false`) và Instructor đã xóa mềm (`is_deleted = true`).

#### Các bước thực hiện (Test Steps)

1. Gọi hàm `AuditLogsService.overview()`.
2. Kiểm tra điều kiện `where` mà service truyền vào `prisma.aiQuotaConfig.aggregate`.

#### Kết quả kỳ vọng (Expected Result)

- Điều kiện `where` là `{ isDeleted: false, user: { role: 'INSTRUCTOR', isActive: true, isDeleted: false } }`.
- Quota của tài khoản bị khóa hoặc đã xóa **không** được cộng vào `total_budget_limit`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsOverview_TC004: Trả kết quả từ cache Redis khi còn hiệu lực (không truy vấn CSDL)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- `RedisService.getJson` trả về sẵn một `OverviewResult` hợp lệ.

#### Các bước thực hiện (Test Steps)

1. Thiết lập `redis.getJson(REPORTS_OVERVIEW_CACHE_KEY)` trả về một `OverviewResult` đã có.
2. Gọi hàm `AuditLogsService.overview()`.

#### Kết quả kỳ vọng (Expected Result)

- Hàm trả về đúng đối tượng lấy từ cache.
- **Không** gọi bất kỳ truy vấn Prisma nào (`user.count`, `aiQuotaConfig.aggregate`, `aiQuotaLog.aggregate`, `aiQuotaLog.groupBy` không được gọi).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsOverview_TC005: Lỗi máy chủ nội bộ khi tổng hợp báo cáo (CSDL ngắt kết nối)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Dịch vụ CSDL PostgreSQL bị ngắt kết nối giả lập. Cache Redis trả về rỗng.

#### Các bước thực hiện (Test Steps)

1. Thiết lập `prisma.user.count` ném lỗi kết nối (`Error('Connection refused')`).
2. Gọi hàm `AuditLogsService.overview()`.
3. Cho `ApiExceptionFilter` bắt ngoại lệ.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `500 Internal Server Error`.
- Phản hồi JSON chứa `error_code = "INTERNAL_SERVER_ERROR"`, `message = "Đã xảy ra lỗi hệ thống."`, `details = null`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsOverview_TC006: Người gọi chưa đăng nhập (Không cung cấp Token xác thực)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Khách vãng lai chưa đăng nhập (Header `Authorization` bỏ trống).

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/reports/overview`.
2. Không truyền Token xác thực.
3. Cho `JwtAuthGuard.handleRequest(error = null, user = false, info = undefined)` xử lý.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401 Unauthorized`.
- Phản hồi JSON chứa `error_code = "AUTH_INVALID_TOKEN"`, `message = "Token không hợp lệ."`, `details = null`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsOverview_TC007: Người gọi gửi Token đã hết hạn sử dụng (Expired Token)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Token của Quản trị viên đã quá hạn hiệu lực. Passport trả `info.name = "TokenExpiredError"`.

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/reports/overview`.
2. Truyền Token đã hết hạn vào Header `Authorization: Bearer <EXPIRED_TOKEN>`.
3. Cho `JwtAuthGuard.handleRequest(error = null, user = false, info = { name: 'TokenExpiredError' })` xử lý.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401 Unauthorized`.
- Phản hồi JSON chứa `error_code = "AUTH_TOKEN_EXPIRED"`, `message = "Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại."`, `details = null`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsOverview_TC008: Người gọi gửi Token có chữ ký sai hoặc bị can thiệp

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Token giả mạo có chữ ký không khớp khóa bí mật nội bộ.

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/reports/overview`.
2. Truyền Token bị sai chữ ký vào Header `Authorization: Bearer <INVALID_SIGNATURE_TOKEN>`.
3. Cho `JwtAuthGuard.handleRequest(error = null, user = false, info = { name: 'JsonWebTokenError' })` xử lý.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401 Unauthorized`.
- Phản hồi JSON chứa `error_code = "AUTH_INVALID_TOKEN"`, `message = "Token không hợp lệ."`, `details = null`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsOverview_TC009: Token hợp lệ nhưng không phải Access Token (dùng Refresh Token)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Payload token có `token_type = "refresh"` (không phải `"access"`).

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/reports/overview`.
2. Truyền Refresh Token vào Header `Authorization: Bearer <REFRESH_TOKEN>`.
3. Gọi `JwtStrategy.validate({ id: '...', token_type: 'refresh' })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401 Unauthorized`.
- Phản hồi JSON chứa `error_code = "AUTH_INVALID_TOKEN"`, `message = "Token không hợp lệ."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsOverview_TC010: Token hợp lệ nhưng tài khoản không còn hoạt động hoặc đã bị xóa

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Payload token hợp lệ mang `id` của một tài khoản không tồn tại, đã xóa mềm hoặc `is_active = false`.

#### Các bước thực hiện (Test Steps)

1. Thiết lập `prisma.user.findFirst` trả `null`.
2. Gọi `JwtStrategy.validate({ id: 'deleted-user-id', token_type: 'access' })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401 Unauthorized`.
- Phản hồi JSON chứa `error_code = "AUTH_ACCOUNT_DISABLED"`, `message = "Tài khoản không còn hoạt động."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsOverview_TC011: Người gọi là Giảng viên (INSTRUCTOR) không có quyền xem báo cáo

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Người gọi đã xác thực hợp lệ nhưng có `role = "INSTRUCTOR"`.

#### Các bước thực hiện (Test Steps)

1. Tạo `ExecutionContext` giả lập với `request.user = { id: '1', username: 'teacher_hung', role: 'INSTRUCTOR' }`.
2. Gọi `RolesGuard.canActivate(context)` khi handler yêu cầu `@Roles('ADMIN')`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `403 Forbidden`.
- Phản hồi JSON chứa `error_code = "FORBIDDEN_ADMIN_ONLY"`, `message = "Bạn không có quyền thực hiện thao tác này."`, `details = null`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# ==============================================================================

# PHẦN 2: API GET /api/v1/admin/reports/ai-usage (UC-05: NHẬT KÝ SỬ DỤNG AI)

# ==============================================================================

# UT04_ReportsAiUsage_TC001: Lấy nhật ký sử dụng AI với tham số mặc định

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Người gọi là Quản trị viên hợp lệ.
- CSDL có bản ghi `ai_quota_logs`.

#### Các bước thực hiện (Test Steps)

1. Thiết lập `prisma.aiQuotaLog.findMany` trả 1 bản ghi kèm `user: { username, fullName }`.
2. Thiết lập `prisma.aiQuotaLog.count` trả `1`.
3. Gọi hàm `AuditLogsService.listAiUsage({ page: 1, page_size: 20 })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200 OK`, `message = "Lấy nhật ký sử dụng AI thành công"`.
- `data.items` chứa các trường `id, user_id, username, full_name, feature_type, model_name, prompt_tokens, completion_tokens, total_tokens, created_at`.
- `data.pagination = { page: 1, page_size: 20, total_items: 1, total_pages: 1 }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsAiUsage_TC002: Lọc nhật ký theo một giảng viên cụ thể

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Người gọi là Quản trị viên hợp lệ.

#### Các bước thực hiện (Test Steps)

1. Gọi hàm `AuditLogsService.listAiUsage({ page: 1, page_size: 20, user_id: '550e8400-e29b-41d4-a716-446655440000' })`.
2. Kiểm tra điều kiện `where` truyền vào `prisma.aiQuotaLog.findMany`.

#### Kết quả kỳ vọng (Expected Result)

- Điều kiện `where` chứa `userId = '550e8400-e29b-41d4-a716-446655440000'` và `isDeleted: false`.
- Chỉ trả về bản ghi của giảng viên được chỉ định.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsAiUsage_TC003: Lọc nhật ký theo khoảng thời gian bao gồm hai mốc (from, to)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Người gọi là Quản trị viên hợp lệ, `from <= to`.

#### Các bước thực hiện (Test Steps)

1. Gọi hàm `AuditLogsService.listAiUsage({ page: 1, page_size: 20, from: '2026-10-01T00:00:00.000Z', to: '2026-10-31T23:59:59.000Z' })`.
2. Kiểm tra điều kiện `where`.

#### Kết quả kỳ vọng (Expected Result)

- Điều kiện `where.createdAt = { gte: new Date('2026-10-01T00:00:00.000Z'), lte: new Date('2026-10-31T23:59:59.000Z') }`.
- Hai mốc thời gian được bao gồm (`gte` / `lte`).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsAiUsage_TC004: Tham số page_size đạt biên trên hợp lệ (page_size = 100)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Người gọi là Quản trị viên hợp lệ.

#### Các bước thực hiện (Test Steps)

1. Gọi hàm `AuditLogsService.listAiUsage({ page: 1, page_size: 100 })`.
2. Kiểm tra giá trị `skip` và `take` truyền vào `findMany`.

#### Kết quả kỳ vọng (Expected Result)

- Không ném lỗi validation vì `100` thỏa `@Max(100)`.
- `skip = 0`, `take = 100`.
- `data.pagination.page_size = 100`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsAiUsage_TC005: Không có bản ghi nào khớp bộ lọc (mảng rỗng)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Người gọi là Quản trị viên hợp lệ, CSDL không có bản ghi khớp.

#### Các bước thực hiện (Test Steps)

1. Thiết lập `prisma.aiQuotaLog.findMany` trả `[]`, `prisma.aiQuotaLog.count` trả `0`.
2. Gọi hàm `AuditLogsService.listAiUsage({ page: 1, page_size: 20 })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200 OK`.
- `data.items = []`.
- `data.pagination.total_items = 0`, `data.pagination.total_pages = 0`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsAiUsage_TC006: Tham số page_size vượt biên trên (page_size = 101)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Người gọi là Quản trị viên hợp lệ.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe` với DTO `ListAiUsageDto` và `{ page: 1, page_size: 101 }`.
2. Gọi hàm `AuditLogsService.listAiUsage(dto)` với DTO đã validate thất bại.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422 Unprocessable Entity`.
- Phản hồi JSON chứa `error_code = "VALIDATION_FAILED"`, `message = "Dữ liệu gửi lên không đúng định dạng."`.
- `details` chứa `{ field: "page_size", issues: [ ... ] }` (thông điệp mặc định của `@Max(100)`).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsAiUsage_TC007: Tham số page vi phạm biên dưới (page = 0)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Người gọi là Quản trị viên hợp lệ.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe` với DTO `ListAiUsageDto` và `{ page: 0, page_size: 20 }`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422 Unprocessable Entity`.
- Phản hồi JSON chứa `error_code = "VALIDATION_FAILED"`.
- `details` chứa `{ field: "page", issues: [ ... ] }` (thông điệp mặc định của `@Min(1)`).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsAiUsage_TC008: Khoảng thời gian không hợp lệ (from > to)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Người gọi là Quản trị viên hợp lệ.

#### Các bước thực hiện (Test Steps)

1. Gọi hàm `AuditLogsService.listAiUsage({ page: 1, page_size: 20, from: '2026-10-20', to: '2026-10-10' })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `400 Bad Request`.
- Phản hồi JSON chứa `error_code = "INVALID_DATE_RANGE"`, `message = "Thời điểm bắt đầu phải nhỏ hơn hoặc bằng thời điểm kết thúc."`, `details = null`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsAiUsage_TC009: Tham số user_id không đúng định dạng UUID

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Người gọi là Quản trị viên hợp lệ.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe` với DTO `ListAiUsageDto` và `{ page: 1, page_size: 20, user_id: 'not-a-uuid' }`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422 Unprocessable Entity`.
- Phản hồi JSON chứa `error_code = "VALIDATION_FAILED"`.
- `details` chứa `{ field: "user_id", issues: [ ... ] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsAiUsage_TC010: Tham số from không đúng định dạng ngày ISO-8601

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Người gọi là Quản trị viên hợp lệ.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe` với DTO `ListAiUsageDto` và `{ page: 1, page_size: 20, from: '31-10-2026' }`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422 Unprocessable Entity`.
- Phản hồi JSON chứa `error_code = "VALIDATION_FAILED"`.
- `details` chứa `{ field: "from", issues: [ ... ] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsAiUsage_TC011: Người gọi chưa đăng nhập (Không cung cấp Token xác thực)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Khách vãng lai chưa đăng nhập.

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/reports/ai-usage`.
2. Không truyền Token xác thực.
3. Cho `JwtAuthGuard.handleRequest(error = null, user = false, info = undefined)` xử lý.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401 Unauthorized`.
- Phản hồi JSON chứa `error_code = "AUTH_INVALID_TOKEN"`, `message = "Token không hợp lệ."`, `details = null`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsAiUsage_TC012: Người gọi là Giảng viên (INSTRUCTOR) không có quyền tra cứu nhật ký

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Người gọi đã xác thực hợp lệ nhưng có `role = "INSTRUCTOR"`.

#### Các bước thực hiện (Test Steps)

1. Tạo `ExecutionContext` giả lập với `request.user = { id: '1', username: 'teacher_hung', role: 'INSTRUCTOR' }`.
2. Gọi `RolesGuard.canActivate(context)` khi handler yêu cầu `@Roles('ADMIN')`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `403 Forbidden`.
- Phản hồi JSON chứa `error_code = "FORBIDDEN_ADMIN_ONLY"`, `message = "Bạn không có quyền thực hiện thao tác này."`, `details = null`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |
