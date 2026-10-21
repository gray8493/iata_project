# Thông Tin Chung Kiểm Thử Unit Test

- **Phân hệ kiểm thử**: Desktop Client — Bộ phân tích dữ liệu dán (tab "Dán Nhiều Testcase")
- **Module kiểm thử**: `TestcasePasteParser` (`apps/desktop-client/src/services/testcase_paste_parser.py`)
- **Người thực hiện (Tester/Dev)**: Đinh Thành Nam
- **Ngày tạo**: 21/10/2026
- **Cập nhật lần cuối**: 21/10/2026 - 10:15
- **Tài liệu liên quan**:
  - [Quy tắc kiểm thử Testcase](file:///e:/AITA/rules/testcase-rules.md)
  - [Đặc tả kiểm thử hệ thống — ST05_TestcaseEditor](file:///e:/AITA/docs/testcases/3-system/system-test-specification.md)
- **Đặc tả Pytest tương ứng**: `tests/unit/test_testcase_paste_parser.py`
- **Tổng số Testcase**: 12 Testcases (Phân loại: 03 Normal, 04 Boundary, 05 Exception)

> **Ghi chú thiết kế (khớp mã nguồn `testcase_paste_parser.py`)**:
> - Đầu vào nhận **một trong hai** định dạng: (1) JSON mảng `[{"input": "...", "output": "..."}]`
>   (chấp nhận bọc trong khoá `testcases`/`data`/`items` và các tên khoá thay thế
>   `stdin`/`input_data`/`input` ↔ `stdout`/`expected_output`/`output`), hoặc
>   (2) các khối văn bản ngăn bằng dòng `---`, trong mỗi khối dùng dòng `===` để tách input/output.
> - Mỗi khối được cắt khoảng trắng/dòng trống ở hai đầu (giữ khoảng trắng bên trong dòng).
> - Hàm **không bao giờ ném ngoại lệ**: luôn trả về danh sách `ParsedTestcase`, mỗi phần tử có
>   `is_valid` và `error` để giao diện tô đỏ dòng lỗi. Dòng lỗi **không** được nạp vào danh sách.
> - `input` rỗng vẫn hợp lệ (bài không đọc stdin); `output` rỗng là lỗi.

---

# ==============================================================================

# PHẦN 1: ĐỊNH DẠNG JSON VÀ KHỐI VĂN BẢN (NORMAL)

# ===================================================================

# UT02_TestcasePasteParser_TC001: Dán JSON mảng hợp lệ tạo đúng danh sách testcase

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Chuỗi dán là `[{"input": "1 2", "output": "3"}, {"input": "4", "output": "8"}]`.

#### Các bước thực hiện (Test Steps)

1. Gọi `parse_testcase_text` với chuỗi trên.
2. Kiểm tra số phần tử, `is_valid`, `input_data`, `expected_output`, `index`.

#### Kết quả kỳ vọng (Expected Result)

- Trả về 2 phần tử, cả hai `is_valid = True`.
- Phần tử 1: input `1 2`, output `3`; phần tử 2 có `index = 2`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | 2 testcase hợp lệ, đúng nội dung | 1 ms | ✅ PASSED |  |

---

# UT02_TestcasePasteParser_TC002: Dán khối văn bản ngăn bằng `---` và `===`

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Chuỗi dán gồm 2 khối: `5\n4 -3 7\n===\nTong = 13` và `1\n===\nTong = 1`, ngăn bởi dòng `---`.

#### Các bước thực hiện (Test Steps)

1. Gọi `parse_testcase_text` với chuỗi trên.

#### Kết quả kỳ vọng (Expected Result)

- Trả về 2 testcase hợp lệ.
- Input lần lượt `5\n4 -3 7`, `1`; output lần lượt `Tong = 13`, `Tong = 1`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | Tách đúng 2 khối, đúng input/output | 1 ms | ✅ PASSED |  |

---

# UT02_TestcasePasteParser_TC003: Output nhiều dòng giữ nguyên thứ tự dòng

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Khối dán có output 3 dòng: `Tong = 6`, `Max = 3`, `Min = 1`.

#### Các bước thực hiện (Test Steps)

1. Gọi `parse_testcase_text` với khối trên.

#### Kết quả kỳ vọng (Expected Result)

- `expected_output == "Tong = 6\nMax = 3\nMin = 1"` (nối bằng `\n`, đúng thứ tự).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | Giữ đúng 3 dòng | 1 ms | ✅ PASSED |  |

---

# ==============================================================================

# PHẦN 2: CÁC TRƯỜNG HỢP BIÊN (BOUNDARY)

# ===================================================================

# UT02_TestcasePasteParser_TC004: Dòng trống đầu/cuối mỗi khối bị cắt bỏ

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Chuỗi dán có nhiều dòng trống bao quanh mỗi khối và quanh dòng `===`.

#### Các bước thực hiện (Test Steps)

1. Gọi `parse_testcase_text` với chuỗi `"\n\n1 2\n\n===\n\n3\n\n---\n\n4\n===\n8\n\n"`.

#### Kết quả kỳ vọng (Expected Result)

- Vẫn nhận 2 testcase hợp lệ.
- Input/output không còn dòng trống ở hai đầu: `1 2`/`3` và `4`/`8`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | Cắt đúng dòng trống | 1 ms | ✅ PASSED |  |

---

# UT02_TestcasePasteParser_TC005: JSON bọc trong khoá `testcases` và tên khoá thay thế

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Chuỗi dán là `{"testcases": [{"input_data": "a", "expected_output": "b"}, {"stdin": ["1", "2"], "stdout": "3"}]}`.

#### Các bước thực hiện (Test Steps)

1. Gọi `parse_testcase_text` với chuỗi trên.

#### Kết quả kỳ vọng (Expected Result)

- Nhận 2 testcase hợp lệ.
- Input lần lượt `a`, `1\n2` (mảng dòng của `stdin` được nối bằng `\n`); output `b`, `3`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | Nhận đúng khoá bọc và khoá thay thế | 1 ms | ✅ PASSED | |

---

# UT02_TestcasePasteParser_TC006: Một testcase duy nhất không cần dòng `---`

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Chuỗi dán chỉ có `7\n===\n14`.

#### Các bước thực hiện (Test Steps)

1. Gọi `parse_testcase_text` với chuỗi trên.

#### Kết quả kỳ vọng (Expected Result)

- Trả về đúng 1 testcase hợp lệ với input `7`, output `14`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | 1 testcase hợp lệ | 1 ms | ✅ PASSED | |

---

# UT02_TestcasePasteParser_TC007: Input rỗng vẫn hợp lệ

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Chuỗi dán là `[{"input": "", "output": "Hello"}]` (bài không đọc stdin).

#### Các bước thực hiện (Test Steps)

1. Gọi `parse_testcase_text` với chuỗi trên.

#### Kết quả kỳ vọng (Expected Result)

- Phần tử có `is_valid = True`, `input_data = ""`, `expected_output = "Hello"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | Input rỗng được chấp nhận | 1 ms | ✅ PASSED | |

---

# ==============================================================================

# PHẦN 3: DỮ LIỆU SAI (EXCEPTION) — KHÔNG ĐƯỢC NẠP IM LẶNG

# ===================================================================

# UT02_TestcasePasteParser_TC008: JSON sai cú pháp trả về dòng lỗi

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Chuỗi dán là `[{"input": "1", "output": }]` (thiếu giá trị).

#### Các bước thực hiện (Test Steps)

1. Gọi `parse_testcase_text` với chuỗi trên.

#### Kết quả kỳ vọng (Expected Result)

- Trả về 1 phần tử có `is_valid = False`, `error` chứa `"JSON không hợp lệ"` kèm vị trí lỗi.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | Báo lỗi JSON, không nạp | 1 ms | ✅ PASSED | |

---

# UT02_TestcasePasteParser_TC009: Khối thiếu dòng `===` bị báo lỗi

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Chuỗi dán là `1 2\n3` (không có `===`).

#### Các bước thực hiện (Test Steps)

1. Gọi `parse_testcase_text` với chuỗi trên.

#### Kết quả kỳ vọng (Expected Result)

- Trả về 1 phần tử `is_valid = False`; `error` nêu rõ thiếu dòng `===`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | Báo thiếu `===`, không nạp | 1 ms | ✅ PASSED | |

---

# UT02_TestcasePasteParser_TC010: Output rỗng bị báo lỗi

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Chuỗi dán có 2 khối: khối 1 hợp lệ, khối 2 có `===` nhưng output rỗng.

#### Các bước thực hiện (Test Steps)

1. Gọi `parse_testcase_text` với chuỗi `"1\n===\n2\n---\n3\n===\n"`.

#### Kết quả kỳ vọng (Expected Result)

- Khối 1 hợp lệ; khối 2 `is_valid = False`, `error` nhắc tới `output`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | Chỉ khối lỗi bị đánh dấu | 1 ms | ✅ PASSED | |

---

# UT02_TestcasePasteParser_TC011: Dữ liệu dán trống báo lỗi rõ ràng

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Chuỗi dán chỉ có khoảng trắng và dòng trống.

#### Các bước thực hiện (Test Steps)

1. Gọi `parse_testcase_text` với `"   \n\n"`.

#### Kết quả kỳ vọng (Expected Result)

- Trả về 1 phần tử `is_valid = False`, `error` chứa `"Chưa có dữ liệu"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | Báo chưa có dữ liệu | 1 ms | ✅ PASSED | |

---

# UT02_TestcasePasteParser_TC012: Một phần tử JSON lỗi không làm mất phần tử hợp lệ

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Mảng JSON có 3 phần tử: 2 hợp lệ, 1 thiếu khoá `output`.

#### Các bước thực hiện (Test Steps)

1. Gọi `parse_testcase_text` với mảng trên.

#### Kết quả kỳ vọng (Expected Result)

- Có đúng 2 phần tử hợp lệ; phần tử thiếu khoá có `is_valid = False` và `error` chứa `"thiếu khoá"`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 21/10/2026 | Pytest Runner | Giữ 2 phần tử hợp lệ, báo lỗi phần tử còn lại | 1 ms | ✅ PASSED | |
