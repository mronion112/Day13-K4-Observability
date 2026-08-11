# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: Quang Dao (bài làm cá nhân)
- Repository URL: https://github.com/mronion112/Day13-K4-Observability
- Commit SHA cuối: cập nhật sau commit nghiệm thu
- Thành viên và vai trò: Quang Dao — triển khai và nghiệm thu toàn bộ lab

## 2. Kết quả kỹ thuật

- Điểm baseline `validate_logs.py`: 30/100
- Điểm cuối `validate_logs.py`: 100/100 ([evidence](evidence/validate-logs.txt))
- Tổng số traces: ít nhất 37 traces có tag `lab` trên Langfuse ([ảnh danh sách](evidence/trace-list.png))
- Số PII leak còn lại: 0
- Link/đường dẫn dashboard: `http://127.0.0.1:8000/dashboard` — [ảnh runtime](evidence/dashboard-runtime.png)

## 3. Logging và tracing

- Evidence correlation ID: `req-e3b71a6a` xuyên API → retrieval → model → response ([chi tiết](evidence/logging-pii.md))
- Evidence PII redaction: email, số điện thoại và thẻ test đều được thay bằng `[REDACTED_*]` ([chi tiết](evidence/logging-pii.md))
- Evidence trace waterfall: trace challenge [`67b99cb08e93951aeaecf1f758648c9c`](https://cloud.langfuse.com/project/cmsodbsww022vad0k540vl1nr/traces/67b99cb08e93951aeaecf1f758648c9c) — [ảnh](evidence/trace-challenge-waterfall.png)
- Giải thích một span đáng chú ý: retrieval mất khoảng 2.507 giây, trong khi generation chỉ khoảng 0.153 giây; retrieval là bottleneck của challenge.

## 4. Prompt versioning

- Prompt name: `day13-chat`
- Version/label baseline: version 1 — labels `baseline`, `production`
- Version/label candidate: version 2 — label `candidate`
- Trace ID của mỗi version: baseline `a0c1eafef0c779f51abb0f9204a8fac8`; candidate `6e19edd88645a6b1c3d7524ad3bb2cc3` ([evidence](evidence/prompt-traces.md))
- Bằng chứng đổi label hoặc rollback: production-v2 trace `db1ef1d645c05f883f87d89c76e09380`; [trước rollback](evidence/prompt-production-v2.png) và [sau rollback](evidence/prompt-rollback.png).

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: `HỢP LỆ: 6/6 panel` ([evidence](evidence/validate-dashboard.txt))
- Evidence dashboard: [dashboard-runtime.png](evidence/dashboard-runtime.png)
- SLO đã chọn và lý do: P95 ≤ 3000 ms (99.5%), error ≤ 2% (99%), daily cost ≤ 2.5 USD, quality ≥ 0.75; các ngưỡng bảo vệ latency, reliability, budget và answer utility.
- Alert rules và runbook: ba symptom-based alerts trong `config/alert_rules.yaml`; quy trình Metrics → Traces → Logs và mitigation trong `docs/alerts.md`.

## 6. Điều tra challenge

- Challenge ID: `day13-k4-observability-v1` (`rag_slow`, feature `monitoring`)
- Triệu chứng từ metrics: P95 10299 ms > SLO 3000 ms; error rate 0%.
- Trace ID liên quan: `67b99cb08e93951aeaecf1f758648c9c`, tổng 3.598 giây.
- Log line/correlation ID liên quan: `req-e3b71a6a`, retrieval 2505 ms, generation 151 ms ([điều tra đầy đủ](evidence/challenge-investigation.md)).
- Root cause: incident tạo độ trễ khoảng 2.5 giây trong retrieval/RAG; span retrieval chiếm phần lớn request.
- Fix action: tắt incident; thêm retrieval timeout và fallback cache; giảm concurrency khi mitigation.
- Preventive measure: theo dõi retrieval span latency, circuit breaker, P95 alert và diễn tập runbook định kỳ.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Quang Dao | Logging/PII, tracing/prompt, dashboard/SLO/alerts, challenge và report | Commit nghiệm thu cuối | Hiểu luồng Metrics → Traces → Logs, correlation context và rollback prompt an toàn |
