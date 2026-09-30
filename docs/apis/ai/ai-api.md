# Đặc Tả API: Phân Hệ AI Gateway & Quản Lý Hạn Ngạch (AI Hub API)

### Thư mục: `docs/apis/ai/`
### Phân hệ: Web Server Backend (NestJS AI Module) & Google Gemini AI Hub

---

## 1. Danh Sách Endpoints (5 APIs)

| Method | Endpoint | Use Case | Mô tả |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/ai/quota` | UC-04 | Kiểm tra hạn ngạch Token hôm nay & thời điểm reset |
| `POST` | `/api/v1/ai/generate-testcases` | UC-10 | Tự động sinh testcase biên bằng Gemini 1.5 Flash |
| `POST` | `/api/v1/ai/review-code` | UC-16 | Phân tích lỗi và sinh nhận xét sư phạm On-Demand cho bài WA |
| `POST` | `/api/v1/ai/verify-plagiarism` | UC-17 | Xác thực ngữ nghĩa nghi vấn đạo văn > 80% (Vòng 2) |
| `POST` | `/api/v1/ai/evaluate-web-ui` | UC-19 | Đánh giá giao diện Web qua ảnh chụp màn hình Multimodal |

---

## 2. Chi Tiết Từng API & Ràng Buộc Dữ Liệu

### 2.1. `GET /api/v1/ai/quota`
- **Mục đích**: Desktop App kiểm tra số token còn lại trước khi gọi AI.
- **Headers**: `Authorization: Bearer <access_token>`

#### Kịch bản phản hồi:
* **Thành công (`success: true`) - HTTP 200 OK**:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Lấy thông tin hạn ngạch AI thành công",
  "data": {
    "daily_limit_tokens": 50000,
    "used_tokens_today": 12450,
    "remaining_tokens": 37550,
    "reset_at_utc": "2026-10-01T00:00:00.000Z"
  },
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

---

### 2.2. `POST /api/v1/ai/generate-testcases` (UC-10)
- **Ràng buộc đầu vào**:
  - `problem_description`: 20-5000 ký tự, bắt buộc.
  - `language`: `"C"`, `"JAVA"`, `"PYTHON"`, `"WEB"`, bắt buộc.
  - `count`: int từ 1 đến 10, mặc định 3.

#### Kịch bản phản hồi:
* **Thành công (`success: true`) - HTTP 200 OK**:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Sinh testcase tự động bằng AI thành công",
  "data": {
    "tokens_consumed": 420,
    "testcases": [
      {
        "input": "1000000",
        "expected_output": "2480437",
        "explanation": "Biên trên tối đa N = 10^6",
        "is_boundary": true
      }
    ]
  },
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

* **Thất bại (`success: false`) - HTTP 429 Too Many Requests (Hết Quota)**:
```json
{
  "success": false,
  "status_code": 429,
  "error_code": "AI_QUOTA_EXCEEDED",
  "message": "Tài khoản của bạn đã sử dụng hết hạn ngạch Token AI trong ngày.",
  "details": null,
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

---

### 2.3. `POST /api/v1/ai/review-code` (UC-16)
- **Ràng buộc đầu vào**:
  - `source_code`: 10-10000 ký tự, bắt buộc.
  - `language`: string, bắt buộc.
  - `problem_statement`: max 3000 ký tự.
  - `failed_testcase`: object `{ input, expected_output, actual_output }`.

#### Kịch bản phản hồi:
* **Thành công (`success: true`) - HTTP 200 OK**:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Phân tích mã nguồn bằng AI thành công",
  "data": {
    "tokens_consumed": 380,
    "suspected_error_line": 5,
    "issue_summary": "Sai điều kiện dừng vòng lặp duyệt ước i < n",
    "pedagogical_feedback": "Em hãy kiểm tra lại điều kiện vòng for(i=1; i<=n; i++) nhé.",
    "bug_category": "OFF_BY_ONE_ERROR"
  },
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

---

### 2.4. `POST /api/v1/ai/verify-plagiarism` (UC-17 Vòng 2)
- **Ràng buộc đầu vào**:
  - `student_a_code`: string.
  - `student_b_code`: string.
  - `ast_similarity_percentage`: float từ 80.0 đến 100.0.

#### Kịch bản phản hồi:
* **Thành công (`success: true`) - HTTP 200 OK**:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Phân tích bằng chứng đạo văn thành công",
  "data": {
    "tokens_consumed": 510,
    "is_plagiarized": true,
    "confidence_percentage": 94.8,
    "evidence_summary": "Đổi tên biến và hoán vị câu lệnh if độc lập",
    "cloned_segments": [
      { "student_a_lines": "5-9", "student_b_lines": "6-10", "technique": "VARIABLE_RENAMING" }
    ]
  },
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```

---

### 2.5. `POST /api/v1/ai/evaluate-web-ui` (UC-19 Web Multimodal)
- **Ràng buộc đầu vào**:
  - `screenshot_base64`: string Base64 ảnh chụp màn hình bài nộp web (tối đa 5MB).
  - `rubric_requirements`: mảng chuỗi tiêu chí thẩm mỹ/bố cục.

#### Kịch bản phản hồi:
* **Thành công (`success: true`) - HTTP 200 OK**:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Đánh giá giao diện Web bằng AI thành công",
  "data": {
    "tokens_consumed": 720,
    "ui_score": 8.5,
    "evaluation_details": [
      {
        "criterion": "Bố cục cân đối có thanh điều hướng navbar",
        "score": 10.0,
        "verdict": "PASS",
        "comment": "Navbar thiết kế chuẩn mực."
      }
    ],
    "overall_feedback": "Trang web thiết kế gọn gàng, độ tương phản tốt."
  },
  "timestamp": "2026-09-30T12:00:00.000Z"
}
```
