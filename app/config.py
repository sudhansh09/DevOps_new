"""
E-Governance Application Configuration
Loads environment variables configured via Kubernetes ConfigMap and Secrets.
"""
import os

class Settings:
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "egov-citizen-portal")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    VERSION: str = os.getenv("VERSION", "1.0.0")
    
    # Database and Security (populated by K8s Secret)
    DB_HOST: str = os.getenv("DB_HOST", "postgres.egov-system.svc.cluster.local")
    DB_NAME: str = os.getenv("DB_NAME", "egov_portal_db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "egov-dev-secret-key-change-in-prod")
    API_KEY: str = os.getenv("API_KEY", "egov-public-api-key-2026")

settings = Settings()
