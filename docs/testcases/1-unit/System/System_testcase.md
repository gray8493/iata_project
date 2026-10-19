# Thông Tin Chung Kiểm Thử Unit Test

- **Phân hệ kiểm thử**: Phân hệ System (Auto-Update Desktop Client)
- **Danh sách API kiểm thử**:
  - `GET /api/v1/system/version` (Công khai — trả manifest phiên bản mới nhất cho Desktop Client)
- **Người thực hiện (Tester/Dev)**: AITA Development Team
- **Ngày tạo**: 19/10/2026
- **Cập nhật lần cuối**: 19/10/2026 - 08:00
- **Tài liệu liên quan**:
  - [Quy tắc kiểm thử Testcase](file:///e:/AITA/rules/testcase-rules.md)
  - [Đặc tả OpenAPI /system/version](file:///e:/AITA/docs/apis/openapi.yaml)
- **Đặc tả Jest tương ứng**: `apps/central-backend/src/__tests__/system.version.spec.ts`
- **Tổng số Testcase**: 04 Testcases (Phân loại: 02 Normal, 01 Boundary, 01 Exception)
  - `GET /system/version`: 04 Testcases (02 Normal, 01 Boundary, 01 Exception)

> **Ghi chú thiết kế (khớp mã nguồn `SystemService`)**:
> - `SystemService.getVersionManifest()` dựng manifest từ biến môi trường (`APP_LATEST_VERSION`, `APP_UPDATE_URL_WINDOWS`, `APP_UPDATE_SHA256_WINDOWS`...).
> - `artifact_type` chỉ nhận `exe` hoặc `zip`; giá trị lạ quy về `zip`.
> - `size_bytes` không hợp lệ/âm quy về `0`; thiếu cấu hình thì mặc định `latest_version = "0.0.0"`, `entrypoint = "AITA.exe"`, `mandatory = false`.
> - Controller bọc manifest trong Response Envelope chuẩn: `{ success, status_code, message, data, timestamp }`.

---

# ==============================================================================

# PHẦN 1: API GET /api/v1/system/version (KIỂM TRA PHIÊN BẢN MỚI NHẤT)

# ==============================================================================

# UT06_System_TC001: Dựng manifest auto-update từ cấu hình đầy đủ

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Biến môi trường cấu hình đầy đủ: version, artifact, URL, checksum, size.

#### Dữ liệu kiểm thử (Test Data)

- `APP_LATEST_VERSION=2.5.0`, `APP_MIN_SUPPORTED_VERSION=2.0.0`, `APP_UPDATE_MANDATORY=true`,
  `APP_UPDATE_ARTIFACT_TYPE=exe`, `APP_UPDATE_URL_WINDOWS=https://github.com/.../AITA.exe`,
  `APP_UPDATE_SHA256_WINDOWS=<64 hex>`, `APP_UPDATE_SIZE_WINDOWS=10485760`, `APP_UPDATE_ENTRYPOINT=AITA.exe`.

#### Các bước thực hiện (Test Steps)

1. Gọi `SystemService.getVersionManifest()`.

#### Kết quả kỳ vọng (Expected Result)

- Trả manifest với `latest_version = "2.5.0"`, `mandatory = true`.
- `platforms.windows` = `{ artifact_type: "exe", url, sha256 (lowercase), size_bytes: 10485760, entrypoint: "AITA.exe" }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  | 19/10/2026 | Jest Runner | Manifest khớp toàn bộ trường | < 50 ms | ✅ PASSED |  |

---

# UT06_System_TC003: Cấu hình không hợp lệ được chuẩn hóa an toàn

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Biến môi trường sai định dạng (`artifact_type = "msi"`, `size = -100`).

#### Dữ liệu kiểm thử (Test Data)

- `APP_UPDATE_ARTIFACT_TYPE=msi`, `APP_UPDATE_SIZE_WINDOWS=-100`.

#### Các bước thực hiện (Test Steps)

1. Gọi `SystemService.getVersionManifest()`.

#### Kết quả kỳ vọng (Expected Result)

- `artifact_type` quy về `"zip"`, `size_bytes` quy về `0` (không ném lỗi, không làm hỏng client).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  | 19/10/2026 | Jest Runner | Giá trị lạ được chuẩn hóa | < 50 ms | ✅ PASSED |  |

---

# UT06_System_TC002: Giá trị mặc định khi thiếu cấu hình (Biên)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Không cấu hình bất kỳ biến `APP_*` nào (biên: tập cấu hình rỗng).

#### Dữ liệu kiểm thử (Test Data)

- Env rỗng.

#### Các bước thực hiện (Test Steps)

1. Gọi `SystemService.getVersionManifest()`.

#### Kết quả kỳ vọng (Expected Result)

- `latest_version = "0.0.0"`, `min_supported_version = "0.0.0"`, `mandatory = false`.
- `artifact_type = "zip"`, `entrypoint = "AITA.exe"`, `size_bytes = 0`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  | 19/10/2026 | Jest Runner | Trả về đúng giá trị mặc định | < 50 ms | ✅ PASSED |  |

---

# UT06_System_TC004: Controller bọc manifest trong envelope chuẩn

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Backend hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- `APP_LATEST_VERSION=2.6.0`.

#### Các bước thực hiện (Test Steps)

1. Gọi `SystemController.version()`.

#### Kết quả kỳ vọng (Expected Result)

- Trả `{ message: "Lấy thông tin phiên bản thành công", data: { latest_version: "2.6.0", ... } }`
  để `ResponseEnvelopeInterceptor` bọc thành envelope chuẩn.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  | 19/10/2026 | Jest Runner | Message + data chính xác | < 50 ms | ✅ PASSED |  |
