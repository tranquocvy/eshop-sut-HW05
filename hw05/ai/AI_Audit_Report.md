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
| T02 · OpenAI Codex · [P-006](PromptLog.md#p-006) | [Load plan JMX](../plans/23120410_Load_20261118.jmx) · [Bằng chứng pilot](../evidence/t02-pilot.json) | INCOMPLETE | Plan đầu dùng `stopthread`, đọc CSV bằng Groovy và giữ một tài khoản cố định cho mỗi VU. Lệnh pilot đầu dựa vào `-v` để chọn Java 25 và lỗi ở lúc Groovy biên dịch. Bản trước duyệt vẫn trỏ mặc định ra runtime ngoài repo. [Review P-008](PromptLog.md#p-008) · [Bổ sung P-009](PromptLog.md#p-009) · [Duyệt P-010](PromptLog.md#p-010) | Vỹ yêu cầu giữ VU sau sample lỗi, dùng CSV Data Set Config, cấp tài khoản mới mỗi vòng và chọn CSV trong repo làm mặc định. Codex áp dụng Start Next Thread Loop, ba CSV Data Set Config, EOF không quay vòng, đường dẫn tương đối trong repo và xác minh lại trên Temurin 17. [Review P-008](PromptLog.md#p-008) · [Bổ sung P-009](PromptLog.md#p-009) · [Duyệt P-010](PromptLog.md#p-010) |
| T02 · OpenAI Codex · [P-006](PromptLog.md#p-006) | Bộ CSV và script provision. [Credentials tổng hợp](../data/load-credentials.csv) · [Sản phẩm](../data/load-products.csv) · [Payload](../data/load-order-payloads.csv) · [Script](../data/provision_load_users.py) | INCOMPLETE | Bản đầu phát sinh credentials ngoài repo từ roster 6 VU. Dữ liệu chỉ đủ theo phương án một tài khoản cố định mỗi VU. [Review P-008](PromptLog.md#p-008) · [Bổ sung P-009](PromptLog.md#p-009) | Vỹ yêu cầu đưa credentials giả vào repo và chuẩn bị đủ dòng dùng một lần cho soak. Codex tạo 1.250 dòng, cập nhật script đăng ký, đồng bộ cột email và mật khẩu giữa CSV nguồn với file xuất tùy chọn, rồi kiểm tra số lượng đã đăng ký bằng SQLite. [Bổ sung P-009](PromptLog.md#p-009) · [Duyệt P-010](PromptLog.md#p-010) |
| T02 · OpenAI Codex · [P-006](PromptLog.md#p-006) | [Tài liệu Load](../Load_Plan.md), kèm cập nhật [môi trường](../Environment.md) | INCOMPLETE | Hướng dẫn đầu thiếu các bước tải và đặt JMeter/JRE. Bảng môi trường vẫn ghi Java 25 sau khi pilot cần Temurin 17. Cách tính một tài khoản cho mỗi VU cần sửa theo yêu cầu dùng tài khoản một lần. [Review P-008](PromptLog.md#p-008) · [Bổ sung P-009](PromptLog.md#p-009) | Vỹ yêu cầu cập nhật runtime, đường dẫn cài công cụ và cách tính số tài khoản từ pilot. Codex ghi Temurin 17, bổ sung lệnh và đường dẫn tái tạo, trình bày giả định, quy ước EOF và dẫn trực tiếp JTL dùng để tính. [Review P-008](PromptLog.md#p-008) · [Bổ sung P-009](PromptLog.md#p-009) · [Duyệt P-010](PromptLog.md#p-010) |

## 4. Tổng kết đánh giá

| Verdict | Số artifact | Tỷ lệ |
| --- | ---: | ---: |
| VALID | 0 | 0% |
| INCOMPLETE | 4 | 100% |
| INVALID | 0 | 0% |
| **Tổng** | **4** | **100%** |

## 5. Xác nhận

Phần cam đoan nằm trong [Biểu mẫu Khai báo Sử dụng AI](AI_Disclosure.md).

| Xác nhận | Thông tin |
| --- | --- |
| Họ tên sinh viên | Trần Quốc Vỹ |
| MSSV | 23120410 |
| Ngày xác nhận | |
| Chữ ký | Trần Quốc Vỹ |
