# T07B - Kiểm chứng Agent Skill trên EShop local

Ngày **19/11/2026** (UTC+7), trên máy `GOYOONJUNG`. Agent dùng [SKILL.md](../../../skills/eshop-perf-testing/SKILL.md) để thực hiện smoke, phân tích JTL và kiểm trạng thái so baseline.

- SUT lấy từ `85af3ba875c88283615e22cb108f13e2fccaf0e9` qua `git archive`, dùng bốn file nguồn và manifest trong `backend/`. Chỉ đổi bind sang `127.0.0.1` trong bản runtime. Node 24.14.0 dùng dependency đã cài của T01 sau khi kiểm hai manifest khớp. Không chép SQLite cũ. Sau lượt, tiến trình Node do agent khởi động được dừng.
- Trước provision có 1 admin, 1 user, 5 sản phẩm, 0 đơn và 0 trạng thái khóa/bộ đếm. T02 cho ngân sách `2 × (ceil(30 / 4,6) + 1) = 16`. Script provision tạo đủ 16 tài khoản giả mới và lưu CSV riêng ngoài repo. Đối chiếu lại SQLite trước khi phát tải. [Biên bản SQLite và cấu hình](verification.json)
- Load JMX chạy **2 VU**, ramp **5 s**, tổng cấu hình **30 s**, think-time **1–2 s**. JMeter 5.6.3 chạy CLI với Temurin 17.0.21+9 và heap tối đa 384 MiB. RAM khả dụng trước khi dựng backend là 5.747 MiB. Giá trị thấp nhất từ 49 mẫu khi chạy wrapper và xuất dashboard là 5.393 MiB, cao hơn ngưỡng 1.536 MiB. [Console](console.log) · [Log JMeter](jmeter.log)

## Lệnh đã chạy

Các lệnh dưới đây dùng PowerShell từ root repo. Biến được dùng để rút gọn đường dẫn tuyệt đối của lượt thực tế. Backend sạch và dependency được chuẩn bị theo [kịch bản demo](../../../skills/eshop-perf-testing/DEMO.md).

```powershell
$skill = 'hw05/skills/eshop-perf-testing'
$runtime = (Resolve-Path '../.runtime').Path
$run = Join-Path $runtime 'T07/skill-smoke-20261119-160755'
$java = Join-Path $runtime 'tools/temurin17-jre/jdk-17.0.21+9-jre/bin/java.exe'
$jar = Join-Path $runtime 'tools/apache-jmeter-5.6.3/bin/ApacheJMeter.jar'
$csv = Join-Path $run 'credentials.csv'
$out = Join-Path $run 'results'
$plan = (Resolve-Path 'hw05/plans/23120410_Load_20261119.jmx').Path

python hw05/data/provision_load_users.py --accounts 16 --output $csv

& "$skill/scripts/run_profile.ps1" -Plan $plan -ResultsDir $out -JavaExe $java -JMeterJar $jar -Properties @{
    'hw05.load.threads' = 2
    'hw05.load.ramp_seconds' = 5
    'hw05.load.duration_seconds' = 30
    'hw05.credentials' = $csv
}

$evidence = 'hw05/evidence/t07/skill-run'
python "$skill/scripts/analyze_jtl.py" --jtl "$evidence/run.jtl" --profile 'smoke-load-2vu-30s-ramp5' --origin-ms 1795079297822 --window 'ramp:0:5' --window 'steady:5:30' --json-out "$evidence/analysis.json"
python "$skill/scripts/compare_baseline.py" --baseline "$evidence/t04-load-reference.json" --runs "$evidence/analysis.json"
```

Wrapper yêu cầu đường dẫn kết quả mới và analyzer yêu cầu file JSON chưa tồn tại. Khi chạy lại, đổi thư mục và dùng mốc Thread Group của lượt mới.

## Kết quả thực tế

Thread Group đầu bắt đầu lúc **16:08:17,822**, tương ứng epoch ms `1795079297822`. Có **35 sample, 1,32 req/s, p95 gộp 13,80 ms và 0 lỗi**. Lịch chạy quan sát đạt 2 VU, còn 1 VU ở một số sample cuối khi thread kết thúc. RPS toàn lượt đo theo khoảng thực của các sample. Pha `[0,5)` có 3 sample và pha `[5,30)` có 32 sample (1,28 req/s trong cửa sổ 25 s). [Bảng CLI của analyzer](analysis.txt) · [JSON phân tích theo pha](analysis.json)

| Label | Số mẫu | RPS theo label | p95 (ms) | % lỗi |
| --- | ---: | ---: | ---: | ---: |
| 01 Login | 8 | 0,32 | 29 | 0 |
| 02 Search products | 8 | 0,33 | 3 | 0 |
| 03 Product detail | 7 | 0,30 | 5 | 0 |
| 04 Add to cart | 6 | 0,36 | 7 | 0 |
| 05 Checkout | 6 | 0,36 | 10 | 0 |

Tất cả sample trả HTTP 200 và `success=true`. Số mẫu, số và tỷ lệ lỗi, RPS và p95 khớp dashboard theo từng label và toàn lượt. SQLite `quick_check` trả `ok` sau lượt. Có 8 tài khoản login riêng biệt, 0 trạng thái khóa hoặc bộ đếm còn khác 0 và 6 đơn khớp toàn bộ cặp `order_id`, `user_id` của checkout thành công. JTL và thống kê dashboard được lưu kèm. HTML đầy đủ được wrapper tạo trong `../.runtime/T07/skill-smoke-20261119-160755/results/dashboard/` trên máy chạy. [JTL gốc](run.jtl) · [Dashboard statistics](statistics.json) · [Đối chiếu SQLite](verification.json)

## Kiểm tra baseline và giới hạn

Chạy comparator trên JSON của smoke với [mốc tham chiếu một lượt Load T04](t04-load-reference.json) để kiểm tra nhánh thiếu dữ liệu. Script trả **WARN / exit 2** vì chỉ có một lượt và profile smoke 2 VU/30 s khác Load 6 VU/150 s. Mốc một lượt này dùng để kiểm tra tương thích input, chưa phải baseline năm lượt của T07A. [Output so sánh](baseline-check.txt)

Kiểm tra riêng bằng JSON tổng hợp với p95 checkout chuẩn 20 ms và giới hạn 25 ms cho kết quả PASS với `[25,25,25]`, WARN với `[25,25,26]` và FAIL với `[25,26,26]`. Analyzer từ chối JTL chỉ có header. Trên bốn JTL có sẵn của T04/T05, analyzer tính khớp số mẫu, p95, RPS và tỷ lệ lỗi cho từng label và toàn lượt với bốn dashboard.

Phần phát tải bằng wrapper mới chỉ chạy smoke Load. Stress, Spike và Endurance được kiểm qua JTL lưu sẵn. CI runner, baseline năm lượt, video và khả năng tự nhận diện skill trong chat mới chưa được kiểm ở bước này.
