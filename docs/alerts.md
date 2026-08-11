# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: `high_latency_p95`
- Severity: warning
- SLI/SLO liên quan: `latency_p95_ms`, mục tiêu dưới 3000 ms
- Điều kiện và thời gian duy trì: `latency_p95 > 3000ms` trong 5 phút
- Ảnh hưởng tới người dùng: phản hồi chat chậm hoặc timeout.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra `/metrics` và đối chiếu P50/P95/P99.
  2. Mở trace chậm nhất, so sánh thời gian `retrieve` và `generate`.
  3. Tìm log `response_sent` cùng `correlation_id`.
- Mitigation tạm thời: giảm concurrency, tắt incident gây chậm, hoặc chuyển sang prompt/local fallback.
- Owner: on-call-engineer

## Alert 2

- Tên: `elevated_error_rate`
- Severity: critical
- SLI/SLO liên quan: `error_rate_pct`, mục tiêu dưới 2%
- Điều kiện và thời gian duy trì: `error_rate_pct > 5` trong 3 phút
- Ảnh hưởng tới người dùng: nhiều request chat thất bại.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra `error_rate_pct` và `error_breakdown` tại `/metrics`.
  2. Lọc log `request_failed` theo `error_type`.
  3. Dùng `correlation_id` để mở trace và xác định span lỗi.
- Mitigation tạm thời: tắt incident hiện tại, bật fallback và giảm lưu lượng gửi vào API.
- Owner: on-call-engineer

## Alert 3

- Tên: `cost_budget_exceeded`
- Severity: warning
- SLI/SLO liên quan: `daily_cost_usd`, ngân sách dưới 2.5 USD/ngày
- Điều kiện và thời gian duy trì: `daily_cost_usd > 2.5`
- Ảnh hưởng tới người dùng: hệ thống có nguy cơ vượt ngân sách vận hành.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra `total_cost_usd`, `avg_cost_usd` và token totals tại `/metrics`.
  2. So sánh cost theo feature/model trong log `response_sent`.
  3. Mở trace có token usage bất thường để kiểm tra prompt và output.
- Mitigation tạm thời: bật giới hạn token, dùng model/prompt tiết kiệm hơn và tạm giảm traffic.
- Owner: team-lead
