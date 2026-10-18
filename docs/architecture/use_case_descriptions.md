# Tài Liệu Đặc Tả Chi Tiết Trường Hợp Sử Dụng (Use Case Descriptions Specification)

# Dự Án AITA: Automated Grading & Assessment Tool for Instructors

### Đề án Môn học SWD392: Thiết Kế Hệ Thống Có Hỗ Trợ Của AI (AI-Assisted System Design)
### Giai đoạn: Đánh giá 1 (Evaluation 1: Requirement Analysis & Modeling)

---

## 1. Giới Thiệu & Mục Đích Tài Liệu

Tài liệu này cung cấp bản đặc tả chi tiết từng bước (**Use Case Descriptions / Specifications**) cho toàn bộ **19 Use Cases** thuộc 6 phân hệ chức năng của hệ sinh thái **AITA (AI-Assisted Automated Grading & Assessment Tool)**. 

Bản đặc tả được xây dựng bám sát theo chuẩn Kỹ nghệ Phần mềm Quốc tế (IEEE 830 / RUP Template), đồng bộ 100% với kiến trúc hệ thống tại [system-overview.md](file:///e:/AITA/docs/architecture/system-overview.md), danh mục tác nhân và sơ đồ tại [actors_and_use_cases.md](file:///e:/AITA/docs/architecture/actors_and_use_cases.md) và ngăn xếp công nghệ tại [tech-stack.md](file:///e:/AITA/docs/architecture/tech-stack.md).

Mỗi Use Case được đặc tả bao gồm:
1. **Mã & Tên Use Case** (Song ngữ Việt - Anh).
2. **Tác nhân chính (Primary Actor)** & **Tác nhân hỗ trợ ngoài (External Supporting Actors)**.
3. **Mô tả tóm tắt (Summary & Scope)**.
4. **Tiền điều kiện (Preconditions)**.
5. **Hậu điều kiện (Postconditions)**.
6. **Tác nhân kích hoạt (Trigger)**.
7. **Luồng sự kiện chính (Step-by-step Main Flow)**: Tương tác tuần tự giữa Actor và System.
8. **Luồng rẽ nhánh & Ngoại lệ (Alternative & Exception Flows)**: Kịch bản rẽ nhánh và các trường hợp ngoại lệ.

---

## 2. Ma Trận 19 Use Cases Theo 6 Phân Hệ Chức Năng

| Mã UC | Tên Use Case | Tác nhân chính | Giao diện thực hiện | Tác nhân ngoài hỗ trợ |
| :--- | :--- | :--- | :--- | :--- |
| **Phân hệ 1: Quản trị Hệ thống & Quản lý Xác thực (System Administration & Authentication)** | | | | |
| **UC-01** | Đăng nhập & Xác thực Hệ thống | Admin, Giảng viên | Web Admin / Desktop App | Web Server Backend |
| **UC-02** | Quản lý Tài khoản & Phân quyền Giảng viên | Admin | Web Admin Dashboard | Web Server Backend |
| **UC-03** | Cấp mới Access Token bằng Refresh Token | Admin, Giảng viên | Web Admin / Desktop App | Web Server Backend |
| **UC-04** | Quản lý hạn ngạch & giám sát sử dụng AI | Admin | Web Admin Dashboard | Web Server Backend, Gemini AI Hub |
| **UC-05** | Xem Báo cáo tài khoản & Sử dụng AI | Admin | Web Admin Dashboard | Web Server Backend |
| **Phân hệ 2: Quản lý Đợt Chấm & Dữ liệu Sinh viên (Session & Submission Management)** | | | | |
| **UC-06** | Cấu hình Môi trường Biên dịch & Sandbox Cục bộ | Giảng viên | Desktop App Client | Sandbox Execution Runner |
| **UC-07** | Quản lý Đợt Chấm & Lớp học | Giảng viên | Desktop App Client | *(Tương tác Local DB)* |
| **UC-08** | Nạp Danh Sách Sinh Viên & Bài Nộp từ File CSV | Giảng viên | Desktop App Client | *(Tương tác File System)* |
| **Phân hệ 3: Quản lý Bộ Kiểm thử & Chiến lược So khớp (Testcase & Matching Strategy)** | | | | |
| **UC-09** | Quản lý Bộ Testcase Kiểm thử Black-box Thủ công | Giảng viên | Desktop App Client | *(Tương tác Local DB)* |
| **UC-10** | Tự động Sinh Testcase Biên bằng AI | Giảng viên | Desktop App Client | Gemini AI Hub |
| **UC-11** | Thiết lập Động cơ So khớp 7 Chế độ | Giảng viên | Desktop App Client | *(Tương tác Local DB)* |
| **Phân hệ 4: Tự động Thực thi & Chấm điểm (Execution & Automated Grading Pipeline)** | | | | |
| **UC-12** | Thực thi Chấm điểm Tự động Hàng loạt | Giảng viên | Desktop App Client | Sandbox Execution Runner |
| **UC-13** | Giám sát Tiến độ Chấm Thời gian thực | Giảng viên | Desktop App Client | Sandbox Execution Runner |
| **UC-14** | Xem Chi tiết Kết quả & Nhật ký Bài nộp | Giảng viên | Desktop App Client | *(Tương tác Local DB)* |
| **UC-15** | Chấm lại & Điều chỉnh Điểm thủ công | Giảng viên | Desktop App Client | Sandbox Execution Runner |
| **UC-19** | Chấm Điểm Bài Tập Web Tự Động | Giảng viên | Desktop App Client | Headless Browser, DOM/CSS Parser, AI Gateway |
| **Phân hệ 5: Tính năng Thông minh có AI Hỗ trợ (Smart AI-Assisted Capabilities)** | | | | |
| **UC-16** | Phân tích Lỗi & Sinh Nhận xét Sư phạm On-Demand | Giảng viên | Desktop App Client | Gemini AI Hub |
| **UC-17** | Kiểm tra Đạo văn qua Cơ chế Lọc 2 Vòng | Giảng viên | Desktop App Client | Gemini AI Hub |
| **Phân hệ 6: Báo cáo, Đánh giá Cục Bộ (Reporting & Local Export)** | | | | |
| **UC-18** | Xuất Báo cáo Kết quả Điểm | Giảng viên | Desktop App Client | *(Tương tác File System)* |

---

## 3. Đặc Tả Chi Tiết Từng Use Case (Detailed Step-by-Step Specifications)

---

### 3.1. Phân Hệ 1: Quản Trị Hệ Thống & Quản Lý Xác Thực (System Administration & Authentication)

---

#### 3.1.1. UC-01: Đăng Nhập & Xác Thực Hệ Thống (Login & System Authentication)

* **Mã Use Case**: `UC-01`
* **Tên Use Case**: Đăng nhập & Xác thực Hệ thống (Login & System Authentication)
* **Tác nhân chính**: Quản trị viên (Admin), Giảng viên (Instructor)
* **Tác nhân hỗ trợ ngoài**: Web Server Backend (NestJS Auth Module, JWT & Bcrypt Engine)
* **Mô tả tóm tắt**: Cung cấp cơ chế xác thực an toàn, tập trung cho cả Quản trị viên (trên Web Admin Dashboard) và Giảng viên (trên Desktop App Client). Hệ thống thẩm định định danh qua OAuth2 Password Request, mã hóa băm Bcrypt và trả về Access Token / Refresh Token định dạng JWT mang thông tin Role-Based Access Control (`admin` hoặc `instructor`).
* **Tiền điều kiện (Preconditions)**:
  1. Người dùng đã được cấp tài khoản hoạt động (`is_active = True`) trên hệ thống Web Server Backend.
  2. Kết nối mạng giữa máy trạm Client và Web Server Backend hoạt động bình thường.
* **Hậu điều kiện (Postconditions)**:
  1. Người dùng được cấp phiên làm việc hợp lệ; JWT Access Token được lưu trữ bảo mật (trên Local Storage / Cookie đối với Web UI, hoặc bộ nhớ ứng dụng đối với Desktop App).
  2. Giao diện chuyển hướng đến không gian làm việc tương ứng với quyền hạn (Web Admin Dashboard cho Admin, Màn hình chính Desktop App cho Giảng viên).
* **Tác nhân kích hoạt (Trigger)**: Người dùng mở ứng dụng và nhập thông tin đăng nhập tại biểu mẫu xác thực.

##### Luồng sự kiện chính (Main Flow):
1. Người dùng truy cập màn hình Đăng nhập (trên trình duyệt web hoặc giao diện khởi động Desktop App).
2. Hệ thống hiển thị form yêu cầu nhập: `Tên đăng nhập / Email` và `Mật khẩu`.
3. Người dùng điền đầy đủ thông tin xác thực và bấm nút **"Đăng nhập" (Login)**.
4. Client đóng gói payload theo chuẩn `OAuth2PasswordRequestForm` và gửi yêu cầu `POST /api/v1/auth/login` tới Web Server Backend.
5. Web Server Backend tiếp nhận yêu cầu, truy vấn cơ sở dữ liệu để tìm tài khoản người dùng theo `username`:
   - Thẩm định trạng thái hoạt động của tài khoản (`is_active`).
   - Sử dụng thư viện `passlib[bcrypt]` để đối chiếu mật khẩu người dùng nhập với chuỗi băm lưu trong CSDL.
6. Khi xác thực thành công, Backend sinh cặp mã token: `access_token` (JWT chứa `sub`, `role`, thời hạn hết hạn `exp`) và `refresh_token`.
7. Backend phản hồi mã trạng thái `HTTP 200 OK` kèm dữ liệu token và thông tin hồ sơ người dùng (`id`, `full_name`, `role`).
8. Client lưu trữ token:
   - **Web Admin**: Lưu token vào bộ nhớ an toàn (HttpOnly Cookie hoặc sessionStorage) và chuyển hướng tới Dashboard Quản trị.
   - **Desktop App**: Lưu token vào phiên làm việc `SessionManager` trong RAM để đính kèm vào header `Authorization: Bearer <token>` cho mọi request gọi API AI Gateway tiếp theo.
9. Hệ thống thông báo đăng nhập thành công. Use Case kết thúc.

##### Luồng rẽ nhánh & Ngoại lệ (Alternative & Exception Flows):
* **A1 - Đăng nhập Offline trên Desktop App**: Tại bước 4, nếu không có kết nối Internet tới Web Backend, Desktop App cung cấp chế độ **"Offline Mode"**: Giảng viên vẫn có thể vào ứng dụng để chấm bài cục bộ bằng Sandbox (`UC-12`) và xuất file CSV (`UC-18`), nhưng các tính năng gọi AI Cloud (`UC-10`, `UC-16`, `UC-17 Vòng 2`) sẽ tạm thời bị vô hiệu hóa.
* **E1 - Sai tên đăng nhập hoặc mật khẩu**: Tại bước 5, nếu không tìm thấy username hoặc mật khẩu không khớp, Backend trả về `HTTP 401 Unauthorized` ("Tên đăng nhập hoặc mật khẩu không chính xác"). Client hiển thị thông báo lỗi màu đỏ và cho phép người dùng thử lại.
* **E2 - Tài khoản bị khóa (Disabled Account)**: Tại bước 5, nếu tài khoản có cờ `is_active = False`, Backend trả về `HTTP 403 Forbidden` ("Tài khoản đã bị vô hiệu hóa bởi Quản trị viên"). Client thông báo người dùng liên hệ Admin.

---

#### 3.1.2. UC-02: Quản Lý Tài Khoản & Phân Quyền Giảng Viên (Manage Instructor Accounts & RBAC)

* **Mã Use Case**: `UC-02`
* **Tên Use Case**: Quản lý Tài khoản & Phân quyền Giảng viên (Manage Instructor Accounts & RBAC)
* **Tác nhân chính**: Quản trị viên (Admin)
* **Tác nhân hỗ trợ ngoài**: Web Server Backend (NestJS RBAC Guards, Prisma ORM)
* **Mô tả tóm tắt**: Cho phép Quản trị viên tạo mới tài khoản cho giảng viên, chỉnh sửa thông tin cá nhân, cấp lại mật khẩu, kích hoạt/vô hiệu hóa tài khoản và gán vai trò quyền hạn (`Admin` hoặc `Instructor`) trên Web Admin Dashboard.
* **Tiền điều kiện (Preconditions)**:
  1. Quản trị viên đã đăng nhập thành công vào Web Admin Dashboard với quyền `Admin` (`role == 'admin'`).
* **Hậu điều kiện (Postconditions)**:
  1. Tài khoản Giảng viên được tạo mới, cập nhật thông tin hoặc thay đổi trạng thái trong CSDL trung tâm.
  2. Mọi thay đổi về quyền hạn và trạng thái có hiệu lực ngay lập tức trong các lần xác thực tiếp theo.
* **Tác nhân kích hoạt (Trigger)**: Quản trị viên điều hướng đến mục **"Quản lý Tài khoản" (User Management)** trên thanh menu Web Admin.

##### Luồng sự kiện chính (Main Flow):
1. Quản trị viên chọn phân hệ **"Quản trị Tài khoản"** trên giao diện Web Admin.
2. Hệ thống gửi yêu cầu `GET /api/v1/admin/users` lên Backend và hiển thị danh sách toàn bộ người dùng dưới dạng bảng dữ liệu phân trang (bao gồm: Họ tên, Email, Tên đăng nhập, Vai trò, Trạng thái hoạt động, Ngày tạo).
3. Quản trị viên lựa chọn thao tác:
   - **Tạo mới**: Bấm nút **"Thêm Giảng viên (+)"**, nhập Họ tên, Email, Username, Mật khẩu ban đầu và chọn Role (`Instructor`).
   - **Chỉnh sửa**: Bấm biểu tượng "Sửa" trên một dòng người dùng, cập nhật Họ tên, Email hoặc Role.
   - **Khóa/Mở khóa**: Nhấn toggle chuyển đổi trạng thái `is_active` của tài khoản.
   - **Đặt lại mật khẩu (Reset Password)**: Bấm nút "Reset Password", nhập mật khẩu mới hoặc chọn tự động sinh mật khẩu ngẫu nhiên.
4. Quản trị viên nhấn nút **"Lưu thay đổi" (Save)**.
5. Client gửi yêu cầu tương ứng (`POST`, `PUT`, hoặc `PATCH /api/v1/admin/users/{id}`) kèm JWT token tới Backend.
6. Backend thẩm định quyền Admin thông qua NestJS RBAC Guards, kiểm tra tính hợp lệ của dữ liệu (email không trùng lặp, độ phức tạp mật khẩu), mã hóa mật khẩu bằng Bcrypt nếu có thay đổi và lưu vào CSDL qua Prisma.
7. Backend trả về thông báo thành công `HTTP 200/201`.
8. Web Admin Dashboard tự động tải lại bảng dữ liệu và hiển thị thông báo "Cập nhật tài khoản thành công". Use Case kết thúc.

##### Luồng rẽ nhánh & Ngoại lệ (Alternative & Exception Flows):
* **E1 - Trùng lặp Email hoặc Username**: Tại bước 6, nếu Email hoặc Username đã tồn tại trong CSDL, Backend trả về `HTTP 409 Conflict` ("Email hoặc Tên đăng nhập đã được sử dụng"). Giao diện Web hiển thị cảnh báo ngay tại ô nhập liệu tương ứng.
* **E2 - Admin tự khóa tài khoản của chính mình**: Nếu Quản trị viên cố gắng chuyển trạng thái tài khoản đang đăng nhập của mình thành vô hiệu hóa hoặc hạ quyền, hệ thống chặn lại và cảnh báo "Không thể tự vô hiệu hóa tài khoản Quản trị viên đang kích hoạt".



#### 3.1.3. UC-04: Quản Lý Hạn Ngạch & Giám Sát Sử Dụng AI

* **Mã Use Case**: `UC-04`
* **Tên Use Case**: Quản lý hạn ngạch và giám sát sử dụng AI
* **Tác nhân chính**: Quản trị viên (Admin)
* **Tác nhân hỗ trợ ngoài**: Web Server Backend, Google Gemini AI Hub
* **Mô tả tóm tắt**: Quản trị viên cấu hình quota token/ngày cho từng giảng viên và theo dõi báo cáo sử dụng AI. Google Gemini API key chỉ được cấu hình bởi vận hành viên trong biến môi trường `GEMINI_API_KEY` của backend; Web Admin không nhận, lưu hoặc hiển thị key.
* **Tiền điều kiện (Preconditions)**:
  1. Quản trị viên đã đăng nhập tài khoản quyền Admin trên Web Admin.
  2. Backend đã được cấu hình `GEMINI_API_KEY` trong môi trường máy chủ.
* **Hậu điều kiện (Postconditions)**:
  1. Quota ngày của giảng viên được lưu và áp dụng tại backend.
  2. Nhật ký và báo cáo sử dụng AI có thể được tra cứu từ Web Admin.
* **Tác nhân kích hoạt (Trigger)**: Quản trị viên chọn mục **"Giám sát AI & Quota"** trên Web Admin.

##### Luồng sự kiện chính (Main Flow):
1. Quản trị viên mở phân hệ **"Quản lý AI & Giám sát Hạn ngạch"**.
2. Web Admin tải số liệu tổng hợp bằng `GET /api/v1/admin/reports/overview` và nhật ký đã lọc bằng `GET /api/v1/admin/reports/ai-usage`.
3. Khi thay đổi quota, Admin cập nhật `daily_token_quota` qua `PUT /api/v1/admin/users/{id}`; backend lưu cấu hình và áp dụng quota ngày UTC cho các yêu cầu AI tiếp theo.
4. Gemini API key được vận hành viên thay đổi trong cấu hình môi trường máy chủ, không qua API hoặc giao diện Admin. Backend không trả giá trị key cho client.
5. Web Admin hiển thị báo cáo/quota đã cập nhật. Use Case kết thúc.

##### Luồng rẽ nhánh & Ngoại lệ (Alternative & Exception Flows):
* **A1 - Điều chỉnh quota**: Admin thay đổi quota qua cập nhật User; quota mới có hiệu lực ngay cho lần kiểm tra quota kế tiếp.
* **E1 - Gemini chưa được cấu hình hoặc key không hợp lệ**: Backend trả lỗi đã lọc thông tin nhạy cảm (`AI_NOT_CONFIGURED` hoặc `AI_PROVIDER_ERROR`); vận hành viên cập nhật biến môi trường máy chủ.

---

#### 3.1.4. UC-05: Xem Báo cáo tài khoản & Sử dụng AI (View Account & AI Usage Reports)

* **Mã Use Case**: `UC-05`
* **Tên Use Case**: Xem Báo cáo tài khoản & Sử dụng AI (View Account & AI Usage Reports)
* **Tác nhân chính**: Quản trị viên (Admin)
* **Tác nhân hỗ trợ ngoài**: Web Server Backend (Reporting Engine, Prisma ORM)
* **Mô tả tóm tắt**: Cung cấp cho Quản trị viên báo cáo số tài khoản giảng viên và hoạt động sử dụng AI, gồm tổng token Gemini đã tiêu thụ, tính năng được dùng và nhật ký từng lượt gọi AI. Backend không lưu phiên chấm hoặc bảng điểm; các dữ liệu đó được quản lý cục bộ trên Desktop App.
* **Tiền điều kiện (Preconditions)**:
  1. Quản trị viên đã đăng nhập vào Web Admin Dashboard với quyền Admin.
* **Hậu điều kiện (Postconditions)**:
  1. Báo cáo thống kê tổng hợp và danh sách nhật ký được hiển thị đầy đủ, hỗ trợ lọc và xuất file báo cáo tổng kết.
* **Tác nhân kích hoạt (Trigger)**: Quản trị viên chọn mục **"Báo cáo tài khoản & Sử dụng AI" (School-wide Analytics & Logs)**.

##### Luồng sự kiện chính (Main Flow):
1. Quản trị viên truy cập mục **"Báo cáo & Thống kê"**.
2. Hệ thống gửi yêu cầu `GET /api/v1/admin/reports/overview` lên Backend.
3. Backend tổng hợp dữ liệu từ bảng người dùng (`users`) và bảng nhật ký tiêu thụ AI (`ai_quota_logs`).
4. Giao diện hiển thị các khối trực quan:
   - Các chỉ số KPI tổng thể: Tổng số giảng viên, Tổng token AI đã tiêu thụ trong tháng.
   - Biểu đồ tần suất sử dụng các tính năng AI (Sinh testcase, Code review lỗi WA, Quét đạo văn Vòng 2).
   - Bảng nhật ký sử dụng AI phục vụ kiểm toán (Giảng viên, Tính năng sử dụng, Số token tiêu hao, Thời gian gọi).
5. Quản trị viên có thể sử dụng bộ lọc theo Giảng viên hoặc Khoảng thời gian.
6. Web Admin có thể xuất PDF/Excel ở phía trình duyệt từ dữ liệu JSON đã tải; backend không tạo hay lưu file báo cáo. Use Case kết thúc.

##### Luồng rẽ nhánh & Ngoại lệ (Alternative & Exception Flows):
* **A1 - Xem chi tiết mức sử dụng Token của Giảng viên**: Quản trị viên nhấp vào một giảng viên cụ thể trong danh sách để xem chi tiết lịch sử các lần gọi AI trong tháng.
* **E1 - Chưa có dữ liệu thống kê**: Nếu hệ thống mới triển khai hoặc chưa có lượt gọi AI nào, giao diện hiển thị thông báo rỗng thân thiện (Empty State): "Chưa có dữ liệu nhật ký sử dụng trong khoảng thời gian đã chọn".

---

### 3.2. Phân Hệ 2: Quản Lý Đợt Chấm & Dữ Liệu Sinh Viên (Session & Submission Management)

---

#### 3.2.1. UC-06: Cấu Hình Môi Trường Biên Dịch & Sandbox Cục Bộ (Configure Local Compilers & Sandbox Settings)

* **Mã Use Case**: `UC-06`
* **Tên Use Case**: Cấu hình Môi trường Biên dịch & Sandbox Cục bộ (Configure Local Compilers & Sandbox Settings)
* **Tác nhân chính**: Giảng viên (Instructor)
* **Tác nhân hỗ trợ ngoài**: Sandbox Execution Runner (Hệ điều hành Windows, GCC/MinGW, Javac, Python Runtime)
* **Mô tả tóm tắt**: Cho phép Giảng viên kiểm tra, định vị và cấu hình đường dẫn tuyệt đối đến các trình biên dịch trên máy trạm cục bộ (`gcc.exe` cho C, `javac.exe`/`java.exe` cho Java, `python.exe` cho Python), đồng thời thiết lập các ngưỡng an toàn tài nguyên cho Sandbox (`Time Limit`, `Memory Limit`, số tiến trình chạy song song `Worker Pool`).
* **Tiền điều kiện (Preconditions)**:
  1. Giảng viên đã cài đặt các trình biên dịch cần thiết trên máy tính Windows.
  2. Ứng dụng Desktop App đang mở và hoạt động.
* **Hậu điều kiện (Postconditions)**:
  1. Các đường dẫn công cụ và thông số Sandbox được kiểm tra hợp lệ và lưu vào file cấu hình cục bộ `config.json` của Desktop App.
  2. `RunnerFactory` và `CompilerAdapter` sẵn sàng biên dịch và thực thi code sinh viên.
* **Tác nhân kích hoạt (Trigger)**: Giảng viên chọn nút **"Cấu hình Môi trường" (Environment Settings)** trên menu hoặc màn hình khởi tạo của Desktop App.

##### Luồng sự kiện chính (Main Flow):
1. Giảng viên mở hộp thoại **"Cấu hình Trình biên dịch & Sandbox"**.
2. Hệ thống kích hoạt tính năng **Tự động quét môi trường (Auto-Detect)**: Quét biến môi trường `PATH` của hệ điều hành để tìm `gcc`, `javac`, `java`, `python`.
3. Hệ thống hiển thị đường dẫn đã nhận diện kèm phiên bản (ví dụ: `GCC 13.2.0`, `OpenJDK 17.0.9`, `Python 3.11.5`) cùng trạng thái màu xanh (Ready).
4. Đối với các trình biên dịch chưa tự động phát hiện được, Giảng viên bấm nút **"Chọn đường dẫn..." (Browse)** để chọn file thực thi `.exe` thủ công từ ổ đĩa.
5. Giảng viên bấm nút **"Kiểm tra (Test)"**: Desktop App biên dịch thử một đoạn code mẫu "Hello World" nhỏ bằng tiến trình subprocess để xác thực môi trường hoạt động tốt.
6. Giảng viên thiết lập các ngưỡng an toàn tài nguyên mặc định cho Sandbox:
   - `Default Time Limit`: 1000 ms - 2000 ms (tùy môn).
   - `Default Memory Limit`: 256 MB - 512 MB.
   - `Parallel Workers`: 4 - 8 luồng song song (dựa trên số nhân CPU của máy).
7. Giảng viên bấm **"Lưu Cấu Hình"**.
8. Hệ thống lưu thiết lập vào tệp cấu hình cục bộ và thông báo "Môi trường biên dịch sẵn sàng". Use Case kết thúc.

##### Luồng rẽ nhánh & Ngoại lệ (Alternative & Exception Flows):
* **E1 - Đường dẫn không hợp lệ hoặc thiếu quyền thực thi**: Tại bước 5, nếu file được chọn không thể thực thi hoặc bị lỗi quyền hạn (Permission Denied), hệ thống hiển thị cảnh báo đỏ: "Không thể khởi chạy trình biên dịch tại đường dẫn đã chọn. Vui lòng kiểm tra lại quyền truy cập hoặc cài đặt công cụ".

---

#### 3.2.2. UC-07: Quản Lý Đợt Chấm & Lớp Học (Manage Classes & Grading Sessions)

* **Mã Use Case**: `UC-07`
* **Tên Use Case**: Quản lý Đợt Chấm & Lớp học (Manage Classes & Grading Sessions)
* **Tác nhân chính**: Giảng viên (Instructor)
* **Tác nhân hỗ trợ ngoài**: Cơ sở dữ liệu SQLite cục bộ (`local_grading.db`)
* **Mô tả tóm tắt**: Cho phép Giảng viên khởi tạo phiên làm việc mới cho từng lớp/kỳ thi, tra cứu lịch sử, tìm kiếm đợt chấm theo mã lớp, lọc theo môn học, mở lại đợt chấm cũ để tiếp tục làm việc hoặc xóa bỏ đợt chấm không còn sử dụng.
* **Tiền điều kiện (Preconditions)**:
  1. Giảng viên đã mở ứng dụng Desktop App.
* **Hậu điều kiện (Postconditions)**:
  1. Đợt chấm mới được tạo hoặc đợt chấm cũ được chọn sẽ trở thành đợt chấm hoạt động (`active session`) trên màn hình chính.
* **Tác nhân kích hoạt (Trigger)**: Giảng viên chọn nút **"Lịch Sử Đợt Chấm"** hoặc **"Tạo Đợt Chấm Mới"** trên giao diện chính.

##### Luồng sự kiện chính (Main Flow):
1. Giảng viên mở cửa sổ **"Lịch Sử & Quản Lý Đợt Chấm Điểm"** (`HistoryDialog`).
2. Hệ thống hiển thị thanh công cụ phía trên gồm:
   - Ô nhập tìm kiếm theo mã lớp (`QLineEdit`, lọc tức thời khi gõ).
   - Danh sách chọn môn học (`QComboBox`: "Tất cả môn học" hoặc các mã môn cụ thể `PRF`, `PRO`, `DSA`, `PHP`...).
   - Dòng tổng quan số lượng rõ ràng: `"{X} đợt chấm, {Y} bài nộp đã xử lý"`.
3. Bảng lịch sử liệt kê đầy đủ các đợt chấm với các cột: *Mã Lớp / Đợt Chấm*, *Môn Học*, *Ngôn Ngữ*, *Số Bài Nộp*, *Tiến Độ Chấm*, *Tỷ Lệ Đạt (AC)*, *Điểm Trung Bình*, và cột *Thao Tác*.
4. Giảng viên tìm thấy đợt chấm cần mở và nhấn nút viền xanh **"Mở Đợt Chấm"**.
5. Hệ thống nạp đợt chấm này lên màn hình làm việc chính, đồng bộ toàn bộ danh sách sinh viên, testcase và kết quả chấm đã lưu từ SQLite cục bộ. Hộp thoại đóng lại, Use Case kết thúc.

##### Luồng rẽ nhánh & Ngoại lệ (Alternative & Exception Flows):
* **A1 - Tạo đợt chấm mới**: Tại bước 2, Giảng viên có thể nhấn nút **"Tạo Đợt Chấm Mới"** để mở hộp thoại nhập tên lớp, môn học, ngôn ngữ lập trình và chọn thư mục bài nộp.
* **A2 - Xóa đợt chấm**: Giảng viên bấm nút chữ đỏ viền mảnh **"Xóa"** tại một hàng trong bảng. Hệ thống hiển thị hộp thoại xác nhận chi tiết: *"Xóa đợt {tên lớp} cùng {số lượng} bài nộp và toàn bộ kết quả chấm? Thao tác này không thể hoàn tác."* với 2 nút: **"Xóa"** (nền đỏ) và **"Hủy"**. Khi Giảng viên xác nhận, hệ thống thực hiện xóa mềm trong SQLite cục bộ và phát tín hiệu đồng bộ làm mới dữ liệu.
* **A3 - Trạng thái khi chưa có đợt chấm nào**: Nếu CSDL chưa có đợt chấm nào, bảng tự động ẩn và hiển thị thông báo *"Chưa có đợt chấm nào"* cùng nút bấm *"Tạo Đợt Chấm Mới"*.

---

#### 3.2.3. UC-08: Nạp Danh Sách Sinh Viên & Bài Nộp Từ File CSV (Import Submissions via `students.csv`)

* **Mã Use Case**: `UC-08`
* **Tên Use Case**: Nạp Danh Sách Sinh Viên & Bài Nộp từ File CSV (Import Submissions via `students.csv`)
* **Tác nhân chính**: Giảng viên (Instructor)
* **Tác nhân hỗ trợ ngoài**: Hệ thống tệp tin cục bộ (Local File System)
* **Mô tả tóm tắt**: Giảng viên nạp danh sách sinh viên dự thi thông qua file CSV chuẩn hóa tinh gọn gồm **đúng 2 cột: `MSSV,File`** (ví dụ: `students.csv`). Hệ thống tự động phân tích cú pháp CSV, đối chiếu với thư mục bài nộp trên máy để kiểm tra sự tồn tại của các file bài làm, và lập bảng danh sách bài nộp sẵn sàng cho quá trình chấm tự động.
* **Tiền điều kiện (Preconditions)**:
  1. Giảng viên đã tạo hoặc mở một đợt chấm bài (`UC-07`).
  2. Giảng viên đã chuẩn bị file `students.csv` và thư mục chứa các file bài nộp của sinh viên.
* **Hậu điều kiện (Postconditions)**:
  1. Toàn bộ danh sách sinh viên cùng đường dẫn bài nộp hợp lệ được nạp vào bộ nhớ và lưu vào bảng `submissions` trong SQLite cục bộ.
  2. Bảng danh sách bài nộp trên giao diện Desktop App hiển thị đầy đủ thông tin với trạng thái ban đầu là `Pending`.
* **Tác nhân kích hoạt (Trigger)**: Giảng viên nhấn nút **"Nạp File Sinh Viên (students.csv)"** trên màn hình Desktop App.

##### Luồng sự kiện chính (Main Flow):
1. Giảng viên nhấn nút **"Nạp Danh Sách (students.csv)"**.
2. Hộp thoại chọn tệp tin của hệ điều hành xuất hiện. Giảng viên chọn file `students.csv` từ máy tính.
3. Desktop App đọc file sử dụng module chuẩn `csv` của Python, tiến hành phân tích và kiểm tra tính hợp lệ của cấu trúc file:
   - Kiểm tra dòng tiêu đề (Header): Bắt buộc chứa 2 trường `MSSV` và `File`.
   - Đọc từng dòng dữ liệu: Trích xuất mã số sinh viên (ví dụ: `SE180001`) và tên file bài nộp (ví dụ: `SE180001_Lab1.c` hoặc tên thư mục câu hỏi `SE180001/`).
4. Hệ thống thực hiện kiểm tra đối chiếu (Cross-check Validation) giữa danh sách CSV và thư mục bài nộp:
   - Với mỗi dòng, kiểm tra xem file/thư mục tương ứng có thực sự tồn tại trong thư mục bài làm hay không.
   - Nếu tồn tại: Đánh dấu trạng thái `Ready`.
   - Nếu không tìm thấy file: Đánh dấu cảnh báo `File Missing` (Thiếu file).
5. Hệ thống hiển thị bảng duyệt trước (Preview Table) kèm tổng kết: "Đã nạp thành công X sinh viên (Y hợp lệ, Z thiếu bài)".
6. Giảng viên xem lại danh sách và bấm **"Xác nhận nạp"**.
7. Dữ liệu được lưu vào SQLite cục bộ và bảng danh sách chính trên giao diện được làm mới với đầy đủ các cột: MSSV, Tên bài nộp, Trạng thái (`Pending`). Use Case kết thúc.

##### Luồng rẽ nhánh & Ngoại lệ (Alternative & Exception Flows):
* **A1 - Kéo thả trực tiếp (Drag & Drop)**: Giảng viên có thể kéo thả trực tiếp file `students.csv` từ Windows Explorer vào vùng làm việc của ứng dụng. Hệ thống tự động kích hoạt tiến trình đọc file từ bước 3.
* **E1 - Sai định dạng file CSV (Invalid CSV Structure)**: Tại bước 3, nếu file thiếu một trong 2 cột chuẩn (`MSSV` hoặc `File`), hoặc file bị lỗi bảng mã (không phải UTF-8), hệ thống hiển thị hộp thoại lỗi: "Cấu trúc file CSV không hợp lệ. File bắt buộc phải có 2 cột tiêu đề: MSSV,File. Vui lòng kiểm tra lại".

---

### 3.3. Phân Hệ 3: Quản Lý Bộ Kiểm Thử & Chiến Lược So Khớp (Testcase & Matching Strategy)

---

#### 3.3.1. UC-09: Quản Lý Bộ Testcase Kiểm Thử Black-box Thủ Công (Manage Black-box Testcases Manually)

* **Mã Use Case**: `UC-09`
* **Tên Use Case**: Quản lý Bộ Testcase Kiểm thử Black-box Thủ công (Manage Black-box Testcases Manually)
* **Tác nhân chính**: Giảng viên (Instructor)
* **Tác nhân hỗ trợ ngoài**: Cơ sở dữ liệu SQLite cục bộ (`local_test_cases`)
* **Mô tả tóm tắt**: Giảng viên quản lý bộ kiểm thử hộp đen (Black-box Testcases) trực tiếp trên tab **"Testcase"** của cửa sổ Quản Lý Bộ Testcase & Chiến Lược So Khớp. Giảng viên định nghĩa các cặp **`INPUT` (dữ liệu nhập qua stdin)** và **`OUTPUT` (kết quả xuất qua stdout)**, cùng thông số giới hạn thời gian (ms), bộ nhớ (MB), trọng số điểm cho từng câu hỏi **mà hoàn toàn không cần phải viết hay nạp bất kỳ dòng mã giải mẫu (solution code) nào**.
* **Tiền điều kiện (Preconditions)**:
  1. Giảng viên đang trong một đợt chấm bài (`UC-07`).
* **Hậu điều kiện (Postconditions)**:
  1. Các cặp testcase được lưu vào bảng `local_test_cases` trong CSDL SQLite cục bộ của đợt chấm.
* **Tác nhân kích hoạt (Trigger)**: Giảng viên mở cửa sổ **"Quản Lý Bộ Testcase & Chiến Lược So Khớp"** trên Desktop App.

##### Luồng sự kiện chính (Main Flow):
1. Giảng viên mở cửa sổ Quản Lý Bộ Testcase & Chiến Lược So Khớp (mặc định mở tab **"Testcase"**).
2. Hệ thống hiển thị thanh công cụ lọc câu hỏi (`Q1`..`Q5` hoặc "Tất cả câu hỏi"), nút viền "Sinh Testcase Bằng AI" và nút viền **"Thêm Testcase"**.
3. Bảng testcase hiển thị danh sách các ca kiểm thử hiện có gồm 9 cột: `#`, `Câu Hỏi`, `INPUT (stdin)`, `OUTPUT (stdout)`, `Trọng Số`, `Giới Hạn (ms)`, `RAM (MB)`, `Chiến Lược`, và cột `Thao Tác` (chứa nút viền Sửa và Xóa được căn giữa dòng).
4. Giảng viên bấm nút viền **"Thêm Testcase"**: Hệ thống hiển thị hộp thoại `TestcaseEditDialog` cho phép nhập Câu hỏi, Trọng số điểm, Dữ liệu đầu vào (stdin), Kết quả kỳ vọng (stdout), Giới hạn thời gian (ms) và Giới hạn bộ nhớ (MB).
5. Giảng viên nhập đầy đủ dữ liệu và bấm **"Lưu Testcase"**.
6. Hệ thống thẩm định dữ liệu không được bỏ trống `OUTPUT (stdout)`, lưu testcase mới vào bảng `local_test_cases` trong SQLite và làm mới bảng hiển thị.
7. Tại chân cửa sổ, Giảng viên bấm nút chính **"Lưu"** để hoàn tất cấu hình. Use Case kết thúc.

##### Luồng rẽ nhánh & Ngoại lệ (Alternative & Exception Flows):
* **A1 - Chỉnh sửa / Xóa testcase**: Tại bước 3, Giảng viên có thể bấm nút "Sửa" trên từng dòng để mở form cập nhật thông số, hoặc bấm nút "Xóa" kèm hộp thoại xác nhận để loại bỏ testcase khỏi CSDL.
* **E1 - Bỏ trống dữ liệu kỳ vọng**: Tại bước 5, nếu trường `OUTPUT` bị bỏ trống, hệ thống hiển thị cảnh báo: *"Kết quả mong đợi (stdout) không được để trống."* và ngăn chặn lưu.

---

#### 3.3.2. UC-10: Tự Động Sinh Testcase Biên Bằng AI (Auto-Generate Boundary Testcases with Gemini AI)

* **Mã Use Case**: `UC-10`
* **Tên Use Case**: Tự động Sinh Testcase Biên bằng AI (AI Black-box Testcase Generator)
* **Tác nhân chính**: Giảng viên (Instructor)
* **Tác nhân hỗ trợ ngoài**: Web Server Backend (NestJS AI Hub), Google Gemini API
* **Mô tả tóm tắt**: Giảng viên dán nội dung tóm tắt đề bài và số lượng testcase cần sinh. Google Gemini AI tự động phân tích và sinh danh sách các cặp **`INPUT` và `OUTPUT kỳ vọng`** hoàn chỉnh (bao gồm các ca kiểm thử giá trị biên: số âm, chuỗi rỗng, giá trị cực đại, mảng rỗng...). Kết quả hiển thị dưới dạng bảng chọn lọc, cho phép nạp trực tiếp vào SQLite cục bộ mà **giảng viên hoàn toàn không cần phải viết code giải mẫu**.
* **Tiền điều kiện (Preconditions)**:
  1. Giảng viên đã đăng nhập tài khoản hợp lệ trên Desktop App.
  2. Hạn ngạch (Quota) gọi AI của Giảng viên trên Web Server Backend còn khả dụng.
* **Hậu điều kiện (Postconditions)**:
  1. Các cặp testcase được Giảng viên tick chọn sẽ được lưu vào bảng `local_test_cases` trong SQLite cục bộ của đợt chấm.
* **Tác nhân kích hoạt (Trigger)**: Giảng viên nhấn nút viền **"Sinh Testcase Bằng AI"** ở đầu tab Testcase.

##### Luồng sự kiện chính (Main Flow):
1. Giảng viên mở tab **"Testcase"** trên cửa sổ Quản Lý Bộ Testcase & Chiến Lược So Khớp và nhấn nút viền **"Sinh Testcase Bằng AI"**.
2. Hệ thống mở hộp thoại riêng `AiTestcaseDialog` gồm:
   - Ô nhập **"Đề bài"** (TextEdit).
   - Ô nhập **"Số lượng testcase"** (SpinBox, mặc định 4).
   - Nút thu gọn **"Tùy chọn"** (chứa Câu hỏi áp dụng và Ngôn ngữ lập trình, lấy mặc định từ đợt chấm đang mở).
   - Nút chính **"Sinh Testcase"** (nền xanh đặc) và nút viền **"Hủy"**.
3. Giảng viên dán đề bài và bấm **"Sinh Testcase"**.
4. Desktop App gửi request bất đồng bộ `POST /api/v1/ai/generate-testcases` tới Web Server Backend.
5. Web Server Backend kiểm tra hạn ngạch Token, gọi Google Gemini API để phân tích đề bài và sinh các testcase biên.
6. Backend trả về kết quả; Desktop App hiển thị bảng danh sách các testcase được đề xuất gồm: Checkbox chọn dòng, cột Input (stdin) và cột Expected Output (stdout) (tuyệt đối không hiển thị mã JSON thô). Nút "Thêm Các Testcase Đã Chọn" được kích hoạt.
7. Giảng viên đánh dấu tick các testcase phù hợp (hỗ trợ nút "Chọn Tất Cả", "Bỏ Chọn Tất Cả") và bấm **"Thêm Các Testcase Đã Chọn"**.
8. Hệ thống lưu các testcase đã chọn vào bảng `local_test_cases` trong SQLite cục bộ và làm mới bảng testcase. Hộp thoại đóng lại, Use Case kết thúc.

##### Luồng rẽ nhánh & Ngoại lệ (Alternative & Exception Flows):
* **E1 - Vượt hạn ngạch AI (Quota Limit Exceeded)**: Tại bước 5, nếu hạn ngạch token trong ngày đã hết, hệ thống hiển thị thông báo lỗi và ghi log kiểm toán.
* **E2 - Lỗi mạng / Dịch vụ AI gián đoạn**: Tại bước 5, nếu mất kết nối hoặc máy chủ AI phản hồi lỗi, Desktop App hiển thị thông báo thân thiện: *"Không kết nối được dịch vụ AI. Thử lại sau."* kèm nút **"Thử Lại"**. Mã lỗi kỹ thuật nội bộ chỉ được ghi vào file log, không hiển thị mã thô ra giao diện người dùng. Nút "Thêm Các Testcase Đã Chọn" tự động vô hiệu hóa khi chưa có kết quả.

---

#### 3.3.3. UC-11: Thiết Lập Động Cơ So Khớp Đầu Ra (Configure Output Matching Strategies)

* **Mã Use Case**: `UC-11`
* **Tên Use Case**: Thiết lập Động cơ So khớp Đầu ra (Configure Output Matching Strategies)
* **Tác nhân chính**: Giảng viên (Instructor)
* **Tác nhân hỗ trợ ngoài**: Cơ sở dữ liệu SQLite cục bộ
* **Mô tả tóm tắt**: Cung cấp cho Giảng viên quyền kết hợp linh hoạt 6 tiêu chí so khớp đầu ra trực tiếp tại tab **"So Khớp Đầu Ra"** trong cửa sổ Quản Lý Bộ Testcase & Chiến Lược So Khớp. Hệ thống hỗ trợ đa lựa chọn kết hợp nhiều cờ đồng thời hoặc khớp chính xác tuyệt đối từng byte (Exact Match).
* **Tiền điều kiện (Preconditions)**:
  1. Giảng viên đang trong một đợt chấm bài.
* **Hậu điều kiện (Postconditions)**:
  1. Chuỗi mã tổ hợp chiến lược so khớp (ví dụ: `IGNORE_WHITESPACE+CASE_INSENSITIVE` hoặc `EXACT_MATCH`) được lưu vào thuộc tính của đợt chấm và testcase trong SQLite cục bộ, sẵn sàng áp dụng cho quá trình chấm điểm tự động trong `UC-12`.
* **Tác nhân kích hoạt (Trigger)**: Giảng viên chọn tab **"So Khớp Đầu Ra"** trong cửa sổ Quản Lý Bộ Testcase & Chiến Lược So Khớp.

##### Luồng sự kiện chính (Main Flow):
1. Giảng viên chọn tab **"So Khớp Đầu Ra"** (nằm ngang hàng với tab "Testcase").
2. Hệ thống hiển thị giao diện gồm dòng mẹo ngắn gọn màu `#475569` (kích thước 13px) và lưới 6 ô checkbox thuần tiếng Việt kèm tooltip chi tiết:
   - **Bỏ qua khoảng trắng**: Bỏ qua khoảng trắng thừa và dấu xuống dòng ở đầu, cuối và giữa các từ (mặc định được chọn).
   - **Không phân biệt chữ hoa, chữ thường**: Chuyển đổi toàn bộ output về chữ thường trước khi đối sánh.
   - **Chấp nhận dung sai số thực**: Chấp nhận sai số dấu phẩy động với độ lệch cho phép $\le 10^{-5}$.
   - **Không phân biệt thứ tự từ hoặc số**: So khớp tập hợp các từ/số mà không phụ thuộc vào thứ tự in ra.
   - **So khớp biểu thức chính quy**: Sử dụng chuỗi đầu ra kỳ vọng như mẫu regex để kiểm tra đối sánh.
   - **Kiểm tra kịch bản chấm tùy biến**: Kích hoạt validator kiểm tra riêng biệt cho bài toán có nhiều nghiệm đúng.
3. Giảng viên tick chọn một hoặc nhiều tiêu chí kết hợp phù hợp với đề thi. Nếu bỏ chọn toàn bộ các ô, hệ thống tự động áp dụng chế độ khớp chính xác 100% từng byte (`EXACT_MATCH`).
4. Tại chân cửa sổ, Giảng viên nhấn nút chính duy nhất **"Lưu"** (nền xanh đặc).
5. Hệ thống lưu cấu hình so khớp vào bảng `local_classes` trong CSDL SQLite cục bộ và đóng cửa sổ. Use Case kết thúc.còn khả dụng.
* **Hậu điều kiện (Postconditions)**:
  1. Các cặp `INPUT` và `OUTPUT kỳ vọng` do AI sinh ra được Giảng viên phê duyệt sẽ lưu trữ vào CSDL SQLite cục bộ của đợt chấm.
* **Tác nhân kích hoạt (Trigger)**: Giảng viên nhấn nút **"Sinh Testcase bằng AI" (Generate with AI)** trên màn hình Quản lý Testcase.

##### Luồng sự kiện chính (Main Flow):
1. Giảng viên mở màn hình Quản lý Testcase của đợt chấm và chọn chức năng **"AI Testcase Generator"**.
2. Hệ thống hiển thị hộp thoại nhập thông tin bài toán: Tên câu hỏi (ví dụ: `Q1 - Kiểm tra số nguyên tố`), mô tả đề bài (Problem Statement), định dạng luồng nhập/xuất và các ràng buộc dữ liệu ($N \le 10^6$).
3. Giảng viên nhập nội dung hoặc nạp file đề bài dạng Markdown/Text và nhấn **"Bắt đầu sinh Testcase"**.
4. Hệ thống Desktop App đóng gói prompt gửi yêu cầu `POST /api/v1/ai/generate-testcases` kèm Bearer JWT Token lên Web Server Backend.
5. Web Server Backend thẩm định token, kiểm tra hạn ngạch token còn lại của Giảng viên và chuyển tiếp prompt đã chuẩn hóa cấu trúc JSON tới Google Gemini API qua SDK chính thức.
6. Gemini AI xử lý và phản hồi danh sách 5-10 testcase dạng JSON gồm:
   - Mục đích kiểm thử (ví dụ: "Số âm", "Mảng rỗng", "Giá trị cực đại $10^6$", "Số 0 và 1").
   - Dữ liệu đầu vào (`INPUT` - stdin).
   - Dữ liệu đầu ra kỳ vọng (`OUTPUT kỳ vọng` - stdout).
   - Điểm số đề xuất.
7. Hệ thống hiển thị bảng duyệt trước (Preview Table) cho Giảng viên trên Desktop UI.
8. Giảng viên xem lại, có thể chỉnh sửa trực tiếp nội dung input/output trên bảng và tick chọn các testcase đạt yêu cầu.
9. Giảng viên bấm nút **"Lưu vào bộ Testcase"**.
10. Hệ thống lưu các cặp testcase đã chọn vào SQLite cục bộ và cập nhật danh sách hiển thị trên giao diện chính. Use Case kết thúc.

##### Luồng rẽ nhánh & Ngoại lệ (Alternative & Exception Flows):
* **A1 - Chỉnh sửa trước khi lưu**: Tại bước 8, Giảng viên có thể nhấp đúp vào ô input/output để sửa nhanh dữ liệu mẫu trước khi nhấn lưu.
* **E1 - Vượt hạn ngạch AI (Quota Limit Exceeded)**: Tại bước 5, nếu hạn ngạch token của Giảng viên đã hết, hệ thống trả về thông báo lỗi `HTTP 429 Too Many Requests`: "Hạn ngạch AI của bạn đã hết cho hôm nay, vui lòng liên hệ Admin hoặc nhập testcase thủ công (`UC-09`)".
* **E2 - Lỗi mạng / API gián đoạn**: Tại bước 5, nếu mất kết nối Internet, hệ thống bắt ngoại lệ và hiển thị thông báo lỗi rõ ràng, cho phép thử lại hoặc chuyển sang nạp testcase thủ công (`UC-09`).

---

#### 3.3.3. UC-11: Thiết Lập Động Cơ So Khớp 7 Chế Độ (Configure 7 Output Matching Strategies)

* **Mã Use Case**: `UC-11`
* **Tên Use Case**: Thiết lập Động cơ So khớp 7 Chế độ (Configure 7 Output Matching Strategies)
* **Tác nhân chính**: Giảng viên (Instructor)
* **Tác nhân hỗ trợ ngoài**: Không *(Xử lý trực tiếp bởi Tầng nghiệp vụ Strategy Pattern của Desktop App)*
* **Mô tả tóm tắt**: Cung cấp cho Giảng viên quyền lựa chọn 1 trong 7 chiến lược so khớp đầu ra (`IMatchingStrategy`) hoặc kết hợp đa cờ (`FlexibleMatchingStrategy`) được hiện thực hóa qua **mẫu thiết kế Strategy Pattern** để đảm bảo việc chấm điểm phù hợp chính xác với từng yêu cầu bài toán (bỏ qua dấu cách thừa, không phân biệt hoa thường, so sánh số thực sai số delta, so khớp không thứ tự, Regex, hoặc chấm đặc biệt qua script).
* **Tiền điều kiện (Preconditions)**:
  1. Giảng viên đang trong giao diện chuẩn bị chấm điểm của một đợt chấm bài.
* **Hậu điều kiện (Postconditions)**:
  1. Chiến lược so khớp được chọn được gán vào đối tượng điều phối chấm bài (`MatchingContext`), sẵn sàng áp dụng cho toàn bộ quá trình so sánh `OUTPUT thực tế` và `OUTPUT kỳ vọng` trong `UC-12`.
* **Tác nhân kích hoạt (Trigger)**: Giảng viên chọn chế độ trong danh sách thả xuống **"Chế độ so khớp" (Matching Strategy)**.

##### Luồng sự kiện chính (Main Flow):
1. Trên màn hình điều khiển chấm bài, Giảng viên nhấp vào menu dropdown **"Chiến lược So khớp (Matching Strategy)"**.
2. Hệ thống hiển thị 7 chiến lược có sẵn kèm giải thích tóm tắt:
   - `ExactMatchStrategy`: Khớp chính xác 100% từng ký tự và dấu xuống dòng.
   - `IgnoreWhitespaceStrategy`: Tự động loại bỏ khoảng trắng thừa, tab và dấu xuống dòng `\r\n` ở cuối dòng/cuối văn bản (khuyến nghị cho các bài lập trình cơ bản).
   - `CaseInsensitiveStrategy`: Không phân biệt chữ hoa, chữ thường (ví dụ: `YES` khớp với `yes` hoặc `Yes`).
   - `FloatingPointToleranceStrategy`: So sánh giá trị số thực với ngưỡng sai số tuyệt đối/tương đối $\epsilon \le 10^{-5}$ cho các bài toán tính toán giải thuật.
   - `UnorderedTokensStrategy`: Tách chuỗi thành các từ/số độc lập và so khớp không phụ thuộc vào thứ tự xuất hiện (ví dụ bài toán: "In ra các ước số của N").
   - `RegexPatternStrategy`: Kiểm tra xem đầu ra của sinh viên có thỏa mãn biểu thức chính quy Regex định nghĩa sẵn hay không.
   - `SpecialJudgeStrategy`: Cho phép chỉ định một file script Python kiểm thử riêng (`checker.py`) đối với các bài toán có nhiều đáp án đúng (Multiple Valid Solutions).
3. Giảng viên lựa chọn chiến lược mong muốn (ví dụ: `IgnoreWhitespaceStrategy`).
4. Nếu chọn các chế độ có tham số (như `FloatingPointToleranceStrategy` hoặc `SpecialJudgeStrategy`), hệ thống hiển thị ô nhập bổ sung (nhập sai số $\epsilon$ hoặc nút chọn file `checker.py`).
5. Hệ thống ghi nhận lựa chọn vào cấu hình của đợt chấm. Khi bấm chấm (`UC-12`), `MatchingContext` sẽ nạp lớp hiện thực chiến lược tương ứng để thực hiện so khớp. Use Case kết thúc.

##### Luồng rẽ nhánh & Ngoại lệ (Alternative & Exception Flows):
* **A1 - Cấu hình chiến lược riêng cho từng câu hỏi**: Giảng viên có thể thiết lập mỗi câu hỏi một chiến lược khác nhau (ví dụ: Câu 1 kiểm tra chuỗi dùng `IgnoreWhitespace`, Câu 2 tính toán số học dùng `FloatingPointTolerance`).
* **E1 - File Special Judge không hợp lệ**: Tại bước 4, nếu file `checker.py` được chọn bị lỗi cú pháp hoặc thiếu hàm kiểm thử chuẩn, hệ thống thông báo: "File script kiểm tra đặc biệt không hợp lệ. Vui lòng kiểm tra lại mã nguồn checker".

---

### 3.4. Phân Hệ 4: Tự Động Thực Thi & Chấm Điểm (Execution & Automated Grading Pipeline)

---

#### 3.4.1. UC-12: Thực Thi Chấm Điểm Tự Động Hàng Loạt (Execute Batch Grading Pipeline)

* **Mã Use Case**: `UC-12`
* **Tên Use Case**: Thực thi Chấm điểm Tự động Hàng loạt (Batch Automated Grading Pipeline)
* **Tác nhân chính**: Giảng viên (Instructor)
* **Tác nhân hỗ trợ ngoài**: Sandbox Execution Runner (GCC/MinGW, Javac, Python Runtime, psutil)
* **Mô tả tóm tắt**: Hệ thống tự động duyệt qua toàn bộ bài nộp trong danh sách `students.csv` (chuẩn 2 cột: `MSSV,File`), kích hoạt luồng xử lý nền đa tiến trình song song (Parallel Subprocesses: 4-8 bài đồng thời). Với mỗi câu hỏi là một file độc lập có hàm `main()`, hệ thống nạp `INPUT` qua `stdin`, hứng `OUTPUT thực tế` qua `stdout` để so khớp với `OUTPUT kỳ vọng`, tính điểm từng câu và cộng dồn thành tổng điểm bài thi mà **hoàn toàn không gọi AI trong lúc chấm** để đạt tốc độ tối đa (15-30 giây cho 40-50 sinh viên).
* **Tiền điều kiện (Preconditions)**:
  1. Đợt chấm đã nạp file `students.csv` (`UC-08`).
  2. Đợt chấm đã có ít nhất một cặp `INPUT` / `OUTPUT kỳ vọng` (`UC-09` hoặc `UC-10`).
  3. Đường dẫn trình biên dịch môi trường đã được cấu hình sẵn sàng (`UC-06`).
  4. Đã lựa chọn một chiến lược so khớp đầu ra (`UC-11`).
* **Hậu điều kiện (Postconditions)**:
  1. Toàn bộ sinh viên được ghi nhận điểm số từng câu, tổng điểm bài thi và verdict chi tiết (`AC`, `WA`, `TLE`, `MLE`, `CE`, `RE`).
  2. Toàn bộ nhật ký thực thi (`stdout`, `stderr`, logs) được lưu trữ vào SQLite cục bộ.
* **Tác nhân kích hoạt (Trigger)**: Giảng viên bấm nút **"Bắt đầu chấm bài" (Start Batch Grading)**.

##### Luồng sự kiện chính (Main Flow):
1. Giảng viên kiểm tra lại danh sách sinh viên và cấu hình, sau đó nhấn nút **"Bắt đầu chấm bài"**.
2. Hệ thống kiểm tra môi trường biên dịch (`gcc`, `javac`, `python`) theo cấu hình.
3. Hệ thống khởi tạo hàng đợi chấm (Grading Queue) và kích hoạt luồng xử lý nền (`QThread` Worker Pool: chạy song song 4-8 subprocesses độc lập) để đảm bảo không làm đơ giao diện Desktop UI.
4. Với từng sinh viên trong hàng đợi:
   - Hệ thống quét thư mục bài làm của sinh viên để nhận diện các file câu hỏi độc lập (ví dụ: `Q1.c`, `Q2.c` hoặc `Q1.java`, `Q2.java` hoặc `q1.py`, `q2.py`).
   - Với mỗi file câu hỏi:
     - **Biên dịch**: `RunnerFactory` tạo Runner phù hợp (`CRunner`, `JavaRunner`, `PythonRunner`). `CompilerAdapter` thực hiện lệnh biên dịch mã nguồn sang file thực thi tạm thời. Nếu có lỗi cú pháp, gán `CE (Compile Error)` kèm toàn bộ nội dung lỗi từ `stderr`, cho 0 điểm câu đó và chuyển sang câu tiếp theo.
     - **Thực thi qua hàm `main()`**: Sandbox Runner khởi chạy subprocess thực thi file đã build:
       - Nạp dữ liệu `INPUT` của từng testcase vào luồng nhập chuẩn (`stdin`). Hàm `main()` tự nhận dữ liệu và truyền đối số vào các hàm con nội bộ của sinh viên.
       - Thư viện `psutil` theo dõi mức tiêu thụ RAM và CPU theo thời gian thực:
         - Nếu thời gian chạy $\ge \text{Time Limit}$, kill tiến trình và gán `TLE (Time Limit Exceeded)`.
         - Nếu bộ nhớ tiêu thụ $\ge \text{Memory Limit}$, kill tiến trình và gán `MLE (Memory Limit Exceeded)`.
         - Nếu tiến trình kết thúc với exit code khác 0, gán `RE (Runtime Error)`.
       - Nếu tiến trình hoàn tất thành công trong hạn mức: Thu nhận `OUTPUT thực tế` từ luồng xuất chuẩn (`stdout`).
     - **So khớp kết quả**: Động cơ so khớp (`MatchingStrategy` đã chọn trong `UC-11`) so sánh `OUTPUT thực tế` với `OUTPUT kỳ vọng`:
       - Nếu khớp theo tiêu chí: Gán `AC (Accepted)` và cộng điểm của câu hỏi đó.
       - Nếu không khớp: Gán `WA (Wrong Answer)`.
   - **Tổng hợp điểm**: Tính tổng điểm của bài thi: $\text{Total Score} = \text{Score\_Q1} + \text{Score\_Q2} + \dots$
5. Trong suốt quá trình thực thi, hệ thống liên tục phát tín hiệu (`pyqtSignal`) cập nhật thanh tiến độ (Progress Bar), hiển thị số bài đã chấm, số bài đạt/lỗi trên màn hình (`UC-13`).
6. Khi hàng đợi xử lý xong toàn bộ sinh viên, hệ thống lưu bảng điểm vào SQLite cục bộ và hiển thị thông báo hoàn thành (thời gian chấm 40-50 bài chỉ từ 15-30 giây). Bảng điểm tự động làm mới với đầy đủ điểm số. Use Case kết thúc.

##### Luồng rẽ nhánh & Ngoại lệ (Alternative & Exception Flows):
* **A1 - Hủy hoặc Tạm dừng đợt chấm**: Giảng viên có thể bấm nút **"Dừng chấm" (Stop)** bất kỳ lúc nào. Hệ thống gửi tín hiệu kết thúc an toàn đến các subprocess đang chạy, lưu kết quả những bài đã hoàn thành và đánh dấu các bài còn lại là `Pending`.
* **E1 - Thiếu trình biên dịch**: Tại bước 2, nếu máy trạm chưa cài GCC hoặc JDK, hệ thống bật cảnh báo và mở ngay cửa sổ **Cấu hình Môi trường** (`UC-06`).

---

#### 3.4.2. UC-13: Giám Sát Tiến Độ Chấm Thời Gian Thực (Monitor Real-Time Grading Progress)

* **Mã Use Case**: `UC-13`
* **Tên Use Case**: Giám sát Tiến độ Chấm Thời gian thực (Monitor Real-Time Grading Progress)
* **Tác nhân chính**: Giảng viên (Instructor)
* **Tác nhân hỗ trợ ngoài**: Không *(Cơ chế nội bộ đa luồng QThread & Signals/Slots của Desktop App)*
* **Mô tả tóm tắt**: Cung cấp giao diện trực quan cho Giảng viên theo dõi tiến độ chấm bài theo thời gian thực: thanh tiến trình phần trăm (Progress Bar), số bài đã hoàn thành / tổng số bài, chỉ báo trạng thái từng luồng worker và bảng log mini hiển thị sự kiện bài thi nào vừa hoàn tất cùng phán quyết verdict.
* **Tiền điều kiện (Preconditions)**:
  1. Quá trình chấm bài tự động hàng loạt (`UC-12`) đang được kích hoạt chạy nền.
* **Hậu điều kiện (Postconditions)**:
  1. Giảng viên nắm bắt được trạng thái chấm chi tiết mà không gặp hiện tượng đơ giật giao diện.
* **Tác nhân kích hoạt (Trigger)**: Tự động kích hoạt khi `UC-12` bắt đầu chạy (`<<include>>`).

##### Luồng sự kiện chính (Main Flow):
1. Khi `UC-12` bắt đầu, giao diện Desktop App hiển thị thanh tiến độ (Progress Bar) và bảng trạng thái thời gian thực.
2. Luồng xử lý nền (`QThread`) trong quá trình thực thi từng bài nộp sẽ phát tín hiệu `progress_updated(current, total, student_id, verdict)` lên luồng giao diện chính (UI Thread).
3. Giao diện Desktop App bắt tín hiệu qua cơ chế Qt Signals/Slots:
   - Cập nhật giá trị thanh tiến độ (ví dụ: `25/45 bài - 55%`).
   - Cập nhật các ô đếm nhanh (Counters): Số bài `AC` (màu xanh lá), `WA` (màu đỏ), `TLE`/`MLE` (màu vàng), `CE`/`RE` (màu tím).
   - Thêm một dòng thông báo ngắn vào khung nhật ký cuộn tự động: `[10:15:32] SE180005: Hoàn tất (Score: 8.5/10 - AC)`.
   - Cập nhật trực tiếp dòng của sinh viên đó trên bảng điểm chính sang trạng thái `Completed`.
4. Khi bài nộp cuối cùng được xử lý xong, thanh tiến trình đạt 100%, hệ thống phát âm thanh thông báo ngắn và hiển thị tổng kết thời gian thực thi (ví dụ: "Đã chấm xong 45 bài trong 18.2 giây"). Use Case kết thúc.

##### Luồng rẽ nhánh & Ngoại lệ (Alternative & Exception Flows):
* **A1 - Ẩn bớt bảng log chi tiết**: Giảng viên có thể bấm nút thu nhỏ (Minimize) khung log để dành toàn bộ không gian cho bảng điểm lớn.

---

#### 3.4.3. UC-14: Xem Chi Tiết Kết Quả & Nhật Ký Bài Nộp (View Submission Result & Execution Logs)

* **Mã Use Case**: `UC-14`
* **Tên Use Case**: Xem Chi tiết Kết quả & Nhật ký Bài nộp (View Submission Result & Execution Logs)
* **Tác nhân chính**: Giảng viên (Instructor)
* **Tác nhân hỗ trợ ngoài**: Cơ sở dữ liệu SQLite cục bộ, File System
* **Mô tả tóm tắt**: Cho phép Giảng viên nhấp đúp vào bất kỳ sinh viên nào trên bảng điểm để mở cửa sổ kiểm tra chi tiết (Submission Detail Inspector): xem mã nguồn bài nộp với cú pháp được tô màu, bảng chi tiết từng testcase (kết quả `INPUT`, `Expected Output`, `Actual Output`, thời gian chạy ms, RAM MB), và toàn bộ nhật ký lỗi `stdout` / `stderr`. Đây cũng là điểm mở rộng (`<<extend>>`) để kích hoạt phân tích lỗi AI (`UC-16`) hoặc điều chỉnh điểm (`UC-15`).
* **Tiền điều kiện (Preconditions)**:
  1. Bài nộp của sinh viên đã được chấm ít nhất một lần (`UC-12`).
* **Hậu điều kiện (Postconditions)**:
  1. Giảng viên hiểu rõ nguyên nhân bài nộp đạt điểm hoặc bị lỗi logic.
* **Tác nhân kích hoạt (Trigger)**: Giảng viên nhấp đúp chuột (Double Click) vào dòng của một sinh viên trên bảng điểm.

##### Luồng sự kiện chính (Main Flow):
1. Giảng viên nhấp đúp vào dòng của sinh viên cần kiểm tra trên bảng điểm chính (ví dụ: sinh viên `SE180002` bị `WA`).
2. Hệ thống mở cửa sổ pop-up **"Chi Tiết Bài Nộp & Nhật Ký Thực Thi" (Submission Inspector)**.
3. Cửa sổ chia thành 2 phân vùng trực quan:
   - **Vùng bên trái - Trình đọc mã nguồn (Code Viewer)**: Hiển thị mã nguồn bài nộp (`.c`, `.java`, `.py`) với số dòng và tô màu cú pháp (Syntax Highlighting). Cho phép chuyển đổi giữa các câu hỏi `Q1`, `Q2`, `Q3`.
   - **Vùng bên phải - Bảng kiểm thử & Nhật ký thực thi**:
     - Bảng chi tiết từng testcase: Mã testcase, Điểm số, Trạng thái (AC/WA/TLE/MLE/CE/RE), Thời gian chạy (ms), Bộ nhớ tiêu thụ (MB).
     - Hộp đối chiếu so sánh: Khi bấm vào 1 testcase bị sai (`WA`), hệ thống hiển thị song song 2 khung: `Đầu ra kỳ vọng` và `Đầu ra thực tế của sinh viên` kèm việc tô sáng các ký tự khác biệt.
     - Khung nhật ký hệ thống: Toàn bộ thông báo lỗi từ trình biên dịch (`gcc`/`javac` stderr) hoặc lỗi runtime traceback.
4. Giảng viên kiểm tra mã nguồn và kết quả kiểm thử của sinh viên.
5. Giảng viên đóng cửa sổ chi tiết khi xem xong. Use Case kết thúc.

##### Luồng rẽ nhánh & Ngoại lệ (Alternative & Exception Flows):
* **A1 - Kích hoạt AI phân tích lỗi**: Tại bước 4, nếu bài thi bị lỗi logic `WA`, Giảng viên có thể bấm nút **`[✨ AI Phân tích lỗi]`** để kích hoạt luồng mở rộng `UC-16`.
* **A2 - Điều chỉnh điểm số**: Giảng viên có thể bấm nút **"Sửa điểm thủ công"** để kích hoạt luồng mở rộng `UC-15`.

---

#### 3.4.4. UC-15: Chấm Lại & Điều Chỉnh Điểm Thủ Công (Re-grade & Override Scores Manually)

* **Mã Use Case**: `UC-15`
* **Tên Use Case**: Chấm lại & Điều chỉnh Điểm thủ công (Re-grade & Override Scores Manually)
* **Tác nhân chính**: Giảng viên (Instructor)
* **Tác nhân hỗ trợ ngoài**: Sandbox Execution Runner, Cơ sở dữ liệu SQLite cục bộ
* **Mô tả tóm tắt**: Cho phép Giảng viên chấm lại một bài nộp đơn lẻ (ví dụ sau khi sinh viên nộp bổ sung hoặc sửa testcase), hoặc ghi đè điểm số trực tiếp bằng tay kèm lý do điều chỉnh khi phát hiện sinh viên có giải thuật đặc biệt sáng tạo hoặc phát hiện sai sót trong testcase gốc.
* **Tiền điều kiện (Preconditions)**:
  1. Giảng viên đang xem chi tiết bài nộp của sinh viên (`UC-14`).
* **Hậu điều kiện (Postconditions)**:
  1. Điểm số mới được cập nhật trong SQLite cục bộ, đánh dấu cờ `is_overridden = True` kèm ghi chú giải trình của giảng viên.
  2. Bảng điểm chính cập nhật lại điểm tổng kết và hiển thị biểu tượng ghi đè điểm.
* **Tác nhân kích hoạt (Trigger)**: Giảng viên bấm nút **"Chấm lại bài này" (Re-grade)** hoặc **"Ghi đè điểm" (Override Score)** trong cửa sổ chi tiết bài nộp.

##### Luồng sự kiện chính (Main Flow):
1. Trong cửa sổ Chi tiết bài nộp (`UC-14`), Giảng viên lựa chọn một trong hai hành động:
   - **Kịch bản Chấm lại**: Giảng viên bấm **"Chấm lại bài này"**.
     - Hệ thống kích hoạt Sandbox Runner thực thi riêng mã nguồn của sinh viên này với bộ testcase hiện tại.
     - Điểm số và verdict mới được cập nhật lại tự động.
   - **Kịch bản Điều chỉnh điểm thủ công**:
     - Giảng viên bấm nút **"Ghi đè điểm thủ công"**.
     - Hộp thoại xuất hiện cho phép Giảng viên nhập: Điểm số mới (thang điểm 10) và Lý do điều chỉnh (ví dụ: "Sinh viên in thêm câu chào nhưng thuật toán xử lý đúng 100%").
     - Giảng viên bấm **"Xác nhận ghi đè"**.
2. Hệ thống lưu điểm số mới vào SQLite cục bộ, cập nhật trường `manual_override_reason` và thời điểm chỉnh sửa.
3. Bảng điểm chính tại Desktop App làm mới dữ liệu, hiển thị điểm số mới kèm biểu tượng cây bút (biểu thị điểm đã qua can thiệp thủ công). Use Case kết thúc.

##### Luồng rẽ nhánh & Ngoại lệ (Alternative & Exception Flows):
* **E1 - Nhập điểm ngoài thang điểm hợp lệ**: Tại bước 1, nếu Giảng viên nhập điểm âm hoặc lớn hơn 10.0, hệ thống báo lỗi: "Điểm số phải nằm trong thang điểm từ 0.0 đến 10.0".

---

#### 3.4.5. UC-19: Chấm Điểm Bài Tập Web Tự Động (Automated Web Assignment Grading & Scoring)

* **Mã Use Case**: `UC-19`
* **Tên Use Case**: Chấm Điểm Bài Tập Web Tự Động (Automated Web Assignment Grading & Scoring)
* **Tác nhân chính**: Giảng viên (Instructor)
* **Tác nhân hỗ trợ ngoài**: Headless Browser Runner (Playwright / Chromium Engine), Local DOM Parser (`BeautifulSoup4`), Local CSS Linter (`tinycss2`), Central AI Gateway (`POST /api/v1/ai/evaluate-web-ui`, gọi OpenRouter Vision)
* **Mô tả tóm tắt**: Cung cấp phân hệ chấm điểm các bài tập thiết kế web (HTML5, CSS3, JavaScript) trực tiếp trên Desktop App của Giảng viên. Giảng viên nhập danh sách bài nộp từ **thư mục bài nộp cục bộ** (mỗi thư mục con tên là MSSV, bên trong có một file `.txt` chứa link **Live Website** và/hoặc **GitHub Repo**) — **không sử dụng `students.csv`**. Hệ thống thẩm định theo Rubric 4 thành phần rồi quy đổi về thang điểm 10. Kết quả được lưu vào bảng `local_web_submissions` trong SQLite cục bộ.
* **Tiền điều kiện (Preconditions)**:
  1. Giảng viên đã nhập danh sách bài nộp từ thư mục (mỗi thư mục con là một MSSV kèm file `.txt` chứa link), hoặc thêm/sửa thủ công từng bài nộp.
  2. Môi trường Desktop App đã tích hợp Playwright Headless Chromium cùng các thư viện phân tích cú pháp (`BeautifulSoup4`, `tinycss2`). Nếu thiếu Playwright/Chromium, engine tự động chuyển sang phân tích tĩnh mã nguồn HTML/CSS cục bộ.
* **Hậu điều kiện (Postconditions)**:
  1. Điểm 4 tiêu chí (`score_dom`, `score_lint`, `score_e2e`, `score_ui`), điểm tổng `total_score` và `verdict` được cập nhật vào bảng `local_web_submissions` qua `DatabaseManager.update_web_submission_scores()`.
  2. Ảnh chụp màn hình toàn trang được lưu trên đĩa tại `data/web_screenshots/`; nhật ký thẩm định (`rubric_log`) hiển thị tại hộp thoại chi tiết để phục vụ phúc khảo.
* **Tác nhân kích hoạt (Trigger)**: Giảng viên mở phân hệ "Chấm Bài Tập & Đồ Án Web" và nhấn nút **"Bắt Đầu Thẩm Định Web" (Start Web Grading)**.

##### Luồng sự kiện chính (Main Flow):
1. Giảng viên mở phân hệ "Chấm Bài Tập & Đồ Án Web" từ màn hình chọn phân hệ.
2. Giảng viên nhập bài nộp bằng một trong hai cách:
   - **Nhập từ thư mục**: chọn thư mục gốc; mỗi thư mục con là một MSSV chứa file `.txt` ghi link. Hệ thống quét, phân loại link (Live/Repo), chuẩn hóa link GitHub và phát hiện link đã thay đổi.
   - **Thêm thủ công / dán nhiều dòng**: nhập MSSV, họ tên, Live URL, GitHub Repo; hỗ trợ dán hàng loạt từ Excel/Google Sheets kèm kiểm tra trùng.
3. Hệ thống nạp danh sách bài nộp từ bảng `local_web_submissions` và hiển thị trên bảng kết quả.
4. Giảng viên nhấn nút **"Bắt Đầu Thẩm Định Web"**.
5. Desktop App khởi tạo `WebRubricEngine` và `WebGradingWorker` (chạy trên `QThread`) rồi chấm tuần tự từng bài nộp theo pipeline:
   - **Bước 5.1 - Render trang**: Playwright Chromium headless mở Live URL (hoặc file `index.html` cục bộ), trích xuất DOM HTML, CSS, các chỉ số tương tác và chụp ảnh toàn trang. Nếu render lỗi, engine ghi lý do vào nhật ký và chuyển sang phân tích tĩnh từ thư mục bài nộp.
   - **Bước 5.2 - Chấm DOM & Ngữ nghĩa (HTML Semantic Analysis)**: `BeautifulSoup4` kiểm tra sự hiện diện của các thẻ ngữ nghĩa (`header`, `nav`, `main`, `footer`, `section`, `article`, `aside`, `form`), phân cấp heading (`h1`/`h2`/`h3`), thuộc tính `alt` của ảnh và cấu trúc form.
   - **Bước 5.3 - Chấm chuẩn CSS (CSS Linting)**: `tinycss2` phát hiện lỗi cú pháp stylesheet, đánh giá việc dùng `@media` (responsive) và mức độ lạm dụng inline-style.
   - **Bước 5.4 - Chấm chức năng/tương tác**: đánh giá qua chỉ số số lượng `script`, số phần tử tương tác (`button`, `a`, `form`, `input`, `select`, `textarea`), số event listener và `onclick`.
   - **Bước 5.5 - Thẩm định giao diện UI/UX bằng AI Vision**: gửi ảnh chụp (base64) kèm danh sách tiêu chí rubric lên Central AI Gateway (`POST /api/v1/ai/evaluate-web-ui`, gọi OpenRouter) để đánh giá bố cục, phối màu, typography và tính responsive.
6. **Tổng hợp điểm số**: Hệ thống áp dụng công thức Rubric cố định:
   $$\text{Final Score} = 0.2 \times S_{DOM} + 0.2 \times S_{Lint} + 0.3 \times S_{Func} + 0.3 \times S_{UI}$$
7. Hệ thống cập nhật kết quả từng bài vào bảng `local_web_submissions` (`score_dom`, `score_lint`, `score_e2e`, `score_ui`, `total_score`, `verdict`) và hiển thị trực quan trên bảng kết quả; thanh tiến độ cập nhật theo thời gian thực (`UC-13`).
8. Giảng viên có thể nhấp vào từng sinh viên để xem điểm 4 tiêu chí, link Live/Repo và nhật ký thẩm định chi tiết. Use Case kết thúc.

##### Luồng rẽ nhánh & Ngoại lệ (Alternative & Exception Flows):
* **A1 - Chấm bài web không cần AI (Hoàn toàn Offline)**: Nếu máy trạm không có Internet hoặc không cấu hình AI, tiêu chí $S_{UI}$ (AI Vision) trả 0 điểm và hệ thống tự động phân bổ lại trọng số cho 3 tiêu chí offline ($S_{DOM}, S_{Lint}, S_{Func}$) theo tỷ lệ tương ứng để đạt tổng 100%.
* **A2 - Không có Playwright/Chromium**: Engine ghi nhận lý do vào nhật ký và chuyển sang phân tích tĩnh mã nguồn HTML/CSS trong thư mục bài nộp.
* **A3 - Điều chỉnh điểm từng tiêu chí thủ công**: Tương tự `UC-15`, tại màn hình xem chi tiết kết quả web, Giảng viên có thể ghi đè điểm kèm ghi chú giải trình.
* **E1 - Không tìm thấy mã nguồn HTML**: Nếu không render được Live URL và thư mục cục bộ không có `index.html`, engine trả `verdict = FAILED` với mã lỗi `NO_HTML`.
* **E2 - Website URL không truy cập được (HTTP 404 / 500 / Connection Refused)**: Playwright bắt exception, ghi nhận vào nhật ký và chuyển sang phân tích tĩnh; các tiêu chí không đánh giá được nhận 0 điểm.
* **E3 - Vòng lặp vô tận trong JavaScript (Infinite Loop / TLE)**: Playwright Timeout Guard (mặc định 5000ms) tự động ngắt tab, tiêu chí $S_{Func}$ nhận 0 điểm và hệ thống tiếp tục chấm các tiêu chí còn lại bình thường.

---

### 3.5. Phân Hệ 5: Tính Năng Thông Minh Có AI Hỗ Trợ (Smart AI-Assisted Capabilities)

---

#### 3.5.1. UC-16: Phân Tích Lỗi & Sinh Nhận Xét Sư Phạm On-Demand (Generate On-Demand AI Code Review)

* **Mã Use Case**: `UC-16`
* **Tên Use Case**: Phân tích Lỗi & Sinh Nhận xét Sư phạm On-Demand bằng AI (Generate On-Demand AI Code Review)
* **Tác nhân chính**: Giảng viên (Instructor)
* **Tác nhân hỗ trợ ngoài**: Web Server Backend (NestJS AI Hub), Google Gemini API
* **Mô tả tóm tắt**: Nhằm tối ưu hóa tài nguyên và tránh nghẽn API (Rate Limit 429), tính năng này vận hành theo cơ chế **On-Demand (Lazy Loading)**: Giảng viên chỉ kích hoạt thủ công khi xem chi tiết một bài nộp cụ thể bị lỗi logic (`WA`). Gemini AI phân tích mã nguồn đối chiếu với testcase sai và tự động sinh bản nhận xét sư phạm ngắn gọn, chỉ ra dòng code gây lỗi và gợi ý logic để sinh viên tự sửa. **Hệ thống bỏ qua hoàn toàn các bài bị lỗi biên dịch (`CE`)** vì đã có sẵn log chi tiết của trình biên dịch.
* **Tiền điều kiện (Preconditions)**:
  1. Bài nộp của sinh viên đã được chấm và có kết quả `WA`.
  2. Phiên làm việc của Giảng viên còn hạn ngạch gọi AI trên Web Backend.
* **Hậu điều kiện (Postconditions)**:
  1. Nội dung nhận xét sau khi Giảng viên duyệt sẽ được lưu vào thuộc tính `teacher_feedback` của bài nộp trong SQLite cục bộ và sẵn sàng xuất kèm ra cột nhận xét của file `results.csv` / Excel.
* **Tác nhân kích hoạt (Trigger)**: Giảng viên bấm nút **`[✨ AI Phân tích lỗi]`** trong cửa sổ Chi tiết bài nộp (`UC-14`).

##### Luồng sự kiện chính (Main Flow):
1. Giảng viên mở cửa sổ Chi tiết bài nộp của một sinh viên có kết quả `WA` (`UC-14`).
2. Giảng viên bấm nút **`[✨ AI Phân tích lỗi]`**.
3. Hệ thống Desktop App đóng gói ngữ cảnh gồm: mã nguồn câu hỏi bị sai, ngôn ngữ lập trình, dữ liệu testcase bị sai (`INPUT`, `Expected Output`, `Actual Output`).
4. Hệ thống gửi yêu cầu bất đồng bộ `POST /api/v1/ai/code-review` kèm JWT token đến Web Server Backend.
5. Web Server Backend thẩm định token, trừ hạn ngạch sử dụng và chuyển tiếp prompt chuẩn hóa tới Gemini AI với chỉ thị sư phạm: "Chỉ ra dòng code lỗi, giải thích bản chất lỗi thuật toán và đưa ra gợi ý tư duy cho sinh viên tự sửa, tuyệt đối không đưa ra toàn bộ code giải sẵn".
6. Gemini AI xử lý và trả về đoạn nhận xét sư phạm ngắn gọn (3-5 câu).
7. Hệ thống Desktop App hiển thị bản nháp nhận xét lên khung văn bản trên giao diện Desktop.
8. Giảng viên xem lại, có thể chỉnh sửa bổ sung nội dung bằng tay nếu muốn.
9. Giảng viên bấm **"Xác nhận & Lưu nhận xét"**.
10. Hệ thống lưu nội dung phản hồi vào cơ sở dữ liệu SQLite cục bộ và hiển thị tích xanh xác nhận. Use Case kết thúc.

##### Luồng rẽ nhánh & Ngoại lệ (Alternative & Exception Flows):
* **A1 - Bỏ qua bài lỗi biên dịch (`CE`)**: Nếu giảng viên nhấn nút trên một bài bị `CE`, hệ thống hiển thị thông báo hướng dẫn: "Bài nộp đã có sẵn thông báo lỗi cú pháp chi tiết từ trình biên dịch bên dưới, không cần sử dụng AI để phân tích để tránh lãng phí token".
* **E1 - Hết hạn ngạch AI**: Tại bước 5, nếu tài khoản giảng viên chạm trần hạn ngạch ngày, hệ thống trả về thông báo yêu cầu liên hệ Admin để cấp thêm quota.

---

#### 3.5.2. UC-17: Kiểm Tra Đạo Văn Qua Cơ Chế Lọc 2 Vòng (Two-Stage Plagiarism Detection)

* **Mã Use Case**: `UC-17`
* **Tên Use Case**: Kiểm tra Đạo văn qua Cơ chế Lọc 2 Vòng (Two-Stage Plagiarism Detection)
* **Tác nhân chính**: Giảng viên (Instructor)
* **Tác nhân hỗ trợ ngoài**: Google Gemini AI Hub (cho Vòng 2), AST Parsing Engine cục bộ
* **Mô tả tóm tắt**: Hệ thống triển khai quy trình phát hiện sao chép mã nguồn thông minh qua **2 vòng lọc**: Vòng 1 quét cây cú pháp trừu tượng AST / Winnowing 100% offline trên máy trạm để tính toán độ tương đồng giữa toàn bộ các cặp bài nộp trong 0.5 giây mà không tốn token; Vòng 2 chỉ chọn lọc 1-3 cặp bài có độ tương đồng bất thường vượt ngưỡng (> 80%) gửi lên Gemini AI để phân tích ngữ nghĩa chuyên sâu và trích xuất bằng chứng sao chép phục vụ lập biên bản.
* **Tiền điều kiện (Preconditions)**:
  1. Đợt chấm có từ hai bài nộp trở lên của cùng một câu hỏi.
* **Hậu điều kiện (Postconditions)**:
  1. Ma trận tương đồng (Similarity Matrix) được tạo lập kèm danh sách các cặp bài nghi vấn vượt ngưỡng.
  2. Bằng chứng vi phạm được trích xuất thành biên bản phục vụ kỷ luật thi cử.
* **Tác nhân kích hoạt (Trigger)**: Giảng viên nhấn nút **"Quét Đạo Văn" (Check Plagiarism)** trên thanh công cụ Desktop App.

##### Luồng sự kiện chính (Main Flow):
1. Giảng viên chọn đợt chấm cần kiểm tra, thiết lập ngưỡng cảnh báo (mặc định $\ge 80\%$) và nhấn **"Bắt đầu phân tích"**.
2. **Vòng 1 - Lọc cục bộ 100% Offline (Local AST Scanning)**:
   - Hệ thống tiền xử lý mã nguồn của tất cả sinh viên: loại bỏ comment, chuẩn hóa khoảng trắng, đổi tên định danh biến về dạng chuẩn, và biến đổi mã nguồn thành chuỗi token của cây cú pháp trừu tượng (Abstract Syntax Tree - AST).
   - Thuật toán Winnowing cục bộ so khớp toàn bộ các cặp bài nộp trong lớp ($O(N^2)$ xử lý siêu tốc trong 0.5 giây).
   - Hệ thống tính toán chỉ số tương đồng (%) cho từng cặp bài và kết xuất danh sách hiển thị trên giao diện theo thứ tự giảm dần.
3. Nếu không có cặp bài nào vượt ngưỡng $\ge 80\%$, hệ thống thông báo "Không phát hiện nghi vấn sao chép mã nguồn bất thường". Use Case kết thúc.
4. **Vòng 2 - Xác thực chuyên sâu bằng AI (AI Semantic Verification)**:
   - Với các cặp bài có độ tương đồng vượt ngưỡng $\ge 80\%$ (thường chỉ 1-3 cặp), hệ thống hiển thị cờ cảnh báo đỏ và cho phép Giảng viên bấm **`[✨ AI Phân tích bằng chứng]`**.
   - Desktop App gửi cấu trúc mã nguồn tóm tắt của 2 bài nghi vấn lên Gemini AI Hub thông qua Web Backend.
   - Gemini AI phân tích các thủ thuật gian lận tinh vi: đổi tên biến, đảo hàm, hoán đổi cấu trúc vòng lặp `for`/`while`, chèn code rác và trả về biên bản tóm tắt bằng chứng sao chép.
5. Giảng viên bấm vào cặp bài nghi vấn: Desktop App mở giao diện so sánh trực quan song song hai bên (Side-by-side Diff Viewer) với các đoạn code nghi vấn được tô sáng màu đỏ kèm nhận xét bằng chứng từ AI.
6. Giảng viên xác nhận đánh dấu vi phạm kỷ luật học thuật cho cặp bài nộp. Use Case kết thúc.

##### Luồng rẽ nhánh & Ngoại lệ (Alternative & Exception Flows):
* **A1 - Tùy chỉnh ngưỡng lọc**: Giảng viên có thể kéo thanh trượt điều chỉnh ngưỡng tương đồng (ví dụ: hạ xuống 70% hoặc nâng lên 90%) để lọc lại danh sách nghi vấn mà không cần quét lại từ đầu.

---

### 3.6. Phân Hệ 6: Báo Cáo, Đánh Giá Cục Bộ (Reporting & Local Export)

---

#### 3.6.1. UC-18: Xuất Báo Cáo Kết Quả Điểm (Export Gradebook)

* **Mã Use Case**: `UC-18`
* **Tên Use Case**: Xuất Báo Cáo Kết Quả Điểm (Export Gradebook)
* **Tác nhân chính**: Giảng viên (Instructor)
* **Tác nhân hỗ trợ ngoài**: Hệ thống tệp tin cục bộ (Local File System)
* **Mô tả tóm tắt**: Cho phép Giảng viên xuất bảng điểm của lớp sau khi chấm ra file định dạng chuẩn `results.csv` (7 cột chuẩn) và file bảng điểm chi tiết Excel (`.xlsx`) có tô màu trực quan kèm nhận xét của AI/giảng viên phục vụ việc nộp điểm cho phòng đào tạo và lưu trữ.
* **Tiền điều kiện (Preconditions)**:
  1. Đợt chấm đã có kết quả điểm của sinh viên (`UC-12`).
* **Hậu điều kiện (Postconditions)**:
  1. File `results.csv` hoặc file `.xlsx` được ghi thành công vào thư mục máy tính của Giảng viên.
* **Tác nhân kích hoạt (Trigger)**: Giảng viên nhấn nút **"Xuất Báo Cáo" (Export Gradebook)** trên Desktop App.

##### Luồng sự kiện chính (Main Flow):
1. Giảng viên nhấn nút **"Xuất Báo Cáo"** trên màn hình kết quả của Desktop App.
2. Hệ thống hiển thị hộp thoại lựa chọn định dạng xuất:
   - **File kết quả chuẩn `results.csv`**: Kế thừa 2 cột ban đầu từ `students.csv` và bổ sung đầy đủ 5 cột kết quả:
     - Cột 1: `MSSV`
     - Cột 2: `File`
     - Cột 3: `Điểm số` (thang điểm 10)
     - Cột 4: `Số testcase đạt` (ví dụ: `9/10`)
     - Cột 5: `Trạng thái` (`AC`, `WA`, `TLE`, `MLE`, `CE`, `RE`)
     - Cột 6: `Thời gian chạy trung bình (ms)`
     - Cột 7: `Nhận xét từ AI Gemini / Giảng viên`
   - **File bảng điểm Excel (`.xlsx`)**: Bảng điểm trình bày đẹp mắt, tự động định dạng điều kiện tô màu xanh cho bài đạt, màu đỏ cho bài lỗi, có kèm biểu đồ thống kê tỷ lệ điểm số của cả lớp.
3. Giảng viên chọn định dạng mong muốn và nhấn **"Xác nhận xuất"**.
4. Hộp thoại hệ điều hành (Native File Dialog) mở ra để Giảng viên chọn thư mục lưu và đặt tên file.
5. Hệ thống truy xuất dữ liệu từ SQLite cục bộ, xuất file và hiển thị thông báo "Xuất báo cáo thành công" kèm nút mở nhanh thư mục chứa file (`Open Folder`). Use Case kết thúc.

##### Luồng rẽ nhánh & Ngoại lệ (Alternative & Exception Flows):
* **E1 - File đang bị mở bởi ứng dụng khác**: Tại bước 5, nếu file đích đang được mở bằng Microsoft Excel khiến hệ thống không thể ghi đè (Permission Denied), Desktop App cảnh báo: "Không thể ghi file. File kết quả đang được mở bởi ứng dụng khác. Vui lòng đóng file và thử lại".
