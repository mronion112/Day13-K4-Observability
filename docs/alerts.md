# Alert Runbook

All alerts are symptom-based and map back to the SLOs in `config/slo.yaml` and the six dashboard panels in `config/dashboard.yaml`. During an incident, use the same investigation path for the demo: Metrics -> Traces -> Logs -> Root cause.

## alert-high-latency-p95

- Name: `high_latency_p95`
- Severity: warning
- Related SLI/SLO: `latency_p95_ms`
- Condition and duration: `latency_p95_ms > 2000 for 5m`
- User impact: Users wait longer for `/chat` responses; repeated slow responses can make the AI assistant feel unavailable.
- First checks:
  - Open the latency dashboard panel and compare p50, p95, and p99 for the last 60 minutes.
  - Compare the current p95 with the official challenge threshold in `config/challenge.json`.
  - Check whether traffic increased at the same time; if traffic is normal, inspect slow traces in Langfuse.
  - Search `data/logs.jsonl` for high `latency_ms` rows and group them by `feature`, `model`, and `correlation_id`.
- Temporary mitigation: Disable the active practice incident if one is enabled, reduce concurrency in load tests, or route the team to a simpler prompt/retrieval path while the slow component is identified.
- Owner: Team AK47 / SRE & Alerts Engineer

## alert-high-error-rate

- Name: `high_error_rate`
- Severity: critical
- Related SLI/SLO: `error_rate_pct`
- Condition and duration: `error_rate_pct > 2 for 5m`
- User impact: Users receive failed requests or missing answers from `/chat`.
- First checks:
  - Open the error dashboard panel and identify the dominant `error_type`.
  - Pick a failed request and use its `correlation_id` to find the matching trace and log entries.
  - Check recent changes or enabled incidents that could affect API, RAG, prompt resolution, or LLM generation.
- Temporary mitigation: Roll back the latest risky change, disable the injected incident, or return to local prompt fallback if Langfuse prompt fetching is the failing path.
- Owner: Team AK47 / SRE & Alerts Engineer

## alert-quality-score-drop

- Name: `quality_score_drop`
- Severity: warning
- Related SLI/SLO: `quality_score_avg`
- Condition and duration: `quality_score_avg < 0.75 for 10m`
- User impact: The API may still respond, but answers are lower quality, incomplete, or less grounded in retrieved documents.
- First checks:
  - Open the quality dashboard panel and confirm whether the drop affects all features or one feature only.
  - Inspect Langfuse traces for affected requests and compare `prompt_name`, `prompt_label`, `prompt_version`, and retrieved document count.
  - Search logs by `feature` and `correlation_id` to verify answer previews, latency, and token usage around the drop.
- Temporary mitigation: Roll back the Langfuse prompt label to the last known good version, disable the quality-related incident, or use the local prompt fallback while investigating.
- Owner: Team AK47 / SRE & Alerts Engineer

## alert-daily-cost-budget-breach

- Name: `daily_cost_budget_breach`
- Severity: warning
- Related SLI/SLO: `daily_cost_usd`
- Condition and duration: `daily_cost_usd > 2.5 for 1d`
- User impact: The system may keep working, but the team risks exceeding the planned cost budget for the lab.
- First checks:
  - Open the cost and token dashboard panels and identify whether input or output tokens are driving the increase.
  - Compare traffic rate with cost per request to separate real load growth from unusually expensive generations.
  - Inspect traces with high token usage and match them to logs using `correlation_id`.
- Temporary mitigation: Limit load-test concurrency, shorten test runs, reduce prompt/context size, or pause nonessential traffic until the budget driver is confirmed.
- Owner: Team AK47 / SRE & Alerts Engineer
