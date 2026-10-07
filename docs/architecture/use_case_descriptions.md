# Tài Liệu Đặc Tả Chi Tiết Trường Hợp Sử Dụng (Use Case Descriptions Specification)

# Dự Án AITA: Automated Grading & Assessment Tool for Instructors

### Đề án Môn học SWD392: Thiết Kế Hệ Thống Có Hỗ Trợ Của AI (AI-Assisted System Design)
### Giai đoạn: Đánh giá 1 (Evaluation 1: Requirement Analysis & Modeling)

---

## 1. Giới Thiệu & Mục Đích Tài Liệu

Tài liệu này cung cấp bản đặc tả chi tiết từng bước (**Use Case Descriptions / Specifications**) cho toàn bộ **18 Use Cases** thuộc 6 phân hệ chức năng của hệ sinh thái **AITA (AI-Assisted Automated Grading & Assessment Tool)**. 

Bản đặc tả được xây dựng bám sát theo chuẩn Kỹ nghệ Phần mềm Quốc tế (IEEE 830 / RUP Template), đồng bộ 100% với kiến trúc hệ thống tại [system-overview.md](file:///d:/Java%20FPT/AITA/docs/architecture/system-overview.md), danh mục tác nhân và sơ đồ tại [actors_and_use_cases.md](file:///d:/Java%20FPT/AITA/docs/architecture/actors_and_use_cases.md) và ngăn xếp công nghệ tại [tech-stack.md](file:///d:/Java%20FPT/AITA/docs/architecture/tech-stack.md).

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

## 2. Ma Trận 18 Use Cases Theo 6 Phân Hệ Chức Năng

| Mã UC | Tên Use Case | Tác nhân chính | Giao diện thực hiện | Tác nhân ngoài hỗ trợ |
| :--- | :--- | :--- | :--- | :--- |
| **Phân hệ 1: Quản trị Hệ thống & Quản lý Xác thực (System Administration & Authentication)** | | | | |
| **UC-01** | Đăng nhập & Xác thực Hệ thống | Admin, Giảng viên | Web Admin / Desktop App | Web Server Backend |
| **UC-02** | Quản lý Tài khoản & Phân quyền Giảng viên | Admin | Web Admin Dashboard | Web Server Backend |
| **UC-04** | Cấu hình API Key & Giám sát Hạn ngạch AI | Admin | Web Admin Dashboard | Web Server Backend, Gemini AI Hub |
| **UC-05** | Xem Báo cáo Tổng quan & Lịch sử Chấm Toàn Trường | Admin | Web Admin Dashboard | Web Server Backend |
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
| **UC-19** | Chấm Điểm Bài Tập Web Tự Động | Giảng viên | Desktop App Client | Headless Browser, W3C Parser, Gemini AI Hub |
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
* **Tác nhân hỗ trợ ngoài**: Web Server Backend (FastAPI Auth Service, JWT & Bcrypt Engine)
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
* **Tác nhân hỗ trợ ngoài**: Web Server Backend (FastAPI RBAC Engine, SQLAlchemy ORM)
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
6. Backend thẩm định quyền Admin thông qua middleware `require_role(["admin"])`, kiểm tra tính hợp lệ của dữ liệu (email không trùng lặp, độ phức tạp mật khẩu), mã hóa mật khẩu bằng Bcrypt nếu có thay đổi và lưu vào CSDL qua SQLAlchemy.
7. Backend trả về thông báo thành công `HTTP 200/201`.
8. Web Admin Dashboard tự động tải lại bảng dữ liệu và hiển thị thông báo "Cập nhật tài khoản thành công". Use Case kết thúc.

##### Luồng rẽ nhánh & Ngoại lệ (Alternative & Exception Flows):
* **E1 - Trùng lặp Email hoặc Username**: Tại bước 6, nếu Email hoặc Username đã tồn tại trong CSDL, Backend trả về `HTTP 409 Conflict` ("Email hoặc Tên đăng nhập đã được sử dụng"). Giao diện Web hiển thị cảnh báo ngay tại ô nhập liệu tương ứng.
* **E2 - Admin tự khóa tài khoản của chính mình**: Nếu Quản trị viên cố gắng chuyển trạng thái tài khoản đang đăng nhập của mình thành vô hiệu hóa hoặc hạ quyền, hệ thống chặn lại và cảnh báo "Không thể tự vô hiệu hóa tài khoản Quản trị viên đang kích hoạt".



#### 3.1.3. UC-04: Cấu Hình API Key & Giám Sát Hạn Ngạch AI (Configure Centralized AI Key & Monitor Quotas)

* **Mã Use Case**: `UC-04`
* **Tên Use Case**: Cấu hình API Key & Giám sát Hạn ngạch AI (Configure Centralized AI Key & Monitor Quotas)
* **Tác nhân chính**: Quản trị viên (Admin)
* **Tác nhân hỗ trợ ngoài**: Web Server Backend, Google Gemini AI Hub
* **Mô tả tóm tắt**: Cung cấp cơ chế quản trị bảo mật tập trung cho dịch vụ AI: Quản trị viên thiết lập và bảo mật Google Gemini API Key tại máy chủ Web Backend (ngăn chặn rò rỉ key ra client máy trạm), cấu hình hạn mức tiêu thụ token/lượt gọi cho từng giảng viên theo ngày/tháng, và theo dõi biểu đồ tiêu thụ tài nguyên AI toàn trường theo thời gian thực.
* **Tiền điều kiện (Preconditions)**:
  1. Quản trị viên đã đăng nhập tài khoản quyền Admin trên Web Admin.
  2. Quản trị viên có Google Gemini API Key hợp lệ từ Google AI Studio.
* **Hậu điều kiện (Postconditions)**:
  1. API Key được mã hóa và lưu trữ an toàn trong biến môi trường hoặc bảng cấu hình bảo mật tại Web Backend.
  2. Định mức hạn ngạch (Rate Limit & Daily Token Quota) được áp dụng cho toàn bộ giảng viên.
* **Tác nhân kích hoạt (Trigger)**: Quản trị viên chọn mục **"Cấu hình & Giám sát AI" (AI Hub & Quota Monitor)** trên Web Admin.

##### Luồng sự kiện chính (Main Flow):
1. Quản trị viên mở phân hệ **"Quản lý AI & Giám sát Hạn ngạch"**.
2. Hệ thống tải thông tin tổng hợp:
   - Trạng thái kết nối Google Gemini API (Sẵn sàng / Lỗi).
   - Biểu đồ trực quan lượng token đã tiêu thụ hôm nay, tuần này và tháng này.
   - Bảng thống kê chi tiết mức tiêu thụ của từng Giảng viên (Số lượt sinh testcase, số lượt review lỗi, số token đã dùng).
3. Quản trị viên thực hiện cấu hình:
   - **Nhập / Đổi API Key**: Nhập Gemini API Key mới vào trường bảo mật (ký tự ẩn `••••••••`).
   - Bấm nút **"Kiểm tra kết nối" (Test Connection)**: Hệ thống gửi request ping nhẹ đến Google Gemini API để kiểm tra tính hợp lệ của Key.
   - **Thiết lập hạn mức**: Đặt trần hạn mức gọi token cho từng Giảng viên (ví dụ: tối đa 100.000 tokens/ngày) hoặc trần số lượt phân tích lỗi On-Demand.
4. Quản trị viên bấm nút **"Lưu Cấu Hình AI"**.
5. Client gửi yêu cầu `POST /api/v1/admin/ai-config` lên Backend.
6. Backend lưu trữ cấu hình bảo mật, thiết lập bộ đếm quota trong CSDL trung tâm và phản hồi xác nhận.
7. Web UI hiển thị thông báo cấu hình thành công kèm chỉ báo kết nối chuyển sang màu xanh (Active). Use Case kết thúc.

##### Luồng rẽ nhánh & Ngoại lệ (Alternative & Exception Flows):
* **A1 - Đặt lại hạn ngạch (Reset Quota) thủ công cho Giảng viên**: Khi một giảng viên cần chấm nhiều lớp trong kỳ thi và bị chạm trần hạn mức, Quản trị viên có thể bấm nút "Cấp thêm hạn ngạch" (+50.000 tokens) trực tiếp tại dòng của giảng viên đó.
* **E1 - API Key không hợp lệ**: Tại bước 3, khi kiểm tra kết nối, nếu Google Gemini API trả về lỗi xác thực `401/403 Invalid API Key`, hệ thống báo lỗi đỏ: "API Key không hợp lệ hoặc đã hết hạn từ Google AI Studio. Vui lòng kiểm tra lại". Không lưu key lỗi vào cấu hình.

---

#### 3.1.4. UC-05: Xem Báo Cáo Tổng Quan & Lịch Sử Chấm Toàn Trường (View School-wide Grading Reports & Logs)

* **Mã Use Case**: `UC-05`
* **Tên Use Case**: Xem Báo cáo Tổng quan & Lịch sử Chấm Toàn Trường (View School-wide Grading Reports & Logs)
* **Tác nhân chính**: Quản trị viên (Admin)
* **Tác nhân hỗ trợ ngoài**: Web Server Backend (Reporting Engine, Prisma ORM)
* **Mô tả tóm tắt**: Cung cấp cho Quản trị viên góc nhìn bao quát toàn bộ hoạt động học thuật và sử dụng AI trên hệ thống: tổng số tài khoản giảng viên, số lượt gọi AI đang hoạt động, biểu đồ tiêu thụ hạn ngạch Token Gemini theo giảng viên, và nhật ký kiểm toán hệ thống (Audit Logs).
* **Tiền điều kiện (Preconditions)**:
  1. Quản trị viên đã đăng nhập vào Web Admin Dashboard với quyền Admin.
* **Hậu điều kiện (Postconditions)**:
  1. Báo cáo thống kê tổng hợp và danh sách nhật ký được hiển thị đầy đủ, hỗ trợ lọc và xuất file báo cáo tổng kết.
* **Tác nhân kích hoạt (Trigger)**: Quản trị viên chọn mục **"Báo cáo Toàn trường & Lịch sử" (School-wide Analytics & Logs)**.

##### Luồng sự kiện chính (Main Flow):
1. Quản trị viên truy cập mục **"Báo cáo & Thống kê"**.
2. Hệ thống gửi yêu cầu `GET /api/v1/admin/reports/overview` lên Backend.
3. Backend tổng hợp dữ liệu từ bảng người dùng (`users`) và bảng nhật ký tiêu thụ AI (`ai_quota_logs`).
4. Giao diện hiển thị các khối trực quan:
   - Các chỉ số KPI tổng thể: Tổng số giảng viên, Tổng token AI đã tiêu thụ trong tháng.
   - Biểu đồ tần suất sử dụng các tính năng AI (Sinh testcase, Code review lỗi WA, Quét đạo văn Vòng 2).
   - Bảng nhật ký hoạt động hệ thống và kiểm toán (Giảng viên, Tính năng sử dụng, Số token tiêu hao, Thời gian gọi).
5. Quản trị viên có thể sử dụng bộ lọc: theo Giảng viên, hoặc theo Khoảng thời gian (Học kỳ / Tháng).
6. Quản trị viên có thể bấm nút **"Xuất Báo Cáo Tổng Hợp (PDF/Excel)"** để tải về máy tính báo cáo phục vụ quản lý chi phí API và nghiệm thu đào tạo. Use Case kết thúc.

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
* **Tác nhân hỗ trợ ngoài**: Cơ sở dữ liệu SQLite cục bộ (Local SQLite Database)
* **Mô tả tóm tắt**: Giảng viên tạo mới, mở lại, đổi tên hoặc lưu trữ các đợt chấm bài (Grading Sessions) theo từng lớp học và môn học cụ thể (ví dụ: `PRF192_SE1801_PracticalExam`). Mỗi đợt chấm là một không gian làm việc độc lập lưu trữ danh sách sinh viên, bộ testcase, kết quả điểm và nhật ký chấm.
* **Tiền điều kiện (Preconditions)**:
  1. Desktop App đã khởi động thành công.
* **Hậu điều kiện (Postconditions)**:
  1. Đợt chấm bài mới được khởi tạo và ghi vào CSDL SQLite cục bộ.
  2. Không gian làm việc của đợt chấm trở thành phiên hoạt động hiện thời (Active Session) trên giao diện.
* **Tác nhân kích hoạt (Trigger)**: Giảng viên nhấn nút **"Tạo Đợt Chấm Mới" (New Session)** hoặc **"Mở Đợt Chấm Cũ" (Open Session)**.

##### Luồng sự kiện chính (Main Flow):
1. Giảng viên chọn nút **"Tạo Đợt Chấm Mới"** trên giao diện chính của Desktop App.
2. Hệ thống hiển thị hộp thoại khởi tạo đợt chấm:
   - Tên đợt chấm (ví dụ: `Thi_Thuc_Hanh_PRF_Lop_SE1801`).
   - Chọn Môn học: Danh sách dropdown gồm `PRF (C)`, `PRO (Java/Python)`, `DSA (Java/Python)`, `PHP (Python)`.
   - Chọn Thư mục gốc chứa bài làm của sinh viên (Submission Directory).
   - Chọn số lượng câu hỏi của đề thi (ví dụ: Đề thi có 3 câu: `Q1`, `Q2`, `Q3`).
3. Giảng viên điền thông tin và bấm **"Khởi tạo"**.
4. Hệ thống tạo bản ghi mới trong bảng `sessions` của CSDL SQLite cục bộ, khởi tạo cấu trúc thư mục làm việc và tải giao diện bảng điểm trống tương ứng với môn học đã chọn.
5. Hệ thống kích hoạt đợt chấm này làm phiên làm việc chính và hiển thị tên đợt chấm lên thanh tiêu đề của ứng dụng. Use Case kết thúc.

##### Luồng rẽ nhánh & Ngoại lệ (Alternative & Exception Flows):
* **A1 - Mở lại đợt chấm đã có từ trước**: Tại bước 1, Giảng viên bấm nút "Mở Đợt Chấm Đã Lưu", chọn một đợt chấm trong danh sách lịch sử. Hệ thống nạp lại toàn bộ dữ liệu sinh viên, testcase và điểm số đã chấm dở trước đó lên bảng giao diện.
* **A2 - Xóa đợt chấm**: Giảng viên chọn một đợt chấm không còn dùng và nhấn "Xóa". Hệ thống yêu cầu xác nhận trước khi xóa bản ghi trong SQLite cục bộ.
* **E1 - Thư mục bài làm không tồn tại**: Tại bước 2, nếu thư mục bài nộp được chọn đã bị di chuyển hoặc xóa khỏi ổ đĩa, hệ thống hiển thị thông báo lỗi và yêu cầu chọn lại đường dẫn hợp lệ.

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
* **Tác nhân hỗ trợ ngoài**: Cơ sở dữ liệu SQLite cục bộ, File System
* **Mô tả tóm tắt**: Giảng viên quản lý bộ kiểm thử hộp đen (Black-box Testcases) trực tiếp trên giao diện Desktop App. Giảng viên chỉ cần định nghĩa các cặp **`INPUT` (dữ liệu nhập qua stdin)** và **`OUTPUT kỳ vọng` (kết quả xuất qua stdout)**, cùng thông số giới hạn thời gian (ms), bộ nhớ (MB) và điểm số cho từng câu hỏi/testcase **mà hoàn toàn không cần phải viết hay nạp bất kỳ dòng mã giải mẫu (solution code) nào**. Hỗ trợ xuất/nạp cả bộ testcase qua file `testcases.json`.
* **Tiền điều kiện (Preconditions)**:
  1. Giảng viên đang trong một đợt chấm bài (`UC-07`).
* **Hậu điều kiện (Postconditions)**:
  1. Các cặp testcase được lưu vào bảng `testcases` trong CSDL SQLite cục bộ của đợt chấm.
  2. Bộ testcase sẵn sàng được nạp vào Sandbox Runner khi chấm điểm.
* **Tác nhân kích hoạt (Trigger)**: Giảng viên chọn tab **"Quản lý Testcase" (Testcase Manager)** trên Desktop App.

##### Luồng sự kiện chính (Main Flow):
1. Giảng viên chuyển sang tab **"Quản lý Testcase"**.
2. Hệ thống hiển thị danh sách các testcase hiện có theo từng câu hỏi (`Q1`, `Q2`, `Q3`).
3. Giảng viên bấm nút **"Thêm Testcase (+)"**.
4. Một dòng mới hoặc form chi tiết xuất hiện, cho phép Giảng viên nhập:
   - Dữ liệu `INPUT` (chuỗi ký tự sẽ truyền vào `stdin` của hàm `main()`).
   - Dữ liệu `OUTPUT kỳ vọng` (chuỗi ký tự mong đợi xuất ra tại `stdout`).
   - `Time Limit` (ms) (mặc định kế thừa từ cấu hình: ví dụ 1000 ms).
   - `Memory Limit` (MB) (mặc định 256 MB).
   - `Điểm số` (ví dụ: 1.0 điểm / testcase).
5. Giảng viên có thể chỉnh sửa trực tiếp, nhân bản (Clone) hoặc bấm nút xóa testcase không mong muốn.
6. Giảng viên bấm **"Lưu bộ Testcase"**.
7. Hệ thống thẩm định dữ liệu không được để trống ô `INPUT` hoặc `OUTPUT kỳ vọng`, lưu toàn bộ testcase vào SQLite cục bộ và cập nhật tổng điểm tối đa của bài thi lên thanh trạng thái. Use Case kết thúc.

##### Luồng rẽ nhánh & Ngoại lệ (Alternative & Exception Flows):
* **A1 - Nạp / Xuất nhanh qua file JSON (Import/Export JSON)**:
  - Giảng viên bấm **"Import JSON"**, chọn file `testcases.json`. Hệ thống nạp tự động toàn bộ 20-30 testcase vào giao diện trong 1 click.
  - Giảng viên bấm **"Export JSON"** để lưu bộ testcase ra file bên ngoài nhằm tái sử dụng cho các kỳ thi tiếp theo.
* **E1 - Bỏ trống dữ liệu kỳ vọng**: Tại bước 6, nếu có dòng testcase bị bỏ trống trường `OUTPUT kỳ vọng`, hệ thống cảnh báo: "Testcase số X chưa có đầu ra kỳ vọng. Vui lòng điền dữ liệu trước khi lưu".

---

#### 3.3.2. UC-10: Tự Động Sinh Testcase Biên Bằng AI (Auto-Generate Boundary Testcases with Gemini AI)

* **Mã Use Case**: `UC-10`
* **Tên Use Case**: Tự động Sinh Testcase Biên bằng AI (AI Black-box Testcase Generator)
* **Tác nhân chính**: Giảng viên (Instructor)
* **Tác nhân hỗ trợ ngoài**: Web Server Backend (FastAPI AI Hub), Google Gemini API
* **Mô tả tóm tắt**: Giảng viên dán nội dung đề bài và các ràng buộc bài toán. Google Gemini AI tự động phân tích và sinh danh sách 5-10 cặp **`INPUT` và `OUTPUT kỳ vọng`** hoàn chỉnh (bao gồm các trường hợp biên: số âm, chuỗi rỗng, mảng 0 phần tử, giá trị cực đại biên giới hạn kiểu dữ liệu). Dữ liệu sinh ra nạp thẳng vào bảng testcase của đợt chấm mà **giảng viên hoàn toàn không cần phải viết code giải mẫu**.
* **Tiền điều kiện (Preconditions)**:
  1. Giảng viên đã đăng nhập tài khoản hợp lệ trên Desktop App (có JWT token).
  2. Hạn ngạch (Quota) gọi AI của Giảng viên trên Web Server Backend còn khả dụng.
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
* **Mô tả tóm tắt**: Cung cấp cho Giảng viên quyền lựa chọn 1 trong 7 chiến lược so khớp đầu ra (`MatchingStrategy`) được hiện thực hóa qua **mẫu thiết kế Strategy Pattern** để đảm bảo việc chấm điểm phù hợp chính xác với từng yêu cầu bài toán (bỏ qua dấu cách thừa, không phân biệt hoa thường, so sánh số thực sai số delta, so khớp không thứ tự, Regex, hoặc chấm đặc biệt qua script).
* **Tiền điều kiện (Preconditions)**:
  1. Giảng viên đang trong giao diện chuẩn bị chấm điểm của một đợt chấm bài.
* **Hậu điều kiện (Postconditions)**:
  1. Chiến lược so khớp được chọn được gán vào đối tượng điều phối chấm bài (`GradingContext`), sẵn sàng áp dụng cho toàn bộ quá trình so sánh `OUTPUT thực tế` và `OUTPUT kỳ vọng` trong `UC-12`.
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
5. Hệ thống ghi nhận lựa chọn vào cấu hình của đợt chấm. Khi bấm chấm (`UC-12`), `GradingContext` sẽ nạp lớp hiện thực chiến lược tương ứng để thực hiện so khớp. Use Case kết thúc.

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
* **Tác nhân hỗ trợ ngoài**: Headless Browser Runner (Playwright / Chromium Engine), Local W3C & DOM Parser (`BeautifulSoup4` / `tinycss2` / `html-validate`), Git Subsystem (`git clone` shallow), Google Gemini AI Hub (API Gateway)
* **Mô tả tóm tắt**: Cung cấp phân hệ chấm điểm toàn diện cho các bài tập thiết kế và phát triển web (HTML5, CSS3, JavaScript, PHP) trực tiếp trên Desktop App của Giảng viên. Hệ thống hỗ trợ nguồn nộp bài linh hoạt thông qua file danh sách sinh viên `students.csv` (chứa link **Domain Website đã deploy**, link **GitHub Repo**, hoặc **cả hai**). Giảng viên có thể tùy chọn 3 chế độ chấm độc lập hoặc kết hợp:
  1. **Chế độ 1: Chỉ chấm Live Website (`LIVE_ONLY`)**: Thẩm định trực tiếp domain website đã deploy (Vercel, Netlify, Render, VPS,...).
  2. **Chế độ 2: Chỉ chấm GitHub Repo (`REPO_ONLY`)**: Tự động clone mã nguồn từ kho GitHub của sinh viên, thẩm định cấu trúc thư mục, chuẩn code và lịch sử commit.
  3. **Chế độ 3: Chế độ kết hợp (`HYBRID`)**: Thực hiện kiểm thử toàn diện cả Live Website lẫn GitHub Repo, đồng thời đối soát chéo (Cross-check) mã nguồn với DOM thực tế để chống gian lận lấy website của người khác nộp.
  Kết quả được lưu trữ độc lập vào bảng CSDL cục bộ riêng biệt `local_web_grading_results` theo khung tiêu chí Rubric 4 thành phần quy đổi về thang điểm 10.
* **Tiền điều kiện (Preconditions)**:
  1. Giảng viên đã nạp danh sách sinh viên `students.csv` với cấu trúc cột linh hoạt: `MSSV,Website_URL,Github_URL` (tùy theo yêu cầu đề bài, sinh viên có thể chỉ nộp Live URL, chỉ nộp GitHub URL, hoặc nộp cả hai). Hoặc Giảng viên nạp thư mục mã nguồn nộp bài offline cục bộ.
  2. Môi trường Desktop App đã tích hợp sẵn Playwright Headless Chromium và các thư viện phân tích cú pháp (`BeautifulSoup4`, `tinycss2`).
* **Hậu điều kiện (Postconditions)**:
  1. Kết quả chấm được lưu riêng biệt vào bảng `local_web_grading_results` trong SQLite cục bộ (gồm: `website_url`, `github_url`, `grading_mode`, điểm thành phần `score_dom`, `score_lint`, `score_func`, `score_ui`, điểm tổng `final_score`, phán quyết `final_verdict`, chi tiết `rubric_log`).
  2. Toàn bộ ảnh chụp màn hình giao diện (Screenshots) ở cả 2 viewport (Desktop `1920x1080` & Mobile `375x667`) cùng nhật ký kiểm thử được lưu trữ để phục vụ phúc khảo.
  3. Bảng điểm Desktop App hiển thị trạng thái đạt/lỗi trực quan và sẵn sàng xuất báo cáo độc lập.
* **Tác nhân kích hoạt (Trigger)**: Giảng viên chuyển sang phân hệ "Chấm Bài Web", chọn chế độ chấm và nhấn nút **"Bắt đầu chấm Web" (Start Web Grading)**.

##### Luồng sự kiện chính (Main Flow):
1. Giảng viên chọn đợt chấm thuộc môn học có nội dung lập trình web (ví dụ: `PHP`, `Web Development / PRF`).
2. Giảng viên chọn **Chế độ chấm (Grading Mode)** phù hợp với đợt thi:
   - **Lựa chọn A - Live Website Only (`LIVE_ONLY`)**: Chấm theo domain đã deploy. Phù hợp với bài thi triển khai thực tế, không yêu cầu clone mã nguồn.
   - **Lựa chọn B - GitHub Repo Only (`REPO_ONLY`)**: Chấm theo source code repository. Phù hợp với bài tập mã nguồn, yêu cầu kiểm tra code convention và commit.
   - **Lựa chọn C - Hybrid Mode (`HYBRID`)**: Chấm kết hợp cả domain và repo. Phù hợp với đồ án môn học lớn, đảm bảo tính xác thực cao nhất.
3. Giảng viên thiết lập các trọng số trong bảng cấu hình **"Tiêu chí & Rubric Chấm Web"**:
   - **$w_1$ (DOM Structure & Semantics)**: Thẻ HTML ngữ nghĩa, cấu trúc layout, form attributes, SEO/Accessibility cơ bản (Mặc định: 30%).
   - **$w_2$ (W3C Validation & Code Style / Git Audit)**: Chuẩn cú pháp W3C HTML5/CSS3 offline và tính đều đặn của Git commits (Mặc định: 10%).
   - **$w_3$ (Interactive Functional Testing)**: Kịch bản Playwright giả lập người dùng thao tác tương tác giao diện (Mặc định: 40%).
   - **$w_4$ (Visual & Quality Assessment)**: Gemini Vision AI chấm bố cục thẩm mỹ hoặc Lighthouse Performance Audit (Mặc định: 20%).
4. Giảng viên nhấn nút **"Bắt đầu chấm Web"**.
5. Desktop App khởi tạo luồng xử lý ngầm đa luồng (`QThread` Worker Pool) và tiến hành chấm tuần tự từng bài nộp:
   - **Bước 5.1 - Tiếp nhận nguồn bài nộp theo Chế độ**:
     - *Nếu chế độ có `REPO_ONLY` hoặc `HYBRID`*: Hệ thống gọi tiến trình Git nội bộ thực hiện shallow clone repo (`git clone --depth 1 <github_url> <temp_dir>`) vào thư mục tạm cục bộ. Phân tích lịch sử commit (`git log`) để ghi nhận tần suất code và kiểm tra tài khoản tác giả.
     - *Nếu chế độ `LIVE_ONLY`*: Bỏ qua bước clone, trích xuất trực tiếp `website_url` của sinh viên.
     - *Nếu chấm thư mục offline cục bộ*: Nhận diện file `index.html` hoặc tự khởi tạo máy chủ PHP tạm (`php -S 127.0.0.1:<port>`).
   - **Bước 5.2 - Kiểm tra cấu trúc DOM & Ngữ nghĩa (HTML Semantic Analysis)**:
     - Parser `BeautifulSoup4` quét cây DOM (từ file offline hoặc DOM render sau khi Playwright nạp trang live): kiểm tra sự hiện diện của các thẻ bắt buộc theo checklist đề bài (ví dụ: `<header>`, `<nav>`, `<footer>`, `<form>`, `<table>`, `<input type="email">`, thuộc tính `required`, thuộc tính `alt`).
     - Tính điểm $S_{DOM} = \frac{\text{Số tiêu chí DOM đạt}}{\text{Tổng số tiêu chí DOM}} \times 10$.
   - **Bước 5.3 - Quét chuẩn cú pháp W3C, Linter & Git Quality**:
     - Với chế độ có Repo: Trình quét W3C offline phân tích toàn bộ file `.html` và `.css` trong repo. Đếm số lỗi (`Errors`) và cảnh báo (`Warnings`). Đánh giá lịch sử commit (trừ điểm nếu chỉ commit 1 lần duy nhất ngay trước giờ nộp).
     - Với chế độ `LIVE_ONLY`: Quét HTML source tải về từ trang web qua W3C validator parser.
     - Tính điểm $S_{Lint} = \max(0, 10 - \text{Errors} \times 1.0 - \text{Warnings} \times 0.2)$.
   - **Bước 5.4 - Kiểm thử chức năng tương tác (Playwright Headless Testing)**:
     - Khởi chạy trình duyệt không đầu Chromium (`playwright-python`), mở URL trang web (Live URL hoặc Localhost server).
     - Tự động thực thi kịch bản kiểm thử: điền form, click button, kích hoạt modal, kiểm tra thay đổi trạng thái giỏ hàng / danh sách, kiểm tra responsive layout ở 2 viewport (`1920x1080` Desktop và `375x667` Mobile).
     - Tính điểm $S_{Func} = \frac{\text{Số test case tương tác Pass}}{\text{Tổng số test case tương tác}} \times 10$.
   - **Bước 5.5 - Chụp ảnh màn hình & Thẩm định giao diện AI Multimodal**:
     - Playwright tự động chụp ảnh màn hình bài nộp (screenshot full-page độ phân giải cao).
     - Nếu có Internet và bật tiêu chí AI: Gửi ảnh chụp kèm rubric lên Gemini AI Hub để đánh giá độ hài hòa màu sắc, tính cân đối của bố cục và phát hiện dùng template có sẵn.
     - Tính điểm $S_{UI}$ (thang điểm 10).
   - **Bước 5.6 - Đối soát chéo chống gian lận (Dành riêng cho chế độ `HYBRID`)**:
     - Hệ thống so khớp hash của các file assets tĩnh (CSS, JS, images) tải từ Live Website với file mã nguồn tương ứng trong GitHub Repo.
     - Nếu phát hiện độ sai lệch lớn hoặc Live Website trỏ về sản phẩm không khớp mã nguồn trong Repo, hệ thống gắn cờ cảnh báo nghi vấn gian lận (`FLAGGED_MISMATCH`) để Giảng viên lưu ý.
6. **Tổng hợp điểm số**: Hệ thống áp dụng công thức Rubric:
   $$\text{Final Score} = w_1 \times S_{DOM} + w_2 \times S_{Lint} + w_3 \times S_{Func} + w_4 \times S_{UI}$$
7. Hệ thống ghi toàn bộ kết quả vào bảng `local_web_grading_results` trong SQLite cục bộ (`submission_id`, `website_url`, `github_url`, `grading_mode`, các điểm thành phần, `final_score`, `final_verdict`, `screenshot_path`, `rubric_log`).
8. Thanh tiến độ chấm trên giao diện cập nhật thời gian thực (`UC-13`).
9. Sau khi hoàn thành toàn bộ lớp, giao diện hiển thị bảng điểm trực quan. Giảng viên có thể nhấp vào từng sinh viên để xem ảnh chụp màn hình trang web, xem link live, link repo và chi tiết lỗi của từng tiêu chí. Use Case kết thúc.

##### Luồng rẽ nhánh & Ngoại lệ (Alternative & Exception Flows):
* **A1 - Chấm bài web không cần AI (Hoàn toàn Offline)**: Nếu máy trạm của giảng viên không có Internet hoặc muốn tiết kiệm Quota AI, giảng viên bỏ chọn tiêu chí $w_4$ (AI Multimodal). Hệ thống tự động phân bổ lại trọng số cho 3 tiêu chí offline ($w_1, w_2, w_3$) để đạt tổng 100%. Quá trình chấm diễn ra 100% offline với tốc độ siêu tốc (1-2 giây / bài).
* **A2 - Điều chỉnh điểm từng tiêu chí thủ công**: Tương tự như `UC-15`, tại màn hình xem chi tiết kết quả web, Giảng viên có thể ghi đè điểm của bất kỳ tiêu chí thành phần nào (ví dụ: cộng điểm sáng tạo giao diện) kèm ghi chú giải trình.
* **E1 - Website URL không truy cập được (HTTP 404 / 500 / Connection Refused)**: Ở chế độ `LIVE_ONLY` hoặc `HYBRID`, nếu trang web của sinh viên bị sập hoặc domain sai: hệ thống thử lại 2 lần (retry backoff). Nếu vẫn lỗi, gán phán quyết `FAILED` với mã lỗi `ERR_LIVE_UNREACHABLE` và cho 0 điểm các tiêu chí tương tác trực tiếp.
* **E2 - Repo GitHub không tồn tại hoặc ở chế độ Private**: Ở chế độ `REPO_ONLY` hoặc `HYBRID`, nếu link repo bị 404 hoặc private không clone được: ghi nhận mã lỗi `ERR_REPO_PRIVATE` và cho 0 điểm phần audit repo.
* **E3 - Vòng lặp vô tận trong JavaScript (Infinite Loop / TLE)**: Tại bước 5.4, nếu mã JavaScript của sinh viên chứa vòng lặp vô tận gây treo trình duyệt, Playwright Timeout Guard (cấu hình mặc định 5000ms) sẽ tự động ngắt tab, ghi nhận tiêu chí $S_{Func} = 0$ với verdict `TLE` (Time Limit Exceeded) và tiếp tục chấm các tiêu chí khác bình thường.

---

### 3.5. Phân Hệ 5: Tính Năng Thông Minh Có AI Hỗ Trợ (Smart AI-Assisted Capabilities)

---

#### 3.5.1. UC-16: Phân Tích Lỗi & Sinh Nhận Xét Sư Phạm On-Demand (Generate On-Demand AI Code Review)

* **Mã Use Case**: `UC-16`
* **Tên Use Case**: Phân tích Lỗi & Sinh Nhận xét Sư phạm On-Demand bằng AI (Generate On-Demand AI Code Review)
* **Tác nhân chính**: Giảng viên (Instructor)
* **Tác nhân hỗ trợ ngoài**: Web Server Backend (FastAPI AI Hub), Google Gemini API
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
