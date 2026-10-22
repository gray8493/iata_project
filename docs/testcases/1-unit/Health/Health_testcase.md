# Thông Tin Chung Kiểm Thử Unit Test

- **Phân hệ kiểm thử**: Phân hệ Health Check (Kiểm tra sức khỏe API & PostgreSQL)
- **Danh sách API kiểm thử**:
  - `GET /api/v1/health` (Kiểm tra API, kết nối PostgreSQL và kho rate-limit storage)
- **Người thực hiện (Tester/Dev)**: AITA Development Team
- **Ngày tạo**: 18/10/2026
- **Cập nhật lần cuối**: 18/10/2026 - 12:30
- **Tài liệu liên quan**:
  - [Quy tắc kiểm thử Testcase](file:///e:/AITA/rules/testcase-rules.md)
- **Đặc tả Jest tương ứng**: `apps/central-backend/src/__tests__/health.docs.spec.ts`
- **Tổng số Testcase**: 04 Testcases (Phân loại: 01 Normal, 01 Boundary, 02 Exception)
  - `GET /health`: 04 Testcases (01 Normal, 01 Boundary, 02 Exception)

> **Ghi chú thiết kế (khớp mã nguồn `HealthController`)**:
>
> - `HealthController.health()` chạy `prisma.$queryRaw\`SELECT 1\``để kiểm tra PostgreSQL, rồi phản hồi`{ message: "Dịch vụ đang hoạt động", data: { status: "ok", database: "ok", rate_limit_storage } }`.
> - `rate_limit_storage` = `"redis"` nếu `ThrottlerStorage` là Redis (`isRedisStorage = true`), ngược lại là `"memory"`.
> - Nếu Redis đang bật nhưng không khỏe (`isHealthy = false`), ném `ServiceUnavailableException` 503 `RATE_LIMIT_STORAGE_UNAVAILABLE` trước khi trả kết quả.
> - Lỗi không phải `HttpException` (ví dụ mất kết nối DB) được `ApiExceptionFilter` chuẩn hóa thành 500 `INTERNAL_SERVER_ERROR`.

---

# ==============================================================================

# PHẦN 1: API GET /api/v1/health (KIỂM TRA SỨC KHỎE DỊCH VỤ)

# ==============================================================================

# UT05_Health_TC001: Kiểm tra sức khỏe API thành công với storage mặc định

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- PostgreSQL hoạt động; ứng dụng dùng rate-limit storage in-memory (không cấu hình Redis).

#### Dữ liệu kiểm thử (Test Data)

- `prisma.$queryRaw` trả kết quả thành công.
- `ThrottlerStorage` không có cờ `isRedisStorage`.

#### Các bước thực hiện (Test Steps)

1. Gọi `HealthController.health()`.

#### Kết quả kỳ vọng (Expected Result)

- Trả `{ message: "Dịch vụ đang hoạt động", data: { status: "ok", database: "ok", rate_limit_storage: "memory" } }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |

---

# UT05_Health_TC002: Lỗi kết nối cơ sở dữ liệu PostgreSQL

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- PostgreSQL không phản hồi hoặc từ chối kết nối.

#### Dữ liệu kiểm thử (Test Data)

- `prisma.$queryRaw` ném `Error("Connection refused")`.

#### Các bước thực hiện (Test Steps)

1. Gọi `HealthController.health()` khi truy vấn DB thất bại.
2. Cho lỗi đi qua `ApiExceptionFilter.catch`.

#### Kết quả kỳ vọng (Expected Result)

- Trả HTTP `500`, `error_code = "INTERNAL_SERVER_ERROR"`, `message = "Đã xảy ra lỗi hệ thống."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT05_Health_TC003: Kho rate-limit Redis không khả dụng

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Ứng dụng dùng Redis để lưu rate-limit nhưng Redis đang lỗi.

#### Dữ liệu kiểm thử (Test Data)

- `ThrottlerStorage = { isRedisStorage: true, isHealthy: false }`.

#### Các bước thực hiện (Test Steps)

1. Gọi `HealthController.health()` khi storage Redis không khỏe.

#### Kết quả kỳ vọng (Expected Result)

- Ném `ServiceUnavailableException` HTTP `503`, `error_code = "RATE_LIMIT_STORAGE_UNAVAILABLE"`, `message = "Kho rate limit hiện không khả dụng."`, `details = null`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT05_Health_TC004: Kho rate-limit Redis khả dụng (Biên trạng thái storage)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Ứng dụng dùng Redis và Redis đang khỏe.

#### Dữ liệu kiểm thử (Test Data)

- `ThrottlerStorage = { isRedisStorage: true, isHealthy: true }`.

#### Các bước thực hiện (Test Steps)

1. Gọi `HealthController.health()` khi storage Redis khỏe.

#### Kết quả kỳ vọng (Expected Result)

- Trả HTTP `200` với `data.rate_limit_storage = "redis"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |     PASS     |          |
