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

Load, Stress và Spike dùng cùng một workflow end-to-end trên REST API, bao phủ auth-heavy, read-heavy và transactional. Workflow cụ thể được xác định ở bước chốt phạm vi sau khi đối chiếu với nhóm.

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

| Mục | Trạng thái tại T00 |
| --- | --- |
| Kịch bản thực thi | Load, Stress, Spike và soak đều chưa chạy. |
| Nhóm endpoint được kiểm thử | Chưa đo độ bao phủ. Phạm vi đề bài gồm auth-heavy, read-heavy và transactional. |
| Ngưỡng endurance | Chưa đo. |
| Số bug hoặc performance issue | Chưa có số liệu từ thực thi HW05. |
| Video demo | Chưa có video HW05. |

## Tài liệu và dữ liệu

- [Báo cáo chính](Report.md) và [lịch sử commit](GitCommitLog.txt).
- [AI Audit Report](ai/AI_Audit_Report.md), [Prompt Log](ai/PromptLog.md) và [AI Critique](ai/AI_Critique.md).
- [Khai báo sử dụng AI](ai/AI_Disclosure.md) và [Bảng kiểm quyền riêng tư](ai/AI_Privacy_Checklist.md).
- `plans/` lưu test plan và `data/` lưu CSV dùng để tham số hóa request.
- `results/` lưu kết quả chạy và `evidence/` lưu bằng chứng tài nguyên, phần cứng và issue.
- `skills/` lưu Agent Skill và tài liệu đi kèm.
