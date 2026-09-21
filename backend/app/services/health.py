from app.core.config import Settings
from app.schemas.health import HealthResponse


def get_health_status(settings: Settings) -> HealthResponse:
    return HealthResponse(status="ok", app_name=settings.app_name, environment=settings.environment)
