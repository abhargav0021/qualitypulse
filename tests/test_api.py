from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import create_app


def build_client(tmp_path: Path) -> TestClient:
    app = create_app(tmp_path / "test.db", seed_data=True)
    return TestClient(app)


def test_health_check(tmp_path: Path) -> None:
    client = build_client(tmp_path)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "qualitypulse"}


def test_create_test_case_and_update_status(tmp_path: Path) -> None:
    client = build_client(tmp_path)

    create_response = client.post(
        "/api/test-cases",
        json={
            "title": "Validate login error handling",
            "module": "Authentication",
            "priority": "high",
            "owner": "Bhargav",
            "automated": True,
            "expected_result": "Invalid users see a clear error message.",
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["status"] == "not_started"
    assert created["automated"] is True

    update_response = client.put(
        f"/api/test-cases/{created['id']}/status",
        json={"status": "passed"},
    )

    assert update_response.status_code == 200
    assert update_response.json()["status"] == "passed"


def test_create_defect_requires_existing_linked_test_case(tmp_path: Path) -> None:
    client = build_client(tmp_path)

    response = client.post(
        "/api/defects",
        json={
            "title": "Checkout total is rounded incorrectly",
            "severity": "critical",
            "linked_test_case_id": 9999,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Linked test case not found"


def test_summary_contains_quality_metrics(tmp_path: Path) -> None:
    client = build_client(tmp_path)

    response = client.get("/api/summary")

    assert response.status_code == 200
    summary = response.json()
    assert summary["total_test_cases"] >= 3
    assert "Reports" in summary["modules_under_test"]
    assert set(summary["test_counts"]).issuperset({"passed", "in_progress", "not_started"})
