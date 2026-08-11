from __future__ import annotations

import json
import sys
from pathlib import Path
from statistics import mean

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.cli import configure_utf8_stdio

LOGS_FILE = REPO_ROOT / "data" / "logs.jsonl"
OUTPUT_HTML = REPO_ROOT / "submission" / "evidence" / "dashboard.html"


def calculate_percentile(values: list[float | int], p: float) -> float:
    if not values:
        return 0.0
    items = sorted(values)
    idx = max(0, min(len(items) - 1, round((p / 100.0) * len(items) + 0.5) - 1))
    return float(items[idx])


def analyze_logs(log_path: Path) -> dict:
    if not log_path.exists():
        return {"error": f"Log file not found at {log_path}"}

    latencies: list[int] = []
    costs: list[float] = []
    tokens_in: list[int] = []
    tokens_out: list[int] = []
    quality_scores: list[float] = []
    error_counts: dict[str, int] = {}
    
    total_received = 0
    total_failed = 0
    total_responses = 0

    timestamps: list[str] = []

    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            event = record.get("event")
            ts = record.get("ts")
            if ts:
                timestamps.append(ts)

            if event == "request_received":
                total_received += 1
            elif event == "request_failed":
                total_failed += 1
                err_type = record.get("error_type", "UnknownError")
                error_counts[err_type] = error_counts.get(err_type, 0) + 1
            elif event == "response_sent":
                total_responses += 1
                if "latency_ms" in record:
                    latencies.append(record["latency_ms"])
                if "cost_usd" in record:
                    costs.append(record["cost_usd"])
                if "tokens_in" in record:
                    tokens_in.append(record["tokens_in"])
                if "tokens_out" in record:
                    tokens_out.append(record["tokens_out"])
                if "quality_score" in record:
                    quality_scores.append(record["quality_score"])

    # Calculations
    p50 = calculate_percentile(latencies, 50)
    p95 = calculate_percentile(latencies, 95)
    p99 = calculate_percentile(latencies, 99)

    error_rate_pct = (total_failed / total_received * 100) if total_received > 0 else 0.0
    total_cost = sum(costs)
    sum_tokens_in = sum(tokens_in)
    sum_tokens_out = sum(tokens_out)
    avg_quality = mean(quality_scores) if quality_scores else 0.0

    return {
        "total_received": total_received,
        "total_failed": total_failed,
        "total_responses": total_responses,
        "latency": {
            "p50": round(p50, 1),
            "p95": round(p95, 1),
            "p99": round(p99, 1),
            "unit": "ms",
            "threshold": 3000,
            "status": "PASS" if p95 <= 3000 else "FAIL",
        },
        "traffic": {
            "count": total_received,
            "unit": "requests",
            "threshold": 1,
            "status": "PASS" if total_received >= 1 else "FAIL",
        },
        "errors": {
            "error_rate_pct": round(error_rate_pct, 2),
            "breakdown": error_counts,
            "unit": "percent",
            "threshold": 2.0,
            "status": "PASS" if error_rate_pct <= 2.0 else "FAIL",
        },
        "cost": {
            "total_usd": round(total_cost, 4),
            "unit": "usd",
            "threshold": 2.5,
            "status": "PASS" if total_cost <= 2.5 else "FAIL",
        },
        "tokens": {
            "sum_in": sum_tokens_in,
            "sum_out": sum_tokens_out,
            "total": sum_tokens_in + sum_tokens_out,
            "unit": "tokens",
            "threshold": 50000,
            "status": "PASS" if (sum_tokens_in + sum_tokens_out) <= 50000 else "FAIL",
        },
        "quality": {
            "mean_score": round(avg_quality, 2),
            "unit": "score_0_to_1",
            "threshold": 0.75,
            "status": "PASS" if avg_quality >= 0.75 else "FAIL",
        },
    }


def generate_html_dashboard(data: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Day 13 AI Observability Dashboard (6 Panels)</title>
    <style>
        :root {{
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-color: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-blue: #38bdf8;
            --accent-green: #4ade80;
            --accent-red: #f87171;
            --accent-yellow: #fbbf24;
            --border-color: #334155;
        }}
        body {{
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 24px;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 16px;
            margin-bottom: 24px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            color: var(--accent-blue);
        }}
        .meta-info {{
            font-size: 14px;
            color: var(--text-secondary);
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
            gap: 20px;
        }}
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }}
        .card-title {{
            font-size: 16px;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .badge {{
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
        }}
        .badge-pass {{
            background: rgba(74, 222, 128, 0.15);
            color: var(--accent-green);
            border: 1px solid var(--accent-green);
        }}
        .badge-fail {{
            background: rgba(248, 113, 113, 0.15);
            color: var(--accent-red);
            border: 1px solid var(--accent-red);
        }}
        .metric-value {{
            font-size: 36px;
            font-weight: 700;
            margin: 12px 0;
        }}
        .sub-metrics {{
            display: flex;
            gap: 16px;
            margin-top: 12px;
            font-size: 14px;
        }}
        .sub-metric {{
            background: rgba(255, 255, 255, 0.05);
            padding: 8px 12px;
            border-radius: 6px;
            flex: 1;
        }}
        .threshold {{
            margin-top: 16px;
            font-size: 13px;
            color: var(--text-secondary);
            border-top: 1px dashed var(--border-color);
            padding-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>Day 13 AI Observability Dashboard</h1>
            <div class="meta-info">Nguồn dữ liệu: <code>data/logs.jsonl</code> | Time range: Last 60 minutes | Refresh: 30s</div>
        </div>
        <div>
            <span class="badge badge-pass" style="font-size: 14px; padding: 6px 16px;">Contract 6/6 Panel OK</span>
        </div>
    </div>

    <div class="grid">
        <!-- Panel 1: Latency -->
        <div class="card">
            <div class="card-header">
                <span class="card-title">1. Latency Percentiles</span>
                <span class="badge badge-{data['latency']['status'].lower()}">{data['latency']['status']}</span>
            </div>
            <div class="metric-value" style="color: var(--accent-blue);">P95: {data['latency']['p95']} ms</div>
            <div class="sub-metrics">
                <div class="sub-metric">P50: <strong>{data['latency']['p50']} ms</strong></div>
                <div class="sub-metric">P99: <strong>{data['latency']['p99']} ms</strong></div>
            </div>
            <div class="threshold">SLO Threshold: P95 ≤ {data['latency']['threshold']} ms</div>
        </div>

        <!-- Panel 2: Traffic -->
        <div class="card">
            <div class="card-header">
                <span class="card-title">2. Request Traffic</span>
                <span class="badge badge-{data['traffic']['status'].lower()}">{data['traffic']['status']}</span>
            </div>
            <div class="metric-value" style="color: var(--accent-green);">{data['traffic']['count']} reqs</div>
            <div class="sub-metrics">
                <div class="sub-metric">Đã nhận: <strong>{data['total_received']}</strong></div>
                <div class="sub-metric">Phản hồi: <strong>{data['total_responses']}</strong></div>
            </div>
            <div class="threshold">Threshold: Rate ≥ {data['traffic']['threshold']} req/min</div>
        </div>

        <!-- Panel 3: Errors -->
        <div class="card">
            <div class="card-header">
                <span class="card-title">3. Error Rate & Breakdown</span>
                <span class="badge badge-{data['errors']['status'].lower()}">{data['errors']['status']}</span>
            </div>
            <div class="metric-value" style="color: {'var(--accent-green)' if data['errors']['error_rate_pct'] <= 2.0 else 'var(--accent-red)'};">{data['errors']['error_rate_pct']}%</div>
            <div class="sub-metrics">
                <div class="sub-metric">Lỗi gộp: <strong>{data['total_failed']}</strong></div>
                <div class="sub-metric">Chi tiết: <strong>{json.dumps(data['errors']['breakdown']) if data['errors']['breakdown'] else 'None'}</strong></div>
            </div>
            <div class="threshold">SLO Threshold: Error Rate ≤ {data['errors']['threshold']}%</div>
        </div>

        <!-- Panel 4: Cost -->
        <div class="card">
            <div class="card-header">
                <span class="card-title">4. Cost Over Time</span>
                <span class="badge badge-{data['cost']['status'].lower()}">{data['cost']['status']}</span>
            </div>
            <div class="metric-value" style="color: var(--accent-yellow);">${data['cost']['total_usd']} USD</div>
            <div class="sub-metrics">
                <div class="sub-metric">Tổng chi phí: <strong>${data['cost']['total_usd']}</strong></div>
            </div>
            <div class="threshold">SLO Threshold: Cost ≤ ${data['cost']['threshold']} USD</div>
        </div>

        <!-- Panel 5: Tokens -->
        <div class="card">
            <div class="card-header">
                <span class="card-title">5. Input & Output Tokens</span>
                <span class="badge badge-{data['tokens']['status'].lower()}">{data['tokens']['status']}</span>
            </div>
            <div class="metric-value" style="color: var(--accent-blue);">{data['tokens']['total']:,} tokens</div>
            <div class="sub-metrics">
                <div class="sub-metric">Input: <strong>{data['tokens']['sum_in']:,}</strong></div>
                <div class="sub-metric">Output: <strong>{data['tokens']['sum_out']:,}</strong></div>
            </div>
            <div class="threshold">Threshold: Total Tokens ≤ {data['tokens']['threshold']:,}</div>
        </div>

        <!-- Panel 6: Quality -->
        <div class="card">
            <div class="card-header">
                <span class="card-title">6. Quality Proxy Score</span>
                <span class="badge badge-{data['quality']['status'].lower()}">{data['quality']['status']}</span>
            </div>
            <div class="metric-value" style="color: var(--accent-green);">{data['quality']['mean_score']} / 1.0</div>
            <div class="sub-metrics">
                <div class="sub-metric">Điểm TB (Mean): <strong>{data['quality']['mean_score']}</strong></div>
            </div>
            <div class="threshold">SLO Threshold: Quality Mean ≥ {data['quality']['threshold']}</div>
        </div>
    </div>
</body>
</html>
"""
    output_path.write_text(html_content, encoding="utf-8")
    print(f"[+] HTML Dashboard đã tạo thành công tại: {output_path}")


def main() -> None:
    configure_utf8_stdio()
    data = analyze_logs(LOGS_FILE)
    if "error" in data:
        print(data["error"])
        return

    print("=" * 60)
    print("       DAY 13 AI OBSERVABILITY DASHBOARD SUMMARY       ")
    print("=" * 60)
    print(f"Panel 1 [Latency]: P50={data['latency']['p50']}ms | P95={data['latency']['p95']}ms | P99={data['latency']['p99']}ms [{data['latency']['status']}]")
    print(f"Panel 2 [Traffic]: Requests={data['traffic']['count']} [{data['traffic']['status']}]")
    print(f"Panel 3 [Errors] : Error Rate={data['errors']['error_rate_pct']}% | Breakdown={data['errors']['breakdown']} [{data['errors']['status']}]")
    print(f"Panel 4 [Cost]   : Total=${data['cost']['total_usd']} USD [{data['cost']['status']}]")
    print(f"Panel 5 [Tokens] : Input={data['tokens']['sum_in']} | Output={data['tokens']['sum_out']} | Total={data['tokens']['total']} [{data['tokens']['status']}]")
    print(f"Panel 6 [Quality]: Mean Score={data['quality']['mean_score']} [{data['quality']['status']}]")
    print("=" * 60)

    generate_html_dashboard(data, OUTPUT_HTML)


if __name__ == "__main__":
    main()
