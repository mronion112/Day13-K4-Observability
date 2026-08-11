from __future__ import annotations

from app.dashboard import build_dashboard_data


def test_dashboard_aggregates_all_six_panels() -> None:
    records = [
        {"event": "request_received", "ts": "2026-08-11T08:00:00Z"},
        {"event": "request_received", "ts": "2026-08-11T08:00:01Z"},
        {
            "event": "response_sent",
            "ts": "2026-08-11T08:00:02Z",
            "latency_ms": 1200,
            "cost_usd": 0.01,
            "tokens_in": 20,
            "tokens_out": 80,
            "quality_score": 0.9,
        },
        {
            "event": "request_failed",
            "ts": "2026-08-11T08:00:03Z",
            "error_type": "TimeoutError",
        },
    ]

    data = build_dashboard_data(records)

    assert data["latency"]["p95"] == 1200
    assert data["traffic"]["count"] == 2
    assert data["errors"]["rate_pct"] == 50
    assert data["errors"]["breakdown"] == {"TimeoutError": 1}
    assert data["cost"]["total"] == 0.01
    assert data["tokens"] == {
        "input": 20,
        "output": 80,
        "threshold": 50000,
        "unit": "tokens",
    }
    assert data["quality"]["mean"] == 0.9
