# Đặc Tả Công Nghệ Sử Dụng (Technology Stack)

## Dự án: AITA - Automated Grading Tool for Instructors

Tài liệu này quy định toàn bộ ngăn xếp công nghệ (Tech Stack), các thư viện bên thứ ba và công cụ nền tảng được sử dụng để xây dựng ứng dụng Desktop **AITA**.

---

## 1. Tổng Quan Ngăn Xếp Công Nghệ (Tech Stack Overview)

```text
+-------------------------------------------------------------------------+
|                  GIAO DIỆN DESKTOP (Desktop UI Layer)                   |
|  - Ngôn ngữ: Python 3.11+                                               |
|  - GUI Framework: PyQt6 / PySide6 (Chuẩn giao diện Desktop công nghiệp)  |
+-------------------------------------------------------------------------+
                                    ↕
+-------------------------------------------------------------------------+
|                  TẦNG XỬ LÝ LÕI (Core Processing Layer)                 |
|  - Quản lý tiến trình & Giám sát RAM/CPU: subprocess, psutil            |
|  - So khớp & Thuật toán: re, difflib, math                              |
|  - Xử lý file bài nộp: pathlib, zipfile, shutil                         |
|  - Báo cáo bảng điểm: openpyxl, pandas                                  |
+-------------------------------------------------------------------------+
                     ↕                                   ↕
+------------------------------------+  +--------------------------------+
|    CƠ SỞ DỮ LIỆU CỤC BỘ (Local DB) |  |   TRÍ TUỆ NHÂN TẠO (AI Engine) |
|  - SQLite (Module sqlite3 built-in)|  |  - Google Gemini API (Flash)   |
|  - Lưu lớp, testcase, lịch sử chấm |  |  - Thư viện: google-genai      |
+------------------------------------+  +--------------------------------+
```

---

## 2. Ngôn Ngữ & Giao Diện Người Dùng (Language & GUI)

### 2.1. Ngôn ngữ lập trình chính: **Python (>= 3.10)**

- **Lý do lựa chọn**:
  - Dễ dàng tích hợp với các thư viện AI hiện đại (Google Gemini SDK).
  - Khả năng xử lý chuỗi (String manipulation), phân tích cú pháp (Regex) và đọc/ghi file cực kỳ mạnh mẽ.
  - Hỗ trợ tốt việc tương tác sâu với hệ điều hành thông qua các module chuẩn.

### 2.2. Khung giao diện Desktop (GUI Framework): **PyQt6 / PySide6** (Đã chốt)

- **Mục đích**: Xây dựng giao diện máy tính chuẩn mực, hỗ trợ Dark/Light theme, khả năng phản hồi mượt mà và xử lý đa luồng qua `QThread`.

- **Tính năng giao diện**:
  - Chọn thư mục bài nộp của lớp dạng kéo thả (Drag & Drop).
  - Bảng hiển thị kết quả chấm theo thời gian thực (Real-time Progress Bar & Data Table).
  - Hỗ trợ giao diện sáng/tối (Dark / Light Theme).

---

## 3. Danh Mục Các Thư Viện Python Chuyên Dụng (Python Libraries)

| Tên thư viện                    | Phiên bản khuyến nghị | Mục đích sử dụng trong AITA                                                                                                                                                                                                        |
| :--------------------------------- | :-----------------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`psutil`**               |       `>= 5.9.0`       | **Giám sát tài nguyên hệ thống**: Đo lường dung lượng RAM tiêu thụ (bắt lỗi `MLE`), phần trăm CPU và cưỡng chế tắt tiến trình (Kill Process) khi bài sinh viên bị lặp vô hạn (bắt lỗi `TLE`). |
| **`subprocess`**           |         Built-in         | **Thực thi mã nguồn**: Gọi trình biên dịch `gcc` (cho C), `javac/java` (cho Java) và `python` để chạy bài nộp sinh viên trong môi trường tiến trình con độc lập.                                      |
| **`openpyxl`**             |       `>= 3.1.0`       | **Xuất báo cáo Excel**: Tạo file bảng điểm định dạng `.xlsx` chuyên nghiệp gồm cột Điểm số, Mã số sinh viên, Thời gian chạy và Nhận xét của giảng viên.                                             |
| **`pandas`**               |       `>= 2.0.0`       | **Xử lý dữ liệu bảng**: Lọc, sắp xếp danh sách bài nộp, tính điểm trung bình lớp và chuyển đổi dữ liệu kết quả chấm.                                                                                     |
| **`pathlib`**              |         Built-in         | **Thao tác đường dẫn**: Quản lý đường dẫn file đa nền tảng (Windows/macOS), tìm kiếm hàng loạt file `.c`, `.java`, `.py` trong thư mục bài nộp.                                                       |
| **`zipfile` & `shutil`** |         Built-in         | **Xử lý nén**: Tự động giải nén file `.zip` bài nộp sinh viên tải về từ hệ thống đào tạo (LMS/Coursera/Google Classroom).                                                                                    |
| **`difflib` & `re`**     |         Built-in         | **Động cơ so khớp kết quả**: So sánh từng ký tự giữa Actual Output và Expected Output, làm nổi bật (highlight) vị trí sai lệch và so khớp biểu thức chính quy Regex.                                       |
| **`pytest`**               |       `>= 7.4.0`       | **Kiểm thử tự động**: Viết và chạy bộ Unit Test, Integration Test theo đúng quy chuẩn kiểm thử của đồ án SWD392.                                                                                                |

---

## 4. Cơ Sở Dữ Liệu Nội Bộ: **SQLite (SQLite3)**

### 4.1. Lý do lựa chọn

- **Không cần cài đặt server**: SQLite lưu trữ toàn bộ CSDL vào một file duy nhất (`aita_database.db`) ngay trên máy tính giảng viên.
- **Tốc độ cực nhanh**: Phù hợp hoàn hảo cho ứng dụng Desktop Offline-first.
- **Có sẵn trong Python**: Không cần cài thêm driver phức tạp, sử dụng module chuẩn `sqlite3`.

### 4.2. Các bảng dữ liệu chính dự kiến:

1. **`classes`**: Thông tin lớp học, môn học (C, Java, Python, DSA, OOP), học kỳ.
2. **`students`**: Danh sách sinh viên (Mã SV, Họ tên, Lớp).
3. **`assignments`**: Thông tin bài tập (Tên bài, môn học, hạn nộp).
4. **`testcases`**: Bộ dữ liệu kiểm thử (Mã bài tập, Input, Expected Output, Time Limit ms, Memory Limit KB, Điểm của testcase).
5. **`submissions`**: Lịch sử nộp bài & kết quả chấm (Sinh viên, Thời gian nộp, Tổng điểm, Mã trạng thái AC/WA/TLE/CE/RE).
6. **`submission_details`**: Chi tiết kết quả từng testcase của một bài nộp.

---

## 5. Trí Tuệ Nhân Tạo: **Google Gemini API**

### 5.1. Thư viện tích hợp

- **Gói cài đặt**: `google-generativeai` (hoặc `google-genai`)
- **Mô hình khuyến nghị**: `gemini-1.5-flash` (tốc độ phản hồi dưới 1 giây, chi phí cực thấp, hỗ trợ context dài).

### 5.2. Các chức năng AI cụ thể trong AITA:

1. **Tự động sinh bộ Testcase biên (Edge Cases Generation)**:
   - *Đầu vào*: Đề bài tập do giảng viên nhập.
   - *Nhiệm vụ của Gemini*: Phân tích đề bài và sinh ra 5-10 bộ testcase đặc thù (Boundary values, mảng rỗng, chuỗi đặc biệt, số nguyên cực đại $2^{31}-1$).
2. **Viết nhận xét giải thích lỗi sư phạm (Code Feedback Generator)**:
   - *Đầu vào*: Đoạn code của sinh viên + Mã lỗi (Compile Error / Wrong Answer tại testcase số X).
   - *Nhiệm vụ của Gemini*: Chỉ ra dòng code sai logic và viết đoạn nhận xét ngắn gọn, mang tính định hướng để sinh viên tự sửa.
3. **Kiểm tra tương đồng & Phát hiện sao chép code (Plagiarism Detection)**:
   - *Nhiệm vụ của Gemini*: Đối chiếu cấu trúc logic giữa 2 bài nộp có điểm giống nhau bất thường để cảnh báo cho giảng viên các trường hợp đổi tên biến hoặc đảo hàm nhằm qua mặt.

---

## 6. Đóng Gói Bộ Cài Đặt (Packaging & Distribution)

- **Công cụ**: **`PyInstaller`**
- **Đầu ra**: Đóng gói toàn bộ mã nguồn Python, CSDL SQLite và giao diện thành **1 file thực thi duy nhất `.exe`** (hoặc bộ cài đặt Inno Setup) chạy độc lập trên hệ điều hành **Windows 10 / 11**.
- **Tiện ích cho giảng viên**: Giảng viên chỉ cần tải file `.exe` về, bấm đúp chuột là mở app chấm bài ngay, không cần cài đặt Python hay gõ lệnh terminal.

---

## 7. Tệp Cấu Hình Phụ Thuộc Mẫu (`requirements.txt`)

Khi khởi tạo môi trường lập trình, nhóm chỉ cần chạy lệnh `pip install -r requirements.txt`:

```text
# GUI Framework
PySide6>=6.5.0

# System Monitoring & Resource Limiting
psutil>=5.9.5

# Excel & Data Reporting
openpyxl>=3.1.2
pandas>=2.0.3

# AI Integration
google-generativeai>=0.3.2

# Testing
pytest>=7.4.0

# Packaging
pyinstaller>=6.0.0
```
