# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

Alert 1
Tên: high_latency_p95
Severity: warning
SLI/SLO liên quan: Request latency P95 ≤ 3000ms
Điều kiện và thời gian duy trì: latency_p95 > 3000ms for 5 minutes
Ảnh hưởng tới người dùng: Người dùng phải chờ lâu hơn khi thực hiện request, có thể gặp timeout nếu tình trạng kéo dài.
Ba bước kiểm tra đầu tiên:
Kiểm tra P95 latency theo endpoint/operation để xác định phạm vi ảnh hưởng.
Kiểm tra error rate, timeout rate và traffic để xác định có spike hoặc lỗi đi kèm hay không.
Kiểm tra các thay đổi gần đây và tình trạng các dependency liên quan.
Mitigation tạm thời: Giảm tải hoặc giới hạn traffic nếu cần; rollback thay đổi gần nhất nếu xác định thay đổi đó gây tăng latency.
Owner: on-call-engineer
Alert 2
Tên: elevated_error_rate
Severity: critical
SLI/SLO liên quan: Request error rate ≤ 5%
Điều kiện và thời gian duy trì: error_rate_pct > 5 for 3 minutes
Ảnh hưởng tới người dùng: Nhiều request thất bại, khiến người dùng không thể hoàn thành thao tác hoặc nhận được lỗi.
Ba bước kiểm tra đầu tiên:
Kiểm tra error rate theo endpoint và loại lỗi để xác định phạm vi ảnh hưởng.
Kiểm tra latency, traffic và dependency health để tìm nguyên nhân liên quan.
Kiểm tra deployment, configuration và các thay đổi gần nhất trước khi alert xảy ra.
Mitigation tạm thời: Rollback thay đổi đáng ngờ; giảm hoặc giới hạn traffic nếu hệ thống quá tải; sử dụng fallback/degraded mode nếu có.
Owner: on-call-engineer
Alert 3
Tên: cost_budget_exceeded
Severity: warning
SLI/SLO liên quan: Daily service cost ≤ 2.5 USD/day
Điều kiện và thời gian duy trì: daily_cost_usd > 2.5
Ảnh hưởng tới người dùng: Không gây ảnh hưởng trực tiếp ngay lập tức, nhưng chi phí tăng cao kéo dài có thể ảnh hưởng đến capacity và khả năng duy trì SLO.
Ba bước kiểm tra đầu tiên:
Kiểm tra cost breakdown để xác định workload/service gây tăng chi phí.
Kiểm tra traffic, request volume và resource usage so với baseline.
Kiểm tra các thay đổi gần đây hoặc usage pattern bất thường có thể làm tăng chi phí.
Mitigation tạm thời: Giảm workload không thiết yếu, áp dụng rate limit hoặc budget guardrail, và tạm dừng workload không cần thiết nếu cần.
Owner: team-lead