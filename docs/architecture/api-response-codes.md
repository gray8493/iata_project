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
  "status_code": 400,
  "error_code": "CSV_INVALID_HEADER",
  "message": "File CSV không đúng định dạng. Yêu cầu chỉ gồm 2 cột: MSSV,File",
  "details": [
    {
      "field": "header",
      "issue": "Thiếu cột 'File' hoặc có cột dư thừa",
      "received": ["MSSV", "StudentName", "FileName"]
    }
  ],
  "timestamp": "2026-09-13T02:30:00Z"
}
```

* **`success`** (`bool`): Luôn luôn là `false`.
* **`status_code`** (`int`): Mã trạng thái HTTP tương ứng (400, 401, 403, 404, 422, 429, 500).
* **`error_code`** (`str`): Mã định danh lỗi nghiệp vụ viết hoa (UPPER_SNAKE_CASE) để phía Client (Desktop App / Web Admin) bắt chính xác mà không phụ thuộc vào chuỗi text `message`.
* **`message`** (`str`): Mô tả lỗi thân thiện, trực quan để hiển thị trực tiếp lên giao diện người dùng.
* **`details`** (`array` | `object` | `null`): Thông tin chi tiết về lỗi (ví dụ: các trường vi phạm validation của DTO, dòng bị sai trong CSV).
* **`timestamp`** (`str`): Mốc thời gian ISO 8601 chuẩn UTC.

---

### 1.3. Cấu trúc phản hồi Danh sách & Phân trang (Pagination Response) - HTTP 200

Áp dụng cho các API lấy danh sách dữ liệu (quản lý user, danh mục môn học, lịch sử chấm):

```json
{
  "success": true,
  "status_code": 200,
  "message": "Lấy danh sách thành công",
  "data": {
    "items": [
      { "id": 1, "code": "PRF", "name": "Lập trình cơ sở", "language": "C" },
      { "id": 2, "code": "PRO", "name": "Lập trình hướng đối tượng", "language": "Java/Python" }
    ],
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total_items": 4,
      "total_pages": 1
    }
  },
  "timestamp": "2026-09-13T02:30:00Z"
}
```

---

## 2. Bảng Phân Loại Mã Trạng Thái HTTP Chuẩn (Standard HTTP Status Codes)

Hệ thống AITA tuân thủ nghiêm ngặt chuẩn **RFC 9110 HTTP Semantics**:

| HTTP Code | Định danh chuẩn | Ý nghĩa trong hệ thống AITA | Khi nào áp dụng? |
| :---: | :--- | :--- | :--- |
| **`200`** | **`OK`** | Yêu cầu xử lý thành công hoàn toàn. | Các request `GET`, `PUT`, `DELETE` hoặc xử lý nghiệp vụ thành công. |
| **`201`** | **`Created`** | Tạo mới tài nguyên thành công. | Khi tạo mới User, thêm Testcase, tạo Đợt chấm bài. |
| **`204`** | **`No Content`** | Thực hiện thành công nhưng không có body trả về. | Xóa thành công hoặc đăng xuất. |
| **`400`** | **`Bad Request`** | Dữ liệu gửi lên sai quy chuẩn nghiệp vụ. | File CSV sai định dạng, dữ liệu đầu vào không hợp lệ. |
| **`401`** | **`Unauthorized`** | Chưa xác thực hoặc Token không hợp lệ/hết hạn. | Thiếu header `Authorization: Bearer <JWT>`, sai mật khẩu. |
| **`403`** | **`Forbidden`** | Đã xác thực nhưng không có quyền truy cập. | Giảng viên cố tình gọi các endpoint quản trị của Admin. |
| **`404`** | **`Not Found`** | Không tìm thấy tài nguyên yêu cầu. | Không tìm thấy User ID, không tìm thấy Môn học. |
| **`409`** | **`Conflict`** | Xung đột dữ liệu trong CSDL. | Tạo tài khoản có `username` đã tồn tại. |
| **`422`** | **`Unprocessable Entity`** | Lỗi thẩm định cấu trúc dữ liệu (DTO Validation). | Thiếu trường bắt buộc, sai kiểu dữ liệu (gửi chuỗi thay vì số). |
| **`429`** | **`Too Many Requests`** | Vượt quá hạn ngạch (Rate Limit / AI Quota). | Giảng viên gọi vượt quá hạn mức token Gemini AI được cấp. |
| **`500`** | **`Internal Server Error`**| Lỗi hệ thống nội bộ máy chủ chưa lường trước. | Lỗi crash database, ngoại lệ chưa được xử lý ở backend. |
| **`502`** | **`Bad Gateway`** | Lỗi giao tiếp với dịch vụ bên ngoài. | Web Server Backend không thể kết nối tới Google Gemini API. |

---

## 3. Bảng Danh Mục Mã Lỗi Nghiệp Vụ Chi Tiết (Business Error Codes Dictionary)

Client (Desktop App PyQt6 & Web Admin) sử dụng trường **`error_code`** để hiển thị thông báo chính xác và điều hướng người dùng phù hợp.

### 3.1. Nhóm Xác thực & Phân quyền (Authentication & Authorization - `AUTH_xxx`)

| Mã HTTP | Mã lỗi (`error_code`) | Thông điệp gợi ý (`message`) | Giải thích kỹ thuật |
| :---: | :--- | :--- | :--- |
| `401` | **`AUTH_INVALID_CREDENTIALS`** | Tên đăng nhập hoặc mật khẩu không chính xác. | Đăng nhập thất bại do sai username hoặc mật khẩu hash không khớp. |
| `401` | **`AUTH_TOKEN_EXPIRED`** | Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại. | JWT Token đã quá thời hạn hiệu lực (hết hạn `exp`). |
| `401` | **`AUTH_TOKEN_INVALID`** | Token xác thực không hợp lệ hoặc đã bị chỉnh sửa. | Chữ ký JWT sai thuật toán hoặc payload bị can thiệp. |
| `401` | **`AUTH_TOKEN_MISSING`** | Vui lòng đăng nhập để thực hiện thao tác này. | Request thiếu header `Authorization: Bearer <token>`. |
| `403` | **`AUTH_FORBIDDEN_ACTION`** | Bạn không có quyền thực hiện thao tác này. | User có role `INSTRUCTOR` cố gọi API của `ADMIN`. |
| `403` | **`AUTH_ACCOUNT_DISABLED`** | Tài khoản của bạn đã bị khóa. Vui lòng liên hệ Admin. | Thuộc tính `is_active == false` trong CSDL. |

---

### 3.2. Nhóm Quản lý Người dùng & Môn học (User & Course Management - `USER_xxx`, `COURSE_xxx`)

| Mã HTTP | Mã lỗi (`error_code`) | Thông điệp gợi ý (`message`) | Giải thích kỹ thuật |
| :---: | :--- | :--- | :--- |
| `409` | **`USER_ALREADY_EXISTS`** | Tên đăng nhập này đã được sử dụng. | Trùng khóa duy nhất `username` trong bảng `users`. |
| `404` | **`USER_NOT_FOUND`** | Không tìm thấy thông tin người dùng yêu cầu. | Truy vấn `id` không tồn tại trong CSDL. |
| `400` | **`USER_CANNOT_DISABLE_SELF`** | Bạn không thể tự khóa tài khoản của chính mình. | Admin thao tác vô hiệu hóa chính tài khoản đang đăng nhập. |
| `404` | **`COURSE_NOT_FOUND`** | Môn học không tồn tại trong hệ thống. | Truy vấn mã môn ngoài danh mục PRF, PRO, DSA, PHP. |
| `400` | **`COURSE_INVALID_LANGUAGE`** | Ngôn ngữ môn học không hợp lệ. | Chỉ hỗ trợ C (cho PRF), Java/Python (cho PRO, DSA), Python (cho PHP). |

---

### 3.3. Nhóm Nạp File CSV & Dữ liệu Sinh viên (CSV Processing - `CSV_xxx`)

| Mã HTTP | Mã lỗi (`error_code`) | Thông điệp gợi ý (`message`) | Giải thích kỹ thuật |
| :---: | :--- | :--- | :--- |
| `400` | **`CSV_EMPTY_FILE`** | File CSV nạp vào không có dữ liệu. | File rỗng dung lượng 0 bytes hoặc chỉ có dòng trắng. |
| `400` | **`CSV_INVALID_COLUMNS`** | File CSV sai cấu trúc. Yêu cầu chỉ gồm 2 cột: `MSSV,File`. | Tiêu đề file khác với quy chuẩn `MSSV,File`. |
| `400` | **`CSV_DUPLICATE_STUDENT`** | Phát hiện mã sinh viên bị lặp lại trong file CSV. | Có từ 2 dòng trở lên trùng cùng một mã số sinh viên. |
| `400` | **`CSV_FILE_NOT_FOUND`** | Không tìm thấy file bài làm tương ứng trong thư mục. | Tên file ở cột 2 không tồn tại trong folder bài nộp của lớp. |
| `400` | **`CSV_ENCODING_ERROR`** | File CSV không đúng bảng mã UTF-8. | File bị lỗi font hoặc lưu bằng bảng mã ANSI/Windows-1258. |

---

### 3.4. Nhóm Bộ Testcase & Chiến lược So khớp (Testcase & Matching - `TEST_xxx`)

| Mã HTTP | Mã lỗi (`error_code`) | Thông điệp gợi ý (`message`) | Giải thích kỹ thuật |
| :---: | :--- | :--- | :--- |
| `400` | **`TEST_EMPTY_INPUT_OUTPUT`** | Testcase bắt buộc phải có Input và Output kỳ vọng. | Trường `input` hoặc `output` bị để trống khi tạo thủ công. |
| `400` | **`TEST_INVALID_JSON_FORMAT`**| File JSON cấu hình testcase không đúng cú pháp. | Lỗi cú pháp phân tích cú pháp JSON khi import `testcases.json`. |
| `400` | **`TEST_INVALID_STRATEGY`** | Chiến lược so khớp không hợp lệ. | Giá trị không nằm trong 7 strategy đã định nghĩa. |
| `400` | **`TEST_WEIGHT_MUST_POSITIVE`**| Điểm số của testcase phải là số dương lớn hơn 0. | Giảng viên nhập điểm âm hoặc bằng 0 cho testcase. |

---

### 3.5. Nhóm Trí Tuệ Nhân Tạo Google Gemini (AI Hub & Quota - `AI_xxx`)

| Mã HTTP | Mã lỗi (`error_code`) | Thông điệp gợi ý (`message`) | Giải thích kỹ thuật |
| :---: | :--- | :--- | :--- |
| `429` | **`AI_QUOTA_EXCEEDED`** | Hạn mức gọi AI trong ngày của bạn đã hết. | Vượt quá số lượng Token/Request được cấp phát bởi Admin. |
| `400` | **`AI_INVALID_PROMPT`** | Đề bài nhập vào quá ngắn hoặc không rõ ràng. | Nội dung đề bài dưới 10 ký tự, không đủ ngữ cảnh để sinh test. |
| `502` | **`AI_SERVICE_UNAVAILABLE`** | Dịch vụ Google Gemini API hiện đang bận hoặc gián đoạn. | Máy chủ Gemini API trả về lỗi 503 hoặc Timeout quá 30 giây. |
| `500` | **`AI_NOT_CONFIGURED`** | Máy chủ chưa được cấu hình Gemini API key. | Vận hành viên cấu hình `GEMINI_API_KEY` trong môi trường máy chủ rồi khởi động lại dịch vụ. |
| `400` | **`AI_PARSE_OUTPUT_FAILED`** | AI phản hồi định dạng không hợp lệ, không thể bóc tách testcase. | Gemini trả về markdown lỗi không thể convert sang JSON. |

---

### 3.6. Nhóm Thực thi Sandbox & Chấm điểm (Execution & Sandbox - `EXEC_xxx`)

*(Chủ yếu trả về nội bộ trên Desktop App Runner hoặc xuất báo cáo cục bộ)*

| Mã HTTP | Mã lỗi (`error_code`) | Thông điệp gợi ý (`message`) | Giải thích kỹ thuật |
| :---: | :--- | :--- | :--- |
| `400` | **`EXEC_COMPILER_NOT_FOUND`** | Không tìm thấy trình biên dịch trên máy trạm. | Hệ điều hành không nhận diện được lệnh `gcc`, `javac` hoặc `python`. |
| `400` | **`EXEC_MAIN_NOT_FOUND`** | File bài nộp không chứa hàm main() hợp lệ. | Bài làm không thể khởi chạy vì thiếu điểm khởi nhập `main()`. |
| `408` | **`EXEC_TIMEOUT_EXCEEDED`** | Thời gian thực thi vượt quá giới hạn quy định (`TLE`). | Bài nộp chạy quá số milli-giây cho phép (`Time Limit`). |
| `413` | **`EXEC_MEMORY_LIMIT_EXCEEDED`**| Bộ nhớ tiêu thụ vượt quá mức cho phép (`MLE`). | Bài nộp vượt quá số MB RAM cho phép (`Memory Limit`). |

## 4. Quy Tắc Ứng Xử Phía Client (Desktop App & Web Admin Guidelines)

1. **Hiển thị thông báo (Notification/Toast)**:
   - Khi `success == true`: Hiển thị thông báo màu xanh lá (Success Toast) với nội dung từ trường `message`.
   - Khi `success == false`: Hiển thị cảnh báo màu đỏ (Error Dialog/Toast) với nội dung từ `message`.
2. **Xử lý mã `401 Unauthorized`**:
   - Desktop App và Web Admin tự động xóa Token đã lưu trong bộ nhớ tạm, hiển thị thông báo "Phiên làm việc đã hết hạn" và tự động điều hướng người dùng về màn hình Đăng nhập (`LoginScreen`).
3. **Xử lý mã `429 Too Many Requests` (AI Quota Exceeded)**:
   - Bắt mã lỗi `AI_QUOTA_EXCEEDED`, hiển thị popup cảnh báo màu vàng: *"Hạn ngạch gọi AI của bạn hôm nay đã hết. Bạn vẫn có thể tiếp tục chấm bài hoặc nhập testcase thủ công bình thường mà không cần AI."*

