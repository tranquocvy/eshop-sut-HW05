# SUT và profile HW05

Nguồn trong repo là `hw05/Environment.md`, `Load_Plan.md`, `Stress_Spike_Plans.md`, `T04_Execution.md` và `T05_Endurance.md`. Dùng revision SUT thực tế để xác minh các hằng số và schema khi chúng thay đổi.

| Label | Workflow | Dữ liệu và kiểm tra |
| --- | --- | --- |
| 01 Login | `POST /api/login` | 200, lấy JWT và ID người dùng từ JSON. |
| 02 Search products | `GET /api/products?search=...` | 200, tìm ID của fixture trong response. |
| 03 Product detail | `GET /api/products/:id` | 200, kiểm ID, tên, giá. |
| 04 Add to cart | `POST /api/cart` | 200 và thông báo thêm giỏ. Dùng JWT và sản phẩm tương ứng. |
| 05 Checkout | `POST /api/checkout` | 200 và `orderId`, dùng JWT, tổng tiền và địa chỉ fixture. |

Express dùng SQLite file. Giỏ nằm trong Node RAM và đơn tích lũy trong SQLite. JWT của bản `85af3ba` không có `exp`. Checkout chỉ INSERT đơn và không dọn giỏ. Bản code đã kiểm ở T01 khóa sau hai lần sai trong 180 s, còn đặc tả FR-02 ghi ba lần và 30 s. Dùng tài khoản giả mới mỗi vòng để tránh chia bộ đếm. Mọi profile đo dùng đăng nhập hợp lệ.

## Chuẩn bị và mức tải

Đọc SQLite của bản runtime trước khi provision để xác nhận seed. Sau provision và trước mỗi lượt, kiểm số tài khoản fixture bằng số dòng đã cấp, số đơn = 0, `login_attempts IS 0`, `locked_until IS NULL` với dữ liệu dự kiến, cùng `PRAGMA quick_check = ok`. Đối chiếu ID sản phẩm đã seed với CSV. Dùng script provision của repo với loopback `127.0.0.1:3000`.

Ngân sách T02 giả định tối đa 10% vòng bị bỏ từ request đầu. Bỏ thời gian HTTP, `W = 0,9 × 5 × min_think + 0,1 × min_think`. Tính lại nếu tăng tải, giảm timer hoặc vòng lỗi nhiều hơn. CSV repo có 7.500 dòng. Provision đủ số cần, chạy theo đúng tập credentials vừa đăng ký.

| Profile đã đo | Lịch và think-time | Ngân sách dự trù |
| --- | --- | ---: |
| Smoke demo | 2 VU, ramp 5 s, tổng 30 s, 1–2 s | 16 |
| Load T04 | 6 VU, ramp 30 s, tổng 150 s, 1–2 s | 204 |
| Stress T04 | 24 → 48 → 96 → 144 VU, 4 bậc 30 s, tổng 120 s, 300–600 ms | 6.984 |
| Spike T04 | 6 VU nền, thêm 138 tại giây 60, đỉnh 20 s rồi về nền, tổng 150 s, 300–600 ms | 2.868 |
| Endurance T05 | 32 VU, ramp 20 s và giữ 900 s, 1–2 s | 6.432, đã provision 7.500 |

Dùng ba property `hw05.load.threads=2`, `hw05.load.ramp_seconds=5`, `hw05.load.duration_seconds=30` cho smoke. Các profile lớn dùng JMX đã chọn hoặc override theo hướng dẫn riêng của profile.

## Theo dõi khi chạy và tiêu chí từ bài

- Trên máy dùng chung, 144 VU là trần thử nghiệm đã chọn vì RAM, chưa xác lập điểm bão hòa. Kiểm RAM còn đủ trước khi phát tải. T04/T05 dừng khi CPU máy ≥90% hoặc RAM khả dụng <1.536 MiB trong 10 giây liên tiếp, backend thoát, EOF sớm hoặc fixture hợp lệ bị lỗi. Hai pilot Endurance đầu đã dừng vì RAM. Khi dùng cùng ngưỡng trên lượt mới, theo dõi chủ động trong terminal khác. Wrapper không tự giám sát.
- Stress T04 còn dừng nếu hai cửa sổ 7 s đủ mẫu ở cùng bậc đều có lỗi ≥5%, hoặc p95 một label ≥max(75 ms, 3 × p95 label ở bậc 24 VU). Lấy các cửa sổ sau ramp theo `Stress_Spike_Plans.md`. Tiêu chí dừng này từng dùng nearest rank, khác quy ước nội suy của dashboard và script phân tích.
- Spike T04 so nền và các cửa sổ 30 s từ 5 s sau khi thread Burst cuối dừng. Hồi phục khi từng label đạt p95 ≤1,2 × nền, lỗi ≤ nền và mỗi label đủ ít nhất 10 sample trong cửa sổ và nền.
- Endurance T05 so năm cửa sổ 180 s sau ramp. p95 label được tăng tối đa max(3 ms, 25% p95 cửa sổ đầu), RPS ≥90% cửa sổ đầu, lỗi ≤0,5% mỗi cửa sổ. Working set Node dùng ≤2 MiB/phút trong 12 phút cuối. Báo cả độ dốc toàn 15 phút để tham khảo. Số đo đã duyệt là 21,26 req/s ở 32 VU trong 15 phút và working set Node cao nhất 64,21 MiB, giới hạn ở máy và profile đã thử.

Để dừng sạch, xác nhận console hiện cổng UDP của chính lượt CLI này, sau đó từ terminal khác dùng cùng Java/JAR và cổng đã truyền cho wrapper.

```powershell
& $java -cp $jar org.apache.jmeter.util.ShutdownClient Shutdown 4445
```

Lưu lỗi và output dở dang trước khi dựng thử lại.
