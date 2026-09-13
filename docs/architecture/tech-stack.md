# Đặc Tả Công Nghệ Sử Dụng (Technology Stack)

## Dự án: AITA - Automated Grading & Assessment Tool for Instructors

Tài liệu này quy định toàn bộ ngăn xếp công nghệ (Tech Stack), các thư viện bên thứ ba và công cụ nền tảng được sử dụng để xây dựng hệ sinh thái tích hợp **AITA** gồm: **Web Server Backend (NestJS / TypeScript)**, **Trang Web Admin Quản Lý (Next.js / TypeScript)** và **Desktop App Client (PyQt6 / Python dành cho Giảng viên)**.

---

## 1. Tổng Quan Ngăn Xếp Công Nghệ Hệ Sinh Thái (Ecosystem Tech Stack Overview)

```text
+------------------------------------+       +------------------------------------+
|   WEB ADMIN DASHBOARD (Next.js)    |       | DESKTOP APP CLIENT (PyQt6/Python)  |
|  - Dành cho Quản trị viên (Admin)  |       |  - Dành cho Giảng viên (Instructor)|
|  - React 18+, TypeScript, Tailwind |       |  - QThread xử lý đa luồng          |
|  - Quản trị User, Môn, Quota AI    |       |  - Chấm bài CSV hàng loạt 7 chế độ |
+------------------------------------+       +------------------------------------+
                  │                                             │
                  │ (HTTPS / JSON RESTful API)                  │ (REST API & Auth Sync)
                  ▼                                             ▼
+---------------------------------------------------------------------------------+
|                   WEB SERVER BACKEND (NestJS / TypeScript Service)              |
|  - Framework: NestJS (Kiến trúc Clean/Modular Architecture chuẩn doanh nghiệp)  |
|  - Runtime: Node.js (v20 LTS), TypeScript                                       |
|  - Phân quyền & Bảo mật (Auth & RBAC): Passport-JWT, Guards, Bcrypt Hashing     |
|  - Thẩm định dữ liệu (Validation): class-validator, class-transformer           |
|  - Tầng dữ liệu & ORM: Prisma ORM / TypeORM                                     |
|  - Điều phối AI: Gemini AI Hub (Quản lý hạn ngạch Token Quota & API Key bí mật) |
|  - Tài liệu API: Swagger OpenAPI (@nestjs/swagger)                              |
+---------------------------------------------------------------------------------+
                                         │
                                         ▼
+---------------------------------------------------------------------------------+
|                 CƠ SỞ DỮ LIỆU TRUNG TÂM (Centralized Database)                  |
|  - Môi trường Dev/Demo: SQLite (dev.db) hoặc PostgreSQL cục bộ                  |
|  - Môi trường Production: PostgreSQL (Hỗ trợ mở rộng & bảo mật cao)            |
+---------------------------------------------------------------------------------+
```

---

## 2. Ngăn Xếp Công Nghệ Chi Tiết Từng Thành Phần

### 2.1. Web Server Backend (NestJS / TypeScript)

- **Framework cốt lõi**: **NestJS (>= 10.x)**
  - *Lý do*: NestJS được xây dựng nguyên bản theo chuẩn **Clean Architecture / Modular Architecture** và Dependency Injection (DI) tương tự như Spring Boot hay ASP.NET Core. Giúp mã nguồn phân tầng rõ rệt (Module, Controller, Service/Use Case, DTO, Entity), đáp ứng tiêu chí cao nhất của môn SWD392.
  - Tự động sinh tài liệu Swagger UI chuẩn OpenAPI (`/api/docs`).
- **Xác thực & Phân quyền (Authentication & RBAC)**:
  - **Passport-JWT (`@nestjs/passport`, `@nestjs/jwt`)**: Cấp phát và thẩm định JSON Web Token với thuật toán `HS256`. Token chứa payload định danh và Role (`admin`, `instructor`).
  - **Bcrypt (`bcrypt`)**: Băm mật khẩu (Password Hashing) an toàn chuẩn công nghiệp.
  - **Guards & Decorators (`@UseGuards(JwtAuthGuard, RolesGuard)`, `@Roles('admin')`)**: Chặn truy cập trái phép cấp Controller và Route.
- **Mô hình hóa dữ liệu & ORM**:
  - **Prisma ORM / TypeORM**: Quản lý schema dữ liệu, quan hệ bảng và migration an toàn kiểu dữ liệu (Type-safe).
  - **`class-validator` & `class-transformer`**: Thẩm định chặt chẽ Payload đầu vào trước khi vào tầng xử lý logic.

### 2.2. Trang Web Admin Quản Lý (Next.js / TypeScript Frontend)

- **Mục đích**: **Dành riêng cho Quản trị viên (Admin)** quản lý toàn bộ hệ thống (không phải web portal dành cho học sinh).
- **Công nghệ Frontend**: **Next.js 14+ (App Router), React 18+, TypeScript**
  - **Giao diện & UI**: **TailwindCSS**, kết hợp bộ icon **Lucide-react** và các thư viện component hiện đại (Shadcn/UI).
  - **Giao tiếp API**: Sử dụng **Axios** hoặc **Fetch API** kết hợp Interceptor tự động gán Bearer Token.
- **Chức năng trọng tâm của Web Admin Dashboard**:
  1. **Quản lý tài khoản Giảng viên & Phân quyền**: Tạo mới, chỉnh sửa thông tin, khóa tài khoản và gán Role (`admin`, `instructor`).
  2. **Quản lý danh mục học thuật**: Quản lý danh mục 4 môn học lập trình cốt lõi (PRF, PRO, DSA, PHP).
  3. **Giám sát hạn ngạch AI (Gemini Quota Management)**: Cấu hình API Key tập trung, thiết lập trần Token Quota hàng ngày cho từng giảng viên, theo dõi số token tiêu thụ theo thời gian thực.
  4. **Báo cáo & Thống kê toàn trường**: Xem tổng hợp số phiên chấm và biểu đồ điểm số các môn thi toàn trường.

### 2.3. Desktop App Client (Ứng Dụng Chấm Bài Dành Cho Giảng Viên - Python / PyQt6)

- **Giao diện Desktop (GUI Framework)**: **PyQt6 / PySide6 (>= 6.5.0)**
  - Thiết kế chuẩn Desktop Native, hỗ trợ kéo thả file, đa tiến trình qua `QThread` đảm bảo giao diện không bao giờ bị treo đơ trong lúc chấm bài số lượng lớn.
- **Xử lý dữ liệu nạp & kết xuất**:
  - Module chuẩn **`csv`**: Đọc file đầu vào `students.csv` (2 cột: `MSSV`, `File`) và xuất file kết quả `results.csv` (7 cột).
- **Bộ máy thực thi & Sandbox bảo mật**:
  - **`subprocess`**: Khởi chạy tiến trình con cô lập để gọi trình biên dịch `gcc` (C), `javac/java` (Java), và `python` (Python).
  - **`psutil` (>= 5.9.0)**: Giám sát tài nguyên RAM (bắt lỗi `MLE`), CPU và kill tiến trình khi bị vòng lặp vô hạn (bắt lỗi `TLE`).
- **Động cơ so khớp kết quả 7 chế độ (Strategy Pattern)**:
  - Sử dụng các module `difflib`, `re`, `math` để triển khai 7 chiến lược so khớp đầu ra linh hoạt.
- **Đồng bộ hóa mạng (Network Sync)**:
  - Sử dụng thư viện `httpx` để đăng nhập JWT, kéo danh mục môn học từ NestJS Backend và đồng bộ kết quả đợt chấm lên máy chủ trung tâm.

---

## 3. Bảng Tổng Hợp Công Nghệ Theo Từng Phân Hệ

| Phân hệ | Công nghệ cốt lõi | Các thư viện / Công cụ chính | Vai trò trong hệ thống AITA |
| :--- | :--- | :--- | :--- |
| **Web Backend** | **NestJS (Node.js)** | `@nestjs/jwt`, `passport`, `prisma`/`typeorm`, `class-validator`, `@nestjs/swagger` | Cung cấp REST API trung tâm, xác thực JWT RBAC, Gateway quản lý Gemini Quota. |
| **Web Admin** | **Next.js (React)** | `TypeScript`, `TailwindCSS`, `Lucide-react`, `Axios` | Dashboard quản trị dành riêng cho System Admin: User, Môn học, Quota AI, Báo cáo. |
| **Desktop App** | **Python (PyQt6)** | `psutil`, `subprocess`, `csv`, `httpx`, `difflib`, `pytest` | Client chấm thi offline-first của Giảng viên: Sandbox, hàm `main()`, 7 chế độ so khớp. |
| **CSDL Trung tâm**| **PostgreSQL / SQLite**| Prisma Client / TypeORM Migrations | Lưu trữ tập trung tài khoản, danh mục môn học, hạn ngạch AI và phiên chấm đồng bộ. |
| **CSDL Cục bộ** | **SQLite3** | Native SQLite Driver | Lưu tạm danh sách bài nộp, bộ testcase và kết quả chấm ngay trên máy tính giảng viên. |
| **AI Cloud Hub** | **Google Gemini** | `@google/genai` (trên NestJS Backend) | Gemini 1.5 Flash: Tự động sinh testcase biên, AI Code Review On-Demand, kiểm tra đạo văn. |

---

## 4. Cơ Sở Dữ Liệu Trung Tâm Quản Lý Bởi NestJS Server

1. **`User`**: Tài khoản người dùng (`id`, `username`, `password_hash`, `full_name`, `email`, `role`, `is_active`, `created_at`).
2. **`Course`**: Danh mục môn học (`id`, `code`, `name`, `language`) - PRF (C), PRO (Java/Python), DSA (Java/Python), PHP (Python).
3. **`GradingSession`**: Phiên chấm điểm do Desktop App đồng bộ lên (`id`, `course_id`, `instructor_id`, `graded_at`, `total_submissions`, `avg_score`).
4. **`SubmissionResult`**: Kết quả chi tiết từng bài nộp (`id`, `session_id`, `mssv`, `score`, `verdict`, `passed_tests`, `runtime_ms`, `teacher_feedback`).
5. **`AiQuotaLog`**: Nhật ký sử dụng AI (`id`, `instructor_id`, `model`, `prompt_tokens`, `completion_tokens`, `cost_estimate`, `created_at`).

---

## 5. Trí Tuệ Nhân Tạo: Google Gemini 1.5 Flash API Gateway

- **Cơ chế điều phối qua NestJS Backend**:
  - NestJS Server đóng vai trò Gateway quản lý hạn ngạch (Quota Guard), lưu trữ API Key bí mật trên biến môi trường `.env`, không để lộ khóa API ra Desktop App.
- **Chiến lược tối ưu hóa lượt gọi AI (Smart Resource Strategy)**:
  - *Sinh Testcase*: Gọi 1 lần duy nhất cho mỗi đề bài để sinh cả bộ 5-10 testcase `(Input, Output)` cho cả lớp.
  - *Phân tích lỗi (Code Review)*: Chế độ **On-Demand** (chỉ gọi khi giảng viên chủ động bấm nút phân tích cho bài nộp bị `WA`, bỏ qua `CE`).
  - *Chống gian lận (Plagiarism)*: Áp dụng **mô hình lọc 2 vòng**: Vòng 1 lọc bằng thuật toán băm cây cú pháp AST cục bộ trên máy tính giảng viên (0 token); Vòng 2 chỉ gửi các cặp có độ tương đồng bất thường (> 80%) cho Gemini AI phân tích đối chứng.ản lý hạn ngạch (Quota Gatekeeper), lưu trữ API Key bí mật trên server, và cấp quota gọi AI cho các giảng viên theo tài khoản.
- **Chiến lược tối ưu hóa lượt gọi AI (Smart Resource Strategy)**:
  - *Sinh Testcase*: Gọi 1 lần duy nhất cho mỗi đề bài để sinh cả bộ 5-10 testcase `(Input, Output)`.
  - *Phân tích lỗi (Code Review)*: Chế độ **On-Demand** (chỉ gọi khi giảng viên chủ động bấm nút phân tích cho 1 bài nộp cụ thể, không gọi tự động hàng loạt khi chấm, bỏ qua lỗi biên dịch `CE`).
  - *Chống gian lận (Plagiarism)*: Áp dụng **mô hình lọc 2 vòng (Two-Stage Filtering)**: Vòng 1 lọc bằng thuật toán băm cây cú pháp AST cục bộ trên máy tính giảng viên (0 token); Vòng 2 chỉ gửi các cặp có độ tương đồng bất thường (> 80%) cho Gemini AI phân tích đối chứng.


---

## 6. Tệp Cấu Hình Phụ Thuộc Hợp Nhất (`requirements.txt`)

```text
# --- Web Server Backend & Authentication ---
fastapi>=0.110.0
uvicorn[standard]>=0.28.0
pydantic>=2.6.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.9
jinja2>=3.1.3

# --- Database & ORM ---
sqlalchemy>=2.0.28
alembic>=1.13.0

# --- Desktop Application Client ---
PySide6>=6.5.0
psutil>=5.9.5
httpx>=0.27.0

# --- Data Processing & CSV ---
pandas>=2.0.3

# --- AI Integration ---
google-generativeai>=0.4.0

# --- Testing & Quality Assurance ---
pytest>=7.4.0
pytest-asyncio>=0.23.0

# --- Packaging & Distribution ---
pyinstaller>=6.0.0
```


