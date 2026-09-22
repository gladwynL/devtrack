import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.membership import ProjectMembership


def is_project_member(db: Session, project_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    stmt = select(ProjectMembership.id).where(
        ProjectMembership.project_id == project_id,
        ProjectMembership.user_id == user_id,
    )
    return db.scalar(stmt) is not None
