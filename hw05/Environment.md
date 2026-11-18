# HW05 — Workflow và môi trường kiểm thử

## Workflow dùng chung

**Load, Stress và Spike** dùng cùng workflow trên REST API EShop với JMeter. Ngày đã chốt cho tên plan là `20261118`.

| Bước | Nhóm | Method | Đường dẫn | Body JSON | HTTP mong đợi và điều kiện kiểm tra |
| --- | --- | --- | --- | --- | --- |
| 1 | Auth-heavy | POST | `/api/login` | `email`, `password` | **200** với tài khoản hợp lệ và đang mở. Response có `token` và `user`; lấy JWT cho bước 4–5. |
| 2 | Read-heavy | GET | `/api/products` hoặc `/api/products?search=keyword` | — | **200**, mảng sản phẩm. Với fixture tìm kiếm đã chọn, kiểm tra mảng chứa ID mong đợi. |
| 3 | Read-heavy | GET | `/api/products/:id` | — | **200** với sản phẩm có sẵn. Kiểm tra ID, tên và giá; với ID chẵn, giá chi tiết là chuỗi. |
| 4 | Transactional | POST | `/api/cart` | `id`, `name`, `price`, `quantity` | **200**, `message = "Added to cart"`. Gửi `Authorization: Bearer <token>`. |
| 5 | Transactional | POST | `/api/checkout` | `total_amount`, `shipping_address` | **200**, `message = "Checkout successful"` và có `orderId`. Gửi `Authorization: Bearer <token>`. |

Body POST dùng `Content-Type: application/json`. Trong workflow, bước 3 dùng ID sản phẩm thuộc fixture đã đối chiếu với kết quả bước 2. Bước 4 dùng thông tin sản phẩm từ bước 3 và bước 5 dùng tổng tiền đã tính từ giá và số lượng. Các route đọc sản phẩm hoạt động khi gửi request không kèm token. Nguồn đối chiếu gồm [đặc tả API](../api_specification.md), [hướng dẫn cài đặt](../setup_guide.md) và [route backend](../backend/server.js).

## FR-02 và reset giữa các lượt

| Nguồn | Kết quả đối chiếu |
| --- | --- |
| Yêu cầu FR-02 | Khóa tạm **30 giây** sau **3 lần** đăng nhập sai liên tiếp. [FR-02](../README.md#fr-02-đăng-nhập--khóa-tài-khoản) |
| Đọc code | Điều kiện khóa là bộ đếm từ 3 trở lên, nhưng mỗi lần sai tăng **2**. Từ bộ đếm 0, code đạt ngưỡng ở lần sai thứ **2**. Code ghi thời hạn **180 giây**. Khi thời hạn còn hiệu lực, login trả **403**. Login đúng sau thời hạn đặt bộ đếm về 0 và xóa `locked_until`. Số lần sai được xác định qua đọc code. [Route login](../backend/server.js#L32-L66) |
| Kiểm tra runtime | Dùng một tài khoản tổng hợp, đặt sẵn trạng thái khóa 180 giây trong SQLite local. Cùng thông tin đăng nhập hợp lệ trả **403** khi đang khóa và **200** ở lần kiểm tra sau **180,378 giây**. SQLite sau login có `login_attempts = 0` và `locked_until = NULL`. [Bằng chứng smoke](evidence/t01-smoke.json) |

Hai cách reset đã kiểm tra trên bản local:

1. **Reset một tài khoản thử.** Dừng phát request, cập nhật `login_attempts = 0` và `locked_until = NULL` cho đúng ID trong cơ sở dữ liệu test. Đọc lại hai cột rồi thử đăng nhập hợp lệ. Smoke ghi **200** sau cập nhật.
2. **Reset toàn bộ trước lượt đo độc lập.** Dừng backend của bản thử và khởi động lại với `node server.js`. Khi nạp `database.js`, backend tạo lại bảng và dữ liệu seed. Sau lần restart kiểm chứng có **2 tài khoản seed**, **5 sản phẩm**, **0 đơn**, và **0 tài khoản seed còn bị khóa hoặc có bộ đếm khác 0**. Tài khoản tổng hợp cũ biến mất. Tạo lại tài khoản dùng trong CSV và kiểm tra fixture sẵn sàng trước khi bắt đầu đo. Việc dừng tiến trình cũng tạo lại giỏ trong bộ nhớ. [Khởi tạo DB](../backend/database.js) · [Bằng chứng smoke](evidence/t01-smoke.json)

## Ràng buộc ảnh hưởng tải

| Mục | Hành vi và hệ quả cho test plan |
| --- | --- |
| Tài khoản | Seed thực tế có **1 admin và 1 user**. Smoke đã tạo một tài khoản thử có role `user` bằng `POST /api/register`. T02 dùng endpoint này để chuẩn bị CSV chung, cấp một tài khoản mới cho mỗi vòng lặp trên toàn bộ lượt chạy. [Cách tính số tài khoản](Load_Plan.md#tính-số-tài-khoản) |
| Sản phẩm | `database.js` seed **5 sản phẩm**. Smoke xác nhận từ khóa `Galaxy` trả về ID `2`. Giá list của ID này là số, giá detail là chuỗi `"28000000"`. Khi tính tiền, chuyển kiểu một cách tường minh. |
| Tồn kho và đơn | Schema `products` không có trường tồn kho. Checkout ghi một hàng `orders` trạng thái `pending` với tổng tiền gửi lên. Route không kiểm tra hay trừ tồn kho và không đọc hoặc dọn giỏ. Các vòng lặp checkout làm tăng số dòng đơn. |
| Giỏ hàng | Mỗi lần thêm món ghi nối vào mảng trong RAM theo ID người dùng. Smoke xác nhận giỏ vẫn còn **1 món** sau checkout. Giỏ tích lũy qua các vòng lặp nếu backend tiếp tục chạy. |
| JWT | Token mới từ login có các claim `id`, `role`, `iat` và không có `exp`. Backend không đặt `expiresIn` khi ký, nên JWT login không có thời hạn hết hiệu lực do ứng dụng đặt. Bằng chứng ghi tên claim. |
| Rate limit | Khi đọc ứng dụng Express và manifest phụ thuộc, không thấy cấu hình rate limit tổng quát hoặc trên năm route này. T01 chạy tuần tự trên loopback, chưa đo throttling dưới tải hoặc qua proxy. Hành vi khóa theo tài khoản được ghi riêng ở trên. |

Nguồn kỹ thuật và bằng chứng. [Route backend](../backend/server.js) · [Schema và seed](../backend/database.js) · [Phụ thuộc backend](../backend/package.json) · [Bằng chứng smoke](evidence/t01-smoke.json)

## Smoke test và cấu hình máy

Smoke chạy ngày **18/11/2026**, từ **14:22:39 đến 14:25:41 (UTC+07)**, trên bản sao backend tại `HW05/.runtime/T01/backend` tính từ workspace `SoftwareTesting`. Bản sao nằm ngoài Git working tree, lấy từ commit `85af3ba` và chỉ đổi địa chỉ lắng nghe trong `server.js` sang **127.0.0.1**. Script Python khởi động backend bằng `node server.js`, gửi request tuần tự tại `http://127.0.0.1:3000` và dùng một tài khoản tổng hợp có role `user`.

T04 sẽ chạy JMeter vào cùng bản sao backend tại `http://127.0.0.1:3000`. Lệnh khởi động từ thư mục `SoftwareTesting` trên PowerShell:

```powershell
Set-Location -LiteralPath 'HW05/.runtime/T01/backend'
node server.js
```

### Dựng lại bản sao backend từ `85af3ba`

Từ thư mục `SoftwareTesting`, lấy các file nguồn và manifest từ commit gốc bằng Git. Bản sao ở `HW05/.runtime/T01/backend`, ngoài repo Git của bài nộp. SQLite được khởi tạo và seed khi chạy `node server.js`.

```powershell
$sut = (Resolve-Path -LiteralPath 'HW05/eshop-sut-HW05').Path
$runtime = (New-Item -ItemType Directory -Path 'HW05/.runtime/T01' -Force).FullName
$archive = Join-Path $runtime 'backend-85af3ba.tar'

git -C $sut archive --format=tar -o $archive 85af3ba backend/server.js backend/database.js backend/package.json backend/package-lock.json
tar -xf $archive -C $runtime

$server = Join-Path $runtime 'backend/server.js'
$source = [System.IO.File]::ReadAllText($server)
$source = $source.Replace('app.listen(PORT, () => {', 'app.listen(PORT, "127.0.0.1", () => {')
[System.IO.File]::WriteAllText($server, $source)

Set-Location -LiteralPath (Join-Path $runtime 'backend')
npm ci
```

### Kết quả smoke

| Request chính | HTTP thực tế | Kiểm tra |
| --- | ---: | --- |
| `POST /api/login` | 200 | JWT có ID tài khoản thử và role `user`. |
| `GET /api/products` | 200 | Có 5 sản phẩm, chọn ID 2. |
| `GET /api/products/2` | 200 | ID, tên và giá khớp list sau khi chuyển kiểu giá. |
| `POST /api/cart` | 200 | Thông báo đúng. Sau khi thêm, đọc lại giỏ thấy một món khớp payload. |
| `POST /api/checkout` | 200 | Trả `orderId = 1`. SQLite có đơn `pending`, thuộc tài khoản thử và tổng tiền 28.000.000. |

Kiểm tra thêm `GET /api/products?search=Galaxy` trả **200** và đúng một kết quả, ID 2. Chi tiết assertion và hai lần reset nằm trong [bằng chứng smoke](evidence/t01-smoke.json).

### Cấu hình máy

| Hạng mục | Thông tin thu được |
| --- | --- |
| Hostname Windows lúc chạy smoke | `GOYOONJUNG` |
| Hostname dùng khi quay video demo | `tranquocvy` |
| Model máy | Dell G15 5520 |
| CPU | Intel Core i7-12700H, 14 lõi, 20 bộ xử lý logic |
| RAM | 15,69 GiB theo `Win32_ComputerSystem` |
| Hệ điều hành | Windows 11 Home 64-bit, build 26300 |
| Lưu trữ workspace | Phân vùng D: NTFS, dung lượng 170,66 GiB, còn trống 45,52 GiB tại thời điểm kiểm tra, trên SSD NVMe SSSTC 512 GB |
| Backend và cơ sở dữ liệu | Node.js 24.14.0, npm 11.21.0, driver `sqlite3` 6.0.1, SQLite engine 3.52.0, journal mode `delete` |
| Công cụ tạo tải | Apache JMeter 5.6.3 chạy plan với Eclipse Temurin JRE 17.0.21+9. Ở T01, `jmeter.bat -v` chạy được với Java 25, nhưng pilot T02 trên Java 25 dừng khi Groovy báo `Unsupported class file major version 69`. Bản ZIP JMeter đã được kiểm tra SHA-512 và chữ ký Apache. [Chuẩn bị công cụ và kết quả pilot](Load_Plan.md) |

Hostname trong bảng cấu hình được lấy từ Windows tại thời điểm chạy smoke T01. Hostname dùng khi quay video demo được ghi riêng để đối chiếu với bản ghi hình. Cấu hình máy lấy bằng `Get-CimInstance`, `Get-Partition` và `Get-Disk`.

Ở các lượt đo dự kiến, JMeter và SUT dùng chung máy nên CPU, RAM và I/O mà chúng sử dụng có thể ảnh hưởng lẫn nhau. SQLite dùng một file, và cùng một workflow có ít nhất hai ghi DB, ở login thành công và checkout. Giỏ được giữ trong bộ nhớ của backend. Chưa đo tranh chấp ghi, tài nguyên dưới tải, p95 hoặc throughput tại T01.
