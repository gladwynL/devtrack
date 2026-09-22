import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import MembershipRole
from app.models.membership import ProjectMembership
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.exceptions import NotFoundError, ValidationError


def create_project(db: Session, data: ProjectCreate) -> Project:
    owner = db.get(User, data.owner_id)
    if owner is None:
        raise ValidationError(f"Owner {data.owner_id} does not exist.")

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


def list_projects(db: Session, limit: int = 100, offset: int = 0) -> list[Project]:
    stmt = select(Project).order_by(Project.created_at).limit(limit).offset(offset)
    return list(db.scalars(stmt))


def update_project(db: Session, project_id: uuid.UUID, data: ProjectUpdate) -> Project:
    project = get_project(db, project_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project_id: uuid.UUID) -> None:
    project = get_project(db, project_id)
    db.delete(project)
    db.commit()
