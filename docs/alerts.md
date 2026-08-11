# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: User-facing latency SLO breach
- Severity: Critical
- SLI/SLO liên quan: P95 latency ≤ 3000 ms trong cửa sổ 28 ngày, target 99.5%.
- Điều kiện và thời gian duy trì: `latency_p95_ms > 3000` liên tục 5 phút.
- Ảnh hưởng tới người dùng: Phản hồi chat chậm rõ rệt hoặc timeout.
- Ba bước kiểm tra đầu tiên:
  1. Mở panel Latency và xác nhận P95/P99 cùng khoảng thời gian.
  2. Mở trace chậm, so sánh span retrieval và generation.
  3. Tìm log `tool_completed` bằng correlation ID để xác nhận component chậm.
- Mitigation tạm thời: Giảm concurrency, bỏ qua nguồn retrieval chậm hoặc dùng fallback đã kiểm thử; theo dõi P95 trở lại dưới ngưỡng.
- Owner: AI Platform On-call

## Alert 2

- Tên: Elevated request failure rate
- Severity: Critical
- SLI/SLO liên quan: Error rate ≤ 2%, target 99.0% trong cửa sổ 28 ngày.
- Điều kiện và thời gian duy trì: `error_rate_pct > 2` liên tục 5 phút.
- Ảnh hưởng tới người dùng: Hơn 2% request chat không trả được câu trả lời.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra breakdown `error_type` trên panel Errors.
  2. Mở trace lỗi gần nhất và xác định span thất bại đầu tiên.
  3. Tìm `request_failed`/`tool_failed` có cùng correlation ID trong log.
- Mitigation tạm thời: Chuyển sang dependency/fallback ổn định hoặc tắt feature gây lỗi, sau đó chạy smoke test.
- Owner: AI Platform On-call

## Alert 3

- Tên: Answer quality degradation
- Severity: Warning
- SLI/SLO liên quan: Quality proxy trung bình ≥ 0.75, target 95% trong cửa sổ 28 ngày.
- Điều kiện và thời gian duy trì: `quality_score_avg < 0.75` liên tục 15 phút.
- Ảnh hưởng tới người dùng: Câu trả lời thiếu context, quá ngắn hoặc không liên quan.
- Ba bước kiểm tra đầu tiên:
  1. Xác nhận traffic và error rate không thay đổi bất thường.
  2. Lọc trace theo `prompt_name`, `prompt_label`, `prompt_version`.
  3. So sánh retrieval metadata và prompt version với giai đoạn trước cảnh báo.
- Mitigation tạm thời: Rollback label `production` về prompt version ổn định và xác nhận quality phục hồi.
- Owner: AI Quality Owner
