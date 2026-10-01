# Thông Tin Chung Kiểm Thử Hệ Thống (System Test Specification)

- **Cấp độ kiểm thử**: System Test (Kiểm thử toàn bộ hệ thống AITA End-to-End)
- **Người thực hiện (Tester/Dev)**: Đinh Thành Nam
- **Ngày tạo**: 01/10/2026
- **Cập nhật lần cuối**: 01/10/2026 - 15:30
- **Tài liệu liên quan**:
  - [Tổng quan hệ thống AITA](file:///d:/SWD_Project/docs/architecture/system-overview.md)
  - [Đặc tả chi tiết Use Cases](file:///d:/SWD_Project/docs/architecture/use_case_descriptions.md)
  - [Quy tắc kiểm thử Testcase](file:///d:/SWD_Project/rules/testcase-rules.md)
  - [Quy tắc Git & Workflow](file:///d:/SWD_Project/rules/git-rules.md)
- **Tổng số Testcase**: 10 Testcases (06 Normal, 02 Boundary, 02 Exception)

---

# ST01_BatchGradingPipeline_TC001: Chấm bài thi C hàng loạt 45 sinh viên thành công dưới 30 giây

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Desktop App đã nạp danh sách 45 sinh viên từ file `students.csv`.
- Đợt chấm đã được cấu hình bộ 5 testcase chuẩn và chọn chiến lược `IgnoreWhitespaceStrategy`.
- Trình biên dịch GCC/MinGW đã được cấu hình sẵn sàng trên máy trạm.

#### Các bước thực hiện (Test Steps)
1. Trên màn hình điều khiển đợt chấm, kiểm tra danh sách 45 bài nộp ở trạng thái `Pending`.
2. Giảng viên bấm nút **"Bắt đầu chấm bài"** (`UC-12`).
3. Quan sát thanh tiến độ thời gian thực (Progress Bar) và bảng nhật ký log mini.
4. Đợi quá trình chấm hoàn tất và ghi nhận thời gian thực thi tổng thể.

#### Kết quả kỳ vọng (Expected Result)
- Luồng xử lý nền đa tiến trình (`ProcessPoolExecutor` 4-8 workers) kích hoạt mượt mà, không làm đơ giao diện UI.
- Toàn bộ 45 bài nộp được xử lý tuần tự qua hàm `main()`, tính đúng điểm và gán trạng thái `AC` hoặc `WA`.
- Thanh tiến độ đạt 100%, hiển thị hộp thoại thông báo hoàn tất: "Chấm xong 45 bài trong 18.2 giây".
- Toàn bộ kết quả điểm số được lưu vào SQLite cục bộ và hiển thị đầy đủ trên bảng điểm.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 01/10/2026 | Đinh Thành Nam | Chấm hoàn tất 45 bài nộp, bảng điểm cập nhật đúng 100% | 18.2 s | ✅ PASSED | Đạt mục tiêu hiệu năng offline |

---

# ST01_BatchGradingPipeline_TC002: Bắt lỗi vòng lặp vô hạn và cưỡng chế kill tiến trình quá 1000ms

#### Loại test
Exception

#### Tiền điều kiện (Pre-condition)
- Có bài nộp của sinh viên chứa lỗi vòng lặp vô hạn `while(1) { }` trong file `Q1.c`.
- Cấu hình thời gian chạy tối đa `Time Limit = 1000 ms`.

#### Các bước thực hiện (Test Steps)
1. Giảng viên nạp bài nộp chứa lỗi vô hạn vào hàng đợi chấm.
2. Bấm nút **"Bắt đầu chấm bài"**.
3. Sandbox khởi chạy subprocess thực thi binary và thư viện `psutil` theo dõi thời gian thực.

#### Kết quả kỳ vọng (Expected Result)
- Sau đúng 1000 ms, hệ thống tự động cưỡng chế kill tiến trình con đang chạy vòng lặp vô hạn.
- Gán phán quyết **TLE (Time Limit Exceeded)** cho câu hỏi đó, điểm câu hỏi = 0.0.
- Không gây treo hệ thống hay chiếm dụng 100% CPU của máy trạm. Quá trình chấm tự động chuyển sang bài tiếp theo.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 01/10/2026 | Đinh Thành Nam | Tiến trình bị kill chính xác ở mốc 1005 ms, gán verdict TLE | 1005 ms | ✅ PASSED | Sandbox bảo vệ tài nguyên an toàn |

---

# ST01_BatchGradingPipeline_TC003: Bắt lỗi đệ quy vô hạn hoặc tràn bộ nhớ RAM vượt 256MB

#### Loại test
Boundary

#### Tiền điều kiện (Pre-condition)
- Bài nộp của sinh viên chứa hàm đệ quy không có điểm dừng hoặc khai báo mảng tĩnh cực lớn vượt mức cấp phát bộ nhớ.
- Cấu hình giới hạn bộ nhớ `Memory Limit = 256 MB`.

#### Các bước thực hiện (Test Steps)
1. Giảng viên bấm chấm bài nộp có nguy cơ tràn bộ nhớ.
2. `psutil` theo dõi liên tục mức tiêu thụ RAM của tiến trình con.

#### Kết quả kỳ vọng (Expected Result)
- Khi mức tiêu thụ RAM chạm ngưỡng 256 MB, hệ thống ngắt ngay tiến trình để bảo vệ hệ điều hành.
- Gán trạng thái **MLE (Memory Limit Exceeded)**, điểm số = 0.0 kèm thông báo rõ ràng trong log chi tiết.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 01/10/2026 | Đinh Thành Nam | Bắt chính xác lỗi tràn RAM tại ngưỡng 256.2 MB, gán MLE | 310 ms | ✅ PASSED | Bắt lỗi bộ nhớ chính xác |

---

# ST01_BatchGradingPipeline_TC004: Xử lý lỗi biên dịch cú pháp và bỏ qua không gọi AI để tiết kiệm Token

#### Loại test
Exception

#### Tiền điều kiện (Pre-condition)
- Bài nộp sinh viên bị thiếu dấu chấm phẩy `;` hoặc sai cú pháp ngôn ngữ C khiến trình biên dịch không thể build ra file thực thi.

#### Các bước thực hiện (Test Steps)
1. Giảng viên bấm chấm bài nộp bị lỗi cú pháp.
2. Trình biên dịch GCC thực hiện build mã nguồn và trả về mã lỗi khác 0 kèm log `stderr`.

#### Kết quả kỳ vọng (Expected Result)
- Hệ thống nhận diện lỗi biên dịch, gán ngay trạng thái **CE (Compile Error)**, cho điểm = 0.0.
- Lưu lại toàn bộ đoạn log lỗi từ `stderr` của compiler để giảng viên xem lại.
- **Quy tắc vàng**: Hệ thống không gửi yêu cầu phân tích lỗi lên Gemini AI để tránh lãng phí token vô ích.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 01/10/2026 | Đinh Thành Nam | Gán verdict CE ngay lập tức, lưu stderr, không kích hoạt AI | 85 ms | ✅ PASSED | Tiết kiệm token đúng thiết kế |

---

# ST02_AITestcaseGen_TC001: Tự động sinh 5 đến 10 cặp testcase biên bằng Gemini AI

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Giảng viên đã đăng nhập tài khoản hợp lệ trên Desktop App (có mã JWT Token).
- Tài khoản giảng viên còn hạn ngạch gọi AI trên Web Server Backend.

#### Các bước thực hiện (Test Steps)
1. Mở màn hình Quản lý Testcase, chọn đợt chấm môn `PRF192`.
2. Dán nội dung đề bài: "Viết chương trình nhập số nguyên N, kiểm tra số nguyên tố và in ra YES hoặc NO".
3. Nhấn nút **"Sinh Testcase bằng AI"** (`UC-10`).
4. Quan sát bảng duyệt trước (Preview Table) do hệ thống hiển thị.
5. Giảng viên tick chọn các testcase đạt yêu cầu và nhấn nút **"Lưu bộ Testcase"**.

#### Kết quả kỳ vọng (Expected Result)
- Backend kiểm tra hạn ngạch hợp lệ, chuyển tiếp prompt sang Google Gemini API.
- Gemini trả về danh sách từ 5 đến 10 testcase dạng JSON gồm đầy đủ các trường hợp biên: số âm (-5), số 0, số 1, số nguyên tố chẵn (2), giá trị cực đại (1000000).
- Sau khi giảng viên bấm lưu, toàn bộ testcase được nạp thành công vào SQLite cục bộ và sẵn sàng cho đợt chấm.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 01/10/2026 | Đinh Thành Nam | Sinh thành công 8 cặp testcase biên bao phủ mọi trường hợp | 2.1 s | ✅ PASSED | Testcase AI sinh ra rất chuẩn xác |

---

# ST02_AITestcaseGen_TC002: Bắt lỗi khi hết hạn ngạch AI và thông báo chuyển sang nhập thủ công

#### Loại test
Exception

#### Tiền điều kiện (Pre-condition)
- Hạn ngạch gọi AI hàng ngày của tài khoản Giảng viên đã chạm trần (0 tokens remaining).

#### Các bước thực hiện (Test Steps)
1. Giảng viên nhập đề bài và bấm nút **"Sinh Testcase bằng AI"**.
2. Desktop App gửi request `POST /api/v1/ai/generate-testcases` lên Backend.

#### Kết quả kỳ vọng (Expected Result)
- Backend kiểm tra hạn ngạch và phản hồi mã lỗi `HTTP 429 Too Many Requests`.
- Desktop App bắt mã lỗi và hiển thị hộp thoại thông báo màu vàng: "Hạn ngạch AI của bạn hôm nay đã hết. Vui lòng liên hệ Admin hoặc sử dụng tính năng nạp testcase thủ công".
- Ứng dụng không bị crash, mở sẵn form nhập testcase thủ công (`UC-09`).

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 01/10/2026 | Đinh Thành Nam | Bắt lỗi 429 mượt mà, hiển thị cảnh báo thân thiện | 150 ms | ✅ PASSED | Cơ chế bảo vệ quota an toàn |

---

# ST03_PlagiarismDetection_TC001: Quét đạo văn Vòng 1 bằng cây cú pháp AST 100% offline dưới 1 giây

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Đợt chấm có 40 bài nộp của cùng một câu hỏi lập trình.
- Mã nguồn các bài thi đã được tải về máy trạm.

#### Các bước thực hiện (Test Steps)
1. Trên thanh công cụ, Giảng viên nhấn nút **"Quét Đạo Văn"** (`UC-17`).
2. Thiết lập ngưỡng cảnh báo tương đồng mặc định từ 80% trở lên.
3. Nhấn nút **"Bắt đầu phân tích"**.

#### Kết quả kỳ vọng (Expected Result)
- Thuật toán bóc tách cây cú pháp trừu tượng (AST) và so khớp Winnowing chạy 100% offline trên máy tính giảng viên.
- Quét đối chiếu toàn bộ các cặp bài thi trong lớp (gần 800 cặp bài) chỉ trong thời gian dưới 1 giây mà không gọi mạng hay tiêu tốn token AI.
- Hiển thị ma trận tương đồng (Similarity Matrix) sắp xếp theo thứ tự phần trăm giảm dần.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 01/10/2026 | Đinh Thành Nam | Hoàn thành quét 780 cặp bài trong 0.48 giây, không tốn token | 0.48 s | ✅ PASSED | Tốc độ quét AST cực kỳ ấn tượng |

---

# ST03_PlagiarismDetection_TC002: Vòng 2 kích hoạt Gemini AI phân tích ngữ nghĩa cặp bài nghi vấn vượt 80%

#### Loại test
Boundary

#### Tiền điều kiện (Pre-condition)
- Kết quả quét Vòng 1 phát hiện 1 cặp bài nộp (`SE180001` và `SE180015`) có độ tương đồng 86%.

#### Các bước thực hiện (Test Steps)
1. Giảng viên bấm vào cặp bài nghi vấn vượt ngưỡng 80% có gắn cờ đỏ cảnh báo.
2. Giảng viên nhấn nút **"AI Phân tích bằng chứng"** (Vòng 2).
3. Backend chuyển tiếp cấu trúc mã nguồn 2 bài thi sang Google Gemini AI.

#### Kết quả kỳ vọng (Expected Result)
- Gemini AI phân tích ngữ nghĩa, vạch trần các thủ thuật: đổi tên biến, đảo vị trí hàm và chèn code rác.
- Trả về biên bản tóm tắt bằng chứng sao chép chi tiết.
- Desktop App mở màn hình đối chiếu song song hai bên (Side-by-side Diff Viewer) có tô sáng màu đỏ các đoạn code trùng khớp phục vụ lập biên bản thi cử.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 01/10/2026 | Đinh Thành Nam | AI chỉ rõ 3 đoạn code đảo hàm và đổi tên biến, Diff Viewer tô màu rõ ràng | 2.4 s | ✅ PASSED | Bằng chứng đối chiếu rất thuyết phục |

---

# ST04_CloudSync_TC001: Đồng bộ kết quả đợt chấm từ Desktop App lên Central Backend qua REST API

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Đợt chấm đã hoàn tất điểm số cho toàn bộ sinh viên trên máy trạm.
- Máy tính có kết nối Internet và phiên đăng nhập hợp lệ với JWT Token.

#### Các bước thực hiện (Test Steps)
1. Giảng viên nhấn nút **"Đồng bộ lên Cloud"** trên thanh công cụ (`UC-19`).
2. Quan sát quá trình gửi request và phản hồi từ máy chủ trung tâm.

#### Kết quả kỳ vọng (Expected Result)
- Desktop App đóng gói toàn bộ bảng điểm, mã lỗi verdict và nhật ký thành payload JSON gửi `POST /api/v1/sync/grading-session`.
- Backend tiếp nhận, xác thực token và lưu đợt chấm vào CSDL trung tâm qua SQLAlchemy ORM.
- Backend phản hồi `HTTP 200 OK` kèm `sync_id`.
- Desktop App đổi trạng thái sang biểu tượng đám mây màu xanh kèm mốc thời gian đồng bộ thành công.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 01/10/2026 | Đinh Thành Nam | Đồng bộ thành công 45 bài nộp lên CSDL trung tâm | 420 ms | ✅ PASSED | Dữ liệu toàn vẹn trên máy chủ |

---

# ST04_CloudSync_TC002: Xử lý ngoại lệ mất kết nối mạng khi đồng bộ và bảo vệ an toàn dữ liệu cục bộ

#### Loại test
Exception

#### Tiền điều kiện (Pre-condition)
- Máy tính của Giảng viên bị ngắt kết nối Internet (mất mạng LAN / Wifi).

#### Các bước thực hiện (Test Steps)
1. Giảng viên bấm nút **"Đồng bộ lên Cloud"**.
2. Hệ thống kiểm tra kết nối mạng và cố gắng kết nối tới Backend Gateway.

#### Kết quả kỳ vọng (Expected Result)
- Hệ thống bắt ngoại lệ mạng `ConnectionError`, không gây treo hay crash ứng dụng.
- Hiển thị hộp thoại cảnh báo: "Không thể kết nối đến máy chủ trung tâm. Dữ liệu của bạn vẫn được lưu an toàn trên máy cục bộ. Vui lòng thử đồng bộ lại khi có mạng".
- Toàn bộ điểm số trong SQLite cục bộ được giữ nguyên vẹn 100%.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 01/10/2026 | Đinh Thành Nam | Bắt lỗi mất mạng chuẩn xác, dữ liệu SQLite hoàn toàn an toàn | 200 ms | ✅ PASSED | Ứng phó mất mạng rất tốt |
