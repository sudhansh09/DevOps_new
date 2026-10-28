"""
Pydantic Data Models for E-Governance Citizen Portal API
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

class HealthStatus(BaseModel):
    status: str = Field(..., example="HEALTHY")
    version: str = Field(..., example="1.0.0")
    service: str = Field(..., example="egov-citizen-portal")
    environment: str = Field(..., example="production")
    timestamp: str = Field(..., example="2026-10-28T19:50:00Z")
    uptime_seconds: float = Field(..., example=3600.5)
    dependencies: Dict[str, str] = Field(default_factory=lambda: {"database": "UP", "identity_vault": "UP"})

class GovernanceService(BaseModel):
    service_code: str
    name: str
    department: str
    sla_days: int
    fee_inr: float
    description: str

class ApplicationSubmissionRequest(BaseModel):
    citizen_id: str = Field(..., min_length=8, max_length=20, example="NAT-ID-8839210")
    citizen_name: str = Field(..., min_length=2, max_length=100, example="Arun Kumar")
    service_code: str = Field(..., example="CIVIL-BIRTH-CERT")
    department: str = Field(..., example="Department of Civil Registration")
    details: Dict[str, Any] = Field(default_factory=dict, example={"child_name": "Rohan Kumar", "date_of_birth": "2026-05-12"})

class ApplicationSubmissionResponse(BaseModel):
    application_id: str
    tracking_code: str
    citizen_id: str
    service_code: str
    status: str
    submitted_at: str
    estimated_completion_date: str
    message: str

class GrievanceSubmissionRequest(BaseModel):
    citizen_id: str = Field(..., min_length=8, max_length=20, example="NAT-ID-8839210")
    citizen_name: str = Field(..., min_length=2, max_length=100, example="Arun Kumar")
    ward_number: int = Field(..., ge=1, le=250, example=14)
    category: str = Field(..., example="Sanitation and Waste Management")
    subject: str = Field(..., min_length=5, max_length=150, example="Garbage collection delayed in Sector 4")
    description: str = Field(..., min_length=10, max_length=1000, example="Municipal garbage collection vehicle has not visited Sector 4 for 3 days.")
    priority: str = Field("NORMAL", example="HIGH")

class GrievanceSubmissionResponse(BaseModel):
    grievance_id: str
    ticket_number: str
    status: str
    ward_number: int
    logged_at: str
    assigned_officer: str
    sla_hours: int
    message: str

class ChaosConfig(BaseModel):
    inject_latency_ms: int = Field(0, description="Add artificial latency in milliseconds")
    error_rate: float = Field(0.0, ge=0.0, le=1.0, description="Ratio of requests returning HTTP 500 (0.0 to 1.0)")
    simulate_unhealthy: bool = Field(False, description="Make /healthz return 503 Service Unavailable")
