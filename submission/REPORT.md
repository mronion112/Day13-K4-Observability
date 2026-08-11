# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py` baseline (CP0): 30/100
- Điểm `validate_logs.py` sau CP1: 100/100
- Tổng số traces: 40 (10 traces × 4 lần load test)
- Số PII leak còn lại: 0
- Link/đường dẫn dashboard: `http://localhost:8000/dashboard`
- Kết quả `validate_dashboard.py`: HỢP LỆ: 6/6 panel

## 3. Logging và tracing

- Evidence correlation ID: Mỗi request có `correlation_id` format `req-<8hex>`, xuất hiện trong log và response header `x-request-id`
- Evidence PII redaction: 0 PII leak, email/SĐT/CCCD được thay bằng `[REDACTED_EMAIL]`, `[REDACTED_PHONE]`, `[REDACTED_CCCD]`, `[REDACTED_CREDIT_CARD]`
- Evidence trace waterfall: Mỗi trace hiển thị 3 span lồng nhau: `run` → `retrieve` → `generate` (đã thêm `@observe` decorator vào `mock_rag.py` và `mock_llm.py`)
- Giải thích một span đáng chú ý: Span `retrieve` hiển thị thời gian truy xuất RAG corpus, span `generate` hiển thị thời gian LLM inference — giúp phân biệt ngay bottleneck ở tầng nào khi có incident

## 4. Prompt versioning

- Prompt name: day13-chat
- Version/label baseline: (cần tạo prompt trên Langfuse — pending)
- Version/label candidate: (pending)
- Trace ID của mỗi version: (pending)
- Bằng chứng đổi label hoặc rollback: (pending)

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: HỢP LỆ: 6/6 panel có trong dashboard contract
- Evidence dashboard: `http://localhost:8000/dashboard` — 6 panel: Latency (P50/P95/P99), Traffic, Error Rate (%), Cost ($USD), Tokens (in/out), Quality (0-1)
- SLO đã chọn và lý do:
  | SLI | Objective | Target | Lý do |
  |---|---|---|---|
  | latency_p95_ms | < 3000ms | 99.5% | Trải nghiệm chat cần phản hồi nhanh |
  | error_rate_pct | < 2% | 99.0% | Dịch vụ phải đáng tin cậy |
  | daily_cost_usd | < $2.50 | 100% | Ngân sách cố định theo ngày |
  | quality_score_avg | ≥ 0.75 | 95.0% | Chất lượng câu trả lời phải đảm bảo |
- Alert rules và runbook: 3 alerts trong `config/alert_rules.yaml`, runbook chi tiết tại `docs/alerts.md`
  | Alert | Severity | Condition |
  |---|---|---|
  | high_latency_p95 | warning | P95 > 3000ms trong 5 phút |
  | elevated_error_rate | critical | Error rate > 5% trong 3 phút |
  | cost_budget_exceeded | warning | Daily cost > $2.50 |

## 6. Điều tra challenge

- Challenge ID:
- Triệu chứng từ metrics:
- Trace ID liên quan:
- Log line/correlation ID liên quan:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| | | | |
