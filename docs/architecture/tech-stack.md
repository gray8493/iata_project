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
|  - Tầng dữ liệu & ORM: Prisma ORM                                               |
|  - Điều phối AI: AI Hub (Quản lý hạn ngạch Token Quota & API Key bí mật)        |
|  - Tài liệu API: Swagger OpenAPI (@nestjs/swagger)                              |
+---------------------------------------------------------------------------------+
                                         │
                                         ▼
+---------------------------------------------------------------------------------+
|                 CƠ SỞ DỮ LIỆU TRUNG TÂM (Centralized Database)                  |
|  - Môi trường Dev/Demo: PostgreSQL cục bộ                                       |
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
  - **Prisma ORM**: Quản lý schema dữ liệu, quan hệ bảng và migration có kiểu dữ liệu an toàn.
  - **`class-validator` & `class-transformer`**: Thẩm định chặt chẽ Payload đầu vào trước khi vào tầng xử lý logic.

### 2.2. Trang Web Admin Quản Lý (Next.js / TypeScript Frontend)

- **Mục đích**: **Dành riêng cho Quản trị viên (Admin)** quản lý toàn bộ hệ thống (không phải web portal dành cho học sinh).
- **Công nghệ Frontend**: **Next.js 14+ (App Router), React 18+, TypeScript**
  - **Giao diện & UI**: **TailwindCSS** kết hợp bộ icon **Lucide-react** (không dùng thư viện component ngoài).
  - **Giao tiếp API**: Sử dụng **Fetch API** bọc trong module `src/lib/api.ts` (tự động gán Bearer Token, tự logout khi nhận `401`) kết hợp **SWR** để lấy/cập nhật dữ liệu caching phía client.
- **Chức năng trọng tâm của Web Admin Dashboard**:
  1. **Quản lý tài khoản Giảng viên & Phân quyền**: Tạo mới, chỉnh sửa thông tin, khóa tài khoản và gán Role (`admin`, `instructor`).
  2. **Giám sát hạn ngạch AI (AI Quota Management)**: Thiết lập trần Token Quota hàng ngày cho từng giảng viên và theo dõi số token tiêu thụ. AI API key do vận hành cấu hình qua biến môi trường máy chủ, không nhập trong Web Admin.
  3. **Báo cáo & Thống kê toàn trường**: Xem tổng hợp số lượng giảng viên, mức độ tiêu thụ Token AI và nhật ký kiểm toán hệ thống.

### 2.3. Desktop App Client (Ứng Dụng Chấm Bài Dành Cho Giảng Viên - Python / PyQt6)

- **Giao diện Desktop (GUI Framework)**: **PyQt6 (>= 6.5.0)**
  - Thiết kế chuẩn Desktop Native, hỗ trợ kéo thả file, đa tiến trình qua `QThread` đảm bảo giao diện không bao giờ bị treo đơ trong lúc chấm bài số lượng lớn.
- **Xử lý dữ liệu nạp & kết xuất**:
  - Chế độ Console: nạp bài nộp trực tiếp từ thư mục mã nguồn bài làm (mỗi thư mục con / file là một sinh viên, tự động phân tích MSSV bằng regex làm định danh duy nhất — không lưu họ tên; không còn nạp qua file `students.csv`).
  - Chế độ Web: nạp bài nộp từ thư mục liên kết, thêm/dán thủ công nhiều link, hoặc nhập file CSV theo chế độ chấm (`MSSV` + URL Live/GitHub).
  - Module chuẩn **`csv`**: Xử lý nhập danh sách bài nộp Web và xuất file kết quả `results.csv` (7 cột).
- **Bộ máy thực thi & Sandbox bảo mật**:
  - **`subprocess`**: Khởi chạy tiến trình con cô lập để gọi trình biên dịch `gcc` (C), `javac/java` (Java), và `python` (Python).
  - **`psutil` (>= 5.9.0)**: Giám sát tài nguyên RAM (bắt lỗi `MLE`), CPU và kill tiến trình khi bị vòng lặp vô hạn (bắt lỗi `TLE`).
- **Bộ máy chấm bài Web tự động (Headless Browser & Parsers)**:
  - **`playwright` (>= 1.40.0)**: Trình duyệt không đầu Chromium giả lập tương tác người dùng (click, submit, navigation) và chụp ảnh full-page screenshot.
  - **`beautifulsoup4` (>= 4.12.0)**: Parser cấu trúc DOM, thẩm định thẻ HTML ngữ nghĩa và thuộc tính theo checklist.
  - **`tinycss2` (>= 1.2.1)**: Phân tích cú pháp CSS/HTML, kiểm tra chuẩn W3C offline.
- **Động cơ so khớp kết quả 7 chế độ (Strategy Pattern)**:
  - Sử dụng các module `difflib`, `re`, `math` để triển khai 7 chiến lược so khớp đầu ra linh hoạt.
- **Kết nối Mạng & Ủy quyền API (API Client)**:
  - Sử dụng thư viện `httpx` để đăng nhập JWT từ NestJS Backend và gửi yêu cầu tới AI Gateway (sinh testcase, review lỗi, quét đạo văn, đánh giá giao diện).

---

## 3. Bảng Tổng Hợp Công Nghệ Theo Từng Phân Hệ

| Phân hệ | Công nghệ cốt lõi | Các thư viện / Công cụ chính | Vai trò trong hệ thống AITA |
| :--- | :--- | :--- | :--- |
| **Web Backend** | **NestJS (Node.js)** | `@nestjs/jwt`, `passport`, `prisma`, `class-validator`, `@nestjs/swagger` | Cung cấp REST API trung tâm, xác thực JWT RBAC, Gateway quản lý AI Quota.     |
| **Web Admin** | **Next.js (React)** | `TypeScript`, `TailwindCSS`, `Lucide-react`, `Fetch API`, `SWR` | Dashboard quản trị dành riêng cho System Admin: User, Quota AI, Báo cáo kiểm toán. |
| **Desktop App** | **Python (PyQt6)** | `playwright`, `beautifulsoup4`, `tinycss2`, `psutil`, `subprocess`, `csv`, `httpx` | Client chấm thi offline-first của Giảng viên: Sandbox, hàm `main()`, chấm Web tự động, 7 chế độ so khớp, xuất CSV. |
| **CSDL Trung tâm**| **PostgreSQL (Neon)**| Prisma Client / Prisma Migrate | Lưu trữ danh mục môn học, tài khoản, cấu hình hạn ngạch và nhật ký AI. |
| **CSDL Cục bộ** | **SQLite3** | Native SQLite Driver | Lưu trữ 100% dữ liệu lớp học, bài nộp, testcase, kết quả chấm điểm và ảnh web trên máy tính giảng viên. |
| **AI Cloud Hub** | **OpenRouter** | REST API `https://openrouter.ai/api/v1` (gọi qua `fetch` trên NestJS Backend) | Cấu hình qua biến môi trường `OPENROUTER_API_KEYS` / `OPENROUTER_MODEL`; sinh testcase, phân tích lỗi, kiểm tra đạo văn, đánh giá giao diện & rubric chấm PE.                |

---

## 4. Cơ Sở Dữ Liệu Trung Tâm Quản Lý Bởi NestJS Server (Neon Cloud)

1. **`User`**: Tài khoản người dùng (`id`, `username`, `password_hash`, `full_name`, `email`, `role`, `is_active`, `is_deleted`, `deleted_at`, `created_at`, `updated_at`).
2. **`AiQuotaConfig`**: Cấu hình trần hạn ngạch Token Quota hàng ngày cho từng Giảng viên (`id`, `user_id`, `daily_token_limit`, `used_tokens_today`, `last_reset_date`, `is_deleted`, `deleted_at`).
3. **`AiQuotaLog`**: Nhật ký sử dụng AI (`id`, `user_id`, `feature_type`, `model_name`, `prompt_tokens`, `completion_tokens`, `total_tokens`, `is_deleted`, `deleted_at`, `created_at`).
4. **`RefreshToken`**: Luân phiên Refresh Token (`id`, `user_id`, `token_hash`, `expires_at`, `revoked_at`, `replaced_by_id`, `created_at`).

---

## 5. Trí Tuệ Nhân Tạo: AI Gateway

- **Cơ chế điều phối qua NestJS Backend**:
  - NestJS Server đóng vai trò Gateway quản lý hạn ngạch (Quota Guard), lưu trữ một **danh sách nhiều API Key bí mật** của OpenRouter trong biến `OPENROUTER_API_KEYS` (phân tách dấu phẩy, tự xoay vòng khi key bị rate-limit), không để lộ khóa API ra Desktop App. Model chính cấu hình bằng `OPENROUTER_MODEL` (ví dụ `google/gemma-4-31b-it:free`), danh sách model dự phòng qua `OPENROUTER_MODEL_FALLBACKS`, endpoint qua `OPENROUTER_BASE_URL` (mặc định `https://openrouter.ai/api/v1`).
- Rate limit: 80 request/phút/User cho API đã xác thực thông thường; 15 request/phút/User cho nhóm API tạo nội dung AI; login 10/phút/IP và refresh 30/phút/IP. Dùng In-Memory Throttler mặc định trên Render.com Web Service; hỗ trợ mở rộng kết nối Redis khi cấu hình biến môi trường `REDIS_URL`.
- **Chiến lược tối ưu hóa lượt gọi AI (Smart Resource Strategy)**:
  - *Sinh Testcase*: Gọi 1 lần duy nhất cho mỗi đề bài để sinh cả bộ 5-10 testcase `(Input, Output)` cho cả lớp.
  - *Phân tích lỗi (Code Review)*: Chế độ **On-Demand** (chỉ gọi khi giảng viên chủ động bấm nút phân tích cho bài nộp bị `WA`, bỏ qua `CE`).
  - *Chống gian lận (Plagiarism)*: Áp dụng **mô hình lọc 2 vòng**: Vòng 1 lọc cục bộ trên máy tính giảng viên; Vòng 2 chỉ gửi các cặp có độ tương đồng trên 80% cho AI Hub phân tích đối chứng.
  - API key AI Hub chỉ nằm trên backend. Mọi yêu cầu AI cần Instructor đăng nhập và được kiểm tra quota hằng ngày UTC; token sử dụng được ghi vào audit log.


---

## 6. Quản lý phụ thuộc theo ứng dụng

Backend sử dụng `apps/central-backend/package.json` và Prisma schema/migrations. Desktop Python dùng riêng `apps/desktop-client/requirements.txt`. Không gộp thư viện backend Node.js và desktop Python vào một tệp phụ thuộc.

Các thành phần backend chính:

```text
NestJS 10, TypeScript 5, Prisma 5, PostgreSQL, class-validator, Swagger
```


