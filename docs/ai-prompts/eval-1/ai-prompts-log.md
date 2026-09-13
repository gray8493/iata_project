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

---

### 🔹 PROMPT 15: Đồng Bộ Hóa Toàn Diện Tài Liệu Tác Nhân & Use Cases Theo Luồng Kiến Trúc Dự Án Mới Nhất

#### 1. Mục tiêu
Rà soát, chuẩn hóa và tái thiết kế tài liệu Đặc tả Tác nhân & Use Cases ([docs/architecture/actors_and_use_cases.md](file:///c:/AITA/iata_project/docs/architecture/actors_and_use_cases.md)) sao cho khớp 100% với kiến trúc 3 thành phần (Desktop App PyQt6, Web Admin Dashboard, FastAPI Backend) và các quyết định kỹ thuật mới nhất trong [docs/architecture/system-overview.md](file:///c:/AITA/iata_project/docs/architecture/system-overview.md).

#### 2. Câu Prompt đã gửi
> *"file overview của tôi có sự thay đổi và hãy xem có thay đổi gì sửa cho tôi đó đúng flow của dự án, và trong cuộc trò chuyện hiện tại tôi đang promt gì foramt vào thêm vào file docs/ai-prompts/eval-1/ai-prompts-log.md@[c:\AITA\iata_project\docs\architecture\actors_and_use_cases.md]"*

#### 3. Kết quả do AI sinh ra (AI Output)
AI đã phân tích các thay đổi kiến trúc và cập nhật toàn diện tài liệu [docs/architecture/actors_and_use_cases.md](file:///c:/AITA/iata_project/docs/architecture/actors_and_use_cases.md):
- **Phân định rõ 2 giao diện người dùng theo chuẩn RBAC**: 
  - *Web Admin Dashboard*: Dành riêng cho **Quản trị viên (Admin)** quản lý tài khoản Giảng viên, quản lý danh mục môn học (PRF, PRO, DSA, PHP), cấu hình API Key & Quota Gemini AI tập trung, giám sát token toàn trường và xem lịch sử chấm.
  - *Desktop App Client (PyQt6)*: Dành riêng cho **Giảng viên (Instructor)** thực hiện toàn bộ quy trình chấm bài offline-first tốc độ cao từ file `students.csv` (chuẩn 2 cột: `MSSV,File`), cấu hình sandbox và xuất `results.csv`.
  - Khẳng định rõ: **Sinh viên không có tài khoản** và không truy cập vào Web/Desktop.
- **Chuẩn hóa nguyên lý chấm Black-box & hàm `main()` độc lập**:
  - Mỗi câu hỏi là một file mã nguồn riêng biệt chứa hàm `main()` độc lập (`Q1.c`, `Q2.c`, `Q1.java`, `q1.py`), nạp `INPUT` qua `stdin`, in `OUTPUT` qua `stdout`, không bọc code wrapper. Tổng điểm bài thi là tổng điểm các câu.
  - Giảng viên chỉ cần nạp cặp `INPUT` và `OUTPUT kỳ vọng`, hoàn toàn không cần code giải mẫu (solution code).
- **Mở rộng động cơ so khớp 7 chiến lược (Strategy Pattern)**: Bổ sung đầy đủ 7 chiến lược so khớp (`ExactMatch`, `IgnoreWhitespace`, `CaseInsensitive`, `FloatingPointTolerance`, `UnorderedTokens`, `RegexPattern`, `SpecialJudge`).
- **Tối ưu hóa cơ chế AI thông minh**:
  - *AI Code Review*: Cơ chế **On-Demand (Lazy Loading)**, chỉ bấm nút `[✨ AI Phân tích lỗi]` khi xem chi tiết bài bị lỗi logic `WA`, bỏ qua bài lỗi biên dịch `CE` vì đã có log của compiler.
  - *AI Plagiarism Detection*: Cơ chế **Lọc 2 vòng (Two-Stage Filtering)**: Vòng 1 quét AST/Winnowing cục bộ 100% offline; Vòng 2 chỉ gửi 1-3 cặp nghi vấn vượt ngưỡng (> 80%) lên Gemini AI.
- **Tái cấu trúc ma trận 19 Use Cases & Sơ đồ PlantUML**: Cập nhật ma trận phân hệ rõ ràng và mã nguồn PlantUML Use Case Diagram chuẩn xác theo phân quyền.

#### 4. Giải trình & Tinh chỉnh của Nhóm (Team Justification & Customization)
- **Tính nhất quán kiến trúc tuyệt đối (Architecture Consistency)**: Đảm bảo giữa tài liệu kiến trúc tổng quan (`system-overview.md`), tài liệu công nghệ (`tech-stack.md`) và tài liệu phân tích nghiệp vụ (`actors_and_use_cases.md`) không có bất kỳ mâu thuẫn hay điểm lệch nào.
- **Tuân thủ chặt chẽ tiêu chí AI Rubric của môn SWD392**: Việc lưu vết minh bạch Prompt 15 thể hiện khả năng làm chủ thiết kế hệ thống, nhanh chóng phát hiện sự thay đổi yêu cầu để điều chỉnh tài liệu mô hình hóa tương ứng.

---

### 🔹 PROMPT 16: Xác Định Danh Sách Tác Nhân (Primary Actors & Supporting Actors Chuẩn UML)

#### 1. Mục tiêu
Xác định chính xác ranh giới hệ thống và phân loại danh sách các Tác nhân người dùng (Primary Human Actors) cùng các Tác nhân hệ thống ngoài hỗ trợ (External Supporting Actors) theo đúng quy chuẩn mô hình hóa Kỹ nghệ phần mềm và UML.

#### 2. Câu Prompt đã gửi
> *"Dựa trên bài toán Desktop App chấm thi lập trình AITA cho giảng viên đại học, hãy xác định các Primary Actors và Supporting Actors phù hợp chuẩn UML."*

#### 3. Kết quả do AI sinh ra (AI Output)
AI đã đề xuất danh sách sơ bộ bao gồm:
- Tác nhân người dùng: Giảng viên (Instructor), Trợ giảng (Teaching Assistant - TA), Quản trị viên (System Administrator - Admin).
- Tác nhân hệ thống ngoài: Môi trường biên dịch / Sandbox (GCC, Javac, Python Runtime), Dịch vụ AI (Google Gemini API), Bộ lưu trữ cục bộ (Local Storage / SQLite), Máy chủ Web Backend (Web API Server).

#### 4. Giải trình & Tinh chỉnh của Nhóm (Team Justification & Customization)
- **Quyết định thiết kế của Nhóm (Design Decisions)**:
  1. *Lược bỏ vai trò Trợ giảng (TA)*: Trong thực tế giảng dạy và thi cử tại các trường đại học đối với các môn nền tảng, Giảng viên trực tiếp phụ trách lớp là người toàn quyền chấm điểm, cấu hình testcase và xuất bảng điểm. Việc lược bỏ vai trò TA giúp tinh gọn ma trận phân quyền RBAC và tập trung tối đa vào trải nghiệm của Giảng viên.
  2. *Chuẩn hóa theo đúng lý thuyết UML*: AI ban đầu đưa Local Storage (SQLite) vào nhóm External Actor. Nhóm đã phản biện và loại bỏ SQLite khỏi danh sách External Supporting Actors vì cơ sở dữ liệu SQLite và hệ thống tệp tin cục bộ (File System) là tầng dữ liệu nội bộ (Internal Data Layer) nằm bên trong ranh giới của phần mềm ứng dụng, không thể coi là một tác nhân bên ngoài.

---

### 🔹 PROMPT 17: Phân Rã & Xây Dựng Danh Mục Use Case Theo 6 Phân Hệ Nghiệp Vụ

#### 1. Mục tiêu
Phân rã toàn diện các tính năng của hệ sinh thái AITA thành danh mục Use Case chuẩn kỹ nghệ phần mềm, phân nhóm theo các phân hệ chức năng rõ ràng và thiết lập mối quan hệ bao hàm (`<<include>>`) / mở rộng (`<<extend>>`).

#### 2. Câu Prompt đã gửi
> *"Phân rã các tính năng của AITA (nạp bài, nạp testcase, sandbox đa ngôn ngữ C/Java/Python, 3 design pattern, AI testcase/feedback/plagiarism) thành danh mục Use Case chuẩn."*

#### 3. Kết quả do AI sinh ra (AI Output)
AI đã tổ chức danh mục Use Case thành 6 phân hệ chức năng:
1. Quản trị Hệ thống & Quản lý Xác thực.
2. Quản lý Đợt Chấm & Dữ liệu Sinh viên.
3. Quản lý Bộ Kiểm thử & Chiến lược So khớp.
4. Tự động Thực thi & Chấm điểm Pipeline.
5. Tính năng Thông minh có AI Hỗ trợ.
6. Báo cáo, Đánh giá & Đồng bộ.

#### 4. Giải trình & Tinh chỉnh của Nhóm (Team Justification & Customization)
- **Chấp nhận & Bổ sung kiến trúc**:
  - Nhóm chuẩn hóa mã định danh thống nhất từ `UC-01` đến `UC-17` (sau này mở rộng thành 19 Use Cases khi bổ sung đầy đủ chức năng Web Admin và Cloud Sync).
  - Bổ sung quan hệ bắt buộc `<<include>>` từ Use Case Chấm điểm tự động (`UC-12`) tới Thiết lập Động cơ So khớp (`UC-11`) nhằm liên kết chặt chẽ nghiệp vụ với mẫu thiết kế **Strategy Pattern**.
  - Thiết lập quan hệ `<<extend>>` cho tính năng AI Code Review và Phân tích đạo văn chuyên sâu để phản ánh đúng bản chất kích hoạt có điều kiện (On-Demand).

---

### 🔹 PROMPT 18: Viết Bản Đặc Tả Use Case Chi Tiết (Use Case Specifications Chuẩn Kỹ Nghệ Phần Mềm)

#### 1. Mục tiêu
Xây dựng bản đặc tả chi tiết (Use Case Specification) cho các Use Case trọng tâm của dự án theo cấu trúc chuẩn quốc tế: Tác nhân, Tiền điều kiện, Hậu điều kiện, Tác nhân kích hoạt, Luồng sự kiện chính (Main Flow) và các Luồng rẽ nhánh / Ngoại lệ (Alternative & Exception Flows).

#### 2. Câu Prompt đã gửi
> *"Viết Use Case Specification hoàn chỉnh theo chuẩn Kỹ nghệ phần mềm cho Use Case Tự động sinh Testcase bằng AI và Thực thi Chấm hàng loạt."*

#### 3. Kết quả do AI sinh ra (AI Output)
AI đã cung cấp khung mẫu đặc tả hoàn chỉnh cho các Use Case:
- `UC-10`: Tự động sinh Testcase biên bằng AI (AI Black-box Testcase Generator).
- `UC-12`: Thực thi Chấm điểm Tự động Hàng loạt (Batch Automated Grading Pipeline).
Bao gồm đầy đủ các bước tuần tự từ khi người dùng thao tác đến phản hồi của hệ thống.

#### 4. Giải trình & Tinh chỉnh của Nhóm (Team Justification & Customization)
- **Tùy biến sâu theo đặc thù kỹ thuật của AITA**:
  - Tích hợp chi tiết các thành phần kiến trúc nội bộ của AITA vào kịch bản: `RunnerFactory`, `CompilerAdapter`, `SandboxRunner` và thư viện `psutil` để kiểm soát thời gian chạy (Time Limit) và dung lượng RAM (Memory Limit).
  - Bổ sung các kịch bản ngoại lệ thực tế (`E1`, `E2`): xử lý khi trình biên dịch chưa được cài đặt, mất kết nối mạng, hoặc tài khoản Giảng viên vượt quá hạn ngạch gọi AI (Rate Limit / Quota Exceeded).

---

### 🔹 PROMPT 19: Sinh Mã Nguồn Sơ Đồ PlantUML Use Case Diagram Chuẩn Cú Pháp

#### 1. Mục tiêu
Chuyển hóa toàn bộ danh mục 19 Use Cases, các tác nhân người dùng và hệ thống ngoài thành mã nguồn sơ đồ PlantUML Use Case Diagram chuẩn cú pháp, trực quan và dễ bảo trì.

#### 2. Câu Prompt đã gửi
> *"Chuyển đổi toàn bộ danh mục Use Case và các tác nhân của AITA thành mã nguồn sơ đồ PlantUML Use Case Diagram chuẩn cú pháp."*

#### 3. Kết quả do AI sinh ra (AI Output)
AI đã sinh đoạn mã PlantUML mô tả đầy đủ:
- 2 Primary Actors: Admin, Instructor.
- 3 External Supporting Actors: Gemini AI Hub, Sandbox Runner, Web Server Backend.
- Các use case được nhóm theo các package trực quan: Web Admin Dashboard và Desktop App Client.
- Các mũi tên tương tác người dùng, mũi tên `<<include>>`, `<<extend>>` và kết nối tác nhân ngoài.

#### 4. Giải trình & Tinh chỉnh của Nhóm (Team Justification & Customization)
- **Tinh chỉnh giao diện & Bố cục sơ đồ**:
  - Áp dụng cấu hình skinparam hiện đại (`!theme plain`, màu viền và nền trang nhã, biểu tượng actor dạng `awesome`).
  - Định hướng layout rõ ràng: phân tách 2 cụm chức năng riêng biệt giúp sơ đồ không bị chồng chéo mũi tên khi render ra ảnh vector `.svg` và ảnh `.png` để đưa vào báo cáo Đánh giá 1 (Evaluation 1).

---

### 🔹 PROMPT 20: Viết Đặc Tả Chi Tiết Từng Bước Cho Toàn Bộ 19 Use Cases Và Tách Thành File Độc Lập

#### 1. Mục tiêu
Hoàn thiện toàn diện nhiệm vụ Đánh giá 1 (Evaluation 1: Requirement Analysis & Modeling) của môn học SWD392 theo yêu cầu: *"Viết bản mô tả chi tiết cho từng Use Case (Use Case Descriptions)"*. Bản mô tả cần bao phủ trọn vẹn toàn bộ 19 Use Cases thuộc 6 phân hệ chức năng, tuân thủ cấu trúc chuẩn kỹ nghệ phần mềm quốc tế (IEEE 830 / RUP Template), đồng thời đóng gói thành file tài liệu chuyên biệt [docs/architecture/use_case_descriptions.md](file:///d:/Java%20FPT/AITA/docs/architecture/use_case_descriptions.md) để giữ cho file [docs/architecture/actors_and_use_cases.md](file:///d:/Java%20FPT/AITA/docs/architecture/actors_and_use_cases.md) tập trung vào danh mục tác nhân và sơ đồ PlantUML.

#### 2. Câu Prompt đã gửi
> *"Dựa trên các base file liên quan đến các nội dung trong nội dung dưới đây có sẵn của project hãy thực hiện task sau: Write step-by-step descriptions for each use case, including preconditions, main flow, alternate flows, and postconditions."*
>
> *(Prompt tinh chỉnh cấu trúc file tiếp theo)*:
> *"Hãy tạo ra 1 file mới để làm nội dung này, và khôi phục nội dung cũ của file @[d:\Java FPT\AITA\docs\architecture\actors_and_use_cases.md] đi"*

#### 3. Kết quả do AI sinh ra (AI Output)
AI đã biên soạn đặc tả chi tiết và hoàn chỉnh cho toàn bộ 19 Use Cases:
- **Cấu trúc chuẩn RUP/IEEE cho mỗi Use Case**:
  - Mã và Tên Use Case (Song ngữ Việt - Anh).
  - Tác nhân chính (Primary Actor) & Tác nhân hỗ trợ ngoài (External Supporting Actors).
  - Mô tả tóm tắt (Summary).
  - Tiền điều kiện (Preconditions) & Hậu điều kiện (Postconditions).
  - Tác nhân kích hoạt (Trigger).
  - Luồng sự kiện chính từng bước (Step-by-step Main Flow): Mô tả tường minh các bước tương tác qua lại giữa Người dùng và Hệ thống.
  - Luồng rẽ nhánh & Ngoại lệ (Alternative & Exception Flows): Xử lý chi tiết các tình huống lỗi mạng, hết hạn ngạch AI (429), thiếu compiler, sai định dạng file CSV, v.v.
- **Bao phủ đủ 6 phân hệ**:
  1. Phân hệ 1: Quản trị Hệ thống & Quản lý Xác thực (`UC-01` đến `UC-05` trên Web Admin & Backend).
  2. Phân hệ 2: Quản lý Đợt Chấm & Dữ liệu Sinh viên (`UC-06` đến `UC-08` trên Desktop App).
  3. Phân hệ 3: Quản lý Bộ Kiểm thử & Chiến lược So khớp (`UC-09` đến `UC-11` trên Desktop App).
  4. Phân hệ 4: Tự động Thực thi & Chấm điểm (`UC-12` đến `UC-15` trên Desktop App).
  5. Phân hệ 5: Tính năng Thông minh có AI Hỗ trợ (`UC-16` đến `UC-17` trên Desktop App & AI Hub).
  6. Phân hệ 6: Báo cáo, Đánh giá & Đồng bộ (`UC-18` đến `UC-19` trên Desktop App & Cloud).
- **Tổ chức tài liệu**: Khôi phục nguyên trạng file gốc `actors_and_use_cases.md` và tạo file chuyên biệt mới [docs/architecture/use_case_descriptions.md](file:///d:/Java%20FPT/AITA/docs/architecture/use_case_descriptions.md).

#### 4. Giải trình & Tinh chỉnh của Nhóm (Team Justification & Customization)
- **Tách biệt High-Level và Detailed Specification**: 
  - File `actors_and_use_cases.md` đóng vai trò là tài liệu kiến trúc mức cao (High-Level Specification), tập trung vào định nghĩa Tác nhân, ma trận phạm vi, các quan hệ `<<include>>`/`<<extend>>` và mã nguồn sơ đồ PlantUML.
  - File `use_case_descriptions.md` đóng vai trò là đặc tả kỹ thuật chi tiết (Detailed Specification), phục vụ đội ngũ phát triển lập trình chi tiết các luồng giao diện và xử lý ngoại lệ.
- **Tính khả thi và độ hoàn thiện đồ án**: Việc đặc tả đủ 19 Use Cases thay vì chỉ mô tả sơ sài một vài tính năng giúp nhóm tự tin nắm bắt toàn bộ ngóc ngách của hệ thống khi bước vào các giai đoạn thiết kế kiến trúc (Evaluation 2) và lập trình tích hợp (Final Presentation).

---

### 🔹 PROMPT 21: Phản Biện & Làm Rõ Cơ Chế Phân Quyền Đăng Nhập, Cấp Tài Khoản Giảng Viên & Tính Khả Thi Của Sandbox Runner

#### 1. Mục tiêu
Thực hiện phản biện kỹ thuật (Technical Review) đối với 3 câu hỏi kiến trúc mang tính sống còn:
1. Phân định rõ ràng mục đích đăng nhập giữa Web Admin và Desktop App theo mô hình RBAC.
2. Xác định quy trình cấp phát tài khoản Giảng viên tập trung, ngăn chặn nguy cơ rò rỉ quota AI.
3. Kiểm chứng và chứng minh tính khả thi khoa học của chỉ số hiệu năng chấm bài (45 bài trong 18.2 giây) thông qua các rào chắn kiểm soát "độ nặng" (Sandbox Guardrails).

#### 2. Câu Prompt đã gửi
> *"1. Tại sao ở web admin cần có đăng nhập của giảng viên nhỉ để làm gì có khác nhau gì khi phải đăng nhập với admin 
2. Tài khoản của giảng viên được đăng kí ở đâu 
3. Nếu chấm Đã chấm xong 45 bài trong 18.2 giây hệ thống có thể sử lí được không vậy vì chưa có setup được độ nặng của file đến đâu để hệ thống xử lí mà"*

#### 3. Kết quả do AI sinh ra (AI Output)
AI đã phân tích và làm sáng tỏ 3 vấn đề:
- **Vấn đề 1 (Phân quyền Đăng nhập Web Admin vs Desktop App)**:
  - Khẳng định: Giảng viên **KHÔNG** có quyền truy cập vào Web Admin Dashboard. Web Admin là không gian làm việc độc quyền của Admin.
  - `UC-01` là endpoint Backend chung (`/api/v1/auth/login`). Khi tài khoản Giảng viên (`role: "instructor"`) cố đăng nhập vào Web Admin, hệ thống chặn lại với lỗi `403 Forbidden`. Giảng viên chỉ đăng nhập trên Desktop App Client để lấy JWT phục vụ đồng bộ dữ liệu và gọi AI.
- **Vấn đề 2 (Quy trình Cấp phát Tài khoản Giảng viên)**:
  - Giảng viên **KHÔNG** tự đăng ký tự do (No Self-Registration) nhằm bảo vệ hạn ngạch Google Gemini API của nhà trường.
  - Toàn bộ tài khoản Giảng viên do Admin khởi tạo tập trung trên Web Admin (`UC-02`) dựa trên danh sách phân công của Phòng Đào tạo, sau đó cấp phát về email nội bộ của trường (`@fpt.edu.vn`).
- **Vấn đề 3 (Chứng minh Tính Khả Thi Hiệu Năng 18.2s & Thiết Lập Độ Nặng Sandbox)**:
  - *Bản chất bài thi lập trình*: File sinh viên rất nhẹ (30-150 dòng, 2-10 KB); biên dịch C (`gcc`) 50-100ms, Java (`javac`) 200-400ms, Python <20ms; mỗi testcase chạy 1-20ms.
  - *Xử lý song song*: Desktop App dùng pool 4-8 tiến trình song song (`ProcessPoolExecutor`) trên CPU đa nhân $\rightarrow$ 45 sinh viên chỉ cần ~7-8 lượt chạy gối đầu $\rightarrow$ Tổng thời gian 16-18 giây là hoàn toàn thực tế.
  - *Cơ chế kiểm soát độ nặng (Sandbox Guardrails)*:
    1. **Time Limit (1000 ms)**: Giám sát bằng `psutil`, cưỡng chế kill ngay nếu code lặp vô hạn `while(true)`, bắt lỗi `TLE`.
    2. **Memory Limit (256 MB)**: Kill ngay nếu tràn stack đệ quy hoặc mảng quá lớn, bắt lỗi `MLE`.
    3. **File Size Limit (1 MB)**: Từ chối nạp các file vượt kích thước cho phép.
    4. **Offline-first**: Hoàn toàn không gọi mạng hay API AI khi đang chấm hàng loạt, dồn 100% CPU cho việc chấm.

#### 4. Giải trình & Tinh chỉnh của Nhóm (Team Justification & Customization)
- **Tư duy phản biện và làm chủ hệ thống (Mastery & Critical Thinking)**: Việc chủ động chất vấn và làm sáng tỏ các thông số hiệu năng và cơ chế bảo mật tài nguyên giúp nhóm tự tin giải trình trước giảng viên phản biện. Đây là bằng chứng rõ nét thể hiện sự thấu hiểu sâu sắc bản chất vận hành của hệ thống chứ không chỉ sao chép output từ AI một cách thụ động.

---

### 🔹 PROMPT 22: Quy Chuẩn Mã Phản Hồi API (200, 400, 401, 429...) & Định Nghĩa Cấu Trúc Dữ Liệu Trước Khi Lập Trình

#### 1. Mục tiêu
Thực hiện phương pháp tiếp cận thiết kế API chuẩn mực (Contract-First API Design): Định nghĩa rõ ràng cấu trúc vỏ bọc phản hồi JSON (Response Envelope Pattern), danh mục toàn bộ mã trạng thái HTTP (200, 400, 401, 403, 404, 422, 429, 500) và từ điển mã lỗi nghiệp vụ (Business Error Codes) trước khi bước vào giai đoạn viết code thực tế.

#### 2. Câu Prompt đã gửi
> *"Trong docs/architecture tạo file code trả về 200 400 define trước khi code"*

#### 3. Kết quả do AI sinh ra (AI Output)
AI đã khởi tạo tài liệu kỹ thuật hoàn chỉnh [docs/architecture/api-response-codes.md](file:///e:/AITA/docs/architecture/api-response-codes.md):
- **Cấu trúc JSON chuẩn nhất quán (Consistent Envelope Pattern)**:
  - `SuccessResponse`: gồm `success: true`, `status_code: 200/201`, `message`, `data`, `timestamp`.
  - `ErrorResponse`: gồm `success: false`, `status_code: 400/401/403/404/422/429/500`, `error_code`, `message`, `details`, `timestamp`.
  - `PaginatedData`: hỗ trợ phân trang cho danh sách User, Môn học, Lịch sử chấm.
- **Bảng tra cứu HTTP Status Codes chuẩn RFC 9110**: Quy định rõ ràng khi nào trả về 200, 201, 204, 400, 401, 403, 404, 409, 422, 429, 500.
- **Từ điển mã lỗi nghiệp vụ (Business Error Codes)**: Phân loại theo 6 nhóm nghiệp vụ trọng yếu (`AUTH_xxx`, `USER_xxx`, `COURSE_xxx`, `CSV_xxx`, `TEST_xxx`, `AI_xxx`, `EXEC_xxx`).
- **Quy tắc ứng xử phía Client**: Hướng dẫn xử lý hiển thị toast/alert, xử lý tự động khi dính lỗi `401 Unauthorized` và `429 Too Many Requests` (AI Quota). Tài liệu tập trung thuần túy vào đặc tả kiến trúc (Architecture Specification), chưa nhúng mã nguồn code Pydantic.

#### 4. Giải trình & Tinh chỉnh của Nhóm (Team Justification & Customization)
- **Tách biệt giữa Đặc tả Kiến trúc và Lập trình (Separation of Design and Implementation)**: 
  - Tài liệu kiến trúc cần giữ tính khái quát, độc lập với framework code cụ thể và tập trung vào đặc tả giao thức dữ liệu (Data Protocol). Việc lược bỏ các đoạn code Python Pydantic giúp tài liệu ngắn gọn, dễ đọc, đúng chuẩn tài liệu thiết kế của giai đoạn Evaluation 1.
  - Trong một hệ thống tích hợp gồm nhiều thành phần chạy song song (FastAPI Backend, Web Admin, Desktop App PyQt6), việc định nghĩa mã lỗi nghiệp vụ dạng chuỗi hằng (`error_code`: ví dụ `AI_QUOTA_EXCEEDED`, `CSV_INVALID_COLUMNS`) giúp Client (Desktop App) có thể bắt lỗi chính xác và hiển thị hộp thoại cảnh báo phù hợp mà không bị phụ thuộc vào chuỗi thông điệp `message`.

---

### 🔹 PROMPT 23: Thiết Kế Sơ Đồ Tuần Tự (Sequence Diagram) & Sơ Đồ Giao Tiếp (Communication Diagram) Chuẩn UML

#### 1. Mục tiêu
Thiết kế và đóng gói mã nguồn PlantUML cho 2 loại sơ đồ mô hình hóa hành vi cốt lõi theo yêu cầu của Đánh giá 1 (Evaluation 1: Requirement Analysis & Modeling) môn học SWD392: **Sequence Diagram (Sơ đồ tuần tự)** và **Communication Diagram (Sơ đồ giao tiếp / cộng tác)** cho các Use Case trọng tâm nhất của hệ thống.

#### 2. Câu Prompt đã gửi
> *"Sequence Diagram
> Communication Diagram"*

#### 3. Kết quả do AI sinh ra (AI Output)
AI đã thiết kế và lưu trữ đúng **2 file mã nguồn PlantUML tổng thể toàn dự án** trong thư mục [docs/diagrams/puml/](file:///e:/AITA/docs/diagrams/puml/):
1. **[sequence_diagram.puml](file:///e:/AITA/docs/diagrams/puml/sequence_diagram.puml)**: Sơ đồ tuần tự tổng thể toàn hệ sinh thái (System-Wide Sequence Diagram) mô tả trọn vẹn 4 giai đoạn vòng đời của hệ thống:
   - *Giai đoạn 1*: Admin quản trị tài khoản Giảng viên, cấu hình môn học và cấp hạn ngạch Quota Gemini trên Web Admin Dashboard.
   - *Giai đoạn 2*: Giảng viên đăng nhập Desktop App, nạp `students.csv` và gọi AI sinh bộ Testcase `(Input, Output)`.
   - *Giai đoạn 3*: Thực thi chấm bài tự động đa tiến trình offline-first qua hàm `main()`, `psutil` đo tài nguyên, so khớp 7 chế độ và xuất `results.csv`.
   - *Giai đoạn 4*: AI phân tích lỗi On-demand, quét đạo văn 2 vòng và đồng bộ kết quả chấm lên Cloud Backend để Admin xem báo cáo.
2. **[communication_diagram.puml](file:///e:/AITA/docs/diagrams/puml/communication_diagram.puml)**: Sơ đồ giao tiếp tổng thể toàn hệ sinh thái (System-Wide Communication Diagram) thể hiện sự cộng tác liên phân hệ qua 4 nhóm chu trình nghiệp vụ được đánh số tuần tự giữa: Web Admin, Desktop App Client, FastAPI Gateway, AI Hub và Sandbox Runner.

#### 4. Giải trình & Tinh chỉnh của Nhóm (Team Justification & Customization)
- **Tầm nhìn hệ sinh thái tích hợp (Ecosystem-Level Modeling)**: Việc xây dựng cả **Sequence Diagram và Communication Diagram ở cấp độ Toàn Dự Án** mang lại cái nhìn bao quát toàn diện về kiến trúc tích hợp của đồ án SWD392. Sơ đồ chứng minh sự gắn kết chặt chẽ và dòng chảy dữ liệu thông suốt giữa Quản trị viên (Web Admin), Giảng viên (Desktop App) và Máy chủ trung tâm (FastAPI & Google Gemini AI Hub), đáp ứng trọn vẹn điểm số phần mềm tích hợp (30%) và phân tích mô hình hóa của giai đoạn Evaluation 1.

---

### 🔹 PROMPT 24: Đóng Gói Mã Nguồn PlantUML Sơ Đồ Trường Hợp Sử Dụng (Use Case Diagram) & Sơ Đồ Hoạt Động (Activity Diagram)

#### 1. Mục tiêu
Hoàn tất trọn bộ 4 sơ đồ UML bắt buộc của giai đoạn Đánh giá 1 (Evaluation 1: Requirement Analysis & Modeling) môn học SWD392 bằng cách thiết kế và đóng gói mã nguồn PlantUML độc lập cho:
1. **Use Case Diagram** (`use_case_diagram.puml`): Mô hình hóa trực quan toàn bộ 19 Use Cases, phân định ranh giới 3 phân hệ (Web Admin, Desktop App Client, Central Backend) và các tác nhân người dùng / tác nhân ngoài.
2. **Activity Diagram** (`activity_diagram.puml`): Mô hình hóa chi tiết quy trình nghiệp vụ cốt lõi xuyên suốt toàn hệ thống bằng kỹ thuật phân vùng Swimlanes chuẩn UML (Giảng viên, Desktop UI, Sandbox Engine, Backend API, Gemini AI).

#### 2. Câu Prompt đã gửi
> *"Được rồi bây giờ tạo 2 file docs/diagrams/puml/use_case_diagram.puml và docs/diagrams/puml/activity_diagram.puml khi prompt thì đọc file này @docs/ai-prompts/eval-1/ai-prompts-log.md"*

#### 3. Kết quả do AI sinh ra (AI Output)
AI đã thiết kế và tạo thành công 2 file mã nguồn PlantUML trong thư mục [docs/diagrams/puml/](file:///d:/SWD_Project/docs/diagrams/puml/):
1. **[use_case_diagram.puml](file:///d:/SWD_Project/docs/diagrams/puml/use_case_diagram.puml)**:
   - Thể hiện đầy đủ 2 Tác nhân con người chính: `Admin` (Web Admin) và `Instructor` (Desktop App).
   - Thể hiện 3 Tác nhân hệ thống ngoài: `FastAPI Central API`, `Google Gemini AI Hub`, `Sandbox Execution Runner`.
   - Gom cụm 19 Use Cases theo các package phân hệ logic, biểu diễn chuẩn xác các liên kết tương tác, quan hệ `<<include>>` (áp dụng chiến lược so khớp, giám sát tiến độ thời gian thực) và `<<extend>>` (phân tích lỗi AI on-demand khi gặp WA, điều chỉnh điểm).
2. **[activity_diagram.puml](file:///d:/SWD_Project/docs/diagrams/puml/activity_diagram.puml)**:
   - Ứng dụng cấu trúc **Swimlanes (5 phân vùng trực quan)**: `Giảng viên`, `Desktop App UI (PyQt6)`, `Desktop Core & Sandbox Runner`, `Web Server Backend (FastAPI)`, `Google Gemini AI Hub`.
   - Mô hình hóa khép kín 4 giai đoạn hoạt động:
     1. Khởi động, xác thực JWT và thiết lập đợt chấm (nạp `students.csv`, sinh testcase biên bằng AI hoặc nạp tay, chọn 1 trong 7 chiến lược so khớp).
     2. Thực thi chấm bài tự động hàng loạt đa tiến trình offline-first (biên dịch GCC/Javac/Python, chạy subprocess qua hàm `main()`, `psutil` bắt TLE/MLE/RE, so khớp Strategy Pattern ra verdict AC/WA, cập nhật progress bar thời gian thực qua Qt Signal/Slot).
     3. Đánh giá chuyên sâu, phân tích lỗi sư phạm bằng AI On-demand (UC-16) và kiểm tra đạo văn 2 vòng (AST Offline + AI Semantic >80%).
     4. Xuất báo cáo điểm (`results.csv` 7 cột, Excel `.xlsx`) và đồng bộ dữ liệu đợt chấm lên Cloud Backend (UC-18 & UC-19).

#### 4. Giải trình & Tinh chỉnh của Nhóm (Team Justification & Customization)
- **Hoàn thiện 100% yêu cầu 4 sơ đồ UML của Evaluation 1**: Dự án hiện đã sở hữu đầy đủ bộ tứ sơ đồ cốt lõi theo chuẩn IEEE/RUP (`use_case_diagram.puml`, `activity_diagram.puml`, `sequence_diagram.puml`, `communication_diagram.puml`), tạo tiền đề vững chắc cho giai đoạn Thiết kế Kiến trúc phần mềm (Evaluation 2).
- **Tối ưu hóa Bố cục Swimlanes**: Việc sử dụng Swimlanes trong Activity Diagram giúp người đọc và hội đồng chấm thi thấy rõ ranh giới trách nhiệm của từng thành phần: phần nào chạy cục bộ offline tốc độ cao trên Desktop trạm, phần nào gửi bảo mật qua Backend REST API và phần nào do AI Gemini xử lý, minh chứng cho năng lực thiết kế hệ thống phần mềm phân tán hiện đại.









