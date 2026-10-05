# Thông Tin Chung Kiểm Thử Unit Test

- **Phân hệ kiểm thử**: Phân hệ Xác thực Tài khoản & Quản lý Phiên làm việc (Authentication API)
- **Danh sách API kiểm thử**:
  - `POST /api/v1/auth/login` (UC-01: Đăng nhập tài khoản, trả về JWT Access Token & Refresh Token)
  - `GET /api/v1/auth/me` (UC-02: Lấy thông tin tài khoản đang đăng nhập từ Access Token)
  - `POST /api/v1/auth/refresh` (UC-03: Cấp mới Access Token bằng Refresh Token)
- **Người thực hiện (Tester/Dev)**: Kim Chi Ha
- **Ngày tạo**: 05/10/2026
- **Cập nhật lần cuối**: 05/10/2026 - 07:30
- **Tài liệu liên quan**:
  - [Đặc tả API Phân hệ Xác thực (Markdown)](file:///c:/AITA/iata_project/docs/apis/auth/auth-api.md)
  - [Đặc tả OpenAPI Phân hệ Xác thực (YAML)](file:///c:/AITA/iata_project/docs/apis/auth/auth.yaml)
  - [Đặc tả API Toàn hệ thống AITA](file:///c:/AITA/iata_project/docs/apis/api-specification.md)
  - [Bảng Danh mục Mã lỗi Phản hồi Hệ thống](file:///c:/AITA/iata_project/docs/architecture/api-response-codes.md)
  - [Quy tắc kiểm thử Testcase](file:///c:/AITA/iata_project/rules/testcase-rules.md)
- **Tổng số Testcase**: 41 Testcases (Trạng thái: Chưa thực thi - Sẵn sàng kiểm thử; Trường hợp False/Lỗi viết trước, True/Thành công viết sau; Đầy đủ Test Data cụ thể cho từng Testcase)
  - `POST /api/v1/auth/login`: 18 Testcases (14 False, 04 True)
  - `GET /api/v1/auth/me`: 11 Testcases (09 False, 02 True)
  - `POST /api/v1/auth/refresh`: 12 Testcases (10 False, 02 True)

---

# ==============================================================================

# PHẦN 1: API POST /api/v1/auth/login (UC-01: ĐĂNG NHẬP HỆ THỐNG VÀ CẤP PHÁT JWT TOKENS)

# ==============================================================================

# UT01_AuthLogin_TC001: Gửi Request Body không đúng định dạng cú pháp JSON

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server Backend (Auth Module) đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/login`
- **Body Input**:
  ```text
  {"username": "teacher_hung", "password": "Password123@"
  ```

  *(Chuỗi JSON bị thiếu dấu ngoặc nhọn kết thúc `}` gây lỗi phân tích cú pháp)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/auth/login`.
2. Đính kèm Headers `Content-Type: application/json` và `Accept: application/json`.
3. Gửi payload Body chứa chuỗi JSON bị lỗi cú pháp lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `400 Bad Request`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 400,
    "error_code": "BAD_REQUEST",
    "message": "Dữ liệu yêu cầu gửi lên không đúng định dạng JSON hợp lệ.",
    "details": null,
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthLogin_TC002: Request Body rỗng thiếu cả hai trường username và password

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server Backend đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/login`
- **Body Input**:
  ```json
  {}
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/auth/login`.
2. Đính kèm Body là một đối tượng JSON rỗng `{}`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "username",
        "issue": "Tên đăng nhập (username) là trường bắt buộc."
      },
      {
        "field": "password",
        "issue": "Mật khẩu (password) là trường bắt buộc."
      }
    ],
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthLogin_TC003: Thiếu trường bắt buộc username trong Request Body

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server Backend đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/login`
- **Body Input**:
  ```json
  {
    "password": "Password123@"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/auth/login`.
2. Đính kèm Body chỉ có trường `password`, khuyết hoàn toàn trường `username`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "username",
        "issue": "Tên đăng nhập (username) là trường bắt buộc."
      }
    ],
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthLogin_TC004: Thiếu trường bắt buộc password trong Request Body

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server Backend đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/login`
- **Body Input**:
  ```json
  {
    "username": "teacher_hung"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/auth/login`.
2. Đính kèm Body chỉ có trường `username`, khuyết hoàn toàn trường `password`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "password",
        "issue": "Mật khẩu (password) là trường bắt buộc."
      }
    ],
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthLogin_TC005: Trường username có độ dài dưới 3 ký tự (Vi phạm biên minLength)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server Backend đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/login`
- **Body Input**:
  ```json
  {
    "username": "th",
    "password": "Password123@"
  }
  ```

  *(Chuỗi `"th"` có đúng 2 ký tự, vi phạm quy định `minLength: 3`)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/auth/login`.
2. Đính kèm Request Body với `username` có độ dài 2 ký tự.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "username",
        "issue": "Tên đăng nhập phải có ít nhất 3 ký tự."
      }
    ],
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthLogin_TC006: Trường username có độ dài vượt quá 50 ký tự (Vi phạm biên maxLength)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server Backend đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/login`
- **Body Input**:
  ```json
  {
    "username": "teacher_hung_extra_long_username_over_limit_fpt_edu_51",
    "password": "Password123@"
  }
  ```

  *(Chuỗi `"teacher_hung_extra_long_username_over_limit_fpt_edu_51"` có đúng 51 ký tự, vi phạm quy định `maxLength: 50`)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/auth/login`.
2. Đính kèm Request Body với `username` có độ dài 51 ký tự.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "username",
        "issue": "Tên đăng nhập không được vượt quá 50 ký tự."
      }
    ],
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthLogin_TC007: Trường password có độ dài dưới 6 ký tự (Vi phạm biên minLength)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server Backend đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/login`
- **Body Input**:
  ```json
  {
    "username": "teacher_hung",
    "password": "12345"
  }
  ```

  *(Chuỗi mật khẩu `"12345"` có đúng 5 ký tự, vi phạm quy định `minLength: 6`)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/auth/login`.
2. Đính kèm Request Body với `password` có độ dài 5 ký tự.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "password",
        "issue": "Mật khẩu phải có ít nhất 6 ký tự."
      }
    ],
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthLogin_TC008: Trường password có độ dài vượt quá 100 ký tự (Vi phạm biên maxLength)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server Backend đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/login`
- **Body Input**:
  ```json
  {
    "username": "teacher_hung",
    "password": "P@ssword123P@ssword123P@ssword123P@ssword123P@ssword123P@ssword123P@ssword123P@ssword123P@ssword123P@ssword1231"
  }
  ```

  *(Chuỗi mật khẩu có đúng 101 ký tự, vi phạm quy định `maxLength: 100`)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/auth/login`.
2. Đính kèm Request Body với `password` dài 101 ký tự.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "password",
        "issue": "Mật khẩu không được vượt quá 100 ký tự."
      }
    ],
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthLogin_TC009: Trường username sai kiểu dữ liệu (Gửi kiểu số thay vì chuỗi)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server Backend đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/login`
- **Body Input**:
  ```json
  {
    "username": 123456,
    "password": "Password123@"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/auth/login`.
2. Đính kèm Request Body với trường `username` là số nguyên `123456`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "username",
        "issue": "Tên đăng nhập phải là một chuỗi ký tự (string)."
      }
    ],
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthLogin_TC010: Trường password sai kiểu dữ liệu (Gửi mảng thay vì chuỗi)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server Backend đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/login`
- **Body Input**:
  ```json
  {
    "username": "teacher_hung",
    "password": ["Pass123", "Secret"]
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/auth/login`.
2. Đính kèm Request Body với trường `password` là mảng dữ liệu.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "password",
        "issue": "Mật khẩu phải là một chuỗi ký tự (string)."
      }
    ],
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthLogin_TC011: Đăng nhập thất bại do tên đăng nhập không tồn tại trong hệ thống

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Tên người dùng `nonexistent_user` không tồn tại trong bảng `users` của CSDL.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/login`
- **Body Input**:
  ```json
  {
    "username": "nonexistent_user",
    "password": "Password123@"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/auth/login`.
2. Đính kèm thông tin tài khoản không tồn tại `nonexistent_user`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `401 Unauthorized`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 401,
    "error_code": "AUTH_INVALID_CREDENTIALS",
    "message": "Tên đăng nhập hoặc mật khẩu không chính xác.",
    "details": null,
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthLogin_TC012: Đăng nhập thất bại do tên đăng nhập đúng nhưng sai mật khẩu

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Tài khoản `teacher_hung` tồn tại trong hệ thống, đang hoạt động (`is_active = true`).
- Mật khẩu thực tế đã hash trong CSDL khác với mật khẩu nhập vào.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/login`
- **Body Input**:
  ```json
  {
    "username": "teacher_hung",
    "password": "WrongPassword999@"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/auth/login`.
2. Đính kèm `username: "teacher_hung"` và mật khẩu sai `WrongPassword999@`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `401 Unauthorized`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 401,
    "error_code": "AUTH_INVALID_CREDENTIALS",
    "message": "Tên đăng nhập hoặc mật khẩu không chính xác.",
    "details": null,
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthLogin_TC013: Đăng nhập thất bại do tài khoản đã bị khóa bởi Quản trị viên

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Tài khoản Giảng viên `teacher_locked` tồn tại trong hệ thống.
- Cột trạng thái tài khoản trong CSDL có giá trị `is_active = false`.
- Mật khẩu nhập vào hoàn toàn chính xác với hash CSDL.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/login`
- **Body Input**:
  ```json
  {
    "username": "teacher_locked",
    "password": "CorrectPassword123@"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/auth/login`.
2. Đính kèm thông tin đăng nhập của tài khoản đã bị vô hiệu hóa `teacher_locked`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `403 Forbidden`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 403,
    "error_code": "AUTH_ACCOUNT_DISABLED",
    "message": "Tài khoản của bạn đã bị vô hiệu hóa. Vui lòng liên hệ Quản trị viên.",
    "details": null,
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthLogin_TC014: Lỗi máy chủ cơ sở dữ liệu nội bộ khi thực hiện truy vấn đăng nhập

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Dịch vụ cơ sở dữ liệu PostgreSQL/MySQL quản lý tài khoản bị ngắt kết nối giả lập (Mock DB Connection Error).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/login`
- **Body Input**:
  ```json
  {
    "username": "teacher_hung",
    "password": "Password123@"
  }
  ```
- **Mock State**: `DatabaseConnectionPool.status = 'DISCONNECTED'`.

#### Các bước thực hiện (Test Steps)

1. Kích hoạt trạng thái lỗi ngắt kết nối database trên Mock Backend Server.
2. Gửi Request `POST /api/v1/auth/login` với dữ liệu đăng nhập chuẩn.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `500 Internal Server Error`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 500,
    "error_code": "INTERNAL_SERVER_ERROR",
    "message": "Đã xảy ra lỗi máy chủ nội bộ. Vui lòng thử lại sau.",
    "details": null,
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthLogin_TC015: Đăng nhập thành công với username và password ở độ dài biên nhỏ nhất

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Tài khoản có `username = "adm"` (3 ký tự - minLength biên dưới), mật khẩu `"Adm12@"` (6 ký tự - minLength biên dưới).
- Tài khoản đang hoạt động (`is_active = true`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/login`
- **Body Input**:
  ```json
  {
    "username": "adm",
    "password": "Adm12@"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/auth/login`.
2. Đính kèm body chứa `username` 3 ký tự và `password` 6 ký tự.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": true,
    "status_code": 200,
    "message": "Đăng nhập thành công",
    "data": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MywidXNlcm5hbWUiOiJhZG0iLCJyb2xlIjoiQURNSU4iLCJleHAiOjE3OTk5OTk5OTl9.MOCK_VALID_SIGNATURE",
      "refresh_token": "def502005a76c8e3boundarytokenminlength",
      "token_type": "Bearer",
      "expires_in": 86400,
      "user": {
        "id": 3,
        "username": "adm",
        "full_name": "Quản Trị Biên Nhỏ",
        "email": "adm@fe.edu.vn",
        "role": "ADMIN",
        "is_active": true
      }
    },
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthLogin_TC016: Đăng nhập thành công với username và password ở độ dài biên tối đa

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Tài khoản có `username` đúng 50 ký tự (`"teacher_hung_exact_fifty_characters_username_aita"`) và `password` đúng 100 ký tự (`"P@ssword123P@ssword123P@ssword123P@ssword123P@ssword123P@ssword123P@ssword123P@ssword123P@ssword123P@ssword12"`).
- Tài khoản đang hoạt động (`is_active = true`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/login`
- **Body Input**:
  ```json
  {
    "username": "teacher_hung_exact_fifty_characters_username_aita",
    "password": "P@ssword123P@ssword123P@ssword123P@ssword123P@ssword123P@ssword123P@ssword123P@ssword123P@ssword123P@ssword12"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/auth/login`.
2. Đính kèm body chứa `username` 50 ký tự và `password` 100 ký tự.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Phản hồi JSON chứa `success = true`, mã `status_code = 200`, cấp `access_token` và `refresh_token` hợp lệ cùng thông tin tài khoản.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthLogin_TC017: Đăng nhập thành công với tài khoản Giảng viên (INSTRUCTOR)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Tài khoản Giảng viên `teacher_hung` tồn tại trong hệ thống, `is_active = true`, `role = "INSTRUCTOR"`.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/login`
- **Body Input**:
  ```json
  {
    "username": "teacher_hung",
    "password": "Password123@"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/auth/login`.
2. Đính kèm Body chứa thông tin tài khoản Giảng viên `teacher_hung`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": true,
    "status_code": 200,
    "message": "Đăng nhập thành công",
    "data": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJ0ZWFjaGVyX2h1bmciLCJyb2xlIjoiSU5TVFJVQ1RPUiIsImV4cCI6MTc5OTk5OTk5OX0.MOCK_INSTRUCTOR_SIGNATURE",
      "refresh_token": "def502005a76c8e3teacherhungrefreshtoken",
      "token_type": "Bearer",
      "expires_in": 86400,
      "user": {
        "id": 1,
        "username": "teacher_hung",
        "full_name": "Nguyễn Văn Hùng",
        "email": "hungnv@fe.edu.vn",
        "role": "INSTRUCTOR",
        "is_active": true
      }
    },
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthLogin_TC018: Đăng nhập thành công với tài khoản Quản trị viên (ADMIN)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Tài khoản Quản trị viên `admin` tồn tại trong hệ thống, `is_active = true`, `role = "ADMIN"`.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/login`
- **Body Input**:
  ```json
  {
    "username": "admin",
    "password": "AdminPassword2026@"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/auth/login`.
2. Đính kèm Body chứa thông tin tài khoản Quản trị viên `admin`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": true,
    "status_code": 200,
    "message": "Đăng nhập thành công",
    "data": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MiwidXNlcm5hbWUiOiJhZG1pbiIsInJvbGUiOiJBRE1JTiIsImV4cCI6MTc5OTk5OTk5OX0.MOCK_ADMIN_SIGNATURE",
      "refresh_token": "def502005a76c8e3adminrefreshtokenstring",
      "token_type": "Bearer",
      "expires_in": 86400,
      "user": {
        "id": 2,
        "username": "admin",
        "full_name": "Quản Trị Viên Hệ Thống",
        "email": "admin@fe.edu.vn",
        "role": "ADMIN",
        "is_active": true
      }
    },
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# ==============================================================================

# PHẦN 2: API GET /api/v1/auth/me (UC-02: LẤY THÔNG TIN TÀI KHOẢN ĐANG ĐĂNG NHẬP)

# ==============================================================================

# UT01_AuthMe_TC001: Không gửi Header Authorization trong yêu cầu lấy thông tin hồ sơ

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server Backend đang hoạt động bình thường.
- Client gửi request không đính kèm Header `Authorization`.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/auth/me`
- **Body Input**: Không có (None).

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/auth/me`.
2. Không đính kèm Header `Authorization`.
3. Gửi Request lên hệ thống.

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
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthMe_TC002: Header Authorization có giá trị rỗng hoặc chỉ chứa tiền tố Bearer

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server Backend đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/auth/me`
- **Body Input**: Không có.

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/auth/me`.
2. Đính kèm Header `Authorization: Bearer ` (không có token đằng sau).
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `401 Unauthorized`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 401,
    "error_code": "AUTH_TOKEN_MISSING",
    "message": "Vui lòng đăng nhập để thực hiện thao tác này.",
    "details": null,
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthMe_TC003: Header Authorization sai định dạng Scheme (Không có tiền tố Bearer)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server Backend đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/auth/me`
- **Body Input**: Không có.

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/auth/me`.
2. Đính kèm Header `Authorization` với tiền tố `Basic ...`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `401 Unauthorized`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 401,
    "error_code": "AUTH_TOKEN_INVALID",
    "message": "Định dạng xác thực không hợp lệ. Vui lòng sử dụng phương thức Bearer Token.",
    "details": null,
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthMe_TC004: Token JWT sai cấu trúc không đủ 3 thành phần tiêu chuẩn

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server Backend đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/auth/me`
- **Body Input**: Không có.

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/auth/me`.
2. Đính kèm Bearer Token bị khuyết thành phần Signature.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `401 Unauthorized`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 401,
    "error_code": "AUTH_TOKEN_INVALID",
    "message": "Token xác thực không hợp lệ hoặc đã bị chỉnh sửa.",
    "details": null,
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthMe_TC005: Token JWT có chữ ký sai hoặc bị can thiệp thay đổi Payload

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server Backend đang hoạt động bình thường với Secret Key bảo mật.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/auth/me`
- **Body Input**: Không có.

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/auth/me`.
2. Đính kèm Token có chữ ký bị giả mạo / không khớp với khóa bí mật HMAC SHA-256 của máy chủ.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `401 Unauthorized`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 401,
    "error_code": "AUTH_TOKEN_INVALID",
    "message": "Mã truy cập không hợp lệ hoặc chữ ký sai.",
    "details": null,
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthMe_TC006: Bearer Access Token gửi lên đã hết hạn hiệu lực (Expired Token)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Token đã được cấp hợp lệ trước đó nhưng timestamp `exp` trong Payload đã nhỏ hơn thời điểm hiện tại (`exp = 1577836800` - năm 2020).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/auth/me`
- **Body Input**: Không có.

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/auth/me`.
2. Đính kèm Token đã hết hạn trong Header `Authorization`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `401 Unauthorized`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 401,
    "error_code": "AUTH_TOKEN_EXPIRED",
    "message": "Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại.",
    "details": null,
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthMe_TC007: Token hợp lệ nhưng tài khoản người dùng trong Token đã bị xóa khỏi CSDL

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Token có chữ ký hợp lệ và còn hạn, chứa `id: 999`.
- Người dùng có `id: 999` đã bị xóa hoàn toàn khỏi cơ sở dữ liệu (`User.findById(999) == null`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/auth/me`
- **Body Input**: Không có.

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/auth/me`.
2. Đính kèm Token của người dùng không còn tồn tại trong hệ thống.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `401 Unauthorized`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 401,
    "error_code": "AUTH_TOKEN_INVALID",
    "message": "Tài khoản liên kết với phiên làm việc không tồn tại trong hệ thống.",
    "details": null,
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthMe_TC008: Tài khoản người dùng trong Bearer Token đã bị vô hiệu hóa bởi Quản trị viên

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Người dùng `teacher_disabled` sở hữu token hợp lệ, còn hạn.
- Quản trị viên vừa thay đổi cờ trạng thái tài khoản thành `is_active = false`.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/auth/me`
- **Body Input**: Không có.

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/auth/me`.
2. Đính kèm Token của tài khoản vừa bị khóa.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `403 Forbidden`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 403,
    "error_code": "AUTH_ACCOUNT_DISABLED",
    "message": "Tài khoản của bạn đã bị vô hiệu hóa. Vui lòng liên hệ Quản trị viên.",
    "details": null,
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthMe_TC009: Lỗi máy chủ cơ sở dữ liệu nội bộ khi truy vấn hồ sơ tài khoản

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Token hợp lệ nhưng dịch vụ cơ sở dữ liệu bị mất kết nối giả lập trong quá trình xử lý truy vấn thông tin người dùng.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/auth/me`
- **Body Input**: Không có (None).
- **Mock State**: `DatabaseConnectionPool.status = 'DISCONNECTED'`.

#### Các bước thực hiện (Test Steps)

1. Thiết lập trạng thái gián đoạn kết nối CSDL trên Mock Server.
2. Gửi Request `GET /api/v1/auth/me` với Token hợp lệ.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `500 Internal Server Error`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 500,
    "error_code": "INTERNAL_SERVER_ERROR",
    "message": "Đã xảy ra lỗi máy chủ nội bộ. Vui lòng thử lại sau.",
    "details": null,
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthMe_TC010: Lấy thông tin tài khoản thành công với Token Giảng viên (INSTRUCTOR)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Giảng viên `teacher_hung` đang hoạt động (`is_active = true`), sở hữu Access Token hợp lệ còn thời hạn.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/auth/me`
- **Body Input**: Không có.

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/auth/me`.
2. Đính kèm Header `Authorization: Bearer <VALID_INSTRUCTOR_TOKEN>`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": true,
    "status_code": 200,
    "message": "Lấy thông tin tài khoản thành công",
    "data": {
      "id": 1,
      "username": "teacher_hung",
      "full_name": "Nguyễn Văn Hùng",
      "email": "hungnv@fe.edu.vn",
      "role": "INSTRUCTOR",
      "is_active": true,
      "created_at": "2026-09-01T08:00:00.000Z"
    },
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthMe_TC011: Lấy thông tin tài khoản thành công với Token Quản trị viên (ADMIN)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` đang hoạt động (`is_active = true`), sở hữu Access Token hợp lệ còn thời hạn.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/auth/me`
- **Body Input**: Không có.

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/auth/me`.
2. Đính kèm Header `Authorization: Bearer <VALID_ADMIN_TOKEN>`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": true,
    "status_code": 200,
    "message": "Lấy thông tin tài khoản thành công",
    "data": {
      "id": 2,
      "username": "admin",
      "full_name": "Quản Trị Viên Hệ Thống",
      "email": "admin@fe.edu.vn",
      "role": "ADMIN",
      "is_active": true,
      "created_at": "2026-09-01T00:00:00.000Z"
    },
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# ==============================================================================

# PHẦN 3: API POST /api/v1/auth/refresh (UC-03: GIA HẠN ACCESS TOKEN BẰNG REFRESH TOKEN)

# ==============================================================================

# UT01_AuthRefresh_TC001: Gửi Request Body không đúng định dạng cú pháp JSON

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server Backend đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/refresh`
- **Body Input**:
  ```text
  {"refresh_token": "def502005a76c8e3...
  ```

  *(Chuỗi JSON bị thiếu dấu đóng ngoặc kép và dấu đóng ngoặc nhọn)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/auth/refresh`.
2. Đính kèm chuỗi Body lỗi cú pháp JSON.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `400 Bad Request`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 400,
    "error_code": "BAD_REQUEST",
    "message": "Dữ liệu yêu cầu gửi lên không đúng định dạng JSON hợp lệ.",
    "details": null,
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthRefresh_TC002: Request Body rỗng thiếu trường bắt buộc refresh_token

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server Backend đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/refresh`
- **Body Input**:
  ```json
  {}
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/auth/refresh`.
2. Đính kèm Body rỗng `{}`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "refresh_token",
        "issue": "Mã gia hạn (refresh_token) là trường bắt buộc."
      }
    ],
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthRefresh_TC003: Trường refresh_token gửi lên là chuỗi rỗng hoặc chỉ có khoảng trắng

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server Backend đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/refresh`
- **Body Input**:
  ```json
  {
    "refresh_token": "   "
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/auth/refresh`.
2. Đính kèm Body chứa `refresh_token` là chuỗi 3 dấu khoảng trắng.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "refresh_token",
        "issue": "Mã gia hạn không được để trống."
      }
    ],
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthRefresh_TC004: Trường refresh_token sai kiểu dữ liệu (Gửi kiểu số thay vì chuỗi)

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server Backend đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/refresh`
- **Body Input**:
  ```json
  {
    "refresh_token": 987654321
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/auth/refresh`.
2. Đính kèm `refresh_token` là số nguyên `987654321`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `422 Unprocessable Entity`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 422,
    "error_code": "VALIDATION_FAILED",
    "message": "Dữ liệu gửi lên không đúng định dạng.",
    "details": [
      {
        "field": "refresh_token",
        "issue": "Mã gia hạn (refresh_token) phải là một chuỗi ký tự (string)."
      }
    ],
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthRefresh_TC005: Chuỗi refresh_token không tồn tại trong hệ thống hoặc giả mạo

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Chuỗi refresh token ngẫu nhiên không có trong bảng phiên làm việc (Redis Session Store / CSDL).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/refresh`
- **Body Input**:
  ```json
  {
    "refresh_token": "random_fake_token_not_exists_in_database_store_12345"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/auth/refresh`.
2. Đính kèm chuỗi `refresh_token` không có trong hệ thống.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `401 Unauthorized`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 401,
    "error_code": "AUTH_INVALID_REFRESH_TOKEN",
    "message": "Mã refresh token không hợp lệ hoặc không tồn tại.",
    "details": null,
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthRefresh_TC006: Mã refresh_token đã hết hạn sử dụng

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Token đã từng được cấp hợp lệ nhưng thời hạn lưu trữ phiên (TTL 7 ngày hoặc 30 ngày) đã hết hạn trong kho lưu trữ phiên làm việc.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/refresh`
- **Body Input**:
  ```json
  {
    "refresh_token": "def502005a76c8e3_expired_after_thirty_days_store"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/auth/refresh`.
2. Đính kèm `refresh_token` đã hết hạn.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `401 Unauthorized`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 401,
    "error_code": "AUTH_INVALID_REFRESH_TOKEN",
    "message": "Mã refresh token không hợp lệ hoặc đã hết hạn.",
    "details": null,
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthRefresh_TC007: Mã refresh_token đã bị thu hồi do đăng xuất hoặc cơ chế Token Rotation

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Refresh token đã được sử dụng một lần trước đó (đã bị vô hiệu hóa bởi cơ chế Refresh Token Rotation) hoặc người dùng đã bấm Đăng xuất (`revoked = true`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/refresh`
- **Body Input**:
  ```json
  {
    "refresh_token": "def502005a76c8e3_previously_used_rotated_token"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/auth/refresh`.
2. Gửi chuỗi Refresh Token đã bị thu hồi lên máy chủ.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `401 Unauthorized`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 401,
    "error_code": "AUTH_INVALID_REFRESH_TOKEN",
    "message": "Mã gia hạn không hợp lệ hoặc đã bị thu hồi.",
    "details": null,
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthRefresh_TC008: Refresh Token hợp lệ nhưng tài khoản người dùng tương ứng đã bị xóa khỏi CSDL

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Refresh token tồn tại trong bảng phiên nhưng `user_id` gắn với token không còn tồn tại trong bảng `users` (`User.findById(userId) == null`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/refresh`
- **Body Input**:
  ```json
  {
    "refresh_token": "def502005a76c8e3_associated_with_deleted_user"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/auth/refresh`.
2. Đính kèm Refresh Token liên kết với người dùng đã bị xóa.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `401 Unauthorized`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 401,
    "error_code": "AUTH_INVALID_REFRESH_TOKEN",
    "message": "Tài khoản liên kết với mã gia hạn không còn tồn tại trong hệ thống.",
    "details": null,
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthRefresh_TC009: Refresh Token hợp lệ nhưng tài khoản người dùng đã bị khóa bởi Quản trị viên

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Refresh token hợp lệ, chưa hết hạn.
- Tài khoản người dùng tương ứng vừa bị chuyển cờ trạng thái `is_active = false`.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/refresh`
- **Body Input**:
  ```json
  {
    "refresh_token": "def502005a76c8e3_associated_with_locked_account"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/auth/refresh`.
2. Đính kèm Refresh Token của tài khoản bị khóa.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `403 Forbidden`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 403,
    "error_code": "AUTH_ACCOUNT_DISABLED",
    "message": "Tài khoản của bạn đã bị vô hiệu hóa. Vui lòng liên hệ Quản trị viên.",
    "details": null,
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthRefresh_TC010: Lỗi máy chủ cơ sở dữ liệu / Redis Session Store khi xử lý gia hạn token

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Dịch vụ Redis Cache lưu trữ phiên làm việc / CSDL backend bị mất kết nối giả lập (Mock Session Store Timeout).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/refresh`
- **Body Input**:
  ```json
  {
    "refresh_token": "def502005a76c8e3_valid_refresh_token_string"
  }
  ```
- **Mock State**: `SessionRedisStore.status = 'DISCONNECTED'`.

#### Các bước thực hiện (Test Steps)

1. Thiết lập trạng thái gián đoạn kết nối Redis Session Store trên mock backend.
2. Gửi Request `POST /api/v1/auth/refresh` với Refresh Token hợp lệ.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `500 Internal Server Error`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 500,
    "error_code": "INTERNAL_SERVER_ERROR",
    "message": "Đã xảy ra lỗi máy chủ nội bộ. Vui lòng thử lại sau.",
    "details": null,
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthRefresh_TC011: Gia hạn Access Token thành công với Refresh Token của Giảng viên (INSTRUCTOR)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Refresh token hợp lệ, còn hạn của Giảng viên `teacher_hung` (`is_active = true`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/refresh`
- **Body Input**:
  ```json
  {
    "refresh_token": "def502005a76c8e3_valid_instructor_refresh_token"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/auth/refresh`.
2. Đính kèm `refresh_token` hợp lệ của tài khoản Giảng viên.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": true,
    "status_code": 200,
    "message": "Gia hạn mã truy cập thành công",
    "data": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJ0ZWFjaGVyX2h1bmciLCJyb2xlIjoiSU5TVFJVQ1RPUiIsImV4cCI6MTgwMDAwMDAwMH0.MOCK_NEW_INSTRUCTOR_SIGNATURE",
      "refresh_token": "def502005a76c8e4_new_rotated_instructor_refresh_token",
      "token_type": "Bearer",
      "expires_in": 86400
    },
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT01_AuthRefresh_TC012: Gia hạn Access Token thành công với Refresh Token của Quản trị viên (ADMIN)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Refresh token hợp lệ, còn hạn của Quản trị viên `admin` (`is_active = true`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/auth/refresh`
- **Body Input**:
  ```json
  {
    "refresh_token": "def502005a76c8e3_valid_admin_refresh_token"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/auth/refresh`.
2. Đính kèm `refresh_token` hợp lệ của tài khoản Quản trị viên.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": true,
    "status_code": 200,
    "message": "Gia hạn mã truy cập thành công",
    "data": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MiwidXNlcm5hbWUiOiJhZG1pbiIsInJvbGUiOiJBRE1JTiIsImV4cCI6MTgwMDAwMDAwMH0.MOCK_NEW_ADMIN_SIGNATURE",
      "refresh_token": "def502005a76c8e4_new_rotated_admin_refresh_token",
      "token_type": "Bearer",
      "expires_in": 86400
    },
    "timestamp": "2026-10-05T07:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |
