# Đặc tả Kiểm thử Hệ thống (System Test Specification)

- **Cấp độ kiểm thử**: System Test
- **Người thực hiện (Tester/Dev)**: Đinh Thành Nam
- **Cập nhật lần cuối**: 18/10/2026
- **Tài liệu liên quan**: `rules/testcase-rules.md`, `docs/architecture/`
- **Tổng số Testcase**: 13 Testcases (06 Normal, 04 Boundary, 03 Exception)
  - Phân hệ Desktop Client (ST01, ST04): 09 Testcases (03 Normal, 03 Boundary, 03 Exception)
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
- `data` gồm `is_plagiarized`, `confidence_percentage` trong [0,100], `evidence_summary`, và `cloned_segments` đúng cấu trúc.

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

## Ngoài phạm vi (Desktop/pytest) — chưa tự động hóa ở tầng backend
- `ST01_BatchGradingPipeline_*`: chấm bài hàng loạt, TLE (`psutil`, kill 1000ms), MLE (256MB), CE và quy tắc bỏ qua AI khi lỗi biên dịch.
- `ST03_PlagiarismDetection_TC001` Vòng 1: quét AST + Winnowing 100% offline dưới 1 giây.
- Đồng bộ kết quả lên máy chủ trung tâm (`sync/grading-session`) — **tính năng đồng bộ cloud đã được gỡ bỏ**, không còn trong phạm vi hệ thống.
