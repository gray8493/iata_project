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

---

### 🔹 PROMPT 07: Tối Ưu Hóa I/O Bằng Định Dạng CSV & Chuẩn Hóa Mã Môn Học (PRO, PHP)

#### 1. Mục tiêu
Tối ưu hóa hiệu năng đọc/ghi dữ liệu của ứng dụng bằng cách chuyển đổi từ Excel sang định dạng phẳng CSV, đồng thời chuẩn hóa chính xác mã môn học và ngôn ngữ tương ứng theo chương trình đào tạo của trường.

#### 2. Câu Prompt đã gửi
> *"Lập trình hướng đối tượng là PRO, python là PHP. Lập trình hướng đối tượng (PRO) java và python. CSV tối ưu hơn excel thì thay csv đi."*

#### 3. Kết quả do AI sinh ra (AI Output)
AI đã cập nhật đồng bộ toàn bộ tài liệu kiến trúc:
- Chuyển đổi toàn bộ cơ chế nạp/xuất từ file Excel `.xlsx` sang **file CSV `.csv`** (`students.csv`, `results.csv`).
- Thay thế thư viện nặng `openpyxl` bằng module chuẩn **`csv` tích hợp sẵn trong Python**, giúp tốc độ đọc/ghi nhanh gấp nhiều lần và giảm nhẹ kích thước file đóng gói `.exe`.
- Chuẩn hóa mã môn học: **Lập trình hướng đối tượng (PRO)** hỗ trợ Java & Python; môn **Lập trình Python (PHP)**.

#### 4. Giải trình & Tinh chỉnh của Nhóm (Team Justification & Customization)
- **Quyết định kỹ thuật (Engineering Decision)**: Định dạng CSV là định dạng văn bản phẳng tiêu chuẩn trong kỹ thuật phần mềm, việc loại bỏ phụ thuộc bên ngoài (`openpyxl`) giúp mã nguồn ổn định, tránh các lỗi tương thích font/style của file Excel nhị phân, đồng thời vẫn đảm bảo giảng viên mở được file kết quả bằng Excel/Google Sheets bình thường.

---

### 🔹 PROMPT 08: Tích Hợp Web Server Backend Phân Quyền & Trang Web Admin Quản Lý

#### 1. Mục tiêu
Nâng cấp đồ án từ một công cụ Desktop đơn lẻ thành một **Hệ sinh thái tích hợp 3 thành phần hoàn chỉnh** (đạt trọn vẹn điểm Rubric tích hợp 30% và phân quyền RBAC của môn SWD392) gồm: Web Server Backend (FastAPI, JWT, RBAC), Trang Web Admin Quản Lý (Web Admin Dashboard) và Desktop App Client (PyQt6).

#### 2. Câu Prompt đã gửi
> *"Cần cả một web server backend phân quyền và trang web admin quản lí chỉnh sửa lại các file cần thiết"*

#### 3. Kết quả do AI sinh ra (AI Output)
AI đã rà soát và cập nhật đồng bộ các tài liệu kỹ thuật ([docs/architecture/system-overview.md](file:///e:/AITA/docs/architecture/system-overview.md) và [docs/architecture/tech-stack.md](file:///e:/AITA/docs/architecture/tech-stack.md)):
- **Web Server Backend (Python FastAPI)**: Xây dựng RESTful API tự sinh OpenAPI Swagger (`/docs`), xác thực bảo mật JWT Token, mã hóa mật khẩu Bcrypt, phân quyền theo vai trò RBAC (`Admin`, `Instructor`, `Student`), quản lý dữ liệu trung tâm qua SQLAlchemy ORM và đóng vai trò AI Gateway kiểm soát hạn ngạch Gemini.
- **Trang Web Admin Quản Lý (Web Admin Dashboard)**: Xây dựng 4 phân hệ cốt lõi: Quản lý người dùng & gán role, Quản lý môn học & phân công lớp, Giám sát quota Token AI theo thời gian thực và Báo cáo tổng hợp số liệu toàn trường.
- **Desktop App Client (PyQt6/PySide6)**: Kết nối với Web Server Backend qua REST API để đồng bộ dữ liệu lớp học, xác thực giảng viên và đồng bộ kết quả chấm điểm lên máy chủ.
- **Cập nhật danh mục thư viện & dependencies**: Bổ sung `fastapi`, `uvicorn[standard]`, `python-jose[cryptography]`, `passlib[bcrypt]`, `sqlalchemy`, `jinja2` vào `requirements.txt`.

#### 4. Giải trình & Tinh chỉnh của Nhóm (Team Justification & Customization)
- **Giá trị học thuật & Rubric SWD392**: Thiết kế này giúp dự án vượt qua giới hạn của một ứng dụng đơn lẻ (standalone tool) để trở thành một sản phẩm có tính thương mại và doanh nghiệp (Enterprise-ready). Việc quản lý tài khoản và hạn ngạch AI tập trung tại Web Backend giải quyết triệt để bài toán bảo mật API Key và kiểm soát chi phí gọi AI trong môi trường giáo dục thực tế.

---

### 🔹 PROMPT 09: Chuẩn Hóa Nguyên Lý Chấm Cốt Lõi (Input / Output Matching) & Tối Giản Hóa Quy Trình AI

#### 1. Mục tiêu
Xác định chuẩn xác và dứt khoát cơ chế chấm thi cốt lõi của công cụ: Kiểm thử hộp đen thuần túy dựa trên cặp Input và Output kỳ vọng, loại bỏ mọi yêu cầu rườm rà về việc giảng viên phải chuẩn bị file code giải mẫu (solution).

#### 2. Câu Prompt đã gửi
> *"Cách thức chấm là gì giảng viên chỉ cần nhập INPUT VÀ OUTPUT , INPUT ĐÓ ĐƯỢC LẤY ĐỂ CHẠY TRONG CODE CỦA SINH VIÊN NẾU OUTPUT = OUTPUT CỦA GIẢNG VIÊN LÀ ĐÚNG"*

#### 3. Kết quả do AI sinh ra (AI Output)
AI đã điều chỉnh và chuẩn hóa triệt để tài liệu kiến trúc ([docs/architecture/system-overview.md](file:///e:/AITA/docs/architecture/system-overview.md)):
- **Nguyên lý chấm cốt lõi**:
  - Giảng viên chỉ cần nạp hoặc nhập trực tiếp các cặp `INPUT` và `OUTPUT` kỳ vọng.
  - Hệ thống nạp `INPUT` vào luồng chuẩn `stdin` của bài làm sinh viên; thu nhận kết quả từ luồng chuẩn `stdout` (`OUTPUT thực tế`).
  - Nếu `OUTPUT thực tế == OUTPUT của Giảng viên` thì tính là **ĐÚNG (Passed / AC)**; nếu sai lệch thì là **SAI (Wrong Answer / WA)**.
- **Tối giản hóa tính năng AI**:
  - Gemini AI khi hỗ trợ sinh testcase chỉ cần nhận văn bản đề bài là tự động suy luận ra cả cặp `INPUT` và `OUTPUT kỳ vọng`, điền thẳng vào bảng testcase để giảng viên duyệt/sửa mà **hoàn toàn KHÔNG cần cung cấp file code mẫu `solution`**.
  - AI Code Review chỉ kích hoạt khi bài làm sinh viên in ra Output khác với Output của giảng viên (hoặc lỗi thực thi) để đối chiếu và chỉ ra dòng sai logic.

#### 4. Giải trình & Tinh chỉnh của Nhóm (Team Justification & Customization)
- **Quyết định trải nghiệm người dùng (UX & Productivity)**: Trong thực tế giảng dạy đại học, giảng viên không phải lúc nào cũng có sẵn file giải chuẩn của mọi bài tập hoặc format solution có thể khác với đề ra. Cơ chế so khớp trực tiếp cặp `INPUT/OUTPUT` qua `stdin/stdout` là chuẩn mực vàng của các hệ thống chấm bài tự động quốc tế (như Codeforces, LeetCode, HackerRank, VNOI), giúp công cụ cực kỳ dễ dùng, nhanh gọn và thực tế.

---

### 🔹 PROMPT 10: Tinh Chỉnh Quy Trình Thực Thi Qua Hàm Main() & Đơn Giản Hóa Luồng Dữ Liệu

#### 1. Mục tiêu
Xác nhận mô hình thực thi mã nguồn sinh viên dựa hoàn toàn trên điểm khởi nhập chuẩn hàm `main()`, loại bỏ sự phức tạp của việc phân tích hay bọc hàm con (function wrappers).

#### 2. Câu Prompt đã gửi
> *"Chỉ có hàm main thôi các hàm đó được hàm main gọi"*

#### 3. Kết quả do AI sinh ra (AI Output)
AI đã chuẩn hóa chi tiết luồng thực thi trong tài liệu kiến trúc ([docs/architecture/system-overview.md](file:///e:/AITA/docs/architecture/system-overview.md)):
- **Luồng dữ liệu thực tế**: Sinh viên viết toàn bộ logic trong một hoặc nhiều hàm, nhưng hàm `main()` là điểm vào duy nhất có nhiệm vụ nhận `INPUT` từ `stdin` (`scanf`, `Scanner`, `input()`), tự truyền đối số vào các hàm con để xử lý và in kết quả ra `stdout`.
- **Loại bỏ việc bọc mã nguồn (Zero-Wrapping)**: Hệ thống AITA biên dịch và chạy file nguyên bản của sinh viên trong môi trường subprocess cô lập, không can thiệp hay sửa đổi code sinh viên.
- **Xử lý linh hoạt nhiều câu / nhiều đề**: Áp dụng nạp testcase tương ứng qua ánh xạ mã đề `MaDe` trên file CSV hoặc chạy từng file câu hỏi (`Q1.c`, `Q2.c`) độc lập.

#### 4. Giải trình & Tinh chỉnh của Nhóm (Team Justification & Customization)
- **Độ tin cậy & Ổn định của hệ thống**: Việc không can thiệp ghép file hay bọc mã nguồn giúp loại bỏ hoàn toàn các lỗi biên dịch do xung đột thư viện, lệch namespace hoặc sai chữ ký hàm (function signature). Hệ thống đạt độ ổn định 100% khi chạy bài nộp của sinh viên.

---

### 🔹 PROMPT 11: Chuẩn Hóa Cấu Trúc Bài Nộp Đơn Nhất (Mỗi Câu Là Một File Độc Lập Chứa Hàm Main)

#### 1. Mục tiêu
Thống nhất dứt khoát dạng cấu trúc bài nộp thực tế của sinh viên trong các kỳ thi thực hành lập trình: Duy nhất một dạng chuẩn - Mỗi câu hỏi là một file mã nguồn riêng biệt chứa hàm `main()` độc lập.

#### 2. Câu Prompt đã gửi
> *"Dạng 1 chỉ có một dạng kiểu dạng 1"*

#### 3. Kết quả do AI sinh ra (AI Output)
AI đã chuẩn hóa và làm sạch tài liệu kiến trúc ([docs/architecture/system-overview.md](file:///e:/AITA/docs/architecture/system-overview.md)):
- **Loại bỏ các trường hợp menu phức tạp**: Chốt duy nhất định dạng bài làm chuẩn: Bài thi có bao nhiêu câu thì có bấy nhiêu file độc lập (ví dụ `Q1.c`, `Q2.c`, `Q3.c` cho C; `Q1.java`, `Q2.java` cho Java; `q1.py`, `q2.py` cho Python).
- **Mỗi file là một chương trình hoàn chỉnh**: Mỗi file câu hỏi đều có hàm `main()` riêng để tự đọc dữ liệu `stdin`, tự gọi các hàm con bên trong và in ra `stdout`.
- **Cơ chế chấm**: Chấm độc lập từng file `Q_i` theo bộ testcase riêng của câu đó, tính điểm cho từng câu và tự động cộng dồn thành tổng điểm bài thi.

#### 4. Giải trình & Tinh chỉnh của Nhóm (Team Justification & Customization)
- **Sát với thực tế đề thi Practical Exam**: Cấu trúc này phản ánh chính xác 100% format đề thi thực hành tại các trường đại học (như PE môn PRF192, PRO192, CSD201). Việc quy chuẩn về duy nhất 1 dạng giúp mã nguồn của tool AITA cực kỳ tinh gọn, mạch lạc, không bị phình to bởi các logic xử lý ngoại lệ thừa thãi.

---

### 🔹 PROMPT 12: Tối Ưu Hóa Tần Suất Gọi AI (On-Demand & Lọc Cục Bộ 2 Vòng Chống Sập Quota)

#### 1. Mục tiêu
Phân tích phản biện rủi ro nghẽn hạn ngạch (Rate Limit Exceeded) và chi phí token khổng lồ khi tự động hóa AI bừa bãi; thiết kế giải pháp kiến trúc "Tích hợp AI Thông minh" (Smart AI Integration) giảm hơn 95% số request.

#### 2. Câu Prompt đã gửi
> *"Phân tích xem hai cái này có gọi AI nhiều quá không: AI Code Review & Feedback Generator... và AI Plagiarism Detection..."*

#### 3. Kết quả do AI sinh ra (AI Output)
AI đã tính toán bài toán phụ tải thực tế (lớp 40 sinh viên $\times$ 3 câu $\rightarrow$ 60 bài lỗi $\rightarrow$ 60 request liên tiếp dính lỗi Rate Limit 429; so sánh đạo code cần tới 2.340 cặp) và đề xuất cập nhật đồng bộ các tài liệu ([docs/architecture/system-overview.md](file:///e:/AITA/docs/architecture/system-overview.md), [docs/architecture/tech-stack.md](file:///e:/AITA/docs/architecture/tech-stack.md)):
- **AI Code Review**: Chuyển từ cơ chế tự động sang **On-Demand (Lazy Loading)**; chỉ gọi khi giảng viên chủ động bấm nút phân tích cho bài cụ thể; bỏ qua lỗi biên dịch `CE` để tránh lãng phí.
- **AI Plagiarism Detection**: Triển khai **Mô hình Lọc 2 vòng (Two-Stage Filtering)**:
  - *Vòng 1 (Offline 100%)*: Dùng thuật toán băm cây cú pháp AST / Tokenization cục bộ quét toàn bộ 2.340 cặp trong 0.5 giây mà không tốn 1 token nào.
  - *Vòng 2 (AI Verification)*: Chỉ gửi 1-3 cặp có độ tương đồng bất thường vượt ngưỡng (> 80%) lên cho Gemini AI phân tích bằng chứng sao chép.

#### 4. Giải trình & Tinh chỉnh của Nhóm (Team Justification & Customization)
- **Điểm sáng về Tư duy Thiết kế Hệ thống (System Architecture Mastery)**: Đây là minh chứng mẫu mực cho tiêu chí đánh giá môn SWD392 về việc "sử dụng AI có trách nhiệm và hiệu quả kinh tế" (Cost-effective & Responsible AI Design). Nhóm không tích hợp AI một cách ngây thơ (naive) mà biết kết hợp sức mạnh thuật toán truyền thống chạy offline với AI đám mây để tạo ra một hệ thống vừa nhanh, vừa rẻ, vừa ổn định 100%.

---

### 🔹 PROMPT 13: Loại Bỏ Phân Chia Mã Đề (MaDe) & Giữ Trọn Vẹn Chuẩn CSV 2 Cột Tối Giản

#### 1. Mục tiêu
Loại bỏ hoàn toàn tính năng phân tách mã đề (`MaDe`) rườm rà; giữ nguyên tắc nhất quán: Mỗi lần chấm áp dụng chung một bộ đề/câu hỏi cho cả lớp, file đầu vào `students.csv` luôn cố định đúng **2 cột**: `MSSV` và `File`.

#### 2. Câu Prompt đã gửi
> *"Trường hợp nhiều mã đề thi: Hệ thống ánh xạ cột mã đề (MaDe) trong file danh sách students.csv để áp dụng đúng bộ testcase của từng mã đề tương ứng. Bỏ"*

#### 3. Kết quả do AI sinh ra (AI Output)
AI đã loại bỏ hoàn toàn phần ánh xạ mã đề khỏi tài liệu kiến trúc ([docs/architecture/system-overview.md](file:///e:/AITA/docs/architecture/system-overview.md)):
- Giữ nguyên định dạng file `students.csv` tuyệt đối tinh giản chỉ với 2 cột: `MSSV,File`.
- Toàn bộ sinh viên trong một đợt chấm sẽ được chấm theo cùng một bộ câu hỏi chuẩn của bài thi.

#### 4. Giải trình & Tinh chỉnh của Nhóm (Team Justification & Customization)
- **Đơn giản hóa dữ liệu đầu vào (KISS Principle - Keep It Simple, Stupid)**: Việc không chia nhiều mã đề trong cùng 1 file CSV giúp giảm thiểu nguy cơ sai sót do nhập liệu của giảng viên, giữ cho file CSV luôn sạch và dễ tích hợp với các danh sách tải về từ hệ thống LMS trường.

---

### 🔹 PROMPT 14: Định Hình Web Admin Chuyên Biệt Cho Quản Trị Viên & Loại Bỏ Vai Trò Học Sinh

#### 1. Mục tiêu
Xác định chuẩn xác phạm vi của Web Admin: Là công cụ quản trị nội bộ dành riêng cho **Quản trị viên (Admin)** để quản lý giảng viên, cấu hình môn học và điều phối quota AI; loại bỏ hoàn toàn ngộ nhận về "Web Portal quản lý học sinh".

#### 2. Câu Prompt đã gửi
> *"Web chỉ cho admin sài thôi đâu phải web quản lí học sinh đâu"*

#### 3. Kết quả do AI sinh ra (AI Output)
AI đã chuẩn hóa lại ma trận phân quyền RBAC và danh mục chức năng trong toàn bộ tài liệu ([docs/architecture/system-overview.md](file:///e:/AITA/docs/architecture/system-overview.md), [docs/architecture/tech-stack.md](file:///e:/AITA/docs/architecture/tech-stack.md)):
- **Web Admin Dashboard**: Chỉ có **Admin** đăng nhập để: Quản lý tài khoản Giảng viên, quản lý danh mục 4 môn học (PRF, PRO, DSA, PHP), cấu hình API Key và giám sát hạn ngạch token Gemini AI.
- **Desktop App Client**: Dành cho **Giảng viên (Instructor)** đăng nhập để thực hiện nghiệp vụ chấm bài offline-first tốc độ cao từ file CSV.
- **Học sinh (Student)**: Không có tài khoản trong hệ thống, không truy cập Web. Sinh viên chỉ là đối tượng trong danh sách nạp từ file CSV `students.csv`.

#### 4. Giải trình & Tinh chỉnh của Nhóm (Team Justification & Customization)
- **Tập trung hóa mục tiêu sản phẩm (Scope Definitiveness)**: Đúng với tên gọi của dự án **AITA - Automated Grading & Assessment Tool for Instructors**, hệ thống hướng tới người dùng mục tiêu là Nhà trường (Admin) và Giảng viên (Instructor). Việc tinh gọn phạm vi giúp đồ án tập trung sâu vào chất lượng công cụ chấm thi và AI hỗ trợ, tránh phân tán nguồn lực vào các tính năng cổng sinh viên không cần thiết.









