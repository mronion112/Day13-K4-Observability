# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`:
- Tổng số traces:
- Số PII leak còn lại:
- Link/đường dẫn dashboard:

## 3. Logging và tracing

- Evidence correlation ID:
- Evidence PII redaction:
- Evidence trace waterfall:
- Giải thích một span đáng chú ý:

## 4. Prompt versioning

- Prompt name:
- Version/label baseline:
- Version/label candidate:
- Trace ID của mỗi version:
- Bằng chứng đổi label hoặc rollback:

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`:
- Evidence dashboard:
- SLO đã chọn và lý do:
- Alert rules và runbook:

## 6. Điều tra challenge

- Challenge ID: `day13-k4-observability-v1` (official challenge, cohort K4).
- Triệu chứng từ metrics: `latency_p95 = 2653 ms`, vượt ngưỡng challenge `2000 ms`; P50 là 151 ms và error rate là 0%, cho thấy lỗi tập trung ở tail latency thay vì lỗi toàn bộ request.
- Trace ID liên quan: trace Langfuse lúc 2026-08-11 09:51 UTC, tìm bằng metadata `correlation_id=req-9fa962a0`; waterfall cho thấy `retrieve` là span chậm.
- Log line/correlation ID liên quan: `req-9fa962a0`, session `k4-challenge-s04`, event `response_sent`, `latency_ms=2654`.
- Root cause: incident chính thức `rag_slow` làm hàm RAG retrieval thêm 2.5 giây delay; đây là nguyên nhân trực tiếp tạo P95 latency vượt threshold.
- Fix action: tắt `rag_slow`, đặt timeout cho retrieval và trả fallback khi vector store/retrieval chậm.
- Preventive measure: alert theo `latency_p95`, trace span `retrieve`, giới hạn thời gian retrieval và load test định kỳ theo feature `monitoring`.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| | | | |
