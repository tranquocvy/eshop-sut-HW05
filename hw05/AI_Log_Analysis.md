# T06 — Đối chiếu phân tích JTL của AI

OpenAI Codex trong chat riêng, model hiển thị **GPT - 6.2 Sol High**, phân tích từ **13:33:46 đến 13:39:13 ngày 19/11/2026 (UTC+7, Asia/Bangkok)** theo lịch sử lượt chat do Vỹ cung cấp. Phản hồi được lưu đúng chuỗi ký tự Vỹ dán. [Output nguyên văn](ai/T06_External_AI_Raw.txt)

Chat riêng **Phân tích JTL Stress và Spike** chạy trong cùng workspace và có thể đọc repo local. Vỹ đính kèm hai JTL gốc và mô tả e-shop dùng Express và SQLite, chạy local trên cùng máy với JMeter. Theo lịch sử công cụ của lượt phân tích, dữ liệu SUT thực sự được đọc gồm đúng hai JTL trong `hw05/results/`. Chat có tìm tên `AGENTS.md` nhưng không nhận được kết quả. Các thao tác còn lại phục vụ tính toán Python và dựng biểu đồ từ JTL. Lịch sử không ghi nhận việc đọc mã backend, dashboard, CSV tài nguyên hay tài liệu T04/T05. Độ khớp của số liệu đến từ việc tính trực tiếp trên JTL. Mã nguồn và biên bản T03–T05 được dùng ở bước đối chiếu này. [JTL Stress](results/23120410_Stress_20261119.jtl) · [JTL Spike](results/23120410_Spike_20261119.jtl)

## 1. Cách tái tạo số liệu

Chạy từ gốc repo với Python 3.10 trở lên. Script dùng thư viện chuẩn và in JSON gồm số liệu theo hai quy ước, cửa sổ T04, pha giữ tải T05 và kế hoạch thực thi SQLite trên schema bảng `products`.

```powershell
python hw05/evidence/t06/recompute_jtl.py
```

- Một bản ghi CSV sau header là một HTTP sample. Lỗi là số bản ghi có `success=false` chia cho số mẫu trong nhóm. Dùng `responseCode` và `failureMessage` để đối chiếu.
- Đặt thời điểm bắt đầu `s = timeStamp`, thời điểm kết thúc `e = timeStamp + elapsed`, theo mili giây. RPS toàn lượt và phần đóng góp của mỗi label trong output AI đều chia cho `(max(e) − min(s)) / 1.000` tính trên toàn file. Dashboard dùng khoảng riêng của từng label khi báo RPS theo label.
- Trong các cửa sổ của AI, lấy mẫu có `e` trong `[min(s) + a×1.000, min(s) + b×1.000)` và chia số mẫu cho `b − a`. Lấy số VU từ `allThreads`. p95 dùng nearest rank, lấy phần tử thứ `ceil(0,95 × N)` từ dãy `elapsed` đã sắp tăng, đánh số từ 1. T04 dùng mốc log luồng và `s` để lọc cửa sổ. Khi tái đối chiếu dashboard hoặc p95 hồi phục Spike của T04, nội suy tại `0,95 × (N+1)` và chặn ở hai đầu dãy.

Chạy thêm khối sau từ gốc repo để đối chiếu hai profile T03 và RAM khả dụng ở 144 VU. Mỗi cửa sổ gồm mốc đầu và bỏ mốc cuối. Các mốc dùng giờ UTC+7.

```powershell
@'
import csv
from datetime import datetime
from pathlib import Path

def rows(path):
    with Path(path).open(encoding="utf-8", newline="") as file:
        yield from csv.DictReader(file)

def epoch_ms(instant):
    return round(datetime.fromisoformat(instant).timestamp() * 1000)

for profile, start in [("standard", "2026-11-18T18:10:59.437+07:00"),
                       ("fast", "2026-11-18T18:13:56.136+07:00")]:
    t0 = epoch_ms(start)
    count = sum(t0 + 58000 <= int(r["timeStamp"]) < t0 + 69000 and r["allThreads"] == "144"
                for r in rows(f"hw05/evidence/t03-calibration-{profile}.jtl"))
    print(profile, count, f"{count / 11:.2f} req/s")

windows = [
    ("hw05/evidence/t03-calibration-fast.csv", "available_phys_mib",
     "2026-11-18T18:14:54.136+07:00", "2026-11-18T18:15:05.136+07:00"),
    ("hw05/results/23120410_Stress_20261119_resources.csv", "host_available_mib",
     "2026-11-19T01:57:14.786+07:00", "2026-11-19T01:57:28.786+07:00"),
    ("hw05/results/23120410_Spike_20261119_resources.csv", "host_available_mib",
     "2026-11-19T01:39:38.421+07:00", "2026-11-19T01:39:55.834+07:00"),
]
for path, ram, start, end in windows:
    measurements = list(rows(path))
    lo, hi = epoch_ms(start), epoch_ms(end)
    at_144_vu = [int(r[ram]) for r in measurements if lo <= int(r["epoch_ms"]) < hi]
    print(Path(path).name, f"144 VU: {min(at_144_vu)} MiB",
          f"full CSV: {min(int(r[ram]) for r in measurements)} MiB")
'@ | python -
```

## 2. Misinterpretation hunt

Không phát hiện số liệu sai so với JTL theo quy ước AI đã công bố. Phần cần phản biện là phạm vi kết luận, giả định về tài nguyên và cách đối chiếu khi phương pháp đo khác nhau.

| Phát biểu hoặc đề xuất của AI | Giá trị đối chiếu và cách tính | Đánh giá |
| --- | --- | --- |
| Spike hồi phục trong khoảng 6 giây nếu cửa sổ 5 giây đạt p95 gộp ≤12 ms và trở về tải nền. | Cửa sổ AI dùng `[80,85)` có **66 mẫu hoàn tất / 5 s = 13,20 req/s**, p95 gộp **7 ms**, kết thúc sau sample Burst cuối **5,999 s**. Lọc riêng 15 mẫu Search theo `label` trong cửa sổ ấy, cả nearest rank và cách nội suy T04 cho **4 ms**. Search nền T04 **3 ms**, giới hạn **3 × 1,2 = 3,6 ms**. T04 xác nhận ở cuối cửa sổ đầu 30 giây, từ giây 5 đến 35 sau khi luồng Burst cuối kết thúc. [JTL Spike](results/23120410_Spike_20261119.jtl) · [T04 Spike](T04_Execution.md#kết-quả-spike--19112026) | **Giới hạn diễn giải.** Khoảng 6 giây đúng với phép kiểm p95 gộp. Cửa sổ đó chưa đáp ứng ngưỡng riêng cho Search. Mốc T04 **35 giây** áp dụng cho kiểm tra từng label và không xác định giây chính xác bắt đầu hồi phục. |
| Lấy ≥300 req/s làm mục tiêu hồi quy Stress ở 144 VU. | Trong một lượt Stress, đếm mẫu hoàn tất ở `[95,115)` và chia cho 20 giây cho **6.325 / 20 = 316,25 req/s**. Bốn cửa sổ 5 giây trong cùng lượt đạt **314,40–318,80 req/s**, với think-time **300–600 ms**. Thăm dò T03 cùng 144 VU, lọc `allThreads=144` và `timeStamp` trong `[58,69)` sau khi bắt đầu nhóm đầu. Kết quả là **3.349 / 11 = 304,45 req/s** ở 300–600 ms và **1.047 / 11 = 95,18 req/s** ở 1–2 s. [Thiết kế và thăm dò T03](Stress_Spike_Plans.md) · [JTL T03 1–2 s](evidence/t03-calibration-standard.jtl) · [JTL T03 300–600 ms](evidence/t03-calibration-fast.jtl) | **Giả định cần giới hạn.** Ngưỡng tạm thời có căn cứ ở profile nhanh. Bốn cửa sổ thuộc cùng một lượt và chưa cho thấy độ lặp lại giữa các lượt. Thay think-time có thể làm throughput thay đổi lớn ngay cả ở cùng số VU. |
| Tăng lên 168 hoặc 192 VU để tìm điểm gãy. | Lọc `epoch_ms` theo cửa sổ 144 VU rồi lấy `min` của cột RAM khả dụng. T03 nhanh có **1.805 MiB** ở `[58,69)` (`available_phys_mib`), cao hơn guard T04 **1.536 MiB** đúng **269 MiB**. T04 Stress có **3.767 MiB** ở `[94,108)` và **3.632 MiB** nếu tính toàn CSV. T04 Spike có **3.540 MiB** ở cửa sổ đỉnh, cũng là min toàn CSV. T04 dùng `host_available_mib`. [CSV T03](evidence/t03-calibration-fast.csv) · [CSV T04 Stress](results/23120410_Stress_20261119_resources.csv) · [CSV T04 Spike](results/23120410_Spike_20261119_resources.csv) | **Giả định tài nguyên chưa được kiểm chứng.** 168 và 192 VU vượt trần thử nghiệm **144 VU** đã chọn theo RAM của máy dùng chung. RAM còn dư thay đổi giữa các lượt. Các mẫu hiện có chưa cho biết hai mức tải cao hơn cần bao nhiêu RAM hoặc có chạm guard hay không. |
| RPS Search của Stress là 34,28 req/s. | Cùng **4.071** mẫu Search. AI chia cho khoảng toàn lượt `max(timeStamp + elapsed) − min(timeStamp)` là **118,759 s**, ra **34,28 req/s**. Dashboard tính khoảng riêng của các mẫu Search là **118,092 s**, ra **4.071 / 118,092 = 34,47 req/s**. [JTL Stress](results/23120410_Stress_20261119.jtl) · [Dashboard Stress](results/23120410_Stress_20261119/statistics.json) | **Khác quy ước hợp lệ.** AI công bố mẫu số toàn lượt để đo phần đóng góp của label. Khi so với dashboard cần ghi mẫu số trước khi so số. |

| Nội dung đối chiếu | Kết quả tái tính |
| --- | --- |
| Toàn lượt | Stress có **20.203 mẫu / 118,759 s = 170,12 req/s**, p95 **10 ms**. Spike có **7.755 mẫu / 148,959 s = 52,06 req/s**, p95 **17 ms**. Cả **27.958** mẫu đều trả HTTP 200, `success=true`, `failureMessage` trống. Số mẫu và p95 của đủ năm label cũng khớp. |
| Stress thay bậc và giữ ở 144 VU | Cửa sổ hoàn tất `[95,115)` có **6.325 mẫu / 20 s = 316,25 req/s**, p95 chung **12 ms**. Trong `[90,91)`, **284 mẫu** cho p95 chung **99 ms**. Có **14 mẫu ≥100 ms**, bắt đầu trong `t=90,012–90,063 s`. Checkout lâu nhất **159 ms**. [JTL dòng 11163](results/23120410_Stress_20261119.jtl#L11163) |
| Spike đỉnh và trở về nền | Cửa sổ hoàn tất `[65,75)` có **3.134 mẫu / 10 s = 313,40 req/s**, p95 chung **16 ms**. Ở `[75,76)`, p95 chung **45 ms**, Checkout chậm nhất **71 ms**. Cửa sổ `[80,85)` có **66 mẫu / 5 s = 13,20 req/s**, p95 chung **7 ms** và 6 VU. [JTL dòng 5701](results/23120410_Spike_20261119.jtl#L5701) · [Mẫu Burst cuối, dòng 6836](results/23120410_Spike_20261119.jtl#L6836) |

JTL xác nhận các đợt tăng độ trễ ngắn. Chênh lệch giữa `Connect`, `Latency` và `elapsed` chưa đủ để quy nguyên nhân cho Node, SQLite hoặc JMeter. Hai lượt ngắn ở trần thử nghiệm 144 VU chưa xác lập điểm bão hòa. Việc đối chiếu đơn hàng dựa trên SQLite của T04, ngoài phạm vi dữ liệu AI nhận được. [Đối chiếu Stress](evidence/t04/stress-verification.json) · [Đối chiếu Spike](evidence/t04/spike-verification.json)

## 3. Đối chiếu đề xuất tối ưu với mã SUT

| Đề xuất trong output AI | Phân loại | Căn cứ trong SUT và phạm vi áp dụng |
| --- | --- | --- |
| Rút ngắn transaction ghi Checkout và đo riêng `COMMIT`. | **hallucinated** | Hướng sửa giả định có khối transaction ứng dụng để rút ngắn. Route gọi đúng một `db.run(INSERT …)` rồi trả `orderId` từ callback. SQLite tự quản lý transaction ngầm của lệnh này. Code hiện tại cho phép đo thời gian cả lệnh INSERT và callback, chưa có điểm gọi `COMMIT` riêng để đặt bộ đo. Giỏ hàng ở RAM trong route cart, còn JWT được xác minh ở middleware trước checkout. [Checkout](../backend/server.js#L297-L309) · [Cart](../backend/server.js#L284-L295) · [JWT](../backend/server.js#L100-L110) |
| Thử bật SQLite WAL nếu thấy đọc và ghi cản nhau. | **feasible** | Backend dùng một kết nối tới file SQLite, môi trường đo dùng `journal_mode=delete`. Có thể thử WAL trên bản sao local và đối chiếu SQLite, thời gian INSERT, `SQLITE_BUSY` và p95 theo cùng profile. Lợi ích đọc/ghi song song phụ thuộc cách kết nối và lịch truy vấn thực tế. Đây là thử nghiệm tùy chọn trong phạm vi bài. [Kết nối SQLite](../backend/database.js#L1-L11) · [Môi trường đo](Environment.md) |
| Kiểm tra kế hoạch và tối ưu Search products / Product detail. | **feasible** | `EXPLAIN QUERY PLAN` trên schema hiện tại cho `SCAN products` với `LIKE '%Galaxy%'`, còn truy vấn chi tiết `WHERE id = ?` dùng `INTEGER PRIMARY KEY`. Có thể đo Search với dữ liệu lớn hơn hoặc cân nhắc chỉ mục hỗ trợ tìm chuỗi con nếu cần. Chỉ mục B-tree thường trên tên không xử lý mẫu bắt đầu bằng `%` theo kiểu tìm tiền tố. Detail đã dùng khóa chính, nên cần profiling trước khi sửa. Kiểm tra SQL và đo so sánh là khả thi trong bài, thay đổi cách tìm kiếm cần giữ ngữ nghĩa và báo thành thử nghiệm riêng. [Truy vấn danh sách và chi tiết](../backend/server.js#L141-L165) · [Schema sản phẩm](../backend/database.js#L64-L71) |
| Đo event-loop delay, profile CPU và chuyển phần đồng bộ đã xác nhận là nặng ra khỏi event loop. | **feasible** | Login gọi SQLite qua callback và ký token bằng `jwt.sign` không truyền callback. Middleware gọi `jwt.verify` rồi cho request đi tiếp, còn cart thao tác trên mảng trong RAM. Có thể đo event-loop delay và CPU Node/JMeter trên bản sao local. Chỉ có căn cứ chuyển tác vụ khi profile cho thấy điểm nóng. Lượt đối chứng tách máy JMeter cần máy bổ sung và quy trình đo riêng. [Login](../backend/server.js#L32-L52) · [Middleware](../backend/server.js#L100-L110) · [Cart](../backend/server.js#L284-L295) |

## 4. Ngưỡng AI đề xuất so với phép đo

| Ngưỡng đề xuất | Đối chiếu T04 / T05 |
| --- | --- |
| **Stress ổn định 144 VU:** mỗi cửa sổ 5 s đạt ≥300 req/s, p95 chung ≤20 ms, Checkout ≤25 ms. | Bốn cửa sổ AI chọn `[95,115)` đạt **314,40–318,80 req/s**, p95 chung **11–13 ms**, Checkout **15–17 ms**. T04 đạt **316,86 req/s** trong hai cửa sổ 7 s ở 144 VU, Checkout **15 và 16 ms**. Kết quả hỗ trợ dùng ngưỡng làm mục tiêu tạm thời trên cùng profile. Các cửa sổ này chưa kiểm đủ mọi cửa sổ của một bậc giữ 30 s. |
| **Stress lúc chuyển bậc:** p95 chung ≤75 ms trong mỗi cửa sổ 1 s đủ 100 mẫu. | Cửa sổ `[90,91)` có **284 mẫu và 99 ms**, vượt mục tiêu AI. T04 dùng ngưỡng dừng theo từng label trong hai cửa sổ 7 s liên tiếp và công thức `max(75 ms, 3 × p95 nền)`. Hai quy tắc đo khác khoảng và độ chi tiết. |
| **Spike tải cao:** ≥300 req/s, p95 chung ≤35 ms, Checkout ≤50 ms trong cửa sổ 5 s. p95 chung trong cửa sổ 1 s đủ mẫu ≤50 ms. | Ba cửa sổ 5 s AI nêu đạt **313,00–313,80 req/s**, p95 chung tối đa **29 ms** và Checkout tối đa **46 ms**. p95 chung cao nhất trong các cửa sổ 1 s đủ mẫu của pha là **45 ms**. T04 ghi **314,36 req/s** và p95 Checkout **34 ms** ở cửa sổ đỉnh riêng, tương thích với mục tiêu tham khảo cho tải ngắn. |
| **Spike hồi phục:** trong 6 s sau sample Burst cuối có cửa sổ 5 s đạt 12–15 req/s, p95 chung ≤12 ms và 0 lỗi, rồi duy trì qua hai cửa sổ liền sau. | Ba cửa sổ `[80,95)` đạt **13,00–13,60 req/s**, p95 chung **7–9 ms**, 0 lỗi. Cửa sổ đầu kết thúc sau sample Burst cuối **5,999 s**. T04 xác nhận sau **35 s** tính từ luồng Burst cuối theo cửa sổ 30 s và điều kiện p95 của từng label ≤1,2 lần nền. Cửa sổ 5 s đầu có Search p95 **4 ms**, vượt mốc **3,6 ms** nếu áp dụng riêng tiêu chí theo label của T04. Hai mốc phục hồi là kết quả của hai phép kiểm khác nhau. |
| **Lỗi tải cao ≤0,10%.** | Cả hai JTL T04 đều **0 lỗi**. Đây là dung sai đề xuất theo `success`, cần tái kiểm khi lặp tải. T05 dùng ngưỡng **≤0,5%** từng cửa sổ 3 phút của soak và cũng đạt **0 lỗi**. |

T05 đo **21,26 req/s ở 32 VU trong 15 phút**, working set Node cao nhất **64,21 MiB** và độ dốc 12 phút cuối **+0,02 MiB/phút**. T05 dùng think-time khác và cửa sổ theo phút, nên đây là mốc endurance riêng. Các mức 300 req/s của AI là mục tiêu ngắn hạn ở 144 VU, chưa được kiểm trong soak. Đề xuất lên 168 và 192 luồng vượt trần thử nghiệm đã chọn cho máy dùng chung của T04, cần một thiết kế đo mới với giới hạn tài nguyên phù hợp trước khi đánh giá. [Thực thi T04](T04_Execution.md) · [Kết quả T05](T05_Endurance.md) · [Script tái tính](evidence/t06/recompute_jtl.py)
