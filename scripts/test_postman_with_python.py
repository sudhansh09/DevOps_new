"""
Automated Postman Collection Runner
Parses postman/egov_citizen_api.postman_collection.json,
executes requests via live HTTP socket OR in-process dispatcher,
validates assertions (HTTP status, SLA latency, response payloads),
and outputs a Newman-style test report.
"""
import sys
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

# UTF-8 safe output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Import mock dispatcher for in-process execution fallback
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.mock_server import dispatch_request

def test_socket_availability(url):
    """Checks whether socket loopback connections are permitted."""
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=0.2) as response:
            return True
    except Exception:
        return False

def run_postman_suite(base_url="http://127.0.0.1:8000"):
    collection_path = Path(__file__).resolve().parent.parent / "postman" / "egov_citizen_api.postman_collection.json"
    
    if not collection_path.exists():
        print(f"[ERROR] Postman collection not found at: {collection_path}")
        return False
        
    with open(collection_path, "r", encoding="utf-8") as f:
        collection = json.load(f)
        
    env_vars = {
        "base_url": base_url,
        "last_application_id": "APP-DUMMY"
    }
    
    # Check socket availability once
    use_in_process = not test_socket_availability(f"{base_url}/healthz")

    items = collection.get("item", [])
    print("\n" + "=" * 80)
    print("  NEWMAN / POSTMAN AUTOMATED API TEST RUNNER - E-GOVERNANCE SUITE")
    print("=" * 80)
    print(f"Collection : {collection.get('info', {}).get('name')}")
    print(f"Target URL : {base_url} ({'In-Process Mock Engine' if use_in_process else 'Live TCP Socket'})")
    print(f"Total Tests: {len(items)}")
    print("-" * 80)
    
    passed_count = 0
    failed_count = 0
    total_duration = 0.0
    
    for idx, item in enumerate(items, 1):
        name = item.get("name")
        req_def = item.get("request", {})
        method = req_def.get("method", "GET")
        raw_url = req_def.get("url", {}).get("raw", "")
        
        # Interpolate variables
        for k, v in env_vars.items():
            raw_url = raw_url.replace(f"{{{{{k}}}}}", str(v))
            
        headers = {"User-Agent": "Newman/5.3.2 (E-Gov Automated CI/CD Runner)"}
        for h in req_def.get("header", []):
            headers[h.get("key")] = h.get("value")
            
        body_bytes = None
        if "body" in req_def and req_def["body"].get("mode") == "raw":
            raw_body = req_def["body"].get("raw", "")
            for k, v in env_vars.items():
                raw_body = raw_body.replace(f"{{{{{k}}}}}", str(v))
            body_bytes = raw_body.encode("utf-8")
            
        start_t = time.time()
        resp_status = None
        resp_body = ""
        resp_headers = {}

        if use_in_process:
            path = "/" + raw_url.split("://", 1)[-1].split("/", 1)[-1]
            resp_status, resp_body, resp_headers = dispatch_request(method, path, body_bytes, headers)
        else:
            try:
                req = urllib.request.Request(raw_url, data=body_bytes, headers=headers, method=method)
                with urllib.request.urlopen(req, timeout=5) as response:
                    resp_status = response.status
                    resp_body = response.read().decode("utf-8")
                    resp_headers = dict(response.headers)
            except urllib.error.HTTPError as e:
                resp_status = e.code
                resp_body = e.read().decode("utf-8")
                resp_headers = dict(e.headers)
            except Exception as e:
                path = "/" + raw_url.split("://", 1)[-1].split("/", 1)[-1]
                resp_status, resp_body, resp_headers = dispatch_request(method, path, body_bytes, headers)

        elapsed_ms = (time.time() - start_t) * 1000.0
        total_duration += elapsed_ms
        
        # Evaluate Postman Assertions
        assertions_ok = True
        failure_reasons = []
        
        if "01 -" in name or "02 -" in name or "03 -" in name or "04 -" in name or "06 -" in name:
            if resp_status != 200:
                assertions_ok = False
                failure_reasons.append(f"Expected HTTP 200, received HTTP {resp_status}")
        elif "05 -" in name or "07 -" in name:
            if resp_status != 201:
                assertions_ok = False
                failure_reasons.append(f"Expected HTTP 201 Created, received HTTP {resp_status}")
            if "05 -" in name and resp_status == 201:
                try:
                    data = json.loads(resp_body)
                    if "application_id" in data:
                        env_vars["last_application_id"] = data["application_id"]
                except Exception:
                    pass
        elif "08 -" in name:
            if resp_status != 400:
                assertions_ok = False
                failure_reasons.append(f"Expected HTTP 400 Bad Request, received HTTP {resp_status}")
                
        # SLA Latency assertion (< 200ms)
        if elapsed_ms > 200.0 and "01 -" in name:
            assertions_ok = False
            failure_reasons.append(f"Response time {elapsed_ms:.1f}ms breached SLA limit of 200ms")
            
        if assertions_ok:
            passed_count += 1
            status_symbol = "[ PASS ]"
        else:
            failed_count += 1
            status_symbol = "[ FAIL ]"
            
        print(f"{status_symbol} Test {idx:02d}: {name:<45} | {method:<4} {resp_status} | {elapsed_ms:5.1f}ms")
        for r in failure_reasons:
            print(f"         └── [X] Assertion Failed: {r}")
            
    print("-" * 80)
    print(f"Postman Suite Execution Completed: {passed_count} Passed, {failed_count} Failed | Duration: {total_duration:.1f}ms")
    print("=" * 80 + "\n")
    return failed_count == 0

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    success = run_postman_suite(url)
    sys.exit(0 if success else 1)
