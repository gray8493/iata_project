# Tài Liệu Tổng Quan Dự Án (System Overview)
# AITA - Automated Grading & Assessment Tool for Instructors
### Công cụ Desktop App Hỗ trợ Giảng viên Chấm điểm Tự động các Môn Lập trình

---

## 1. Giới thiệu & Bối cảnh dự án (Project Background)

### 1.1. Bối cảnh bài toán
Trong công tác giảng dạy các môn lập trình nền tảng tại trường đại học (như Lập trình cơ sở PRF, Lập trình hướng đối tượng PRO, Cấu trúc dữ liệu và Giải thuật DSA, Lập trình Python PHP), giảng viên và trợ giảng (TA) thường xuyên phải đối mặt với số lượng bài tập thực hành rất lớn từ hàng trăm sinh viên mỗi kỳ. Việc chấm điểm thủ công từng bài gây ra nhiều bất cập:
- Mất rất nhiều thời gian biên dịch, nạp input và so sánh kết quả từng testcase.
- Dễ nhầm lẫn, không đồng nhất tiêu chí giữa các lần chấm.
- Khó kiểm soát thời gian chạy thực tế (Time Limit) và bộ nhớ tiêu thụ (Memory Limit).
- Khó phát hiện các trường hợp sinh viên sao chép mã nguồn của nhau.

### 1.2. Mục tiêu của dự án AITA
**AITA** là một ứng dụng Desktop chuyên nghiệp dành riêng cho **Giảng viên và Trợ giảng**, cho phép:
- Nạp danh sách sinh viên qua file CSV tinh gọn 2 cột (`MSSV`, `File`) và chọn thư mục bài nộp.
- Nạp bộ testcase linh hoạt bằng tay trên giao diện hoặc qua file cấu hình JSON.
- Tự động thực thi bài nộp với bộ testcase chuẩn và so khớp kết quả đầu ra theo 7 chiến lược (Strategy Pattern).
- Trả về bảng điểm chi tiết ngay lập tức (Pass/Fail từng testcase, thời gian chạy, mã lỗi biên dịch/thực thi).
- Tận dụng sức mạnh của **Google Gemini AI** để sinh testcase biên, phân tích lỗi code và viết nhận xét tự động điền thẳng vào file CSV kết quả.

---

## 2. Các môn học & Ngôn ngữ được hỗ trợ

Hệ thống được thiết kế theo mô hình mô-đun (Modular Runner), hỗ trợ linh hoạt các môn học và ngôn ngữ:

| Môn học | Ngôn ngữ hỗ trợ | Định dạng bài nộp tiếp nhận | Cơ chế biên dịch & Thực thi |
| :--- | :--- | :--- | :--- |
| **Lập trình cơ sở (PRF)** | **C** | Mã nguồn `.c` hoặc file build nhị phân `.exe` | Biên dịch qua `GCC/MinGW`, chạy subprocess có giới hạn Timeout. |
| **Cấu trúc dữ liệu & Giải thuật (DSA)** | **Java, Python** | File `.java`, `.class`, `.jar` hoặc `.py` | Đo lường thời gian thực thi (ms) và mức tiêu thụ bộ nhớ (RAM) cho từng thuật toán. |
| **Lập trình hướng đối tượng (PRO)** | **Java, Python** | File mã nguồn (`.java`, `.py`), package hoặc file nén `.zip` | Kiểm tra cấu trúc lớp, tính bao đóng, kế thừa, đa hình và chạy testcase kiểm thử chức năng. |
| **Lập trình Python (PHP)** | **Python** | Script `.py` | Thực thi trực tiếp qua Python Runtime trong môi trường an toàn. |

---

## 3. Quy trình 8 bước sử dụng thực tế của Giảng viên (User Flow)

Hệ thống được tối ưu hóa cho trải nghiệm của một Giảng viên qua 4 giai đoạn với 8 bước tuần tự:

```text
[GIAI ĐOẠN 1: THIẾT LẬP]
Bước 1: Mở app AITA (PyQt6/PySide6) & Chọn môn học
Bước 2: Nạp bộ Testcase (Nhập tay trên GUI VÀ/HOẶC Import file JSON)
Bước 3: Nạp file CSV (MSSV, File) & Chọn thư mục bài nộp

[GIAI ĐOẠN 2: CHẤM BÀI TỰ ĐỘNG]
Bước 4: Chọn 1 trong 7 chế độ so khớp (Matching Strategy)
Bước 5: Bấm "BẮT ĐẦU CHẤM" (Chấm song song 4-8 sinh viên cùng lúc)

[GIAI ĐOẠN 3: XEM KẾT QUẢ & SOI LỖI]
Bước 6: Xem bảng điểm trực quan & biểu đồ thống kê cả lớp
Bước 7: Bấm vào sinh viên bị lỗi để soi code & Xem nhận xét từ AI Gemini

[GIAI ĐOẠN 4: KẾT XUẤT]
Bước 8: Bấm "XUẤT BẢNG ĐIỂM CSV" hoàn chỉnh để nộp phòng đào tạo
```

### 3.1. Chuẩn hóa File CSV đầu vào (Input) & đầu ra (Output):
- **File CSV đầu vào do Giảng viên nạp** (ví dụ: `students.csv`): Chỉ gồm đúng **2 cột**:
  - Cột 1: `MSSV` (Mã số sinh viên, ví dụ: `SE180001`).
  - Cột 2: `File` (Tên file bài làm, ví dụ: `SE180001_Lab1.c`).
- **File CSV kết quả do Tool xuất ra** (ví dụ: `results.csv`): Giữ nguyên 2 cột trên và tự động bổ sung:
  - Cột 3: `Điểm số` (thang điểm 10).
  - Cột 4: `Số testcase đạt` (ví dụ: `9/10`).
  - Cột 5: `Trạng thái` (`AC`, `WA`, `TLE`, `MLE`, `CE`, `RE`).
  - Cột 6: `Thời gian chạy (ms)` trung bình.
  - Cột 7: `Nhận xét từ AI Gemini`: Gợi ý sư phạm chỉ rõ dòng code gây lỗi.

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

### 4.1. Nguyên lý chấm điểm cốt lõi (Core Judging Principle)
Hệ thống vận hành theo nguyên lý kiểm thử hộp đen (Black-box Testing) tinh gọn, nhất quán và chuẩn xác tuyệt đối:
- **Đầu vào kiểm thử**: Giảng viên **chỉ cần nhập cặp `INPUT` và `OUTPUT` kỳ vọng** (Expected Output) trực tiếp trên giao diện hoặc nạp từ file JSON. Giảng viên **hoàn toàn không cần phải viết hay cung cấp bất kỳ file code giải mẫu (solution)** nào.
- **Cơ chế thực thi & Luồng gọi hàm thông qua `main()`**:
  - Mọi chương trình nộp của sinh viên (C, Java, Python) đều có điểm khởi nhập là **hàm `main()`**.
  - Hàm `main()` chịu trách nhiệm nhận dữ liệu `INPUT` từ luồng nhập chuẩn (`stdin`) thông qua các lệnh đọc chuẩn (`scanf` trong C, `Scanner/BufferedReader` trong Java, `input()` trong Python).
  - Sau khi nhận dữ liệu, **hàm `main()` sẽ tự động truyền các đối số (arguments) vào các hàm con nghiệp vụ** (functions/methods do sinh viên tự định nghĩa) để tính toán, và in kết quả cuối cùng ra luồng xuất chuẩn (`stdout`) (`printf`, `System.out.println`, `print()`).
  - *Lợi ích kỹ thuật*: Hệ thống AITA **hoàn toàn không cần can thiệp hay bọc (wrap) mã nguồn của sinh viên**, không cần biết sinh viên đặt tên hàm con là gì, giúp loại bỏ triệt để lỗi xung đột mã nguồn và đảm bảo mã sinh viên được chạy nguyên bản 100%.
- **Quy chuẩn cấu trúc bài nộp (Duy nhất 1 dạng chuẩn mực)**:
  - **Mỗi câu hỏi là một file mã nguồn riêng biệt có hàm `main()` độc lập**: Trong các kỳ thi thực hành lập trình (như Practical Exam), bài làm luôn được tổ chức theo quy chuẩn mỗi câu là một file riêng (ví dụ: `Q1.c`, `Q2.c`, `Q3.c` với C; `Q1.java`, `Q2.java` với Java; `q1.py`, `q2.py` với Python).
  - **Cơ chế chấm từng câu & Tổng hợp điểm**:
    - Hệ thống tự động nhận diện từng file tương ứng với từng câu hỏi.
    - Lần lượt nạp `INPUT` của câu hỏi vào hàm `main()` của file đó, hứng `OUTPUT thực tế` và so khớp với `OUTPUT kỳ vọng` của giảng viên để chấm điểm cho câu đó.
    - Điểm cuối cùng của sinh viên là tổng điểm của tất cả các câu hỏi cộng lại (`Total Score = Score_Q1 + Score_Q2 + ...`).
- **Cơ chế phân định kết quả**: Thu nhận `OUTPUT thực tế` (`stdout`) của sinh viên và so sánh với `OUTPUT kỳ vọng` của giảng viên:
  - **Nếu `OUTPUT thực tế == OUTPUT của Giảng viên`**: Đánh giá là **ĐÚNG (Passed / AC)**.
  - **Nếu khác nhau**: Đánh giá là **SAI (Wrong Answer / WA)**.


---

### 4.2. Các năng lực AI hỗ trợ tăng cường & Cơ chế gọi thông minh (Smart AI Integration)
Tuân thủ đúng định hướng môn học **SWD392 (AI-Assisted System Design)**, AITA tích hợp Google Gemini AI theo cơ chế tối ưu hóa tài nguyên (Smart Resource Management) nhằm ngăn chặn triệt để tình trạng nghẽn mạng (Rate Limit 429), tiết kiệm hơn 95% chi phí token và đảm bảo tốc độ chấm bài siêu tốc:

1. **AI Auto-Generate Testcases (Tự động sinh bộ kiểm thử biên Input & Output)**:
   - Giảng viên chỉ cần dán nội dung đề bài (hoặc yêu cầu bài toán) vào ô nhập liệu trên Desktop App.
   - Gemini AI tự động phân tích nghiệp vụ đề bài để sinh ra danh sách 5-10 cặp **`INPUT` và `OUTPUT kỳ vọng`** hoàn chỉnh (bao gồm các testcase biên: số âm, mảng rỗng, giá trị cực đại, chuỗi đặc biệt).
   - Dữ liệu sinh ra tự động nạp thẳng vào bảng Testcase trên giao diện để giảng viên xem lại, tinh chỉnh hoặc sử dụng ngay mà **không cần viết code giải mẫu**.

2. **AI Code Review & Feedback Generator (Phân tích lỗi theo yêu cầu - On-Demand Lazy Loading)**:
   - **Không gọi tự động khi đang chấm hàng loạt**: Lúc chấm cả lớp, hệ thống tập trung toàn bộ CPU để chạy code sinh viên với tốc độ tối đa (10-15 giây xong 40 bài) và xuất ngay bảng điểm.
   - **Cơ chế kích hoạt theo yêu cầu (On-Demand)**: Khi giảng viên muốn soi bài của sinh viên bị sai (`WA`), chỉ cần bấm vào sinh viên đó rồi chọn **`[✨ AI Phân tích lỗi]`**. Lúc này hệ thống mới gửi duy nhất bài đó lên Gemini.
   - **Bỏ qua lỗi biên dịch (`CE`)**: Lỗi cú pháp đã có log chi tiết của trình biên dịch (`gcc`, `javac`), hệ thống không gửi lên AI để tránh lãng phí token vô ích.
   - Kết quả: Giảm số lượng request từ hàng trăm lượt xuống còn vài lượt theo đúng nhu cầu thực tế của giảng viên.

3. **AI Plagiarism Detection (Phát hiện gian lận qua cơ chế Lọc 2 vòng - Two-Stage Filtering)**:
   - **Vòng 1 - Lọc cục bộ 100% Offline (Không tốn token, chạy siêu tốc)**:
     - Hệ thống sử dụng thuật toán phân tích cây cú pháp trừu tượng (AST / Tokenization & Winnowing tương tự chuẩn MOSS của Stanford) chạy trực tiếp trên máy tính giảng viên.
     - Thuật toán chuẩn hóa code (loại bỏ tên biến, khoảng trắng, thứ tự khai báo) và tính toán phần trăm tương đồng giữa toàn bộ các cặp bài nộp trong lớp chỉ trong 0.5 giây.
   - **Vòng 2 - Chỉ gửi các cặp nghi vấn cao cho AI (Threshold > 80%)**:
     - Thay vì gửi toàn bộ hàng nghìn cặp bài lên AI (ví dụ lớp 40 sinh viên có 2.340 cặp/3 câu), hệ thống chỉ chọn lọc **1-3 cặp có độ tương đồng bất thường vượt ngưỡng (> 80%)**.
     - Gemini AI đóng vai trò chuyên gia phân tích chuyên sâu: Chỉ ra các vị trí đổi tên biến, đảo hàm, viết lại cấu trúc nhằm qua mặt giảng viên và đưa ra bằng chứng rõ ràng để lập biên bản.
   - Kết quả: Tiết kiệm 99.8% số lượt gọi AI, loại bỏ hoàn toàn nguy cơ sập quota API.

---

## 5. Kiến trúc hệ sinh thái tích hợp (Integrated System Architecture)

Hệ thống AITA được thiết kế thành một hệ sinh thái phần mềm tích hợp hoàn chỉnh gồm 3 thành phần chính theo đúng chuẩn đồ án SWD392:

```text
+------------------------------------+       +------------------------------------+
|  WEB ADMIN DASHBOARD (Next.js FE)  |       |   DESKTOP APP CLIENT (PyQt6/Python)|
|  - Dành cho Quản trị viên (Admin)  |       |  - Dành cho Giảng viên (Instructor)|
|  - Quản lý User, Môn học, Quota AI |       |  - Chấm bài CSV hàng loạt tốc độ cao|
|  - Giám sát hạn ngạch Gemini AI    |       |  - Chạy Sandbox Runner C/Java/Py   |
+------------------------------------+       +------------------------------------+
                  │                                             │
                  │ (HTTPS / RESTful API)                       │ (HTTPS / REST API & Sync)
                  ▼                                             ▼
+---------------------------------------------------------------------------------+
|                   WEB SERVER BACKEND (NestJS / TypeScript)                      |
|  - Tầng API Gateway & Định tuyến: NestJS Controllers & RESTful Endpoints        |
|  - Xác thực & Phân quyền (Auth & RBAC): Passport-JWT, Guards (@Roles)           |
|  - Quản lý nghiệp vụ: Quản lý Tài khoản Giảng viên, Danh mục Môn học, Hạn ngạch AI |
|  - Tích hợp AI Hub: Cầu nối điều phối hạn ngạch gọi Google Gemini API           |
|  - Cơ sở dữ liệu trung tâm: PostgreSQL trên Neon Serverless Cloud qua Prisma   |
+---------------------------------------------------------------------------------+
```

### 5.1. Ma trận Phân quyền người dùng (Role-Based Access Control - RBAC)

Web Admin Dashboard là hệ thống quản trị nội bộ **dành riêng cho Quản trị viên (Admin)**, không phải cổng thông tin học sinh. Hệ thống kiểm soát 2 vai trò người dùng có tài khoản:

| Chức năng hệ thống | Quản trị viên (Admin) | Giảng viên (Instructor) | Nơi thực hiện |
| :--- | :---: | :---: | :--- |
| **Đăng nhập hệ thống (Auth JWT)** | ✅ Đăng nhập Web Admin | ✅ Đăng nhập Desktop App | Web Backend API |
| **Quản lý tài khoản Giảng viên (Thêm/Sửa/Khóa)** | ✅ Toàn quyền | ❌ | Web Admin Dashboard |
| **Phân quyền hệ thống (Gán Role Admin/Instructor)** | ✅ | ❌ | Web Admin Dashboard |
| **Quản lý quota Gemini AI** | ✅ Qua API quản trị | ❌ | Web Admin Dashboard; Gemini API key do vận hành cấu hình bằng biến môi trường máy chủ |
| **Giám sát nhật ký sử dụng Token AI toàn trường** | ✅ Xem toàn bộ logs | ❌ | Web Admin Dashboard |
| **Nạp Testcase & Cấu hình bài tập** | ❌ | ✅ Toàn quyền trên lớp | Desktop App Client |
| **Chấm bài tự động từ file CSV (MSSV, File)** | ❌ | ✅ Chấm bài của lớp | Desktop App Client |
| **Chấm bài tập Web tự động (HTML/CSS/JS/PHP)** | ❌ | ✅ Chấm bài theo Rubric | Desktop App Client |
| **Xuất bảng điểm CSV kết quả (results.csv)** | ❌ | ✅ Xuất lớp phụ trách | Desktop App Client |

*(Lưu ý: Sinh viên không có tài khoản và không truy cập vào Web. Sinh viên chỉ là danh sách nạp từ file CSV mà Giảng viên thực hiện chấm điểm cục bộ. Bảng điểm và mã nguồn sinh viên được bảo vệ tuyệt đối trên máy tính cá nhân của Giảng viên - Local-First Data Privacy).*

---

### 5.2. Kiến trúc nội bộ của Desktop App Client (PyQt6)
Khi Giảng viên sử dụng Desktop App, ứng dụng vận hành theo mô hình Clean Architecture:
- **Tầng Giao diện (UI)**: PyQt6 / PySide6 hiện đại, xử lý đa luồng qua `QThread` để không đơ màn hình khi chấm bài.
- **Tầng Nghiệp vụ**: Động cơ so khớp 7 chế độ (`MatchingStrategy`), bộ thẩm định Rubric chấm Web 4 thành phần, quản lý đọc/ghi file CSV (`students.csv`, `results.csv`).
- **Tầng Thực thi an toàn & Trình duyệt (Sandbox & Web Runner Engine)**:
  - Subprocess cô lập gọi `gcc`, `java`, `python` kết hợp thư viện `psutil` để kiểm soát RAM (bắt `MLE`) và cưỡng chế kill khi quá giờ (bắt `TLE`).
  - Tích hợp `playwright` (Chromium Headless), `beautifulsoup4` (DOM parser) và `tinycss2` (W3C linter) để chấm điểm tự động bài tập Web (HTML/CSS/JS/PHP).
- **Tầng Kết nối Mạng & AI (Network & AI Gateway Client)**: Kết nối với Web Server Backend qua REST API để xác thực tài khoản và gọi dịch vụ Gemini AI (sinh testcase biên, review bài WA, phát hiện đạo văn vòng 2, đánh giá chất lượng giao diện Web).

---

### 5.3. Kiến trúc & Nhiệm vụ của Web Server Backend (NestJS & RBAC Engine)
Web Server Backend đóng vai trò "Bộ não trung tâm" kết nối và điều phối toàn bộ luồng dữ liệu của hệ sinh thái AITA:
1. **Dịch vụ RESTful API & Swagger UI**: Cung cấp các endpoint chuẩn mực, tự động sinh tài liệu kiểm thử tương tác tại `/api/docs` qua `@nestjs/swagger`.
2. **Cơ chế Phân quyền & Xác thực tập trung (Authentication & RBAC)**:
   - Cấp phát và thẩm định **JWT (JSON Web Token)** bằng `@nestjs/passport` và `@nestjs/jwt` với thời hạn sống an toàn (Access Token + Refresh Token).
   - Mã hóa mật khẩu một chiều chuẩn công nghiệp bằng **Bcrypt**.
   - Kiểm soát quyền truy cập tài nguyên thông qua NestJS Guards & Decorators (`@UseGuards(JwtAuthGuard, RolesGuard)`, `@Roles('admin')`).
3. **AI Hub & Hạn ngạch (Quota Management)**:
   - Lưu trữ bí mật Google Gemini API Key tại máy chủ, ngăn chặn lộ key ra phía client.
   - Kiểm soát số lượt gọi AI (Rate Limiting) và quota token hàng ngày/hàng tháng cho từng giảng viên.
4. **Bảo Mật Tập Trung & Nguyên Tắc Local-First (Neon PostgreSQL)**:
   - Lưu trữ an toàn danh mục môn học, tài khoản, cấu hình hạn ngạch và nhật ký kiểm toán AI.
   - Đảm bảo nguyên tắc bảo mật Local-First: Toàn bộ bảng điểm thi cử và mã nguồn sinh viên được lưu giữ cục bộ 100% trên máy Giảng viên, Backend không lưu giữ bài thi của sinh viên.

---

### 5.4. Các Phân Hệ Trên Trang Web Admin Quản Lý (Web Admin Management Dashboard)
Giao diện Web Admin chuyên dụng dành riêng cho Quản trị viên (Admin) với các phân hệ chức năng:
1. **Phân hệ Tổng quan (Executive Overview Dashboard)**:
   - Thống kê thời gian thực: Tổng số tài khoản, số lượt gọi AI đang hoạt động, biểu đồ tiêu thụ Token Gemini AI toàn trường.
2. **Phân hệ Quản trị Tài khoản & Phân quyền (User & Role Management)**:
   - Tạo mới, chỉnh sửa thông tin, đặt lại mật khẩu hoặc vô hiệu hóa tài khoản Giảng viên.
   - Gán quyền hệ thống (`Admin`, `Instructor`).
3. **Phân hệ Giám sát Hạn ngạch AI (AI Quota & Usage Monitor)**:
   - Xem chi tiết bảng tiêu thụ Token Gemini theo từng Giảng viên.
   - Cấu hình trần hạn ngạch (Quota limit) để tối ưu chi phí và tránh nghẽn API.
4. **Phân hệ Báo cáo & Kiểm Toán (Reports & Audit Logs)**:
   - Xem lịch sử kiểm toán các yêu cầu AI và xuất báo cáo tổng hợp.


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
