# HW05 — AI Audit Report

## 1. Thông tin sinh viên

| Mục | Thông tin |
| --- | --- |
| Họ tên | Trần Quốc Vỹ |
| MSSV | 23120410 |
| Lớp | 23_3 |
| Mã bài tập | HW05-AI |
| Bài tập | Performance Testing |
| Chính sách AI | Open, yêu cầu khai báo và đính kèm AI Audit Report |

## 2. Khai báo và nhật ký sử dụng

I use AI tools for the following tasks,

Công cụ, ngày giờ, prompt và phản hồi được ghi trong [Prompt Log](PromptLog.md).

## 3. Bảng Audit theo artifact

Mỗi dòng dành cho một sản phẩm thực tế trong bộ nộp, chẳng hạn test plan, CSV, log hoặc báo cáo.

| (1) Prompt và công cụ | (2) Output AI | (3) Verdict | (4) Lý do | (5) Bản sinh viên sửa |
| --- | --- | --- | --- | --- |
| T01 · OpenAI Codex · [P-003](PromptLog.md#p-003) | Bản đầu tài liệu môi trường và workflow. [Bản đã sửa](../Environment.md) · [Bằng chứng smoke](../evidence/t01-smoke.json) | INCOMPLETE | Bản đầu thiếu ghi riêng hai hostname, thiếu mô tả bản backend dùng cho T04 và còn câu hướng dẫn nháp trong tài liệu. [Review của Vỹ](PromptLog.md#p-004) | Vỹ nêu các thiếu sót và yêu cầu ghi hai hostname theo ngữ cảnh, chỉ rõ backend T04 và bỏ các câu nháp. Codex đã sửa theo review. Ở lượt duyệt, Vỹ yêu cầu dùng cách ghi trung tính và bổ sung lệnh dựng lại từ `85af3ba`. Codex đã cập nhật cả hai điểm. [Review](PromptLog.md#p-004) · [Duyệt và chỉnh sửa cuối](PromptLog.md#p-005) |

## 4. Tổng kết đánh giá

| Verdict | Số artifact | Tỷ lệ |
| --- | ---: | ---: |
| VALID | 0 | 0% |
| INCOMPLETE | 1 | 100% |
| INVALID | 0 | 0% |
| **Tổng** | **1** | **100%** |

## 5. Xác nhận

Phần cam đoan nằm trong [Biểu mẫu Khai báo Sử dụng AI](AI_Disclosure.md).

| Xác nhận | Thông tin |
| --- | --- |
| Họ tên sinh viên | Trần Quốc Vỹ |
| MSSV | 23120410 |
| Ngày xác nhận | |
| Chữ ký | Trần Quốc Vỹ |
