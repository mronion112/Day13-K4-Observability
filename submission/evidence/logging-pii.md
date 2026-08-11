# Logging, correlation và PII evidence

Validator cuối ghi nhận 18 correlation ID, không thiếu trường bắt buộc/enrichment và không có PII leak.

Ba input thử nghiệm được scrub trước khi render JSON:

- Email: `req-cdd8bf09` → `My email is [REDACTED_EMAIL]`
- Điện thoại: `req-46b39032` → `Here is my phone [REDACTED_PHONE_VN]`
- Thẻ tín dụng: `req-7279ceba` → `credit card [REDACTED_CREDIT_CARD]`

Ví dụ propagation xuyên request challenge `req-e3b71a6a`:

| Event | Service | Correlation ID | Metadata đáng chú ý |
|---|---|---|---|
| `request_received` | api | `req-e3b71a6a` | session `k4-challenge-s04`, feature `monitoring` |
| `tool_started` | agent | `req-e3b71a6a` | tool `retrieval` |
| `tool_completed` | agent | `req-e3b71a6a` | retrieval `2505 ms` |
| `model_completed` | agent | `req-e3b71a6a` | generation `151 ms` |
| `response_sent` | api | `req-e3b71a6a` | total `3597 ms`, quality `0.9` |

Các dòng nguồn nằm trong `data/logs.jsonl`; user ID chỉ xuất hiện ở dạng SHA-256 rút gọn.
