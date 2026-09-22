import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.membership import ProjectMembership
from app.models.user import User
from app.schemas.membership import MembershipCreate, MembershipResponse
from app.services import memberships as memberships_service

# Membership routes are nested under /projects/{project_id}, which FastAPI
# does not allow as a router `prefix` (prefixes can't contain path
# parameters), so each route spells out its full path instead.
router = APIRouter(tags=["memberships"])


@router.get("/projects/{project_id}/members", response_model=list[MembershipResponse])
def list_members(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProjectMembership]:
    return memberships_service.list_members(db, project_id, current_user.id)


@router.post(
    "/projects/{project_id}/members", response_model=MembershipResponse, status_code=status.HTTP_201_CREATED
)
def add_member(
    project_id: uuid.UUID,
    data: MembershipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectMembership:
    return memberships_service.add_member(db, project_id, current_user.id, data)


@router.delete("/projects/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    memberships_service.remove_member(db, project_id, user_id, current_user.id)
