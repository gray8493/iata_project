# Đặc Tả Kiến Trúc Triển Khai Hệ Điều Hành & Máy Chủ (System Deployment Specification)

## Dự án: AITA - Automated Grading & Assessment Tool for Instructors
### Môn học: SWD392 (AI-Assisted System Design) – Đánh giá Giai đoạn 2 (Evaluation 2)

---

## 1. Tổng Quan Kiến Trúc Triển Khai (Deployment Architecture Overview)

Hệ sinh thái phần mềm **AITA** được thiết kế theo mô hình **Kiến trúc Lai (Hybrid Architecture)** kết hợp giữa **Ứng dụng Desktop chạy độc lập trên máy trạm ngoại tuyến (Offline-First Native Client)** và **Hệ thống Quản lý tập trung trên nền tảng Đám mây (Cloud Central Server & AI Gateway Hub)**.

Mô hình này mang lại 3 ưu thế vượt trội:
1. **Tốc độ chấm bài tối đa**: Toàn bộ quá trình biên dịch mã nguồn C, Java, Python và so khớp testcase diễn ra trực tiếp trên phần cứng máy tính của Giảng viên mà không chịu độ trễ mạng (Network Latency) hay nguy cơ nghẽn hàng đợi (Queue Bottleneck).
2. **Khả năng hoạt động ngoại tuyến (Offline-First)**: Giảng viên vẫn có thể chấm bài thi bình thường trong phòng thi bị ngắt kết nối Internet; kết quả chấm được lưu đệm an toàn vào SQLite và xuất thẳng ra file `results.csv`.
3. **Quản trị bảo mật & kiểm soát chi phí AI**: Quản trị viên quản lý phân quyền tài khoản Giảng viên và kiểm soát hạn ngạch token AI Hub tập trung tại máy chủ, ngăn chặn tuyệt đối lộ API Key ra phía người dùng cuối.

Sơ đồ PlantUML tương ứng: [deployment_diagram.puml](file:///e:/AITA/docs/diagrams/puml/deployment_diagram.puml).

---

## 2. Đặc Tả Các Node Hệ Thống & Hệ Điều Hành (System Nodes & OS Specifications)

Toàn bộ hệ thống AITA được phân bổ trên **5 Node kiến trúc** chính:

```text
+-------------------------------------------------------------+
|   Node 1: Instructor Workstation (Windows 10/11 64-bit)     |
|   - Artifact: AITA_Grader_v1.exe (PyQt6 Client)             |
|   - 3 Design Patterns: Factory Method, Adapter, Strategy    |
|   - Toolchain: MinGW GCC, OpenJDK, Python & psutil Sandbox  |
+-------------------------------------------------------------+
                              │
                              │ HTTPS / TLS 1.3 (Port 443)
                              ▼
+-------------------------------------------------------------+       +------------------------------------+
|   Node 3: Render.com Cloud Platform (Web Service)           |       | Node 2: Administrator Terminal     |
|   - Managed TLS 1.3 Ingress & Edge Proxy                    | ◄──── | (Chrome/Edge/Firefox on any OS)    |
|   - central-backend (NestJS 10, Node.js 20 LTS Runtime)    |       | - Next.js Web Admin Dashboard      |
|   - In-Memory Rate Limiting (Sliding Window Throttler)      |       +------------------------------------+
+-------------------------------------------------------------+
         │                                            │
         │ PostgreSQL over TLS (Port 5432)            │ HTTPS / TLS 1.3 (Port 443)
         ▼                                            ▼
+------------------------------------+       +------------------------------------+
| Node 4: Neon Serverless Postgres   |       | Node 5: OpenRouter AI Service      |
| (Managed Cloud Database)           |       | (Managed AI Infrastructure)        |
| - Lakebase PostgreSQL 16 Engine    |       | - Model Aggregator API             |
| - aita_central_db (Pooled/Direct)  |       | - openrouter.ai/api/v1             |
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
  - **Môi trường ảo AITA**: File thực thi `AITA_Grader_v1.exe` tích hợp sẵn Python 3.11 Runtime, PyQt6 Native Engine.
  - **Toolchain portable đi kèm**: Thư mục `toolchains/` nằm cạnh file chạy (trong `_internal/toolchains/`) chứa MinGW-w64 GCC, OpenJDK rút gọn bằng `jlink` và Python embeddable. App **ưu tiên** dùng bộ này trước, nên máy giảng viên không cần cài đặt gì thêm; nếu giảng viên muốn dùng bản cài riêng thì chỉ định trong **Cấu Hình Môi Trường** (lưu tại `config.json`).
  - **Trình biên dịch C**: MinGW-w64 GCC 13+ (`toolchains/mingw64/bin/gcc.exe`).
  - **Trình biên dịch & Máy ảo Java**: OpenJDK 17/21 (`toolchains/jdk/bin/javac.exe`, `toolchains/jdk/bin/java.exe`).
  - **Trình thông dịch Python**: Python 3.11 embeddable (`toolchains/python/python.exe`) hoặc Python 3.10+ trên máy.
  - **Công cụ bảo vệ HĐH (Sandbox Guard)**: Thư viện `psutil` tích hợp sẵn trong client để giám sát mức chiếm dụng RAM, CPU và tự động cưỡng chế diệt các tiến trình lặp vô hạn.
- **Lưu trữ cục bộ**: 
  - Cơ sở dữ liệu SQLite 3 (`%LOCALAPPDATA%/AITA/data/local_grading.db` khi chạy bản đóng gói; `apps/desktop-client/data/local_grading.db` khi chạy dev — chế độ WAL): Lưu cấu hình đợt chấm, testcase và kết quả chấm offline.
  - Tập tin CSV: `results.csv` (đầu ra: 7 cột hoàn chỉnh) — đầu vào là thư mục bài nộp (mỗi thư mục con = 1 MSSV, không còn nạp `students.csv`).

---

### 2.2. Node 2: Máy Trạm Quản Trị Viên (Administrator Terminal)

- **Vai trò**: Cung cấp giao diện Web Admin để Quản trị viên (Admin) cấu hình hệ thống, quản lý tài khoản giảng viên, theo dõi hạn ngạch AI Hub và kiểm toán hệ thống.
- **Hệ điều hành**: Độc lập nền tảng (Hỗ trợ tốt trên Windows, macOS, Linux).
- **Phần mềm yêu cầu**: Trình duyệt Web chuẩn HTML5 hiện đại (Google Chrome ≥ 115, Microsoft Edge ≥ 115, Mozilla Firefox ≥ 118, Safari ≥ 16).
- **Giao diện Web Frontend**: Ứng dụng Single Page Application (SPA) xây dựng trên nền tảng Next.js 14+ / React với thiết kế Modern Dashboard, tải trực tiếp qua giao thức HTTPS.

---

### 2.3. Node 3: Dịch Vụ Máy Chủ Đám Mây (Render.com Cloud PaaS Web Service)

- **Vai trò**: Đóng vai trò Backend API tập trung, cung cấp endpoint xác thực JWT, quản lý tài khoản giảng viên, kiểm soát hạn ngạch và đóng vai trò AI Gateway Hub bảo mật trung gian khi gọi AI Hub.
- **Nền tảng triển khai**: **Render.com Cloud Platform (Managed Web Service)**.
  - *Môi trường Production*: Triển khai trên Linux Containerized Runtime chạy Node.js 20 LTS tại địa chỉ `https://iata-project-o4z6.onrender.com/api/v1`.
  - *Môi trường Local Development*: Khởi chạy trực tiếp bằng Node.js 20 LTS qua lệnh `npm run start:dev` (lắng nghe tại `http://localhost:3000/api/v1`).
- **Cấu hình & Quản lý lưu lượng**:
  - **Tự động quản lý SSL/TLS 1.3**: Nền tảng Render tự động cung cấp chứng chỉ SSL/TLS 1.3 Let's Encrypt, hỗ trợ HTTP/2 và cơ chế phòng chống DDoS tầng mạng.
  - **In-Memory Rate Limiting**: Sử dụng bộ lưu trữ bộ nhớ trong (In-Memory Sliding Window Storage) thông qua `@nestjs/throttler` để kiểm soát tần suất request (mặc định 80 requests/phút). Hỗ trợ mở rộng kết nối biến `REDIS_URL` khi triển khai cụm phân tán mà không bắt buộc phụ thuộc Redis.
  - **6 Modules Kiến trúc Cốt lõi**:
    1. `AuthModule`: Xác thực đăng nhập qua JWT Bearer, mã hóa mật khẩu Bcrypt, cấp và thu hồi Refresh Token.
    2. `UsersModule`: Quản lý danh sách tài khoản giảng viên, phân quyền RBAC (`ADMIN`, `INSTRUCTOR`).
    3. `AiGatewayModule`: Proxy an toàn gọi OpenRouter API, tích hợp cơ chế đếm token tiêu thụ và khóa gọi khi vượt hạn ngạch ngày.
    4. `AuditLogsModule`: Ghi nhận và truy vấn nhật ký gọi AI theo người dùng, khoảng thời gian và tính năng.
    5. `HealthModule`: Cung cấp endpoint kiểm tra tình trạng dịch vụ (`/health`).
    6. `SystemModule`: Cung cấp manifest cập nhật desktop (`/system/version`) từ GitHub Release hoặc biến môi trường.

---

### 2.4. Node 4: Dịch Vụ Cơ Sở Dữ Liệu Đám Mây (Neon Serverless PostgreSQL Cloud)

- **Vai trò**: Lưu trữ dữ liệu tập trung gồm tài khoản người dùng, cấu hình hạn ngạch AI, refresh token và nhật ký sử dụng AI. Toàn bộ phiên chấm, bài nộp sinh viên và bảng điểm được lưu cục bộ trên Desktop App theo nguyên tắc Local-First (SQLite `apps/desktop-client/data/local_grading.db` và `results.csv`).
- **Nền tảng**: **Neon Serverless Postgres** (Database-as-a-Service xây dựng trên kiến trúc Lakebase Postgres hiện đại).
- **Hệ quản trị CSDL**: **PostgreSQL 16 Engine**.
- **Tính năng nổi bật & Bảo đảm**:
  - Giao tiếp mã hóa đầu cuối qua giao thức PostgreSQL over TLS 1.3 (cổng 5432).
  - Cơ chế Connection Pooling tích hợp: Prisma ORM sử dụng biến `DATABASE_URL` (kết nối qua PgBouncer connection pooling) cho các truy vấn ứng dụng và `DATABASE_URL_UNPOOLED` (Direct Connection) cho các tác vụ Prisma Migrate.
  - Khả năng tự động co giãn tài nguyên (Auto-scaling) và tự động sao lưu dữ liệu (Continuous Backup & Point-in-Time Recovery).

---

### 2.5. Node 5: Dịch Vụ Trí Tuệ Nhân Tạo Đám Mây (OpenRouter AI Service)

- **Vai trò**: Cung cấp mô hình ngôn ngữ lớn (LLM) hỗ trợ tự động sinh testcase biên, phân tích lỗi code, đối chứng gian lận học thuật, đánh giá giao diện Web (AI Vision) và rubric chấm bài thực hành (PE).
- **Nền tảng**: **OpenRouter** (nền tảng tổng hợp nhiều LLM — tổng hợp truy cập nhiều model qua một API duy nhất).
- **Endpoint**: `https://openrouter.ai/api/v1` (giao tiếp qua REST API HTTPS).
- **Mô hình triển khai**: Model AI chính cấu hình bằng biến `OPENROUTER_MODEL` (Ví dụ mẫu `google/gemma-4-31b-it:free`), model dự phòng qua `OPENROUTER_MODEL_FALLBACKS`; backend giữ danh sách nhiều API key trong secret `OPENROUTER_API_KEYS` (xoay vòng tự động khi key bị giới hạn) — key chỉ nằm trong secret môi trường của backend, không bao giờ lộ ra client.

---

## 3. Danh Mục Artifacts & Môi Trường Triển Khai (Deployed Artifacts Matrix)

| Artifact Name | Định dạng đóng gói | Nơi triển khai (Deployed Node) | Công nghệ nền tảng | Mục đích sử dụng |
| :--- | :--- | :--- | :--- | :--- |
| **`AITA_Grader_v1.exe`** | Standalone Executable | Node 1 (Instructor PC) | PyInstaller, Python 3.11, PyQt6 | Ứng dụng Desktop bản địa dành cho Giảng viên |
| **`local_grading.db`** | SQLite 3 File | Node 1 (Instructor PC) | SQLite Embedded Engine (WAL) | Lưu testcases, bài nộp và kết quả chấm offline |
| **`Web Admin UI`** | SPA Static Bundle | Node 2 (Admin Browser) | Next.js 14, React, TailwindCSS | Giao diện điều hành hệ thống của Admin |
| **`central-backend`** | Web Service Artifact | Node 3 (Render.com PaaS) | NestJS 10, Node.js 20, TypeScript | REST API Gateway, Auth RBAC, AI Quota Guard |
| **`aita_central_db`**| Cloud Relational DB | Node 4 (Neon Cloud) | Neon Serverless PostgreSQL 16 | Cơ sở dữ liệu tập trung lưu Users, Quota Configs/Logs, Refresh Tokens |

---

## 4. Ma Trận Giao Thức Mạng, Cổng Truyền Thông & Bảo Mật (Network Protocols & Ports)

| Nguồn kết nối (Source) | Đích kết nối (Destination) | Giao thức (Protocol) | Cổng mạng (Port) | Cơ chế bảo mật & Xác thực |
| :--- | :--- | :--- | :---: | :--- |
| Admin Web Browser | Central Backend (Render) | **HTTPS (HTTP/2)** | `443` | Mã hóa TLS 1.3, Chứng chỉ SSL Let's Encrypt |
| Desktop Client (`AITA_Grader_v1.exe`) | Central Backend (Render) | **HTTPS REST** | `443` | JSON Web Token (JWT Bearer Authorization) |
| Central Backend (Render) | Neon Serverless Postgres | **PostgreSQL over TLS** | `5432` | TLS 1.3 Encrypted, Prisma Connection Pool (PgBouncer) |
| Central Backend (Render) | OpenRouter AI API | **HTTPS / REST** | `443` | TLS 1.3, Secure API Key trong Header máy chủ (`Authorization: Bearer sk-or-...`) |
| Desktop Client (`AITA_Grader_v1.exe`) | Local Compiler Toolchain | **OS Standard Streams** | `IPC` | Đường ống Stdin, Stdout, Stderr qua `subprocess` |

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
  - Dùng `--onedir` (thư mục `dist/AITA_Grader_v1/`) thay vì `--onefile`, vì bộ toolchain portable đi kèm nặng ~340 MB; `--onefile` sẽ giải nén lại toàn bộ ra thư mục tạm ở **mỗi lần khởi động**, làm app chậm và tốn RAM/đĩa.
  - Bổ sung file `.spec` tối ưu hóa, loại bỏ các package thừa của Python (`tkinter`, `matplotlib`, `numpy`…) để phần lõi app chỉ còn ~15 MB.
  - **Toolchain portable đi kèm** (thư mục `toolchains/` trong `_internal/`, phát hiện qua `core/app_paths.bundled_toolchains_dir()`):
    - `mingw64/bin/gcc.exe`: MinGW-w64 GCC đã cắt bộ tối thiểu (chỉ giữ `cc1`, `as`, `ld`, `collect2`, các thư viện `libgcc`/`libmingwex`/`crt*.o`), ~277 MB.
    - `jdk/bin/{javac,java}.exe`: OpenJDK rút gọn bằng `jlink` (`java.base, java.compiler, jdk.compiler, java.logging, jdk.jfr, java.management, jdk.unsupported`), ~44 MB.
    - `python/python.exe`: Python 3.11 embeddable chính thức của python.org, ~21 MB.
  - Tạo toolchain bằng script tái lập được (chạy trên máy dev đã cài sẵn GCC/JDK):
    ```bash
    python apps/desktop-client/scripts/build_toolchains.py \
        --mingw "C:/path/to/mingw64" \
        --jdk "C:/Program Files/Java/jdk-21" \
        --out apps/desktop-client/toolchains \
        --smoke-test
    ```
  - Build bản phát hành: `python -m PyInstaller apps/desktop-client/AITA_Grader_v1.spec --noconfirm`
    (kết quả `dist/AITA_Grader_v1/`, tổng ~590 MB, nén ZIP còn ~150 MB).
  - **Thứ tự dò công cụ** (áp dụng cho cả `gcc`, `javac`, `java`, `python`): toolchain đóng kèm → đường dẫn giảng viên lưu trong `config.json` → `JAVA_HOME` / biến môi trường (`AITA_PYTHON`) → `PATH` → registry / WinGet. Nhờ vậy bản đóng gói chấm được ngay cả khi máy đích **chưa cài** GCC/JDK/Python, mà vẫn ưu tiên bản cài trên máy nếu giảng viên muốn dùng bản mới hơn.
  - **Tự kiểm tra môi trường**: `AITA_Grader_v1.exe --selftest` chạy thật `gcc`/`javac`+`java`/`python` trên một chương trình `a + b`, in kết quả ra console **và** ghi `aita_selftest.txt` cạnh file exe (tự mở bằng Notepad nếu chạy bằng double-click). Đây là công cụ hỗ trợ từ xa khi giảng viên gặp lỗi môi trường.
  - **Dữ liệu người dùng**: CSDL SQLite và `config.json` được ghi vào `%LOCALAPPDATA%/AITA/data/` (không ghi vào thư mục tạm của PyInstaller, tránh mất điểm đã chấm sau khi tắt app).

### 6.2. Triển khai Máy chủ Trung tâm trên Render.com & Neon Cloud
- **Triển khai Production trên Render.com**:
  - Kết nối repository Git trực tiếp với Render Web Service.
  - Thiết lập Build Command: `npm install && npm run build && npm run db:generate`
  - Thiết lập Start Command: `npm run start:prod`
  - Khai báo các Environment Secrets: `DATABASE_URL`, `DATABASE_URL_UNPOOLED`, `OPENROUTER_API_KEYS`, `OPENROUTER_MODEL`, `JWT_ACCESS_SECRET`, `JWT_REFRESH_SECRET`, `CORS_ORIGINS` (xem `.env.example`).
- **Khởi chạy môi trường phát triển cục bộ (Local Development)**:
  ```bash
  cd apps/central-backend
  npm install
  npm run db:generate
  npm run start:dev
  ```

### 6.3. Quy Trình Phát Hành Bản Cập Nhật & Cơ Chế Tự Cập Nhật (Release & Auto-Update Runbook)

Desktop Client **không** tự ý tải bản mới: khi khởi động nó hỏi *manifest* tại `GET /api/v1/system/version`,
rồi so sánh với `APP_VERSION` trong `src/core/version.py` (`services/update_service.py::is_newer`).
Manifest **không** đọc từ CSDL. Nguồn ưu tiên là **release mới nhất trên GitHub**: `GitHubReleaseService`
gọi `GET https://api.github.com/repos/{APP_UPDATE_GITHUB_REPO}/releases/latest` (bật/tắt bằng
`APP_UPDATE_SOURCE=github|env`, mặc định `github`), backend tự suy ra `latest_version` từ tag
(`v1.1.0-portable` → `1.1.0`), `url`, `sha256` (từ `digest` của asset ZIP) và `size_bytes`, cache trong
`APP_UPDATE_GITHUB_TTL_SECONDS` (mặc định 300 giây). Khi tắt nguồn GitHub, chưa cấu hình repo, hoặc GitHub
lỗi (401/404/rate-limit/timeout) thì manifest rơi về các biến `APP_UPDATE_*`; nhờ vậy `/system/version`
**không bao giờ trả 500 chỉ vì GitHub**.

**Các bước phát hành một bản mới:**

| # | Bước | Chi tiết |
| :-: | :--- | :--- |
| 1 | Tăng phiên bản | Sửa `APP_VERSION` (và `APP_BUILD`) trong `apps/desktop-client/src/core/version.py` — nguồn duy nhất cho màn hình đăng nhập, `User-Agent` và phép so sánh cập nhật. |
| 2 | Chạy kiểm thử | `pytest` (desktop) và `npx jest` (backend). |
| 3 | Đóng gói | Chạy `build.bat` ở gốc repo → sinh `dist/AITA_Grader_v1/` và `dist/AITA_Grader_v1_portable.zip`, in ra **kích thước (byte)** và **SHA-256** (dùng để đối chiếu thủ công khi cần). |
| 4 | Kiểm tra gói | `AITA_Grader_v1.exe --selftest` phải báo GCC/JDK/Python đều `OK (3+4=7)`, sau đó mở app chấm thử một bài. Chỉ chạy file trong `dist/`; **không** chạy file trong `build/` (file trung gian, thiếu `_internal/` nên báo lỗi "Failed to load Python DLL"). |
| 5 | Phát hành | Tạo GitHub Release với **tag mới** và upload gói ZIP:<br>`gh release create v1.0.1 dist/AITA_Grader_v1_portable.zip --target master --title "AITA Grader v1.0.1" --notes-file notes.md --latest` |
| 6 | Cấu hình backend (chỉ làm **một lần**) | Khai báo trên Render: `APP_UPDATE_SOURCE=github`, `APP_UPDATE_GITHUB_REPO=<owner>/<repo>`, `GITHUB_TOKEN` (chỉ cần khi repo **private** — fine-grained PAT có quyền `Contents: Read-only`), `APP_MIN_SUPPORTED_VERSION`, `APP_UPDATE_ENTRYPOINT=AITA_Grader_v1.exe`, `APP_UPDATE_ARTIFACT_TYPE=zip`, (tuỳ chọn) `APP_UPDATE_MANDATORY`. **Không phải sửa `APP_LATEST_VERSION` / `APP_UPDATE_URL_WINDOWS` / `APP_UPDATE_SHA256_WINDOWS` / `APP_UPDATE_SIZE_WINDOWS` mỗi bản** — backend tự lấy từ release. Chỉ dùng nhóm biến đó khi muốn tắt nguồn GitHub (`APP_UPDATE_SOURCE=env`). |
| 7 | Nghiệm thu | `curl https://iata-project-o4z6.onrender.com/api/v1/system/version` để xem manifest, rồi mở bản cũ trên máy giảng viên và xác nhận hộp thoại "Cập nhật AITA". |

**Cơ chế tự cập nhật phía client** (`services/update_service.py`, `ui/dialogs/update_dialog.py`):

- Kiểm tra **một lần mỗi 24 giờ** lúc khởi động (khoá `QSettings("AITA", "Updater")`), ghi nhớ `skipped_version` khi giảng viên chọn "Nhắc lại sau"; mọi lỗi mạng/500 đều **im lặng**, không chặn màn hình đăng nhập.
- Chỉ tải khi URL bắt đầu bằng `https://`, sau đó **đối chiếu SHA-256**; sai lệch là huỷ, không cài.
- Gói ZIP phải để file **ngay ở gốc** (không bọc thư mục `AITA_Grader_v1/`): client giải nén vào thư mục payload rồi `robocopy /E /XF *.db /XD data` đè thẳng lên thư mục cài đặt, nhờ vậy dữ liệu người dùng (`data/`, `*.db`) luôn được giữ nguyên.
- Sau khi tải xong, client sinh `update.bat`, tự thoát, chờ tiến trình AITA kết thúc rồi mới thay file và mở lại exe mới.
- `min_supported_version` đã có trong manifest và được client đọc, nhưng **chưa cưỡng chế**; chỉ cờ `mandatory` có tác dụng thật (ẩn nút "Nhắc lại sau").

> ⚠️ **Lưu ý vận hành**: (1) Với repo **private**, client tải asset ẩn danh sẽ nhận HTTP 404 (auto-update im lặng không chạy) và backend **bắt buộc** có `GITHUB_TOKEN` mới đọc được release — cách gọn nhất là chuyển repo sang **public** khi phát hành cho giảng viên. (2) Phiên bản mới phải **lớn hơn** phiên bản đang chạy — máy còn bản `2.5.0` sẽ coi mọi bản `1.x` là cũ. (3) Nếu repository bật **immutable releases**, tag đã dùng không thể tạo lại nên mỗi lần phát hành phải dùng tag mới. (4) Ghi chú cập nhật hiển thị cho giảng viên lấy từ **tên release** (hoặc `APP_UPDATE_NOTES` nếu có khai báo).

---

## 7. Mối Liên Kết Triển Khai Của 3 Mẫu Thiết Kế (Design Patterns Deployment Context)

Cả **3 Mẫu thiết kế cốt lõi** bắt buộc của đồ án AITA đều được đóng gói trực tiếp bên trong artifact **`AITA_Grader_v1.exe`** trên máy trạm của Giảng viên (Node 1):

1. **`RunnerFactory` (Creational Pattern)**: 
   - Nằm tại module `src/core/factories/`.
   - Vận hành tại thời điểm người dùng bắt đầu phiên chấm: Đọc phần mở rộng của file bài nộp sinh viên (`.c`, `.java`, `.py`) từ danh sách nạp để khởi tạo đối tượng `BaseRunner` phù hợp với tài nguyên của máy trạm.
2. **`CompilerAdapter` (Structural Pattern)**:
   - Nằm tại module `src/core/adapters/`.
   - Đóng vai trò cầu nối tương tác trực tiếp với các trình biên dịch cục bộ cài trên HĐH Windows (`MinGW GCC`, `Javac`, `Python Runtime`), chuẩn hóa lệnh gọi OS và ánh xạ các thông báo lỗi `stderr` thành các mã kết quả chuẩn (`CE`, `RE`).
3. **`IMatchingStrategy` & `MatchingContext` (Behavioral Pattern)**:
   - Nằm tại module `src/core/strategies/`.
   - Nằm ở tầng xử lý logic cốt lõi: Nhận kết quả `stdout` từ tiến trình con do Runner trả về và so khớp với `expected_output` của giảng viên. Cung cấp 7 thuật toán so khớp độc lập cùng bộ điều phối linh hoạt `FlexibleMatchingStrategy` (kết hợp các cờ: Bỏ qua khoảng trắng, Không phân biệt hoa thường, Dung sai số thực, Cho phép hoán vị từ, Regex, Special Judge; bỏ chọn tất cả ứng với Exact Match) trước khi xuất ra bảng điểm `results.csv`.

Chi tiết kiến trúc và phân tích nguyên lý của 3 mẫu này được đặc tả tại: [docs/architecture/design-patterns.md](file:///e:/AITA/docs/architecture/design-patterns.md).
