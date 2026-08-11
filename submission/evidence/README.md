# Evidence index

| Yêu cầu | Evidence |
|---|---|
| Log validator 100/100 | [validate-logs.txt](validate-logs.txt) |
| Correlation ID và PII redaction | [logging-pii.md](logging-pii.md) |
| Ít nhất 10 traces | [trace-list.png](trace-list.png) |
| Prompt baseline v1 trace | [trace-baseline-v1.png](trace-baseline-v1.png) |
| Prompt candidate v2 trace | [trace-candidate-v2.png](trace-candidate-v2.png) |
| Promote production lên v2 | [prompt-production-v2.png](prompt-production-v2.png) |
| Rollback production về v1 | [prompt-rollback.png](prompt-rollback.png) |
| Dashboard validator | [validate-dashboard.txt](validate-dashboard.txt) |
| Dashboard runtime 6 panel | [dashboard-runtime.png](dashboard-runtime.png) |
| Challenge Metrics → Traces → Logs | [challenge-investigation.md](challenge-investigation.md) |
| Challenge trace waterfall | [trace-challenge-waterfall.png](trace-challenge-waterfall.png) |
| Public tests và schema checks | [test-results.txt](test-results.txt) |

`cp0-baseline-logs.jsonl` giữ nguyên log baseline ban đầu; `cp1-pre-final-logs.jsonl` giữ
log trung gian trước khi áp dụng context mặc định toàn cục. Hai file được lưu để không xóa
lịch sử quan sát trong quá trình làm lab.
