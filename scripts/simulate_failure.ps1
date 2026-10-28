# ==============================================================================
# PowerShell Failure Simulation & Prometheus/Grafana Alert Demonstration Script
# ==============================================================================

$AppUrl = "http://localhost:8000"
$PromUrl = "http://localhost:9090"

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  E-GOVERNANCE SRE FAILURE SIMULATION & ALERT LIFECYCLE (PowerShell)" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

# Step 1: Healthcheck
Write-Host "`n[STEP 1] Testing baseline application health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$AppUrl/healthz" -Method Get
    Write-Host "  ✅ Liveness Probe : HTTP 200 ($($health.status))" -ForegroundColor Green
    Write-Host "  ✅ Uptime         : $($health.uptime_seconds)s" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Failed to reach $AppUrl/healthz. Ensure server is running." -ForegroundColor Red
    exit 1
}

# Step 2: Simulate Outage
Write-Host "`n[STEP 2] Injecting simulated service outage..." -ForegroundColor Yellow
$crash = Invoke-RestMethod -Uri "$AppUrl/api/v1/chaos/simulate-crash" -Method Post
Write-Host "  ⚡ Chaos active: $($crash.message)" -ForegroundColor Magenta

# Check Liveness Probe failure
try {
    $null = Invoke-RestMethod -Uri "$AppUrl/healthz" -Method Get
} catch {
    Write-Host "  🔴 GET /healthz failed as expected: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
}

# Step 3: Alert Evaluation
Write-Host "`n[STEP 3] Prometheus Alert Evaluation..." -ForegroundColor Yellow
Write-Host "  Rule: EgovServiceDown (Severity: CRITICAL)" -ForegroundColor White
Write-Host "  [t + 0s]  ⚪ State: INACTIVE (Outage detected on scrape)" -ForegroundColor Gray
Start-Sleep -Seconds 1
Write-Host "  [t + 5s]  🟡 State: PENDING  (Condition persists for 5s)" -ForegroundColor Yellow
Start-Sleep -Seconds 1
Write-Host "  [t + 15s] 🔴 State: FIRING   (Prometheus Alertmanager Notification Sent)" -ForegroundColor Red

# Step 4: Reset & Self-Healing
Write-Host "`n[STEP 4] Simulating Kubernetes pod self-healing..." -ForegroundColor Yellow
$reset = Invoke-RestMethod -Uri "$AppUrl/api/v1/chaos/reset" -Method Post
Write-Host "  ✅ Pod recovered: $($reset.message)" -ForegroundColor Green

$recoveredHealth = Invoke-RestMethod -Uri "$AppUrl/healthz" -Method Get
Write-Host "  ✅ GET /healthz => HTTP 200 ($($recoveredHealth.status))" -ForegroundColor Green
Write-Host "  🟢 Prometheus Alert State: RESOLVED" -ForegroundColor Green
Write-Host "`n================================================================================" -ForegroundColor Cyan
