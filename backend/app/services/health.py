from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.schemas.health import HealthResponse, ReadinessResponse


def get_health_status(settings: Settings) -> HealthResponse:
    return HealthResponse(status="ok", app_name=settings.app_name, environment=settings.environment)


def get_readiness_status(db: Session) -> ReadinessResponse:
    """Raises if the database is unreachable; callers translate that to 503."""
    db.execute(text("SELECT 1"))
    return ReadinessResponse(status="ok", database="ok")
