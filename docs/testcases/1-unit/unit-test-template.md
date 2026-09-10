# Thông Tin Chung Kiểm Thử Unit Test

- **API / Module kiểm thử**: `MatchingStrategy`
- **Người thực hiện (Tester/Dev)**: Nguyễn Văn A
- **Ngày tạo**: 10/09/2026
- **Cập nhật lần cuối**: 10/09/2026 - 23:59
- **Tài liệu liên quan**:
  - [Tổng quan hệ thống AITA](file:///e:/AITA/docs/architecture/system-overview.md)
  - [Quy tắc kiểm thử Testcase](file:///e:/AITA/rules/testcase-rules.md)
  - [Quy tắc Git &amp; Workflow](file:///e:/AITA/rules/git-rules.md)
- **Tổng số Testcase**: 06 Testcases (06 Passed, 00 Failed)

---

# UT01_MatchingStrategy_TC001: Khớp chính xác hoàn toàn (Exact Match)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Khởi tạo instance của `MatchingStrategy`.
- Hai chuỗi đầu ra không bị null hoặc undefined.

#### Các bước thực hiện (Test Steps)

1. Khởi tạo `actualOutput = "Hello World"`.
2. Khởi tạo `expectedOutput = "Hello World"`.
3. Thiết lập options: `{ trimWhitespace: false }`.
4. Gọi hàm `MatchingStrategy.compare(actualOutput, expectedOutput, options)`.

#### Kết quả kỳ vọng (Expected Result)

Hàm trả về `true` (Accepted - AC).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result)          | Thời gian chạy | Trạng thái | Ghi chú                |
| :-------: | :--------: | :----------------- | :------------------------------------------- | :--------------: | :----------: | :---------------------- |
|  Lần 1  | 10/09/2026 | Nguyễn Văn A     | Trả về`true`, không có lỗi ngoại lệ |       2 ms       |  ✅ PASSED  | Testcase cơ bản đạt |

---

# UT01_MatchingStrategy_TC002: Bỏ qua khoảng trắng và dấu xuống dòng thừa ở cuối

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Khởi tạo instance của `MatchingStrategy`.
- Tùy chọn `ignoreTrailingWhitespace` được kích hoạt.

#### Các bước thực hiện (Test Steps)

1. Khởi tạo `actualOutput = "Hello World  \n\n"`.
2. Khởi tạo `expectedOutput = "Hello World"`.
3. Thiết lập options: `{ ignoreTrailingWhitespace: true }`.
4. Gọi hàm `MatchingStrategy.compare(actualOutput, expectedOutput, options)`.

#### Kết quả kỳ vọng (Expected Result)

Hàm tự cắt bỏ khoảng trắng cuối và trả về `true` (Accepted - AC).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result)     | Thời gian chạy | Trạng thái | Ghi chú                    |
| :-------: | :--------: | :----------------- | :-------------------------------------- | :--------------: | :----------: | :-------------------------- |
|  Lần 1  | 10/09/2026 | Nguyễn Văn A     | Cắt bỏ`\n` thừa, trả về `true` |       3 ms       |  ✅ PASSED  | Tiêu chí linh hoạt đạt |

---

# UT01_MatchingStrategy_TC003: Khác biệt nội dung chữ (Sai kết quả)

#### Loại test

Normal

#### Tiền điều kiện (Pre-condition)

- Khởi tạo instance của `MatchingStrategy`.

#### Các bước thực hiện (Test Steps)

1. Khởi tạo `actualOutput = "Hello Python"`.
2. Khởi tạo `expectedOutput = "Hello World"`.
3. Thiết lập options: `{}` (mặc định).
4. Gọi hàm `MatchingStrategy.compare(actualOutput, expectedOutput, options)`.

#### Kết quả kỳ vọng (Expected Result)

Hàm trả về `false` (Wrong Answer - WA).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú                          |
| :-------: | :--------: | :----------------- | :---------------------------------- | :--------------: | :----------: | :-------------------------------- |
|  Lần 1  | 10/09/2026 | Nguyễn Văn A     | Trả về`false`, ghi nhận WA     |       1 ms       |  ✅ PASSED  | Phát hiện lỗi bài làm đúng |

---

# UT01_MatchingStrategy_TC004: Xử lý chuỗi rỗng (Empty String)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Khởi tạo instance của `MatchingStrategy`.

#### Các bước thực hiện (Test Steps)

1. Khởi tạo `actualOutput = ""`.
2. Khởi tạo `expectedOutput = ""`.
3. Gọi hàm `MatchingStrategy.compare(actualOutput, expectedOutput, {})`.

#### Kết quả kỳ vọng (Expected Result)

Hàm trả về `true` (Accepted - AC).

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result)  | Thời gian chạy | Trạng thái | Ghi chú                 |
| :-------: | :--------: | :----------------- | :----------------------------------- | :--------------: | :----------: | :----------------------- |
|  Lần 1  | 10/09/2026 | Nguyễn Văn A     | Trả về`true`, xử lý biên tốt |       1 ms       |  ✅ PASSED  | Biên chuỗi rỗng đạt |

---

# UT01_MatchingStrategy_TC005: So sánh số thực có sai số delta cho phép (Floating Tolerance)

#### Loại test

Boundary

#### Tiền điều kiện (Pre-condition)

- Khởi tạo instance của `MatchingStrategy`.
- Cấu hình mức sai số epsilon `0.00001`.

#### Các bước thực hiện (Test Steps)

1. Khởi tạo `actualOutput = "3.141592"`.
2. Khởi tạo `expectedOutput = "3.141590"`.
3. Thiết lập options: `{ epsilon: 0.00001 }`.
4. Gọi hàm `MatchingStrategy.compare(actualOutput, expectedOutput, options)`.

#### Kết quả kỳ vọng (Expected Result)

Độ lệch $|3.141592 - 3.141590| = 0.000002 \le 0.00001$, trả về `true`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result)      | Thời gian chạy | Trạng thái | Ghi chú                |
| :-------: | :--------: | :----------------- | :--------------------------------------- | :--------------: | :----------: | :---------------------- |
|  Lần 1  | 10/09/2026 | Nguyễn Văn A     | Trả về`true`, sai số trong ngưỡng |       4 ms       |  ✅ PASSED  | Phục vụ tốt môn DSA |

---

# UT01_MatchingStrategy_TC006: Xử lý dữ liệu đầu vào bị null hoặc undefined

#### Loại test

Exception

#### Tiền điều kiện (Pre-condition)

- Khởi tạo instance của `MatchingStrategy`.

#### Các bước thực hiện (Test Steps)

1. Khởi tạo `actualOutput = null`.
2. Khởi tạo `expectedOutput = "Result"`.
3. Gọi hàm `MatchingStrategy.compare(actualOutput, expectedOutput, {})`.

#### Kết quả kỳ vọng (Expected Result)

Không làm sập ứng dụng, bắt ngoại lệ an toàn và trả về `false`.

#### Bảng kết quả kiểm thử (Execution Result)

| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result)   | Thời gian chạy | Trạng thái | Ghi chú                      |
| :-------: | :--------: | :----------------- | :------------------------------------ | :--------------: | :----------: | :---------------------------- |
|  Lần 1  | 10/09/2026 | Nguyễn Văn A     | Bắt lỗi an toàn, trả về`false` |       2 ms       |  ✅ PASSED  | Chống crash app thành công |
