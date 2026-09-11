# Đặc Tả Công Nghệ Sử Dụng (Technology Stack)

## Dự án: AITA - Automated Grading & Assessment Tool for Instructors

Tài liệu này quy định toàn bộ ngăn xếp công nghệ (Tech Stack), các thư viện bên thứ ba và công cụ nền tảng được sử dụng để xây dựng hệ sinh thái tích hợp **AITA** gồm: **Web Server Backend (Phân quyền & Dữ liệu trung tâm)**, **Trang Web Admin Quản Lý (Web Admin Dashboard)** và **Desktop App Client (PyQt6/PySide6 dành cho Giảng viên)**.

---

## 1. Tổng Quan Ngăn Xếp Công Nghệ Hệ Sinh Thái (Ecosystem Tech Stack Overview)

```text
+------------------------------------+       +------------------------------------+
|   WEB ADMIN DASHBOARD (Web UI)     |       | DESKTOP APP CLIENT (PyQt6/PySide6) |
|  - Dành cho Quản trị viên (Admin)  |       |  - Dành cho Giảng viên (Instructor)|
|  - HTML5, CSS3, Modern UI/Bootstrap|       |  - QThread xử lý đa luồng          |
|  - Quản trị User, Môn, Quota AI    |       |  - Chấm bài CSV hàng loạt 7 chế độ |
+------------------------------------+       +------------------------------------+
                  │                                             │
                  │ (HTTPS / JSON RESTful API)                  │ (REST API & Auth Sync)
                  ▼                                             ▼
+---------------------------------------------------------------------------------+
|                   WEB SERVER BACKEND (Python FastAPI Service)                   |
|  - Framework: FastAPI (Tốc độ cao, chuẩn OpenAPI/Swagger tự động)               |
|  - ASGI Server: Uvicorn (Xử lý hàng nghìn request bất đồng bộ async/await)     |
|  - Phân quyền & Bảo mật (Auth & RBAC): JWT Bearer Token, OAuth2, Bcrypt Hashing |
|  - Xác thực dữ liệu: Pydantic v2                                                |
|  - Tầng dữ liệu & ORM: SQLAlchemy v2 + Alembic (Migration)                      |
|  - Điều phối AI: Gemini AI Hub (Quản lý hạn ngạch, API Keys tập trung)          |
+---------------------------------------------------------------------------------+
                                         │
                                         ▼
+---------------------------------------------------------------------------------+
|                 CƠ SỞ DỮ LIỆU TRUNG TÂM (Centralized Database)                  |
|  - Môi trường Dev/Demo: SQLite (sqlite3 file tập trung)                         |
|  - Môi trường Production: PostgreSQL (Hỗ trợ mở rộng & bảo mật cao)            |
+---------------------------------------------------------------------------------+
```

---

## 2. Ngăn Xếp Công Nghệ Chi Tiết Từng Thành Phần

### 2.1. Web Server Backend (Hệ Thống Phân Quyền & Quản Lý Trung Tâm)

- **Framework cốt lõi**: **Python FastAPI (>= 0.110.0)**
  - *Lý do*: Tốc độ thực thi cực nhanh (tiệm cận Go/NodeJS nhờ kiến trúc Asynchronous ASGI), hỗ trợ sẵn tài liệu API trực quan Swagger UI (`/docs`) và ReDoc (`/redoc`) phục vụ chấm điểm đồ án SWD392.
- **Máy chủ Web ASGI**: **Uvicorn (>= 0.28.0)**
  - Hỗ trợ kiến trúc Non-blocking I/O, phục vụ song song nhiều kết nối đồng thời từ Web Admin và Desktop App.
- **Xác thực & Phân quyền (Authentication & RBAC)**:
  - **JSON Web Token (JWT)**: Sử dụng thư viện `python-jose` với thuật toán mã hóa `HS256`. Token chứa payload định danh và Role (`admin`, `instructor`).
  - **Mã hóa mật khẩu**: Sử dụng `passlib[bcrypt]` để băm (hash) mật khẩu an toàn chuẩn công nghiệp.
  - **Cơ chế phân quyền**: Dependency Injection của FastAPI (`Depends()`) để chặn truy cập trái phép theo từng endpoint (Role-Based Access Control).
- **Mô hình hóa dữ liệu & ORM**:
  - **SQLAlchemy (>= 2.0.0)**: Ánh xạ quan hệ đối tượng ORM linh hoạt, cho phép chuyển đổi dễ dàng giữa SQLite và PostgreSQL.
  - **Pydantic (>= 2.0.0)**: Kiểm tra kiểu dữ liệu đầu vào/ra (Data Validation & Serialization) chuẩn xác.

### 2.2. Trang Web Admin Quản Lý (Web Admin Management Dashboard)

- **Mục đích**: **Dành riêng cho Quản trị viên (Admin)** quản lý toàn bộ hệ thống (không phải web portal dành cho học sinh).
- **Công nghệ Frontend**: **HTML5, Modern CSS, JavaScript ES6+ kết hợp Jinja2 Templates** (hoặc phục vụ giao diện Single Page qua FastAPI static files).
- **Giao diện & Trải nghiệm (UI/UX)**:
  - Sử dụng giao diện Dark/Light hiện đại, responsive, trực quan hóa số liệu qua các thẻ thống kê (Metric Cards) và bảng dữ liệu (DataTables).
- **Chức năng trọng tâm của Web Admin**:
  1. **Quản lý tài khoản Giảng viên & Phân quyền**: Tạo mới, chỉnh sửa thông tin, khóa tài khoản và gán Role (`admin`, `instructor`).
  2. **Quản lý danh mục học thuật**: Quản lý danh mục 4 môn học lập trình cốt lõi (PRF, PRO, DSA, PHP).
  3. **Giám sát hạn ngạch AI (Gemini Quota Management)**: Cấu hình API Key tập trung, thiết lập giới hạn số lượt gọi AI cho từng giảng viên, theo dõi số token tiêu thụ theo thời gian thực.
  4. **Báo cáo & Thống kê toàn trường**: Xem tổng hợp số phiên chấm và nhật ký sử dụng hệ thống.

### 2.3. Desktop App Client (Ứng Dụng Chấm Bài Dành Cho Giảng Viên)

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
  - Sử dụng thư viện `httpx` hoặc `requests` để đăng nhập JWT, kéo danh sách lớp từ Web Backend và đồng bộ kết quả chấm lên máy chủ trung tâm.

---

## 3. Danh Mục Thư Viện Python Chuyên Dụng (Python Dependencies)

| Nhóm chức năng | Tên thư viện | Phiên bản | Mục đích sử dụng trong hệ thống AITA |
| :--- | :--- | :---: | :--- |
| **Backend API** | `fastapi` | `>= 0.110.0` | Khung xây dựng RESTful API Backend hiệu năng cao, tự sinh Swagger docs. |
| **Backend Server** | `uvicorn[standard]` | `>= 0.28.0` | Máy chủ web chuẩn ASGI phục vụ FastAPI service. |
| **Bảo mật & Auth** | `python-jose[cryptography]` | `>= 3.3.0` | Tạo, mã hóa và giải mã JSON Web Token (JWT) để phân quyền RBAC. |
| **Bảo mật & Auth** | `passlib[bcrypt]` | `>= 1.7.4` | Băm mật khẩu (Password Hashing) an toàn trước khi lưu vào CSDL. |
| **Backend Forms** | `python-multipart` | `>= 0.0.9` | Xử lý dữ liệu form đăng nhập chuẩn OAuth2 Password Request. |
| **ORM & Database** | `sqlalchemy` | `>= 2.0.28` | Thư viện ORM tương tác với CSDL trung tâm (SQLite/PostgreSQL). |
| **ORM Migration** | `alembic` | `>= 1.13.0` | Quản lý lịch sử thay đổi cấu trúc bảng cơ sở dữ liệu. |
| **Web Admin UI** | `jinja2` | `>= 3.1.3` | Động cơ Template render giao diện Web Admin Dashboard. |
| **Desktop GUI** | `PySide6` | `>= 6.5.0` | Bộ công cụ xây dựng giao diện ứng dụng Desktop chuyên nghiệp cho Giảng viên. |
| **Giám sát HĐH** | `psutil` | `>= 5.9.5` | Giám sát RAM (phát hiện `MLE`), CPU và diệt tiến trình lặp vô hạn (`TLE`). |
| **Thực thi code** | `subprocess` | Built-in | Biên dịch và thực thi mã nguồn sinh viên C/Java/Python trong tiến trình cô lập. |
| **Xử lý CSV** | `csv` | Built-in | Đọc danh sách `students.csv` và xuất bảng điểm `results.csv` tốc độ cao. |
| **Xử lý Bảng biểu**| `pandas` | `>= 2.0.3` | Lọc, tổng hợp dữ liệu thống kê điểm số và phân tích kết quả bài nộp. |
| **Đồng bộ API** | `httpx` | `>= 0.27.0` | Client HTTP bất đồng bộ để Desktop App gọi API lên Web Server Backend. |
| **Trí tuệ nhân tạo**| `google-generativeai` | `>= 0.4.0` | Tích hợp Google Gemini 1.5 Flash sinh testcase biên và viết nhận xét code. |
| **Kiểm thử tự động**| `pytest` | `>= 7.4.0` | Viết và chạy bộ kiểm thử Unit Test & Integration Test đáp ứng chuẩn đồ án. |
| **Đóng gói Desktop**| `pyinstaller` | `>= 6.0.0` | Đóng gói Desktop Client thành file `.exe` duy nhất cho Windows. |

---

## 4. Cơ Sở Dữ Liệu: SQLite (Local/Dev) & PostgreSQL (Production)

### 4.1. Kiến trúc lưu trữ linh hoạt
- **Môi trường cục bộ / Đồ án demo**: Sử dụng SQLite file tập trung (`server_database.db`) và SQLite cục bộ tại Desktop (`local_cache.db`), không đòi hỏi cài đặt phức tạp, chạy ngay lập tức.
- **Môi trường mở rộng (Production)**: Kết nối CSDL quan hệ PostgreSQL qua chuỗi kết nối của SQLAlchemy ORM mà không cần sửa đổi mã nguồn xử lý.

### 4.2. Các bảng dữ liệu trung tâm quản lý bởi Web Server:
1. **`users`**: Tài khoản người dùng (`id`, `username`, `hashed_password`, `full_name`, `email`, `role`, `is_active`, `created_at`).
2. **`roles`**: Định nghĩa vai trò hệ thống (`ADMIN`, `INSTRUCTOR`) và danh sách quyền hạn.
3. **`courses`**: Danh mục môn học (`id`, `code`, `name`, `language`) - PRF (C), PRO (Java/Python), DSA (Java/Python), PHP (Python).
4. **`grading_sessions`**: Phiên chấm điểm do Desktop App đồng bộ lên (`id`, `course_id`, `graded_by`, `graded_at`, `total_submissions`, `avg_score`).
5. **`submission_results`**: Kết quả chi tiết từng bài nộp (`id`, `session_id`, `mssv`, `score`, `verdict`, `passed_tests`, `runtime_ms`, `ai_feedback`).
6. **`ai_usage_logs`**: Nhật ký sử dụng AI (`id`, `user_id`, `model`, `prompt_tokens`, `completion_tokens`, `cost_estimate`, `created_at`).

---

## 5. Trí Tuệ Nhân Tạo: Google Gemini API & Chiến Lược Tối Ưu Quota

- **Mô hình chuẩn**: `gemini-1.5-flash` (Tốc độ phản hồi cực nhanh < 1s, hạn ngạch rộng, chi phí tối ưu).
- **Cơ chế điều phối qua Web Backend**:
  - Web Server Backend đóng vai trò Gateway quản lý hạn ngạch (Quota Gatekeeper), lưu trữ API Key bí mật trên server, và cấp quota gọi AI cho các giảng viên theo tài khoản.
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


