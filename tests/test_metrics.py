from app.metrics import percentile, record_error, record_request, snapshot


def test_percentile_basic() -> None:
    assert percentile([100, 200, 300, 400], 50) >= 100


def test_snapshot_metrics() -> None:
    record_request(latency_ms=150, cost_usd=0.001, tokens_in=50, tokens_out=100, quality_score=0.8)
    record_error("HTTPException")

    sn = snapshot()
    assert "error_rate_pct" in sn
    assert sn["traffic"] >= 2
    assert sn["error_rate_pct"] > 0
    assert "HTTPException" in sn["error_breakdown"]

