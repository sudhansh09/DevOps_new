"""
End-to-End Orchestrator and Demonstration Runner
Executes the automated Postman/Newman API regression suite,
and demonstrates simulated failure injection with Prometheus alert generation.
"""
import sys
import time
from pathlib import Path

# Enable UTF-8 safe output for Windows cmd/powershell
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.test_postman_with_python import run_postman_suite
from scripts.simulate_failure import demonstrate_incident_lifecycle

def main():
    print("\n" + "=" * 80)
    print("  [*] E-GOVERNANCE DEVOPS PIPELINE: LOCAL AUTOMATION & DEMONSTRATION")
    print("=" * 80)
    print("Initializing E-Governance microservice environment...")
    time.sleep(0.2)
    
    # 1. Run Automated Postman API Test Suite (Newman replication)
    print("\n>>> RUNNING STEP 1: Automated API Testing (Postman / Newman Suite)")
    api_tests_passed = run_postman_suite("http://127.0.0.1:8000")
    
    if not api_tests_passed:
        print("[FAIL] Postman test suite encountered failures!")
        sys.exit(1)
    else:
        print("[PASS] Automated API Regression Test Suite: 100% Passed (Quality Gate Met)")
        
    # 2. Run Failure Simulation & Alert Evaluation
    print("\n>>> RUNNING STEP 2: Simulated Service Failure & Prometheus Alert Generation")
    demonstrate_incident_lifecycle()
    
    print("\n" + "=" * 80)
    print("  [SUCCESS] ALL PIPELINE STAGES, API TESTS, AND FAILURE ALERT SIMULATIONS VERIFIED!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
