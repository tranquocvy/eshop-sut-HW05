# HW05 — T02 · Dữ liệu CSV và Load plan

## 1. Tham số Load

Plan [`23120410_Load_20261118.jmx`](plans/23120410_Load_20261118.jmx) chạy workflow năm request trên bản EShop local tại `127.0.0.1:3000`.

| Tham số | Load mặc định | Căn cứ thiết kế |
| --- | --- | --- |
| Thread | 6 VU | Mức khởi đầu cho máy dùng chung giữa JMeter và EShop. Mỗi vòng dùng một tài khoản mới để cô lập bộ đếm đăng nhập và giỏ. |
| Ramp-up | 30 giây | Khởi động mỗi VU cách nhau khoảng 5 giây để hạn chế đăng nhập và ghi SQLite dồn cùng lúc. |
| Thời lượng | 150 giây tính cả ramp-up | Dành 120 giây theo cấu hình sau ramp-up để lặp workflow. Giới hạn thời gian tích lũy giỏ trong RAM và ghi đơn vào SQLite trong lượt Load. |
| Think-time | Uniform Random Timer, 1–2 giây | Jitter 1.000 ms trên mức cố định 1.000 ms trước mỗi HTTP request. |

Đây là mức khởi đầu của Load. Vỹ sẽ điều chỉnh ở T04 theo kết quả đo thực tế. Mỗi vòng gọi login để giữ bước auth-heavy, dù JWT của SUT không có `exp`. Login thành công cập nhật bộ đếm trong SQLite và checkout ghi đơn. Thread Group dùng **Start Next Thread Loop**. JMeter ghi sample lỗi, bỏ các request phụ thuộc còn lại của vòng và giữ VU cho vòng tiếp theo. Mỗi vòng bắt đầu bằng login mới và xóa các giá trị correlation cũ. [Môi trường T01](Environment.md) · [JMeter Thread Group](https://jmeter.apache.org/usermanual/component_reference.html#Thread_Group) · [Uniform Random Timer](https://jmeter.apache.org/usermanual/component_reference.html#Uniform_Random_Timer)

## 2. FR-01 và dữ liệu CSV

Đặc tả FR-01 yêu cầu họ tên, email đúng định dạng và duy nhất, mật khẩu ít nhất 8 ký tự có chữ hoa, chữ thường, số, ký tự đặc biệt và xác nhận mật khẩu ở form. API `POST /api/register` nhận `name`, `email`, `password` và trả ID. Script kiểm tra tên, email duy nhất và quy tắc mật khẩu trước khi gửi. Trường xác nhận mật khẩu thuộc form theo đặc tả. [FR-01](../README.md#fr-01-đăng-ký-tài-khoản) · [Đặc tả API](../api_specification.md) · [Route register](../backend/server.js#L20-L30) · [Schema users](../backend/database.js#L50-L62)

| CSV | Vai trò |
| --- | --- |
| [`load-credentials.csv`](data/load-credentials.csv) | Nguồn mặc định của plan, gồm 1.250 tên, email miền `hw05.example.test` và mật khẩu giả dùng cho EShop local. JMX tìm file ở `../data/load-credentials.csv` tính từ thư mục `plans`. |
| `credentials.csv` | CSV tùy chọn do [script provision](data/provision_load_users.py) ghi ngoài repo bằng `--output`. File giới hạn ở các tài khoản đã đăng ký và bổ sung ID do API trả về. JMeter dùng file này khi có `-Jhw05.credentials`. |
| [`load-products.csv`](data/load-products.csv) | Cặp `fixture_product_id,search_keyword` cho 5 sản phẩm seed. |
| [`load-order-payloads.csv`](data/load-order-payloads.csv) | Cặp `quantity,shipping_address` tổng hợp. Giá và tên lấy từ response chi tiết. Tổng đơn là giá nhân số lượng. |

Ba **CSV Data Set Config** chuẩn đọc UTF-8 và lấy tên cột từ header. Config credentials dùng **All threads**. Ở đầu mỗi vòng, JMeter cấp dòng kế tiếp từ một con trỏ chung, nên mỗi tài khoản chỉ được cấp một lần trong cả lượt. Config đặt **Recycle on EOF = false** và **Stop thread on EOF = true**. VU gặp EOF khi bắt đầu vòng tiếp theo sẽ dừng. EOF trước hết thời lượng là dấu hiệu lượt chạy thiếu dữ liệu và không đạt mức tải cấu hình. Hai config sản phẩm và payload vẫn dùng **Current thread** và được phép quay về đầu file. [JMeter CSV Data Set Config](https://jmeter.apache.org/usermanual/component_reference.html#CSV_Data_Set_Config)

### Tính số tài khoản

Pilot 03 cung cấp 6 khoảng thời gian từ lúc gửi login đến lúc gửi login kế tiếp của cùng VU, với điều kiện vòng trước đã checkout. Trung vị là **7,852 giây/vòng**, khoảng **7,439–8,969 giây**. Cách đo này bao gồm các request và phần think-time giữa hai mốc. [Raw JTL pilot 03 dùng để tính số tài khoản](evidence/t02-sizing-pilot.jtl)

- **Giả định soak dài nhất:** 6 VU, 15 phút tải ổn định và tối đa 30 giây ramp-up. Lấy `D = 930` giây cho mọi VU để tính cả ramp-up. Theo trung vị pilot, cần khoảng `6 × (ceil(930 / 7,852) + 1) = 720` dòng, gồm một dòng dự phòng biên thời gian cho mỗi VU.
- **Dự phòng vòng chạy nhanh và vòng lỗi:** một vòng đủ 5 request có ít nhất 5 giây think-time. Vòng bị bỏ từ request đầu vẫn có ít nhất 1 giây. Giả định tối đa 10% vòng bị cắt ngắn và bỏ qua thời gian HTTP để lấy cận lập kế hoạch `0,9 × 5 + 0,1 × 1 = 4,6` giây/vòng. Số dòng dự trù là `6 × (ceil(930 / 4,6) + 1) = 1.224`, làm tròn lên **1.250 tài khoản tổng hợp**.

Áp dụng cùng cách tính, Load mặc định 6 VU trong 150 giây cần **204** dòng, còn pilot 3 VU trong 25 giây cần **21** dòng theo giả định trên. Số 1.250 dành cho soak 15 phút theo giả định 6 VU. Nếu tăng VU, đổi think-time hoặc tỷ lệ vòng bị cắt ngắn vượt giả định, cần tính lại số dòng. Script đăng ký số dòng yêu cầu qua `--accounts` sau khi backend T01 khởi động lại và seed lại DB.

Kiểm tra lại trên pilot 05 với CSV dùng một lần cho trung vị **7,6355 giây/vòng** từ 6 khoảng login, tương ứng khoảng **738 dòng** theo cách ước lượng trên. Số dòng dự trù vẫn là 1.250 theo cận think-time. [JTL pilot 05](evidence/t02-pilot.jtl)

## 3. Assertion, correlation và listener

| Request | Assertion nội dung ngoài HTTP 200 | Correlation |
| --- | --- | --- |
| `POST /api/login` | Thông báo thành công, role `user`, email khớp dòng CSV, ID dương và token có dạng JWT. Nếu CSV có `expected_user_id`, ID trả về phải khớp ID đã đăng ký. | Trích `$.token` để gửi Bearer ở giỏ và checkout. |
| `GET /api/products?search=…` | Response chứa sản phẩm theo ID fixture, với tên hợp lệ. | Trích ID khớp từ mảng response cho đường dẫn detail. |
| `GET /api/products/:id` | ID và tên khớp kết quả tìm kiếm. Giá dạng số hoặc chuỗi số được chuyển thành số nguyên dương. | Tạo JSON giỏ và đơn từ detail, số lượng và địa chỉ trong CSV. |
| `POST /api/cart` | Thông báo `Added to cart`. | Dùng Bearer từ login. |
| `POST /api/checkout` | Thông báo `Checkout successful` và `orderId` là số nguyên dương. | Trích `$.orderId` để đối chiếu SQLite trong pilot. |

Listener của Load là **Summary Report**. View này tổng hợp theo label với ít bộ nhớ hơn Aggregate Report. Pilot chạy non-GUI, ghi JTL CSV qua `-l`. Cấu hình JTL không lưu body và header. Groovy dùng cho tạo JSON và assertion nội dung. Việc đọc CSV do các config chuẩn của JMeter thực hiện. [Summary Report](https://jmeter.apache.org/usermanual/component_reference.html#Summary_Report)

## 4. Bản AI đầu và chỉnh sửa

Bản đầu của JMX, ba CSV và script provision được lưu trước khi chạy tại `HW05/.runtime/T02/initial/hw05`. Lệnh pilot ban đầu chọn Java 25 dựa trên kết quả `jmeter.bat -v` ở T01. Bước kiểm phiên bản chưa kiểm chứng khả năng biên dịch Groovy trong plan. Pilot đầu đăng ký được 6 tài khoản, sau đó cả 3 thread dừng ở bước khởi tạo Groovy với lỗi `Unsupported class file major version 69`. Dù tiến trình JMeter trả mã 0, JTL có **0 HTTP sample**. Log gốc của lượt này được lưu tại `HW05/.runtime/T02/pilot-01`.

JMeter 5.6.3 được chạy lại với **Eclipse Temurin JRE 17.0.21+9** trong runtime riêng. File ZIP của JRE được kiểm tra SHA-256. Bản JMX đã ghi phiên bản Java đã dùng và thuộc tính trỏ tới CSV credentials. [Eclipse Temurin 17](https://adoptium.net/temurin/releases/?version=17)

Bản trước review dùng Groovy để đọc CSV và `stopthread` khi lỗi. Theo góp ý của Vỹ, plan chuyển sang ba CSV Data Set Config và **Start Next Thread Loop**. Bản sửa tiếp theo thay cách gán tài khoản cố định theo VU bằng CSV chung, dùng mỗi dòng một lần. Ở lượt duyệt, đường dẫn mặc định được chuyển sang CSV tổng hợp trong repo.

## 5. Kết quả pilot

Các pilot chạy ngày 18/11/2026. Mỗi lượt dùng backend T01 mới khởi động để DB seed lại.

| Lượt và giờ bắt đầu (UTC+07) | Cấu hình | HTTP sample | Kết quả |
| --- | --- | ---: | --- |
| Pilot 01, 15:44:27 | Java 25, 3 VU, 6 s ramp-up, 25 s | 0 | Dừng khi biên dịch Groovy. |
| Pilot 02, 15:46:56 | Java 17, 3 VU, 6 s ramp-up, 25 s | 42 | Bản trước review. 42 sample đạt, 7 checkout. |
| Pilot 03, 15:58:47 | Java 17, 3 VU, 6 s ramp-up, 25 s | 41 | CSV chuẩn với tài khoản cố định theo VU. 41 sample đạt, 6 checkout. |
| Pilot 04, 16:00:10 | Java 17, 1 VU, 1 s ramp-up, 18 s | 12 | Kiểm tra chuyển vòng với tài khoản cố định. 1 lỗi assertion chủ đích, 2 checkout sau lỗi. |
| Pilot 05, 16:20:59 | Java 17, 3 VU, 6 s ramp-up, 25 s | 44 | CSV chung dùng một lần. 44 sample đạt, 8 checkout và 0 lần dừng do EOF. |
| Pilot 06, 16:22:17 | Java 17, 1 VU, 2 dòng credentials, tối đa 18 s | 7 | Kiểm tra chuyển vòng và EOF. Bộ tổng hợp gặp lỗi giải mã log Windows. Đã sửa cách đọc và đối chiếu lại JTL, log JMeter và SQLite gốc. |
| Pilot 07, 16:23:22 | Java 17, 1 VU, 2 dòng credentials, tối đa 18 s | 7 | Xác nhận 1 lỗi assertion chủ đích, 1 checkout sau lỗi và 1 lần dừng do EOF. |
| Pilot 08, 16:30:24 | Java 17, 3 VU, 6 s ramp-up, 25 s | 47 | Dùng CSV trong repo theo mặc định. 47 sample đạt, 11 lần login với ID khác nhau và 8 checkout. |
| Pilot 09, 16:30:54 | Java 17, 1 VU, CSV thay thế có 2 dòng, tối đa 18 s | 7 | 1 lỗi assertion chủ đích, 1 checkout sau lỗi và 1 lần dừng do EOF. |

Pilot 05 đăng ký đủ **1.250 tài khoản** trước khi phát tải và xác nhận số tài khoản trong SQLite. JTL có 9 login với **9 ID khác nhau**. Các request trong cùng vòng giữ cùng ID. Cả 8 đơn khớp SQLite theo ID, tài khoản, tổng tiền, trạng thái và địa chỉ CSV. [JTL pilot 05](evidence/t02-pilot.jtl)

Pilot 08 chạy từ thư mục kết quả bên ngoài repo và JMeter không nhận `hw05.credentials`. Nó tìm được CSV theo đường dẫn tương đối với JMX, đăng nhập bằng các tài khoản đã đăng ký và xác minh cả 8 đơn trong SQLite. [JTL pilot dùng CSV mặc định](evidence/t02-default-credentials.jtl)

Pilot 09 lặp lại phép kiểm tra của pilot 07 trên bản plan cuối và dùng CSV credentials thay thế có 2 dòng. Search ở vòng đầu trả HTTP 200 nhưng lỗi assertion vì từ khóa thử không khớp sản phẩm. Cùng VU bắt đầu lại từ login bằng tài khoản thứ hai, hoàn tất checkout, rồi dừng tại EOF trước khi phát login thứ ba. Log JMeter ghi `stopThread:true, recycle:false`. [JTL pilot 09](evidence/t02-next-loop.jtl) · [Tổng hợp các lượt và dòng log EOF](evidence/t02-pilot.json)

## 6. Tải và đặt công cụ

Tải bản ZIP [Apache JMeter 5.6.3](https://archive.apache.org/dist/jmeter/binaries/apache-jmeter-5.6.3.zip) và bản ZIP [Eclipse Temurin JRE 17.0.21+9 cho Windows x64](https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.21%2B9/OpenJDK17U-jre_x64_windows_hotspot_17.0.21_9.zip). Lưu hai ZIP trong `HW05/.runtime/tools` rồi giải nén từ thư mục `SoftwareTesting`:

```powershell
$toolRoot = (Resolve-Path -LiteralPath 'HW05/.runtime/tools').Path
Expand-Archive -LiteralPath (Join-Path $toolRoot 'apache-jmeter-5.6.3.zip') -DestinationPath $toolRoot
Expand-Archive -LiteralPath (Join-Path $toolRoot 'OpenJDK17U-jre_x64_windows_hotspot_17.0.21_9.zip') -DestinationPath (Join-Path $toolRoot 'temurin17-jre')
```

Sau giải nén, công cụ nằm trong `apache-jmeter-5.6.3/bin` và `temurin17-jre/jdk-17.0.21+9-jre/bin`, tính từ `HW05/.runtime/tools`. Lệnh dưới đây gọi trực tiếp `java.exe` 17, nên không cần đổi Java mặc định của máy.

## 7. Chạy lại pilot

Khởi động EShop theo [môi trường T01](Environment.md) ở terminal riêng. Backend seed hai tài khoản ban đầu, nên script cần đăng ký tài khoản thử trước khi chạy. Ví dụ dưới đây đăng ký 21 tài khoản cho pilot 3 VU và để JMeter dùng CSV mặc định trong repo. Với cấu hình Load mặc định, có thể đăng ký toàn bộ 1.250 dòng rồi chạy plan với thông số mặc định. Nếu chỉ muốn đăng ký và sử dụng một phần CSV có ranh giới EOF tương ứng, dùng `--output` để xuất file và truyền `-Jhw05.credentials` chỉ tới file đó.

Từ thư mục `SoftwareTesting`, chạy pilot với JMeter 5.6.3 và JRE 17 đã giải nén:

```powershell
$suite = (Resolve-Path -LiteralPath 'HW05/eshop-sut-HW05/hw05').Path
$toolRoot = (Resolve-Path -LiteralPath 'HW05/.runtime/tools').Path
$runDir = (New-Item -ItemType Directory -Path ('HW05/.runtime/T02/manual-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))).FullName
$provision = Join-Path $suite 'data/provision_load_users.py'
python $provision --accounts 21
if ($LASTEXITCODE -ne 0) { throw 'Provisioning failed' }

$java = Join-Path $toolRoot 'temurin17-jre/jdk-17.0.21+9-jre/bin/java.exe'
$jar = Join-Path $toolRoot 'apache-jmeter-5.6.3/bin/ApacheJMeter.jar'
$plan = Join-Path $suite 'plans/23120410_Load_20261118.jmx'
$options = @(
  '-n', '-t', $plan, '-l', (Join-Path $runDir 'pilot.jtl'), '-j', (Join-Path $runDir 'jmeter.log'),
  '-Jhw05.load.threads=3',
  '-Jhw05.load.ramp_seconds=6', '-Jhw05.load.duration_seconds=25',
  '-Jsample_variables=fixture_product_id,expected_user_id,authenticated_user_id,order_id',
  '-Jjmeterengine.nongui.port=0', '-Jjmeter.save.saveservice.output_format=csv',
  '-Jjmeter.save.saveservice.response_data=false', '-Jjmeter.save.saveservice.response_data.on_error=false',
  '-Jjmeter.save.saveservice.requestHeaders=false', '-Jjmeter.save.saveservice.responseHeaders=false',
  '-Jjmeter.save.saveservice.samplerData=false'
)
& $java -jar $jar @options
```
