# T05 — Endurance (soak) 15 phút

Lượt chính ngày **19/11/2026** bắt đầu lúc **12:37:47.507** và kết thúc theo lịch lúc **12:53:07.507** (UTC+7). Plan đặt **32 VU** sau ramp-up 20 giây cho pha đo 900 giây, think-time ngẫu nhiên **1–2 giây trước mỗi request**. [Plan](plans/23120410_Endurance_20261119.jmx) · [JTL](results/23120410_Endurance_20261119.jtl) · [Dashboard HTML](results/23120410_Endurance_20261119/index.html) · [CSV CPU/RAM](results/23120410_Endurance_20261119_resources.csv) · [Đối chiếu chi tiết](evidence/t05/endurance-verification.json)

## Môi trường và chuẩn bị

Chạy trên máy `GOYOONJUNG` từ bản sao backend `85af3ba` bind `127.0.0.1:3000`. Node (PID 23804) và Apache JMeter 5.6.3 CLI (PID 9368) dùng chung máy. JMeter chạy trên Temurin 17 với `-Xmx384m`. Simple Data Writer ghi một JTL CSV theo `-Jhw05.endurance.jtl`, chứa mã phản hồi, thời gian, số luồng và ID cần đối chiếu. [Môi trường](Environment.md) · [Các phép đo T04](T04_Execution.md)

Cấu hình 32 VU dùng cùng think-time của thăm dò T03, nơi 24 VU đạt 16,27 req/s và 72 VU đạt 48,09 req/s. T04 chưa xác lập bão hòa tại 144 VU. Mức tải Endurance thấp hơn trần thử đó để dành RAM cho lần chạy dài và theo dõi giỏ hàng, đơn hàng tích lũy. [Thăm dò T03](Stress_Spike_Plans.md)

Sau pilot, dựng lại backend từ bản gốc và khởi động riêng cho lượt chính. SQLite mới có 2 tài khoản seed, 5 sản phẩm và 0 đơn. Đăng ký lại 7.500 tài khoản tổng hợp bằng `provision_load_users.py --accounts 7500`. Đối chiếu toàn bộ email trong CSV với SQLite, xác nhận đúng 7.500 tài khoản thử, 0 đơn, 0 tài khoản có dấu khóa hoặc bộ đếm sai và `PRAGMA quick_check` trả `ok`. Nhu cầu theo công thức T02 là `32 × (ceil(920 / 4,6) + 1) = 6.432` dòng. Mỗi vòng JMeter dùng một dòng mới, dừng luồng khi EOF. 4,6 giây/vòng giả định tối đa 10% vòng rút ngắn. [Cách tính T02](Load_Plan.md#tính-số-tài-khoản) · [Biên bản chuẩn bị](evidence/t05/endurance-verification.json)

Guard dừng lượt nếu CPU máy ≥90% hoặc RAM khả dụng <1.536 MiB trong 10 giây liên tục, tỷ lệ lỗi ≥5% trong hai cửa sổ 30 giây liên tiếp, tiến trình thoát bất thường, hết tài khoản hoặc fixture hợp lệ bị từ chối. Lượt chính kết thúc theo lịch với exit code `0`.

Log ghi đủ 32 luồng. Luồng cuối vào ở giây 19,378. Các luồng kết thúc từ giây 918,353 đến 919,994. Khi kiểm tra 32 VU từ JTL, dùng số luồng ở thời điểm hoàn tất mẫu và chừa hai giây cuối cho timer và các luồng lần lượt kết thúc theo lịch. [Mốc luồng](evidence/t05/endurance-verification.json)

## Kết quả từ JTL và đối chiếu SQLite

| Label | Request | RPS | p95 (ms) | Lỗi |
| --- | --- | --- | --- | --- |
| 01 Login | 3.880 | 4,23 | 3,00 | 0 (0,00%) |
| 02 Search products | 3.871 | 4,23 | 2,00 | 0 (0,00%) |
| 03 Product detail | 3.863 | 4,22 | 2,00 | 0 (0,00%) |
| 04 Add to cart | 3.861 | 4,23 | 2,00 | 0 (0,00%) |
| 05 Checkout | 3.858 | 4,23 | 10,00 | 0 (0,00%) |
| **Toàn lượt** | 19.333 | 21,06 | 8,00 | 0 (0,00%) |

JTL có 19.334 dòng gồm header. Kết quả tự tính khớp `statistics.json` về số mẫu, số lỗi, tỷ lệ lỗi, RPS và p95 của từng label và toàn lượt. RPS dùng khoảng từ đầu request đầu tiên đến cuối response cuối cùng của nhóm mẫu. p95 nội suy ở vị trí `0,95 × (n+1)` trên các giá trị `elapsed` đã sắp xếp. [JTL](results/23120410_Endurance_20261119.jtl) · [Thống kê từ dashboard](results/23120410_Endurance_20261119/statistics.json)

Sau lượt đo, SQLite có **3.858 đơn pending**, khớp từng checkout theo mã đơn, chủ đơn, số tiền, địa chỉ và trạng thái. **3.880 tài khoản thử khác nhau** được dùng để login thành công. `PRAGMA quick_check` trả `ok`, 0 tài khoản có dấu khóa hoặc bộ đếm sai, không có đơn thiếu, thừa, trùng hoặc mồ côi. [Đối chiếu SQLite](evidence/t05/endurance-verification.json)

## Diễn biến trong 15 phút giữ tải

Cửa sổ đầu bắt đầu tại giây 20 của lượt. Mỗi cửa sổ lấy request bắt đầu trong 180 giây và chia số request cho 180 để tính RPS. Dãy p95 theo thứ tự login, search, detail, cart, checkout. Working set dùng trung vị và đỉnh của các mẫu Windows. CSV có 900 mẫu trong pha giữ tải, khoảng cách trung vị 1,000 giây và lớn nhất 1,003 giây. Độ dốc là hệ số hồi quy tuyến tính của working set theo số phút thực giữa các mẫu.

| Giây từ đầu lượt | Request | RPS | p95 từng label (ms) | Lỗi | Node MiB trung vị / đỉnh | RAM khả dụng thấp nhất (MiB) |
| --- | --- | --- | --- | --- | --- | --- |
| 20–200 | 3.828 | 21,27 | 3,00 / 3,00 / 3,00 / 2,00 / 11,00 | 0,00% | 60,88 / 64,21 | 4.245 |
| 200–380 | 3.838 | 21,32 | 3,00 / 2,00 / 2,00 / 2,00 / 10,00 | 0,00% | 63,09 / 63,96 | 4.013 |
| 380–560 | 3.833 | 21,29 | 3,00 / 2,00 / 2,00 / 1,00 / 10,80 | 0,00% | 63,28 / 64,08 | 4.206 |
| 560–740 | 3.823 | 21,24 | 2,00 / 2,00 / 2,00 / 1,00 / 10,00 | 0,00% | 63,20 / 63,52 | 4.553 |
| 740–920 | 3.810 | 21,17 | 3,00 / 2,00 / 2,00 / 1,00 / 10,00 | 0,00% | 63,43 / 63,84 | 4.652 |

| Tiêu chí đã duyệt | Thực đo | Kết quả |
| --- | --- | --- |
| Hoàn tất pha đo 15 phút ở cấu hình 32 VU | 32 luồng khởi động và kết thúc theo lịch, 5 cửa sổ đủ dữ liệu | Đạt |
| p95 từng label tăng tối đa max(25% mốc đầu, 3 ms) | Đầu → cuối (ms) · Login 3,00 → 3,00, Search products 3,00 → 2,00, Product detail 3,00 → 2,00, Add to cart 2,00 → 1,00, Checkout 11,00 → 10,00 | Đạt |
| RPS từng cửa sổ sau ≥90% cửa sổ đầu | Thấp nhất 21,17 req/s. Ngưỡng 19,14 req/s | Đạt |
| Lỗi từng cửa sổ ≤0,5% | Cao nhất 0,00% | Đạt |
| Độ dốc working set Node trong 12 phút cuối ≤2 MiB/phút | 0,02 MiB/phút | Đạt |
| RAM khả dụng ≥2.048 MiB | Thấp nhất 4.013 MiB trong 15 phút | Đạt |

## Kết luận Endurance

**21,26 req/s** là mức RPS bền vững quan sát được trong 15 phút ở cấu hình 32 VU. Cửa sổ 3 phút cao nhất đạt **21,32 req/s** ở giây 200–380.

Working set Node cao nhất trong CSV là **64,21 MiB**. Hồi quy cho độ dốc **0,18 MiB/phút** trên toàn 15 phút và **0,02 MiB/phút** trên 12 phút cuối. Độ dốc toàn 15 phút dùng để tham khảo. Ngưỡng 2 MiB/phút áp dụng sau khi bỏ 3 phút làm nóng. p95 theo từng label nằm trong ngưỡng ở cả năm cửa sổ. p95 đầu → cuối (ms) · Login 3,00 → 3,00, Search products 3,00 → 2,00, Product detail 3,00 → 2,00, Add to cart 2,00 → 1,00, Checkout 11,00 → 10,00. [CSV CPU/RAM](results/23120410_Endurance_20261119_resources.csv) · [Số liệu theo cửa sổ](evidence/t05/endurance-verification.json)

Phạm vi kết luận là 15 phút ở cấu hình đã đo trên một máy dùng chung cho Node và JMeter. Giỏ nằm trong RAM của backend, đơn tích lũy vào SQLite. Đỉnh working set là giá trị cao nhất ghi được trong các mẫu một giây.

## Ảnh trong lượt đo

| Mốc | CAPTURE NOW (UTC+7) | VU quanh marker theo JTL | Ảnh |
| --- | --- | --- | --- |
| 35 s | 12:38:23.248 | 32 | [Ảnh đầu lúc 12:38:26](evidence/t05/Endurance_start_20261119_123826.png) |
| 470 s | 12:45:38.248 | 32 | [Ảnh giữa](evidence/t05/Endurance_mid_20261119_124538.png) |
| 900 s | 12:52:48.248 | 32 | [Ảnh cuối](evidence/t05/Endurance_end_20261119_125248.png) |

Tên file nguồn và giờ tạo file của ảnh giữa, ảnh cuối muộn hơn giờ hiển thị trên màn hình. Mốc trong bảng lấy từ dòng CAPTURE NOW trên ảnh, đối chiếu với log và số VU trong JTL.

Ba marker do terminal phát trong lượt chính với Node PID `23804` và JMeter PID `9368`. Ảnh Task Manager hiển thị CPU tức thời và active private working set của Node. CSV CPU/RAM lấy mẫu mỗi giây và dùng WorkingSetSize của tiến trình để tính xu hướng. [Marker và mẫu CSV gần nhất](evidence/t05/endurance-verification.json)

## Pilot, lượt dừng và lỗi

| Pilot (UTC+7) | Kết quả | Request | RAM khả dụng thấp nhất (MiB) |
| --- | --- | --- | --- |
| 10:17:45.886 | Dừng do RAM <1.536 MiB trong 10 giây | 0 | 186 |
| 10:20:08.009 | Dừng do RAM <1.536 MiB trong 10 giây | 898 | 256 |
| 12:10:20.341 | Đủ 110 giây | 2.121 | 3.878 |

Giữ toàn bộ JTL, log và CSV của các pilot trong `HW05/.runtime/T05/pilot-*`. Hai lượt đầu dừng theo guard RAM. Pilot thứ ba đạt 32 VU, ghi 2.121 request và 0 lỗi. 410 đơn khớp SQLite. Lượt chính dùng DB và tài khoản provision lại.

Lượt chính không ghi nhận HTTP 5xx, timeout, crash hay lỗi assertion. Không phát sinh nháp Issue.
