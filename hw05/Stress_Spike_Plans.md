# HW05 — T03 · Stress và Spike

[Stress plan](plans/23120410_Stress_20261118.jmx) và [Spike plan](plans/23120410_Spike_20261118.jmx) chạy trên bản backend local T01 bằng JMeter 5.6.3 và Temurin 17.0.21+9. Tải và cài công cụ theo hướng dẫn T02. [Môi trường](Environment.md) · [Cài công cụ](Load_Plan.md#6-tải-và-đặt-công-cụ)

## 1. Thiết kế tải

### Thăm dò trước khi chốt tải

Giữ workflow login → tìm kiếm → chi tiết → giỏ → checkout, mỗi vòng cấp một tài khoản mới. Login và checkout ghi vào cùng SQLite. Giỏ và số đơn tích lũy trong lượt. JMeter dùng chung máy i7-12700H, RAM 15,69 GiB với backend. Chạy mỗi thăm dò sau một lần restart và đăng ký dữ liệu, với JMeter CLI và giới hạn heap 384 MiB. [Môi trường T01](Environment.md#ràng-buộc-ảnh-hưởng-tải) · [Pilot Load](evidence/t02-sizing-pilot.jtl)

Mỗi thăm dò có bốn bậc 18 giây, ramp 2 giây mỗi nhóm bổ sung. Lấy mẫu theo timestamp bắt đầu trong `[b+4,b+15)` giây của bậc `b` và có `allThreads` đúng mức. Req/s là số mẫu chia 11 giây, p95 theo nearest rank. Ghi CPU và RAM khả dụng theo mẫu khoảng 1 giây từ bộ đếm Windows. CPU của Node và JMeter được chuẩn hóa theo một lõi logic nên có thể lớn hơn 100%. Lượt ngắn dừng theo lịch tại 144 VU hoặc nếu 5 mẫu CPU/RAM liên tiếp chạm ngưỡng CPU toàn máy ≥90% hay RAM khả dụng <1.250 MiB.

| Think-time | VU | Req/s | p95 login / checkout (ms) | Lỗi trong cửa sổ | CPU máy trung bình |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1–2 s | 6 | 3,82 | 4 / 37 | 0 | 11,60% |
| 1–2 s | 24 | 16,27 | 10 / 24 | 0 | 10,79% |
| 1–2 s | 72 | 48,09 | 15 / 23 | 0 | 13,58% |
| 1–2 s | 144 | 95,18 | 20 / 28 | 0 | 16,27% |
| 300–600 ms | 24 | 51,73 | 12 / 21 | 0 | 15,05% |
| 300–600 ms | 48 | 103,00 | 18 / 34 | 0 | 19,79% |
| 300–600 ms | 96 | 210,00 | 17 / 21 | 0 | 20,67% |
| 300–600 ms | 144 | 304,45 | 45 / 100 | 0 | 22,57% |

Lượt 1–2 giây ghi 2.754 sample, không có lỗi. Throughput còn tăng ở 144 VU với p95 checkout 28 ms. Vì vậy lượt tiếp theo rút think-time xuống 300–600 ms trước mỗi request để tăng tải, giữ nguyên workflow. [JTL thăm dò 1–2 giây](evidence/t03-calibration-standard.jtl) · [CPU/RAM thăm dò 1–2 giây](evidence/t03-calibration-standard.csv)

Lượt 300–600 ms ghi 11.686 sample, không có lỗi. Từ 96 lên 144 VU, p95 checkout tăng từ 21 lên 100 ms và p95 tìm kiếm tăng từ 13 lên 55 ms. Throughput vẫn tăng từ 210 lên 304,45 req/s. Trong cửa sổ 144 VU, CPU máy đạt đỉnh 38,42%, Node dùng trung bình 51,36% của một lõi logic và RAM khả dụng thấp nhất 1.805 MiB. Thăm dò **chưa xác lập điểm bão hòa**. Mốc **144 VU là trần thử nghiệm chọn theo RAM khả dụng trên máy dùng chung**. Số đo ngắn ở mốc này chưa đủ để kết luận backend chịu được mức tải đó. T04 sẽ kiểm tra xem độ trễ tăng có lặp lại với bậc dài hơn. [JTL thăm dò 300–600 ms](evidence/t03-calibration-fast.jtl) · [CPU/RAM thăm dò 300–600 ms](evidence/t03-calibration-fast.csv) · [Số liệu theo endpoint](evidence/t03-pilots.json)

Load giữ think-time **1–2 giây** cho nhịp tải cơ sở. Stress và Spike dùng **300–600 ms** để mỗi VU gửi request dày hơn, tăng áp lực lên backend ở cùng số VU và trong giới hạn RAM của máy dùng chung.

### Stress

| Thời gian từ đầu lượt | VU thêm | Ramp-up của nhóm thêm | Thời lượng của nhóm thêm | Tổng VU sau ramp |
| --- | ---: | ---: | ---: | ---: |
| 0–30 s | 24 | 2 s | 120 s | 24 |
| 30–60 s | 24 | 2 s | 90 s | 48 |
| 60–90 s | 48 | 2 s | 60 s | 96 |
| 90–120 s | 48 | 2 s | 30 s | 144 |

Giữ bốn mức đã thăm dò với think-time 300–600 ms. Khi đối chiếu với Load 1–2 giây, dùng cả req/s và VU vì nhịp phát request đã đổi. Tăng bậc từ 18 lên 30 giây để có hai cửa sổ đối chiếu và thời gian cho request đang chờ kết thúc. Các nhóm giữ hoạt động đến khoảng giây 120. Bật **Delay Thread creation until needed** để JMeter tạo VU theo lịch. Căn mốc thời gian vào `Starting ThreadGroup: 1` trong log. `timeStamp` là lúc bắt đầu HTTP sample và `allThreads` là ảnh chụp số thread hoạt động khi sample hoàn tất. Dùng hai nguồn cùng nhau ở biên bậc. [JMeter Thread Group](https://jmeter.apache.org/usermanual/component_reference.html#Thread_Group) · [Trường JTL](https://jmeter.apache.org/usermanual/listeners.html#csvlogformat)

**Tiêu chí dừng tại T04.** Dùng JTL đang ghi và CPU/RAM toàn máy cùng số liệu tiến trình Node, Java. JMeter CLI bật tự flush để đọc được mẫu đã xong. Với mỗi bậc bắt đầu tại giây `b`, xem hai cửa sổ theo lúc gửi sample `[b+4,b+11)` và `[b+11,b+18)` sau khi các request trong cửa sổ đã có thời gian kết thúc. Tính lỗi từ `success=false` và p95 của `elapsed` theo từng label bằng nearest rank. Lấy p95 chuẩn theo label từ hai cửa sổ ở 24 VU nếu bậc đó đạt. Dừng sớm khi có một trong các dấu hiệu sau.

- Tỷ lệ lỗi **≥ 5%** ở cả hai cửa sổ, mỗi cửa sổ có ít nhất 20 HTTP sample, hoặc p95 của cùng một label ở cả hai cửa sổ đạt **max(75 ms, 3 × p95 ở 24 VU)**, với ít nhất 10 sample của label trong mỗi cửa sổ và trong dữ liệu chuẩn. Mốc 75 ms nằm giữa hai p95 checkout đã thấy ở 96 VU (21 ms) và 144 VU (100 ms). Với cửa sổ thiếu mẫu, ghi số mẫu và dựa thêm vào timeout, log và tài nguyên.
- CPU toàn máy **≥ 90%** hoặc RAM khả dụng **< 1.536 MiB**, duy trì 10 giây, hay tiến trình backend thoát hoặc mất khả năng phản hồi. Chọn mốc RAM thấp hơn 1.805 MiB đã quan sát ở bậc 144 VU để dừng nếu phần RAM còn lại giảm thêm. Ghi số liệu từng tiến trình để thấy ảnh hưởng của việc dùng chung máy.
- Có EOF sớm hoặc phát hiện tài khoản fixture đăng nhập hợp lệ bị khóa hay chưa được provision. Ghi lý do dừng là dữ liệu hoặc trạng thái thử và kiểm tra lại trước khi diễn giải hiệu năng.

Nếu không chạm điều kiện dừng sớm, plan kết thúc ở trần **144 VU / khoảng 120 giây**. Người vận hành kiểm tra trong lúc chạy và gửi lệnh Shutdown ở mục 5. Lưu mốc, số VU, điều kiện dừng và sample của bậc cuối để đối chiếu. `Start Next Thread Loop` tiếp tục ghi lỗi sample mà vẫn giữ VU cho đến khi người vận hành dừng, chạm lịch kết thúc hoặc gặp EOF.

### Spike

| Pha | Thời gian cấu hình | VU |
| --- | --- | ---: |
| Nền | 0–60 s, ramp-up 1 s | 6 |
| Đỉnh | 60–80 s, thêm 138 VU với ramp-up 1 s | 144 |
| Hồi phục | 80–150 s, nhóm thêm kết thúc | 6 |

Đỉnh gấp 24 lần nền, dùng đúng mức 144 VU có dấu hiệu tăng độ trễ trong thăm dò. Duy trì think-time 300–600 ms ở cả ba pha để cô lập thay đổi số VU. Timer làm request đầu tới muộn hơn thời điểm tạo thread. Dùng JTL và log thread để xác định ranh giới pha.

Ở T04, ghi p95 theo label, tỷ lệ lỗi và số VU thực tế ở nền, đỉnh và hồi phục. Sau khi hạ tải, xem các cửa sổ 30 giây liên tiếp bắt đầu từ 5 giây sau khi nhóm Burst thực sự kết thúc. Ghi thời điểm kết thúc cửa sổ đầu tiên có p95 từng label ≤ 1,2 lần mốc nền và tỷ lệ lỗi ≤ mức nền, nếu có ít nhất 10 sample cho từng label trong cả cửa sổ và dữ liệu nền. Nếu thiếu mẫu hoặc hết pha mà chỉ số chưa trở lại nền, ghi giới hạn đó. Response Time Graph hiển thị **trung bình** trong mỗi khoảng. Tính p95 từ raw JTL.

## 2. Dữ liệu, assertion và listener

Mỗi plan giữ đúng ba CSV Data Set Config và workflow T02. Các Thread Group gọi cùng một Test Fragment trong plan qua Module Controller. Credentials `../data/load-credentials.csv` dùng chung giữa mọi nhóm, cấp một dòng mới ở đầu mỗi vòng, **Recycle on EOF = false**, **Stop thread on EOF = true**. Sản phẩm và payload vẫn đọc riêng theo thread, có quay vòng. [CSV và assertion trong Load](Load_Plan.md#3-assertion-correlation-và-listener) · [JMeter Module Controller](https://jmeter.apache.org/usermanual/component_reference.html#Module_Controller)

Cả hai plan giữ nguyên kiểm HTTP 200 và assertion JSON từng endpoint. JWT lấy từ login cho giỏ và checkout. ID dùng cho detail phải khớp dòng CSV trong kết quả tìm kiếm. Giá từ detail và payload CSV tạo body giỏ và đơn. `orderId` dùng đối chiếu SQLite. Mỗi login xóa correlation cũ, kể cả khi JWT của SUT không có `exp`. Tài khoản dùng một lần tránh việc các VU chia sẻ bộ đếm FR-02 và giỏ.

| Plan | Listener | Cách dùng |
| --- | --- | --- |
| Load | Summary Report | Tổng hợp nhanh theo label. |
| Stress | Aggregate Report | Đọc p90/p95/p99, lỗi và throughput theo label. Dùng JTL chia theo thời gian để so từng bậc. |
| Spike | Response Time Graph | Xem diễn tiến thời gian đáp ứng trung bình theo label, khoảng gộp 5 giây. |

Listener của Stress và Spike đều **bật**. Dùng CLI với `-l` trong lượt đo và để trường Filename của từng listener trống. Ở CLI, các view GUI không tổng hợp mẫu trực tiếp. JTL CSV chỉ ghi số đo và ID đối chiếu, bỏ body, header và dữ liệu request kể cả khi lỗi. Sau lượt, mở plan, chọn listener và nạp JTL vào ô Filename/Browse. Aggregate Report gộp mẫu cùng thời gian đáp ứng. Response Time Graph dùng khoảng gộp 5 giây để giảm số điểm khi xem lại. Với JTL dài có thể nạp riêng phần cần xem. [Aggregate Report](https://jmeter.apache.org/usermanual/component_reference.html#Aggregate_Report) · [Response Time Graph](https://jmeter.apache.org/usermanual/component_reference.html#Response_Time_Graph) · [Sử dụng listener và tài nguyên](https://jmeter.apache.org/usermanual/listeners.html)

### Số tài khoản cần chuẩn bị

Dùng công thức T02 cho từng nhóm `sum(VU × (ceil(D / W) + 1))`. `D` là thời lượng nhóm tính cả ramp-up và bỏ startup delay. Thăm dò 300–600 ms đo trung vị vòng hoàn tất giữa hai login là 2,263–2,357 giây tùy bậc. Dự báo dùng trung vị thấp nhất `W = 2,263 s` ở 96 VU, từ 370 khoảng hợp lệ. Dự trù bỏ thời gian HTTP. Think-time tối thiểu của vòng đủ là 1,5 giây và của vòng cắt ở request đầu là 0,3 giây. Với giả định tối đa 10% vòng cắt sớm, dùng `W = 0,9 × 1,5 + 0,1 × 0,3 = 1,38 s`. Cộng một dòng biên mỗi VU. [Cách tính T02](Load_Plan.md#tính-số-tài-khoản) · [Số vòng quan sát được theo bậc](evidence/t03-pilots.json)

| Plan | Số giây hoạt động theo nhóm | Ước lượng từ thăm dò | Dự trù theo 1,38 s/vòng |
| --- | --- | ---: | ---: |
| Stress | 24 VU × 120 s, 24 × 90 s, 48 × 60 s, 48 × 30 s | 4.368 | **6.984** = 24 × (88 + 67) + 48 × (45 + 23) |
| Spike | 6 VU × 150 s và 138 × 20 s | 1.788 | **2.868** = 6 × 110 + 138 × 16 |

CSV repo dùng chung nay có **7.500 dòng tổng hợp**, gồm 1.250 dòng T02 và 6.250 dòng thêm. Đăng ký 7.500 sau mỗi restart để chạy mặc định với dự phòng. Nếu chuẩn bị ít hơn, dùng `--output` rồi truyền file tương ứng qua `-Jhw05.credentials` để EOF trùng số dòng đã đăng ký. Tính lại khi đổi lịch, VU, timer hoặc tỷ lệ vòng lỗi. EOF trước lịch làm giảm VU thực tế, cần ghi và loại lượt đó khỏi so sánh mức tải đích.

## 3. Reset trước lượt độc lập

1. Dừng JMeter và tiến trình backend T01 của lượt trước. Giữ JTL, log và số liệu tài nguyên. Khởi động lại bằng `node server.js` trong `HW05/.runtime/T01/backend` theo [hướng dẫn dựng và chạy bản T01](Environment.md). Khởi động mới tạo lại giỏ RAM và seed SQLite. Dùng HTTP GET `/api/products` để đợi API trả 200 với 5 sản phẩm rồi kiểm DB.
2. Trước provision, đọc SQLite của **bản runtime** để xác nhận 1 admin, 1 user, 5 sản phẩm, 0 đơn và 0 bộ đếm hoặc dấu khóa. Xác nhận danh sách sản phẩm còn khớp fixture CSV.
3. Chạy `provision_load_users.py --accounts N`. Kiểm số lượng tài khoản đúng `2 + N`, đủ `N` tài khoản fixture role `user` có email khớp các dòng được provision, sản phẩm vẫn là 5, đơn vẫn là 0 và trạng thái khóa/bộ đếm vẫn sạch. Nếu kiểm tra thất bại, xem log backend và làm lại bước restart trước khi đo.

Truy vấn SQLite chỉ đọc dùng được ở bước 2 và 3. Chạy trên `HW05/.runtime/T01/backend/database.sqlite` với SQLite CLI hoặc module Python `sqlite3`.

```sql
SELECT role, COUNT(*) FROM users GROUP BY role;
SELECT COUNT(*) FROM users WHERE role = 'user' AND email LIKE '%@hw05.example.test';
SELECT id, name FROM products ORDER BY id;
SELECT COUNT(*) FROM orders;
SELECT COUNT(*) FROM users WHERE login_attempts IS NOT 0 OR locked_until IS NOT NULL;
```

**Reset riêng một tài khoản thử** dùng để điều tra lỗi login giữa các lượt, khi cần giữ nguyên dữ liệu hiện có. Dừng phát request. Tìm ID theo email tổng hợp được cấp cho vòng lỗi, đối chiếu row và hai cột trạng thái. Chạy cập nhật có tham số ràng buộc cả ID và email, xác nhận chỉ đúng một row được sửa, commit, đọc lại hai cột, rồi đăng nhập một lần bằng thông tin đúng để kiểm HTTP 200. T01 đã kiểm chứng cả reset riêng và restart. Với lượt đo độc lập tiếp theo, luôn dùng restart và provision lại để bỏ giỏ, đơn và trạng thái tích lũy của lượt trước. [Reset T01](Environment.md#fr-02-và-reset-giữa-các-lượt) · [Bằng chứng T01](evidence/t01-smoke.json)

```sql
UPDATE users
SET login_attempts = 0, locked_until = NULL
WHERE id = :fixture_id AND email = :fixture_email AND role = 'user';
```

## 4. Bản AI đầu và chỉnh sửa

Bản đầu của thiết kế và hai JMX được lưu ở `HW05/.runtime/T03/initial/hw05` trước khi sửa. Các điểm được rà lại:

| Bản đầu | Nguyên nhân | Cách sửa |
| --- | --- | --- |
| Nhân đỉnh VU với toàn bộ thời lượng, dự trù 1.296 tài khoản cho cấu hình Stress đầu tiên. | Ước lượng sơ bộ gán thời lượng cả lượt cho nhóm khởi động muộn. | Tính theo từng nhóm và cập nhật think-time sau thăm dò. |
| Lặp nguyên workflow trong từng nhóm. | Sao chép cấu hình T02 nhanh để giữ tương đương, bỏ sót chi phí sửa đồng bộ. | Đặt CSV chung ngoài các nhóm và dùng một Test Fragment trong mỗi plan. |
| Ghi chung chung “lỗi tăng hoặc độ trễ tăng rõ”, chưa có ngưỡng hay cách dừng. | Bản phác thảo chưa chuyển yêu cầu quá tải thành thao tác quan sát và lệnh CLI. | Thêm cửa sổ theo bậc, điều kiện p95/lỗi/tài nguyên/dữ liệu, trần và lệnh Shutdown. |
| Bản gửi review tắt Aggregate Report và Response Time Graph. | Cấu hình nhằm giảm chi phí vẽ kết quả nhưng không đáp ứng yêu cầu bật đủ ba loại listener. | Bật cả hai listener, ghi JTL gọn qua CLI và nạp để xem sau lượt. |
| Bản gửi review đặt trần Stress 24 VU và đỉnh Spike 18 VU dựa trên pilot Load nhỏ. | Chưa đo mối liên hệ giữa VU, nhịp request và response time ở các mức cao. | Thăm dò ở hai cấu hình think-time và chọn lại các bậc và đỉnh từ JTL và số liệu tài nguyên. |

## 5. Chạy lại

Sau khi restart và kiểm tra seed theo mục 3, từ `SoftwareTesting` đăng ký dữ liệu trước. Đổi `7500` theo bảng bên dưới khi tái tạo pilot hoặc thăm dò.

```powershell
$suite = (Resolve-Path -LiteralPath 'HW05/eshop-sut-HW05/hw05').Path
python (Join-Path $suite 'data/provision_load_users.py') --accounts 7500
if ($LASTEXITCODE -ne 0) { throw 'Provisioning failed' }
```

Kiểm tra số tài khoản, sản phẩm, đơn và trạng thái khóa bằng truy vấn ở mục 3. Sau khi xác nhận dữ liệu sẵn sàng, chọn `Stress` hoặc `Spike`. Các plan dùng CSV repo mặc định.

```powershell
$scenario = 'Stress'
$tools = (Resolve-Path -LiteralPath 'HW05/.runtime/tools').Path
$run = (New-Item -ItemType Directory -Path ('HW05/.runtime/T03/' + $scenario + '-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))).FullName
$java = Join-Path $tools 'temurin17-jre/jdk-17.0.21+9-jre/bin/java.exe'
$jar = Join-Path $tools 'apache-jmeter-5.6.3/bin/ApacheJMeter.jar'
$plan = Join-Path $suite "plans/23120410_${scenario}_20261118.jmx"
$cli = @(
  '-n', '-t', $plan, '-l', (Join-Path $run 'run.jtl'), '-j', (Join-Path $run 'jmeter.log'),
  '-Jjmeterengine.nongui.port=4445', '-Jjmeterengine.nongui.maxport=4445',
  '-Jjmeter.save.saveservice.autoflush=true', '-Jjmeter.save.saveservice.output_format=csv',
  '-Jjmeter.save.saveservice.timestamp_format=ms', '-Jsampleresult.timestamp.start=true',
  '-Jjmeter.save.saveservice.thread_counts=true',
  '-Jsample_variables=fixture_product_id,authenticated_user_id,order_id',
  '-Jjmeter.save.saveservice.response_data=false', '-Jjmeter.save.saveservice.response_data.on_error=false',
  '-Jjmeter.save.saveservice.requestHeaders=false', '-Jjmeter.save.saveservice.responseHeaders=false',
  '-Jjmeter.save.saveservice.samplerData=false'
)
& $java -Xmx384m -jar $jar @cli
```

Dùng cổng UDP 4445 trống. Kiểm console có `Waiting for possible Shutdown` với cổng 4445 để xác nhận JMeter sẵn sàng nhận lệnh dừng của lượt này. Khi chạm tiêu chí dừng, từ terminal thứ hai đặt lại `$java` và `$jar` như trên rồi gọi:

```powershell
& $java -cp $jar org.apache.jmeter.util.ShutdownClient Shutdown 4445
```

Lệnh gửi yêu cầu dừng sạch. JMeter chờ các sample đang thực hiện. Tạo dashboard sau khi kết thúc phép đo bằng `& $java -jar $jar -g <run.jtl> -o <thư-mục-HTML-mới>`. [JMeter CLI Shutdown](https://jmeter.apache.org/usermanual/build-test-plan.html) · [Tạo HTML dashboard từ JTL](https://jmeter.apache.org/usermanual/generating-dashboard.html)

Để tái tạo thăm dò hoặc pilot, provision theo cột `N` sau khi restart và thay các thuộc tính nhóm trong `$cli` trước lệnh chạy. Với mỗi nhóm, thêm bốn đối số `-Jhw05.<scenario-lowercase>.gN.threads=<VU>`, `...gN.delay=<delay>`, `...gN.ramp_time=<ramp>`, `...gN.duration=<duration>`. Thăm dò dùng plan Stress. Lượt 1–2 giây thêm `-Jhw05.think.min_ms=1000` và `-Jhw05.think.jitter_ms=1000`. Các lượt còn lại giữ mặc định `300` cho cả hai thuộc tính.

| Lượt | N | Các nhóm (VU, delay, ramp, duration), thời gian theo giây |
| --- | ---: | --- |
| Thăm dò 1–2 giây | 1.250 | (6,0,2,72), (18,18,2,54), (48,36,2,36), (72,54,2,18) |
| Thăm dò 300–600 ms | 4.500 | (24,0,2,72), (24,18,2,54), (48,36,2,36), (48,54,2,18) |
| Pilot Stress | 7.500 để kiểm toàn bộ roster, dự trù 284 | (2,0,1,48), (2,12,1,36), (4,24,1,24), (8,36,1,12) |
| Pilot Spike | 198 | (2,0,1,38), (14,12,1,12) |

## 6. Kết quả pilot

Chạy lại ngày 18/11/2026, giờ UTC+07, với listener đã bật và think-time 300–600 ms. Mỗi lượt restart backend T01, kiểm SQLite sạch trước và sau provision, rồi chạy CLI từ thư mục ngoài repo với ba CSV theo đường dẫn mặc định.

| Lượt, giờ bắt đầu nhóm đầu | Mức VU quan sát được | HTTP sample đạt | ID login riêng biệt | Đơn khớp SQLite |
| --- | --- | ---: | ---: | ---: |
| Stress, 18:17:47 | 2 → 4 → 8 → 16 | 752/752 | 156 | 143 |
| Spike, 18:18:44 | 2 → 16 → 2 | 502/502 | 106 | 93 |
| Kiểm Shutdown Stress, 18:19:34 | 2, dừng trước bậc 2 | 10/10 | 2 | 2 |

Trong Stress, bốn cửa sổ ổn định `[2,9)`, `[14,21)`, `[26,33)`, `[38,45)` giây có lần lượt 30, 60, 121 và 235 mẫu ở đúng số VU dự kiến. Trong Spike, `[2,11)`, `[14,22)`, `[26,35)` có lần lượt 37, 277 và 39 mẫu ở mức 2, 16 và 2 VU. Nhóm nền tiếp tục qua pha hồi phục. Trước pilot Stress, cả 7.500 tài khoản fixture được xác nhận trong SQLite, với 0 đơn và 0 tài khoản có dấu khóa hoặc bộ đếm khác 0. Kiểm tra từng vòng xác nhận đúng thứ tự request, không trùng ID login giữa các nhóm, và từng đơn khớp tài khoản, tổng tiền, địa chỉ và trạng thái trong SQLite. Không có EOF hoặc trạng thái khóa/bộ đếm khác 0 sau các lượt. Hai JTL tạo được HTML dashboard bằng CLI. [JTL Stress](evidence/t03-stress-pilot.jtl) · [JTL Spike](evidence/t03-spike-pilot.jtl) · [Tổng hợp và số liệu theo cửa sổ](evidence/t03-pilots.json)

Ở bản trước review, cửa sổ `[38,47)` chạm phần kết thúc lệch nhau giữa các thread. Vì vậy cửa sổ pilot cuối chỉ xét đến giây 45. Ở lượt kiểm tra dừng sớm trên bản sửa, JMeter nhận `Shutdown` sau checkout đầu tiên và kết thúc với mã 0. Ba nhóm được lên lịch sau đó không phát sample. [JTL kiểm Shutdown](evidence/t03-stress-shutdown.jtl) · [Tổng hợp và trích log Shutdown](evidence/t03-pilots.json)

Hai pilot xác nhận workflow và lịch tải của bản sửa ở quy mô nhỏ. T04 sẽ kiểm tra độ trễ Stress có lặp lại ở bậc 30 giây và đo thời gian hồi phục của Spike sau đỉnh 144 VU.
