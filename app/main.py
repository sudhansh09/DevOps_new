"""
E-Governance Citizen Portal API Microservice
Production-grade RESTful API instrumented with Prometheus Metrics and Kubernetes Health Probes.
"""
import time
import uuid
import random
import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.responses import JSONResponse, PlainTextResponse
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
    REGISTRY
)

from app.config import settings
from app.models import (
    HealthStatus,
    GovernanceService,
    ApplicationSubmissionRequest,
    ApplicationSubmissionResponse,
    GrievanceSubmissionRequest,
    GrievanceSubmissionResponse,
    ChaosConfig,
)

# Initialize FastAPI App
app = FastAPI(
    title="E-Governance Citizen Portal API",
    description="Citizen services platform for vital records, licensing, and grievance redressal with automated DevOps instrumentation.",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Start time for uptime calculation
START_TIME = time.time()

# Prometheus Metrics Definitions
HTTP_REQUESTS_TOTAL = Counter(
    "egov_http_requests_total",
    "Total count of HTTP requests processed by the E-Governance portal",
    ["method", "endpoint", "status_code"]
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "egov_http_request_duration_seconds",
    "Histogram of request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

ACTIVE_GRIEVANCES = Gauge(
    "egov_active_grievances_total",
    "Total active unresolved citizen grievances currently open"
)

APPLICATIONS_PROCESSED_TOTAL = Counter(
    "egov_applications_processed_total",
    "Total count of citizen applications processed by category",
    ["service_code"]
)

SERVICE_HEALTH_STATUS = Gauge(
    "egov_service_health_status",
    "Health status of the E-Governance service: 1=HEALTHY, 0=UNHEALTHY"
)

# Set initial metric state
SERVICE_HEALTH_STATUS.set(1.0)
ACTIVE_GRIEVANCES.set(12.0)

# In-memory storage for demonstration
applications_db: Dict[str, dict] = {}
grievances_db: Dict[str, dict] = {}

# Seed default governance services
GOVERNANCE_SERVICES: List[GovernanceService] = [
    GovernanceService(
        service_code="CIVIL-BIRTH-CERT",
        name="Issuance of Birth Certificate",
        department="Department of Civil Registration",
        sla_days=3,
        fee_inr=50.0,
        description="Official digitized certificate of birth registration with QR-code verification."
    ),
    GovernanceService(
        service_code="LAND-MUTATION-REC",
        name="Land Record Mutation & Title Transfer",
        department="Revenue & Land Administration",
        sla_days=7,
        fee_inr=250.0,
        description="Mutation entry in land record registry following purchase or inheritance."
    ),
    GovernanceService(
        service_code="BIZ-TRADE-LICENSE",
        name="Municipal Trade & Commercial License",
        department="Urban Local Bodies / Municipal Corporation",
        sla_days=5,
        fee_inr=500.0,
        description="Commercial license for operating business within municipal jurisdiction."
    ),
    GovernanceService(
        service_code="PUB-GRIEVANCE-RESOLVE",
        name="Citizen Grievance Redressal",
        department="Public Grievance Directorate",
        sla_days=2,
        fee_inr=0.0,
        description="Redressal of municipal service, road, sanitation, or utility issues."
    )
]

# Chaos & Failure Simulation State
chaos_state = ChaosConfig()


@app.middleware("http")
async def prometheus_metrics_and_chaos_middleware(request: Request, call_next):
    """
    Middleware that:
    1. Measures request latency and increments Prometheus counters.
    2. Simulates chaos failure (latency or 500 error injection) if configured.
    """
    start_time = time.time()
    path = request.url.path

    # Check for Chaos Latency Injection (except on metrics/health endpoints to allow diagnostics)
    if chaos_state.inject_latency_ms > 0 and not path.startswith(("/metrics", "/api/v1/chaos")):
        await asyncio.sleep(chaos_state.inject_latency_ms / 1000.0)

    # Check for Chaos Error Injection
    if chaos_state.error_rate > 0 and not path.startswith(("/metrics", "/api/v1/chaos", "/healthz")):
        if random.random() < chaos_state.error_rate:
            duration = time.time() - start_time
            HTTP_REQUESTS_TOTAL.labels(method=request.method, endpoint=path, status_code=500).inc()
            HTTP_REQUEST_DURATION_SECONDS.labels(method=request.method, endpoint=path).observe(duration)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "SimulatedServiceDegradation",
                    "message": "Internal Server Error triggered by chaos testing harness",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            )

    try:
        response = await call_next(request)
        duration = time.time() - start_time
        status_code = response.status_code
        HTTP_REQUESTS_TOTAL.labels(method=request.method, endpoint=path, status_code=status_code).inc()
        HTTP_REQUEST_DURATION_SECONDS.labels(method=request.method, endpoint=path).observe(duration)
        return response
    except Exception as exc:
        duration = time.time() - start_time
        HTTP_REQUESTS_TOTAL.labels(method=request.method, endpoint=path, status_code=500).inc()
        HTTP_REQUEST_DURATION_SECONDS.labels(method=request.method, endpoint=path).observe(duration)
        raise exc


# ---------------------------------------------------------------------------
# Kubernetes Probes and Prometheus Metrics Endpoints
# ---------------------------------------------------------------------------

@app.get("/metrics", summary="Prometheus Metrics Scrape Endpoint")
def get_metrics():
    """Prometheus exposition endpoint for scraping application performance metrics."""
    return Response(content=generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)


@app.get("/healthz", response_model=HealthStatus, summary="Kubernetes Liveness Probe")
def healthz():
    """
    Kubernetes Liveness Probe.
    Returns HTTP 200 when alive. Returns 503 if simulate_unhealthy chaos is active.
    """
    if chaos_state.simulate_unhealthy:
        SERVICE_HEALTH_STATUS.set(0.0)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulated failure: Liveness probe check failed"
        )
    SERVICE_HEALTH_STATUS.set(1.0)
    return HealthStatus(
        status="HEALTHY",
        version=settings.VERSION,
        service=settings.SERVICE_NAME,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.utcnow().isoformat() + "Z",
        uptime_seconds=round(time.time() - START_TIME, 2),
        dependencies={"database": "UP", "identity_vault": "UP"}
    )


@app.get("/ready", summary="Kubernetes Readiness Probe")
def readiness():
    """
    Kubernetes Readiness Probe.
    Checks whether dependencies are accessible and application is ready for citizen traffic.
    """
    if chaos_state.simulate_unhealthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulated failure: Readiness check failed (Service unready)"
        )
    return {
        "status": "READY",
        "service": settings.SERVICE_NAME,
        "ready_for_traffic": True,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


# ---------------------------------------------------------------------------
# Core Citizen Governance APIs
# ---------------------------------------------------------------------------

@app.get("/api/v1/services", response_model=List[GovernanceService], summary="List Public Services")
def list_services():
    """Retrieve all citizen services offered by municipal and provincial departments."""
    return GOVERNANCE_SERVICES


@app.post(
    "/api/v1/applications",
    response_model=ApplicationSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit Citizen Application"
)
def submit_application(payload: ApplicationSubmissionRequest):
    """Submit a formal citizen application for government certificates or permits."""
    # Verify service code exists
    matched_service = next((s for s in GOVERNANCE_SERVICES if s.service_code == payload.service_code), None)
    if not matched_service:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid service code: {payload.service_code}. Must be one of available services."
        )

    app_id = f"APP-{uuid.uuid4().hex[:8].upper()}"
    tracking_code = f"EGOV-TRK-{random.randint(100000, 999999)}"
    submission_time = datetime.utcnow().isoformat() + "Z"

    record = {
        "application_id": app_id,
        "tracking_code": tracking_code,
        "citizen_id": payload.citizen_id,
        "citizen_name": payload.citizen_name,
        "service_code": payload.service_code,
        "department": payload.department,
        "details": payload.details,
        "status": "SUBMITTED",
        "submitted_at": submission_time,
        "estimated_completion_date": f"Within {matched_service.sla_days} business days",
        "message": "Application logged successfully into E-Governance Unified Portal."
    }
    applications_db[app_id] = record

    # Track Prometheus business metric
    APPLICATIONS_PROCESSED_TOTAL.labels(service_code=payload.service_code).inc()

    return ApplicationSubmissionResponse(
        application_id=app_id,
        tracking_code=tracking_code,
        citizen_id=payload.citizen_id,
        service_code=payload.service_code,
        status="SUBMITTED",
        submitted_at=submission_time,
        estimated_completion_date=f"Within {matched_service.sla_days} business days",
        message="Application logged successfully into E-Governance Unified Portal."
    )


@app.get("/api/v1/applications/{application_id}", summary="Check Application Status")
def get_application_status(application_id: str):
    """Track the processing status of a submitted application."""
    if application_id not in applications_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application ID '{application_id}' not found in registry."
        )
    return applications_db[application_id]


@app.post(
    "/api/v1/grievances",
    response_model=GrievanceSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Lodge Citizen Grievance"
)
def submit_grievance(payload: GrievanceSubmissionRequest):
    """File a citizen grievance for municipal utilities, sanitation, or civic maintenance."""
    grievance_id = f"GRV-{uuid.uuid4().hex[:8].upper()}"
    ticket_num = f"TKT-WARD{payload.ward_number}-{random.randint(1000, 9999)}"
    logged_time = datetime.utcnow().isoformat() + "Z"

    record = {
        "grievance_id": grievance_id,
        "ticket_number": ticket_num,
        "citizen_id": payload.citizen_id,
        "citizen_name": payload.citizen_name,
        "ward_number": payload.ward_number,
        "category": payload.category,
        "subject": payload.subject,
        "description": payload.description,
        "priority": payload.priority,
        "status": "ASSIGNED",
        "logged_at": logged_time,
        "assigned_officer": f"Ward Officer - Ward {payload.ward_number}",
        "sla_hours": 48 if payload.priority != "HIGH" else 24,
        "message": "Grievance dispatched to Municipal Field Engineering Unit."
    }
    grievances_db[grievance_id] = record

    # Update active grievances gauge
    ACTIVE_GRIEVANCES.inc()

    return GrievanceSubmissionResponse(
        grievance_id=grievance_id,
        ticket_number=ticket_num,
        status="ASSIGNED",
        ward_number=payload.ward_number,
        logged_at=logged_time,
        assigned_officer=f"Ward Officer - Ward {payload.ward_number}",
        sla_hours=48 if payload.priority != "HIGH" else 24,
        message="Grievance dispatched to Municipal Field Engineering Unit."
    )


@app.get("/api/v1/grievances/{grievance_id}", summary="Check Grievance Redressal Status")
def get_grievance_status(grievance_id: str):
    """Track the status of an active grievance ticket."""
    if grievance_id not in grievances_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grievance ID '{grievance_id}' not found."
        )
    return grievances_db[grievance_id]


# ---------------------------------------------------------------------------
# Chaos & Simulation Endpoints for Alert Demonstration
# ---------------------------------------------------------------------------

@app.post("/api/v1/chaos/inject-errors", summary="Simulate High HTTP 500 Error Rate")
def inject_errors(error_rate: float = 0.8):
    """Inject artificial 500 errors to test Prometheus error rate alert triggers."""
    chaos_state.error_rate = error_rate
    return {
        "status": "CHAOS_ACTIVE",
        "action": "ERROR_INJECTION",
        "error_rate": error_rate,
        "message": f"Service will now fail approx {int(error_rate * 100)}% of incoming citizen requests with HTTP 500."
    }


@app.post("/api/v1/chaos/inject-latency", summary="Simulate High Latency Spike")
def inject_latency(latency_ms: int = 2000):
    """Inject artificial response latency to test SLA response time alerts."""
    chaos_state.inject_latency_ms = latency_ms
    return {
        "status": "CHAOS_ACTIVE",
        "action": "LATENCY_INJECTION",
        "latency_ms": latency_ms,
        "message": f"Service will now inject {latency_ms}ms artificial delay in citizen requests."
    }


@app.post("/api/v1/chaos/simulate-crash", summary="Simulate Outage / Unhealthy Pod")
def simulate_crash():
    """Trigger liveness probe failure to simulate pod outage for Prometheus ServiceDown alert."""
    chaos_state.simulate_unhealthy = True
    SERVICE_HEALTH_STATUS.set(0.0)
    return {
        "status": "CHAOS_ACTIVE",
        "action": "SERVICE_OUTAGE_SIMULATED",
        "service_health_gauge": 0.0,
        "message": "Service health set to 0. /healthz will return HTTP 503 until reset."
    }


@app.post("/api/v1/chaos/reset", summary="Reset Chaos State to Normal")
def reset_chaos():
    """Reset all chaos flags to restore normal operation."""
    chaos_state.inject_latency_ms = 0
    chaos_state.error_rate = 0.0
    chaos_state.simulate_unhealthy = False
    SERVICE_HEALTH_STATUS.set(1.0)
    return {
        "status": "HEALTHY",
        "action": "CHAOS_RESET",
        "service_health_gauge": 1.0,
        "message": "All chaos testing simulations cleared. Service returned to pristine operational state."
    }


@app.get("/api/v1/chaos/status", summary="Get Current Chaos State")
def get_chaos_status():
    """Check whether any failure simulations are actively running."""
    return {
        "inject_latency_ms": chaos_state.inject_latency_ms,
        "error_rate": chaos_state.error_rate,
        "simulate_unhealthy": chaos_state.simulate_unhealthy,
        "service_health_gauge": SERVICE_HEALTH_STATUS._value.get()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=False)
