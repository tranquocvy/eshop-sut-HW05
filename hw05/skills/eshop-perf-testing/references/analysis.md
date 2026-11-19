# Quy ước số liệu và baseline

`analyze_jtl.py` nhận CSV JTL chỉ gồm HTTP sample. Cột bắt buộc là `timeStamp` dạng epoch ms lúc gửi, `elapsed`, `label`, `responseCode`, `success`. Nếu có `allThreads`, bảng in thêm khoảng VU quan sát. RPS toàn lượt và RPS mỗi label dùng khoảng từ sample đầu bắt đầu tới response cuối hoàn tất của chính nhóm, như dashboard HW05. RPS trong cửa sổ dùng số sample bắt đầu trong `[a,b)` chia cho `b-a`. p95 nội suy tại hạng `0,95 × (n+1)` sau khi sắp `elapsed` và chặn hai đầu. Tỷ lệ lỗi dựa trên `success=false`, kể cả assertion lỗi khi HTTP 200. Cửa sổ rỗng hoặc thời lượng bằng 0 hiển thị chỉ số không xác định khi không tính được.

Nếu lấy mốc từ log, tìm `Starting ThreadGroup: 1` và chuyển timestamp log theo múi giờ của máy sang epoch ms. Không nhầm mốc với giờ phát lệnh Java. Gợi ý khi khớp lịch T04/T05 là Stress `[94,108)` ở 144 VU, Spike dùng mốc thread thật của Burst, Endurance dùng `[20,200)` tới `[740,920)`. Xem báo cáo gốc để chọn đúng rule hoặc tái tạo kết quả.

## So baseline T07A

Dùng 5 lượt hợp lệ trên `main` với cùng runner và workload để lấy trung vị p95 từng label/khoảng đo. Gắn profile ID với revision của plan/fixture, lịch tải, công cụ và môi trường. Ghi SHA SUT mốc, năm lượt nguồn và cấu hình runner trong metadata của baseline. Đổi profile hoặc runner thì hiệu chỉnh lại. Thiết kế T07A dùng ba lượt ứng viên, đủ 100 sample trở lên mỗi label trong mỗi khoảng, có assertion và kiểm fixture. Chỉ cấp ba JSON riêng từ ba lượt đã kiểm độc lập.

Baseline JSON có `profile`, `scopes` như dưới. Số trong ví dụ chỉ minh họa. Mỗi scope liệt kê đủ label và p95. `rps` tùy chọn để cảnh báo nếu một lượt thấp hơn 90% mốc. Scope cửa sổ dùng `window_s: [start,end]` và `origin_kind: "thread-group"` hoặc `"first-sample"`. Scope toàn lượt dùng `window_s: null`.

```json
{
  "profile": "load-6vu-150s-local-v1",
  "scopes": {
    "full": {
      "window_s": null,
      "p95_ms": {
        "01 Login": 4,
        "02 Search products": 3,
        "03 Product detail": 3,
        "04 Add to cart": 2,
        "05 Checkout": 10
      },
      "rps": 3.7
    }
  }
}
```

```powershell
python "$skill/scripts/compare_baseline.py" --baseline "$baseline" --runs "$run1" "$run2" "$run3"
```

- **PASS / exit 0** khi cả ba lượt hợp lệ và không lượt nào vượt `B + max(4 ms, 25% × B)` ở một label/khoảng đo.
- **WARN / exit 2** khi chỉ một lượt vượt ở một label/khoảng, thiếu lượt/mẫu, profile hoặc scope lệch, có lỗi sample cần điều tra, hoặc RPS giảm theo guard. Nếu thiếu baseline, báo chưa đủ dữ liệu so sánh. Xem thông báo của script để phân biệt input không hợp lệ (exit 3).
- **FAIL / exit 1** khi trung vị p95 của ba lượt vượt ngưỡng cùng label/khoảng. Xử lý chức năng hoặc fixture lỗi riêng và lưu bằng chứng, sau đó mới xác định có phép so p95 hợp lệ.

Dung sai **4 ms hoặc 25%, lấy mức lớn hơn** dựa trên biên độ tối đa 3,55 ms giữa hai lượt Load, 1 ms giữa ba lượt Stress toàn lượt, 3 ms ở bậc 144 VU và 1 ms giữa năm cửa sổ Endurance. Đây là đề xuất từ máy local ở T07A, chưa kiểm chứng trên CI. Smoke 2 VU 30 s có ích để kiểm workflow và đường chạy script. Chỉ so regression khi có baseline cùng cấu hình và đủ mẫu.
