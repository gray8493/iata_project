# Thông Tin Chung Kiểm Thử Unit Test

- **Phân hệ kiểm thử**: Phân hệ System (Auto-Update Desktop Client)
- **Danh sách API kiểm thử**:
  - `GET /api/v1/system/version` (Công khai — trả manifest phiên bản mới nhất cho Desktop Client)
- **Người thực hiện (Tester/Dev)**: AITA Development Team
- **Ngày tạo**: 19/10/2026
- **Cập nhật lần cuối**: 21/10/2026 - 09:00
- **Tài liệu liên quan**:
  - [Quy tắc kiểm thử Testcase](file:///e:/AITA/rules/testcase-rules.md)
  - [Đặc tả OpenAPI /system/version](file:///e:/AITA/docs/apis/openapi.yaml)
- **Đặc tả Jest tương ứng**: `apps/central-backend/src/__tests__/system.version.spec.ts`
- **Tổng số Testcase**: 09 Testcases (Phân loại: 04 Normal, 02 Boundary, 03 Exception)
  - `GET /system/version`: 09 Testcases (04 Normal, 02 Boundary, 03 Exception)

> **Ghi chú thiết kế (khớp mã nguồn `SystemService`)**:
> - **Nguồn ưu tiên (mới)**: `APP_UPDATE_SOURCE=github` (mặc định) → `GitHubReleaseService` gọi GitHub Releases API lấy release mới nhất, tự suy ra `latest_version` (tag `v1.2.3-portable` → `1.2.3`), `url`, `sha256` (từ `digest` của asset) và `size_bytes`. Nhờ vậy mỗi bản phát hành chỉ cần tạo GitHub Release, **không phải sửa biến môi trường rồi redeploy**.
> - **Đường dự phòng**: `APP_UPDATE_SOURCE=env`, chưa cấu hình `APP_UPDATE_GITHUB_REPO`, hoặc GitHub lỗi (401/404/rate-limit/timeout) → dựng manifest từ biến môi trường như các gạch đầu dòng dưới; endpoint **không bao giờ trả 500 chỉ vì GitHub**. Kết quả GitHub được cache `APP_UPDATE_GITHUB_TTL_SECONDS` (mặc định 300 giây).
> - `SystemService.getVersionManifest()` dựng manifest từ biến môi trường (`APP_LATEST_VERSION`, `APP_UPDATE_URL_WINDOWS`, `APP_UPDATE_SHA256_WINDOWS`...).
> - `artifact_type` chỉ nhận `exe` hoặc `zip`; giá trị lạ quy về `zip`.
> - `size_bytes` không hợp lệ/âm quy về `0`; thiếu cấu hình thì mặc định `latest_version = "0.0.0"`, `entrypoint = "AITA_Grader_v1.exe"`, `mandatory = false`.
> - Controller bọc manifest trong Response Envelope chuẩn: `{ success, status_code, message, data, timestamp }`.
> - **Bẫy kiểu dữ liệu (đã sửa)**: Joi trong `app.module.ts` ép `APP_UPDATE_MANDATORY` → `boolean` và `APP_UPDATE_SIZE_WINDOWS` → `number`, mà `ConfigService.get()` ưu tiên trả bản đã ép kiểu (trước cả `process.env`). Vì vậy `SystemService` phải `String(...)` trước khi `.trim()`, nếu không `GET /system/version` ném `TypeError` → **500**, khiến Auto-Update ở Desktop Client im lặng không bao giờ chạy.

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
- `artifact_type = "zip"`, `entrypoint = "AITA_Grader_v1.exe"`, `size_bytes = 0`.

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

---

# UT06_System_TC005: Giá trị đã qua Joi (boolean/number) vẫn dựng được manifest

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Chạy qua `ConfigModule.forRoot({ validationSchema })` thật (không mock `ConfigService`),
  mô phỏng đúng môi trường production: `APP_UPDATE_MANDATORY` và `APP_UPDATE_SIZE_WINDOWS`
  đã bị Joi ép về `boolean` / `number`.

#### Dữ liệu kiểm thử (Test Data)

- `APP_LATEST_VERSION=2.6.0`, `APP_UPDATE_MANDATORY=true`, `APP_UPDATE_ARTIFACT_TYPE=zip`,
  `APP_UPDATE_ENTRYPOINT=AITA_Grader_v1.exe`, `APP_UPDATE_SIZE_WINDOWS=10485760`,
  `APP_UPDATE_SHA256_WINDOWS=<64 hex>`.
- Ca phụ: chỉ có `APP_UPDATE_MANDATORY=false`.

#### Các bước thực hiện (Test Steps)

1. Dựng `ConfigService` thật qua `ConfigModule.forRoot` với Joi `validationSchema`.
2. Gọi `SystemService.getVersionManifest()`.

#### Kết quả kỳ vọng (Expected Result)

- `typeof config.get("APP_UPDATE_MANDATORY") === "boolean"` và `typeof config.get("APP_UPDATE_SIZE_WINDOWS") === "number"`
  (xác nhận bẫy tồn tại), nhưng manifest vẫn dựng đúng: `mandatory = true`,
  `entrypoint = "AITA_Grader_v1.exe"`, `size_bytes = 10485760`, `sha256` viết thường.
- Ca phụ trả `mandatory = false`, `size_bytes = 0` — **không ném `TypeError`** (trước khi sửa,
  cả hai ca đều ném `TypeError: ...trim is not a function` làm `GET /system/version` trả 500).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  | 20/10/2026 | Jest Runner | Manifest đúng, không ném lỗi | < 900 ms | ✅ PASSED | Chạy qua Nest `ConfigModule` thật |
|  Lần 2  | 20/10/2026 | Jest Runner (hoàn nguyên tạm `read()`) | `TypeError: ...trim is not a function` | < 900 ms | ✅ PASSED (bắt đúng lỗi cũ) | Xác nhận test bắt được hồi quy |

---

# UT06_System_TC006: Chuyển payload GitHub Releases thành thông tin manifest

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Có payload JSON của `GET https://api.github.com/repos/{repo}/releases/latest`
  (`releaseToInfo()` là hàm thuần, không gọi mạng).

#### Dữ liệu kiểm thử (Test Data)

- `tag_name = "v1.1.0-portable"`, `name = "AITA Grader v1.1.0 (portable)"`.
- `assets`: `aita_selftest.txt` (file phụ) và `AITA_Grader_v1_portable.zip`
  (`size = 215437452`, `digest = "sha256:<64 hex thường>"`).
- Ca phụ: tag `nightly`, tag `v2.5.0`, release chỉ có `.exe`, release không có asset.

#### Các bước thực hiện (Test Steps)

1. Gọi `releaseToInfo(payload)`.
2. Gọi `versionFromTag()` / `pickZipAsset()` với các ca phụ.

#### Kết quả kỳ vọng (Expected Result)

- `version = "1.1.0"` (bỏ tiền tố `v` và hậu tố `-portable`), `url` là link của asset ZIP,
  `sha256` = 64 hex **viết thường** (đã bỏ tiền tố `sha256:`), `sizeBytes = 215437452`.
- `notes` lấy từ `name` của release, `publishedAt` lấy từ `published_at`.
- Tag không có số phiên bản (`nightly`) hoặc release thiếu asset ZIP → trả `null` (để `SystemService` fallback env).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  | 21/10/2026 | Jest Runner | Mapping đúng, bỏ qua file phụ | < 50 ms | ✅ PASSED |  |

---

# UT06_System_TC007: Manifest tự lấy từ GitHub Release (không cần sửa env)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- `APP_UPDATE_SOURCE=github` (mặc định), `GitHubReleaseService` trả về release `1.1.0` (stub, không gọi mạng).
- Env cũ vẫn còn `APP_LATEST_VERSION=1.0.0` và `APP_UPDATE_URL_WINDOWS` cũ.

#### Dữ liệu kiểm thử (Test Data)

- Env: `APP_MIN_SUPPORTED_VERSION=1.0.0`, `APP_UPDATE_ENTRYPOINT=AITA_Grader_v1.exe`.
- Release: `version=1.1.0`, `url/sha256/sizeBytes` của bản mới.

#### Các bước thực hiện (Test Steps)

1. Gọi `SystemService.getVersionManifest()`.

#### Kết quả kỳ vọng (Expected Result)

- `latest_version = "1.1.0"`, `url`/`sha256`/`size_bytes` lấy từ GitHub (đè giá trị env cũ).
- `min_supported_version`, `entrypoint`, `mandatory` vẫn theo env (GitHub không quản lý các trường này).
- `notes`/`published_at` lấy từ release khi env để trống.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  | 21/10/2026 | Jest Runner | Manifest lấy đúng bản mới từ GitHub | < 50 ms | ✅ PASSED | Không cần sửa env mỗi bản |

---

# UT06_System_TC008: GitHub lỗi hoặc tắt nguồn github thì quay về env

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Ca 1: `APP_UPDATE_SOURCE=env` nhưng vẫn truyền `GitHubReleaseService` có dữ liệu.
- Ca 2: `APP_UPDATE_SOURCE=github`, service ném lỗi (`rate limit`).
- Ca 3: chưa cấu hình `APP_UPDATE_GITHUB_REPO` (service thật, không gọi mạng).

#### Dữ liệu kiểm thử (Test Data)

- `APP_LATEST_VERSION=9.9.9` (ca 1), `1.0.0` + `APP_UPDATE_URL_WINDOWS` (ca 2), `1.2.3` (ca 3).

#### Các bước thực hiện (Test Steps)

1. Gọi `SystemService.getVersionManifest()` ở từng ca.

#### Kết quả kỳ vọng (Expected Result)

- Ca 1: bỏ qua GitHub, `latest_version = "9.9.9"`.
- Ca 2: `latest_version = "1.0.0"`, `url` giữ nguyên của env — **không ném lỗi** (endpoint vẫn 200).
- Ca 3: `latest_version = "1.2.3"`, không phát sinh request mạng.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  | 21/10/2026 | Jest Runner | Fallback env đúng ở cả 3 ca | < 50 ms | ✅ PASSED | Auto-Update không bị chết vì GitHub |

---

# UT06_System_TC009: Cache TTL của GitHubReleaseService

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `APP_UPDATE_GITHUB_REPO=x/y`, `APP_UPDATE_GITHUB_TTL_SECONDS=300` (biên: 2 lần gọi liên tiếp trong cùng TTL).
- `global.fetch` được mock trả release hợp lệ, đếm số lần gọi.

#### Dữ liệu kiểm thử (Test Data)

- Release: `tag_name = "v1.1.0"`, một asset `AITA_Grader_v1_portable.zip` có `digest`.

#### Các bước thực hiện (Test Steps)

1. Gọi `getLatestRelease()` lần 1.
2. Gọi `getLatestRelease()` lần 2 ngay sau đó.

#### Kết quả kỳ vọng (Expected Result)

- Cả hai lần trả `version = "1.1.0"`.
- `fetch` chỉ được gọi **1 lần** → không vượt rate-limit 60 request/giờ của GitHub.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  | 21/10/2026 | Jest Runner | `fetch` gọi đúng 1 lần cho 2 request | < 50 ms | ✅ PASSED | Cache theo `APP_UPDATE_GITHUB_TTL_SECONDS` |
