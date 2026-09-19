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
