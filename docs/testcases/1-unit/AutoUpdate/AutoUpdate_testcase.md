# Thông Tin Chung Kiểm Thử Unit Test

- **Phân hệ kiểm thử**: Phân hệ Auto-Update (Desktop Client)
- **Đối tượng kiểm thử**:
  - `services.update_service` — so sánh phiên bản, tải artifact, xác minh SHA-256, sinh `update.bat`.
  - `core.version` — nguồn phiên bản duy nhất.
- **Người thực hiện (Tester/Dev)**: AITA Development Team
- **Ngày tạo**: 19/10/2026
- **Cập nhật lần cuối**: 19/10/2026 - 08:00
- **Tài liệu liên quan**:
  - [Quy tắc kiểm thử Testcase](file:///e:/AITA/rules/testcase-rules.md)
  - [OpenAPI /system/version](file:///e:/AITA/docs/apis/openapi.yaml)
- **Đặc tả Pytest tương ứng**: `apps/desktop-client/tests/test_update_service.py`
- **Tổng số Testcase**: 08 Testcases (Phân loại: 03 Normal, 02 Boundary, 03 Exception)

> **Ghi chú thiết kế (khớp mã nguồn `UpdateService`)**:
> - `is_newer(remote, current)` so sánh version kiểu số, zero-pad (2.10 > 2.9).
> - `download()` chỉ chấp nhận URL `https://`, tải về file `.part`, xác minh SHA-256 rồi mới đổi tên.
> - `build_update_script()` sinh `update.bat`: artifact `exe` thì `copy /Y`, artifact `zip` thì `robocopy /E` có loại trừ `data/`, `*.db`.
> - `check_for_update()` nuốt lỗi mạng và trả `None` để không chặn đăng nhập.

---

# UT07_AutoUpdate_TC001: Phát hiện có phiên bản mới hơn

#### Loại test

Normal

#### Dữ liệu kiểm thử (Test Data)

- `is_newer("2.5.0", "2.4.9")`, `is_newer("2.6.0", "2.5.0")`.

#### Các bước thực hiện (Test Steps)

1. Gọi `is_newer()` với version mới > version hiện tại.

#### Kết quả kỳ vọng (Expected Result)

- Trả `True` để UI hiển thị hộp thoại cập nhật.

---

# UT07_AutoUpdate_TC002: Biên so sánh phiên bản bằng nhau & so sánh kiểu số

#### Loại test

Boundary

#### Dữ liệu kiểm thử (Test Data)

- `is_newer("2.5.0", "2.5")` (bằng nhau sau zero-pad) và `is_newer("2.10.0", "2.9.0")`.

#### Các bước thực hiện (Test Steps)

1. Gọi `is_newer()` với hai version bằng nhau và với cặp 2.10 vs 2.9.

#### Kết quả kỳ vọng (Expected Result)

- `2.5.0` vs `2.5` trả `False`; `2.10.0` vs `2.9.0` trả `True` (không so sánh chuỗi).

---

# UT07_AutoUpdate_TC003: Tải artifact và xác minh SHA-256 hợp lệ

#### Loại test

Normal

#### Dữ liệu kiểm thử (Test Data)

- Payload giả, checksum đúng, HTTP 200 qua MockTransport.

#### Các bước thực hiện (Test Steps)

1. Gọi `UpdateService.download(artifact, dest_dir)`.

#### Kết quả kỳ vọng (Expected Result)

- File được ghi đúng nội dung; không còn file `.part`.

---

# UT07_AutoUpdate_TC006: Sinh update.bat cho artifact .exe

#### Loại test

Normal

#### Dữ liệu kiểm thử (Test Data)

- `install_dir="C:\AITA"`, `exe_name="AITA.exe"`, `artifact_path="C:\Temp\AITA.exe"`, `pid=4242`.

#### Các bước thực hiện (Test Steps)

1. Gọi `build_update_script(artifact_type="exe", ...)`.

#### Kết quả kỳ vọng (Expected Result)

- Script chờ PID thoát, `copy /Y "%NEW%" "%TARGET%"`, `start "" "%TARGET%"`, tự xóa `%~f0`.

---

# UT07_AutoUpdate_TC007: Sinh update.bat cho artifact .zip giữ dữ liệu người dùng

#### Loại test

Boundary

#### Dữ liệu kiểm thử (Test Data)

- `install_dir="C:\AITA"`, `payload_dir="C:\Temp\payload"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `build_update_script(artifact_type="zip", ...)`.

#### Kết quả kỳ vọng (Expected Result)

- Dùng `robocopy "%SRC%" "%TARGET%" /E` kèm `/XD data` và `/XF *.db ...` để không xóa `local_grading.db`.

---

# UT07_AutoUpdate_TC004: Từ chối khi checksum không khớp

#### Loại test

Exception

#### Dữ liệu kiểm thử (Test Data)

- Payload tải về khác với checksum trong manifest.

#### Các bước thực hiện (Test Steps)

1. Gọi `UpdateService.download()` với checksum sai.

#### Kết quả kỳ vọng (Expected Result)

- Ném `UpdateError`; xóa sạch file tạm; KHÔNG thay thế bản cài đặt.

---

# UT07_AutoUpdate_TC005: Từ chối URL tải không an toàn

#### Loại test

Exception

#### Dữ liệu kiểm thử (Test Data)

- `artifact.url = "http://example.com/AITA.exe"`.

#### Các bước thực hiện (Test Steps)

1. Gọi `UpdateService.download()`.

#### Kết quả kỳ vọng (Expected Result)

- Ném `UpdateError` vì chỉ chấp nhận `https://`.

---

# UT07_AutoUpdate_TC008: Không chặn app khi backend lỗi mạng

#### Loại test

Exception

#### Dữ liệu kiểm thử (Test Data)

- `ApiClient.get` ném `httpx.ConnectError`.

#### Các bước thực hiện (Test Steps)

1. Gọi `UpdateService.check_for_update()`.

#### Kết quả kỳ vọng (Expected Result)

- Trả `None`; app khởi động bình thường tới màn hình Đăng Nhập.
