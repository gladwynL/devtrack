import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.issue import Issue
from app.schemas.issue import IssueCreate, IssueResponse, IssueUpdate
from app.services import issues as issues_service

# Issue routes span two path shapes (/projects/{project_id}/issues and
# /issues/{issue_id}), so this router carries no shared prefix.
router = APIRouter(tags=["issues"])


@router.post(
    "/projects/{project_id}/issues", response_model=IssueResponse, status_code=status.HTTP_201_CREATED
)
def create_issue(project_id: uuid.UUID, data: IssueCreate, db: Session = Depends(get_db)) -> Issue:
    return issues_service.create_issue(db, project_id, data)


@router.get("/projects/{project_id}/issues", response_model=list[IssueResponse])
def list_project_issues(
    project_id: uuid.UUID, limit: int = 100, offset: int = 0, db: Session = Depends(get_db)
) -> list[Issue]:
    return issues_service.list_project_issues(db, project_id, limit=limit, offset=offset)


@router.get("/issues/{issue_id}", response_model=IssueResponse)
def get_issue(issue_id: uuid.UUID, db: Session = Depends(get_db)) -> Issue:
    return issues_service.get_issue(db, issue_id)


@router.patch("/issues/{issue_id}", response_model=IssueResponse)
def update_issue(issue_id: uuid.UUID, data: IssueUpdate, db: Session = Depends(get_db)) -> Issue:
    return issues_service.update_issue(db, issue_id, data)


@router.delete("/issues/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_issue(issue_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    issues_service.delete_issue(db, issue_id)
