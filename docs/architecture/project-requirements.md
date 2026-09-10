# Đề Án Môn Học SWD392: Thiết Kế Hệ Thống Có Hỗ Trợ Của AI (AI-Assisted System Design)
## Đề tài: AITA (AI-Assisted System / AITA Desktop App)

---

## 1. Tổng quan & Mục tiêu dự án (Project Overview & Objectives)

Dự án được thực hiện bởi nhóm từ 4–5 thành viên nhằm phân tích, thiết kế và phát triển một hệ thống phần mềm toàn diện (Full-stack Software System) có sự hỗ trợ của các công cụ Trí tuệ nhân tạo (AI Tools: ChatGPT, Copilot, PlantUML,...).

### Các giai đoạn chính của đồ án:
1. **Requirement Analysis & Modeling**: Phân tích yêu cầu và mô hình hóa hệ thống.
2. **Software Architecture & Design**: Thiết kế kiến trúc phần mềm và cơ sở dữ liệu.
3. **AI-Assisted Coding & UML Modeling**: Lập trình và dựng mô hình UML với sự hỗ trợ của AI.
4. **Final Integration & Demo**: Tích hợp toàn diện các thành phần và báo cáo sản phẩm hoàn chỉnh.

---

## 2. Quy định & Tiêu chí sử dụng AI (AI Usage Policy & Rubric)

Nhóm được khuyến khích sử dụng công cụ AI (ChatGPT, GitHub Copilot, PlantUML,...) nhưng bắt buộc phải tuân thủ các điều kiện:
- **Minh bạch hóa (Transparency)**: Ghi nhận rõ ràng tất cả các Prompt đã sử dụng và Output mà AI đã sinh ra.
- **Thấu hiểu và Làm chủ (Mastery & Justification)**: Tự giải thích các kết quả do AI tạo ra bằng hiểu biết của nhóm; nêu rõ lý do tại sao áp dụng, chỉnh sửa hoặc loại bỏ phần nào.

### Thang đo đánh giá năng lực sử dụng AI (AI Evaluation Rubric - tối đa 10 điểm):
1. **Understanding of AI Output**: Mức độ hiểu sâu về mã nguồn và sơ đồ do AI sinh ra.
2. **Customization & Enhancement**: Khả năng tùy biến, tinh chỉnh và nâng cấp output từ AI cho khớp với bài toán AITA.
3. **Transparency**: Khai báo đầy đủ Prompt + kết quả AI tương ứng trong tài liệu.
4. **Effective & Ethical Usage**: Sử dụng AI hiệu quả, có trách nhiệm và đúng chuẩn mực đạo đức học thuật.

---

## 3. Kế hoạch đánh giá quá trình (On-going Assessment - 40%)

### 3.1. Đánh giá 1 (Evaluation 1 - 20%): Phân tích yêu cầu & Mô hình hóa (Requirement Analysis & Modeling)
- **Nhiệm vụ (Tasks)**:
  - Xác định các Tác nhân (Actors) và Trường hợp sử dụng (Use Cases).
  - Viết bản mô tả chi tiết cho từng Use Case (Use Case Descriptions).
  - Xây dựng 4 loại sơ đồ UML (bằng PlantUML):
    1. **Use Case Diagram**
    2. **Activity Diagram**
    3. **Sequence Diagram**
    4. **Communication Diagram**
- **Sản phẩm nộp (Deliverables)**:
  - Tài liệu lưu vết Prompts và AI Output kèm giải trình nhóm đã hiểu/sửa đổi những gì.
  - File mã nguồn sơ đồ PlantUML (`.puml`) đặt tại `docs/diagrams/puml/`.
  - Ảnh xuất từ sơ đồ (`.png`, `.svg`) để hiển thị báo cáo.

---

### 3.2. Đánh giá 2 (Evaluation 2 - 20%): Kiến trúc & Thiết kế phần mềm (Software Architecture & Design)
- **Nhiệm vụ (Tasks)**:
  - Lựa chọn kiến trúc phần mềm phù hợp (Layered, Clean Architecture, Microservices,...) với sự tham vấn từ AI.
  - Thiết kế các sơ đồ hệ thống:
    - **Component Diagram** (Sơ đồ thành phần)
    - **Deployment Diagram** (Sơ đồ triển khai hệ điều hành / server)
    - **Database Schema** (Thiết kế cơ sở dữ liệu & quan hệ bảng ERD)
    - **Class Diagram** (Sơ đồ lớp cho ít nhất 3 phân hệ - subsystems)
  - Áp dụng đủ **3 mẫu thiết kế (Design Patterns)** trong mã nguồn:
    1. *Một mẫu Khởi tạo (Creational)*: ví dụ Factory Method / Singleton / Builder.
    2. *Một mẫu Cấu trúc (Structural)*: ví dụ Adapter / Facade / Proxy.
    3. *Một mẫu Hành vi (Behavioral)*: ví dụ Strategy / Observer / Command.
- **Sản phẩm nộp (Deliverables)**:
  - Tài liệu kiến trúc kèm lý do lựa chọn (Justification).
  - Các sơ đồ UML thiết kế hệ thống.
  - Đoạn code mẫu đã chú thích (Annotated code) chỉ rõ vị trí áp dụng 3 Design Patterns.
  - Đánh dấu rõ ràng những đoạn code/nội dung được AI hỗ trợ sinh ra.

---

## 4. Đánh giá cuối kỳ & Báo cáo sản phẩm (Final Presentation - 60%)

### 4.1. Yêu cầu sản phẩm (Product Requirements)
- Hoàn thiện báo cáo toàn diện theo mẫu quy định (Report Template).
- Toàn bộ mã nguồn dự án phải hoàn chỉnh, có thể chạy thật và không có lỗi nghiêm trọng (Complete & Functional).
- Trình diễn sản phẩm phần mềm tích hợp hoàn chỉnh (Integrated Software Product Demonstration):
  - **Desktop App (AITA)**: Giao diện máy tính, xử lý offline, tương tác hệ điều hành.
  - **Web API Backend**: Xử lý logic nghiệp vụ trung tâm và xác thực.
  - **Web Admin / Dashboard**: Phân hệ quản trị.

### 4.2. Cơ cấu điểm đánh giá cá nhân (Grading Breakdown)
- **Demo sản phẩm phần mềm tích hợp (Integrated Software Product Demo)**: 30%
- **Làm chủ phần việc được phân công (Mastery of assigned works)**: 20%
- **Kỹ năng mềm & Thái độ làm việc (Soft Skills & Working Attitudes)**: 10%
- **Điểm đánh giá sử dụng AI cá nhân (AI Evaluation Rubric)**: Thang điểm 10.

### 4.3. Điều kiện tiên quyết để đạt môn (Eligibility Criteria)
- Điểm đánh giá Evaluation 1 và Evaluation 2 đều phải đạt **≥ 5.0 / 10**.
- Tuyệt đối không gian lận hoặc sao chép mã nguồn (No cheating / plagiarism).
- Đóng góp thực chất vào các sản phẩm bàn giao chung của nhóm.

---

## 5. Bản đồ cấu trúc thư mục dự án tương ứng với yêu cầu môn học

Để đáp ứng chính xác từng tiêu chí đánh giá trên, toàn bộ dự án AITA đã được quy hoạch:

```text
e:/AITA/
├── docs/
│   ├── architecture/
│   │   ├── system-overview.md     <-- Tài liệu này (Tổng quan bài toán môn học SWD392)
│   │   └── database-design.md     <-- Database Schema cho Eval 2
│   ├── apis/                      <-- Đặc tả API cho từng subsystem
│   ├── diagrams/puml/             <-- Chứa 7 sơ đồ UML (Use Case, Activity, Sequence, Communication, Component, Deployment, Class)
│   └── testcases/                 <-- Kịch bản kiểm thử theo 4 levels (Unit, Integration, System, Acceptance)
│
├── rules/
│   └── branch-naming-rules.md     <-- Quy chuẩn làm việc nhóm Git: docs-*, code-*, test-*
│
├── src/                           <-- Toàn bộ mã nguồn hoàn chỉnh (Desktop App, 3 Design Patterns)
└── tests/                         <-- Code kiểm thử tự động phục vụ nghiệm thu sản phẩm
```
