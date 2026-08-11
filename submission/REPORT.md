Báo cáo Day 13 Observability
# 1. Thông tin nhóm
Tên nhóm: Chưa có thông tin
Repository URL: Chưa có thông tin
Commit SHA cuối: Chưa có thông tin
Thành viên và vai trò: Chưa có thông tin
# 2. Kết quả kỹ thuật
Điểm validate_logs.py: Chưa có thông tin
Tổng số traces: Chưa xác định được từ log hiện tại. Log xác nhận tracing_enabled: true nhưng chưa có trace_id/span_id.
Số PII leak còn lại: Không phát hiện PII plaintext trong log được cung cấp. Email, số điện thoại và credit card đều được redacted.
Link/đường dẫn dashboard: Chưa có thông tin
# 3. Logging và tracing

Evidence correlation ID:

req-fd39978d
req-9eabd17e
req-70e4f259
req-41b8c25d
Các request đều có correlation_id và có thể đối chiếu giữa request_received và response_sent.

Evidence PII redaction:

req-41000292: email được hiển thị dưới dạng [REDACTED_EMAIL]
req-9e18ee29: phone được hiển thị dưới dạng [REDACTED_PHONE_VN]
req-88c82ab9: credit card được hiển thị dưới dạng [REDACTED_CREDIT_CARD]
Các request retry sau đó cũng tiếp tục sử dụng dạng redacted.

Evidence trace waterfall:

Application log xác nhận tracing đã được bật với "tracing_enabled": true.
Tuy nhiên log hiện tại chưa chứa trace_id, span_id hoặc start/end time của từng span nên chưa thể dựng trace waterfall đầy đủ.

Giải thích một span đáng chú ý:

Request req-9eabd17e với câu hỏi "How should an engineer investigate tail latency?" có latency 3099 ms.
Trước khi bật incident rag_slow, cùng challenge có latency khoảng 268–488 ms.
Sau khi bật rag_slow, nhiều request tăng lên khoảng 2.7–3.1 giây.
Điều này cho thấy rag_slow gây ra regression rõ rệt về latency, mặc dù log hiện tại chưa có span ID để xác định chính xác operation bên trong RAG gây delay.
# 4. Prompt versioning
Prompt name: Chưa có thông tin
Version/label baseline: Chưa có thông tin
Version/label candidate: Chưa có thông tin
Trace ID của mỗi version: Chưa có thông tin
Bằng chứng đổi label hoặc rollback: Chưa có thông tin
# 5. Dashboard, SLO và alerts
Kết quả validate_dashboard.py: Chưa có thông tin
Evidence dashboard: Chưa có thông tin
SLO đã chọn và lý do:
Đề xuất theo dõi API tail latency bằng p95/p99.
Lý do: challenge cho thấy latency tăng mạnh từ khoảng 250–490 ms lên khoảng 2.7–3.6 giây khi rag_slow được bật.
Alert rules và runbook:
Chưa có thông tin cụ thể trong log.
Nên có alert cho p95/p99 latency vượt SLO và runbook để kiểm tra metrics → trace → logs → RAG dependency.
# 6. Điều tra challenge

Challenge ID: rag_slow

Triệu chứng từ metrics:

Khi rag_slow disabled, latency chủ yếu khoảng 250–490 ms.
Khi rag_slow enabled, latency tăng lên khoảng 2.7–3.6 giây.
Ví dụ:
req-fd39978d: 488 ms
req-bf64a606: 301 ms
req-9eabd17e: 3099 ms
req-00320c81: 2872 ms
req-701219f4: 2817 ms
req-f9eaf656: 2772 ms
req-a3dd1abd: 3563 ms
req-7b233611: 3549 ms

Trace ID liên quan:

Chưa có trace_id/span_id trong log.
Có thể sử dụng correlation_id để truy vết request.

Log line/correlation ID liên quan:

req-7533e28a: incident_enabled cho rag_slow
req-a3dd1abd: latency 3563 ms
req-9170b54c: latency 2963 ms
req-101a08fe: latency 2920 ms
req-5b77a365: latency 2920 ms
req-7b233611: latency 3549 ms
req-3c04a8f8: latency 2908 ms
req-aaa77b31: latency 2921 ms
req-f429bdd1: latency 2920 ms
req-54206987: latency 2928 ms
req-12b9b2ad: latency 2902 ms

Root cause:

Incident rag_slow gây regression rõ rệt về API latency.
Khi incident được bật, latency tăng từ khoảng 250–490 ms lên khoảng 2.7–3.6 giây.
Việc bật/tắt incident và quan sát latency tương ứng cung cấp bằng chứng mạnh rằng rag_slow là nguyên nhân của latency regression.
Chưa đủ evidence để xác định chính xác span/operation nội bộ nào trong RAG gây ra delay vì log chưa có trace_id/span_id.

Fix action:

Disable incident rag_slow để khôi phục latency.
Log có evidence:
incident_disabled với name: "rag_slow".

Preventive measure:

Theo dõi p95/p99 API latency.
Duy trì correlation ID xuyên suốt request, trace và log.
Bổ sung trace_id và span_id vào application logs.
Dùng trace waterfall để xác định chính xác RAG span gây chậm.
Thiết lập alert khi tail latency vượt SLO.
Xây dựng runbook cho RAG latency regression.
Tiếp tục redaction PII trước khi ghi request logs.
Thực hiện controlled incident test và rollback để phát hiện regression sớm.
# 7. Đóng góp cá nhân
Thành viên	Phần việc	Commit/PR	Điều đã học
Chưa có thông tin	Chưa có thông tin	Chưa có thông tin	Chưa có thông tin
Chưa có thông tin	Chưa có thông tin	Chưa có thông tin	Chưa có thông tin
Chưa có thông tin	Chưa có thông tin	Chưa có thông tin	Chưa có thông tin