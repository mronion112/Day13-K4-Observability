from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean
from typing import Any

from .logging_config import LOG_PATH
from .metrics import percentile


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.astimezone(timezone.utc)


def load_recent_records(
    path: Path | None = None, *, minutes: int = 60, now: datetime | None = None
) -> list[dict[str, Any]]:
    log_path = path or LOG_PATH
    if not log_path.exists():
        return []
    current = now or datetime.now(timezone.utc)
    cutoff = current - timedelta(minutes=minutes)
    records: list[dict[str, Any]] = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        timestamp = _parse_timestamp(record.get("ts"))
        if timestamp is not None and timestamp >= cutoff:
            records.append(record)
    return records


def build_dashboard_data(records: list[dict[str, Any]]) -> dict[str, Any]:
    responses = [record for record in records if record.get("event") == "response_sent"]
    requests = [record for record in records if record.get("event") == "request_received"]
    failures = [record for record in records if record.get("event") == "request_failed"]

    latencies = [int(record["latency_ms"]) for record in responses if isinstance(record.get("latency_ms"), int)]
    costs = [float(record["cost_usd"]) for record in responses if isinstance(record.get("cost_usd"), (int, float))]
    quality = [float(record["quality_score"]) for record in responses if isinstance(record.get("quality_score"), (int, float))]
    errors = Counter(str(record.get("error_type") or "Unknown") for record in failures)

    per_minute: dict[str, dict[str, float]] = defaultdict(
        lambda: {"requests": 0, "errors": 0, "cost_usd": 0.0}
    )
    for record in records:
        timestamp = _parse_timestamp(record.get("ts"))
        if timestamp is None:
            continue
        bucket = timestamp.strftime("%H:%M")
        if record.get("event") == "request_received":
            per_minute[bucket]["requests"] += 1
        elif record.get("event") == "request_failed":
            per_minute[bucket]["errors"] += 1
        elif record.get("event") == "response_sent" and isinstance(record.get("cost_usd"), (int, float)):
            per_minute[bucket]["cost_usd"] += float(record["cost_usd"])

    return {
        "window_minutes": 60,
        "records": len(records),
        "latency": {
            "p50": percentile(latencies, 50),
            "p95": percentile(latencies, 95),
            "p99": percentile(latencies, 99),
            "threshold": 3000,
            "unit": "ms",
        },
        "traffic": {
            "count": len(requests),
            "rate_per_minute": round(len(requests) / 60, 2),
            "unit": "requests/min",
        },
        "errors": {
            "rate_pct": round((len(failures) / len(requests)) * 100, 2) if requests else 0.0,
            "breakdown": dict(errors),
            "threshold": 2,
            "unit": "%",
        },
        "cost": {
            "total": round(sum(costs), 6),
            "threshold": 2.5,
            "unit": "USD",
        },
        "tokens": {
            "input": sum(
                int(record["tokens_in"])
                for record in responses
                if isinstance(record.get("tokens_in"), int)
            ),
            "output": sum(
                int(record["tokens_out"])
                for record in responses
                if isinstance(record.get("tokens_out"), int)
            ),
            "threshold": 50000,
            "unit": "tokens",
        },
        "quality": {
            "mean": round(mean(quality), 3) if quality else 0.0,
            "threshold": 0.75,
            "unit": "score 0–1",
        },
        "series": [
            {"minute": minute, **values}
            for minute, values in sorted(per_minute.items())
        ],
    }


DASHBOARD_HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Day 13 AI Observability</title>
<style>
:root{font-family:Inter,system-ui,sans-serif;color:#18212f;background:#f4f7fb}body{margin:0;padding:28px}.top{display:flex;justify-content:space-between;align-items:end;margin-bottom:18px}h1{margin:0;font-size:27px}.meta{color:#667085}.grid{display:grid;grid-template-columns:repeat(3,minmax(260px,1fr));gap:16px}.card{background:#fff;border:1px solid #dce3ed;border-radius:14px;padding:18px;box-shadow:0 4px 16px #1e293b0a}.card h2{font-size:15px;margin:0 0 12px;color:#475467}.value{font-size:30px;font-weight:720}.detail{color:#667085;margin-top:8px;font-size:13px}.ok{color:#087a55}.bad{color:#c4320a}.bar{height:8px;background:#e7edf4;border-radius:8px;margin-top:15px;overflow:hidden}.bar span{display:block;height:100%;background:#3478f6}.footer{margin-top:18px;color:#667085;font-size:13px}@media(max-width:900px){.grid{grid-template-columns:1fr 1fr}}@media(max-width:600px){.grid{grid-template-columns:1fr}}
</style></head><body>
<div class="top"><div><h1>Day 13 AI Observability</h1><div class="meta">Source: data/logs.jsonl · Rolling time range: 60 minutes</div></div><div class="meta">Auto-refresh: 30 seconds · <span id="updated">loading…</span></div></div>
<main class="grid" id="grid"></main><div class="footer">Thresholds: latency P95 ≤ 3000 ms · error rate ≤ 2% · cost ≤ $2.50 · tokens ≤ 50,000 · quality ≥ 0.75</div>
<script>
const card=(title,value,detail,status='ok',pct=50)=>`<section class="card"><h2>${title}</h2><div class="value ${status}">${value}</div><div class="detail">${detail}</div><div class="bar"><span style="width:${Math.min(100,Math.max(2,pct))}%"></span></div></section>`;
async function refresh(){const d=await fetch('/dashboard/data').then(r=>r.json());const l=d.latency,e=d.errors,c=d.cost,t=d.tokens,q=d.quality,tr=d.traffic;document.getElementById('grid').innerHTML=
card('Latency percentiles',`${l.p95} ms`,`P50 ${l.p50} · P95 ${l.p95} · P99 ${l.p99} · SLO ≤ ${l.threshold} ms`,l.p95<=l.threshold?'ok':'bad',l.p95/l.threshold*100)+
card('Request traffic',`${tr.count}`,`${tr.rate_per_minute} requests/min · window 60 min`,'ok',tr.count)+
card('Error rate & breakdown',`${e.rate_pct}%`,`Types: ${JSON.stringify(e.breakdown)} · threshold ≤ ${e.threshold}%`,e.rate_pct<=e.threshold?'ok':'bad',e.rate_pct/e.threshold*100)+
card('Cost over time',`$${c.total}`,`Total USD · threshold ≤ $${c.threshold}`,c.total<=c.threshold?'ok':'bad',c.total/c.threshold*100)+
card('Input / output tokens',`${t.input} / ${t.output}`,`Total tokens · threshold ≤ ${t.threshold}`,t.input+t.output<=t.threshold?'ok':'bad',(t.input+t.output)/t.threshold*100)+
card('Quality proxy',`${q.mean}`,`Mean score 0–1 · threshold ≥ ${q.threshold}`,q.mean>=q.threshold?'ok':'bad',q.mean*100);document.getElementById('updated').textContent=`Updated ${new Date().toLocaleTimeString()} · ${d.records} records`;}
refresh();setInterval(refresh,30000);
</script></body></html>"""
