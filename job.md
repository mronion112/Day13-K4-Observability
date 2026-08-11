# Bảng Phân Công Công Việc Song Song (Parallel Jobs)

Để tối ưu hóa thời gian 4 tiếng của bài Lab, nhóm sẽ chia thành **3 luồng công việc chạy song song hoàn toàn** trong giai đoạn đầu. Mọi người chú ý phần **[ĐANG ĐỢI]** để biết khi nào mình cần kết nối với thành viên khác.

---

## 🚀 Luồng 1: Middleware & Logging (Thành viên A & B)
*Luồng này quyết định chất lượng dữ liệu đầu ra của cả hệ thống.*

### Thành viên A (API & Middleware)
- **[LÀM NGAY - ĐỘC LẬP]:** 
  - Khởi tạo khung Custom Middleware.
  - Viết logic tạo `Correlation ID` (dùng `uuid4`).
  - Viết Exception Handler bắt các lỗi crash không lường trước.
  - Chỉnh sửa cấu trúc JSON Log chuẩn (đảm bảo có `user_id_hash`, `session_id`).
- **[ĐANG ĐỢI]:** 
  - Đợi B đưa cho các pattern/hàm Regex để ráp vào formatter xóa PII trước khi xuất log.

### Thành viên B (Security Engineer)
- **[LÀM NGAY - ĐỘC LẬP]:** 
  - Tạo một file/module riêng biệt chuyên xử lý PII.
  - Viết, test độc lập các Regex rules: ẩn Email (ví dụ: `a***@gmail.com`), ẩn Phone, ẩn Credit Card.
  - Làm Unit test ngắn cho các hàm Regex của mình để chắc chắn nó che đúng.
- **[ĐANG ĐỢI]:** 
  - Chờ A gọi hàm PII scrubber này vào luồng Log xuất ra file `logs.jsonl`.
  - Chờ E chạy Script Load Test để đọc file `logs.jsonl` xem PII còn sót không.

---

## 🚀 Luồng 2: Observability & Tracing (Thành viên E)
*Luồng này đi sâu vào logic AI (RAG/LLM) và điều phối chung.*

### Thành viên E (QA & Chief Investigator)
- **[LÀM NGAY - ĐỘC LẬP]:** 
  - Setup tài khoản/môi trường Langfuse.
  - Bọc Tracing (Decorators) vào các hàm gọi LLM và RAG (sub-components).
  - Setup 2 version của prompt theo hướng dẫn `PROMPT_VERSIONING.md` và bắn log lên Langfuse.
  - Soạn sẵn khung xương báo cáo `REPORT.md`.
- **[ĐANG ĐỢI]:** 
  - (Liên tục) Chạy load test phụ team để kiểm tra luồng của A, B, C.
  - Chờ Coach tung `challenge.json` để kích hoạt kịch bản lỗi.

---

## 🚀 Luồng 3: Metrics, Dashboard & SLO (Thành viên C & D)
*Luồng này làm việc với các file cấu hình và đo lường cảnh báo.*

### Thành viên C (Metrics & Dashboard)
- **[LÀM NGAY - ĐỘC LẬP]:** 
  - Nghiên cứu `dashboard.yaml` và `data/logs.jsonl` mẫu để hình dung data.
  - Thiết kế cấu trúc/query cho 6 panel dashboard (Latency, Traffic, Error, Token/Cost, Quality).
  - Bổ sung logic đo `error_rate_pct` vào code (có thể xin nhánh của A để chèn thêm 1-2 dòng đếm).
- **[ĐANG ĐỢI]:** 
  - Đợi A & B hoàn tất format `logs.jsonl` chuẩn thì mới chạy lệnh validator thành công 100%.

### Thành viên D (SRE & Alerts Engineer)
- **[LÀM NGAY - ĐỘC LẬP]:** 
  - Điền mục tiêu cho `config/slo.yaml` (các mốc Target 99%, 95%...).
  - Viết bộ rules cảnh báo trong `config/alert_rules.yaml`.
  - Soạn thảo **Alert Runbook** (Tài liệu hướng dẫn: Nếu cảnh báo A nổ thì các bước debug là 1, 2, 3...). Việc này hoàn toàn không phụ thuộc vào code của ai.
- **[ĐANG ĐỢI]:** 
  - Cùng C thống nhất ngưỡng báo động (Threshold).
  - Chờ đến CP3 (Challenge) để xem kịch bản lỗi có "nổ" đúng Alert mình setup không.

---

## ⚡ Nút Thắt Giao Điểm (Choke Point) - CP3 Challenge
*Khi tới Checkpoint 3 (Challenge phát hành), toàn bộ các luồng song song DỪNG LẠI và gộp làm một.*

1. **E** chạy Inject Incident (tạo lỗi).
2. **C & D** ngồi canh Dashboard/Alert, báo cáo ngay thành phần nào đang bị sập/chậm.
3. **E** lên Langfuse dò theo Trace ID, phát hiện hàm cụ thể bị lỗi.
4. **B & A** cầm Trace ID tra trong file `logs.jsonl` để trích xuất dòng log báo lỗi gốc (Root cause).
5. **Cả nhóm** họp nhanh bàn fix, commit code và E viết báo cáo bằng chứng.
