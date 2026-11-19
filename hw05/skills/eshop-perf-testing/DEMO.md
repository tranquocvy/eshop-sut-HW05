# Demo Agent Skill EShop

Quay một lượt từ chuẩn bị đến phân tích của đủ năm request. Dự kiến **6–7 phút** nếu dùng clip này cho phần demo HW05. Đề yêu cầu tổng video demo ít nhất 6 phút, YouTube unlisted, có thuyết minh tiếng Việt bằng giọng của Vỹ. Khi chạy tải, đặt terminal JMeter cạnh Task Manager trong cùng khung. Dùng PID Node của lượt đang quay để chọn đúng tiến trình.

## 1. Gọi skill và cho thấy tài liệu nguồn (0:00–0:50)

Mở chat Codex trong repo. Dán lời yêu cầu sau và mở file `SKILL.md` trong editor để thấy hướng dẫn được áp dụng.

> Dùng skill eshop-perf-testing tại `hw05/skills/eshop-perf-testing/SKILL.md`. Đọc file này và hai references cần thiết. Chạy smoke trên EShop loopback với 2 VU, ramp 5 giây, tổng 30 giây qua login, search, detail, cart và checkout. Dựng backend và SQLite mới, tính đủ tài khoản, dùng script của skill và báo số mẫu, RPS, p95 từng label, lỗi, số đơn đối chiếu SQLite. Lưu kết quả vào thư mục mới. Dừng trước khi phát tải để mình mở Task Manager.

Cho agent hoặc terminal chạy:

```powershell
$skill = 'hw05/skills/eshop-perf-testing'
Get-Content "$skill/SKILL.md"
Get-Content "$skill/references/eshop.md"
```

## 2. Chuẩn bị Node, SQLite và 16 tài khoản (0:50–2:30)

Chạy trong PowerShell từ root repo. Dùng Java/JMeter đã chuẩn bị theo `hw05/Load_Plan.md`. Dựng backend từ revision đã đo. Có thể cài dependency trước khi quay và dùng thư mục dependency đã cài từ đúng lockfile nếu cần rút thời gian.

```powershell
$skill = 'hw05/skills/eshop-perf-testing'
$tools = (Resolve-Path '../.runtime/tools').Path
$java = (Get-ChildItem "$tools/temurin17-jre/*/bin/java.exe" | Select-Object -First 1).FullName
$jar = Join-Path $tools 'apache-jmeter-5.6.3/bin/ApacheJMeter.jar'
$run = (New-Item -ItemType Directory -Path ("../.runtime/T07/demo-" + (Get-Date -Format 'yyyyMMdd-HHmmss'))).FullName
$archive = Join-Path $run 'backend.tar'
git archive --format=tar -o $archive 85af3ba backend/server.js backend/database.js backend/package.json backend/package-lock.json
tar -xf $archive -C $run
$backend = Join-Path $run 'backend'
$server = Join-Path $backend 'server.js'
$text = [IO.File]::ReadAllText($server)
[IO.File]::WriteAllText($server, $text.Replace('app.listen(PORT, () => {', 'app.listen(PORT, "127.0.0.1", () => {'))
Push-Location $backend
npm.cmd ci
Pop-Location
$sut = Start-Process -FilePath 'node.exe' -ArgumentList 'server.js' -WorkingDirectory $backend -WindowStyle Hidden -PassThru
$sut.Id
(Invoke-RestMethod 'http://127.0.0.1:3000/api/products').Count
```

Trước khi khởi động Node, kiểm cổng 3000 trống. Chờ seed sẵn sàng, thấy 5 sản phẩm. Đọc SQLite ở lần đầu rồi lặp cùng kiểm tra sau khi provision.

```powershell
$db = Join-Path $backend 'database.sqlite'
@'
import sqlite3
import sys
from pathlib import Path

with sqlite3.connect(Path(sys.argv[1]).as_uri() + "?mode=ro", uri=True) as db:
    for sql in (
        "PRAGMA quick_check",
        "SELECT role, COUNT(*) FROM users GROUP BY role",
        "SELECT COUNT(*) FROM products",
        "SELECT COUNT(*) FROM orders",
        "SELECT COUNT(*) FROM users WHERE login_attempts IS NOT 0 OR locked_until IS NOT NULL",
    ):
        print(sql, db.execute(sql).fetchall())
'@ | python - $db

$csv = Join-Path $run 'credentials.csv'
python hw05/data/provision_load_users.py --accounts 16 --output $csv
```

Giải thích `2 × (ceil(30 / 4,6) + 1) = 16`, tài khoản cấp một lần mỗi vòng. Sau provision cần có 1 admin, 17 user (gồm 16 fixture), 5 sản phẩm, 0 đơn và 0 trạng thái khóa. Mở Task Manager tab Details, lọc bằng PID in từ `$sut.Id`.

## 3. Cho thấy JMeter CLI và Node cùng khung hình (2:30–3:30)

Báo agent bắt đầu, hoặc chạy lệnh sau trong terminal đang quay sau khi xác nhận trạng thái máy. Giữ cửa sổ Task Manager bên cạnh terminal trong lúc phát tải. Giữ kết quả riêng cho lượt demo.

```powershell
$out = Join-Path $run 'results'
$plan = 'hw05/plans/23120410_Load_20261119.jmx'
$properties = @{
    'hw05.load.threads' = 2
    'hw05.load.ramp_seconds' = 5
    'hw05.load.duration_seconds' = 30
    'hw05.credentials' = $csv
}
& "$skill/scripts/run_profile.ps1" -Plan $plan -ResultsDir $out -JavaExe $java -JMeterJar $jar -Properties $properties
```

Trỏ vào phiên bản Java/JMeter, dòng active threads và số lỗi. Nêu đây là smoke ngắn kiểm đủ workflow, có tải riêng với các lượt T04 đã đo.

## 4. Tính lại JTL và đọc kết quả (3:30–5:20)

```powershell
$line = Select-String -LiteralPath "$out/jmeter.log" -Pattern 'Starting ThreadGroup: 1' | Select-Object -First 1
$stamp = [datetime]::ParseExact($line.Line.Substring(0, 23), 'yyyy-MM-dd HH:mm:ss,fff', [cultureinfo]::InvariantCulture)
$t0 = ([datetimeoffset]$stamp).ToUnixTimeMilliseconds()
$profile = 'smoke-load-2vu-30s-ramp5'
python "$skill/scripts/analyze_jtl.py" --jtl "$out/run.jtl" --profile $profile --origin-ms $t0 --window 'ramp:0:5' --window 'steady:5:30' --json-out "$out/analysis.json"
Invoke-Item -LiteralPath "$out/dashboard/index.html"
```

Cho thấy đủ năm label trong bảng và giải thích ngắn RPS, p95, lỗi assertion. Mở dashboard để đối chiếu tổng số request và p95 từng label. So `order_id` và `authenticated_user_id` của checkout thành công trong JTL với `SELECT id, user_id FROM orders` trên DB của lượt quay. Dùng số thực tế của lượt quay. [Lượt smoke kiểm chứng của bài](../../evidence/t07/skill-run/Run.md)

## 5. Giải thích baseline và kết thúc (5:20–6:10)

Mở `references/analysis.md` và chỉ cờ `max(4 ms, 25% baseline)`. Một lượt smoke chưa đủ cho verdict regression. Khi có baseline cùng profile và ba lượt ứng viên hợp lệ, chiếu cách gọi sau:

```powershell
python "$skill/scripts/compare_baseline.py" --baseline "$baseline" --runs "$run1" "$run2" "$run3"
```

Chỉ đường dẫn JTL, dashboard và phân tích. Dừng đúng tiến trình Node thử nghiệm qua `Stop-Process -Id $sut.Id` nếu terminal của Vỹ đã khởi động nó và không còn dùng. Thu xong, kiểm video đủ lời thuyết minh và thấy rõ CLI cùng tài nguyên trong lúc tải chạy.
