# Nhật Ký Ghi Nhận Sử Dụng AI (AI Prompts & Usage Log)
## Giai đoạn: Evaluation 2 - Software Architecture & Design (SWD392)
## Dự án: AITA - Automated Grading Tool for Instructors

Tài liệu này ghi nhận minh bạch toàn bộ các câu Prompt và kết quả hỗ trợ từ AI được sử dụng trong giai đoạn **Đánh giá 2 (Evaluation 2: Software Architecture & Design - 20%)**, tuân thủ tiêu chí đánh giá **AI Evaluation Rubric (Transparency, Understanding & Customization)** của môn học SWD392.

---

## 1. Thông Tin Chung

- **Công cụ AI sử dụng**: Antigravity AI Assistant / ChatGPT / Google Gemini
- **Người thực hiện**: Nhóm phát triển dự án AITA
- **Mục tiêu giai đoạn Evaluation 2**:
  1. Lựa chọn kiến trúc phần mềm tổng thể (Layered & Clean Architecture, Client-Server RESTful).
  2. Thiết kế và đóng gói 4 sơ đồ hệ thống chuẩn UML & CSDL:
     - **Component Diagram** (Sơ đồ thành phần các phân hệ).
     - **Deployment Diagram** (Sơ đồ triển khai hệ điều hành máy trạm & cloud server).
     - **Database Schema / ERD** (Thiết kế thực thể CSDL tập trung & SQLite cục bộ).
     - **Class Diagram** (Sơ đồ lớp chi tiết cho ít nhất 3 phân hệ - subsystems).
  3. Áp dụng đủ **3 mẫu thiết kế (Design Patterns)** trong mã nguồn và sơ đồ lớp:
     - *Mẫu Khởi tạo (Creational)*: Factory Method (`RunnerFactory`).
     - *Mẫu Cấu trúc (Structural)*: Adapter Pattern (`CompilerAdapter`).
     - *Mẫu Hành vi (Behavioral)*: Strategy Pattern (`MatchingStrategy` với 7 chế độ so khớp).
  4. Biên soạn đoạn code mẫu có chú thích (Annotated Code) chứng minh tính khớp nối giữa sơ đồ lớp và mã nguồn thực tế.

---

## 2. Nhật Ký Chi Tiết Các Prompt Đã Sử Dụng

---

### 🔹 PROMPT 01: Thiết Kế Sơ Đồ Lớp (Class Diagram) Cho 3 Phân Hệ & Tích Hợp 3 Mẫu Thiết Kế (Design Patterns)

#### 1. Mục tiêu
Nhờ AI tư vấn phương án phân bổ 3 phân hệ (Subsystems) và tích hợp đủ 3 nhóm Design Patterns (Creational, Structural, Behavioral) vào mô hình Class Diagram của đồ án AITA để đáp ứng hoàn hảo tiêu chí chấm điểm Evaluation 2 môn học SWD392.

#### 2. Câu Prompt đã gửi
> *"task Class Diagram làm như nào (Sơ đồ lớp cho ít nhất 3 phân hệ - subsystems, Áp dụng đủ 3 mẫu thiết kế (Design Patterns))"*

#### 3. Kết quả do AI sinh ra (AI Output)
AI đã tư vấn kiến trúc phân bổ sơ đồ lớp thành 3 phân hệ cốt lõi:
1. **Phân hệ 1: Sandbox & Execution Engine**:
   - Áp dụng **Factory Method** (`RunnerFactory` tự động sinh `CRunner`, `JavaRunner`, `PythonRunner` theo phần mở rộng file).
   - Áp dụng **Adapter Pattern** (`CompilerAdapter` đóng gói và chuẩn hóa lệnh biên dịch của `GccAdapter`, `JavacAdapter`).
   - Tích hợp lớp giám sát tài nguyên `ResourceMonitor` (thư viện `psutil` bắt lỗi TLE/MLE).
2. **Phân hệ 2: Grading Core & Matching Engine**:
   - Áp dụng **Strategy Pattern** (`MatchingStrategy` làm interface, triển khai 7 lớp chiến lược: Exact, Ignore Whitespace, Case-Insensitive, Float Tolerance, Unordered, Regex, Special Judge).
   - Lớp điều phối ngữ cảnh `GradingContext` và các thực thể dữ liệu (`Submission`, `TestCase`, `GradingResult`).
3. **Phân hệ 3: Central Backend & AI Gateway (FastAPI Service)**:
   - Tầng dịch vụ quản lý xác thực JWT và kiểm soát hạn ngạch Quota (`AuthService`, `QuotaManager`).
   - Cầu nối AI Hub (`GeminiGateway`) điều phối gọi Google Gemini API bảo mật.
   - Dịch vụ đồng bộ dữ liệu đợt chấm `GradingSessionSyncService` lưu CSDL trung tâm qua SQLAlchemy ORM.

#### 4. Giải trình & Tinh chỉnh của Nhóm (Team Justification & Customization)
- **Điểm nhóm làm chủ và đánh giá cao**: Việc phân chia ranh giới 3 phân hệ giúp sơ đồ lớp không bị rối rắm, thể hiện rõ tính độc lập giữa động cơ chạy code cục bộ (Sandbox) và tầng nghiệp vụ tính điểm (Strategy).
- **Quyết định kỹ thuật của nhóm**: 
  - Khẳng định 3 mẫu thiết kế được chọn (`RunnerFactory`, `CompilerAdapter`, `MatchingStrategy`) là những giải pháp tự nhiên và bắt buộc đối với một hệ thống chấm điểm đa ngôn ngữ, không phải đưa vào để đối phó đề bài.
  - Nhóm quyết định chuẩn bị đóng gói file mã nguồn PlantUML `docs/diagrams/puml/class_diagram.puml` bám sát chính xác khung kiến trúc này.

---

### 🔹 PROMPT 02: Hiện Thực Hóa Mã Nguồn PlantUML Sơ Đồ Lớp (Class Diagram) Cho 3 Phân Hệ & Tích Hợp 3 Mẫu Thiết Kế

#### 1. Mục tiêu
Chuyển hóa khung thiết kế kiến trúc đã thống nhất ở Prompt 01 thành mã nguồn sơ đồ lớp PlantUML chi tiết, trực quan và hoàn chỉnh, đặt tại [docs/diagrams/puml/class_diagram.puml](file:///d:/SWD_Project/docs/diagrams/puml/class_diagram.puml). Sơ đồ cần thể hiện rõ đầy đủ thuộc tính, phương thức, kiểu dữ liệu, các mối quan hệ hướng đối tượng (Inheritance, Realization, Dependency, Aggregation, Composition) và gắn ghi chú nổi bật cho 3 mẫu thiết kế bắt buộc theo Rubric SWD392.

#### 2. Câu Prompt đã gửi
> *"docs/ai-prompts/eval-2/ai-prompts-log.md ghi lại log khi tôi prompt. Thực hiện task Class Diagram (theo phân hệ 1 2 3 đã prompt trước đó)"*

#### 3. Kết quả do AI sinh ra (AI Output)
AI đã thiết kế và đóng gói thành công file mã nguồn PlantUML [docs/diagrams/puml/class_diagram.puml](file:///d:/SWD_Project/docs/diagrams/puml/class_diagram.puml) bao quát trọn vẹn:
1. **Phân hệ 1 (Sandbox Execution & Compiler Engine - Màu xanh lá #E8F5E9)**:
   - **Factory Method**: Lớp `RunnerFactory` sở hữu phương thức `create_runner(file_extension, source_path)` tự động khởi tạo đối tượng `CRunner`, `JavaRunner`, `PythonRunner` kế thừa lớp trừu tượng `BaseRunner`.
   - **Adapter Pattern**: Giao diện `CompilerAdapter` cùng 2 lớp hiện thực `GccAdapter` và `JavacAdapter` chuẩn hóa các lệnh biên dịch và bóc tách thông báo lỗi `stderr`.
   - Lớp `ResourceMonitor` (psutil) liên kết với `BaseRunner` để đo đạc thời gian, bộ nhớ và cưỡng chế kill tiến trình khi vượt trần (bắt TLE 1000ms / MLE 256MB).
2. **Phân hệ 2 (Grading Core & Output Matching Subsystem - Màu tím #EDE7F6)**:
   - **Strategy Pattern**: Interface `MatchingStrategy` cùng 7 lớp chiến lược hiện thực (`ExactMatchStrategy`, `IgnoreWhitespaceStrategy`, `CaseInsensitiveStrategy`, `FloatingPointToleranceStrategy`, `UnorderedTokensStrategy`, `RegexPatternStrategy`, `SpecialJudgeStrategy`).
   - Lớp ngữ cảnh `GradingContext` nắm giữ tham chiếu `MatchingStrategy` và cho phép hoán đổi thuật toán linh hoạt lúc runtime.
   - Lớp điều phối `BatchGradingManager` quản lý danh sách `Submission`, nạp `TestCase`, gọi `RunnerFactory` và sinh kết quả `GradingResult`.
3. **Phân hệ 3 (Central Backend & AI Gateway Subsystem - Màu xanh dương #E3F2FD)**:
   - Tầng điều khiển & định tuyến API: `AuthController`, `AIGatewayController`, `SyncController`.
   - Tầng dịch vụ nghiệp vụ: `AuthService` (băm mật khẩu Bcrypt, mã hóa JWT), `QuotaManager` (kiểm tra và trừ hạn ngạch gọi AI), `GeminiGatewayService` (kết nối bảo mật với Google Gemini API), `GradingSessionSyncService` (lưu trữ CSDL trung tâm).
   - Tầng thực thể CSDL ORM: `User`, `Course`, `GradingSessionRecord`.
4. **Liên kết liên phân hệ (Cross-subsystem relationships)** và các ghi chú (Notes) làm nổi bật 3 Design Patterns theo yêu cầu đề bài.

#### 4. Giải trình & Tinh chỉnh của Nhóm (Team Justification & Customization)
- **Tính chuẩn xác và gắn kết mã nguồn**: Các thuộc tính, phương thức và kiểu dữ liệu được mô hình hóa trong sơ đồ khớp 100% với kiến trúc mã nguồn Python hiện có trong thư mục `src/`, không tạo ra các lớp "ảo" vô nghĩa.
- **Tính trực quan và thẩm mỹ**: Áp dụng 3 tông màu phân biệt cho 3 phân hệ, phân nhóm package mạch lạc giúp người xem và hội đồng chấm thi dễ dàng nhận diện ngay vị trí áp dụng của từng Design Pattern, sẵn sàng phục vụ cho buổi bảo vệ Evaluation 2.

---

### 🔹 PROMPT 03: Thiết Kế Sơ Đồ Triển Khai Hệ Điều Hành / Máy Chủ (Deployment Diagram) & Đặc Tả Hạ Tầng Triển Khai

#### 1. Mục tiêu
Nhờ AI hỗ trợ thiết kế mô hình sơ đồ triển khai (UML 2.5 Deployment Diagram) bao quát toàn bộ các Node vật lý, hệ điều hành (Windows 10/11 cho máy trạm Giảng viên, Ubuntu Linux 22.04 LTS cho máy chủ trung tâm), các môi trường thực thi runtime, cổng mạng và giao thức truyền thông; đồng thời làm rõ vị trí triển khai của 3 Design Patterns cốt lõi bên trong ứng dụng Desktop của Giảng viên.

#### 2. Câu Prompt đã gửi
> *"lead đang giao task này cho tôi bạn hãy đọc hết nội dung task này rồi lên plan thực hiện: Deployment Diagram - Sơ đồ triển khai hệ điều hành / server, Áp dụng đủ 3 mẫu thiết kế (Design Patterns)"*

#### 3. Kết quả do AI sinh ra (AI Output)
AI đã thiết kế trọn vẹn giải pháp kiến trúc triển khai gồm:
1. **Sơ đồ PlantUML chuẩn mực `docs/diagrams/puml/deployment_diagram.puml`**:
   - **Node 1: Instructor Workstation (Windows 10/11 64-bit)**: Chạy `AITA.exe` (PyQt6/Python 3.11), tích hợp sẵn 3 Design Patterns (`RunnerFactory`, `CompilerAdapter`, `MatchingStrategy`), tương tác với bộ Toolchain cục bộ (`gcc.exe`, `javac.exe`, `python.exe`) và bộ giám sát tài nguyên `psutil`.
   - **Node 2: Administrator Workstation**: Trình duyệt Web hiện đại kết nối Next.js Web Admin Dashboard qua HTTPS (Port 443).
   - **Node 3: Central Application Server Host (Ubuntu Linux 22.04 LTS)**: Chạy Nginx Ingress Proxy (chặn SSL/TLS 1.3, rate limit) chuyển tiếp vào Docker Container `central-backend` (NestJS 10, JWT RBAC Guard, AI Gateway Hub) và Redis In-Memory Cache (Port 6379).
   - **Node 4: Central Database Server Node (Ubuntu Linux / Managed DB)**: Chạy PostgreSQL 16 RDBMS (Port 5432, SSL encrypted).
   - **Node 5: Google Cloud Platform (PaaS AI)**: Dịch vụ Google Gemini 1.5 Flash API phục vụ sinh testcase và phân tích lỗi.
2. **Tài liệu đặc tả kiến trúc triển khai `docs/architecture/deployment-specification.md`**:
   - Thuyết minh chi tiết thông số phần cứng tối thiểu/khuyến nghị (CPU Cores, RAM, SSD NVMe).
   - Ma trận cổng mạng, giao thức truyền thông (HTTPS Port 443, PostgreSQL 5432, Redis 6379, IPC Stdin/Stdout).
   - Cơ chế cách ly 4 lớp bảo vệ an toàn HĐH (Subprocess Isolation, psutil Memory Poller, Anti-Freeze Timeout, Isolated Temp Folder).

#### 4. Giải trình & Tinh chỉnh của Nhóm (Team Justification & Customization)
- **Điểm nhóm làm chủ**: Lựa chọn mô hình Hybrid (Offline-first trên máy trạm Windows của Giảng viên kết hợp Central Cloud Sync) giải quyết triệt để 2 bài toán sống còn: (1) Chấm 50 bài thi trong 15-30 giây không bị nghẽn mạng; (2) Giảng viên vẫn chấm thi được khi phòng máy bị ngắt Internet.
- **Tinh chỉnh của nhóm**: Bổ sung chi tiết cổng mạng (Ports), cơ chế mã hóa TLS 1.3 và lưu vết rõ ràng vị trí của 3 Design Patterns được đóng gói bên trong file nhị phân `AITA.exe`.

---

### 🔹 PROMPT 04: Đặc Tả Kiến Trúc & Giải Trình 3 Mẫu Thiết Kế (Design Patterns Specification & SOLID Justification)

#### 1. Mục tiêu
Biên soạn tài liệu đặc tả kiến trúc chuyên sâu giải trình lý do lựa chọn và cách thức áp dụng đủ 3 nhóm Design Patterns (Creational, Structural, Behavioral) trong phân hệ Động cơ Chấm bài của AITA theo đúng quy chuẩn học thuật môn học SWD392.

#### 2. Câu Prompt đã gửi
> *"Áp dụng đủ 3 mẫu thiết kế (Design Patterns) trong tài liệu kiến trúc: phân tích chi tiết bài toán, giải pháp thiết kế, sơ đồ lớp, mã nguồn cấu trúc và giải trình theo các nguyên lý thiết kế hướng đối tượng SOLID."*

#### 3. Kết quả do AI sinh ra (AI Output)
AI đã biên soạn hoàn chỉnh tài liệu học thuật `docs/architecture/design-patterns.md`:
1. **Creational Pattern - Factory Method (`RunnerFactory`)**:
   - Giải quyết bài toán sinh đối tượng Runner tương ứng với các ngôn ngữ C (`CRunner`), Java (`JavaRunner`), Python (`PythonRunner`) dựa trên phần mở rộng file bài nộp.
   - Thỏa mãn nguyên lý Open/Closed (OCP) qua cơ chế `register_runner()` động.
2. **Structural Pattern - Adapter Pattern (`CompilerAdapter`)**:
   - Chuẩn hóa giao diện gọi dòng lệnh và mã lỗi `stderr` của các bộ biên dịch ngoại vi khác nhau (`gcc`, `javac`, `python.exe`) thành đối tượng dữ liệu `CompileResult` đồng nhất.
   - Thỏa mãn Single Responsibility (SRP) và Interface Segregation (ISP).
3. **Behavioral Pattern - Strategy Pattern (`MatchingStrategy`)**:
   - Hiện thực hóa 7 chiến lược so khớp đầu ra (`ExactMatch`, `IgnoreWhitespace`, `CaseInsensitive`, `FloatingPointTolerance`, `UnorderedTokens`, `RegexPattern`, `SpecialJudge`).
   - Cho phép Giảng viên thay đổi thuật toán so khớp ngay tại thời điểm chạy (runtime) từ giao diện GUI mà không làm thay đổi luồng điều khiển `GradingContext`.
4. **Sơ đồ phối hợp tuần tự (Collaborative Workflow)** minh họa luồng tương tác giữa 3 mẫu khi giảng viên ấn nút chấm bài.

#### 4. Giải trình & Tinh chỉnh của Nhóm (Team Justification & Customization)
- **Điểm nhóm làm chủ**: Nhóm khẳng định việc áp dụng 3 Design Patterns là xuất phát từ yêu cầu kỹ thuật thực tế của phần mềm chấm thi tự động đa ngôn ngữ, giúp mã nguồn đạt độ tách biệt cao (decoupling), dễ dàng viết unit test với các đối tượng giả lập (Mocking) và đảm bảo tính mở rộng bền vững cho các kỳ học tiếp theo.

