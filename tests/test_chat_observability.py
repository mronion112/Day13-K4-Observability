from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app import logging_config
from app.main import app


def test_chat_response_log_exposes_quality_for_dashboard(
    monkeypatch, tmp_path: Path
) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    with TestClient(app) as client:
        response = client.post(
            "/chat",
            json={
                "user_id": "student-01",
                "session_id": "session-01",
                "feature": "qa",
                "message": "Explain observability",
            },
        )

    assert response.status_code == 200
    events = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    response_event = next(event for event in events if event["event"] == "response_sent")
    assert response_event["quality_score"] == response.json()["quality_score"]


def test_chat_propagates_correlation_context_and_redacts_pii(
    monkeypatch, tmp_path: Path
) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    with TestClient(app) as client:
        response = client.post(
            "/chat",
            headers={"x-request-id": "req-deadbeef"},
            json={
                "user_id": "student@example.com",
                "session_id": "session-02",
                "feature": "monitoring",
                "message": "Call 090 123 4567 about the monitoring policy",
            },
        )

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "req-deadbeef"
    assert response.json()["correlation_id"] == "req-deadbeef"
    records = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    api_records = [record for record in records if record.get("service") == "api"]
    assert api_records
    for record in api_records:
        assert record["correlation_id"] == "req-deadbeef"
        assert record["session_id"] == "session-02"
        assert record["feature"] == "monitoring"
        assert record["model"]
        assert record["env"]
        assert "user_id_hash" in record
    assert "090 123 4567" not in log_path.read_text(encoding="utf-8")
