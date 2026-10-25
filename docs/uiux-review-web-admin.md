# Báo cáo đánh giá UI/UX — Web Admin AITA

> Tài liệu thuộc đồ án SWD392 — đánh giá giao diện `apps/web-admin` (Next.js 14, Tailwind CSS) theo các tiêu chuẩn thiết kế giao diện người dùng.
>
> Ngày đánh giá: 25/10/2026

## 1. Mục tiêu và phạm vi

Đánh giá giao diện Cổng quản trị web AITA (web-admin) gồm 5 màn hình chính:

1. Trang Đăng nhập (`/login`)
2. Bảng điều khiển tổng quan (`/dashboard`)
3. Quản lý tài khoản giảng viên (`/users`)
4. Giám sát hạn ngạch AI (`/ai-quota`)
5. Báo cáo & kiểm toán (`/reports`)

## 2. Tiêu chuẩn áp dụng

- **10 nguyên tắc heuristic của Jakob Nielsen** (visibility of system status, match between system and real world, user control and freedom, consistency and standards, error prevention, recognition rather than recall, flexibility and efficiency of use, aesthetic and minimalist design, help users recognize/diagnose/recover from errors, help and documentation).
- **WCAG 2.1 mức AA** (khả năng truy cập: ngữ nghĩa HTML, ARIA, điều hướng bàn phím, focus visible, tương phản).
- **Quy ước App Router của Next.js 14** (loading/error/not-found boundaries, metadata).
- **Nguyên tắc thiết kế trực quan**: hierarchy, consistency, feedback, affordance.

## 3. Điểm mạnh (đã đạt chuẩn)

| Tiêu chí | Nhận xét |
|---|---|
| Hệ thống thiết kế nhất quán | Màu chủ đạo `#2F80ED` đồng bộ với desktop app (`ui/styles/theme.py`), card/table/button dùng chung một bộ class Tailwind trên mọi trang |
| Phản hồi trạng thái đầy đủ | Trạng thái loading (spinner), empty state có mô tả hướng dẫn, banner lỗi/thành công tự ẩn sau 4–6 giây |
| Responsive | Sidebar chuyển thành drawer trên mobile, lưới KPI 1→2→4 cột, bảng cuộn ngang |
| Ngăn ngừa lỗi | Confirm dialog khi xóa, chặn khóa/xóa tài khoản đang đăng nhập và tài khoản ADMIN, nút nguy hiểm màu đỏ |
| Nhận diện hơn ghi nhớ | Breadcrumb, tiêu đề trang rõ ràng, badge màu cho vai trò/trạng thái, mã log hiển thị rút gọn |
| Ngôn ngữ | Toàn bộ tiếng Việt, có `lang="vi"`, font Inter hỗ trợ subset tiếng Việt |
| Hiệu quả sử dụng | Debounce tìm kiếm 350ms, phân trang, xuất CSV có BOM UTF-8 (không lỗi font tiếng Việt trên Excel) |

## 4. Thiếu sót phát hiện (theo mức độ nghiêm trọng)

### 4.1. Nghiêm trọng

| # | Vấn đề | Vị trí | Tác động |
|---|---|---|---|
| N1 | Key `feature_type` trong bảng ánh xạ nhãn **không khớp enum backend**. Backend dùng `TESTCASE_GEN, CODE_REVIEW, PLAGIARISM, UI_EVALUATION, PE_CODE_EVAL` (xem `apps/central-backend/src/modules/ai-gateway/ai-quota.service.ts:5`), trong khi trang dashboard/reports dùng `GENERATE_TESTCASES, REVIEW_CODE, VERIFY_PLAGIARISM, EVALUATE_WEB_UI` | `dashboard/page.tsx`, `reports/page.tsx` | Nhãn tính năng luôn hiện mã thô (ví dụ "TESTCASE_GEN"); bộ lọc "Tác vụ AI" ở trang reports **không bao giờ khớp** → danh sách luôn rỗng khi lọc |
| N2 | Không có cơ chế bảo vệ route: truy cập `/dashboard` khi chưa đăng nhập chỉ hiện banner lỗi thay vì chuyển hướng `/login`; không có middleware/auth guard | `(dashboard)/layout.tsx` | Trải nghiệm khó hiểu + lộ giao diện nội bộ khi chưa xác thực |
| N3 | Checkbox "Ghi nhớ phiên đăng nhập" không có tác dụng — token luôn ghi vào `localStorage` bất kể người dùng chọn gì | `(auth)/login/page.tsx` | Vi phạm nguyên tắc "trung thực với người dùng" (phần tử điều khiển chết) |

### 4.2. Trung bình

| # | Vấn đề | Vị trí | Tác động |
|---|---|---|---|
| T1 | Modal thiếu chuẩn a11y: không `role="dialog"`/`aria-modal`, không đóng bằng phím Esc, không đóng khi click nền mờ, không đưa focus vào khi mở | 5 modal ở `users`, `ai-quota`, `reports` | Người dùng bàn phím/màn hình đọc không thao tác được; hành vi đóng không nhất quán với drawer mobile |
| T2 | Lỗi validate form (tên đăng nhập, mật khẩu...) hiển thị ở banner **đầu trang** trong khi modal đang mở ở giữa màn hình | `users/page.tsx` | Người dùng không nhìn thấy thông báo lỗi (visibility of system status) |
| T3 | Trạng thái "Cập nhật lúc ..." luôn hiển thị chấm xanh kể cả khi mất kết nối | `dashboard/page.tsx` | Thông tin trạng thái sai lệch |
| T4 | Sidebar không có icon, link đang mở thiếu `aria-current="page"` | `(dashboard)/layout.tsx` | Khó quét nhanh; trình đọc màn hình không biết trang hiện tại |
| T5 | Form đăng nhập thiếu thuộc tính `autocomplete`; modal tạo/sửa tài khoản không có nút hiện/ẩn mật khẩu (thiếu nhất quán với trang login) | `login/page.tsx`, `users/page.tsx` | Trình quản lý mật khẩu không hoạt động; kém nhất quán |
| T6 | Dropdown "Xuất báo cáo" không đóng khi click ra ngoài hoặc nhấn Esc, thiếu `aria-expanded` | `dashboard/page.tsx` | User control and freedom |
| T7 | Trang reports có 3 nút xuất rời rạc (Làm mới, Tải JSON, Xuất báo cáo); Tải JSON là nút phụ nhưng chiếm vị trí ngang hàng | `reports/page.tsx` | Aesthetic and minimalist design; tải thủ công |
| T8 | `document.title` tĩnh cho mọi trang; thiếu `not-found.tsx`; không có `loading.tsx`/`error.tsx` theo chuẩn App Router | toàn bộ app | Khó phân biệt tab khi mở nhiều trang; 404 mặc định |

### 4.3. Thấp

| # | Vấn đề | Gợi ý |
|---|---|---|
| TH1 | KPI "Lượt yêu cầu AI" ghi chú "Ghi nhận trong tháng này" nhưng dữ liệu là tổng mọi thời gian | Đổi chú thích cho đúng hoặc bổ sung API đếm theo tháng |
| TH2 | Bảng "Nhật ký sử dụng AI" lặp 3 lần (dashboard, tab LOGS của ai-quota, reports) | Giữ bảng tóm tắt ở dashboard (5 dòng), bảng đầy đủ chỉ ở reports |
| TH3 | Empty state chỉ có chữ, không icon; ô tìm kiếm không có nút xóa | Thêm icon minh họa + nút x |
| TH4 | Bảng chưa có sort theo cột; chưa có skeleton loading | Thêm sort server-side cho cột token/thời gian |
| TH5 | Chữ 13px cho nội dung bảng (nhỏ hơn khuyến nghị 16px của WCAG nhưng chấp nhận được với mật độ admin) | Cân nhắc 14px nếu đối tượng dùng lâu dài |
| TH6 | Class animation `animate-in fade-in zoom-in-95` được dùng nhưng chưa cài plugin `tailwindcss-animate` → animation không có hiệu lực | Đã bật plugin trong đợt sửa này |

## 5. Các thay đổi đã thực hiện (sửa code)

### 5.1. Tài sản dùng chung mới

| File | Mô tả |
|---|---|
| `src/lib/feature-labels.ts` | Bản đồ nhãn tính năng AI dùng chung, key **đúng enum backend** (gồm `PE_CODE_EVAL`), kèm màu badge và hàm `featureLabel()`/`featureBadgeClass()` |
| `src/components/ui/modal.tsx` | Component Modal chuẩn a11y: `role="dialog"`, `aria-modal`, `aria-labelledby/describedby`, đóng bằng Esc, click backdrop, khóa scroll nền, focus vào dialog khi mở |
| `src/components/ui/alert.tsx` | Component thông báo dùng chung: `role="alert"` (lỗi) / `role="status"` (thành công/info), nút Đóng |
| `src/app/not-found.tsx` | Trang 404 tiếng Việt có nút quay về bảng điều khiển |

### 5.2. Sửa theo từng màn hình

| Màn hình | Thay đổi |
|---|---|
| **Login** | `autoComplete="username"/"current-password"`; nối dây "Ghi nhớ phiên đăng nhập": tích → `localStorage`, bỏ tích → `sessionStorage` (phiên hết khi đóng trình duyệt, có ghi chú giải thích); redirect `/dashboard` nếu đã có phiên; thông báo "Quên mật khẩu?" chuyển sang dạng thông tin (xanh dương) thay vì style lỗi |
| **Layout (sidebar)** | Auth guard: không có token → chuyển `/login`; menu có icon (lucide); link đang mở có `aria-current="page"`; `<nav aria-label>`; `document.title` đổi theo trang; logout xóa cả hai storage |
| **Dashboard** | Nhãn tính năng đúng (fix N1); chấm trạng thái đỏ + "Không kết nối được máy chủ" khi lỗi (fix T3); chú thích KPI "Tổng lượt ghi nhận" (fix TH1); dropdown xuất đóng khi click ngoài/Esc + `aria-expanded` (fix T6); banner lỗi dùng Alert; badge tính năng có màu; empty state có icon; `th scope="col"` |
| **Users** | 3 modal dùng Modal dùng chung (Esc/backdrop/focus) (fix T1); lỗi validate hiển thị **bên trong** modal (fix T2); nút Hiện/Ẩn mật khẩu ở modal tạo/sửa (fix T5); nút xóa nội dung tìm kiếm; banner dùng Alert; copy xác nhận xóa nêu rõ "vô hiệu hóa vĩnh viễn, thu hồi phiên" (đúng hành vi soft-delete của backend) |
| **AI Quota** | Map nhãn dùng chung (bổ sung nhãn `PE_CODE_EVAL`); modal điều chỉnh hạn ngạch dùng Modal chung; banner dùng Alert; badge màu; empty state icon; `th scope="col"` |
| **Reports** | **Fix bộ lọc "Tác vụ AI"** dùng đúng key backend (fix N1); gộp "Tải JSON" vào modal xuất báo cáo (fix T7); 2 modal dùng Modal chung; banner dùng Alert; badge màu; empty state icon; `th scope="col"` |
| **Cấu hình** | Bật plugin `tailwindcss-animate` để các class `animate-in` đã dùng có hiệu lực (fix TH6) |

## 6. Gợi ý cải tiến dài hạn (chưa thực hiện trong đợt này)

1. **Biểu đồ trực quan**: dùng `recharts` vẽ biểu đồ đường/cột cho tiến độ tiêu thụ token theo ngày thay vì thanh tiến trình đơn giản.
2. **Sort cột server-side**: sắp xếp bảng nhật ký theo tổng token/thời gian (backend thêm tham số `sort_by`, `order`).
3. **Skeleton loading** thay spinner cho KPI và bảng (giảm cảm giác giật layout).
4. **Toast tập trung**: dùng `sonner` hoặc một toast manager duy nhất thay vì banner nội tuyến từng trang.
5. **Hợp nhất bảng nhật ký**: dashboard chỉ giữ 5 bản ghi gần nhất dạng tóm tắt, bảng đầy đủ chỉ ở reports (tránh trùng lặp IA).
6. **Dark mode** (class strategy của Tailwind) nếu người dùng làm việc ban đêm.
7. **Kiểm thử tự động UX**: chạy Lighthouse CI để theo dõi điểm accessibility/performance qua từng PR.
8. **Đồng bộ hóa phiên toàn cục**: hiện mỗi trang tự xử lý 401; nên có một interceptor tập trung tự chuyển `/login` khi token hết hạn.
