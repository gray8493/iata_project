# Đặc tả Kiểm thử Chấp Nhận (Acceptance Test Specification)

- **Cấp độ kiểm thử**: Acceptance Test (UAT)
- **Người thực hiện (Tester/Dev)**: Đinh Thành Nam
- **Cập nhật lần cuối**: 17/10/2026
- **Tài liệu liên quan**: `rules/testcase-rules.md`, `docs/architecture/`
- **Tổng số Testcase trong phạm vi backend**: 3 (02 Normal, 00 Boundary, 01 Exception)

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

## Ngoài phạm vi (Desktop/pytest) — chưa tự động hóa ở tầng backend
- `AT01_SubmissionIngestion_TC001/TC002`: quét thư mục bài nộp, nhận diện MSSV, cảnh báo thư mục rỗng.
- `AT02_ExportGradebook_TC001/TC002`: xuất `results.csv` 7 cột, Excel tô màu, xử lý file bị khóa.
- `AT03_ManualScoreOverride_TC001`: ghi đè điểm thủ công kèm lý do giải trình.

Các tiêu chí trên thuộc `apps/desktop-client` và cần bộ kiểm thử Python (pytest) riêng.
