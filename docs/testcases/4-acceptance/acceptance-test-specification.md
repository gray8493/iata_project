# Thông Tin Chung Kiểm Thử Chấp Nhận (Acceptance Test Specification)

- **Cấp độ kiểm thử**: Acceptance Test (Kiểm thử chấp nhận người dùng - UAT)
- **Người thực hiện (Tester/Dev)**: Đinh Thành Nam
- **Ngày tạo**: 01/10/2026
- **Cập nhật lần cuối**: 01/10/2026 - 15:45
- **Tài liệu liên quan**:
  - [Tổng quan hệ thống AITA](file:///d:/SWD_Project/docs/architecture/system-overview.md)
  - [Đặc tả chi tiết Use Cases](file:///d:/SWD_Project/docs/architecture/use_case_descriptions.md)
  - [Quy tắc kiểm thử Testcase](file:///d:/SWD_Project/rules/testcase-rules.md)
  - [Quy tắc Git & Workflow](file:///d:/SWD_Project/rules/git-rules.md)
- **Tổng số Testcase**: 08 Testcases (05 Normal, 01 Boundary, 02 Exception)

---

# AT01_SubmissionIngestion_TC001: Nạp danh sách lớp từ file students.csv chuẩn 2 cột thành công

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Giảng viên đã tạo một đợt chấm bài mới trên Desktop App (`UC-07`).
- File `students.csv` nằm trong thư mục bài làm, chứa danh sách sinh viên gồm đúng 2 cột: `MSSV` và `File`.

#### Các bước thực hiện (Test Steps)
1. Giảng viên bấm nút **"Nạp Danh Sách Sinh Viên"** (`UC-08`).
2. Chọn đường dẫn đến file `students.csv`.
3. Hệ thống tiến hành phân tích cú pháp (parse) file và đối chiếu với các file bài nộp trong thư mục.

#### Kết quả kỳ vọng (Expected Result)
- Bảng danh sách sinh viên hiển thị đầy đủ thông tin: Mã sinh viên, tên file bài làm (`.c`, `.java`, `.py`).
- Cột trạng thái ban đầu hiển thị `Pending` (Sẵn sàng chấm).
- Hệ thống thông báo: "Đã nạp thành công X sinh viên sẵn sàng chấm bài".

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 01/10/2026 | Đinh Thành Nam | Nạp đầy đủ 45 sinh viên, ánh xạ đúng file bài làm | 95 ms | ✅ PASSED | Giao diện nạp mượt mà |

---

# AT01_SubmissionIngestion_TC002: Bật cảnh báo khi nạp file CSV sai cấu trúc hoặc thiếu cột bắt buộc

#### Loại test
Exception

#### Tiền điều kiện (Pre-condition)
- File CSV đầu vào bị thiếu cột `File` hoặc đặt sai tên tiêu đề cột (ví dụ: `ID, FileName`).

#### Các bước thực hiện (Test Steps)
1. Giảng viên chọn nạp file CSV bị sai cấu trúc cột.
2. Hệ thống kiểm tra định dạng dòng tiêu đề (Header row).

#### Kết quả kỳ vọng (Expected Result)
- Hệ thống từ chối nạp file, không làm crash ứng dụng.
- Bật hộp thoại cảnh báo lỗi thân thiện: "File CSV không đúng định dạng chuẩn. File bắt buộc phải có đúng 2 cột tiêu đề: 'MSSV' và 'File'. Vui lòng kiểm tra lại".

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 01/10/2026 | Đinh Thành Nam | Bật thông báo lỗi chi tiết, từ chối nạp file sai định dạng | 45 ms | ✅ PASSED | Kiểm soát đầu vào chặt chẽ |

---

# AT02_ExportGradebook_TC001: Xuất bảng điểm results.csv 7 cột chuẩn và file Excel có tô màu

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Đợt chấm đã hoàn tất điểm số cho toàn bộ sinh viên trong lớp (`UC-12`).

#### Các bước thực hiện (Test Steps)
1. Giảng viên nhấn nút **"Xuất Báo Cáo"** trên thanh công cụ (`UC-18`).
2. Chọn định dạng xuất: File CSV chuẩn `results.csv` và Bảng điểm Excel (`.xlsx`).
3. Chọn thư mục lưu file và nhấn **"Xác nhận xuất"**.

#### Kết quả kỳ vọng (Expected Result)
- File `results.csv` được tạo thành công với đầy đủ 7 cột chuẩn: `MSSV, File, Điểm số, Số test đạt, Trạng thái, Thời gian chạy trung bình, Nhận xét`.
- File Excel `.xlsx` mở lên trình bày đẹp mắt, tự động định dạng điều kiện tô màu xanh lá cho bài đạt điểm tối đa, màu đỏ cảnh báo cho bài 0 điểm/lỗi, có biểu đồ thống kê điểm.
- Hiển thị nút bấm tiện ích **"Mở Thư Mục"** cho phép mở ngay thư mục chứa file.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 01/10/2026 | Đinh Thành Nam | Xuất thành công cả 2 file, dữ liệu 7 cột và màu sắc Excel rất chuẩn | 380 ms | ✅ PASSED | Sẵn sàng nộp văn phòng khoa |

---

# AT02_ExportGradebook_TC002: Bắt lỗi quyền truy cập khi file Excel đích đang bị ứng dụng khác mở

#### Loại test
Exception

#### Tiền điều kiện (Pre-condition)
- File `results.xlsx` trong thư mục đích đang được mở sẵn bằng Microsoft Excel trên máy tính của Giảng viên.

#### Các bước thực hiện (Test Steps)
1. Trên Desktop App, Giảng viên bấm xuất báo cáo đè lên file `results.xlsx`.
2. Hệ thống thực hiện ghi đè file.

#### Kết quả kỳ vọng (Expected Result)
- Hệ thống bắt ngoại lệ quyền truy cập (`PermissionError: File is locked by another process`).
- Không làm crash phần mềm, hiển thị hộp thoại cảnh báo rõ ràng: "Không thể ghi file. File kết quả đang được mở bởi ứng dụng khác. Vui lòng đóng file Excel và thử lại".

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 01/10/2026 | Đinh Thành Nam | Bắt lỗi khóa file chính xác, cảnh báo rõ ràng | 60 ms | ✅ PASSED | Xử lý ngoại lệ I/O an toàn |

---

# AT03_PedagogicalAIReview_TC001: AI sinh nhận xét sư phạm gợi ý tư duy cho sinh viên bị sai logic

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Bài thi của sinh viên `SE180002` bị kết luận `WA` (Sai kết quả ở testcase số 3).
- Tài khoản Giảng viên còn hạn ngạch gọi AI.

#### Các bước thực hiện (Test Steps)
1. Giảng viên nhấp đúp vào dòng sinh viên `SE180002` trên bảng điểm để mở cửa sổ chi tiết bài nộp (`UC-14`).
2. Xem phần hiển thị khác biệt giữa đầu ra kỳ vọng và đầu ra thực tế.
3. Bấm nút **"AI Phân tích lỗi"** (`UC-16`).
4. Quan sát đoạn nhận xét do Google Gemini AI sinh ra.

#### Kết quả kỳ vọng (Expected Result)
- AI trả về đoạn văn bản nhận xét sư phạm ngắn gọn từ 3 đến 5 câu.
- **Tiêu chuẩn sư phạm**: Chỉ ra chính xác dòng code gây lỗi (ví dụ: dòng 18 quên cập nhật biến đếm), giải thích bản chất lỗi thuật toán và đưa ra câu hỏi gợi mở cho sinh viên tự sửa.
- **Cam kết an toàn**: Tuyệt đối không sinh ra toàn bộ đoạn code giải sẵn.
- Giảng viên có thể chỉnh sửa lại nội dung trước khi bấm nút **"Lưu nhận xét"**.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 01/10/2026 | Đinh Thành Nam | Nhận xét mang tính sư phạm cao, gợi ý đúng tư duy mà không giải hộ | 2.2 s | ✅ PASSED | Rất hữu ích cho sinh viên học tập |

---

# AT03_ManualScoreOverride_TC001: Giảng viên ghi đè điểm số thủ công kèm lý do giải trình

#### Loại test
Boundary

#### Tiền điều kiện (Pre-condition)
- Sinh viên có bài nộp bị chấm 0 điểm do in thừa một câu chào `printf("Hello")`, nhưng thuật toán xử lý cốt lõi hoàn toàn chính xác.

#### Các bước thực hiện (Test Steps)
1. Trong cửa sổ Chi tiết bài nộp (`UC-14`), Giảng viên bấm nút **"Ghi đè điểm thủ công"** (`UC-15`).
2. Nhập điểm số điều chỉnh: `8.5`.
3. Nhập lý do giải trình: "Sinh viên in thừa câu chào nhưng giải thuật tìm kiếm nhị phân đúng 100%".
4. Bấm **"Xác nhận ghi đè"**.

#### Kết quả kỳ vọng (Expected Result)
- Hệ thống lưu điểm số mới `8.5` vào SQLite cục bộ, đánh dấu cờ `is_overridden = True` kèm nội dung giải trình và thời điểm sửa.
- Trên bảng điểm chính, điểm của sinh viên được cập nhật sang `8.5` kèm biểu tượng cây bút để phân biệt điểm đã qua can thiệp của Giảng viên.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 01/10/2026 | Đinh Thành Nam | Điểm cập nhật ngay, lưu lý do minh bạch, hiện biểu tượng cây bút | 80 ms | ✅ PASSED | Tính năng can thiệp thủ công rất linh hoạt |

---

# AT04_AdminOverview_TC001: Quản trị viên xem Dashboard thống kê và giám sát quota AI toàn trường

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Quản trị viên đã đăng nhập thành công vào Web Admin Dashboard với quyền `ADMIN`.

#### Các bước thực hiện (Test Steps)
1. Truy cập trang chủ Web Admin Dashboard (`UC-05`).
2. Quan sát các thẻ thống kê tổng quan (Metrics cards) và biểu đồ tiêu thụ token.
3. Chuyển sang mục **"Giám Sát Hạn Ngạch AI"** (`UC-04`).

#### Kết quả kỳ vọng (Expected Result)
- Hiển thị đầy đủ số liệu tổng hợp toàn trường: Tổng số tài khoản giảng viên, tổng số bài đã chấm, tổng lượt gọi AI.
- Bảng giám sát quota hiển thị rõ ràng từng giảng viên: Số token đã dùng trong ngày, số token còn lại và tỷ lệ phần trăm hạn ngạch.
- Dữ liệu hiển thị trực quan, cập nhật theo thời gian thực từ CSDL trung tâm.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 01/10/2026 | Đinh Thành Nam | Thống kê số liệu trực quan, biểu đồ quota rõ ràng | 290 ms | ✅ PASSED | Quản trị hạn ngạch minh bạch |

---

# AT04_AdminSecurityRBAC_TC001: Giảng viên cố tình truy cập Web Admin bị từ chối bằng lỗi 403 Forbidden

#### Loại test
Exception

#### Tiền điều kiện (Pre-condition)
- Tài khoản người dùng có vai trò Giảng viên (`role = "instructor"`).

#### Các bước thực hiện (Test Steps)
1. Giảng viên sử dụng tài khoản của mình đăng nhập vào đường dẫn trang quản trị Web Admin.
2. Hoặc gửi request có gắn JWT Token của Giảng viên tới API quản trị `GET /api/v1/admin/users`.

#### Kết quả kỳ vọng (Expected Result)
- Backend kiểm tra phân quyền RBAC Guard, phát hiện tài khoản không có quyền `ADMIN`.
- Hệ thống chặn đứng truy cập, trả về mã lỗi `HTTP 403 Forbidden`.
- Giao diện Web hiển thị thông báo từ chối truy cập: "Bạn không có quyền hạn truy cập vào không gian làm việc của Quản trị viên".

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 01/10/2026 | Đinh Thành Nam | Chặn truy cập thành công, trả về 403 Forbidden chuẩn xác | 110 ms | ✅ PASSED | Phân quyền RBAC an toàn tuyệt đối |
