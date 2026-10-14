# Thông Tin Chung Kiểm Thử Unit Test

- **Phân hệ kiểm thử**: Phân hệ Báo Cáo & Kiểm Toán Hệ Thống (Audit & Reports API - UC-05)
- **Danh sách API kiểm thử**:
  - `GET /api/v1/admin/reports/overview` (UC-05: Thống kê số liệu người dùng, môn học và kiểm toán tiêu thụ token AI toàn trường)
- **Người thực hiện (Tester/Dev)**: Kim Chi Ha
- **Ngày tạo**: 05/10/2026
- **Cập nhật lần cuối**: 05/10/2026 - 08:00
- **Tài liệu liên quan**:
  - [Đặc tả API Phân hệ Báo cáo &amp; Kiểm toán (Markdown)](file:///c:/AITA/iata_project/docs/apis/reports/reports-api.md)
  - [Đặc tả OpenAPI Phân hệ Báo cáo &amp; Kiểm toán (YAML)](file:///c:/AITA/iata_project/docs/apis/reports/reports.yaml)
  - [Đặc tả API Toàn hệ thống AITA](file:///c:/AITA/iata_project/docs/apis/api-specification.md)
  - [Bảng Danh mục Mã lỗi Phản hồi Hệ thống](file:///c:/AITA/iata_project/docs/architecture/api-response-codes.md)
  - [Quy tắc kiểm thử Testcase](file:///c:/AITA/iata_project/rules/testcase-rules.md)
- **Tổng số Testcase**: 18 Testcases (Phân loại: 03 Normal, 11 Abnormal, 04 Binary; 100% có bước truyền Token xác thực; Không có role học sinh)
  - `GET /api/v1/admin/reports/overview`: 18 Testcases (03 Normal, 11 Abnormal, 04 Binary)

---

# ==============================================================================

# PHẦN 1: API GET /api/v1/admin/reports/overview (UC-05: THỐNG KÊ BÁO CÁO TỔNG QUAN HỆ THỐNG)

# ==============================================================================

# UT04_ReportsOverview_TC001: Người gọi chưa đăng nhập (Không cung cấp Token xác thực)

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server Backend (AuditLogs Module) đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/reports/overview`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Khách vãng lai chưa đăng nhập (Token = `None`).
- **Dữ liệu tham số đầu vào (Input Parameters)**:
  ```json
  {}
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/reports/overview`.
2. Không truyền Token xác thực (bỏ trống Header `Authorization`).
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
    "timestamp": "2026-10-05T08:00:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsOverview_TC002: Người gọi gửi Token có giá trị rỗng

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server Backend đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/reports/overview`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Token mang giá trị rỗng (`Token = ""`).
- **Dữ liệu tham số đầu vào (Input Parameters)**:
  ```json
  {}
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/reports/overview`.
2. Truyền Token rỗng vào Header `Authorization: Bearer `.
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
    "timestamp": "2026-10-05T08:00:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsOverview_TC003: Người gọi gửi phương thức xác thực sai Scheme (Dùng Basic thay vì Bearer)

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server Backend đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/reports/overview`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Định dạng Basic Auth `Basic YWRtaW46UGFzc3dvcmRAMTIz` (Sai scheme xác thực).
- **Dữ liệu tham số đầu vào (Input Parameters)**:
  ```json
  {}
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/reports/overview`.
2. Truyền Header `Authorization` sai định dạng Scheme (không có tiền tố Bearer, ví dụ `Basic ...`).
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
    "timestamp": "2026-10-05T08:00:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsOverview_TC004: Người gọi gửi Token JWT có chữ ký sai hoặc bị can thiệp

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server Backend đang hoạt động bình thường với khóa bí mật nội bộ.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/reports/overview`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Token giả mạo có chữ ký không khớp `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.tampered_payload.fake_signature`.
- **Dữ liệu tham số đầu vào (Input Parameters)**:
  ```json
  {}
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/reports/overview`.
2. Truyền Token bị sai chữ ký bảo mật vào Header `Authorization: Bearer <INVALID_SIGNATURE_TOKEN>`.
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
    "timestamp": "2026-10-05T08:00:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsOverview_TC005: Người gọi gửi Token đã hết hạn sử dụng (Expired Token)

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Token của Quản trị viên đã quá hạn hiệu lực (`exp = 1577836800`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/reports/overview`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Token đã hết hạn trong quá khứ.
- **Dữ liệu tham số đầu vào (Input Parameters)**:
  ```json
  {}
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/reports/overview`.
2. Truyền Token đã hết hạn sử dụng vào Header `Authorization: Bearer <EXPIRED_TOKEN>`.
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
    "timestamp": "2026-10-05T08:00:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsOverview_TC006: Token hợp lệ nhưng tài khoản Quản trị viên đã bị xóa khỏi CSDL

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Token hợp lệ mang `id: 888`, nhưng bản ghi `id: 888` đã bị xóa hoàn toàn khỏi bảng `users`.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/reports/overview`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Token của người dùng không còn tồn tại trong CSDL (`User.findById(888) == null`).
- **Dữ liệu tham số đầu vào (Input Parameters)**:
  ```json
  {}
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/reports/overview`.
2. Truyền Token của tài khoản đã bị xóa khỏi CSDL vào Header `Authorization: Bearer <DELETED_USER_TOKEN>`.
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
    "timestamp": "2026-10-05T08:00:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsOverview_TC007: Người gọi là Giảng viên (INSTRUCTOR) không có quyền xem báo cáo

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Tài khoản đang đăng nhập có vai trò `role = "INSTRUCTOR"` (`teacher_hung`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/reports/overview`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Giảng viên hợp lệ (`id: 1, role: "INSTRUCTOR"`).
- **Dữ liệu tham số đầu vào (Input Parameters)**:
  ```json
  {}
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/reports/overview`.
2. Truyền Token xác thực của tài khoản Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `403 Forbidden`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 403,
    "error_code": "FORBIDDEN_ADMIN_ONLY",
    "message": "Chỉ Quản trị viên mới có quyền xem báo cáo thống kê này.",
    "details": null,
    "timestamp": "2026-10-05T08:00:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsOverview_TC008: Người gọi mang vai trò không hợp lệ trong hệ thống (INVALID_ROLE) không có quyền xem báo cáo

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Tài khoản đang đăng nhập mang vai trò không hợp lệ `role = "INVALID_ROLE"`.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/reports/overview`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Người dùng có vai trò không hợp lệ (`id: 101, role: "INVALID_ROLE"`).
- **Dữ liệu tham số đầu vào (Input Parameters)**:
  ```json
  {}
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/reports/overview`.
2. Truyền Token của tài khoản có vai trò không hợp lệ vào Header `Authorization: Bearer <INVALID_ROLE_TOKEN>`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `403 Forbidden`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 403,
    "error_code": "FORBIDDEN_ADMIN_ONLY",
    "message": "Chỉ Quản trị viên mới có quyền xem báo cáo thống kê này.",
    "details": null,
    "timestamp": "2026-10-05T08:00:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsOverview_TC009: Tài khoản Quản trị viên trong Token đã bị vô hiệu hóa

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Quản trị viên có `role = "ADMIN"` nhưng cờ `is_active` đã bị đổi thành `false`.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/reports/overview`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên bị khóa (`id: 2, role: "ADMIN", is_active: false`).
- **Dữ liệu tham số đầu vào (Input Parameters)**:
  ```json
  {}
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/reports/overview`.
2. Truyền Token của tài khoản Admin đã bị vô hiệu hóa vào Header `Authorization: Bearer <DISABLED_ADMIN_TOKEN>`.
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
    "timestamp": "2026-10-05T08:00:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsOverview_TC010: Tham số tháng (month) vượt quá khoảng hợp lệ 1 - 12 (month = 13)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`, `is_active = true`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/reports/overview?month=13&year=2026`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Dữ liệu tham số đầu vào (Input Parameters)**:
  ```json
  {
    "month": 13,
    "year": 2026
  }
  ```

  *(Giá trị `month = 13` vi phạm biên trên `maximum: 12`)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/reports/overview?month=13&year=2026`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
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
        "field": "month",
        "issue": "Giá trị tháng (month) phải nằm trong khoảng từ 1 đến 12."
      }
    ],
    "timestamp": "2026-10-05T08:00:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsOverview_TC011: Tham số tháng (month) bằng 0 vi phạm biên dưới (month = 0)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`, `is_active = true`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/reports/overview?month=0&year=2026`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Dữ liệu tham số đầu vào (Input Parameters)**:
  ```json
  {
    "month": 0,
    "year": 2026
  }
  ```

  *(Giá trị `month = 0` vi phạm biên dưới `minimum: 1`)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/reports/overview?month=0&year=2026`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
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
        "field": "month",
        "issue": "Giá trị tháng (month) phải nằm trong khoảng từ 1 đến 12."
      }
    ],
    "timestamp": "2026-10-05T08:00:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsOverview_TC012: Tham số năm (year) nhỏ hơn năm thành lập hệ thống (year = 2023)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/reports/overview?month=10&year=2023`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Dữ liệu tham số đầu vào (Input Parameters)**:
  ```json
  {
    "month": 10,
    "year": 2023
  }
  ```

  *(Giá trị `year = 2023` vi phạm biên dưới `minimum: 2024`)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/reports/overview?month=10&year=2023`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
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
        "field": "year",
        "issue": "Năm báo cáo (year) phải từ năm 2024 trở về sau."
      }
    ],
    "timestamp": "2026-10-05T08:00:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsOverview_TC013: Tham số tính năng (feature) không thuộc danh mục enum cho phép

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/reports/overview?feature=UNKNOWN_AI_MODULE`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Dữ liệu tham số đầu vào (Input Parameters)**:
  ```json
  {
    "feature": "UNKNOWN_AI_MODULE"
  }
  ```

  *(Giá trị không nằm trong enum: `[ALL, TESTCASE_GEN, CODE_REVIEW, VERIFY_PLAGIARISM, EVALUATE_WEB_UI]`)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/reports/overview?feature=UNKNOWN_AI_MODULE`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
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
        "field": "feature",
        "issue": "Tính năng AI phải thuộc một trong các giá trị: ALL, TESTCASE_GEN, CODE_REVIEW, VERIFY_PLAGIARISM, EVALUATE_WEB_UI."
      }
    ],
    "timestamp": "2026-10-05T08:00:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsOverview_TC014: Lỗi máy chủ cơ sở dữ liệu nội bộ khi tổng hợp báo cáo

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Dịch vụ CSDL PostgreSQL quản lý `audit_logs` bị ngắt kết nối giả lập (Mock DB Disconnection).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/reports/overview`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Dữ liệu tham số đầu vào (Input Parameters)**:
  ```json
  {
    "month": 10,
    "year": 2026
  }
  ```
- **Mock State**: `DatabaseConnectionPool.status = 'DISCONNECTED'`.

#### Các bước thực hiện (Test Steps)

1. Thiết lập trạng thái gián đoạn kết nối CSDL trên Mock Backend.
2. Khởi tạo HTTP Request `GET /api/v1/admin/reports/overview`.
3. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
4. Gửi Request lên hệ thống.

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
    "timestamp": "2026-10-05T08:00:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsOverview_TC015: Lấy báo cáo mặc định khi hệ thống mới khởi tạo chưa có dữ liệu (Biên 0)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`, `is_active = true`).
- CSDL mới khởi tạo chưa có giảng viên và chưa có lịch sử gọi AI.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/reports/overview`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`id: 1, role: "ADMIN"`).
- **Dữ liệu tham số đầu vào (Input Parameters)**:
  ```json
  {}
  ```

  *(Không truyền tham số: Hệ thống tự động lấy theo tháng và năm hiện tại)*
- **Dữ liệu nguồn CSDL giả lập (Database Seed Input)**:
  - Bảng `users`: `[{ "id": 1, "username": "admin", "role": "ADMIN", "is_active": true }]` (0 giảng viên).
  - Bảng `ai_quota_logs`: `[]` (0 giao dịch AI).
  - Ngân sách tháng mặc định: `5,000,000` tokens.

#### Các bước thực hiện (Test Steps)

1. Nạp bộ dữ liệu CSDL rỗng ở trên vào Mock Database.
2. Khởi tạo HTTP Request `GET /api/v1/admin/reports/overview`.
3. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": true,
    "status_code": 200,
    "message": "Lấy số liệu thống kê tổng quan thành công",
    "data": {
      "total_instructors": 0,
      "ai_token_usage": {
        "total_tokens_consumed_month": 0,
        "total_budget_limit": 5000000,
        "top_consuming_feature": null
      }
    },
    "timestamp": "2026-10-05T08:00:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsOverview_TC016: Lấy báo cáo mặc định khi hệ thống đang vận hành bình thường

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`, `is_active = true`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/reports/overview`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`id: 1, role: "ADMIN"`).
- **Dữ liệu tham số đầu vào (Input Parameters)**:
  ```json
  {}
  ```

  *(Mặc định tháng hiện tại 10/2026, toàn bộ tính năng)*
- **Dữ liệu nguồn CSDL giả lập (Database Seed Input)**:
  - Bảng `users`: 24 tài khoản giảng viên `is_active = true` (id: 10..33) và 1 tài khoản bị khóa `is_active = false`.
  - Bảng `ai_quota_logs` (tháng 10/2026):
    - `TESTCASE_GEN`: `750,000` tokens (150 lượt gọi)
    - `CODE_REVIEW`: `320,000` tokens (80 lượt gọi)
    - `VERIFY_PLAGIARISM`: `150,000` tokens (45 lượt gọi)
    - `EVALUATE_WEB_UI`: `65,000` tokens (15 lượt gọi)
    - Tổng cộng: `1,285,000` tokens.
  - Ngân sách tháng: `5,000,000` tokens.

#### Các bước thực hiện (Test Steps)

1. Nạp bộ dữ liệu CSDL ở trên vào Mock Database.
2. Khởi tạo HTTP Request `GET /api/v1/admin/reports/overview`.
3. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": true,
    "status_code": 200,
    "message": "Lấy số liệu thống kê tổng quan thành công",
    "data": {
      "total_instructors": 24,
      "ai_token_usage": {
        "total_tokens_consumed_month": 1285000,
        "total_budget_limit": 5000000,
        "top_consuming_feature": "TESTCASE_GEN"
      }
    },
    "timestamp": "2026-10-05T08:00:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsOverview_TC017: Lấy báo cáo có tham số lọc theo tháng và năm chỉ định (month = 9, year = 2026)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/reports/overview?month=9&year=2026`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Dữ liệu tham số đầu vào (Input Parameters)**:
  ```json
  {
    "month": 9,
    "year": 2026
  }
  ```
- **Dữ liệu nguồn CSDL giả lập (Database Seed Input)**:
  - Bảng `ai_quota_logs` (tháng 9/2026):
    - `TESTCASE_GEN`: `850,000` tokens
    - `CODE_REVIEW`: `150,000` tokens
    - Tổng tháng 9: `1,000,000` tokens.
  - Bảng `ai_quota_logs` (tháng 10/2026): `1,285,000` tokens (Backend phải lọc bỏ qua dữ liệu tháng 10).

#### Các bước thực hiện (Test Steps)

1. Nạp dữ liệu đa tháng vào CSDL Mock.
2. Khởi tạo HTTP Request `GET /api/v1/admin/reports/overview?month=9&year=2026`.
3. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": true,
    "status_code": 200,
    "message": "Lấy số liệu thống kê tổng quan thành công",
    "data": {
      "total_instructors": 24,
      "ai_token_usage": {
        "total_tokens_consumed_month": 1000000,
        "total_budget_limit": 5000000,
        "top_consuming_feature": "TESTCASE_GEN"
      }
    },
    "timestamp": "2026-10-05T08:00:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT04_ReportsOverview_TC018: Lấy báo cáo có tham số lọc theo tính năng AI cụ thể (feature = CODE_REVIEW)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/reports/overview?feature=CODE_REVIEW`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Dữ liệu tham số đầu vào (Input Parameters)**:
  ```json
  {
    "feature": "CODE_REVIEW"
  }
  ```
- **Dữ liệu nguồn CSDL giả lập (Database Seed Input)**:
  - Bảng `ai_quota_logs` (tháng 10/2026):
    - `TESTCASE_GEN`: `750,000` tokens
    - `CODE_REVIEW`: `320,000` tokens
    - `VERIFY_PLAGIARISM`: `150,000` tokens
      *(Backend lọc chỉ tính riêng tính năng `CODE_REVIEW` -> tổng token tiêu thụ là `320,000` tokens)*

#### Các bước thực hiện (Test Steps)

1. Nạp dữ liệu các tính năng AI vào Mock Database.
2. Khởi tạo HTTP Request `GET /api/v1/admin/reports/overview?feature=CODE_REVIEW`.
3. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": true,
    "status_code": 200,
    "message": "Lấy số liệu thống kê tổng quan thành công",
    "data": {
      "total_instructors": 24,
      "ai_token_usage": {
        "total_tokens_consumed_month": 320000,
        "total_budget_limit": 5000000,
        "top_consuming_feature": "CODE_REVIEW"
      }
    },
    "timestamp": "2026-10-05T08:00:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |
