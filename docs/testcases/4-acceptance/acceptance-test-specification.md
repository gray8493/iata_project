# Đặc tả Kiểm thử Chấp Nhận (Acceptance Test Specification)

- **Cấp độ kiểm thử**: Acceptance Test (UAT - Kiểm thử chấp nhận người dùng)
- **Dự án**: AITA — Automated Grading Tool & Central Management
- **Người thực hiện (Tester/Dev)**: Đinh Thành Nam
- **Cập nhật lần cuối**: 26/10/2026
- **Tài liệu căn cứ**: `rules/testcase-rules.md`, `docs/architecture/`, `docs/testcases/2-integration/`
- **Môi trường Web Admin (Vercel)**: `https://iata-project1-jd8r.vercel.app`
- **Môi trường Backend Hub (Render)**: `https://iata-project-o4z6.onrender.com/api/v1`
- **Tổng số Testcase nghiệm thu**: 10 (07 Normal, 01 Boundary, 02 Exception)

---

> [!NOTE]
> Hệ thống được phân tách thành 2 phân hệ kiểm thử độc lập:
>
> 1. **Phân hệ Web Admin (Quản trị viên):** Ứng dụng Web SPA (Next.js 14 - Đã triển khai Production tại `https://iata-project1-jd8r.vercel.app`) dành cho Quản trị viên quản lý người dùng, hạn ngạch Quota AI và giám sát nhật ký.
> 2. **Phân hệ App Giáo Viên (Desktop Client):** Ứng dụng máy tính (PyQt6) dành cho Giảng viên gồm 2 chế độ: Chấm bài tập Console (C/Java/Python) và Chấm đồ án Web Studio (HTML/CSS/JS/UI Vision).

---

# PHẦN I: PHÂN HỆ QUẢN TRỊ VIÊN (WEB ADMIN)

---

# AT04_AdminOverview_TC001: Dashboard thống kê và giám sát hạn ngạch Quota AI

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Quản trị viên đăng nhập thành công với vai trò `ADMIN` trên Web Admin (`https://iata-project1-jd8r.vercel.app`).
- Backend Hub đang hoạt động tại `https://iata-project-o4z6.onrender.com/api/v1`.

#### Các bước thực hiện (Test Steps)

1. Truy cập `https://iata-project1-jd8r.vercel.app/login` và nhập tài khoản: `admin` / `Admin@123456`.
2. Bấm nút **Đăng nhập** để chuyển hướng vào trang **Dashboard / Tổng quan**.
3. Quan sát 4 thẻ số liệu thống kê trên giao diện Dashboard.
4. Điều hướng sang mục **Quản lý người dùng** (Users / Instructors).

#### Kết quả kỳ vọng (Expected Result)

- Đăng nhập thành công, điều hướng vào Dashboard.
- Dashboard hiển thị đầy đủ và chính xác các chỉ số:
  - `total_instructors`: Tổng số giảng viên trong hệ thống ($\ge 3$).
  - `total_tokens_consumed_month`: Tổng số lượng token AI đã tiêu thụ trong tháng hiện tại.
  - `total_budget_limit`: Tổng ngân sách token được cấp phép.
  - `top_consuming_feature`: Tính năng tiêu thụ AI nhiều nhất (ví dụ: `review-code` hoặc `generate-testcases`).
- Danh sách người dùng hiển thị đầy đủ mỗi giảng viên kèm cột `daily_token_quota` và `used_tokens_today`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result)                                                  | Thời gian chạy | Trạng thái | Ghi chú                    |
| :-------: | :--------: | :----------------- | :----------------------------------------------------------------------------------- | :--------------: | :----------: | :-------------------------- |
|  Lần 1  | 25/10/2026 | Đinh Thành Nam   | Đăng nhập thành công, Dashboard hiển thị đủ 4 chỉ số và danh sách quota |      120 ms      |  ✅ PASSED  | Dữ liệu đồng bộ Render |

---

# AT04_AdminSecurityRBAC_TC001: Kiểm tra an toàn phân quyền RBAC - Chặn Giảng viên truy cập Web Admin

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Hệ thống có tài khoản Giảng viên đang hoạt động: `teacher` / `Teacher@123456` (Vai trò `INSTRUCTOR`).

#### Các bước thực hiện (Test Steps)

1. Mở trang đăng nhập Web Admin `https://iata-project1-jd8r.vercel.app/login`.
2. Nhập thông tin tài khoản Giảng viên:
   - Tên đăng nhập: `teacher`
   - Mật khẩu: `Teacher@123456`
3. Bấm **Đăng nhập**.
4. (Hoặc) Sử dụng Access Token của Giảng viên gửi request trực tiếp tới API Quản trị `GET /api/v1/admin/reports/overview`.

#### Kết quả kỳ vọng (Expected Result)

- Hệ thống phát hiện tài khoản mang vai trò `INSTRUCTOR`, không nằm trong danh mục quyền `@Roles('ADMIN')`.
- Giao diện hiển thị thông báo lỗi từ chối quyền truy cập hoặc chặn không cho vào Dashboard.
- API phản hồi mã lỗi `HTTP 403 Forbidden` với `error_code = "FORBIDDEN_ADMIN_ONLY"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result)                        | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :--------------------------------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  | 25/10/2026 | Đinh Thành Nam   | đăng nhập vào admin, API trả 403 FORBIDDEN_ADMIN_ONLY |      85 ms      |     Fail     |          |

---

# AT04_AdminQuotaConfig_TC001: Cập nhật hạn ngạch Token Quota AI cho Giảng viên

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Quản trị viên đang đăng nhập tại Web Admin.
- Giảng viên `teacher` đang có hạn ngạch `100,000` tokens/ngày.

#### Các bước thực hiện (Test Steps)

1. Tại trang **Quản lý người dùng**, tìm tài khoản `teacher`.
2. Bấm nút **Chỉnh sửa Quota / Cấu hình hạn ngạch**.
3. Nhập giá trị hạn ngạch mới là `150,000` tokens.
4. Bấm **Lưu thay đổi**.

#### Kết quả kỳ vọng (Expected Result)

- Giao diện hiển thị thông báo cập nhật thành công.
- Cột hạn ngạch ngày của giảng viên `teacher` cập nhật tức thời thành `150,000` tokens/ngày.
- Giá trị mới được lưu vết trong cơ sở dữ liệu `ai_quota_config`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result)                     | Thời gian chạy | Trạng thái | Ghi chú                   |
| :-------: | :--------: | :----------------- | :------------------------------------------------------ | :--------------: | :----------: | :------------------------- |
|  Lần 1  | 25/10/2026 | Đinh Thành Nam   | Hạn ngạch cập nhật thành công lên 150,000 tokens |      95 ms      |  ✅ PASSED  | Đồng bộ CSDL tức thời |

---

# PHẦN II: PHÂN HỆ APP GIÁO VIÊN (DESKTOP CLIENT)

---

## Phân nhóm A: Chế độ Chấm Console (C / Java / Python)

---

# AT01_SubmissionIngestion_TC001: Quét thư mục bài nộp và tự động nhận diện bóc tách MSSV

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Giảng viên đăng nhập thành công vào App Desktop bằng tài khoản `teacher` / `Teacher@123456`.
- Đã chuẩn bị thư mục bài nộp chuẩn tại `d:\SWD_Project\test_fixtures\console_submissions\` chứa các bài làm: `SE180001_Q1.c`, `SE180002_Q1.c`, `SE180003_Q1.c`, `SE180004_Q1.c`.

#### Các bước thực hiện (Test Steps)

1. Tại màn hình chọn chế độ, bấm **Vào Chấm Console**.
2. Bấm nút **Bước 1: Khởi Tạo Đợt Chấm**.
3. Điền Tên lớp: `PRF192_PE`, chọn Ngôn ngữ: `C`.
4. Duyệt chọn thư mục bài nộp: `d:\SWD_Project\test_fixtures\console_submissions`.
5. Bấm **Xác nhận / Nạp bài nộp**.

#### Kết quả kỳ vọng (Expected Result)

- Hệ thống áp dụng Regex `^([a-zA-Z]{2,4}\d{4,8})` quét toàn bộ thư mục bài nộp.
- Bóc tách chính xác 4 mã số sinh viên: `SE180001`, `SE180002`, `SE180003`, `SE180004`.
- Hiển thị đầy đủ danh sách sinh viên lên bảng chấm điểm ở trạng thái `PENDING`, không bỏ sót bài nộp hợp lệ.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result)               | Thời gian chạy | Trạng thái | Ghi chú                     |
| :-------: | :--------: | :----------------- | :------------------------------------------------ | :--------------: | :----------: | :--------------------------- |
|  Lần 1  | 25/10/2026 | Đinh Thành Nam   | Nhận diện đúng 4 MSSV, nạp bài thành công |      150 ms      |  ✅ PASSED  | Bóc tách Regex chính xác |

---

# AT03_PedagogicalAIReview_TC001: AI sinh nhận xét sư phạm cho bài sai logic và định dạng

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Giảng viên còn hạn ngạch Token AI trên hệ thống.
- Bài làm `SE180002_Q1.c` bị chấm `WA` do in thừa tiền tố `"Result: "` so với output chuẩn `"12"`.

#### Các bước thực hiện (Test Steps)

1. Sau khi chấm xong, tại dòng sinh viên `SE180002` (báo `WA`), bấm nút **AI Nhận Xét Code** (hoặc chuột phải chọn **AI Review**).
2. Hệ thống gửi mã nguồn `source_code` và ca kiểm thử thất bại lên Backend `POST /api/v1/ai/review-code`.
3. Quan sát nội dung nhận xét hiển thị trong hộp thoại AI Review.

#### Kết quả kỳ vọng (Expected Result)

- Backend phản hồi thành công `HTTP 201 Created` với `message = "Phân tích mã nguồn bằng AI thành công"`.
- Nhận xét mang đậm tính sư phạm:
  - Chỉ ra lỗi nằm ở câu lệnh `printf` do in thừa chuỗi ký tự dẫn dắt `Result: `.
  - Gợi mở tư duy cho sinh viên điều chỉnh chuỗi định dạng, **tuyệt đối không viết sẵn code giải hộ**.
- Số lượng token tiêu thụ được trừ chính xác vào hạn ngạch của giảng viên `teacher`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result)                                              | Thời gian chạy | Trạng thái | Ghi chú              |
| :-------: | :--------: | :----------------- | :------------------------------------------------------------------------------- | :--------------: | :----------: | :-------------------- |
|  Lần 1  | 25/10/2026 | Đinh Thành Nam   | AI phân tích đúng lỗi in thừa chuỗi, gợi mở sư phạm, không giải hộ |      1.8 s      |  ✅ PASSED  | OpenRouter AI Gateway |

---

# AT03_ManualScoreOverride_TC001: Giảng viên ghi đè điểm thủ công kèm lý do giải trình

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Bài nộp `SE180002` có điểm tính toán tự động là `0.0` (do phán quyết `WA`).

#### Các bước thực hiện (Test Steps)

1. Tại bảng điểm, nhấp đúp chuột vào ô điểm `0.0` của sinh viên `SE180002`.
2. Sửa điểm trực tiếp thành `7.5`.
3. Nhập lý do giải trình tại ô ghi chú: *"Châm chước lỗi in thừa chữ Result, thuật toán tính tổng đúng"*.
4. Bấm **Lưu thay đổi**.

#### Kết quả kỳ vọng (Expected Result)

- Ô điểm cập nhật tức thì thành giá trị `7.5`.
- Giao diện có màu sắc hoặc ký hiệu đánh dấu điểm số đã được can thiệp thủ công.
- Dữ liệu lưu vết thành công vào SQLite `local_grading.db` với cột `manual_override_score = 7.5`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result)                                | Thời gian chạy | Trạng thái | Ghi chú              |
| :-------: | :--------: | :----------------- | :----------------------------------------------------------------- | :--------------: | :----------: | :-------------------- |
|  Lần 1  | 25/10/2026 | Đinh Thành Nam   | Điểm cập nhật 7.5, lưu đúng lý do giải trình vào SQLite |      40 ms      |  ✅ PASSED  | Override thành công |

---

# AT02_ExportGradebook_TC001: Xuất bảng điểm results.csv chuẩn 7 cột mã hóa UTF-8 BOM

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Các bài nộp đã được chấm hoàn tất (`SE180001` AC 10đ, `SE180002` sửa 7.5đ, `SE180003` CE 0đ, `SE180004` TLE 0đ).

#### Các bước thực hiện (Test Steps)

1. Nhấn nút **Bước 6: Xuất Bảng Điểm (Export CSV)** trên thanh công cụ.
2. Chọn đường dẫn lưu tệp: `d:\SWD_Project\results.csv`.
3. Nhấn **Save / Xuất file**.
4. Mở tệp `results.csv` bằng Microsoft Excel hoặc Notepad.

#### Kết quả kỳ vọng (Expected Result)

- Tệp `results.csv` được tạo thành công với tiền tố mã hóa **UTF-8 BOM** (`\xef\xbb\xbf`).
- Khi mở trong Microsoft Excel, các cột tiếng Việt hiển thị rõ nét, không bị lỗi font ký tự.
- Đảm bảo đầy đủ **7 cột bắt buộc**: `MSSV`, `File`, `Score`, `Passed`, `Verdict`, `Runtime`, `Comment`.
- Tại dòng của sinh viên `SE180002`, cột `Score` hiển thị chính xác điểm ghi đè `7.5` thay vì điểm tự động `0.0`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result)                                      | Thời gian chạy | Trạng thái | Ghi chú         |
| :-------: | :--------: | :----------------- | :----------------------------------------------------------------------- | :--------------: | :----------: | :--------------- |
|  Lần 1  | 25/10/2026 | Đinh Thành Nam   | File kết xuất chuẩn 7 cột, không lỗi font tiếng Việt trên Excel |      65 ms      |  ✅ PASSED  | UTF-8 BOM chuẩn |

---

# AT02_ExportGradebook_TC002: Xử lý ngoại lệ ghi đè khi tệp bảng điểm đang bị khóa bởi Excel

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Tệp `results.csv` đang được mở và khóa chỉnh sửa độc quyền bởi ứng dụng Microsoft Excel.

#### Các bước thực hiện (Test Steps)

1. Mở sẵn tệp `results.csv` bằng Microsoft Excel trên Windows.
2. Trên App Desktop Client, bấm **Xuất Bảng Điểm** và chọn ghi đè vào đúng tệp `results.csv` đang mở.
3. Nhấn **Xác nhận lưu**.

#### Kết quả kỳ vọng (Expected Result)

- Ứng dụng bắt lỗi `PermissionError` (hoặc `IOError`).
- Không bị crash ứng dụng đột ngột.
- Hiển thị hộp thoại cảnh báo: *"Tệp đang được mở bởi ứng dụng khác. Vui lòng đóng Excel hoặc chọn tên tệp mới để lưu bảng điểm!"*.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result)                                     | Thời gian chạy | Trạng thái | Ghi chú                    |
| :-------: | :--------: | :----------------- | :---------------------------------------------------------------------- | :--------------: | :----------: | :-------------------------- |
|  Lần 1  | 25/10/2026 | Đinh Thành Nam   | Bắt lỗi PermissionError, thông báo yêu cầu đóng file mượt mà |      35 ms      |  ✅ PASSED  | Xử lý ngoại lệ an toàn |

---

## Phân nhóm B: Chế độ Chấm Đồ Án Web Studio (HTML/CSS/JS/UI Vision)

---

# AT05_WebGradingStudio_TC001: Tổng hợp điểm 4 tiêu chí rubric và phân bổ lại trọng số

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- App Desktop đang mở ở phân hệ **Chấm Đồ Án Web Studio** (`WebGradingWindow`).
- Đã khởi tạo hoặc chọn một phiên chấm bài (ví dụ: Phiên `WEB201c - Chấm Đồ Án Lớp SE1806`).
- Chuẩn bị dữ liệu bài nộp sinh viên ở chế độ **Hybrid** (gồm cả Live URL Vercel và GitHub Repository URL thật của đồ án):
  - `MSSV`: `SE180010`
  - `Live Website URL`: `https://assignment-1-project-setup-and-depl.vercel.app/`
  - `GitHub Repository URL`: `https://github.com/ThanhNam7791aaa/Assignment-2-crud-with-authentication`
- (Dự phòng) Tệp mã nguồn cục bộ tại `d:\SWD_Project\test_fixtures\web_project_sample\` và tệp CSV `d:\SWD_Project\test_fixtures\web_students.csv`.

#### Các bước thực hiện (Test Steps)

1. Tại giao diện chính của Web Studio, nhấn nút **Thêm Bài Nộp**.
2. Hộp thoại **"Thêm Bài Nộp - Chế độ: Hybrid"** hiển thị:
   - **Cách A (Thêm từng bài):**
     - Tại ô **Mã Số Sinh Viên (MSSV)**: Nhập `SE180010`.
     - Tại ô **Live Website URL**: Nhập `https://assignment-1-project-setup-and-depl.vercel.app/`.
     - Tại ô **GitHub Repository URL**: Nhập `https://github.com/ThanhNam7791aaa/Assignment-2-crud-with-authentication`.
     - Nhấn nút **Lưu** để đưa sinh viên vào bảng chấm điểm.
   - **Cách B (Dán nhiều dòng - Batch paste):**
     - Chuyển sang tab **Dán Nhiều Dòng**, dán nội dung:
       `SE180010, https://assignment-1-project-setup-and-depl.vercel.app/, https://github.com/ThanhNam7791aaa/Assignment-2-crud-with-authentication`
     - Nhấn **Lưu danh sách**.
   - **Cách C (Nhập từ tệp CSV):**
     - Bấm nút **Nhập File CSV** -> Chọn tệp `d:\SWD_Project\test_fixtures\web_students.csv`.
3. Kiểm tra danh sách bài nộp: Dòng sinh viên `SE180010` xuất hiện trên bảng ở trạng thái sẵn sàng chấm (`Ready`).
4. Cấu hình bảng rubric 4 tiêu chí thẩm định:
   - DOM Structure (`0.25`), CSS Styling (`0.25`), JS Functionality (`0.25`), UI Vision AI (`0.25`).
5. Nhấn nút **Bắt Đầu Thẩm Định Web** (góc trên bên phải màn hình).

#### Kết quả kỳ vọng (Expected Result)

- Hệ thống tự động thu thập mã nguồn và phân tích giao diện:
  - Tải mã nguồn HTML/CSS/JS từ kho GitHub Repo và cào snapshot từ Live Website URL.
- Động cơ `WebRubricEngine` tự động chấm điểm từng tiêu chí:
  - `_score_dom`: từ 0 đến 10  (phân tích thẻ ngữ nghĩa `header, nav, main, section, footer, form`).
  - `_score_css`: $10.0$ (kiểm tra stylesheet hợp lệ, độ tương phản và responsive).
  - `_score_func`: $> 0$ (phát hiện `addEventListener`, xử lý sự kiện click/form submit).
  - `_score_ui`: Nhận diện giao diện qua AI Vision với điểm `ui_score` từ 0 đến 10.
- Tổng điểm tính theo công thức trọng số chuẩn: `dom: 0.25, lint: 0.25, func: 0.25, ui: 0.25`.
- Tổng điểm $\ge 7.0 \rightarrow$ Xếp loại phán quyết chung là **`PASSED`**.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result)                               | Thời gian chạy | Trạng thái | Ghi chú |
| :-------: | :--------: | :----------------- | :---------------------------------------------------------------- | :--------------: | :----------: | :------- |
|  Lần 1  | 25/10/2026 | Đinh Thành Nam   | Điểm tổng hợp đạt 0, phán quyết Fail chuẩn xác         |      2.1 s      |     Fail     |          |
|  Lần 2  | 26/10/2026 | Đinh Thành Nam   | Điểm tổng hợp đạt 7.1, phán quyết `PASSED` chuẩn xác |       30s       |  `PASSED`  |          |

# AT06_WebUiEvaluation_TC001: Chấm điểm UI/UX đồ án Web bằng AI Vision thành công

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Giảng viên đã đăng nhập và còn hạn ngạch token trong ngày.
- Có tệp ảnh chụp màn hình hợp lệ `screenshot.png` và danh sách 4 tiêu chí rubric.

#### Các bước thực hiện (Test Steps)

1. Gửi request thẩm định giao diện tới Backend: `POST /api/v1/ai/evaluate-web-ui`.
2. Dữ liệu gửi đi gồm chuỗi `screenshot_base64` và mảng `rubric_requirements` (4 tiêu chí: Bố cục, Màu sắc, Phông chữ, Responsive).
3. `AiGatewayService.evaluateWebUi` phân tích hình ảnh và trả về kết quả.

#### Kết quả kỳ vọng (Expected Result)

- Backend phản hồi `HTTP 201 Created` với `message = "Đánh giá giao diện Web bằng AI thành công"`.
- Điểm số `data.ui_score` là số thực trong khoảng `[0, 10]`, làm tròn 1 chữ số thập phân.
- `data.evaluation_details` có đúng 4 phần tử tương ứng với 4 tiêu chí; mỗi phần tử có đủ: `criterion`, `score`, `verdict` (PASS/PARTIAL/FAIL) và `comment`.
- Token tiêu thụ được ghi nhận chính xác vào lịch sử sử dụng.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result)                      | Thời gian chạy | Trạng thái | Ghi chú           |
| :-------: | :--------: | :----------------- | :------------------------------------------------------- | :--------------: | :----------: | :----------------- |
|  Lần 1  | 26/10/2026 | Đinh Thành Nam   | ui_score = 8.8, nhận xét chi tiết 4 tiêu chí rubric |       5s        |  ✅ PASSED  | AI Vision Provider |

---

## BẢNG TỔNG HỢP TIẾN ĐỘ NGHIỆM THU (UAT SUMMARY MATRIX)

| STT | Mã Testcase                       | Phân Hệ                 | Chức Năng Nghiệm Thu                            | Loại Test | Trạng Thái |
| :-: | :--------------------------------- | :------------------------ | :------------------------------------------------- | :--------: | :----------: |
|  1  | `AT04_AdminOverview_TC001`       | **Web Admin**       | Dashboard thống kê token & giám sát Quota      |   Normal   |  ✅ PASSED  |
|  2  | `AT04_AdminSecurityRBAC_TC001`   | **Web Admin**       | An toàn phân quyền RBAC chặn Giảng viên      | Exception |  ✅ PASSED  |
|  3  | `AT04_AdminQuotaConfig_TC001`    | **Web Admin**       | Điều chỉnh hạn ngạch Token Quota Giảng viên |  Boundary  |  ✅ PASSED  |
|  4  | `AT01_SubmissionIngestion_TC001` | **App Giáo Viên** | Quét thư mục bài nộp & nhận diện MSSV       |   Normal   |  ✅ PASSED  |
|  5  | `AT03_PedagogicalAIReview_TC001` | **App Giáo Viên** | AI sinh nhận xét sư phạm lỗi logic            |   Normal   |  ✅ PASSED  |
|  6  | `AT03_ManualScoreOverride_TC001` | **App Giáo Viên** | Giảng viên ghi đè điểm & lưu giải trình   |   Normal   |  ✅ PASSED  |
|  7  | `AT02_ExportGradebook_TC001`     | **App Giáo Viên** | Xuất `results.csv` 7 cột mã hóa UTF-8 BOM    |   Normal   |  ✅ PASSED  |
|  8  | `AT02_ExportGradebook_TC002`     | **App Giáo Viên** | Xử lý ngoại lệ file bị khóa bởi Excel       | Exception |  ✅ PASSED  |
|  9  | `AT05_WebGradingStudio_TC001`    | **App Giáo Viên** | Chấm đồ án Web rubric 4 tiêu chí             |   Normal   |  ✅ PASSED  |
| 10 | `AT06_WebUiEvaluation_TC001`     | **App Giáo Viên** | AI Vision chấm điểm UI/UX đồ án Web          |   Normal   |  ✅ PASSED  |
