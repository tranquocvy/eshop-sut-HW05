# HW05 — Báo cáo Performance Testing trên EShop

**Trần Quốc Vỹ · 23120410 · 23_3**

## 1. Phạm vi và mốc mã nguồn

HW05-AI kiểm thử hiệu năng REST API của EShop. Bản làm việc lấy từ commit [`85af3ba875c88283615e22cb108f13e2fccaf0e9`](https://github.com/ttbhanh/eshop-sut/tree/85af3ba875c88283615e22cb108f13e2fccaf0e9) trên nhánh `main` của `ttbhanh/eshop-sut`. Tài liệu SUT gồm [đặc tả API](../api_specification.md) và [hướng dẫn cài đặt](../setup_guide.md).

Mỗi kịch bản Load, Stress và Spike phải chạy cùng một workflow bao phủ auth-heavy, read-heavy và transactional. Workflow cần được đối chiếu với các thành viên trong nhóm trước khi thiết kế test.

## 2. Thiết kế và thực thi

| Hạng mục | Yêu cầu dùng để đối chiếu |
| --- | --- |
| Test plan | Ba plan dùng dữ liệu CSV và có lý giải think-time, ramp-up, số thread hoặc VU. Tên theo `{StudentID}_{ScenarioType}_{YYYYMMDD}`. |
| Báo cáo kết quả | Mỗi kịch bản dùng một report view riêng. Lưu raw log `.jtl` và thư mục HTML report tương ứng. |
| Bằng chứng chạy | Mỗi lượt có ảnh công cụ test cùng mức sử dụng tài nguyên của tiến trình backend. Báo cáo phần cứng gồm ảnh công cụ hệ thống và bảng cấu hình, với hostname khớp các HW trước. |
| Account lockout | Khi Stress hoặc Spike kích hoạt khóa sau ba lần đăng nhập sai, ghi quy trình reset thực tế giữa các lượt. |
| Endurance | Duy trì tải 10–15 phút và báo cáo ngưỡng có số liệu đo. |
| Demo và issue | Demo unlisted từ 6 phút, có công cụ và resource monitor cùng khung hình, với lời thuyết minh tiếng Việt của sinh viên. Issue thực tế có ảnh bằng chứng. |

T00 thiết lập nơi lưu tài liệu và bằng chứng. Việc chọn endpoint, cấu hình môi trường và chạy smoke test thuộc T01. Mọi số liệu kiểm thử sẽ được đối chiếu từ `.jtl` thực tế.

## 3. Phân tích kết quả và phản biện AI

Task 2 dùng raw log để yêu cầu AI phân tích và đề xuất ngưỡng. Mỗi lỗi diễn giải phát hiện được sẽ có giá trị đúng, cách đối chiếu từ log và lý do sai. Tính khả thi của từng đề xuất tối ưu được đánh giá theo mã nguồn và cấu hình SUT.

## 4. Kết luận và Continuous Performance Testing

Đề xuất ở Task 3 cần mô tả trigger từ commit SUT, điều kiện chạy performance test và cách phát hiện regression p95. Flowchart phải thể hiện các nhánh quyết định. Phần thảo luận xem xét chi phí chạy và cảnh báo giả.

## Phụ lục AI

Các lượt trao đổi với OpenAI Codex được ghi trong [Prompt Log](ai/PromptLog.md). [AI Audit Report](ai/AI_Audit_Report.md) dùng để đánh giá các sản phẩm trong bộ nộp. Vỹ tự viết phần nhận xét trong [AI Critique](ai/AI_Critique.md).
