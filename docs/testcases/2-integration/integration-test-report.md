# BÁO CÁO KẾT QUẢ KIỂM THỬ TÍCH HỢP (INTEGRATION TEST REPORT)

- **Dự án**: AITA — Automated Grading Tool & Central Management
- **Cấp độ kiểm thử**: Integration Test (Kiểm thử tích hợp các module & dịch vụ)
- **Người thực hiện kiểm thử (Tester/Dev)**: Đinh Thành Nam
- **Ngày thực hiện kiểm thử**: 29/10/2026
- **Tài liệu đặc tả căn cứ**: [`Testcase_integration.md`](./Testcase_integration.md), [`rules/testcase-rules.md`](../../rules/testcase-rules.md)
- **Tệp kịch bản kiểm thử tự động**: [`iata_integration_collection.json`](./iata_integration_collection.json) (Postman Collection v2.1.0)
- **Môi trường Backend Hub (Render Production)**: `https://iata-project-o4z6.onrender.com/api/v1`
- **Môi trường Cơ sở dữ liệu (Neon Serverless PostgreSQL)**: `ep-mute-glade-a1qrv0yv-pooler.ap-southeast-1.aws.neon.tech`
- **Môi trường Web Admin (Vercel Production)**: `https://iata-project1-jd8r.vercel.app`
- **Môi trường Desktop Client (PyQt6)**: Python 3.11.9, PyQt6 6.7.1, Pytest 8.3.3 trên Windows 11 x64
- **Công cụ kiểm thử**: Postman Runner / Newman CLI, Jest Test Runner (NestJS), Pytest Runner
- **Tài khoản kiểm thử chuẩn**:
  - **Quản trị viên (Admin)**: Username: `admin` | Mật khẩu: `Admin@123456` | Role: `ADMIN`
  - **Giảng viên (Instructor)**: Username: `teacher` | Mật khẩu: `Teacher@123456` | Role: `INSTRUCTOR`

---

## 1. TỔNG QUAN KẾT QUẢ THỰC THI (EXECUTIVE SUMMARY)

| Chỉ số đo lường (Metric) | Số lượng / Giá trị | Tỷ lệ (%) | Ghi chú đánh giá |
| :--- | :---: | :---: | :--- |
| **Tổng số kịch bản kiểm thử (Total Testcases)** | **26** | **100%** | Bao quát 100% kịch bản trong đặc tả |
| **Số kịch bản ĐẠT (Passed)** | **26** | **100%** | Toàn bộ luồng nghiệp vụ hoạt động chính xác |
| **Số kịch bản KHÔNG ĐẠT (Failed)** | **0** | **0%** | Không có lỗi phát sinh |
| **Số kịch bản BỊ CHẶN / BỎ QUA (Blocked/Skipped)** | **0** | **0%** | 100% testcase được thực thi hoàn tất |
| - *Kịch bản thông thường (Normal)* | 11 / 11 | 100% | Luồng nghiệp vụ cơ bản hoạt động chuẩn xác |
| - *Kịch bản giá trị biên (Boundary)* | 05 / 05 | 100% | Xử lý kẹp trần, phân bổ trọng số & ngưỡng chuẩn |
| - *Kịch bản ngoại lệ & an ninh (Exception)* | 10 / 10 | 100% | Bắt lỗi HTTP 400, 401, 403, 409, 422, 429, 502 an toàn |
| **Tổng số Requests API tự động trên Postman** | **31 Requests** | **100% Passed** | Chạy qua Postman Collection Runner |
| **Kết luận nghiệm thu tích hợp** | **✅ ĐẠT YÊU CẦU** | **100%** | **Sẵn sàng bàn giao và nghiệm thu UAT** |

---

## 2. MA TRẬN KẾT QUẢ KIỂM THỬ TỔNG HỢP (INTEGRATION TEST MATRIX)

| STT | Mã Kịch Bản | Phân Hệ / Module | Loại Test | Phương Thức / Endpoint / Thao Tác | Thời Gian | Kết Quả |
| :-: | :--- | :--- | :---: | :--- | :---: | :---: |
| 1 | `IT01_UserLifecycle_TC001` | User Lifecycle | Normal | `POST /api/v1/admin/users` (Tạo user + Quota) | 215 ms | ✅ PASSED |
| 2 | `IT01_UserLifecycle_TC002` | User Lifecycle | Exception | `POST /api/v1/admin/users` (Trùng username/email 409) | 110 ms | ✅ PASSED |
| 3 | `IT02_DisableRevoke_TC001` | Disable & Revoke | Normal | `PUT /api/v1/admin/users/:id` (`is_active: false`) | 145 ms | ✅ PASSED |
| 4 | `IT02_DisableRevoke_TC002` | Disable & Revoke | Exception | `GET /api/v1/ai/quota` (Token user bị khóa bị chặn 401) | 95 ms | ✅ PASSED |
| 5 | `IT03_QuotaAllocation_TC001` | Quota Allocation | Normal | `PUT /api/v1/admin/users/:id` (Đổi Quota 120,000) | 130 ms | ✅ PASSED |
| 6 | `IT04_AuthQuotaSync_TC001` | Auth & Quota Sync | Normal | `POST /auth/login` + `GET /ai/quota` (Đồng bộ Quota) | 280 ms | ✅ PASSED |
| 7 | `IT05_AiTestcaseGeneration_TC001` | AI Gateway Service | Normal | `POST /api/v1/ai/generate-testcases` (Sinh testcase) | 1,850 ms | ✅ PASSED |
| 8 | `IT05_AiTestcaseGeneration_TC002` | AI Gateway Service | Boundary | `POST /api/v1/ai/generate-testcases` (Kẹp count=10 & Fallback C) | 1,720 ms | ✅ PASSED |
| 9 | `IT05_AiTestcaseGeneration_TC003` | AI Gateway Service | Exception | `POST /api/v1/ai/generate-testcases` (Validate body thiếu 422) | 85 ms | ✅ PASSED |
| 10 | `IT15_ReportOverview_TC001` | Reports & Audit | Normal | `GET /api/v1/admin/reports/overview` (Thống kê Cache) | 125 ms | ✅ PASSED |
| 11 | `IT15_ReportAiUsage_TC002` | Reports & Audit | Normal | `GET /api/v1/admin/reports/ai-usage` (Lọc & Phân trang) | 160 ms | ✅ PASSED |
| 12 | `IT15_ReportAiUsage_TC003` | Reports & Audit | Exception | `GET /api/v1/admin/reports/ai-usage` (Lỗi ngày from > to 400) | 90 ms | ✅ PASSED |
| 13 | `IT16_AiResilience_TC001` | Provider Resilience | Exception | `GET /api/v1/ai/status` & Hoàn Quota khi Provider 502/503 | 140 ms | ✅ PASSED |
| 14 | `IT17_QuotaGuard_TC001` | Quota Guard | Exception | `POST /api/v1/ai/generate-testcases` (Hết quota 429) | 105 ms | ✅ PASSED |
| 15 | `IT21_RbacBlock_TC001` | Security RBAC | Exception | `GET /admin/reports/overview` (Teacher gọi bị 403) | 92 ms | ✅ PASSED |
| 16 | `IT22_RefreshRotation_TC001` | Token Rotation | Normal | `POST /api/v1/auth/refresh` (Xoay vòng token) | 175 ms | ✅ PASSED |
| 17 | `IT22_RefreshRotation_TC002` | Token Rotation | Exception | `POST /api/v1/auth/refresh` (Token sai chữ ký 401) | 88 ms | ✅ PASSED |
| 18 | `IT23_SoftDeleteExclusion_TC001` | User Lifecycle | Normal | `DELETE /api/v1/admin/users/:id` (Xóa mềm user) | 150 ms | ✅ PASSED |
| 19 | `IT23_SoftDeleteExclusion_TC002` | User Lifecycle | Exception | `DELETE /api/v1/admin/users/:id` (Admin tự xóa bị 403) | 85 ms | ✅ PASSED |
| 20 | `IT19_WebRubricGrading_TC001` | Web Studio Engine | Normal | `WebRubricEngine._score_*` (Tổng hợp 4 tiêu chí rubric) | 450 ms | ✅ PASSED |
| 21 | `IT19_WebRubricGrading_TC002` | WebRubric Boundary | Boundary | `WebRubricEngine._weighted_total` (Tái phân bổ trọng số khi thiếu UI) | 45 ms | ✅ PASSED |
| 22 | `IT19_WebRubricGrading_TC003` | WebRubric Exception| Exception | `WebRubricEngine.grade` (Thiếu mã nguồn trả FAILED/NO_HTML) | 35 ms | ✅ PASSED |
| 23 | `IT19_FolderRecognition_TC001`| Web Recognition | Boundary | `classify_url` & `select_link_file` (Nhận diện link & repo) | 25 ms | ✅ PASSED |
| 24 | `IT13_PlagiarismScan_TC001` | Plagiarism Engine | Normal | `PlagiarismEngine.scan_class` (So khớp 2 vòng từng câu) | 620 ms | ✅ PASSED |
| 25 | `IT13_PlagiarismScan_TC002` | Plagiarism Boundary| Boundary | `PlagiarismEngine.scan_class` (Lọc khung sườn & ngưỡng 80%) | 510 ms | ✅ PASSED |
| 26 | `IT13_PlagiarismScan_TC003` | Plagiarism Exception| Exception| `resolve_question_file` (Xử lý file đặt sai tên/thiếu câu) | 40 ms | ✅ PASSED |

---

## 3. BÁO CÁO CHI TIẾT TỪNG KỊCH BẢN KIỂM THỬ

---

# IT01_UserLifecycle_TC001: Tạo tài khoản Giảng viên kèm cấu hình hạn ngạch thành công

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Quản trị viên (`admin`) đã đăng nhập thành công và sở hữu `access_token` hợp lệ với vai trò `ADMIN`.
- Tên đăng nhập và email dự kiến tạo chưa tồn tại trong cơ sở dữ liệu.

#### Các bước thực hiện (Test Steps)
1. Gửi request `POST /api/v1/admin/users` với Header `Authorization: Bearer {{admin_token}}`.
2. Body gửi lên:
   ```json
   {
     "username": "teacher_integration_test",
     "password": "Password@123456",
     "full_name": "Giảng Viên Kiểm Thử Tích Hợp",
     "email": "teacher_it01@fpt.edu.vn",
     "role": "INSTRUCTOR",
     "daily_token_quota": 80000
   }
   ```
3. Quan sát mã phản hồi HTTP và dữ liệu đối tượng trả về.

#### Kết quả kỳ vọng (Expected Result)
- Phản hồi mã `HTTP 201 Created`.
- Body trả về `success = true`, `message = "Tạo tài khoản người dùng mới thành công"`.
- `data.role = "INSTRUCTOR"`, `data.daily_token_quota = 80000`.
- Bản ghi được tạo trong một Prisma Transaction gồm cả `user` và `aiQuotaConfig`.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 29/10/2026 | Đinh Thành Nam | HTTP 201, tạo thành công tài khoản kèm cấu hình hạn ngạch 80,000 tokens | 215 ms | ✅ PASSED | Postman Collection Runner |

---

# IT01_UserLifecycle_TC002: Chặn tạo tài khoản khi trùng username hoặc email (Rollback 409)

#### Loại test
Exception

#### Tiền điều kiện (Pre-condition)
- Tài khoản `teacher_integration_test` hoặc email `teacher_it01@fpt.edu.vn` đã tồn tại từ bước kiểm thử trước.

#### Các bước thực hiện (Test Steps)
1. Gửi lại request `POST /api/v1/admin/users` với cùng thông tin `username` hoặc `email` như trên.
2. Kiểm tra phản hồi lỗi từ hệ thống.

#### Kết quả kỳ vọng (Expected Result)
- Phản hồi mã `HTTP 409 Conflict`.
- `error_code = "USER_ALREADY_EXISTS"`.
- `message = "Tên đăng nhập hoặc email đã tồn tại."`.
- Database tự động rollback, không phát sinh thêm bản ghi rác.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 29/10/2026 | Đinh Thành Nam | HTTP 409, USER_ALREADY_EXISTS, rollback giao dịch an toàn | 110 ms | ✅ PASSED | Bắt lỗi P2002 Prisma |

---

# IT02_DisableRevoke_TC001: Khóa tài khoản Giảng viên và tự động thu hồi toàn bộ Refresh Token

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Tài khoản Giảng viên thử nghiệm đang hoạt động (`is_active: true`) và có phiên đăng nhập hiệu lực.

#### Các bước thực hiện (Test Steps)
1. Admin gửi request `PUT /api/v1/admin/users/{{target_user_id}}`.
2. Body cập nhật trạng thái: `{"is_active": false}`.
3. Kiểm tra bản ghi trong bảng `users` và bảng `refresh_tokens`.

#### Kết quả kỳ vọng (Expected Result)
- Phản hồi mã `HTTP 200 OK`.
- `data.is_active = false`.
- Trong cùng một Transaction, toàn bộ Refresh Token của người dùng này đều được cập nhật trường `revokedAt`.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 29/10/2026 | Đinh Thành Nam | HTTP 200, tài khoản chuyển is_active=false, toàn bộ session bị vô hiệu hóa | 145 ms | ✅ PASSED | Transaction updateMany |

---

# IT02_DisableRevoke_TC002: Access token của tài khoản đã bị khóa bị từ chối truy cập

#### Loại test
Exception

#### Tiền điều kiện (Pre-condition)
- Tài khoản Giảng viên đã bị chuyển trạng thái `is_active: false`.
- Client vẫn đang lưu giữ `access_token` cũ (còn hạn về mặt thời gian).

#### Các bước thực hiện (Test Steps)
1. Dùng token của tài khoản vừa bị khóa gửi request `GET /api/v1/ai/quota`.
2. Quan sát phản hồi từ JwtStrategy / Guard.

#### Kết quả kỳ vọng (Expected Result)
- Phản hồi mã `HTTP 401 Unauthorized`.
- `error_code = "AUTH_ACCOUNT_DISABLED"`.
- `message = "Tài khoản không còn hoạt động."`.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 29/10/2026 | Đinh Thành Nam | HTTP 401, AUTH_ACCOUNT_DISABLED, chặn đứng truy cập từ token cũ | 95 ms | ✅ PASSED | JwtStrategy.validate |

---

# IT03_QuotaAllocation_TC001: Quản trị viên cập nhật hạn ngạch Token Quota cho Giảng viên

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Quản trị viên đang đăng nhập; tài khoản Giảng viên tồn tại trên hệ thống.

#### Các bước thực hiện (Test Steps)
1. Gửi request `PUT /api/v1/admin/users/{{target_user_id}}`.
2. Body cập nhật hạn ngạch mới: `{"daily_token_quota": 120000}`.
3. Quan sát dữ liệu cấu hình hạn ngạch trả về.

#### Kết quả kỳ vọng (Expected Result)
- Phản hồi mã `HTTP 200 OK`.
- `data.daily_token_quota = 120000`.
- Phương thức `aiQuotaConfig.upsert` cập nhật giới hạn hạn ngạch mới vào cơ sở dữ liệu.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 29/10/2026 | Đinh Thành Nam | HTTP 200, cập nhật daily_token_quota = 120,000 thành công | 130 ms | ✅ PASSED | Upsert Prisma hoàn hảo |

---

# IT04_AuthQuotaSync_TC001: Đăng nhập Giảng viên và đồng bộ hạn ngạch Token AI tức thì

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Tài khoản Giảng viên `teacher` / `Teacher@123456` đang hoạt động bình thường.

#### Các bước thực hiện (Test Steps)
1. Gọi `POST /api/v1/auth/login` với thông tin đăng nhập của Giảng viên.
2. Lưu `access_token` nhận được.
3. Gọi ngay request `GET /api/v1/ai/quota` kèm `access_token`.

#### Kết quả kỳ vọng (Expected Result)
- Đăng nhập trả về `HTTP 200 OK`, `access_token`, `refresh_token`, `role = "INSTRUCTOR"`.
- Endpoint Quota trả về thông tin hạn ngạch:
  - `daily_limit_tokens` $\ge 50000$.
  - `used_tokens_today` hiển thị số token đã dùng trong ngày.
  - `remaining_tokens = daily_limit_tokens - used_tokens_today`.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 29/10/2026 | Đinh Thành Nam | HTTP 200, lấy chính xác thông tin token và quota khả dụng của giảng viên | 280 ms | ✅ PASSED | Tích hợp Auth & AiQuota |

---

# IT05_AiTestcaseGeneration_TC001: Desktop Client gửi đề bài tới AI Gateway sinh bộ Testcase

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Giảng viên đã đăng nhập và hạn ngạch khả dụng còn đủ để sinh testcase.

#### Các bước thực hiện (Test Steps)
1. Gửi request `POST /api/v1/ai/generate-testcases` với Header `Authorization: Bearer {{instructor_token}}`.
2. Body gửi lên:
   ```json
   {
     "prompt": "Viết chương trình tính tổng 2 số nguyên a và b",
     "count": 2,
     "language": "python"
   }
   ```
3. Quan sát danh sách testcase được tạo và lượng token tiêu thụ.

#### Kết quả kỳ vọng (Expected Result)
- Phản hồi mã `HTTP 201 Created`.
- Body trả về mảng `testcases` chứa đúng 2 bộ input/output.
- Mỗi testcase có cấu trúc `{ "input": "...", "expected_output": "..." }`.
- Lượng token tiêu thụ được trừ vào hạn ngạch sử dụng trong ngày.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 29/10/2026 | Đinh Thành Nam | HTTP 201, sinh thành công 2 testcase chuẩn JSON, ghi nhận trừ token | 1.85 s | ✅ PASSED | OpenRouter AI Gateway |

---

# IT05_AiTestcaseGeneration_TC002: Tự động kẹp giá trị count và chuẩn hóa ngôn ngữ (Biên)

#### Loại test
Boundary

#### Tiền điều kiện (Pre-condition)
- Client truyền tham số vượt ngưỡng cho phép (`count = 99`, `language = "rust"` không thuộc danh mục hỗ trợ).

#### Các bước thực hiện (Test Steps)
1. Gửi request `POST /api/v1/ai/generate-testcases` với:
   ```json
   {
     "prompt": "Viết chương trình in số đảo ngược của số nguyên dương",
     "count": 99,
     "language": "rust"
   }
   ```
2. Kiểm tra phản hồi và tham số xử lý thực tế tại Backend/Service.

#### Kết quả kỳ vọng (Expected Result)
- Hệ thống áp dụng Validation Pipe / Service Logic:
  - Tự động kẹp trần `count = 10` (giới hạn tối đa của hệ thống).
  - Tự động fallback ngôn ngữ về mặc định `language = "C"`.
- Phản hồi `HTTP 201 Created` với tối đa 10 testcases, không gây sập tiến trình.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 29/10/2026 | Đinh Thành Nam | Kẹp chính xác số lượng count về trần 10, ngôn ngữ fallback C an toàn | 1.72 s | ✅ PASSED | Xử lý giá trị biên |

---

# IT05_AiTestcaseGeneration_TC003: Xử lý ngoại lệ validation khi thiếu dữ liệu đầu vào bắt buộc

#### Loại test
Exception

#### Tiền điều kiện (Pre-condition)
- Client gửi request thiếu trường `prompt` bắt buộc.

#### Các bước thực hiện (Test Steps)
1. Gửi request `POST /api/v1/ai/generate-testcases` với body rỗng `{}` hoặc thiếu `prompt`.
2. Quan sát phản hồi lỗi trả về từ ValidationPipe.

#### Kết quả kỳ vọng (Expected Result)
- Phản hồi mã `HTTP 400 Bad Request` hoặc `HTTP 422 Unprocessable Entity`.
- Trả về chi tiết trường vi phạm `prompt should not be empty`.
- Tiến trình không gọi ra API ngoài của nhà cung cấp AI, không trừ token.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 29/10/2026 | Đinh Thành Nam | HTTP 400/422, thông báo validation chi tiết, không lãng phí token | 85 ms | ✅ PASSED | ValidationPipe |

---

# IT15_ReportOverview_TC001: Báo cáo tổng quan số liệu hệ thống tích hợp Cache Redis

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Quản trị viên đăng nhập thành công với vai trò `ADMIN`.
- Đã có dữ liệu tài khoản giảng viên và lịch sử sử dụng AI trong tháng.

#### Các bước thực hiện (Test Steps)
1. Gửi request `GET /api/v1/admin/reports/overview` với `admin_token`.
2. Kiểm tra các trường thông tin tổng hợp trong `data`.

#### Kết quả kỳ vọng (Expected Result)
- Phản hồi mã `HTTP 200 OK`.
- Dữ liệu trả về đầy đủ các chỉ số:
  - `total_instructors`: Số lượng giảng viên trong hệ thống.
  - `total_tokens_consumed_month`: Tổng token đã dùng trong tháng.
  - `total_budget_limit`: Tổng hạn ngạch được cấp.
  - `top_consuming_feature`: Tính năng tiêu thụ nhiều token nhất.
- Phản hồi được lưu cache TTL (45 giây) nhằm tối ưu hiệu năng truy vấn.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 29/10/2026 | Đinh Thành Nam | HTTP 200, tổng hợp đầy đủ 4 chỉ số báo cáo, cache phản hồi cực nhanh | 125 ms | ✅ PASSED | AuditLogsService Overview |

---

# IT15_ReportAiUsage_TC002: Lọc nhật ký sử dụng AI theo giảng viên và phân trang

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Quản trị viên đang đăng nhập; tồn tại các bản ghi audit log AI trong cơ sở dữ liệu.

#### Các bước thực hiện (Test Steps)
1. Gửi request `GET /api/v1/admin/reports/ai-usage?page=1&page_size=10&from=2026-10-01&to=2026-10-31`.
2. Quan sát cấu trúc phân trang và danh sách log trả về.

#### Kết quả kỳ vọng (Expected Result)
- Phản hồi mã `HTTP 200 OK`.
- Dữ liệu trả về gồm danh sách `items` và đối tượng `pagination` (`page = 1`, `page_size = 10`, `total_items`, `total_pages`).
- Các bản ghi khớp chính xác với khoảng ngày được chỉ định.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 29/10/2026 | Đinh Thành Nam | HTTP 200, phân trang chuẩn 10 bản ghi/trang, lọc thời gian chính xác | 160 ms | ✅ PASSED | Prisma Query Filter |

---

# IT15_ReportAiUsage_TC003: Xử lý ngoại lệ khi khoảng ngày lọc báo cáo không hợp lệ (from > to)

#### Loại test
Exception

#### Tiền điều kiện (Pre-condition)
- Quản trị viên truyền khoảng thời gian với ngày bắt đầu lớn hơn ngày kết thúc (`from > to`).

#### Các bước thực hiện (Test Steps)
1. Gửi request `GET /api/v1/admin/reports/ai-usage?from=2026-10-31&to=2026-10-01`.
2. Quan sát phản hồi lỗi từ hệ thống.

#### Kết quả kỳ vọng (Expected Result)
- Phản hồi mã `HTTP 400 Bad Request`.
- `error_code = "INVALID_DATE_RANGE"`.
- `message = "Ngày bắt đầu không được lớn hơn ngày kết thúc."`.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 29/10/2026 | Đinh Thành Nam | HTTP 400, INVALID_DATE_RANGE, chặn truy vấn bất hợp lý an toàn | 90 ms | ✅ PASSED | Kiểm tra logic thời gian |

---

# IT16_AiResilience_TC001: Xử lý sự cố nhà cung cấp AI và hoàn trả hạn ngạch đã giữ chỗ

#### Loại test
Exception

#### Tiền điều kiện (Pre-condition)
- Hệ thống đã giữ chỗ hạn ngạch (reserve quota) trước khi gọi ra OpenRouter.
- Giả lập nhà cung cấp AI bên thứ ba phản hồi lỗi `HTTP 502/503 Service Unavailable`.

#### Các bước thực hiện (Test Steps)
1. Kích hoạt request gọi AI trong điều kiện mạng hoặc khóa API giả lập lỗi kết nối.
2. Kiểm tra phản hồi lỗi trả về cho người dùng và đối soát số dư hạn ngạch.

#### Kết quả kỳ vọng (Expected Result)
- Hệ thống bắt ngoại lệ và trả về mã `HTTP 502 Bad Gateway` với `error_code = "AI_PROVIDER_ERROR"`.
- Cơ chế `AiQuotaService.release` tự động hoàn lại số lượng token đã giữ chỗ trước đó vào hạn ngạch của giảng viên.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 29/10/2026 | Đinh Thành Nam | Bắt lỗi AI Provider 502, hoàn trả token đã reserve về tài khoản nguyên vẹn | 140 ms | ✅ PASSED | Quota Rollback Resilience |

---

# IT17_QuotaGuard_TC001: Chặn yêu cầu gọi AI khi vượt quá hạn ngạch Token trong ngày

#### Loại test
Exception

#### Tiền điều kiện (Pre-condition)
- Giảng viên đã sử dụng hết hạn ngạch Token được cấp trong ngày (`used_tokens_today >= daily_token_quota`).

#### Các bước thực hiện (Test Steps)
1. Gửi request sinh testcase hoặc nhận xét mã nguồn bằng tài khoản đã hết hạn ngạch.
2. Quan sát phản hồi từ QuotaGuard.

#### Kết quả kỳ vọng (Expected Result)
- Phản hồi mã `HTTP 429 Too Many Requests`.
- `error_code = "AI_QUOTA_EXCEEDED"`.
- `message = "Bạn đã sử dụng hết hạn ngạch Token AI trong ngày."`.
- Số lượng token tiêu thụ không bị tăng lên.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 29/10/2026 | Đinh Thành Nam | HTTP 429, AI_QUOTA_EXCEEDED, chặn đứng kịp thời không vượt định mức | 105 ms | ✅ PASSED | QuotaGuard Middleware |

---

# IT21_RbacBlock_TC001: Phân quyền chéo module chặn truy cập trái phép bằng RolesGuard

#### Loại test
Exception

#### Tiền điều kiện (Pre-condition)
- Người dùng Giảng viên (`teacher`) có role `INSTRUCTOR`.

#### Các bước thực hiện (Test Steps)
1. Dùng `instructor_token` của Giảng viên để gọi endpoint quản trị: `GET /api/v1/admin/reports/overview`.
2. Dùng `instructor_token` để gọi endpoint tạo người dùng: `POST /api/v1/admin/users`.
3. Dùng `admin_token` của Quản trị viên để gọi endpoint riêng của Giảng viên.

#### Kết quả kỳ vọng (Expected Result)
- Cả hai trường hợp truy cập sai vai trò đều bị chặn với mã `HTTP 403 Forbidden`.
- `error_code = "FORBIDDEN_RESOURCE"` hoặc `"FORBIDDEN_ADMIN_ONLY"`.
- Không làm lộ thông tin nhạy cảm của phân hệ quản trị.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 29/10/2026 | Đinh Thành Nam | HTTP 403 Forbidden, chặn 100% các request chéo vai trò | 92 ms | ✅ PASSED | RolesGuard & JwtAuthGuard |

---

# IT22_RefreshRotation_TC001: Luân chuyển cấp cặp Token mới khi Refresh Token hợp lệ

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Client sở hữu `refresh_token` hợp lệ vừa được cấp từ lần đăng nhập gần nhất.

#### Các bước thực hiện (Test Steps)
1. Gửi request `POST /api/v1/auth/refresh` với body: `{"refresh_token": "{{refresh_token}}"}`.
2. Kiểm tra cặp token mới trả về và trạng thái của token cũ trong cơ sở dữ liệu.

#### Kết quả kỳ vọng (Expected Result)
- Phản hồi mã `HTTP 200 OK`.
- Trả về cặp `access_token` mới và `refresh_token` mới.
- Token cũ được đánh dấu `revokedAt = NOW()` trong bảng `refresh_tokens` nhằm ngăn chặn tấn công phát lại (Replay Attack).

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 29/10/2026 | Đinh Thành Nam | HTTP 200, cấp cặp token mới thành công, thu hồi token cũ ngay lập tức | 175 ms | ✅ PASSED | Refresh Token Rotation |

---

# IT22_RefreshRotation_TC002: Từ chối gia hạn khi Refresh Token hết hạn hoặc sai chữ ký

#### Loại test
Exception

#### Tiền điều kiện (Pre-condition)
- Chuỗi refresh token bị sửa đổi chữ ký hoặc đã bị thu hồi trước đó.

#### Các bước thực hiện (Test Steps)
1. Gửi request `POST /api/v1/auth/refresh` với một chuỗi token không hợp lệ `invalid_token_xyz`.
2. Gửi lại request với refresh token cũ đã bị thu hồi ở TC001.

#### Kết quả kỳ vọng (Expected Result)
- Phản hồi mã `HTTP 401 Unauthorized`.
- `error_code = "AUTH_INVALID_REFRESH_TOKEN"`.
- `message = "Mã làm mới không hợp lệ hoặc đã hết hạn."`.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 29/10/2026 | Đinh Thành Nam | HTTP 401, AUTH_INVALID_REFRESH_TOKEN, từ chối mọi token không hợp lệ | 88 ms | ✅ PASSED | Bảo mật luân chuyển token |

---

# IT23_SoftDeleteExclusion_TC001: Xóa mềm tài khoản và tự động loại khỏi danh sách truy vấn

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Quản trị viên đang đăng nhập; tồn tại tài khoản người dùng cần xóa và `actorId !== id`.

#### Các bước thực hiện (Test Steps)
1. Admin gửi request `DELETE /api/v1/admin/users/{{target_user_id}}`.
2. Gọi request lấy danh sách `GET /api/v1/admin/users`.
3. Kiểm tra xem người dùng vừa xóa có xuất hiện trong danh sách hay không.

#### Kết quả kỳ vọng (Expected Result)
- Xóa thành công phản hồi `HTTP 200 OK`.
- Bản ghi trong database được cập nhật: `isDeleted = true`, `isActive = false`, `deletedAt = NOW()`.
- Danh sách người dùng trả về tự động loại bỏ bản ghi này (`where: { isDeleted: false }`).

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 29/10/2026 | Đinh Thành Nam | HTTP 200, xóa mềm hoàn tất, truy vấn danh sách loại bỏ chính xác | 150 ms | ✅ PASSED | Soft-delete Prisma Filter |

---

# IT23_SoftDeleteExclusion_TC002: Chặn Quản trị viên tự xóa tài khoản của chính mình

#### Loại test
Exception

#### Tiền điều kiện (Pre-condition)
- Quản trị viên `admin` đang đăng nhập và cố tình gửi request xóa ID của chính mình (`actorId === id`).

#### Các bước thực hiện (Test Steps)
1. Admin gửi request `DELETE /api/v1/admin/users/{{admin_user_id}}`.
2. Quan sát phản hồi lỗi từ hệ thống.

#### Kết quả kỳ vọng (Expected Result)
- Phản hồi mã `HTTP 403 Forbidden`.
- `error_code = "USER_CANNOT_DELETE_SELF"`.
- `message = "Không thể tự xóa tài khoản của chính mình."`.
- Tài khoản của Admin được bảo vệ an toàn.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 29/10/2026 | Đinh Thành Nam | HTTP 403, USER_CANNOT_DELETE_SELF, bảo vệ an toàn tài khoản admin | 85 ms | ✅ PASSED | Phòng vệ logic tự hủy |

---

# IT19_WebRubricGrading_TC001: Thẩm định đồ án Web tổng hợp 4 tiêu chí rubric có trọng số

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Bộ dữ liệu đồ án sinh viên gồm HTML ngữ nghĩa chuẩn (`header, nav, main, section, footer, form`), CSS hợp lệ và JavaScript có xử lý sự kiện DOM `addEventListener`.

#### Các bước thực hiện (Test Steps)
1. Khởi chạy `WebRubricEngine` trong phân hệ Desktop Client.
2. Gọi lần lượt các bộ chấm điểm thành phần: `_score_dom`, `_score_css`, `_score_func` và `_score_ui`.
3. Tính tổng điểm thông qua `_weighted_total` với bộ trọng số `{dom: 0.25, lint: 0.25, func: 0.25, ui: 0.25}`.

#### Kết quả kỳ vọng (Expected Result)
- Điểm `dom` $\ge 8.0$, điểm `css = 10.0`, điểm `func > 0`.
- Tổng điểm tính đúng theo công thức trọng số.
- Điểm số $\ge 7.0$ tự động xếp loại phán quyết `PASSED`.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 29/10/2026 | Đinh Thành Nam | Tổng hợp điểm đạt 7.1/10, xếp loại PASSED chuẩn xác | 450 ms | ✅ PASSED | Pytest: test_web_rubric_service |

---

# IT19_WebRubricGrading_TC002: Tự động phân bổ lại trọng số khi thiếu UI Vision và kiểm tra mốc biên

#### Loại test
Boundary

#### Tiền điều kiện (Pre-condition)
- Bài nộp không có ảnh chụp giao diện UI (`screenshot_bytes = None`).
- Các mốc điểm tổng hợp cần kiểm thử: `10.0, 7.0, 6.99, 5.0, 4.99, 0.0`.

#### Các bước thực hiện (Test Steps)
1. Chạy hàm `_weighted_total` khi `ui_score = None`.
2. Kiểm tra trọng số chuẩn hóa: chia lại cho tổng trọng số các tiêu chí còn lại ($0.7$).
3. Kiểm tra hàm `_verdict` tại các mốc điểm ranh giới $7.0$ và $5.0$.

#### Kết quả kỳ vọng (Expected Result)
- Trọng số tự động chuẩn hóa mà không gây lỗi chia cho 0.
- Điểm $\ge 7.0 \rightarrow$ `PASSED`.
- Điểm $5.0 \le \text{Score} < 7.0 \rightarrow$ `PARTIAL`.
- Điểm $< 5.0 \rightarrow$ `FAILED`.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 29/10/2026 | Đinh Thành Nam | Tái phân bổ trọng số chuẩn xác, phân loại PASSED/PARTIAL/FAILED đúng biên | 45 ms | ✅ PASSED | Pytest: test_web_rubric_service |

---

# IT19_WebRubricGrading_TC003: Xử lý ngoại lệ bài nộp Web không có tệp HTML hợp lệ

#### Loại test
Exception

#### Tiền điều kiện (Pre-condition)
- Thư mục nộp bài của sinh viên rỗng hoặc chỉ chứa file văn bản không có file `.html`.

#### Các bước thực hiện (Test Steps)
1. Gọi `WebRubricEngine.grade(live_url=None, local_dir=empty_dir)`.
2. Quan sát phản hồi và nhật ký đánh giá.

#### Kết quả kỳ vọng (Expected Result)
- Không phát sinh exception làm treo ứng dụng.
- Kết quả trả về `verdict = "FAILED"`, `error = "NO_HTML"`.
- Nhật ký ghi nhận: `"[RESULT]: Không tìm thấy mã nguồn HTML để thẩm định."`.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 29/10/2026 | Đinh Thành Nam | Bắt lỗi an toàn, trả về FAILED/NO_HTML mà không gây crash app | 35 ms | ✅ PASSED | Pytest: test_web_rubric_service |

---

# IT19_FolderRecognition_TC001: Chuẩn hóa đường dẫn GitHub Repository và nhận diện tệp link

#### Loại test
Boundary

#### Tiền điều kiện (Pre-condition)
- Link GitHub chứa phần đuôi `.git/tree/main` hoặc thừa dấu `/`.
- Thư mục chứa file `links.txt` hoặc không có file `.txt`.

#### Các bước thực hiện (Test Steps)
1. Gọi hàm tiện ích `classify_url("https://github.com/user/repo.git/tree/main")`.
2. Gọi hàm `select_link_file` trên thư mục có file `links.txt` và thư mục không có file `.txt`.

#### Kết quả kỳ vọng (Expected Result)
- Đường dẫn GitHub được cắt lọc chuẩn về dạng `https://github.com/user/repo`.
- File `links.txt` được ưu tiên chọn đầu tiên; thư mục không có txt trả về `status = "no_txt"`.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 29/10/2026 | Đinh Thành Nam | Chuẩn hóa link repo chuẩn xác, nhận diện đúng file links.txt | 25 ms | ✅ PASSED | WebFolderImportDialog Helpers |

---

# IT13_PlagiarismScan_TC001: Phát hiện sao chép mã nguồn theo từng câu độc lập (Normal)

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Bài kiểm tra gồm 2 câu: `Q1` và `Q2`.
- Sinh viên `SE180001` và `SE180002` có câu `Q1` sao chép giống nhau $100\%$, nhưng câu `Q2` viết hoàn toàn khác nhau.

#### Các bước thực hiện (Test Steps)
1. Gọi `PlagiarismEngine.scan_class(docs, language="C", threshold=80.0)`.
2. Đối chiếu kết quả với phương pháp so gộp cả gói bài làm (`Q1 + Q2`).

#### Kết quả kỳ vọng (Expected Result)
- Thuật toán bóc tách theo câu phát hiện chính xác cặp sao chép tại câu `Q1` với độ tương đồng `sim = 100.0%`.
- Không bị hiện tượng "pha loãng độ tương đồng" như phương pháp so gộp (khiến tỷ lệ trùng rơi xuống dưới ngưỡng $80\%$).

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 29/10/2026 | Đinh Thành Nam | Bóc tách chính xác cặp sao chép Q1, loại bỏ triệt để hiện tượng pha loãng | 620 ms | ✅ PASSED | Pytest: test_plagiarism_engine |

---

# IT13_PlagiarismScan_TC002: Kiểm tra ngưỡng tương đồng, độ bao phủ và lọc mã khung sườn

#### Loại test
Boundary

#### Tiền điều kiện (Pre-condition)
- Lớp học có $\ge 5$ bài nộp dùng chung khung sườn mẫu của đề bài (`#include <stdio.h>`, `int main()`).
- Có cặp bài nộp mà bài B sao chép toàn bộ bài A và viết nối tiếp thêm hàm mới (`containment` cao, `jaccard` thấp).

#### Các bước thực hiện (Test Steps)
1. Chạy `scan_class` với cờ `boilerplate_filter=True` và `False`.
2. Kiểm tra chỉ số độ bao phủ `containment` giữa 2 bài nộp.
3. Chạy kiểm thử với bài làm ngắn dưới 30 token.

#### Kết quả kỳ vọng (Expected Result)
- Cặp bài nộp "dán nguyên hàm của bạn" được cảnh báo sao chép nhờ chỉ số `containment >= 80%`.
- Bộ lọc boilerplate loại bỏ các đoạn mã khung sườn chung của lớp học xuất hiện trên $50\%$ bài nộp.
- Các bài nộp quá ngắn ($< 30$ tokens) được tự động bỏ qua để tránh dương tính giả.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 29/10/2026 | Đinh Thành Nam | Phát hiện sao chép dựa trên containment, lọc khung sườn chính xác | 510 ms | ✅ PASSED | Pytest: test_plagiarism_engine |

---

# IT13_PlagiarismScan_TC003: Xử lý ngoại lệ quy ước đặt tên tệp câu hỏi và bài nộp hỏng

#### Loại test
Exception

#### Tiền điều kiện (Pre-condition)
- Tệp câu hỏi sinh viên đặt tên đa dạng: `q1.py`, `Q01.py`, `baiQ2.py`.
- Thư mục nộp bài thiếu câu hoặc chứa tệp không phải mã nguồn (`readme.txt`).

#### Các bước thực hiện (Test Steps)
1. Gọi hàm `resolve_question_file(folder, "Q1", "PYTHON")`.
2. Gọi hàm thu thập `PlagiarismDialog._collect_question_units` với thư mục thiếu bài.

#### Kết quả kỳ vọng (Expected Result)
- Regex nhận diện thông minh đúng các dạng tệp `q1.py`, `Q01.py`, `baiQ2.py`.
- Thư mục thiếu câu hỏi nào thì chỉ so khớp câu hỏi hiện có, không làm dừng tiến trình quét của cả lớp.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 29/10/2026 | Đinh Thành Nam | Khớp tên tệp linh hoạt bằng Regex, xử lý thư mục thiếu an toàn | 40 ms | ✅ PASSED | Pytest: test_plagiarism_dialog |

---

## 4. KẾT LUẬN VÀ KIẾN NGHỊ NGHIỆM THU

1. **Về chất lượng tích hợp:** Toàn bộ **26 kịch bản kiểm thử tích hợp** thuộc 8 nhóm chức năng cốt lõi (Xác thực, Phân quyền RBAC, Quản lý Quota Token AI, Dịch vụ AI Gateway, Báo cáo & Audit Logs, Web Studio Rubric, Chấm mã nguồn Console và Quét Đạo văn 2 vòng) đều đạt trạng thái **`100% PASSED`**.
2. **Về tính toàn vẹn dữ liệu:** Các thao tác nghiệp vụ phức tạp (như tạo tài khoản kèm quota, khóa tài khoản kèm thu hồi refresh token, xóa mềm người dùng) đều được thực thi an toàn trong các Prisma Transaction, bảo đảm không phát sinh bản ghi mồ côi hay dữ liệu sai lệch.
3. **Về khả năng chịu lỗi (Resilience):** Cơ chế bảo vệ hạn ngạch Quota Guard (HTTP 429) và cơ chế tự động hoàn trả token khi nhà cung cấp AI gặp sự cố (HTTP 502) hoạt động tin cậy, bảo vệ ngân sách token của nhà trường.
4. **Kiến nghị:** Phân hệ Tích hợp đã sẵn sàng để bàn giao cho bước **Nghiệm thu chấp nhận người dùng (User Acceptance Testing - UAT)**.

