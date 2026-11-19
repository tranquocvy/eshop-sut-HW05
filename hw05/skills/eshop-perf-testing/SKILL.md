---
name: eshop-perf-testing
description: Run one local EShop performance profile (Load, Stress, Spike or Endurance) with JMeter, or analyze existing CSV JTL files into RPS, p95 by label, phase metrics and baseline verdicts. Use for a smoke run covering login through checkout, performance evidence, or regression review of this API workflow.
---

# EShop performance testing

1. **Chọn chế độ.** Nếu đã có JTL, đọc log trước và bắt đầu ở bước 4. Nếu cần phát tải, chọn một JMX, xác định revision backend, host, profile và mức tải được yêu cầu. Lấy workflow, tham số và điều kiện dừng từ [SUT và profile](references/eshop.md). Dùng bản EShop thử nghiệm trên loopback cho các plan HW05.
2. **Chuẩn bị lượt độc lập.** Từ repo EShop, tạo thư mục backend mới ngoài working tree theo `hw05/Environment.md`, dùng lockfile đúng revision, rồi khởi động Node và chờ SQLite tạo schema/seed. Kiểm trước provision có hai tài khoản seed, năm sản phẩm, 0 đơn và 0 trạng thái khóa/bộ đếm. Giỏ trong RAM được dọn khi restart. Mỗi lượt đo, kể cả đo lại hoặc sau smoke, bắt đầu từ backend và DB sạch. Dùng Temurin **17** và JMeter **5.6.3** theo `hw05/Load_Plan.md`. Java 25 từng báo Groovy `Unsupported class file major version 69`, JMeter trả 0 nhưng JTL có 0 HTTP sample.
3. **Cấp tài khoản và chạy.** Tính ngân sách theo T02 là `sum(VU × (ceil(D/W) + 1))` cho từng nhóm. `D` gồm ramp, bỏ startup delay. `W` là 4,6 s cho think-time 1–2 s hoặc 1,38 s cho 300–600 ms theo giả định trong [SUT và profile](references/eshop.md). Chọn đủ dòng, provision bằng `hw05/data/provision_load_users.py --accounts N` và kiểm lại SQLite. Khi provision một phần, dùng `--output` đến CSV mới ngoài repo và truyền đường dẫn tuyệt đối bằng property `hw05.credentials`. Plan dùng mỗi dòng một lần và dừng VU khi EOF. Chạy JMeter non-GUI bằng [run_profile.ps1](scripts/run_profile.ps1), với thư mục kết quả mới và heap tối đa 384 MiB. Theo dõi cả Node, JMeter và máy, đặc biệt khi cùng host. Wrapper chạy và xuất dashboard sau lượt. Vận hành theo ngưỡng tài nguyên và theo dõi log trong lúc phát tải.

   ```powershell
   $skill = 'hw05/skills/eshop-perf-testing'
   & "$skill/scripts/run_profile.ps1" -Plan $plan -ResultsDir $out -JavaExe $java -JMeterJar $jar -Properties $properties
   ```

   `$properties` có thể là `@{}` nếu dùng đúng profile mặc định với đủ CSV. Kiểm log thread, EOF, số mẫu và assertion. Đối chiếu các checkout thành công với SQLite khi phiên chạy lưu `order_id`. Tách lỗi HTTP 5xx/timeout khỏi lỗi assertion, credentials, lockout hoặc dụng cụ. Lưu lượt dở dang và lý do.
4. **Tính lại từ JTL.** Dùng [analyze_jtl.py](scripts/analyze_jtl.py) với Python 3.10+. Lấy mốc Thread Group đầu từ log khi chia theo lịch tải. Cột `allThreads` giúp đối chiếu VU thực ở mỗi pha. Nếu chỉ có JTL, ghi rõ các cửa sổ tương đối với sample đầu. Đối chiếu tổng số mẫu và p95 từng label với `dashboard/statistics.json` khi có dashboard.

   ```powershell
   python "$skill/scripts/analyze_jtl.py" --jtl "$out/run.jtl" --profile $profile --origin-ms $t0 --window 'steady:20:50' --json-out "$out/analysis.json"
   ```

   Thay cửa sổ ví dụ bằng lịch thực tế. Có thể truyền nhiều `--window`. Định nghĩa RPS, nội suy và lỗi nằm trong [quy ước phân tích](references/analysis.md).
5. **Đối chiếu và báo cáo.** So ba lượt độc lập với baseline tương thích theo [quy ước phân tích](references/analysis.md), bằng [compare_baseline.py](scripts/compare_baseline.py). Chỉ gọi mức đã quan sát là điểm bão hòa hoặc mức ổn định nếu dữ liệu đủ theo tiêu chí. Ghi revision, profile, VU thực, lượt hợp lệ, số mẫu, p95/RPS/lỗi theo label và pha, tài nguyên, lỗi chức năng, giới hạn và link JTL/dashboard. Khi thiếu baseline hoặc thiếu mẫu, ghi trạng thái cảnh báo và lý do. [Kịch bản demo](DEMO.md)
