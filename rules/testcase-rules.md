# Quy Tắc Đặt Mã & Soạn Thảo Testcase (Testcase Specification Rules)
## Dự án: AITA - Automated Grading Tool

Tài liệu này quy định chuẩn bắt buộc khi đặt mã định danh, phân loại và trình bày kịch bản kiểm thử (Testcase) cho toàn bộ các thành viên trong dự án **AITA**.

---

## 1. Cấu Trúc Đặt Mã Định Danh Testcase (Testcase ID Syntax)

Mọi testcase trong dự án bắt buộc phải tuân theo cấu trúc chuẩn:

```text
<Loại Test><Số phân hệ>_<Tên API hoặc Module>_TC<Số thứ tự testcase>
```

### Chi tiết các thành phần:

1. **`<Loại Test>`**: 2 chữ cái viết hoa xác định cấp độ kiểm thử:
   - **`UT`**: Unit Test (Kiểm thử đơn vị hàm / class / logic nhỏ)
   - **`IT`**: Integration Test (Kiểm thử tích hợp giữa các module)
   - **`ST`**: System Test (Kiểm thử toàn bộ hệ thống ứng dụng Desktop)
   - **`AT`**: Acceptance Test (Kiểm thử chấp nhận / Nghiệm thu UAT)

2. **`<Số phân hệ>`**: 2 chữ số (`01`, `02`, `03`,...) đại diện cho mã module trong dự án (sẽ được đánh số theo Danh mục API/Module chính thức sau khi chốt). 
   *(Ví dụ minh họa: `01` - MatchingStrategy, `02` - CRunner, `03` - JavaRunner, `04` - PythonRunner,...)*


3. **`_`**: Dấu gạch dưới để phân tách giữa các nhóm thông tin.

4. **`<Tên API hoặc Module>`**: Tên chính xác của API hoặc Class được test, viết theo kiểu **PascalCase** (ví dụ: `MatchingStrategy`, `CRunner`, `JavaRunner`).

5. **`_`**: Dấu gạch dưới.

6. **`TC<Số thứ tự>`**: Tiền tố `TC` kèm theo 3 chữ số (`TC001`, `TC002`, `TC003`,...).

---

## 2. Bảng Ví Dụ Đặt Mã Chuẩn

| Cấp độ test | Module kiểm thử | Mã Testcase HỢP LỆ (✅ Valid) | Mã SAI QUY TẮC (❌ Invalid) | Lý do sai |
| :--- | :--- | :--- | :--- | :--- |
| **Unit Test** | So khớp kết quả | `UT01_MatchingStrategy_TC001` | `tc01_matching` | Không đúng định dạng |
| **Unit Test** | So khớp kết quả | `UT01_MatchingStrategy_TC002` | `UT01-MatchingStrategy-TC02` | Dùng dấu gạch ngang `-` |
| **Unit Test** | Trình chạy code C | `UT02_CRunner_TC001` | `UT_C_01` | Thiếu tên đầy đủ của module |
| **Integration**| Tích hợp C Runner & Timeout | `IT02_CRunnerTimeout_TC001` | `IT_runner_1` | Thiếu mã phân hệ và số TC |
| **System Test**| Chấm bài cả lớp | `ST01_BatchGrading_TC001` | `test_system_01` | Viết thường toàn bộ |

---

## 3. Quy Chuẩn Trình Bày Kịch Bản Test (Format Rules)

> [!IMPORTANT]
> 1. **TIÊU ĐỀ TESTCASE LÀ HEADING 1 (`#`) BAO GỒM CẢ MÃ VÀ TÊN TESTCASE**:
>    Cú pháp: `# <Mã_Testcase>: <Tên testcase>`
>    Ví dụ: `# UT01_Login_TC001: Đăng nhập thành công với tài khoản hợp lệ`.
> 2. **TẤT CẢ CÁC MỤC BÊN TRONG NÂNG LÊN HEADING 4 (`####`)**:
>    - `#### Loại test`
>    - `#### Tiền điều kiện (Pre-condition)`
>    - `#### Các bước thực hiện (Test Steps)`
>    - `#### Kết quả kỳ vọng (Expected Result)`
>    - `#### Bảng kết quả kiểm thử (Execution Result)`
> 3. **BỎ MỤC MÔ TẢ**: Không cần viết mục mô tả lặp lại.

### Mẫu khối chuẩn cho từng Testcase:

```markdown
# UT01_Login_TC001: Đăng nhập thành công với tài khoản hợp lệ

#### Loại test
Normal

#### Tiền điều kiện (Pre-condition)
- Hệ thống đang mở giao diện đăng nhập.
- Tài khoản "teacher@fpt.edu.vn" đã được kích hoạt trong CSDL.

#### Các bước thực hiện (Test Steps)
1. Nhập email "teacher@fpt.edu.vn" vào ô Email.
2. Nhập mật khẩu "Password@123" vào ô Mật khẩu.
3. Bấm nút "Đăng nhập".

#### Kết quả kỳ vọng (Expected Result)
Đăng nhập thành công, chuyển hướng vào Dashboard giảng viên và lưu phiên làm việc.

#### Bảng kết quả kiểm thử (Execution Result)
| Lần test | Ngày test | Người chạy test | Kết quả thực tế (Actual Result) | Thời gian chạy | Trạng thái | Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| Lần 1 | 10/09/2026 | Nguyễn Văn A | Đăng nhập thành công, vào Dashboard | 120 ms | ✅ PASSED | Chạy mượt mà |
```

---

## 4. Phân Loại Kịch Bản Kiểm Thử (Test Types)

Mỗi module khi viết testcase bắt buộc phải có đủ 3 nhóm trường hợp:

1. **Normal (Trường hợp thông thường)**:
   - Dữ liệu đầu vào đúng chuẩn, bài làm sinh viên chạy ra kết quả thông thường.
2. **Boundary (Trường hợp biên)**:
   - Đầu ra là chuỗi rỗng `""`, số 0, số âm, mảng rỗng, sai số làm tròn số thực ($10^{-5}$), giá trị cực đại/cực tiểu.
3. **Exception (Trường hợp lỗi / ngoại lệ)**:
   - Dữ liệu `null`, `undefined`, file không tồn tại, lỗi vòng lặp vô hạn `while(true)`, tràn bộ nhớ RAM.

---

## 5. Tài Liệu Mẫu Tham Khảo

File kịch bản mẫu hoàn chỉnh đã được triển khai sẵn tại:
👉 **[docs/testcases/1-unit/unit-test-template.md](file:///e:/AITA/docs/testcases/1-unit/unit-test-template.md)**
