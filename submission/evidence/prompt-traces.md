# Langfuse prompt và trace evidence

API Langfuse ghi nhận ít nhất 37 traces có tag `lab` tại thời điểm nghiệm thu.
Ảnh danh sách: [trace-list.png](trace-list.png).

Hai trace dùng cùng input `Explain why metrics, traces, and logs work together.`:

| Label | Version | Trace ID | Correlation ID | Metadata | Waterfall |
|---|---:|---|---|---|---|
| baseline | 1 | [`a0c1eafef0c779f51abb0f9204a8fac8`](https://cloud.langfuse.com/project/cmsodbsww022vad0k540vl1nr/traces/a0c1eafef0c779f51abb0f9204a8fac8) | `req-a0c1eafe` | `prompt_source=langfuse` | `run → retrieval + llm_generation` |
| candidate | 2 | [`6e19edd88645a6b1c3d7524ad3bb2cc3`](https://cloud.langfuse.com/project/cmsodbsww022vad0k540vl1nr/traces/6e19edd88645a6b1c3d7524ad3bb2cc3) | `req-6e19edd8` | `prompt_source=langfuse` | `run → retrieval + llm_generation` |

Ảnh trace: [baseline v1](trace-baseline-v1.png) và [candidate v2](trace-candidate-v2.png).

## Promote và rollback

Label `production` đã được chuyển sang version 2, sau đó một request được chạy với trace
[`db1ef1d645c05f883f87d89c76e09380`](https://cloud.langfuse.com/project/cmsodbsww022vad0k540vl1nr/traces/db1ef1d645c05f883f87d89c76e09380),
metadata `prompt_label=production`, `prompt_version=2`. Sau đó `production` được rollback về
version 1 và xác minh lại qua SDK.

- Trước rollback: [prompt-production-v2.png](prompt-production-v2.png)
- Sau rollback: [prompt-rollback.png](prompt-rollback.png)

Prompt `day13-chat` giữ đủ ba biến `feature`, `docs`, `message`. Version 1 có labels
`baseline` và `production`; version 2 có label `candidate`. Script tạo prompt là
`scripts/setup_prompts.py`; script tạo lại trace so sánh là `scripts/generate_prompt_traces.py`.
