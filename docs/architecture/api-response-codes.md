# Quy Chuẩn Mã Phản Hồi & Cấu Trúc Dữ Liệu API (API Status & Response Codes Specification)

## Dự án: AITA - Automated Grading & Assessment Tool for Instructors

Tài liệu này định nghĩa chuẩn mực cấu trúc phản hồi (Response Envelope) và danh mục toàn bộ mã trạng thái HTTP (200, 400, 401, 403, 404, 422, 429, 500) cùng các mã lỗi nghiệp vụ (Business Error Codes) áp dụng cho **Web Server Backend (NestJS)**, **Web Admin Dashboard (Next.js)** và **Desktop App Client (PyQt6)** trước khi bước vào giai đoạn lập trình.

---

## 1. Cấu Trúc Phản Hồi Chuẩn (Standard Response Envelope Schema)

Tất cả các API của hệ thống AITA đều trả về dữ liệu định dạng **JSON** theo cấu trúc bao bọc nhất quán (Consistent Envelope Pattern):

### 1.1. Cấu trúc phản hồi Thành công (Success Response) - HTTP 200, 201

Áp dụng khi thao tác thực hiện thành công:

```json
{
  "success": true,
  "status_code": 200,
  "message": "Thao tác thành công",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "teacher_hung",
    "full_name": "Nguyễn Văn Hùng",
    "role": "INSTRUCTOR"
  },
  "timestamp": "2026-09-13T02:30:00Z"
}
```

* **`success`** (`bool`): Luôn luôn là `true`.
* **`status_code`** (`int`): Mã trạng thái HTTP (200, 201).
* **`message`** (`str`): Thông điệp mô tả ngắn gọn bằng tiếng Việt thân thiện với người dùng.
* **`data`** (`object` | `array` | `null`): Dữ liệu kết quả nghiệp vụ trả về.
* **`timestamp`** (`str`): Mốc thời gian ISO 8601 chuẩn UTC.

---

### 1.2. Cấu trúc phản hồi Thất bại / Lỗi (Error Response) - HTTP 400, 401, 403, 404, 422, 429, 500

Áp dụng khi xảy ra lỗi nghiệp vụ, lỗi thẩm định dữ liệu hoặc lỗi hệ thống:

```json
{
  "success": false,
  "status_code": 429,
  "error_code": "AI_QUOTA_EXCEEDED",
  "message": "Tài khoản của bạn đã sử dụng hết hạn ngạch Token AI trong ngày.",
  "details": null,
  "timestamp": "2026-10-21T02:30:00Z"
}
```

* **`success`** (`bool`): Luôn luôn là `false`.
* **`status_code`** (`int`): Mã trạng thái HTTP tương ứng (400, 401, 403, 404, 422, 429, 500).
* **`error_code`** (`str`): Mã định danh lỗi nghiệp vụ viết hoa (UPPER_SNAKE_CASE) để phía Client (Desktop App / Web Admin) bắt chính xác mà không phụ thuộc vào chuỗi text `message`.
* **`message`** (`str`): Mô tả lỗi thân thiện, trực quan để hiển thị trực tiếp lên giao diện người dùng.
* **`details`** (`array` | `object` | `null`): Thông tin chi tiết về lỗi (ví dụ: danh sách lỗi thẩm định của DTO — khi Validation Pipe trả về `message` dạng mảng, filter sẽ chuyển thành `details`).
* **`timestamp`** (`str`): Mốc thời gian ISO 8601 chuẩn UTC.

---

### 1.3. Cấu trúc phản hồi Danh sách & Phân trang (Pagination Response) - HTTP 200

Áp dụng cho các API lấy danh sách dữ liệu (quản lý user, nhật ký AI, nhật ký kiểm toán):

```json
{
  "success": true,
  "status_code": 200,
  "message": "Lấy danh sách người dùng thành công",
  "data": {
    "items": [
      { "id": "550e8400-e29b-41d4-a716-446655440000", "username": "teacher_hung", "full_name": "Nguyễn Văn Hùng", "email": "hung@univ.edu.vn", "role": "INSTRUCTOR", "is_active": true, "is_deleted": false, "daily_token_quota": 50000, "used_tokens_today": 1024, "created_at": "2026-09-01T03:00:00Z", "updated_at": "2026-10-01T09:00:00Z" },
      { "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8", "username": "admin", "full_name": "Quản trị viên", "email": "admin@univ.edu.vn", "role": "ADMIN", "is_active": true, "is_deleted": false, "daily_token_quota": 50000, "used_tokens_today": 0, "created_at": "2026-09-01T03:00:00Z", "updated_at": "2026-09-20T11:00:00Z" }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_items": 4,
      "total_pages": 1
    }
  },
  "timestamp": "2026-10-21T02:30:00Z"
}
```

---

## 2. Bảng Phân Loại Mã Trạng Thái HTTP Chuẩn (Standard HTTP Status Codes)

Hệ thống AITA tuân thủ nghiêm ngặt chuẩn **RFC 9110 HTTP Semantics**:

| HTTP Code | Định danh chuẩn | Ý nghĩa trong hệ thống AITA | Khi nào áp dụng? |
| :---: | :--- | :--- | :--- |
| **`200`** | **`OK`** | Yêu cầu xử lý thành công hoàn toàn. | Các request `GET`, `PUT`, `DELETE` hoặc xử lý nghiệp vụ thành công (bao gồm cả **Xóa user — trả về `200` với `data: null`**). |
| **`201`** | **`Created`** | Tạo mới tài nguyên thành công. | Khi tạo mới User. |
| **`204`** | **`No Content`** | Thực hiện thành công nhưng không có body trả về. | *Không sử dụng* — mọi endpoint thành công đều trả envelope JSON. |
| **`400`** | **`Bad Request`** | Dữ liệu gửi lên sai quy chuẩn nghiệp vụ. | Khoảng thời gian báo cáo sai (`from` > `to`), payload AI thiếu/giá trị sai. |
| **`401`** | **`Unauthorized`** | Chưa xác thực hoặc Token không hợp lệ/hết hạn. | Thiếu header `Authorization: Bearer <JWT>`, sai mật khẩu, refresh token sai/hết hạn. |
| **`403`** | **`Forbidden`** | Đã xác thực nhưng không có quyền truy cập. | Giảng viên gọi endpoint quản trị (`@Roles('admin')`); tài khoản bị khóa; tự khóa/xóa chính mình. |
| **`404`** | **`Not Found`** | Không tìm thấy tài nguyên yêu cầu. | Không tìm thấy User ID yêu cầu. |
| **`409`** | **`Conflict`** | Xung đột dữ liệu trong CSDL. | Tạo tài khoản `username`/`email` đã tồn tại; vô hiệu hóa/xóa Admin hoạt động cuối cùng. |
| **`422`** | **`Unprocessable Entity`** | Lỗi thẩm định cấu trúc dữ liệu (DTO Validation). | Thiếu trường bắt buộc, sai kiểu dữ liệu, sai định dạng mật khẩu/username. |
| **`429`** | **`Too Many Requests`** | Vượt quá hạn ngạch (Rate Limit / AI Quota). | Vượt giới hạn request/phút hoặc hết hạn ngạch token AI trong ngày.    |
| **`500`** | **`Internal Server Error`**| Lỗi hệ thống nội bộ máy chủ chưa lường trước. | Lỗi crash database, ngoại lệ chưa được xử lý ở backend. |
| **`502`** | **`Bad Gateway`** | Lỗi giao tiếp với dịch vụ bên ngoài. | Không nhận được phản hồi đúng định dạng từ dịch vụ AI (OpenRouter).    |
| **`503`** | **`Service Unavailable`** | Dịch vụ tạm thời chưa sẵn sàng. | Backend chưa cấu hình API key AI, hoặc kho rate-limit (Redis) không khả dụng. |

---

## 3. Bảng Danh Mục Mã Lỗi Nghiệp Vụ Chi Tiết (Business Error Codes Dictionary)

Client (Desktop App PyQt6 & Web Admin) sử dụng trường **`error_code`** để hiển thị thông báo chính xác và điều hướng người dùng phù hợp.

### 3.1. Nhóm Xác thực & Phân quyền (Authentication & Authorization - `AUTH_xxx`)

| Mã HTTP | Mã lỗi (`error_code`) | Thông điệp gợi ý (`message`) | Giải thích kỹ thuật |
| :---: | :--- | :--- | :--- |
| `401` | **`AUTH_INVALID_CREDENTIALS`** | Tên đăng nhập hoặc mật khẩu không chính xác. | Đăng nhập thất bại do sai username hoặc mật khẩu hash không khớp. |
| `401` | **`AUTH_TOKEN_EXPIRED`** | Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại. | JWT đã quá hạn `exp` (bắt ở `JwtAuthGuard` khi `TokenExpiredError`). |
| `401` | **`AUTH_INVALID_TOKEN`** | Token không hợp lệ. | Chữ ký JWT sai, token bị chỉnh sửa hoặc không đọc được. |
| `401` | **`AUTH_INVALID_REFRESH_TOKEN`** | Mã refresh token không hợp lệ hoặc đã hết hạn. | Refresh token sai, đã bị thu hồi (rotation) hoặc quá hạn. |
| `401` | **`AUTH_ACCOUNT_DISABLED`** | Tài khoản không còn hoạt động. | Token hợp lệ nhưng user đã bị xóa mềm/không còn trong CSDL. |
| `403` | **`AUTH_ACCOUNT_DISABLED`** | Tài khoản của bạn đã bị vô hiệu hóa. | Đăng nhập khi `is_active == false`. |
| `403` | **`FORBIDDEN_ADMIN_ONLY`** | Bạn không có quyền thực hiện thao tác này. | `RolesGuard` chặn request thiếu role `ADMIN`. |

---

### 3.2. Nhóm Quản lý Người dùng (User Management - `USER_xxx`)

| Mã HTTP | Mã lỗi (`error_code`) | Thông điệp gợi ý (`message`) | Giải thích kỹ thuật |
| :---: | :--- | :--- | :--- |
| `409` | **`USER_ALREADY_EXISTS`** | Tên đăng nhập hoặc email đã tồn tại. | Trùng khóa duy nhất trong bảng `users` (Prisma `P2002`). |
| `404` | **`USER_NOT_FOUND`** | Không tìm thấy người dùng với ID đã chỉ định. | Truy vấn `id` không tồn tại trong CSDL. |
| `403` | **`USER_CANNOT_DISABLE_SELF`** | Bạn không thể tự vô hiệu hóa tài khoản đang sử dụng. | Admin thao tác vô hiệu hóa chính tài khoản đang đăng nhập. |
| `403` | **`USER_CANNOT_DELETE_SELF`** | Bạn không thể xóa tài khoản đang sử dụng. | Admin thao tác xóa mềm chính tài khoản đang đăng nhập. |
| `409` | **`LAST_ACTIVE_ADMIN`** | Không thể vô hiệu hóa hoặc hạ quyền Admin hoạt động cuối cùng. | Chặn việc hệ thống không còn Admin hoạt động nào. |

> *Lưu ý*: Backend **không có module Quản lý Môn học** — các mã `COURSE_xxx` trong bản đặc tả cũ đã bị loại bỏ.

---

### 3.3. Nhóm Thẩm Định Dữ Liệu & Kiểm Soát Tần Suất (Validation & Rate Limiting)

| Mã HTTP | Mã lỗi (`error_code`) | Thông điệp gợi ý (`message`) | Giải thích kỹ thuật |
| :---: | :--- | :--- | :--- |
| `422` | **`VALIDATION_FAILED`** | Dữ liệu gửi lên không đúng định dạng. | Global Validation Pipe bắt lỗi DTO (`class-validator`), `details` là mảng lỗi chi tiết. |
| `400` | **`INVALID_DATE_RANGE`** | Thời điểm bắt đầu phải nhỏ hơn hoặc bằng thời điểm kết thúc. | Tham số `from`/`to` của báo cáo AI usage sai thứ tự. |
| `429` | **`RATE_LIMIT_EXCEEDED`** | Bạn đã gửi quá nhiều yêu cầu. Vui lòng thử lại sau. | Adaptive ThrottlerGuard vượt giới hạn request/phút (80 chung, 15 cho API AI, 10 login, 30 refresh). |
| `503` | **`RATE_LIMIT_STORAGE_UNAVAILABLE`** | Kho rate limit hiện không khả dụng. | `GET /health` phát hiện Redis/`RATE_LIMIT` storage không kết nối được. |

> *Lưu ý*: Lỗi nạp file CSV/JSON của Desktop App (sai cột, file rỗng, trùng MSSV, JSON hỏng…) là **lỗi phía client**, hiển thị bằng hộp thoại tiếng Việt — **không đi qua backend và không có mã `CSV_xxx` / `TEST_xxx` / `EXEC_xxx`**.

---

### 3.4. Nhóm Trí Tuệ Nhân Tạo (AI Hub & Quota - `AI_xxx`)

| Mã HTTP | Mã lỗi (`error_code`) | Thông điệp gợi ý (`message`) | Giải thích kỹ thuật |
| :---: | :--- | :--- | :--- |
| `429` | **`AI_QUOTA_EXCEEDED`** | Tài khoản của bạn đã sử dụng hết hạn ngạch Token AI trong ngày. | Vượt trần `daily_token_limit` hoặc reservation token thất bại (hết quota trong ngày UTC). |
| `403` | **`AI_QUOTA_NOT_CONFIGURED`** | Tài khoản chưa được cấu hình hạn ngạch AI. | Thiếu bản ghi `AiQuotaConfig` cho user. |
| `400` | **`AI_IMAGE_INVALID`** | Ảnh phải là dữ liệu PNG/JPEG base64 hợp lệ / tối đa 5 MB. | Validate ảnh base64 đầu vào của `evaluate-web-ui`. |
| `429` | **`AI_PROVIDER_RATE_LIMITED`** | Dịch vụ AI đang giới hạn số yêu cầu. Vui lòng thử lại sau. | OpenRouter trả về 429 (đã thử hết key/model dự phòng). |
| `502` | **`AI_INVALID_RESPONSE`** | Dịch vụ AI trả về dữ liệu không đúng định dạng. | Phản hồi không parse được JSON/pyramid kiểm định theo schema. |
| `502` | **`AI_PROVIDER_ERROR`** | Không thể nhận phản hồi từ dịch vụ AI. | Lỗi kết nối/timeout tới OpenRouter. |
| `503` | **`AI_NOT_CONFIGURED`** | Dịch vụ AI chưa được cấu hình trên máy chủ. | Vận hành viên chưa cấu hình `OPENROUTER_API_KEYS` trong môi trường máy chủ. |

---

### 3.5. Nhóm Mã Lỗi Dự Phong (Fallback Error Codes)

Khi exception không kèm `error_code` riêng, `ApiExceptionFilter` gán mã theo HTTP status:

| Mã HTTP | Mã lỗi dự phòng | Áp dụng |
| :---: | :--- | :--- |
| `400` | **`BAD_REQUEST`** | `BadRequestException` không kèm mã lỗi riêng. |
| `401` | **`AUTH_UNAUTHORIZED`** | Lỗi 401 không xác định được nguyên nhân cụ thể. |
| `403` | **`FORBIDDEN`** | Lỗi 403 không xác định được nguyên nhân cụ thể. |
| `404` | **`NOT_FOUND`** | Lỗi 404 không xác định được nguyên nhân cụ thể. |
| `409` | **`CONFLICT`** | Lỗi 409 không xác định được nguyên nhân cụ thể. |
| `502` | **`UPSTREAM_SERVICE_ERROR`** | Lỗi 502 từ dịch vụ ngoài. |
| `500` | **`INTERNAL_SERVER_ERROR`** | Ngoại lệ chưa bắt, lỗi CSDL, crash không lường trước. |

---

### 3.6. Nhóm Thực thi Sandbox & Chấm điểm (Desktop App — không dùng mã lỗi HTTP)

*(Chạy hoàn toàn cục bộ trên Desktop App; kết quả biểu diễn bằng **verdict** và thông báo tiếng Việt, không phát sinh `error_code` từ backend)*

| Biểu diễn | Ý nghĩa |
| :--- | :--- |
| **`AC` / `WA` / `TLE` / `MLE` / `CE` / `RE`** | Verdict chấm điểm (7 cột file `results.csv`). |
| Cảnh báo hộp thoại khi thiếu trình biên dịch (`gcc`, `javac`, `python`) | Mở ngay cửa sổ Cấu hình Môi trường. |
| Lỗi nạp file CSV/JSON/Testcase | Hiển thị message tiếng Việt từ client (VD: “File CSV không đúng định dạng…”, “Không thể đọc file JSON…”). |

## 4. Quy Tắc Ứng Xử Phía Client (Desktop App & Web Admin Guidelines)

1. **Hiển thị thông báo (Notification/Toast)**:
   - Khi `success == true`: Hiển thị thông báo màu xanh lá (Success Toast) với nội dung từ trường `message`.
   - Khi `success == false`: Hiển thị cảnh báo màu đỏ (Error Dialog/Toast) với nội dung từ `message`.
2. **Xử lý mã `401 Unauthorized`**:
   - Desktop App và Web Admin tự động xóa Token đã lưu trong bộ nhớ tạm, hiển thị thông báo "Phiên làm việc đã hết hạn" và tự động điều hướng người dùng về màn hình Đăng nhập (`LoginScreen`).
3. **Xử lý mã `429 Too Many Requests` (AI Quota Exceeded)**:
   - Bắt mã lỗi `AI_QUOTA_EXCEEDED`, hiển thị popup cảnh báo màu vàng: *"Hạn ngạch gọi AI của bạn hôm nay đã hết. Bạn vẫn có thể tiếp tục chấm bài hoặc nhập testcase thủ công bình thường mà không cần AI."*

