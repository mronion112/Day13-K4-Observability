# Điều tra challenge day13-k4-observability-v1

## Metrics

Sau 5 input chính thức, dashboard 60 phút ghi nhận P95 `10299 ms`, vượt SLO `3000 ms`;
error rate vẫn `0%`. Đây là latency incident, không phải availability incident.

## Trace

Trace [`67b99cb08e93951aeaecf1f758648c9c`](https://cloud.langfuse.com/project/cmsodbsww022vad0k540vl1nr/traces/67b99cb08e93951aeaecf1f758648c9c)
của session `k4-challenge-s04` kéo dài `3.598 s`:

- `retrieval`: 08:54:45.228–08:54:47.735 UTC, khoảng `2.507 s`.
- `llm_generation`: 08:54:48.672–08:54:48.825 UTC, khoảng `0.153 s`.

Span retrieval chiếm phần lớn thời gian xử lý và vượt ngưỡng challenge `2000 ms`.
Ảnh waterfall: [trace-challenge-waterfall.png](trace-challenge-waterfall.png).

## Logs

Correlation ID `req-e3b71a6a` nối trace với chuỗi log:

- `request_received` lúc 08:54:45.227976 UTC.
- `tool_completed`, `tool_name=retrieval`, `latency_ms=2505`.
- `model_completed`, `latency_ms=151`.
- `response_sent`, `latency_ms=3597`.

Baseline trước incident có retrieval khoảng `0 ms`; cả 5 request challenge có retrieval
`2502–2505 ms`. Root cause là độ trễ được inject vào retrieval/RAG cho feature `monitoring`,
không phải LLM generation.

## Action

- Fix/mitigation: tắt incident, đặt timeout cho retrieval và dùng fallback document cache khi
  dependency vượt timeout; giới hạn concurrency trong lúc khắc phục.
- Preventive measure: theo dõi latency riêng cho retrieval span, alert theo P95 end-to-end,
  thêm timeout/circuit breaker và chạy practice incident định kỳ để kiểm tra runbook.
