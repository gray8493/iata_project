# Thông Tin Chung Kiểm Thử Unit Test

- **Phân hệ kiểm thử**: Phân hệ AI Gateway & Quản lý Hạn ngạch (AI Hub API - UC-04, UC-10, UC-16, UC-17, UC-19)
- **Danh sách API kiểm thử**:
  - `GET /api/v1/ai/quota` (Kiểm tra hạn ngạch Token hôm nay & thời điểm reset)
  - `GET /api/v1/ai/provider-status` (Trạng thái AI Hub OpenRouter multi-key - chỉ ADMIN)
  - `POST /api/v1/ai/generate-testcases` (Tự động sinh testcase bằng AI OpenRouter)
  - `POST /api/v1/ai/review-code` (Phân tích lỗi và sinh nhận xét sư phạm cho bài WA)
  - `POST /api/v1/ai/verify-plagiarism` (Xác thực ngữ nghĩa nghi vấn đạo văn Vòng 2)
  - `POST /api/v1/ai/evaluate-web-ui` (Đánh giá giao diện Web qua ảnh chụp màn hình Multimodal)
- **Người thực hiện (Tester/Dev)**: Kim Chi Ha
- **Ngày tạo**: 04/10/2026
- **Cập nhật lần cuối**: 17/10/2026 - 10:00
- **Tài liệu liên quan**:
  - [Đặc tả API Phân hệ AI (Markdown)](file:///e:/AITA/docs/apis/ai/ai-api.md)
  - [Đặc tả OpenAPI Phân hệ AI (YAML)](file:///e:/AITA/docs/apis/ai/ai.yaml)
  - [Quy tắc kiểm thử Testcase](file:///e:/AITA/rules/testcase-rules.md)
- **Tổng số Testcase**: 88 Testcases (Phân loại: 16 Normal, 25 Boundary, 47 Exception)
  - `GET /ai/quota`: 09 Testcases (02 Normal, 01 Boundary, 06 Exception)
  - `GET /ai/provider-status`: 05 Testcases (01 Normal, 01 Boundary, 03 Exception)
  - `POST /ai/generate-testcases`: 17 Testcases (02 Normal, 05 Boundary, 10 Exception)
  - `POST /ai/review-code`: 15 Testcases (02 Normal, 04 Boundary, 09 Exception)
  - `POST /ai/verify-plagiarism`: 14 Testcases (02 Normal, 05 Boundary, 07 Exception)
  - `POST /ai/evaluate-web-ui`: 16 Testcases (03 Normal, 05 Boundary, 08 Exception)
  - `OpenRouterService (AiProvider)`: 12 Testcases (04 Normal, 04 Boundary, 04 Exception)

> **Ghi chú thiết kế (khớp mã nguồn `AiGatewayController`, `AiGatewayService`, `OpenRouterService`, `AiQuotaService`, các DTO)**:
> - Toàn bộ controller dùng `JwtAuthGuard, RolesGuard, AdaptiveThrottlerGuard` và `@Roles('INSTRUCTOR')`. Vì vậy cả người chưa đăng nhập (401) lẫn tài khoản `ADMIN` (403 `FORBIDDEN_ADMIN_ONLY`) đều không gọi được.
> - `AdaptiveThrottlerGuard` chặn `429 RATE_LIMIT_EXCEEDED` khi vượt giới hạn (các endpoint POST dùng `@Throttle` limit 15/phút).
> - `GenerateTestcasesDto`: `problem_description` chuỗi `20..5000`; `language` ∈ `{C, JAVA, PYTHON, WEB}`; `count` số nguyên `1..10` (mặc định 3); `include_boundary` boolean (mặc định true).
> - `ReviewCodeDto`: `source_code` chuỗi `10..10000`; `language` ∈ `{C, JAVA, PYTHON, PHP}`; `problem_statement` chuỗi `1..3000`; `failed_testcase` là object lồng gồm `input`, `expected_output`, `actual_output` (mỗi chuỗi ≤ 10000).
> - `VerifyPlagiarismDto`: `student_a_code`, `student_b_code` chuỗi `10..10000`; `ast_similarity_percentage` số trong `[80, 100]`; `language` ∈ `{C, JAVA, PYTHON, PHP}`.
> - `EvaluateWebUiDto`: `screenshot_base64` chuỗi ≤ 7.000.000 ký tự; `rubric_requirements` mảng `1..20` phần tử (mỗi chuỗi ≤ 500).
> - DTO validation message là **mặc định class-validator (tiếng Anh)**; lỗi lồng trong `failed_testcase` được báo qua `field = "failed_testcase"`.
> - Lỗi nghiệp vụ AI: `AI_QUOTA_NOT_CONFIGURED` (403), `AI_QUOTA_EXCEEDED` (429), `AI_INVALID_RESPONSE` (502), `AI_IMAGE_INVALID` (400), `AI_PROVIDER_ERROR` (502), `AI_PROVIDER_RATE_LIMITED` (429), `AI_NOT_CONFIGURED` (503).
> - `AiQuotaService.snapshot` trả `{ daily_limit_tokens, used_tokens_today, remaining_tokens (Math.max 0), reset_at_utc }`; tự reset `usedTokensToday` khi `lastResetDate` cũ hơn hôm nay (UTC).
> - `AiGatewayService` kiểm tra cấu trúc dữ liệu nhà cung cấp AI (OpenRouter) trả về và ném `AI_INVALID_RESPONSE` khi sai; `evaluateWebUi` tính lại `ui_score` = trung bình cộng các điểm, làm tròn 1 chữ số thập phân.
> - `GET /ai/provider-status` có `@Roles('ADMIN')` ghi đè `@Roles('INSTRUCTOR')` của controller: chỉ ADMIN gọi được, giảng viên nhận 403 `FORBIDDEN_ADMIN_ONLY`. Trả về danh sách API key OpenRouter kèm `state` (`READY`/`COOLDOWN`), `cooldown_remaining_seconds`, `accounts_configured`, `structured_outputs_supported`.
> - `OpenRouterService` xoay vòng nhiều API key; key bị `429`/`401`/`402`/`403` hoặc lỗi tạm thời sẽ bị đưa vào cooldown (rate: `OPENROUTER_KEY_COOLDOWN_MS`; exhausted: 30 phút; transient: 5 giây). Khi không còn key khả dụng vì tất cả đang cooldown, `generateJson` ném 429 `AI_PROVIDER_RATE_LIMITED`; lỗi không thuộc nhóm giới hạn/hết quota ném 502 `AI_PROVIDER_ERROR`. Không cấu hình key nào (`OPENROUTER_API_KEYS` rỗng) ném 503 `AI_NOT_CONFIGURED`.

---

# ==============================================================================

# PHẦN 1: API GET /api/v1/ai/quota (KIỂM TRA HẠN NGẠCH TOKEN HÔM NAY)

# ==============================================================================

# UT03_AiQuota_TC001: Không gửi Header Authorization trong yêu cầu lấy hạn ngạch

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Hệ thống AI Gateway đang hoạt động bình thường.

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

# UT03_AiQuota_TC002: Header Authorization chứa Bearer Token không hợp lệ hoặc sai chữ ký

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Hệ thống AI Gateway đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- Header `Authorization: Bearer <INVALID_TOKEN>`.

#### Các bước thực hiện (Test Steps)

1. Gọi `JwtAuthGuard.handleRequest(null, false, { name: 'JsonWebTokenError' })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401`, `error_code = "AUTH_INVALID_TOKEN"`, `message = "Token không hợp lệ."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiQuota_TC003: Bearer Token gửi lên đã hết hạn (Expired Token)

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

# UT03_AiQuota_TC004: Tài khoản người dùng trong Bearer Token đã bị vô hiệu hóa

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Token hợp lệ nhưng tài khoản đã bị xóa mềm/vô hiệu hóa.

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

# UT03_AiQuota_TC005: Lỗi máy chủ cơ sở dữ liệu nội bộ khi truy vấn hạn ngạch

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Dịch vụ cơ sở dữ liệu quản lý quota bị ngắt kết nối giả lập.

#### Dữ liệu kiểm thử (Test Data)

- `prisma.$transaction` ném `Error('Connection refused')`.

#### Các bước thực hiện (Test Steps)

1. Gọi `AiQuotaService.snapshot(userId)`; cho `ApiExceptionFilter` bắt ngoại lệ.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `500`, `error_code = "INTERNAL_SERVER_ERROR"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiQuota_TC006: Lấy thông tin hạn ngạch thành công khi tài khoản còn hạn ngạch

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Giảng viên đã xác thực, có cấu hình quota hợp lệ.

#### Dữ liệu kiểm thử (Test Data)

- `dailyTokenLimit = 50000`, `usedTokensToday = 15000`.

#### Các bước thực hiện (Test Steps)

1. `aiQuotaConfig.findFirst`/`findUnique` trả cấu hình quota; gọi `AiQuotaService.snapshot(userId)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200`, `daily_limit_tokens = 50000`, `used_tokens_today = 15000`, `remaining_tokens = 35000`, `reset_at_utc` là đầu ngày UTC kế tiếp.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiQuota_TC007: Lấy thông tin hạn ngạch thành công khi tài khoản đã dùng hết hạn ngạch (Biên 0 còn lại)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Giảng viên đã dùng đúng bằng hạn mức trong ngày.

#### Dữ liệu kiểm thử (Test Data)

- `dailyTokenLimit = 50000`, `usedTokensToday = 50000`.

#### Các bước thực hiện (Test Steps)

1. `aiQuotaConfig.findFirst`/`findUnique` trả cấu hình quota; gọi `AiQuotaService.snapshot(userId)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200`, `remaining_tokens = 0` (dùng `Math.max(0, ...)` để không trả số âm).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiQuota_TC008: Giảng viên chưa được cấu hình hạn ngạch AI

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Người dùng chưa có bản ghi `aiQuotaConfig` (hoặc bản ghi đã bị xóa mềm).

#### Dữ liệu kiểm thử (Test Data)

- `aiQuotaConfig.findFirst` trả `null`.

#### Các bước thực hiện (Test Steps)

1. Gọi `AiQuotaService.snapshot(userId)` khi không tìm thấy cấu hình quota.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `403`, `error_code = "AI_QUOTA_NOT_CONFIGURED"`, `message = "Tài khoản chưa được cấu hình hạn ngạch AI."`, `details = null`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiQuota_TC009: Tự động đặt lại hạn ngạch khi sang ngày UTC mới

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Bản ghi quota có `lastResetDate` là ngày hôm qua (UTC).

#### Dữ liệu kiểm thử (Test Data)

- `dailyTokenLimit = 50000`, `usedTokensToday = 40000`, `lastResetDate` = hôm qua.

#### Các bước thực hiện (Test Steps)

1. `aiQuotaConfig.findFirst` trả cấu hình cũ; `updateMany` reset; `findUnique` trả cấu hình đã reset; gọi `AiQuotaService.snapshot(userId)`.

#### Kết quả kỳ vọng (Expected Result)

- `updateMany` được gọi để reset; HTTP `200` với `used_tokens_today = 0`, `remaining_tokens = 50000`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# ==============================================================================

# PHẦN 2: API POST /api/v1/ai/generate-testcases (SINH TESTCASE TỰ ĐỘNG)

# ==============================================================================

# UT03_AiGenerateTestcases_TC001: Không gửi Header Authorization trong yêu cầu sinh testcase

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Hệ thống AI Gateway đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- Header `Authorization` bỏ trống.

#### Các bước thực hiện (Test Steps)

1. Gọi `JwtAuthGuard.handleRequest(null, false, undefined)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401`, `error_code = "AUTH_INVALID_TOKEN"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC002: Quản trị viên (ADMIN) không có quyền gọi API sinh testcase

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Người gọi xác thực hợp lệ với `role = "ADMIN"`.

#### Dữ liệu kiểm thử (Test Data)

- `request.user.role = "ADMIN"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `RolesGuard.canActivate(context)` với yêu cầu `@Roles('INSTRUCTOR')`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `403`, `error_code = "FORBIDDEN_ADMIN_ONLY"`, `message = "Bạn không có quyền thực hiện thao tác này."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC003: Tài khoản Giảng viên đã sử dụng hết hạn ngạch Token AI trong ngày

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Tài khoản đã dùng hết quota, bước `reserve` thất bại.

#### Dữ liệu kiểm thử (Test Data)

- `OpenRouterService.generateJson` ném `HttpException` 429 `AI_QUOTA_EXCEEDED`.

#### Các bước thực hiện (Test Steps)

1. Gọi `AiGatewayService.generateTestcases(userId, dto)` với `provider.generateJson` ném lỗi 429.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `429`, `error_code = "AI_QUOTA_EXCEEDED"`, `message = "Tài khoản của bạn đã sử dụng hết hạn ngạch Token AI trong ngày."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC004: Thiếu trường bắt buộc problem_description trong Body

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ language: "C" }` (thiếu `problem_description`).

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(body, { type: 'body', metatype: GenerateTestcasesDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "problem_description", issues: ["problem_description must be a string"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC005: problem_description có độ dài dưới 20 ký tự (Biên dưới)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- `problem_description = "Too short"` (9 ký tự).

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(body, { type: 'body', metatype: GenerateTestcasesDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "problem_description", issues: ["problem_description must be longer than or equal to 20 characters"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC006: problem_description vượt quá 5000 ký tự (Biên trên)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- `problem_description = "a".repeat(5001)`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(body, { type: 'body', metatype: GenerateTestcasesDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "problem_description", issues: ["problem_description must be shorter than or equal to 5000 characters"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC007: Thiếu trường bắt buộc language trong Body

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Body có `problem_description` hợp lệ nhưng thiếu `language`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(body, { type: 'body', metatype: GenerateTestcasesDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `field = "language"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC008: Ngôn ngữ lập trình không hợp lệ (Không thuộc Enum)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- `language = "JAVASCRIPT"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(body, { type: 'body', metatype: GenerateTestcasesDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "language", issues: ["language must be one of the following values: C, JAVA, PYTHON, WEB"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC009: Số lượng testcase count nằm ngoài khoảng [1, 10]

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Trường hợp A: `count = 0`. Trường hợp B: `count = 11`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(body, { type: 'body', metatype: GenerateTestcasesDto })` cho từng trường hợp.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `count must not be less than 1` (A) và `count must not be greater than 10` (B).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC010: Dịch vụ AI gặp sự cố kết nối hoặc quá tải

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Nhà cung cấp AI phản hồi lỗi (không phải 429).

#### Dữ liệu kiểm thử (Test Data)

- Client nội bộ ném lỗi `{ status: 503 }`.

#### Các bước thực hiện (Test Steps)

1. Gọi `OpenRouterService.generateJson(...)` với tầng HTTP `post()` ném `{ status: 503 }`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `502`, `error_code = "AI_PROVIDER_ERROR"`, `message = "Không thể nhận phản hồi từ dịch vụ AI."`, và quota đã đặt trước được hoàn (`release`).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC011: Phản hồi từ mô hình AI bị sai cấu trúc JSON

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- OpenRouter trả JSON thiếu trường `testcases` hoặc số phần tử không khớp `count`.

#### Dữ liệu kiểm thử (Test Data)

- `provider.generateJson` trả `{ data: { testcases: undefined }, tokensConsumed: 10 }`.

#### Các bước thực hiện (Test Steps)

1. Gọi `AiGatewayService.generateTestcases(userId, dto)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `502`, `error_code = "AI_INVALID_RESPONSE"`, `message = "Dịch vụ AI trả về dữ liệu không đúng định dạng."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC012: Sinh testcase thành công với tham số mặc định (count = 3, include_boundary = true)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Giảng viên đã xác thực, còn hạn ngạch, OpenRouter trả đúng cấu trúc.

#### Dữ liệu kiểm thử (Test Data)

- Body: `{ problem_description: <chuỗi hợp lệ>, language: "C" }`; OpenRouter trả 3 testcase hợp lệ.

#### Các bước thực hiện (Test Steps)

1. `provider.generateJson` trả `{ data: { testcases: [...3 phần tử...] }, tokensConsumed: 1234 }`; gọi `AiGatewayService.generateTestcases(userId, dto)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200`, `message = "Sinh testcase tự động bằng AI thành công"`, `data.tokens_consumed = 1234`, `data.testcases` có 3 phần tử đủ trường `input/expected_output/explanation/is_boundary`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC013: Sinh testcase thành công với số lượng biên dưới count = 1

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Giảng viên đã xác thực, còn hạn ngạch.

#### Dữ liệu kiểm thử (Test Data)

- `count = 1`; OpenRouter trả đúng 1 testcase.

#### Các bước thực hiện (Test Steps)

1. `provider.generateJson` trả 1 testcase hợp lệ; gọi `AiGatewayService.generateTestcases(userId, dto)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200`, `data.testcases` có đúng 1 phần tử.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC014: Sinh testcase thành công với số lượng biên trên count = 10

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Giảng viên đã xác thực, còn hạn ngạch.

#### Dữ liệu kiểm thử (Test Data)

- `count = 10`; OpenRouter trả đúng 10 testcase.

#### Các bước thực hiện (Test Steps)

1. `provider.generateJson` trả 10 testcase hợp lệ; gọi `AiGatewayService.generateTestcases(userId, dto)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200`, `data.testcases` có đúng 10 phần tử.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC015: Sinh testcase thành công với problem_description dài đúng biên dưới (20 ký tự)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động; còn hạn ngạch.

#### Dữ liệu kiểm thử (Test Data)

- `problem_description = "a".repeat(20)`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(...)` — không ném lỗi.
2. Gọi `AiGatewayService.generateTestcases(userId, dto)` với OpenRouter trả đúng `count` testcase.

#### Kết quả kỳ vọng (Expected Result)

- Validation hợp lệ, HTTP `200`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC016: Sinh testcase thành công cho ngôn ngữ PYTHON với include_boundary = false

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Giảng viên đã xác thực, còn hạn ngạch.

#### Dữ liệu kiểm thử (Test Data)

- `language = "PYTHON"`, `include_boundary = false`.

#### Các bước thực hiện (Test Steps)

1. `provider.generateJson` trả đúng testcase; gọi `AiGatewayService.generateTestcases(userId, dto)`.

#### Kết quả kỳ vọng (Expected Result)

- Prompt gửi OpenRouter chứa ngôn ngữ PYTHON và KHÔNG chèn cụm "including boundary cases"; HTTP `200`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC017: Vượt giới hạn tần suất gọi API AI (Throttle)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Giảng viên đã gửi quá 15 yêu cầu POST trong 60 giây.

#### Dữ liệu kiểm thử (Test Data)

- `AdaptiveThrottlerGuard` với `limit = 15`, `ttl = 60s`.

#### Các bước thực hiện (Test Steps)

1. `AdaptiveThrottlerGuard.throwThrottlingException(...)` khi vượt ngưỡng.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `429`, `error_code = "RATE_LIMIT_EXCEEDED"`, `message = "Bạn đã gửi quá nhiều yêu cầu. Vui lòng thử lại sau."`, `details = { limit: 15, retry_after_seconds: 60 }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# ==============================================================================

# PHẦN 3: API POST /api/v1/ai/review-code (PHÂN TÍCH LỖI BÀI WA)

# ==============================================================================

# UT03_AiReviewCode_TC001: Không gửi Header Authorization trong yêu cầu review code

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Hệ thống AI Gateway đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- Header `Authorization` bỏ trống.

#### Các bước thực hiện (Test Steps)

1. Gọi `JwtAuthGuard.handleRequest(null, false, undefined)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401`, `error_code = "AUTH_INVALID_TOKEN"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiReviewCode_TC002: Quản trị viên (ADMIN) không có quyền gọi API review code

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Người gọi xác thực hợp lệ với `role = "ADMIN"`.

#### Dữ liệu kiểm thử (Test Data)

- `request.user.role = "ADMIN"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `RolesGuard.canActivate(context)` với `@Roles('INSTRUCTOR')`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `403`, `error_code = "FORBIDDEN_ADMIN_ONLY"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiReviewCode_TC003: Giảng viên đã dùng hết hạn ngạch Token AI trong ngày

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Bước `reserve` thất bại do vượt quota.

#### Dữ liệu kiểm thử (Test Data)

- `provider.generateJson` ném `HttpException` 429 `AI_QUOTA_EXCEEDED`.

#### Các bước thực hiện (Test Steps)

1. Gọi `AiGatewayService.reviewCode(userId, dto)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `429`, `error_code = "AI_QUOTA_EXCEEDED"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiReviewCode_TC004: Thiếu trường bắt buộc source_code trong Body

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Body thiếu `source_code`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(body, { type: 'body', metatype: ReviewCodeDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "source_code", issues: ["source_code must be a string"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiReviewCode_TC005: source_code có độ dài nhỏ hơn 10 ký tự (Biên dưới)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- `source_code = "int a;"` (6 ký tự).

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(body, { type: 'body', metatype: ReviewCodeDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "source_code", issues: ["source_code must be longer than or equal to 10 characters"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiReviewCode_TC006: source_code vượt quá độ dài tối đa 10000 ký tự (Biên trên)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- `source_code = "a".repeat(10001)`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(body, { type: 'body', metatype: ReviewCodeDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "source_code", issues: ["source_code must be shorter than or equal to 10000 characters"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiReviewCode_TC007: Thiếu trường bắt buộc problem_statement trong Body

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Body thiếu `problem_statement`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(body, { type: 'body', metatype: ReviewCodeDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `field = "problem_statement"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiReviewCode_TC008: problem_statement vượt quá độ dài tối đa 3000 ký tự

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- `problem_statement = "a".repeat(3001)`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(body, { type: 'body', metatype: ReviewCodeDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "problem_statement", issues: ["problem_statement must be shorter than or equal to 3000 characters"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiReviewCode_TC009: Thiếu Object failed_testcase trong Body

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Body thiếu `failed_testcase`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(body, { type: 'body', metatype: ReviewCodeDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "failed_testcase", issues: ["failed_testcase must be an object"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiReviewCode_TC010: Object failed_testcase thiếu trường con bắt buộc (expected_output)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động (có `ValidateNested`).

#### Dữ liệu kiểm thử (Test Data)

- `failed_testcase = { input: "1 2", actual_output: "4" }` (thiếu `expected_output`).

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(body, { type: 'body', metatype: ReviewCodeDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `field = "failed_testcase"` (lỗi lồng từ DTO con được báo ở trường cha).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiReviewCode_TC011: Dịch vụ AI gặp sự cố kết nối hoặc model quá tải

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Nhà cung cấp AI phản hồi lỗi (không phải 429).

#### Dữ liệu kiểm thử (Test Data)

- OpenRouter ném `BadGatewayException` 502 `AI_PROVIDER_ERROR`.

#### Các bước thực hiện (Test Steps)

1. Gọi `AiGatewayService.reviewCode(userId, dto)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `502`, `error_code = "AI_PROVIDER_ERROR"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiReviewCode_TC012: Phân tích lỗi mã nguồn C thành công (Lỗi Off-by-one trong vòng for)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Giảng viên đã xác thực, còn hạn ngạch; OpenRouter trả cấu trúc hợp lệ.

#### Dữ liệu kiểm thử (Test Data)

- `source_code` C lỗi `for (i = 0; i <= n; i++)`; OpenRouter trả `suspected_error_line = 4`, các trường chuỗi đầy đủ.

#### Các bước thực hiện (Test Steps)

1. `provider.generateJson` trả `{ data: { suspected_error_line: 4, issue_summary, pedagogical_feedback, bug_category }, tokensConsumed: 900 }`; gọi `AiGatewayService.reviewCode(userId, dto)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200`, `message = "Phân tích mã nguồn bằng AI thành công"`, `data.suspected_error_line = 4`, `data.tokens_consumed = 900`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiReviewCode_TC013: Phân tích lỗi mã nguồn Java thành công (Không xác định được dòng lỗi)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Giảng viên đã xác thực, còn hạn ngạch.

#### Dữ liệu kiểm thử (Test Data)

- OpenRouter KHÔNG trả `suspected_error_line` (trường tùy chọn).

#### Các bước thực hiện (Test Steps)

1. `provider.generateJson` trả dữ liệu hợp lệ không có `suspected_error_line`; gọi `AiGatewayService.reviewCode(userId, dto)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200`, `data.suspected_error_line` là `undefined` nhưng vẫn hợp lệ.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiReviewCode_TC014: Phân tích mã nguồn với source_code dài đúng biên dưới (10 ký tự)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động; còn hạn ngạch.

#### Dữ liệu kiểm thử (Test Data)

- `source_code = "a".repeat(10)`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(...)` — không ném lỗi.
2. Gọi `AiGatewayService.reviewCode(userId, dto)` với OpenRouter trả dữ liệu hợp lệ.

#### Kết quả kỳ vọng (Expected Result)

- Validation hợp lệ, HTTP `200`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiReviewCode_TC015: Phân tích mã nguồn với failed_testcase chứa chuỗi rỗng biên (actual_output = "")

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động; còn hạn ngạch.

#### Dữ liệu kiểm thử (Test Data)

- `failed_testcase.actual_output = ""`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(...)` — không ném lỗi (chuỗi rỗng vẫn hợp lệ do chỉ có `MaxLength`).
2. Gọi `AiGatewayService.reviewCode(userId, dto)` với OpenRouter trả dữ liệu hợp lệ.

#### Kết quả kỳ vọng (Expected Result)

- Chuỗi rỗng hợp lệ, HTTP `200`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# ==============================================================================

# PHẦN 4: API POST /api/v1/ai/verify-plagiarism (XÁC THỰC ĐẠO VĂN VÒNG 2)

# ==============================================================================

# UT03_AiVerifyPlagiarism_TC001: Không gửi Header Authorization trong yêu cầu xác thực đạo văn

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Hệ thống AI Gateway đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- Header `Authorization` bỏ trống.

#### Các bước thực hiện (Test Steps)

1. Gọi `JwtAuthGuard.handleRequest(null, false, undefined)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401`, `error_code = "AUTH_INVALID_TOKEN"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiVerifyPlagiarism_TC002: Quản trị viên (ADMIN) không có quyền gọi API xác thực đạo văn

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Người gọi xác thực hợp lệ với `role = "ADMIN"`.

#### Dữ liệu kiểm thử (Test Data)

- `request.user.role = "ADMIN"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `RolesGuard.canActivate(context)` với `@Roles('INSTRUCTOR')`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `403`, `error_code = "FORBIDDEN_ADMIN_ONLY"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiVerifyPlagiarism_TC003: Giảng viên đã dùng hết hạn ngạch Token AI trong ngày

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Bước `reserve` thất bại do vượt quota.

#### Dữ liệu kiểm thử (Test Data)

- `provider.generateJson` ném `HttpException` 429 `AI_QUOTA_EXCEEDED`.

#### Các bước thực hiện (Test Steps)

1. Gọi `AiGatewayService.verifyPlagiarism(userId, dto)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `429`, `error_code = "AI_QUOTA_EXCEEDED"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiVerifyPlagiarism_TC004: Thiếu trường bắt buộc student_a_code hoặc student_b_code

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Body thiếu `student_b_code`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(body, { type: 'body', metatype: VerifyPlagiarismDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "student_b_code", issues: ["student_b_code must be a string"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiVerifyPlagiarism_TC005: student_a_code hoặc student_b_code có độ dài dưới 10 ký tự

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- `student_a_code = "abc"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(body, { type: 'body', metatype: VerifyPlagiarismDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "student_a_code", issues: ["student_a_code must be longer than or equal to 10 characters"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiVerifyPlagiarism_TC006: student_a_code hoặc student_b_code vượt quá 10000 ký tự

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- `student_a_code = "a".repeat(10001)`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(body, { type: 'body', metatype: VerifyPlagiarismDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "student_a_code", issues: ["student_a_code must be shorter than or equal to 10000 characters"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiVerifyPlagiarism_TC007: ast_similarity_percentage nhỏ hơn 80.0% (Biên dưới)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- `ast_similarity_percentage = 79.9`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(body, { type: 'body', metatype: VerifyPlagiarismDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "ast_similarity_percentage", issues: ["ast_similarity_percentage must not be less than 80"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiVerifyPlagiarism_TC008: ast_similarity_percentage lớn hơn 100.0% (Biên trên)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- `ast_similarity_percentage = 100.1`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(body, { type: 'body', metatype: VerifyPlagiarismDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "ast_similarity_percentage", issues: ["ast_similarity_percentage must not be greater than 100"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiVerifyPlagiarism_TC009: Thiếu trường bắt buộc language trong Body

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Body thiếu `language`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(body, { type: 'body', metatype: VerifyPlagiarismDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `field = "language"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiVerifyPlagiarism_TC010: Dịch vụ AI gặp sự cố kết nối hoặc mạng bị timeout

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Nhà cung cấp AI phản hồi lỗi.

#### Dữ liệu kiểm thử (Test Data)

- OpenRouter ném `BadGatewayException` 502 `AI_PROVIDER_ERROR`.

#### Các bước thực hiện (Test Steps)

1. Gọi `AiGatewayService.verifyPlagiarism(userId, dto)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `502`, `error_code = "AI_PROVIDER_ERROR"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiVerifyPlagiarism_TC011: Xác thực thành công nghi vấn đạo văn tinh vi (Đổi tên biến & đảo câu lệnh if)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Giảng viên đã xác thực, còn hạn ngạch; OpenRouter trả cấu trúc hợp lệ.

#### Dữ liệu kiểm thử (Test Data)

- OpenRouter trả `is_plagiarized = true`, `confidence_percentage = 92`, `cloned_segments` có 1 phần tử.

#### Các bước thực hiện (Test Steps)

1. `provider.generateJson` trả dữ liệu hợp lệ; gọi `AiGatewayService.verifyPlagiarism(userId, dto)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200`, `message = "Phân tích bằng chứng đạo văn thành công"`, `data.is_plagiarized = true`, `data.confidence_percentage = 92`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiVerifyPlagiarism_TC012: Xác thực thành công khi độ tương đồng đúng biên dưới 80.0% (Biên dưới hợp lệ)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động; còn hạn ngạch.

#### Dữ liệu kiểm thử (Test Data)

- `ast_similarity_percentage = 80`; OpenRouter trả `is_plagiarized = false`, `confidence_percentage = 30`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(...)` — không ném lỗi.
2. Gọi `AiGatewayService.verifyPlagiarism(userId, dto)` với OpenRouter trả `is_plagiarized = false`.

#### Kết quả kỳ vọng (Expected Result)

- Hợp lệ, HTTP `200`, `data.is_plagiarized = false` (kết luận trùng hợp ngẫu nhiên).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiVerifyPlagiarism_TC013: Xác thực thành công khi độ tương đồng đạt biên trên tối đa 100.0% (Sao chép nguyên văn)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động; còn hạn ngạch.

#### Dữ liệu kiểm thử (Test Data)

- `ast_similarity_percentage = 100`; OpenRouter trả `is_plagiarized = true`, `confidence_percentage = 100`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(...)` — không ném lỗi.
2. Gọi `AiGatewayService.verifyPlagiarism(userId, dto)` với OpenRouter trả `is_plagiarized = true`.

#### Kết quả kỳ vọng (Expected Result)

- Hợp lệ, HTTP `200`, `data.confidence_percentage = 100`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiVerifyPlagiarism_TC014: Xác thực thành công cho bài thi Java với kỹ thuật tách hàm con (Modular Refactoring)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Giảng viên đã xác thực, còn hạn ngạch.

#### Dữ liệu kiểm thử (Test Data)

- `language = "JAVA"`, `student_a_code`/`student_b_code` khác cấu trúc hàm nhưng tương đồng logic.

#### Các bước thực hiện (Test Steps)

1. `provider.generateJson` trả `cloned_segments` = `[]` nhưng `is_plagiarized = true`; gọi `AiGatewayService.verifyPlagiarism(userId, dto)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200`, `data.cloned_segments = []` vẫn hợp lệ (mảng rỗng được chấp nhận).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# ==============================================================================

# PHẦN 5: API POST /api/v1/ai/evaluate-web-ui (ĐÁNH GIÁ GIAO DIỆN WEB)

# ==============================================================================

# UT03_AiEvaluateWebUI_TC001: Không gửi Header Authorization trong yêu cầu đánh giá giao diện Web

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Hệ thống AI Gateway đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- Header `Authorization` bỏ trống.

#### Các bước thực hiện (Test Steps)

1. Gọi `JwtAuthGuard.handleRequest(null, false, undefined)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401`, `error_code = "AUTH_INVALID_TOKEN"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiEvaluateWebUI_TC002: Quản trị viên (ADMIN) không có quyền gọi API chấm giao diện Web

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Người gọi xác thực hợp lệ với `role = "ADMIN"`.

#### Dữ liệu kiểm thử (Test Data)

- `request.user.role = "ADMIN"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `RolesGuard.canActivate(context)` với `@Roles('INSTRUCTOR')`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `403`, `error_code = "FORBIDDEN_ADMIN_ONLY"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiEvaluateWebUI_TC003: Giảng viên đã dùng hết hạn ngạch Token AI trong ngày

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Bước `reserve` thất bại do vượt quota.

#### Dữ liệu kiểm thử (Test Data)

- `provider.generateJson` ném `HttpException` 429 `AI_QUOTA_EXCEEDED`.

#### Các bước thực hiện (Test Steps)

1. Gọi `AiGatewayService.evaluateWebUi(userId, dto)` với ảnh hợp lệ.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `429`, `error_code = "AI_QUOTA_EXCEEDED"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiEvaluateWebUI_TC004: Thiếu trường bắt buộc screenshot_base64 trong Body

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Body thiếu `screenshot_base64`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(body, { type: 'body', metatype: EvaluateWebUiDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "screenshot_base64", issues: ["screenshot_base64 must be a string"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiEvaluateWebUI_TC005: screenshot_base64 không phải định dạng chuỗi Base64 hợp lệ

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` đã cho qua; `AiGatewayService.decodeImage` kiểm tra định dạng.

#### Dữ liệu kiểm thử (Test Data)

- `screenshot_base64 = "not base64!!!"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `AiGatewayService.evaluateWebUi(userId, dto)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `400`, `error_code = "AI_IMAGE_INVALID"`, `message = "Ảnh phải là dữ liệu PNG/JPEG base64 hợp lệ."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiEvaluateWebUI_TC006: screenshot_base64 vượt quá dung lượng tối đa 5MB (Biên trên)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Ảnh giải mã vượt 5 MB.

#### Dữ liệu kiểm thử (Test Data)

- Base64 giải mã thành `5 MB + 1 byte`.

#### Các bước thực hiện (Test Steps)

1. Gọi `AiGatewayService.evaluateWebUi(userId, dto)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `400`, `error_code = "AI_IMAGE_INVALID"`, `message = "Ảnh phải có kích thước tối đa 5 MB."`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiEvaluateWebUI_TC007: Thiếu trường rubric_requirements trong Body

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- Body thiếu `rubric_requirements`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(body, { type: 'body', metatype: EvaluateWebUiDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "rubric_requirements", issues: ["rubric_requirements must be an array"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiEvaluateWebUI_TC008: rubric_requirements là mảng rỗng không có phần tử nào (Biên dưới)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động.

#### Dữ liệu kiểm thử (Test Data)

- `rubric_requirements = []`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(body, { type: 'body', metatype: EvaluateWebUiDto })`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `details` chứa `{ field: "rubric_requirements", issues: ["rubric_requirements must contain at least 1 elements"] }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiEvaluateWebUI_TC009: Dịch vụ AI Multimodal Vision gặp sự cố hoặc timeout phản hồi

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Nhà cung cấp AI phản hồi lỗi.

#### Dữ liệu kiểm thử (Test Data)

- OpenRouter ném `BadGatewayException` 502 `AI_PROVIDER_ERROR`.

#### Các bước thực hiện (Test Steps)

1. Gọi `AiGatewayService.evaluateWebUi(userId, dto)` với ảnh hợp lệ.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `502`, `error_code = "AI_PROVIDER_ERROR"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiEvaluateWebUI_TC010: Đánh giá giao diện Web thành công với 3 tiêu chí rubric chuẩn

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Giảng viên đã xác thực, còn hạn ngạch; OpenRouter trả cấu trúc hợp lệ.

#### Dữ liệu kiểm thử (Test Data)

- Ảnh PNG hợp lệ; 3 tiêu chí; OpenRouter trả điểm `[9, 8, 7]` với verdict PASS/PASS/PARTIAL.

#### Các bước thực hiện (Test Steps)

1. `provider.generateJson` trả `evaluation_details` khớp 3 tiêu chí; gọi `AiGatewayService.evaluateWebUi(userId, dto)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200`, `message = "Đánh giá giao diện Web bằng AI thành công"`, `data.ui_score = 8` (trung bình 8.0).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiEvaluateWebUI_TC011: Đánh giá giao diện Web thành công với đúng 1 tiêu chí rubric (Biên dưới)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `ValidationPipe` toàn cục đang hoạt động; còn hạn ngạch.

#### Dữ liệu kiểm thử (Test Data)

- `rubric_requirements` có đúng 1 phần tử; OpenRouter trả 1 `evaluation_details`.

#### Các bước thực hiện (Test Steps)

1. Gọi `ValidationPipe.transform(...)` — không ném lỗi.
2. Gọi `AiGatewayService.evaluateWebUi(userId, dto)` với OpenRouter trả đúng 1 phần tử.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200`, `data.ui_score` bằng điểm của tiêu chí duy nhất.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiEvaluateWebUI_TC012: Đánh giá giao diện Web thành công với ảnh định dạng JPEG chất lượng cao

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Giảng viên đã xác thực, còn hạn ngạch.

#### Dữ liệu kiểm thử (Test Data)

- `screenshot_base64` là data URL `data:image/jpeg;base64,...` hợp lệ.

#### Các bước thực hiện (Test Steps)

1. Gọi `AiGatewayService.evaluateWebUi(userId, dto)` với OpenRouter trả dữ liệu hợp lệ.

#### Kết quả kỳ vọng (Expected Result)

- `decodeImage` chấp nhận JPEG; HTTP `200`, `data.ui_score` được tính đúng.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiEvaluateWebUI_TC013: Đánh giá thành công khi bài làm vi phạm rubric (ui_score thấp, verdict FAIL)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Giảng viên đã xác thực, còn hạn ngạch.

#### Dữ liệu kiểm thử (Test Data)

- OpenRouter trả điểm thấp `[2, 3, 1]` với verdict FAIL.

#### Các bước thực hiện (Test Steps)

1. `provider.generateJson` trả `evaluation_details` toàn FAIL; gọi `AiGatewayService.evaluateWebUi(userId, dto)`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200`, `data.ui_score = 2` (trung bình 2.0), các `verdict` đều `FAIL`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiEvaluateWebUI_TC014: rubric_requirements vượt 20 phần tử (Biên trên)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Giảng viên đã xác thực; ảnh hợp lệ.

#### Dữ liệu kiểm thử (Test Data)

- `rubric_requirements` có 21 phần tử.

#### Các bước thực hiện (Test Steps)

1. Gọi `createValidationPipe()` với `EvaluateWebUiDto` và payload 21 tiêu chí.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `error_code = "VALIDATION_FAILED"`, `details` chứa `field = "rubric_requirements"` với issue `rubric_requirements must contain no more than 20 elements`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiEvaluateWebUI_TC015: Phần tử rubric vượt 500 ký tự (Biên trên)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Giảng viên đã xác thực; ảnh hợp lệ.

#### Dữ liệu kiểm thử (Test Data)

- `rubric_requirements = ["a" × 501]`.

#### Các bước thực hiện (Test Steps)

1. Gọi `createValidationPipe()` với `EvaluateWebUiDto` và 1 tiêu chí dài 501 ký tự.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `error_code = "VALIDATION_FAILED"`, `details` chứa `field = "rubric_requirements"` với issue `each value in rubric_requirements must be shorter than or equal to 500 characters`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiEvaluateWebUI_TC016: screenshot_base64 vượt 7.000.000 ký tự (Biên trên)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Giảng viên đã xác thực.

#### Dữ liệu kiểm thử (Test Data)

- `screenshot_base64` dài 7.000.001 ký tự.

#### Các bước thực hiện (Test Steps)

1. Gọi `createValidationPipe()` với `EvaluateWebUiDto` và ảnh vượt giới hạn.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `422`, `error_code = "VALIDATION_FAILED"`, `details` chứa `field = "screenshot_base64"` với issue `screenshot_base64 must be shorter than or equal to 7000000 characters`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# ==============================================================================

# PHẦN 6: API GET /api/v1/ai/provider-status (TRẠNG THÁI AI HUB OPENROUTER)

# ==============================================================================

# UT03_AiProviderStatus_TC001: Không gửi Header Authorization trong yêu cầu lấy trạng thái AI

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Hệ thống AI Gateway đang hoạt động bình thường.

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

# UT03_AiProviderStatus_TC002: Bearer Token đã hết hạn (Expired Token)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Token hết hạn được gửi lên.

#### Dữ liệu kiểm thử (Test Data)

- `handleRequest(null, false, { name: 'TokenExpiredError' })`.

#### Các bước thực hiện (Test Steps)

1. Gọi `JwtAuthGuard.handleRequest` với lỗi `TokenExpiredError`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `401`, `error_code = "AUTH_TOKEN_EXPIRED"`, `message = "Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại."`, `details = null`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiProviderStatus_TC003: Giảng viên (INSTRUCTOR) không có quyền xem trạng thái AI

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Người dùng đã đăng nhập với vai trò `INSTRUCTOR`.

#### Dữ liệu kiểm thử (Test Data)

- `@Roles('ADMIN')` ghi đè; `RolesGuard` với metadata `['ADMIN']`.

#### Các bước thực hiện (Test Steps)

1. Xác thực request với user `role = "INSTRUCTOR"` qua `RolesGuard`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `403`, `error_code = "FORBIDDEN_ADMIN_ONLY"`, `message = "Bạn không có quyền thực hiện thao tác này."`, `details = null`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiProviderStatus_TC004: ADMIN lấy trạng thái AI Hub thành công (tất cả key READY)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Cấu hình 2 API key OpenRouter, không key nào đang cooldown.

#### Dữ liệu kiểm thử (Test Data)

- `OPENROUTER_API_KEYS = "key-a,key-b"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `OpenRouterService.providerStatus()` với tất cả key đang READY.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200`, `data.provider = "openrouter"`, `accounts_configured = 2`, `structured_outputs_supported = true`; mỗi account có `state = "READY"`, `cooldown_remaining_seconds = 0`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiProviderStatus_TC005: Trạng thái khi một key đang COOLDOWN (Biên)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Một API key vừa gặp lỗi và đang trong thời gian cooldown.

#### Dữ liệu kiểm thử (Test Data)

- 1 key, `cooldownUntil` đặt trong tương lai.

#### Các bước thực hiện (Test Steps)

1. Giả lập key trong cooldown rồi gọi `OpenRouterService.providerStatus()`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `200`, account tương ứng có `state = "COOLDOWN"` và `cooldown_remaining_seconds > 0`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# ==============================================================================

# PHẦN 7: DỊCH VỤ NHÀ CUNG CẤP AI (OpenRouterService - XOAY VÒNG NHIỀU API KEY)

# ==============================================================================

# UT03_AiProvider_TC001: Gọi thành công qua tài khoản quay vòng trong pool

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Pool có 3 API key OpenRouter; `post()` trả nội dung JSON hợp lệ.

#### Dữ liệu kiểm thử (Test Data)

- `OPENROUTER_API_KEYS = "key-1,key-2,key-3"`, `schema` kiểu object có `ok`.

#### Các bước thực hiện (Test Steps)

1. Gọi `OpenRouterService.generateJson(...)` 3 lần liên tiếp.

#### Kết quả kỳ vọng (Expected Result)

- Lần lượt dùng `key-1`, `key-2`, `key-3`; body gửi đi có `model = "openrouter/free"`, `temperature = 0.2`, `max_tokens = 100`, 2 message và `response_format.type = "json_schema"`; trả `{ data: { ok: true }, tokensConsumed: 15 }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiProvider_TC002: Token usage từ provider được ghi vết qua settle

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Provider trả `usage` thực tế `{ prompt_tokens: 120, completion_tokens: 80, total_tokens: 200 }`.

#### Dữ liệu kiểm thử (Test Data)

- 1 API key; `feature = "TESTCASE_GEN"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `generateJson` và kiểm tra lời gọi `quota.settle`.

#### Kết quả kỳ vọng (Expected Result)

- `tokensConsumed = 200`; `settle` nhận đúng prompt/completion/total tokens; `release` không được gọi.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiProvider_TC003: Tài khoản bị 429 thì tự chuyển sang tài khoản kế tiếp

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Pool có 2 API key; key đầu trả `429`, key thứ hai thành công.

#### Dữ liệu kiểm thử (Test Data)

- `OPENROUTER_API_KEYS = "key-1,key-2"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `generateJson` khi key-1 bị 429 và key-2 trả JSON hợp lệ.

#### Kết quả kỳ vọng (Expected Result)

- `post` được gọi 2 lần theo thứ tự `key-1`, `key-2`; trả kết quả thành công; `settle` gọi 1 lần; `release` không được gọi.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiProvider_TC004: Tất cả tài khoản đều bị giới hạn

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Pool 3 API key; mọi key đều trả `429`.

#### Dữ liệu kiểm thử (Test Data)

- `OPENROUTER_API_KEYS = "key-1,key-2,key-3"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `generateJson` khi tất cả request đều bị 429.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `429`, `error_code = "AI_PROVIDER_RATE_LIMITED"`; `post` gọi 3 lần; `release` được gọi để hoàn quota; `settle` không được gọi.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiProvider_TC005: Tài khoản đang cooldown bị bỏ qua ở lượt gọi kế tiếp (Biên)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Lượt gọi đầu làm toàn bộ key bị 429 và rơi vào cooldown.

#### Dữ liệu kiểm thử (Test Data)

- `OPENROUTER_API_KEYS = "key-1,key-2"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `generateJson` lần 1 (thất bại do 429).
2. Gọi `generateJson` lần 2 ngay sau đó.

#### Kết quả kỳ vọng (Expected Result)

- Cả hai lượt đều ném `429`; `post` chỉ được gọi 2 lần ở lượt đầu, lượt hai bỏ qua key đang cooldown (không đốt thêm request).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiProvider_TC006: Model không hỗ trợ response_format thì fallback tự động (Biên)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Model trả `400` với thông báo không hỗ trợ `json_schema`.

#### Dữ liệu kiểm thử (Test Data)

- 1 API key; lỗi `400 "response_format json_schema is not supported for this model"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `generateJson`; lần 1 bị 400 do `response_format`, lần 2 retry không kèm `response_format`.

#### Kết quả kỳ vọng (Expected Result)

- `post` gọi 2 lần; body lần 2 không có `response_format` và schema được nhúng vào prompt (`messages[0].content` chứa "JSON Schema"); trả kết quả thành công.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiProvider_TC007: Phản hồi bọc markdown code fence (Biên)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Provider trả nội dung ` ```json ... ``` `.

#### Dữ liệu kiểm thử (Test Data)

- `content = "```json\n{\"ok\":true}\n```"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `generateJson` với phản hồi bọc code fence.

#### Kết quả kỳ vọng (Expected Result)

- Bóc tách được code fence và trả `data = { ok: true }`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiProvider_TC008: Tính năng chấm UI gửi ảnh kèm prompt (Biên chức năng vision)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `feature = "UI_EVALUATION"` và có ảnh PNG.

#### Dữ liệu kiểm thử (Test Data)

- `image = { mimeType: "image/png", base64: "QUJD" }`.

#### Các bước thực hiện (Test Steps)

1. Gọi `generateJson` kèm `image`.

#### Kết quả kỳ vọng (Expected Result)

- `messages[1].content` gồm 1 phần tử text và 1 phần tử `image_url` với URL `data:image/png;base64,QUJD`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiProvider_TC009: Chưa cấu hình tài khoản AI nào

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- `OPENROUTER_API_KEYS` rỗng.

#### Dữ liệu kiểm thử (Test Data)

- `OPENROUTER_API_KEYS = ""`.

#### Các bước thực hiện (Test Steps)

1. Gọi `generateJson`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `503`, `error_code = "AI_NOT_CONFIGURED"`; `quota.reserve` và `post` không được gọi.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiProvider_TC010: Nhà cung cấp lỗi tạm thời chỉ có 1 tài khoản

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Pool chỉ có 1 API key; provider trả `503`.

#### Dữ liệu kiểm thử (Test Data)

- `OPENROUTER_API_KEYS = "key-1"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `generateJson` khi provider lỗi tạm thời.

#### Kết quả kỳ vọng (Expected Result)

- HTTP `502`, `error_code = "AI_PROVIDER_ERROR"`, `message = "Không thể nhận phản hồi từ dịch vụ AI."`; `post` gọi 1 lần; `release` được gọi; `settle` không được gọi.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiProvider_TC011: Tài khoản hết hạn mức credits (402)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Pool 2 API key; provider trả `402` (hết credits).

#### Dữ liệu kiểm thử (Test Data)

- `OPENROUTER_API_KEYS = "key-1,key-2"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `generateJson` khi mọi key bị 402.

#### Kết quả kỳ vọng (Expected Result)

- `402` được xếp vào nhóm capacity nên trả `429`, `error_code = "AI_PROVIDER_RATE_LIMITED"`; `post` gọi 2 lần và không thử lại key vừa lỗi.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiProvider_TC012: Trạng thái pool phục vụ Web Admin

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Cấu hình 2 API key OpenRouter.

#### Dữ liệu kiểm thử (Test Data)

- `OPENROUTER_API_KEYS = "sk-or-v1-fedcba987654,sk-or-v1-0123456789ab"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `OpenRouterService.providerStatus()`.

#### Kết quả kỳ vọng (Expected Result)

- `provider = "openrouter"`, `model = "openrouter/free"`, `accounts_configured = 2`; `accounts[0] = { account: "ACC-01", key_hint: "sk-or-v1-…7654", state: "READY", cooldown_remaining_seconds: 0 }`; response không chứa key gốc.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |


