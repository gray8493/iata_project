# Thông Tin Chung Kiểm Thử Unit Test

- **Phân hệ kiểm thử**: Phân hệ AI Gateway & Quản lý Hạn ngạch (AI Hub API)
- **Danh sách API kiểm thử**:
  - `GET /api/v1/ai/quota` (UC-04: Kiểm tra hạn ngạch Token hôm nay & thời điểm reset)
  - `POST /api/v1/ai/generate-testcases` (UC-10: Tự động sinh testcase biên bằng Gemini 1.5 Flash)
  - `POST /api/v1/ai/review-code` (UC-16: Phân tích lỗi và sinh nhận xét sư phạm On-Demand cho bài WA)
  - `POST /api/v1/ai/verify-plagiarism` (UC-17: Xác thực ngữ nghĩa nghi vấn đạo văn > 80% Vòng 2)
  - `POST /api/v1/ai/evaluate-web-ui` (UC-19: Đánh giá giao diện Web qua ảnh chụp màn hình Multimodal)
- **Người thực hiện (Tester/Dev)**: Kim Chi Ha
- **Ngày tạo**: 04/10/2026
- **Cập nhật lần cuối**: 04/10/2026 - 09:35
- **Tài liệu liên quan**:
  - [Đặc tả API Phân hệ AI (Markdown)](file:///c:/AITA/iata_project/docs/apis/ai/ai-api.md)
  - [Đặc tả OpenAPI Phân hệ AI (YAML)](file:///c:/AITA/iata_project/docs/apis/ai/ai.yaml)
  - [Đặc tả API Toàn hệ thống AITA](file:///c:/AITA/iata_project/docs/apis/api-specification.md)
  - [Quy tắc kiểm thử Testcase](file:///c:/AITA/iata_project/rules/testcase-rules.md)
- **Tổng số Testcase**: 65 Testcases (Trạng thái: Chưa thực thi - Sẵn sàng kiểm thử; Trường hợp False/Lỗi viết trước, True/Thành công viết sau; Đầy đủ Test Data cụ thể cho từng Testcase)
  - `GET /api/v1/ai/quota`: 07 Testcases (05 False, 02 True)
  - `POST /api/v1/ai/generate-testcases`: 16 Testcases (11 False, 05 True)
  - `POST /api/v1/ai/review-code`: 15 Testcases (11 False, 04 True)
  - `POST /api/v1/ai/verify-plagiarism`: 14 Testcases (10 False, 04 True)
  - `POST /api/v1/ai/evaluate-web-ui`: 13 Testcases (09 False, 04 True)

---

# ==============================================================================

# PHẦN 1: API GET /api/v1/ai/quota (UC-04: KIỂM TRA HẠN NGẠCH TOKEN HÔM NAY)

# ==============================================================================

# UT03_AiQuota_TC001: Không gửi Header Authorization trong yêu cầu lấy hạn ngạch

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server AI Gateway đang hoạt động bình thường.
- Client gửi request không đính kèm Token trong Header.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/ai/quota`
- **Body Input**: Không có (None).

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/ai/quota`.
2. Không truyền Token xác thực (bỏ trống Header `Authorization`).
3. Đính kèm Request Body dữ liệu.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `401 Unauthorized`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 401,
    "error_code": "AUTH_TOKEN_MISSING",
    "message": "Yêu cầu xác thực tài khoản. Vui lòng cung cấp Access Token.",
    "details": null,
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiQuota_TC002: Header Authorization chứa Bearer Token không hợp lệ hoặc sai chữ ký

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server AI Gateway đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/ai/quota`
- **Body Input**: Không có.

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/ai/quota`.
2. Truyền token của tài khoản có vai trò không hợp lệ vào Header `Authorization: Bearer <INVALID_ROLE_TOKEN>`.
3. Đính kèm Request Body dữ liệu.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `401 Unauthorized`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 401,
    "error_code": "AUTH_TOKEN_INVALID",
    "message": "Mã truy cập không hợp lệ hoặc chữ ký sai.",
    "details": null,
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiQuota_TC003: Bearer Token gửi lên đã hết hạn (Expired Token)

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server AI Gateway đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/ai/quota`
- **Body Input**: Không có.

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/ai/quota`.
2. Truyền token của Giảng viên đã cạn hạn ngạch ngày vào Header `Authorization: Bearer <EXHAUSTED_QUOTA_TOKEN>`.
3. Đính kèm Request Body dữ liệu.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `401 Unauthorized`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 401,
    "error_code": "AUTH_TOKEN_EXPIRED",
    "message": "Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại.",
    "details": null,
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiQuota_TC004: Tài khoản người dùng trong Bearer Token đã bị vô hiệu hóa

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Tài khoản Giảng viên `id = 99` sở hữu Token đã bị chuyển cờ `is_active = false`.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/ai/quota`
- **Body Input**: Không có.

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/ai/quota`.
2. Đính kèm Header `Authorization: Bearer <DISABLED_USER_TOKEN>`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `403 Forbidden`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 403,
    "error_code": "AUTH_ACCOUNT_DISABLED",
    "message": "Tài khoản của bạn đã bị vô hiệu hóa. Vui lòng liên hệ Quản trị viên.",
    "details": null,
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiQuota_TC005: Lỗi máy chủ cơ sở dữ liệu nội bộ khi truy vấn hạn ngạch

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Dịch vụ cơ sở dữ liệu quản lý quota bị ngắt kết nối giả lập (Mock DB connection error).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/ai/quota`
- **Body Input**: Không có (None).
- **Mock State**: `DatabaseConnectionPool.status = 'DISCONNECTED'`.

#### Các bước thực hiện (Test Steps)

1. Kích hoạt trạng thái lỗi ngắt kết nối database trên mock server.
2. Gửi Request `GET /api/v1/ai/quota` với `VALID_INSTRUCTOR_TOKEN`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `500 Internal Server Error`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 500,
    "error_code": "INTERNAL_SERVER_ERROR",
    "message": "Đã xảy ra lỗi máy chủ nội bộ. Vui lòng thử lại sau.",
    "details": null,
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiQuota_TC006: Lấy thông tin hạn ngạch thành công khi tài khoản còn hạn ngạch

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Giảng viên `teacher_hung` còn hạn ngạch: `daily_limit_tokens = 50000`, `used_tokens_today = 12450`.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/ai/quota`
- **Body Input**: Không có.

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/ai/quota`.
2. Đính kèm Header `Authorization: Bearer <VALID_INSTRUCTOR_TOKEN>`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Phản hồi JSON:
  ```json
  {
    "success": true,
    "status_code": 200,
    "message": "Lấy thông tin hạn ngạch AI thành công",
    "data": {
      "daily_limit_tokens": 50000,
      "used_tokens_today": 12450,
      "remaining_tokens": 37550,
      "percentage_used": 24.9,
      "reset_at_utc": "2026-10-05T00:00:00.000Z"
    },
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiQuota_TC007: Lấy thông tin hạn ngạch thành công khi tài khoản đã dùng hết hạn ngạch (Biên 0 còn lại)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Giảng viên `teacher_quang` đã dùng hết toàn bộ hạn ngạch trong ngày (`used_tokens_today = 50000`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/ai/quota`
- **Body Input**: Không có.

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/ai/quota`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Phản hồi JSON:
  ```json
  {
    "success": true,
    "status_code": 200,
    "message": "Lấy thông tin hạn ngạch AI thành công",
    "data": {
      "daily_limit_tokens": 50000,
      "used_tokens_today": 50000,
      "remaining_tokens": 0,
      "percentage_used": 100.0,
      "reset_at_utc": "2026-10-05T00:00:00.000Z"
    },
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# ==============================================================================

# PHẦN 2: API POST /api/v1/ai/generate-testcases (UC-10: SINH TESTCASE BIÊN TỰ ĐỘNG)

# ==============================================================================

# UT03_AiGenerateTestcases_TC001: Không gửi Header Authorization trong yêu cầu sinh testcase

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server AI Gateway đang hoạt động bình thường.
- Request không truyền header Authorization.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/generate-testcases`
- **Body Input**:
  ```json
  {
    "problem_description": "Nhập vào số nguyên dương N (1 <= N <= 10^6). Tính tổng các ước số nguyên của N.",
    "language": "C",
    "count": 3
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/generate-testcases`.
2. Không truyền Token xác thực (bỏ trống Header `Authorization`).
3. Đính kèm Request Body dữ liệu.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `401 Unauthorized`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 401,
    "error_code": "AUTH_TOKEN_MISSING",
    "message": "Yêu cầu xác thực tài khoản. Vui lòng cung cấp Access Token.",
    "details": null,
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC002: Quản trị viên (ADMIN) không có quyền gọi API sinh testcase của Giảng viên

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Người dùng đã đăng nhập với vai trò Quản trị viên `role = "ADMIN"`.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/generate-testcases`
- **Body Input**:
  ```json
  {
    "problem_description": "Nhập vào số nguyên N. Đếm số lượng ước số của N.",
    "language": "C",
    "count": 3
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/generate-testcases`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. Đính kèm Request Body dữ liệu.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `403 Forbidden`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 403,
    "error_code": "AUTH_PERMISSION_DENIED",
    "message": "Chỉ Giảng viên mới có quyền sử dụng tính năng sinh testcase AI.",
    "details": null,
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC003: Tài khoản Giảng viên đã sử dụng hết hạn ngạch Token AI trong ngày

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Giảng viên `teacher_quang` đã dùng hết hạn ngạch 50,000/50,000 tokens trong ngày.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/generate-testcases`
- **Body Input**:
  ```json
  {
    "problem_description": "Nhập vào số nguyên dương N. Liệt kê tất cả các ước số lẻ của N.",
    "language": "PYTHON",
    "count": 3
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/generate-testcases`.
2. Truyền token của Giảng viên đã cạn hạn ngạch ngày vào Header `Authorization: Bearer <EXHAUSTED_QUOTA_TOKEN>`.
3. Đính kèm Request Body dữ liệu.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `429 Too Many Requests`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 429,
    "error_code": "AI_QUOTA_EXCEEDED",
    "message": "Tài khoản của bạn đã sử dụng hết hạn ngạch Token AI trong ngày (50,000/50,000 tokens). Vui lòng liên hệ Quản trị viên để cấp thêm quota hoặc đợi sang ngày hôm sau.",
    "details": {
      "daily_limit": 50000,
      "current_usage": 50000,
      "reset_at": "2026-10-05T00:00:00.000Z"
    },
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC004: Thiếu trường bắt buộc problem_description trong Body

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Giảng viên có Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/generate-testcases`
- **Body Input**:
  ```json
  {
    "language": "C",
    "count": 3
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/generate-testcases`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/generate-testcases` với request body thiếu trường `problem_description`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "problem_description",
        "issue": "Mô tả bài toán (problem_description) là trường bắt buộc."
      }
    ],
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC005: problem_description có độ dài dưới 20 ký tự (Vi phạm biên minLength)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Giảng viên có Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/generate-testcases`
- **Body Input**:

  ```json
  {
    "problem_description": "Tinh uoc so cua N.",
    "language": "C",
    "count": 3
  }
  ```

  *(Chuỗi `"Tinh uoc so cua N."` có đúng 19 ký tự, vi phạm quy định minLength: 20)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/generate-testcases`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/generate-testcases` với request body chứa 19 ký tự.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "problem_description",
        "issue": "Mô tả bài toán phải có độ dài tối thiểu 20 ký tự."
      }
    ],
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC006: problem_description có độ dài vượt quá 5000 ký tự (Vi phạm biên maxLength)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Giảng viên có Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/generate-testcases`
- **Body Input**:

  ```json
  {
    "problem_description": "A...[chuỗi ký tự A lặp lại đúng 5001 lần]...A",
    "language": "C",
    "count": 3
  }
  ```

  *(Tổng độ dài chuỗi là 5001 ký tự, vượt quá ngưỡng 5000 ký tự)*

#### Các bước thực hiện (Test Steps)

1. Tạo chuỗi ký tự độ dài 5001 ký tự.
2. Khởi tạo HTTP Request `POST /api/v1/ai/generate-testcases`.
3. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "problem_description",
        "issue": "Mô tả bài toán không được vượt quá 5000 ký tự."
      }
    ],
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC007: Thiếu trường bắt buộc language trong Body

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Giảng viên có Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/generate-testcases`
- **Body Input**:
  ```json
  {
    "problem_description": "Nhập vào số nguyên dương N. Tính tổng các ước số nguyên tố của N.",
    "count": 3
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/generate-testcases`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/generate-testcases` với request body không có trường `language`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "language",
        "issue": "Ngôn ngữ lập trình (language) là trường bắt buộc."
      }
    ],
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC008: Ngôn ngữ lập trình không hợp lệ (Không thuộc Enum [C, JAVA, PYTHON])

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Giảng viên có Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/generate-testcases`
- **Body Input**:
  ```json
  {
    "problem_description": "Nhập vào số nguyên N. In ra số Fibonacci thứ N trong dãy.",
    "language": "RUBY",
    "count": 3
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/generate-testcases`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/generate-testcases` với `language = "ruby"`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "language",
        "issue": "Ngôn ngữ không được hỗ trợ. Giá trị hợp lệ: C, JAVA, PYTHON."
      }
    ],
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC009: Số lượng testcase count nhỏ hơn 1 hoặc lớn hơn 10 (Vi phạm khoảng min 1 max 10)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Giảng viên có Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Body Input A (Dưới biên min: `count = 0`)**:
  ```json
  {
    "problem_description": "Nhập vào số nguyên N. Kiểm tra tính chẵn lẻ của N.",
    "language": "C",
    "count": 0
  }
  ```
- **Body Input B (Trên biên max: `count = 11`)**:
  ```json
  {
    "problem_description": "Nhập vào số nguyên N. Kiểm tra tính chẵn lẻ của N.",
    "language": "C",
    "count": 11
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request ``.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/generate-testcases` lần lượt với payload a và payload b.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- Cả 2 request đều nhận HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "count",
        "issue": "Số lượng testcase sinh tự động phải nằm trong khoảng từ 1 đến 10."
      }
    ],
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC010: Dịch vụ Google Gemini AI bị gián đoạn kết nối hoặc quá tải (503 Service Unavailable)

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Google Gemini API phía ngoài trả mã lỗi 503 hoặc timeout kết nối mạng quá 30 giây.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/generate-testcases`
- **Body Input**:
  ```json
  {
    "problem_description": "Nhập mảng số nguyên A gồm N phần tử. Tìm giá trị lớn nhất trong mảng.",
    "language": "C",
    "count": 3
  }
  ```
- **Mock State**: `GeminiService.generateContent() -> throws TimeoutException(30000ms)`.

#### Các bước thực hiện (Test Steps)

1. Cấu hình mock Gemini Service ném lỗi gián đoạn dịch vụ / timeout 30s.
2. Khởi tạo HTTP Request `POST /api/v1/ai/generate-testcases`.
3. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `503 Service Unavailable`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 503,
    "error_code": "AI_SERVICE_UNAVAILABLE",
    "message": "Dịch vụ Gemini AI hiện không khả dụng hoặc phản hồi quá lâu. Vui lòng thử lại sau.",
    "details": null,
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC011: Phản hồi từ mô hình Gemini AI bị lỗi cấu trúc JSON (Parsing Failed)

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Google Gemini API trả chuỗi Markdown tự do không parse được thành JSON mảng testcases.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/generate-testcases`
- **Body Input**:
  ```json
  {
    "problem_description": "Giải phương trình bậc hai ax^2 + bx + c = 0.",
    "language": "JAVA",
    "count": 3
  }
  ```
- **Mock Gemini Output**: `"Xin lỗi, tôi không thể tạo JSON theo định dạng yêu cầu được."`

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/generate-testcases`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. Thiết lập mock Gemini trả về chuỗi text thuần túy không chứa cấu trúc JSON.
4. Gửi Request `POST /api/v1/ai/generate-testcases`.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `500 Internal Server Error`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 500,
    "error_code": "AI_RESPONSE_PARSING_FAILED",
    "message": "Mô hình AI trả về dữ liệu sai định dạng cấu trúc testcase.",
    "details": null,
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC012: Sinh testcase thành công với tham số mặc định (count = 3, include_boundary = true)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Giảng viên sở hữu Token hợp lệ và còn quota.
- Dịch vụ Gemini AI hoạt động ổn định.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/generate-testcases`
- **Body Input**:
  ```json
  {
    "problem_description": "Viết chương trình nhập vào số nguyên dương N (1 <= N <= 10^6). Tính tổng các ước số của N.",
    "language": "C"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/generate-testcases`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/generate-testcases` với request body ở trên.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Phản hồi JSON:
  ```json
  {
    "success": true,
    "status_code": 200,
    "message": "Sinh testcase tự động bằng AI thành công",
    "data": {
      "tokens_consumed": 420,
      "testcases": [
        {
          "input": "1",
          "expected_output": "1",
          "explanation": "Biên dưới nhỏ nhất N = 1",
          "is_boundary": true
        },
        {
          "input": "1000000",
          "expected_output": "2480437",
          "explanation": "Biên trên tối đa N = 10^6",
          "is_boundary": true
        },
        {
          "input": "999983",
          "expected_output": "999984",
          "explanation": "Số nguyên tố lớn chỉ có 2 ước",
          "is_boundary": true
        }
      ]
    },
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC013: Sinh testcase thành công với số lượng biên dưới count = 1

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Giảng viên sở hữu Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/generate-testcases`
- **Body Input**:
  ```json
  {
    "problem_description": "Kiểm tra xem số nguyên dương N có phải là số chính phương hay không.",
    "language": "C",
    "count": 1,
    "include_boundary": true
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/generate-testcases`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/generate-testcases` với `count = 1`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- `data.testcases`: Mảng có chính xác 1 phần tử testcase biên.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC014: Sinh testcase thành công với số lượng biên trên count = 10

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Giảng viên sở hữu Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/generate-testcases`
- **Body Input**:
  ```json
  {
    "problem_description": "Nhập ma trận vuông cấp N. Tính định thức của ma trận vuông các số thực.",
    "language": "JAVA",
    "count": 10,
    "include_boundary": true
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/generate-testcases`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/generate-testcases` với `count = 10`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- `data.testcases`: Mảng gồm đúng 10 phần tử testcases.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC015: Sinh testcase thành công với problem_description có độ dài đúng biên dưới (20 ký tự)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Giảng viên sở hữu Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/generate-testcases`
- **Body Input**:

  ```json
  {
    "problem_description": "Tim uoc so nguyen N!",
    "language": "JAVA",
    "count": 2
  }
  ```

  *(Chuỗi `"Tim uoc so nguyen N!"` có chính xác 20 ký tự)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/generate-testcases`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/generate-testcases` với request body chứa đúng 20 ký tự.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Hệ thống chấp nhận chuỗi 20 ký tự và trả về `data.testcases` có 2 phần tử.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiGenerateTestcases_TC016: Sinh testcase thành công cho ngôn ngữ PYTHON với include_boundary = false

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Giảng viên sở hữu Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/generate-testcases`
- **Body Input**:
  ```json
  {
    "problem_description": "Đọc file văn bản và đếm tần số xuất hiện của từng từ tiếng Anh.",
    "language": "PYTHON",
    "count": 3,
    "include_boundary": false
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/generate-testcases`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/generate-testcases` với `include_boundary = false`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- `data.testcases`: Chứa 3 testcase bình thường, các giá trị `is_boundary` đều là `false`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |


---

# ==============================================================================

# PHẦN 3: API POST /api/v1/ai/review-code (UC-16: PHÂN TÍCH LỖI VÀ NHẬN XÉT SƯ PHẠM)

# ==============================================================================

# UT03_AiReviewCode_TC001: Không gửi Header Authorization trong yêu cầu review code

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Request không truyền Token xác thực.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/review-code`
- **Body Input**:
  ```json
  {
    "source_code": "#include <stdio.h>\nint main(){ int a; scanf(\"%d\", &a); printf(\"%d\", a*2); return 0; }",
    "language": "C",
    "problem_statement": "Nhập số a, in ra gấp đôi số a.",
    "failed_testcase": {
      "input": "5",
      "expected_output": "10",
      "actual_output": "5"
    }
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/review-code`.
2. Không truyền Token xác thực (bỏ trống Header `Authorization`).
3. Đính kèm Request Body dữ liệu.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `401 Unauthorized`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 401,
    "error_code": "AUTH_TOKEN_MISSING",
    "message": "Yêu cầu xác thực tài khoản. Vui lòng cung cấp Access Token.",
    "details": null,
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiReviewCode_TC002: Quản trị viên (ADMIN) không có quyền gọi API review code của Giảng viên

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Người dùng đã đăng nhập với vai trò Quản trị viên `role = "ADMIN"`.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/review-code`
- **Body Input**:
  ```json
  {
    "source_code": "#include <stdio.h>\nint main(){ printf(\"Hello\"); return 0; }",
    "language": "C",
    "problem_statement": "In ra Hello",
    "failed_testcase": {
      "input": "",
      "expected_output": "Hello",
      "actual_output": "Hi"
    }
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/review-code`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. Đính kèm Request Body dữ liệu.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `403 Forbidden`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 403,
    "error_code": "AUTH_PERMISSION_DENIED",
    "message": "Chỉ Giảng viên mới có quyền sử dụng tính năng nhận xét sư phạm On-Demand.",
    "details": null,
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiReviewCode_TC003: Giảng viên đã dùng hết hạn ngạch Token AI trong ngày

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Giảng viên `teacher_quang` đã dùng hết quota 50,000/50,000 tokens.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/review-code`
- **Body Input**:
  ```json
  {
    "source_code": "#include <stdio.h>\nint main(){ int a; scanf(\"%d\", &a); printf(\"%d\", a); return 0; }",
    "language": "C",
    "problem_statement": "In ra so a",
    "failed_testcase": {
      "input": "1",
      "expected_output": "1",
      "actual_output": "0"
    }
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/review-code`.
2. Truyền token của Giảng viên đã cạn hạn ngạch ngày vào Header `Authorization: Bearer <EXHAUSTED_QUOTA_TOKEN>`.
3. Đính kèm Request Body dữ liệu.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `429 Too Many Requests`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 429,
    "error_code": "AI_QUOTA_EXCEEDED",
    "message": "Tài khoản của bạn đã sử dụng hết hạn ngạch Token AI trong ngày.",
    "details": {
      "daily_limit": 50000,
      "current_usage": 50000
    },
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiReviewCode_TC004: Thiếu trường bắt buộc source_code trong Body

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Giảng viên có Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/review-code`
- **Body Input**:
  ```json
  {
    "language": "C",
    "problem_statement": "Tính tổng ước số của N.",
    "failed_testcase": {
      "input": "6",
      "expected_output": "12",
      "actual_output": "6"
    }
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/review-code`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/review-code` với body thiếu `source_code`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "source_code",
        "issue": "Mã nguồn bài làm (source_code) là trường bắt buộc."
      }
    ],
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiReviewCode_TC005: source_code có độ dài nhỏ hơn 10 ký tự (Vi phạm biên minLength)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Giảng viên có Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/review-code`
- **Body Input**:

  ```json
  {
    "source_code": "int a=1;",
    "language": "C",
    "problem_statement": "Tính tổng các ước số",
    "failed_testcase": {
      "input": "1",
      "expected_output": "1",
      "actual_output": "0"
    }
  }
  ```

  *(Chuỗi `"int a=1;"` chỉ có 8 ký tự, vi phạm minLength: 10)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/review-code`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/review-code` với `source_code` dưới 10 ký tự.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "source_code",
        "issue": "Mã nguồn phải có độ dài tối thiểu 10 ký tự."
      }
    ],
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiReviewCode_TC006: source_code vượt quá độ dài tối đa 10000 ký tự (Vi phạm biên maxLength)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Giảng viên có Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/review-code`
- **Body Input**:
  ```json
  {
    "source_code": "int main(){ /* ...chuỗi comment dài 10001 ký tự... */ return 0; }",
    "language": "C",
    "problem_statement": "Bài toán lớn",
    "failed_testcase": {
      "input": "0",
      "expected_output": "0",
      "actual_output": "1"
    }
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Tạo chuỗi mã nguồn có độ dài 10001 ký tự.
2. Khởi tạo HTTP Request `POST /api/v1/ai/review-code`.
3. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "source_code",
        "issue": "Mã nguồn không được vượt quá 10000 ký tự."
      }
    ],
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiReviewCode_TC007: Thiếu trường bắt buộc problem_statement trong Body

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Giảng viên có Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/review-code`
- **Body Input**:
  ```json
  {
    "source_code": "#include <stdio.h>\nint main(){ return 0; }",
    "language": "C",
    "failed_testcase": {
      "input": "1",
      "expected_output": "1",
      "actual_output": "0"
    }
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/review-code`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/review-code` thiếu trường `problem_statement`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "problem_statement",
        "issue": "Đề bài (problem_statement) là trường bắt buộc."
      }
    ],
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiReviewCode_TC008: problem_statement vượt quá độ dài tối đa 3000 ký tự

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Giảng viên có Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/review-code`
- **Body Input**:
  ```json
  {
    "source_code": "#include <stdio.h>\nint main(){ return 0; }",
    "language": "C",
    "problem_statement": "Mô tả đề bài...[chuỗi văn bản lặp lại gồm 3005 ký tự]...",
    "failed_testcase": {
      "input": "1",
      "expected_output": "1",
      "actual_output": "0"
    }
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/review-code`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/review-code` với `problem_statement` gồm 3005 ký tự.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "problem_statement",
        "issue": "Đề bài không được vượt quá 3000 ký tự."
      }
    ],
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiReviewCode_TC009: Thiếu Object failed_testcase trong Body

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Giảng viên có Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/review-code`
- **Body Input**:
  ```json
  {
    "source_code": "#include <stdio.h>\nint main(){ return 0; }",
    "language": "C",
    "problem_statement": "Tính tổng các ước số của N"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/review-code`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/review-code` không truyền object `failed_testcase`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "failed_testcase",
        "issue": "Thông tin testcase bị sai (failed_testcase) là trường bắt buộc."
      }
    ],
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiReviewCode_TC010: Object failed_testcase thiếu một trong các trường con bắt buộc (expected_output)

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Giảng viên có Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/review-code`
- **Body Input**:
  ```json
  {
    "source_code": "#include <stdio.h>\nint main(){ return 0; }",
    "language": "C",
    "problem_statement": "Tính tổng các ước số",
    "failed_testcase": {
      "input": "6",
      "actual_output": "6"
    }
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/review-code`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/review-code` với `failed_testcase` thiếu `expected_output`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "failed_testcase.expected_output",
        "issue": "Kết quả kỳ vọng của testcase (expected_output) là trường bắt buộc."
      }
    ],
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiReviewCode_TC011: Dịch vụ Gemini AI gặp sự cố kết nối hoặc model quá tải (503 Service Unavailable)

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Google Gemini API trả mã lỗi 503 hoặc timeout kết nối mạng quá 30 giây.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/review-code`
- **Body Input**:
  ```json
  {
    "source_code": "#include <stdio.h>\nint main(){ int a; scanf(\"%d\", &a); printf(\"%d\", a); return 0; }",
    "language": "C",
    "problem_statement": "In ra số a",
    "failed_testcase": {
      "input": "5",
      "expected_output": "5",
      "actual_output": "0"
    }
  }
  ```
- **Mock State**: `GeminiService.reviewCode() -> throws TimeoutException(30000ms)`.

#### Các bước thực hiện (Test Steps)

1. Giả lập lỗi timeout mạng hoặc mã lỗi 503 từ máy chủ Google Gemini.
2. Khởi tạo HTTP Request `POST /api/v1/ai/review-code`.
3. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `503 Service Unavailable`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 503,
    "error_code": "AI_SERVICE_UNAVAILABLE",
    "message": "Dịch vụ Gemini AI hiện không khả dụng hoặc phản hồi quá lâu. Vui lòng thử lại sau.",
    "details": null,
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiReviewCode_TC012: Phân tích lỗi mã nguồn C thành công (Lỗi Off-by-one trong vòng for)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Giảng viên sở hữu Token hợp lệ và còn hạn ngạch Token.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/review-code`
- **Body Input**:
  ```json
  {
    "source_code": "#include <stdio.h>\nint main() {\n  int n; scanf(\"%d\", &n);\n  int sum = 0;\n  for(int i=1; i<n; i++) if(n%i==0) sum+=i;\n  printf(\"%d\", sum);\n  return 0;\n}",
    "language": "C",
    "problem_statement": "Tính tổng tất cả các ước số của số nguyên dương N (bao gồm cả N).",
    "failed_testcase": {
      "input": "6",
      "expected_output": "12",
      "actual_output": "6"
    }
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/review-code`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/review-code` với payload ở trên.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Phản hồi JSON:
  ```json
  {
    "success": true,
    "status_code": 200,
    "message": "Phân tích mã nguồn bằng AI thành công",
    "data": {
      "tokens_consumed": 380,
      "suspected_error_line": 5,
      "issue_summary": "Thiếu ước số chính là N do điều kiện dừng vòng lặp là i < n thay vì i <= n.",
      "pedagogical_feedback": "Em đã xử lý đúng thuật toán duyệt ước, tuy nhiên đề bài yêu cầu tính cả chính số N. Em hãy kiểm tra lại điều kiện vòng for(i=1; i<=n; i++) nhé.",
      "bug_category": "OFF_BY_ONE_ERROR"
    },
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiReviewCode_TC013: Phân tích lỗi mã nguồn Java thành công (Lỗi logic điều kiện rẽ nhánh)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Giảng viên sở hữu Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/review-code`
- **Body Input**:
  ```json
  {
    "source_code": "import java.util.Scanner;\npublic class Main {\n  public static void main(String[] args){\n    Scanner sc = new Scanner(System.in);\n    int a = sc.nextInt();\n    if (a % 4 == 0) System.out.println(\"YES\");\n    else System.out.println(\"NO\");\n  }\n}",
    "language": "JAVA",
    "problem_statement": "Kiểm tra năm nhuận dương lịch (chia hết cho 400 hoặc chia hết cho 4 nhưng không chia hết cho 100).",
    "failed_testcase": {
      "input": "1900",
      "expected_output": "NO",
      "actual_output": "YES"
    }
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/review-code`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/review-code` với payload java ở trên.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Phản hồi JSON:
  - `success`: `true`
  - `status_code`: `200`
  - `data.bug_category`: `"LOGIC_CONDITION_ERROR"`
  - `data.suspected_error_line`: 6
  - `data.pedagogical_feedback`: Nhắc nhở sinh viên bổ sung điều kiện loại trừ năm tròn thế kỷ không chia hết cho 400 (`a % 100 != 0 || a % 400 == 0`).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiReviewCode_TC014: Phân tích mã nguồn Python với source_code có độ dài đúng biên dưới (10 ký tự)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Giảng viên sở hữu Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/review-code`
- **Body Input**:

  ```json
  {
    "source_code": "print(1/0)",
    "language": "PYTHON",
    "problem_statement": "In ra kết quả phép chia",
    "failed_testcase": {
      "input": "",
      "expected_output": "0",
      "actual_output": "ZeroDivisionError"
    }
  }
  ```

  *(Chuỗi `"print(1/0)"` có đúng 10 ký tự)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/review-code`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/review-code` với mã nguồn python 10 ký tự.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- `data.bug_category`: `"DIVISION_BY_ZERO"`
- `data.pedagogical_feedback`: Chỉ ra lỗi chia cho số 0 trong Python.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiReviewCode_TC015: Phân tích mã nguồn với failed_testcase chứa chuỗi rỗng biên (actual_output = "")

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Giảng viên sở hữu Token hợp lệ và còn quota.
- Bài làm của sinh viên không in ra bất kỳ ký tự nào ra màn hình (`actual_output = ""`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/review-code`
- **Body Input**:
  ```json
  {
    "source_code": "#include <stdio.h>\nint main(){ int a; scanf(\"%d\", &a); return 0; }",
    "language": "C",
    "problem_statement": "Nhập số a và in ra bình phương của a.",
    "failed_testcase": {
      "input": "5",
      "expected_output": "25",
      "actual_output": ""
    }
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/review-code`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/review-code` với `actual_output = ""`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- `data.issue_summary`: Chỉ rõ bài làm thiếu thao tác in kết quả `printf`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# ==============================================================================

# PHẦN 4: API POST /api/v1/ai/verify-plagiarism (UC-17: XÁC THỰC ĐẠO VĂN VÒNG 2)

# ==============================================================================

# UT03_AiVerifyPlagiarism_TC001: Không gửi Header Authorization trong yêu cầu xác thực đạo văn

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Request không đính kèm Token xác thực.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/verify-plagiarism`
- **Body Input**:
  ```json
  {
    "student_a_code": "#include <stdio.h>\nint main(){ int a; scanf(\"%d\", &a); printf(\"%d\", a); return 0; }",
    "student_b_code": "#include <stdio.h>\nint main(){ int b; scanf(\"%d\", &b); printf(\"%d\", b); return 0; }",
    "ast_similarity_percentage": 95.0,
    "language": "C"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/verify-plagiarism`.
2. Không truyền Token xác thực (bỏ trống Header `Authorization`).
3. Đính kèm Request Body dữ liệu.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `401 Unauthorized`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 401,
    "error_code": "AUTH_TOKEN_MISSING",
    "message": "Yêu cầu xác thực tài khoản. Vui lòng cung cấp Access Token.",
    "details": null,
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiVerifyPlagiarism_TC002: Quản trị viên (ADMIN) không có quyền gọi API xác thực đạo văn của Giảng viên

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Người dùng đã đăng nhập với vai trò Quản trị viên `role = "ADMIN"`.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/verify-plagiarism`
- **Body Input**:
  ```json
  {
    "student_a_code": "#include <stdio.h>\nint main(){ int a; return 0; }",
    "student_b_code": "#include <stdio.h>\nint main(){ int b; return 0; }",
    "ast_similarity_percentage": 90.0,
    "language": "C"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/verify-plagiarism`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. Đính kèm Request Body dữ liệu.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `403 Forbidden`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 403,
    "error_code": "AUTH_PERMISSION_DENIED",
    "message": "Chỉ Giảng viên mới có quyền sử dụng tính năng giám định đạo văn AI Vòng 2.",
    "details": null,
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiVerifyPlagiarism_TC003: Giảng viên đã dùng hết hạn ngạch Token AI trong ngày

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Giảng viên `teacher_quang` đã dùng hết 50,000/50,000 tokens.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/verify-plagiarism`
- **Body Input**:
  ```json
  {
    "student_a_code": "#include <stdio.h>\nint main(){ int a; return 0; }",
    "student_b_code": "#include <stdio.h>\nint main(){ int b; return 0; }",
    "ast_similarity_percentage": 92.0,
    "language": "C"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/verify-plagiarism`.
2. Truyền token của Giảng viên đã cạn hạn ngạch ngày vào Header `Authorization: Bearer <EXHAUSTED_QUOTA_TOKEN>`.
3. Đính kèm Request Body dữ liệu.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `429 Too Many Requests`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 429,
    "error_code": "AI_QUOTA_EXCEEDED",
    "message": "Tài khoản của bạn đã sử dụng hết hạn ngạch Token AI trong ngày.",
    "details": null,
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiVerifyPlagiarism_TC004: Thiếu trường bắt buộc student_a_code hoặc student_b_code

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Giảng viên có Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/verify-plagiarism`
- **Body Input**:
  ```json
  {
    "student_a_code": "#include <stdio.h>\nint main(){ return 0; }",
    "ast_similarity_percentage": 90.0,
    "language": "C"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/verify-plagiarism`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/verify-plagiarism` thiếu `student_b_code`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "student_b_code",
        "issue": "Mã nguồn bài nộp 2 (student_b_code) là trường bắt buộc."
      }
    ],
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiVerifyPlagiarism_TC005: student_a_code hoặc student_b_code có độ dài dưới 10 ký tự

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Giảng viên có Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/verify-plagiarism`
- **Body Input**:

  ```json
  {
    "student_a_code": "int a=0;",
    "student_b_code": "#include <stdio.h>\nint main(){ return 0; }",
    "ast_similarity_percentage": 85.0,
    "language": "C"
  }
  ```

  *(Chuỗi `"int a=0;"` có đúng 8 ký tự, vi phạm minLength: 10)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/verify-plagiarism`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/verify-plagiarism` với `student_a_code` 8 ký tự.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "student_a_code",
        "issue": "Mã nguồn bài nộp 1 phải có độ dài tối thiểu 10 ký tự."
      }
    ],
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiVerifyPlagiarism_TC006: student_a_code hoặc student_b_code vượt quá 10000 ký tự

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Giảng viên có Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/verify-plagiarism`
- **Body Input**:
  ```json
  {
    "student_a_code": "#include <stdio.h>\nint main(){ return 0; }",
    "student_b_code": "int main(){ /* ...chuỗi dài 10005 ký tự... */ return 0; }",
    "ast_similarity_percentage": 85.0,
    "language": "C"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Tạo mã nguồn `student_b_code` có độ dài 10005 ký tự.
2. Khởi tạo HTTP Request `POST /api/v1/ai/verify-plagiarism`.
3. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "student_b_code",
        "issue": "Mã nguồn bài nộp không được vượt quá 10000 ký tự."
      }
    ],
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiVerifyPlagiarism_TC007: ast_similarity_percentage nhỏ hơn 80.0% (Vi phạm ngưỡng tối thiểu đưa vào Vòng 2)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Giảng viên có Token hợp lệ và còn quota.
- Quy định hệ thống: Chỉ các cặp bài nộp có AST >= 80.0% mới được chuyển sang AI Vòng 2.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/verify-plagiarism`
- **Body Input**:
  ```json
  {
    "student_a_code": "#include <stdio.h>\nint main(){ int x; scanf(\"%d\", &x); return 0; }",
    "student_b_code": "#include <stdio.h>\nint main(){ int y; scanf(\"%d\", &y); return 0; }",
    "ast_similarity_percentage": 79.9,
    "language": "C"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/verify-plagiarism`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/verify-plagiarism` với `ast_similarity_percentage = 79.9`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "ast_similarity_percentage",
        "issue": "Độ tương đồng AST đưa vào xác thực vòng 2 phải đạt tối thiểu 80.0%."
      }
    ],
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiVerifyPlagiarism_TC008: ast_similarity_percentage lớn hơn 100.0%

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Giảng viên có Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/verify-plagiarism`
- **Body Input**:
  ```json
  {
    "student_a_code": "#include <stdio.h>\nint main(){ int a; return 0; }",
    "student_b_code": "#include <stdio.h>\nint main(){ int b; return 0; }",
    "ast_similarity_percentage": 105.0,
    "language": "C"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/verify-plagiarism`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/verify-plagiarism` với `ast_similarity_percentage = 105.0`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "ast_similarity_percentage",
        "issue": "Độ tương đồng AST không được vượt quá 100.0%."
      }
    ],
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiVerifyPlagiarism_TC009: Thiếu trường bắt buộc language trong Body

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Giảng viên có Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/verify-plagiarism`
- **Body Input**:
  ```json
  {
    "student_a_code": "#include <stdio.h>\nint main(){ return 0; }",
    "student_b_code": "#include <stdio.h>\nint main(){ return 0; }",
    "ast_similarity_percentage": 95.0
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/verify-plagiarism`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/verify-plagiarism` thiếu trường `language`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "language",
        "issue": "Ngôn ngữ lập trình (language) là trường bắt buộc."
      }
    ],
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiVerifyPlagiarism_TC010: Dịch vụ Gemini AI gặp sự cố kết nối hoặc mạng bị timeout khi giám định đạo văn

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Google Gemini API trả lỗi 503 hoặc timeout kết nối mạng quá 30 giây.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/verify-plagiarism`
- **Body Input**:
  ```json
  {
    "student_a_code": "#include <stdio.h>\nint main(){ int a; scanf(\"%d\", &a); return 0; }",
    "student_b_code": "#include <stdio.h>\nint main(){ int b; scanf(\"%d\", &b); return 0; }",
    "ast_similarity_percentage": 90.0,
    "language": "C"
  }
  ```
- **Mock State**: `GeminiService.verifyPlagiarism() -> throws TimeoutException(30000ms)`.

#### Các bước thực hiện (Test Steps)

1. Cấu hình mock Gemini Service gặp lỗi timeout 30s.
2. Khởi tạo HTTP Request `POST /api/v1/ai/verify-plagiarism`.
3. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `503 Service Unavailable`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 503,
    "error_code": "AI_SERVICE_UNAVAILABLE",
    "message": "Dịch vụ Gemini AI hiện không khả dụng hoặc phản hồi quá lâu. Vui lòng thử lại sau.",
    "details": null,
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiVerifyPlagiarism_TC011: Xác thực thành công nghi vấn đạo văn tinh vi (Đổi tên biến & đảo câu lệnh if)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Giảng viên sở hữu Token hợp lệ và còn hạn ngạch Token.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/verify-plagiarism`
- **Body Input**:
  ```json
  {
    "student_a_code": "#include <stdio.h>\nint main() {\n  int n; scanf(\"%d\", &n);\n  int sum = 0;\n  for(int i=1; i<=n; i++) if(n%i==0) sum+=i;\n  printf(\"%d\", sum);\n  return 0;\n}",
    "student_b_code": "#include <stdio.h>\nint main() {\n  int total = 0;\n  int m; scanf(\"%d\", &m);\n  for(int j=1; j<=m; j++) {\n    if (m % j == 0) total += j;\n  }\n  printf(\"%d\", total);\n  return 0;\n}",
    "ast_similarity_percentage": 94.8,
    "language": "C"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/verify-plagiarism`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/verify-plagiarism` với request body ở trên.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Phản hồi JSON:
  ```json
  {
    "success": true,
    "status_code": 200,
    "message": "Phân tích bằng chứng đạo văn thành công",
    "data": {
      "tokens_consumed": 510,
      "is_plagiarized": true,
      "confidence_percentage": 94.8,
      "evidence_summary": "Phát hiện đổi tên biến n -> m, sum -> total, hoán đổi thứ tự câu lệnh if không làm thay đổi luồng điều khiển; cấu trúc giải thuật giống nhau 100%.",
      "cloned_segments": [
        {
          "student_a_lines": "5-9",
          "student_b_lines": "6-10",
          "technique": "VARIABLE_RENAMING"
        }
      ]
    },
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiVerifyPlagiarism_TC012: Xác thực thành công khi độ tương đồng đúng biên dưới 80.0% (Kết luận trùng hợp ngẫu nhiên)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Giảng viên sở hữu Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/verify-plagiarism`
- **Body Input**:
  ```json
  {
    "student_a_code": "#include <stdio.h>\nint main(){ printf(\"Hello World\"); return 0; }",
    "student_b_code": "#include <stdio.h>\nint main(){ printf(\"Hello World\"); return 0; }",
    "ast_similarity_percentage": 80.0,
    "language": "C"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/verify-plagiarism`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/verify-plagiarism` với `ast_similarity_percentage = 80.0`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- `data.is_plagiarized`: `false`.
- `data.evidence_summary`: Xác định đây là mã nguồn mẫu in chuỗi cơ bản, việc trùng lặp là ngẫu nhiên, không cấu thành hành vi gian lận.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiVerifyPlagiarism_TC013: Xác thực thành công khi độ tương đồng đạt biên trên tối đa 100.0% (Sao chép nguyên văn)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Giảng viên sở hữu Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/verify-plagiarism`
- **Body Input**:
  ```json
  {
    "student_a_code": "#include <stdio.h>\nint main(){ int a, b; scanf(\"%d%d\", &a, &b); printf(\"%d\", a+b); return 0; }",
    "student_b_code": "#include <stdio.h>\nint main(){ int a, b; scanf(\"%d%d\", &a, &b); printf(\"%d\", a+b); return 0; }",
    "ast_similarity_percentage": 100.0,
    "language": "C"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/verify-plagiarism`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/verify-plagiarism` với `ast_similarity_percentage = 100.0`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- `data.is_plagiarized`: `true`.
- `data.confidence_percentage`: `100.0`.
- `data.evidence_summary`: Kết luận sao chép nguyên văn từng dòng code (Exact copy).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiVerifyPlagiarism_TC014: Xác thực thành công cho bài thi Java với kỹ thuật tách hàm con (Modular Refactoring)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Giảng viên sở hữu Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/verify-plagiarism`
- **Body Input**:
  ```json
  {
    "student_a_code": "import java.util.Scanner;\npublic class Calc {\n  public static void main(String[] args){\n    Scanner sc = new Scanner(System.in);\n    int a = sc.nextInt(), b = sc.nextInt();\n    System.out.println(a * b + (a - b));\n  }\n}",
    "student_b_code": "import java.util.Scanner;\npublic class Calc {\n  public static int compute(int x, int y){ return x * y + (x - y); }\n  public static void main(String[] args){\n    Scanner sc = new Scanner(System.in);\n    int x = sc.nextInt(), y = sc.nextInt();\n    System.out.println(compute(x, y));\n  }\n}",
    "ast_similarity_percentage": 88.5,
    "language": "JAVA"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/verify-plagiarism`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/verify-plagiarism` với payload java ở trên.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- `data.is_plagiarized`: `true`.
- `data.evidence_summary`: Nhận diện kỹ thuật bọc biểu thức tính toán thành hàm con `compute()` nhằm ngụy trang gian lận.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# ==============================================================================

# PHẦN 5: API POST /api/v1/ai/evaluate-web-ui (UC-19: ĐÁNH GIÁ GIAO DIỆN WEB MULTIMODAL)

# ==============================================================================

# UT03_AiEvaluateWebUI_TC001: Không gửi Header Authorization trong yêu cầu đánh giá giao diện Web

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Request không truyền Token xác thực.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/evaluate-web-ui`
- **Body Input**:
  ```json
  {
    "screenshot_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    "rubric_requirements": [
      "Bố cục cân đối có thanh điều hướng navbar trên đầu"
    ]
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/evaluate-web-ui`.
2. Không truyền Token xác thực (bỏ trống Header `Authorization`).
3. Đính kèm Request Body dữ liệu.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `401 Unauthorized`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 401,
    "error_code": "AUTH_TOKEN_MISSING",
    "message": "Yêu cầu xác thực tài khoản. Vui lòng cung cấp Access Token.",
    "details": null,
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiEvaluateWebUI_TC002: Quản trị viên (ADMIN) không có quyền gọi API chấm giao diện Web của Giảng viên

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Người dùng đã đăng nhập với vai trò Quản trị viên `role = "ADMIN"`.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/evaluate-web-ui`
- **Body Input**:
  ```json
  {
    "screenshot_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    "rubric_requirements": [
      "Có thanh điều hướng navbar"
    ]
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/evaluate-web-ui`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. Đính kèm Request Body dữ liệu.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `403 Forbidden`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 403,
    "error_code": "AUTH_PERMISSION_DENIED",
    "message": "Chỉ Giảng viên mới có quyền sử dụng tính năng đánh giá giao diện Web qua AI.",
    "details": null,
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiEvaluateWebUI_TC003: Giảng viên đã dùng hết hạn ngạch Token AI trong ngày

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Giảng viên `teacher_quang` đã dùng hết 50,000/50,000 tokens.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/evaluate-web-ui`
- **Body Input**:
  ```json
  {
    "screenshot_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    "rubric_requirements": [
      "Có thanh điều hướng navbar"
    ]
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/evaluate-web-ui`.
2. Truyền token của Giảng viên đã cạn hạn ngạch ngày vào Header `Authorization: Bearer <EXHAUSTED_QUOTA_TOKEN>`.
3. Đính kèm Request Body dữ liệu.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `429 Too Many Requests`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 429,
    "error_code": "AI_QUOTA_EXCEEDED",
    "message": "Tài khoản của bạn đã sử dụng hết hạn ngạch Token AI trong ngày.",
    "details": null,
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiEvaluateWebUI_TC004: Thiếu trường bắt buộc screenshot_base64 trong Body

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Giảng viên có Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/evaluate-web-ui`
- **Body Input**:
  ```json
  {
    "rubric_requirements": [
      "Bố cục cân đối có thanh điều hướng navbar"
    ]
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/evaluate-web-ui`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/evaluate-web-ui` thiếu `screenshot_base64`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "screenshot_base64",
        "issue": "Ảnh chụp màn hình (screenshot_base64) là trường bắt buộc."
      }
    ],
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiEvaluateWebUI_TC005: screenshot_base64 không phải định dạng chuỗi Base64 hợp lệ

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Giảng viên có Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/evaluate-web-ui`
- **Body Input**:
  ```json
  {
    "screenshot_base64": "invalid_base64_string_not_an_image!@#$%",
    "rubric_requirements": [
      "Có thanh điều hướng navbar"
    ]
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/evaluate-web-ui`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/evaluate-web-ui` với chuỗi `screenshot_base64` rác.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "screenshot_base64",
        "issue": "Dữ liệu ảnh phải là chuỗi định dạng Base64 hợp lệ của tệp hình ảnh."
      }
    ],
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiEvaluateWebUI_TC006: screenshot_base64 vượt quá dung lượng tối đa 5MB (413 Payload Too Large)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Giảng viên có Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/evaluate-web-ui`
- **Body Input**:
  ```json
  {
    "screenshot_base64": "data:image/png;base64,...[chuỗi base64 có dung lượng giải mã tương đương 5.2 MB]...",
    "rubric_requirements": [
      "Có navbar"
    ]
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Tạo chuỗi ảnh Base64 có kích thước vượt quá 5MB.
2. Khởi tạo HTTP Request `POST /api/v1/ai/evaluate-web-ui`.
3. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `413 Payload Too Large`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 413,
    "error_code": "PAYLOAD_TOO_LARGE",
    "message": "Dung lượng ảnh chụp màn hình vượt quá giới hạn cho phép (tối đa 5MB).",
    "details": null,
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiEvaluateWebUI_TC007: Thiếu trường rubric_requirements hoặc truyền null trong Body

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Giảng viên có Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/evaluate-web-ui`
- **Body Input**:
  ```json
  {
    "screenshot_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/evaluate-web-ui`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/evaluate-web-ui` thiếu `rubric_requirements`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "rubric_requirements",
        "issue": "Tiêu chí đánh giá giao diện (rubric_requirements) là trường bắt buộc."
      }
    ],
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiEvaluateWebUI_TC008: rubric_requirements là mảng rỗng không có phần tử nào (Vi phạm minItems: 1)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Giảng viên có Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/evaluate-web-ui`
- **Body Input**:
  ```json
  {
    "screenshot_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    "rubric_requirements": []
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/evaluate-web-ui`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/evaluate-web-ui` với `rubric_requirements: []`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "rubric_requirements",
        "issue": "Danh sách tiêu chí đánh giá phải có tối thiểu 1 tiêu chí."
      }
    ],
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiEvaluateWebUI_TC009: Dịch vụ Gemini Multimodal Vision gặp sự cố hoặc timeout phản hồi

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Google Gemini Multimodal Vision API trả mã lỗi 503 hoặc timeout kết nối mạng quá 35 giây.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/evaluate-web-ui`
- **Body Input**:
  ```json
  {
    "screenshot_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    "rubric_requirements": [
      "Có thanh điều hướng navbar trên đầu"
    ]
  }
  ```
- **Mock State**: `GeminiVisionService.evaluateImage() -> throws TimeoutException(35000ms)`.

#### Các bước thực hiện (Test Steps)

1. Giả lập kết nối mạng tới Gemini Vision bị nghẽn (timeout > 35s) hoặc mã lỗi 503.
2. Khởi tạo HTTP Request `POST /api/v1/ai/evaluate-web-ui`.
3. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `503 Service Unavailable`.
- Phản hồi JSON:
  ```json
  {
    "success": false,
    "status_code": 503,
    "error_code": "AI_SERVICE_UNAVAILABLE",
    "message": "Dịch vụ Gemini AI hiện không khả dụng hoặc phản hồi quá lâu. Vui lòng thử lại sau.",
    "details": null,
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiEvaluateWebUI_TC010: Đánh giá giao diện Web thành công với 3 tiêu chí rubric chuẩn

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Giảng viên sở hữu Token hợp lệ và còn hạn ngạch Token.
- Dịch vụ Gemini Vision hoạt động ổn định.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/evaluate-web-ui`
- **Body Input**:
  ```json
  {
    "screenshot_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    "rubric_requirements": [
      "Bố cục cân đối có thanh điều hướng navbar trên đầu",
      "Form đăng ký gồm 3 input và nút bấm nổi bật",
      "Phối màu hài hòa, có độ tương phản văn bản tốt"
    ]
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/evaluate-web-ui`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/evaluate-web-ui` với request body ở trên.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Phản hồi JSON:
  ```json
  {
    "success": true,
    "status_code": 200,
    "message": "Đánh giá giao diện Web bằng AI thành công",
    "data": {
      "tokens_consumed": 720,
      "ui_score": 8.5,
      "evaluation_details": [
        {
          "criterion": "Bố cục cân đối có thanh điều hướng navbar trên đầu",
          "score": 10.0,
          "verdict": "PASS",
          "comment": "Navbar thiết kế rõ ràng, logo bên trái và link bên phải chuẩn mực."
        },
        {
          "criterion": "Form đăng ký gồm 3 input và nút bấm nổi bật",
          "score": 8.0,
          "verdict": "PASS",
          "comment": "Có đủ input nhưng khoảng cách padding giữa các trường hơi sát nhau."
        },
        {
          "criterion": "Phối màu hài hòa, có độ tương phản văn bản tốt",
          "score": 7.5,
          "verdict": "PARTIAL",
          "comment": "Màu nền sáng và chữ đen tương phản tốt, nhưng nút phụ viền xám nhạt hơi khó thấy."
        }
      ],
      "overall_feedback": "Trang web có bố cục hài hòa, màu sắc nhã nhặn, đáp ứng tốt yêu cầu đề thi."
    },
    "timestamp": "2026-10-04T09:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiEvaluateWebUI_TC011: Đánh giá giao diện Web thành công với đúng 1 tiêu chí rubric (Biên dưới minItems: 1)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Giảng viên sở hữu Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/evaluate-web-ui`
- **Body Input**:
  ```json
  {
    "screenshot_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    "rubric_requirements": [
      "Trang web có footer chứa thông tin bản quyền và liên hệ"
    ]
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/evaluate-web-ui`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/evaluate-web-ui` với mảng `rubric_requirements` có đúng 1 phần tử.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- `data.evaluation_details`: Mảng có chính xác 1 phần tử kết quả đánh giá cho tiêu chí footer.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiEvaluateWebUI_TC012: Đánh giá giao diện Web thành công với ảnh định dạng JPEG chất lượng cao

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Giảng viên sở hữu Token hợp lệ và còn quota.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/evaluate-web-ui`
- **Body Input**:
  ```json
  {
    "screenshot_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA=",
    "rubric_requirements": [
      "Giao diện tương thích độ phân giải desktop 1920x1080"
    ]
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/evaluate-web-ui`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/evaluate-web-ui` với ảnh định dạng jpeg.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Hệ thống nhận diện chuẩn định dạng JPEG, trả về kết quả đánh giá thẩm mỹ giao diện.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT03_AiEvaluateWebUI_TC013: Đánh giá giao diện Web thành công khi bài làm vi phạm rubric (ui_score thấp, verdict FAIL)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Giảng viên sở hữu Token hợp lệ và còn quota.
- Bài làm của sinh viên bị vỡ bố cục nghiêm trọng, chữ đè lên ảnh.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/ai/evaluate-web-ui`
- **Body Input**:
  ```json
  {
    "screenshot_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    "rubric_requirements": [
      "Bố cục cân đối, nội dung không bị tràn khung hay chữ đè lên nhau",
      "Màu sắc chữ có độ tương phản đạt chuẩn WCAG AA"
    ]
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/ai/evaluate-web-ui`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. `post /api/v1/ai/evaluate-web-ui` với ảnh bài nộp bị lỗi giao diện.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- `data.ui_score`: Điểm thấp (dưới 4.0 / 10.0).
- `data.evaluation_details[].verdict`: `"FAIL"`.
- `data.evaluation_details[].comment`: Nhận xét chỉ rõ các lỗi hiển thị vỡ layout và độ tương phản kém.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |
