# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: AK47
- Repository URL: https://github.com/Donggnp/K4-Day13-2A202601474
- Commit SHA cuối: xem commit cuối trên GitHub sau khi push hoặc chạy `git rev-parse HEAD`.
- Thành viên và vai trò:
  - Nguyễn Phương Đông - 01474: Role API & Middleware, nhóm trưởng.
  - Trần Thị Kiều Trang - 01498: Role SRE & Alerts Engineer.
  - Ngô Minh Phước - 01576: Role Security Engineer.
  - Nguyễn Quý Dũng - 01200: Role Metrics & Dashboard.
  - Nguyễn Nhật Minh - 01950: Role QA & Chief Investigator.

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100.
- Tổng số traces: tối thiểu 40 observations/traces đã hiển thị trên Langfuse trong project `labs13`.
- Số PII leak còn lại: 0.
- Link/đường dẫn dashboard: `submission/evidence/dashboard.html`.
- Kết quả dashboard validator: `submission/evidence/validate_dashboard_result.txt`.
- Kết quả logging validator: `submission/evidence/validate_logs_result.txt`.

## 3. Logging và tracing

- Evidence correlation ID: `submission/evidence/logging_pii_evidence.txt`.
- Evidence PII redaction: `submission/evidence/logging_pii_evidence.txt`.
- Evidence trace waterfall: ảnh chụp Langfuse trace waterfall đặt trong `submission/evidence/` khi nộp.
- Giải thích một span đáng chú ý: challenge trace thuộc feature `monitoring` cho thấy request đi qua agent/RAG/LLM path. Khi incident `rag_slow` bật, latency tăng mạnh nhưng error rate vẫn 0%, nên span/log liên quan được dùng để khoanh vùng vấn đề là tail latency thay vì crash.

## 4. Prompt versioning

- Prompt name: `day13-chat`.
- Version/label baseline: `baseline` -> version 1.
- Version/label candidate: `candidate` -> version 2.
- Trace ID của mỗi version:
  - Baseline v1: `83cd9c5e58e04fc3c6bf15e203fe6b31`.
  - Candidate v2: `ac4dd7096f2985d732464db452de9546`.
- Bằng chứng đổi label hoặc rollback:
  - `production` switched to version 2: `db8f481f27ea036b4822c9c9c4620243`.
  - `production` rolled back to version 1: `4552b148cbaabfa9097a8021c9c5e0f0`.
- Evidence chi tiết: `submission/evidence/langfuse_prompt_versioning.txt`.

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: hợp lệ, 6/6 panel.
- Evidence dashboard: `submission/evidence/dashboard.html`.
- SLO đã chọn và lý do:
  - `latency_p95_ms <= 3000`: giới hạn tail latency cho trải nghiệm người dùng.
  - `error_rate_pct <= 2`: kiểm soát lỗi request.
  - `daily_cost_usd <= 2.5`: giữ chi phí trong ngân sách lab.
  - `quality_score_avg >= 0.75`: theo dõi proxy chất lượng câu trả lời.
- Alert rules và runbook:
  - Rules nằm trong `config/alert_rules.yaml`.
  - SLO nằm trong `config/slo.yaml`.
  - Runbook nằm trong `docs/alerts.md`.
  - Alert chính dùng trong challenge: `high_latency_p95`, threshold `latency_p95_ms > 2000 for 5m`.

## 6. Điều tra challenge

- Challenge ID: `day13-k4-observability-v1`.
- Triệu chứng từ metrics:
  - `latency_p50`: 2653.0 ms.
  - `latency_p95`: 3665.0 ms.
  - `latency_p99`: 3665.0 ms.
  - Latency panel status: FAIL.
  - Error rate: 0.0%.
- Trace ID liên quan:
  - `6322ccc6f1dedf4fac677d25632ef815`, session `k4-challenge-s01`.
  - `af9cbc145cb66f928919161a4287c4d2`, session `k4-challenge-s04`.
  - `fd003c7d17a0c777ff563b7a92f3de03`, session `k4-challenge-s05`.
  - `3070430784c8bee092f4ce8a5b74d187`, session `k4-challenge-s03`.
  - `6978c4aa5fcd213d7d155186f8885d9b`, session `k4-challenge-s02`.
- Log line/correlation ID liên quan:
  - `req-f45226fe`, feature `monitoring`, `latency_ms=3665`.
  - `req-56d36767`, feature `monitoring`, `latency_ms=2654`.
  - `req-4cbff256`, feature `monitoring`, `latency_ms=2653`.
- Root cause: challenge bật incident `rag_slow`; trong `app/mock_rag.py`, khi `STATE["rag_slow"]` là true thì `retrieve()` sleep 2.5 giây, làm các request feature `monitoring` chậm.
- Fix action: tắt incident bằng `python scripts/inject_incident.py --disable`; với hệ thống thật, tối ưu hoặc rollback retrieval/vector-store path trước khi mở lại traffic.
- Preventive measure: giữ alert `high_latency_p95`, dùng dashboard latency để phát hiện triệu chứng, mở trace để khoanh vùng span chậm, rồi tra log theo `correlation_id`.
- Evidence chi tiết: `submission/evidence/challenge_investigation.txt`.

## 7. Đóng góp cá nhân

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Nguyễn Phương Đông - 01474 | Role A: API middleware, correlation ID, exception handler, JSON log context. | Repo main branch | Cách gắn request context vào log để truy vết request end-to-end. |
| Trần Thị Kiều Trang - 01498 | Role D: SLO, alert rules, threshold, alert runbook, mapping alert với CP3. | Repo main branch | Cách thiết kế alert dựa trên triệu chứng người dùng và SLO thay vì tên implementation nội bộ. |
| Ngô Minh Phước - 01576 | Role B: PII scrubbing, regex email/phone/card, kiểm chứng log không lộ PII. | Repo main branch | Cách redact dữ liệu nhạy cảm trước khi ghi log và kiểm tra bằng validator. |
| Nguyễn Quý Dũng - 01200 | Role C: metrics, `error_rate_pct`, dashboard 6 panel, render dashboard từ `data/logs.jsonl`. | Repo main branch | Cách chuyển log runtime thành các nhóm metrics latency, traffic, error, cost, token, quality. |
| Nguyễn Nhật Minh - 01950 | Role E: Langfuse traces, prompt v1/v2, load test, challenge investigation. | Repo main branch | Cách nối metrics -> traces -> logs để chứng minh root cause bằng evidence. |
