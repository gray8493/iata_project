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

- Nạp hàng loạt bài tập của sinh viên (file mã nguồn hoặc file đã build).
- Tự động thực thi bài nộp với bộ testcase chuẩn và so khớp kết quả đầu ra.
- Trả về bảng điểm chi tiết ngay lập tức (Pass/Fail từng testcase, thời gian chạy, mã lỗi biên dịch/thực thi).
- Tận dụng sức mạnh của **Trí tuệ nhân tạo (AI)** để sinh thêm testcase biên, phân tích phong cách code và gợi ý phản hồi tự động gửi cho sinh viên.

---

## 2. Các môn học & Ngôn ngữ được hỗ trợ

Hệ thống được thiết kế theo mô hình mô-đun (Modular Runner), hỗ trợ linh hoạt các môn học và ngôn ngữ:

| Môn học                                           | Ngôn ngữ hỗ trợ    | Định dạng bài nộp tiếp nhận                          | Cơ chế biên dịch & Thực thi                                                                             |
| :-------------------------------------------------- | :--------------------- | :---------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------- |
| **Lập trình cơ sở (PRF)**                 | **C**            | Mã nguồn`.c` hoặc file build nhị phân `.exe`       | Biên dịch qua`GCC/MinGW`, chạy subprocess có giới hạn Timeout.                                       |
| **Cấu trúc dữ liệu & Giải thuật (DSA)** | **Java, Python** | File`.java`, `.class`, `.jar` hoặc `.py`           | Đo lường thời gian thực thi (ms) và mức tiêu thụ bộ nhớ (RAM) cho từng thuật toán.             |
| **Lập trình hướng đối tượng (OOP)**   | **Java, C++**    | File mã nguồn theo gói (package) hoặc file nén`.zip` | Kiểm tra cấu trúc lớp, tính bao đóng, kế thừa, đa hình và chạy testcase kiểm thử chức năng. |
| **Lập trình Python (PRO)**                  | **Python**       | Script`.py`                                               | Thực thi trực tiếp qua Python Runtime trong môi trường an toàn.                                       |

---

## 3. Quy trình vận hành cốt lõi (Core Grading Pipeline)

Quy trình tự động hóa chấm điểm của AITA diễn ra qua 5 bước liên hoàn, hỗ trợ tối đa cho việc chấm hàng loạt cả lớp:

```text
[1. Import File Excel Danh Sách Lớp] ───> [2. Tự động đối chiếu bài nộp trong Thư mục]
(MSSV, Họ tên, Tên file bài làm)          (Auto-mapping sinh viên với file nộp)
                                                         │
                                                         ▼
                                            [3. Nạp Bộ Testcase Chuẩn]
                                            (Input, Expected Output, Time Limit, Memory Limit)
                                                         │
                                                         ▼
                                            [4. Chấm Hàng Loạt Song Song (Parallel Batch Runner)]
                                            - Chạy đa tiến trình: 4 - 8 sinh viên cùng lúc
                                            - Bắt lỗi CE, RE, TLE (quá giờ), MLE (tràn RAM)
                                            - So khớp kết quả (Matching Engine)
                                                         │
                                                         ▼
                                            [5. Cập nhật & Xuất File Excel Bảng Điểm Hoàn Chỉnh]
                                            - Điền trực tiếp: Điểm, Số TC đạt, Thời gian chạy, Verdict
                                            - Ghi nhận xét chi tiết từ AI (AI Feedback)
```

### 3.1. Cơ chế Import Excel & Tự động đối chiếu (Excel Import & Auto-Mapping)

- **Định dạng tiếp nhận**: File bảng tính `.xlsx` chuẩn xuất từ hệ thống đào tạo của trường (Canvas, LMS, Google Classroom).
- **Các trường dữ liệu**:
  - `MSSV`: Mã số sinh viên (ví dụ: `SE180001`).
  - `Họ và tên`: Tên sinh viên (ví dụ: `Nguyễn Văn A`).
  - `Tên file bài làm`: Tên file cụ thể (ví dụ: `SE180001_Lab1.c`). Nếu không có cột này, tool sẽ tự động tìm kiếm file trong thư mục dựa theo tiền tố `MSSV`.
- **Phát hiện ngoại lệ**: Tự động đánh dấu sinh viên chưa nộp bài (Điểm 0) hoặc sinh viên nộp sai định dạng bài làm.

### 3.2. Chấm đồng thời đa tiến trình (Parallel Batch Processing)

- Thay vì chấm tuần tự từng người gây mất thời gian, tool tận dụng vi xử lý đa nhân trên máy tính giảng viên để **chấm đồng thời 4 – 8 sinh viên cùng lúc**.
- Giảng viên quan sát được thanh tiến trình thời gian thực: *"Đang chấm: 35/50 sinh viên (70%)"*.
- Toàn bộ lớp học 50 sinh viên được chấm xong trọn vẹn chỉ trong **15 – 30 giây**.

### 3.3. Chi tiết các trạng thái kết quả (Verdict Codes):

- **AC (Accepted)**: Bài nộp cho kết quả đầu ra khớp 100% với testcase.
- **WA (Wrong Answer)**: Đầu ra thực tế khác với đầu ra kỳ vọng.
- **TLE (Time Limit Exceeded)**: Quá thời gian quy định (ví dụ: vòng lặp vô hạn `while(true)`).
- **MLE (Memory Limit Exceeded)**: Tràn bộ nhớ quy định (ví dụ: đệ quy vô hạn `StackOverflow`).
- **CE (Compile Error)**: Lỗi cú pháp không thể biên dịch thành công.
- **RE (Runtime Error)**: Chương trình crash trong lúc chạy (truy cập mảng ngoài giới hạn, chia cho 0, null pointer).

### 3.4. Xuất bảng điểm Excel tự động

- Sau khi chấm xong, hệ thống tự động sinh file Excel kết quả (ví dụ: `KetQua_SE1801_Assignment1.xlsx`) đã được điền sẵn đầy đủ các cột:
  - Cột `Điểm số`: Tính theo trọng số testcase (thang điểm 10).
  - Cột `Số testcase đạt`: Ví dụ `9/10`.
  - Cột `Trạng thái chung`: `AC`, `WA`, `TLE`,...
  - Cột `Thời gian chạy (ms)`: Thời gian thực thi trung bình.
  - Cột `Nhận xét từ AI`: Đoạn văn nhận xét sư phạm gợi ý sửa lỗi cho sinh viên.
- Giảng viên chỉ việc lấy file này nộp thẳng về cho phòng đào tạo mà không cần sao chép thủ công.

---

## 4. Các tính năng mở rộng có sự hỗ trợ của AI (AI-Assisted Capabilities)

Tuân thủ đúng định hướng môn học **SWD392 (AI-Assisted System Design)**, AITA tích hợp AI để tối ưu hóa công việc của giảng viên:

1. **AI Auto-Generate Testcases (Tự động sinh bộ kiểm thử)**:
   - Giảng viên chỉ cần đưa đề bài, AI tự động phân tích và sinh ra các bộ testcase đặc biệt (Corner cases, Boundary values, Large input tests).
2. **AI Code Review & Feedback Generator (Tự động viết nhận xét cho sinh viên)**:
   - Khi bài của sinh viên bị sai (WA/RE/CE), AI tự động đọc code, chỉ ra dòng code gây lỗi và viết đoạn nhận xét sư phạm ngắn gọn để giảng viên gửi lại cho sinh viên tự sửa.
3. **AI Plagiarism Detection (Phát hiện gian lận & Độ tương đồng mã nguồn)**:
   - AI so sánh cấu trúc cú pháp trừu tượng (AST - Abstract Syntax Tree) giữa các bài nộp của sinh viên trong cùng lớp để phát hiện các trường hợp đổi tên biến, đảo hàm nhằm qua mặt giảng viên.

---

## 5. Kiến trúc hệ thống Desktop App (High-Level Architecture)

Ứng dụng được xây dựng theo kiến trúc phân tầng (Clean / Layered Architecture):

```text
+-------------------------------------------------------------------------+
|                  GIAO DIỆN NGƯỜI DÙNG (Desktop UI Layer)                |
| - Màn hình chọn thư mục bài nộp, quản lý danh sách sinh viên            |
| - Màn hình tạo & chỉnh sửa bộ Testcase                                  |
| - Bảng kết quả chấm thi thời gian thực, bộ lọc bài lỗi                  |
+-------------------------------------------------------------------------+
                                    ↕
+-------------------------------------------------------------------------+
|                TẦNG NGHIỆP VỤ CỐT LÕI (Core Business Layer)             |
| - Testcase Manager: Quản lý Input/Output/Timeout                        |
| - Matcher Engine: So khớp chuỗi, loại bỏ khoảng trắng thừa              |
| - Report Exporter: Xuất bảng điểm Excel, PDF                            |
| - AI Service Bridge: Tương tác với OpenAI/Gemini/Ollama API             |
+-------------------------------------------------------------------------+
                                    ↕
+-------------------------------------------------------------------------+
|                 TẦNG THỰC THI AN TOÀN (Execution & Sandbox)             |
| - C Runner (gcc compile & execution)                                    |
| - Java Runner (javac compile, java runtime watcher)                     |
| - Python Runner (python subprocess controller)                          |
| - Process Watcher: Giám sát RAM, CPU, cưỡng chế ngắt (Kill Timeout)     |
+-------------------------------------------------------------------------+
                                    ↕
+-------------------------------------------------------------------------+
|                   TẦNG LƯU TRỮ NỘI BỘ (Local Storage)                   |
| - SQLite: Lưu lịch sử các đợt chấm, danh sách lớp, bộ testcase mẫu       |
| - File System: Lưu file log chi tiết của từng sinh viên                 |
+-------------------------------------------------------------------------+
```

---

## 6. Áp dụng 3 Mẫu thiết kế (Design Patterns) theo yêu cầu SWD392

Để đáp ứng tiêu chuẩn của môn học, 3 mẫu thiết kế được tích hợp trực tiếp vào nhân của tool:

1. **Factory Method (Creational Pattern) - `RunnerFactory`**:
   - Tự động tạo ra đối tượng Runner phù hợp (`CRunner`, `JavaRunner`, `PythonRunner`) dựa trên phần mở rộng của file bài nộp sinh viên (`.c`, `.java`, `.py`).
2. **Strategy Pattern (Behavioral Pattern) - `MatchingStrategy`**:
   - Cho phép giảng viên linh hoạt chọn cách so sánh kết quả:
     - `ExactMatchStrategy`: So sánh chính xác từng ký tự.
     - `IgnoreWhitespaceStrategy`: Bỏ qua khoảng trắng và dấu xuống dòng thừa.
     - `RegexMatchingStrategy`: So sánh bằng biểu thức chính quy.
     - `FloatingPointToleranceStrategy`: Cho phép sai số số thực (ví dụ sai số $10^{-6}$).
3. **Adapter Pattern (Structural Pattern) - `CompilerAdapter`**:
   - Tạo bộ chuyển đổi trung gian đồng nhất các lệnh biên dịch và trả về mã lỗi chuẩn cho các trình biên dịch khác nhau (`GCC/Clang` cho C, `Javac` cho Java, `Python Interpreter`).

---

## 7. Yêu cầu phi chức năng (Non-Functional Requirements)

1. **An toàn hệ thống (Security & Sandboxing)**:
   - Ngăn chặn triệt để mã độc sinh viên vô tình hoặc cố ý: Không cho phép truy cập trái phép file hệ thống, không cho phép mở cổng mạng tùy tiện, tự động diệt các process chạy quá thời gian (Anti-Fork Bomb).
2. **Hiệu năng cao (High Performance)**:
   - Hỗ trợ chấm song song đa luồng (Multi-threading): Chấm đồng thời 5-10 bài nộp trên máy có CPU nhiều nhân mà không làm đơ giao diện.
3. **Tiện dụng & Độc lập (Portability)**:
   - Đóng gói trọn gói dạng file cài đặt `.exe` độc lập cho Windows, không đòi hỏi cài đặt môi trường phức tạp.
