# Đặc Tả API: Phân Hệ Báo Cáo & Kiểm Toán Hệ Thống (Audit & Reports API)

### Thư mục: `docs/apis/reports/`
### Phân hệ: Web Server Backend (NestJS AuditLogs Module) & Web Admin Dashboard

---

## 1. Danh Sách Endpoint (2 APIs)

| Method | Endpoint | Quyền hạn | Mô tả |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/admin/reports/overview` | Admin Only | Thống kê giảng viên và tiêu thụ token AI toàn trường |
| `GET` | `/api/v1/admin/reports/ai-usage` | Admin Only | Tra cứu nhật ký AI, lọc theo giảng viên/thời gian và phân trang |

---

## 2. Chi Tiết API & Ràng Buộc Dữ Liệu

### 2.1. `GET /api/v1/admin/reports/ai-usage`
- **Mục đích**: Hiển thị nhật ký từng lượt gọi AI cho báo cáo Admin (UC-05); không chứa mã nguồn hoặc bài làm sinh viên.
- **Query**: `page` (mặc định 1), `page_size` (mặc định 20, tối đa 100), `user_id` (UUID, tùy chọn), `from` và `to` (ISO-8601, tùy chọn, bao gồm hai mốc thời gian).
- `from` phải nhỏ hơn hoặc bằng `to`.
- **Headers**: `Authorization: Bearer <access_token>` (Role: `ADMIN`)

Phản hồi thành công trả `data.items` gồm `id`, `user_id`, `username`, `full_name`, `feature_type`, `model_name`, `prompt_tokens`, `completion_tokens`, `total_tokens`, `created_at`; `data.pagination` gồm `page`, `page_size`, `total_items`, `total_pages`.

---

### 2.2. `GET /api/v1/admin/reports/overview`
- **Mục đích**: Phục vụ trang Dashboard của Quản trị viên (UC-05). Không chứa dữ liệu bài làm sinh viên vì Desktop App hoạt động hoàn toàn offline-first.
- `total_budget_limit` là hạn mức tháng suy ra từ tổng quota/ngày của các Instructor đang hoạt động nhân với số ngày trong tháng UTC hiện tại.
- **Headers**: `Authorization: Bearer <access_token>` (Role: `ADMIN`)

#### Kịch bản phản hồi:
* **Thành công (`success: true`) - HTTP 200 OK**:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Lấy số liệu thống kê tổng quan thành công",
  "data": {
    "total_instructors": 24,
    "ai_token_usage": {
      "total_tokens_consumed_month": 1285000,
      "total_budget_limit": 5000000,
      "top_consuming_feature": "TESTCASE_GEN"
    }
  },
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

* **Thất bại (`success: false`) - HTTP 403 Forbidden**:
```json
{
  "success": false,
  "status_code": 403,
  "error_code": "FORBIDDEN_ADMIN_ONLY",
  "message": "Chỉ Quản trị viên mới có quyền xem báo cáo thống kê này.",
  "details": null,
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```
