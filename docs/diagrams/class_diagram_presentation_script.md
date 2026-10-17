# KỊCH BẢN BÁO CÁO VÀ BẢO VỆ SƠ ĐỒ LỚP TOÀN DIỆN (CLASS DIAGRAM)
**Hệ Sinh Thái AITA — Tự Động Hóa Chấm Điểm Đa Ngôn Ngữ & Trợ Lý Giảng Dạy AI**
**Môn học:** SWD392 — Software Architecture & Design

---

> [!NOTE]
> **Tài liệu tham chiếu:** [`docs/diagrams/puml/class_diagram.puml`](file:///e:/AITA/docs/diagrams/puml/class_diagram.puml)  
> **Thời lượng báo cáo đề xuất:** 4 – 6 phút thuyết trình + 4 phút trả lời câu hỏi phản biện (Q&A).  
> **Mục tiêu chính:** Trình bày rõ ràng kiến trúc 3 phân hệ, cách phân tách ranh giới an toàn giữa Local Engine và Cloud Backend, và phân tích sâu **3 Mẫu thiết kế Gang of Four (GoF)** theo rubric đồ án.

---

## 📌 BẢNG TỔNG QUAN PHÂN BỔ THỜI GIAN & SLIDE VISUAL

| STT | Phân Đoạn Báo Cáo | Thời Lượng | Điểm Nhấn Trực Quan Trên Sơ Đồ Class Diagram | Design Pattern / Trọng Tâm |
|---|---|---|---|---|
| **1** | **Lời Mở Đầu & Tổng Quan Hệ Thống** | 0:00 – 0:45 (45s) | Toàn cảnh 3 khối màu: Xanh lá (Local), Tím (Desktop), Xanh dương (Backend) | Kiến trúc phân tầng, nguyên tắc Loose Coupling & High Cohesion |
| **2** | **Phân Hệ 1: Sandbox & Compiler Engine** | 0:45 – 2:00 (75s) | Khối màu xanh lá: `RunnerFactory`, `BaseRunner`, `CompilerAdapter`, `ResourceMonitor` | **Factory Method** (Creational) & **Adapter Pattern** (Structural) |
| **3** | **Phân Hệ 2: Grading Core & Output Matching** | 2:00 – 3:15 (75s) | Khối màu tím: `GradingContext`, `MatchingStrategy` và cây 7 chiến lược dẫn xuất | **Strategy Pattern** (Behavioral) & Quản lý Batch Grading |
| **4** | **Phân Hệ 3: Central Backend & AI Gateway** | 3:15 – 4:15 (60s) | Khối màu xanh dương: `AuthController`, `AIGatewayController`, `QuotaManager`, `GeminiGatewayService` | Service Layer / Facade, Quota Management & RBAC |
| **5** | **Giao Tiếp Đa Phân Hệ & Kết Luận** | 4:15 – 4:45 (30s) | 2 mũi tên liên kết xuyên phân hệ (dòng 333 & 336 trong file puml) | Tách biệt Local Execution (Offline) và Cloud AI (Online) |
| **6** | **Hỏi & Đáp (Q&A Phản Biện)** | 4:45 – 8:00+ | Sẵn sàng zoom vào từng method và quan hệ class cụ thể | Trả lời trực diện các bẫy phản biện của Giảng viên |

---

## 🎙️ KỊCH BẢN CHI TIẾT TỪNG PHẦN (SPEECH SCRIPT)

### PHẦN 1: LỜI MỞ ĐẦU & TỔNG QUAN KIẾN TRÚC HỆ THỐNG
* **Thời lượng:** ~45 giây  
* **Thao tác trình chiếu:** Chiếu toàn bộ sơ đồ lớp, quét tay/con trỏ chuột qua 3 khối màu lớn.

> 🗣️ **Lời thoại thuyết trình:**
>
> *"Kính thưa Thầy/Cô và Hội đồng phản biện, sau đây em xin phép đại diện nhóm trình bày về **Sơ đồ lớp toàn diện (System-Wide Class Diagram)** của hệ thống AITA.
>
> Xuất phát từ bài toán thực tế: Giảng viên cần một công cụ chấm bài tự động chạy **nhanh, bảo mật và an toàn cục bộ**, nhưng vẫn tận dụng được sức mạnh của **Trợ lý AI trên đám mây**, kiến trúc hệ thống của chúng em được phân rã thành **3 phân hệ độc lập** với tính kết dính cao và độ phụ thuộc lỏng lẻo:
>
> 1. **Phân hệ 1 (Khối màu xanh lá):** *Sandbox Execution & Compiler Engine* — Động cơ biên dịch và thực thi mã nguồn an toàn trên máy cục bộ.
> 2. **Phân hệ 2 (Khối màu tím):** *Grading Core & Output Matching Subsystem* — Lõi nghiệp vụ chấm điểm hàng loạt và so khớp kết quả linh hoạt.
> 3. **Phân hệ 3 (Khối màu xanh dương):** *Central Backend & AI Gateway Subsystem* — Dịch vụ đám mây quản lý người dùng và điều tiết hạn ngạch gọi Google Gemini LLM.
>
> Đặc biệt, để đảm bảo tính mở rộng cao và tuân thủ các nguyên lý SOLID, nhóm đã áp dụng chuẩn mực **3 mẫu thiết kế Gang of Four (GoF)** gồm: *Factory Method*, *Adapter Pattern* và *Strategy Pattern*."*

---

### PHẦN 2: PHÂN HỆ 1 — SANDBOX EXECUTION & COMPILER ENGINE
* **Thời lượng:** ~1 phút 15 giây  
* **Thao tác trình chiếu:** Phóng to vào **Khối màu xanh lá**, chỉ vào `RunnerFactory`, `BaseRunner` và `CompilerAdapter`.

> 🗣️ **Lời thoại thuyết trình:**
>
> *"Đi vào phân hệ đầu tiên — **Local Engine**, mục tiêu hàng đầu là thực thi mã nguồn sinh viên mà không gây treo máy, đồng thời hỗ trợ đa ngôn ngữ (.c, .java, .py, web HTML/CSS/JS).
>
> Tại đây, nhóm áp dụng 2 Design Pattern quan trọng:
>
> **1. Creational Pattern — Factory Method:**
> * Lớp `RunnerFactory` cung cấp phương thức `get_runner(language)` cùng cơ chế đăng ký động `register_runner(language_key, runner_cls)`. Dựa trên ngôn ngữ của môn thi, nó sẽ tự động phân giải và khởi tạo đối tượng Runner tương ứng kế thừa từ `BaseRunner`: đó là `CRunner`, `JavaRunner`, hoặc `PythonRunner` (kết hợp dịch vụ chấm Web chuyên biệt `WebRubricEngine` ở tầng Services).
> * **Lợi ích kiến trúc:** Tuân thủ triệt để nguyên lý *Open/Closed (OCP)*. Khi nhà trường muốn bổ sung ngôn ngữ mới như C++ hay Rust, nhóm chỉ cần viết thêm class Runner mới và đăng ký vào Factory qua `register_runner` tại runtime mà không phải sửa đổi mã nguồn của tầng điều phối chấm bài.
>
> **2. Structural Pattern — Adapter Pattern:**
> * Trình biên dịch C (`gcc`) và Java (`javac`) có giao diện dòng lệnh (CLI flags) hoàn toàn khác nhau, và định dạng log lỗi `stderr` cũng không đồng nhất.
> * Nhóm đã xây dựng Interface `CompilerAdapter` cùng hai lớp hiện thực là `GccAdapter` và `JavacAdapter`. Hai Adapter này bọc các lệnh CLI hệ điều hành, phân tích cú pháp stderr và chuẩn hóa kết quả trả về thành một đối tượng đồng nhất duy nhất là `CompileResult`.
> * Nhờ vậy, `CRunner` và `JavaRunner` chỉ phụ thuộc vào Interface `CompilerAdapter` trừu tượng, tuân thủ nguyên lý *Dependency Inversion (DIP)*.
>
> **Về kiểm soát tài nguyên:** Lớp `ResourceMonitor` kết hợp với thư viện `psutil` để theo dõi PID tiến trình con. Nếu sinh viên viết vòng lặp vô tận vượt quá `time_limit_ms` hoặc tràn bộ nhớ `memory_limit_mb`, phương thức `enforce_kill_if_exceeded()` sẽ bắn lệnh ngắt tiến trình ngay lập tức, trả kết quả an toàn về `ExecutionResult`."*

---

### PHẦN 3: PHÂN HỆ 2 — GRADING CORE & OUTPUT MATCHING SUBSYSTEM
* **Thời lượng:** ~1 phút 15 giây  
* **Thao tác trình chiếu:** Chuyển con trỏ sang **Khối màu tím**, chỉ vào `GradingContext` và cây 7 nhánh của `MatchingStrategy`.

> 🗣️ **Lời thoại thuyết trình:**
>
> *"Tiếp theo là **Phân hệ 2: Lõi chấm điểm và so khớp đầu ra** tại ứng dụng Desktop.
>
> Tại đây, nhóm áp dụng mẫu thiết kế hành vi **Behavioral Pattern — Strategy Pattern** thông qua Interface `MatchingStrategy` cùng lớp ngữ cảnh `GradingContext`:
>
> * **Vấn đề thực tế:** Mỗi bài toán lập trình lại có tiêu chí so sánh đầu ra khác nhau. Có bài yêu cầu so khớp chính xác từng ký tự, có bài cho phép bỏ qua dấu cách thừa ở cuối dòng, có bài chấm số thực cho phép sai số $\epsilon = 10^{-6}$, hoặc kết quả là tập hợp không quan tâm thứ tự các từ.
> * **Giải pháp kiến trúc:** Nhóm đã đóng gói thuật toán so khớp thành **7 chiến lược độc lập**:
>   1. `ExactMatchStrategy`: So khớp chính xác 100%.
>   2. `IgnoreWhitespaceStrategy`: Tự động chuẩn hóa dấu cách và xuống dòng thừa.
>   3. `CaseInsensitiveStrategy`: Không phân biệt chữ hoa, chữ thường.
>   4. `FloatingPointToleranceStrategy`: So khớp sai số số thực với ngưỡng sai số `tolerance_epsilon`.
>   5. `UnorderedTokensStrategy`: Tách từ và so khớp tập hợp không phụ thuộc thứ tự xuất hiện.
>   6. `RegexPatternStrategy`: So khớp định dạng đầu ra dựa trên biểu thức chính quy.
>   7. `SpecialJudgeStrategy`: Ủy quyền cho một script Python/C bên ngoài chấm các bài toán đặc thù nhiều đáp án.
> * Lớp `GradingContext` nắm giữ một tham chiếu đến `MatchingStrategy`. Giảng viên có thể chuyển đổi thuật toán so khớp linh hoạt ngay tại thời điểm runtime thông qua hàm `set_strategy()`.
>
> **Về quản lý chấm hàng loạt:** Lớp `BatchGradingManager` quản lý một thread pool (`worker_pool_size`), nạp danh sách bài nộp từ CSV (`Submission`), nạp các bộ `TestCase`, yêu cầu `RunnerFactory` cấp Runner để chạy code, và tổng hợp kết quả chi tiết thành `GradingResult` hoặc `WebGradingResult` (đánh giá đa tiêu chí gồm DOM, Lint, Playwright E2E và AI Vision)."*

---

### PHẦN 4: PHÂN HỆ 3 — CENTRAL BACKEND & AI GATEWAY SUBSYSTEM
* **Thời lượng:** ~1 phút  
* **Thao tác trình chiếu:** Chuyển con trỏ sang **Khối màu xanh dương**, chỉ vào `QuotaManager` đứng trước `GeminiGatewayService`.

> 🗣️ **Lời thoại thuyết trình:**
>
> *"Phân hệ thứ 3 là **Central Backend** được xây dựng theo kiến trúc Service Layer / Facade trên nền tảng FastAPI:
>
> * `AuthController` kết hợp cùng `AuthService`: Chịu trách nhiệm xác thực người dùng bằng OAuth2 Password Flow và cấp phát/kiểm tra JWT Token an toàn.
> * `AIGatewayController` đóng vai trò là một **Facade Pattern** duy nhất đón nhận mọi yêu cầu liên quan đến AI từ Desktop: sinh TestCase biên (`generate_testcases`), giải thích lỗi sư phạm cho sinh viên (`review_code_error`), và kiểm tra đạo văn ngữ nghĩa (`check_plagiarism_semantic`).
> * **Điểm nhấn tối ưu chi phí & Quota:** API Google Gemini có giới hạn gọi và phát sinh chi phí. Vì vậy, nhóm thiết kế lớp `QuotaManager` chặn trước `GeminiGatewayService`. 
>   * Mỗi khi có request, `QuotaManager` sẽ kiểm tra hạn ngạch của giảng viên trong bảng `User` (`check_quota_available`).
>   * Chỉ khi còn hạn mức, hệ thống mới gọi ra ngoài Google Gemini. Sau khi xử lý xong, số token thực tế sẽ được ghi vết vào thực thể `AIQuotaLog` thông qua phương thức `consume_quota()`. Điều này giúp quản trị viên kiểm soát chi phí minh bạch và ngăn chặn tình trạng spam API."*

---

### PHẦN 5: GIAO TIẾP LIÊN PHÂN HỆ & LỜI KẾT
* **Thời lượng:** ~30 giây  
* **Thao tác trình chiếu:** Chỉ vào 2 mũi tên liên kết liên phân hệ ở phần dưới cùng của sơ đồ.

> 🗣️ **Lời thoại thuyết trình:**
>
> *"Cuối cùng, em xin làm rõ **cơ chế tương tác giữa các phân hệ**:
>
> * Quan sát ở cạnh dưới, `BatchGradingManager` gọi trực tiếp `BaseRunner` để chạy mã nguồn **hoàn toàn cục bộ (Offline)** trên máy giảng viên. Điều này đem lại 3 lợi thế vượt trội: tốc độ phản hồi tức thì, bảo mật tuyệt đối mã nguồn sinh viên, và không phát sinh chi phí duy trì server chấm thi đắt đỏ.
> * Ứng dụng Desktop chỉ thiết lập kết nối mạng HTTP RESTful tới `AIGatewayController` khi và chỉ khi giảng viên bấm nút yêu cầu Trợ lý AI hỗ trợ hoặc đồng bộ dữ liệu.
>
> Tổng kết lại, Sơ đồ lớp của AITA đã hiện thực hóa trọn vẹn yêu cầu nghiệp vụ với **3 Mẫu thiết kế chuẩn mực**, phân tách ranh giới rõ ràng giữa Local Engine và Cloud Service.
>
> Em xin chân thành cảm ơn Thầy/Cô và Hội đồng đã lắng nghe. Nhóm em rất mong nhận được câu hỏi phản biện từ Thầy/Cô ạ!"*

---

## 🛡️ BỘ CÂU HỎI PHẢN BIỆN TIỀM NĂNG TỪ HỘI ĐỒNG & ĐÁP ÁN CHUẨN MỰC

> [!TIP]
> Hãy nắm vững các câu trả lời dưới đây để ghi điểm tối đa phần phản biện kiến trúc.

### ❓ Câu hỏi 1: Tại sao ở Phân hệ 1 lại cần cả Factory Method lẫn Adapter Pattern mà không gộp chung vào Runner?
* **Đáp án chuẩn mực:**
  > *"Dạ thưa Thầy/Cô, việc tách riêng tuân thủ nghiêm ngặt nguyên lý **Single Responsibility Principle (SRP)**:
  > * `RunnerFactory` chỉ chịu trách nhiệm **Creational** (Khởi tạo): Quyết định *loại đối tượng nào* được tạo ra dựa trên định dạng tệp (.c, .java, .py).
  > * `CompilerAdapter` giải quyết bài toán **Structural** (Cấu trúc): Chuẩn hóa sự bất tương thích về cờ lệnh CLI và định dạng stderr của các trình biên dịch khác nhau (`gcc` vs `javac`).
  > * Nếu gộp thẳng lệnh `gcc` hay `javac` vào trong `CRunner` hay `JavaRunner`, khi trình biên dịch thay đổi phiên bản hoặc đổi cờ tối ưu hóa (như `-O2`, `-std=c11`), chúng ta sẽ buộc phải sửa đổi mã nguồn của lớp Runner vốn đang làm nhiệm vụ điều phối luồng chạy. Việc tách Adapter giúp Runner chỉ cần gọi phương thức `compile()`, hoàn toàn độc lập với chi tiết biên dịch bên dưới."*

---

### ❓ Câu hỏi 2: Phân biệt quan hệ giữa `BatchGradingManager` với `GradingContext` (Composition `*--`) và `GradingContext` với `MatchingStrategy` (Aggregation `o--`)?
* **Đáp án chuẩn mực:**
  > *"Dạ thưa Thầy/Cô:
  > * `BatchGradingManager *-- GradingContext` là quan hệ **Composition (Sở hữu chặt - Vòng đời phụ thuộc)**: `GradingContext` là thành phần cốt lõi của một phiên chấm điểm hàng loạt. Khi phiên chấm `BatchGradingManager` kết thúc và bị hủy bỏ khỏi bộ nhớ, đối tượng `GradingContext` đi kèm cũng sẽ bị hủy theo.
  > * `GradingContext o-- MatchingStrategy` là quan hệ **Aggregation (Sở hữu lỏng - Tham chiếu độc lập)**: `GradingContext` chỉ giữ một con trỏ tham chiếu đến chiến lược hiện tại. Chiến lược này có thể thay đổi linh hoạt lúc runtime qua hàm `set_strategy()`, và vòng đời của các lớp Strategy hoàn toàn độc lập với Context."*

---

### ❓ Câu hỏi 3: Nếu sinh viên cố tình viết mã độc hại như gọi `system("rmdir /s /q C:\\")` hoặc vòng lặp `while(true)`, hệ thống xử lý ra sao trong sơ đồ này?
* **Đáp án chuẩn mực:**
  > *"Dạ thưa Thầy/Cô:
  > 1. **Đối với vòng lặp vô tận hoặc ngốn RAM:** Lớp `BaseRunner` sở hữu phương thức `monitor_resources()` liên kết với `ResourceMonitor`. Khi tiến trình con được spawn qua `subprocess`, `ResourceMonitor` sẽ khởi chạy một luồng giám sát PID bằng `psutil`. Nếu thời gian thực thi vượt quá `time_limit_ms` hoặc RAM vượt quá `memory_limit_mb`, hàm `enforce_kill_if_exceeded()` sẽ bắn tín hiệu SIGKILL/Terminate ngay lập tức và trả cờ `is_timeout = true` về đối tượng `ExecutionResult`.
  > 2. **Đối với lệnh phá hoại hệ thống:** Quá trình thực thi diễn ra trong thư mục cách ly `scratch/` với quyền người dùng hạn chế (Restricted Subprocess), đồng thời hệ thống có thể kết hợp regex kiểm tra các lời gọi hàm nguy hiểm trước khi cho phép biên dịch."*

---

### ❓ Câu hỏi 4: Tại sao không đưa toàn bộ việc chấm bài lên Cloud Backend mà lại chia thành Local Desktop và Cloud AI Gateway?
* **Đáp án chuẩn mực:**
  > *"Dạ thưa Thầy/Cô, đây là quyết định kiến trúc mang tính chiến lược của nhóm dựa trên 3 yếu tố:
  > 1. **Chi phí hạ tầng:** Chấm hàng trăm bài nộp C/Java/Python đòi hỏi máy chủ Cloud cấu hình CPU/RAM cực lớn và container cô lập phức tạp, dẫn đến chi phí duy trì rất cao.
  > 2. **Tính sẵn sàng & Tốc độ:** Giảng viên thường chấm bài tại phòng thi hoặc phòng lab trường học. Chạy cục bộ giúp tận dụng tối đa CPU của máy giảng viên, tốc độ phản hồi tức thì và không bị nghẽn mạng do upload hàng loạt file zip nặng.
  > 3. **Ranh giới trách nhiệm rõ ràng:** Cloud Backend chỉ tập trung vào việc quản lý tài khoản và làm cổng trung gian điều tiết AI Gemini có tính phí, giữ cho backend luôn nhẹ, an toàn và dễ bảo trì."*

---

## 🎯 DANH SÁCH TỪ KHÓA CHUYÊN NGÀNH CẦN DÙNG TRONG BÁO CÁO
*(Sử dụng các từ khóa này giúp bài báo cáo đạt điểm chuyên nghiệp cao nhất)*

* **High Cohesion, Loose Coupling** (Độ gắn kết cao, độ phụ thuộc thấp)
* **Single Responsibility Principle - SRP** (Nguyên lý đơn trách nhiệm)
* **Open/Closed Principle - OCP** (Nguyên lý mở rộng nhưng đóng với sửa đổi)
* **Dependency Inversion Principle - DIP** (Nguyên lý đảo ngược phụ thuộc)
* **Gang of Four (GoF) Design Patterns** (Factory Method, Adapter, Strategy)
* **Runtime Polymorphism** (Đa hình lúc thực thi)
* **Process Isolation & Resource Capping** (Cách ly tiến trình & Giới hạn tài nguyên)
* **Facade & Service Layer Pattern** (Kiến trúc tầng dịch vụ và cổng giao tiếp đồng nhất)
