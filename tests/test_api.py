"""
Unit and Integration Tests for E-Governance API
Executed automatically in GitLab CI/CD pipeline during 'test' stage.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_healthz_healthy():
    """Test Kubernetes Liveness Probe when healthy."""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "uptime_seconds" in data
    assert data["service"] == "egov-citizen-portal"

def test_readiness_probe():
    """Test Kubernetes Readiness Probe."""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "READY"
    assert data["ready_for_traffic"] is True

def test_prometheus_metrics_endpoint():
    """Verify Prometheus scrapes can parse metrics format."""
    # Issue a dummy request first to increment counters
    client.get("/api/v1/services")
    
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    body = response.text
    assert "egov_http_requests_total" in body
    assert "egov_http_request_duration_seconds" in body
    assert "egov_service_health_status" in body

def test_list_services():
    """Verify public citizen services catalog."""
    response = client.get("/api/v1/services")
    assert response.status_code == 200
    services = response.json()
    assert len(services) >= 4
    service_codes = [s["service_code"] for s in services]
    assert "CIVIL-BIRTH-CERT" in service_codes
    assert "LAND-MUTATION-REC" in service_codes

def test_submit_and_get_application():
    """Verify citizen application lifecycle: submit -> track."""
    payload = {
        "citizen_id": "NAT-ID-9928192",
        "citizen_name": "Priya Sharma",
        "service_code": "CIVIL-BIRTH-CERT",
        "department": "Department of Civil Registration",
        "details": {"child_name": "Aarav Sharma", "date_of_birth": "2026-04-10"}
    }
    
    # 1. Submit
    create_res = client.post("/api/v1/applications", json=payload)
    assert create_res.status_code == 201
    created_data = create_res.json()
    app_id = created_data["application_id"]
    assert app_id.startswith("APP-")
    assert created_data["status"] == "SUBMITTED"
    assert "tracking_code" in created_data
    
    # 2. Track
    get_res = client.get(f"/api/v1/applications/{app_id}")
    assert get_res.status_code == 200
    assert get_res.json()["citizen_name"] == "Priya Sharma"

def test_submit_grievance():
    """Verify citizen grievance filing."""
    grievance = {
        "citizen_id": "NAT-ID-7721890",
        "citizen_name": "Vikram Seth",
        "ward_number": 12,
        "category": "Sanitation and Waste Management",
        "subject": "Street light malfunction in Main Cross",
        "description": "Streetlight #42 has been non-functional for past 5 days.",
        "priority": "HIGH"
    }
    response = client.post("/api/v1/grievances", json=grievance)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "ASSIGNED"
    assert data["ward_number"] == 12
    assert "ticket_number" in data

def test_chaos_simulation_and_recovery():
    """Verify chaos testing harness injects and cleans up failures."""
    # Simulate crash
    crash_res = client.post("/api/v1/chaos/simulate-crash")
    assert crash_res.status_code == 200
    
    # Health probe should now return 503
    unhealthy_res = client.get("/healthz")
    assert unhealthy_res.status_code == 503
    
    # Reset
    reset_res = client.post("/api/v1/chaos/reset")
    assert reset_res.status_code == 200
    
    # Health probe must be healthy again
    healthy_res = client.get("/healthz")
    assert healthy_res.status_code == 200
    assert healthy_res.json()["status"] == "HEALTHY"
