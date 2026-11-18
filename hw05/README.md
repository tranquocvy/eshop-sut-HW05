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

Load, Stress và Spike dùng chung workflow JMeter trên REST API. Login phủ auth-heavy. Danh sách hoặc tìm kiếm và chi tiết sản phẩm phủ read-heavy. Thêm vào giỏ và checkout phủ transactional. [Bảng endpoint và cách dựng backend](Environment.md)

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

| Mục | Trạng thái sau T03 |
| --- | --- |
| Kịch bản thực thi | Smoke T01, pilot Load T02, hai lượt thăm dò và pilot Stress/Spike T03. Pilot Load dùng CSV mặc định có 47 sample đạt. Pilot Stress đạt 752/752 và Spike đạt 502/502. |
| Nhóm endpoint được kiểm thử | Smoke và pilot phủ auth-heavy, read-heavy và transactional qua workflow đăng nhập, tìm kiếm, xem chi tiết, thêm giỏ và checkout. |
| Điểm bão hòa | Chưa xác lập. Mốc 144 VU là trần thử nghiệm trên máy dùng chung. |
| Ngưỡng endurance | Chưa đo. |
| Số bug hoặc performance issue | T01 ghi nhận sai lệch FR-02 khi đối chiếu code với đặc tả. Chưa có kết quả phân loại issue từ các lượt đo tải. |
| Video demo | Chưa có video HW05. |

## Tài liệu và dữ liệu

- [Báo cáo chính](Report.md) và [lịch sử commit](GitCommitLog.txt).
- [Môi trường và workflow](Environment.md) và [bằng chứng smoke T01](evidence/t01-smoke.json).
- [Load plan](plans/23120410_Load_20261118.jmx), [cách chuẩn bị CSV và chạy lại](Load_Plan.md) và [bằng chứng pilot T02](evidence/t02-pilot.json).
- [Stress plan](plans/23120410_Stress_20261118.jmx), [Spike plan](plans/23120410_Spike_20261118.jmx), [thiết kế và cách chạy lại](Stress_Spike_Plans.md) và [bằng chứng thăm dò, pilot T03](evidence/t03-pilots.json).
- [AI Audit Report](ai/AI_Audit_Report.md), [Prompt Log](ai/PromptLog.md) và [AI Critique](ai/AI_Critique.md).
- [Khai báo sử dụng AI](ai/AI_Disclosure.md) và [Bảng kiểm quyền riêng tư](ai/AI_Privacy_Checklist.md).
- `plans/` lưu test plan và `data/` lưu CSV dùng để tham số hóa request.
- `results/` lưu kết quả chạy và `evidence/` lưu bằng chứng tài nguyên, phần cứng và issue.
- `skills/` lưu Agent Skill và tài liệu đi kèm.
