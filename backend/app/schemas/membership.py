import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import MembershipRole


class MembershipCreate(BaseModel):
    user_id: uuid.UUID
    role: MembershipRole = MembershipRole.MEMBER


class MembershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    user_id: uuid.UUID
    role: MembershipRole
    created_at: datetime
