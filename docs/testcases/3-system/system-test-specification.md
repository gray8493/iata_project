# Đặc tả Kiểm thử Hệ thống (System Test Specification)

- **Cấp độ kiểm thử**: System Test
- **Người thực hiện (Tester/Dev)**: Đinh Thành Nam
- **Cập nhật lần cuối**: 17/10/2026
- **Tài liệu liên quan**: `rules/testcase-rules.md`, `docs/architecture/`
- **Tổng số Testcase trong phạm vi backend**: 4 (02 Normal, 01 Boundary, 01 Exception)

> Tài liệu đã được viết lại cho khớp mã nguồn `apps/central-backend`.
> Phạm vi tự động hóa: các kịch bản liên quan tới Backend (AI testcase generation, AI plagiarism verification).
> Kịch bản thuần Desktop client (sandbox chấm bài, quét AST offline) **không** được gắn ID `ST..` để tránh trùng nguồn kiểm thử; xem mục "Ngoài phạm vi".

---

# ST02_AITestcaseGen_TC001: Sinh bộ testcase bằng Gemini AI thành công

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Giảng viên có JWT Token hợp lệ và còn hạn ngạch AI.
- `GEMINI_API_KEY` đã được cấu hình; nhà cung cấp AI phản hồi JSON hợp lệ.

#### Các bước thực hiện (Test Steps)
1. Giảng viên gửi `POST /api/v1/ai/generate-testcases` với `count = 3`.
2. `GeminiService` giữ chỗ hạn ngạch, gọi nhà cung cấp và nhận JSON.
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
2. `GeminiService` giữ chỗ hạn ngạch và gọi provider.
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

## Ngoài phạm vi (Desktop/pytest) — chưa tự động hóa ở tầng backend
- `ST01_BatchGradingPipeline_*`: chấm bài hàng loạt, TLE (`psutil`, kill 1000ms), MLE (256MB), CE và quy tắc bỏ qua AI khi lỗi biên dịch.
- `ST03_PlagiarismDetection_TC001` Vòng 1: quét AST + Winnowing 100% offline dưới 1 giây.
- Đồng bộ kết quả lên máy chủ trung tâm (`sync/grading-session`) — **tính năng đồng bộ cloud đã được gỡ bỏ**, không còn trong phạm vi hệ thống.
