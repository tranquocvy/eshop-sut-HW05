# HW05 Prompt Log

Phạm vi: Đọc đề và chuẩn bị T00, tới lượt cập nhật đang đối chiếu transcript.

<a id="msg-997ca8f2585397bacf70"></a>

## P-000

- Timestamp: 13:27:24 18/11/2026 (UTC+07:00)
- Công cụ: OpenAI Codex

### Prompt

```text
session này tập trung vào hw05, hãy đọc và hiểu đề trước
```

<a id="msg-beceab931f80127a2da8"></a>

### Output

#### Phản hồi 1 — 13:27:32 18/11/2026 (UTC+07:00)

- Công cụ: OpenAI Codex

```text
Mình sẽ tìm đề HW05 trong workspace, đọc cùng rubric nếu có, rồi tóm tắt yêu cầu và các mục cần nộp trước khi bắt đầu làm bài.
```

<a id="msg-b1ce5aa23669736f365a"></a>

#### Phản hồi 2 — 13:27:43 18/11/2026 (UTC+07:00)

- Công cụ: OpenAI Codex

```text
Mình tìm thấy bản tiếng Việt và PDF tiếng Anh trong thư mục HW05. Mình sẽ dùng skill `pdf` để đọc bản tiếng Anh và đối chiếu các yêu cầu giữa hai bản.
```

<a id="msg-1fb8a44b0a008e295bf1"></a>

#### Phản hồi 3 — 13:29:11 18/11/2026 (UTC+07:00)

- Công cụ: OpenAI Codex

> Nội dung đã được xử lý; không phải nguyên văn đầy đủ. Đường dẫn tuyệt đối trong liên kết nguồn đã chuyển thành đường dẫn tương đối để chia sẻ.

```text
Mình đã đọc đề HW05-AI, đối chiếu bản tiếng Việt và checklist trong workspace. Đây là bài **Performance Testing cá nhân trên REST API của EShop**. Vỹ cần chọn **một workflow end-to-end riêng trong nhóm**, bao phủ đủ **auth-heavy, read-heavy và transactional**, rồi dùng cùng workflow đó cho cả **Load, Stress và Spike**.

- **Task 1 — Thiết kế và chạy test (70 điểm).** Hướng dẫn AI từng bước, sau đó Vỹ review và sửa các test plan. Dùng CSV để tham số hóa request, đặt tên plan theo `{StudentID}_{ScenarioType}_{YYYYMMDD}` và dùng một report view khác nhau cho mỗi kịch bản. Chạy đủ ba kịch bản, lưu ba log `.jtl` đầy đủ, ba thư mục HTML report và ảnh công cụ cùng mức sử dụng tài nguyên của tiến trình backend. Nếu Stress hoặc Spike kích hoạt lockout sau ba lần đăng nhập sai, ghi lại cách reset giữa các lượt. Chạy thêm một lượt **soak 10–15 phút** để báo cáo ngưỡng tải duy trì bằng số liệu đo.
- **Task 2 — Phân tích và phản biện AI (10 điểm).** Cho AI đọc `.jtl` thật và đề xuất ngưỡng hiệu năng. Với mỗi lỗi diễn giải phát hiện được, đối chiếu giá trị đúng từ raw log và giải thích sai ở đâu. Đánh giá từng đề xuất tối ưu dựa trên EShop thực tế.
- **Task 3 — Continuous Performance Testing (10 điểm).** Trong kết luận, đề xuất cách theo dõi commit, quyết định khi nào chạy test và cảnh báo khi p95 suy giảm. Kèm flowchart và thảo luận chi phí, cảnh báo giả.
- **Agent Skill (10 điểm).** Đề khuyến khích xây dựng skill tái sử dụng cho kiểm thử hiệu năng và phân tích log. Để lấy điểm phần này, nộp skill và video YouTube minh họa cách dùng trên một nhóm endpoint hoàn chỉnh.

**Bộ nộp** gồm báo cáo chính, AI Audit Report và AI Critique **200–300 từ** ở cả Markdown và PDF, cùng link repo GitHub công khai chứa plan và dữ liệu, bằng chứng chạy, Git commit log dạng văn bản và README có bảng tự chấm. Báo cáo phần cứng cần ảnh `dxdiag` hoặc tương đương, bảng cấu hình và hostname trùng với các bài trước. Video demo chính phải **unlisted, tổng ít nhất 6 phút**, có công cụ test và resource monitor trong cùng khung hình, với lời thuyết minh tiếng Việt bằng chính giọng Vỹ. Nộp ZIP `​<StudentID>_HW05_AI_Performance_<SelfAssessedGrade>.zip` trên Moodle, nơi công bố hạn nộp. Đề quy định thiếu tài liệu bắt buộc sẽ bị **0 điểm**.

Đề đưa luồng đăng nhập → duyệt sản phẩm → thêm giỏ → checkout làm ví dụ. Workflow của Vỹ vẫn cần đối chiếu với lựa chọn của các thành viên và endpoint thực tế của EShop trước khi thiết kế test plan.

`HW05/2026.HW05.Performance Testing_En.pdf` · `HW05/2026.HW05.Performance Testing_vn.md` · `HW05/REVIEW_CHECKLIST.md`
```

<a id="msg-9d29d552a7b73a8660d4"></a>

## P-001

- Timestamp: 13:30:11 18/11/2026 (UTC+07:00)
- Công cụ: OpenAI Codex

### Prompt

```text
Thực hiện HW05 — Performance Testing (HW05-AI).
Đề gốc: HW05/2026.HW05.Performance Testing_En.pdf (bản vn.md chỉ để tham khảo). Làm theo nếp HW04 (repo eshop-sut-HW04, thư mục hw04/, hồ sơ AI, README, Report, GitCommitLog). Tôi (Vỹ) là người duy nhất duyệt và quyết định.

=== NGUYÊN TẮC CHUNG ===
- AI-first: dẫn AI từng bước theo kỹ thuật, không một prompt chung chung. Lưu bản AI ban đầu trước khi sửa; ghi rõ AI sai/sót gì, vì sao (chất lượng prompt / giới hạn model / đặc thù endpoint) và đã sửa thế nào.
- Mọi số liệu lấy từ file .jtl thật. Lượt chạy hỏng, bỏ dở, blocked phải khai báo, không giấu.
- Tuyệt đối không làm giả hoặc để AI bịa: tên test plan/ngày, .jtl, video, ảnh resource monitor/hardware, hostname, chữ ký form AI. Những việc chỉ Vỹ làm được (quay video, chụp màn hình, ký form AI, điền link video, nộp Moodle) hãy liệt kê rõ cho Vỹ; không tự làm thay.
- Không chép nội dung/prompt của sinh viên khác (chép bị 0 điểm cả hai bên). Workflow của Vỹ không được trùng thành viên khác trong nhóm.
- Prompt Log và AI Audit chỉ ghi tương tác thật (công cụ, ngày giờ, prompt, output), không hồi tố, không dựng lại.
- Không commit secret, dữ liệu riêng, node_modules, file quá lớn.
- Thiếu bất kỳ tài liệu bắt buộc nào = 0 điểm; không nộp trễ.

=== QUY TRÌNH MỖI TASK (T00–T08) ===
1. Làm task, giữ kết quả ở working tree, CHƯA commit. Lưu bản AI đầu và ghi nhận các tương tác thật để cập nhật hồ sơ AI.
2. Dừng, báo Vỹ review. Vỹ phản hồi thì sửa theo phản hồi, lặp lại tới khi Vỹ duyệt. Không tự sang task sau.
3. Sau khi Vỹ duyệt (task done): cập nhật các file AI (PromptLog, AI_Audit_Report, AI_Critique nếu liên quan), README, Report cho khớp với task vừa xong, gồm cả các lượt review/sửa theo phản hồi của Vỹ. GHI ĐÈ / BỔ SUNG các file này dần qua các commit.
4. Chỉ lúc này mới commit artifact của task VÀ các file AI đã cập nhật, rồi push. Một task nhiều bước đáng tách thì tách thành vài commit nhỏ, nhưng vẫn chỉ commit sau khi cả task được duyệt. Conventional Commits, tác giả tranquocvy, không commit rỗng, không hồi tố.
5. Mọi commit đều ở trạng thái bản nộp cuối: không placeholder, TODO, "chờ Vỹ quyết", không nội dung dở dang. Điều gì chưa xong thì chưa commit.
6. GitCommitLog.txt xuất từ lịch sử commit thật; chỉ hoàn chỉnh ở T08. Các commit trước giữ file này đúng với trạng thái hiện có, không viết trước commit chưa tồn tại.

=== YÊU CẦU CỦA ĐỀ (tóm tắt để bám) ===
- Workflow end-to-end duy nhất dùng chung cho Load, Stress, Spike, phủ đủ 3 nhóm: auth-heavy (login, lưu ý khóa tài khoản FR-02 sau 3 lần sai), read-heavy (list/search/detail sản phẩm), transactional (add-to-cart, checkout/tạo đơn). Giải thích ngắn workflow phủ từng nhóm bằng request nào.
- Data-driven bằng CSV (credentials, product ID, payload đơn); không hardcode inline.
- Chọn think-time, ramp-up, số thread/VU hợp lý cho từng kịch bản, có lý giải.
- Ba test plan, ba loại listener/report khác nhau (không lặp). Tên plan: {StudentID}_{ScenarioType}_{YYYYMMDD}, ví dụ 23120410_Load_YYYYMMDD. JMeter mặc định (k6 là bonus).
- Mỗi lượt chạy: ảnh công cụ + resource monitor của tiến trình backend, .jtl thô đầy đủ, thư mục HTML report; hardware report (dxdiag/screenfetch + bảng spec), hostname khớp các HW trước. Reset khóa tài khoản giữa các lượt và ghi lại các bước.
- Endurance/soak 10–15 phút, ngưỡng bằng số cụ thể (max stable RPS, memory ceiling).
- Video YouTube unlisted ≥ 6 phút, công cụ và resource monitor cùng khung hình, giọng Vỹ tiếng Việt.
- Bug/perf issue thật: GitHub Issue kèm ảnh (Vỹ duyệt nội dung trước khi đăng).
- Task 2: AI phân tích .jtl và đề xuất ngưỡng; mỗi misinterpretation kèm giá trị đúng trích từ .jtl; đề xuất tối ưu phân loại feasible/hallucinated.
- Task 3: Continuous Performance Testing (theo dõi commit, quyết định chạy test, cờ p95 regression, flow chart, trade-off chi phí/báo động giả).
- Agent Skill + video demo trên một nhóm endpoint hoàn chỉnh.
- Rubric: Load 30, Stress 20, Spike 20, Task 2 10, Task 3 10, Skill 10.

=== CÁC TASK ===

T00 — Setup repo (làm trước hết)
- Tạo repo eshop-sut-HW05 (fork/copy SUT như HW04) và thư mục hw05/ theo cấu trúc bản nộp cuối: README.md, Report.md, ai/ (AI_Audit_Report.md, AI_Critique.md, PromptLog.md, AI forms theo mẫu), plans/, data/, results/, evidence/, skills/, GitCommitLog.txt.
- Điền sẵn các file từ mẫu AI đúng khung; README đúng bảng tự chấm 30/20/20/10/10/10 và khung test summary. Chỉ ghi nội dung thật; không dựng chỗ trống giả.
- Ghi vào Prompt Log/Audit các tương tác thật của bước setup (kể cả đọc đề).
- Không đoán tên repo/remote; hỏi Vỹ nếu chưa rõ. Báo Vỹ review rồi mới commit + push.

T01 — Chốt đầu vào & môi trường
- Hỏi Vỹ: workflow/endpoint (không trùng nhóm), JMeter hay k6, ngày dùng trong tên plan.
- Đọc api_specification.md và setup_guide.md; lập bảng endpoint thật theo auth / read / transactional kèm quy tắc khóa tài khoản FR-02.
- Chạy backend, smoke từng endpoint; ghi hostname và cấu hình máy; nêu hạn chế (load generator và SUT cùng máy...).

T02 — Dữ liệu CSV + Load plan
- Dẫn AI từng bước: chọn tham số, thiết kế CSV (đủ tài khoản để tránh lockout, product ID, payload đơn), dựng plan 23120410_Load_<YYYYMMDD> với assertion có nghĩa và correlation (token, ID giỏ/đơn).
- Lưu bản AI đầu, ghi danh sách AI sai/sót và nguyên nhân; chạy thử nhỏ để kiểm tra plan.

T03 — Stress + Spike plan
- Cùng workflow và CSV; Stress tăng dần tới vỡ, Spike tăng đột ngột; listener loại 2 và 3, không trùng loại 1.
- Viết quy trình reset khóa tài khoản/DB giữa các lượt, dựa trên thao tác thực tế.

T04 — Thực thi Load / Stress / Spike
- Chạy non-GUI. Mỗi lượt: .jtl thô, HTML report, ảnh công cụ + resource monitor, hardware report (hostname khớp HW trước). Đối chiếu số trong report với .jtl.
- Việc cần ảnh chụp hoặc video thật từ máy Vỹ: nêu rõ cho Vỹ, chờ Vỹ cung cấp.
- Bug hoặc perf issue thật: soạn Issue kèm ảnh, Vỹ duyệt trước khi đăng.

T05 — Endurance / soak 10–15 phút
- Tải ổn định, .jtl + resource monitor theo thời gian; kết luận ngưỡng bằng số và nêu tiêu chí "ổn định" đã dùng.

T06 — Task 2: AI phân tích log
- Đưa .jtl thật cho AI để phân tích và đề xuất ngưỡng; lưu nguyên output.
- Liệt kê từng misinterpretation kèm giá trị đúng trích từ .jtl và cách tính.
- Cho AI đề xuất tối ưu; phân loại feasible / hallucinated dựa trên stack thật của SUT (code, SQLite, Express...).

T07 — Task 3 + Agent Skill
- Mô hình Continuous Performance Testing: theo dõi commit, quyết định chạy test, cờ p95 regression, flow chart đọc được trong PDF, trade-off chi phí/báo động giả (nằm trong phần kết luận của Report).
- Agent Skill cho workflow perf + phân tích log, đủ thư mục (SKILL.md, references/scripts). Việc quay video demo skill do Vỹ làm.

T08 — Chốt bộ nộp
- Report.md + PDF (kết quả perf + phản biện AI + Task 3), AI Audit MD + PDF, AI Critique MD + PDF (200–300 từ, đếm thật), README (bảng tự chấm + test summary: kịch bản đã chạy, nhóm endpoint phủ, ngưỡng endurance kèm số, số bug/perf issue, link video), GitCommitLog.txt xuất từ git thật, ZIP 23120410_HW05_AI_Performance_<NNN>.zip (NNN = điểm tự chấm 3 chữ số).
- Giải nén ở chỗ khác kiểm tra: PDF mở được, link tương đối không hỏng, HTML report chạy offline.
- Còn lại cho Vỹ: quay video, chụp ảnh thật, rà và ký form AI, điền link video, nộp Moodle.

=== BẮT ĐẦU ===
Làm T00 ngay. Trước khi tạo gì, hỏi Vỹ những thông tin còn thiếu (tên repo/remote). Xong T00 thì dừng và báo Vỹ review.
```

<a id="msg-fe401fea65364a714ef3"></a>

### Output

#### Phản hồi 1 — 13:30:17 18/11/2026 (UTC+07:00)

- Công cụ: OpenAI Codex

```text
Mình sẽ đọc yêu cầu trong tệp đính kèm và đối chiếu với đề HW05 trước khi bắt đầu.
```

<a id="msg-571eed366b22869cf6dc"></a>

#### Phản hồi 2 — 13:30:28 18/11/2026 (UTC+07:00)

- Công cụ: OpenAI Codex

```text
Mình sẽ giới hạn lượt này ở T00 và dừng để Vỹ review trước khi commit hoặc push. Mình dùng skill `course-ai-log` để đối chiếu mẫu hồ sơ AI và cách lấy prompt, output từ các lượt trao đổi thật. Trước khi tạo repo, mình sẽ kiểm tra thông tin Git và các mẫu có sẵn trong workspace.
```

<a id="msg-6adbffd5b2bf081f7a33"></a>

#### Phản hồi 3 — 13:30:58 18/11/2026 (UTC+07:00)

- Công cụ: OpenAI Codex

```text
Vỹ xác nhận repo công khai `tranquocvy/eshop-sut-HW05`, lấy mã nguồn từ `ttbhanh/eshop-sut` như HW04, hay muốn dùng remote hoặc nguồn SUT khác?

- Dùng repo và nguồn như trên
- Tôi sẽ gửi remote hoặc nguồn khác
```

<a id="msg-eb9f4db5cbffc2f0343c"></a>

## P-002

- Timestamp: 13:31:09 18/11/2026 (UTC+07:00)
- Công cụ: OpenAI Codex

### Prompt

```text
Dùng repo và nguồn như trên
```

<a id="msg-1e33b49f037375d38659"></a>

### Output

#### Phản hồi 1 — 13:31:40 18/11/2026 (UTC+07:00)

- Công cụ: OpenAI Codex

```text
HW04 dùng repo công khai độc lập với `ttbhanh/eshop-sut` làm upstream. Mình sẽ dùng cùng cách cho HW05, giữ lịch sử gốc của SUT và để các file T00 ở working tree cho Vỹ review.
```

<a id="msg-17db39aba9499c760f9e"></a>

#### Phản hồi 2 — 13:34:06 18/11/2026 (UTC+07:00)

- Công cụ: OpenAI Codex

```text
Repo GitHub công khai đã được tạo và đang trống. Bản local dùng mốc EShop `85af3ba`, cùng mốc HW04 đã dùng. Mình đang đối chiếu hồ sơ AI với transcript để giữ đúng prompt, phản hồi và thời gian thực.
```
