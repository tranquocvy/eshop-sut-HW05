# HW05 — Performance Testing trên EShop

| Mục | Thông tin |
| --- | --- |
| Sinh viên | Trần Quốc Vỹ |
| MSSV | 23120410 |
| Lớp | 23_3 |
| Bài tập | HW05-AI |
| Repository | [tranquocvy/eshop-sut-HW05](https://github.com/tranquocvy/eshop-sut-HW05) |
| Mã nguồn gốc | [ttbhanh/eshop-sut tại `85af3ba`](https://github.com/ttbhanh/eshop-sut/tree/85af3ba875c88283615e22cb108f13e2fccaf0e9) |

## Phạm vi

Load, Stress, Spike và Endurance dùng chung workflow JMeter trên REST API. Login phủ auth-heavy. Danh sách hoặc tìm kiếm và chi tiết sản phẩm phủ read-heavy. Thêm vào giỏ và checkout phủ transactional. [Bảng endpoint và cách dựng backend](Environment.md)

## Bảng tự chấm

| STT | Tiêu chí | Điểm tối đa | Điểm tự chấm |
| --- | --- | ---: | ---: |
| 1 | Task 1 — Load testing | 30 | |
| 2 | Task 1 — Stress testing | 20 | |
| 3 | Task 1 — Spike testing | 20 | |
| 4 | Task 2 — Phân tích bằng AI và misinterpretation hunt, kèm giá trị từ raw log | 10 | |
| 5 | Task 3 — Đề xuất Continuous Performance Testing | 10 | |
| 6 | Agent Skill | 10 | |
| | **Tổng** | **100** | |

## Tóm tắt kiểm thử

| Mục | Trạng thái sau T07B |
| --- | --- |
| Kịch bản thực thi | Load 6 VU, 548 request, 3,70 RPS. Stress 24 → 48 → 96 → 144 VU, 20.203 request, 170,12 RPS. Spike 6 → 144 → 6 VU, 7.755 request, 52,06 RPS. Endurance 32 VU trong pha giữ tải 15 phút. Các lượt đo chính đều có 0 lỗi. [Chi tiết T04](T04_Execution.md) · [Chi tiết T05](T05_Endurance.md) |
| Nhóm endpoint được kiểm thử | Các lượt đo phủ auth-heavy, read-heavy và transactional qua đăng nhập, tìm kiếm, xem chi tiết, thêm giỏ và checkout. |
| Điểm bão hòa | Chưa xác lập. Stress và Spike dùng 144 VU làm trần thử nghiệm trên máy dùng chung. |
| Ngưỡng endurance | Quan sát **21,26 req/s ở 32 VU trong 15 phút**. Working set Node cao nhất **64,21 MiB**, độ dốc 12 phút cuối **+0,02 MiB/phút**. Phép đo thực hiện trên máy dùng chung với JMeter. [Kết quả Endurance](T05_Endurance.md#kết-luận-endurance) |
| Bug và performance issue | T01 ghi nhận sai lệch FR-02. T04 dùng credentials hợp lệ và không kiểm lại FR-02. Các lượt đo chính T04 và T05 không phát sinh lỗi để soạn nháp Issue mới. |
| Phản biện phân tích AI | Số liệu khớp JTL theo quy ước đã công bố. T06 làm rõ bốn điểm khi diễn giải và đánh giá bốn đề xuất tối ưu, gồm 1 hallucinated và 3 feasible. [Đối chiếu T06](AI_Log_Analysis.md) |
| Continuous Performance Testing | Đề xuất lọc path, chạy smoke và đo lặp Load trên PR, dành Stress và Endurance cho lịch đêm. Cờ regression so p95 từng label với dung sai `max(4 ms, 25% baseline)`, hiệu chỉnh từ số liệu local. Thiết kế chưa chạy trên CI. [Đề xuất T07A](Continuous_Perf_Testing.md) |
| Agent Skill | Quy trình chạy profile và phân tích JTL đã được kiểm bằng smoke local qua năm endpoint, có 35 sample và 0 lỗi. [Skill](skills/eshop-perf-testing/SKILL.md) · [Bằng chứng](evidence/t07/skill-run/Run.md) |
| Link video demo | |

## Tài liệu và dữ liệu

- [Báo cáo chính](Report.md) và [lịch sử commit](GitCommitLog.txt).
- [Môi trường và workflow](Environment.md) và [bằng chứng smoke T01](evidence/t01-smoke.json).
- [Load plan](plans/23120410_Load_20261119.jmx), [cách chuẩn bị CSV và chạy lại](Load_Plan.md) và [bằng chứng pilot T02](evidence/t02-pilot.json).
- [Stress plan](plans/23120410_Stress_20261119.jmx), [Spike plan](plans/23120410_Spike_20261119.jmx), [thiết kế và cách chạy lại](Stress_Spike_Plans.md) và [bằng chứng thăm dò, pilot T03](evidence/t03-pilots.json).
- [Thực thi T04](T04_Execution.md) · [Dashboard Load](results/23120410_Load_20261119/index.html) · [Dashboard Stress](results/23120410_Stress_20261119/index.html) · [Dashboard Spike](results/23120410_Spike_20261119/index.html).
- [Endurance plan](plans/23120410_Endurance_20261119.jmx) · [Thực thi T05](T05_Endurance.md) · [Dashboard Endurance](results/23120410_Endurance_20261119/index.html).
- [Phân tích JTL và phản biện T06](AI_Log_Analysis.md) · [Output nguyên văn](ai/T06_External_AI_Raw.txt) · [Script tái tính](evidence/t06/recompute_jtl.py).
- [Continuous Performance Testing](Continuous_Perf_Testing.md) · [Sơ đồ để chèn PDF A4](Continuous_Perf_Testing_Flow.png) · [Script tái tính biên độ p95](evidence/t07/recompute_noise.py).
- [AI Audit Report](ai/AI_Audit_Report.md), [Prompt Log](ai/PromptLog.md) và [AI Critique](ai/AI_Critique.md).
- [Khai báo sử dụng AI](ai/AI_Disclosure.md) và [Bảng kiểm quyền riêng tư](ai/AI_Privacy_Checklist.md).
- `plans/` lưu test plan và `data/` lưu CSV dùng để tham số hóa request.
- `results/` lưu kết quả chạy và `evidence/` lưu bằng chứng tài nguyên, phần cứng và issue.
- [Agent Skill EShop](skills/eshop-perf-testing/SKILL.md) · [Kịch bản quay demo](skills/eshop-perf-testing/DEMO.md) · [Lệnh và kết quả smoke](evidence/t07/skill-run/Run.md).
