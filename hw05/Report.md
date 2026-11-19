# HW05 — Báo cáo Performance Testing trên EShop

**Trần Quốc Vỹ · 23120410 · 23_3**

## 1. Phạm vi và mốc mã nguồn

HW05-AI kiểm thử hiệu năng REST API của EShop. Bản làm việc lấy từ commit [`85af3ba875c88283615e22cb108f13e2fccaf0e9`](https://github.com/ttbhanh/eshop-sut/tree/85af3ba875c88283615e22cb108f13e2fccaf0e9) trên nhánh `main` của `ttbhanh/eshop-sut`. Tài liệu SUT gồm [đặc tả API](../api_specification.md) và [hướng dẫn cài đặt](../setup_guide.md).

Load, Stress, Spike và Endurance dùng cùng workflow trên JMeter. Luồng gồm login, danh sách hoặc tìm kiếm, chi tiết sản phẩm, thêm giỏ và checkout. [Bảng endpoint, cấu hình máy và kết quả smoke](Environment.md)

## 2. Thiết kế và thực thi

| Hạng mục | Yêu cầu dùng để đối chiếu |
| --- | --- |
| Test plan | Ba plan dùng dữ liệu CSV và có lý giải think-time, ramp-up, số thread hoặc VU. Tên theo `{StudentID}_{ScenarioType}_{YYYYMMDD}`. |
| Báo cáo kết quả | Mỗi kịch bản dùng một report view riêng. Lưu raw log `.jtl` và thư mục HTML report tương ứng. |
| Bằng chứng chạy | Mỗi lượt có ảnh công cụ test cùng mức sử dụng tài nguyên của tiến trình backend. Báo cáo phần cứng gồm ảnh công cụ hệ thống và bảng cấu hình, với hostname khớp các HW trước. |
| Account lockout | Ghi nhận nếu Stress hoặc Spike kích hoạt khóa. Đối chiếu với FR-02 và dùng quy trình reset đã kiểm chứng tại T01. |
| Endurance | Duy trì tải 10–15 phút và báo cáo ngưỡng có số liệu đo. |
| Demo và issue | Demo unlisted từ 6 phút, có công cụ và resource monitor cùng khung hình, với lời thuyết minh tiếng Việt của sinh viên. Issue thực tế có ảnh bằng chứng. |

T01 kiểm chứng năm endpoint trên bản sao backend `85af3ba` tại `http://127.0.0.1:3000`. Cả năm request chính và lượt tìm kiếm `Galaxy` đều trả HTTP 200. Đối chiếu code FR-02 với đặc tả cho thấy sai lệch về số lần đăng nhập sai và thời hạn khóa. Smoke kiểm tra trạng thái khóa đặt sẵn, đăng nhập sau khi hết hạn và hai cách reset. [Môi trường và workflow](Environment.md) · [Bằng chứng smoke T01](evidence/t01-smoke.json)

T02 tạo Load plan trên JMeter 5.6.3 và Temurin 17, với mức khởi đầu 6 VU, ramp-up 30 giây, tổng 150 giây và think-time 1–2 giây. Plan đọc ba CSV bằng CSV Data Set Config và cấp một tài khoản mới cho mỗi vòng. Credentials mặc định lấy từ repo sau khi đăng ký tài khoản thử. Sau lỗi sample, VU chạy vòng mới. Khi hết dòng credentials, VU dừng theo cấu hình EOF.

Pilot 05 dùng 3 VU với 1.250 tài khoản đã đăng ký. Có 44 sample đạt, 9 ID đăng nhập riêng biệt và 8 đơn khớp SQLite. Pilot 08 xác minh đường dẫn CSV mặc định từ thư mục làm việc ngoài repo, với 47 sample đạt và 8 đơn khớp SQLite. Pilot 09 xác nhận VU dùng tài khoản kế tiếp sau lỗi assertion và dừng khi hết dòng. Các lượt này xác minh plan và fixture trước khi đo chính. [Thiết kế Load và cách tính số tài khoản](Load_Plan.md) · [Bằng chứng pilot](evidence/t02-pilot.json)

T03 dùng think-time 300–600 ms để tăng mật độ request trong giới hạn RAM của máy chạy chung JMeter và backend. Stress tăng 24 → 48 → 96 → 144 VU với Aggregate Report. Spike đi từ 6 lên 144 rồi về 6 VU với Response Time Graph. Pilot của bản sửa ghi 752/752 sample đạt cho Stress và 502/502 cho Spike. Các lượt nhỏ xác nhận đúng lịch tải và checkout khớp SQLite. [Thiết kế Stress và Spike](Stress_Spike_Plans.md) · [Bằng chứng T03](evidence/t03-pilots.json)

Ở lượt thăm dò 300–600 ms, từ 96 lên 144 VU, p95 checkout tăng từ 21 lên 100 ms và throughput tăng từ 210 lên 304,45 request/giây. Lượt thăm dò chưa xác lập điểm bão hòa. Mốc 144 VU là trần thử nghiệm chọn theo RAM khả dụng của máy dùng chung. Số đo ngắn chưa đủ để kết luận backend chịu được mức tải đó. [JTL thăm dò](evidence/t03-calibration-fast.jtl) · [CPU và RAM](evidence/t03-calibration-fast.csv)

### Kết quả thực thi T04

Ngày 19/11/2026, ba plan được chạy lần lượt trên `GOYOONJUNG` bằng JMeter 5.6.3 CLI non-GUI và Temurin 17, heap tối đa 384 MiB. Mỗi lượt dùng một bản backend mới từ `85af3ba` và SQLite sạch. Các tài khoản được đăng ký lại từ CSV và đối chiếu trong SQLite trước khi đo. [Quy trình reset và bằng chứng](T04_Execution.md)

| Kịch bản | VU thực tế | Request | RPS toàn lượt | p95 (ms) | Lỗi | Checkout khớp đơn |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Load | 6 | 548 | 3,70 | 9 | 0% | 107 |
| Stress | 24 → 48 → 96 → 144 | 20.203 | 170,12 | 10 | 0% | 3.986 |
| Spike | 6 → 144 → 6 | 7.755 | 52,06 | 17 | 0% | 1.490 |

Load chỉ dùng 6 VU với think-time 1–2 giây. Stress và Spike dùng think-time 300–600 ms và trần 144 VU trên máy dùng chung. Stress đạt 316,86 RPS trong các cửa sổ ổn định ở 144 VU, chưa xác lập điểm bão hòa. Spike đạt 314,36 RPS ở đỉnh. Cửa sổ đầu tiên đạt tiêu chí hồi phục kết thúc 35 giây sau khi nhóm Burst dừng. [Số liệu theo bậc, pha và label](T04_Execution.md)

Dashboard mỗi lượt được sinh từ JTL tương ứng. Số mẫu, RPS, p95 và tỷ lệ lỗi được tính lại và đối chiếu theo label. SQLite khớp từng checkout của ba lượt trong bộ nộp. Load chạy lại một lần và Stress chạy lại hai lần để bổ sung ảnh. Lịch sử và ảnh trong báo cáo ghi đúng lượt. CSV CPU/RAM là nguồn số đo tài nguyên dùng cho phân tích. [JTL, dashboard và ảnh giám sát](T04_Execution.md)

Cả ba lượt kết thúc đúng lịch với 0 lỗi, nên không có nháp Issue mới từ T04. T04 dùng credentials hợp lệ và không kiểm lại hành vi khóa tài khoản FR-02 khi nhập sai. [Kết quả đối chiếu và giới hạn](T04_Execution.md)

### Kết quả Endurance T05

Ngày 19/11/2026, Endurance chạy trên máy `GOYOONJUNG` với **32 VU**, ramp-up 20 giây, think-time 1–2 giây và pha giữ tải 15 phút. Hai pilot đầu dừng theo ngưỡng RAM khả dụng. Sau khi Vỹ giải phóng RAM, pilot thứ ba hoàn tất 110 giây. Lượt chính dùng backend mới với SQLite sạch và 7.500 tài khoản thử đăng ký lại. [Quy trình và lịch sử pilot](T05_Endurance.md)

Mức RPS bền vững quan sát được là **21,26 req/s ở 32 VU trong 15 phút**. Cửa sổ 3 phút cao nhất đạt 21,32 req/s. Toàn lượt gồm ramp-up có **19.333 request, 0 lỗi**, khớp dashboard và 3.858 đơn trong SQLite. `PRAGMA quick_check` trả `ok`. Working set Node cao nhất **64,21 MiB**. Độ dốc working set là **+0,02 MiB/phút trong 12 phút cuối**, thấp hơn ngưỡng 2 MiB/phút. Độ dốc toàn 15 phút là +0,18 MiB/phút để tham khảo. RAM khả dụng thấp nhất là 4.013 MiB. [JTL](results/23120410_Endurance_20261119.jtl) · [Dashboard](results/23120410_Endurance_20261119/index.html) · [CSV CPU/RAM](results/23120410_Endurance_20261119_resources.csv)

| Label | p95 3 phút đầu sau ramp-up (ms) | p95 3 phút cuối (ms) |
| --- | ---: | ---: |
| 01 Login | 3 | 3 |
| 02 Search products | 3 | 2 |
| 03 Product detail | 3 | 2 |
| 04 Add to cart | 2 | 1 |
| 05 Checkout | 11 | 10 |

p95 theo từng label nằm trong ngưỡng ở cả năm cửa sổ. Kết quả giới hạn ở pha đo **15 phút** và cấu hình đã thử trên cùng máy cho Node và JMeter. Giỏ hàng nằm trong RAM của backend và đơn tích lũy vào SQLite. Không ngoại suy công suất tối đa hay kết quả chạy dài hơn. [Cửa sổ đo, tiêu chí và ba ảnh giám sát](T05_Endurance.md)

## 3. Phân tích kết quả và phản biện AI

T06 dùng OpenAI Codex trong chat riêng để phân tích JTL gốc của Stress và Spike. Lịch sử công cụ ghi nhận hai JTL là dữ liệu SUT được đọc trong lượt đó. Tính lại số request, p95, RPS và tỷ lệ lỗi từ JTL chưa phát hiện số liệu sai theo quy ước AI công bố. [Prompt và phản hồi chat riêng](ai/PromptLog.md#p-049) · [Output nguyên văn](ai/T06_External_AI_Raw.txt) · [Script tái tính](evidence/t06/recompute_jtl.py)

Phản biện làm rõ bốn điểm khi diễn giải:

1. Mốc hồi phục Spike khoảng 6 giây dùng p95 gộp. Search ở cửa sổ đầu đạt 4 ms, cao hơn ngưỡng riêng 3,6 ms. T04 xác nhận theo từng label ở 35 giây.
2. Mục tiêu ≥300 req/s ở 144 VU là ngưỡng tạm thời cho think-time 300–600 ms. Thăm dò ở cùng số VU với think-time 1–2 giây đạt 95,18 req/s.
3. Đề xuất 168 hoặc 192 VU vượt trần thử nghiệm của máy dùng chung. RAM khả dụng từng xuống 1.805 MiB ở cửa sổ 144 VU của T03.
4. RPS Search trong Stress là 34,28 theo khoảng toàn lượt và 34,47 theo khoảng riêng của label. Cả hai hợp lệ với mẫu số tương ứng.

Đối chiếu mã nguồn phân loại **1 đề xuất hallucinated** là rút ngắn khối transaction Checkout ở tầng ứng dụng, vì route chỉ gọi một INSERT và dùng transaction ngầm của SQLite. **3 đề xuất feasible có điều kiện** gồm thử WAL, kiểm tra kế hoạch truy vấn Search/Detail và profiling event loop trước khi cân nhắc chuyển tác vụ. Các ngưỡng AI đề xuất cho tải ngắn được đối chiếu với T04 và mức soak riêng của T05. [Báo cáo Task 2](AI_Log_Analysis.md)

## 4. Kết luận và Continuous Performance Testing

Kết quả local mô tả từng profile đã chạy. Stress chưa xác lập điểm bão hòa ở trần 144 VU. Endurance duy trì 21,26 req/s ở 32 VU trong 15 phút. Các mức này phụ thuộc cấu hình tải và tài nguyên của máy dùng chung.

Task 3 đề xuất lọc thay đổi từ commit hoặc PR theo đường dẫn. Thay đổi backend, schema, seed, dependency server, plan/CSV và cấu hình đo kích hoạt smoke và phép đo phù hợp. PR chạy smoke rồi lặp Load ba lần, còn Stress và Endurance dành cho lịch đêm. Mỗi lượt khởi động SUT với SQLite sạch và tài khoản giả được đăng ký lại.

Cờ regression lấy trung vị của ba p95 theo từng label. Dung sai đề xuất là giá trị lớn hơn giữa **4 ms và 25% p95 baseline**. Biên độ quan sát lớn nhất là **3,55 ms** giữa hai lượt Load, **1 ms** giữa ba lượt Stress toàn lượt, **3 ms** riêng bậc Stress 144 VU và **1 ms** giữa các cửa sổ Endurance. Baseline sẽ được đo trên runner mục tiêu và chỉ cập nhật sau khi xác nhận kết quả trên commit đã merge. Đề xuất chưa được kiểm chứng trên CI runner. [Thiết kế](Continuous_Perf_Testing.md) · [Sơ đồ A4](Continuous_Perf_Testing_Flow.png) · [Script tái tính biên độ p95](evidence/t07/recompute_noise.py)

## Phụ lục AI

Các lượt trao đổi với OpenAI Codex được ghi trong [Prompt Log](ai/PromptLog.md). [AI Audit Report](ai/AI_Audit_Report.md) dùng để đánh giá các sản phẩm trong bộ nộp. Vỹ tự viết phần nhận xét trong [AI Critique](ai/AI_Critique.md).
