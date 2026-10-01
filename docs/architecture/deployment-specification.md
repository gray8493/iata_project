# Đặc Tả Kiến Trúc Triển Khai Hệ Điều Hành & Máy Chủ (System Deployment Specification)

## Dự án: AITA - Automated Grading & Assessment Tool for Instructors
### Môn học: SWD392 (AI-Assisted System Design) – Đánh giá Giai đoạn 2 (Evaluation 2)

---

## 1. Tổng Quan Kiến Trúc Triển Khai (Deployment Architecture Overview)

Hệ sinh thái phần mềm **AITA** được thiết kế theo mô hình **Kiến trúc Lai (Hybrid Architecture)** kết hợp giữa **Ứng dụng Desktop chạy độc lập trên máy trạm ngoại tuyến (Offline-First Native Client)** và **Hệ thống Quản lý tập trung trên nền tảng Đám mây (Cloud Central Server & AI Gateway Hub)**.

Mô hình này mang lại 3 ưu thế vượt trội:
1. **Tốc độ chấm bài tối đa**: Toàn bộ quá trình biên dịch mã nguồn C, Java, Python và so khớp testcase diễn ra trực tiếp trên phần cứng máy tính của Giảng viên mà không chịu độ trễ mạng (Network Latency) hay nguy cơ nghẽn hàng đợi (Queue Bottleneck).
2. **Khả năng hoạt động ngoại tuyến (Offline-First)**: Giảng viên vẫn có thể chấm bài thi bình thường trong phòng thi bị ngắt kết nối Internet; kết quả chấm được lưu đệm an toàn vào SQLite và xuất thẳng ra file `results.csv`.
3. **Quản trị bảo mật & kiểm soát chi phí AI**: Quản trị viên quản lý danh mục môn học, phân quyền tài khoản Giảng viên và kiểm soát hạn ngạch token Google Gemini AI tập trung tại máy chủ, ngăn chặn tuyệt đối lộ API Key ra phía người dùng cuối.

Sơ đồ PlantUML tương ứng: [deployment_diagram.puml](file:///d:/Source/AITA/docs/diagrams/puml/deployment_diagram.puml).

---

## 2. Đặc Tả Các Node Hệ Thống & Hệ Điều Hành (System Nodes & OS Specifications)

Toàn bộ hệ thống AITA được phân bổ trên **5 Node kiến trúc** chính:

```text
+-------------------------------------------------------------+
|   Node 1: Instructor Workstation (Windows 10/11 64-bit)     |
|   - Artifact: AITA.exe (PyQt6 Client)                       |
|   - 3 Design Patterns: Factory Method, Adapter, Strategy    |
|   - Toolchain: MinGW GCC, OpenJDK, Python & psutil Sandbox  |
+-------------------------------------------------------------+
                              │
                              │ HTTPS / TLS 1.3 (Port 443)
                              ▼
+-------------------------------------------------------------+       +------------------------------------+
|   Node 3: Central Application Server (Ubuntu Linux 22.04)   |       | Node 2: Administrator Terminal     |
|   - Nginx Reverse Proxy (TLS 1.3 Termination, Port 443)    | ◄──── | (Chrome/Edge/Firefox on any OS)    |
|   - Docker Container: central-backend (NestJS API & Guard) |       | - Next.js Web Admin Dashboard      |
|   - Docker Container: Redis 7.x (Rate Limit & Token Cache)  |       +------------------------------------+
+-------------------------------------------------------------+
         │                                            │
         │ PostgreSQL Protocol (Port 5432)            │ HTTPS / TLS 1.3 (Port 443)
         ▼                                            ▼
+------------------------------------+       +------------------------------------+
| Node 4: Database Server Host       |       | Node 5: Google Cloud Platform      |
| (Ubuntu Linux 22.04 LTS)           |       | (Managed AI Infrastructure)        |
| - PostgreSQL 16 RDBMS              |       | - Google Gemini 1.5 Flash API      |
| - aita_central_db & Backup Volume  |       | - generativelanguage.googleapis.com|
+------------------------------------+       +------------------------------------+
```

---

### 2.1. Node 1: Máy Trạm Giảng Viên (Instructor Workstation)

- **Vai trò**: Chạy ứng dụng Desktop phục vụ nhập danh sách bài thi, nạp testcase, thực thi sandbox chấm bài tự động và đồng bộ điểm số.
- **Hệ điều hành yêu cầu**: **Microsoft Windows 10 / 11 64-bit (x86-64)**.
- **Cấu hình phần cứng (Hardware Specifications)**:
  - *Vi xử lý (CPU)*: Tối thiểu 4 Cores, khuyến nghị 8 Cores (Intel Core i5 Gen 10+ hoặc AMD Ryzen 5 trở lên) để chạy mượt mà 4-8 tiến trình biên dịch song song.
  - *Bộ nhớ trong (RAM)*: Tối thiểu 8 GB DDR4, khuyến nghị 16 GB (đảm bảo đủ dung lượng cấp phát đồng thời cho JVM Java và Python Runtime).
  - *Ổ đĩa lưu trữ (Disk Storage)*: Tối thiểu 20 GB dung lượng trống chuẩn SSD NVMe để đọc/ghi hàng trăm bài nộp sinh viên tốc độ cao.
- **Môi trường thực thi & Công cụ biên dịch tại chỗ (Local Execution Environment)**:
  - **Môi trường ảo AITA**: File thực thi `AITA.exe` tích hợp sẵn Python 3.11 Runtime, PyQt6/PySide6 Native Engine.
  - **Trình biên dịch C**: MinGW-w64 GCC 13+ (đường dẫn `bin/gcc.exe`).
  - **Trình biên dịch & Máy ảo Java**: OpenJDK 17 hoặc 21 (đường dẫn `bin/javac.exe`, `bin/java.exe`).
  - **Trình thông dịch Python**: Python 3.10+ Standard Runtime (`python.exe`).
  - **Công cụ bảo vệ HĐH (Sandbox Guard)**: Thư viện `psutil` tích hợp sẵn trong client để giám sát mức chiếm dụng RAM, CPU và tự động cưỡng chế diệt các tiến trình lặp vô hạn.
- **Lưu trữ cục bộ**: 
  - Cơ sở dữ liệu SQLite 3 (`local_cache.db`): Lưu tạm cấu hình bài thi và kết quả chấm offline.
  - Tập tin CSV: `students.csv` (đầu vào: 2 cột `MSSV`, `File`) và `results.csv` (đầu ra: 7 cột hoàn chỉnh).

---

### 2.2. Node 2: Máy Trạm Quản Trị Viên (Administrator Terminal)

- **Vai trò**: Cung cấp giao diện Web Admin để Quản trị viên (Admin) cấu hình hệ thống, quản lý tài khoản giảng viên, theo dõi hạn ngạch Gemini AI và kiểm toán hệ thống.
- **Hệ điều hành**: Độc lập nền tảng (Hỗ trợ tốt trên Windows, macOS, Linux).
- **Phần mềm yêu cầu**: Trình duyệt Web chuẩn HTML5 hiện đại (Google Chrome ≥ 115, Microsoft Edge ≥ 115, Mozilla Firefox ≥ 118, Safari ≥ 16).
- **Giao diện Web Frontend**: Ứng dụng Single Page Application (SPA) xây dựng trên nền tảng Next.js 14+ / React với thiết kế Modern Dashboard, tải trực tiếp qua giao thức HTTPS.

---

### 2.3. Node 3: Máy Chủ Ứng Dụng Trung Tâm (Central Application Server Host)

- **Vai trò**: Đóng vai trò "Bộ não trung tâm" cung cấp API phân quyền RBAC, lưu trữ lịch sử chấm, kiểm soát hạn ngạch và làm Gateway bảo mật trung gian khi gọi Google Gemini AI.
- **Hệ điều hành**: **Ubuntu Linux 22.04 LTS (Jammy Jellyfish) 64-bit Server Edition**.
- **Cấu hình phần cứng (Hardware Specifications)**:
  - *Vi xử lý (vCPU)*: 4 vCPU (2.5 GHz+).
  - *Bộ nhớ trong (RAM)*: 8 GB (có thể mở rộng lên 16 GB khi số lượng giảng viên đồng bộ tăng cao).
  - *Ổ đĩa lưu trữ (Disk)*: 80 GB SSD (Enterprise Grade).
- **Môi trường ảo hóa & Đóng gói (Containerization)**:
  - **Docker Engine (>= 24.0)** & **Docker Compose (>= 2.20)**: Cô lập hoàn toàn các thành phần backend thành các micro-services / containers riêng biệt.
  - **Nginx Reverse Proxy Container**: Lắng nghe cổng 80 (chuyển hướng HTTP sang HTTPS) và cổng 443 (chứng chỉ bảo mật SSL/TLS 1.3 Let's Encrypt), chịu trách nhiệm cân bằng tải và giới hạn tần suất request (Rate Limiting).
  - **Backend Service Container (`central-backend`)**: Xây dựng trên NestJS 10 (Node.js 20 LTS runtime) hoặc FastAPI (Python 3.11 ASGI), tích hợp Passport-JWT, RBAC Guards, Swagger OpenAPI (`/docs`).
  - **In-Memory Cache Container (`Redis 7.x`)**: Quản lý danh sách đen Token thu hồi (JWT Blacklist) và bộ đếm hạn ngạch Token AI theo thời gian thực (Token Bucket / Sliding Window Rate Limiter).

---

### 2.4. Node 4: Máy Chủ Cơ Sở Dữ Liệu Trung Tâm (Database Server Node)

- **Vai trò**: Lưu trữ dữ liệu có cấu trúc, quan hệ người dùng, môn học, phiên chấm, bảng điểm và nhật ký kiểm toán hệ thống.
- **Hệ điều hành**: **Ubuntu Linux 22.04 LTS** (triển khai trên VM chuyên dụng hoặc dịch vụ Managed Cloud Database: AWS RDS / GCP Cloud SQL).
- **Hệ quản trị CSDL**: **PostgreSQL 16 Enterprise RDBMS**.
- **Cấu hình lưu trữ**: 100 GB NVMe SSD High-IOPS có cấu hình RAID 10 để bảo vệ toàn vẹn dữ liệu học thuật.
- **Tính năng bảo đảm**:
  - Giao tiếp mã hóa SSL/TLS khi nhận kết nối từ Application Server.
  - Cơ chế Connection Pooling tối ưu hóa tài nguyên kết nối qua Prisma / PgBouncer.
  - Cơ chế sao lưu tự động (Automated Backup): Tự động snapshot mỗi ngày một lần và lưu trữ bản ghi giao dịch Write-Ahead Logging (WAL) để phục hồi thảm họa (Disaster Recovery).

---

### 2.5. Node 5: Dịch Vụ Trí Tuệ Nhân Tạo Đám Mây (Google Cloud Platform AI Service)

- **Vai trò**: Cung cấp mô hình ngôn ngữ lớn (LLM) hỗ trợ tự động sinh testcase biên, phân tích lỗi code và đối chứng gian lận học thuật.
- **Nền tảng**: Google Cloud Platform (PaaS) – Google AI Studio / Vertex AI Foundation Models.
- **Endpoint**: `https://generativelanguage.googleapis.com` (Giao tiếp qua REST API & gRPC).
- **Mô hình triển khai**: **`gemini-1.5-flash`** (độ trễ phản hồi < 1 giây, context window lớn 1 triệu tokens, hạn ngạch rộng và chi phí tối ưu nhất cho đồ án giáo dục).

---

## 3. Danh Mục Artifacts & Môi Trường Triển Khai (Deployed Artifacts Matrix)

| Artifact Name | Định dạng đóng gói | Nơi triển khai (Deployed Node) | Công nghệ nền tảng | Mục đích sử dụng |
| :--- | :--- | :--- | :--- | :--- |
| **`AITA.exe`** | Standalone Executable | Node 1 (Instructor PC) | PyInstaller, Python 3.11, PyQt6 | Ứng dụng Desktop bản địa dành cho Giảng viên |
| **`local_cache.db`** | SQLite 3 File | Node 1 (Instructor PC) | SQLite Embedded Engine | Lưu tạm testcases, cache phiên chấm offline |
| **`Web Admin UI`** | SPA Static Bundle | Node 2 (Admin Browser) | Next.js 14, React, TailwindCSS | Giao diện điều hành hệ thống của Admin |
| **`central-backend`** | Docker Image | Node 3 (Application Server) | NestJS 10, Node.js 20, TypeScript | REST API Gateway, Auth RBAC, AI Quota Guard |
| **`nginx.conf`** | Config Artifact | Node 3 (Application Server) | Nginx 1.25 Alpine | Reverse Proxy, SSL/TLS Termination |
| **`redis.conf`** | In-Memory Store | Node 3 (Application Server) | Redis 7.2 Alpine | Bộ nhớ đệm Token Blacklist & AI Rate Limiter |
| **`aita_central_db`**| Relational Schema | Node 4 (Database Server) | PostgreSQL 16 RDBMS | Cơ sở dữ liệu tập trung lưu Users, Grades, Logs |

---

## 4. Ma Trận Giao Thức Mạng, Cổng Truyền Thông & Bảo Mật (Network Protocols & Ports)

| Nguồn kết nối (Source) | Đích kết nối (Destination) | Giao thức (Protocol) | Cổng mạng (Port) | Cơ chế bảo mật & Xác thực |
| :--- | :--- | :--- | :---: | :--- |
| Admin Web Browser | Central Server (Nginx) | **HTTPS (HTTP/2)** | `443` | Mã hóa TLS 1.3, Chứng chỉ SSL Let's Encrypt |
| Desktop Client (`AITA.exe`) | Central Server (Nginx) | **HTTPS REST** | `443` | JSON Web Token (JWT Bearer Authorization) |
| Nginx Reverse Proxy | Backend Container | **HTTP / Internal** | `3000` | Mạng cô lập Docker Bridge Network |
| Backend Container | Redis Cache | **RESP Protocol** | `6379` | Docker Network nội bộ, xác thực mật khẩu Redis |
| Backend Container | PostgreSQL Server | **TCP / libpq** | `5432` | SSL Encrypted, User/Password, Connection Pool |
| Backend Container | Google Gemini API | **HTTPS / REST** | `443` | TLS 1.3, Secure API Key trong Header máy chủ |
| Desktop Client (`AITA.exe`) | Local Compiler Toolchain | **OS Standard Streams** | `IPC` | Đường ống Stdin, Stdout, Stderr qua `subprocess` |

---

## 5. Cơ Chế Cô Lập & An Toàn Trên Hệ Điều Hành (OS Sandboxing & Security Protection)

Do hệ thống phải thực thi trực tiếp các file mã nguồn do sinh viên nộp (vốn tiềm ẩn nguy cơ chứa mã độc, vòng lặp vô hạn hoặc cố ý chiếm dụng bộ nhớ), tầng Desktop Client triển khai **Cơ chế Sandbox 4 lớp**:

1. **Khởi chạy tiến trình con cô lập (Subprocess Isolation)**:
   - Toàn bộ lệnh biên dịch (`gcc`, `javac`) và thực thi bài làm (`.exe`, `java`, `python`) đều được khởi tạo qua module `subprocess.Popen` với cờ `CREATE_NO_WINDOW`, tách biệt hoàn toàn với luồng giao diện chính của ứng dụng (`QThread`).
2. **Kiểm soát thời gian chạy & Diệt vòng lặp vô hạn (Anti-Freeze & Time Limit Exceeded - TLE)**:
   - Mỗi câu hỏi được áp đặt thời gian giới hạn nghiêm ngặt (mặc định 1.000 ms - 2.000 ms).
   - Tiến trình giám sát sử dụng cơ chế `process.wait(timeout=limit_seconds)`. Nếu quá giờ quy định, hệ thống phát tín hiệu `SIGKILL` (`process.kill()`) lập tức để thu hồi tài nguyên, ghi nhận kết quả `TLE`.
3. **Giám sát bộ nhớ RAM & Bắt lỗi tràn bộ nhớ (Memory Limit Exceeded - MLE)**:
   - Sử dụng thư viện `psutil` để liên tục lấy mẫu dung lượng RAM (`rss` - Resident Set Size) của tiến trình con với tần suất 50ms/lần.
   - Nếu bộ nhớ tiến trình vượt ngưỡng quy định (ví dụ 128 MB hoặc 256 MB), hệ thống lập tức cưỡng chế chấm dứt tiến trình và gắn nhãn `MLE`.
4. **Vùng làm việc tạm thời an toàn (Isolated Temp Directory)**:
   - Mỗi bài nộp của sinh viên được sao chép và biên dịch trong một thư mục tạm thời độc lập (UUID Temp Folder trong `AppData/Local/Temp/AITA_Sandbox/`).
   - Sau khi kết thúc phiên chấm câu hỏi, toàn bộ file nhị phân trung gian (`.exe`, `.class`, `.o`) sẽ bị xóa sạch, ngăn ngừa xung đột và không làm rác ổ cứng giảng viên.

---

## 6. Chiến Lược Đóng Gói & Phân Phối (Packaging & Distribution Strategy)

### 6.1. Đóng gói Desktop Client cho Giảng viên
- **Công cụ**: `PyInstaller 6.x`.
- **Cấu hình đóng gói**:
  - Tùy chọn `--onefile` hoặc `--onedir` kết hợp nén tài nguyên giao diện PyQt6, icon, và file cấu hình mẫu.
  - Bổ sung file `.spec` tối ưu hóa, loại bỏ các package thừa của Python để file chạy nhẹ nhất có thể (~40-60 MB).
  - Tích hợp bộ MinGW portable và OpenJDK rút gọn nếu giảng viên chưa cài đặt toolchain trên máy tính.

### 6.2. Triển khai Máy chủ Trung tâm bằng Docker Compose
- Hệ thống backend được khởi chạy dễ dàng chỉ với một câu lệnh:
  ```bash
  docker compose -f docker-compose.prod.yml up -d
  ```
- File cấu hình Docker quản lý tự động: Nginx Ingress, NestJS API Server, Redis Cache và PostgreSQL, đi kèm chính sách tự khởi động lại (`restart: unless-stopped`) và kiểm tra sức khỏe dịch vụ (`healthcheck`).

---

## 7. Mối Liên Kết Triển Khai Của 3 Mẫu Thiết Kế (Design Patterns Deployment Context)

Cả **3 Mẫu thiết kế cốt lõi** bắt buộc của đồ án AITA đều được đóng gói trực tiếp bên trong artifact **`AITA.exe`** trên máy trạm của Giảng viên (Node 1):

1. **`RunnerFactory` (Creational Pattern)**: 
   - Nằm tại module `src/core/factories/`.
   - Vận hành tại thời điểm người dùng bắt đầu phiên chấm: Đọc phần mở rộng của file bài nộp sinh viên (`.c`, `.java`, `.py`) từ danh sách nạp để khởi tạo đối tượng `BaseRunner` phù hợp với tài nguyên của máy trạm.
2. **`CompilerAdapter` (Structural Pattern)**:
   - Nằm tại module `src/core/adapters/`.
   - Đóng vai trò cầu nối tương tác trực tiếp với các trình biên dịch cục bộ cài trên HĐH Windows (`MinGW GCC`, `Javac`, `Python Runtime`), chuẩn hóa lệnh gọi OS và ánh xạ các thông báo lỗi `stderr` thành các mã kết quả chuẩn (`CE`, `RE`).
3. **`MatchingStrategy` (Behavioral Pattern)**:
   - Nằm tại module `src/core/strategies/`.
   - Nằm ở tầng xử lý logic cốt lõi: Nhận kết quả `stdout` từ tiến trình con do Runner trả về và so khớp với `expected_output` của giảng viên theo 1 trong 7 thuật toán đã chọn trên giao diện trước khi xuất ra bảng điểm `results.csv`.

Chi tiết kiến trúc và phân tích nguyên lý của 3 mẫu này được đặc tả tại: [docs/architecture/design-patterns.md](file:///d:/Source/AITA/docs/architecture/design-patterns.md).
