# Khung thiết kế Observability

Dùng khung này trước khi triển khai, sau đó chuyển kết quả cuối sang `submission/REPORT.md`.

## Người dùng và luồng chính

- Người dùng/client gửi `POST /chat` với `user_id`, `session_id`, `feature` và `message`.
- Request đi qua FastAPI middleware → API handler → retrieval/RAG → prompt resolver → fake LLM → response.
- `CorrelationIdMiddleware` nhận `x-request-id` hợp lệ hoặc tạo `req-<8 ký tự hex>`, bind vào
  structlog contextvars, lưu trong `request.state`, trả lại qua response header và truyền vào
  mọi log API/agent trong request.

## Tín hiệu quan sát

| Thành phần | Log cần có | Metric cần có | Span cần có |
|---|---|---|---|
| API | `request_received`, `response_sent`, `request_failed`, correlation ID, metadata | traffic, end-to-end latency, error rate | root generation `run` |
| Retrieval | `tool_started`, `tool_completed`, `tool_failed`, tool latency | retrieval latency qua log/dashboard điều tra | span `retrieval` |
| LLM | `model_completed`, tokens, cost | tokens input/output, cost, quality proxy | span `llm_generation` trong generation `run` |

## SLO và alert

| SLI | Mục tiêu | Cửa sổ đo | Alert |
|---|---:|---|---|
| Latency P95 | ≤ 3000 ms, target 99.5% | 28 ngày | Critical nếu P95 > 3000 ms trong 5 phút |
| Error rate | ≤ 2%, target 99% | 28 ngày | Critical nếu > 2% trong 5 phút |
| Cost | ≤ 2.5 USD/ngày | 28 ngày | Theo dõi threshold trên dashboard và điều tra token/model khi vượt |
| Quality | Trung bình ≥ 0.75, target 95% | 28 ngày | Warning nếu < 0.75 trong 15 phút |

## Rủi ro dữ liệu

- PII có thể xuất hiện trong message, answer, exception, payload lồng nhau hoặc request ID do client gửi.
- Log chỉ giữ preview đã scrub, user ID đã hash, session/feature/model, số liệu vận hành và error type;
  không ghi raw prompt/answer hoặc secret.
- Processor scrub đệ quy chạy sau khi exception/stack info được chuẩn hóa nhưng trước
  `JSONRenderer` và trước khi ghi xuống `data/logs.jsonl`.
