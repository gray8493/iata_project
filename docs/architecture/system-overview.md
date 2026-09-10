# Tài Liệu Tổng Quan Dự Án (System Overview)
# AITA - Automated Grading & Assessment Tool for Instructors
### Công cụ Desktop App Hỗ trợ Giảng viên Chấm điểm Tự động các Môn Lập trình

---

## 1. Giới thiệu & Bối cảnh dự án (Project Background)

### 1.1. Bối cảnh bài toán
Trong công tác giảng dạy các môn lập trình nền tảng tại trường đại học (như Lập trình cơ sở C, Lập trình hướng đối tượng OOP, Cấu trúc dữ liệu và Giải thuật DSA, Lập trình Python), giảng viên và trợ giảng (TA) thường xuyên phải đối mặt với số lượng bài tập thực hành rất lớn từ hàng trăm sinh viên mỗi kỳ. Việc chấm điểm thủ công từng bài gây ra nhiều bất cập:
- Mất rất nhiều thời gian biên dịch, nạp input và so sánh kết quả từng testcase.
- Dễ nhầm lẫn, không đồng nhất tiêu chí giữa các lần chấm.
- Khó kiểm soát thời gian chạy thực tế (Time Limit) và bộ nhớ tiêu thụ (Memory Limit).
- Khó phát hiện các trường hợp sinh viên sao chép mã nguồn của nhau.

### 1.2. Mục tiêu của dự án AITA
**AITA** là một ứng dụng Desktop chuyên nghiệp dành riêng cho **Giảng viên và Trợ giảng**, cho phép:
- Nạp danh sách sinh viên qua file Excel tinh gọn 2 cột (`MSSV`, `File`) và chọn thư mục bài nộp.
- Nạp bộ testcase linh hoạt bằng tay trên giao diện hoặc qua file cấu hình JSON.
- Tự động thực thi bài nộp với bộ testcase chuẩn và so khớp kết quả đầu ra theo 7 chiến lược (Strategy Pattern).
- Trả về bảng điểm chi tiết ngay lập tức (Pass/Fail từng testcase, thời gian chạy, mã lỗi biên dịch/thực thi).
- Tận dụng sức mạnh của **Google Gemini AI** để sinh testcase biên, phân tích lỗi code và viết nhận xét tự động điền thẳng vào file Excel kết quả.

---

## 2. Các môn học & Ngôn ngữ được hỗ trợ

Hệ thống được thiết kế theo mô hình mô-đun (Modular Runner), hỗ trợ linh hoạt các môn học và ngôn ngữ:

| Môn học | Ngôn ngữ hỗ trợ | Định dạng bài nộp tiếp nhận | Cơ chế biên dịch & Thực thi |
| :--- | :--- | :--- | :--- |
| **Lập trình cơ sở (PRF)** | **C** | Mã nguồn `.c` hoặc file build nhị phân `.exe` | Biên dịch qua `GCC/MinGW`, chạy subprocess có giới hạn Timeout. |
| **Cấu trúc dữ liệu & Giải thuật (DSA)** | **Java, Python** | File `.java`, `.class`, `.jar` hoặc `.py` | Đo lường thời gian thực thi (ms) và mức tiêu thụ bộ nhớ (RAM) cho từng thuật toán. |
| **Lập trình hướng đối tượng (OOP)** | **Java, C++** | File mã nguồn theo gói (package) hoặc file nén `.zip` | Kiểm tra cấu trúc lớp, tính bao đóng, kế thừa, đa hình và chạy testcase kiểm thử chức năng. |
| **Lập trình Python (PRO)** | **Python** | Script `.py` | Thực thi trực tiếp qua Python Runtime trong môi trường an toàn. |

---

## 3. Quy trình 8 bước sử dụng thực tế của Giảng viên (User Flow)

Hệ thống được tối ưu hóa cho trải nghiệm của một Giảng viên qua 4 giai đoạn với 8 bước tuần tự:

```text
[GIAI ĐOẠN 1: THIẾT LẬP]
Bước 1: Mở app AITA (PyQt6/PySide6) & Chọn môn học
Bước 2: Nạp bộ Testcase (Nhập tay trên GUI VÀ/HOẶC Import file JSON)
Bước 3: Nạp file Excel (MSSV, File) & Chọn thư mục bài nộp

[GIAI ĐOẠN 2: CHẤM BÀI TỰ ĐỘNG]
Bước 4: Chọn 1 trong 7 chế độ so khớp (Matching Strategy)
Bước 5: Bấm "BẮT ĐẦU CHẤM" (Chấm song song 4-8 sinh viên cùng lúc)

[GIAI ĐOẠN 3: XEM KẾT QUẢ & SOI LỖI]
Bước 6: Xem bảng điểm trực quan & biểu đồ thống kê cả lớp
Bước 7: Bấm vào sinh viên bị lỗi để soi code & Xem nhận xét từ AI Gemini

[GIAI ĐOẠN 4: KẾT XUẤT]
Bước 8: Bấm "XUẤT BẢNG ĐIỂM EXCEL" hoàn chỉnh để nộp phòng đào tạo
```

### 3.1. Chuẩn hóa File Excel đầu vào (Input) & đầu ra (Output):
- **File Excel đầu vào do Giảng viên nạp**: Chỉ gồm đúng **2 cột**:
  - Cột A: `MSSV` (Mã số sinh viên, ví dụ: `SE180001`).
  - Cột B: `File` (Tên file bài làm, ví dụ: `SE180001_Lab1.c`).
- **File Excel kết quả do Tool xuất ra**: Giữ nguyên 2 cột trên và tự động bổ sung:
  - Cột C: `Điểm số` (thang điểm 10).
  - Cột D: `Số testcase đạt` (ví dụ: `9/10`).
  - Cột E: `Trạng thái` (`AC`, `WA`, `TLE`, `MLE`, `CE`, `RE`).
  - Cột F: `Thời gian chạy (ms)` trung bình.
  - Cột G: `Nhận xét từ AI Gemini`: Gợi ý sư phạm chỉ rõ dòng code gây lỗi.

### 3.2. Cơ chế nạp Testcase đa dạng:
- **Nhập bằng tay trên GUI**: Giảng viên bấm nút "Thêm Testcase (+)", gõ trực tiếp Input, Expected Output, Time Limit (ms), Memory Limit (MB) và Điểm số.
- **Nạp / Xuất qua file JSON**: Hỗ trợ nạp cả bộ 20-30 testcase từ file `testcases.json` trong 1 click, có nút Export để lưu lại tái sử dụng cho các kỳ sau.

### 3.3. Chi tiết các trạng thái kết quả (Verdict Codes):
- **AC (Accepted)**: Bài nộp cho kết quả đầu ra khớp 100% với testcase.
- **WA (Wrong Answer)**: Đầu ra thực tế khác với đầu ra kỳ vọng.
- **TLE (Time Limit Exceeded)**: Quá thời gian quy định (ví dụ: vòng lặp vô hạn `while(true)`).
- **MLE (Memory Limit Exceeded)**: Tràn bộ nhớ quy định (ví dụ: đệ quy vô hạn `StackOverflow`).
- **CE (Compile Error)**: Lỗi cú pháp không thể biên dịch thành công.
- **RE (Runtime Error)**: Chương trình crash trong lúc chạy (truy cập mảng ngoài giới hạn, chia cho 0, null pointer).

---

## 4. Các tính năng mở rộng có sự hỗ trợ của AI (AI-Assisted Capabilities)

Tuân thủ đúng định hướng môn học **SWD392 (AI-Assisted System Design)**, AITA tích hợp AI để tối ưu hóa công việc của giảng viên:

1. **AI Auto-Generate Testcases (Tự động sinh bộ kiểm thử biên)**:
   - Giảng viên chỉ cần đưa đề bài, Gemini AI tự động phân tích và sinh ra các bộ testcase đặc biệt (Corner cases, Boundary values, Large input tests).
   - Tool tự động lấy file `solution` chuẩn của giảng viên chạy với Input của AI để kiểm định ra Expected Output chuẩn xác 100%.
2. **AI Code Review & Feedback Generator (Tự động viết nhận xét cho sinh viên)**:
   - Khi bài của sinh viên bị sai (WA/RE/CE), AI tự động đọc code, chỉ ra dòng code gây lỗi và viết đoạn nhận xét sư phạm ngắn gọn để điền thẳng vào file Excel.
3. **AI Plagiarism Detection (Phát hiện gian lận & Độ tương đồng mã nguồn)**:
   - AI so sánh cấu trúc logic và cây cú pháp AST giữa các bài nộp trong cùng lớp để cảnh báo các trường hợp đổi tên biến, đảo hàm nhằm sao chép bài.

---

## 5. Kiến trúc hệ thống Desktop App (High-Level Architecture)

Ứng dụng được xây dựng theo kiến trúc phân tầng (Clean / Layered Architecture):

```text
+-------------------------------------------------------------------------+
|                  GIAO DIỆN NGƯỜI DÙNG (Desktop UI Layer)                |
| - Giao diện PyQt6 / PySide6 hiện đại (Dark/Light mode)                  |
| - Màn hình chọn file Excel 2 cột (MSSV, File) và Thư mục bài nộp        |
| - Màn hình quản lý Testcase (Nhập tay GUI + Import/Export JSON)         |
| - Bảng kết quả chấm thi thời gian thực, bộ lọc bài lỗi                  |
+-------------------------------------------------------------------------+
                                    ↕
+-------------------------------------------------------------------------+
|                TẦNG NGHIỆP VỤ CỐT LÕI (Core Business Layer)             |
| - Testcase Manager: Quản lý Input/Output/Timeout/JSON                   |
| - Matching Strategy Engine: 7 chế độ so khớp kết quả linh hoạt           |
| - Report Exporter: Đọc & Xuất bảng điểm Excel qua openpyxl              |
| - AI Service Bridge: Tương tác với Google Gemini API                    |
+-------------------------------------------------------------------------+
                                    ↕
+-------------------------------------------------------------------------+
|                 TẦNG THỰC THI AN TOÀN (Execution & Sandbox)             |
| - C Runner (gcc compile & execution)                                    |
| - Java Runner (javac compile, java runtime watcher)                     |
| - Python Runner (python subprocess controller)                          |
| - Process Watcher (psutil): Giám sát RAM, CPU, cưỡng chế ngắt TLE       |
+-------------------------------------------------------------------------+
                                    ↕
+-------------------------------------------------------------------------+
|                   TẦNG LƯU TRỮ NỘI BỘ (Local Storage)                   |
| - SQLite: Lưu lịch sử các đợt chấm, danh sách lớp, bộ testcase mẫu       |
| - File System: Lưu file log chi tiết của từng sinh viên                 |
+-------------------------------------------------------------------------+
```

---

## 6. Hiện thực hóa 3 Mẫu thiết kế (Design Patterns) theo yêu cầu SWD392

### 6.1. Strategy Pattern (Behavioral Pattern) – Động cơ so khớp 7 chế độ (`MatchingStrategy`)
Hệ thống cung cấp 7 chiến lược so khớp đầu ra để phù hợp với mọi dạng bài tập lập trình:
1. **`ExactMatchStrategy`**: So sánh chính xác 100% từng ký tự.
2. **`IgnoreWhitespaceStrategy`**: Bỏ qua khoảng trắng và dấu xuống dòng thừa ở cuối.
3. **`CaseInsensitiveStrategy`**: Không phân biệt chữ hoa, chữ thường (ví dụ: `YES` / `yes`).
4. **`FloatingPointToleranceStrategy`**: So sánh số thực với sai số delta $\le 10^{-5}$ cho các bài giải thuật/toán học.
5. **`UnorderedTokensStrategy`**: Không quan tâm thứ tự xuất hiện các phần tử (ví dụ: in ra các ước số của N).
6. **`RegexPatternStrategy`**: So khớp định dạng theo biểu thức chính quy Regex (ví dụ: ngày tháng, mã số).
7. **`SpecialJudgeStrategy`**: Gọi mã kiểm thử riêng (`checker.py`) của giảng viên cho các bài toán có nhiều đáp án đúng.

### 6.2. Factory Method (Creational Pattern) – `RunnerFactory`
Tự động nhận diện đuôi file bài nộp sinh viên (`.c`, `.java`, `.py`) để sản xuất ra đối tượng thực thi phù hợp (`CRunner`, `JavaRunner`, `PythonRunner`) mà không làm ảnh hưởng đến mã nguồn chung.

### 6.3. Adapter Pattern (Structural Pattern) – `CompilerAdapter`
Đồng nhất hóa cách truyền lệnh biên dịch và chuẩn hóa các mã lỗi trả về giữa các trình biên dịch khác nhau (`GCC/MinGW` của C, `Javac` của Java, `Python Interpreter`).

---

## 7. Yêu cầu phi chức năng (Non-Functional Requirements)

1. **An toàn hệ thống (Security & Sandboxing)**:
   - Ngăn chặn triệt để mã độc sinh viên: Không cho phép truy cập file hệ điều hành, tự động diệt các process chạy quá thời gian (Anti-Fork Bomb).
2. **Hiệu năng cao (High Performance)**:
   - Chấm song song đa tiến trình (Parallel Subprocess): Chấm đồng thời 4-8 bài nộp trên máy có CPU nhiều nhân, hoàn thành lớp 50 sinh viên trong 15-30 giây.
3. **Tiện dụng & Độc lập (Portability)**:
   - Đóng gói trọn gói dạng file `.exe` duy nhất bằng `PyInstaller`, mở lên chạy ngay trên Windows mà không cần cài đặt Python.
