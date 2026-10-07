# Đặc Tả API: Phân Hệ Báo Cáo & Kiểm Toán Hệ Thống (Audit & Reports API)

### Thư mục: `docs/apis/reports/`
### Phân hệ: Web Server Backend (NestJS AuditLogs Module) & Web Admin Dashboard

---

## 1. Danh Sách Endpoint (1 API)

| Method | Endpoint | Quyền hạn | Mô tả |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/admin/reports/overview` | Admin Only | Thống kê số liệu người dùng, môn học và kiểm toán tiêu thụ token AI toàn trường |

---

## 2. Chi Tiết API & Ràng Buộc Dữ Liệu

### 2.1. `GET /api/v1/admin/reports/overview`
- **Mục đích**: Phục vụ trang Dashboard của Quản trị viên (UC-05). Không chứa dữ liệu bài làm sinh viên vì Desktop App hoạt động hoàn toàn offline-first.
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
