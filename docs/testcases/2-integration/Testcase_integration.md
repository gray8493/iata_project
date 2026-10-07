# TÀI LIỆU KỊCH BẢN KIỂM THỬ TÍCH HỢP HỆ THỐNG TOÀN DIỆN (COMPREHENSIVE INTEGRATION TEST SPECIFICATION)

# DỰ ÁN: AITA – HỆ THỐNG CHẤM ĐIỂM & ĐÁNH GIÁ TỰ ĐỘNG DÀNH CHO GIẢNG VIÊN (AUTOMATED GRADING & ASSESSMENT TOOL)

# MÃ TÀI LIỆU: SYS_IT – SYSTEM INTEGRATION TEST SUITE

# CẤP ĐỘ KIỂM THỬ: KIỂM THỬ TÍCH HỢP LIÊN PHÂN HỆ (CROSS-MODULE INTEGRATION TEST - IT)

---

## 1. THÔNG TIN CHUNG

- **HỆ THỐNG KIỂM THỬ:** Nền tảng AITA (Hệ sinh thái tích hợp 3 phân hệ: Web Server Backend NestJS Modular Monolith & PostgreSQL Neon Serverless Cloud, Web Admin Dashboard Next.js, Desktop App Client PyQt6/Python Local-First SQLite3).
- **CÁC DỊCH VỤ & MODULE TÍCH HỢP LIÊN QUAN:**
  - **Phân hệ Máy chủ Trung tâm & Điều phối AI (Web Server Backend - NestJS):**
    - `AuthModule`: Quản lý xác thực định danh tập trung, cấp phát & thẩm định cặp JWT Tokens (Access Token & Refresh Token Rotation), mã hóa mật khẩu một chiều chuẩn Bcrypt, kiểm soát phân quyền đa cấp RBAC (`ADMIN`, `INSTRUCTOR`) qua `JwtAuthGuard` và `RolesGuard`.
    - `UsersModule`: Quản lý danh mục tài khoản Giảng viên và Quản trị viên, hỗ trợ khóa/mở khóa tài khoản thời gian thực (`is_active`), cơ chế xóa mềm (`is_deleted`, `deleted_at`) và bảo toàn toàn vẹn dữ liệu.
    - `AiGatewayModule`: Đóng vai trò AI Hub trung tâm lưu trữ bảo mật Google Gemini API Key tại máy chủ, tích hợp `AiGatewayGuard` kiểm soát hạn ngạch Token hàng ngày (`daily_token_limit`), ngăn chặn nghẽn mạng Rate Limit (429), điều phối các tác vụ sinh testcase biên (`generate-testcases`), phân tích lỗi sư phạm On-Demand (`review-code`), thẩm định đạo văn vòng 2 (`verify-plagiarism`) và đánh giá thẩm mỹ giao diện Web Multimodal (`evaluate-web-ui`).
    - `AuditLogsModule` & `ReportsModule`: Ghi nhận nhật ký kiểm toán tiêu thụ Token AI chi tiết vào bảng `AI_QUOTA_LOGS`, cung cấp API báo cáo tổng hợp toàn trường (`/admin/reports/overview`) cho Quản trị viên.
    - `PrismaService` & `PostgreSQL (Neon Cloud)`: Tầng truy xuất dữ liệu trung tâm, thực thi giao dịch ACID và ràng buộc khóa ngoại an toàn.
  - **Phân hệ Ứng dụng Máy trạm Giảng viên (Desktop App Client - PyQt6 / Python):**
    - `AuthClientService`: Kết nối RESTful API với Backend, quản lý lưu trữ an toàn Token trong bộ nhớ phiên, xử lý tự động gia hạn phiên (Auto-Refresh Token).
    - `SessionClassService`: Quản lý đợt chấm bài, thông tin lớp học và môn học (`PRF`, `PRO`, `DSA`, `PHP`, `WEB`) lưu trữ trực tiếp vào CSDL cục bộ `LOCAL_CLASSES`.
    - `CsvService`: Đọc và thẩm định định dạng file `students.csv` chuẩn 2 cột (`MSSV`, `File`), kiểm tra tính hợp lệ của thư mục bài nộp, thực hiện giao dịch ghi vào `LOCAL_STUDENT_SUBMISSIONS` và kết xuất bảng điểm hoàn chỉnh ra `results.csv` / Excel `.xlsx`.
    - `TestcaseService`: Quản lý bộ kiểm thử Black-box (chỉ cần cặp `INPUT` và `OUTPUT kỳ vọng`, không cần code giải mẫu), nạp/xuất qua file `testcases.json`, đồng bộ với dữ liệu sinh tự động từ Gemini AI vào `LOCAL_TESTCASES`.
    - `MatchingEngineService`: Động cơ so khớp kết quả đầu ra theo Strategy Pattern gồm 7 chiến lược độc lập: `ExactMatch`, `IgnoreWhitespace`, `CaseInsensitive`, `FloatingPointTolerance`, `UnorderedTokens`, `RegexPattern`, `SpecialJudge`.
    - `SandboxExecutionEngine`: Môi trường thực thi an toàn đa tiến trình (`QThread`), sử dụng Factory Pattern (`RunnerFactory`) khởi tạo các Runner tương ứng (`CRunner`, `JavaRunner`, `PythonRunner`, `WebRunner`), cô lập subprocess gọi trình biên dịch của Hệ điều hành (`GCC/MinGW`, `Javac/JVM`, `Python Runtime`), kết hợp thư viện `psutil` đo lường thời gian chạy (ms) và dung lượng RAM (MB), cưỡng chế ngắt tiến trình bắt lỗi `TLE` và `MLE`.
    - `WebRubricEngine`: Phân hệ chấm bài tập Web kết hợp Playwright Chromium Headless render trang, BeautifulSoup4 phân tích DOM cấu trúc HTML, TinyCSS2 lint cú pháp CSS W3C và Gemini Vision đánh giá giao diện.
    - `PlagiarismEngine`: Cơ chế phát hiện gian lận 2 vòng: Vòng 1 phân tích cây cú pháp trừu tượng AST (Tokenization & Winnowing MOSS-like) chạy 100% offline tại máy trạm; Vòng 2 kích hoạt gửi cặp bài nghi vấn vượt ngưỡng (> 80%) lên Gemini AI Hub để lấy bằng chứng đối soát.
    - `LocalDatabaseService (SQLite3)`: Cơ sở dữ liệu cục bộ quản lý giao dịch ACID, chỉ mục tối ưu truy vấn đợt chấm, đảm bảo nguyên tắc bảo mật Local-First: Mã nguồn và điểm thi của sinh viên tuyệt đối không bị tải lên đám mây.
  - **Phân hệ Giao diện Quản trị Cấp cao (Web Admin Dashboard - Next.js):**
    - Cổng thông tin nội bộ dành riêng cho Quản trị viên: Quản lý người dùng, gán hạn ngạch AI Quota, giám sát biểu đồ sử dụng Token và nhật ký kiểm toán hệ thống.
  - **Dịch vụ Ngoại vi & Cơ sở Dữ liệu Phụ thuộc:**
    - `PostgreSQL (Neon Serverless Cloud)`: CSDL quan hệ trung tâm quản lý tài khoản, cấu hình hạn ngạch và nhật ký kiểm toán.
    - `SQLite3 Local Database Engine`: CSDL quan hệ cục bộ nhúng trong Desktop App.
    - `Google Gemini AI API (gemini-1.5-flash & gemini-1.5-pro/vision)`: Trợ lý AI đám mây sinh testcase biên, phân tích lỗi sư phạm, đối soát đạo văn và chấm giao diện.
    - `OS Subprocess & Compilers`: MinGW GCC (C), OpenJDK Javac & JVM (Java), Python 3.11+ Interpreter.
    - `Playwright Headless Chromium Engine`: Môi trường giả lập trình duyệt chạy kiểm thử bài thi Web Frontend.
- **MÔ TẢ NGHIỆP VỤ TÍCH HỢP:** Kiểm thử toàn diện sự phối hợp hoạt động, tính toàn vẹn dữ liệu, giao dịch (Transactions & Rollbacks), khả năng tự phục hồi khi dịch vụ ngoài gián đoạn (Resilience & Graceful Degradation), cơ chế ủy quyền đa cấp (RBAC), kiểm soát hạn ngạch Token AI (Quota Guards) và tính nhất quán giữa 3 phân hệ (Desktop App, Web Backend, Web Admin) xuyên suốt chu trình quản lý tài khoản, nạp đề bài, nạp danh sách sinh viên, thực thi sandbox chấm điểm đa ngôn ngữ và kết xuất bảng điểm.
- **NGƯỜI THỰC HIỆN / VIẾT TESTCASE:** Đội ngũ Đảm bảo Chất lượng Phần mềm (QA/QC Team) - Dự án AITA.
- **TẬP TIN ĐẶC TẢ LIÊN QUAN:**
  - Tổng quan kiến trúc hệ thống: [system-overview.md](file:///c:/AITA/iata_project/docs/architecture/system-overview.md)
  - Thiết kế Cơ sở dữ liệu: [database_schema.md](file:///c:/AITA/iata_project/docs/architecture/database_schema.md)
  - Quy chuẩn phản hồi & Mã lỗi API: [api-response-codes.md](file:///c:/AITA/iata_project/docs/architecture/api-response-codes.md)
  - Đặc tả API chi tiết: [api-specification.md](file:///c:/AITA/iata_project/docs/apis/api-specification.md)
  - Đặc tả Tác nhân & Use Cases: [actors_and_use_cases.md](file:///c:/AITA/iata_project/docs/architecture/actors_and_use_cases.md)
  - Mô tả chi tiết Use Cases: [use_case_descriptions.md](file:///c:/AITA/iata_project/docs/architecture/use_case_descriptions.md)
  - Thiết kế Mẫu kiến trúc: [design-patterns.md](file:///c:/AITA/iata_project/docs/architecture/design-patterns.md)
  - Quy tắc viết testcase dự án: [testcase-rules.md](file:///c:/AITA/iata_project/rules/testcase-rules.md)
- **MÔI TRƯỜNG KIỂM THỬ:** PostgreSQL Local / Neon Test Database, SQLite3 In-Memory / File Test Engine, Mock Google Gemini GenAI SDK / WireMock Provider, Jest & Supertest (Backend Integration), Pytest & pytest-mock / QTest (Desktop Client Integration) trên nền tảng Windows 11 x64.

---

## 2. BẢNG MA TRẬN KỊCH BẢN KIỂM THỬ TÍCH HỢP (INTEGRATION TEST SUITE)

| Mã Testcase | Tên Kịch Bản Tích Hợp | Các Thành Phần Tương Tác | Dữ Liệu Đầu Vào Chính | Kết Quả Tích Hợp Kỳ Vọng | Trạng Thái |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **IT01_Admin_User_Lifecycle** | Quản trị viên khởi tạo tài khoản Giảng viên và cấp phát hạn ngạch Token AI ban đầu | Web Admin $\leftrightarrow$ UsersModule $\leftrightarrow$ Prisma $\leftrightarrow$ Neon DB | `POST /api/v1/admin/users` (thông tin GV, `daily_token_quota`) | Tạo bản ghi `USERS`, tự động cấp `AI_QUOTA_CONFIGS`, HTTP 201 |  |
| **IT02_Admin_Disable_User_Revoke** | Khóa tài khoản Giảng viên thu hồi quyền truy cập API Gateway tức thì | AdminController $\leftrightarrow$ UsersService $\leftrightarrow$ JwtAuthGuard $\leftrightarrow$ Neon DB | `PUT /api/v1/admin/users/:id` `{ "is_active": false }` | Cập nhật `is_active=false`, Desktop App dùng token cũ bị chặn với HTTP 403 `AUTH_ACCOUNT_DISABLED` |  |
| **IT03_Admin_Quota_Allocation** | Admin điều chỉnh hạn ngạch Token AI và áp dụng ràng buộc thời gian thực | AdminController $\leftrightarrow$ AiGatewayModule $\leftrightarrow$ Prisma $\leftrightarrow$ Neon DB | `PUT /api/v1/ai/quota-config` (`user_id`, `daily_token_limit`) | Cập nhật `AI_QUOTA_CONFIGS`, AiGatewayGuard áp dụng hạn mức mới cho Giảng viên |  |
| **IT04_Desktop_Auth_Sync** | Giảng viên đăng nhập Desktop App qua REST API, xác thực JWT và kiểm tra Quota AI | Desktop App $\leftrightarrow$ AuthController $\leftrightarrow$ AiGatewayController $\leftrightarrow$ Neon DB | `POST /api/v1/auth/login` $\rightarrow$ `GET /api/v1/ai/quota` | Trả về Access Token, Refresh Token, đồng bộ thông tin hạn ngạch AI còn lại trong ngày |  |
| **IT05_Session_CSV_Import_LocalDB** | Khởi tạo đợt chấm, nạp danh sách sinh viên từ `students.csv` và lưu an toàn vào SQLite | Desktop UI $\leftrightarrow$ CsvService $\leftrightarrow$ File System $\leftrightarrow$ Local SQLite | File `students.csv` (MSSV, File) + Thư mục bài nộp mã nguồn | Tạo bản ghi `LOCAL_CLASSES`, lưu danh sách vào `LOCAL_STUDENT_SUBMISSIONS`, xác thực file tồn tại |  |
| **IT06_Manual_Testcase_Config** | Nạp bộ testcase Black-box thủ công / JSON và lưu cấu hình điểm số vào Local DB | Desktop UI $\leftrightarrow$ TestcaseService $\leftrightarrow$ Local SQLite | Bảng Testcase (Input, Expected Output, Time Limit, Mem Limit) | Lưu danh sách testcase vào `LOCAL_TESTCASES`, sẵn sàng cấp phát cho Runner |  |
| **IT07_AI_Generate_Boundary_Testcases** | Nhập đề bài trên Desktop App, Gemini AI sinh bộ testcase biên và trừ hạn ngạch Token | Desktop App $\leftrightarrow$ AiGatewayService $\leftrightarrow$ Gemini API $\leftrightarrow$ Local DB | `POST /api/v1/ai/generate-testcases` (đề bài, ngôn ngữ, count) | Gemini sinh JSON testcase biên, ghi log `AI_QUOTA_LOGS`, trừ quota, nạp vào `LOCAL_TESTCASES` |  |
| **IT08_Batch_Grading_C_Execution** | Chấm bài C hàng loạt: Biên dịch GCC, chạy subprocess qua hàm `main()`, so khớp `ExactMatch` | Desktop App $\leftrightarrow$ CRunner $\leftrightarrow$ Subprocess $\leftrightarrow$ psutil $\leftrightarrow$ Local DB | Thư mục bài nộp `.c`, bộ testcase C, Strategy `ExactMatch` | Biên dịch thành công, đo thời gian/RAM, so khớp kết quả chuẩn xác, ghi nhận điểm vào `LOCAL_GRADING_RESULTS` |  |
| **IT09_Batch_Grading_Java_Memory_Tracking** | Chấm bài Java thuật toán DSA: Biên dịch Javac, đo lường RAM/CPU, so khớp `FloatingPoint` | Desktop App $\leftrightarrow$ JavaRunner $\leftrightarrow$ JVM $\leftrightarrow$ psutil $\leftrightarrow$ MatchingEngine | Thư mục bài nộp `.java`, bộ testcase số thực, Tolerance $10^{-5}$ | Chạy JVM, kiểm soát heap RAM, so khớp dung sai số thực thành công, ghi nhận verdict `AC` |  |
| **IT10_Batch_Grading_Python_Unordered_Tokens** | Chấm bài Python: Thực thi script, so khớp kết quả danh sách không phân biệt thứ tự | Desktop App $\leftrightarrow$ PythonRunner $\leftrightarrow$ Python 3.11 $\leftrightarrow$ MatchingEngine | Thư mục bài `.py`, testcase có đầu ra mảng token đảo thứ tự | Runner nạp stdin, hứng stdout, Strategy `UnorderedTokens` đánh giá `AC` chính xác |  |
| **IT11_Web_Assignment_Grading_Multimodal** | Chấm bài tập Web: Playwright render, BeautifulSoup + TinyCSS2 lint, Gemini Vision chấm UI | Desktop App $\leftrightarrow$ Playwright $\leftrightarrow$ WebRubric $\leftrightarrow$ Gemini Vision | Thư mục web (HTML/CSS/JS), ảnh chụp màn hình, Rubric | Trích xuất DOM & CSS, gửi screenshot lên `POST /ai/evaluate-web-ui`, tổng hợp điểm Rubric 4 thành phần |  |
| **IT12_OnDemand_AI_CodeReview_WA** | Giảng viên bấm xem bài lỗi `WA`, AI phân tích nguyên nhân và xuất nhận xét sư phạm | Desktop UI $\leftrightarrow$ AiGatewayService $\leftrightarrow$ Gemini 1.5 Flash $\leftrightarrow$ Local DB | `POST /api/v1/ai/review-code` (code sinh viên, testcase trượt) | Trả về dòng code lỗi nghi vấn, nhận xét sư phạm, trừ token, lưu nhận xét vào kết quả chấm |  |
| **IT13_Plagiarism_TwoStage_Filter** | Quét đạo văn 2 vòng: Vòng 1 lọc AST Winnowing offline, Vòng 2 Gemini AI xác minh cặp >80% | Desktop App $\leftrightarrow$ AST Winnowing $\leftrightarrow$ Gemini API $\leftrightarrow$ Local DB | Toàn bộ bài nộp của lớp, ngưỡng nghi vấn tương đồng > 80% | Vòng 1 lọc AST trong 0.5s ra cặp nghi vấn; Vòng 2 gửi lên Gemini lấy bằng chứng đổi tên biến |  |
| **IT14_Gradebook_Export_CSV** | Tổng hợp kết quả từ CSDL cục bộ và xuất file bảng điểm `results.csv` kèm nhận xét AI | Desktop UI $\leftrightarrow$ CsvExportService $\leftrightarrow$ Local SQLite $\leftrightarrow$ File System | Dữ liệu chấm trong `LOCAL_GRADING_RESULTS`, yêu cầu xuất CSV | Xuất file `results.csv` chuẩn 7 cột (MSSV, File, Điểm, Testcase đạt, Verdict, Runtime, Nhận xét AI) |  |
| **IT15_Admin_AuditLogs_Reporting** | Quản trị viên xem báo cáo tổng hợp mức tiêu thụ Token AI toàn trường theo thời gian thực | Web Admin $\leftrightarrow$ ReportsController $\leftrightarrow$ Prisma $\leftrightarrow$ Neon DB | `GET /api/v1/admin/reports/overview` với token Admin | Tổng hợp dữ liệu từ `AI_QUOTA_LOGS`, thống kê tổng token đã dùng theo từng phân hệ chức năng |  |
| **IT16_AI_Service_Timeout_Resilience** | Google Gemini API bị nghẽn mạng quá 30 giây hoặc gián đoạn dịch vụ đám mây | AiGatewayService $\leftrightarrow$ Mock Gemini Client (Timeout > 30s / 503) | `POST /api/v1/ai/generate-testcases` | Ngắt an toàn, trả HTTP 502 `AI_SERVICE_UNAVAILABLE`, không trừ token quota, không crash app |  |
| **IT17_AI_Daily_Quota_Exceeded_Block** | Chặn yêu cầu gọi AI khi Giảng viên đã sử dụng hết hạn ngạch Token trong ngày | AiGatewayGuard $\leftrightarrow$ Prisma $\leftrightarrow$ Neon Database | `POST /api/v1/ai/generate-testcases` khi used >= limit | Trả về HTTP 429 `AI_QUOTA_EXCEEDED`, chặn ngay tại Guard trước khi gọi sang Gemini API |  |
| **IT18_Sandbox_Timeout_Quarantine_TLE** | Sinh viên nộp bài có vòng lặp vô hạn `while(true)`, ProcessWatcher kill tiến trình an toàn | SandboxEngine $\leftrightarrow$ ProcessWatcher $\leftrightarrow$ psutil $\leftrightarrow$ C/Py Runner | Bài nộp mã nguồn chứa vòng lặp vô hạn, Time Limit 1000ms | Cưỡng chế kill subprocess sau 1000ms, trả kết quả `TLE`, giải phóng CPU, không treo UI |  |
| **IT19_Sandbox_Memory_Limit_Exceeded_MLE** | Sinh viên nộp bài đệ quy vô hạn / tràn RAM, ProcessWatcher kill tiến trình bắt `MLE` | SandboxEngine $\leftrightarrow$ ProcessWatcher $\leftrightarrow$ psutil $\leftrightarrow$ Java/C Runner | Bài nộp đệ quy vô hạn ngốn RAM > 128MB (Memory Limit) | `psutil` phát hiện vượt ngưỡng bộ nhớ, kill tiến trình ngay lập tức, trả kết quả `MLE` an toàn |  |
| **IT20_CSV_Duplicate_MSSV_Rollback** | Nạp file `students.csv` chứa mã sinh viên trùng lặp kích hoạt Rollback toàn bộ | CsvImportService $\leftrightarrow$ Local SQLite Transaction | File `students.csv` có 2 dòng cùng chứa mã `SE180001` | Phát hiện trùng lặp, rollback giao dịch, không lưu bản ghi rác, báo lỗi `CSV_DUPLICATE_STUDENT` |  |
| **IT21_RBAC_Instructor_AdminEndpoint_Block** | Chặn Giảng viên cố tình gọi các API quản trị cấp cao của Quản trị viên | RolesGuard $\leftrightarrow$ UsersController $\leftrightarrow$ AiGatewayController | Request với Bearer token của `INSTRUCTOR` tới endpoint Admin | Trả về HTTP 403 `FORBIDDEN_ADMIN_ONLY`, từ chối truy cập và ghi log cảnh báo bảo mật |  |
| **IT22_Token_Expired_Refresh_Rotation** | Tự động làm mới Access Token khi hết hạn bằng Refresh Token Rotation an toàn | Desktop App $\leftrightarrow$ AuthController $\leftrightarrow$ Prisma $\leftrightarrow$ Neon DB | `POST /api/v1/auth/refresh` kèm `refresh_token` hợp lệ | Cấp Access Token & Refresh Token mới, thu hồi token cũ, duy trì phiên làm việc không ngắt quãng |  |
| **IT23_Soft_Delete_Cascade_Exclusion** | Xóa mềm tài khoản Giảng viên và tự động loại trừ khỏi mọi truy vấn danh sách hệ thống | AdminController $\leftrightarrow$ UsersService $\leftrightarrow$ Prisma $\leftrightarrow$ Neon DB | `DELETE /api/v1/admin/users/:id` | Cập nhật `is_deleted=true`, `deleted_at=now`, loại khỏi danh sách, bảo toàn nhật ký `AI_QUOTA_LOGS` |  |

---

## 3. CHI TIẾT CÁC KỊCH BẢN KIỂM THỬ TÍCH HỢP

---

### PHẦN I: CÁC KỊCH BẢN TÍCH HỢP THÀNH CÔNG (POSITIVE / INTEGRATION FLOW CASES)

---

#### 1. Nhóm Kịch Bản Quản Trị Hệ Thống & Vòng Đời Người Dùng (Admin & User Lifecycle Integration)

---

##### IT01_Admin_User_Lifecycle : KHỞI TẠO TÀI KHOẢN GIẢNG VIÊN VÀ TỰ ĐỘNG CẤP PHÁT HẠN NGẠCH TOKEN AI

- **ĐIỀU KIỆN TIÊN QUYẾT:**
  - Tài khoản Quản trị viên (`admin`) đã đăng nhập thành công trên Web Admin Dashboard, sở hữu Bearer JWT hợp lệ mang claim `role = "ADMIN"`.
  - Cơ sở dữ liệu trung tâm PostgreSQL (Neon Serverless Cloud) đang kết nối ổn định thông qua `PrismaService`.
  - Chưa tồn tại người dùng nào có tên đăng nhập `teacher_minh` trong bảng `users`.
- **CÁC THÀNH PHẦN THAM GIA TÍCH HỢP:**
  - `AdminController` & `UsersService` (Tiếp nhận yêu cầu tạo người dùng mới).
  - `PrismaService` (Thực thi giao dịch CSDL trung tâm).
  - Bảng `USERS` (Lưu thông tin hồ sơ người dùng và mật khẩu băm Bcrypt).
  - Bảng `AI_QUOTA_CONFIGS` (Tự động khởi tạo hạn ngạch Token hàng ngày cho Giảng viên).
- **DỮ LIỆU ĐẦU VÀO:**
  - **Tiêu đề (Headers):**
    - `Authorization: Bearer <token_admin_hop_le>`
    - `Content-Type: application/json`
  - **Endpoint & Method:** `POST /api/v1/admin/users`
  - **Dữ liệu thân (Body JSON):**
    ```json
    {
      "username": "teacher_minh",
      "password": "MinhPassword2026@",
      "full_name": "Phạm Quang Minh",
      "email": "minhpq@fe.edu.vn",
      "role": "INSTRUCTOR",
      "daily_token_quota": 50000
    }
    ```
- **CÁC BƯỚC THỰC HIỆN:**
  1. Gửi yêu cầu HTTP **`POST`** tới endpoint: `/api/v1/admin/users` với dữ liệu cấu hình trên.
  2. `UsersService` kiểm tra tính duy nhất của `username` và `email`.
  3. Băm mật khẩu bằng Bcrypt với salt rounds = 10.
  4. Mở Prisma Transaction: Thực hiện ghi đồng thời bản ghi mới vào bảng `USERS` và bảng cấu hình hạn ngạch `AI_QUOTA_CONFIGS`.
  5. Đóng giao dịch và lắng nghe phản hồi Envelope từ máy chủ.
  6. Sử dụng tài khoản `teacher_minh` vừa tạo để gọi thử API Đăng nhập `POST /api/v1/auth/login`.
- **KẾT QUẢ MONG ĐỢI (ASSERTIONS):**
  - **Phản hồi API Admin:** Trả về **HTTP 201 (CREATED)** với cấu trúc chuẩn Envelope:
    ```json
    {
      "success": true,
      "status_code": 201,
      "message": "Tạo tài khoản người dùng mới thành công",
      "data": {
        "id": 10,
        "username": "teacher_minh",
        "full_name": "Phạm Quang Minh",
        "email": "minhpq@fe.edu.vn",
        "role": "INSTRUCTOR",
        "is_active": true,
        "created_at": "2026-10-06T08:00:00.000Z"
      },
      "timestamp": "2026-10-06T08:00:00.000Z"
    }
    ```
  - **Trạng thái Database (PostgreSQL Neon):**
    - Bảng `USERS`: Tồn tại bản ghi `username = "teacher_minh"`, trường `password_hash` không chứa mật khẩu thô, `role = "INSTRUCTOR"`, `is_active = true`, `is_deleted = false`.
    - Bảng `AI_QUOTA_CONFIGS`: Tự động tạo bản ghi có `user_id = 10`, `daily_token_limit = 50000`, `used_tokens_today = 0`, `last_reset_date = CURRENT_DATE`.
  - **Tương tác Xác thực Tích hợp:** Giảng viên đăng nhập thành công với mật khẩu `"MinhPassword2026@"`, nhận về cặp JWT Access Token và Refresh Token hợp lệ.
- **TRẠNG THÁI KIỂM THỬ:**

---

##### IT02_Admin_Disable_User_Revoke : KHÓA TÀI KHOẢN GIẢNG VIÊN VÀ CHẶN QUYỀN TRUY CẬP GATEWAY THỜI GIAN THỰC

- **ĐIỀU KIỆN TIÊN QUYẾT:**
  - Admin có token hợp lệ.
  - Tài khoản Giảng viên `teacher_minh` (ID: 10) đang hoạt động bình thường (`is_active = true`) và đang nắm giữ một Access Token hợp lệ còn thời hạn 24 giờ.
- **CÁC THÀNH PHẦN THAM GIA TÍCH HỢP:**
  - `AdminController` & `UsersService` (Thực thi cập nhật trạng thái người dùng).
  - `PostgreSQL (Neon Cloud)` (Cập nhật cột `is_active = false` trong bảng `USERS`).
  - `JwtAuthGuard` & API Gateway (Kiểm tra trạng thái kích hoạt tài khoản trong CSDL khi token gửi request tới).
- **DỮ LIỆU ĐẦU VÀO:**
  - **Tiêu đề (Headers):** `Authorization: Bearer <token_admin_hop_le>`
  - **Endpoint & Method:** `PUT /api/v1/admin/users/10`
  - **Body JSON:**
    ```json
    {
      "is_active": false
    }
    ```
- **CÁC BƯỚC THỰC HIỆN:**
  1. Quản trị viên gửi request khóa tài khoản qua API `PUT /api/v1/admin/users/10`.
  2. Backend cập nhật `is_active = false` cho người dùng ID 10 trong CSDL.
  3. Mô phỏng Desktop App của Giảng viên `teacher_minh` tiếp tục sử dụng Access Token cũ đã cấp trước đó để gửi request lấy hạn ngạch AI: `GET /api/v1/ai/quota`.
  4. Quan sát cách `JwtAuthGuard` và tầng Gateway phản hồi.
- **KẾT QUẢ MONG ĐỢI (ASSERTIONS):**
  - **Phản hồi Admin API:** Trả về **HTTP 200 (OK)** với message: `"Cập nhật tài khoản thành công"`, trường `data.is_active: false`.
  - **Trạng thái Database (PostgreSQL):** Bản ghi của người dùng ID 10 được cập nhật `is_active = false`.
  - **Thực thi Bảo mật Gateway:** Yêu cầu gọi API tiếp theo của `teacher_minh` bằng token cũ lập tức bị từ chối với **HTTP 403 (FORBIDDEN)** kèm cấu trúc lỗi chuẩn:
    ```json
    {
      "success": false,
      "status_code": 403,
      "error_code": "AUTH_ACCOUNT_DISABLED",
      "message": "Tài khoản của bạn đã bị vô hiệu hóa. Vui lòng liên hệ Quản trị viên.",
      "details": null,
      "timestamp": "2026-10-06T08:05:00.000Z"
    }
    ```
  - **Phản ứng Desktop App:** Bắt mã lỗi `AUTH_ACCOUNT_DISABLED`, tự động xóa token lưu trong phiên và điều hướng về màn hình Đăng nhập.
- **TRẠNG THÁI KIỂM THỬ:**

---

##### IT03_Admin_Quota_Allocation : ĐIỀU CHỈNH HẠN NGẠCH TOKEN AI VÀ THỰC THI RÀNG BUỘC KIỂM SOÁT TỨC THÌ

- **ĐIỀU KIỆN TIÊN QUYẾT:**
  - Giảng viên `teacher_hung` đang có cấu hình hạn ngạch 50,000 token/ngày trong bảng `AI_QUOTA_CONFIGS`.
  - Admin đăng nhập với token hợp lệ.
- **CÁC THÀNH PHẦN THAM GIA TÍCH HỢP:**
  - `AiGatewayController` & `AiGatewayService` (Tiếp nhận cấu hình hạn ngạch).
  - `PostgreSQL (Neon Cloud)` (Bảng `AI_QUOTA_CONFIGS`).
  - `AiGatewayGuard` (Đọc hạn ngạch để áp dụng kiểm tra khi Giảng viên gọi các dịch vụ AI).
- **DỮ LIỆU ĐẦU VÀO:**
  - **Tiêu đề (Headers):** `Authorization: Bearer <token_admin_hop_le>`
  - **Endpoint & Method:** `PUT /api/v1/ai/quota-config`
  - **Body JSON:**
    ```json
    {
      "user_id": 2,
      "daily_token_limit": 100000
    }
    ```
- **CÁC BƯỚC THỰC HIỆN:**
  1. Quản trị viên gửi request nâng hạn mức Token AI cho `teacher_hung` lên 100,000 token.
  2. Kiểm tra phản hồi từ API cập nhật hạn ngạch.
  3. Giảng viên `teacher_hung` gửi request kiểm tra hạn ngạch của mình qua `GET /api/v1/ai/quota`.
- **KẾT QUẢ MONG ĐỢI (ASSERTIONS):**
  - **Phản hồi Admin API:** Trả về **HTTP 200 (OK)**, message: `"Cập nhật cấu hình hạn ngạch thành công"`.
  - **Trạng thái Database (PostgreSQL):** Bảng `AI_QUOTA_CONFIGS` của user 2 ghi nhận `daily_token_limit = 100000`.
  - **Phản hồi Giảng viên API:** Endpoint `GET /api/v1/ai/quota` trả về `daily_limit_tokens: 100000`, phản ánh ngay lập tức hạn mức mới mà không cần khởi động lại máy chủ.
- **TRẠNG THÁI KIỂM THỬ:**

---

#### 2. Nhóm Kịch Bản Xác Thực Client & Quản Lý Đợt Chấm Cục Bộ (Auth Sync & Session Management)

---

##### IT04_Desktop_Auth_Sync : GIẢNG VIÊN ĐĂNG NHẬP DESKTOP APP QUA REST API VÀ ĐỒNG BỘ THÔNG TIN HẠN NGẠCH

- **ĐIỀU KIỆN TIÊN QUYẾT:**
  - Tài khoản Giảng viên `teacher_hung` đã được kích hoạt trong CSDL trung tâm (`is_active = true`, `role = "INSTRUCTOR"`).
  - Desktop App Client (PyQt6) khởi động và sẵn sàng kết nối qua mạng Internet tới máy chủ Web Backend NestJS.
- **CÁC THÀNH PHẦN THAM GIA TÍCH HỢP:**
  - `Desktop App AuthClientService`.
  - `AuthController` & `JwtService` (Web Backend).
  - `AiGatewayController` & `PostgreSQL (Neon DB)`.
- **DỮ LIỆU ĐẦU VÀO:**
  - **Bước 1 (Đăng nhập):**
    - Endpoint: `POST /api/v1/auth/login`
    - Body JSON:
      ```json
      {
        "username": "teacher_hung",
        "password": "Password123@"
      }
      ```
  - **Bước 2 (Kiểm tra Quota AI sau khi có token):**
    - Endpoint: `GET /api/v1/ai/quota`
    - Headers: `Authorization: Bearer <access_token_vua_nhan>`
- **CÁC BƯỚC THỰC HIỆN:**
  1. Desktop App gửi thông tin đăng nhập lên Web Server Backend.
  2. Backend thẩm định thông tin, trả về `access_token` và `refresh_token`.
  3. Desktop App lưu token an toàn trong Session Memory và tự động gửi request truy vấn hạn ngạch AI hiện tại.
  4. Hiển thị thông tin Giảng viên và thanh phần trăm Token AI còn lại lên thanh trạng thái (Status Bar) của Desktop App.
- **KẾT QUẢ MONG ĐỢI (ASSERTIONS):**
  - **Đăng nhập:** HTTP 200 (OK), nhận `access_token` hợp lệ có thời hạn 86400s (24h), thông tin user chứa `role: "INSTRUCTOR"`.
  - **Truy vấn Quota:** HTTP 200 (OK), trả về đầy đủ các trường: `daily_limit_tokens: 50000`, `used_tokens_today`, `remaining_tokens`, `reset_at_utc`.
  - **Trạng thái Desktop App:** UI hiển thị badge người dùng: `"GV: Nguyễn Văn Hùng | AI Quota: 37,550/50,000 tokens còn lại (75.1%)"`.
- **TRẠNG THÁI KIỂM THỬ:**

---

##### IT05_Session_CSV_Import_LocalDB : NẠP DANH SÁCH SINH VIÊN TỪ FILE CSV CHUẨN VÀ LƯU AN TOÀN VÀO CSDL CỤC BỘ

- **ĐIỀU KIỆN TIÊN QUYẾT:**
  - Giảng viên đã mở Desktop App và chọn môn học Lập trình cơ sở (`course_code: "PRF"`).
  - File `students.csv` chuẩn bị sẵn gồm đúng 2 cột `MSSV,File` chứa 3 sinh viên (`SE180001`, `SE180002`, `SE180003`).
  - Thư mục bài nộp chứa đầy đủ 3 file mã nguồn tương ứng: `SE180001_Q1.c`, `SE180002_Q1.c`, `SE180003_Q1.c`.
  - File CSDL cục bộ SQLite3 (`aita_local.db`) đã được khởi tạo các bảng `LOCAL_CLASSES` và `LOCAL_STUDENT_SUBMISSIONS`.
- **CÁC THÀNH PHẦN THAM GIA TÍCH HỢP:**
  - `Desktop App SessionUI` & `CsvService`.
  - Hệ thống tệp tin cục bộ Hệ điều hành (File System).
  - Cơ sở dữ liệu Cục bộ SQLite3 (`LOCAL_CLASSES`, `LOCAL_STUDENT_SUBMISSIONS`).
- **DỮ LIỆU ĐẦU VÀO:**
  - **Tên đợt chấm / Lớp học:** `"SE1801_PRF192_PE"`
  - **Môn học:** `"PRF"`
  - **Nội dung file `students.csv`:**
    ```csv
    MSSV,File
    SE180001,SE180001_Q1.c
    SE180002,SE180002_Q1.c
    SE180003,SE180003_Q1.c
    ```
- **CÁC BƯỚC THỰC HIỆN:**
  1. Giảng viên nhập tên đợt chấm, chọn môn học và bấm "Chọn file students.csv".
  2. Bấm "Chọn thư mục bài nộp" trỏ tới folder chứa các file `.c`.
  3. `CsvService` mở file CSV, thẩm định tính hợp lệ của Header (chỉ gồm 2 cột `MSSV,File`), kiểm tra mã hóa UTF-8.
  4. Quét kiểm tra sự tồn tại vật lý của từng file bài làm trong thư mục.
  5. Mở SQLite Transaction: Tạo 1 bản ghi trong `LOCAL_CLASSES` và ghi 3 bản ghi vào `LOCAL_STUDENT_SUBMISSIONS`.
- **KẾT QUẢ MONG ĐỢI (ASSERTIONS):**
  - **Xử lý CSV:** Phân tích cú pháp thành công 3/3 sinh viên, không có lỗi định dạng hay thiếu file.
  - **Trạng thái Database Cục bộ (SQLite3):**
    - Bảng `LOCAL_CLASSES`: Có 1 bản ghi mới với `class_name = "SE1801_PRF192_PE"`, `course_code = "PRF"`, `is_deleted = 0`.
    - Bảng `LOCAL_STUDENT_SUBMISSIONS`: Lưu 3 bản ghi tương ứng với 3 MSSV, mỗi bản ghi lưu đầy đủ đường dẫn tuyệt đối của file và nội dung mã nguồn đọc từ đĩa.
  - **Nguyên tắc Bảo mật Local-First:** Toàn bộ thông tin sinh viên và mã nguồn chỉ lưu trữ trên đĩa cứng cục bộ của Giảng viên, tuyệt đối không gửi bất kỳ gói tin nào chứa dữ liệu sinh viên lên Cloud.
- **TRẠNG THÁI KIỂM THỬ:**

---

##### IT06_Manual_Testcase_Config : NẠP BỘ TESTCASE BLACK-BOX THỦ CÔNG VÀ LƯU CẤU HÌNH ĐIỂM VÀO SQLITE

- **ĐIỀU KIỆN TIÊN QUYẾT:**
  - Đợt chấm `SE1801_PRF192_PE` (ID: 1) đã được tạo thành công từ testcase `IT05`.
  - Giảng viên đang mở tab "Cấu hình Testcase".
- **CÁC THÀNH PHẦN THAM GIA TÍCH HỢP:**
  - `Desktop App TestcaseUI` & `TestcaseService`.
  - Cơ sở dữ liệu Cục bộ SQLite3 (`LOCAL_TESTCASES`).
- **DỮ LIỆU ĐẦU VÀO:**
  - Bộ 2 testcase Black-box (chỉ cần cặp Input và Output kỳ vọng):
    - Testcase 1: `input = "5\n"`, `expected_output = "15"`, `time_limit_ms = 1000`, `memory_limit_mb = 128`, `weight = 5.0`.
    - Testcase 2: `input = "10\n"`, `expected_output = "55"`, `time_limit_ms = 1000`, `memory_limit_mb = 128`, `weight = 5.0`.
- **CÁC BƯỚC THỰC HIỆN:**
  1. Giảng viên thêm từng dòng testcase trên giao diện hoặc bấm "Import testcases.json".
  2. `TestcaseService` thẩm định dữ liệu: `input` và `expected_output` không rỗng, `time_limit_ms > 0`, `weight > 0`.
  3. Ghi các testcase vào bảng `LOCAL_TESTCASES` theo `class_id = 1`.
- **KẾT QUẢ MONG ĐỢI (ASSERTIONS):**
  - **Thẩm định dữ liệu:** Hợp lệ 100%, tổng trọng số điểm = 10.0 điểm.
  - **Trạng thái Database Cục bộ (SQLite3):** Bảng `LOCAL_TESTCASES` lưu 2 bản ghi có `class_id = 1`, liên kết chặt chẽ với đợt chấm, sẵn sàng nạp cho động cơ chấm tự động.
- **TRẠNG THÁI KIỂM THỬ:**

---

#### 3. Nhóm Kịch Bản Tích Hợp Trí Tuệ Nhân Tạo Gemini AI Hub (AI-Assisted Capabilities)

---

##### IT07_AI_Generate_Boundary_Testcases : NHẬP ĐỀ BÀI TRÊN DESKTOP APP, GEMINI AI SINH TESTCASE BIÊN VÀ ĐỒNG BỘ LOCAL DB

- **ĐIỀU KIỆN TIÊN QUYẾT:**
  - Giảng viên đã đăng nhập và sở hữu token hợp lệ, còn hạn ngạch Token AI trong ngày.
  - Mock Gemini AI Hub (hoặc Google Gemini API `gemini-1.5-flash`) sẵn sàng nhận kết nối.
  - Đợt chấm ID: 1 đang mở trên Desktop App.
- **CÁC THÀNH PHẦN THAM GIA TÍCH HỢP:**
  - `Desktop App AIClient` $\leftrightarrow$ `Web Backend AiGatewayController` & `AiGatewayService`.
  - `GoogleGenAI Client SDK` (Gemini 1.5 Flash).
  - `PostgreSQL (Neon Cloud)` (Bảng `AI_QUOTA_CONFIGS`, `AI_QUOTA_LOGS`).
  - `SQLite3 Local Database` (Bảng `LOCAL_TESTCASES`).
- **DỮ LIỆU ĐẦU VÀO:**
  - **Endpoint & Method:** `POST /api/v1/ai/generate-testcases`
  - **Headers:** `Authorization: Bearer <access_token_giang_vien>`
  - **Body JSON:**
    ```json
    {
      "problem_description": "Viết chương trình nhập vào số nguyên dương N (1 <= N <= 10^6). Tính tổng các ước số của N.",
      "language": "C",
      "count": 3,
      "include_boundary": true
    }
    ```
- **CÁC BƯỚC THỰC HIỆN:**
  1. Giảng viên dán đề bài vào Desktop App và bấm "✨ AI Sinh Testcase Biên".
  2. Desktop App gửi request tới Web Backend AI Gateway.
  3. `AiGatewayGuard` kiểm tra Giảng viên còn đủ hạn ngạch Token.
  4. Backend chuyển tiếp prompt chuẩn hóa tới Google Gemini API `gemini-1.5-flash`.
  5. Gemini AI phân tích đề bài và trả về JSON danh sách 3 testcase biên kèm giải thích.
  6. Backend ghi log tiêu thụ 420 tokens vào `AI_QUOTA_LOGS`, cập nhật `used_tokens_today` trong `AI_QUOTA_CONFIGS`.
  7. Backend trả kết quả về Desktop App; Desktop App tự động nạp 3 testcase vào bảng `LOCAL_TESTCASES`.
- **KẾT QUẢ MONG ĐỢI (ASSERTIONS):**
  - **Phản hồi API:** HTTP 200 (OK), nhận mảng 3 testcase chứa các giá trị biên ($N = 1$, $N = 10^6$, $N = 999983$), `tokens_consumed: 420`.
  - **Trạng thái Database Trung tâm (PostgreSQL):** Bảng `AI_QUOTA_LOGS` lưu 1 bản ghi có `feature_type = "TESTCASE_GEN"`, `total_tokens = 420`; bảng `AI_QUOTA_CONFIGS` có `used_tokens_today` tăng thêm 420.
  - **Trạng thái Database Cục bộ (SQLite3):** Bảng `LOCAL_TESTCASES` được nạp tự động 3 dòng testcase với đầy đủ `input`, `expected_output` mà Giảng viên hoàn toàn không cần phải viết code giải mẫu.
- **TRẠNG THÁI KIỂM THỬ:**

---

##### IT12_OnDemand_AI_CodeReview_WA : GIẢNG VIÊN SOI BÀI SAI KẾT QUẢ (WA), AI PHÂN TÍCH LỖI VÀ XUẤT NHẬN XÉT SƯ PHẠM

- **ĐIỀU KIỆN TIÊN QUYẾT:**
  - Bài làm của sinh viên `SE180002` sau khi chấm bị trạng thái `WA` (Wrong Answer) do vòng lặp dừng ở `i < n` thay vì `i <= n`.
  - Giảng viên bấm vào chi tiết sinh viên đó trên bảng điểm và chọn nút `[✨ AI Phân tích lỗi]`.
- **CÁC THÀNH PHẦN THAM GIA TÍCH HỢP:**
  - `Desktop App ReviewDialog` & `AIClientService`.
  - `AiGatewayService` & `Gemini 1.5 Flash`.
  - `PostgreSQL (AI_QUOTA_LOGS)` & `SQLite3 (LOCAL_GRADING_RESULTS)`.
- **DỮ LIỆU ĐẦU VÀO:**
  - **Endpoint & Method:** `POST /api/v1/ai/review-code`
  - **Headers:** `Authorization: Bearer <access_token>`
  - **Body JSON:**
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
- **CÁC BƯỚC THỰC HIỆN:**
  1. Desktop App kích hoạt cơ chế Lazy Loading (chỉ gửi bài này, không gửi hàng loạt).
  2. Web Backend thẩm định request, gọi Gemini AI phân tích đoạn code ngắn kèm testcase bị trượt.
  3. Gemini AI chỉ ra dòng lỗi số 5 và sinh nhận xét sư phạm thân thiện bằng tiếng Việt.
  4. Backend ghi log 380 tokens vào `AI_QUOTA_LOGS` và trả phản hồi.
  5. Desktop App lưu nhận xét vào trường `ai_feedback` của bài nộp trong SQLite và hiển thị lên màn hình soi lỗi.
- **KẾT QUẢ MONG ĐỢI (ASSERTIONS):**
  - **Phản hồi API:** HTTP 200 (OK), nhận `suspected_error_line: 5`, `bug_category: "OFF_BY_ONE_ERROR"`, `pedagogical_feedback: "Em đã xử lý đúng thuật toán... kiểm tra lại điều kiện for(i=1; i<=n; i++)..."`.
  - **Tiết kiệm tài nguyên:** Chỉ tiêu tốn 380 tokens cho duy nhất 1 bài cần soi lỗi, loại bỏ hoàn toàn việc gọi AI lãng phí trong quá trình chấm hàng loạt cả lớp.
  - **Trạng thái Database Cục bộ:** Bản ghi của sinh viên `SE180002` trong `LOCAL_GRADING_RESULTS` được cập nhật cột `ai_feedback` đầy đủ.
- **TRẠNG THÁI KIỂM THỬ:**

---

##### IT13_Plagiarism_TwoStage_Filter : QUÉT ĐẠO VĂN 2 VÒNG: LỌC AST CỤC BỘ OFFLINE VÀ GỬI CẶP NGHI VẤN >80% LÊN AI

- **ĐIỀU KIỆN TIÊN QUYẾT:**
  - Lớp học có 2 bài nộp của sinh viên `SE180001` và `SE180003` có cấu trúc giải thuật giống hệt nhau, chỉ thay đổi tên biến `n` thành `m`, `sum` thành `total`.
- **CÁC THÀNH PHẦN THAM GIA TÍCH HỢP:**
  - `PlagiarismEngine` (Vòng 1: AST Tokenization & Winnowing MOSS-like chạy 100% offline).
  - `Desktop App AIClient` & `Web Backend AiGatewayModule`.
  - `Google Gemini AI API` (Vòng 2: Xác thực ngữ nghĩa chuyên sâu).
  - `Local Database SQLite` (Bảng `LOCAL_PLAGIARISM_REPORTS`).
- **DỮ LIỆU ĐẦU VÀO:**
  - Hai file mã nguồn: `SE180001_Q1.c` và `SE180003_Q1.c`.
  - Cấu hình ngưỡng nghi vấn: `threshold = 80.0%`.
- **CÁC BƯỚC THỰC HIỆN:**
  1. Giảng viên bấm nút "Quét Đạo Văn Lớp Học".
  2. **Vòng 1 (Offline)**: `PlagiarismEngine` phân tích AST của toàn bộ các cặp bài trong lớp, chuẩn hóa mã nguồn và tính độ tương đồng bằng thuật toán Winnowing trong 0.2 giây.
  3. Phát hiện cặp `SE180001` và `SE180003` có độ tương đồng AST đạt **92.5%** (> 80%).
  4. **Vòng 2 (AI Verification)**: Desktop App tự động chọn lọc duy nhất cặp nghi vấn này gửi lên API `POST /api/v1/ai/verify-plagiarism`.
  5. Gemini AI đối soát ngữ nghĩa, xác nhận hành vi sao chép và trích xuất bằng chứng kỹ thuật.
  6. Lưu báo cáo đạo văn hoàn chỉnh vào SQLite và hiển thị giao diện đối chiếu 2 cột code song song (Side-by-side Diff Viewer).
- **KẾT QUẢ MONG ĐỢI (ASSERTIONS):**
  - **Tối ưu hóa Token:** Toàn bộ lớp 40 sinh viên chỉ phát sinh đúng 1 request AI cho cặp bài nghi vấn, tiết kiệm hơn 99% chi phí token so với việc gửi tất cả bài lên AI.
  - **Phản hồi API:** HTTP 200 (OK), `is_plagiarized: true`, `confidence_percentage: 94.8%`, `evidence_summary: "Phát hiện đổi tên biến n -> m, sum -> total..."`.
  - **Trạng thái Database Cục bộ:** Bảng `LOCAL_PLAGIARISM_REPORTS` lưu báo cáo chi tiết kèm danh sách đoạn code trùng lặp để phục vụ lập biên bản vi phạm.
- **TRẠNG THÁI KIỂM THỬ:**

---

#### 4. Nhóm Kịch Bản Chấm Điểm Tự Động Đa Ngôn Ngữ & Sandbox Cô Lập (Grading Engine & Sandbox Runners)

---

##### IT08_Batch_Grading_C_Execution : CHẤM BÀI C HÀNG LOẠT: BIÊN DỊCH GCC, CHẠY QUA HÀM MAIN() VÀ SO KHỚP EXACT MATCH

- **ĐIỀU KIỆN TIÊN QUYẾT:**
  - Trình biên dịch MinGW GCC đã được cấu hình và nhận diện trong biến môi trường PATH.
  - 3 bài nộp C của sinh viên và bộ testcase từ testcase `IT06` sẵn sàng.
  - Chiến lược so khớp được chọn là `ExactMatchStrategy`.
- **CÁC THÀNH PHẦN THAM GIA TÍCH HỢP:**
  - `Desktop App BatchGradingWorker` (Đa luồng `QThread`).
  - `RunnerFactory` $\rightarrow$ `CRunner`.
  - `Subprocess Engine` (`gcc -O2`, `./SE180001_Q1.exe`).
  - `ProcessWatcher` (`psutil` giám sát thời gian và RAM).
  - `MatchingEngine` (`ExactMatchStrategy`).
  - `Local Database SQLite` (Bảng `LOCAL_GRADING_RESULTS`).
- **DỮ LIỆU ĐẦU VÀO:**
  - Thư mục bài nộp chứa file `SE180001_Q1.c`.
  - Bộ 2 testcase Black-box (Input: `5\n` -> Output: `15`; Input: `10\n` -> Output: `55`).
  - Time Limit: 1000ms, Memory Limit: 128MB.
- **CÁC BƯỚC THỰC HIỆN:**
  1. Giảng viên bấm nút "BẮT ĐẦU CHẤM BÀI".
  2. `CRunner` gọi lệnh biên dịch: `gcc SE180001_Q1.c -o SE180001_Q1.exe`.
  3. Kiểm tra biên dịch thành công (exit code = 0).
  4. Lần lượt khởi chạy tiến trình con `SE180001_Q1.exe`, nạp chuỗi `5\n` qua `stdin` vào hàm `main()`.
  5. Hứng chuỗi kết quả in ra từ `stdout` qua các hàm in chuẩn (`printf`).
  6. `ExactMatchStrategy` so khớp chuỗi thực tế nhận được với `expected_output`.
  7. Lặp lại với testcase 2, cộng dồn tổng điểm và ghi kết quả vào SQLite.
- **KẾT QUẢ MONG ĐỢI (ASSERTIONS):**
  - **Biên dịch:** Thành công, sinh file thực thi nhị phân tạm thời.
  - **Thực thi:** Thời gian chạy thực tế trung bình < 50ms, RAM tiêu thụ < 15MB.
  - **Đánh giá So khớp:** Cả 2 testcase đều trả về kết quả khớp tuyệt đối (`is_match = true`), bài làm đạt phán quyết **`AC` (Accepted)**, điểm số tuyệt đối: **10.0/10.0**.
  - **Trạng thái Database Cục bộ:** Bảng `LOCAL_GRADING_RESULTS` ghi nhận 2 bản ghi kết quả chi tiết từng testcase và tổng kết bài nộp của `SE180001`.
- **TRẠNG THÁI KIỂM THỬ:**

---

##### IT09_Batch_Grading_Java_Memory_Tracking : CHẤM BÀI JAVA THUẬT TOÁN: BIÊN DỊCH JAVAC, ĐO RAM VÀ SO KHỚP DUNG SAI SỐ THỰC

- **ĐIỀU KIỆN TIÊN QUYẾT:**
  - Môi trường OpenJDK 17+ (javac, java) sẵn sàng.
  - Bài nộp môn Cấu trúc dữ liệu & Giải thuật (DSA): `Q1.java` tính toán số thực (ví dụ diện tích hình tròn hoặc logarit).
  - Chiến lược so khớp: `FloatingPointToleranceStrategy` với dung sai epsilon $\epsilon = 10^{-5}$.
- **CÁC THÀNH PHẦN THAM GIA TÍCH HỢP:**
  - `RunnerFactory` $\rightarrow$ `JavaRunner`.
  - `Subprocess` (`javac Q1.java`, `java -Xmx128m Q1`).
  - `psutil Process Watcher`.
  - `FloatingPointToleranceStrategy`.
  - `Local Database SQLite`.
- **DỮ LIỆU ĐẦU VÀO:**
  - Testcase: `input = "3.5\n"`, `expected_output = "38.48451"`.
  - Bài sinh viên in ra qua `System.out.println`: `"38.484512"`.
- **CÁC BƯỚC THỰC HIỆN:**
  1. `JavaRunner` biên dịch file `Q1.java` sang bytecode `Q1.class`.
  2. Khởi chạy JVM với đối số hạn chế bộ nhớ `-Xmx128m`, truyền `3.5` vào luồng `stdin` (được đọc bởi `Scanner` trong `main()`).
  3. `psutil` đo lường mức RAM thực tế của tiến trình JVM.
  4. Hứng đầu ra `38.484512` từ `stdout`.
  5. `FloatingPointToleranceStrategy` so sánh hiệu số thực: $|38.484512 - 38.484510| = 0.000002 \le 10^{-5}$.
- **KẾT QUẢ MONG ĐỢI (ASSERTIONS):**
  - **Kết quả So khớp:** Đánh giá là **HỢP LỆ (AC)** do nằm trong giới hạn sai số cho phép của số thực.
  - **Đo lường Tài nguyên:** Ghi nhận chính xác bộ nhớ JVM tiêu thụ (ví dụ: 45.2 MB) và thời gian thực thi (ví dụ: 120 ms).
  - Lưu kết quả đầy đủ vào `LOCAL_GRADING_RESULTS`.
- **TRẠNG THÁI KIỂM THỬ:**

---

##### IT10_Batch_Grading_Python_Unordered_Tokens : CHẤM BÀI PYTHON: SO KHỚP DANH SÁCH KẾT QUẢ KHÔNG PHÂN BIỆT THỨ TỰ

- **ĐIỀU KIỆN TIÊN QUYẾT:**
  - Python 3.11+ Runtime sẵn sàng.
  - Bài nộp môn Python (`PHP`): `q1.py` tìm các số nguyên tố trong khoảng $[A, B]$.
  - Chiến lược so khớp: `UnorderedTokensStrategy` (các số in ra phân cách bởi khoảng trắng/xuống dòng nhưng không bắt buộc đúng thứ tự).
- **CÁC THÀNH PHẦN THAM GIA TÍCH HỢP:**
  - `PythonRunner` $\leftrightarrow$ `python q1.py`.
  - `UnorderedTokensStrategy`.
  - `Local Database SQLite`.
- **DỮ LIỆU ĐẦU VÀO:**
  - `input`: `"1 10\n"`
  - `expected_output`: `"2 3 5 7"`
  - Bài sinh viên in ra: `"7 5 3 2"` (do lưu trong `set` không có thứ tự).
- **CÁC BƯỚC THỰC HIỆN:**
  1. `PythonRunner` khởi chạy file script, truyền input qua `stdin`.
  2. Thu nhận output `"7 5 3 2"` từ `stdout`.
  3. `UnorderedTokensStrategy` bóc tách cả 2 chuỗi thành mảng các token độc lập và so sánh tập hợp đa phần tử (Multiset / Bag comparison).
- **KẾT QUẢ MONG ĐỢI (ASSERTIONS):**
  - Strategy xác định 2 tập hợp token chứa cùng các phần tử với số lần xuất hiện tương đương.
  - Phán quyết: **`AC` (Accepted)**, không bị trừ điểm oan do thứ tự in ra của thuật toán.
  - Cập nhật điểm tối đa cho sinh viên trong CSDL cục bộ.
- **TRẠNG THÁI KIỂM THỬ:**

---

##### IT11_Web_Assignment_Grading_Multimodal : CHẤM BÀI TẬP WEB TỰ ĐỘNG KẾT HỢP HEADLESS BROWSER, W3C LINT VÀ GEMINI VISION

- **ĐIỀU KIỆN TIÊN QUYẾT:**
  - Bài nộp của sinh viên gồm bộ file mã nguồn Web: `index.html`, `style.css`, `app.js`.
  - Môi trường kiểm thử có cài đặt thư viện Playwright Chromium, BeautifulSoup4 và TinyCSS2.
  - Tài khoản Giảng viên có quyền gọi API AI Hub.
- **CÁC THÀNH PHẦN THAM GIA TÍCH HỢP:**
  - `WebRunner` & `WebRubricEngine` (Desktop App).
  - `Playwright Headless Chromium Engine` (Khởi dựng giao diện và chụp ảnh).
  - `TinyCSS2` (Linter CSS W3C) & `BeautifulSoup4` (DOM Structure Validator).
  - `Web Backend AiGatewayModule` & `Google Gemini 1.5 Pro / Vision`.
  - `Local Database SQLite` (Bảng `LOCAL_WEB_GRADING_RESULTS`).
- **DỮ LIỆU ĐẦU VÀO:**
  - Thư mục chứa bài làm Web của sinh viên.
  - Rubric chấm gồm 4 thành phần:
    1. Cấu trúc HTML (Semantic tags): Trọng số 2.0 điểm.
    2. Chuẩn mực CSS (No inline styles, valid syntax): Trọng số 2.0 điểm.
    3. Tương tác JS (DOM Event Listeners): Trọng số 3.0 điểm.
    4. Thẩm mỹ giao diện & Bố cục (Gemini Vision đánh giá ảnh chụp): Trọng số 3.0 điểm.
- **CÁC BƯỚC THỰC HIỆN:**
  1. `WebRubricEngine` đọc file `index.html` bằng BeautifulSoup4 kiểm tra các thẻ `<nav>`, `<header>`, `<main>`, `<form>`.
  2. Đọc `style.css` bằng TinyCSS2 thẩm định cú pháp CSS W3C, xác nhận không có lỗi cú pháp.
  3. Khởi động Chromium qua Playwright ở chế độ Headless, nạp trang `index.html`, kích hoạt thử sự kiện click nút bấm để kiểm tra logic JavaScript.
  4. Playwright chụp ảnh màn hình trang web (`screenshot.png`), chuyển đổi sang chuỗi Base64.
  5. Gửi request `POST /api/v1/ai/evaluate-web-ui` lên Web Backend kèm ảnh Base64 và tiêu chí bố cục.
  6. Gemini Vision phân tích hình ảnh và trả về điểm số giao diện (ví dụ: 2.8 / 3.0 điểm).
  7. Tổng hợp điểm 4 thành phần thành điểm tổng thể (ví dụ: 9.3 / 10.0) và lưu vào `LOCAL_WEB_GRADING_RESULTS`.
- **KẾT QUẢ MONG ĐỢI (ASSERTIONS):**
  - **Phản hồi API AI:** HTTP 200 (OK), trả về `ui_score: 8.5` (tương ứng 2.55/3.0 điểm quy đổi), nhận xét bố cục cân đối và phối màu chuẩn mực.
  - **Trạng thái Database Cục bộ:** Bảng `LOCAL_WEB_GRADING_RESULTS` ghi nhận đầy đủ chi tiết điểm số từng thành phần (HTML, CSS, JS, UI/UX) và tổng điểm.
- **TRẠNG THÁI KIỂM THỬ:**

---

#### 5. Nhóm Kịch Bản Kết Xuất Bảng Điểm & Báo Cáo Kiểm Toán (Export & Audit Reporting)

---

##### IT14_Gradebook_Export_CSV : TỔNG HỢP KẾT QUẢ TỪ SQLITE VÀ XUẤT FILE BẢNG ĐIỂM RESULTS.CSV CHUẨN 7 CỘT

- **ĐIỀU KIỆN TIÊN QUYẾT:**
  - Toàn bộ sinh viên của lớp `SE1801_PRF192_PE` đã hoàn tất quá trình chấm điểm tự động.
  - Các bài có nhận xét từ AI đã được ghi nhận vào `LOCAL_GRADING_RESULTS`.
- **CÁC THÀNH PHẦN THAM GIA TÍCH HỢP:**
  - `Desktop App GradebookUI` & `CsvExportService`.
  - `SQLite3 Local Database` (Đọc dữ liệu chấm bài).
  - Hệ thống tệp tin cục bộ (File System ghi file `results.csv`).
- **DỮ LIỆU ĐẦU VÀO:**
  - Yêu cầu xuất file từ giao diện: Đường dẫn lưu file `D:/Grades/SE1801_results.csv`.
- **CÁC BƯỚC THỰC HIỆN:**
  1. Giảng viên bấm nút "XUẤT BẢNG ĐIỂM CSV".
  2. `CsvExportService` thực thi câu lệnh SQL SELECT liên kết giữa `LOCAL_STUDENT_SUBMISSIONS` và `LOCAL_GRADING_RESULTS`.
  3. Định dạng dữ liệu thành chuỗi CSV theo chuẩn 7 cột bắt buộc:
     - Cột 1: `MSSV`
     - Cột 2: `File`
     - Cột 3: `Điểm số`
     - Cột 4: `Số testcase đạt`
     - Cột 5: `Trạng thái`
     - Cột 6: `Thời gian chạy (ms)`
     - Cột 7: `Nhận xét từ AI Gemini`
  4. Ghi file ra ổ đĩa với bảng mã UTF-8 có BOM (Byte Order Mark) để hiển thị chuẩn tiếng Việt trên Microsoft Excel.
- **KẾT QUẢ MONG ĐỢI (ASSERTIONS):**
  - **File Đầu ra:** Tệp `SE1801_results.csv` được tạo thành công, dung lượng > 0 bytes.
  - **Toàn vẹn Dữ liệu:**
    - Sinh viên `SE180001`: Đạt `10.0`, `2/2`, `AC`, `35ms`, Nhận xét: `""`.
    - Sinh viên `SE180002`: Đạt `5.0`, `1/2`, `WA`, `42ms`, Nhận xét: `"Em đã xử lý đúng thuật toán... kiểm tra lại for(i=1; i<=n; i++)..."`.
  - Mở file trên Excel hoặc Notepad hiển thị đúng cấu trúc và không bị lỗi font tiếng Việt.
- **TRẠNG THÁI KIỂM THỬ:**

---

##### IT15_Admin_AuditLogs_Reporting : QUẢN TRỊ VIÊN XEM BÁO CÁO TỔNG QUAN TIÊU THỤ TOKEN AI TOÀN TRƯỜNG THỜI GIAN THỰC

- **ĐIỀU KIỆN TIÊN QUYẾT:**
  - Các Giảng viên đã thực hiện các thao tác sinh testcase và review code, làm phát sinh dữ liệu trong bảng `AI_QUOTA_LOGS`.
  - Admin đăng nhập Web Admin Dashboard.
- **CÁC THÀNH PHẦN THAM GIA TÍCH HỢP:**
  - `Web Admin Dashboard` (Next.js).
  - `ReportsController` & `ReportsService` (NestJS).
  - `PrismaService` & `PostgreSQL (Neon Cloud)`.
- **DỮ LIỆU ĐẦU VÀO:**
  - **Endpoint & Method:** `GET /api/v1/admin/reports/overview`
  - **Headers:** `Authorization: Bearer <token_admin>`
- **CÁC BƯỚC THỰC HIỆN:**
  1. Quản trị viên truy cập màn hình Dashboard trên trình duyệt web.
  2. Web Admin gửi request HTTP `GET` lấy số liệu thống kê.
  3. `ReportsService` thực hiện các truy vấn aggregate trong PostgreSQL: Đếm tổng giảng viên, tính tổng token đã tiêu thụ trong tháng và phân loại tính năng sử dụng nhiều nhất.
- **KẾT QUẢ MONG ĐỢI (ASSERTIONS):**
  - **Phản hồi API:** HTTP 200 (OK) với dữ liệu:
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
      "timestamp": "2026-10-06T08:30:00.000Z"
    }
    ```
  - **Hiển thị Giao diện:** Biểu đồ trên Web Admin Dashboard hiển thị chính xác tỷ lệ tiêu thụ 25.7% hạn ngạch ngân sách toàn trường.
- **TRẠNG THÁI KIỂM THỬ:**

---

### PHẦN II: CÁC KỊCH BẢN XỬ LÝ LỖI TÍCH HỢP & NGOẠI LỆ (FAILURE, RESILIENCE & ROLLBACK CASES)

---

#### 1. Nhóm Kịch Bản Dịch Vụ Phụ Thuộc Bị Lỗi Hoặc Gián Đoạn (External Service Failures & Timeouts)

---

##### IT16_AI_Service_Timeout_Resilience : GOOGLE GEMINI API BỊ TIMEOUT QUÁ 30 GIÂY HOẶC GIÁN ĐOẠN ĐÁM MÂY

- **ĐIỀU KIỆN TIÊN QUYẾT:**
  - Giảng viên thực hiện gửi yêu cầu sinh testcase bằng AI.
  - Mock Gemini Client hoặc Google API bị ngắt kết nối mạng giả lập hoặc phản hồi trễ quá ngưỡng 30 giây (Timeout threshold).
- **CÁC THÀNH PHẦN THAM GIA TÍCH HỢP:**
  - `Desktop App AIClient`.
  - `Web Backend AiGatewayService`.
  - `GoogleGenAI Client Library`.
  - `PostgreSQL Database`.
- **DỮ LIỆU ĐẦU VÀO:**
  - Request `POST /api/v1/ai/generate-testcases` với payload hợp lệ.
- **CÁC BƯỚC THỰC HIỆN:**
  1. Gửi request sinh testcase từ Desktop App.
  2. Backend thiết lập timeout controller 30s. Sau 30s không nhận được phản hồi từ Google Gemini.
  3. Backend ngắt kết nối an toàn, kích hoạt cơ chế Circuit Breaker / Graceful Fallback.
  4. Kiểm tra phản hồi trả về cho Desktop App và kiểm tra CSDL trung tâm.
- **KẾT QUẢ MONG ĐỢI (ASSERTIONS):**
  - Tiến trình NestJS không bị treo hoặc rò rỉ kết nối socket.
  - Phản hồi mã lỗi chuẩn **HTTP 502 (BAD GATEWAY)** kèm envelope:
    ```json
    {
      "success": false,
      "status_code": 502,
      "error_code": "AI_SERVICE_UNAVAILABLE",
      "message": "Dịch vụ Google Gemini API hiện đang bận hoặc gián đoạn. Vui lòng thử lại sau.",
      "details": null,
      "timestamp": "2026-10-06T08:35:00.000Z"
    }
    ```
  - **Bảo toàn Hạn ngạch:** Tuyệt đối không trừ bất kỳ token nào của Giảng viên trong bảng `AI_QUOTA_CONFIGS`, không ghi bản ghi rác vào `AI_QUOTA_LOGS`.
  - **Phản ứng Desktop App:** Hiển thị thông báo gợi ý: *"Dịch vụ AI đang gián đoạn, Thầy/Cô có thể tiếp tục nhập testcase thủ công bình thường mà không ảnh hưởng đến việc chấm bài."*
- **TRẠNG THÁI KIỂM THỬ:**

---

##### IT17_AI_Daily_Quota_Exceeded_Block : CHẶN YÊU CẦU GỌI AI KHI GIẢNG VIÊN ĐÃ VƯỢT HẠN MỨC TOKEN TRONG NGÀY

- **ĐIỀU KIỆN TIÊN QUYẾT:**
  - Giảng viên `teacher_hung` có hạn mức `daily_token_limit = 50000`.
  - Trong ngày hôm nay, Giảng viên đã sử dụng hết 50,000 tokens (`used_tokens_today = 50000`).
- **CÁC THÀNH PHẦN THAM GIA TÍCH HỢP:**
  - `AiGatewayGuard` (Tầng bảo vệ Gateway).
  - `AiGatewayService` & `PrismaService`.
  - `PostgreSQL (AI_QUOTA_CONFIGS)`.
- **DỮ LIỆU ĐẦU VÀO:**
  - Gửi request `POST /api/v1/ai/generate-testcases` hoặc `POST /api/v1/ai/review-code`.
- **CÁC BƯỚC THỰC HIỆN:**
  1. Giảng viên gửi request yêu cầu AI từ Desktop App.
  2. `AiGatewayGuard` chặn request ngay trước khi vào Controller, đối chiếu `used_tokens_today >= daily_token_limit`.
- **KẾT QUẢ MONG ĐỢI (ASSERTIONS):**
  - Trả về mã lỗi **HTTP 429 (TOO MANY REQUESTS)**.
  - Cấu trúc phản hồi lỗi chuẩn:
    ```json
    {
      "success": false,
      "status_code": 429,
      "error_code": "AI_QUOTA_EXCEEDED",
      "message": "Tài khoản của bạn đã sử dụng hết hạn ngạch Token AI trong ngày (50,000/50,000 tokens). Vui lòng liên hệ Quản trị viên để cấp thêm quota hoặc đợi sang ngày hôm sau.",
      "details": {
        "daily_limit": 50000,
        "current_usage": 50000,
        "reset_at": "2026-10-07T00:00:00.000Z"
      },
      "timestamp": "2026-10-06T08:40:00.000Z"
    }
    ```
  - **Tối ưu chi phí:** Không gọi sang Google Gemini API (tiết kiệm 100% chi phí).
  - Desktop App hiển thị popup cảnh báo màu vàng, các chức năng chấm bài offline vẫn hoạt động bình thường.
- **TRẠNG THÁI KIỂM THỬ:**

---

#### 2. Nhóm Kịch Bản Cách Ly Sandbox & An Toàn Thực Thi (Sandbox Quarantine & Safety)

---

##### IT18_Sandbox_Timeout_Quarantine_TLE : CƯỠNG CHẾ KILL TIẾN TRÌNH KHI BÀI NỘP CHỨA VÒNG LẶP VÔ HẠN (TLE)

- **ĐIỀU KIỆN TIÊN QUYẾT:**
  - Sinh viên nộp bài C có lỗi logic vòng lặp vô hạn `while(1) { sum++; }`.
  - Cấu hình đợt chấm: `Time Limit = 1000 ms`.
- **CÁC THÀNH PHẦN THAM GIA TÍCH HỢP:**
  - `CRunner` $\leftrightarrow$ `Subprocess`.
  - `ProcessWatcher` kết hợp thư viện `psutil`.
  - `Local Database SQLite`.
- **DỮ LIỆU ĐẦU VÀO:**
  - File mã nguồn `SE180099_InfiniteLoop.c`.
  - Cặp testcase Input: `1\n`.
- **CÁC BƯỚC THỰC HIỆN:**
  1. `CRunner` biên dịch thành công file `.c` sang `.exe`.
  2. Khởi chạy subprocess và kích hoạt đồng hồ đếm thời gian thực `ProcessWatcher`.
  3. Sau 1000ms, tiến trình con vẫn tiếp tục chiếm dụng CPU và không tự thoát.
  4. `ProcessWatcher` can thiệp: Gọi hàm `psutil.Process(pid).kill()` để cưỡng chế hủy tiến trình và toàn bộ cây tiến trình con (Child Processes).
- **KẾT QUẢ MONG ĐỢI (ASSERTIONS):**
  - Tiến trình con bị tiêu diệt hoàn toàn, giải phóng 100% tài nguyên CPU.
  - Giao diện Desktop App không bị đơ giật (nhờ xử lý đa luồng `QThread`).
  - Ghi nhận kết quả cho sinh viên: Trạng thái **`TLE` (Time Limit Exceeded)**, điểm testcase: **0.0 điểm**, thời gian chạy: `> 1000 ms`.
  - Tiếp tục chuyển sang chấm sinh viên tiếp theo bình thường.
- **TRẠNG THÁI KIỂM THỬ:**

---

##### IT19_Sandbox_Memory_Limit_Exceeded_MLE : CƯỠNG CHẾ KILL TIẾN TRÌNH KHI BÀI NỘP GÂY TRÀN BỘ NHỚ RAM (MLE)

- **ĐIỀU KIỆN TIÊN QUYẾT:**
  - Sinh viên nộp bài Java hoặc C đệ quy vô hạn hoặc cấp phát mảng động khổng lồ vượt quá giới hạn cho phép.
  - Cấu hình đợt chấm: `Memory Limit = 128 MB`.
- **CÁC THÀNH PHẦN THAM GIA TÍCH HỢP:**
  - `Runner` $\leftrightarrow$ `Subprocess Engine`.
  - `ProcessWatcher` (`psutil.Process(pid).memory_info().rss`).
  - `Local Database SQLite`.
- **DỮ LIỆU ĐẦU VÀO:**
  - Bài nộp cấp phát liên tục `malloc(1024 * 1024 * 10)` trong vòng lặp.
- **CÁC BƯỚC THỰC HIỆN:**
  1. Khởi chạy bài nộp sinh viên trong môi trường Sandbox.
  2. `ProcessWatcher` liên tục lấy mẫu mức tiêu thụ RAM (RSS memory) mỗi 20ms.
  3. Mức tiêu thụ bộ nhớ vượt qua ngưỡng 128MB.
  4. `ProcessWatcher` lập tức gửi tín hiệu `SIGKILL` dừng khẩn cấp tiến trình.
- **KẾT QUẢ MONG ĐỢI (ASSERTIONS):**
  - Tiến trình bị chặn đứng trước khi gây tràn bộ nhớ hệ thống (OOM) làm treo máy trạm Giảng viên.
  - Ghi nhận phán quyết: **`MLE` (Memory Limit Exceeded)**, điểm số: **0.0 điểm**.
  - Ghi nhận thông tin bộ nhớ đỉnh điểm (Peak RAM) vào log thực thi trong SQLite.
- **TRẠNG THÁI KIỂM THỬ:**

---

#### 3. Nhóm Kịch Bản Xung Đột Dữ Liệu & Toàn Vẹn Giao Dịch (Conflict & Rollback Cases)

---

##### IT20_CSV_Duplicate_MSSV_Rollback : ROLLBACK TOÀN BỘ GIAO DỊCH KHI PHÁT HIỆN TRÙNG MÃ SINH VIÊN TRONG FILE CSV

- **ĐIỀU KIỆN TIÊN QUYẾT:**
  - Giảng viên nạp file `students.csv` có 10 dòng, trong đó dòng 3 và dòng 8 đều mang cùng mã số sinh viên `"SE180001"`.
- **CÁC THÀNH PHẦN THAM GIA TÍCH HỢP:**
  - `CsvService` (Thẩm định dữ liệu đầu vào).
  - `Local Database SQLite` (SQLite Transaction Context Manager).
- **DỮ LIỆU ĐẦU VÀO:**
  - File `students.csv` chứa dữ liệu trùng lặp nội bộ.
- **CÁC BƯỚC THỰC HIỆN:**
  1. Giảng viên bấm nạp file CSV.
  2. `CsvService` duyệt qua các dòng và đưa MSSV vào tập hợp kiểm tra tính duy nhất (`Set`).
  3. Phát hiện mã `"SE180001"` xuất hiện lần thứ hai.
  4. Kích hoạt ngoại lệ nghiệp vụ và thực hiện lệnh `ROLLBACK` toàn bộ giao dịch CSDL cục bộ.
- **KẾT QUẢ MONG ĐỢI (ASSERTIONS):**
  - Quá trình nạp bị hủy bỏ ngay lập tức, trả về mã lỗi nội bộ: `CSV_DUPLICATE_STUDENT`.
  - Hiển thị hộp thoại cảnh báo: *"Phát hiện mã sinh viên SE180001 bị lặp lại tại dòng 8 trong file CSV. Vui lòng kiểm tra lại file!"*.
  - **Tính toàn vẹn CSDL (Rollback):** Bảng `LOCAL_CLASSES` không tạo đợt chấm dở dang, bảng `LOCAL_STUDENT_SUBMISSIONS` không lưu bất kỳ sinh viên nào của file bị lỗi. Trạng thái SQLite giữ nguyên 100%.
- **TRẠNG THÁI KIỂM THỬ:**

---

#### 4. Nhóm Kịch Bản Vi Phạm Phân Quyền & Bảo Mật (RBAC & Security Enforcement)

---

##### IT21_RBAC_Instructor_AdminEndpoint_Block : CHẶN GIẢNG VIÊN CỐ TÌNH TRUY CẬP VÀO CÁC ENDPOINT QUẢN TRỊ CỦA ADMIN

- **ĐIỀU KIỆN TIÊN QUYẾT:**
  - Giảng viên `teacher_hung` đang đăng nhập hợp lệ với token mang claim `role = "INSTRUCTOR"`.
- **CÁC THÀNH PHẦN THAM GIA TÍCH HỢP:**
  - `JwtAuthGuard` & `RolesGuard` (Tầng bảo mật NestJS).
  - `UsersController` / `ReportsController` (`@Roles('ADMIN')`).
- **DỮ LIỆU ĐẦU VÀO:**
  - Header mang Bearer token của Giảng viên.
  - Gửi request HTTP tới các endpoint quản trị:
    - Endpoint 1: `GET /api/v1/admin/users`
    - Endpoint 2: `PUT /api/v1/ai/quota-config`
    - Endpoint 3: `GET /api/v1/admin/reports/overview`
- **CÁC BƯỚC THỰC HIỆN:**
  1. Thực hiện gửi request từ client tới endpoint quản trị bằng token của Giảng viên.
  2. `JwtAuthGuard` xác thực token thành công.
  3. `RolesGuard` kiểm tra metadata `@Roles('ADMIN')` đối chiếu với role `INSTRUCTOR` của user.
- **KẾT QUẢ MONG ĐỢI (ASSERTIONS):**
  - Tất cả các request đều bị chặn đứng tại tầng Guard với mã lỗi **HTTP 403 (FORBIDDEN)**.
  - Cấu trúc phản hồi lỗi:
    ```json
    {
      "success": false,
      "status_code": 403,
      "error_code": "FORBIDDEN_ADMIN_ONLY",
      "message": "Bạn không có quyền truy cập vào chức năng quản trị này.",
      "details": null,
      "timestamp": "2026-10-06T08:45:00.000Z"
    }
    ```
  - Dữ liệu người dùng và báo cáo quản trị được bảo mật tuyệt đối.
- **TRẠNG THÁI KIỂM THỬ:**

---

##### IT22_Token_Expired_Refresh_Rotation : LÀM MỚI PHIÊN ĐĂNG NHẬP BẰNG REFRESH TOKEN VÀ THU HỒI TOKEN CŨ

- **ĐIỀU KIỆN TIÊN QUYẾT:**
  - Access Token của Giảng viên đã hết hạn hiệu lực sau 24 giờ.
  - Giảng viên đang sở hữu một `refresh_token` hợp lệ trong phiên làm việc.
- **CÁC THÀNH PHẦN THAM GIA TÍCH HỢP:**
  - `Desktop App AuthClientService`.
  - `AuthController` & `JwtService`.
  - `PrismaService` & `PostgreSQL (Neon Cloud)`.
- **DỮ LIỆU ĐẦU VÀO:**
  - **Endpoint & Method:** `POST /api/v1/auth/refresh`
  - **Body JSON:**
    ```json
    {
      "refresh_token": "def502005a76c8e3..."
    }
    ```
- **CÁC BƯỚC THỰC HIỆN:**
  1. Desktop App phát hiện request gửi đi bị lỗi `401 AUTH_TOKEN_EXPIRED`.
  2. Desktop App tự động kích hoạt bộ đánh chặn (Axios Interceptor) gửi `refresh_token` lên endpoint `/auth/refresh`.
  3. Backend xác thực chữ ký và kiểm tra tính hợp lệ của Refresh Token.
  4. Backend cấp phát cặp token mới và vô hiệu hóa (revoke) refresh token cũ.
  5. Desktop App lưu token mới và gửi lại request ban đầu một cách trong suốt (Transparent retry).
- **KẾT QUẢ MONG ĐỢI (ASSERTIONS):**
  - **Phản hồi API:** HTTP 200 (OK), nhận `access_token` mới và `refresh_token` mới.
  - **Cơ chế Token Rotation:** Refresh token cũ không thể tái sử dụng lần thứ 2.
  - Giảng viên tiếp tục làm việc bình thường mà không bị gián đoạn hoặc bị bắt đăng nhập lại thủ công.
- **TRẠNG THÁI KIỂM THỬ:**

---

##### IT23_Soft_Delete_Cascade_Exclusion : VÒNG ĐỜI XÓA MỀM TÀI KHOẢN VÀ BẢO TOÀN LỊCH SỬ NHẬT KÝ KIỂM TOÁN

- **ĐIỀU KIỆN TIÊN QUYẾT:**
  - Giảng viên `teacher_lan` (ID: 3) đã từng tiêu thụ token và có lịch sử trong bảng `AI_QUOTA_LOGS`.
  - Quản trị viên thực hiện thao tác xóa tài khoản này.
- **CÁC THÀNH PHẦN THAM GIA TÍCH HỢP:**
  - `AdminController` & `UsersService`.
  - `PrismaService` & `PostgreSQL (Neon Cloud)`.
  - Bảng `USERS`, `AI_QUOTA_CONFIGS`, `AI_QUOTA_LOGS`.
- **DỮ LIỆU ĐẦU VÀO:**
  - `DELETE /api/v1/admin/users/3` với token Admin.
- **CÁC BƯỚC THỰC HIỆN:**
  1. Quản trị viên gửi lệnh xóa người dùng ID 3.
  2. `UsersService` thực thi cơ chế Xóa mềm (Soft Delete): Cập nhật `is_deleted = true`, `deleted_at = now()`, `is_active = false`.
  3. Quản trị viên gọi API lấy danh sách người dùng: `GET /api/v1/admin/users`.
  4. Quản trị viên gọi API lấy báo cáo kiểm toán AI: `GET /api/v1/admin/reports/overview`.
- **KẾT QUẢ MONG ĐỢI (ASSERTIONS):**
  - **Phản hồi Xóa:** HTTP 200 (OK), message: `"Xóa tài khoản người dùng thành công"`.
  - **Loại trừ Danh sách (Auto-exclusion):** Người dùng ID 3 không xuất hiện trong danh sách trả về của API `GET /api/v1/admin/users` (do mệnh đề lọc `where: { is_deleted: false }`).
  - **Bảo toàn Lịch sử (Audit Preservation):** Toàn bộ các dòng log tiêu thụ token trước đây của `teacher_lan` trong bảng `AI_QUOTA_LOGS` vẫn được giữ nguyên vẹn 100%, đảm bảo số liệu báo cáo tài chính và kiểm toán không bị sai lệch.
- **TRẠNG THÁI KIỂM THỬ:**

---

## 4. KẾT LUẬN & HƯỚNG DẪN THỰC THI KIỂM THỬ TÍCH HỢP TỰ ĐỘNG

1. **Bộ Test Suite Chuẩn Hóa:** Tài liệu này bao quát trọn vẹn **23 kịch bản kiểm thử tích hợp** (15 kịch bản Positive Flows và 8 kịch bản Failure/Resilience/Security Cases), bao quát 100% vòng đời vận hành thực tế của hệ sinh thái AITA: từ Quản trị viên trên Web Admin Dashboard, Giảng viên trên Desktop App Client, đến Web Server Backend và các dịch vụ ngoại vi (Gemini AI Hub, MinGW GCC, JVM, Python Runtime, Playwright, SQLite3, Neon PostgreSQL).
2. **Khởi chạy Bộ Kiểm thử Tích hợp Tự động:**
   - **Phân hệ Web Server Backend (NestJS & PostgreSQL):**
     ```bash
     cd apps/central-backend
     # Thiết lập biến môi trường kiểm thử
     export DATABASE_URL="postgresql://test_user:test_pass@localhost:5432/aita_test_db"
     # Chạy toàn bộ kịch bản kiểm thử tích hợp qua Jest & Supertest
     pnpm test:e2e
     ```
   - **Phân hệ Desktop App Client (Python / PyQt6 & SQLite):**
     ```bash
     cd apps/desktop-client
     # Cài đặt các thư viện kiểm thử phụ thuộc
     pip install -r requirements.txt pytest pytest-mock pytest-qt
     # Chạy toàn bộ kịch bản kiểm thử tích hợp luồng Runner, CSV và Database
     pytest tests/integration/ -v --durations=10
     ```
3. **Tiêu chuẩn Hoàn tất (Definition of Done - DoD):**
   - Tất cả 23/23 kịch bản kiểm thử tích hợp phải đạt kết quả **PASS**.
   - Thời gian thực thi trung bình mỗi testcase < 500ms (ngoại trừ các testcase Timeout có chủ đích).
   - Tỷ lệ bao phủ kiểm thử (Code Coverage) đạt trên **85%** cho các tầng Service, Guard, Runner và Matching Strategy.
   - Xử lý ngoại lệ an toàn, tuân thủ tuyệt đối cấu trúc phản hồi chuẩn Standard Response Envelope và nguyên tắc bảo mật Local-First của hệ thống AITA.
