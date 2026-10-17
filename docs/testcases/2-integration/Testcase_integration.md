# Đặc tả Kiểm thử Tích hợp (Integration Test Specification)

> Tài liệu này đã được viết lại cho khớp với mã nguồn hiện tại của `apps/central-backend`.
> Phạm vi tự động hóa: **chỉ các kịch bản kiểm thử được ở tầng backend (NestJS service-level)**.
> Các kịch bản thuộc luồng Desktop client (PyQt6) được liệt kê ở mục "Ngoài phạm vi" và không được đánh ID `IT..` để tránh trùng nguồn kiểm thử.

## 1. Mục tiêu
Kiểm thử sự phối hợp giữa nhiều thành phần backend trong cùng một luồng nghiệp vụ: service ↔ transaction ↔ quota ↔ token ↔ guard, đảm bảo tính nhất quán dữ liệu khi thao tác gồm nhiều bước (ví dụ: tạo người dùng kèm cấu hình hạn ngạch, khóa tài khoản kèm thu hồi token).

## 2. Cách chạy
```
cd apps/central-backend
npm test -- integration.docs.spec.ts
```

## 3. Quy ước ID
`IT<NN>_<ModulePascalCase>_TC<nnn>` theo `rules/testcase-rules.md`.

## 4. Ma trận kịch bản

| Mã | Module | Loại | Endpoint / Service liên quan |
|---|---|---|---|
| IT01_UserLifecycle_TC001 | UserLifecycle | Normal | `POST /api/v1/admin/users` |
| IT01_UserLifecycle_TC002 | UserLifecycle | Exception | `POST /api/v1/admin/users` |
| IT02_DisableRevoke_TC001 | DisableRevoke | Normal | `PUT /api/v1/admin/users/:id` |
| IT02_DisableRevoke_TC002 | DisableRevoke | Exception | `JwtStrategy.validate` |
| IT03_QuotaAllocation_TC001 | QuotaAllocation | Normal | `PUT /api/v1/admin/users/:id` |
| IT04_AuthQuotaSync_TC001 | AuthQuotaSync | Normal | `POST /api/v1/auth/login` + `GET /api/v1/ai/quota` |
| IT05_AiTestcaseGeneration_TC001 | AiTestcaseGeneration | Normal | `POST /api/v1/ai/generate-testcases` (Desktop -> Backend) |
| IT05_AiTestcaseGeneration_TC002 | AiTestcaseGeneration | Boundary | `POST /api/v1/ai/generate-testcases` (Desktop -> Backend) |
| IT05_AiTestcaseGeneration_TC003 | AiTestcaseGeneration | Exception | `POST /api/v1/ai/generate-testcases` (Desktop -> Backend) |
| IT15_ReportOverview_TC001 | ReportOverview | Normal | `GET /api/v1/admin/reports/overview` |
| IT15_ReportAiUsage_TC002 | ReportOverview | Normal | `GET /api/v1/admin/reports/ai-usage` |
| IT15_ReportAiUsage_TC003 | ReportOverview | Exception | `GET /api/v1/admin/reports/ai-usage` |
| IT16_AiResilience_TC001 | AiProviderResilience | Exception | `POST /api/v1/ai/generate-testcases` |
| IT17_QuotaGuard_TC001 | AiQuotaExceeded | Exception | `POST /api/v1/ai/*` |
| IT21_RbacBlock_TC001 | RbacBlock | Exception | Guards `JwtAuthGuard` + `RolesGuard` |
| IT22_RefreshRotation_TC001 | RefreshRotation | Normal | `POST /api/v1/auth/refresh` |
| IT22_RefreshRotation_TC002 | RefreshRotation | Exception | `POST /api/v1/auth/refresh` |
| IT23_SoftDeleteExclusion_TC001 | SoftDeleteExclusion | Normal | `DELETE /api/v1/admin/users/:id` |
| IT23_SoftDeleteExclusion_TC002 | SoftDeleteExclusion | Exception | `DELETE /api/v1/admin/users/:id` |

---

## 5. Chi tiết kịch bản

### IT01_UserLifecycle_TC001 — Tạo tài khoản Giảng viên kèm cấu hình hạn ngạch
- **Loại test:** Normal
- **Pre-condition:** Admin đang đăng nhập; username/email chưa tồn tại.
- **Test Data:** `{ username: "teacher_an", password: "Abc12345", full_name: "Nguyễn An", email: "an@example.com", role: "INSTRUCTOR", daily_token_quota: 80000 }`
- **Test Steps:**
  1. Gọi `UsersService.create`.
  2. Quan sát lời gọi `prisma.$transaction(callback)`.
- **Expected Result:**
  - Trong cùng một transaction: `user.create` được gọi với `role = INSTRUCTOR`, `email` đã hạ chữ thường; `aiQuotaConfig.create` được gọi với `dailyTokenLimit = 80000`.
  - Kết quả trả về `message = "Tạo tài khoản người dùng mới thành công"`, `data.daily_token_quota = 80000`, `data.role = INSTRUCTOR`.

### IT01_UserLifecycle_TC002 — Tạo tài khoản trùng username/email (rollback)
- **Loại test:** Exception
- **Pre-condition:** Đã tồn tại bản ghi cùng username hoặc email.
- **Test Data:** `Prisma.PrismaClientKnownRequestError` mã `P2002`.
- **Test Steps:** `UsersService.create` ném `P2002`.
- **Expected Result:** `rethrowUniqueConflict` chuyển thành `409` với `error_code = "USER_ALREADY_EXISTS"`, `message = "Tên đăng nhập hoặc email đã tồn tại."`; không có tài khoản nào được tạo.

### IT02_DisableRevoke_TC001 — Khóa tài khoản thì vô hiệu hóa token
- **Loại test:** Normal
- **Pre-condition:** Tài khoản Giảng viên tồn tại và đang có refresh token hiệu lực.
- **Test Data:** `UpdateUserDto { is_active: false }`.
- **Test Steps:** Gọi `UsersService.update(id, dto, actorId)`.
- **Expected Result:**
  - `user.update` nhận `data.isActive = false`.
  - Trong cùng transaction, `refreshToken.updateMany` được gọi với `where: { userId: id, revokedAt: null }` và `data.revokedAt` được set.

### IT02_DisableRevoke_TC002 — Access token của tài khoản đã khóa bị từ chối
- **Loại test:** Exception
- **Pre-condition:** Access token còn hạn nhưng user đã `isActive = false`.
- **Test Data:** Payload `{ id, username, role, token_type: 'access' }`; `prisma.user.findFirst` trả `null`.
- **Test Steps:** Gọi `JwtStrategy.validate(payload)`.
- **Expected Result:** Ném `401` với `error_code = "AUTH_ACCOUNT_DISABLED"`, `message = "Tài khoản không còn hoạt động."`.

### IT03_QuotaAllocation_TC001 — Admin cấp/đổi hạn ngạch qua cập nhật người dùng
- **Loại test:** Normal
- **Pre-condition:** Tài khoản tồn tại; có thể chưa có `aiQuotaConfig`.
- **Test Data:** `UpdateUserDto { daily_token_quota: 120000 }`.
- **Test Steps:** Gọi `UsersService.update`.
- **Expected Result:** `aiQuotaConfig.upsert` được gọi với `where.userId = id`, `create.dailyTokenLimit = 120000`, `update.dailyTokenLimit = 120000`; kết quả `data.daily_token_quota = 120000`.

### IT04_AuthQuotaSync_TC001 — Đăng nhập rồi truy vấn hạn ngạch còn lại
- **Loại test:** Normal
- **Pre-condition:** Giảng viên có `aiQuotaConfig { dailyTokenLimit: 50000, usedTokensToday: 12000 }`.
- **Test Data:** `LoginDto { username: "teacher_an", password: "Abc12345" }`.
- **Test Steps:**
  1. `AuthService.login` thành công.
  2. `AiQuotaService.snapshot(userId)`.
- **Expected Result:**
  - Login trả `expires_in = 900` (mặc định `15m`) và `user.role = INSTRUCTOR`.
  - Snapshot trả `daily_limit_tokens = 50000`, `used_tokens_today = 12000`, `remaining_tokens = 38000`.

### IT05_AiTestcaseGeneration_TC001 — Nạp đề bài từ file và gửi tới AI Gateway
- **Loại test:** Normal
- **Pre-condition:** `AiService` khởi tạo với `ApiClient`, nạp thành công file đề bài qua `document_reader`.
- **Test Data:** Nội dung đề bài hợp lệ, `count = 2`, `language = "python"`.
- **Test Steps:** Gọi `AiService.generate_testcases`.
- **Expected Result:** Gửi request chuẩn cấu trúc tới backend `POST /api/v1/ai/generate-testcases`; trả về danh sách testcase và token tiêu thụ.

### IT05_AiTestcaseGeneration_TC002 — Kẹp giá trị count và chuẩn hóa ngôn ngữ (Biên)
- **Loại test:** Boundary
- **Pre-condition:** `AiService` sẵn sàng.
- **Test Data:** `count = 99` (vượt trần 10), `language = "rust"` (ngôn ngữ không thuộc danh mục).
- **Test Steps:** Gọi `AiService.generate_testcases`.
- **Expected Result:** Payload gửi đi tự kẹp `count = 10` và fallback `language = "C"`.

### IT05_AiTestcaseGeneration_TC003 — Lan truyền lỗi từ Backend lên Desktop UI (Ngoại lệ)
- **Loại test:** Exception
- **Pre-condition:** Backend phản hồi `429 AI_QUOTA_EXCEEDED`.
- **Test Steps:** Gọi `AiService.generate_testcases`.
- **Expected Result:** `AiService` bắt lỗi an toàn, trả về `success = False` và `error_code = "AI_QUOTA_EXCEEDED"`.

### IT15_ReportOverview_TC001 — Báo cáo tổng quan tổng hợp nhiều bảng
- **Loại test:** Normal
- **Pre-condition:** Có giảng viên và log sử dụng AI trong tháng.
- **Test Data:** `dailyTokenLimit = 200000`; `totalTokens (month) = 1285000`; top feature `TESTCASE_GEN`.
- **Test Steps:** Gọi `AuditLogsService.overview()`.
- **Expected Result:** `total_instructors` đúng; `total_budget_limit = 200000 * daysInMonth`; `top_consuming_feature = "TESTCASE_GEN"`; kết quả được ghi cache Redis TTL 45 giây.

### IT15_ReportAiUsage_TC002 — Lọc nhật ký theo giảng viên và khoảng ngày
- **Loại test:** Normal
- **Pre-condition:** Có log thỏa bộ lọc.
- **Test Data:** `{ page: 1, page_size: 20, user_id: <UUID>, from, to }`.
- **Test Steps:** Gọi `AuditLogsService.listAiUsage(query)`.
- **Expected Result:** `where` chứa `isDeleted = false`, `userId`, `createdAt: { gte, lte }`; `pagination` tính đúng `total_pages`.

### IT15_ReportAiUsage_TC003 — Khoảng ngày không hợp lệ
- **Loại test:** Exception
- **Pre-condition:** `from > to`.
- **Test Data:** `{ from: "2026-10-20", to: "2026-10-10" }`.
- **Test Steps:** Gọi `AuditLogsService.listAiUsage`.
- **Expected Result:** Ném `400` với `error_code = "INVALID_DATE_RANGE"`.

### IT16_AiResilience_TC001 — Lỗi nhà cung cấp AI được hoàn hạn ngạch
- **Loại test:** Exception
- **Pre-condition:** `GEMINI_API_KEY` đã cấu hình; `AiQuotaService.reserve` thành công.
- **Test Data:** `client.models.generateContent` từ chối với `{ status: 503 }`.
- **Test Steps:** Gọi `GeminiService.generateJson(...)`.
- **Expected Result:** Ném `502` với `error_code = "AI_PROVIDER_ERROR"`; `quota.release` được gọi để hoàn phần đã giữ chỗ.

### IT17_QuotaGuard_TC001 — Chặn khi vượt hạn ngạch trong ngày
- **Loại test:** Exception
- **Pre-condition:** `usedTokensToday` gần chạm `dailyTokenLimit`.
- **Test Data:** `amount` khiến `usedTokensToday + amount > dailyTokenLimit`.
- **Test Steps:** Gọi `AiQuotaService.reserve`.
- **Expected Result:** Ném `429` với `error_code = "AI_QUOTA_EXCEEDED"`; `usedTokensToday` không bị tăng.

### IT21_RbacBlock_TC001 — Phân quyền chéo module
- **Loại test:** Exception
- **Pre-condition:** Người dùng INSTRUCTOR gọi endpoint Admin và ngược lại.
- **Test Data:** `@Roles('ADMIN')` với user `INSTRUCTOR`; `@Roles('INSTRUCTOR')` với user `ADMIN`.
- **Test Steps:** Gọi `RolesGuard.canActivate`.
- **Expected Result:** Cả hai trường hợp ném `403` với `error_code = "FORBIDDEN_ADMIN_ONLY"`.

### IT22_RefreshRotation_TC001 — Luân chuyển refresh token
- **Loại test:** Normal
- **Pre-condition:** Refresh token hợp lệ, chưa thu hồi, còn hạn; user đang hoạt động.
- **Test Data:** Payload `{ token_type: 'refresh', jti, id }`; `tx.refreshToken.findFirst` trả bản ghi hợp lệ; `updateMany` trả `count = 1`.
- **Test Steps:** Gọi `AuthService.refresh(rawToken)`.
- **Expected Result:** Token cũ được thu hồi (`revokedAt`), cấp cặp token mới; `message = "Gia hạn mã truy cập thành công"`.

### IT22_RefreshRotation_TC002 — Refresh token không hợp lệ/hết hạn
- **Loại test:** Exception
- **Pre-condition:** Token sai chữ ký, hết hạn, đã thu hồi hoặc user bị khóa/xóa.
- **Test Data:** `jwt.verifyAsync` ném lỗi.
- **Test Steps:** Gọi `AuthService.refresh`.
- **Expected Result:** Ném `401` với `error_code = "AUTH_INVALID_REFRESH_TOKEN"`.

### IT23_SoftDeleteExclusion_TC001 — Xóa mềm và loại khỏi danh sách
- **Loại test:** Normal
- **Pre-condition:** Tài khoản tồn tại, actorId khác id.
- **Test Data:** `id`, `actorId` khác nhau.
- **Test Steps:** Gọi `UsersService.delete(id, actorId)`.
- **Expected Result:** Trong một transaction: `user.update` set `isDeleted = true`, `isActive = false`, `deletedAt`; `aiQuotaConfig.updateMany` và `refreshToken.updateMany` được gọi; `list` luôn lọc `isDeleted = false`.

### IT23_SoftDeleteExclusion_TC002 — Không thể xóa chính mình
- **Loại test:** Exception
- **Pre-condition:** `id === actorId`.
- **Test Data:** —
- **Test Steps:** Gọi `UsersService.delete(id, id)`.
- **Expected Result:** Ném `403` với `error_code = "USER_CANNOT_DELETE_SELF"`.

---

## 6. Phân hệ Desktop Client (Pytest Integration)
Các kịch bản tích hợp thuộc phân hệ Desktop Client được tự động hóa độc lập qua bộ test Python:
- `IT05_AiTestcaseGeneration`: Tích hợp nạp file đề bài với `AiService` và `ApiClient` (đã test tại `tests/integration/test_testcase_generation_from_document.py`).
- `IT08_CExactMatch`: Tích hợp biên dịch và so khớp byte-exact cho môn C (`test_matching_strategies.py`).
- `IT09_JavaFloatingPoint`: Tích hợp máy ảo Java và so khớp sai số thực epsilon $\le 10^{-5}$ (`test_matching_strategies.py`).
- `IT10_PythonUnorderedTokens`: Tích hợp trình thông dịch Python và so khớp token không phụ thuộc thứ tự (`test_matching_strategies.py`).
- `IT14_GradebookExport`: Tích hợp dữ liệu chấm điểm và xuất file `results.csv` 7 cột UTF-8 BOM (`test_export_service.py`).
