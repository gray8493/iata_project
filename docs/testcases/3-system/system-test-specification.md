# Đặc tả Kiểm thử Hệ thống (System Test Specification)

- **Cấp độ kiểm thử**: System Test
- **Người thực hiện (Tester/Dev)**: Đinh Thành Nam
- **Cập nhật lần cuối**: 21/10/2026
- **Tài liệu liên quan**: `rules/testcase-rules.md`, `docs/architecture/`
- **Tổng số Testcase**: 30 Testcases (12 Normal, 13 Boundary, 05 Exception)
  - Phân hệ Desktop Client (ST01, ST04, ST05): 26 Testcases (09 Normal, 12 Boundary, 05 Exception)
  - Phân hệ Central Backend (ST02 - ST03): 04 Testcases (02 Normal, 01 Boundary, 01 Exception)

---

# ST01_TestcaseImport_TC001: Nạp nội dung đề bài từ file .docx vào ô Prompt AI thành công

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Ứng dụng Desktop Client đang mở màn hình `AiTestcaseDialog`.
- File đề bài Word `.docx` tồn tại và hợp lệ.

#### Các bước thực hiện (Test Steps)
1. Giảng viên bấm nút "Nhập Từ File Đề Bài".
2. Chọn file `de_bai.docx` chứa các đoạn văn đề bài.

#### Kết quả kỳ vọng (Expected Result)
- Nội dung văn bản trong file Word được đổ chính xác vào ô `txt_prompt`.
- Tên tệp hiển thị đầy đủ trên nhãn `lbl_doc_name`.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 17/10/2026 | Pytest Runner | Đổ nội dung Word vào ô prompt chuẩn xác | 15 ms | ✅ PASSED | PyQt6 Offscreen |

---

# ST01_TestcaseImport_TC002: Nối thêm nội dung khi ô Prompt đã có dữ liệu

#### Loại test
Boundary

#### Tiền điều kiện (Pre-condition)
- Ô `txt_prompt` đang chứa sẵn một phần nội dung đề bài cũ.

#### Các bước thực hiện (Test Steps)
1. Bấm nút nhập file và chọn file `de_bai.txt`.
2. Khi hộp thoại hỏi "Ghi đè hay Nối thêm", chọn "No" (Nối thêm).

#### Kết quả kỳ vọng (Expected Result)
- Nội dung mới được nối tiếp vào cuối nội dung cũ mà không làm mất dữ liệu đang soạn.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 17/10/2026 | Pytest Runner | Nối thêm chuỗi chính xác | 8 ms | ✅ PASSED | PyQt6 Offscreen |

---

# ST01_TestcaseImport_TC003: Cắt ngắn đề bài vượt quá giới hạn 5000 ký tự của Backend

#### Loại test
Boundary

#### Tiền điều kiện (Pre-condition)
- File đề bài chứa chuỗi văn bản dài trên 5000 ký tự (ví dụ: 6000 ký tự).

#### Các bước thực hiện (Test Steps)
1. Nhập file văn bản dung lượng lớn vào dialog.

#### Kết quả kỳ vọng (Expected Result)
- Hệ thống hiển thị hộp thoại cảnh báo "Đề Bài Quá Dài".
- Nội dung trong ô `txt_prompt` tự động cắt đúng 5000 ký tự đầu tiên để đảm bảo hợp lệ khi gửi API.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 17/10/2026 | Pytest Runner | Cắt đúng 5000 ký tự, bật thông báo | 10 ms | ✅ PASSED | PyQt6 Offscreen |

---

# ST01_TestcaseImport_TC004: Cảnh báo khi nạp định dạng file không hỗ trợ (.doc)

#### Loại test
Exception

#### Tiền điều kiện (Pre-condition)
- Người dùng chọn file Word nhị phân cũ `.doc`.

#### Các bước thực hiện (Test Steps)
1. Bấm nút chọn file `de_bai.doc`.

#### Kết quả kỳ vọng (Expected Result)
- Hiển thị hộp thoại cảnh báo định dạng không hỗ trợ.
- Ô `txt_prompt` giữ nguyên trạng thái cũ, không nạp rác nhị phân.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 17/10/2026 | Pytest Runner | Bật cảnh báo, bảo toàn ô prompt | 6 ms | ✅ PASSED | PyQt6 Offscreen |

---

# ST01_TestcaseImport_TC005: Người dùng hủy hộp thoại chọn file

#### Loại test
Exception

#### Tiền điều kiện (Pre-condition)
- Dialog chọn file xuất hiện.

#### Các bước thực hiện (Test Steps)
1. Bấm nút "Cancel" hoặc đóng hộp thoại chọn tệp.

#### Kết quả kỳ vọng (Expected Result)
- Không có lỗi ngoại lệ (No-op), trạng thái giao diện được giữ nguyên vẹn.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 17/10/2026 | Pytest Runner | Xử lý no-op an toàn | 5 ms | ✅ PASSED | PyQt6 Offscreen |

---

# ST02_AITestcaseGen_TC001: Sinh bộ testcase bằng AI OpenRouter thành công

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Giảng viên có JWT Token hợp lệ và còn hạn ngạch AI.
- `OPENROUTER_API_KEYS` đã được cấu hình; nhà cung cấp AI phản hồi JSON hợp lệ.

#### Các bước thực hiện (Test Steps)
1. Giảng viên gửi `POST /api/v1/ai/generate-testcases` với `count = 3`.
2. `OpenRouterService` giữ chỗ hạn ngạch, gọi nhà cung cấp và nhận JSON.
3. `AiGatewayService.generateTestcases` kiểm tra số lượng và định dạng từng testcase.

#### Kết quả kỳ vọng (Expected Result)
- Trả về `message = "Sinh testcase tự động bằng AI thành công"`.
- `data.testcases` có đúng `count` phần tử, mỗi phần tử đủ `input`, `expected_output`, `explanation`, `is_boundary`.
- `data.tokens_consumed` bằng tổng token do nhà cung cấp trả về.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 17/10/2026 | Đinh Thành Nam | Sinh đúng 3 testcase, kiểm tra định dạng đạt | 12 ms | ✅ PASSED | Service-level, provider được mock |

---

# ST02_AITestcaseGen_TC002: Chặn khi hết hạn ngạch AI trong ngày

#### Loại test
Exception

#### Tiền điều kiện (Pre-condition)
- Hạn ngạch AI hàng ngày của giảng viên đã chạm trần.

#### Các bước thực hiện (Test Steps)
1. Giảng viên gửi `POST /api/v1/ai/generate-testcases`.
2. `AiQuotaService.reserve` phát hiện `usedTokensToday + amount > dailyTokenLimit`.

#### Kết quả kỳ vọng (Expected Result)
- Backend phản hồi `HTTP 429` với `error_code = "AI_QUOTA_EXCEEDED"`.
- Yêu cầu **không** được chuyển tiếp tới nhà cung cấp AI (không tiêu tốn token).

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 17/10/2026 | Đinh Thành Nam | Ném 429 AI_QUOTA_EXCEEDED, không gọi provider | 8 ms | ✅ PASSED | Bảo vệ quota hiệu quả |

---

# ST03_PlagiarismVong2_TC001: AI phân tích ngữ nghĩa cặp bài nghi vấn (Vòng 2)

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Vòng 1 (Desktop, offline AST) đã phát hiện cặp bài vượt ngưỡng.
- Giảng viên còn hạn ngạch AI.

#### Các bước thực hiện (Test Steps)
1. Giảng viên gửi `POST /api/v1/ai/verify-plagiarism` với mã nguồn 2 bài.
2. `OpenRouterService` giữ chỗ hạn ngạch và gọi provider.
3. `AiGatewayService.verifyPlagiarism` kiểm tra cấu trúc JSON trả về.

#### Kết quả kỳ vọng (Expected Result)
- Trả về `message = "Phân tích bằng chứng đạo văn thành công"`.
- `data` gồm `ket_luan` (string tiếng Việt), `do_tin_cay` trong [0,100], `bang_chung` (mảng `{mo_ta, dong_a[2], dong_b[2]}`), `khac_biet`, `de_xuat` đúng cấu trúc.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 17/10/2026 | Đinh Thành Nam | Trả về bằng chứng 2 đoạn sao chép, confidence 86% | 10 ms | ✅ PASSED | Provider được mock |

---

# ST03_PlagiarismVong2_TC002: Giá trị biên ngưỡng tương đồng AST

#### Loại test
Boundary

#### Tiền điều kiện (Pre-condition)
- DTO `VerifyPlagiarismDto` yêu cầu `ast_similarity_percentage` trong khoảng [80, 100].

#### Các bước thực hiện (Test Steps)
1. Gửi payload với `ast_similarity_percentage = 80` (biên dưới hợp lệ).
2. Gửi payload với `ast_similarity_percentage = 100` (biên trên hợp lệ).
3. Gửi payload với `ast_similarity_percentage = 79` (dưới biên).

#### Kết quả kỳ vọng (Expected Result)
- 80 và 100 hợp lệ (đi qua ValidationPipe).
- 79 bị từ chối `HTTP 422` với `error_code = "VALIDATION_FAILED"`, `details[].field = "ast_similarity_percentage"`.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 17/10/2026 | Đinh Thành Nam | 80/100 hợp lệ, 79 trả 422 VALIDATION_FAILED | 6 ms | ✅ PASSED | Kiểm tra biên DTO |

---

# ST04_WebGrading_TC001: Nhập thư mục bài nộp Web và nhận diện đúng MSSV + link

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Ứng dụng Desktop Client đang mở màn hình `WebGradingMainWindow` (Web Studio).
- Thư mục gốc `WebSub/` chứa 2 thư mục con `SE180001/`, `SE180002/`, mỗi thư mục có `links.txt` ghi Live URL và GitHub Repo.

#### Các bước thực hiện (Test Steps)
1. Bấm "Chọn Thư Mục Bài Nộp" và chọn thư mục gốc `WebSub/`.
2. Quan sát bảng xem trước trong `WebFolderImportDialog` (MSSV, File link, Live URL, GitHub Repo, Trạng Thái).
3. Bấm "Nạp Các Bài Hợp Lệ".

#### Kết quả kỳ vọng (Expected Result)
- Mỗi thư mục con được nhận diện đúng MSSV; trạng thái "Đủ link".
- Sau khi nạp, bảng điểm chính hiển thị đúng 2 bài với Live URL và GitHub Repo tương ứng.
- Bản ghi được lưu vào bảng `local_web_submissions` với `course_code`/`class_name` đang chọn.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 18/10/2026 | Pytest Runner | Nhận diện + nạp đúng 2 bài, lưu đủ URL | 22 ms | ✅ PASSED | `test_web_rubric_service.py` |

---

# ST04_WebGrading_TC002: Thư mục sai mẫu MSSV và thiếu file link (Biên)

#### Loại test
Boundary

#### Tiền điều kiện (Pre-condition)
- Thư mục gốc chứa: `SE18001/` (thiếu 1 chữ số), `NguyenVanA/` (không phải MSSV), `SE180003/` (không có file `.txt`), và `SE180004/links.txt` hợp lệ.

#### Các bước thực hiện (Test Steps)
1. Chọn thư mục gốc; để tùy chọn "Thư mục sai mẫu MSSV: Bỏ qua".
2. Quan sát cột Trạng Thái và khung "Báo cáo nhận diện".
3. Bấm "Nạp Các Bài Hợp Lệ"; sau đó mở lại và bấm "Nạp Tất Cả (kể cả bài thiếu link)".

#### Kết quả kỳ vọng (Expected Result)
- `SE18001`, `NguyenVanA` báo "không phải MSSV hợp lệ"; `SE180003` báo "Thiếu file link".
- "Nạp Các Bài Hợp Lệ" chỉ nạp `SE180004`; "Nạp Tất Cả" nạp thêm cả các bài thiếu link (Live/Repo = rỗng).
- Báo cáo liệt kê đúng danh sách thư mục bị bỏ qua và MSSV trùng (nếu có).

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 18/10/2026 | Pytest Runner | Phân loại đúng 3 bài lỗi, chỉ nạp bài hợp lệ | 18 ms | ✅ PASSED | `MSSV_PATTERN`, `select_link_file` |

---

# ST04_WebGrading_TC003: Chấm bài không có HTML → FAILED, không crash (Ngoại lệ)

#### Loại test
Exception

#### Tiền điều kiện (Pre-condition)
- Một bài nộp không có Live URL và thư mục cục bộ không chứa `index.html`.

#### Các bước thực hiện (Test Steps)
1. Thêm bài nộp thủ công không có Live URL và không có thư mục nguồn.
2. Bấm "Bắt Đầu Thẩm Định Web".
3. Mở "Xem Chi Tiết" của bài đó.

#### Kết quả kỳ vọng (Expected Result)
- `WebRubricEngine.grade()` trả `verdict = "FAILED"`, `error = "NO_HTML"`.
- Nhật ký thẩm định ghi `[RESULT]: Không tìm thấy mã nguồn HTML để thẩm định.`
- Không có ngoại lệ văng ra UI; các bài khác vẫn được chấm bình thường.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 18/10/2026 | Pytest Runner | Trả FAILED/NO_HTML, không crash | 4 ms | ✅ PASSED | `test_grade_without_html_returns_failed` |

---

# ST04_WebGrading_TC004: Xuất bảng điểm Web giữ đúng điểm 0.0 (Normal)

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Bảng điểm đã có ít nhất một bài đã chấm với một tiêu chí bằng 0.0 (ví dụ `Lint = 0.0`).

#### Các bước thực hiện (Test Steps)
1. Bấm "Xuất Bảng Điểm" → "Xuất File Excel (.xlsx)".
2. Mở file, kiểm tra cột "Lint (10)" của bài có điểm 0.
3. Lặp lại với "Xuất File Báo Cáo PDF (.pdf)".

#### Kết quả kỳ vọng (Expected Result)
- Ô điểm `0.0` hiển thị đúng là `0` (không bị bỏ trống); các tiêu chí chưa chấm hiển thị trống/`—` tương ứng.
- Cả Excel và PDF nhất quán về giá trị điểm.
- Tên/MSSV chứa ký tự `&`, `<` không làm vỡ bố cục PDF (đã escape HTML).

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 18/10/2026 | Pytest Runner | Điểm 0.0 hiển thị đúng, PDF không vỡ | 90 ms | ✅ PASSED | Kiểm thử hồi quy |

---

---

# ST05_TestcaseEditor_TC001: Mở hộp thoại Thêm/Sửa Testcase nạp đúng bộ testcase của câu hỏi

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Đợt chấm có 3 testcase thuộc câu `Q1` (trọng số 1.0, 2.0, 1.0) và 1 testcase thuộc `Q2`.
- Testcase thứ 3 của `Q1` có giới hạn riêng (1500 ms, 256 MB), hai testcase còn lại 1000 ms / 128 MB.

#### Các bước thực hiện (Test Steps)

1. Mở cửa sổ **Quản Lý Bộ Testcase**, chọn câu `Q1`.
2. Bấm **Thêm Testcase** (hoặc **Sửa** ở một dòng bất kỳ).

#### Kết quả kỳ vọng (Expected Result)

- Cột trái hiển thị đúng 3 testcase của `Q1`, không lẫn testcase của `Q2`.
- Nhãn tổng hiển thị `3 testcase, tổng trọng số 4.0`.
- Form chi tiết chỉ có **Câu Hỏi** và **Trọng Số Điểm**; không còn ô giới hạn thời gian/bộ nhớ (đó là cấu hình chung của ứng dụng).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | Nạp đủ 3 testcase Q1, tổng trọng số 4.0 | 12 ms | ✅ PASSED | PyQt6 Offscreen + SQLite in-memory |

---

# ST05_TestcaseEditor_TC002: Lưu nội dung nhiều dòng của testcase đã sửa

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Hộp thoại đang mở bộ testcase của `Q1`.

#### Các bước thực hiện (Test Steps)

1. Chọn testcase 1.
2. Nhập ô **Đầu Vào (stdin)** 3 dòng: `1`, `2`, `3`.
3. Nhập ô **Kết Quả Kỳ Vọng (stdout)** là `6`.
4. Đổi **Trọng Số Điểm** thành `2.5`.
5. Bấm **Lưu**.

#### Kết quả kỳ vọng (Expected Result)

- CSDL ghi `input_data = "1\n2\n3"` (các dòng nối bằng `\n`), `expected_output = "6"`.
- `score_weight = 2.5`; kiểu lưu chuỗi của CSDL không thay đổi.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | Lưu đúng chuỗi 3 dòng và trọng số 2.5 | 14 ms | ✅ PASSED | Không đổi schema |

---

# ST05_TestcaseEditor_TC003: Thêm testcase mới vào câu hỏi

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Bộ testcase của `Q1` đang có 3 testcase.

#### Các bước thực hiện (Test Steps)

1. Bấm **Thêm Testcase** (danh sách tăng lên 4, dòng mới được chọn).
2. Nhập stdin `10`, stdout `20`.
3. Bấm **Lưu**.

#### Kết quả kỳ vọng (Expected Result)

- CSDL có thêm 1 bản ghi thuộc `Q1` với nội dung vừa nhập.
- Danh sách và nhãn tổng trọng số cập nhật theo số testcase mới.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | Thêm đúng 1 bản ghi Q1 | 11 ms | ✅ PASSED |  |

---

# ST05_TestcaseEditor_TC004: Xóa testcase khỏi câu hỏi

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Bộ testcase của `Q1` có 3 testcase.

#### Các bước thực hiện (Test Steps)

1. Chọn testcase 2.
2. Bấm **Xóa**, xác nhận **Yes** ở hộp thoại cảnh báo.
3. Bấm **Lưu**.

#### Kết quả kỳ vọng (Expected Result)

- Danh sách còn 2 testcase.
- CSDL xóa mềm bản ghi vừa chọn (`is_deleted = 1`), các bản ghi khác giữ nguyên.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | Còn 2 testcase, bản ghi bị xóa mềm | 13 ms | ✅ PASSED |  |

---

# ST05_TestcaseEditor_TC005: Lưu và Thêm Tiếp giữ cửa sổ mở để nhập testcase kế tiếp

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Đang sửa testcase 1 của `Q1`.

#### Các bước thực hiện (Test Steps)

1. Sửa stdout thành `3`.
2. Bấm **Lưu và Thêm Tiếp**.

#### Kết quả kỳ vọng (Expected Result)

- Thay đổi được ghi vào CSDL ngay.
- Cửa sổ không đóng, tự thêm một testcase trống và chuyển vùng chọn xuống dòng mới.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | Ghi CSDL, thêm dòng trống và chọn dòng mới | 15 ms | ✅ PASSED |  |

---

# ST05_TestcaseEditor_TC006: Chuyển qua lại giữa chế độ Văn bản và Theo dòng không mất dữ liệu

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Ô **Đầu Vào (stdin)** đang ở chế độ **Văn bản** với nội dung `5\n4 -3 7 2 11`.

#### Các bước thực hiện (Test Steps)

1. Bấm công tắc **Theo dòng**.
2. Quan sát danh sách dòng (phải có 2 dòng).
3. Bấm lại **Văn bản**.
4. Lặp lại 3 lần.

#### Kết quả kỳ vọng (Expected Result)

- Nội dung chuỗi giữ nguyên `5\n4 -3 7 2 11` ở cả hai chế độ và sau nhiều lần chuyển.
- Không mất dòng, không thêm ký tự lạ.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | Dữ liệu giữ nguyên sau 3 lần chuyển | 9 ms | ✅ PASSED |  |

---

# ST05_TestcaseEditor_TC007: Chế độ Theo dòng nối các dòng bằng ký tự xuống dòng

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Ô stdin đang ở chế độ **Theo dòng** với 1 dòng nội dung `1`.

#### Các bước thực hiện (Test Steps)

1. Bấm **Thêm dòng**.
2. Gõ `2` vào dòng thứ hai.

#### Kết quả kỳ vọng (Expected Result)

- Chuỗi lưu là `1\n2` (dòng trống mới thêm tạo `1\n` trước khi gõ).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | Ghép đúng `1\n2` | 7 ms | ✅ PASSED |  |

---

# ST05_TestcaseEditor_TC008: Hiện ký tự ẩn chỉ để xem, không làm đổi dữ liệu

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Ô stdin có nội dung `a  \nb` (2 khoảng trắng cuối dòng 1).

#### Các bước thực hiện (Test Steps)

1. Bật **Hiện ký tự ẩn**.
2. Quan sát ô dữ liệu.
3. Tắt **Hiện ký tự ẩn**.

#### Khi bật, ô dữ liệu hiển thị `a··↵` (khoảng trắng = dấu chấm, cuối dòng = mũi tên) và chuyển sang chỉ đọc; giá trị lưu vẫn là `a  \nb`. Tắt đi thì sửa được như cũ.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | Ký tự ẩn hiển thị đúng, dữ liệu không đổi | 8 ms | ✅ PASSED | Không dùng icon ảnh |

---

# ST05_TestcaseEditor_TC009: Dán nhiều testcase, dòng lỗi không được nạp im lặng

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Hộp thoại đang mở tab **Dán Nhiều Testcase**.

#### Các bước thực hiện (Test Steps)

1. Dán 3 khối: khối 1 và 2 hợp lệ, khối 3 thiếu dòng `===`.
2. Bấm **Xem Trước**.
3. Bấm **Thêm Tất Cả**.

#### Kết quả kỳ vọng (Expected Result)

- Bảng xem trước có 3 dòng; dòng lỗi tô đỏ kèm lý do thiếu `===`.
- Nhãn kết quả: `2 testcase hợp lệ, 1 dòng lỗi.`
- Chỉ 2 testcase hợp lệ được thêm; hộp thông báo nêu rõ số dòng bị bỏ qua.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | Thêm 2 testcase, báo 1 dòng lỗi | 18 ms | ✅ PASSED |  |

---

# ST05_TestcaseEditor_TC010: Dán toàn dòng lỗi thì không cho thêm

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Tab **Dán Nhiều Testcase** đang mở.

#### Các bước thực hiện (Test Steps)

1. Dán JSON thiếu khoá `output`.
2. Bấm **Xem Trước**.

#### Kết quả kỳ vọng (Expected Result)

- Nhãn kết quả: `0 testcase hợp lệ, 1 dòng lỗi.`
- Nút **Thêm Tất Cả** bị vô hiệu, danh sách testcase không thay đổi.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | Nút thêm bị vô hiệu | 6 ms | ✅ PASSED |  |

---

# ST05_TestcaseEditor_TC011: Kéo thả đổi thứ tự testcase được lưu lại

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `Q1` có 3 testcase với stdin lần lượt `1 2`, `4\n5`, `7`.

#### Các bước thực hiện (Test Steps)

1. Kéo thả đảo thứ tự danh sách (hoặc gọi sự kiện đổi thứ tự tương đương).
2. Bấm **Lưu**.
3. Mở lại hộp thoại cho `Q1`.

#### Kết quả kỳ vọng (Expected Result)

- Thứ tự hiển thị sau khi lưu là `7`, `4\n5`, `1 2`.
- Mở lại thấy đúng thứ tự đó (không thêm cột `order_index` vào CSDL).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | Thứ tự được giữ sau khi lưu | 22 ms | ✅ PASSED |  |

---

# ST05_TestcaseEditor_TC012: Testcase mới kế thừa giới hạn phổ biến của câu hỏi

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- `Q1` có 3 testcase đã lưu: testcase 1–2 dùng 1000 ms / 128 MB, testcase 3 dùng 1500 ms / 256 MB.

#### Các bước thực hiện (Test Steps)

1. Mở hộp thoại testcase của `Q1` (không có ô nhập giới hạn thời gian/bộ nhớ).
2. Bấm **Thêm Testcase**, nhập stdin `10`, stdout `20`.
3. Bấm **Lưu**.

#### Kết quả kỳ vọng (Expected Result)

- Testcase mới nhận giới hạn phổ biến nhất của câu: 1000 ms / 128 MB.
- Testcase 3 giữ nguyên 1500 ms / 256 MB (không bị đổi ngầm).
- CSDL lưu đúng các giá trị trên.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | Testcase mới 1000 ms / 128 MB, testcase 3 giữ 1500 ms | 16 ms | ✅ PASSED | Không đổi schema |

---

# ST05_TestcaseEditor_TC013: Thống kê dòng/ký tự và cảnh báo không chặn lưu

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Hàm thuần `line_stats`, `text_warnings`, `visualize_hidden_chars` của module `ui.components.multiline_field`.

#### Các bước thực hiện (Test Steps)

1. Gọi `line_stats` với `""`, `"a"`, `"a\nb\n"`.
2. Gọi `text_warnings` với `"a"`, `"a  \n"`, `"a\n"`.
3. Gọi `visualize_hidden_chars` với `"a  \nb"`.

#### Kết quả kỳ vọng (Expected Result)

- `line_stats` trả `(0, 0)`, `(1, 1)`, `(2, 4)`.
- `"a"` cảnh báo thiếu xuống dòng cuối; `"a  \n"` cảnh báo khoảng trắng thừa; `"a\n"` không cảnh báo.
- `visualize_hidden_chars` trả `a··↵\nb↵`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | Đúng toàn bộ giá trị kỳ vọng | 3 ms | ✅ PASSED | Cảnh báo chỉ hiển thị, không chặn lưu |

---

# ST05_TestcaseEditor_TC014: Bảng quản lý hiển thị dòng đầu và số dòng còn lại của INPUT/OUTPUT

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Testcase có expected output 3 dòng `Tong = 21`, `Max = 11`, `Min = -3`.

#### Các bước thực hiện (Test Steps)

1. Mở cửa sổ **Quản Lý Bộ Testcase**.
2. Quan sát cột OUTPUT, sau đó rê chuột lên ô.

#### Kết quả kỳ vọng (Expected Result)

- Ô hiển thị `Tong = 21  (+2 dòng)`.
- Tooltip hiển thị đầy đủ 3 dòng; ô rỗng hiển thị `(trống)` màu xám.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | Đúng định dạng dòng đầu + (+N dòng) | 2 ms | ✅ PASSED |  |

---

# ST05_TestcaseEditor_TC015: Chặn lưu khi Kết Quả Kỳ Vọng (stdout) đang trống

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Testcase 1 của `Q1` có stdout `3` trong CSDL.

#### Các bước thực hiện (Test Steps)

1. Chọn testcase 1, xoá trắng ô stdout.
2. Bấm **Lưu**.

#### Kết quả kỳ vọng (Expected Result)

- Hộp thoại **Dữ Liệu Không Hợp Lệ** nêu rõ testcase 1 thiếu stdout.
- Cửa sổ không đóng, CSDL không đổi (stdout vẫn là `3`).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | Chặn lưu, CSDL giữ nguyên | 12 ms | ✅ PASSED |  |

---

# ST05_TestcaseEditor_TC016: Cảnh báo khi đóng cửa sổ mà chưa lưu thay đổi

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Đã sửa nội dung testcase nhưng chưa bấm Lưu.

#### Các bước thực hiện (Test Steps)

1. Sửa ô stdin.
2. Bấm **Hủy** (hoặc phím Esc).
3. Chọn **No** ở hộp thoại xác nhận.
4. Lặp lại và chọn **Yes**.

#### Kết quả kỳ vọng (Expected Result)

- Bước 3: cửa sổ vẫn mở, thay đổi còn nguyên.
- Bước 4: cửa sổ đóng, thay đổi bị bỏ (CSDL không đổi).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | Hỏi xác nhận đúng, No giữ cửa sổ, Yes đóng | 7 ms | ✅ PASSED |  |

---

# ST05_TestcaseEditor_TC017: Nút Sửa/Xóa trong bảng không bị cắt mép dưới

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Áp theme `LIGHT_THEME_QSS` (theme đặt `QPushButton` cao 40px).

#### Các bước thực hiện (Test Steps)

1. Tạo cột thao tác bằng `make_row_button("Sửa"/"Xóa", height=26)` và `make_action_cell`.
2. Hiển thị widget và xử lý sự kiện vẽ.
3. Đo kích thước nút.

#### Kết quả kỳ vọng (Expected Result)

- Nút đúng 54 × 26 px (không bị theme kéo lên 42 px), không bị cắt viền dưới.
- Ô thao tác cao không quá 34 px.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | Nút 54 × 26 px, hiển thị đầy đủ viền | 5 ms | ✅ PASSED | Hồi quy lỗi lệch UI cột Thao Tác |

---
## Ngoài phạm vi (Desktop/pytest) — chưa tự động hóa ở tầng backend
- `ST01_BatchGradingPipeline_*`: chấm bài hàng loạt, TLE (`psutil`, kill 1000ms), MLE (256MB), CE và quy tắc bỏ qua AI khi lỗi biên dịch.
- `ST03_PlagiarismDetection_TC001` Vòng 1: chuẩn hoá token + Winnowing 100% offline dưới 1 giây, **so theo từng câu** (Q1 ↔ Q1) kèm chỉ số Jaccard + độ bao phủ và lọc mã khung sườn chung của lớp (đã tự động hoá ở tầng Desktop: `test_plagiarism_engine.py` / `test_plagiarism_dialog.py`).
- Đồng bộ kết quả lên máy chủ trung tâm (`sync/grading-session`) — **tính năng đồng bộ cloud đã được gỡ bỏ**, không còn trong phạm vi hệ thống.
