# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1 — high_latency_p95

- Tên: high_latency_p95
- Severity: warning
- SLI/SLO liên quan: latency_p95_ms — P95 < 3000ms, target 99.5% (28 ngày)
- Điều kiện và thời gian duy trì: `latency_p95 > 3000ms` trong 5 phút liên tục
- Ảnh hưởng tới người dùng: Người dùng chờ phản hồi lâu (>3 giây), trải nghiệm chat bị giật, có thể bỏ cuộc giữa chừng
- Ba bước kiểm tra đầu tiên:
  1. Vào Langfuse Dashboard → Traces, lọc theo thời gian 5 phút gần nhất, sắp xếp theo duration giảm dần để tìm trace chậm nhất
  2. Mở waterfall trace chậm nhất, xác định span nào chiếm nhiều thời gian nhất (retrieve hay generate)
  3. Nếu retrieve chậm → kiểm tra incident `rag_slow` đã bị bật chưa (`curl http://localhost:8000/health`). Nếu generate chậm → kiểm tra incident `cost_spike`
- Mitigation tạm thời:
  - Nếu `rag_slow` đang bật: `python scripts/inject_incident.py --scenario rag_slow --disable`
  - Nếu do tải cao: giảm concurrency trong load test
  - Fallback: chuyển prompt sang phiên bản ngắn hơn (nếu có prompt v2 optimized)
- Owner: on-call-engineer

## Alert 2 — elevated_error_rate

- Tên: elevated_error_rate
- Severity: critical
- SLI/SLO liên quan: error_rate_pct — error rate < 2%, target 99.0% (28 ngày)
- Điều kiện và thời gian duy trì: `error_rate_pct > 5%` trong 3 phút liên tục
- Ảnh hưởng tới người dùng: Người dùng nhận HTTP 500 thay vì câu trả lời, không thể sử dụng dịch vụ chat — đây là outage từng phần hoặc toàn phần
- Ba bước kiểm tra đầu tiên:
  1. Gọi `curl http://localhost:8000/metrics` → kiểm tra `error_breakdown` để biết loại lỗi (RuntimeError, KeyError, ...)
  2. Nếu có `RuntimeError` → kiểm tra `curl http://localhost:8000/health` xem incident `tool_fail` có đang bật không
  3. Mở `data/logs.jsonl`, tìm dòng có `event: "request_failed"`, lấy `correlation_id` → vào Langfuse trace để xem chi tiết lỗi
- Mitigation tạm thời:
  - Nếu `tool_fail` đang bật: `python scripts/inject_incident.py --scenario tool_fail --disable`
  - Nếu lỗi khác: xem log chi tiết, có thể cần rollback code hoặc restart service
  - Kích hoạt circuit breaker tạm thời nếu có
- Owner: on-call-engineer

## Alert 3 — cost_budget_exceeded

- Tên: cost_budget_exceeded
- Severity: warning
- SLI/SLO liên quan: daily_cost_usd — chi phí < $2.50/ngày, target 100%
- Điều kiện và thời gian duy trì: `daily_cost_usd > $2.50` (tổng tích lũy trong ngày vượt ngưỡng)
- Ảnh hưởng tới người dùng: Chưa ảnh hưởng trực tiếp nhưng nếu không kiểm soát, ngân sách có thể cạn kiệt trước cuối tháng → phải tạm dừng dịch vụ
- Ba bước kiểm tra đầu tiên:
  1. Mở log `data/logs.jsonl`, lọc `event: "response_sent"`, tính tổng `cost_usd` để xác nhận số liệu
  2. Kiểm tra `curl http://localhost:8000/health` xem incident `cost_spike` có đang bật không (làm output tokens x4)
  3. Vào Langfuse trace gần nhất, kiểm tra `usage_details` — nếu `completion_tokens` cao bất thường (>500) là dấu hiệu cost spike
- Mitigation tạm thời:
  - Nếu `cost_spike` đang bật: `python scripts/inject_incident.py --scenario cost_spike --disable`
  - Nếu do traffic cao: tạm thời giới hạn rate limit hoặc giảm max_tokens
  - Thông báo team lead để xin phê duyệt tăng ngân sách nếu cần
- Owner: team-lead
