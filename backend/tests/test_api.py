from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthz() -> None:
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_ingest_chat_and_trace() -> None:
    ingest = client.post(
        "/api/knowledge/ingest",
        json={
            "source": "kb://faq/auth.md",
            "content": (
                "Password reset:\nUse forgot password on login page.\n\n"
                "Timeout troubleshooting:\nRetry after checking API key and region."
            ),
        },
    )
    assert ingest.status_code == 200
    assert ingest.json()["chunk_count"] >= 1

    chat = client.post(
        "/api/chat",
        json={
            "session_id": "test-session",
            "question": "How can I reset my password?",
            "customer_tier": "pro",
        },
    )
    assert chat.status_code == 200
    payload = chat.json()
    assert payload["trace_id"]
    assert len(payload["citations"]) >= 1

    trace = client.get(f"/api/traces/{payload['trace_id']}")
    assert trace.status_code == 200
    assert len(trace.json()["events"]) >= 2


def test_run_evals() -> None:
    # Ensure there is at least one knowledge item before eval.
    client.post(
        "/api/knowledge/ingest",
        json={
            "source": "kb://faq/plans.md",
            "content": (
                "SSO support:\nPro and enterprise plans support SSO.\n\n"
                "Timeout issues:\nUse retry with exponential backoff."
            ),
        },
    )
    res = client.post("/api/evals/run", json={"eval_suite_id": "default"})
    assert res.status_code == 200
    data = res.json()
    assert "metrics" in data
    assert data["metrics"]["total_cases"] >= 1

