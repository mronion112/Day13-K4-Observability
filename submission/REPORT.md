# Báo cáo Day 13 — AI Observability

## 1. Thông tin nhóm

- Tên nhóm: Nhóm Day 13 — AI Observability.
- Repository URL: `https://github.com/mronion112/Day13-K4-Observability`
- Commit hoàn thiện hiện tại: `5f2d5e7` (`Xong`).
- Thành viên:
  - Nguyễn Hoàng Anh — 2A2202601186
  - Trần Quang Minh — 2A2202601210
  - Ngô Văn Nam — 2A2202601340
  - Phạm Khắc Khương Duy — 2A2202601982
  - Đào Kiều Thịnh Quang — 2A2202601014

## 2. Kết quả kỹ thuật

- API FastAPI cung cấp `/health`, `/chat` và `/metrics`; Langfuse tracing đã được bật.
- Test tự động: `22 passed` (có cảnh báo FastAPI `on_event` deprecated, không làm hỏng chức năng).
- `python scripts/validate_logs.py`: **100/100**; không thiếu trường bắt buộc, không thiếu context và không phát hiện PII leak.
- `python scripts/validate_dashboard.py`: **6/6 panel hợp lệ**.
- Có hơn 10 traces trên Langfuse với metadata request/session/user, span `retrieve` và generation `generate`.
- Dashboard contract: [config/dashboard.yaml](../config/dashboard.yaml); evidence: [cp2-dashboard-config.png](evidence/cp2-dashboard-config.png).

## 3. Logging và tracing

Mỗi request được middleware tạo/nhận `X-Request-ID`, bind vào context và trả về response header. Log JSON được enrich với `correlation_id`, `session_id`, `user_id_hash`, `feature`, `model` và `env`. PII được scrub trước khi ghi log: email, số điện thoại Việt Nam và số thẻ thử nghiệm được thay bằng placeholder.

- Correlation ID mẫu: `req-8a14a634`; xem [cp1-validation.txt](evidence/cp1-validation.txt).
- Bằng chứng PII redaction: [cp1-pii-redaction.png](evidence/cp1-pii-redaction.png). Ví dụ email được ghi thành `[REDACTED_EMAIL]`.
- Kết quả validator: [cp1-validator.png](evidence/cp1-validator.png).
- Danh sách trace: [cp2-trace-list.png](evidence/cp2-trace-list.png).
- Waterfall trace: [cp2-trace-waterfall.png](evidence/cp2-trace-waterfall.png). Span `retrieve` biểu diễn thời gian lấy tài liệu; span `generate` biểu diễn thời gian sinh câu trả lời. Việc tách span cho phép định vị phần nào của một request gây tăng latency.

## 4. Prompt versioning

- Prompt name: `day13-chat`.
- Version/label đang có bằng chứng: version `v1`, label `production`.
- Prompt nhận ba biến `{{feature}}`, `{{docs}}`, `{{message}}`; generation ghi metadata prompt/model trên Langfuse.
- **Việc còn phải thực hiện trước khi nộp theo rubric:** tạo `v2` (candidate), chạy tối thiểu một trace cho từng version, đổi label `production` hoặc rollback, rồi lưu ảnh các trace và ảnh thao tác vào `submission/evidence/`. Không có evidence hiện tại cho v2/rollback nên nhóm không tuyên bố đã hoàn tất mục này.

## 5. Dashboard, SLO và alerts

- Dashboard gồm 6 panel: latency percentiles, traffic, error rate, token usage, cost và quality; kết quả validator 6/6 có trong [cp2-dashboard-config.png](evidence/cp2-dashboard-config.png).
- SLO cấu hình tại [config/slo.yaml](../config/slo.yaml): latency P95 mục tiêu dưới 3000 ms; error rate dưới 2%; daily cost dưới 2.5 USD; quality score trung bình từ 0.75.
- Alert rules tại [config/alert_rules.yaml](../config/alert_rules.yaml): `high_latency_p95`, `elevated_error_rate`, `cost_budget_exceeded`.
- Runbook xử lý alert tại [docs/alerts.md](../docs/alerts.md), bao gồm kiểm tra metrics → trace → log/correlation ID và phương án giảm thiểu.

## 6. Điều tra challenge

- Challenge ID: `day13-k4-observability-v1`; incident chính thức: `rag_slow`; threshold latency: 2000 ms.
- Sau khi bật incident và chạy `python scripts/load_test.py --challenge --concurrency 5`, metrics ghi nhận P50 = 151 ms, **P95 = 2653 ms**, P99 = 2654 ms và error rate = 0%. Điều này cho thấy tail latency tăng cao, không phải lỗi diện rộng. Evidence: [cp3-metrics.png](evidence/cp3-metrics.png).
- Log xác nhận incident đã được bật: [cp3-log-rag-slow-enabled.png](evidence/cp3-log-rag-slow-enabled.png).
- Request được điều tra có `correlation_id=req-9fa962a0`, `session_id=k4-challenge-s04`, feature `monitoring`; log `response_sent` ghi `latency_ms=2654`. Evidence: [cp3-log-correlation.png](evidence/cp3-log-correlation.png).
- Trace cùng request cho thấy span `retrieve` mất khoảng **2.50 giây**, trong khi `generate` khoảng 0.15 giây. Evidence: [cp3-trace-retrieve-slow.png](evidence/cp3-trace-retrieve-slow.png).
- Root cause: `rag_slow` chủ động thêm 2.5 giây vào retrieval, trực tiếp làm P95 vượt threshold.
- Fix action: tắt incident sau khi thu thập evidence; đặt timeout cho retrieval và trả fallback khi retrieval/vector store chậm.
- Preventive measure: alert theo latency P95, giám sát span `retrieve`, giới hạn thời gian retrieval và chạy load test định kỳ cho feature `monitoring`.
- Biên bản đầy đủ: [cp3-investigation.txt](evidence/cp3-investigation.txt).

## 7. Đóng góp cá nhân

| Thành viên | Phần việc/phân công | Bằng chứng trong repository | Điều đã học |
|---|---|---|---|
| Nguyễn Hoàng Anh — 2A2202601186 | Logging có cấu trúc và chuẩn hóa schema | `app/logging_config.py`, `config/logging_schema.json` | Thiết kế log machine-readable và enrichment theo request. |
| Trần Quang Minh — 2A2202601210 | Tracing Langfuse và prompt management | `app/agent.py`, `app/tracing.py`, `docs/PROMPT_VERSIONING.md` | Dùng trace/span để theo dõi một request AI end-to-end. |
| Ngô Văn Nam — 2A2202601340 | Tích hợp, kiểm thử và hoàn thiện submission | commit `5f2d5e7`, `submission/` | Liên kết metrics, traces và logs để điều tra sự cố. |
| Phạm Khắc Khương Duy — 2A2202601982 | Metrics, SLO, dashboard và alert rules | `app/metrics.py`, `config/dashboard.yaml`, `config/slo.yaml` | Đặt SLI/SLO và cảnh báo dựa trên triệu chứng người dùng. |
| Đào Kiều Thịnh Quang — 2A2202601014 | PII scrubbing, incident challenge và runbook | `app/pii.py`, `docs/alerts.md`, `submission/evidence/cp3-*` | Điều tra root cause bằng correlation ID và waterfall span. |

> Lưu ý: Bảng phân công được điền theo phạm vi artefact. Nếu mỗi thành viên có commit/PR riêng, bổ sung link commit/PR tương ứng trước khi nộp.
