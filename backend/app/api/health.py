from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.schemas.health import HealthResponse, ReadinessResponse
from app.services.health import get_health_status, get_readiness_status

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Liveness: the process is up. Deliberately cheap — no external calls."""
    return get_health_status(settings)


@router.get("/ready", response_model=ReadinessResponse)
def ready(db: Session = Depends(get_db)) -> ReadinessResponse:
    """Readiness: the process is up AND the database is reachable."""
    try:
        return get_readiness_status(db)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable"
        ) from exc
