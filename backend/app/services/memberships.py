import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.membership import ProjectMembership
from app.models.user import User
from app.schemas.membership import MembershipCreate
from app.services.exceptions import ConflictError, NotFoundError, ValidationError
from app.services.projects import get_project


def add_member(db: Session, project_id: uuid.UUID, data: MembershipCreate) -> ProjectMembership:
    get_project(db, project_id)  # 404 if the project does not exist

    user = db.get(User, data.user_id)
    if user is None:
        raise ValidationError(f"User {data.user_id} does not exist.")

    membership = ProjectMembership(project_id=project_id, user_id=data.user_id, role=data.role)
    db.add(membership)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(f"User {data.user_id} is already a member of project {project_id}.") from exc
    db.refresh(membership)
    return membership


def list_members(db: Session, project_id: uuid.UUID) -> list[ProjectMembership]:
    get_project(db, project_id)  # 404 if the project does not exist
    stmt = (
        select(ProjectMembership)
        .where(ProjectMembership.project_id == project_id)
        .order_by(ProjectMembership.created_at)
    )
    return list(db.scalars(stmt))


def remove_member(db: Session, project_id: uuid.UUID, user_id: uuid.UUID) -> None:
    project = get_project(db, project_id)

    if project.owner_id == user_id:
        raise ValidationError("The project owner cannot be removed from the project.")

    stmt = select(ProjectMembership).where(
        ProjectMembership.project_id == project_id,
        ProjectMembership.user_id == user_id,
    )
    membership = db.scalar(stmt)
    if membership is None:
        raise NotFoundError(f"User {user_id} is not a member of project {project_id}.")

    db.delete(membership)
    db.commit()


def is_project_member(db: Session, project_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    stmt = select(ProjectMembership.id).where(
        ProjectMembership.project_id == project_id,
        ProjectMembership.user_id == user_id,
    )
    return db.scalar(stmt) is not None
