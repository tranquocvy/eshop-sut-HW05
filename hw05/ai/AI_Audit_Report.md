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

- Đọc đề, đối chiếu yêu cầu và chuẩn bị cấu trúc bộ nộp HW05 (T00).
- Đối chiếu đặc tả, xác định workflow, kiểm thử smoke và ghi cấu hình môi trường (T01).
- Thiết kế và hiệu chỉnh các plan JMeter cho Load, Stress và Spike (T02–T03).
- Tạo CSV dữ liệu tổng hợp và script đăng ký tài khoản thử (T02–T03).
- Chạy pilot, thăm dò và ba kịch bản đo chính bằng JMeter CLI (T02–T04).
- Tạo dashboard, thu CPU/RAM, tính lại số liệu JTL và đối chiếu đơn trong SQLite (T04).
- Soạn và sửa tài liệu kiểm thử, báo cáo và hồ sơ AI theo review (T00–T04).

Công cụ, ngày giờ, prompt và phản hồi được ghi trong [Prompt Log](PromptLog.md).

## 3. Bảng Audit theo artifact

Mỗi dòng dành cho một sản phẩm thực tế trong bộ nộp, chẳng hạn test plan, CSV, log hoặc báo cáo.

| (1) Prompt và công cụ | (2) Output AI | (3) Verdict | (4) Lý do | (5) Bản sinh viên sửa |
| --- | --- | --- | --- | --- |
| T01 · OpenAI Codex · [P-003](PromptLog.md#p-003) | Bản đầu tài liệu môi trường và workflow. [Bản đã sửa](../Environment.md) · [Bằng chứng smoke](../evidence/t01-smoke.json) | INCOMPLETE | Bản đầu thiếu ghi riêng hai hostname, thiếu mô tả bản backend dùng cho T04 và còn câu hướng dẫn nháp trong tài liệu. [Review của Vỹ](PromptLog.md#p-004) | Vỹ nêu các thiếu sót và yêu cầu ghi hai hostname theo ngữ cảnh, chỉ rõ backend T04 và bỏ các câu nháp. Codex đã sửa theo review. Ở lượt duyệt, Vỹ yêu cầu dùng cách ghi trung tính và bổ sung lệnh dựng lại từ `85af3ba`. Codex đã cập nhật cả hai điểm. [Review](PromptLog.md#p-004) · [Duyệt và chỉnh sửa cuối](PromptLog.md#p-005) |
| T02 · OpenAI Codex · [P-006](PromptLog.md#p-006) | [Load plan JMX](../plans/23120410_Load_20261119.jmx) · [Bằng chứng pilot](../evidence/t02-pilot.json) | INCOMPLETE | Plan đầu dùng `stopthread`, đọc CSV bằng Groovy và giữ một tài khoản cố định cho mỗi VU. Lệnh pilot đầu dựa vào `-v` để chọn Java 25 và lỗi ở lúc Groovy biên dịch. Bản trước duyệt vẫn trỏ mặc định ra runtime ngoài repo. [Review P-008](PromptLog.md#p-008) · [Bổ sung P-009](PromptLog.md#p-009) · [Duyệt P-010](PromptLog.md#p-010) | Vỹ yêu cầu giữ VU sau sample lỗi, dùng CSV Data Set Config, cấp tài khoản mới mỗi vòng và chọn CSV trong repo làm mặc định. Codex áp dụng Start Next Thread Loop, ba CSV Data Set Config, EOF không quay vòng, đường dẫn tương đối trong repo và xác minh lại trên Temurin 17. [Review P-008](PromptLog.md#p-008) · [Bổ sung P-009](PromptLog.md#p-009) · [Duyệt P-010](PromptLog.md#p-010) |
| T02 · OpenAI Codex · [P-006](PromptLog.md#p-006) | Bộ CSV và script provision. [Credentials tổng hợp](../data/load-credentials.csv) · [Sản phẩm](../data/load-products.csv) · [Payload](../data/load-order-payloads.csv) · [Script](../data/provision_load_users.py) | INCOMPLETE | Bản đầu phát sinh credentials ngoài repo từ roster 6 VU. Dữ liệu chỉ đủ theo phương án một tài khoản cố định mỗi VU. [Review P-008](PromptLog.md#p-008) · [Bổ sung P-009](PromptLog.md#p-009) | Vỹ yêu cầu đưa credentials giả vào repo và chuẩn bị đủ dòng dùng một lần cho soak. Codex tạo 1.250 dòng, cập nhật script đăng ký, đồng bộ cột email và mật khẩu giữa CSV nguồn với file xuất tùy chọn, rồi kiểm tra số lượng đã đăng ký bằng SQLite. [Bổ sung P-009](PromptLog.md#p-009) · [Duyệt P-010](PromptLog.md#p-010) |
| T02 · OpenAI Codex · [P-006](PromptLog.md#p-006) | [Tài liệu Load](../Load_Plan.md), kèm cập nhật [môi trường](../Environment.md) | INCOMPLETE | Hướng dẫn đầu thiếu các bước tải và đặt JMeter/JRE. Bảng môi trường vẫn ghi Java 25 sau khi pilot cần Temurin 17. Cách tính một tài khoản cho mỗi VU cần sửa theo yêu cầu dùng tài khoản một lần. [Review P-008](PromptLog.md#p-008) · [Bổ sung P-009](PromptLog.md#p-009) | Vỹ yêu cầu cập nhật runtime, đường dẫn cài công cụ và cách tính số tài khoản từ pilot. Codex ghi Temurin 17, bổ sung lệnh và đường dẫn tái tạo, trình bày giả định, quy ước EOF và dẫn trực tiếp JTL dùng để tính. [Review P-008](PromptLog.md#p-008) · [Bổ sung P-009](PromptLog.md#p-009) · [Duyệt P-010](PromptLog.md#p-010) |
| T03 · OpenAI Codex · [P-011](PromptLog.md#p-011) | [Stress plan JMX](../plans/23120410_Stress_20261119.jmx) | INCOMPLETE | Bản trình review tắt Aggregate Report. Trần 24 VU với think-time 1–2 giây lấy từ thiết kế ban đầu, chưa có số đo ở tải cao để chọn bậc và trần. [Review P-012](PromptLog.md#p-012) | Vỹ yêu cầu bật listener và đo thăm dò trước khi chốt. Codex bật Aggregate Report, chọn 24 → 48 → 96 → 144 VU với think-time 300–600 ms theo số đo, rồi chạy lại pilot. [Review P-012](PromptLog.md#p-012) · [Duyệt P-013](PromptLog.md#p-013) |
| T03 · OpenAI Codex · [P-011](PromptLog.md#p-011) | [Spike plan JMX](../plans/23120410_Spike_20261119.jmx) | INCOMPLETE | Bản trình review tắt Response Time Graph. Đỉnh 18 VU gấp sáu lần nền 3 VU và chưa dựa trên thăm dò tải cao. [Review P-012](PromptLog.md#p-012) | Vỹ yêu cầu bật listener và chọn lại đỉnh dựa trên số đo. Codex bật Response Time Graph với khoảng gộp 5 giây, chọn 6 → 144 → 6 VU, giữ đỉnh 20 giây và chạy lại pilot. [Review P-012](PromptLog.md#p-012) · [Duyệt P-013](PromptLog.md#p-013) |
| T03 · OpenAI Codex · [P-011](PromptLog.md#p-011) | [CSV credentials dùng chung](../data/load-credentials.csv) | INCOMPLETE | Bản trình review chỉ tính dung lượng CSV theo lịch ban đầu. Bộ 1.250 dòng thiếu so với dự trù sau khi hiệu chỉnh tải theo yêu cầu review. [Review P-012](PromptLog.md#p-012) | Vỹ yêu cầu tính và đăng ký thêm nếu thiếu. Codex tính 6.984 dòng cho Stress và 2.868 cho Spike, giữ nguyên 1.250 dòng T02, bổ sung lên 7.500 dòng và đăng ký, kiểm tra đủ số dòng trong SQLite. [Review P-012](PromptLog.md#p-012) · [Duyệt P-013](PromptLog.md#p-013) |
| T03 · OpenAI Codex · [P-011](PromptLog.md#p-011) | [Tài liệu thiết kế và chạy lại](../Stress_Spike_Plans.md) | INCOMPLETE | Bản trình review thiếu số liệu thực nghiệm để lý giải mức tải và cách chạy gọn với listener bật. Ở lượt duyệt, Vỹ yêu cầu giải thích chênh lệch think-time và ghi rõ ý nghĩa trần 144 VU. [Review P-012](PromptLog.md#p-012) · [Duyệt P-013](PromptLog.md#p-013) | Theo góp ý của Vỹ, Codex bổ sung số liệu hai lượt thăm dò, căn cứ chọn lịch, cấu hình CSV JTL bỏ body/header, lý do rút think-time và giới hạn của phép đo trên máy dùng chung. [Review P-012](PromptLog.md#p-012) · [Duyệt P-013](PromptLog.md#p-013) |
| T03 · OpenAI Codex · [P-011](PromptLog.md#p-011) | Bộ bằng chứng T03 gồm [tổng hợp](../evidence/t03-pilots.json), [JTL thăm dò](../evidence/t03-calibration-fast.jtl) và [CPU/RAM](../evidence/t03-calibration-fast.csv) | INCOMPLETE | Bản trình review có pilot nhỏ kiểm workflow và lịch tải. Hồ sơ thiếu lượt thăm dò với số đo p95, lỗi và tài nguyên để lý giải tải đã chọn. [Review P-012](PromptLog.md#p-012) | Vỹ yêu cầu chạy thăm dò và cập nhật pilot. Codex ghi JTL và CPU/RAM cho hai mức think-time, chạy lại pilot với listener bật, đối chiếu đơn trong SQLite và kiểm chứng Shutdown. [Review P-012](PromptLog.md#p-012) · [Duyệt P-013](PromptLog.md#p-013) |
| T04 · OpenAI Codex · [P-019](PromptLog.md#p-019) | Load: [JTL](../results/23120410_Load_20261119.jtl) · [HTML dashboard](../results/23120410_Load_20261119/index.html) · [CSV CPU/RAM](../results/23120410_Load_20261119_resources.csv) · [Đối chiếu SQLite](../evidence/t04/load-verification.json) | VALID | Vỹ duyệt số liệu. JTL của lượt nộp có 548 request, khớp dashboard và 107 đơn trong SQLite. CSV tài nguyên thuộc cùng lượt. [P-036](PromptLog.md#p-036) · [P-041](PromptLog.md#p-041) | Theo yêu cầu bổ sung ảnh, Codex lưu riêng lượt đầu có 550 request rồi ghi bộ dữ liệu mới sau khi reset backend. [P-022](PromptLog.md#p-022) · [P-023](PromptLog.md#p-023) |
| T04 · OpenAI Codex · [P-027](PromptLog.md#p-027) | Stress: [JTL](../results/23120410_Stress_20261119.jtl) · [HTML dashboard](../results/23120410_Stress_20261119/index.html) · [CSV CPU/RAM](../results/23120410_Stress_20261119_resources.csv) · [Đối chiếu SQLite](../evidence/t04/stress-verification.json) | VALID | Vỹ duyệt lượt đạt 144 VU với 20.203 request, 170,12 RPS và 3.986 đơn khớp SQLite. Dashboard và CSV tài nguyên khớp lượt đo này. [P-040](PromptLog.md#p-040) · [P-041](PromptLog.md#p-041) | Codex lưu riêng hai lượt trước và đo lại theo yêu cầu lấy ảnh. Bộ nộp dùng dữ liệu của lượt có ảnh 96 và 144 VU. [P-029](PromptLog.md#p-029) · [P-036](PromptLog.md#p-036) · [P-038](PromptLog.md#p-038) · [P-039](PromptLog.md#p-039) |
| T04 · OpenAI Codex · [P-033](PromptLog.md#p-033) | Spike: [JTL](../results/23120410_Spike_20261119.jtl) · [HTML dashboard](../results/23120410_Spike_20261119/index.html) · [CSV CPU/RAM](../results/23120410_Spike_20261119_resources.csv) · [Đối chiếu SQLite và hồi phục](../evidence/t04/spike-verification.json) | VALID | Vỹ duyệt số liệu Spike. JTL có 7.755 request, 0 lỗi, khớp dashboard và 1.490 đơn. CSV ghi tài nguyên của cùng lượt. [P-036](PromptLog.md#p-036) | Giữ bộ dữ liệu của lượt đã đo. Vỹ yêu cầu làm rõ cách đọc CPU trong tài liệu. [P-036](PromptLog.md#p-036) · [P-041](PromptLog.md#p-041) |
| T04 · OpenAI Codex · [P-014](PromptLog.md#p-014) | [Ảnh cấu hình dxdiag](../evidence/t04/hardware_dxdiag_20261118_152538Z.jpg) | VALID | Ảnh cấu hình được chụp bằng computer use từ máy đo. Vỹ yêu cầu giữ ảnh này làm bằng chứng phần cứng. [P-016](PromptLog.md#p-016) · [P-018](PromptLog.md#p-018) | Giữ ảnh gốc và ghi hostname thật `GOYOONJUNG` trong tài liệu T04 theo xác nhận của Vỹ. [P-016](PromptLog.md#p-016) · [P-018](PromptLog.md#p-018) |
| T04 · OpenAI Codex · [P-014](PromptLog.md#p-014) · [P-035](PromptLog.md#p-035) | [Tài liệu thực thi T04](../T04_Execution.md), kèm đối chiếu ảnh do Vỹ chụp | INCOMPLETE | Bộ bằng chứng trước review thiếu ảnh Load đủ hai mốc và ảnh backend ở đỉnh Stress. Bản trước chốt còn thiếu lượt Stress dùng để nộp trong bảng lịch sử và số CSV tại mốc 144 VU. [P-020](PromptLog.md#p-020) · [P-031](PromptLog.md#p-031) · [P-040](PromptLog.md#p-040) | Vỹ yêu cầu đo lại Load một lần và Stress hai lần để chụp ảnh. Vỹ xác nhận ảnh Load và Stress mới, đồng thời giữ ảnh Spike. Codex ghi lịch sử ba lượt Stress, đối chiếu dashboard và dẫn số CPU/RAM tại mốc ảnh. [P-022](PromptLog.md#p-022) · [P-024](PromptLog.md#p-024) · [P-029](PromptLog.md#p-029) · [P-034](PromptLog.md#p-034) · [P-036](PromptLog.md#p-036) · [P-039](PromptLog.md#p-039) · [P-040](PromptLog.md#p-040) · [P-041](PromptLog.md#p-041) |

## 4. Tổng kết đánh giá

| Verdict | Số artifact | Tỷ lệ |
| --- | ---: | ---: |
| VALID | 4 | 28,57% |
| INCOMPLETE | 10 | 71,43% |
| INVALID | 0 | 0% |
| **Tổng** | **14** | **100%** |

## 5. Xác nhận

Phần cam đoan nằm trong [Biểu mẫu Khai báo Sử dụng AI](AI_Disclosure.md).

| Xác nhận | Thông tin |
| --- | --- |
| Họ tên sinh viên | Trần Quốc Vỹ |
| MSSV | 23120410 |
| Ngày xác nhận | |
| Chữ ký | Trần Quốc Vỹ |
