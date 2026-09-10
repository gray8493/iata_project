# Nhật Ký Ghi Nhận Sử Dụng AI (AI Prompts & Usage Log)
## Giai đoạn: Evaluation 1 - Requirement Analysis & Modeling (SWD392)
## Dự án: AITA - Automated Grading Tool for Instructors

Tài liệu này ghi nhận minh bạch toàn bộ các câu Prompt và kết quả hỗ trợ từ AI được sử dụng trong giai đoạn 1, tuân thủ tiêu chí đánh giá **AI Evaluation Rubric (Transparency, Understanding & Customization)** của môn học SWD392.

---

## 1. Thông Tin Chung

- **Công cụ AI sử dụng**: Antigravity AI Assistant / ChatGPT / Google Gemini
- **Người thực hiện**: Nhóm phát triển dự án AITA
- **Mục đích**: Hỗ trợ phân tích yêu cầu, xây dựng kiến trúc thư mục, chuẩn hóa quy trình làm việc nhóm và thiết lập mẫu kịch bản kiểm thử.

---

## 2. Nhật Ký Chi Tiết Các Prompt Đã Sử Dụng

---

### 🔹 PROMPT 01: Thiết Kế Khung Thư Mục Dự Án Desktop App Chuyên Nghiệp

#### 1. Mục tiêu
Nhờ AI tư vấn và thiết kế bộ khung thư mục chuẩn cho một ứng dụng máy tính (Desktop App) có quy mô vừa và lớn, bao quát đầy đủ phần mã nguồn, kiểm thử đa tầng và tài liệu kỹ thuật.

#### 2. Câu Prompt đã gửi
> *"Gợi ý cho tôi các thư mục khi làm một dự án desktop app, có một phần để document nữa các tài liệu thiết kế, các testcase, file puml, yaml; code nằm ở đâu, testing thì có nhiều loại và design cũng có nhiều design cho từng API. Tôi chỉ cần danh sách thư mục trước."*

#### 3. Kết quả do AI sinh ra (AI Output)
AI đã đề xuất cây thư mục phân tầng gồm:
- `docs/`: Chứa `architecture/`, `apis/` (chia theo từng API), `diagrams/puml/`, `testcases/` (chia 4 cấp độ: unit, integration, system, acceptance).
- `src/`: Tổ chức theo Feature-based (`app/`, `core/`, `features/`, `shared/`).
- `tests/`: Phân tầng kiểm thử hệ thống (`unit/`, `integration/`, `system/`, `acceptance/`, `e2e/`, `performance/`).
- `assets/` và `build/`: Quản lý tài nguyên icon, hình ảnh và script đóng gói `.exe`.

#### 4. Giải trình & Tinh chỉnh của Nhóm (Team Justification & Customization)
- **Điểm nhóm hiểu và đồng ý**: Cách tổ chức phân tầng rõ rệt giữa tài liệu (`docs/`) và code thật (`src/`) giúp các thành viên làm việc độc lập mà không bị giẫm chân nhau.
- **Tinh chỉnh của nhóm**: 
  - Tạo thêm thư mục `rules/` tại root để lưu trữ toàn bộ quy chuẩn làm việc nhóm.
  - Tạo thư mục `docs/ai-prompts/` để lưu vết prompt theo đúng yêu cầu đề bài SWD392.
  - Tự động chèn các file `.gitkeep` vào tất cả các thư mục con rỗng để Git có thể theo dõi và đẩy lên GitHub.

---

### 🔹 PROMPT 02: Thiết Lập Quy Chuẩn Đặt Tên Nhánh Git & Quy Tắc Khóa Nhánh Master

#### 1. Mục tiêu
Chuẩn hóa cách đặt tên nhánh Git cho 4-5 thành viên trong nhóm và thiết lập kỷ luật nghiêm ngặt: không commit/push trực tiếp vào nhánh `master`.

#### 2. Câu Prompt đã gửi
> *"Tạo rule với dự án cách đặt tên nhánh: docs-tên api-tên người tạo, code-features gì-tên, test-level nào-tên, và rule không commit vào nhánh master."*

#### 3. Kết quả do AI sinh ra (AI Output)
AI đã tạo tài liệu [rules/git-rules.md](file:///e:/AITA/rules/git-rules.md) bao gồm:
- 3 cấu trúc nhánh chuẩn: `docs-<api>-<tên>`, `code-<feature>-<tên>`, `test-<level>-<tên>`.
- Quy chuẩn chữ thường, không dấu, ngăn cách bằng dấu gạch ngang `-`.
- Quy tắc vàng cấm commit trực tiếp lên `master`, bắt buộc tuân theo quy trình 4 bước qua **Pull Request (PR)** có người duyệt trước khi merge.
- Hướng dẫn cài đặt Branch Protection trên GitHub repository.

#### 4. Giải trình & Tinh chỉnh của Nhóm (Team Justification & Customization)
- **Đánh giá của nhóm**: Quy tắc này giúp bảo vệ nhánh `master` luôn ổn định để giảng viên vào chấm bài, đồng thời thể hiện kỹ năng làm việc nhóm chuyên nghiệp trong đồ án. Nhóm quyết định áp dụng 100% quy tắc này vào dự án.

---

### 🔹 PROMPT 03: Phân Tích Tổng Quan Hệ Thống Tool Chấm Điểm AITA Cho Giảng Viên

#### 1. Mục tiêu
Xây dựng tài liệu kiến trúc tổng quan mô tả chính xác nghiệp vụ của công cụ Desktop App chấm điểm bài tập sinh viên cho giảng viên các môn lập trình nền tảng.

#### 2. Câu Prompt đã gửi
> *"Tạo một file overview: dự án này chúng tôi làm cho giảng viên một desktopApp tool để chấm điểm các môn học về cơ sở lập trình như cấu trúc dữ liệu giải thuật (python, java), lập trình hướng đối tượng, lập trình cơ sở (C), lập trình python. Yêu cầu tool chấm điểm khi nhận file đã build so với testcase và trả kết quả. Cho phép import file excel có thông tin MSSV, tên sinh viên, file bài làm để xử lý nhiều sinh viên cùng lúc."*

#### 3. Kết quả do AI sinh ra (AI Output)
AI đã biên soạn tài liệu [docs/architecture/system-overview.md](file:///e:/AITA/docs/architecture/system-overview.md) mô tả toàn diện:
- Phạm vi 4 môn học: C, Java, Python, DSA, OOP.
- Quy trình chấm điểm khép kín 5 bước: Import Excel danh sách lớp ➔ Tự động ánh xạ (Auto-mapping) theo MSSV ➔ Nạp testcase ➔ Chấm song song đa tiến trình (Parallel Batch Runner) ➔ Xuất bảng điểm Excel hoàn chỉnh.
- Hệ thống mã lỗi chuẩn: `AC`, `WA`, `TLE` (quá giờ), `MLE` (tràn RAM), `CE` (lỗi biên dịch), `RE` (lỗi runtime).
- Ứng dụng AI Gemini: Tự động sinh testcase biên, phân tích mã lỗi và viết nhận xét sư phạm điền thẳng vào cột Excel của từng sinh viên.
- Áp dụng 3 Design Patterns bắt buộc của đề bài: Factory Method (`RunnerFactory`), Strategy Pattern (`MatchingStrategy`), Adapter Pattern (`CompilerAdapter`).

#### 4. Giải trình & Tinh chỉnh của Nhóm (Team Justification & Customization)
- **Lý do nhóm tích hợp AI thay vì dùng web ngoài**: Tích hợp trực tiếp giúp tự động hóa khép kín (nhận xét hàng loạt 50 bài nộp điền thẳng vào Excel trong 1 click), cơ chế tự kiểm định testcase bằng Code chuẩn của giảng viên, và quan trọng nhất là đáp ứng tiêu chí 30% Integrated Demo của môn học SWD392.

---

### 🔹 PROMPT 04: Chuẩn Hóa Ngăn Xếp Công Nghệ (Python, SQLite, Gemini)

#### 1. Mục tiêu
Xác định công nghệ cụ thể và các thư viện bên thứ ba đảm nhiệm từng tính năng của Desktop App.

#### 2. Câu Prompt đã gửi
> *"Tạo file công nghệ sử dụng gồm python, các thư viện python, SQLite, gemini."*

#### 3. Kết quả do AI sinh ra (AI Output)
AI đã tạo tài liệu [docs/architecture/tech-stack.md](file:///e:/AITA/docs/architecture/tech-stack.md) chi tiết:
- Ngôn ngữ: Python 3.11+; GUI: PySide6 / PyQt6.
- Thư viện: `psutil` (giám sát RAM/CPU, bắt TLE/MLE), `subprocess` (chạy gcc, java, python), `openpyxl`/`pandas` (đọc/ghi file Excel bảng điểm), `pathlib`/`zipfile` (quản lý bài nộp).
- Database: SQLite3 cục bộ (bảng lớp, sinh viên, testcase, kết quả).
- AI: Google Gemini API (`google-generativeai`).
- Đóng gói: `PyInstaller` ra 1 file `.exe` duy nhất cho Windows.

#### 4. Giải trình & Tinh chỉnh của Nhóm (Team Justification & Customization)
- **Đánh giá của nhóm**: Python và SQLite là sự kết hợp hoàn hảo cho ứng dụng Desktop Offline-first. Nhóm lựa chọn mô hình `gemini-1.5-flash` vì tốc độ phản hồi dưới 1 giây và chi phí token cực thấp.

---

### 🔹 PROMPT 05: Chuẩn Hóa Cấu Trúc Kịch Bản Kiểm Thử (Unit Test Specification)

#### 1. Mục tiêu
Quy định mẫu kịch bản kiểm thử đơn vị đồng nhất cho tất cả các thành viên trong nhóm, đảm bảo tính chuyên nghiệp theo tiêu chuẩn kiểm thử phần mềm.

#### 2. Câu Prompt đã gửi
> *"Tạo file unit test mẫu MD gồm có API nào, ai làm, ngày làm, update lần cuối, tài liệu liên quan, bao nhiêu testcase. Trình bày theo hàng dọc không theo bảng. Chỗ rule thêm quy tắc đặt tên testcase UT01_API gì TC001 tên testcase luôn. Gồm có pre-condition, test step, expected result và một bảng để lưu kết quả test. Bỏ mô tả đi, tất cả mục nâng lên H4."*

#### 3. Kết quả do AI sinh ra (AI Output)
AI đã triển khai:
- File quy tắc riêng [rules/testcase-rules.md](file:///e:/AITA/rules/testcase-rules.md) quy định cú pháp mã định danh và cấu trúc khối.
- File kịch bản mẫu [docs/testcases/1-unit/unit-test-template.md](file:///e:/AITA/docs/testcases/1-unit/unit-test-template.md) với:
  - Tiêu đề Heading 1: `# UT01_MatchingStrategy_TC001: Khớp chính xác hoàn toàn (Exact Match)`.
  - Các mục con dạng H4: `#### Loại test`, `#### Tiền điều kiện (Pre-condition)`, `#### Các bước thực hiện (Test Steps)`, `#### Kết quả kỳ vọng (Expected Result)`.
  - Bảng kết quả kiểm thử (Execution Result Table) ghi lại lần test, ngày test, người test, kết quả thực tế, thời gian ms và trạng thái Pass/Fail.

#### 4. Giải trình & Tinh chỉnh của Nhóm (Team Justification & Customization)
- **Lý do nhóm yêu cầu đổi từ bảng ngang sang hàng dọc**: Khi viết dữ liệu input/output phức tạp của các bài tập lập trình, việc viết trong bảng ngang rất khó đọc và dễ vỡ giao diện Markdown. Chuyển sang hàng dọc giúp từng kịch bản rõ ràng, mạch lạc và dễ bổ sung các lần test sau này.

---

### 🔹 PROMPT 06: Tinh Chỉnh Nghiệp Vụ Thực Tế Của Giảng Viên & Mở Rộng Strategy Pattern

#### 1. Mục tiêu
Tối ưu hóa các thao tác thực tế của giảng viên (đơn giản hóa định dạng file Excel đầu vào, nạp testcase linh hoạt, chọn GUI PyQt6/PySide6) và làm sâu sắc thêm mô hình thiết kế Strategy Pattern với 7 chế độ so khớp.

#### 2. Câu Prompt đã gửi
> *"Giảng viên import file excel gồm có mssv và file thôi. Testcase cho phép input bằng tay và file json. Chọn PyQt6 / PySide6. Nêu cho tôi các steps bạn nghĩ một giáo viên sẽ thực hiện. Bước 4: Chọn chế độ so khớp (Matching Options) chỗ nào thì xử lý như thế nào, phải nhiều kiểu chứ?"*

#### 3. Kết quả do AI sinh ra (AI Output)
AI đã hoàn thiện thiết kế chi tiết:
- Đơn giản hóa file Excel đầu vào đúng **2 cột cốt lõi**: `MSSV` và `File`.
- Cho phép nạp Testcase linh hoạt cả 2 hình thức: **Nhập trực tiếp trên GUI** VÀ **Import/Export file JSON** (`testcases.json`).
- Chốt sử dụng **PyQt6 / PySide6** làm GUI Framework chính.
- Xây dựng quy trình **8 bước tuần tự của Giảng viên** chia thành 4 giai đoạn rõ ràng.
- Mở rộng **Strategy Pattern thành 7 chế độ so khớp chuyên nghiệp**: *Exact Match, Ignore Whitespace, Case-Insensitive, Float Tolerance, Unordered Match, Regex Pattern Match, Special Judge (Custom Checker)*.

#### 4. Giải trình & Tinh chỉnh của Nhóm (Team Justification & Customization)
- **Đánh giá của nhóm**: Việc mở rộng ra 7 chế độ so khớp giải quyết triệt để các bài toán thực tế của sinh viên (không bị chấm sai oan khi thừa khoảng trắng, làm tròn số thực hoặc bài toán có nhiều đáp án). Đây là minh chứng mẫu mực cho việc nhóm hiểu sâu và làm chủ (Mastery) mẫu thiết kế **Strategy Pattern** trong đề bài môn SWD392.

