# Đặc tả Kiểm thử Chấp Nhận (Acceptance Test Specification)

- **Cấp độ kiểm thử**: Acceptance Test (UAT)
- **Người thực hiện (Tester/Dev)**: Đinh Thành Nam
- **Cập nhật lần cuối**: 18/10/2026
- **Tài liệu liên quan**: `rules/testcase-rules.md`, `docs/architecture/`
- **Tổng số Testcase trong phạm vi backend**: 6 (03 Normal, 01 Boundary, 02 Exception)

> Tài liệu đã được viết lại cho khớp mã nguồn `apps/central-backend`.
> Phạm vi tự động hóa: các tiêu chí chấp nhận quan sát được qua Backend (AI review, dashboard Admin, RBAC).
> Tiêu chí thuần Desktop client (nhập bài nộp, xuất bảng điểm, ghi đè điểm) **không** được gắn ID `AT..` để tránh trùng nguồn kiểm thử; xem mục "Ngoài phạm vi".

---

# AT03_PedagogicalAIReview_TC001: AI sinh nhận xét sư phạm cho bài sai logic

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Giảng viên còn hạn ngạch AI.
- Có bài nộp kết luận `WA` kèm testcase thất bại.

#### Các bước thực hiện (Test Steps)
1. Giảng viên gửi `POST /api/v1/ai/review-code` kèm `source_code`, `problem_statement`, `failed_testcase`.
2. Backend giữ chỗ hạn ngạch và gọi nhà cung cấp AI.
3. `AiGatewayService.reviewCode` kiểm tra cấu trúc phản hồi.

#### Kết quả kỳ vọng (Expected Result)
- Trả về `message = "Phân tích mã nguồn bằng AI thành công"`.
- `data` gồm `issue_summary`, `pedagogical_feedback`, `bug_category`, và `suspected_error_line` (nếu xác định được).
- Tiêu chuẩn sư phạm: nêu bản chất lỗi và gợi mở tư duy; không trả về lời giải hoàn chỉnh.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 17/10/2026 | Đinh Thành Nam | Nhận xét sư phạm đúng, chỉ ra dòng lỗi, không giải hộ | 11 ms | ✅ PASSED | Provider được mock |

---

# AT04_AdminOverview_TC001: Dashboard thống kê và giám sát quota AI

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Quản trị viên đăng nhập với quyền `ADMIN`.

#### Các bước thực hiện (Test Steps)
1. Gọi `GET /api/v1/admin/reports/overview`.
2. Gọi `GET /api/v1/admin/users` để xem hạn ngạch từng giảng viên.

#### Kết quả kỳ vọng (Expected Result)
- Overview trả `total_instructors`, `total_tokens_consumed_month`, `total_budget_limit`, `top_consuming_feature`.
- Danh sách người dùng trả mỗi giảng viên kèm `daily_token_quota` và `used_tokens_today`.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 17/10/2026 | Đinh Thành Nam | Số liệu tổng quan và quota từng giảng viên hiển thị đúng | 9 ms | ✅ PASSED | Service-level |

---

# AT04_AdminSecurityRBAC_TC001: Giảng viên truy cập API Admin bị từ chối

#### Loại test
Exception

#### Tiền điều kiện (Pre-condition)
- Người dùng có vai trò `INSTRUCTOR`.

#### Các bước thực hiện (Test Steps)
1. Gửi request gắn JWT Token của Giảng viên tới endpoint Admin (ví dụ `GET /api/v1/admin/users` yêu cầu `@Roles('ADMIN')`).
2. Hệ thống chạy `JwtAuthGuard` → `RolesGuard`.

#### Kết quả kỳ vọng (Expected Result)
- Token hợp lệ nhưng vai trò không nằm trong `@Roles(...)` → chặn truy cập.
- Trả về `HTTP 403` với `error_code = "FORBIDDEN_ADMIN_ONLY"`.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 17/10/2026 | Đinh Thành Nam | Chặn truy cập, trả 403 FORBIDDEN_ADMIN_ONLY | 4 ms | ✅ PASSED | RBAC an toàn |

---

# AT06_WebUiEvaluation_TC001: Chấm điểm UI/UX đồ án Web bằng AI Vision thành công

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Giảng viên đã đăng nhập (JWT hợp lệ) và còn hạn ngạch AI trong ngày.
- Có ảnh chụp màn hình đồ án Web (PNG/JPEG) và danh sách 4 tiêu chí rubric.

#### Các bước thực hiện (Test Steps)
1. Gửi `POST /api/v1/ai/evaluate-web-ui` với `screenshot_base64` (ảnh PNG hợp lệ) và `rubric_requirements` gồm 4 tiêu chí.
2. `OpenRouterService` giữ chỗ hạn ngạch rồi gọi provider với ảnh.
3. `AiGatewayService.evaluateWebUi` kiểm cấu trúc JSON trả về.

#### Kết quả kỳ vọng (Expected Result)
- Trả về `message = "Đánh giá giao diện Web bằng AI thành công"`.
- `data.ui_score` là trung bình cộng điểm các tiêu chí, làm tròn 1 chữ số thập phân, trong [0, 10].
- `data.evaluation_details` có đúng số phần tử bằng `rubric_requirements`; mỗi phần tử có `criterion`, `score`, `verdict` (PASS/PARTIAL/FAIL), `comment`.
- `data.tokens_consumed` được ghi nhận vào hạn ngạch.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 18/10/2026 | Đinh Thành Nam | ui_score = trung bình 4 tiêu chí, quota trừ đúng | 9 ms | ✅ PASSED | Provider được mock |

---

# AT06_WebUiEvaluation_TC002: Giới hạn số tiêu chí rubric và dung lượng ảnh (Biên)

#### Loại test
Boundary

#### Tiền điều kiện (Pre-condition)
- DTO `EvaluateWebUiDto`: `rubric_requirements` từ 1 đến 20 phần tử (mỗi phần tử ≤ 500 ký tự); `decodeImage` giới hạn ảnh PNG/JPEG tối đa 5 MB.

#### Các bước thực hiện (Test Steps)
1. Gửi request với `rubric_requirements` đúng 20 phần tử (biên trên hợp lệ).
2. Gửi request với `rubric_requirements` 21 phần tử (vượt biên).
3. Gửi ảnh PNG có dung lượng vượt 5 MB.

#### Kết quả kỳ vọng (Expected Result)
- 20 phần tử: hợp lệ (đi qua ValidationPipe), AI trả `ui_score` cho 20 tiêu chí.
- 21 phần tử: `HTTP 422` với `error_code = "VALIDATION_FAILED"`, `details[].field = "rubric_requirements"`.
- Ảnh > 5 MB: `HTTP 400` với `error_code = "AI_IMAGE_INVALID"`, `message = "Ảnh phải có kích thước tối đa 5 MB."`.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 18/10/2026 | Đinh Thành Nam | 20 OK, 21 trả 422, ảnh >5MB trả 400 | 6 ms | ✅ PASSED | Kiểm tra biên DTO + ảnh |

---

# AT06_WebUiEvaluation_TC003: Ảnh không hợp lệ bị từ chối (Ngoại lệ)

#### Loại test
Exception

#### Tiền điều kiện (Pre-condition)
- Giảng viên đã đăng nhập và còn hạn ngạch.

#### Các bước thực hiện (Test Steps)
1. Gửi `POST /api/v1/ai/evaluate-web-ui` với `screenshot_base64 = "not-a-valid-base64!@#"`.

#### Kết quả kỳ vọng (Expected Result)
- `decodeImage` từ chối trước khi gọi provider.
- Trả về `HTTP 400` với `error_code = "AI_IMAGE_INVALID"`, `message = "Ảnh phải là dữ liệu PNG/JPEG base64 hợp lệ."`.
- Không tiêu tốn token; hạn ngạch không bị trừ.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 18/10/2026 | Đinh Thành Nam | Trả 400 AI_IMAGE_INVALID, không trừ quota | 3 ms | ✅ PASSED | Chặn sớm, an toàn |

---

## Phân hệ Desktop Client (Pytest) — Hiện trạng tự động hóa
- `AT01_SubmissionIngestion`: Đã tự động hóa trong [test_submission_ingestion.py](file:///e:/AITA/apps/desktop-client/tests/test_submission_ingestion.py) (quét thư mục bài nộp, nhận diện MSSV, đồng bộ đợt chấm).
- `AT02_ExportGradebook`: Đã tự động hóa trong [test_export_service.py](file:///e:/AITA/apps/desktop-client/tests/test_export_service.py) (xuất `results.csv` 7 cột UTF-8 BOM, định dạng có điều kiện Excel, xử lý file bị khóa `PermissionError`).
- `AT03_ManualScoreOverride`: Đã tự động hóa trong [test_export_service.py](file:///e:/AITA/apps/desktop-client/tests/test_export_service.py) và [test_db_manager.py](file:///e:/AITA/apps/desktop-client/tests/test_db_manager.py) (ghi đè điểm thủ công, lưu lý do giải trình).
- `AT05_WebGradingStudio`: Đã tự động hóa trong [test_web_rubric_service.py](file:///e:/AITA/apps/desktop-client/tests/test_web_rubric_service.py) (nhận diện thư mục bài nộp, chấm 4 tiêu chí DOM/CSS/JS/UI, trọng số phân bổ lại khi thiếu UI, ngưỡng PASSED/PARTIAL/FAILED, giữ điểm 0.0 khi xuất bảng điểm).

Toàn bộ các ca nghiệm thu Desktop trên đều đã chạy thành công qua bộ kiểm thử `pytest apps/desktop-client/tests/`.
