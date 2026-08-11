# Câu hỏi tự kiểm tra

1. Vì sao chỉ nhìn average latency có thể bỏ sót vấn đề?

   Average làm phẳng các request rất chậm nếu phần lớn request còn lại nhanh. P95/P99 phản ánh
   tail latency mà một nhóm người dùng thực sự gặp; challenge này là ví dụ khi retrieval tăng
   khoảng 2.5 giây và P95 vượt SLO.

2. Correlation ID khác trace ID như thế nào?

   Correlation ID là định danh ở lớp ứng dụng để nối các log của cùng request và có thể được
   truyền qua HTTP header. Trace ID là định danh của hệ thống distributed tracing, gom các
   observation/span theo quan hệ cha-con. Một request nên lưu được mapping giữa hai loại ID.

3. Nếu error rate tăng, bạn mở metric, trace hay log trước? Vì sao?

   Mở metric trước để xác nhận mức tăng, loại lỗi và khoảng thời gian; sau đó mở một trace lỗi
   trong cửa sổ đó để tìm span thất bại; cuối cùng dùng correlation ID tìm log chi tiết để chứng
   minh root cause. Đây là luồng Metrics → Traces → Logs.

4. PII cần được scrub trước hay sau khi render JSON?

   Phải scrub trước `JSONRenderer` và trước khi ghi/đẩy log. Các processor tạo exception/stack
   text chạy trước scrub để cả chuỗi phát sinh này cũng được làm sạch.

5. Một alert tốt cần condition, duration, severity và owner như thế nào?

   Condition phải dựa trên triệu chứng/SLO có ngưỡng đo được; duration đủ dài để tránh spike
   ngắn; severity phản ánh tác động người dùng; owner là người/nhóm có quyền xử lý. Alert cũng
   cần runbook gồm bước kiểm tra và mitigation ban đầu.

6. Khi cost tăng nhưng traffic không tăng, bạn sẽ kiểm tra những trường nào?

   Kiểm tra `tokens_in`, `tokens_out`, `cost_usd`, model, prompt name/label/version, output length,
   retry/tool-call và phân phối cost theo request. Cost tăng trong traffic không đổi thường đến
   từ prompt/context dài hơn, output dài hơn, đổi model hoặc retry.

7. Evidence nào đủ để kết luận một span là root cause?

   Cần metric xác nhận triệu chứng/cửa sổ, trace cho thấy span bất thường chiếm phần lớn latency
   hoặc phát sinh lỗi, và log cùng correlation ID xác nhận component/cause cụ thể. Nên có baseline
   so sánh và chứng minh triệu chứng phục hồi sau mitigation.

8. Vì sao `validate_logs.py` đạt 100 chưa đồng nghĩa bài lab đạt 100 điểm?

   Validator chỉ kiểm tra schema, correlation, enrichment và một số mẫu PII. Rubric còn chấm
   trace/prompt version/rollback, dashboard runtime, SLO/alerts, điều tra incident, evidence,
   báo cáo, demo, mức độ hiểu bài và đóng góp Git.
