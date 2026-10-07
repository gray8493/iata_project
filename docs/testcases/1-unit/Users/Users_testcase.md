# Thông Tin Chung Kiểm Thử Unit Test

- **Phân hệ kiểm thử**: Phân hệ Quản Lý Người Dùng & Phân Quyền (Users Management API - Admin Only)
- **Danh sách API kiểm thử**:
  - `GET /api/v1/admin/users` (UC-03 / UC-Admin: Lấy danh sách tài khoản kèm phân trang và tìm kiếm)
  - `POST /api/v1/admin/users` (UC-04 / UC-Admin: Tạo mới tài khoản Giảng viên hoặc Quản trị viên)
  - `GET /api/v1/admin/users/{id}` (UC-Admin: Xem chi tiết thông tin hồ sơ tài khoản theo ID)
  - `PUT /api/v1/admin/users/{id}` (UC-Admin: Cập nhật thông tin hồ sơ / Khóa hoặc mở khóa tài khoản)
  - `DELETE /api/v1/admin/users/{id}` (UC-Admin: Xóa tài khoản người dùng khỏi hệ thống)
- **Người thực hiện (Tester/Dev)**: Kim Chi Ha
- **Ngày tạo**: 05/10/2026
- **Cập nhật lần cuối**: 05/10/2026 - 08:30
- **Tài liệu liên quan**:
  - [Đặc tả API Phân hệ Người dùng (Markdown)](file:///c:/AITA/iata_project/docs/apis/users/users-api.md)
  - [Đặc tả OpenAPI Phân hệ Người dùng (YAML)](file:///c:/AITA/iata_project/docs/apis/users/users.yaml)
  - [Đặc tả API Toàn hệ thống AITA](file:///c:/AITA/iata_project/docs/apis/api-specification.md)
  - [Bảng Danh mục Mã lỗi Phản hồi Hệ thống](file:///c:/AITA/iata_project/docs/architecture/api-response-codes.md)
  - [Quy tắc kiểm thử Testcase](file:///c:/AITA/iata_project/rules/testcase-rules.md)
- **Tổng số Testcase**: 61 Testcases (Phân loại: 11 Normal, 30 Abnormal, 20 Binary; 100% có bước truyền Token xác thực; Tuyệt đối không có role học sinh)
  - `GET /api/v1/admin/users`: 13 Testcases (04 Normal, 07 Abnormal, 02 Binary)
  - `POST /api/v1/admin/users`: 21 Testcases (04 Normal, 09 Abnormal, 08 Binary)
  - `GET /api/v1/admin/users/{id}`: 07 Testcases (02 Normal, 04 Abnormal, 01 Binary)
  - `PUT /api/v1/admin/users/{id}`: 13 Testcases (03 Normal, 06 Abnormal, 04 Binary)
  - `DELETE /api/v1/admin/users/{id}`: 07 Testcases (01 Normal, 04 Abnormal, 02 Binary)

---

# ==============================================================================

# PHẦN 1: API GET /api/v1/admin/users (LẤY DANH SÁCH TÀI KHOẢN KÈM PHÂN TRANG)

# ==============================================================================

# UT02_UsersList_TC001: Người gọi chưa đăng nhập (Không có Token xác thực)

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server Backend (Users Module) đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/users`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Khách vãng lai chưa đăng nhập (Token = `None`).
- **Tham số đầu vào (Input Parameters)**:
  ```json
  {}
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/users`.
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
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersList_TC002: Người gọi gửi Token đã hết hạn sử dụng

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Token của Quản trị viên đã quá hạn hiệu lực (`exp` trong quá khứ).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/users`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Token đã hết hạn (`exp = 1577836800`).
- **Tham số đầu vào (Input Parameters)**:
  ```json
  {}
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/users`.
2. Đính kèm Token đã hết hạn.
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
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersList_TC003: Người gọi là Giảng viên (INSTRUCTOR) không có quyền xem danh sách quản trị

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Người dùng đã đăng nhập với tài khoản có `role = "INSTRUCTOR"`.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/users`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Giảng viên hợp lệ (`id: 2, role: "INSTRUCTOR"`).
- **Tham số đầu vào (Input Parameters)**:
  ```json
  {}
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/users`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `403 Forbidden`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 403,
    "error_code": "FORBIDDEN_ADMIN_ONLY",
    "message": "Bạn không có quyền truy cập vào chức năng quản trị này.",
    "details": null,
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersList_TC004: Tài khoản Quản trị viên trong Token đã bị vô hiệu hóa

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Quản trị viên có `role = "ADMIN"` nhưng cờ `is_active = false`.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/users`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên bị khóa (`id: 3, role: "ADMIN", is_active: false`).
- **Tham số đầu vào (Input Parameters)**:
  ```json
  {}
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/users`.
2. Đính kèm Token của tài khoản Admin bị vô hiệu hóa.
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
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersList_TC005: Tham số page nhỏ hơn 1 vi phạm biên dưới (page = 0)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`, `is_active = true`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/users?page=0&page_size=10`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Tham số đầu vào (Input Parameters)**:
  ```json
  {
    "page": 0,
    "page_size": 10
  }
  ```

  *(Giá trị `page = 0` vi phạm ràng buộc `minimum: 1`)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/users?page=0&page_size=10`.
2. Gửi request với Token Admin hợp lệ.

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
        "field": "page",
        "issue": "Số trang (page) phải là số nguyên dương lớn hơn hoặc bằng 1."
      }
    ],
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersList_TC006: Tham số page_size vượt quá 100 vi phạm biên trên (page_size = 101)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`, `is_active = true`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/users?page=1&page_size=101`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Tham số đầu vào (Input Parameters)**:
  ```json
  {
    "page": 1,
    "page_size": 101
  }
  ```

  *(Giá trị `page_size = 101` vi phạm ràng buộc `maximum: 100`)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/users?page=1&page_size=101`.
2. Gửi request với Token Admin hợp lệ.

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
        "field": "page_size",
        "issue": "Kích thước trang (page_size) không được vượt quá 100 phần tử."
      }
    ],
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersList_TC007: Tham số role không thuộc danh mục phân quyền hợp lệ

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/users?role=SUPERADMIN`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Tham số đầu vào (Input Parameters)**:
  ```json
  {
    "role": "SUPERADMIN"
  }
  ```

  *(Giá trị không thuộc enum `[ADMIN, INSTRUCTOR]`)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/users?role=SUPERADMIN`.
2. Gửi request kèm Token Admin hợp lệ.

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
        "field": "role",
        "issue": "Vai trò người dùng phải thuộc một trong các giá trị: ADMIN, INSTRUCTOR."
      }
    ],
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersList_TC008: Từ khóa tìm kiếm search vượt quá 50 ký tự (search = 51 ký tự)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/users?search=this_is_an_extremely_long_search_query_over_fifty_51`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Tham số đầu vào (Input Parameters)**:
  ```json
  {
    "search": "this_is_an_extremely_long_search_query_over_fifty_51"
  }
  ```

  *(Chuỗi có đúng 51 ký tự, vượt quá giới hạn 50 ký tự)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/users?search=...`.
2. Gửi request kèm Token Admin hợp lệ.

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
        "field": "search",
        "issue": "Từ khóa tìm kiếm không được vượt quá 50 ký tự."
      }
    ],
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersList_TC009: Lỗi máy chủ cơ sở dữ liệu khi truy vấn danh sách người dùng

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- CSDL PostgreSQL quản lý bảng `users` bị ngắt kết nối giả lập (Mock DB Connection Error).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/users?page=1&page_size=10`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Tham số đầu vào (Input Parameters)**:
  ```json
  {
    "page": 1,
    "page_size": 10
  }
  ```
- **Mock State**: `DatabaseConnectionPool.status = 'DISCONNECTED'`.

#### Các bước thực hiện (Test Steps)

1. Thiết lập trạng thái gián đoạn kết nối CSDL trên Mock Backend.
2. Khởi tạo HTTP Request `GET /api/v1/admin/users?page=1&page_size=10`.
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
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersList_TC010: Lấy danh sách thành công khi bảng người dùng rỗng hoặc trang không có dữ liệu (Biên 0)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`, `is_active = true`).
- Truy vấn tới trang vượt quá số trang hiện có (`page = 99`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/users?page=99&page_size=10`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`id: 1, role: "ADMIN"`).
- **Tham số đầu vào (Input Parameters)**:
  ```json
  {
    "page": 99,
    "page_size": 10
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/users?page=99&page_size=10`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Phản hồi JSON chứa mảng `items: []` rỗng:
  ```json
  {
    "success": true,
    "status_code": 200,
    "message": "Lấy danh sách người dùng thành công",
    "data": {
      "items": [],
      "pagination": {
        "page": 99,
        "page_size": 10,
        "total_items": 2,
        "total_pages": 1
      }
    },
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersList_TC011: Lấy danh sách tài khoản thành công với tham số phân trang mặc định

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).
- Hệ thống đang có 2 tài khoản: 1 Admin và 1 Giảng viên.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/users`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`id: 1, role: "ADMIN"`).
- **Tham số đầu vào (Input Parameters)**:
  ```json
  {}
  ```

  *(Mặc định: page = 1, page_size = 10)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/users`.
2. Đính kèm Token Admin hợp lệ.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": true,
    "status_code": 200,
    "message": "Lấy danh sách người dùng thành công",
    "data": {
      "items": [
        {
          "id": 1,
          "username": "admin",
          "full_name": "Quản Trị Viên Hệ Thống",
          "email": "admin@fe.edu.vn",
          "role": "ADMIN",
          "is_active": true,
          "created_at": "2026-09-01T00:00:00.000Z"
        },
        {
          "id": 2,
          "username": "teacher_hung",
          "full_name": "Nguyễn Văn Hùng",
          "email": "hungnv@fe.edu.vn",
          "role": "INSTRUCTOR",
          "is_active": true,
          "created_at": "2026-09-10T08:30:00.000Z"
        }
      ],
      "pagination": {
        "page": 1,
        "page_size": 10,
        "total_items": 2,
        "total_pages": 1
      }
    },
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersList_TC012: Lấy danh sách thành công kèm bộ lọc vai trò (role = INSTRUCTOR)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/users?role=INSTRUCTOR&page=1&page_size=10`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Tham số đầu vào (Input Parameters)**:
  ```json
  {
    "role": "INSTRUCTOR",
    "page": 1,
    "page_size": 10
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/users?role=INSTRUCTOR&page=1&page_size=10`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Phản hồi JSON chứa danh sách người dùng chỉ gồm các tài khoản có `role = "INSTRUCTOR"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersList_TC013: Tìm kiếm người dùng theo từ khóa search hợp lệ (search = hung)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/users?search=hung`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Tham số đầu vào (Input Parameters)**:
  ```json
  {
    "search": "hung"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/users?search=hung`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Phản hồi JSON chứa tài khoản Giảng viên `teacher_hung` khớp với từ khóa tìm kiếm.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# ==============================================================================

# PHẦN 2: API POST /api/v1/admin/users (TẠO MỚI TÀI KHOẢN GIẢNG VIÊN / QUẢN TRỊ VIÊN)

# ==============================================================================

# UT02_UsersCreate_TC001: Người gọi chưa đăng nhập (Không có Token xác thực)

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server Backend đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/admin/users`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Khách vãng lai chưa đăng nhập (Token = `None`).
- **Body Input**:
  ```json
  {
    "username": "teacher_lan",
    "password": "LanPassword2026@",
    "full_name": "Trần Thị Lan",
    "email": "lantt@fe.edu.vn",
    "role": "INSTRUCTOR"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/admin/users`.
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
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC002: Người gọi là Giảng viên không có quyền tạo tài khoản

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Người dùng đăng nhập có `role = "INSTRUCTOR"`.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/admin/users`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Giảng viên (`id: 2, role: "INSTRUCTOR"`).
- **Body Input**:
  ```json
  {
    "username": "teacher_lan",
    "password": "LanPassword2026@",
    "full_name": "Trần Thị Lan",
    "email": "lantt@fe.edu.vn",
    "role": "INSTRUCTOR"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/admin/users`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `403 Forbidden`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 403,
    "error_code": "FORBIDDEN_ADMIN_ONLY",
    "message": "Bạn không có quyền truy cập vào chức năng quản trị này.",
    "details": null,
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC003: Gửi Request Body không đúng định dạng cú pháp JSON

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/admin/users`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```text
  {"username": "teacher_lan", "password": "LanPassword2026@"
  ```

  *(Chuỗi JSON bị thiếu dấu đóng ngoặc nhọn)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/admin/users`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. `post /api/v1/admin/users` với payload lỗi cú pháp json.
4. Gửi Request lên hệ thống.

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
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC004: Request Body rỗng thiếu toàn bộ các trường bắt buộc

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/admin/users`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```json
  {}
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/admin/users`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. `post /api/v1/admin/users` với body là đối tượng rỗng `{}`.
4. Gửi Request lên hệ thống.

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
      { "field": "username", "issue": "Tên đăng nhập (username) là trường bắt buộc." },
      { "field": "password", "issue": "Mật khẩu (password) là trường bắt buộc." },
      { "field": "full_name", "issue": "Họ và tên (full_name) là trường bắt buộc." },
      { "field": "email", "issue": "Địa chỉ email (email) là trường bắt buộc." },
      { "field": "role", "issue": "Vai trò (role) là trường bắt buộc." }
    ],
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC005: Trường username có độ dài dưới 3 ký tự (username = 2 ký tự)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/admin/users`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```json
  {
    "username": "la",
    "password": "LanPassword2026@",
    "full_name": "Trần Thị Lan",
    "email": "lantt@fe.edu.vn",
    "role": "INSTRUCTOR"
  }
  ```

  *(Chuỗi `"la"` có đúng 2 ký tự, vi phạm `minLength: 3`)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/admin/users`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. `post /api/v1/admin/users` với `username = "la"`.
4. Gửi Request lên hệ thống.

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
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC006: Trường username vượt quá 30 ký tự (username = 31 ký tự)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/admin/users`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```json
  {
    "username": "teacher_lan_thirty_one_chars_31",
    "password": "LanPassword2026@",
    "full_name": "Trần Thị Lan",
    "email": "lantt@fe.edu.vn",
    "role": "INSTRUCTOR"
  }
  ```

  *(Chuỗi có đúng 31 ký tự, vi phạm `maxLength: 30`)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/admin/users`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. `post /api/v1/admin/users` với `username` 31 ký tự.
4. Gửi Request lên hệ thống.

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
        "issue": "Tên đăng nhập không được vượt quá 30 ký tự."
      }
    ],
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC007: Trường username chứa chữ hoa hoặc ký tự đặc biệt vi phạm regex

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/admin/users`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```json
  {
    "username": "Teacher@Lan",
    "password": "LanPassword2026@",
    "full_name": "Trần Thị Lan",
    "email": "lantt@fe.edu.vn",
    "role": "INSTRUCTOR"
  }
  ```

  *(Chứa chữ hoa `'T'`, `'L'` và ký tự `'@'` vi phạm regex `^[a-z0-9_]+$`)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/admin/users`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. `post /api/v1/admin/users` với `username = "teacher@lan"`.
4. Gửi Request lên hệ thống.

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
        "issue": "Tên đăng nhập chỉ được chứa chữ cái thường, số và dấu gạch dưới (^[a-z0-9_]+$)."
      }
    ],
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC008: Trường password dưới 8 ký tự vi phạm biên minLength (password = 7 ký tự)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/admin/users`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```json
  {
    "username": "teacher_lan",
    "password": "Pass12@",
    "full_name": "Trần Thị Lan",
    "email": "lantt@fe.edu.vn",
    "role": "INSTRUCTOR"
  }
  ```

  *(Mật khẩu `"Pass12@"` có đúng 7 ký tự, vi phạm `minLength: 8`)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/admin/users`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. `post /api/v1/admin/users` với mật khẩu 7 ký tự.
4. Gửi Request lên hệ thống.

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
        "issue": "Mật khẩu phải có độ dài tối thiểu 8 ký tự."
      }
    ],
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC009: Trường password không đủ độ phức tạp (Thiếu chữ hoa và số)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/admin/users`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```json
  {
    "username": "teacher_lan",
    "password": "passwordonly",
    "full_name": "Trần Thị Lan",
    "email": "lantt@fe.edu.vn",
    "role": "INSTRUCTOR"
  }
  ```

  *(Chuỗi 12 ký tự nhưng chỉ chứa chữ thường, thiếu chữ hoa và số)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/admin/users`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. `post /api/v1/admin/users` với mật khẩu yếu.
4. Gửi Request lên hệ thống.

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
        "issue": "Mật khẩu phải chứa ít nhất 1 chữ cái in hoa, 1 chữ cái thường và 1 chữ số."
      }
    ],
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC010: Trường full_name dưới 2 ký tự (full_name = 1 ký tự)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/admin/users`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```json
  {
    "username": "teacher_lan",
    "password": "LanPassword2026@",
    "full_name": "L",
    "email": "lantt@fe.edu.vn",
    "role": "INSTRUCTOR"
  }
  ```

  *(Chuỗi `"L"` có 1 ký tự, vi phạm `minLength: 2`)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/admin/users`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. `post /api/v1/admin/users` với `full_name = "l"`.
4. Gửi Request lên hệ thống.

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
        "field": "full_name",
        "issue": "Họ và tên phải có độ dài từ 2 đến 100 ký tự."
      }
    ],
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC011: Trường email sai định dạng cú pháp RFC 5322

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/admin/users`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```json
  {
    "username": "teacher_lan",
    "password": "LanPassword2026@",
    "full_name": "Trần Thị Lan",
    "email": "invalid-email-syntax-without-at",
    "role": "INSTRUCTOR"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/admin/users`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. `post /api/v1/admin/users` với email sai định dạng.
4. Gửi Request lên hệ thống.

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
        "field": "email",
        "issue": "Địa chỉ email không đúng định dạng tiêu chuẩn (RFC 5322)."
      }
    ],
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC012: Trường role sai giá trị ngoài danh mục enum cho phép

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/admin/users`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```json
  {
    "username": "teacher_lan",
    "password": "LanPassword2026@",
    "full_name": "Trần Thị Lan",
    "email": "lantt@fe.edu.vn",
    "role": "GUEST"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/admin/users`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. Đính kèm Body chứa `role = "GUEST"`.
4. Gửi Request lên hệ thống.

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
        "field": "role",
        "issue": "Vai trò tài khoản chỉ có thể là ADMIN hoặc INSTRUCTOR."
      }
    ],
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC013: Trường daily_token_quota nhỏ hơn 1,000 (quota = 500)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/admin/users`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```json
  {
    "username": "teacher_lan",
    "password": "LanPassword2026@",
    "full_name": "Trần Thị Lan",
    "email": "lantt@fe.edu.vn",
    "role": "INSTRUCTOR",
    "daily_token_quota": 500
  }
  ```

  *(Giá trị `500` vi phạm biên dưới `minimum: 1000`)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/admin/users`.
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
        "field": "daily_token_quota",
        "issue": "Hạn ngạch token hàng ngày phải tối thiểu là 1,000 tokens."
      }
    ],
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC014: Trường daily_token_quota vượt quá 1,000,000 (quota = 1,500,000)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/admin/users`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```json
  {
    "username": "teacher_lan",
    "password": "LanPassword2026@",
    "full_name": "Trần Thị Lan",
    "email": "lantt@fe.edu.vn",
    "role": "INSTRUCTOR",
    "daily_token_quota": 1500000
  }
  ```

  *(Giá trị `1,500,000` vi phạm biên trên `maximum: 1000000`)*

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/admin/users`.
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
        "field": "daily_token_quota",
        "issue": "Hạn ngạch token hàng ngày không được vượt quá 1,000,000 tokens."
      }
    ],
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC015: Trùng lặp tên đăng nhập username đã tồn tại trong CSDL

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Tên đăng nhập `"teacher_hung"` đã tồn tại trong CSDL.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/admin/users`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```json
  {
    "username": "teacher_hung",
    "password": "NewPassword2026@",
    "full_name": "Nguyễn Văn Hùng Mới",
    "email": "hungnew@fe.edu.vn",
    "role": "INSTRUCTOR"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/admin/users`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. `post /api/v1/admin/users` với `username = "teacher_hung"` đã có sẵn.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `409 Conflict`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 409,
    "error_code": "USER_ALREADY_EXISTS",
    "message": "Tên đăng nhập hoặc địa chỉ email đã được sử dụng.",
    "details": [
      {
        "field": "username",
        "issue": "Tên đăng nhập 'teacher_hung' đã tồn tại trong hệ thống."
      }
    ],
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC016: Trùng lặp địa chỉ email đã tồn tại trong CSDL

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Địa chỉ email `"hungnv@fe.edu.vn"` đã được sử dụng bởi tài khoản khác trong CSDL.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/admin/users`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```json
  {
    "username": "teacher_lan",
    "password": "LanPassword2026@",
    "full_name": "Trần Thị Lan",
    "email": "hungnv@fe.edu.vn",
    "role": "INSTRUCTOR"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/admin/users`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. `post /api/v1/admin/users` với email đã tồn tại trong hệ thống.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `409 Conflict`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 409,
    "error_code": "USER_ALREADY_EXISTS",
    "message": "Tên đăng nhập hoặc địa chỉ email đã được sử dụng.",
    "details": [
      {
        "field": "email",
        "issue": "Địa chỉ email 'hungnv@fe.edu.vn' đã được sử dụng."
      }
    ],
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC017: Lỗi máy chủ cơ sở dữ liệu khi thực hiện tạo người dùng mới

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- CSDL PostgreSQL bị ngắt kết nối giả lập (Mock DB Error).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/admin/users`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```json
  {
    "username": "teacher_lan",
    "password": "LanPassword2026@",
    "full_name": "Trần Thị Lan",
    "email": "lantt@fe.edu.vn",
    "role": "INSTRUCTOR"
  }
  ```
- **Mock State**: `DatabaseConnectionPool.status = 'DISCONNECTED'`.

#### Các bước thực hiện (Test Steps)

1. Kích hoạt trạng thái lỗi ngắt kết nối CSDL trên Mock Backend.
2. Khởi tạo HTTP Request `POST /api/v1/admin/users`.
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
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC018: Tạo tài khoản thành công với các trường ở độ dài biên nhỏ nhất

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).
- `username = "lan"` (3 ký tự), `password = "Lan1234@"` (8 ký tự), `full_name = "Le"` (2 ký tự), `daily_token_quota = 1000` (min limit).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/admin/users`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```json
  {
    "username": "lan",
    "password": "Lan1234@",
    "full_name": "Le",
    "email": "le.lan@fe.edu.vn",
    "role": "INSTRUCTOR",
    "daily_token_quota": 1000
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/admin/users`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. `post /api/v1/admin/users` với các trường dữ liệu ở biên dưới nhỏ nhất.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `201 Created`.
- Phản hồi JSON chứa `success = true`, tạo tài khoản thành công với ID mới.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC019: Tạo tài khoản thành công với các trường ở độ dài biên lớn nhất

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).
- `username` đúng 30 ký tự, `full_name` đúng 100 ký tự, `daily_token_quota = 1000000` (max limit).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/admin/users`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```json
  {
    "username": "teacher_lan_exact_30_character",
    "password": "LanPassword2026@",
    "full_name": "Trần Thị Lan Nguyễn Hoàng Kim Cương Long Lanh Lấp Lánh Ánh Bình Minh Tỏa Sáng Khắp Muôn Nơi Miền Đất Nước",
    "email": "lan.maxlength@fe.edu.vn",
    "role": "INSTRUCTOR",
    "daily_token_quota": 1000000
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/admin/users`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. `post /api/v1/admin/users` với các trường dữ liệu ở biên trên lớn nhất.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `201 Created`.
- Phản hồi JSON chứa `success = true`, tạo tài khoản thành công.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC020: Tạo mới thành công tài khoản Giảng viên (INSTRUCTOR)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).
- Username `"teacher_lan"` và email `"lantt@fe.edu.vn"` chưa tồn tại trong hệ thống.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/admin/users`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```json
  {
    "username": "teacher_lan",
    "password": "LanPassword2026@",
    "full_name": "Trần Thị Lan",
    "email": "lantt@fe.edu.vn",
    "role": "INSTRUCTOR",
    "daily_token_quota": 60000
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/admin/users` với payload hợp lệ ở trên.
2. Gửi request kèm Token Admin hợp lệ.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `201 Created`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": true,
    "status_code": 201,
    "message": "Tạo tài khoản người dùng mới thành công",
    "data": {
      "id": 3,
      "username": "teacher_lan",
      "full_name": "Trần Thị Lan",
      "email": "lantt@fe.edu.vn",
      "role": "INSTRUCTOR",
      "is_active": true,
      "created_at": "2026-10-05T08:30:00.000Z"
    },
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersCreate_TC021: Tạo mới thành công tài khoản Quản trị viên phụ (ADMIN)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `POST /api/v1/admin/users`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```json
  {
    "username": "admin_sub",
    "password": "SubAdminPassword2026@",
    "full_name": "Lê Văn Quản Trị",
    "email": "admin_sub@fe.edu.vn",
    "role": "ADMIN",
    "daily_token_quota": 100000
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `POST /api/v1/admin/users`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. `post /api/v1/admin/users` để tạo tài khoản quản trị viên phụ.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `201 Created`.
- Phản hồi JSON chứa `success = true`, tài khoản mới có `role = "ADMIN"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# ==============================================================================

# PHẦN 3: API GET /api/v1/admin/users/ (XEM CHI TIẾT TÀI KHOẢN THEO ID)

# ==============================================================================

# UT02_UsersGetDetail_TC001: Người gọi chưa đăng nhập (Không có Token xác thực)

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server Backend đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/users/2`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Khách vãng lai chưa đăng nhập (Token = `None`).
- **Tham số đầu vào (Input Parameters)**:
  ```json
  {
    "id": 2
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/users/2`.
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
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersGetDetail_TC002: Người gọi là Giảng viên không có quyền xem chi tiết người dùng

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Người dùng đăng nhập có `role = "INSTRUCTOR"`.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/users/1`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Giảng viên (`id: 2, role: "INSTRUCTOR"`).
- **Tham số đầu vào (Input Parameters)**:
  ```json
  {
    "id": 1
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/users/1`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `403 Forbidden`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 403,
    "error_code": "FORBIDDEN_ADMIN_ONLY",
    "message": "Bạn không có quyền truy cập vào chức năng quản trị này.",
    "details": null,
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersGetDetail_TC003: Tham số id trên đường dẫn không phải số nguyên dương (id = 0 hoặc chuỗi)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/users/abc`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Tham số đầu vào (Input Parameters)**:
  ```json
  {
    "id": "abc"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/users/abc`.
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
        "field": "id",
        "issue": "Mã ID người dùng phải là một số nguyên dương hợp lệ."
      }
    ],
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersGetDetail_TC004: Không tìm thấy người dùng với mã ID đã chỉ định (id = 9999)

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Trong CSDL không tồn tại bản ghi người dùng có `id = 9999`.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/users/9999`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Tham số đầu vào (Input Parameters)**:
  ```json
  {
    "id": 9999
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/users/9999`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `404 Not Found`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 404,
    "error_code": "USER_NOT_FOUND",
    "message": "Không tìm thấy người dùng với mã ID đã chỉ định.",
    "details": null,
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersGetDetail_TC005: Lỗi máy chủ cơ sở dữ liệu khi truy vấn chi tiết tài khoản

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- CSDL PostgreSQL bị ngắt kết nối giả lập (Mock DB Connection Error).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/users/2`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Tham số đầu vào (Input Parameters)**:
  ```json
  {
    "id": 2
  }
  ```
- **Mock State**: `DatabaseConnectionPool.status = 'DISCONNECTED'`.

#### Các bước thực hiện (Test Steps)

1. Kích hoạt trạng thái lỗi ngắt kết nối CSDL trên Mock Backend.
2. Khởi tạo HTTP Request `GET /api/v1/admin/users/2`.
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
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersGetDetail_TC006: Xem chi tiết thành công thông tin hồ sơ tài khoản Giảng viên

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Giảng viên `id = 2` (`teacher_hung`) đang tồn tại trong hệ thống.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/users/2`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Tham số đầu vào (Input Parameters)**:
  ```json
  {
    "id": 2
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/users/2`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
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
      "username": "teacher_hung",
      "full_name": "Nguyễn Văn Hùng",
      "email": "hungnv@fe.edu.vn",
      "role": "INSTRUCTOR",
      "is_active": true,
      "daily_token_quota": 50000,
      "created_at": "2026-09-10T08:30:00.000Z"
    },
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersGetDetail_TC007: Xem chi tiết thành công thông tin hồ sơ tài khoản Quản trị viên

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `id = 1` (`admin`) đang tồn tại trong hệ thống.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `GET /api/v1/admin/users/1`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Tham số đầu vào (Input Parameters)**:
  ```json
  {
    "id": 1
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `GET /api/v1/admin/users/1`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Phản hồi JSON chứa thông tin hồ sơ tài khoản Admin với `role = "ADMIN"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# ==============================================================================

# PHẦN 4: API PUT /api/v1/admin/users/ (CẬP NHẬT THÔNG TIN / KHÓA TÀI KHOẢN)

# ==============================================================================

# UT02_UsersUpdate_TC001: Người gọi chưa đăng nhập (Không có Token xác thực)

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server Backend đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `PUT /api/v1/admin/users/2`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Khách vãng lai chưa đăng nhập (Token = `None`).
- **Body Input**:
  ```json
  {
    "full_name": "Nguyễn Văn Hùng (TS)"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `PUT /api/v1/admin/users/2`.
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
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersUpdate_TC002: Người gọi là Giảng viên không có quyền cập nhật người dùng

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Người dùng đăng nhập có `role = "INSTRUCTOR"`.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `PUT /api/v1/admin/users/2`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Giảng viên (`id: 2, role: "INSTRUCTOR"`).
- **Body Input**:
  ```json
  {
    "full_name": "Nguyễn Văn Hùng (TS)"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `PUT /api/v1/admin/users/2`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `403 Forbidden`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 403,
    "error_code": "FORBIDDEN_ADMIN_ONLY",
    "message": "Bạn không có quyền truy cập vào chức năng quản trị này.",
    "details": null,
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersUpdate_TC003: Cập nhật tài khoản không tồn tại trong CSDL (id = 9999)

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Trong CSDL không tồn tại bản ghi người dùng `id = 9999`.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `PUT /api/v1/admin/users/9999`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```json
  {
    "is_active": false
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `PUT /api/v1/admin/users/9999`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `404 Not Found`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 404,
    "error_code": "USER_NOT_FOUND",
    "message": "Không tìm thấy người dùng với mã ID đã chỉ định.",
    "details": null,
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersUpdate_TC004: Quản trị viên tự thực hiện thao tác khóa tài khoản của chính mình

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Quản trị viên đang đăng nhập sở hữu `id = 1`.
- Quản trị viên gửi yêu cầu cập nhật `is_active = false` vào chính endpoint `/api/v1/admin/users/1`.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `PUT /api/v1/admin/users/1`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên đang đăng nhập (`id: 1, role: "ADMIN"`).
- **Body Input**:
  ```json
  {
    "is_active": false
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `PUT /api/v1/admin/users/1` với body `{"is_active": false}`.
2. Đính kèm Token của tài khoản Admin `id = 1`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `400 Bad Request`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 400,
    "error_code": "USER_CANNOT_DISABLE_SELF",
    "message": "Bạn không thể tự khóa tài khoản của chính mình.",
    "details": null,
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersUpdate_TC005: Cập nhật email sai định dạng cú pháp tiêu chuẩn

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `PUT /api/v1/admin/users/2`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```json
  {
    "email": "invalid_email_format"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `PUT /api/v1/admin/users/2`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. `put /api/v1/admin/users/2` với email sai định dạng.
4. Gửi Request lên hệ thống.

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
        "field": "email",
        "issue": "Địa chỉ email không đúng định dạng tiêu chuẩn (RFC 5322)."
      }
    ],
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersUpdate_TC006: Cập nhật vai trò role sai giá trị ngoài ADMIN hoặc INSTRUCTOR

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `PUT /api/v1/admin/users/2`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```json
  {
    "role": "MODERATOR"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `PUT /api/v1/admin/users/2`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. `put /api/v1/admin/users/2` với `role = "moderator"`.
4. Gửi Request lên hệ thống.

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
        "field": "role",
        "issue": "Vai trò tài khoản chỉ có thể là ADMIN hoặc INSTRUCTOR."
      }
    ],
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersUpdate_TC007: Cập nhật daily_token_quota mang giá trị số âm

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `PUT /api/v1/admin/users/2`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```json
  {
    "daily_token_quota": -500
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `PUT /api/v1/admin/users/2`.
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
        "field": "daily_token_quota",
        "issue": "Hạn ngạch token hàng ngày phải là số nguyên lớn hơn hoặc bằng 0."
      }
    ],
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersUpdate_TC008: Cập nhật email bị trùng lặp với tài khoản khác trong hệ thống

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Tài khoản `id = 1` đang dùng email `admin@fe.edu.vn`.
- Cập nhật email của tài khoản `id = 2` thành `admin@fe.edu.vn`.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `PUT /api/v1/admin/users/2`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```json
  {
    "email": "admin@fe.edu.vn"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `PUT /api/v1/admin/users/2`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. `put /api/v1/admin/users/2` với email đã được dùng bởi tài khoản khác.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `409 Conflict`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 409,
    "error_code": "USER_ALREADY_EXISTS",
    "message": "Tên đăng nhập hoặc địa chỉ email đã được sử dụng.",
    "details": [
      {
        "field": "email",
        "issue": "Địa chỉ email 'admin@fe.edu.vn' đã được sử dụng."
      }
    ],
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersUpdate_TC009: Tham số id trên đường dẫn không hợp lệ (id = 0)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `PUT /api/v1/admin/users/0`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```json
  {
    "full_name": "Test Update"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `PUT /api/v1/admin/users/0`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. `put /api/v1/admin/users/0`.
4. Gửi Request lên hệ thống.

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
        "field": "id",
        "issue": "Mã ID người dùng phải là một số nguyên dương hợp lệ."
      }
    ],
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersUpdate_TC010: Lỗi máy chủ cơ sở dữ liệu khi thực hiện cập nhật tài khoản

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- CSDL PostgreSQL bị ngắt kết nối giả lập (Mock DB Connection Error).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `PUT /api/v1/admin/users/2`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```json
  {
    "full_name": "Nguyễn Văn Hùng (TS)"
  }
  ```
- **Mock State**: `DatabaseConnectionPool.status = 'DISCONNECTED'`.

#### Các bước thực hiện (Test Steps)

1. Kích hoạt lỗi ngắt kết nối CSDL trên Mock Backend.
2. Khởi tạo HTTP Request `PUT /api/v1/admin/users/2`.
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
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersUpdate_TC011: Cập nhật thông tin hồ sơ thành công cho Giảng viên

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Tài khoản Giảng viên `id = 2` đang tồn tại và hoạt động trong hệ thống.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `PUT /api/v1/admin/users/2`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```json
  {
    "full_name": "Nguyễn Văn Hùng (Tiến Sĩ)",
    "daily_token_quota": 80000
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `PUT /api/v1/admin/users/2`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": true,
    "status_code": 200,
    "message": "Cập nhật tài khoản thành công",
    "data": {
      "id": 2,
      "username": "teacher_hung",
      "full_name": "Nguyễn Văn Hùng (Tiến Sĩ)",
      "email": "hungnv@fe.edu.vn",
      "role": "INSTRUCTOR",
      "is_active": true,
      "daily_token_quota": 80000,
      "updated_at": "2026-10-05T08:30:00.000Z"
    },
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersUpdate_TC012: Khóa tài khoản Giảng viên thành công (is_active = false)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Tài khoản Giảng viên `id = 2` đang hoạt động (`is_active = true`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `PUT /api/v1/admin/users/2`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```json
  {
    "is_active": false
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `PUT /api/v1/admin/users/2`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. `put /api/v1/admin/users/2` với body `{"is_active": false}`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Phản hồi JSON chứa `success = true`, cờ `is_active = false`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersUpdate_TC013: Mở khóa tài khoản Giảng viên thành công (is_active = true)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Tài khoản Giảng viên `id = 2` đang bị khóa (`is_active = false`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `PUT /api/v1/admin/users/2`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Body Input**:
  ```json
  {
    "is_active": true
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `PUT /api/v1/admin/users/2`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. `put /api/v1/admin/users/2` với body `{"is_active": true}`.
4. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Phản hồi JSON chứa `success = true`, cờ `is_active = true`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# ==============================================================================

# PHẦN 5: API DELETE /api/v1/admin/users/ (XÓA TÀI KHOẢN NGƯỜI DÙNG)

# ==============================================================================

# UT02_UsersDelete_TC001: Người gọi chưa đăng nhập (Không có Token xác thực)

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Hệ thống Web Server Backend đang hoạt động bình thường.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `DELETE /api/v1/admin/users/2`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Khách vãng lai chưa đăng nhập (Token = `None`).
- **Tham số đầu vào (Input Parameters)**:
  ```json
  {
    "id": 2
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `DELETE /api/v1/admin/users/2`.
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
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersDelete_TC002: Người gọi là Giảng viên không có quyền xóa tài khoản

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Người dùng đăng nhập có `role = "INSTRUCTOR"`.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `DELETE /api/v1/admin/users/2`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Giảng viên (`id: 2, role: "INSTRUCTOR"`).
- **Tham số đầu vào (Input Parameters)**:
  ```json
  {
    "id": 2
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `DELETE /api/v1/admin/users/2`.
2. Truyền token xác thực của Giảng viên vào Header `Authorization: Bearer <INSTRUCTOR_TOKEN>`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `403 Forbidden`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 403,
    "error_code": "FORBIDDEN_ADMIN_ONLY",
    "message": "Bạn không có quyền truy cập vào chức năng quản trị này.",
    "details": null,
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersDelete_TC003: Tham số id trên đường dẫn không hợp lệ (id = 0 hoặc chuỗi)

#### Loại test

Binary

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `DELETE /api/v1/admin/users/invalid_id`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Tham số đầu vào (Input Parameters)**:
  ```json
  {
    "id": "invalid_id"
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `DELETE /api/v1/admin/users/invalid_id`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. `delete /api/v1/admin/users/invalid_id`.
4. Gửi Request lên hệ thống.

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
        "field": "id",
        "issue": "Mã ID người dùng phải là một số nguyên dương hợp lệ."
      }
    ],
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersDelete_TC004: Xóa tài khoản người dùng không tồn tại trong CSDL (id = 9999)

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Trong CSDL không tồn tại bản ghi người dùng `id = 9999`.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `DELETE /api/v1/admin/users/9999`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Tham số đầu vào (Input Parameters)**:
  ```json
  {
    "id": 9999
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `DELETE /api/v1/admin/users/9999`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `404 Not Found`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 404,
    "error_code": "USER_NOT_FOUND",
    "message": "Không tìm thấy người dùng với mã ID đã chỉ định.",
    "details": null,
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersDelete_TC005: Quản trị viên cố tình tự xóa tài khoản của chính mình

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- Quản trị viên đang đăng nhập sở hữu `id = 1`.
- Quản trị viên gửi yêu cầu `DELETE /api/v1/admin/users/1`.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `DELETE /api/v1/admin/users/1`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên đang đăng nhập (`id: 1, role: "ADMIN"`).
- **Tham số đầu vào (Input Parameters)**:
  ```json
  {
    "id": 1
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `DELETE /api/v1/admin/users/1`.
2. Truyền token xác thực của Quản trị viên vào Header `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `400 Bad Request`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": false,
    "status_code": 400,
    "error_code": "BAD_REQUEST",
    "message": "Bạn không thể tự xóa tài khoản Quản trị viên của chính mình.",
    "details": null,
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersDelete_TC006: Lỗi máy chủ cơ sở dữ liệu khi thực hiện xóa người dùng

#### Loại test

Abnormal

#### Tiền điều kiện (Pre-condition)

- CSDL PostgreSQL bị ngắt kết nối giả lập (Mock DB Connection Error).

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `DELETE /api/v1/admin/users/2`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Tham số đầu vào (Input Parameters)**:
  ```json
  {
    "id": 2
  }
  ```
- **Mock State**: `DatabaseConnectionPool.status = 'DISCONNECTED'`.

#### Các bước thực hiện (Test Steps)

1. Kích hoạt lỗi ngắt kết nối CSDL trên Mock Backend.
2. Khởi tạo HTTP Request `DELETE /api/v1/admin/users/2`.
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
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |

---

# UT02_UsersDelete_TC007: Xóa tài khoản Giảng viên thành công khỏi hệ thống

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Quản trị viên `admin` có quyền truy cập hợp lệ (`role = "ADMIN"`).
- Tài khoản Giảng viên `id = 2` (`teacher_hung`) đang tồn tại trong hệ thống.

#### Dữ liệu kiểm thử (Test Data)

- **Method & Endpoint**: `DELETE /api/v1/admin/users/2`
- **Ngữ cảnh người gọi (Caller Identity Input)**: Quản trị viên hợp lệ (`role = "ADMIN"`).
- **Tham số đầu vào (Input Parameters)**:
  ```json
  {
    "id": 2
  }
  ```

#### Các bước thực hiện (Test Steps)

1. Khởi tạo HTTP Request `DELETE /api/v1/admin/users/2`.
2. Đính kèm Token Admin hợp lệ.
3. Gửi Request lên hệ thống.

#### Kết quả kỳ vọng (Expected Result)

- HTTP Status Code: `200 OK`.
- Phản hồi JSON chứa:
  ```json
  {
    "success": true,
    "status_code": 200,
    "message": "Xóa người dùng thành công",
    "data": null,
    "timestamp": "2026-10-05T08:30:00.000Z"
  }
  ```

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  |            |                    |                                     |                  |              |          |
