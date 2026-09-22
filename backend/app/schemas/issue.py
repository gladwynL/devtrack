import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import IssuePriority, IssueStatus


class IssueBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    status: IssueStatus = IssueStatus.TODO
    priority: IssuePriority = IssuePriority.MEDIUM
    assignee_id: uuid.UUID | None = None


class IssueCreate(IssueBase):
    # No authentication yet, so the creator is supplied explicitly.
    created_by_id: uuid.UUID


class IssueUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: IssueStatus | None = None
    priority: IssuePriority | None = None
    assignee_id: uuid.UUID | None = None


class IssueResponse(IssueBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    created_by_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
