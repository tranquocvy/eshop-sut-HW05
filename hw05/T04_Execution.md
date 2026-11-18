# T04 — Thực thi Load, Stress và Spike

## Môi trường

- Hostname của máy đo là `GOYOONJUNG`, khớp với [Environment.md](Environment.md). Ảnh cấu hình được chụp lúc 22:25:38 ngày 18/11/2026 (UTC+7) bằng dxdiag. Máy Dell G15 5520, Intel Core i7-12700H, 20 luồng logic, RAM 16 GB. [Ảnh cấu hình](evidence/t04/hardware_dxdiag_20261118_152538Z.jpg) · [Mốc giờ chụp](evidence/t04/hardware-capture.json)
- Node và JMeter dùng chung máy. Backend sử dụng SQLite và giỏ hàng trong RAM. Tên plan và kết quả T04 dùng hậu tố `20261119`, theo ngày chạy. Load giữ nguyên 6 VU, ramp-up 30 giây và tổng 150 giây. [Load](plans/23120410_Load_20261119.jmx) · [Stress](plans/23120410_Stress_20261119.jmx) · [Spike](plans/23120410_Spike_20261119.jmx)

## Tổng hợp ba lượt đo

| Kịch bản | VU thực tế | Request | RPS toàn lượt | p95 toàn lượt (ms) | Tỷ lệ lỗi | Đơn khớp SQLite |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Load | 6 | 548 | 3,70 | 9,00 | 0,00% | 107 |
| Stress | 24 → 48 → 96 → 144 | 20.203 | 170,12 | 10,00 | 0,00% | 3.986 |
| Spike | 6 → 144 → 6 | 7.755 | 52,06 | 17,00 | 0,00% | 1.490 |

Cả ba lượt đã kết thúc đúng lịch. Các lượt Load và Stress trước đó được giữ riêng sau khi chạy lại cho phần ảnh. Không ghi nhận 5xx, timeout, crash, EOF, lỗi assertion hay lỗi lockout trong các lượt đo. Stress chưa xác lập điểm bão hòa ở trần 144 VU. Spike đạt tiêu chí hồi phục ở cuối cửa sổ kiểm tra đầu tiên, 35 giây sau khi nhóm Burst kết thúc.

## Chuẩn bị và trạng thái hiện tại

Trước lượt Load, tạo bản sao backend mới từ commit `85af3ba875c88283615e22cb108f13e2fccaf0e9`, đổi địa chỉ bind thành `127.0.0.1:3000` và chạy `node server.js` trong thư mục bản sao, dùng dependency đã cài ở T01. Backend tự tạo SQLite mới. Kiểm tra sau khi khởi động thấy 1 admin, 1 user seed, 5 sản phẩm với ID 1–5, 0 đơn và 0 tài khoản có bộ đếm login khác 0 hoặc `locked_until` khác `NULL`.

Lượt Load chạy lại được chuẩn bị ngày 19/11/2026 (UTC+7). Backend có PID `31688`. Đã xác minh trạng thái seed lúc 01:08:27 và chạy `provision_load_users.py --accounts 1250`. Đối chiếu SQLite lúc 01:08:50 xác nhận đúng tập 1.250 email tổng hợp, 1 admin, 1.251 user, 0 đơn và 0 tài khoản bị khóa hoặc có bộ đếm đăng nhập sai khác 0. `PRAGMA quick_check` trả `ok`. Lượt Load cần tối thiểu `6 × (ceil(150 / 4,6) + 1) = 204` dòng. [Biên bản SQLite](evidence/t04/load-ready.json) · [Cách tính số tài khoản](Load_Plan.md#tính-số-tài-khoản)

## Kết quả Load — 19/11/2026

Apache JMeter 5.6.3 chạy CLI non-GUI với Temurin 17, heap tối đa 384 MiB, JMeter PID `1184` và backend PID `31688`. Plan giữ 6 VU, ramp-up 30 giây, tổng thời lượng 150 giây và think-time 1–2 giây. Nhóm thread bắt đầu lúc **01:12:25.936 (UTC+7)**. JMeter đạt **6 VU thực tế**, ghi đủ 6 thread đã khởi động và kết thúc, dừng theo lịch và thoát mã `0`. [Bằng chứng chạy và đối chiếu](evidence/t04/load-verification.json)

| Label | Request | RPS | p95 (ms) | Lỗi |
| --- | ---: | ---: | ---: | ---: |
| 01 Login | 112 | 0,76 | 4,00 | 0 (0,00%) |
| 02 Search products | 111 | 0,76 | 3,00 | 0 (0,00%) |
| 03 Product detail | 109 | 0,77 | 3,00 | 0 (0,00%) |
| 04 Add to cart | 109 | 0,77 | 2,00 | 0 (0,00%) |
| 05 Checkout | 107 | 0,76 | 10,00 | 0 (0,00%) |
| **Toàn lượt** | **548** | **3,70** | **9,00** | **0 (0,00%)** |

JTL có 549 dòng vật lý gồm header và 548 bản ghi HTTP. Tất cả trả `200` và đạt assertion. Dashboard được tạo bằng `-g` trực tiếp từ JTL. Kết quả tính lại khớp dashboard về số mẫu, số lỗi, tỷ lệ lỗi, RPS và p95 theo từng label và toàn lượt. RPS là số request chia cho khoảng thời gian từ lúc request đầu tiên bắt đầu đến lúc response cuối cùng kết thúc trong tập mẫu tương ứng. p95 nội suy theo vị trí `0,95 × (n+1)` trên thời gian phản hồi đã sắp xếp. [JTL gốc](results/23120410_Load_20261119.jtl) · [HTML report](results/23120410_Load_20261119/index.html) · [Thống kê dashboard](results/23120410_Load_20261119/statistics.json)

CSV tài nguyên có 154 mẫu cách nhau khoảng một giây. CPU toàn máy cao nhất **31,47%**, RAM khả dụng thấp nhất **3.953 MiB**. Node đạt **4,71% CPU theo một lõi logic** và working set **58,64 MiB** tại các đỉnh đo tương ứng. JMeter đạt **277,69% CPU theo một lõi logic** và working set **189,83 MiB**. [CSV CPU/RAM](results/23120410_Load_20261119_resources.csv)

SQLite có **107 đơn `pending`**, khớp từng checkout theo mã đơn, chủ đơn, số tiền, địa chỉ và trạng thái. 112 login thành công dùng 112 tài khoản tổng hợp khác nhau. Không có tài khoản bị khóa hoặc còn bộ đếm đăng nhập sai. `PRAGMA quick_check` trả `ok`. Không ghi nhận timeout, 5xx, crash, lỗi assertion hay dữ liệu bất thường trong lượt này. Không có nháp Issue từ Load. [Đối chiếu SQLite và mã phản hồi](evidence/t04/load-verification.json)

### Ảnh theo dõi Load

Vỹ chụp thủ công hai ảnh trong lượt chạy lại. Các mốc dưới đây là timestamp `CAPTURE NOW` hiển thị trên terminal (UTC+7). Cả hai ảnh có JMeter CLI và Task Manager tab Details trong cùng khung, với hàng `node.exe` PID `31688` cùng cột CPU và Memory.

| Giai đoạn | Mốc terminal | VU đang chạy theo JMeter | Ảnh |
| --- | --- | ---: | --- |
| Tăng tải | 01:12:40.267 (`t=14,3 s`) | 3 | [Load ramp](evidence/t04/Load_ramp_20261119_011240.png) |
| Đỉnh ổn định | 01:13:55.952 (`t=90,0 s`) | 6 | [Load peak](evidence/t04/Load_peak_20261119_011355.png) |

Ảnh tăng tải cũng còn dòng tổng kết lượt đầu ở phía trên. Mốc dùng cho kết quả Load là lượt chạy lại lúc 01:12 với PID `31688`.

## Lịch sử Load

- Hai lần chuẩn bị ngày 18/11 và đầu ngày 19/11 kết thúc ở bước chờ thiết lập ảnh, trước khi phát tải. Lần thứ hai kết thúc lúc 00:12:28 (UTC+7). [Biên bản lần chuẩn bị trước](evidence/t04/load-preparation.json)
- Lượt đo bắt đầu lúc 00:55:03 ngày 19/11 đã kết thúc đúng lịch. Vỹ yêu cầu đo lại vì bộ ảnh thiếu ảnh chụp lúc tăng tải và thiếu PID trong Task Manager. Dữ liệu thô, dashboard và bản đối chiếu của lượt đầu được cất ngoài bộ nộp.

## Chuẩn bị Stress — 19/11/2026

Dựng bản backend mới từ `85af3ba`, bind `127.0.0.1:3000` và chạy `node server.js` với PID `26400`. SQLite mới lúc 01:50:55 (UTC+7) có 1 admin, 1 user seed, 5 sản phẩm, 0 đơn và 0 tài khoản có dấu khóa hay bộ đếm đăng nhập sai.

Chạy `provision_load_users.py --accounts 7500` để tạo mới tài khoản từ CSV tổng hợp trên SQLite sạch. Đối chiếu lúc 01:53:44 (UTC+7) xác nhận đúng tập 7.500 email, 1 admin, 7.501 user, 0 đơn và 0 tài khoản có dấu khóa hay bộ đếm đăng nhập sai. `PRAGMA quick_check` trả `ok`. Nhu cầu dự trù là `24 × (88 + 67) + 48 × (45 + 23) = 6.984` dòng. JMeter dùng CSV mặc định của plan và cấp mỗi dòng một lần trong lượt. [Biên bản SQLite](evidence/t04/stress-ready.json) · [Cách tính số tài khoản](Stress_Spike_Plans.md#số-tài-khoản-cần-chuẩn-bị)

## Kết quả Stress — 19/11/2026

Lượt Stress dùng cho bộ nộp bắt đầu lúc **01:55:40.786 (UTC+7)** với backend PID `26400` và JMeter PID `7660`. Apache JMeter 5.6.3 chạy CLI non-GUI với Temurin 17 và heap tối đa 384 MiB. Lượt đạt đủ bốn bậc **24 → 48 → 96 → 144 VU** với think-time 300–600 ms, kết thúc đúng lịch sau khoảng 120 giây và trả mã thoát `0`. [Bằng chứng chạy và đối chiếu](evidence/t04/stress-verification.json)

| Label | Request | RPS | p95 (ms) | Lỗi |
| --- | ---: | ---: | ---: | ---: |
| 01 Login | 4.092 | 34,46 | 9,00 | 0 (0,00%) |
| 02 Search products | 4.071 | 34,47 | 9,00 | 0 (0,00%) |
| 03 Product detail | 4.041 | 34,34 | 9,00 | 0 (0,00%) |
| 04 Add to cart | 4.013 | 34,23 | 2,00 | 0 (0,00%) |
| 05 Checkout | 3.986 | 34,10 | 14,00 | 0 (0,00%) |
| **Toàn lượt** | **20.203** | **170,12** | **10,00** | **0 (0,00%)** |

JTL có 20.204 dòng gồm header và 20.203 bản ghi HTTP. Mọi bản ghi trả `200` và đạt assertion. Tính lại số mẫu, số lỗi, tỷ lệ lỗi, RPS và p95 cho từng label và toàn lượt đều khớp `statistics.json`. Request đầu bắt đầu lúc **01:55:42.043** và response cuối kết thúc lúc **01:57:40.802** (UTC+7). Theo cách tính dashboard, `20.203 / 118,759 = 170,117633…` request/giây, làm tròn thành **170,12 RPS**. CLI hiển thị 168,3 req/s trên khoảng 120 giây của lượt. [JTL gốc](results/23120410_Stress_20261119.jtl) · [HTML report](results/23120410_Stress_20261119/index.html) · [Thống kê dashboard](results/23120410_Stress_20261119/statistics.json)

Trong mỗi bậc, gộp số request bắt đầu ở hai cửa sổ 7 giây để tính RPS. `allThreads` xác nhận mỗi mẫu trong các cửa sổ có đúng số VU của bậc. p95 checkout dùng nearest rank cho từng cửa sổ, theo tiêu chí dừng Stress. Cả tám cửa sổ có 0% lỗi. [Số liệu theo cửa sổ và label](evidence/t04/stress-verification.json)

| Bậc thực tế (VU) | Khoảng đo tính từ lúc nhóm đầu bắt đầu (s) | Request | RPS | p95 checkout ở cửa sổ 1 / 2 (ms) |
| ---: | --- | ---: | ---: | ---: |
| 24 | [4, 18) | 751 | 53,64 | 10 / 35 |
| 48 | [34, 48) | 1.487 | 106,21 | 11 / 11 |
| 96 | [64, 78) | 2.953 | 210,93 | 20 / 14 |
| 144 | [94, 108) | 4.436 | 316,86 | 15 / 16 |

Không chạm tiêu chí dừng theo p95, tỷ lệ lỗi hay tài nguyên. Throughput còn tăng đến bậc 144 VU, trần đã chọn cho máy dùng chung, nên lượt này chưa xác lập điểm bão hòa. CSV có 139 mẫu cách nhau khoảng một giây, từ khi JVM khởi động đến cuối lượt. CPU toàn máy cao nhất **30,06%**, RAM khả dụng thấp nhất **3.632 MiB**. Đỉnh Node là **43,11% CPU theo một lõi logic** và **99,96 MiB working set**. Đỉnh JMeter là **299,45% CPU theo một lõi logic** và **274,70 MiB working set**. [CSV CPU/RAM](results/23120410_Stress_20261119_resources.csv)

Đối chiếu lại SQLite từ bản sao của lượt này xác nhận **3.986 đơn `pending`** khớp 1–1 với 3.986 checkout theo mã đơn, chủ đơn, số tiền, địa chỉ và trạng thái. Không có mã đơn trùng, đơn thiếu, đơn thừa hay đơn mồ côi. 4.092 login thành công dùng 4.092 tài khoản tổng hợp khác nhau. Kiểm tra cuối có 0 tài khoản có dấu khóa hoặc còn bộ đếm sai. `PRAGMA quick_check` trả `ok`. Không ghi nhận 5xx, timeout, crash, lỗi assertion, EOF hay lockout. Không có nháp Issue từ Stress. [Đối chiếu SQLite và mã phản hồi](evidence/t04/stress-verification.json)

### Ảnh theo dõi Stress

Vỹ chụp thủ công hai ảnh khi Stress đang chạy. Giờ chụp lấy theo tên file gốc (UTC+7). Cả hai ảnh hiện JMeter CLI và Task Manager tab Details trong cùng khung, với `node.exe` PID `26400` và các cột CPU, Memory. Đối chiếu `allThreads` trong JTL quanh giờ chụp xác nhận đúng bậc hiển thị trên terminal.

| Giờ chụp | Mốc terminal | Bậc theo JMeter và JTL | Ảnh |
| --- | --- | ---: | --- |
| **01:56:54** | `CAPTURE NOW` lúc 01:56:51.001 (`t=70,2 s`) | 96 VU (`Active: 96`) | [Ảnh Stress 96 VU](evidence/t04/Stress_96VU_20261119_015654.png) |
| **01:57:25** | `CAPTURE NOW` lúc 01:57:20.927 (`t=100,1 s`) | 144 VU (`Active: 144`) | [Ảnh Stress 144 VU](evidence/t04/Stress_144VU_20261119_015725.png) |

Cột CPU trong tab Details là ảnh chụp tức thời của lần cập nhật gần nhất và có thể hiển thị chậm khi tải đổi. Ở ảnh **144 VU**, Task Manager hiện **01%** cho PID `26400`. Mẫu gần giờ chụp nhất ở **dòng 123** của CSV, lúc **01:57:24.825 (UTC+7)**, ghi **29,09% CPU theo một lõi logic** và **98,94 MiB working set** của Node. 29,09% theo một lõi tương đương khoảng 1,45% nếu quy trên toàn bộ 20 luồng logic. Số đo chính thức dùng cho phân tích là CSV CPU/RAM. [CSV CPU/RAM](results/23120410_Stress_20261119_resources.csv)

### Lịch sử Stress

| Lượt bắt đầu (UTC+7) | VU cao nhất | Request | RPS | p95 toàn lượt (ms) | Tỷ lệ lỗi | Đơn khớp SQLite | Trạng thái và lý do |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 01:23:49.100 | 144 | 20.246 | 170,20 | 10 | 0,00% | 3.988 | Lưu riêng. Vỹ báo chụp sai mốc và yêu cầu chạy lại. |
| 01:30:48.380 | 144 | 20.224 | 170,00 | 10 | 0,00% | 3.991 | Lưu riêng. Do lỗi kỹ thuật khi chụp, ảnh đỉnh được chụp sau khi backend đã dừng. |
| **01:55:40.786** | **144** | **20.203** | **170,12** | **10** | **0,00%** | **3.986** | **Bộ nộp**. Backend PID `26400`, có hai ảnh được Vỹ xác nhận ở 96 và 144 VU. |

Cả ba lượt kết thúc đúng lịch. JTL, dashboard, CSV tài nguyên, bản đối chiếu và ảnh có sẵn của hai lượt đầu được lưu ngoài bộ nộp. JTL, dashboard, CSV tài nguyên và hai ảnh trong bộ nộp đều thuộc lượt bắt đầu lúc 01:55:40.786.

## Chuẩn bị Spike — 19/11/2026

Dựng bản backend riêng từ `85af3ba`, bind `127.0.0.1:3000` rồi chạy `node server.js` với PID `6536`. SQLite mới lúc 01:35:40 (UTC+7) có 1 admin, 1 user seed, sản phẩm ID 1–5, 0 đơn và 0 tài khoản có dấu khóa hay bộ đếm đăng nhập sai.

Đã chạy `provision_load_users.py --accounts 3000 --output <đường dẫn runtime>/registered.csv`. Đối chiếu lúc 01:36:46 (UTC+7) xác nhận đúng tập 3.000 email tổng hợp, 1 admin, 3.001 user, 0 đơn và 0 tài khoản có dấu khóa hay bộ đếm đăng nhập sai. `PRAGMA quick_check` trả `ok`. Nhu cầu tính theo lịch nhóm và giả định 1,38 giây/vòng là `6 × 110 + 138 × 16 = 2.868` dòng. Tham số `-Jhw05.credentials` trỏ JMeter tới `registered.csv` chứa đúng 3.000 tài khoản đã đăng ký. [Biên bản SQLite](evidence/t04/spike-ready.json) · [Cách tính số tài khoản](Stress_Spike_Plans.md#số-tài-khoản-cần-chuẩn-bị)

## Kết quả Spike — 19/11/2026

Apache JMeter 5.6.3 chạy CLI non-GUI với Temurin 17 và heap tối đa 384 MiB. JMeter PID `26188`, backend PID `6536`. Nhóm đầu tiên bắt đầu lúc **01:38:36.417 (UTC+7)**. Lượt 150 giây giữ think-time 300–600 ms, ghi **6 → 144 → 6 VU** và kết thúc theo lịch với mã thoát `0`. [Bằng chứng chạy và đối chiếu](evidence/t04/spike-verification.json)

| Label | Request | RPS | p95 (ms) | Lỗi |
| --- | ---: | ---: | ---: | ---: |
| 01 Login | 1.609 | 10,81 | 19,00 | 0 (0,00%) |
| 02 Search products | 1.588 | 10,76 | 11,00 | 0 (0,00%) |
| 03 Product detail | 1.551 | 10,51 | 11,00 | 0 (0,00%) |
| 04 Add to cart | 1.517 | 10,29 | 6,00 | 0 (0,00%) |
| 05 Checkout | 1.490 | 10,16 | 30,00 | 0 (0,00%) |
| **Toàn lượt** | **7.755** | **52,06** | **17,00** | **0 (0,00%)** |

JTL có 7.756 dòng gồm header và 7.755 bản ghi HTTP. Tất cả trả `200` và đạt assertion. Số mẫu, lỗi, RPS và p95 tính lại đều khớp `statistics.json` theo từng label và toàn lượt. [JTL gốc](results/23120410_Spike_20261119.jtl) · [HTML report](results/23120410_Spike_20261119/index.html) · [Thống kê dashboard](results/23120410_Spike_20261119/statistics.json)

Log ghi 138 thread Burst bắt đầu trong khoảng **01:39:36.421–01:39:37.421**, thread Burst cuối kết thúc lúc **01:39:56.406** (UTC+7). Đo nền từ giây 5 đến khi thread Burst đầu tiên bắt đầu. Đo đỉnh từ một giây sau khi thread Burst cuối bắt đầu đến khi thread Burst đầu tiên kết thúc. Hai cửa sổ hồi phục liên tiếp dài 30 giây, bắt đầu 5 giây sau khi thread Burst cuối kết thúc. RPS từng cửa sổ là số request bắt đầu trong cửa sổ chia cho độ dài cửa sổ. [Mốc thread và số liệu theo pha](evidence/t04/spike-verification.json)

| Pha và cửa sổ (UTC+7) | VU theo JTL | Request | RPS | p95 login / search / detail / cart / checkout (ms) | Lỗi |
| --- | ---: | ---: | ---: | --- | ---: |
| Nền 01:38:41.417–01:39:36.421 | 6 | 729 | 13,25 | 3 / 3 / 3 / 2 / 12 | 0,00% |
| Đỉnh 01:39:38.421–01:39:55.834 | 144 | 5.474 | 314,36 | 24 / 15 / 13 / 7 / 34 | 0,00% |
| Hồi phục 1, 01:40:01.406–01:40:31.406 | 6 | 394 | 13,13 | 3 / 2 / 2 / 2 / 9,05 | 0,00% |
| Hồi phục 2, 01:40:31.406–01:41:01.406 | 6 | 392 | 13,07 | 2,10 / 2 / 2 / 1 / 10,10 | 0,00% |

Cả hai cửa sổ hồi phục có ít nhất 10 mẫu ở mỗi label, p95 từng label ≤1,2 lần nền và tỷ lệ lỗi bằng nền. Mốc xác nhận đầu tiên là **01:40:31.406**, tức **35 giây** sau khi nhóm Burst kết thúc. Đây là thời điểm kết thúc cửa sổ kiểm tra đầu tiên. [Số mẫu và đối chiếu ngưỡng](evidence/t04/spike-verification.json)

CSV tài nguyên có 154 mẫu cách nhau khoảng một giây. CPU toàn máy cao nhất **32,96%**, RAM khả dụng thấp nhất **3.540 MiB**. Đỉnh Node là **55,12% CPU theo một lõi logic** và **119,54 MiB working set**. Đỉnh JMeter là **292,07% CPU theo một lõi logic** và **279,66 MiB working set**. [CSV CPU/RAM](results/23120410_Spike_20261119_resources.csv)

SQLite có **1.490 đơn `pending`** khớp mỗi checkout theo mã đơn, chủ đơn, số tiền, địa chỉ và trạng thái. 1.609 login thành công dùng 1.609 tài khoản tổng hợp khác nhau. Có 0 tài khoản bị khóa hoặc còn bộ đếm đăng nhập sai. `PRAGMA quick_check` trả `ok`. Không ghi nhận 5xx, timeout, crash, lỗi assertion, EOF hay dấu hiệu lockout. Không có nháp Issue từ Spike. [Đối chiếu SQLite và mã phản hồi](evidence/t04/spike-verification.json)

### Ảnh theo dõi Spike

Vỹ chụp thủ công hai ảnh khi Spike đang chạy. Giờ chụp lấy theo tên file gốc (UTC+7). Cả hai ảnh có JMeter CLI và Task Manager tab Details cùng khung, với `node.exe` PID `6536` và cột CPU, Memory.

| Giờ chụp | Mốc terminal hiển thị | Pha tại thời điểm chụp | Ảnh |
| --- | --- | --- | --- |
| **01:39:41** | `RAMP` lúc 01:39:36.499 (`t=60,1 s`) | Đầu đỉnh, JTL ghi 144 VU quanh giờ chụp. Terminal giữ dòng tổng hợp 78 VU từ lúc tăng tải. | [Ảnh đầu đỉnh Spike](evidence/t04/Spike_early_peak_20261119_013941.png) |
| **01:39:49** | `PEAK` lúc 01:39:45.698 (`t=69,3 s`) | Trong đỉnh 144 VU, khớp log JMeter và JTL. | [Ảnh đỉnh Spike](evidence/t04/Spike_peak_20261119_013949.png) |

Hai ảnh ghi nhận backend đang chạy ở đầu và giữa đỉnh 144 VU. Bước chuyển từ 6 lên 144 VU diễn ra trong một giây, từ 01:39:36.421 đến 01:39:37.421 theo log thread. Log và JTL ghi lại bước chuyển đó. [JTL gốc](results/23120410_Spike_20261119.jtl) · [Mốc thread](evidence/t04/spike-verification.json)
