# ==============================================================================
# Multi-Stage Production Dockerfile for E-Governance Citizen Portal API
# Security Hardened: Non-Root Execution, Minimal Attack Surface, Healthchecks
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Dependency Builder Stage
# ------------------------------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and build wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ------------------------------------------------------------------------------
# Stage 2: Hardened Production Runtime Stage
# ------------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

# Create dedicated non-root application user and group
RUN groupadd -g 10001 egov && \
    useradd -u 10001 -g egov -s /bin/false -m -d /app egovuser

WORKDIR /app

# Copy installed Python packages from builder stage
COPY --from=builder /root/.local /home/egovuser/.local

# Copy application source code
COPY --chown=egovuser:egov ./app ./app

# Set environment variables
ENV PATH=/home/egovuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    HOST=0.0.0.0

# Expose microservice and Prometheus metrics port
EXPOSE 8000

# Container Healthcheck (Kubernetes/Docker health probe)
HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz')" || exit 1

# Switch to non-privileged user
USER 10001

# Start Uvicorn ASGI server with production workers
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--log-level", "info"]
