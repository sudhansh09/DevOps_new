"""
Zero-Dependency Standalone E-Governance Portal Server & In-Process Dispatcher
Supports both:
1. Live network socket mode (http.server) for Docker, Kubernetes, and local CLI
2. In-process direct dispatcher for sandboxed execution without network sockets
"""
import sys
import json
import time
import uuid
import random
from datetime import datetime
from io import BytesIO

START_TIME = time.time()

# In-memory store & metrics state
STATE = {
    "requests_total": {
        ("GET", "/healthz", "200"): 0,
        ("GET", "/ready", "200"): 0,
        ("GET", "/metrics", "200"): 0,
        ("GET", "/api/v1/services", "200"): 0,
        ("POST", "/api/v1/applications", "201"): 0,
        ("GET", "/api/v1/applications", "200"): 0,
        ("POST", "/api/v1/grievances", "201"): 0,
        ("POST", "/api/v1/applications", "400"): 0,
    },
    "health_status": 1.0,
    "active_grievances": 14,
    "applications_processed": {
        "CIVIL-BIRTH-CERT": 42,
        "LAND-MUTATION-REC": 18,
        "BIZ-TRADE-LICENSE": 29
    },
    "chaos": {
        "inject_latency_ms": 0,
        "error_rate": 0.0,
        "simulate_unhealthy": False
    },
    "applications": {},
    "grievances": {}
}

SERVICES = [
    {
        "service_code": "CIVIL-BIRTH-CERT",
        "name": "Issuance of Birth Certificate",
        "department": "Department of Civil Registration",
        "sla_days": 3,
        "fee_inr": 50.0,
        "description": "Official digitized certificate of birth registration with QR-code verification."
    },
    {
        "service_code": "LAND-MUTATION-REC",
        "name": "Land Record Mutation & Title Transfer",
        "department": "Revenue & Land Administration",
        "sla_days": 7,
        "fee_inr": 250.0,
        "description": "Mutation entry in land record registry following purchase or inheritance."
    },
    {
        "service_code": "BIZ-TRADE-LICENSE",
        "name": "Municipal Trade & Commercial License",
        "department": "Urban Local Bodies / Municipal Corporation",
        "sla_days": 5,
        "fee_inr": 500.0,
        "description": "Commercial license for operating business within municipal jurisdiction."
    },
    {
        "service_code": "PUB-GRIEVANCE-RESOLVE",
        "name": "Citizen Grievance Redressal",
        "department": "Public Grievance Directorate",
        "sla_days": 2,
        "fee_inr": 0.0,
        "description": "Redressal of municipal service, road, sanitation, or utility issues."
    }
]

def record_metric(method, endpoint, status_code):
    key = (method, endpoint, str(status_code))
    STATE["requests_total"][key] = STATE["requests_total"].get(key, 0) + 1

def dispatch_request(method: str, path: str, body: bytes = None, headers: dict = None):
    """
    Direct in-process HTTP dispatcher.
    Returns (status_code, response_body_str, response_headers).
    """
    clean_path = path.split("?")[0]
    headers = headers or {}
    
    # 1. Latency simulation
    if STATE["chaos"]["inject_latency_ms"] > 0 and not clean_path.startswith(("/metrics", "/api/v1/chaos")):
        time.sleep(STATE["chaos"]["inject_latency_ms"] / 1000.0)

    # 2. Chaos Error Injection (500)
    if STATE["chaos"]["error_rate"] > 0 and not clean_path.startswith(("/metrics", "/api/v1/chaos", "/healthz")):
        if random.random() < STATE["chaos"]["error_rate"]:
            record_metric(method, clean_path, 500)
            res = {
                "error": "SimulatedServiceDegradation",
                "message": "Internal Server Error triggered by chaos testing harness"
            }
            return 500, json.dumps(res, indent=2), {"Content-Type": "application/json"}

    # 3. GET routes
    if method == "GET":
        if clean_path == "/healthz":
            if STATE["chaos"]["simulate_unhealthy"]:
                record_metric("GET", "/healthz", 503)
                return 503, json.dumps({"status": "UNHEALTHY", "error": "Liveness probe failed"}, indent=2), {"Content-Type": "application/json"}
            else:
                record_metric("GET", "/healthz", 200)
                return 200, json.dumps({
                    "status": "HEALTHY",
                    "version": "1.0.0",
                    "service": "egov-citizen-portal",
                    "environment": "production",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "uptime_seconds": round(time.time() - START_TIME, 2),
                    "dependencies": {"database": "UP", "identity_vault": "UP"}
                }, indent=2), {"Content-Type": "application/json"}
                
        elif clean_path == "/ready":
            if STATE["chaos"]["simulate_unhealthy"]:
                record_metric("GET", "/ready", 503)
                return 503, json.dumps({"status": "UNREADY"}, indent=2), {"Content-Type": "application/json"}
            else:
                record_metric("GET", "/ready", 200)
                return 200, json.dumps({
                    "status": "READY",
                    "service": "egov-citizen-portal",
                    "ready_for_traffic": True
                }, indent=2), {"Content-Type": "application/json"}
                
        elif clean_path == "/metrics":
            record_metric("GET", "/metrics", 200)
            lines = [
                "# HELP egov_service_health_status Health status of portal: 1=HEALTHY, 0=UNHEALTHY",
                "# TYPE egov_service_health_status gauge",
                f"egov_service_health_status {STATE['health_status']}",
                "# HELP egov_active_grievances_total Active citizen grievances open",
                "# TYPE egov_active_grievances_total gauge",
                f"egov_active_grievances_total {STATE['active_grievances']}",
                "# HELP egov_http_requests_total Total count of HTTP requests",
                "# TYPE egov_http_requests_total counter"
            ]
            for (m, ep, sc), count in STATE["requests_total"].items():
                lines.append(f'egov_http_requests_total{{method="{m}",endpoint="{ep}",status_code="{sc}"}} {count}')
            lines.extend([
                "# HELP egov_http_request_duration_seconds Histogram of request duration",
                "# TYPE egov_http_request_duration_seconds histogram",
                'egov_http_request_duration_seconds_bucket{le="0.05"} 120',
                'egov_http_request_duration_seconds_bucket{le="0.1"} 180',
                'egov_http_request_duration_seconds_bucket{le="0.5"} 195',
                'egov_http_request_duration_seconds_bucket{le="+Inf"} 200',
                'egov_http_request_duration_seconds_sum 14.8',
                'egov_http_request_duration_seconds_count 200',
                "# HELP egov_applications_processed_total Total citizen applications processed",
                "# TYPE egov_applications_processed_total counter"
            ])
            for code, total in STATE["applications_processed"].items():
                lines.append(f'egov_applications_processed_total{{service_code="{code}"}} {total}')
            return 200, "\n".join(lines) + "\n", {"Content-Type": "text/plain; version=0.0.4; charset=utf-8"}
            
        elif clean_path == "/api/v1/services":
            record_metric("GET", "/api/v1/services", 200)
            return 200, json.dumps(SERVICES, indent=2), {"Content-Type": "application/json"}
            
        elif clean_path.startswith("/api/v1/applications/"):
            app_id = clean_path.split("/")[-1]
            if app_id in STATE["applications"]:
                record_metric("GET", "/api/v1/applications", 200)
                return 200, json.dumps(STATE["applications"][app_id], indent=2), {"Content-Type": "application/json"}
            return 404, json.dumps({"error": "Application not found"}, indent=2), {"Content-Type": "application/json"}
            
        elif clean_path.startswith("/api/v1/grievances/"):
            grv_id = clean_path.split("/")[-1]
            if grv_id in STATE["grievances"]:
                return 200, json.dumps(STATE["grievances"][grv_id], indent=2), {"Content-Type": "application/json"}
            return 404, json.dumps({"error": "Grievance not found"}, indent=2), {"Content-Type": "application/json"}
            
        elif clean_path == "/api/v1/chaos/status":
            return 200, json.dumps(STATE["chaos"], indent=2), {"Content-Type": "application/json"}
            
    # 4. POST routes
    elif method == "POST":
        payload = {}
        if body:
            try:
                payload = json.loads(body.decode("utf-8"))
            except Exception:
                pass
                
        if clean_path == "/api/v1/applications":
            service_code = payload.get("service_code")
            if not any(s["service_code"] == service_code for s in SERVICES):
                record_metric("POST", "/api/v1/applications", 400)
                return 400, json.dumps({"detail": f"Invalid service code: {service_code}."}, indent=2), {"Content-Type": "application/json"}

            app_id = f"APP-{uuid.uuid4().hex[:8].upper()}"
            tracking_code = f"EGOV-TRK-{random.randint(100000, 999999)}"
            rec = {
                "application_id": app_id,
                "tracking_code": tracking_code,
                "citizen_id": payload.get("citizen_id"),
                "citizen_name": payload.get("citizen_name"),
                "service_code": service_code,
                "status": "SUBMITTED",
                "submitted_at": datetime.utcnow().isoformat() + "Z",
                "message": "Application logged successfully."
            }
            STATE["applications"][app_id] = rec
            STATE["applications_processed"][service_code] = STATE["applications_processed"].get(service_code, 0) + 1
            record_metric("POST", "/api/v1/applications", 201)
            return 201, json.dumps(rec, indent=2), {"Content-Type": "application/json"}

        elif clean_path == "/api/v1/grievances":
            grv_id = f"GRV-{uuid.uuid4().hex[:8].upper()}"
            rec = {
                "grievance_id": grv_id,
                "ticket_number": f"TKT-WARD{payload.get('ward_number', 1)}-{random.randint(1000, 9999)}",
                "citizen_id": payload.get("citizen_id"),
                "citizen_name": payload.get("citizen_name"),
                "ward_number": payload.get("ward_number", 1),
                "status": "ASSIGNED",
                "sla_hours": 24 if payload.get("priority") == "HIGH" else 48,
                "logged_at": datetime.utcnow().isoformat() + "Z",
                "message": "Grievance dispatched to Municipal Field Unit."
            }
            STATE["grievances"][grv_id] = rec
            STATE["active_grievances"] += 1
            record_metric("POST", "/api/v1/grievances", 201)
            return 201, json.dumps(rec, indent=2), {"Content-Type": "application/json"}

        elif clean_path == "/api/v1/chaos/simulate-crash":
            STATE["chaos"]["simulate_unhealthy"] = True
            STATE["health_status"] = 0.0
            return 200, json.dumps({
                "status": "CHAOS_ACTIVE",
                "action": "CRASH_SIMULATION",
                "message": "Service health set to 0. /healthz will return HTTP 503."
            }, indent=2), {"Content-Type": "application/json"}

        elif clean_path == "/api/v1/chaos/inject-errors":
            rate = 0.8
            if "?" in path:
                for param in path.split("?")[1].split("&"):
                    if param.startswith("error_rate="):
                        rate = float(param.split("=")[1])
            STATE["chaos"]["error_rate"] = rate
            return 200, json.dumps({
                "status": "CHAOS_ACTIVE",
                "action": "ERROR_INJECTION",
                "error_rate": rate,
                "message": f"Service will fail ~{int(rate*100)}% of requests with HTTP 500."
            }, indent=2), {"Content-Type": "application/json"}

        elif clean_path == "/api/v1/chaos/reset":
            STATE["chaos"]["inject_latency_ms"] = 0
            STATE["chaos"]["error_rate"] = 0.0
            STATE["chaos"]["simulate_unhealthy"] = False
            STATE["health_status"] = 1.0
            return 200, json.dumps({
                "status": "HEALTHY",
                "action": "CHAOS_RESET",
                "message": "All failure simulations cleared. Service returned to healthy state."
            }, indent=2), {"Content-Type": "application/json"}

    return 404, json.dumps({"error": "Endpoint not found"}, indent=2), {"Content-Type": "application/json"}
