# HW05 — Báo cáo Performance Testing trên EShop

**Trần Quốc Vỹ · 23120410 · 23_3**

## 1. Phạm vi và mốc mã nguồn

HW05-AI kiểm thử hiệu năng REST API của EShop. Bản làm việc lấy từ commit [`85af3ba875c88283615e22cb108f13e2fccaf0e9`](https://github.com/ttbhanh/eshop-sut/tree/85af3ba875c88283615e22cb108f13e2fccaf0e9) trên nhánh `main` của `ttbhanh/eshop-sut`. Tài liệu SUT gồm [đặc tả API](../api_specification.md) và [hướng dẫn cài đặt](../setup_guide.md).

Load, Stress và Spike dùng cùng workflow trên JMeter. Luồng gồm login, danh sách hoặc tìm kiếm, chi tiết sản phẩm, thêm giỏ và checkout. [Bảng endpoint, cấu hình máy và kết quả smoke](Environment.md)

## 2. Thiết kế và thực thi

| Hạng mục | Yêu cầu dùng để đối chiếu |
| --- | --- |
| Test plan | Ba plan dùng dữ liệu CSV và có lý giải think-time, ramp-up, số thread hoặc VU. Tên theo `{StudentID}_{ScenarioType}_{YYYYMMDD}`. |
| Báo cáo kết quả | Mỗi kịch bản dùng một report view riêng. Lưu raw log `.jtl` và thư mục HTML report tương ứng. |
| Bằng chứng chạy | Mỗi lượt có ảnh công cụ test cùng mức sử dụng tài nguyên của tiến trình backend. Báo cáo phần cứng gồm ảnh công cụ hệ thống và bảng cấu hình, với hostname khớp các HW trước. |
| Account lockout | Ghi nhận nếu Stress hoặc Spike kích hoạt khóa. Đối chiếu với FR-02 và dùng quy trình reset đã kiểm chứng tại T01. |
| Endurance | Duy trì tải 10–15 phút và báo cáo ngưỡng có số liệu đo. |
| Demo và issue | Demo unlisted từ 6 phút, có công cụ và resource monitor cùng khung hình, với lời thuyết minh tiếng Việt của sinh viên. Issue thực tế có ảnh bằng chứng. |

T01 kiểm chứng năm endpoint trên bản sao backend `85af3ba` tại `http://127.0.0.1:3000`. Cả năm request chính và lượt tìm kiếm `Galaxy` đều trả HTTP 200. Đối chiếu code FR-02 với đặc tả cho thấy sai lệch về số lần đăng nhập sai và thời hạn khóa. Smoke kiểm tra trạng thái khóa đặt sẵn, đăng nhập sau khi hết hạn và hai cách reset. T04 dự kiến dùng cùng bản sao backend theo lệnh dựng và khởi động đã ghi. [Môi trường và workflow](Environment.md) · [Bằng chứng smoke T01](evidence/t01-smoke.json)

T02 tạo Load plan trên JMeter 5.6.3 và Temurin 17, với mức khởi đầu 6 VU, ramp-up 30 giây, tổng 150 giây và think-time 1–2 giây. Plan đọc ba CSV bằng CSV Data Set Config và cấp một tài khoản mới cho mỗi vòng. Credentials mặc định lấy từ repo sau khi đăng ký tài khoản thử. Sau lỗi sample, VU chạy vòng mới. Khi hết dòng credentials, VU dừng theo cấu hình EOF.

Pilot 05 dùng 3 VU với 1.250 tài khoản đã đăng ký. Có 44 sample đạt, 9 ID đăng nhập riêng biệt và 8 đơn khớp SQLite. Pilot 08 xác minh đường dẫn CSV mặc định từ thư mục làm việc ngoài repo, với 47 sample đạt và 8 đơn khớp SQLite. Pilot 09 xác nhận VU dùng tài khoản kế tiếp sau lỗi assertion và dừng khi hết dòng. Các lượt này xác minh plan và fixture trước khi đo chính. [Thiết kế Load và cách tính số tài khoản](Load_Plan.md) · [Bằng chứng pilot](evidence/t02-pilot.json)

T03 dùng think-time 300–600 ms để tăng mật độ request trong giới hạn RAM của máy chạy chung JMeter và backend. Stress tăng 24 → 48 → 96 → 144 VU với Aggregate Report. Spike đi từ 6 lên 144 rồi về 6 VU với Response Time Graph. Pilot của bản sửa ghi 752/752 sample đạt cho Stress và 502/502 cho Spike. Các lượt nhỏ xác nhận đúng lịch tải và checkout khớp SQLite. [Thiết kế Stress và Spike](Stress_Spike_Plans.md) · [Bằng chứng T03](evidence/t03-pilots.json)

Ở lượt thăm dò 300–600 ms, từ 96 lên 144 VU, p95 checkout tăng từ 21 lên 100 ms và throughput tăng từ 210 lên 304,45 request/giây. Lượt thăm dò chưa xác lập điểm bão hòa. Mốc 144 VU là trần thử nghiệm chọn theo RAM khả dụng của máy dùng chung. Số đo ngắn chưa đủ để kết luận backend chịu được mức tải đó. [JTL thăm dò](evidence/t03-calibration-fast.jtl) · [CPU và RAM](evidence/t03-calibration-fast.csv)

## 3. Phân tích kết quả và phản biện AI

Task 2 dùng raw log để yêu cầu AI phân tích và đề xuất ngưỡng. Mỗi lỗi diễn giải phát hiện được sẽ có giá trị đúng, cách đối chiếu từ log và lý do sai. Tính khả thi của từng đề xuất tối ưu được đánh giá theo mã nguồn và cấu hình SUT.

## 4. Kết luận và Continuous Performance Testing

Đề xuất ở Task 3 cần mô tả trigger từ commit SUT, điều kiện chạy performance test và cách phát hiện regression p95. Flowchart phải thể hiện các nhánh quyết định. Phần thảo luận xem xét chi phí chạy và cảnh báo giả.

## Phụ lục AI

Các lượt trao đổi với OpenAI Codex được ghi trong [Prompt Log](ai/PromptLog.md). [AI Audit Report](ai/AI_Audit_Report.md) dùng để đánh giá các sản phẩm trong bộ nộp. Vỹ tự viết phần nhận xét trong [AI Critique](ai/AI_Critique.md).
