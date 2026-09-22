import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import MembershipRole
from app.models.membership import ProjectMembership
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.authorization import is_project_member
from app.services.exceptions import AuthorizationError, NotFoundError


def create_project(db: Session, owner: User, data: ProjectCreate) -> Project:
    project = Project(name=data.name, description=data.description, owner_id=owner.id)
    db.add(project)
    db.flush()  # assign project.id before creating the owner membership

    # Business rule: creating a project automatically creates an owner membership.
    db.add(ProjectMembership(project_id=project.id, user_id=owner.id, role=MembershipRole.OWNER))

    db.commit()
    db.refresh(project)
    return project


def get_project(db: Session, project_id: uuid.UUID) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise NotFoundError(f"Project {project_id} not found.")
    return project


def get_project_for_member(db: Session, project_id: uuid.UUID, user_id: uuid.UUID) -> Project:
    """Fetch a project, requiring the caller to be one of its members."""
    project = get_project(db, project_id)
    if not is_project_member(db, project_id, user_id):
        raise AuthorizationError(f"User {user_id} is not a member of project {project_id}.")
    return project


def list_projects_for_user(
    db: Session, user_id: uuid.UUID, limit: int = 100, offset: int = 0
) -> list[Project]:
    stmt = (
        select(Project)
        .join(ProjectMembership, ProjectMembership.project_id == Project.id)
        .where(ProjectMembership.user_id == user_id)
        .order_by(Project.created_at)
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(stmt))


def update_project(db: Session, project_id: uuid.UUID, user_id: uuid.UUID, data: ProjectUpdate) -> Project:
    project = get_project(db, project_id)
    if project.owner_id != user_id:
        raise AuthorizationError("Only the project owner can update this project.")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project_id: uuid.UUID, user_id: uuid.UUID) -> None:
    project = get_project(db, project_id)
    if project.owner_id != user_id:
        raise AuthorizationError("Only the project owner can delete this project.")

    db.delete(project)
    db.commit()
