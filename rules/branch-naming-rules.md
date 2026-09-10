# Quy tắc đặt tên nhánh Git (Git Branch Naming Rules)

Tài liệu này quy định chuẩn đặt tên nhánh Git khi làm việc với tài liệu, đặc tả thiết kế và API trong dự án **AITA Desktop App**.

---

## 1. Cấu trúc đặt tên nhánh chuẩn (Naming Convention)

Dự án quy định 3 nhóm nhánh chính phục vụ cho toàn bộ quy trình phát triển:

### 1.1. Nhánh Tài liệu & Thiết kế API (`docs`)

Dành riêng cho việc tạo tài liệu kiến trúc, đặc tả API (OpenAPI YAML), kịch bản testcase và sơ đồ PlantUML:

- **`docs`**: Tiền tố cố định cho tài liệu.
- **`<tên api>`**: Tên API hoặc module thiết kế (ví dụ: `auth`, `sync`, `user-profile`).
- **`<tên người tạo>`**: Tên hoặc username của người tạo (viết thường, không dấu).

---

### 1.2. Nhánh Lập trình Tính năng (`code`)

Dành cho việc viết mã nguồn phát triển các tính năng, giao diện hoặc logic nghiệp vụ mới:

```text
code-<tên feature>-<tên người tạo>
```

- **`code`**: Tiền tố cố định cho phần viết mã nguồn tính năng.
- **`<tên feature>`**: Tên chức năng/tính năng đang làm (ví dụ: `login-form`, `sync-worker`, `dark-mode`, `document-export`).
- **`<tên người tạo>`**: Tên hoặc username của lập trình viên (viết thường, không dấu).

---

### 1.3. Nhánh Kiểm thử (`test`)

Dành cho việc viết kịch bản test (manual testcases) hoặc viết mã nguồn kiểm thử tự động (automated tests):

```text
test-<level>-<tên người tạo>
```

- **`test`**: Tiền tố cố định cho nhánh kiểm thử.
- **`<level>`**: Cấp độ kiểm thử, chọn đúng một trong các cấp độ chuẩn sau:
  - `unit`: Kiểm thử đơn vị hàm/class/logic nhỏ.
  - `integration`: Kiểm thử tích hợp (IPC, database, API client).
  - `system`: Kiểm thử toàn hệ thống ứng dụng Desktop.
  - `acceptance`: Kiểm thử chấp nhận / nghiệm thu tính năng (UAT).
  - `e2e`: Kiểm thử tự động giao diện End-to-End.
  - `perf`: Kiểm thử hiệu năng (RAM, CPU, thời gian mở app).
- **`<tên người tạo>`**: Tên hoặc username của người thực hiện kiểm thử (viết thường, không dấu).

---

## 2. Quy chuẩn ký tự & Định dạng (Formatting Rules)

1. **Chữ thường (Lowercase)**: Toàn bộ tên nhánh phải viết thường, không viết hoa bất kỳ ký tự nào.
2. **Ký tự phân cách**: Bắt buộc dùng dấu gạch ngang (`-`) giữa các thành phần và giữa các từ. Tuyệt đối không dùng dấu gạch dưới (`_`), dấu gạch chéo (`/`) hoặc khoảng trắng.
3. **Tiếng Việt không dấu**: Tên người tạo, tên tính năng, tên cấp độ phải viết liền không dấu, không dùng emoji hay ký tự đặc biệt.

---

## 3. Bảng ví dụ minh họa (Examples)

| Loại nhánh   | Tình huống                                 | Tên nhánh HỢP LỆ (✅ Valid) | Tên nhánh SAI (❌ Invalid) | Lý do sai                   |
| :------------- | :------------------------------------------- | :------------------------------ | :--------------------------- | :--------------------------- |
| **Docs** | Viết spec cho API Auth do Nam tạo          | `docs-auth-namnv`             | `Docs-Auth-NamNV`          | Viết hoa                    |
| **Docs** | Viết sơ đồ luồng Sync do Linh tạo      | `docs-sync-linh`              | `docs_sync_linh`           | Dùng dấu gạch dưới`_` |
| **Code** | Code form Đăng nhập do Nam làm           | `code-login-form-namnv`       | `code/login-form/namnv`    | Dùng dấu gạch chéo`/`  |
| **Code** | Code tính năng Chế độ tối do An làm   | `code-dark-mode-an`           | `code-chế-độ-tối-an`   | Chứa tiếng Việt có dấu  |
| **Test** | Viết unit test do Tuấn làm                | `test-unit-tuan`              | `test_unit_tuan`           | Dùng dấu gạch dưới`_` |
| **Test** | Viết kiểm thử tích hợp do Linh làm     | `test-integration-linh`       | `test-integration`         | Thiếu tên người tạo     |
| **Test** | Viết kịch bản nghiệm thu UAT do Nam làm | `test-acceptance-namnv`       | `Test-UAT-NamNV`           | Viết hoa                    |

---

## 4. Hướng dẫn lệnh Git thao tác nhanh

### 4.1. Nhánh Tài liệu (`docs`)

```bash
# Tạo và chuyển sang nhánh docs
git checkout -b docs-auth-namnv

# Đẩy nhánh lên remote
git push -u origin docs-auth-namnv
```

### 4.2. Nhánh Lập trình tính năng (`code`)

```bash
# Tạo và chuyển sang nhánh code
git checkout -b code-login-form-namnv

# Đẩy nhánh lên remote
git push -u origin code-login-form-namnv
```

### 4.3. Nhánh Kiểm thử (`test`)

```bash
# Tạo và chuyển sang nhánh test
git checkout -b test-unit-namnv
# hoặc
git checkout -b test-integration-linh

# Đẩy nhánh lên remote
git push -u origin test-unit-namnv
```
